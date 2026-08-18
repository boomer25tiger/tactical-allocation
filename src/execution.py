"""Execution layer.

Decision 4.1. The signal is stamped at the T close; the order fills at the
T+1 price of the configured mode; returns accumulate along the same mode
series. Both modes live in one code path parameterised by
config.EXECUTION_MODE:

    close_to_close   fills at the T+1 adjusted close, accumulation on
                     adjusted closes
    open_to_open     fills at the T+1 adjusted open (AdjOpen per 1.5),
                     accumulation on adjusted opens

Decision 4.7 / 5.5 / 5.5a. SIZING_MODE selects fractional shares or integer
truncation. Share counts are taken against the raw close (1.4). Under
truncation the residual accrues to sleeve cash at the risk-free rate
(RISK_FREE_SERIES, 8.1) under the 5.5a convention: rate / 360 per CALENDAR
day, earned on every day held including weekends and holidays. The daily
factors come from src.data.risk_free_daily_factors, which owns the
conversion and the null-day carry; this module multiplies factors across
the holding span and adds nothing of its own. (Session 01's provisional
rate/252-per-trading-session form was superseded by 5.5a in session 02 and
migrated here in session 04.)

Degenerate series. Under open_to_open, any series whose AdjOpen equals its
AdjClose on every row collapses the two modes into one. The detection below
is general — it reports every such series rather than special-casing the one
known case (RYMFX, NAV-priced, Open == Close on all 4,901 rows, established
by the step 0 verification gates). Detection reports; it never alters
behaviour.

Nothing in this module is run against data/ in this session; every function
is exercised on hand-constructed frames only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src import config
from src.data import TickerFrame

__all__ = [
    "fill_series",
    "fill_session",
    "size_position",
    "accrue_cash",
    "execute_transition",
    "degenerate_open_to_open",
    "Fill",
]

def _check_mode(mode: str) -> None:
    if mode not in config.EXECUTION_MODES:
        raise ValueError(f"unknown EXECUTION_MODE {mode!r}; one of {config.EXECUTION_MODES}")


def _check_sizing(sizing: str) -> None:
    if sizing not in config.SIZING_MODES:
        raise ValueError(f"unknown SIZING_MODE {sizing!r}; one of {config.SIZING_MODES}")


def fill_series(frame: TickerFrame, mode: str = config.EXECUTION_MODE) -> pd.Series:
    """The adjusted series fills and accumulation run on, by mode.

    One parameterised path: the mode selects the series; nothing downstream
    branches on the mode again.
    """
    _check_mode(mode)
    return frame.adj_close if mode == "close_to_close" else frame.adj_open


def fill_session(calendar: pd.DatetimeIndex, signal_date) -> pd.Timestamp | None:
    """T+1: the session after the signal date on the trading calendar.

    Returns None when the signal date is the final session (no fill exists);
    raises if the signal date is not on the calendar at all.
    """
    signal_date = pd.Timestamp(signal_date)
    i = calendar.get_indexer([signal_date])[0]
    if i == -1:
        raise KeyError(f"signal date {signal_date.date()} not on the trading calendar")
    if i + 1 >= len(calendar):
        return None
    return calendar[i + 1]


def size_position(
    allocation: float,
    raw_price: float,
    sizing: str = config.SIZING_MODE,
) -> tuple[float, float]:
    """Shares for a currency allocation at a raw-close price (1.4, 4.7).

    Returns (shares, residual). Fractional: exact shares, zero residual.
    Truncate: whole shares rounded toward zero, residual currency returned
    to the caller for sleeve cash (5.5).
    """
    _check_sizing(sizing)
    if not (isinstance(raw_price, (int, float)) and math.isfinite(raw_price)) or raw_price <= 0:
        raise ValueError(f"raw price must be a positive finite number, got {raw_price!r}")
    exact = allocation / raw_price
    if sizing == "fractional":
        return exact, 0.0
    whole = math.trunc(exact)
    return float(whole), allocation - whole * raw_price


def accrue_cash(
    cash: float,
    daily_factors: pd.Series,
    start,
    end,
) -> float:
    """Sleeve cash accrued from `start` to `end` at the risk-free rate (5.5a).

    `daily_factors` is the calendar-day factor series from
    src.data.risk_free_daily_factors -- one factor per calendar day,
    weekends and holidays included. The holding span accrues the factors of
    every calendar day strictly after `start` through `end` inclusive, so a
    Friday-to-Monday hold earns Saturday, Sunday, and Monday: three days,
    which is what the 5.5a calendar-day convention means. `start == end`
    accrues nothing.

    A NaN factor inside the span (only possible before the series' first
    published rate, since later nulls carry) is unavailable input: this
    raises rather than treating the day as zero-rate.
    """
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if end < start:
        raise ValueError(f"end {end.date()} precedes start {start.date()}")
    if end == start:
        return cash
    span = daily_factors.loc[start + pd.Timedelta(days=1): end]
    n_days = (end - start).days
    if len(span) != n_days:
        raise ValueError(
            f"factor series covers {len(span)} of {n_days} calendar days in "
            f"({start.date()}, {end.date()}]; accrual needs every day"
        )
    if span.isna().any():
        first_bad = span[span.isna()].index[0].date()
        raise ValueError(
            f"factor unavailable on {first_bad}, before the first published "
            "rate; cannot accrue across it"
        )
    return cash * float(span.prod())


@dataclass(frozen=True)
class Fill:
    """One instrument's fill at the T+1 session."""

    ticker: str
    shares: float
    fill_price: float  # mode-series price used for accumulation
    raw_price: float   # raw close used for share counts and commission
    residual: float    # currency returned to sleeve cash (truncate only)


