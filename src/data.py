"""Two-path data loader.

Decision 1.4 requires a two-path structure:

    signal path   adjusted total return, used for every signal and every return
    raw path      raw close, retained for share counts and commission

Decision 1.11 fixes the total-return construction, reinvestment at the ex-date
close, carried over from scripts/s00c_download.py unchanged:

    ret_total_t = (Close_t + Div_t) / Close_{t-1} - 1

Decision 1.5 fixes the adjusted open:

    AdjOpen = Open * (AdjClose / Close)

Decision 1.9 forbids forward-fill. A missing bar is unavailable. Under the
interior-gap treatment closed in session 09 (config.INTERIOR_GAP_TREATMENT
= "skip"), a missing observation is removed from the series: the return
across the gap is computed from the last available close, the next
available session carries a multi-day return, and the total-return index
continues on the compressed series. The gap date itself stays unavailable.

    Divergence from session 00C, flagged rather than silently reconciled.
    scripts/s00c_download.py builds tr_index as
    (1.0 + r_div.fillna(0.0)).cumprod(), which reads an unavailable return
    as a zero return -- a value asserted where none was observed. Skip is
    different: no value exists at the gap date, and the post-gap return is
    a genuine observed multi-day return, not an invented flat session. The
    panel at data/interim/etf-panel.parquet still carries the 00C
    convention; this loader does not read it.

Decision 2.5a. TREND_SIGNAL_SERIES is NAV-priced with a one-session posting
lag, so a signal stamped at the T close reads the T-1 NAV. The lag is applied
here, once, at load time. No downstream module knows that one series is
lagged, and applying it twice raises.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src import config

__all__ = [
    "TickerFrame",
    "Panel",
    "build_ticker_frame",
    "load_panel",
    "load_risk_free_series",
    "risk_free_daily_factors",
    "DEFAULT_ROOT",
    "DEFAULT_RATES_ROOT",
]

DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "data" / "raw" / "etf"

# Columns as pulled with auto_adjust=False, actions=True (decision 1.5).
REQUIRED_COLUMNS = (
    "Open", "High", "Low", "Close", "Adj Close",
    "Volume", "Dividends", "Stock Splits", "Capital Gains",
)


@dataclass(frozen=True)
class TickerFrame:
    """Both paths for a single instrument, on a shared date index."""

    ticker: str
    frame: pd.DataFrame
    lag_applied: int = 0

    # -- signal path ------------------------------------------------------
    @property
    def tr_index(self) -> pd.Series:
        """Total-return index. The canonical signal series (1.2, 1.4)."""
        return self.frame["tr_index"]

    @property
    def ret_total(self) -> pd.Series:
        """Total return, used for accumulation (1.3)."""
        return self.frame["ret_total"]

    @property
    def adj_close(self) -> pd.Series:
        return self.frame["adj_close"]

    @property
    def adj_open(self) -> pd.Series:
        """AdjOpen = Open * (AdjClose / Close), decision 1.5."""
        return self.frame["adj_open"]

    # -- raw path ---------------------------------------------------------
    @property
    def raw_close(self) -> pd.Series:
        """Raw close, for share counts and commission only (1.4)."""
        return self.frame["close"]

    @property
    def raw_open(self) -> pd.Series:
        return self.frame["open"]

    @property
    def index(self) -> pd.DatetimeIndex:
        return self.frame.index

    def __len__(self) -> int:
        return len(self.frame)


@dataclass
class Panel:
    """A set of TickerFrames sharing a session calendar."""

    frames: dict[str, TickerFrame] = field(default_factory=dict)
    _lagged: set[str] = field(default_factory=set)

    def __getitem__(self, ticker: str) -> TickerFrame:
        return self.frames[ticker]

    def __contains__(self, ticker: str) -> bool:
        return ticker in self.frames

    def __len__(self) -> int:
        return len(self.frames)

    @property
    def tickers(self) -> list[str]:
        return sorted(self.frames)

    def calendar(self) -> pd.DatetimeIndex:
        """Union of every member's sessions, ascending."""
        if not self.frames:
            return pd.DatetimeIndex([])
        out = None
        for f in self.frames.values():
            out = f.index if out is None else out.union(f.index)
        return out.sort_values()

    def apply_trend_lag(
        self,
        ticker: str = config.TREND_SIGNAL_SERIES,
        lag: int = config.TREND_SIGNAL_LAG,
    ) -> None:
        """Shift the trend signal series forward by `lag` sessions (2.5a).

        Applied exactly once. A second application raises, so no downstream
        module can double-lag the series by re-invoking the loader's helper.
        """
        if ticker not in self.frames:
            raise KeyError(
                f"trend signal series {ticker!r} not loaded; "
                f"available: {self.tickers}"
            )
        if ticker in self._lagged:
            raise RuntimeError(
                f"TREND_SIGNAL_LAG already applied to {ticker!r}; "
                "applying it twice would shift the signal by 2 sessions"
            )
        if lag < 0:
            raise ValueError(f"lag must be non-negative, got {lag}")

        tf = self.frames[ticker]
        shifted = tf.frame.shift(lag) if lag else tf.frame.copy()
        self.frames[ticker] = TickerFrame(ticker, shifted, lag_applied=lag)
        self._lagged.add(ticker)

        assert self.frames[ticker].lag_applied == lag
        assert self.lag_application_count(ticker) == 1

    def lag_application_count(self, ticker: str) -> int:
        return int(ticker in self._lagged)

    def assert_trend_lag_applied_once(
        self, ticker: str = config.TREND_SIGNAL_SERIES
    ) -> None:
        """Assert the 2.5a lag was applied exactly once to `ticker`."""
        n = self.lag_application_count(ticker)
        if n != 1:
            raise AssertionError(
                f"TREND_SIGNAL_LAG must be applied exactly once to {ticker!r}, "
                f"applied {n} times"
            )
        if self.frames[ticker].lag_applied != config.TREND_SIGNAL_LAG:
            raise AssertionError(
                f"{ticker!r} carries lag {self.frames[ticker].lag_applied}, "
                f"expected {config.TREND_SIGNAL_LAG}"
            )


