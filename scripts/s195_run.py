"""Session 19.5 steps 1 through 3, run from the frozen inputs.

MEMORY CEILING 4.0 GB, stated before running. Single-specification runs are
expected far below it; the figure is recorded because the machine carries 8 GB
and session 19 reached 3.355 GB.

TOLERANCES, FIXED HERE BEFORE ANY COMPARISON RUNS.
  TOL_CANON  = 5e-7 on the canonical positive control, being six decimals.
  TOL_LADDER = 5e-5 on a ladder row reproduced against the emitted CSV, the
               same bound session 15 used for its own positive control.
  TOL_SCALING = 5e-3 on annualised Sharpe when testing whether a ladder row
               equals a costless compounded scaling of QQQ. A row inside this
               bound of the costless construction, while outside it against
               the live fund, is a scaling.
"""
from __future__ import annotations

import csv
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s13_backtest as bt       # noqa: E402
import scripts.s14_common as C          # noqa: E402
import scripts.s15_lines as L           # noqa: E402
from src import config                  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-19_5"
OUT.mkdir(parents=True, exist_ok=True)

MEM_CEILING_GB = 4.0
TOL_CANON, TOL_LADDER, TOL_SCALING = 5e-7, 5e-5, 5e-3
CORRECTED_START = pd.Timestamp("2011-10-04")
LADDER_START = pd.Timestamp("2011-10-03")     # what session 15 actually used
TARGET_ANN, TARGET_SLO = 0.521845, 1.381701
timings = {}


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def lo_parts(excess: pd.Series, q: int = 252):
    """Reproduce bt.lo_sharpe and return its internals."""
    x = excess.dropna().to_numpy()
    mu, sd = x.mean(), x.std(ddof=1)
    n = len(x)
    xc = x - mu
    denom = float(np.dot(xc, xc))
    acf_sum = 0.0
    for k in range(1, q):
        acf_sum += (q - k) * float(np.dot(xc[:-k], xc[k:])) / denom
    scale_sq = q + 2.0 * acf_sum
    rho1 = float(np.dot(xc[:-1], xc[1:])) / denom
    naive = mu / sd * math.sqrt(252.0)
    lo = mu / sd * q / math.sqrt(scale_sq) if scale_sq > 0 else float("nan")
    return dict(n=n, mu=mu, sd=sd, rho1=rho1, acf_sum=acf_sum,
                scale_sq=scale_sq, q=q, naive=naive, lo=lo,
                lo_factor=lo / naive if naive else float("nan"))


t0 = time.time()
C.PRIMARY_START = CORRECTED_START
env = C.build_env(verbose=False)
panels, cal, sigs, o2o = env["panels"], env["cal"], env["sigs"], env["o2o"]
cap_fn = env["cap_fn"]
LINES = L.make_lines(cal)
timings["build_env"] = time.time() - t0
print(f"env built in {timings['build_env']:.1f}s, calendar {len(cal)} sessions")


def run(rows, panel, sig, conv="o2o"):
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    return bt.run_account(sig["sig"], panel, rows, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM], slip_fn=sf,
                          cap_fn=cap_fn)


def window(s: pd.Series, start: pd.Timestamp) -> pd.Series:
    return s.loc[s.index >= start].dropna()


def eff_exposure(acc, start):
    """Mean gross leveraged exposure, weight times fund multiple, per session."""
    daily = acc["daily"]
    idx = daily.index
    sel = idx >= start
    tot, cnt = 0.0, 0
    for d, w in zip(idx[sel], daily["weights"][sel]):
        if not isinstance(w, dict):
            continue
        e = 0.0
        for t, wt in w.items():
            try:
                m = bt.fund_multiple(t, d) if hasattr(bt, "fund_multiple") else None
            except Exception:
                m = None
            if m is None:
                import src.schedule as sch
                try:
                    m = sch.fund_terms(t, d).multiple
                except Exception:
                    m = None
            e += abs(wt) * (abs(m) if m else 1.0)
        tot += e; cnt += 1
    return tot / cnt if cnt else float("nan")


rows_out = []