def execute_transition(
    nav: float,
    targets: dict[str, float],
    raw_prices_t1: dict[str, float],
    sizing: str = config.SIZING_MODE,
    fill_prices_t1: dict[str, float] | None = None,
) -> tuple[dict[str, Fill], float]:
    """Turn target weights (signal at T) into fills at the T+1 session.

    `raw_prices_t1` are raw closes at the fill session, for share counts.
    `fill_prices_t1` are the mode-series prices at the fill session; they
    default to the raw prices in synthetic tests that do not distinguish the
    paths. Returns (fills by ticker, total residual cash).

    A target whose fill-session price is unavailable is a missing bar at the
    fill. Decision 1.9 makes the input unavailable; what execution does about
    it belongs to the open half of 2.11, so this raises NotImplementedError
    naming the instrument rather than choosing a default.
    """
    _check_sizing(sizing)
    fill_prices_t1 = fill_prices_t1 or raw_prices_t1
    fills: dict[str, Fill] = {}
    residual_total = 0.0
    for ticker, weight in targets.items():
        raw = raw_prices_t1.get(ticker)
        px = fill_prices_t1.get(ticker)
        if raw is None or px is None or not math.isfinite(raw) or not math.isfinite(px):
            raise NotImplementedError(
                f"fill price unavailable for {ticker} at the T+1 session; "
                "the open half of decision 2.11 lands here"
            )
        shares, residual = size_position(nav * weight, raw, sizing)
        fills[ticker] = Fill(ticker, shares, px, raw, residual)
        residual_total += residual
    return fills, residual_total


def degenerate_open_to_open(frames: dict[str, TickerFrame]) -> list[str]:
    """Every ticker whose AdjOpen equals AdjClose on all jointly-available rows.

    General detection per the session prompt: RYMFX is known to be degenerate,
    and the scan is over every frame so a second case cannot pass silently.
    Uses a tight numeric tolerance because AdjOpen is computed as
    Open * (AdjClose / Close) and float rounding can leave last-ulp
    differences even when Open == Close exactly.
    """
    out = []
    for ticker in sorted(frames):
        f = frames[ticker]
        ao, ac = f.adj_open, f.adj_close
        both = ao.notna() & ac.notna()
        if both.sum() == 0:
            continue
        if np.allclose(ao[both].to_numpy(), ac[both].to_numpy(), rtol=1e-12, atol=0.0):
            out.append(ticker)
    return out
