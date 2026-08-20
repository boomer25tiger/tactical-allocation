"""Session 19.5 step 0: locate the ladder artifact and match prose against it."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-19_5"
OUT.mkdir(parents=True, exist_ok=True)
LADDER = ROOT / "outputs" / "session-15" / "metrics-full.csv"
NULLS = ROOT / "outputs" / "session-14" / "nulls.csv"
rows = []

d = pd.read_csv(LADDER)
m = d[(d.table == "metrics") & (d.panel == "realized")
      & (d.convention == "o2o") & (d.window == "primary")].copy()
m = m.sort_values("sharpe_lo", ascending=False).reset_index(drop=True)

rows.append({"table": "artifact", "item": "path",
             "text": str(LADDER.relative_to(ROOT))})
rows.append({"table": "artifact", "item": "written_by",
             "text": "session 15, the ladder-emitting session; register 8.11 names this "
                     "file as the metric values"})
rows.append({"table": "artifact", "item": "prior_partial",
             "text": "outputs/session-14/ladder.csv carries 14 lines including the "
                     "intraday-only and overnight-only hold universes, which the "
                     "twelve-row ladder does not"})
rows.append({"table": "artifact", "item": "n_columns", "value": len(d.columns)})
rows.append({"table": "artifact", "item": "n_rows_file", "value": len(d)})
rows.append({"table": "artifact", "item": "n_rows_designated_cell", "value": len(m),
             "text": "realized panel, open-to-open, primary window"})
rows.append({"table": "artifact", "item": "twelve_rows_exist",
             "value": int(len(m) == 12)})
rows.append({"table": "artifact", "item": "columns",
             "text": " ".join(map(str, d.columns))})

print(f"artifact {LADDER.relative_to(ROOT)}")
print(f"  written by session 15, {len(d)} rows, {len(d.columns)} columns")
print(f"  designated cell carries {len(m)} rows, twelve rows exist: {len(m) == 12}")

PROSE = {"buy_hold_TQQQ": 1.794, "buy_hold_QQQ": 1.792,
         "matched_exposure_levered_QQQ_1.70": 1.790, "long_legs_only": 1.461,
         "vol_targeted_QQQ_matched": 1.435, "STRATEGY": 1.385}
print("\n  rank  line                                  sharpe_lo  sharpe_naive  prose  gap")
disagree = 0
for i, r in m.iterrows():
    pr = PROSE.get(r.line)
    gap = abs(round(r.sharpe_lo, 3) - pr) if pr is not None else None
    ok = pr is None or gap < 5e-4
    if pr is not None and not ok:
        disagree += 1
    rows.append({"table": "ladder_row", "item": r.line, "rank": i + 1,
                 "value": r.sharpe_lo, "sharpe_naive": r.sharpe_naive,
                 "ann_return": r.ann_return, "ann_vol": r.ann_vol,
                 "n_sessions": r.n_sessions,
                 "prose_figure": pr if pr is not None else "",
                 "prose_matches_csv": "" if pr is None else int(ok)})
    print(f"  {i+1:>4}  {r.line:<36} {r.sharpe_lo:>9.4f}  {r.sharpe_naive:>12.4f}  "
          f"{'' if pr is None else f'{pr:.3f}'}  "
          f"{'' if gap is None else f'{gap:.5f}'}")
rows.append({"table": "prose_check", "item": "figures_checked", "value": len(PROSE)})
rows.append({"table": "prose_check", "item": "disagreements", "value": disagree,
             "text": "rounded to three decimals, the precision the prose carries"})
print(f"\n  prose figures checked {len(PROSE)}, disagreements {disagree}")

# the strategy row against the corrected boundary
strat = m[m.line == "STRATEGY"].iloc[0]
rows.append({"table": "boundary", "item": "ladder_strategy_sharpe_lo",
             "value": float(strat.sharpe_lo)})
rows.append({"table": "boundary", "item": "ladder_strategy_ann_return",
             "value": float(strat.ann_return)})
rows.append({"table": "boundary", "item": "ladder_strategy_n_sessions",
             "value": float(strat.n_sessions)})
rows.append({"table": "boundary", "item": "register_7_14a_corrected_sharpe_lo",
             "value": 1.3817})
rows.append({"table": "boundary", "item": "register_7_14a_corrected_ann_return",
             "value": 0.5218})
rows.append({"table": "boundary", "item": "ladder_on_corrected_boundary",
             "value": int(abs(float(strat.sharpe_lo) - 1.3817) < 5e-4),
             "text": "the ladder's STRATEGY row carries the pre-correction 2011-10-03 "
                     "figures, being 1.3846 and 0.5226, which register 7.14a superseded "
                     "with 1.3817 and 0.5218 on the 2011-10-04 start. Every ladder row "
                     "is therefore on the superseded window"})
print(f"\n  ladder STRATEGY sharpe_lo {strat.sharpe_lo:.4f} against the register's "
      f"corrected 1.3817")
print(f"  ladder STRATEGY n_sessions {strat.n_sessions:.0f}")

# Romano-Wolf with signs
n = pd.read_csv(NULLS)
rw = n[n.table == "romano_wolf"]
print(f"\n  Romano-Wolf, family of {int(rw.family_size.iloc[0])}, one-sided")
for _, r in rw.sort_values("rw_adjusted_p").iterrows():
    sign = "strategy above" if r.mean_daily_diff > 0 else "strategy below"
    rows.append({"table": "romano_wolf", "item": r.hypothesis,
                 "value": float(r.rw_adjusted_p),
                 "mean_daily_diff": float(r.mean_daily_diff),
                 "t_stat": float(r.t_stat),
                 "sign": sign,
                 "below_0_05": int(float(r.rw_adjusted_p) < 0.05),
                 "text": r.note if isinstance(r.note, str) else ""})
    print(f"    p={r.rw_adjusted_p:.3f}  t={r.t_stat:+.3f}  {sign:<14} "
          f"{r.hypothesis}")
sig = rw[rw.rw_adjusted_p < 0.05]
rows.append({"table": "romano_wolf_summary", "item": "comparisons", "value": len(rw)})
rows.append({"table": "romano_wolf_summary", "item": "below_0_05", "value": len(sig)})
for _, r in sig.iterrows():
    rows.append({"table": "romano_wolf_summary", "item": "significant_hypothesis",
                 "text": r.hypothesis, "value": float(r.rw_adjusted_p),
                 "sign": "strategy above" if r.mean_daily_diff > 0 else "strategy below",
                 "mean_daily_diff": float(r.mean_daily_diff)})
print(f"\n  {len(sig)} of {len(rw)} below 0.05, being "
      f"{', '.join(sig.hypothesis)} with the strategy "
      f"{'above' if sig.mean_daily_diff.iloc[0] > 0 else 'below'}")

COLS = ["table", "item", "value", "rank", "sharpe_naive", "ann_return", "ann_vol",
        "n_sessions", "prose_figure", "prose_matches_csv", "mean_daily_diff",
        "t_stat", "sign", "below_0_05", "text"]
with open(OUT / "ladder-source.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"\nwrote {OUT/'ladder-source.csv'} with {len(rows)} rows")