def add(table, **kw):
    rows_out.append({"table": table, **kw})


# ===========================================================================
# STEP 1, positive control then QQQ
# ===========================================================================
print("\n== STEP 1, positive control ==")
t = time.time()
sig = sigs["realized"]
acc_s = run(sig["rows"], o2o, sig)
r_s = window(acc_s["daily"]["ret"], CORRECTED_START)
nav_s = acc_s["daily"]["nav"]
ms = L.standalone_metrics(r_s, nav_s, acc_s["orders"])
d_ann, d_slo = abs(ms["ann_return"] - TARGET_ANN), abs(ms["sharpe_lo"] - TARGET_SLO)
ok = d_ann < TOL_CANON and d_slo < TOL_CANON
timings["step1_canonical"] = time.time() - t
print(f"  canonical ann_return {ms['ann_return']:.6f} target {TARGET_ANN} gap {d_ann:.2e}")
print(f"  canonical sharpe_lo  {ms['sharpe_lo']:.6f} target {TARGET_SLO} gap {d_slo:.2e}")
print(f"  sessions {len(r_s)}   positive control {'PASS' if ok else 'FAIL'}")
add("positive_control", item="tolerance", value=TOL_CANON,
    note="stated before comparing, six decimals")
add("positive_control", item="ann_return", value=ms["ann_return"],
    target=TARGET_ANN, abs_gap=d_ann, within=int(d_ann < TOL_CANON))
add("positive_control", item="sharpe_lo", value=ms["sharpe_lo"],
    target=TARGET_SLO, abs_gap=d_slo, within=int(d_slo < TOL_CANON))
add("positive_control", item="n_sessions", value=len(r_s))
add("positive_control", item="verdict", note="PASS" if ok else "FAIL")
if not ok:
    with open(OUT / "qqq-control.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "target",
                                           "abs_gap", "within", "note"],
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows_out)
    raise SystemExit("canonical positive control failed, halting")

print("\n== STEP 1, QQQ over the primary window ==")
t = time.time()
# Two accounts. The ladder entered at its own 2011-10-03 start, and the entry
# index sets the first fill, so comparing a corrected-start account against the
# ladder's figures measures the entry index rather than the ladder.
I_CORR = int(np.searchsorted(cal.to_numpy(), np.datetime64(CORRECTED_START)))
I_LAD = int(np.searchsorted(cal.to_numpy(), np.datetime64(LADDER_START)))
acc_q = run(LINES["buy_hold_QQQ"][0](o2o, sig["rows"], I_CORR), o2o, sig)
acc_q_lad = run(LINES["buy_hold_QQQ"][0](o2o, sig["rows"], I_LAD), o2o, sig)
rf_all = bt.rf_per_session(acc_q["daily"].index)
for label, start, acc_use in (("corrected_2011_10_04", CORRECTED_START, acc_q),
                              ("ladder_2011_10_03", LADDER_START, acc_q_lad)):
    r_q = window(acc_use["daily"]["ret"], start)
    rf = rf_all.reindex(r_q.index).fillna(0.0)
    ex = (r_q - rf).dropna()
    p = lo_parts(ex)
    mq = L.standalone_metrics(r_q, acc_use["daily"]["nav"], acc_use["orders"])
    add("qqq", item=label, ann_return=mq["ann_return"], ann_vol=mq["ann_vol"],
        mean_rf_ann=float(rf.mean() * 252.0), sharpe_naive=p["naive"],
        sharpe_lo=p["lo"], lo_factor=p["lo_factor"], rho1=p["rho1"],
        lag_count=p["q"] - 1, acf_sum=p["acf_sum"], scale_sq=p["scale_sq"],
        n_sessions=p["n"],
        note="q=252 in bt.lo_sharpe, so 251 lags enter the correction")
    print(f"  [{label}] n={p['n']} ann_ret {mq['ann_return']:.6f} "
          f"vol {mq['ann_vol']:.6f} rf {rf.mean()*252:.6f}")
    print(f"      naive {p['naive']:.6f}  lo {p['lo']:.6f}  factor {p['lo_factor']:.6f} "
          f"rho1 {p['rho1']:+.6f} acf_sum {p['acf_sum']:.3f}")

