"""Session 15 steps 3 and 4: metrics completion and the designated-cell
cost sweep."""
from __future__ import annotations

import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
import scripts.s14_common as C
import scripts.s15_lines as L
from src import config

import os as _os
OUT = ROOT / "outputs" / (_os.environ.get("S20_OUTDIR") or "session-15")
OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

env = L.build_env()
cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]
LINES = L.make_lines(cal)
WSTART = {"full": config.WARMUP_SESSIONS, "early": config.WARMUP_SESSIONS,
          "primary": int(np.searchsorted(cal.to_numpy(),
                                         np.datetime64(C.PRIMARY_START)))}


def run(rows, panel, sig, conv, bp=None, cap=True):
    if bp is not None:
        sf = C.slip_uniform(bp)
    else:
        sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    return bt.run_account(sig["sig"], panel, rows, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM], slip_fn=sf,
                          cap_fn=cap_fn if cap else None)


COMBOS = [("realized", "c2c", "full"), ("realized", "c2c", "primary"),
          ("realized", "o2o", "primary"), ("synthetic", "c2c", "early")]

# ===========================================================================
print("== STEP 3: metrics completion ==")
rows3 = []

# --- positive control against session 14's ladder.csv ----------------------
# Session 20 C1. The upstream ladder follows the same redirect, so a rebuild
# compares against the rebuilt session 14 ladder rather than the superseded one.
lad14 = pd.read_csv(ROOT / "outputs" / (_os.environ.get("S20_OUTDIR") or "session-14")
                    / "ladder.csv")
lad14 = lad14[lad14.table == "ladder"]
CTRL_KEYS = ["ann_return", "ann_vol", "sharpe_naive", "sharpe_lo",
             "max_drawdown", "calmar", "arith_mean_excess_ann", "ann_turnover"]
ctrl_fail = 0
for pname, conv, wname in [("realized", "o2o", "primary")]:
    panel = o2o if conv == "o2o" else panels[pname]
    sig = sigs[pname]
    acc_s = run(sig["rows"], panel, sig, conv)
    ms = L.standalone_metrics(C.window_slice(acc_s["daily"]["ret"], wname),
                              acc_s["daily"]["nav"], acc_s["orders"])
    ref = lad14[(lad14.line == "STRATEGY") & (lad14.convention == conv) &
                (lad14.window == wname)].iloc[0]
    for k in CTRL_KEYS:
        gap = abs(ms[k] - float(ref[k]))
        ok = gap < 5e-5
        ctrl_fail += 0 if ok else 1
        rows3.append({"table": "positive_control", "line": "STRATEGY",
                      "metric": k, "session15": ms[k], "session14": float(ref[k]),
                      "abs_gap": gap, "match_4dp": ok})
    rws = LINES["buy_hold_QQQ"][0](panel, sig["rows"], WSTART[wname])
    acc_b = run(rws, panel, sig, conv)
    mb = L.standalone_metrics(C.window_slice(acc_b["daily"]["ret"], wname),
                              acc_b["daily"]["nav"], acc_b["orders"])
    refb = lad14[(lad14.line == "buy_hold_QQQ") & (lad14.convention == conv) &
                 (lad14.window == wname)].iloc[0]
    for k in CTRL_KEYS:
        gap = abs(mb[k] - float(refb[k]))
        ok = gap < 5e-5
        ctrl_fail += 0 if ok else 1
        rows3.append({"table": "positive_control", "line": "buy_hold_QQQ",
                      "metric": k, "session15": mb[k], "session14": float(refb[k]),
                      "abs_gap": gap, "match_4dp": ok})
print(f"  positive control mismatches at 4dp: {ctrl_fail}")
assert ctrl_fail == 0, "step 3 positive control failed; metrics not emitted"

