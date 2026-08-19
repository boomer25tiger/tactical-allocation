"""Sleeve weight functions: t10_weights, t11_weights, s2_weights, s3_weights.

Structure follows docs/source-quantconnect.py exactly: the T10 cascade order,
the two-tier overbought structure in T11, the 50/50 split across the two T11
bear sub-models, the TQQQ gate in S2, and the four-vote count in S3. Every
numeric parameter comes from src/config.py; nothing numeric is taken from
source (the divergences are recorded in
outputs/session-01/parameter-divergence.csv).

Weights are fractions of the sleeve's own budget: a sleeve fully invested in
one name returns {ticker: 1.0}, and cash is the empty dict. Source expresses
the same states as fractions of total capital (QUARTER = 0.25); the mapping
is source QUARTER == 1.0 here. Scaling by the sleeve budget happens once, in
src/portfolio.py.

Four substitutions against source:

1. Every KMLM signal reference becomes config.TREND_SIGNAL_SERIES (decision
   2.5; RYMFX, read at a one-session lag applied in src/data.py per 2.5a).
   KMLM appears in no weight dictionary in source, so no held position
   changes.
2. The hardcoded crash test qqq_60d < -12 becomes a comparison of the
   trailing CRASH_HORIZON_SESSIONS QQQ total return against
   CRASH_THRESHOLD_PCT (decision 6.10: the rolling quantile was withdrawn
   in session 04 and the absolute threshold re-closed at -15 in session
   09; the canonical value lives in config, which this module reads --
   docstring corrected by session 13.9, D4). The test is a threshold test:
   an unavailable return -- including the boundary where the horizon has
   not yet accumulated -- reads false per 1.9.
3. The permissive fallback (not kmlm_ready) or (r["XLK"] > r["KMLM"]) is
   removed. It routed to risk-on whenever the trend series was unready — a
   directional assumption, not a neutral default. The pairwise rule below
   replaces it.
4. Every per-name threshold exception collapses to the tier values in
   config: single-tier overbought sites take OVERBOUGHT_TIER_1, T11's two
   tiers take OVERBOUGHT_TIER_1 / OVERBOUGHT_TIER_2, and every oversold site
   takes OVERSOLD (A1 resolved dip sites included).

Unavailable inputs (the settled half of decision 2.11, matching 1.9):

  * A threshold test whose input is unavailable reads false. This covers
    RSI-against-constant tests, price-against-own-SMA tests (including the
    four S3 votes, which therefore read bearish when unavailable), and the
    crash test.
  * A pairwise comparison (RSI against RSI across instruments) with either
    side unavailable raises NotImplementedError naming the call site. No
    default is chosen; the raise marks where the open half of 2.11 lands.
    The nine sites are listed in PAIRWISE_SITES.

One construct source expresses through date guards that this implementation
may not carry (date guards on instrument availability are excluded from what
is taken from source): the SVIX-else-SVXY switch in T10 (source line 198,
guard SVIX_LIVE = 2022-03-30) and the UVIX-else-UVXY switch in S3 (source
lines 286-290, guard UVIX_LIVE plus a has_data check). Both are implemented
as availability switches on the state object — use the later-listed
instrument when its bar is available at the signal date, else the earlier
one. That is source's own has_data logic minus the hardcoded date, expressed
through the study's 1.9 availability notion. Flagged in the session report.
"""

from __future__ import annotations

import math
from typing import Protocol

from src import config

__all__ = [
    "IndicatorState",
    "t10_weights",
    "t11_weights",
    "s2_weights",
    "s3_weights",
    "PAIRWISE_SITES",
    "T10_CASCADE",
    "T11_PANEL",
    "S3_VOTES",
]

# Ticker sets, taken from source (structure, not parameters).
T10_CASCADE = ("QQQE", "VTV", "VOX", "TECL", "VOOG", "VOOV", "XLP",
               "TQQQ", "XLY", "FAS", "SPY")
