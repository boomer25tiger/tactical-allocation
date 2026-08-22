"""Session 27 phase D. The prediction components.

Phase C did not persist the per-session sleeve dicts and portfolio weights that
P3 part two, P4 and P5 require. This phase re-executes the IDENTICAL deterministic
environment build and account run to obtain them, varying no specification and
recomputing no quantity differently, and it ASSERTS that the canonical's holdout
figures reproduce exactly against what phase C already wrote. A mismatch would
mean the pass was not identical and halts the phase.

Each component is marked confirmed, falsified, or not evaluable against the
condition as stated in docs/HOLDOUT-PREDICTION.md. Nothing beyond that is written.
"""
from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                    # noqa: E402
import pandas as pd                                   # noqa: E402
import scripts.s13_backtest as bt                     # noqa: E402
import scripts.s14_common as C                        # noqa: E402
import scripts.s15_lines as L                         # noqa: E402
import src.sleeves as SL                              # noqa: E402
from src import config                                # noqa: E402

OUT = ROOT / "outputs" / "session-27"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRED = (ROOT / "docs" / "HOLDOUT-PREDICTION.md").read_text()
rows = []


def add(**kw):
    rows.append(kw)


def condition(marker):
    """The exact sentence from the prediction that states a component's condition."""
    for line in PRED.split("\n"):
        if line.strip().startswith(marker):
            return re.sub(r"\*\*|`", "", line.strip())
    return ""


# ---- the ladder as phase C wrote it ------------------------------------------
LAD = [r for r in csv.DictReader(open(OUT / "holdout-ladder.csv"))
       if r["table"] == "line"]
RANK = [r for r in csv.DictReader(open(OUT / "holdout-ladder.csv"))
        if r["table"] == "rank"]
byline = {r["line"]: r for r in LAD}
def rank_of(line, conv):
    r = next(x for x in RANK if x["line"] == line and x["convention"] == conv)
    return int(r["rank"]), int(r["of"])


# ---- P1 -----------------------------------------------------------------------
n_rank, n_of = rank_of("STRATEGY", "sharpe_naive")
l_rank, _ = rank_of("STRATEGY", "sharpe_lo")
p1 = "falsified" if n_rank <= 5 else "confirmed"
add(component="P1", quantity="rank on the naive Sharpe", value=n_rank,
    of=n_of, verdict=p1, condition=condition("**In the holdout, on the designated"),
    note=f"the condition is falsified by any rank of fifth or better and the rank is "
         f"{n_rank} of {n_of}")
add(component="P1", quantity="rank on the Lo-corrected Sharpe", value=l_rank, of=n_of,
    verdict="reported alongside",
    note="8.2 leads on the naive figure while the pre-registered convention is Lo")
add(component="P1", quantity="the two ranks diverge", value=int(n_rank != l_rank),
    verdict="reportable" if n_rank != l_rank else "no divergence",
    note=f"naive {n_rank}, Lo-corrected {l_rank}")
add(component="P1", quantity="strategy naive Sharpe",
    value=byline["STRATEGY"]["sharpe_naive"], verdict="")
add(component="P1", quantity="strategy Lo-corrected Sharpe",
    value=byline["STRATEGY"]["sharpe_lo"], verdict="")

# ---- P2 -----------------------------------------------------------------------
sn = float(byline["STRATEGY"]["sharpe_naive"])
lo_b, hi_b = 0.25, 0.85
p2 = "confirmed" if lo_b <= sn <= hi_b else "falsified"
near = min(abs(sn - lo_b), abs(sn - hi_b))
which = "0.25" if abs(sn - lo_b) < abs(sn - hi_b) else "0.85"
add(component="P2", quantity="holdout naive Sharpe", value=repr(sn), verdict=p2,
    condition=condition("**The strategy's holdout naive Sharpe"),
    note=f"the band is 0.25 to 0.85 and the figure sits "
         f"{'inside' if p2=='confirmed' else 'outside'} it")
