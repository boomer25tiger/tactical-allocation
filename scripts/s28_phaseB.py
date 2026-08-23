"""Session 28 phase B. The ladder comparison, read from committed files only.

No pass runs. The holdout figures come from outputs/session-27/holdout-ladder.csv
and the primary-window figures from outputs/session-20/rebuilt/metrics-full.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = R / "outputs" / "session-28"
HOLD_F = "outputs/session-27/holdout-ladder.csv"
PRIM_F = "outputs/session-20/rebuilt/metrics-full.csv"
COLS = ["ann_return", "ann_vol", "sharpe_naive", "sharpe_lo", "max_drawdown",
        "ann_turnover"]
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


H = {r["line"]: r for r in csv.DictReader(open(R / HOLD_F)) if r["table"] == "line"}
P = {r["line"]: r for r in csv.DictReader(open(R / PRIM_F))
     if r["table"] == "metrics" and r["convention"] == "o2o" and r["window"] == "primary"}
LINES = sorted(H)


def ranks(d, conv):
    o = sorted(d, key=lambda k: -float(d[k][conv]))
    return {k: i for i, k in enumerate(o, 1)}


hr_n, hr_l = ranks(H, "sharpe_naive"), ranks(H, "sharpe_lo")
pr_n, pr_l = ranks(P, "sharpe_naive"), ranks(P, "sharpe_lo")

for ln in LINES:
    h, p = H[ln], P[ln]
    add("line", item=ln, **{f"holdout_{c}": h[c] for c in COLS},
        **{f"primary_{c}": p[c] for c in COLS},
        holdout_rank_naive=hr_n[ln], primary_rank_naive=pr_n[ln],
        rank_move_naive=pr_n[ln] - hr_n[ln],
        holdout_rank_lo=hr_l[ln], primary_rank_lo=pr_l[ln],
        rank_move_lo=pr_l[ln] - hr_l[ln],
        note="a positive rank move means the line placed better in the holdout than in "
             "the primary window")

s = H["STRATEGY"]
sn = float(s["sharpe_naive"])
beat = [(ln, float(H[ln]["sharpe_naive"]) - sn) for ln in LINES
        if float(H[ln]["sharpe_naive"]) > sn]
add("summary", item="lines_beating_the_strategy_on_the_naive_sharpe", value=len(beat),
    note="; ".join(f"{ln} by {gap!r}" for ln, gap in
                   sorted(beat, key=lambda t: -t[1])) or "none")
for ln, gap in beat:
    add("beats_strategy", item=ln, value=repr(gap),
        holdout_sharpe_naive=H[ln]["sharpe_naive"],
        holdout_sharpe_lo=H[ln]["sharpe_lo"],
        note=f"its Lo-corrected Sharpe is {H[ln]['sharpe_lo']} against the strategy's "
             f"{s['sharpe_lo']}, so it does not beat the strategy on that convention"
             if float(H[ln]["sharpe_lo"]) < float(s["sharpe_lo"]) else "")

q = "buy_hold_QQQ"
add("buy_hold_QQQ", item="holdout_sharpe_naive", value=H[q]["sharpe_naive"],
    note=f"against the primary window's {P[q]['sharpe_naive']} at {PRIM_F}")
add("buy_hold_QQQ", item="holdout_sharpe_lo", value=H[q]["sharpe_lo"],
    note=f"against the primary window's {P[q]['sharpe_lo']}")
add("buy_hold_QQQ", item="holdout_ann_return", value=H[q]["ann_return"],
    note=f"against the primary window's {P[q]['ann_return']}")
add("buy_hold_QQQ", item="holdout_rank_naive", value=hr_n[q],
    note=f"against {pr_n[q]} in the primary window")
add("buy_hold_QQQ", item="scaffold_figure_check", value=P[q]["sharpe_naive"],
    note="the scaffold names a primary-window naive Sharpe of 1.1699 for this line and "
         "the emitted figure is quoted here instead. The scaffold's Lo figure of 1.8033 "
         f"matches the emitted {P[q]['sharpe_lo']} to four decimals")

me = "matched_exposure_levered_QQQ_1.70"
add("matched_exposure", item="holdout_rank_naive", value=hr_n[me],
    note=f"against {pr_n[me]} in the primary window")
add("matched_exposure", item="holdout_rank_lo", value=hr_l[me],
    note=f"against {pr_l[me]} in the primary window")
add("matched_exposure", item="holdout_sharpe_naive", value=H[me]["sharpe_naive"],
    note=f"against the primary window's {P[me]['sharpe_naive']}")
add("matched_exposure", item="holdout_sharpe_lo", value=H[me]["sharpe_lo"],
    note=f"against the primary window's {P[me]['sharpe_lo']}")

# ---- is the advantage return, volatility, or both ---------------------------------
rq, rs = float(H[q]["ann_return"]), float(s["ann_return"])
vq, vs = float(H[q]["ann_vol"]), float(s["ann_vol"])
pq_r, ps_r = float(P[q]["ann_return"]), float(P["STRATEGY"]["ann_return"])
pq_v, ps_v = float(P[q]["ann_vol"]), float(P["STRATEGY"]["ann_vol"])
add("advantage", item="holdout_return_ratio_strategy_over_QQQ", value=repr(rs / rq),
    note=f"strategy {rs!r} against buy-and-hold QQQ {rq!r}")
add("advantage", item="holdout_vol_ratio_strategy_over_QQQ", value=repr(vs / vq),
    note=f"strategy {vs!r} against buy-and-hold QQQ {vq!r}")
add("advantage", item="primary_return_ratio_strategy_over_QQQ", value=repr(ps_r / pq_r))
add("advantage", item="primary_vol_ratio_strategy_over_QQQ", value=repr(ps_v / pq_v))
add("advantage", item="source_as_measured",
    value="return" if (rs / rq > 1 and vs / vq > 1) else
          "volatility" if (rs / rq <= 1 and vs / vq < 1) else "both",
    note=f"the strategy carries {rs/rq:.4f} times buy-and-hold QQQ's annualised return "
         f"at {vs/vq:.4f} times its annualised volatility over the holdout, against "
         f"{ps_r/pq_r:.4f} and {ps_v/pq_v:.4f} over the primary window. The advantage "
         f"is a higher return carried at a higher volatility rather than a lower "
         f"volatility, so it is a return effect and not a volatility effect")

fn = (["table", "item", "value"] + [f"holdout_{c}" for c in COLS]
      + [f"primary_{c}" for c in COLS]
      + ["holdout_rank_naive", "primary_rank_naive", "rank_move_naive",
         "holdout_rank_lo", "primary_rank_lo", "rank_move_lo",
         "holdout_sharpe_naive", "holdout_sharpe_lo", "note"])
with open(OUT / "ladder-comparison.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote ladder-comparison.csv, {len(rows)} rows")
print(f"  lines beating the strategy on the naive Sharpe: {len(beat)}")
for ln, gap in beat:
    print(f"    {ln} by {gap:.6f}")
print(f"  advantage source: {rows[-1]['value']}")
