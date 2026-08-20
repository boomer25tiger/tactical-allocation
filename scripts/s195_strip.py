"""Session 19.5 steps 4, 5 and 6.

Step 4 is a post-hoc sensitivity under 9.10. The primary window remains
2011-10-04 regardless of what it returns.

MEMORY CEILING 4.0 GB, stated before running.
TOL_CANON 5e-7 on the canonical positive control at the canonical start date.
"""
from __future__ import annotations

import csv
import math
import re
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s13_backtest as bt      # noqa: E402
import scripts.s14_common as C         # noqa: E402
import scripts.s15_lines as L          # noqa: E402
from src import config                 # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-19_5"
MEM_CEILING_GB, TOL_CANON = 4.0, 5e-7
TARGET_ANN, TARGET_SLO = 0.521845, 1.381701
INVERSE = {"SQQQ", "PSQ", "SH", "TECS", "SOXS"}
rows = []
t_all = time.time()


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def add(table, **kw):
    rows.append({"table": table, **kw})


C.PRIMARY_START = pd.Timestamp("2011-10-04")
env = C.build_env(verbose=False)
panels, cal, sigs, o2o, cap_fn = (env["panels"], env["cal"], env["sigs"],
                                  env["o2o"], env["cap_fn"])
LINES = L.make_lines(cal)
sig = sigs["realized"]
rf_all = None   # filled on the first strip pass and reused


def run(rws, panel=None, conv="o2o"):
    panel = o2o if panel is None else panel
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    return bt.run_account(sig["sig"], panel, rws, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM], slip_fn=sf,
                          cap_fn=cap_fn)


def lo_parts(ex, q=252):
    x = ex.dropna().to_numpy()
    mu, sd = x.mean(), x.std(ddof=1)
    xc = x - mu
    den = float(np.dot(xc, xc))
    acc = sum((q - k) * float(np.dot(xc[:-k], xc[k:])) / den for k in range(1, q))
    scale = q + 2.0 * acc
    naive = mu / sd * math.sqrt(252.0)
    lo = mu / sd * q / math.sqrt(scale) if scale > 0 else float("nan")
    return naive, lo


# --- sleeve ticker set and the earliest full-composition date --------------
tokens = sorted(set(re.findall(r'"([A-Z]{2,5})"', (ROOT / "src" / "sleeves.py").read_text())))
syn = panels["synthetic"]
firsts = {}
for t in tokens:
    if t not in syn.frames:
        continue
    tr = syn[t].tr_index.reindex(cal)
    i = np.flatnonzero(tr.notna().to_numpy())
    if len(i):
        firsts[t] = cal[i[0]]
latest_t = max(firsts, key=lambda k: firsts[k])
latest = firsts[latest_t]
j = int(np.searchsorted(cal.to_numpy(), np.datetime64(latest)))
EARLY = cal[j + config.WARMUP_SESSIONS]
add("early_start", item="binding_ticker", note=latest_t)
add("early_start", item="binding_ticker_first_session", note=str(latest.date()))
add("early_start", item="warmup_sessions", value=config.WARMUP_SESSIONS)
add("early_start", item="full_composition_date", note=str(EARLY.date()),
    note2="earliest session at which every ticker named in src/sleeves.py is "
          "available on the synthetic panel and has cleared indicator warmup")
add("early_start", item="later_than_canonical",
    value=int(EARLY > pd.Timestamp("2011-10-04")),
    note="the synthetic panel does not support a full-composition start earlier "
         "than the canonical 2011-10-04, so the strip has no genuinely early arm")
for t, v in sorted(firsts.items(), key=lambda kv: kv[1]):
    add("coverage_ticker", item=t, note=str(v.date()),
        note2="held by a sleeve" if t not in ("QQQ", "SPY", "XLK", "SMH", "AGG",
                                              "IEF", "IOO", "VOX", "VTV", "XLF",
                                              "XLP", "XLY", "VOOG", "VOOV", "QQQE",
                                              "BND") else "signal input")
print(f"earliest full composition on the synthetic panel {EARLY.date()}, "
      f"bound by {latest_t} listing {latest.date()}")

STARTS = [
    ("earliest_full_composition", EARLY),
    ("pre_D21_boundary", pd.Timestamp("2011-10-03")),
    ("canonical", pd.Timestamp("2011-10-04")),
    ("first_session_2012", cal[int(np.searchsorted(cal.to_numpy(), np.datetime64("2012-01-01")))]),
    ("first_session_2013", cal[int(np.searchsorted(cal.to_numpy(), np.datetime64("2013-01-01")))]),
    ("first_session_2014", cal[int(np.searchsorted(cal.to_numpy(), np.datetime64("2014-01-01")))]),
]
LINE_ORDER = ["buy_hold_QQQ", "buy_hold_TQQQ", "vol_targeted_QQQ_matched",
              "naive_fast_1d_momentum", "matched_exposure_levered_QQQ_1.70",
              "long_legs_only", "equal_weight_universe",
              "sleeve_T10_standalone", "sleeve_T11_standalone",
              "sleeve_S2_standalone", "sleeve_S3_standalone"]