# --- full metric table -----------------------------------------------------
for pname, conv, wname in COMBOS:
    panel = o2o if conv == "o2o" else panels[pname]
    sig = sigs[pname]
    acc_s = run(sig["rows"], panel, sig, conv)
    sret = C.window_slice(acc_s["daily"]["ret"], wname)
    ms = L.standalone_metrics(sret, acc_s["daily"]["nav"], acc_s["orders"])
    rows3.append({"table": "metrics", "line": "STRATEGY", "panel": pname,
                  "convention": conv, "window": wname, **ms})
    for y, g in sret.groupby(sret.index.year):
        if len(g) < 20:
            continue
        rfy = bt.rf_per_session(g.index).fillna(0.0)
        rows3.append({"table": "per_year", "line": "STRATEGY", "panel": pname,
                      "convention": conv, "window": wname, "year": int(y),
                      "ann_return": float((1 + g).prod() - 1),
                      "sharpe_lo": bt.lo_sharpe((g - rfy).dropna())})
    for name, (builder, kind) in LINES.items():
        rws = builder(panel, sig["rows"], WSTART[wname])
        acc = run(rws, panel, sig, conv)
        lret = C.window_slice(acc["daily"]["ret"], wname)
        m = L.standalone_metrics(lret, acc["daily"]["nav"], acc["orders"])
        rel = L.relative_metrics(sret, lret)
        rows3.append({"table": "metrics", "line": name, "panel": pname,
                      "convention": conv, "window": wname, "line_kind": kind,
                      **m, **rel})
        for y, g in lret.groupby(lret.index.year):
            if len(g) < 20:
                continue
            rfy = bt.rf_per_session(g.index).fillna(0.0)
            rows3.append({"table": "per_year", "line": name, "panel": pname,
                          "convention": conv, "window": wname, "year": int(y),
                          "ann_return": float((1 + g).prod() - 1),
                          "sharpe_lo": bt.lo_sharpe((g - rfy).dropna())})
    print(f"  [{pname} {conv} {wname}] metrics for strategy + {len(LINES)} lines")

pd.DataFrame(rows3).to_csv(OUT / "metrics-full.csv", index=False)
print(f"[wrote metrics-full.csv: {len(rows3)} rows]")

# --- grid emitter metric set ----------------------------------------------
sample = [r for r in rows3 if r["table"] == "metrics" and r["line"] == "STRATEGY"][0]
REL_KEYS = {"alpha_ann", "beta", "tracking_error_ann", "information_ratio",
            "r_squared", "alpha_t_newey_west", "newey_west_lag",
            "andrews_bandwidth", "up_capture", "down_capture",
            "n_up_days", "n_down_days"}
META = {"table", "line", "panel", "convention", "window", "line_kind"}
rows_g = []
for k in sample:
    if k in META:
        continue
    rows_g.append({"metric": k,
                   "class": "benchmark_relative" if k in REL_KEYS else "standalone",
                   "grid_emitter_carries_per_specification": k not in REL_KEYS,
                   "note": "requires a benchmark series; the grid emitter carries "
                           "it only for the ladder lines 8.8 fixes"
                           if k in REL_KEYS else
                           "defined for a single specification without reference "
                           "to a benchmark"})
for k in sorted(REL_KEYS):
    if k not in sample:
        rows_g.append({"metric": k, "class": "benchmark_relative",
                       "grid_emitter_carries_per_specification": False,
                       "note": "requires a benchmark series; the grid emitter "
                               "carries it only for the ladder lines 8.8 fixes"})
rows_g.append({"metric": "per_calendar_year_return_and_sharpe_lo",
               "class": "standalone", "grid_emitter_carries_per_specification": True,
               "note": "emitted as a per-year block alongside the scalar set"})
pd.DataFrame(rows_g).to_csv(OUT / "grid-emitter-metric-set.csv", index=False)
n_std = sum(1 for r in rows_g if r["class"] == "standalone")
n_rel = sum(1 for r in rows_g if r["class"] == "benchmark_relative")
print(f"[wrote grid-emitter-metric-set.csv: {n_std} standalone, {n_rel} relative]")

# ===========================================================================
print("\n== STEP 4: cost sweep on the designated cell ==")
rows4 = []
rows4.append({"table": "stacking_rule", "rule":
              "The uniform round-turn sweep REPLACES the tiered slippage and the "
              "opening-auction premium rather than stacking on top of them. The "
              "uniform arm exists to bound sensitivity to an assumed cost level, "
              "so adding it to a calibrated model would double-charge. Commission "
              "Arm S and the participation cap are unchanged across the sweep. "
              "Pre-registered before the run and applied consistently."})