add(component="P2", quantity=f"distance to the nearer bound, being {which}",
    value=repr(near), verdict="",
    note="against the primary-window naive Sharpe of 1.0910863648060856")

# ---- the identical re-execution -------------------------------------------------
print("re-executing the identical pass to obtain the retained state series")
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]
r_hold = d["ret"].loc[d.index >= BOUNDARY].dropna()
m = L.standalone_metrics(r_hold, d["nav"].loc[d.index >= BOUNDARY], acc["orders"])
gap_n = abs(m["sharpe_naive"] - float(byline["STRATEGY"]["sharpe_naive"]))
gap_l = abs(m["sharpe_lo"] - float(byline["STRATEGY"]["sharpe_lo"]))
identical = gap_n == 0.0 and gap_l == 0.0 and len(r_hold) == int(
    float(byline["STRATEGY"]["n_sessions"]))
add(component="pass", quantity="re-execution reproduces phase C exactly",
    value=int(identical), verdict="PASS" if identical else "FAIL",
    note=f"naive gap {gap_n}, Lo gap {gap_l}, sessions {len(r_hold)}. The re-execution "
         f"varies no specification and exists only because phase C did not persist the "
         f"per-session sleeve dicts")
print(f"  reproduction {'exact' if identical else 'MISMATCH'}")
if not identical:
    with open(OUT / "prediction-verdicts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["component", "quantity", "value", "of",
                                          "verdict", "condition", "note"],
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    sys.exit(1)

panel = env["panels"]["realized"]
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
ret_panel = pd.DataFrame({t: panel[t].ret_total for t in TICK})
srows = {r["date"]: r for r in sig["rows"]}
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK} for r in acc["raw_rows"]],
                  index=d.index)
hold_idx = d.index[d.index >= BOUNDARY]
prim_idx = d.index[d.index >= C.PRIMARY_START]

# ---- P3 part one, from prices alone --------------------------------------------
a = ret_panel["SQQQ"].reindex(hold_idx).dropna()
b = ret_panel["TLT"].reindex(hold_idx).dropna()
j = a.index.intersection(b.index)
corr_hold = float(a.loc[j].corr(b.loc[j]))
ap = ret_panel["SQQQ"].reindex(prim_idx).dropna()
bp = ret_panel["TLT"].reindex(prim_idx).dropna()
jp = ap.index.intersection(bp.index)
corr_prim = float(ap.loc[jp].corr(bp.loc[jp]))
p3a = "confirmed" if corr_hold > 0 else "falsified"
add(component="P3 part one", quantity="SQQQ and TLT daily return correlation, holdout",
    value=repr(corr_hold), of=len(j), verdict=p3a,
    condition=condition("**Part one. SQQQ and TLT"),
    note="computed from the frozen realized panel's daily total returns without "
         "reference to the strategy")
add(component="P3 part one",
    quantity="the same pair over the primary window", value=repr(corr_prim), of=len(jp),
    verdict="", note="computed here for the first time, since no committed CSV carried "
                     "the direct pair")
add(component="P3 part one", quantity="committed sleeve-level baseline",
    value="-0.5618926986740371", verdict="",
    note="the short leg against the rest of its own sleeve on arm A at "
         "outputs/session-15.5/short-leg-decomposition.csv, which the prediction names "
         "as the committed baseline and flags as not the direct pair")
add(component="P3 part one", quantity="sign flips from the primary window",
    value=int((corr_prim < 0) and (corr_hold > 0)), verdict="",
    note=f"primary {corr_prim}, holdout {corr_hold}")

# ---- P3 part two, T10's risk-off branch ------------------------------------------
RISK_OFF = SL.t10_weights.__doc__ or ""
def is_risk_off(dt):
    r = srows.get(dt)
    if r is None:
        return False
    w = r["sleeves"].get("T10") or {}
    return set(w) == {"SQQQ", "TLT"}
mask = pd.Series([is_risk_off(dt) for dt in d.index], index=d.index)
budget = config.SLEEVE_BUDGET
t10w = pd.DataFrame(
    [{t: (srows[dt]["sleeves"].get("T10") or {}).get(t, 0.0) * budget
      if dt in srows else 0.0 for t in ("SQQQ", "TLT")} for dt in d.index],
    index=d.index)