T11_PANEL = ("SPY", "IOO", "TQQQ", "VTV", "XLF")
S3_VOTES = ("SPY", "QQQ", "SMH", "SOXL")

# Every pairwise call site that can raise, for tests and the report.
PAIRWISE_SITES = (
    "t10_weights:XLK>TREND",
    "t11_weights:XLK>TREND",
    "t11_bond_baller:TLT>PSQ",
    "t11_bond_baller:AGG>SH",
    "t11_bond_baller:IEF>PSQ",
    "t11_feaver_bear:BND>QQQ",
    "t11_feaver_bear:AGG>SH",
    "t11_feaver_bear:IEF>PSQ",
    "s2_weights:SQQQ>BSV",
)


class IndicatorState(Protocol):
    """Indicator values at one signal date. None means unavailable (1.9).

    The three RSI accessors are function-tied per decision 6.1 and the
    confirmed mapping in outputs/session-01/rsi-function-mapping.md. All
    three take period 14 under the canonical spec; the accessors exist so the
    grid can vary them independently.

    The trend series is read through config.TREND_SIGNAL_SERIES like any
    other ticker; its 2.5a lag is already applied at load time.
    """

    def rsi_exhaustion(self, ticker: str) -> float | None: ...
    def rsi_dip(self, ticker: str) -> float | None: ...
    def rsi_rs(self, ticker: str) -> float | None: ...
    def price(self, ticker: str) -> float | None: ...
    def sma(self, ticker: str, length: int) -> float | None: ...
    def trailing_return_pct(self, ticker: str, horizon: int) -> float | None: ...
    def available(self, ticker: str) -> bool: ...


# ---------------------------------------------------------------------------
# Unavailable-input rule
# ---------------------------------------------------------------------------

def _avail(x: float | None) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def _gt(value: float | None, bound: float) -> bool:
    """Threshold test; unavailable reads false (1.9)."""
    return _avail(value) and value > bound


def _lt(value: float | None, bound: float) -> bool:
    """Threshold test; unavailable reads false (1.9)."""
    return _avail(value) and value < bound


def _pairwise_gt(a: float | None, b: float | None, site: str) -> bool:
    """Pairwise comparison; either side unavailable raises (open half of 2.11)."""
    if not _avail(a) or not _avail(b):
        raise NotImplementedError(
            f"pairwise comparison with unavailable input at {site}; "
            "the open half of decision 2.11 lands here"
        )
    return a > b


def _price_above_sma(state: IndicatorState, ticker: str, length: int) -> bool:
    """Threshold test with a derived threshold; unavailable reads false."""
    p, m = state.price(ticker), state.sma(ticker, length)
    return _avail(p) and _avail(m) and p > m


def _price_below_sma(state: IndicatorState, ticker: str, length: int) -> bool:
    """Not the negation of _price_above_sma: unavailable reads false on both."""
    p, m = state.price(ticker), state.sma(ticker, length)
    return _avail(p) and _avail(m) and p < m


# ---------------------------------------------------------------------------
# T10 — eleven-name overbought cascade (register's S1; source's T10)
# ---------------------------------------------------------------------------

def t10_weights(date, state: IndicatorState) -> dict[str, float]:
    ex, dip, rs = state.rsi_exhaustion, state.rsi_dip, state.rsi_rs

    # Cascade, source order preserved (source L188-192).
    if any(_gt(ex(t), config.OVERBOUGHT_TIER_1) for t in T10_CASCADE):
        return {"UVXY": 1.0}

    # Dip-buys, source order preserved (L193-197).
    if _lt(dip("TQQQ"), config.OVERSOLD):
        return {"TECL": 1.0}
    if _lt(dip("SOXL"), config.OVERSOLD):
        return {"SOXL": 1.0}
    if _lt(dip("SPXL"), config.OVERSOLD):
        return {"SPXL": 1.0}
    if _lt(dip("LABU"), config.OVERSOLD):
        return {"LABU": 1.0}

    # Availability switch replacing the SVIX_LIVE date guard (L198); flagged.
    vol_short = "SVIX" if state.available("SVIX") else "SVXY"

    # Relative strength, XLK against the trend series (L199-204). The
    # permissive not-ready fallback is removed (substitution 3).
    if _pairwise_gt(rs("XLK"), rs(config.TREND_SIGNAL_SERIES),
                    "t10_weights:XLK>TREND"):
        return {"TECL": 1 / 3, "SOXL": 1 / 3, vol_short: 1 / 3}
    return {"SQQQ": 0.5, "TLT": 0.5}


