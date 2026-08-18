"""Bid-ask spread estimators from daily OHLC (decision 4.3, session 05).

Corwin & Schultz (2012, Journal of Finance): closed-form high-low estimator.
The squared log range over a two-day window carries twice the variance
contribution of a one-day range but the same bid-ask bounce contribution,
which lets the two be separated in closed form:

    beta_t  = [ln(H_t/L_t)]^2 + [ln(H_{t+1}/L_{t+1})]^2
    gamma_t = [ln(max(H_t,H_{t+1}) / min(L_t,L_{t+1}))]^2
    alpha_t = (sqrt(2 beta) - sqrt(beta)) / (3 - 2 sqrt(2))
              - sqrt(gamma / (3 - 2 sqrt(2)))
    S_t     = 2 (e^alpha - 1) / (1 + e^alpha)

Published-methodology treatments implemented here, per the session prompt:

  * Missing high/low prices are replaced with the most recent good values
    from prior trading days (carry, applied to H and L jointly).
  * Overnight-return adjustment: if day t+1 opens beyond day t's close
    range, day t+1's high and low are shifted by the gap (down by
    L_{t+1} - C_t on a gap up, up by C_t - H_{t+1} on a gap down) before
    beta and gamma are computed.
  * Negative two-day estimates are reported under three treatments:
    "zero" (negative daily estimates set to zero), "unchanged" (kept as
    computed), and "exclude" (negative observations dropped). The negative
    rate itself is treatment-independent and reported alongside, since
    zeroing is known to bias estimated spreads downward in illiquid times.

Abdi & Ranaldo (2017, RFS), the close-high-low robustness arm:

    eta_t = (ln H_t + ln L_t) / 2                     (log midrange)
    s2_t  = 4 (c_t - eta_t)(c_t - eta_{t+1})          (c = ln Close)
    s_t   = sqrt(max(s2_t, 0))

Both estimators are computed on the raw OHLC path as stored (Yahoo's
split-consistent basis): spreads are proportional, so a uniform split basis
cancels in every ratio. Dividends leave raw prices unadjusted, and the
overnight gap they create is absorbed by the CS overnight adjustment.

All spreads are returned as proportional (decimal) values; callers convert
to basis points. Two-day windows overlap by construction; the window's
estimate is indexed to its FIRST day.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["corwin_schultz", "abdi_ranaldo", "CS_DENOM"]

CS_DENOM = 3.0 - 2.0 * np.sqrt(2.0)


def _carry_missing_hl(high: pd.Series, low: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Replace missing H/L with the most recent good prior values, jointly."""
    good = high.notna() & low.notna() & (high > 0) & (low > 0)
    h = high.where(good).ffill()
    l = low.where(good).ffill()
    return h, l


def corwin_schultz(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    overnight_adjust: bool = True,
) -> pd.DataFrame:
    """Two-day Corwin-Schultz spread estimates.

    Returns a DataFrame indexed like the input (last row NaN, since each
    window needs t and t+1) with columns:
        spread      raw two-day estimate, negatives kept ("unchanged")
        spread_zero negatives floored at zero ("zero" treatment)
        negative    boolean, estimate below zero (for the "exclude"
                    treatment and the negative-rate accounting)
    """
    if not (len(high) == len(low) == len(close)):
        raise ValueError("high, low, close must share an index")
    h, l = _carry_missing_hl(high.astype(float), low.astype(float))
    c = close.astype(float)

    h0, l0 = h.to_numpy(), l.to_numpy()
    h1, l1 = np.roll(h0, -1), np.roll(l0, -1)
    c0 = c.to_numpy()

    if overnight_adjust:
        # gap up: tomorrow's low above today's close -> shift day t+1 down
        gap_up = l1 - c0
        gap_dn = c0 - h1
        shift = np.where(gap_up > 0, -gap_up, np.where(gap_dn > 0, gap_dn, 0.0))
        h1 = h1 + shift
        l1 = l1 + shift

    with np.errstate(divide="ignore", invalid="ignore"):
        r0 = np.log(h0 / l0)
        r1 = np.log(h1 / l1)
        beta = r0**2 + r1**2
        gamma = np.log(np.maximum(h0, h1) / np.minimum(l0, l1)) ** 2
        alpha = (np.sqrt(2.0 * beta) - np.sqrt(beta)) / CS_DENOM - np.sqrt(
            gamma / CS_DENOM
        )
        spread = 2.0 * (np.exp(alpha) - 1.0) / (1.0 + np.exp(alpha))

    spread[-1] = np.nan  # no t+1 for the final row
    out = pd.DataFrame(index=high.index)
    out["spread"] = spread
    out["spread_zero"] = np.where(np.isnan(spread), np.nan, np.maximum(spread, 0.0))
    out["negative"] = pd.Series(spread, index=high.index) < 0
    return out


def abdi_ranaldo(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> pd.DataFrame:
    """Daily Abdi-Ranaldo close-high-low estimates.

    Columns: spread (sqrt(max(s2,0)) daily estimate, their standard daily
    form), s2 (the signed squared-spread term), negative (s2 < 0).
    """
    if not (len(high) == len(low) == len(close)):
        raise ValueError("high, low, close must share an index")
    h, l = _carry_missing_hl(high.astype(float), low.astype(float))
    with np.errstate(divide="ignore", invalid="ignore"):
        eta = (np.log(h.to_numpy()) + np.log(l.to_numpy())) / 2.0
        c = np.log(close.astype(float).to_numpy())
        eta_next = np.roll(eta, -1)
        s2 = 4.0 * (c - eta) * (c - eta_next)
        s = np.sqrt(np.maximum(s2, 0.0))
    s2[-1] = np.nan
    s[-1] = np.nan
    out = pd.DataFrame(index=high.index)
    out["spread"] = s
    out["s2"] = s2
    out["negative"] = pd.Series(s2, index=high.index) < 0
    return out
