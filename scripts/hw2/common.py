"""Shared setup for the HW2 investor-pitch re-runs (Columbia B9339, Homework 2).

Everything under scripts/hw2/ is a post-read analysis layered on the frozen
study. Nothing here changes a registered specification, a frozen input or an
output of an earlier session. Results are written to outputs/hw2/.

Windows used by the pitch deck
    P11  2011-10-04 to 2021-07-30, the registered primary window (decision 7.14a)
    P12  2012-01-03 to 2021-07-30, the deck's analysis window, the first full
         calendar year in which every order the strategy places can fill
    H    2021-08-02 to 2026-08-14, the sealed holdout
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

os.environ.setdefault("READ_HOLDOUT_THROUGH", "2026-08-14")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np   # noqa: E402
import pandas as pd  # noqa: E402

OUT = ROOT / "outputs" / "hw2"
OUT.mkdir(parents=True, exist_ok=True)

P11 = ("2011-10-04", "2021-07-30")
P12 = ("2012-01-03", "2021-07-30")
H = ("2021-08-02", "2026-08-14")
WINDOWS = {"P11": P11, "P12": P12, "H": H}

# Fund overlay. Exposure w = min(1, TARGET / sigma), sigma the annualised sd of
# the last LOOKBACK daily engine returns, applied LAG sessions later. The
# remainder earns T-bills and every unit of exposure change pays WEIGHT_COST_BP.
TARGET, LOOKBACK, LAG, WEIGHT_COST_BP = 0.25, 60, 2, 10.0

# Fee terms in the deck: one class, 1% management fee and a 20% incentive fee
# on returns above QQQ's for the year, above a high-water mark. The earlier
# 2% and 20% over T-bills remains available as a comparison.
FEE_MGMT, FEE_INC = 0.01, 0.20

ANN = math.sqrt(252.0)


def sl(s, w):
    """Slice a series or frame to an inclusive (start, end) window."""
    a, b = w
    return s[(s.index >= a) & (s.index <= b)]


def metrics(r: pd.Series, rf: pd.Series) -> dict:
    """Metric set used throughout the deck.

    sortino: annualised mean excess return over T-bills divided by the
    annualised root mean square of min(excess, 0) taken over ALL days.
    calmar: CAGR divided by the absolute maximum drawdown over the window.
    sharpe_lo: Lo (2002) correction at q = 252, scripts/s13_backtest.lo_sharpe.
    """
    import scripts.s13_backtest as bt
    r = r.dropna()
    rf = rf.reindex(r.index).fillna(0.0)
    ex = r - rf
    n = len(r)
    g = (1 + r).cumprod()
    dd = float((g / g.cummax() - 1).min())
    ann = float(g.iloc[-1] ** (252 / n) - 1)
    dsd = math.sqrt(float((np.minimum(ex, 0) ** 2).mean())) * ANN
    return dict(n=n, ann_return=ann, ann_vol=float(r.std(ddof=1) * ANN),
                sharpe_naive=float(ex.mean() / ex.std(ddof=1) * ANN),
                sharpe_lo=float(bt.lo_sharpe(ex)),
                sortino=float(ex.mean() * 252 / dsd), calmar=ann / abs(dd), max_dd=dd)


def overlay(strat: pd.Series, rf: pd.Series, target=TARGET, lookback=LOOKBACK,
            lag=LAG, cost_bp=WEIGHT_COST_BP, estimator=None):
    """Vol-target overlay on a daily engine return series. Returns (fund, w)."""
    sig = estimator if estimator is not None else strat.rolling(lookback).std() * ANN
    sig = sig.shift(lag)
    w = (target / sig).clip(upper=1.0).fillna(1.0)
    fund = w * strat + (1 - w) * rf - w.diff().abs().fillna(0) * cost_bp / 1e4
    return fund, w


def net_of_fees(x: pd.Series, rf: pd.Series, mgmt: float, inc: float,
                nav0: float = 1.0, years: int | None = None, hurdle: pd.Series | None = None):
    """Daily NAV after fees.

    The management fee accrues daily at mgmt / 252. The incentive fee accrues
    daily in NAV on gains above max(high-water mark, year-start NAV times
    (1 + that year's hurdle return)) and is paid at each anniversary, so a fall
    in NAV reduces the accrued fee. The hurdle is the T-bill series rf unless a
    daily return series is passed, such as QQQ's for the deck's fee terms.
    Returns (daily net returns, dict of totals).
    """
    rf = (rf if hurdle is None else hurdle).reindex(x.index).fillna(0.0)
    G, hwm, ys, hg = nav0, nav0, nav0, 1.0
    start = x.index[0]
    k = 1
    out, prev = [], nav0
    fm = fi = 0.0
    gross = nav0
    end_date = x.index[-1]
    for i, (d, ri) in enumerate(x.items()):
        gross *= 1 + ri
        G *= 1 + ri
        hg *= 1 + rf[d]
        m = G * mgmt / 252
        G -= m
        fm += m
        acc = inc * max(0.0, G - max(hwm, ys * hg))
        nav = G - acc
        anniversary = d >= start + pd.DateOffset(years=k)
        last = i == len(x) - 1
        if anniversary or last:
            fi += acc
            G = nav
            hwm = max(hwm, nav)
            ys, hg = nav, 1.0
            k += 1
        out.append(nav / prev - 1)
        prev = nav
        if years is not None and anniversary and k > years:
            end_date = d
            break
    s = pd.Series(out, index=x.index[:len(out)])
    return s, dict(end_date=end_date, gross=gross, net=prev, mgmt_fees=fm, incentive_fees=fi)


def stationary_blocks(rng, n, mean_block, length=None):
    """Politis-Romano stationary bootstrap index vector, as in scripts/s30_phaseF.py."""
    L = n if length is None else length
    p = 1.0 / mean_block
    idx = np.empty(L, dtype=np.int64)
    i = 0
    while i < L:
        st = rng.integers(n)
        b = min(int(rng.geometric(p)), L - i)
        idx[i:i + b] = (st + np.arange(b)) % n
        i += b
    return idx