lad = pd.read_csv(ROOT / "outputs/session-15/metrics-full.csv")
lad = lad[(lad.table == "metrics") & (lad.panel == "realized")
          & (lad.convention == "o2o") & (lad.window == "primary")]
ref_q = lad[lad.line == "buy_hold_QQQ"].iloc[0]
r_q13 = window(acc_q_lad["daily"]["ret"], LADDER_START)
m13 = L.standalone_metrics(r_q13, acc_q_lad["daily"]["nav"], acc_q_lad["orders"])
gaps = {k: abs(m13[k] - float(ref_q[k]))
        for k in ("ann_return", "ann_vol", "sharpe_naive", "sharpe_lo")}
worst = max(gaps.values())
add("qqq_vs_ladder", item="tolerance", value=TOL_LADDER,
    note="stated before comparing")
for k, v in gaps.items():
    add("qqq_vs_ladder", item=k, value=m13[k], target=float(ref_q[k]), abs_gap=v,
        within=int(v < TOL_LADDER),
        note="reproduced with the ladder's own 2011-10-03 entry index and start")
add("qqq_vs_ladder", item="worst_gap", value=worst,
    within=int(worst < TOL_LADDER))
print(f"\n  QQQ reproduced against the ladder CSV on its own start, worst gap "
      f"{worst:.2e} against tolerance {TOL_LADDER:.0e} -> "
      f"{'WITHIN' if worst < TOL_LADDER else 'OUTSIDE'}")

ind = ROOT / "data" / "raw" / "etf" / "QQQ.parquet"
add("qqq_external", item="independent_series",
    note=f"the only QQQ total-return path in this repository is the frozen input "
         f"{ind.relative_to(ROOT)}, which is the same series the ladder used. No "
         f"second independent QQQ source exists offline and no network fetch is "
         f"attempted, so external verification is PENDING rather than performed")
print("  external verification PENDING, no independent offline QQQ path exists")
timings["step1_qqq"] = time.time() - t

# ===========================================================================
# STEP 2, decompose every ladder row
# ===========================================================================
print("\n== STEP 2, ladder decomposition ==")
t = time.time()
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(LADDER_START)))
dec = []
for line in lad.line:
    if line == "STRATEGY":
        acc = acc_s
    else:
        rws = LINES[line][0](o2o, sig["rows"], i0)
        acc = run(rws, o2o, sig)
    r = window(acc["daily"]["ret"], LADDER_START)
    rf = rf_all.reindex(r.index).fillna(0.0)
    p = lo_parts((r - rf).dropna())
    mm = L.standalone_metrics(r, acc["daily"]["nav"], acc["orders"])
    ref = lad[lad.line == line].iloc[0]
    g = abs(p["lo"] - float(ref.sharpe_lo))
    dec.append(dict(line=line, ann_return=mm["ann_return"], ann_vol=mm["ann_vol"],
                    sharpe_naive=p["naive"], sharpe_lo=p["lo"],
                    lo_factor=p["lo_factor"], rho1=p["rho1"], lag_count=p["q"] - 1,
                    acf_sum=p["acf_sum"],
                    mean_eff_exposure=eff_exposure(acc, LADDER_START),
                    ann_turnover=mm["ann_turnover"], n_sessions=p["n"],
                    csv_sharpe_lo=float(ref.sharpe_lo), abs_gap=g,
                    reproduces=int(g < TOL_LADDER)))
    print(f"  {line:<36} naive {p['naive']:.4f}  lo {p['lo']:.4f}  "
          f"factor {p['lo_factor']:.4f}  rho1 {p['rho1']:+.4f}  gap {g:.2e}")

