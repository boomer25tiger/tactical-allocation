"""Unit tests for src/execution.py. All frames are hand-constructed; nothing
under data/ is opened and no performance statistic is computed."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.data import build_ticker_frame  # noqa: E402
from src.execution import (  # noqa: E402
    accrue_cash,
    degenerate_open_to_open,
    execute_transition,
    fill_series,
    fill_session,
    size_position,
)


def frame(n=6, open_=None, close=None, adj=None, start="2020-01-01"):
    idx = pd.date_range(start, periods=n, freq="B")
    close = np.asarray(close if close is not None else np.linspace(100, 105, n), float)
    open_ = np.asarray(open_ if open_ is not None else close - 1.0, float)
    adj = np.asarray(adj if adj is not None else close * 0.8, float)
    raw = pd.DataFrame(
        {
            "Open": open_, "High": close + 1, "Low": open_ - 1, "Close": close,
            "Adj Close": adj, "Volume": np.full(n, 1e5),
            "Dividends": np.zeros(n), "Stock Splits": np.zeros(n),
            "Capital Gains": np.zeros(n),
        },
        index=idx,
    )
    return build_ticker_frame("TEST", raw)


def nav_frame(n=6):
    """NAV-priced series: Open == Close on every row, like RYMFX."""
    close = np.linspace(50, 55, n)
    return frame(n=n, open_=close.copy(), close=close)


# ---------------------------------------------------------------------------
# Mode selection: one parameterised path (4.1)
# ---------------------------------------------------------------------------

def test_fill_series_close_to_close_is_adj_close():
    f = frame()
    pd.testing.assert_series_equal(fill_series(f, "close_to_close"), f.adj_close)


def test_fill_series_open_to_open_is_adj_open():
    f = frame()
    pd.testing.assert_series_equal(fill_series(f, "open_to_open"), f.adj_open)


def test_fill_series_default_mode_comes_from_config():
    f = frame()
    pd.testing.assert_series_equal(fill_series(f), fill_series(f, config.EXECUTION_MODE))


def test_fill_series_rejects_unknown_mode():
    with pytest.raises(ValueError, match="EXECUTION_MODE"):
        fill_series(frame(), "at_the_mid")


def test_modes_coincide_exactly_on_degenerate_series():
    f = nav_frame()
    a = fill_series(f, "close_to_close").to_numpy()
    b = fill_series(f, "open_to_open").to_numpy()
    np.testing.assert_allclose(a, b, rtol=1e-12)


# ---------------------------------------------------------------------------
# T+1 fill timing (4.1)
# ---------------------------------------------------------------------------

def test_fill_is_next_session():
    cal = frame(n=6).index
    assert fill_session(cal, cal[2]) == cal[3]


def test_fill_skips_weekend_via_calendar():
    cal = pd.DatetimeIndex(pd.date_range("2020-01-01", periods=10, freq="B"))
    fri = pd.Timestamp("2020-01-03")
    assert fill_session(cal, fri) == pd.Timestamp("2020-01-06")  # Monday


def test_no_fill_after_final_session():
    cal = frame(n=4).index
    assert fill_session(cal, cal[-1]) is None


def test_signal_off_calendar_raises():
    cal = frame(n=4).index
    with pytest.raises(KeyError, match="not on the trading calendar"):
        fill_session(cal, "2019-06-15")


# ---------------------------------------------------------------------------
# Sizing (4.7) and residual cash (5.5)
# ---------------------------------------------------------------------------

def test_fractional_shares_exact_no_residual():
    shares, residual = size_position(50.0, 3.0, "fractional")
    assert shares == pytest.approx(50.0 / 3.0)
    assert residual == 0.0


def test_truncate_whole_shares_with_residual():
    shares, residual = size_position(50.0, 3.0, "truncate")
    assert shares == 16.0
    assert residual == pytest.approx(50.0 - 48.0)


def test_truncate_exact_multiple_leaves_no_residual():
    shares, residual = size_position(9.0, 3.0, "truncate")
    assert shares == 3.0 and residual == pytest.approx(0.0)


def test_sizing_rejects_bad_price():
    for bad in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            size_position(10.0, bad)


def test_sizing_rejects_unknown_mode():
    with pytest.raises(ValueError, match="SIZING_MODE"):
        size_position(10.0, 1.0, "round_up")


def rate_series(values, start, freq="B"):
    """Synthetic business-day rate series in percent, like the frozen DTB3
    shape. The frozen file itself is never read in tests."""
    idx = pd.date_range(start, periods=len(values), freq=freq)
    return pd.Series(np.asarray(values, dtype=float), index=idx, name="DTB3")


def test_accrue_cash_weekend_span_earns_three_days():
    """5.5a calendar-day accrual: Friday close -> Monday close earns
    Saturday, Sunday, and Monday at rate/360."""
    from src.data import risk_free_daily_factors

    # Mon 2020-01-06 .. Mon 2020-01-13 business days, constant 3.6%
    factors = risk_free_daily_factors(rate_series([3.6] * 6, "2020-01-06"))
    daily = 1.0 + 0.036 / config.RISK_FREE_DAY_COUNT
    got = accrue_cash(100.0, factors, "2020-01-10", "2020-01-13")  # Fri -> Mon
    assert got == pytest.approx(100.0 * daily**3)


def test_accrue_cash_holiday_span_carries_published_rate():
    """A null published day inside the span accrues at the carried rate."""
    from src.data import risk_free_daily_factors

    # Wed 4.0, Thu null (holiday), Fri 4.0 -> Thu carries Wednesday's 4.0
    factors = risk_free_daily_factors(
        rate_series([4.0, np.nan, 4.0], "2020-01-08"))
    daily = 1.0 + 0.04 / config.RISK_FREE_DAY_COUNT
    got = accrue_cash(100.0, factors, "2020-01-08", "2020-01-10")  # Wed -> Fri
    assert got == pytest.approx(100.0 * daily**2)


def test_accrue_cash_zero_span_is_identity():
    from src.data import risk_free_daily_factors

    factors = risk_free_daily_factors(rate_series([3.6] * 4, "2020-01-06"))
    assert accrue_cash(100.0, factors, "2020-01-07", "2020-01-07") == 100.0


def test_accrue_cash_negative_rate_shrinks_cash():
    from src.data import risk_free_daily_factors

    factors = risk_free_daily_factors(rate_series([-0.05] * 4, "2020-01-06"))
    got = accrue_cash(100.0, factors, "2020-01-06", "2020-01-08")
    assert got < 100.0


def test_accrue_cash_reversed_span_raises():
    from src.data import risk_free_daily_factors

    factors = risk_free_daily_factors(rate_series([3.6] * 4, "2020-01-06"))
    with pytest.raises(ValueError, match="precedes"):
        accrue_cash(100.0, factors, "2020-01-09", "2020-01-06")


def test_accrue_cash_leading_unavailable_raises():
    """Days before the first published rate are unavailable, not zero-rate."""
    from src.data import risk_free_daily_factors

    factors = risk_free_daily_factors(
        rate_series([np.nan, np.nan, 3.6, 3.6], "2020-01-06"))
    with pytest.raises(ValueError, match="unavailable"):
        accrue_cash(100.0, factors, "2020-01-06", "2020-01-08")


def test_accrue_cash_span_outside_factor_coverage_raises():
    from src.data import risk_free_daily_factors

    factors = risk_free_daily_factors(rate_series([3.6] * 4, "2020-01-06"))
    with pytest.raises(ValueError, match="covers"):
        accrue_cash(100.0, factors, "2020-01-06", "2020-03-01")


# ---------------------------------------------------------------------------
# Transition execution
# ---------------------------------------------------------------------------

def test_execute_transition_fractional():
    fills, residual = execute_transition(
        nav=1000.0,
        targets={"A": 0.25, "B": 0.25},
        raw_prices_t1={"A": 10.0, "B": 40.0},
        sizing="fractional",
    )
    assert fills["A"].shares == pytest.approx(25.0)
    assert fills["B"].shares == pytest.approx(6.25)
    assert residual == 0.0


def test_execute_transition_truncate_accumulates_residual():
    fills, residual = execute_transition(
        nav=1000.0,
        targets={"A": 0.25, "B": 0.25},
        raw_prices_t1={"A": 6.0, "B": 40.0},
        sizing="truncate",
    )
    assert fills["A"].shares == 41.0  # 250/6 = 41.67 -> 41
    assert fills["B"].shares == 6.0   # 250/40 = 6.25 -> 6
    assert residual == pytest.approx((250 - 41 * 6.0) + (250 - 6 * 40.0))


def test_execute_transition_separates_fill_and_raw_prices():
    """Share counts on raw close; accumulation price is the mode series."""
    fills, _ = execute_transition(
        nav=100.0,
        targets={"A": 1.0},
        raw_prices_t1={"A": 20.0},
        sizing="fractional",
        fill_prices_t1={"A": 16.0},  # adjusted path differs from raw
    )
    assert fills["A"].shares == pytest.approx(5.0)   # 100/20, raw
    assert fills["A"].fill_price == 16.0
    assert fills["A"].raw_price == 20.0


def test_execute_transition_missing_fill_price_raises():
    with pytest.raises(NotImplementedError, match="fill price unavailable for B"):
        execute_transition(
            nav=100.0,
            targets={"A": 0.5, "B": 0.5},
            raw_prices_t1={"A": 10.0},
        )


# ---------------------------------------------------------------------------
# Degenerate-series detection
# ---------------------------------------------------------------------------

def test_degenerate_detection_flags_nav_series_only():
    frames = {"NAVLIKE": nav_frame(), "NORMAL": frame()}
    assert degenerate_open_to_open(frames) == ["NAVLIKE"]


def test_degenerate_detection_is_general_multiple_cases():
    frames = {"N1": nav_frame(), "N2": nav_frame(8), "OK": frame()}
    assert degenerate_open_to_open(frames) == ["N1", "N2"]


def test_degenerate_detection_tolerates_nulls():
    close = np.linspace(50, 55, 8)
    f = frame(n=8, open_=close.copy(), close=close)
    holed = f.frame.copy()
    holed.iloc[3, holed.columns.get_loc("adj_open")] = np.nan
    from src.data import TickerFrame

    frames = {"HOLED": TickerFrame("HOLED", holed)}
    assert degenerate_open_to_open(frames) == ["HOLED"]


def test_degenerate_detection_all_null_series_not_flagged():
    f = frame()
    empty = f.frame.copy()
    empty["adj_open"] = np.nan
    from src.data import TickerFrame

    assert degenerate_open_to_open({"EMPTY": TickerFrame("EMPTY", empty)}) == []


def test_one_intraday_move_defeats_degeneracy():
    close = np.linspace(50, 55, 8)
    open_ = close.copy()
    open_[4] = close[4] - 0.75  # a single genuine open-close spread
    frames = {"ALMOST": frame(n=8, open_=open_, close=close)}
    assert degenerate_open_to_open(frames) == []
