"""HYPOTHETICAL side run requested in conversation after session 13 halted.

Sample start moved to 2011-10-01 (Q4 2011, the date from which the
realized arm fills every order). Decision 2.9 is NOT changed: the
registered sample start remains 2007-01-01 and this run closes nothing.
Everything else is identical to the canonical session 13 pipeline:
warm-up 210 sessions from the new load start, holdout truncation at
2021-07-31 inside the loader, both 2.8 arms, the full slippage grid, the
provisional operating values, and the lookahead check.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.s13_backtest as bt
from src import config

OUT = ROOT / "outputs" / "session-13" / "hypothetical-q4-2011"
OUT.mkdir(parents=True, exist_ok=True)

# The single change: load window starts Q4 2011.
bt.SAMPLE_START = pd.Timestamp("2011-10-01")

panels = {a: bt.load_arm_panel(a) for a in ("synthetic", "realized")}
for a, p in panels.items():
    ok, mx = bt.assert_holdout(p)
    print(f"holdout [{a}]: PASS max {mx.date()}")
cal = panels["synthetic"]["SPY"].index
print(f"calendar: {cal[0].date()} .. {cal[-1].date()}, {len(cal)} sessions; "
      f"first signal {cal[config.WARMUP_SESSIONS].date()}, "
      f"first fill {cal[config.WARMUP_SESSIONS + 1].date()}")

rows = []
uf_notes = {}
sigs = {}
for a in ("synthetic", "realized"):
    s = bt.ArmSignals(panels[a], cal)
    sigs[a] = {"sig": s, **bt.run_signals(s)}
    n_tr = sum(1 for r in sigs[a]["rows"] if r["changed"])
    post_raises = [e for e in sigs[a]["raises"]
                   if cal.get_indexer([e["date"]])[0] >= config.WARMUP_SESSIONS]
    print(f"[{a}] transitions {n_tr} "
          f"({n_tr / ((len(cal) - config.WARMUP_SESSIONS) / 252):.1f}/yr), "
          f"post-warm-up raises {len(post_raises)}")
    for bp in config.SLIPPAGE_BASE_GRID_BP:
        acc = bt.run_account(s, panels[a], sigs[a]["rows"], bp)
        m = bt.headline_metrics(acc["daily"], acc["orders"])
        rows.append({"arm": a, "slippage_bp": bp, **m})
        if bp == 10:
            uf = acc["unavailable_fills"]
            uf_notes[a] = (uf.groupby("ticker").agg(
                n=("date", "size"), first=("date", "min"), last=("date", "max"))
                if len(uf) else None)
            acc["daily"][["nav", "cash", "transition", "ret"]].to_csv(
                OUT / f"daily-nav-{a}-10bp.csv")
            if a == "synthetic":
                r_ = acc["daily"]["ret"].dropna()
                yearly = pd.DataFrame(
                    {"total_return": r_.groupby(r_.index.year)
                     .apply(lambda g: (1 + g).prod() - 1.0)})
                d2 = bt.run_account(s, panels[a], sigs[a]["rows"], bp, fill_lag=2)
                lag_m = bt.headline_metrics(d2["daily"], d2["orders"])

hl = pd.DataFrame(rows)
hl.to_csv(OUT / "headline-hypothetical.csv", index=False)
print()
print(hl[["arm", "slippage_bp", "total_return", "ann_return", "ann_vol",
          "sharpe_naive", "sharpe_lo", "max_drawdown", "calmar",
          "ann_turnover_one_sided"]].round(4).to_string(index=False))

for a, uf in uf_notes.items():
    print(f"\nunavailable fills [{a}]:")
    print(uf.to_string() if uf is not None else "  none")

print("\nyearly total returns (synthetic, 10bp):")
print(yearly.round(4).to_string())
yearly.to_csv(OUT / "yearly-synthetic-10bp.csv")

m1 = hl[(hl.arm == "synthetic") & (hl.slippage_bp == 10)].iloc[0]
print(f"\nlookahead check at 10bp (synthetic): "
      f"T+1 ann {m1['ann_return']:.4f} SR_lo {m1['sharpe_lo']:.4f} | "
      f"T+2 ann {lag_m['ann_return']:.4f} SR_lo {lag_m['sharpe_lo']:.4f}")
pd.DataFrame([{"check": "lag2_10bp", **lag_m}]).to_csv(
    OUT / "lag-check-hypothetical.csv", index=False)