dd = pd.DataFrame(dec)
dd["rank_naive"] = dd.sharpe_naive.rank(ascending=False, method="min").astype(int)
dd["rank_lo"] = dd.sharpe_lo.rank(ascending=False, method="min").astype(int)
dd["rank_changed"] = (dd.rank_naive != dd.rank_lo).astype(int)
for _, r in dd.iterrows():
    add("decomposition", item=r.line, **{k: r[k] for k in
        ("ann_return", "ann_vol", "sharpe_naive", "sharpe_lo", "lo_factor", "rho1",
         "lag_count", "acf_sum", "mean_eff_exposure", "ann_turnover", "n_sessions",
         "csv_sharpe_lo", "abs_gap", "reproduces", "rank_naive", "rank_lo",
         "rank_changed")})
n_changed = int(dd.rank_changed.sum())
st = dd[dd.line == "STRATEGY"].iloc[0]
add("ranking", item="rows_with_rank_change", value=n_changed,
    note="of twelve, comparing the naive Sharpe ranking against the Lo-corrected one")
add("ranking", item="strategy_rank_naive", value=int(st.rank_naive))
add("ranking", item="strategy_rank_lo", value=int(st.rank_lo))
add("ranking", item="worst_reproduction_gap", value=float(dd.abs_gap.max()),
    within=int(dd.abs_gap.max() < TOL_LADDER))
print(f"\n  rank changes between the two metrics: {n_changed} of 12")
print(f"  strategy rank naive {int(st.rank_naive)}, Lo-corrected {int(st.rank_lo)}")
print(dd[["line", "sharpe_naive", "rank_naive", "sharpe_lo", "rank_lo"]]
      .sort_values("rank_lo").to_string(index=False,
                                        float_format=lambda x: f"{x:.4f}"))
timings["step2"] = time.time() - t

# ===========================================================================
# STEP 3, construction audit
# ===========================================================================
print("\n== STEP 3, construction audit ==")
t = time.time()
LEV_LINES = {"buy_hold_TQQQ": ["TQQQ"],
             "matched_exposure_levered_QQQ_1.70": ["TQQQ"],
             "vol_targeted_QQQ_matched": ["TQQQ"]}
for ln, tks in LEV_LINES.items():
    add("line_construction", item=ln, note=
        f"holds the {'/'.join(tks)} ticker from the panel rather than a scaling of "
        f"QQQ. On the realized arm bt.load_arm_panel takes levered tickers from "
        f"_frozen_frame, being the frozen fund parquet, so the series is the live "
        f"fund's own history carrying its real daily reset, financing and expense. "
        f"On the synthetic arm the same tickers come from _synthetic_frame, being "
        f"the reconstruction. The designated cell is the realized arm")

add("financing", item="rate_source",
    note="frozen DTB3 accrued at rate/360 per calendar day between sessions, the "
         "5.5a convention, applied inside scripts/s10_build.py")
add("financing", item="spread",
    note=f"config.FINANCING_SPREAD_BP = {config.FINANCING_SPREAD_BP} bp over the "
         f"reference for multiples above one, a haircut for inverse funds, and "
         f"k=0 for the volatility funds which are futures-based under 2.15. D16 "
         f"records the spread as assumed rather than measured")
add("financing", item="applies_to",
    note="the reconstructions only. The realized arm carries the live fund prices, "
         "in which financing is already embedded by the issuer")
add("daily_reset", item="convention",
    note="the levered daily return compounds session to session inside the "
         "reconstruction, so path dependence and volatility decay are carried "
         "rather than assumed away. Rebalance is daily at the close")

val = None
for cand in ("outputs/session-11/synthetic-validation.csv",
             "outputs/session-10/synthetic-validation-primary.csv",
             "outputs/session-12/final-validation.csv"):
    if (ROOT / cand).exists():
        val = cand
        break
add("reconstruction_validation", item="artifact", note=val or "NOT FOUND")
print(f"  reconstruction validation artifact: {val}")

# decisive check
qret = o2o["QQQ"].ret_total.reindex(cal)
tret = o2o["TQQQ"].ret_total.reindex(cal)
mask = (cal >= LADDER_START)
q = qret[mask].dropna()
tq = tret[mask].dropna()
common = q.index.intersection(tq.index)
q, tq = q.loc[common], tq.loc[common]
costless = 3.0 * q                      # daily reset, no financing, no expense
rfc = rf_all.reindex(common).fillna(0.0)


