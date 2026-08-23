"""Session 28 phase F. The cost sweep over the holdout.

DISCLOSED POST-HOC SENSITIVITY under 9.10, pre-registered at 9.70. The sweep
varies a disclosed sensitivity axis and selects nothing. The cost model is fixed
and no canonical value moves whatever this returns.

The range is read from src/config.py. The stacking rule recorded at session 20
holds, so the uniform round-turn sweep REPLACES the tiered slippage and the
opening-auction premium rather than stacking on them.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s14_common as C                         # noqa: E402
import scripts.s15_lines as L                          # noqa: E402
from src import config                                 # noqa: E402

OUT = ROOT / "outputs" / "session-28"
BOUNDARY = bt.HOLDOUT_BOUNDARY
GRID = list(config.SLIPPAGE_BASE_GRID_BP)
LADDER = ["buy_hold_QQQ", "buy_hold_TQQQ", "vol_targeted_QQQ_matched",
          "naive_fast_1d_momentum", "matched_exposure_levered_QQQ_1.70",
          "long_legs_only", "equal_weight_universe", "sleeve_T10_standalone",
          "sleeve_T11_standalone", "sleeve_S2_standalone", "sleeve_S3_standalone"]
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


add("preregistration", item="range_source", value="src/config.SLIPPAGE_BASE_GRID_BP",
    note=f"read rather than assumed, being {GRID} basis points round turn")
add("preregistration", item="stacking_rule", value="replaces",
    note="the uniform round-turn sweep replaces the tiered slippage and the "
         "opening-auction premium rather than stacking on them, as session 20 "
         "pre-registered. Commission Arm S and the participation cap are unchanged")
add("preregistration", item="disclosed_post_hoc", value=1,
    note="recorded under 9.10 at 9.70. It selects nothing and cannot change the "
         "canonical whatever it returns")

print(f"sweeping {GRID} bp over the holdout")
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
o2o, cap_fn, cal = env["o2o"], env["cap_fn"], env["cal"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))

table = {}
for bp in GRID:
    sf = C.slip_uniform(bp)
    accs = {"STRATEGY": bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                                       slip_fn=sf, cap_fn=cap_fn)}
    for ln in LADDER:
        accs[ln] = bt.run_account(sig["sig"], o2o,
                                  LINES[ln][0](o2o, sig["rows"], i0), C.ANCHOR,
                                  commission_fn=C.ARMS[C.CANONICAL_ARM],
                                  slip_fn=sf, cap_fn=cap_fn)
    vals = {}
    for ln, a in accs.items():
        dd = a["daily"]
        r = dd["ret"].loc[dd.index >= BOUNDARY].dropna()
        m = L.standalone_metrics(r, dd["nav"].loc[dd.index >= BOUNDARY], a["orders"])
        vals[ln] = m
        add("sweep", item=ln, slippage_bp=bp, sharpe_naive=q(m["sharpe_naive"]),
            sharpe_lo=q(m["sharpe_lo"]), ann_return=q(m["ann_return"]),
            ann_turnover=q(m["ann_turnover"]))
    for conv in ("sharpe_naive", "sharpe_lo"):
        order = sorted(vals, key=lambda k: -vals[k][conv])
        add("rank", item="STRATEGY", slippage_bp=bp, convention=conv,
            value=order.index("STRATEGY") + 1, note=f"of {len(order)}")
    table[bp] = vals
    print(f"  {bp:>3} bp  naive {vals['STRATEGY']['sharpe_naive']:.6f}  "
          f"rank {sorted(vals, key=lambda k: -vals[k]['sharpe_naive']).index('STRATEGY')+1}")


def rank_at(bp, conv):
    o = sorted(table[bp], key=lambda k: -table[bp][k][conv])
    return o.index("STRATEGY") + 1


def crossing(target_rank, conv):
    """Linear interpolation in bp between the two swept levels that bracket the
    first level at which the strategy's rank reaches target_rank or worse."""
    rs = [(bp, rank_at(bp, conv)) for bp in GRID]
    for i in range(1, len(rs)):
        if rs[i][1] >= target_rank and rs[i - 1][1] < target_rank:
            b0, r0 = rs[i - 1]
            b1, r1 = rs[i]
            if r1 == r0:
                return b1, "inside"
            return b0 + (b1 - b0) * (target_rank - r0) / (r1 - r0), "inside"
    if rs[0][1] >= target_rank:
        return GRID[0], "inside, already at or worse than the target at the lowest level"
    return float("nan"), "extrapolation, the rank does not reach the target inside the range"


for conv in ("sharpe_naive", "sharpe_lo"):
    for tr in (6, 8):
        bpv, kind = crossing(tr, conv)
        add("rank_crossing", item=f"rank_falls_to_{tr}", convention=conv,
            value=q(bpv) if bpv == bpv else "nan", note=kind)
    # below buy-and-hold QQQ
    hit = None
    for bp in GRID:
        if table[bp]["STRATEGY"][conv] < table[bp]["buy_hold_QQQ"][conv]:
            hit = bp
            break
    add("rank_crossing", item="falls_below_buy_hold_QQQ", convention=conv,
        value=q(hit) if hit is not None else "nan",
        note="inside the swept range" if hit is not None else
             "extrapolation, the strategy leads buy-and-hold QQQ at every swept level")
    for bp in GRID:
        add("gap_to_buy_hold_QQQ", item=conv, slippage_bp=bp,
            value=q(table[bp]["STRATEGY"][conv] - table[bp]["buy_hold_QQQ"][conv]))

# ---- the primary window, from the committed file --------------------------------
PF = "outputs/session-20/rebuilt/cost-sweep-designated.csv"
F1 = [r for r in csv.DictReader(open(ROOT / "outputs/session-21/reads.csv"))
      if r["table"] == "F1" and "|" in r["item"]]
for r in F1:
    ln, met = r["item"].split("|")
    add("primary_crossing", item=ln, convention=met, value=r["value"],
        note=("inside the swept range" if r["value"] != "nan"
              else "no crossing inside the swept range, so any figure would be an "
                   "extrapolation") + f", from outputs/session-21/reads.csv")
ins = sum(1 for r in F1 if r["value"] != "nan")
add("primary_summary", item="crossings_inside_the_swept_range", value=ins,
    note=f"of {len(F1)} across the eleven lines and both conventions, the rest being "
         f"extrapolations, at {PF} and outputs/session-21/reads.csv")

fn = ["table", "item", "slippage_bp", "convention", "value", "sharpe_naive",
      "sharpe_lo", "ann_return", "ann_turnover", "note"]
with open(OUT / "holdout-cost-sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote holdout-cost-sweep.csv, {len(rows)} rows")
for r in rows:
    if r["table"] == "rank_crossing":
        print(f"  {r['convention']:14s} {r['item']:28s} {r['value']}  {r['note'][:60]}")
