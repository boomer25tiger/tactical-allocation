"""Session 13 — canonical in-sample backtest.

First strategy result in the project. Every strategy parameter comes from
src/config.py; the two provisional operating values the session prompt
amendments supply are marked below and reported before any statistic:

  * START_NAV = 1,000,000 — provisional under decision 4.6, which stays
    OPEN pending a liquidity check against the realized NAV path. Not
    canonical.
  * IBKR Fixed commission terms — v2 decision 4.5, closed in conversation
    (only schedule continuously available 2007-2026, conservative on
    level) but NOT yet ported into DECISIONS-v3.md or src/config.py.
    Carried inline; the port is outstanding.

Holdout (2.10): every input series is truncated at HOLDOUT_LAST_DATE
inside the loader, before any strategy code runs, and an assertion after
loading verifies no frame carries a later observation.

Unavailable fills (the open half of 2.11): a target whose fill-session
raw price does not exist (BTAL before its 2011-09-13 listing in both
arms; every unlisted fund in the realized arm) is recorded as an
unavailable-fill event and the slice stays in sleeve cash at DTB3. This
is a PROVISIONAL completion rule stated in the report, not a register
closure; src/execution.py's raise marks where the decision lands and this
script records every event the raise would have thrown.

Raw path for synthetics (1.4): share counts and commission need a
per-share price. Where the fund is listed the real raw close is used;
before listing the raw price is back-extended from the first listed raw
close with synthetic returns (raw[t-1] = raw[t] / (1 + syn_ret[t])).
Deterministic, disclosed; no split schedule is invented for the
pre-listing window.
"""

from __future__ import annotations

import json
import math
import os as _os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config
from src.data import Panel, build_ticker_frame, TickerFrame, load_risk_free_series, risk_free_daily_factors
from src.indicators import sma, wilder_rsi
from src.portfolio import PortfolioTracker, SLEEVE_ORDER, sleeve_label
from src.schedule import FUND_SCHEDULE
from src.sleeves import s2_weights, s3_weights, t10_weights, t11_weights, T10_CASCADE, T11_PANEL, S3_VOTES

OUT = ROOT / "outputs" / "session-13"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Sample window and holdout (2.9, 2.10)
# ---------------------------------------------------------------------------
SAMPLE_START = pd.Timestamp("2007-01-01")      # 2.9
HOLDOUT_BOUNDARY = pd.Timestamp("2021-08-01")  # 2.10, the sealed boundary, unchanged
# 2.10 truncates every loaded series at the session before the boundary. Session 27
# reads the sealed span exactly once, under the prediction committed at 9.64, and
# lifts the truncation for that read alone through an explicit environment variable.
# THE DEFAULT IS UNCHANGED, so every other context still loads nothing past
# 2021-07-31 and assert_holdout still fires on a breach. The boundary itself is not
# moved, and no strategy parameter reads this variable.
HOLDOUT_LAST_DATE = pd.Timestamp(
    _os.environ.get("READ_HOLDOUT_THROUGH") or "2021-07-31")  # 2.10: boundary 2021-08-01

# Starting NAV: closed at 1,000,000 by session 13.7 (4.6, with the
# liquidity check recorded in the register). Commission constants: ported
# to src/config.py by session 13.7 (4.5 / D2); Arm F remains the engine
# default for comparability.
START_NAV = 1_000_000.0
COMMISSION_PER_SHARE = config.COMMISSION_F_PER_SHARE
COMMISSION_MINIMUM = config.COMMISSION_F_MINIMUM
COMMISSION_CAP_FRAC = config.COMMISSION_F_CAP_FRAC

# Instrument sourcing (2.8). SVIX/UVIX list 2022-03-28, outside the sample,
# and are deliberately NOT loaded: sleeves' availability switches then
# resolve the T10 short-vol and S3 vol legs to SVXY/UVXY throughout.
LEVERED = ("TQQQ", "SQQQ", "QLD", "PSQ", "SH", "SPXL", "TECL", "TECS",
           "SOXL", "SOXS", "FAS", "LABU", "UVXY", "SVXY")
