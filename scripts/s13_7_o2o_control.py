"""Session 13.7 step 7 — open-to-open control.

Passive accumulation control, signed leverage deviation, and the
volatility-fund exclusion statement. Realized panel only (the synthetic
rebuild does not touch it), matched 2012+ window.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt

OUT = ROOT / "outputs" / "session-13.7"
OUT.mkdir(parents=True, exist_ok=True)
CUT = pd.Timestamp("2012-01-01")
rows = []

panel = bt.load_arm_panel("realized")
ok, mx = bt.assert_holdout(panel)
print(f"holdout: PASS max {mx.date()}")
cal = panel["SPY"].index


def metrics(r: pd.Series) -> dict:
    r = r.dropna()
    n = len(r)
    nav = (1 + r).cumprod()
    rf = bt.rf_per_session(r.index).fillna(0.0)
    ex = (r - rf).dropna()
    return {"ann_return": float(nav.iloc[-1] ** (252 / n) - 1),
            "ann_vol": float(r.std(ddof=1) * math.sqrt(252)),
            "sharpe_lo": bt.lo_sharpe(ex),
            "max_drawdown": float((nav / nav.cummax() - 1).min())}


print("== passive accumulation control ==")
for t in ("TQQQ", "QQQ"):
    tf = panel[t]
    c2c = tf.ret_total[tf.ret_total.index >= CUT]
    ao = tf.adj_open
    o2o = (ao / ao.shift(1) - 1.0)
    o2o = o2o[o2o.index >= CUT]
    m_c = metrics(c2c)
    m_o = metrics(o2o)
    rows.append({"table": "passive_control", "instrument": t, "convention": "close_to_close", **m_c})
    rows.append({"table": "passive_control", "instrument": t, "convention": "open_to_open", **m_o})
    rows.append({"table": "passive_control", "instrument": t, "convention": "GAP_o2o_minus_c2c",
                 **{k: m_o[k] - m_c[k] for k in m_c}})
    print(f"  {t}: c2c ann {m_c['ann_return']:.4f} | o2o ann {m_o['ann_return']:.4f} | "
          f"gap {m_o['ann_return']-m_c['ann_return']:+.4f}")

gap_tqqq = [r for r in rows if r["instrument"] == "TQQQ" and r["convention"].startswith("GAP")][0]
gap_qqq = [r for r in rows if r["instrument"] == "QQQ" and r["convention"].startswith("GAP")][0]
verdict = ("negligible_passive_gap: the strategy's open-to-open advantage is a "
           "property of WHEN IT TRADES, not accumulation arithmetic"
           if abs(gap_tqqq["ann_return"]) < 0.02 and abs(gap_qqq["ann_return"]) < 0.02
           else "large_passive_gap: the advantage is accumulation arithmetic and "
                "the strategy o2o result is NOT interpretable as an execution finding")
rows.append({"table": "verdict", "note": verdict,
             "tqqq_gap_ann": gap_tqqq["ann_return"], "qqq_gap_ann": gap_qqq["ann_return"]})
print("verdict:", verdict)

print("== signed leverage deviation by vol decile ==")
UND = {"TQQQ": ("QQQ", 3), "SQQQ": ("QQQ", -3), "QLD": ("QQQ", 2), "PSQ": ("QQQ", -1),
       "SPXL": ("SPY", 3), "TECL": ("XLK", 3), "TECS": ("XLK", -3),
       "SOXL": ("SOXX", 3), "SOXS": ("SOXX", -3), "LABU": ("XBI", 3)}
extra = {u: bt._frozen_frame(u) for u in ("SOXX", "XBI")}

def o2o_ret_of(tf):
    ao = tf.frame["adj_open"]
    return (ao / ao.shift(1) - 1.0).reindex(cal)

und_ret = {u: o2o_ret_of(panel[u]) for u in ("QQQ", "SPY", "XLK")}
und_ret.update({u: o2o_ret_of(extra[u]) for u in ("SOXX", "XBI")})

# holdings: rerun the o2o account cheaply to get held sessions (anchor).
sig = bt.ArmSignals(panel, cal)
srows = bt.run_signals(sig)["rows"]
from src.data import TickerFrame
o2o_frames = {}
for t, tf in panel.frames.items():
    fr = tf.frame.copy()
    ao = fr["adj_open"]
    fr["ret_total"] = ao / ao.shift(1) - 1.0
    fr["close"] = fr["open"]
    o2o_frames[t] = TickerFrame(t, fr)
o2o_panel = bt.Panel()
o2o_panel.frames = o2o_frames
o2o_panel._lagged = {bt.config.TREND_SIGNAL_SERIES}
acc = bt.run_account(sig, o2o_panel, srows, 10)
import scripts.s13_runall as ra
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                   for r in acc["raw_rows"]], index=acc["daily"].index)

devs = []
for t, (u, M) in UND.items():
    held = (rw[t].shift(1) > 0)
    held = held[held.index >= CUT]
    if held.sum() < 20:
        continue
    rf_ = o2o_frames[t].frame["ret_total"].reindex(rw.index)
    ru = und_ret[u].reindex(rw.index)
    vol = ru.rolling(60).std() * math.sqrt(252)
    dd = pd.DataFrame({"dev": rf_ - M * ru, "vol": vol})
    dd = dd[held.reindex(dd.index).fillna(False)].dropna()
    devs.append(dd.assign(ticker=t))
alldev = pd.concat(devs)
dec = pd.qcut(alldev["vol"], 10, labels=False, duplicates="drop")
for di in sorted(dec.dropna().unique()):
    g = alldev[dec == di]["dev"]
    rows.append({"table": "signed_deviation", "vol_decile": int(di),
                 "mean_signed_dev_daily": float(g.mean()),
                 "std_error": float(g.std(ddof=1) / math.sqrt(len(g))),
                 "compounded_annual_effect": float((1 + g.mean()) ** 252 - 1),
                 "n": int(len(g))})
g = alldev["dev"]
rows.append({"table": "signed_deviation", "vol_decile": "ALL",
             "mean_signed_dev_daily": float(g.mean()),
             "std_error": float(g.std(ddof=1) / math.sqrt(len(g))),
             "compounded_annual_effect": float((1 + g.mean()) ** 252 - 1),
             "n": int(len(g))})
print(f"  all-decile mean signed dev {g.mean():+.5f}/day "
      f"({(1+g.mean())**252-1:+.3f} compounded/yr), n={len(g)}")

rows.append({"table": "vol_fund_exclusion", "note":
             "UVXY/SVXY remain excluded: raw CFE files carry Open columns but no "
             "validated 30-day constant-maturity OPEN index exists; constructing "
             "one re-derives construction B on a price stamp with no NAV "
             "validation target. Unmeasured fraction of dollar exposure: "
             "UVXY 18.5% + SVXY 4.0% = 22.5% (session 13 time-in-instrument)."})

pd.DataFrame(rows).to_csv(OUT / "o2o-control.csv", index=False)
print(f"[wrote o2o-control.csv: {len(rows)} rows]")