# ---------------------------------------------------------------------------
# T11 — two-tier overbought, trend switcher, 50/50 bear split
# ---------------------------------------------------------------------------

def _t11_bond_baller(state: IndicatorState) -> str:
    """Bear sub-model 1 (source L155-163). Returns a single ticker."""
    dip, rs = state.rsi_dip, state.rsi_rs
    if _pairwise_gt(rs("TLT"), rs("PSQ"), "t11_bond_baller:TLT>PSQ"):
        return "QQQ"
    if _price_above_sma(state, "TQQQ", config.SMA_SHORT):
        if _lt(dip("PSQ"), config.OVERSOLD):  # A1 resolved to dip; 35 -> 30
            return "PSQ"
        if _pairwise_gt(rs("AGG"), rs("SH"), "t11_bond_baller:AGG>SH"):
            return "TQQQ"
        return "PSQ"
    if _pairwise_gt(rs("IEF"), rs("PSQ"), "t11_bond_baller:IEF>PSQ"):
        return "PSQ"
    return "SQQQ"


def _t11_feaver_bear(state: IndicatorState) -> str:
    """Bear sub-model 2 (source L165-180). Returns a single ticker.

    The crash test replaces source's hardcoded qqq_60d < -12 with the
    absolute threshold of 6.10 as re-closed in session 04: the trailing
    CRASH_HORIZON_SESSIONS total return of CRASH_REFERENCE_TICKER against
    CRASH_THRESHOLD_PCT, strict less-than, both in percent. It is a
    threshold test: an unavailable return -- the horizon not yet
    accumulated, or the reference series missing -- reads false per 1.9.
    """
    dip, rs = state.rsi_dip, state.rsi_rs
    crash_input = state.trailing_return_pct(
        config.CRASH_REFERENCE_TICKER, config.CRASH_HORIZON_SESSIONS
    )
    if _lt(crash_input, config.CRASH_THRESHOLD_PCT):
        if _pairwise_gt(rs("BND"), rs("QQQ"), "t11_feaver_bear:BND>QQQ"):
            return "QLD"
        return "BTAL"
    if _price_above_sma(state, "TQQQ", config.SMA_SHORT):
        if _lt(dip("PSQ"), config.OVERSOLD):
            return "PSQ"
        if _pairwise_gt(rs("AGG"), rs("SH"), "t11_feaver_bear:AGG>SH"):
            return "TQQQ"
        return "PSQ"
    if _pairwise_gt(rs("IEF"), rs("PSQ"), "t11_feaver_bear:IEF>PSQ"):
        return "PSQ"
    return "SQQQ"