UNLEVERED = ("SPY", "QQQ", "XLK", "SMH", "RYMFX", "TLT", "AGG", "IEF",
             "BND", "BSV", "BIL", "BTAL", "IOO", "VTV", "VOX", "VOOG",
             "VOOV", "XLP", "XLY", "XLF", "QQQE")

# Underlying groups for the 5.7 HHI-on-underlyings (target tickers only).
UNDERLYING = {
    "QQQ": "NDX", "TQQQ": "NDX", "QLD": "NDX", "SQQQ": "NDX", "PSQ": "NDX",
    "SPY": "SPX", "SPXL": "SPX", "SH": "SPX",
    "XLK": "TECH", "TECL": "TECH", "TECS": "TECH",
    "SMH": "SEMI", "SOXL": "SEMI", "SOXS": "SEMI",
    "XLF": "FIN", "FAS": "FIN",
    "LABU": "BIOTECH",
    "UVXY": "VIXFUT", "SVXY": "VIXFUT",
    "TLT": "TSY_LONG", "IEF": "TSY_INT", "AGG": "AGGREGATE", "BND": "AGGREGATE",
    "BSV": "TSY_SHORT", "BIL": "TSY_SHORT", "BTAL": "ANTIBETA",
}

SLEEVE_FNS = {"T10": t10_weights, "T11": t11_weights, "S2": s2_weights, "S3": s3_weights}


# ---------------------------------------------------------------------------
# Loading with holdout truncation INSIDE the loader
# ---------------------------------------------------------------------------

