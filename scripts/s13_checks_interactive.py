"""Session 13 — engine verification pass (positive controls, raise/fill audit).

Run before diagnostics. Nothing here tunes anything; it verifies the
engine and decomposes the two flagged findings (raise events, lookahead).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.s13_backtest as bt
from src import config

panels = {"synthetic": bt.load_arm_panel("synthetic"),
          "realized": bt.load_arm_panel("realized")}
cal = panels["synthetic"]["SPY"].index

sigs, runs = {}, {}
for arm in ("synthetic", "realized"):
    sig = bt.ArmSignals(panels[arm], cal)
    out = bt.run_signals(sig)
    sigs[arm] = {"sig": sig, **out}

print("== raise events by arm, warm-up split ==")
for arm in ("synthetic", "realized"):
    ev = pd.DataFrame(sigs[arm]["raises"])
    ev["idx"] = ev["date"].map(lambda d: cal.get_indexer([d])[0])
    pre = ev[ev["idx"] < config.WARMUP_SESSIONS]
    post = ev[ev["idx"] >= config.WARMUP_SESSIONS]
    print(f"[{arm}] total {len(ev)}, pre-warm-up {len(pre)}, POST-warm-up {len(post)}")
    print(f"  pre dates {pre['date'].min().date()} .. {pre['date'].max().date()}; "
          f"distinct sessions {pre['date'].nunique()}")
    print("  by sleeve:", pre.groupby("sleeve").size().to_dict())
    # positive control for the site search: the known RYMFX seeding raise
    assert (pre["msg"].str.contains("XLK>TREND").any()), "positive control failed"
    if len(post):
        print("  POST-WARM-UP RAISES:", post[["date", "sleeve"]].to_string())
    ev.to_csv(bt.OUT / f"_raises-{arm}.csv", index=False)

print("\n== unavailable fills at 10bp ==")
for arm in ("synthetic", "realized"):
    acc = bt.run_account(sigs[arm]["sig"], panels[arm], sigs[arm]["rows"], 10)
    runs[arm] = acc
    uf = acc["unavailable_fills"]
    if len(uf):
        by = uf.groupby("ticker").agg(n=("date", "size"), first=("date", "min"),
                                      last=("date", "max"))
        print(f"[{arm}] {len(uf)} events")
        print(by.to_string())
        uf.to_csv(bt.OUT / f"_unavailable-fills-{arm}.csv", index=False)
    else:
        print(f"[{arm}] none")

print("\n== engine positive control: constant SPY target ==")
# Feed the account engine a single transition to 100% SPY at the first
# post-warm-up session and no further transitions. The engine's ending NAV
# must match SPY's total-return path over the held window within the
# truncation-residual and commission tolerance.
first_i = config.WARMUP_SESSIONS
ctrl_rows = [{"i": first_i, "date": cal[first_i], "label": "CTRL",
              "changed": True, "targets": {"SPY": 1.0},
              "gross_before_cap": 1.0, "cap_truncated": False,
              "sleeves": {}, "raised": {}}]
ctrl = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"], ctrl_rows, 0)
nav = ctrl["daily"]["nav"]
spy = panels["synthetic"]["SPY"].tr_index.reindex(cal)
fill_i = first_i + 1
spy_growth = float(spy.iloc[-1] / spy.iloc[fill_i])
# invested fraction: shares*px / NAV at fill; residual stays at DTB3
print(f"engine NAV growth  : {nav.iloc[-1]/nav.iloc[0]:.6f}")
print(f"SPY TR growth (fill->end): {spy_growth:.6f}")
rel = abs(nav.iloc[-1] / (bt.START_NAV * spy_growth) - 1.0)
print(f"relative gap (incl. residual cash at DTB3 vs SPY, 1 commission): {rel:.5%}")
assert rel < 0.005, "positive control failed: engine does not reproduce buy-and-hold"

print("\n== lookahead decomposition at 0 bp (cost-free) ==")
for lagn in (1, 2):
    acc = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"],
                         sigs["synthetic"]["rows"], 0, fill_lag=lagn)
    m = bt.headline_metrics(acc["daily"], acc["orders"])
    print(f"lag {lagn}: ann {m['ann_return']:.4f}  vol {m['ann_vol']:.4f}  "
          f"SR_lo {m['sharpe_lo']:.4f}  MDD {m['max_drawdown']:.4f}")

print("\n== transition-day event study (synthetic, 0bp path) ==")
acc0 = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"], sigs["synthetic"]["rows"], 0)
d = acc0["daily"]
tr_next = d["ret"].shift(-1)[d["transition"]]
print(f"mean strategy return on the session AFTER a fill: {d['ret'][d['transition']].mean():.5f}")
print(f"mean next-session return following fills        : {tr_next.mean():.5f}")
print(f"mean all-session return                         : {d['ret'].mean():.5f}")
