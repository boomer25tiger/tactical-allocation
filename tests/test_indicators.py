"""Unit tests for src/indicators.py.

Every series here is hand-constructed. Nothing is read from data/ and no
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
sys.path.insert(0, str(ROOT / "scripts"))

from src.indicators import rsi_from, sma, wilder_rsi  # noqa: E402


def idx(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2020-01-01", periods=n, freq="D")


def series(values) -> pd.Series:
    return pd.Series(np.asarray(values, dtype=float), index=idx(len(values)))


# ---------------------------------------------------------------------------
# Analytic cases, computed by hand
# ---------------------------------------------------------------------------

def test_rsi_known_analytic_answer():
    """Prices 100, 101, 100, 102, 103 with n = 3.

    changes  +1, -1, +2, +1
    gains     1,  0,  2,  1
    losses    0,  1,  0,  0

    seed   avg_gain = (1 + 0 + 2) / 3 = 1
           avg_loss = (0 + 1 + 0) / 3 = 1/3
           RSI[3]   = 100 - 100 / (1 + 1 / (1/3)) = 100 - 25 = 75

    step   avg_gain = (1 * 2 + 1) / 3 = 1
           avg_loss = ((1/3) * 2 + 0) / 3 = 2/9
           RSI[4]   = 100 - 100 / (1 + 1 / (2/9)) = 100 - 100/5.5 = 81.8181...
    """
    r = wilder_rsi(series([100, 101, 100, 102, 103]), 3)
    assert np.isnan(r.iloc[:3]).all()
    assert r.iloc[3] == pytest.approx(75.0, abs=1e-12)
    assert r.iloc[4] == pytest.approx(100.0 - 100.0 / 5.5, abs=1e-12)


def test_rsi_all_gains_is_100():
    r = wilder_rsi(series(np.arange(100, 130, dtype=float)), 14)
    assert r.dropna().eq(100.0).all()


def test_rsi_all_losses_is_0():
    r = wilder_rsi(series(np.arange(130, 100, -1, dtype=float)), 14)
    assert r.dropna().eq(0.0).all()


def test_rsi_flat_series_is_50():
    r = wilder_rsi(series([100.0] * 30), 14)
    assert r.dropna().eq(50.0).all()


def test_rsi_first_output_index_is_n():
    """The seed consumes n changes, so the first value lands at position n."""
    for n in (3, 7, 14, 28):
        r = wilder_rsi(series(np.linspace(100, 200, 60)), n)
        assert r.notna().idxmax() == r.index[n]
        assert r.iloc[:n].isna().all()


def test_rsi_from_edge_cases():
    assert rsi_from(0.0, 0.0) == 50.0
    assert rsi_from(1.0, 0.0) == 100.0
    assert rsi_from(0.0, 1.0) == 0.0
    assert rsi_from(1.0, 1.0) == pytest.approx(50.0)


def test_rsi_too_short_yields_all_nan():
    assert wilder_rsi(series([100, 101, 102]), 14).isna().all()


# ---------------------------------------------------------------------------
# Fidelity of the lift: identical to session 00C on null-free input
# ---------------------------------------------------------------------------

def test_lift_matches_s00c_exactly_when_no_nulls():
    from s00c_indicators import sma as s00c_sma
    from s00c_indicators import wilder_rsi as s00c_rsi

    rng = np.random.default_rng(20260817)
    p = series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 400))))
    for n in (7, 14, 28):
        pd.testing.assert_series_equal(
            wilder_rsi(p, n), s00c_rsi(p, n), check_names=False
        )
    for n in (20, 200):
        pd.testing.assert_series_equal(sma(p, n), s00c_sma(p, n), check_names=False)


# ---------------------------------------------------------------------------
# Decision 1.9: nulls propagate, they are never filled
# ---------------------------------------------------------------------------

def test_rsi_null_is_not_treated_as_zero_change():
    """Regression against the session 00C defect.

    In 00C a NaN change failed both np.where tests and was recorded as a zero
    gain and a zero loss, so an interior null produced output bit-identical to
    the null-free series. Here the null must change the output.
    """
    from s00c_indicators import wilder_rsi as s00c_rsi

    clean = series(np.linspace(100, 130, 30))
    holed = clean.copy()
    holed.iloc[10] = np.nan

    # the 00C defect, pinned so it cannot be reintroduced by a future lift
    assert np.allclose(
        s00c_rsi(clean, 14).dropna().to_numpy(),
        s00c_rsi(holed, 14).dropna().to_numpy(),
    ), "expected the 00C implementation to ignore the null"

    ours = wilder_rsi(holed, 14)
    assert ours.isna().sum() > wilder_rsi(clean, 14).isna().sum()
    assert np.isnan(ours.iloc[10]), "the null bar itself must be unavailable"


def test_rsi_values_before_a_gap_are_unaffected():
    clean = series(np.concatenate([np.linspace(100, 140, 40), np.linspace(140, 180, 40)]))
    holed = clean.copy()
    holed.iloc[50] = np.nan
    a, b = wilder_rsi(clean, 14), wilder_rsi(holed, 14)
    pd.testing.assert_series_equal(a.iloc[:50], b.iloc[:50])


def test_rsi_skips_gap_next_session_available():
    """The closed 1.9 treatment: the gap date is unavailable, the next
    available session carries a multi-day change into the recursion, and
    output continues immediately — no reseed warm-up. (Session 01's
    reseeding regression test asserted 14 blank sessions here; replaced.)"""
    p = series(np.linspace(100, 200, 80))
    p.iloc[40] = np.nan
    r = wilder_rsi(p, 14)
    assert np.isnan(r.iloc[40]), "the gap date itself has no observation"
    assert r.iloc[41:].notna().all(), "output continues on the session after"


def test_rsi_multiday_change_enters_recursion_once():
    """The post-gap step consumes the compressed two-day change as ONE
    Wilder step: the holed series must equal the same series with the gap
    row physically deleted, value for value on shared dates."""
    p = series(np.linspace(100, 200, 60))
    holed = p.copy()
    holed.iloc[30] = np.nan
    deleted = p.drop(p.index[30])
    a = wilder_rsi(holed, 14).dropna()
    b = wilder_rsi(deleted, 14).dropna()
    pd.testing.assert_series_equal(a, b, check_names=False)


def test_rsi_short_tail_after_gap_stays_available():
    """A trailing stretch shorter than n + 1 after a gap keeps producing
    output under skip, because the recursion never restarted."""
    p = series(np.linspace(100, 130, 30))
    p.iloc[20] = np.nan
    r = wilder_rsi(p, 14)
    assert np.isnan(r.iloc[20])
    assert r.iloc[21:].notna().all()


def test_rsi_all_null_input():
    assert wilder_rsi(series([np.nan] * 30), 14).isna().all()


def test_rsi_leading_nulls_do_not_shift_the_seed():
    p = series([np.nan] * 5 + list(np.linspace(100, 130, 30)))
    r = wilder_rsi(p, 14)
    assert r.iloc[: 5 + 14].isna().all()
    assert not np.isnan(r.iloc[5 + 14])


def test_sma_skips_gap_window_spans_it():
    """Skip semantics: the window is the last n AVAILABLE sessions, so the
    session after a gap has an average spanning the gap; only the gap date
    itself is unavailable."""
    p = series(np.arange(100, 140, dtype=float))
    p.iloc[10] = np.nan
    s = sma(p, 5)
    assert np.isnan(s.iloc[10]), "the gap date has no observation"
    assert s.iloc[11:].notna().all(), "the average is available right after"
    # window at position 11 = mean of positions 6,7,8,9,11
    expected = np.mean([p.iloc[6], p.iloc[7], p.iloc[8], p.iloc[9], p.iloc[11]])
    assert s.iloc[11] == pytest.approx(expected)


def test_sma_200_one_day_gap_available_next_session():
    """The step 1 mandated case: a one-day interior gap in a 200-session
    moving average must leave the average available on the session after
    the gap."""
    p = series(np.linspace(100, 300, 260))
    p.iloc[220] = np.nan
    s = sma(p, 200)
    assert np.isnan(s.iloc[220])
    assert not np.isnan(s.iloc[221]), (
        "under the closed 1.9 skip treatment a one-day gap must not blank "
        "the 200-session average"
    )
    expected = p.dropna().loc[:p.index[221]].iloc[-200:].mean()
    assert s.iloc[221] == pytest.approx(expected)


def test_sma_known_answer():
    s = sma(series([1, 2, 3, 4, 5, 6]), 3)
    assert s.iloc[:2].isna().all()
    assert s.iloc[2] == pytest.approx(2.0)
    assert s.iloc[5] == pytest.approx(5.0)


def test_neither_indicator_fills():
    """No output may be produced at a position whose input is unavailable."""
    p = series(np.linspace(100, 200, 60))
    p.iloc[30] = np.nan
    assert np.isnan(wilder_rsi(p, 14).iloc[30])
    assert np.isnan(sma(p, 20).iloc[30])


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [0, -1, 2.5, "14", None])
def test_rejects_bad_period(bad):
    with pytest.raises((ValueError, TypeError)):
        wilder_rsi(series([1, 2, 3]), bad)


def test_rejects_non_series():
    with pytest.raises(TypeError):
        wilder_rsi([1, 2, 3], 14)


def test_rejects_unsorted_index():
    p = series(np.linspace(100, 130, 30))
    with pytest.raises(ValueError):
        wilder_rsi(p.iloc[::-1], 14)


def test_rejects_duplicate_index():
    p = pd.Series([1.0, 2.0, 3.0], index=[idx(1)[0]] * 3)
    with pytest.raises(ValueError):
        wilder_rsi(p, 2)