def _full_forward_split_factor(ticker: str, index: pd.DatetimeIndex) -> pd.Series:
    """F(t) = product of split ratios strictly after t through the download
    date, from the frozen file's FULL split history (session 13.6 decode).

    2.10 reasoning, recorded per the session prompt: the frozen panel was
    downloaded in 2026 and its Close column already expresses every
    in-sample price in 2026 share units, so post-boundary split history is
    already embedded in the data the backtest reads. Reading the split
    ratios removes that embedding rather than adding out-of-sample
    information; a split ratio is a corporate action carrying no
    information about strategy performance. ONLY the 'Stock Splits'
    column is read over the full span -- no post-boundary price or volume
    is retrieved, loaded, or computed on.
    """
    sp = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{ticker}.parquet",
                         columns=["Stock Splits"])["Stock Splits"]
    idx = pd.to_datetime(sp.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    sp.index = idx.normalize()
    sp = _apply_split_patch(ticker, sp.astype(float))
    f = sp.astype(float).fillna(0.0).replace(0.0, 1.0)
    rev_incl = f[::-1].cumprod()[::-1]   # product over s >= t, full history
    factor = rev_incl / f                # product over s > t
    return factor.reindex(index)


def _as_traded(ticker: str, close: pd.Series) -> pd.Series:
    """As-traded price: adjusted Close x forward split factor (full span).

    Direction verified by positive controls in scripts/s13_6_run.py
    (reverse-splitters come DOWN from the inflated adjusted level,
    forward-splitters come UP)."""
    return close * _full_forward_split_factor(ticker, close.index)


# D15 patch (session 13.8, authorized): the vendor split record for SOXS
# omits the 2021-03-02 1:15 reverse split — Direxion's companion to SOXL's
# same-date 15:1 forward split, which IS present in SOXL's record. The
# frozen file is NOT modified (1.1); the patch applies at load. Evidence:
# SEC-sourced NAV control (16.25 on 2017-10-31, Direxion FY2017 N-CSR
# 0001104659-18-000153-era filings), adjusted-close continuity through the
# date, and the recovered x15 level error (session 13.7 price control).
SPLIT_PATCHES: dict[str, dict[str, float]] = {
    "SOXS": {"2021-03-02": 1.0 / 15.0},
}


def _apply_split_patch(ticker: str, splits: pd.Series) -> pd.Series:
    for ds, ratio in SPLIT_PATCHES.get(ticker, {}).items():
        d = pd.Timestamp(ds)
        if d in splits.index:
            splits.loc[d] = ratio
    return splits


def _load_raw(ticker: str) -> pd.DataFrame:
    raw = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{ticker}.parquet")
    idx = pd.to_datetime(raw.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    raw.index = idx.normalize()
    if ticker in SPLIT_PATCHES:
        raw = raw.copy()
        raw["Stock Splits"] = _apply_split_patch(
            ticker, raw["Stock Splits"].astype(float))
    # Holdout truncation before anything downstream sees the frame (2.10),
    # and the 2.9 sample start.
    return raw.loc[(raw.index >= SAMPLE_START) & (raw.index <= HOLDOUT_LAST_DATE)]


def _apply_smh_accrual(tf: TickerFrame) -> TickerFrame:
    """3.12: SMH pre-2013 constant accrual on ret_total, 252-day basis.

    Applied to sessions strictly before the first real distribution
    (2012-12-24 per session 00C) so the accrual and the resumed real
    dividends never overlap. tr_index rebuilt on the amended returns.
    """
    f = tf.frame.copy()
    first_dist = pd.Timestamp("2012-12-24")
    add = config.SMH_PRE2013_ACCRUAL_PCT / 100.0 / 252.0
    mask = (f.index < first_dist) & f["ret_total"].notna()
    f.loc[mask, "ret_total"] = f.loc[mask, "ret_total"] + add
    valid = f["ret_total"].notna()
    r = f.loc[valid, "ret_total"].copy()
    if len(r):
        r.iloc[0] = 0.0
    f["tr_index"] = (1.0 + r).cumprod().reindex(f.index)
    return TickerFrame(tf.ticker, f)


def _synthetic_frame(ticker: str) -> TickerFrame:
    """Primary-arm frame for a levered fund from data/interim/synthetics/.

    Signal path: tr_index from syn_index, ret_total = syn_ret, both sliced
    to the sample window. Raw path: the real fund's raw close where
    listed; back-extended with synthetic returns before listing, anchored
    at the first listed raw close. Split factors carried from the real
    file (zero pre-listing; no schedule invented).
    """
    syn = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{ticker}.parquet")
    syn.index = pd.to_datetime(syn.index).normalize()
    syn = syn.loc[(syn.index >= SAMPLE_START) & (syn.index <= HOLDOUT_LAST_DATE)]

    real = _load_raw(ticker)  # already truncated; may start mid-window

    f = pd.DataFrame(index=syn.index)
    f.index.name = "date"
    f["ret_total"] = syn["syn_ret"].astype(float)
    r = f["ret_total"].copy()
    if len(r):
        r.iloc[0] = 0.0
    f["tr_index"] = (1.0 + r).cumprod()
    f["adj_close"] = f["tr_index"]
    f["adj_open"] = np.nan
    f["multiple"] = syn["multiple"].astype(float)

    close = pd.Series(np.nan, index=f.index)
    split = pd.Series(0.0, index=f.index)
    if len(real):
        rc = _as_traded(ticker, real["Close"].astype(float))
        close.loc[rc.index.intersection(f.index)] = rc.reindex(f.index).loc[rc.index.intersection(f.index)]
        sp = real["Stock Splits"].astype(float).fillna(0.0)
        split.loc[sp.index.intersection(f.index)] = sp.reindex(f.index).loc[sp.index.intersection(f.index)]
        # Back-extension: walk backward from the first listed close.
        pos = f.index.get_indexer([rc.index.min()])[0]
        anchor = float(rc.iloc[0])
        rets = f["ret_total"].to_numpy()
        vals = close.to_numpy().copy()
        p = anchor
        for i in range(pos, 0, -1):
            p = p / (1.0 + rets[i])
            vals[i - 1] = p
        close = pd.Series(vals, index=f.index)
    f["close"] = close
    f["open"] = np.nan
    f["split"] = split
    f["ret_price"] = np.nan
    return TickerFrame(ticker, f)


# Session 13.6: the $100 listing anchor (session 13's provisional value 4)
# is superseded by the full-history split decode above. True as-traded
# levels are recovered for every listed period; only pre-listing synthetic
# back-extensions remain a convention (anchored at the first listed
# as-traded price, extended backward with synthetic returns).


def _frozen_frame(ticker: str) -> TickerFrame:
    tf = build_ticker_frame(ticker, _load_raw(ticker))
    if ticker == "SMH":
        tf = _apply_smh_accrual(tf)
    # Raw path to as-traded prices (share counts and commission, 1.4).
    fr = tf.frame.copy()
    fr["close"] = _as_traded(ticker, fr["close"])
    fr["open"] = _as_traded(ticker, fr["open"])
    return TickerFrame(ticker, fr)


def load_arm_panel(arm: str) -> Panel:
    """Assemble one arm's panel. arm in {'synthetic', 'realized'}."""
    panel = Panel()
    for t in UNLEVERED:
        panel.frames[t] = _frozen_frame(t)
    for t in LEVERED:
        if arm == "synthetic":
            panel.frames[t] = _synthetic_frame(t)
        else:
            tf = _frozen_frame(t)
            fr = tf.frame.copy()
            fr["multiple"] = np.nan
            panel.frames[t] = TickerFrame(t, fr)
    panel.apply_trend_lag()           # 2.5a, once, inside the loader
    panel.assert_trend_lag_applied_once()
    return panel


def assert_holdout(panel: Panel) -> tuple[bool, pd.Timestamp]:
    """2.10 assertion: no loaded frame carries a post-boundary observation."""
    mx = max(f.index.max() for f in panel.frames.values() if len(f))
    if mx > HOLDOUT_LAST_DATE:
        raise AssertionError(f"holdout breach: max loaded date {mx.date()}")
    return True, mx


# ---------------------------------------------------------------------------
# Indicator panel and state (6.1-6.6, 6.10; all periods from config)
# ---------------------------------------------------------------------------

class ArmSignals:
    def __init__(self, panel: Panel, calendar: pd.DatetimeIndex):
        self.calendar = calendar
        self.rsi: dict[int, dict[str, np.ndarray]] = {}
        self.smas: dict[int, dict[str, np.ndarray]] = {}
        self.price: dict[str, np.ndarray] = {}
        self.avail: dict[str, np.ndarray] = {}
        periods = {config.RSI_PERIOD_EXHAUSTION, config.RSI_PERIOD_DIP,
                   config.RSI_PERIOD_RELATIVE_STRENGTH}
        lengths = {config.SMA_LONG, config.SMA_SHORT}
        for t, tf in panel.frames.items():
            tr = tf.tr_index.reindex(calendar)
            self.price[t] = tr.to_numpy()
            self.avail[t] = tr.notna().to_numpy()
            for n in periods:
                self.rsi.setdefault(n, {})[t] = wilder_rsi(tr, n).to_numpy()
            for n in lengths:
                self.smas.setdefault(n, {})[t] = sma(tr, n).to_numpy()
        # 6.10 crash input: trailing CRASH_HORIZON_SESSIONS total return, %,
        # on the reference ticker's available subsequence.
        ref = panel[config.CRASH_REFERENCE_TICKER].tr_index.reindex(calendar)
        av = ref.dropna()
        trail = (av / av.shift(config.CRASH_HORIZON_SESSIONS) - 1.0) * 100.0
        self.crash = trail.reindex(calendar).to_numpy()

    def state_at(self, i: int) -> "State":
        return State(self, i)


class State:
    """IndicatorState protocol implementation at calendar index i."""

    def __init__(self, sig: ArmSignals, i: int):
        self.sig, self.i = sig, i

    def _get(self, table, t):
        arr = table.get(t)
        if arr is None:
            return None
        v = arr[self.i]
        return None if (isinstance(v, float) and math.isnan(v)) else float(v)

    def rsi_exhaustion(self, t): return self._get(self.sig.rsi[config.RSI_PERIOD_EXHAUSTION], t)
    def rsi_dip(self, t): return self._get(self.sig.rsi[config.RSI_PERIOD_DIP], t)
    def rsi_rs(self, t): return self._get(self.sig.rsi[config.RSI_PERIOD_RELATIVE_STRENGTH], t)
    def price(self, t): return self._get(self.sig.price, t)
    def sma(self, t, length): return self._get(self.sig.smas[length], t)

    def trailing_return_pct(self, t, horizon):
        assert t == config.CRASH_REFERENCE_TICKER and horizon == config.CRASH_HORIZON_SESSIONS
        v = self.sig.crash[self.i]
        return None if math.isnan(v) else float(v)

    def available(self, t):
        arr = self.sig.avail.get(t)
        return bool(arr[self.i]) if arr is not None else False


# ---------------------------------------------------------------------------
# Signal run: labels, targets, per-sleeve states, raise diagnostics (5.1, 5.2)
# ---------------------------------------------------------------------------

def run_signals(sig: ArmSignals) -> dict:
    cal = sig.calendar
    tracker = PortfolioTracker()
    rows = []
    raise_events = []          # every session x sleeve where a pairwise site raised
    for i in range(len(cal)):
        date = cal[i]
        state = sig.state_at(i)
        sleeves, raised = {}, {}
        for name in SLEEVE_ORDER:
            try:
                sleeves[name] = SLEEVE_FNS[name](date, state)
            except NotImplementedError as e:
                raised[name] = str(e)
                raise_events.append({"date": date, "sleeve": name, "msg": str(e)})
                sleeves[name] = None
        if i < config.WARMUP_SESSIONS:
            continue           # 2.11: no sleeve emits a weight during warm-up
        if raised:
            # Post-warm-up raise: the open half of 2.11 fired inside the
            # traded window. Recorded; the run marks the session and the
            # affected sleeve holds no target (provisional rule, reported).
            sleeves = {k: (v if v is not None else {}) for k, v in sleeves.items()}
        d = tracker.step(date, sleeves["T10"], sleeves["T11"], sleeves["S2"], sleeves["S3"])
        rows.append({
            "i": i, "date": date, "label": d.label, "changed": d.changed,
            "targets": d.targets, "gross_before_cap": d.gross_before_cap,
            "cap_truncated": d.cap_truncated,
            "sleeves": {k: dict(v) for k, v in sleeves.items()},
            "raised": dict(raised),
        })
    return {"rows": rows, "raises": raise_events}


# ---------------------------------------------------------------------------
# Execution and accounting (4.1 close-to-close, 4.7 truncation, 5.5a accrual)
# ---------------------------------------------------------------------------

def default_commission(date, ticker, side, shares, value) -> float:
    """Arm F: IBKR Fixed (v2 4.5). The engine default since session 13."""
    return min(max(COMMISSION_MINIMUM, COMMISSION_PER_SHARE * shares),
               COMMISSION_CAP_FRAC * value)


# Session 17: run_account rebuilds the same spec-independent arrays on every
# call and reloads the rate file each time. Across a 364,500-specification
# grid that is 37% of the call. The caches below are opt-in and default off,
# so every script written before session 17 keeps its exact prior behaviour.
_S17_CACHE = {"on": False, "arrays": {}, "rf": None}


def s17_enable_engine_cache(on: bool = True) -> None:
    _S17_CACHE["on"] = bool(on)
    if not on:
        _S17_CACHE["arrays"].clear()
        _S17_CACHE["rf"] = None


def _account_arrays(panel: Panel, cal):
    build = lambda: (
        {t: panel[t].ret_total.reindex(cal).to_numpy() for t in panel.frames},
        {t: panel[t].raw_close.reindex(cal).to_numpy() for t in panel.frames},
        {t: panel[t].frame["split"].reindex(cal).fillna(0.0).to_numpy()
         for t in panel.frames},
    )
    if not _S17_CACHE["on"]:
        return build()
    key = (id(panel), id(cal), len(cal))
    hit = _S17_CACHE["arrays"].get(key)
    if hit is None:
        hit = build()
        _S17_CACHE["arrays"][key] = hit
    return hit


def _account_rf():
    if not _S17_CACHE["on"]:
        return risk_free_daily_factors(load_risk_free_series())
    if _S17_CACHE["rf"] is None:
        _S17_CACHE["rf"] = risk_free_daily_factors(load_risk_free_series())
    return _S17_CACHE["rf"]


def run_account(sig: ArmSignals, panel: Panel, signal_rows: list[dict],
                slippage_bp: float, fill_lag: int = 1,
                commission_fn=None, slip_fn=None, cap_fn=None,
                rf_factors=None) -> dict:
    """One arm at one cost level. fill_lag=2 is the step-7 lookahead check.

    Session 13.7 extensions (defaults reproduce prior behaviour exactly):
    commission_fn(date, ticker, side, shares, value) -> dollars replaces
    Arm F when given; slip_fn(date, ticker) -> round-turn bp replaces the
    uniform slippage_bp when given (the engine halves it per side).
    """
    cal = sig.calendar
    ret, raw, splitf = _account_arrays(panel, cal)
    rf = _account_rf()
    rf = rf.loc[:HOLDOUT_LAST_DATE]

    by_index = {r["i"]: r for r in signal_rows}
    pending: list[tuple[int, dict]] = []   # (fill index, targets)

    positions: dict[str, dict] = {}        # ticker -> {shares, value}
    cash = START_NAV
    prev_date = None
    half_slip = (slippage_bp / 2.0) / 1e4
    comm = commission_fn or default_commission
    def half_slip_of(date, ticker):
        if slip_fn is None:
            return half_slip
        return (slip_fn(date, ticker) / 2.0) / 1e4

    daily = []
    orders = []
    unavailable_fills = []
    cap_events = []
    start_i = config.WARMUP_SESSIONS

    for i in range(start_i, len(cal)):
        date = cal[i]
        if prev_date is not None:
            if rf_factors is None:
                span = rf.loc[prev_date + pd.Timedelta(days=1): date]
                cash *= float(span.prod())
            else:
                # Session 17: the same product, precomputed per calendar
                # position. Bit-exactness asserted in s17_common.
                cash *= rf_factors[i]
        # Mark positions to today's close (1.3 total-return accumulation)
        # and apply real split factors to share counts.
        for t, p in positions.items():
            r = ret[t][i]
            if math.isnan(r):
                raise AssertionError(f"return unavailable mid-hold: {t} {date.date()}")
            p["value"] *= (1.0 + r)
            s = splitf[t][i]
            if s and not math.isnan(s) and s > 0:
                p["shares"] *= s

        transition = False
        while pending and pending[0][0] <= i:
            fill_i, targets = pending.pop(0)
            transition = True
            nav = sum(p["value"] for p in positions.values()) + cash
            # Which targets are fillable at this session's raw close?
            fillable = {}
            for t, w in targets.items():
                px = raw[t][i]
                if math.isnan(px) or px <= 0:
                    unavailable_fills.append(
                        {"date": date, "ticker": t, "weight": w, "bp": slippage_bp})
                else:
                    fillable[t] = (w, float(px))
            # Delta trading toward integer target share counts (source
            # _rebalance structure; sizing at the fill-session raw close
            # per 4.7 / src.execution.size_position semantics).
            #
            # Session 14 step 0b: participation cap (4.6). cap_fn(i, ticker)
            # returns the maximum dollar position admissible at the fill
            # session, from a point-in-time trailing denominator. The capped
            # remainder is simply not bought, so it stays in portfolio cash
            # accruing DTB3 through the existing unfilled-slice path (1.9,
            # 2.11); no new accounting path is created. Universal: the
            # machinery applies to every instrument on identical terms.
            target_shares = {}
            for t, (w, px) in fillable.items():
                alloc = nav * w
                if cap_fn is not None:
                    lim = cap_fn(i, t)
                    if lim is not None and lim < alloc:
                        cap_events.append(
                            {"date": date, "ticker": t, "target_dollars": alloc,
                             "cap_dollars": lim, "dollars_to_cash": alloc - lim,
                             "nav": nav})
                        alloc = lim
                target_shares[t] = math.trunc(alloc / px)
            # Sells first (including full liquidation of non-targets).
            for t in list(positions):
                cur = positions[t]
                tgt = target_shares.get(t, 0)
                if cur["shares"] > tgt:
                    dshares = cur["shares"] - tgt
                    px = raw[t][i]
                    if math.isnan(px) or px <= 0:
                        # Cannot price the sale; the position is carried.
                        unavailable_fills.append(
                            {"date": date, "ticker": t, "weight": None, "bp": slippage_bp})
                        continue
                    frac = dshares / cur["shares"]
                    proceeds = cur["value"] * frac
                    order_value = dshares * px
                    c_ = comm(date, t, "sell", dshares, order_value)
                    slip = half_slip_of(date, t) * order_value
                    cash += proceeds - c_ - slip
                    cur["value"] -= proceeds
                    cur["shares"] -= dshares
                    orders.append({"date": date, "ticker": t, "side": "sell",
                                   "shares": dshares, "value": order_value,
                                   "commission": c_, "slippage": slip})
                    if cur["shares"] <= 0:
                        del positions[t]
            # Buys.
            for t, (w, px) in fillable.items():
                tgt = target_shares[t]
                cur = positions.get(t)
                have = cur["shares"] if cur else 0
                if tgt > have:
                    dshares = tgt - have
                    order_value = dshares * px
                    c_ = comm(date, t, "buy", dshares, order_value)
                    slip = half_slip_of(date, t) * order_value
                    cash -= order_value + c_ + slip
                    if cur:
                        cur["shares"] += dshares
                        cur["value"] += order_value
                    else:
                        positions[t] = {"shares": dshares, "value": order_value}
                    orders.append({"date": date, "ticker": t, "side": "buy",
                                   "shares": dshares, "value": order_value,
                                   "commission": c_, "slippage": slip})

        # Signal evaluated at today's close fills at t + fill_lag.
        srow = by_index.get(i)
        if srow is not None and srow["changed"] and srow["targets"] is not None:
            if i + fill_lag < len(cal):
                pending.append((i + fill_lag, srow["targets"]))

        pos_value = sum(p["value"] for p in positions.values())
        nav = pos_value + cash
        daily.append({
            "date": date, "i": i, "nav": nav, "cash": cash,
            "pos_value": pos_value, "transition": transition,
            "weights": {t: p["value"] / nav for t, p in positions.items()},
        })
        prev_date = date

    df = pd.DataFrame(daily).set_index("date")
    df["ret"] = df["nav"] / df["nav"].shift(1) - 1.0
    return {"daily": df, "orders": pd.DataFrame(orders),
            "unavailable_fills": pd.DataFrame(unavailable_fills),
            "cap_events": pd.DataFrame(cap_events),
            "raw_rows": daily}


# ---------------------------------------------------------------------------
# Metrics (8.1, 8.2)
# ---------------------------------------------------------------------------

def rf_per_session(dates: pd.DatetimeIndex) -> pd.Series:
    rf = risk_free_daily_factors(load_risk_free_series()).loc[:HOLDOUT_LAST_DATE]
    out = [np.nan]
    for a, b in zip(dates[:-1], dates[1:]):
        out.append(float(rf.loc[a + pd.Timedelta(days=1): b].prod()) - 1.0)
    return pd.Series(out, index=dates)


def lo_sharpe(excess: pd.Series, q: int = 252) -> float:
    """Lo (2002) autocorrelation-corrected annualised Sharpe."""
    x = excess.dropna().to_numpy()
    mu, sd = x.mean(), x.std(ddof=1)
    if sd == 0:
        return np.nan
    sr = mu / sd
    n = len(x)
    xc = x - mu
    denom = float(np.dot(xc, xc))
    acf_sum = 0.0
    for k in range(1, q):
        rho = float(np.dot(xc[:-k], xc[k:])) / denom
        acf_sum += (q - k) * rho
    scale_sq = q + 2.0 * acf_sum
    if scale_sq <= 0:
        return np.nan
    return sr * q / math.sqrt(scale_sq)


def headline_metrics(daily: pd.DataFrame, orders: pd.DataFrame) -> dict:
    nav = daily["nav"]
    r = daily["ret"].dropna()
    n = len(r)
    years = n / 252.0
    total = nav.iloc[-1] / nav.iloc[0] - 1.0
    ann = (nav.iloc[-1] / nav.iloc[0]) ** (1.0 / years) - 1.0
    vol = r.std(ddof=1) * math.sqrt(252.0)
    rf = rf_per_session(daily.index)
    excess = (daily["ret"] - rf).dropna()
    sr_naive = excess.mean() / excess.std(ddof=1) * math.sqrt(252.0) if excess.std(ddof=1) > 0 else np.nan
    sr_lo = lo_sharpe(excess)
    dd = nav / nav.cummax() - 1.0
    mdd = dd.min()
    calmar = ann / abs(mdd) if mdd < 0 else np.nan
    if len(orders):
        one_sided = orders["value"].sum() / 2.0
        turn = one_sided / nav.mean() / years
        commission = orders["commission"].sum()
        slippage = orders["slippage"].sum()
    else:
        turn, commission, slippage = 0.0, 0.0, 0.0
    return {
        "total_return": total, "ann_return": ann, "ann_vol": vol,
        "sharpe_naive": sr_naive, "sharpe_lo": sr_lo,
        "max_drawdown": mdd, "calmar": calmar,
        "ann_turnover_one_sided": turn,
        "total_commission": commission, "total_slippage": slippage,
        "end_nav": nav.iloc[-1], "n_sessions": len(nav), "years": years,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main() -> None:
    print("== loading arms with holdout truncation ==")
    panels = {"synthetic": load_arm_panel("synthetic"),
              "realized": load_arm_panel("realized")}
    for arm, p in panels.items():
        ok, mx = assert_holdout(p)
        print(f"holdout assertion [{arm}]: PASS, max loaded date {mx.date()}")

    cal = panels["synthetic"]["SPY"].index
    assert cal.equals(panels["realized"]["SPY"].index)
    print(f"calendar: {cal[0].date()} .. {cal[-1].date()}, {len(cal)} sessions")
    print(f"warm-up: first signal index {config.WARMUP_SESSIONS} "
          f"({cal[config.WARMUP_SESSIONS].date()}), first fill "
          f"{cal[config.WARMUP_SESSIONS + 1].date()}")

    signals, accounts = {}, {}
    for arm in ("synthetic", "realized"):
        sig = ArmSignals(panels[arm], cal)
        signals[arm] = {"sig": sig, **run_signals(sig)}
        n_tr = sum(1 for r in signals[arm]["rows"] if r["changed"])
        print(f"[{arm}] evaluated {len(signals[arm]['rows'])} sessions, "
              f"{n_tr} transitions, {len(signals[arm]['raises'])} raise events")
        accounts[arm] = {}
        for bp in config.SLIPPAGE_BASE_GRID_BP:
            accounts[arm][bp] = run_account(sig, panels[arm],
                                            signals[arm]["rows"], bp)
        print(f"[{arm}] accounts done")

    # Lookahead check: one extra session of lag, primary arm, 10 bp anchor.
    lag = run_account(signals["synthetic"]["sig"], panels["synthetic"],
                      signals["synthetic"]["rows"], 10, fill_lag=2)

    # Persist intermediates for the diagnostics stage.
    store = {"calendar": cal, "signals": signals, "accounts": accounts,
             "lag_check": lag, "panels": panels}
    import pickle
    with open(OUT / "_state.pkl", "wb") as fh:
        pickle.dump({
            "signal_rows": {a: signals[a]["rows"] for a in signals},
            "raises": {a: signals[a]["raises"] for a in signals},
        }, fh)

    # Headline table.
    rows = []
    for arm in ("synthetic", "realized"):
        for bp in config.SLIPPAGE_BASE_GRID_BP:
            m = headline_metrics(accounts[arm][bp]["daily"], accounts[arm][bp]["orders"])
            rows.append({"arm": arm, "slippage_bp": bp, **m})
    hl = pd.DataFrame(rows)
    hl.to_csv(OUT / "headline-results.csv", index=False)
    print(hl.to_string(index=False))

    m_lag = headline_metrics(lag["daily"], lag["orders"])
    pd.DataFrame([{"check": "fill_lag_2_anchor10bp", **m_lag}]).to_csv(
        OUT / "_lag-check.csv", index=False)
    print("lag check (T+2 fills, 10bp):",
          {k: round(v, 4) for k, v in m_lag.items() if isinstance(v, float)})

    print("unavailable fills (synthetic, 10bp):",
          len(accounts["synthetic"][10]["unavailable_fills"]))
    print("unavailable fills (realized, 10bp):",
          len(accounts["realized"][10]["unavailable_fills"]))

    return store


if __name__ == "__main__":
    main()