def stat(r):
    p = lo_parts((r - rfc.reindex(r.index).fillna(0.0)).dropna())
    nav = (1.0 + r).cumprod()
    yrs = len(r) / 252.0
    return dict(ann_return=float(nav.iloc[-1] ** (1.0 / yrs) - 1.0),
                ann_vol=float(r.std(ddof=1) * math.sqrt(252.0)),
                sharpe_naive=p["naive"], sharpe_lo=p["lo"], n=len(r))


s_costless, s_live = stat(costless), stat(tq)
ref_t = lad[lad.line == "buy_hold_TQQQ"].iloc[0]
gap_costless = abs(s_costless["sharpe_naive"] - float(ref_t.sharpe_naive))
gap_live = abs(s_live["sharpe_naive"] - float(ref_t.sharpe_naive))
# Annualised volatility discriminates more sharply than the Sharpe, since it is
# untouched by the risk-free subtraction and by the account's cash accrual.
vgap_costless = abs(s_costless["ann_vol"] - float(ref_t.ann_vol))
vgap_live = abs(s_live["ann_vol"] - float(ref_t.ann_vol))
add("decisive_check", item="vol_gap_vs_costless", value=vgap_costless)
add("decisive_check", item="vol_gap_vs_live", value=vgap_live)
add("decisive_check", item="closer_on_volatility",
    note="live fund" if vgap_live < vgap_costless else "costless scaling")
is_scaling = (gap_costless < TOL_SCALING and gap_live > TOL_SCALING) or \
             (vgap_costless < vgap_live and vgap_costless < TOL_SCALING)
add("decisive_check", item="tolerance", value=TOL_SCALING,
    note="stated before comparing, on annualised naive Sharpe")
for nm, s in (("costless_3x_QQQ", s_costless), ("live_TQQQ", s_live)):
    add("decisive_check", item=nm, ann_return=s["ann_return"], ann_vol=s["ann_vol"],
        sharpe_naive=s["sharpe_naive"], sharpe_lo=s["sharpe_lo"], n_sessions=s["n"])
add("decisive_check", item="ladder_buy_hold_TQQQ",
    ann_return=float(ref_t.ann_return), ann_vol=float(ref_t.ann_vol),
    sharpe_naive=float(ref_t.sharpe_naive), sharpe_lo=float(ref_t.sharpe_lo))
add("decisive_check", item="gap_vs_costless", value=gap_costless,
    within=int(gap_costless < TOL_SCALING))
add("decisive_check", item="gap_vs_live", value=gap_live,
    within=int(gap_live < TOL_SCALING))
add("decisive_check", item="row_is_costless_scaling", value=int(is_scaling),
    note="a row inside tolerance of the costless construction while outside it "
         "against the live fund would be a scaling")
print(f"  costless 3x QQQ   ann {s_costless['ann_return']:.6f} vol "
      f"{s_costless['ann_vol']:.6f} naive {s_costless['sharpe_naive']:.6f}")
print(f"  live TQQQ         ann {s_live['ann_return']:.6f} vol "
      f"{s_live['ann_vol']:.6f} naive {s_live['sharpe_naive']:.6f}")
print(f"  ladder TQQQ row   ann {float(ref_t.ann_return):.6f} vol "
      f"{float(ref_t.ann_vol):.6f} naive {float(ref_t.sharpe_naive):.6f}")
print(f"  Sharpe gap against costless {gap_costless:.6f}, against live {gap_live:.6f}")
print(f"  vol gap against costless {vgap_costless:.6f}, against live {vgap_live:.6f} "
      f"-> closer to {'live fund' if vgap_live < vgap_costless else 'costless scaling'}")
print(f"  row is a costless scaling: {is_scaling}")
timings["step3"] = time.time() - t

