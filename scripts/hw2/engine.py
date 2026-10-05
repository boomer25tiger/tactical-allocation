"""Constant-NAV account for the HW2 re-runs, shared by h01 and h02.

Re-implements the designated cell's account loop (realized panel,
open-to-open fills at the next open, class-tiered slippage with the 2.0x
opening-auction premium, commission arm S, 5% participation cap) with one
switch: reset=True tops capital up or withdraws it after every session so NAV
stays at nav0. With reset=False and nav0 = $1M it reproduces the canonical
designated cell (primary-window CAGR 0.521845). SLIP is a module global so a
caller can swap the slippage function, as h02 does for the uniform-cost sweep.
Importing this module builds the panel and signals but runs no backtest.
"""


import math
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT  # noqa: E402  (sets READ_HOLDOUT_THROUGH and sys.path)

import numpy as np            # noqa: E402
import pandas as pd           # noqa: E402
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
from src import config              # noqa: E402


panel = bt.load_arm_panel("realized")
bt.assert_holdout(panel)
cal = panel["SPY"].index
_s = bt.ArmSignals(panel, cal)
sig = {"sig": _s, **bt.run_signals(_s)}
o2o = C.o2o_panel_from(panel)
cap_fn = C.make_cap_fn(C.dollar_volume_frame(cal, sorted(C.TIER_CLASS)))
COMM = C.ARMS[C.CANONICAL_ARM]
SLIP = C.slip_class_premium()


def run(nav0, reset=True):
    s = sig["sig"]
    cal_ = s.calendar
    ret, raw, splitf = bt._account_arrays(o2o, cal_)
    rf = bt._account_rf().loc[:bt.HOLDOUT_LAST_DATE]
    by_index = {r["i"]: r for r in sig["rows"]}
    pending, positions = [], {}
    cash, prev = nav0, None
    daily, caps, tlog, orders = [], [], [], []
    for i in range(config.WARMUP_SESSIONS, len(cal_)):
        date = cal_[i]
        if prev is not None:
            cash *= float(rf.loc[prev + pd.Timedelta(days=1): date].prod())
        for t, p in positions.items():
            r = ret[t][i]
            if math.isnan(r):
                raise AssertionError(f"return unavailable mid-hold {t} {date}")
            p["value"] *= (1.0 + r)
            sp = splitf[t][i]
            if sp and not math.isnan(sp) and sp > 0:
                p["shares"] *= sp
        while pending and pending[0][0] <= i:
            _, targets = pending.pop(0)
            nav = sum(p["value"] for p in positions.values()) + cash
            fillable = {}
            for t, w in targets.items():
                px = raw[t][i]
                if not (math.isnan(px) or px <= 0):
                    fillable[t] = (w, float(px))
            tshares, tot, tocash = {}, 0.0, 0.0
            for t, (w, px) in fillable.items():
                alloc = nav * w
                tot += alloc
                lim = cap_fn(i, t)
                if lim is not None and lim < alloc:
                    caps.append({"date": date, "ticker": t, "target": alloc,
                                 "cap": lim, "frac_capped": (alloc - lim) / alloc})
                    tocash += alloc - lim
                    alloc = lim
                tshares[t] = math.trunc(alloc / px)
            tlog.append({"date": date, "target": tot, "to_cash": tocash})
            for t in list(positions):
                cur = positions[t]
                tgt = tshares.get(t, 0)
                if cur["shares"] > tgt:
                    px = raw[t][i]
                    if math.isnan(px) or px <= 0:
                        continue
                    d = cur["shares"] - tgt
                    frac = d / cur["shares"]
                    proceeds = cur["value"] * frac
                    ov = d * px
                    c_ = COMM(date, t, "sell", d, ov)
                    sl = (SLIP(date, t) / 2.0) / 1e4 * ov
                    cash += proceeds - c_ - sl
                    cur["value"] -= proceeds
                    cur["shares"] -= d
                    orders.append({"date": date, "value": ov})
                    if cur["shares"] <= 0:
                        del positions[t]
            for t, (w, px) in fillable.items():
                tgt = tshares[t]
                cur = positions.get(t)
                have = cur["shares"] if cur else 0
                if tgt > have:
                    d = tgt - have
                    ov = d * px
                    c_ = COMM(date, t, "buy", d, ov)
                    sl = (SLIP(date, t) / 2.0) / 1e4 * ov
                    cash -= ov + c_ + sl
                    if cur:
                        cur["shares"] += d
                        cur["value"] += ov
                    else:
                        positions[t] = {"shares": d, "value": ov}
                    orders.append({"date": date, "value": ov})
        srow = by_index.get(i)
        if srow is not None and srow["changed"] and srow["targets"] is not None:
            if i + 1 < len(cal_):
                pending.append((i + 1, srow["targets"]))
        pv = sum(p["value"] for p in positions.values())
        nav = pv + cash
        daily.append({"date": date, "nav": nav, "invested": pv / nav})
        if reset:
            cash += nav0 - nav
        prev = date
    df = pd.DataFrame(daily).set_index("date")
    if reset:
        df["ret"] = df["nav"] / nav0 - 1.0
        df.iloc[0, df.columns.get_loc("ret")] = np.nan
    else:
        df["ret"] = df["nav"] / df["nav"].shift(1) - 1.0
    return df, pd.DataFrame(caps), pd.DataFrame(tlog), pd.DataFrame(orders)


RF = bt.rf_per_session(cal)


def stats(r, nav0=None, tl=None, cp=None, od=None):
    r = r.dropna()
    n = len(r)
    g = (1 + r).cumprod()
    cagr = g.iloc[-1] ** (252.0 / n) - 1.0
    vol = r.std(ddof=1) * math.sqrt(252.0)
    ex = (r - RF.reindex(r.index)).dropna()
    sh = ex.mean() / ex.std(ddof=1) * math.sqrt(252.0)
    mdd = (g / g.cummax() - 1.0).min()
    out = {"n": n, "cagr": cagr, "vol": vol, "sharpe_naive": sh, "max_dd": mdd}
    if tl is not None and len(tl):
        out["to_cash_share"] = tl["to_cash"].sum() / tl["target"].sum()
        out["transitions"] = len(tl)
        out["capped_transitions"] = (tl["to_cash"] > 0).mean()
    if od is not None and len(od):
        out["turnover"] = od["value"].sum() / 2.0 / nav0 / (n / 252.0)
    return out