def t11_weights(date, state: IndicatorState) -> dict[str, float]:
    ex, dip, rs = state.rsi_exhaustion, state.rsi_dip, state.rsi_rs

    # Two-tier overbought (source L220-229).
    if any(_gt(ex(t), config.OVERBOUGHT_TIER_1) for t in T11_PANEL):
        if any(_gt(ex(t), config.OVERBOUGHT_TIER_2) for t in T11_PANEL):
            return {"UVXY": 1.0}
        return {"UVXY": 1 / 3, "BIL": 1 / 3, "BTAL": 1 / 3}

    # Dips (L230-231).
    if _lt(dip("TQQQ"), config.OVERSOLD):
        return {"TQQQ": 1.0}
    if _lt(dip("SPY"), config.OVERSOLD):
        return {"SPXL": 1.0}

    # Bull side: trend switcher (L233-245).
    if _price_above_sma(state, "SPY", config.SMA_LONG):
        if _pairwise_gt(rs("XLK"), rs(config.TREND_SIGNAL_SERIES),
                        "t11_weights:XLK>TREND"):
            return {"TECL": 1 / 3, "SOXL": 1 / 3, "TQQQ": 1 / 3}
        # Trend series won on RSI but sits below its own short SMA: signal
        # discounted, stay long (source L239-242 with KMLM -> TREND).
        if _price_below_sma(state, config.TREND_SIGNAL_SERIES, config.SMA_SHORT):
            return {"TECL": 1 / 3, "SOXL": 1 / 3, "TQQQ": 1 / 3}
        return {"TECS": 1 / 3, "SOXS": 1 / 3, "SQQQ": 1 / 3}

    # Bear side: 50/50 across the two sub-models (L246-252). If both pick the
    # same ticker the weights sum, exactly as source's get-accumulate does.
    bb = _t11_bond_baller(state)
    fb = _t11_feaver_bear(state)
    w: dict[str, float] = {}
    w[bb] = w.get(bb, 0.0) + 0.5
    w[fb] = w.get(fb, 0.0) + 0.5
    return w


# ---------------------------------------------------------------------------
# S2 — TQQQ 200-SMA gate with BSV defensive
# ---------------------------------------------------------------------------

def s2_weights(date, state: IndicatorState) -> dict[str, float]:
    ex, dip, rs = state.rsi_exhaustion, state.rsi_dip, state.rsi_rs

    # The gate (source L263-265).
    if _price_above_sma(state, "TQQQ", config.SMA_LONG):
        if _gt(ex("TQQQ"), config.OVERBOUGHT_TIER_1):
            return {"UVXY": 1.0}
        return {"TQQQ": 1.0}

    # Dips (L266-267).
    if _lt(dip("TQQQ"), config.OVERSOLD):
        return {"TECL": 1.0}
    if _lt(dip("SOXL"), config.OVERSOLD):
        return {"SOXL": 1.0}

    # Defensive split (L268-270).
    if _price_below_sma(state, "TQQQ", config.SMA_SHORT):
        if _pairwise_gt(rs("SQQQ"), rs("BSV"), "s2_weights:SQQQ>BSV"):
            return {"SQQQ": 1.0}
        return {"BSV": 1.0}

    return {"TQQQ": 1.0}


# ---------------------------------------------------------------------------
# S3 — four-vote SMA regime with RSI triggers
# ---------------------------------------------------------------------------

def s3_weights(date, state: IndicatorState) -> dict[str, float]:
    ex, dip = state.rsi_exhaustion, state.rsi_dip

    # Four votes (source L275-279). A vote whose input is unavailable reads
    # false, i.e. bearish, per the threshold rule.
    votes = sum(_price_above_sma(state, t, config.SMA_LONG) for t in S3_VOTES)
    bull = votes >= config.S3_VOTE_THRESHOLD

    overbought = any(_gt(ex(t), config.OVERBOUGHT_TIER_1) for t in S3_VOTES)

    if bull:
        if overbought:
            # Availability switch replacing the UVIX_LIVE date guard
            # (source L286-290); flagged.
            vol = "UVIX" if state.available("UVIX") else "UVXY"
            return {vol: 1.0}
        return {"TQQQ": 0.5, "SOXL": 0.5}

    # Bear-side dip trigger (L294-295).
    if _lt(dip("QQQ"), config.OVERSOLD) or _lt(dip("SMH"), config.OVERSOLD):
        return {"SOXL": 1.0}

    return {}  # cash