t10w = t10w.where(mask, 0.0)
contrib = {}
for leg in ("SQQQ", "TLT"):
    w = t10w[leg].shift(1).reindex(hold_idx).fillna(0.0)
    ri = ret_panel[leg].reindex(hold_idx).fillna(0.0)
    contrib[leg] = float((w * ri).sum())
branch_total = contrib["SQQQ"] + contrib["TLT"]
p3b = "confirmed" if branch_total < 0 else "falsified"
add(component="P3 part two", quantity="T10 risk-off branch contribution, holdout",
    value=repr(branch_total), of=int(mask.reindex(hold_idx).sum()), verdict=p3b,
    condition=condition("**Part two. T10's risk-off branch"),
    note="the arithmetic sum of the lagged portfolio weight times the realised return "
         "on each leg across the sessions the branch fired, the same construction "
         "session 15.5 used")
for leg in ("SQQQ", "TLT"):
    add(component="P3 part two", quantity=f"the {leg} leg alone", value=repr(contrib[leg]),
        verdict="", note="")
wp = t10w["SQQQ"].shift(1).reindex(prim_idx).fillna(0.0)
rp = ret_panel["SQQQ"].reindex(prim_idx).fillna(0.0)
add(component="P3 part two", quantity="the SQQQ leg over the primary window",
    value=repr(float((wp * rp).sum())), verdict="",
    note="against the -1.074235187878671 the prediction names, which is the "
         "portfolio-level short-leg figure at session 15.5 rather than a T10-only one")
add(component="P3 part two", quantity="the part predicts persistence rather than change",
    value=1, verdict="",
    note="recorded in the prediction, since the primary-window sign is already negative")
add(component="P3 part two", quantity="sessions the branch fired, holdout",
    value=int(mask.reindex(hold_idx).sum()), verdict="")
add(component="P3 part two", quantity="sessions the branch fired, primary window",
    value=int(mask.reindex(prim_idx).sum()), verdict="")

# ---- P4, the specified examination ------------------------------------------------
mult = {}
for t in TICK:
    fr = panel[t].frame
    if "multiple" in fr.columns and fr["multiple"].notna().any():
        mult[t] = fr["multiple"]
    else:
        mult[t] = pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index)
eff = pd.Series(sum(rw[t].to_numpy() * mult[t].reindex(rw.index).fillna(0.0).to_numpy()
                    for t in TICK), index=rw.index)
qqq_px = panel["QQQ"].ret_total.reindex(d.index).fillna(0.0)
qqq_lv = (1.0 + qqq_px).cumprod()
y22 = qqq_lv.loc[(qqq_lv.index >= "2022-01-01") & (qqq_lv.index <= "2022-12-31")]
peak_dt = y22.idxmax()
after = mask.loc[mask.index > peak_dt]
first_ro = after[after].index.min() if after.any() else None
add(component="P4", quantity="the 2022 peak, taken as buy-and-hold QQQ's 2022 high",
    value=str(peak_dt.date()), verdict="not a prediction",
    condition=condition("**State-classification latency"),
    note="the mechanism concerns classification of a market regime, so the market line "
         "the state machine watches is the peak used. The strategy's own NAV peak is "
         "reported beside it")
snav = d["nav"]
s22 = snav.loc[(snav.index >= "2022-01-01") & (snav.index <= "2022-12-31")]
add(component="P4", quantity="the strategy's own 2022 NAV peak",
    value=str(s22.idxmax().date()), verdict="")
