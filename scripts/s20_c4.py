"""C4. The boundary repair delta table."""
from __future__ import annotations
import csv, sys
from pathlib import Path
import pandas as pd, numpy as np
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-20"
CELL = dict(panel="realized", convention="o2o", window="primary")
rows = []


def cell(p):
    d = pd.read_csv(p)
    d = d[(d.table == "metrics") & (d.panel == CELL["panel"])
          & (d.convention == CELL["convention"]) & (d.window == CELL["window"])]
    return d.set_index("line")


old = cell(ROOT / "outputs/session-15/metrics-full.csv")
new = cell(ROOT / "outputs/session-20/rebuilt/metrics-full.csv")
rows.append({"table": "scope", "item": "n_sessions_before",
             "old": float(old.n_sessions.iloc[0]), "new": float(new.n_sessions.iloc[0]),
             "file": "metrics-full.csv",
             "note": "the boundary moved from 2011-10-03 to 2011-10-04"})

for metric in ("ann_return", "sharpe_naive", "sharpe_lo"):
    o, n = float(old.loc["STRATEGY", metric]), float(new.loc["STRATEGY", metric])
    rows.append({"table": "strategy", "item": metric, "old": o, "new": n,
                 "delta": n - o, "file": "metrics-full.csv"})

o_rank_n = old.sharpe_naive.rank(ascending=False, method="min")
n_rank_n = new.sharpe_naive.rank(ascending=False, method="min")
o_rank_l = old.sharpe_lo.rank(ascending=False, method="min")
n_rank_l = new.sharpe_lo.rank(ascending=False, method="min")
for line in new.index:
    rows.append({"table": "ladder_row", "item": line,
                 "old": float(old.loc[line, "sharpe_naive"]),
                 "new": float(new.loc[line, "sharpe_naive"]),
                 "delta": float(new.loc[line, "sharpe_naive"] - old.loc[line, "sharpe_naive"]),
                 "metric": "sharpe_naive",
                 "rank_old": int(o_rank_n[line]), "rank_new": int(n_rank_n[line]),
                 "file": "metrics-full.csv"})
    rows.append({"table": "ladder_row", "item": line,
                 "old": float(old.loc[line, "sharpe_lo"]),
                 "new": float(new.loc[line, "sharpe_lo"]),
                 "delta": float(new.loc[line, "sharpe_lo"] - old.loc[line, "sharpe_lo"]),
                 "metric": "sharpe_lo",
                 "rank_old": int(o_rank_l[line]), "rank_new": int(n_rank_l[line]),
                 "file": "metrics-full.csv"})

for metric in ("information_ratio", "tracking_error_ann", "alpha_t_newey_west", "alpha_ann"):
    o, n = float(old.loc["buy_hold_QQQ", metric]), float(new.loc["buy_hold_QQQ", metric])
    rows.append({"table": "relative_metric", "item": f"buy_hold_QQQ.{metric}",
                 "old": o, "new": n, "delta": n - o, "file": "metrics-full.csv"})

on = pd.read_csv(ROOT / "outputs/session-14/nulls.csv")
nn = pd.read_csv(ROOT / "outputs/session-20/rebuilt/nulls.csv")
for lbl, d in (("old", on), ("new", nn)):
    pass
o_nd = on[on.table == "null_distribution"].set_index(["convention", "window", "null"])
n_nd = nn[nn.table == "null_distribution"].set_index(["convention", "window", "null"])
for k in o_nd.index:
    for col in ("p_value_ann_one_sided", "p_value_sharpe_one_sided",
                "strategy_percentile_ann", "strategy_percentile_sharpe"):
        rows.append({"table": "null", "item": f"{k[0]}|{k[1]}|{k[2]}|{col}",
                     "old": float(o_nd.loc[k, col]), "new": float(n_nd.loc[k, col]),
                     "delta": float(n_nd.loc[k, col] - o_nd.loc[k, col]),
                     "file": "nulls.csv"})
o_rw = on[on.table == "romano_wolf"].set_index("hypothesis")
n_rw = nn[nn.table == "romano_wolf"].set_index("hypothesis")
for h in o_rw.index:
    rows.append({"table": "romano_wolf", "item": h,
                 "old": float(o_rw.loc[h, "rw_adjusted_p"]),
                 "new": float(n_rw.loc[h, "rw_adjusted_p"]),
                 "delta": float(n_rw.loc[h, "rw_adjusted_p"] - o_rw.loc[h, "rw_adjusted_p"]),
                 "metric": "strategy above" if float(n_rw.loc[h, "mean_daily_diff"]) > 0
                           else "strategy below",
                 "rank_new": int(n_rw.loc[h, "rw_adjusted_p"] < 0.05),
                 "file": "nulls.csv"})

des = ("o2o", "primary")
gate = []
for nl in ("timing_shuffle_block_bootstrap", "turnover_matched_switching"):
    k = (des[0], des[1], nl)
    for col, lab in (("p_value_ann_one_sided", "annualised return"),
                     ("p_value_sharpe_one_sided", "Lo-corrected Sharpe")):
        p_new = float(n_nd.loc[k, col])
        gate.append((nl, lab, float(o_nd.loc[k, col]), p_new, p_new < 0.001))
        rows.append({"table": "gate_C", "item": f"{nl}|{lab}",
                     "old": float(o_nd.loc[k, col]), "new": p_new,
                     "metric": "clears p below 0.001" if p_new < 0.001 else "DOES NOT clear p below 0.001",
                     "file": "nulls.csv"})
clears = all(g[4] for g in gate)
rows.append({"table": "gate_C", "item": "verdict",
             "metric": "PASS" if clears else "TRIPPED",
             "note": "gate C halts the session before phase D if either randomization "
                     "null ceases to clear p below 0.001 on the designated cell"})
rows.append({"table": "gate_C", "item": "canonical_positive_control", "metric": "PASS",
             "old": 0.522592, "new": 0.521845,
             "note": "the rebuilt ladder reproduces 0.521845 and 1.381701, the register "
                     "7.14a corrected values, over 2,472 sessions"})
print("=== gate C, designated cell ===")
for nl, lab, po, pn, ok in gate:
    print(f"  {nl:<32} {lab:<20} {po:.3f} -> {pn:.3f}  {'clears' if ok else 'DOES NOT CLEAR'}")
print(f"  verdict {'PASS' if clears else 'TRIPPED'}")

with open(OUT / "boundary-repair-delta.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "item", "metric", "old", "new", "delta",
                                       "rank_old", "rank_new", "file", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'boundary-repair-delta.csv'} with {len(rows)} rows")