# --- sampling control for the Lo correction -------------------------------
# The Lo scale sums 251 weighted sample autocorrelations from 2472 observations.
# Under a null with no autocorrelation the sum is neither zero nor tightly
# distributed, so the observed factor is compared against that null rather than
# read as signal. The null is an iid bootstrap of the same excess returns, which
# preserves the marginal distribution and destroys the serial dependence.
print("\n== Lo correction sampling control ==")
t = time.time()
LO_SEED, LO_DRAWS = 20260819, 300
rq_c = window(acc_q["daily"]["ret"], CORRECTED_START)
ex_q = (rq_c - rf_all.reindex(rq_c.index).fillna(0.0)).dropna()
obs = lo_parts(ex_q)
rng = np.random.default_rng(LO_SEED)
xv = ex_q.to_numpy()
sums, facs = [], []
for _ in range(LO_DRAWS):
    d = pd.Series(rng.permutation(xv))
    pp = lo_parts(d)
    sums.append(pp["acf_sum"]); facs.append(pp["lo_factor"])
sums, facs = np.array(sums), np.array(facs)
z = (obs["acf_sum"] - sums.mean()) / sums.std(ddof=1)
add("lo_control", item="seed", value=LO_SEED, note="fixed before drawing")
add("lo_control", item="draws", value=LO_DRAWS,
    note="iid permutation of the same excess returns, marginal preserved, serial "
         "dependence destroyed")
add("lo_control", item="observed_acf_sum", value=obs["acf_sum"])
add("lo_control", item="null_acf_sum_mean", value=float(sums.mean()),
    note="not zero, because each sample autocorrelation carries a negative "
         "small-sample bias of order -1/n and 251 of them are summed with "
         "weights up to 251")
add("lo_control", item="null_acf_sum_sd", value=float(sums.std(ddof=1)))
add("lo_control", item="observed_z_against_null", value=float(z))
add("lo_control", item="observed_lo_factor", value=obs["lo_factor"])
add("lo_control", item="null_lo_factor_mean", value=float(facs.mean()))
add("lo_control", item="null_lo_factor_sd", value=float(facs.std(ddof=1)))
add("lo_control", item="null_lo_factor_p05", value=float(np.percentile(facs, 5)))
add("lo_control", item="null_lo_factor_p95", value=float(np.percentile(facs, 95)))
add("lo_control", item="null_lo_factor_max", value=float(facs.max()))
print(f"  observed acf_sum {obs['acf_sum']:.3f}, null mean {sums.mean():.3f} "
      f"sd {sums.std(ddof=1):.3f}, z {z:+.3f}")
print(f"  observed Lo factor {obs['lo_factor']:.4f}, null mean {facs.mean():.4f} "
      f"sd {facs.std(ddof=1):.4f}, null p05 {np.percentile(facs,5):.4f} "
      f"p95 {np.percentile(facs,95):.4f}")
timings["lo_control"] = time.time() - t

peak = rss_gb()
add("resources", item="memory_ceiling_gb", value=MEM_CEILING_GB,
    note="stated before running")
add("resources", item="peak_rss_gb", value=round(peak, 3),
    within=int(peak <= MEM_CEILING_GB))
for k, v in timings.items():
    add("resources", item=f"seconds_{k}", value=round(v, 2))
print(f"\npeak RSS {peak:.3f} GB against a {MEM_CEILING_GB} GB ceiling")

COLS = ["table", "item", "value", "target", "abs_gap", "within", "ann_return",
        "ann_vol", "mean_rf_ann", "sharpe_naive", "sharpe_lo", "lo_factor", "rho1",
        "lag_count", "acf_sum", "scale_sq", "mean_eff_exposure", "ann_turnover",
        "n_sessions", "csv_sharpe_lo", "reproduces", "rank_naive", "rank_lo",
        "rank_changed", "note"]


def dump(name, tables):
    sel = [r for r in rows_out if r["table"] in tables]
    with open(OUT / name, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader(); w.writerows(sel)
    print(f"wrote {OUT/name} with {len(sel)} rows")


dump("qqq-control.csv", {"positive_control", "qqq", "qqq_vs_ladder", "qqq_external"})
dump("ladder-decomposition.csv", {"decomposition", "ranking"})
dump("construction-audit.csv", {"line_construction", "financing", "daily_reset",
                                "reconstruction_validation", "decisive_check",
                                "resources"})
dump("lo-control.csv", {"lo_control"})