def build_ticker_frame(ticker: str, raw: pd.DataFrame) -> TickerFrame:
    """Build both paths from a raw yfinance frame. Pure; touches no disk."""
    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"{ticker}: missing columns {missing}")
    if not raw.index.is_monotonic_increasing:
        raise ValueError(f"{ticker}: index is not sorted ascending")
    if raw.index.has_duplicates:
        raise ValueError(f"{ticker}: index contains duplicate dates")

    idx = pd.to_datetime(raw.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    idx = idx.normalize()

    close = raw["Close"].astype(float).to_numpy()
    open_ = raw["Open"].astype(float).to_numpy()
    adj_close = raw["Adj Close"].astype(float).to_numpy()
    div = raw["Dividends"].astype(float).fillna(0.0).to_numpy()
    cg = raw["Capital Gains"].astype(float).fillna(0.0).to_numpy()

    out = pd.DataFrame(index=idx)
    out.index.name = "date"
    out["close"] = close
    out["open"] = open_
    out["high"] = raw["High"].astype(float).to_numpy()
    out["low"] = raw["Low"].astype(float).to_numpy()
    out["adj_close"] = adj_close
    out["volume"] = raw["Volume"].astype(float).to_numpy()
    out["dividend"] = div
    out["capital_gain"] = cg
    out["split"] = raw["Stock Splits"].astype(float).fillna(0.0).to_numpy()

    # 1.5. Undefined where Close is zero or unavailable; never filled.
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(close != 0, adj_close / close, np.nan)
    out["adj_open"] = open_ * ratio

    # 1.11 total return, reinvestment at the ex-date close, computed on the
    # compressed (available-only) series per the block below.
    # 1.9 interior-gap treatment, closed as "skip" (session 09,
    # config.INTERIOR_GAP_TREATMENT): a missing observation is removed from
    # the series, the return across the gap is computed from the last
    # available close, so the next available session carries a multi-day
    # return, and the total-return index continues on the compressed series.
    # The gap date itself stays unavailable. The return columns are rebuilt
    # on the same compressed basis so ret_total at a post-gap session is the
    # multi-day return that the tr_index step embeds. (A dividend whose
    # ex-date falls ON a missing-close session cannot be reinvested at an
    # observable price; none exists in any held series — the only interior
    # gaps on disk are three ^NETR index sessions with no distributions —
    # and this loader would drop such a dividend silently, which is recorded
    # here as a stated limitation of the skip implementation.)
    valid = out["close"].notna()
    c_av = out.loc[valid, "close"]
    d_av = out.loc[valid, "dividend"]
    cg_av = out.loc[valid, "capital_gain"]
    prev_av = c_av.shift(1)
    ret_price_av = c_av / prev_av - 1.0
    ret_total_av = (c_av + d_av) / prev_av - 1.0
    ret_totcg_av = (c_av + d_av + cg_av) / prev_av - 1.0
    out["ret_price"] = ret_price_av.reindex(out.index)
    out["ret_total"] = ret_total_av.reindex(out.index)
    out["ret_total_incl_cg"] = ret_totcg_av.reindex(out.index)
    r = ret_total_av.copy()
    if len(r):
        r.iloc[0] = 0.0  # the first observation has no prior close
    out["tr_index"] = (1.0 + r).cumprod().reindex(out.index)

    return TickerFrame(ticker, out)


DEFAULT_RATES_ROOT = Path(__file__).resolve().parents[1] / "data" / "raw" / "rates"


def load_risk_free_series(root: Path | str = DEFAULT_RATES_ROOT) -> pd.Series:
    """The frozen risk-free series (8.1), raw published percent, nulls intact.

    Reads data/raw/rates/<RISK_FREE_SERIES>.parquet as frozen by session 02.
    No conversion happens here; the frozen file carries FRED's published
    values and this function returns them unchanged.
    """
    p = Path(root) / f"{config.RISK_FREE_SERIES}.parquet"
    if not p.exists():
        raise FileNotFoundError(f"risk-free series not frozen at {p}")
    frame = pd.read_parquet(p)
    s = frame[config.RISK_FREE_SERIES].astype(float)
    s.index = pd.to_datetime(s.index)
    return s


def risk_free_daily_factors(rates_pct: pd.Series) -> pd.Series:
    """Daily cash accrual factors from a risk-free rate series (5.5, 5.5a).

    Input is the rate series as frozen: raw published percent on a
    business-day index, nulls where FRED did not publish. Output is one
    accrual factor per day:

        factor = 1 + (rate / 100) / RISK_FREE_DAY_COUNT

    Under RISK_FREE_ACCRUAL_BASIS = "calendar" the output index is every
    calendar day from the series' first date through its last, so weekends
    and holidays carry a factor and a position held across them accrues, per
    5.5a. Under "trading" the output stays on the input's own index.
    Compounding across a holding period is the product of the daily factors.

    Null-day treatment -- a stated departure from 1.9, not an inheritance.
    Decision 1.9 prohibits forward-fill for price series: a missing bar is
    unavailable because no trade can occur at an unobserved price. A rate is
    not a price. The bill in a money market position continues to accrue on
    days FRED does not publish -- weekends, federal holidays, and gap days --
    at the last rate set before them. So a null or absent day carries the
    last published rate FOR ACCRUAL PURPOSES ONLY. This carry lives entirely
    inside this function; the frozen file keeps its nulls, and nothing else
    in the codebase reads a filled rate. Days before the first published
    rate have no rate to carry and stay unavailable (NaN factor); nothing is
    backfilled.
    """
    if not isinstance(rates_pct, pd.Series):
        raise TypeError(f"expected a pandas Series, got {type(rates_pct).__name__}")
    if len(rates_pct) == 0:
        raise ValueError("rate series is empty")
    if not rates_pct.index.is_monotonic_increasing:
        raise ValueError("rate series index must be sorted ascending")
    if rates_pct.index.has_duplicates:
        raise ValueError("rate series index contains duplicate dates")

    idx = pd.to_datetime(rates_pct.index)
    s = pd.Series(rates_pct.to_numpy(dtype=float), index=idx)

    if config.RISK_FREE_ACCRUAL_BASIS == "calendar":
        cal = pd.date_range(idx.min(), idx.max(), freq="D")
        s = s.reindex(cal)

    # The stated departure: carry the last published rate forward. ffill only
    # -- the leading edge before the first published rate stays NaN.
    carried = s.ffill()

    return 1.0 + (carried / 100.0) / config.RISK_FREE_DAY_COUNT


def load_panel(
    tickers,
    root: Path | str = DEFAULT_ROOT,
    apply_trend_lag: bool = True,
) -> Panel:
    """Load `tickers` from `root` and return a Panel.

    When `apply_trend_lag` is true and TREND_SIGNAL_SERIES is among `tickers`,
    the 2.5a lag is applied here, once. Downstream code reads the trend series
    like any other and does not know it is lagged.
    """
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"data root does not exist: {root}")

    panel = Panel()
    for t in tickers:
        p = root / f"{t}.parquet"
        if not p.exists():
            raise FileNotFoundError(f"{t}: no parquet at {p}")
        panel.frames[t] = build_ticker_frame(t, pd.read_parquet(p))

    if apply_trend_lag and config.TREND_SIGNAL_SERIES in panel:
        panel.apply_trend_lag()
        panel.assert_trend_lag_applied_once()

    return panel