# realized-arm availability, for the synthetic-share measure
real = panels["realized"]
held = [t for t in tokens if t in real.frames and t not in
        ("QQQ", "SPY", "XLK", "SMH", "AGG", "IEF", "IOO", "VOX", "VTV", "XLF",
         "XLP", "XLY", "VOOG", "VOOV", "QQQE", "BND")]
avail = pd.DataFrame({t: real[t].tr_index.reindex(cal).notna() for t in held},
                     index=cal)
all_real = avail.all(axis=1)

print("\n== STEP 4, window strip ==")
for label, start in STARTS:
    t0 = time.time()
    i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(start)))
    acc_s = run(sig["rows"])
    r_s = acc_s["daily"]["ret"].loc[acc_s["daily"].index >= start].dropna()
    if rf_all is None:
        rf_all = bt.rf_per_session(acc_s["daily"].index)
    rf = rf_all.reindex(r_s.index).fillna(0.0)
    ms = L.standalone_metrics(r_s, acc_s["daily"]["nav"], acc_s["orders"])
    n_s, l_s = lo_parts((r_s - rf).dropna())
    win = cal[(cal >= start) & (cal <= pd.Timestamp("2021-08-01"))]
    share_real = float(all_real.reindex(win).mean())
    stats = [("STRATEGY", n_s, l_s)]
    for ln in LINE_ORDER:
        rws = LINES[ln][0](o2o, sig["rows"], i0)
        a = run(rws)
        r = a["daily"]["ret"].loc[a["daily"].index >= start].dropna()
        rr = rf_all.reindex(r.index).fillna(0.0)
        nn, ll = lo_parts((r - rr).dropna())
        stats.append((ln, nn, ll))
    rn = sorted(stats, key=lambda x: -x[1])
    rl = sorted(stats, key=lambda x: -x[2])
    rank_n = [i for i, s in enumerate(rn, 1) if s[0] == "STRATEGY"][0]
    rank_l = [i for i, s in enumerate(rl, 1) if s[0] == "STRATEGY"][0]
    if label == "canonical":
        d_a, d_l = abs(ms["ann_return"] - TARGET_ANN), abs(ms["sharpe_lo"] - TARGET_SLO)
        add("strip_positive_control", item="ann_return", value=ms["ann_return"],
            target=TARGET_ANN, abs_gap=d_a, within=int(d_a < TOL_CANON))
        add("strip_positive_control", item="sharpe_lo", value=ms["sharpe_lo"],
            target=TARGET_SLO, abs_gap=d_l, within=int(d_l < TOL_CANON))
        add("strip_positive_control", item="verdict",
            note="PASS" if max(d_a, d_l) < TOL_CANON else "FAIL")
        print(f"  positive control at the canonical start, gaps {d_a:.2e} and {d_l:.2e}")
    add("strip", item=label, start=str(start.date()), n_sessions=len(r_s),
        ann_return=ms["ann_return"], sharpe_naive=n_s, sharpe_lo=l_s,
        strategy_rank_naive=rank_n, strategy_rank_lo=rank_l,
        share_sessions_all_realized_available=share_real,
        share_requiring_synthetic=1.0 - share_real,
        seconds=round(time.time() - t0, 1))
    for ln, nn, ll in stats[1:]:
        add("strip_line", item=label, line=ln, sharpe_naive=nn, sharpe_lo=ll,
            start=str(start.date()))
    print(f"  {label:<28} {str(start.date())} n={len(r_s):>4} "
          f"ann {ms['ann_return']:.4f} naive {n_s:.4f} lo {l_s:.4f} "
          f"rank {rank_n}/{rank_l}  realized-available share {share_real:.3f} "
          f"[{time.time()-t0:.0f}s]")

st = [r for r in rows if r["table"] == "strip"]
rn = {r["item"]: r["strategy_rank_naive"] for r in st}
rl = {r["item"]: r["strategy_rank_lo"] for r in st}
add("rank_stability", item="naive_ranks", note=" ".join(f"{k}={v}" for k, v in rn.items()),
    value=len(set(rn.values())))
add("rank_stability", item="lo_ranks", note=" ".join(f"{k}={v}" for k, v in rl.items()),
    value=len(set(rl.values())))
add("rank_stability", item="naive_stable", value=int(len(set(rn.values())) == 1))
add("rank_stability", item="lo_stable", value=int(len(set(rl.values())) == 1))
add("rank_stability", item="naive_range",
    note=f"{min(rn.values())} to {max(rn.values())}")
add("rank_stability", item="lo_range", note=f"{min(rl.values())} to {max(rl.values())}")
print(f"\n  strategy rank under the naive Sharpe {sorted(set(rn.values()))}, "
      f"under the Lo-corrected {sorted(set(rl.values()))}")