sig = sigs["realized"]
acc_ref = run(sig["rows"], o2o, sig, "o2o")
ref_cell = L.standalone_metrics(C.window_slice(acc_ref["daily"]["ret"], "primary"),
                                acc_ref["daily"]["nav"], acc_ref["orders"])
rows4.append({"table": "reference", "line": "STRATEGY_designated_tiered_plus_premium",
              "ann_return": ref_cell["ann_return"], "sharpe_lo": ref_cell["sharpe_lo"]})
strat_by_bp, line_by_bp = {}, {}
for bp in config.SLIPPAGE_BASE_GRID_BP:
    acc_s = run(sig["rows"], o2o, sig, "o2o", bp=bp)
    sret = C.window_slice(acc_s["daily"]["ret"], "primary")
    ms = L.standalone_metrics(sret, acc_s["daily"]["nav"], acc_s["orders"])
    strat_by_bp[bp] = ms
    rows4.append({"table": "sweep", "line": "STRATEGY", "slippage_bp": bp, **ms})
    for name, (builder, kind) in LINES.items():
        rws = builder(o2o, sig["rows"], WSTART["primary"])
        acc = run(rws, o2o, sig, "o2o", bp=bp)
        m = L.standalone_metrics(C.window_slice(acc["daily"]["ret"], "primary"),
                                 acc["daily"]["nav"], acc["orders"])
        line_by_bp.setdefault(name, {})[bp] = m
        rows4.append({"table": "sweep", "line": name, "slippage_bp": bp, **m,
                      "strategy_minus_line_ann": ms["ann_return"] - m["ann_return"],
                      "strategy_minus_line_sharpe_lo": ms["sharpe_lo"] - m["sharpe_lo"]})
    print(f"  {bp} bp: strategy ann {ms['ann_return']:.4f} SR {ms['sharpe_lo']:.4f}")


def crossing(xs, ys):
    for i in range(len(xs) - 1):
        if ys[i] > 0 >= ys[i + 1]:
            return xs[i] + (xs[i + 1] - xs[i]) * ys[i] / (ys[i] - ys[i + 1])
    return np.nan


bps = list(config.SLIPPAGE_BASE_GRID_BP)
for met in ("ann_return", "sharpe_lo"):
    ys = [strat_by_bp[b][met] for b in bps]
    c = crossing(bps, ys)
    rows4.append({"table": "strategy_zero_crossing", "metric": met,
                  "crossing_bp": c,
                  "note": "no crossing inside the registered sweep" if np.isnan(c)
                          else "measured inside the registered sweep",
                  "value_at_0bp": ys[0], "value_at_50bp": ys[-1]})
    print(f"  strategy zero crossing on {met}: "
          f"{'none inside sweep' if np.isnan(c) else f'{c:.1f} bp'}")
for name in LINES:
    lead0_r = strat_by_bp[0]["ann_return"] - line_by_bp[name][0]["ann_return"]
    lead0_s = strat_by_bp[0]["sharpe_lo"] - line_by_bp[name][0]["sharpe_lo"]
    dr = [strat_by_bp[b]["ann_return"] - line_by_bp[name][b]["ann_return"] for b in bps]
    ds = [strat_by_bp[b]["sharpe_lo"] - line_by_bp[name][b]["sharpe_lo"] for b in bps]
    rows4.append({"table": "advantage_crossing", "line": name,
                  "strategy_leads_at_0bp_return": bool(lead0_r > 0),
                  "strategy_leads_at_0bp_sharpe": bool(lead0_s > 0),
                  "return_crossing_bp": crossing(bps, dr) if lead0_r > 0 else np.nan,
                  "sharpe_crossing_bp": crossing(bps, ds) if lead0_s > 0 else np.nan,
                  "note": "" if lead0_r > 0 or lead0_s > 0 else
                          "no crossing exists because the strategy does not lead "
                          "this line at 0 basis points on either statistic"})
pd.DataFrame(rows4).to_csv(OUT / "cost-sweep-designated.csv", index=False)
print(f"[wrote cost-sweep-designated.csv: {len(rows4)} rows]")