if first_ro is not None:
    n_between = int(((d.index > peak_dt) & (d.index <= first_ro)).sum())
    seg = eff.loc[(eff.index > peak_dt) & (eff.index <= first_ro)]
    add(component="P4", quantity="first risk-off state after the peak",
        value=str(first_ro.date()), verdict="")
    add(component="P4", quantity="sessions from the peak to the first risk-off state",
        value=n_between, verdict="")
    add(component="P4", quantity="mean effective exposure across that interval",
        value=repr(float(seg.mean())), of=len(seg), verdict="")
    add(component="P4", quantity="minimum effective exposure across that interval",
        value=repr(float(seg.min())), verdict="")
    add(component="P4", quantity="maximum effective exposure across that interval",
        value=repr(float(seg.max())), verdict="")
    add(component="P4", quantity="sessions in that interval with exposure above 1.0",
        value=int((seg > 1.0).sum()), of=len(seg), verdict="")
else:
    add(component="P4", quantity="first risk-off state after the peak", value="none",
        verdict="not evaluable",
        note="the branch did not fire after the 2022 peak inside the span")
add(component="P4", quantity="the guard", value="", verdict="",
    note="P4 carries no verdict and does not qualify any other component unless the "
         "state series shows the latency mechanism operating")

# ---- P5, evaluated because P1 is falsified ---------------------------------------
SHORTS = [t for t in ("SQQQ", "TECS", "SOXS", "PSQ", "SH") if t in TICK]
sc = {}
for t in SHORTS:
    w = rw[t].shift(1).reindex(hold_idx).fillna(0.0)
    ri = ret_panel[t].reindex(hold_idx).fillna(0.0)
    sc[t] = float((w * ri).sum())
short_total = sum(sc.values())
if p1 == "falsified":
    net = r_hold - pd.Series(
        sum(rw[t].shift(1).reindex(hold_idx).fillna(0.0)
            * ret_panel[t].reindex(hold_idx).fillna(0.0) for t in SHORTS),
        index=hold_idx).reindex(r_hold.index).fillna(0.0)
    rf = bt.rf_per_session(r_hold.index).reindex(r_hold.index).fillna(0.0)
    ex_net = (net - rf).dropna()
    sh_net = float(ex_net.mean() / ex_net.std(ddof=1) * np.sqrt(252))
    others = sorted((float(x["sharpe_naive"]) for x in LAD if x["line"] != "STRATEGY"),
                    reverse=True)
    rank_net = sum(1 for v in others if v > sh_net) + 1
    add(component="P5", quantity="short-equity sleeve holdout contribution",
        value=repr(short_total), verdict="positive" if short_total > 0 else "negative",
        condition=condition("**If P1 fails"),
        note="the arithmetic sum across " + ", ".join(SHORTS))
    for t in SHORTS:
        add(component="P5", quantity=f"the {t} contribution", value=repr(sc[t]),
            verdict="")
    add(component="P5", quantity="naive Sharpe with the short contribution removed",
        value=repr(sh_net), verdict="",
        note="the pre-specified examination of whether the short sleeve accounts for "
             "the rank, computed once")
    add(component="P5", quantity="rank the strategy would hold on that series",
        value=rank_net, of=n_of, verdict="",
        note=f"against its actual rank of {n_rank}. The short sleeve accounts for the "
             f"rank only if removing it moves the rank past fifth")
    add(component="P5", quantity="the short sleeve accounts for the rank",
        value=int(rank_net > 5), verdict="",
        note="P5's premise requires that removing the short contribution would put the "
             "strategy at sixth or worse")
else:
    add(component="P5", quantity="evaluated", value=0, verdict="not evaluable",
        note="P5 is evaluated only if P1 is falsified, and P1 is confirmed")

fn = ["component", "quantity", "value", "of", "verdict", "condition", "note"]
with open(OUT / "prediction-verdicts.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote prediction-verdicts.csv, {len(rows)} rows")
for r in rows:
    if r.get("verdict") in ("confirmed", "falsified", "not evaluable", "positive",
                            "negative", "PASS", "not a prediction"):
        print(f"  {r['component']:14s} {r['verdict']:16s} {r['quantity']} = {r['value']}")

# retained for phases E through G
pd.DataFrame({"eff_exposure": eff, "t10_risk_off": mask.astype(int)}).to_parquet(
    OUT / "_state_series.parquet")
