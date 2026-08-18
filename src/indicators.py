"""Shared indicator library.

Lifted from scripts/s00c_indicators.py (used by scripts/s00c_rsi.py and
scripts/s00c_structure.py) rather than rewritten. The Wilder recursion and the
SMA seed are carried over unchanged:

    RSI  Wilder smoothing, alpha = 1/n (decision 1.6), seeded with the simple
         mean of the first n gains and losses, then the exact Wilder recursion
         avg = (prev * (n - 1) + cur) / n.
    SMA  simple moving average over n sessions, min_periods = n.

One behavioural change against the session 00C original, required by decision
1.9 (forward-fill prohibited, a missing bar is treated as unavailable):

    The 00C wilder_rsi took np.diff over the raw array and then applied
    np.where(d > 0, d, 0.0) and np.where(d < 0, -d, 0.0). A null price yields a
    NaN change, and both np.where tests are False for NaN, so the change was
    silently recorded as a zero gain and a zero loss -- that is, a missing bar
    was read as "no price change". On a series with one interior null the 00C
    output is bit-identical to the output on the same series without the null.
    That is forward-fill in effect and it violates 1.9.

    Under the 1.9 interior-gap treatment closed in session 09
    (config.INTERIOR_GAP_TREATMENT = "skip"), a missing observation is
    REMOVED from the series rather than triggering a reseed: the change
    across the gap is computed from the last available observation, so the
    next available session carries a multi-day change, and the Wilder
    recursion proceeds on the compressed series. The gap date itself stays
    unavailable in the output. Session 01 originally implemented segment
    reseeding here; that discarded a full moving-average window for a
    one-day gap, which the 1.9 closure judged disproportionate. On a
    null-free series the arithmetic remains identical to 00C, which
    tests/test_indicators.py asserts directly against the 00C
    implementation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["wilder_rsi", "sma", "rsi_from"]


def rsi_from(avg_gain: float, avg_loss: float) -> float:
    """RSI from a smoothed gain and loss. Carried over from session 00C."""
    if avg_loss == 0.0 and avg_gain == 0.0:
        return 50.0
    if avg_loss == 0.0:
        return 100.0
    if avg_gain == 0.0:
        return 0.0
    return 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)


def _check(price: pd.Series, n: int) -> None:
    if not isinstance(price, pd.Series):
        raise TypeError(f"expected a pandas Series, got {type(price).__name__}")
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError(f"period must be a positive integer, got {n!r}")
    if not price.index.is_monotonic_increasing:
        raise ValueError("price series index must be sorted ascending")
    if price.index.has_duplicates:
        raise ValueError("price series index contains duplicate timestamps")


def wilder_rsi(price: pd.Series, n: int) -> pd.Series:
    """Wilder RSI, alpha = 1/n, SMA seed over the first n changes.

    Interior gaps are SKIPPED per the closed 1.9 treatment: missing
    observations are removed, the recursion runs on the compressed series
    (so the first session after a gap contributes a multi-day change as one
    Wilder step), and outputs are indexed back to the original calendar.
    The gap date itself is unavailable in the output. Never fills, never
    interpolates. Fewer than n + 1 available observations yield no output.
    """
    _check(price, n)
    avail = price.dropna()
    m = len(avail)
    out = np.full(m, np.nan)
    if m >= n + 1:
        d = np.diff(avail.to_numpy(dtype=float))
        gain = np.where(d > 0, d, 0.0)
        loss = np.where(d < 0, -d, 0.0)
        avg_gain = gain[:n].mean()
        avg_loss = loss[:n].mean()
        out[n] = rsi_from(avg_gain, avg_loss)
        for k in range(n, m - 1):
            avg_gain = (avg_gain * (n - 1) + gain[k]) / n
            avg_loss = (avg_loss * (n - 1) + loss[k]) / n
            out[k + 1] = rsi_from(avg_gain, avg_loss)
    return pd.Series(out, index=avail.index, name=price.name).reindex(price.index)


def sma(price: pd.Series, n: int) -> pd.Series:
    """Simple moving average over the last n AVAILABLE sessions.

    Interior gaps are skipped per the closed 1.9 treatment: the window is
    taken over available observations, so a one-day gap does not blank the
    average for the following n sessions — it remains available on the
    session after the gap, spanning the gap. The gap date itself stays
    unavailable. (Session 00C's form, rolling(n, min_periods=n) on the raw
    series, blanked n windows per interior null; that was the
    pre-closure propagation behaviour.)
    """
    _check(price, n)
    avail = price.dropna()
    return avail.rolling(n, min_periods=n).mean().reindex(price.index)
