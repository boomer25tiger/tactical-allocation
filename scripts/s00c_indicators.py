"""Session 00C shared indicator library.

RSI: Wilder smoothing, alpha = 1/n (decision 1.6). Seeded with the simple mean
of the first n gains and losses, then recursive avg = (prev*(n-1) + cur)/n,
which is the exact Wilder recursion and is equivalent to an EWM with
alpha = 1/n under an SMA seed. Computed on the total return series.

SMA: simple moving average over n sessions, min_periods = n.
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00c"

RSI_PERIODS = [7, 14, 28]
SMA_LENGTHS = [20, 50, 100, 150, 200, 250]
RSI_THRESHOLDS = [70, 80, 30, 20]


def wilder_rsi(price: pd.Series, n: int) -> pd.Series:
    """Wilder RSI, alpha = 1/n, SMA seed over the first n changes."""
    p = price.to_numpy(dtype=float)
    m = len(p)
    out = np.full(m, np.nan)
    if m < n + 1:
        return pd.Series(out, index=price.index)

    d = np.diff(p)
    gain = np.where(d > 0, d, 0.0)
    loss = np.where(d < 0, -d, 0.0)

    ag = gain[:n].mean()
    al = loss[:n].mean()
    out[n] = _rsi_from(ag, al)
    for i in range(n, m - 1):
        ag = (ag * (n - 1) + gain[i]) / n
        al = (al * (n - 1) + loss[i]) / n
        out[i + 1] = _rsi_from(ag, al)
    return pd.Series(out, index=price.index)


def _rsi_from(ag: float, al: float) -> float:
    if al == 0.0 and ag == 0.0:
        return 50.0
    if al == 0.0:
        return 100.0
    if ag == 0.0:
        return 0.0
    return 100.0 - 100.0 / (1.0 + ag / al)


def sma(price: pd.Series, n: int) -> pd.Series:
    return price.rolling(n, min_periods=n).mean()


def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(INTERIM / "etf-panel.parquet")
    p["date"] = pd.to_datetime(p["date"])
    return p.sort_values(["ticker", "date"]).reset_index(drop=True)


def tr_series(panel: pd.DataFrame) -> dict:
    """ticker -> total return index series indexed by date."""
    return {t: g.set_index("date")["tr_index"].astype(float)
            for t, g in panel.groupby("ticker", sort=True)}


def rsi_table(tr: dict, tickers=None, periods=RSI_PERIODS) -> dict:
    """(ticker, period) -> RSI series."""
    tickers = tickers or list(tr)
    return {(t, n): wilder_rsi(tr[t], n) for t in tickers for n in periods}


def effective_independent(corr: np.ndarray) -> float:
    """Reciprocal of the sum of squared normalized eigenvalues of a
    correlation matrix. Normalized so the eigenvalues sum to one."""
    ev = np.linalg.eigvalsh(corr)
    ev = np.clip(ev, 0.0, None)
    s = ev.sum()
    if s <= 0:
        return np.nan
    w = ev / s
    return float(1.0 / np.square(w).sum())


def run_lengths(mask: np.ndarray) -> np.ndarray:
    """Lengths of consecutive True runs."""
    if mask.size == 0 or not mask.any():
        return np.array([], dtype=int)
    m = mask.astype(np.int8)
    padded = np.concatenate(([0], m, [0]))
    diff = np.diff(padded)
    starts = np.flatnonzero(diff == 1)
    ends = np.flatnonzero(diff == -1)
    return ends - starts


def pctile(a, q):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    return float(np.percentile(a, q)) if a.size else np.nan


def describe(a: np.ndarray, prefix: str = "") -> dict:
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return {f"{prefix}n": 0, f"{prefix}mean": np.nan, f"{prefix}median": np.nan,
                f"{prefix}sd": np.nan, f"{prefix}min": np.nan, f"{prefix}p05": np.nan,
                f"{prefix}p25": np.nan, f"{prefix}p75": np.nan, f"{prefix}p95": np.nan,
                f"{prefix}max": np.nan}
    return {
        f"{prefix}n": int(a.size), f"{prefix}mean": float(a.mean()),
        f"{prefix}median": float(np.median(a)), f"{prefix}sd": float(a.std(ddof=1)) if a.size > 1 else np.nan,
        f"{prefix}min": float(a.min()), f"{prefix}p05": float(np.percentile(a, 5)),
        f"{prefix}p25": float(np.percentile(a, 25)), f"{prefix}p75": float(np.percentile(a, 75)),
        f"{prefix}p95": float(np.percentile(a, 95)), f"{prefix}max": float(a.max()),
    }
