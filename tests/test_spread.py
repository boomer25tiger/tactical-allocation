"""Unit tests for src/spread.py against known analytic answers.

The Corwin-Schultz estimator has a closed form, so a series constructed
from pure bid-ask bounce with zero volatility must recover the true spread
exactly: with H = M(1+S/2), L = M(1-S/2) on both days of a window,
beta = 2r^2 and gamma = r^2 for r = ln((1+S/2)/(1-S/2)), and the algebra
collapses to alpha = r, giving S back exactly. Everything here is
hand-constructed; no data under data/ is opened.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.spread import abdi_ranaldo, corwin_schultz  # noqa: E402


def series(vals, start="2020-01-06"):
    return pd.Series(
        np.asarray(vals, dtype=float),
        index=pd.date_range(start, periods=len(vals), freq="B"),
    )


def bounce_frame(spread: float, n: int = 10, mid: float = 100.0):
    """Pure bid-ask bounce, zero volatility: the CS analytic case."""
    h = series([mid * (1 + spread / 2)] * n)
    l = series([mid * (1 - spread / 2)] * n)
    c = series([mid] * n)
    return h, l, c


# ---------------------------------------------------------------------------
# Corwin-Schultz analytic answers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("true_s", [0.001, 0.01, 0.05])
def test_cs_recovers_constant_spread_exactly(true_s):
    h, l, c = bounce_frame(true_s)
    out = corwin_schultz(h, l, c)
    est = out["spread"].dropna()
    assert len(est) == 9  # n-1 windows
    np.testing.assert_allclose(est.to_numpy(), true_s, rtol=1e-10)
    assert not out["negative"].dropna().any()


def test_cs_zero_range_gives_zero_spread():
    """H = L = C (NAV-priced series like RYMFX): no range, no spread."""
    h, l, c = (series([100.0] * 8),) * 3
    out = corwin_schultz(h, l, c)
    np.testing.assert_allclose(out["spread"].dropna().to_numpy(), 0.0, atol=1e-14)


def test_cs_pure_volatility_goes_negative():
    """A strong trend with zero bounce drives gamma above beta's implied
    level and alpha negative -- the documented negative-estimate case."""
    n = 12
    mid = 100.0 * np.exp(0.05 * np.arange(n))  # 5 percent per day trend
    h = series(mid * 1.0001)
    l = series(mid * 0.9999)
    c = series(mid)
    out = corwin_schultz(h, l, c, overnight_adjust=False)
    assert out["negative"].dropna().any()
    assert (out["spread_zero"].dropna() >= 0).all()


def test_cs_treatments_relate_correctly():
    n = 12
    mid = 100.0 * np.exp(0.05 * np.arange(n))
    h, l, c = series(mid * 1.0001), series(mid * 0.9999), series(mid)
    out = corwin_schultz(h, l, c, overnight_adjust=False)
    v = out.dropna(subset=["spread"])
    assert (v["spread_zero"] >= v["spread"]).all()
    excl = v.loc[~v["negative"], "spread"]
    assert (excl >= 0).all()


def test_cs_overnight_adjustment_shift_rule():
    """The adjustment shifts day t+1 additively by the gap: on a gap up,
    H and L both drop by L_{t+1} - C_t, so the shifted low lands exactly on
    the prior close. The test hand-computes the closed form from the shifted
    prices and requires an exact match, which pins the shift semantics.

    Note what the adjustment does NOT promise: a large gap plus real drift
    still leaves genuine two-day variance, so the adjusted estimate need not
    equal the gap-free analytic value. Day 2's range here nests inside day
    1's after the shift, so gamma equals day 1's squared range and the
    estimate is positive; unadjusted, gamma sees the 20 percent gap and the
    estimate is deeply negative.
    """
    h = series([100.5, 120.2], start="2020-01-06")
    l = series([99.5, 119.8], start="2020-01-06")
    c = series([100.0, 120.0], start="2020-01-06")

    unadj = corwin_schultz(h, l, c, overnight_adjust=False)["spread"].iloc[0]
    adj = corwin_schultz(h, l, c, overnight_adjust=True)["spread"].iloc[0]

    # hand-computed closed form from the explicitly shifted day-2 prices
    shift = -(119.8 - 100.0)          # gap up: L_{t+1} - C_t
    h1, l1 = 120.2 + shift, 119.8 + shift
    assert l1 == pytest.approx(100.0)  # shifted low abuts the prior close
    beta = np.log(100.5 / 99.5) ** 2 + np.log(h1 / l1) ** 2
    gamma = np.log(max(100.5, h1) / min(99.5, l1)) ** 2
    denom = 3.0 - 2.0 * np.sqrt(2.0)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / denom - np.sqrt(gamma / denom)
    expected = 2.0 * (np.exp(alpha) - 1.0) / (1.0 + np.exp(alpha))

    assert unadj < -0.3, "unadjusted gamma must see the 20 percent gap"
    assert adj == pytest.approx(expected, rel=1e-12)
    assert adj > 0, "with the gap removed the nested range implies a spread"


def test_cs_missing_hl_carries_prior_good_values():
    h, l, c = bounce_frame(0.01, n=8)
    h.iloc[3] = np.nan
    l.iloc[3] = np.nan
    out = corwin_schultz(h, l, c)
    est = out["spread"].dropna()
    np.testing.assert_allclose(est.to_numpy(), 0.01, rtol=1e-10)


def test_cs_last_row_is_nan():
    h, l, c = bounce_frame(0.01, n=5)
    assert np.isnan(corwin_schultz(h, l, c)["spread"].iloc[-1])


def test_cs_mismatched_lengths_raise():
    h, l, c = bounce_frame(0.01, n=5)
    with pytest.raises(ValueError):
        corwin_schultz(h.iloc[:4], l, c)


# ---------------------------------------------------------------------------
# Abdi-Ranaldo analytic answers
# ---------------------------------------------------------------------------

def test_ar_recovers_constant_spread():
    """Close at ask, midrange at mid: (c - eta_t)(c - eta_{t+1}) = (s/2)^2
    in log space, so the estimator returns the log-scale spread."""
    s = 0.01
    n = 10
    mid = 100.0
    h = series([mid * (1 + s / 2)] * n)
    l = series([mid * (1 - s / 2)] * n)
    c = series([mid * (1 + s / 2)] * n)  # close pinned at the ask
    out = abdi_ranaldo(h, l, c)
    est = out["spread"].dropna()
    # in logs the half-spread is ln(1+s/2) - (ln(1+s/2)+ln(1-s/2))/2
    half = (np.log(1 + s / 2) - np.log(1 - s / 2)) / 2
    np.testing.assert_allclose(est.to_numpy(), 2 * half, rtol=1e-10)
    assert est.iloc[0] == pytest.approx(s, rel=1e-4)  # log-scale ~ s


def test_ar_zero_range_zero_spread():
    h, l, c = (series([100.0] * 6),) * 3
    out = abdi_ranaldo(h, l, c)
    np.testing.assert_allclose(out["spread"].dropna().to_numpy(), 0.0, atol=1e-14)


def test_ar_negative_s2_floors_daily_estimate():
    """Close at mid, drifting midrange: products can go negative and the
    daily estimate floors at zero while s2 keeps the sign."""
    h = series([101.0, 103.0, 101.0, 103.0, 101.0, 103.0])
    l = series([99.0, 101.0, 99.0, 101.0, 99.0, 101.0])
    c = series([101.0, 101.0, 101.0, 101.0, 101.0, 101.0])
    out = abdi_ranaldo(h, l, c)
    v = out.dropna(subset=["s2"])
    assert v["negative"].any()
    assert (v["spread"] >= 0).all()
