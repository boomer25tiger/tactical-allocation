"""Unit tests for src/data.py.

Every frame here is hand-constructed. Nothing under data/ is opened and no
strategy return, allocation or performance statistic is computed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import config  # noqa: E402
from src.data import (  # noqa: E402
    Panel,
    build_ticker_frame,
    load_panel,
    load_risk_free_series,
    risk_free_daily_factors,
)


def raw_frame(n=10, close=None, open_=None, div=None, adj=None, start="2020-01-01"):
    idx = pd.date_range(start, periods=n, freq="B")
    close = np.asarray(close if close is not None else np.linspace(100, 100 + n - 1, n), float)
    open_ = np.asarray(open_ if open_ is not None else close - 0.5, float)
    adj = np.asarray(adj if adj is not None else close * 0.9, float)
    div = np.asarray(div if div is not None else np.zeros(n), float)
    return pd.DataFrame(
        {
            "Open": open_, "High": close + 1, "Low": close - 1, "Close": close,
            "Adj Close": adj, "Volume": np.full(n, 1e6), "Dividends": div,
            "Stock Splits": np.zeros(n), "Capital Gains": np.zeros(n),
        },
        index=idx,
    )


# ---------------------------------------------------------------------------
# Construction, decisions 1.5 and 1.11
# ---------------------------------------------------------------------------

def test_adj_open_formula():
    """AdjOpen = Open * (AdjClose / Close), decision 1.5."""
    raw = raw_frame()
    tf = build_ticker_frame("TEST", raw)
    expected = raw["Open"] * (raw["Adj Close"] / raw["Close"])
    np.testing.assert_allclose(tf.adj_open.to_numpy(), expected.to_numpy())


def test_ret_total_includes_dividend_at_ex_date():
    """ret_total = (Close_t + Div_t) / Close_{t-1} - 1, decision 1.11."""
    div = np.zeros(10)
    div[5] = 2.0
    tf = build_ticker_frame("TEST", raw_frame(div=div))
    c = tf.raw_close
    assert tf.ret_total.iloc[5] == pytest.approx((c.iloc[5] + 2.0) / c.iloc[4] - 1.0)
    assert tf.frame["ret_price"].iloc[5] == pytest.approx(c.iloc[5] / c.iloc[4] - 1.0)
    assert tf.ret_total.iloc[5] > tf.frame["ret_price"].iloc[5]


def test_first_return_is_unavailable():
    tf = build_ticker_frame("TEST", raw_frame())
    assert np.isnan(tf.ret_total.iloc[0])


def test_tr_index_starts_at_one():
    tf = build_ticker_frame("TEST", raw_frame())
    assert tf.tr_index.iloc[0] == pytest.approx(1.0)


def test_two_paths_are_distinct():
    """The raw path must not be the adjusted path (1.4)."""
    tf = build_ticker_frame("TEST", raw_frame())
    assert not np.allclose(tf.raw_close.to_numpy(), tf.adj_close.to_numpy())
    assert not np.allclose(tf.raw_open.to_numpy(), tf.adj_open.to_numpy())


# ---------------------------------------------------------------------------
# Decision 1.9, unavailability propagates
# ---------------------------------------------------------------------------

def test_interior_hole_skipped_multiday_return():
    """The closed 1.9 skip treatment: the gap date is unavailable, the next
    available session carries a MULTI-DAY return from the last available
    close, and the total-return index continues (no restart, no flat fill).
    (Session 01's segment-restart regression test asserted a rebase to 1.0
    here; replaced by the skip pin.)"""
    close = np.linspace(100, 110, 11)
    close[5] = np.nan
    tf = build_ticker_frame("TEST", raw_frame(n=11, close=close))

    assert np.isnan(tf.ret_total.iloc[5]), "the gap date has no return"
    assert np.isnan(tf.tr_index.iloc[5]), "the gap date has no level"
    assert tf.tr_index.iloc[:5].notna().all(), "history before is unaffected"

    # post-gap: a two-day return off the last available close
    expected_ret = close[6] / close[4] - 1.0
    assert tf.ret_total.iloc[6] == pytest.approx(expected_ret)
    assert tf.tr_index.iloc[6] == pytest.approx(
        tf.tr_index.iloc[4] * (1.0 + expected_ret)
    ), "the index continues across the gap, it does not restart"
    assert tf.tr_index.iloc[7:].notna().all()


def test_tr_index_skip_differs_from_s00c_zero_fill():
    """00C's (1 + r.fillna(0)).cumprod() invents a flat session at the gap
    (and, with a missing close, a second flat session after it). Skip embeds
    the observed multi-day return instead. The two must differ at the gap
    date (level present vs absent) even though the post-gap LEVELS coincide
    on a series whose gap return equals the compounded single-day returns."""
    close = np.linspace(100, 110, 11)
    close[5] = np.nan
    tf = build_ticker_frame("TEST", raw_frame(n=11, close=close))
    s00c_style = (1.0 + tf.ret_total.fillna(0.0)).cumprod()
    assert np.isnan(tf.tr_index.iloc[5]) and not np.isnan(s00c_style.iloc[5]), (
        "zero-fill asserts a level at the gap; skip must not"
    )
    # and the return stream itself differs: zero-fill reads the gap as 0%
    assert tf.ret_total.iloc[6] != pytest.approx(0.0)


def test_adj_open_undefined_when_close_is_zero():
    close = np.linspace(100, 110, 11)
    close[3] = 0.0
    tf = build_ticker_frame("TEST", raw_frame(n=11, close=close))
    assert np.isnan(tf.adj_open.iloc[3])


# ---------------------------------------------------------------------------
# Decision 2.5a, the trend lag is applied exactly once
# ---------------------------------------------------------------------------

def test_trend_lag_shifts_by_configured_sessions():
    p = Panel()
    p.frames[config.TREND_SIGNAL_SERIES] = build_ticker_frame(
        config.TREND_SIGNAL_SERIES, raw_frame(n=10)
    )
    before = p[config.TREND_SIGNAL_SERIES].tr_index.copy()
    p.apply_trend_lag()
    after = p[config.TREND_SIGNAL_SERIES].tr_index

    lag = config.TREND_SIGNAL_LAG
    assert after.iloc[:lag].isna().all()
    np.testing.assert_allclose(
        after.iloc[lag:].to_numpy(), before.iloc[: len(before) - lag].to_numpy()
    )


def test_trend_lag_applied_twice_raises():
    p = Panel()
    p.frames[config.TREND_SIGNAL_SERIES] = build_ticker_frame(
        config.TREND_SIGNAL_SERIES, raw_frame()
    )
    p.apply_trend_lag()
    with pytest.raises(RuntimeError, match="already applied"):
        p.apply_trend_lag()


def test_assert_lag_applied_once_detects_zero_applications():
    p = Panel()
    p.frames[config.TREND_SIGNAL_SERIES] = build_ticker_frame(
        config.TREND_SIGNAL_SERIES, raw_frame()
    )
    with pytest.raises(AssertionError, match="exactly once"):
        p.assert_trend_lag_applied_once()
    p.apply_trend_lag()
    p.assert_trend_lag_applied_once()  # must not raise


def test_trend_lag_on_absent_series_raises():
    with pytest.raises(KeyError):
        Panel().apply_trend_lag()


def test_only_the_trend_series_is_lagged(tmp_path):
    for t in (config.TREND_SIGNAL_SERIES, "QQQ"):
        raw_frame().to_parquet(tmp_path / f"{t}.parquet")

    panel = load_panel([config.TREND_SIGNAL_SERIES, "QQQ"], root=tmp_path)
    panel.assert_trend_lag_applied_once()

    assert panel.lag_application_count(config.TREND_SIGNAL_SERIES) == 1
    assert panel.lag_application_count("QQQ") == 0
    assert panel["QQQ"].lag_applied == 0
    assert np.isnan(panel[config.TREND_SIGNAL_SERIES].tr_index.iloc[0])
    assert panel["QQQ"].tr_index.iloc[0] == pytest.approx(1.0)


def test_loader_can_skip_the_lag_for_diagnostics(tmp_path):
    raw_frame().to_parquet(tmp_path / f"{config.TREND_SIGNAL_SERIES}.parquet")
    panel = load_panel([config.TREND_SIGNAL_SERIES], root=tmp_path, apply_trend_lag=False)
    assert panel.lag_application_count(config.TREND_SIGNAL_SERIES) == 0
    with pytest.raises(AssertionError):
        panel.assert_trend_lag_applied_once()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_missing_columns_raise():
    with pytest.raises(ValueError, match="missing columns"):
        build_ticker_frame("TEST", raw_frame().drop(columns=["Adj Close"]))


def test_unsorted_index_raises():
    with pytest.raises(ValueError, match="sorted"):
        build_ticker_frame("TEST", raw_frame().iloc[::-1])


def test_duplicate_index_raises():
    raw = raw_frame(n=3)
    raw.index = [raw.index[0]] * 3
    with pytest.raises(ValueError, match="duplicate"):
        build_ticker_frame("TEST", raw)


def test_missing_parquet_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="NOPE"):
        load_panel(["NOPE"], root=tmp_path)


def test_missing_root_raises():
    with pytest.raises(FileNotFoundError, match="data root"):
        load_panel(["QQQ"], root="/nonexistent/path/xyz")


def test_calendar_is_the_union_of_members(tmp_path):
    raw_frame(n=5, start="2020-01-01").to_parquet(tmp_path / "A.parquet")
    raw_frame(n=5, start="2020-01-06").to_parquet(tmp_path / "B.parquet")
    cal = load_panel(["A", "B"], root=tmp_path).calendar()
    assert cal.is_monotonic_increasing
    assert not cal.has_duplicates
    assert len(cal) >= 5


# ---------------------------------------------------------------------------
# Risk-free accrual factors (5.5, 5.5a) -- synthetic input only; the frozen
# file is never read in tests
# ---------------------------------------------------------------------------

def rate_series(values, start="2020-01-06", freq="B"):
    """Business-day rate series in percent, like the frozen DTB3 shape."""
    idx = pd.date_range(start, periods=len(values), freq=freq)
    return pd.Series(np.asarray(values, dtype=float), index=idx, name="DTB3")


def test_factor_formula_percent_and_day_count():
    """3.6 percent -> 1 + 0.036/360 = 1.0001 per calendar day."""
    f = risk_free_daily_factors(rate_series([3.6, 3.6, 3.6, 3.6, 3.6]))
    assert f.dropna().iloc[0] == pytest.approx(1.0 + 0.036 / config.RISK_FREE_DAY_COUNT)
    assert f.dropna().iloc[0] == pytest.approx(1.0001)


def test_calendar_basis_covers_weekends_with_carried_rate():
    """Mon 2020-01-06 .. Fri 2020-01-10 input; Sat/Sun must carry Friday's
    rate, per 5.5a calendar-day accrual."""
    f = risk_free_daily_factors(rate_series([1.0, 1.0, 1.0, 1.0, 2.0],
                                            start="2020-01-06"))
    # input spans Mon..Fri; extend via a second week to include the weekend
    f2 = risk_free_daily_factors(rate_series([1.0, 1.0, 1.0, 1.0, 2.0, 3.0],
                                             start="2020-01-06"))
    sat, sun = pd.Timestamp("2020-01-11"), pd.Timestamp("2020-01-12")
    assert sat in f2.index and sun in f2.index
    expected = 1.0 + (2.0 / 100.0) / config.RISK_FREE_DAY_COUNT
    assert f2.loc[sat] == pytest.approx(expected)
    assert f2.loc[sun] == pytest.approx(expected)
    # the plain Mon..Fri series has no weekend inside its span
    assert sat not in f.index


def test_null_day_carries_last_published_rate():
    s = rate_series([4.0, np.nan, 4.5])
    f = risk_free_daily_factors(s)
    holiday = s.index[1]
    assert f.loc[holiday] == pytest.approx(1.0 + 0.04 / config.RISK_FREE_DAY_COUNT)


def test_leading_nulls_stay_unavailable_no_backfill():
    s = rate_series([np.nan, np.nan, 4.0, 4.0])
    f = risk_free_daily_factors(s)
    assert f.iloc[:2].isna().all()
    assert f.iloc[2:].notna().all()


def test_negative_and_zero_rates_are_real():
    f = risk_free_daily_factors(rate_series([-0.05, 0.0, 0.01]))
    vals = f.dropna()
    assert vals.iloc[0] < 1.0
    assert vals.loc[f.index[1]] == pytest.approx(1.0)


def test_compounding_across_period_is_product_of_factors():
    f = risk_free_daily_factors(rate_series([3.6] * 6)).dropna()
    growth = float(f.prod())
    n = len(f)
    assert growth == pytest.approx((1.0 + 0.036 / config.RISK_FREE_DAY_COUNT) ** n)


def test_day_count_read_from_config(monkeypatch):
    monkeypatch.setattr(config, "RISK_FREE_DAY_COUNT", 252)
    f = risk_free_daily_factors(rate_series([2.52, 2.52]))
    assert f.dropna().iloc[0] == pytest.approx(1.0 + 0.0252 / 252)


def test_trading_basis_stays_on_input_index(monkeypatch):
    monkeypatch.setattr(config, "RISK_FREE_ACCRUAL_BASIS", "trading")
    s = rate_series([1.0, 1.0, 1.0, 1.0, 2.0, 3.0], start="2020-01-06")
    f = risk_free_daily_factors(s)
    assert f.index.equals(s.index)  # no weekend expansion


def test_factor_input_validation():
    with pytest.raises(TypeError):
        risk_free_daily_factors([1.0, 2.0])
    with pytest.raises(ValueError, match="empty"):
        risk_free_daily_factors(pd.Series([], dtype=float))
    s = rate_series([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="sorted"):
        risk_free_daily_factors(s.iloc[::-1])
    dup = pd.Series([1.0, 2.0], index=[s.index[0], s.index[0]])
    with pytest.raises(ValueError, match="duplicate"):
        risk_free_daily_factors(dup)


def test_load_risk_free_series_roundtrip(tmp_path):
    """Loader shape-test against a synthetic parquet, not the frozen file."""
    s = rate_series([4.0, np.nan, 4.5])
    s.to_frame().to_parquet(tmp_path / f"{config.RISK_FREE_SERIES}.parquet")
    back = load_risk_free_series(root=tmp_path)
    assert back.isna().sum() == 1  # nulls intact, no fill at load
    assert back.iloc[0] == 4.0    # raw percent, unconverted


def test_load_risk_free_series_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="not frozen"):
        load_risk_free_series(root=tmp_path)
