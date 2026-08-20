"""Session 14 shared environment: verified cost model, participation cap,
panels, signals, metrics. Imported by every session-14 script so the
ladder, the nulls, and the decompositions all run on one anchor.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.s13_backtest as bt
import scripts.s13_runall as ra
from src import config
from src.data import TickerFrame

import os as _os
OUT = ROOT / "outputs" / (_os.environ.get("S20_OUTDIR") or "session-14")
OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
S138 = ROOT / "outputs" / "session-13.8"
S139 = ROOT / "outputs" / "session-13.9"

ANCHOR = 10
# Session 20 C1 repair. Register 7.14a moved the primary window start to
# 2011-10-04, and this default was never updated, so every session 15 output
# carried the superseded boundary at 2,473 sessions.
PRIMARY_START = pd.Timestamp("2011-10-04")
EARLY_END = pd.Timestamp("2011-10-02")
SPLICE = pd.Timestamp(config.COMMISSION_SPLICE_DATE)

# 4.4 as amended in 13.9: class-based tiers, multipliers, anchor.
TIER_CLASS = {"QQQ": 1, "TLT": 1, "BIL": 1, "BSV": 1, "SPY": 1, "XLK": 1,
              "SMH": 1, "IOO": 1, "VTV": 1, "VOX": 1, "VOOG": 1, "VOOV": 1,
              "XLP": 1, "XLY": 1, "XLF": 1, "QQQE": 1, "AGG": 1, "IEF": 1,
              "BND": 1, "RYMFX": 1, "SOXX": 1, "XBI": 1,
              "TQQQ": 2, "SQQQ": 2, "QLD": 2, "PSQ": 2, "SH": 2,
              "QID": 2, "SSO": 2, "SDS": 2,
              "SOXL": 3, "SOXS": 3, "TECL": 3, "TECS": 3, "SPXL": 3,
              "FAS": 3, "LABU": 3, "UVXY": 3, "SVXY": 3, "BTAL": 3}
TIER_MULT = {1: 0.2, 2: 0.5, 3: 1.5}

# 4.4a as recorded in 13.9: opening-auction premium, o2o arm only.
_prem = json.load(open(S139 / "_premium.json"))
PREMIUM_CENTRAL = float(_prem["central"])
PREMIUM_SWEEP = [float(x) for x in _prem["sweep"]]

# 2.13a expense constants as corrected in 13.8.
_er = json.load(open(S138 / "_er_new.json"))
ER_OLD, ER_NEW = _er["ER_OLD"], _er["ER_NEW"]

# 4.5 commission arms, constants from config.
SEC_FEE = 27.80 / 1e6
TAF = 0.000166
TAF_CAP = 8.30
PASSTHRU = 0.0012


def arm_F(date, t, side, sh, v):
    return min(max(config.COMMISSION_F_MINIMUM, config.COMMISSION_F_PER_SHARE * sh),
               config.COMMISSION_F_CAP_FRAC * v)


def arm_T(date, t, side, sh, v):
    c = min(max(config.COMMISSION_T_MINIMUM, config.COMMISSION_T_PER_SHARE * sh),
            config.COMMISSION_T_CAP_FRAC * v) + PASSTHRU * sh
    if side == "sell":
        c += SEC_FEE * v + min(TAF * sh, TAF_CAP)
    return c


def arm_S(date, t, side, sh, v):
    return arm_F(date, t, side, sh, v) if date < SPLICE else 0.0


def arm_Z(date, t, side, sh, v):
    return 0.0


ARMS = {"F": arm_F, "T": arm_T, "S": arm_S, "Z": arm_Z}
CANONICAL_ARM = "S"


def slip_class(date, t):
    return ANCHOR * TIER_MULT[TIER_CLASS.get(t, 3)]


def slip_class_premium(mult=PREMIUM_CENTRAL):
    def f(date, t):
        return ANCHOR * TIER_MULT[TIER_CLASS.get(t, 3)] * mult
    return f


def slip_uniform(bp):
    def f(date, t):
        return bp
    return f


# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------

def adjusted_syn_panel() -> bt.Panel:
    p = bt.load_arm_panel("synthetic")
    for t in ER_NEW:
        if t not in p.frames:
            continue
        d = (ER_NEW[t] - ER_OLD[t]) / 100.0 / 252.0
        if d == 0:
            continue
        fr = p[t].frame.copy()
        fr["ret_total"] = fr["ret_total"] - d
        r = fr["ret_total"].copy()
        if len(r):
            r.iloc[0] = 0.0
        fr["tr_index"] = (1.0 + r).cumprod()
        fr["adj_close"] = fr["tr_index"]
        p.frames[t] = TickerFrame(t, fr)
    return p


def o2o_panel_from(p: bt.Panel) -> bt.Panel:
    frames = {}
    for t, tf in p.frames.items():
        fr = tf.frame.copy()
        ao = fr["adj_open"]
        fr["ret_total"] = ao / ao.shift(1) - 1.0
        fr["close"] = fr["open"]
        frames[t] = TickerFrame(t, fr)
    out = bt.Panel()
    out.frames = frames
    out._lagged = {config.TREND_SIGNAL_SERIES}
    return out


# ---------------------------------------------------------------------------
# Participation cap (4.6 as amended, session 14 step 0b)
# ---------------------------------------------------------------------------
CAP_LOOKBACK = 21
CAP_LEVEL = 0.05


def dollar_volume_frame(cal: pd.DatetimeIndex, tickers) -> pd.DataFrame:
    """Point-in-time trailing denominator, one column per ticker.

    Trailing median daily dollar volume over CAP_LOOKBACK sessions, lagged
    one session, expanding where fewer than CAP_LOOKBACK sessions of
    history exist. Zero-volume sessions are excluded from the median: for
    the extreme reverse-splitters the stored adjusted-volume record
    truncates to zero (session 05 established SOXS at 57.7 percent of
    sessions and TECS at 28.6 percent), which is a property of the stored
    record rather than a measurement of liquidity, and including those
    rows would drive the median to zero and cap the position to nothing on
    an artifact.
    """
    out = {}
    for t in tickers:
        raw = bt._load_raw(t)
        dv = (raw["Volume"].astype(float) * raw["Close"].astype(float))
        dv = dv.where(raw["Volume"].astype(float) > 0)
        dv = dv.reindex(cal)
        med = dv.rolling(CAP_LOOKBACK, min_periods=1).median().shift(1)
        out[t] = med
    return pd.DataFrame(out, index=cal)


def make_cap_fn(dvf: pd.DataFrame, level: float = CAP_LEVEL):
    arr = {t: dvf[t].to_numpy() for t in dvf.columns}

    def cap_fn(i: int, ticker: str):
        a = arr.get(ticker)
        if a is None:
            return None
        v = a[i]
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        return level * float(v)
    return cap_fn


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def window_slice(s: pd.Series, window: str) -> pd.Series:
    if window == "primary":
        return s[s.index >= PRIMARY_START]
    if window == "early":
        return s[s.index <= EARLY_END]
    return s


def metrics(ret: pd.Series, orders: pd.DataFrame | None = None,
            nav: pd.Series | None = None) -> dict | None:
    r = ret.dropna()
    if len(r) < 60:
        return None
    n = len(r)
    growth = (1 + r).cumprod()
    rf = bt.rf_per_session(r.index).fillna(0.0)
    ex = (r - rf).dropna()
    mdd = float((growth / growth.cummax() - 1).min())
    ann = float(growth.iloc[-1] ** (252 / n) - 1)
    out = {"n_sessions": n,
           "total_return": float(growth.iloc[-1] - 1),
           "ann_return": ann,
           "ann_vol": float(r.std(ddof=1) * math.sqrt(252)),
           "sharpe_naive": float(ex.mean() / ex.std(ddof=1) * math.sqrt(252)),
           "sharpe_lo": bt.lo_sharpe(ex),
           "max_drawdown": mdd,
           "calmar": ann / abs(mdd) if mdd < 0 else np.nan,
           "arith_mean_excess_ann": float(ex.mean() * 252)}
    if orders is not None and nav is not None and len(orders):
        od = orders[(orders["date"] >= r.index.min()) & (orders["date"] <= r.index.max())]
        navw = nav.reindex(r.index)
        out["ann_turnover"] = float(od["value"].sum() / 2 / navw.mean() / (n / 252)) \
            if len(od) else 0.0
    else:
        out["ann_turnover"] = 0.0
    return out


def alpha_beta(strategy: pd.Series, benchmark: pd.Series) -> dict:
    j = pd.DataFrame({"s": strategy, "b": benchmark}).dropna()
    if len(j) < 60:
        return {"alpha_ann": np.nan, "beta": np.nan, "n": len(j)}
    rf = bt.rf_per_session(j.index).fillna(0.0)
    y = (j["s"] - rf).to_numpy()
    x = (j["b"] - rf).to_numpy()
    beta = float(np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1))
    alpha_d = float(y.mean() - beta * x.mean())
    return {"alpha_ann": alpha_d * 252, "beta": beta, "n": len(j)}


# ---------------------------------------------------------------------------
# Environment builder
# ---------------------------------------------------------------------------

def build_env(verbose=True):
    panels = {"synthetic": adjusted_syn_panel(), "realized": bt.load_arm_panel("realized")}
    for a, p in panels.items():
        ok, mx = bt.assert_holdout(p)
        if verbose:
            print(f"holdout [{a}]: PASS max {mx.date()}")
    cal = panels["synthetic"]["SPY"].index
    sigs = {}
    for a in panels:
        s = bt.ArmSignals(panels[a], cal)
        sigs[a] = {"sig": s, **bt.run_signals(s)}
    o2o = o2o_panel_from(panels["realized"])
    dvf = dollar_volume_frame(cal, sorted(TIER_CLASS))
    return {"panels": panels, "cal": cal, "sigs": sigs, "o2o": o2o,
            "dvf": dvf, "cap_fn": make_cap_fn(dvf)}