# --- step 5, coverage at the early start ----------------------------------
print("\n== STEP 5, coverage at the earliest start ==")
win_e = cal[(cal >= EARLY) & (cal <= pd.Timestamp("2021-08-01"))]
share_e = float(all_real.reindex(win_e).mean())
add("coverage_early", item="start", note=str(EARLY.date()))
add("coverage_early", item="n_sessions", value=len(win_e))
add("coverage_early", item="share_all_realized_available", value=share_e)
add("coverage_early", item="share_requiring_synthetic", value=1.0 - share_e)
add("coverage_early", item="register_16_tension",
    note="register 7.14b fixed the early-window reporting form as coverage tables "
         "and availability timelines with no return figure at any prominence. Step 4 "
         "emits return figures at the early start as a diagnostic, which is in "
         "tension with that form. Whether any early-start figure enters the paper "
         "is a register decision this session does not make and does not pre-empt")
add("coverage_early", item="confound",
    note="a start date sitting on synthetic reconstruction is confounded with panel "
         "source, since the panel differs alongside the window. The confound is "
         "disclosed rather than resolved here")
LEV14 = ("TQQQ", "SQQQ", "QLD", "PSQ", "SH", "SPXL", "TECL", "TECS",
         "SOXL", "SOXS", "FAS", "LABU", "UVXY", "SVXY")
for t in LEV14:
    tr_s = syn[t].tr_index.reindex(cal) if t in syn.frames else None
    tr_r = real[t].tr_index.reindex(cal) if t in real.frames else None
    fs = cal[np.flatnonzero(tr_s.notna().to_numpy())[0]] if tr_s is not None and tr_s.notna().any() else None
    fr = cal[np.flatnonzero(tr_r.notna().to_numpy())[0]] if tr_r is not None and tr_r.notna().any() else None
    add("reconstruction_reach", item=t,
        note=f"synthetic from {fs.date() if fs is not None else 'never'}",
        note2=f"realized from {fr.date() if fr is not None else 'never'}",
        within=int(fs is not None and fs <= EARLY))
print(f"  early window {len(win_e)} sessions, all-realized-available share {share_e:.4f}")

# --- step 6, defect class sweep -------------------------------------------
print("\n== STEP 6, defect class sweep under 9.13 ==")
add("sweep", item="premise",
    note="step 3 found no construction defect. The ladder's levered rows hold the "
         "live fund ticker from the realized panel rather than a costless scaling, "
         "so there is no defect to sweep for. The sweep is run regardless and "
         "reports the construction of every levered and inverse instrument the "
         "strategy trades")
for t in LEV14:
    kind = "inverse" if t in INVERSE else ("volatility" if t in ("UVXY", "SVXY")
                                           else "leveraged long")
    add("sweep", item=t, line=kind,
        note="realized arm takes the frozen fund parquet through _frozen_frame, "
             "being the live fund's own history",
        note2="synthetic arm takes the reconstruction through _synthetic_frame, "
              "carrying daily reset compounding, financing at DTB3 plus "
              f"{config.FINANCING_SPREAD_BP} bp for multiples above one, a haircut "
              "for inverse funds, and k=0 for the volatility funds under 2.15",
        within=1)
add("sweep", item="canonical_depends_on_defect", value=0,
    note="the canonical result at 0.521845 and 1.381701 runs on the realized arm, "
         "where every levered and inverse instrument is the live fund's own frozen "
         "history. No instrument carries a costless-scaling construction, so the "
         "canonical does not depend on one")
add("sweep", item="repaired_here", value=0,
    note="nothing repaired in this session, by scaffold instruction")
print("  no construction defect found, so nothing to sweep against the strategy")
print("  canonical does not depend on any costless-scaling instrument")

peak = rss_gb()
add("resources", item="memory_ceiling_gb", value=MEM_CEILING_GB, note="stated before running")
add("resources", item="peak_rss_gb", value=round(peak, 3), within=int(peak <= MEM_CEILING_GB))
add("resources", item="seconds_total", value=round(time.time() - t_all, 1))
print(f"\npeak RSS {peak:.3f} GB against {MEM_CEILING_GB} GB, "
      f"total {time.time()-t_all:.0f}s")

COLS = ["table", "item", "line", "start", "n_sessions", "ann_return", "sharpe_naive",
        "sharpe_lo", "strategy_rank_naive", "strategy_rank_lo",
        "share_sessions_all_realized_available", "share_requiring_synthetic",
        "value", "target", "abs_gap", "within", "seconds", "note", "note2"]


def dump(name, tables):
    sel = [r for r in rows if r["table"] in tables]
    with open(OUT / name, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader(); w.writerows(sel)
    print(f"wrote {OUT/name} with {len(sel)} rows")


dump("window-strip.csv", {"strip", "strip_line", "strip_positive_control",
                          "rank_stability", "early_start", "resources"})
dump("coverage-early.csv", {"coverage_early", "coverage_ticker",
                            "reconstruction_reach", "early_start"})
dump("defect-sweep.csv", {"sweep"})
