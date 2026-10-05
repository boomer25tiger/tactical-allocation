"""h02. Uniform round-turn cost sweep from January 2012 (slide 14 notes).

Re-runs the session-20 uniform-cost sweep: the tiered slippage and the
opening-auction premium are REPLACED by one uniform round-turn cost of 0, 5,
10, 20, 35 or 50 bp on every instrument, commission arm S and the 5% cap are
unchanged, and NAV compounds from $1M as in the canonical run. The October
2011 rows reproduce outputs/session-20 (1.21 down to 0.86); the January 2012
rows are the ones the deck shows.

Writes outputs/hw2/cost-sweep.csv.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
from common import OUT, WINDOWS, metrics, sl  # noqa: E402
import pandas as pd  # noqa: E402

bt, C = engine.bt, engine.C
GRID = [0, 5, 10, 20, 35, 50]
cl = pd.read_parquet(engine.ROOT / "outputs" / "session-27" / "_combined_line_returns.parquet")
cl.index = pd.DatetimeIndex(cl.index)

rows = []
for bp in GRID:
    engine.SLIP = C.slip_uniform(bp)
    d, *_ = engine.run(1_000_000.0, reset=False)
    r = d["ret"]
    rf = bt.rf_per_session(r.index).fillna(0.0)
    for wn in ("P11", "P12"):
        m = metrics(sl(r, WINDOWS[wn]), rf)
        rows.append({"window": wn, "line": "STRATEGY", "round_turn_bp": bp, **m})
    print(f"{bp} bp done")
engine.SLIP = C.slip_class_premium()
for wn in ("P11", "P12"):
    q = sl(cl["buy_hold_QQQ"], WINDOWS[wn])
    rows.append({"window": wn, "line": "buy_hold_QQQ", "round_turn_bp": "",
                 **metrics(q, bt.rf_per_session(cl.index).fillna(0.0))})
res = pd.DataFrame(rows)
res.to_csv(OUT / "cost-sweep.csv", index=False)
print(res[["window", "line", "round_turn_bp", "sharpe_naive", "ann_return"]].round(4).to_string(index=False))
