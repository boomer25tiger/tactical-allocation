"""Session 00C, Step 1. Pull the equity ETF panel from yfinance.

Pull-freeze protocol (decision 1.1): pull once to parquet, SHA-256, record pull
date and yfinance version, never re-pull. This script refuses to overwrite an
existing raw parquet unless --force is passed.

Writes:
    data/raw/etf/<TICKER>.parquet          raw pull, one file per ticker
    outputs/session-00c/panel-coverage.csv
    outputs/session-00c/etf-manifest.csv
    data/interim/etf-panel.parquet         long form total return + adj close
    outputs/session-00c/pull-metadata.json
"""

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "etf"
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00c"

START = "1995-01-01"

GROUPS = {
    "leveraged_inverse": ["TQQQ", "TECL", "SOXL", "SPXL", "FAS", "LABU", "QLD",
                          "SQQQ", "TECS", "SOXS", "PSQ", "SH"],
    "benchmark": ["SPY", "QQQ", "IOO", "QQQE", "SMH", "XLK", "XLY", "XLP",
                  "XLF", "VTV", "VOX", "VOOG", "VOOV"],
    "defensive": ["TLT", "IEF", "AGG", "BND", "BIL", "BSV", "BTAL", "KMLM"],
    "additional_underlying": ["XBI", "IBB"],
}
TICKERS = [t for g in GROUPS.values() for t in g]
GROUP_OF = {t: g for g, ts in GROUPS.items() for t in ts}

COLS = ["Open", "High", "Low", "Close", "Adj Close", "Volume",
        "Dividends", "Stock Splits", "Capital Gains"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def flatten(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """yf.download returns MultiIndex (Price, Ticker) columns. Flatten to Price."""
    if isinstance(df.columns, pd.MultiIndex):
        df = df.droplevel(-1, axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    for c in COLS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[COLS]
    df.index.name = "Date"
    return df


def pull_one(ticker: str, force: bool):
    path = RAW / f"{ticker}.parquet"
    if path.exists() and not force:
        df = pd.read_parquet(path)
        return df, "cached"
    df = yf.download(ticker, start=START, auto_adjust=False, actions=True,
                     progress=False, threads=False, group_by="column")
    if df is None or len(df) == 0:
        return None, "empty"
    df = flatten(df, ticker)
    df.to_parquet(path, engine="pyarrow", index=True)
    return df, "pulled"


def build_total_return(df: pd.DataFrame) -> pd.DataFrame:
    """Total return from raw (split-adjusted) close compounded with the
    dividend stream. Reinvestment at ex-date close per decision 1.11.

        r_t = (Close_t + Div_t) / Close_{t-1} - 1

    A second series adds Yahoo's Capital Gains column, so that any ticker whose
    Adj Close embeds capital-gain distributions can be identified in Step 2.
    """
    close = df["Close"].astype(float)
    div = df["Dividends"].astype(float).fillna(0.0)
    cg = df["Capital Gains"].astype(float).fillna(0.0)

    r_div = (close + div) / close.shift(1) - 1.0
    r_divcg = (close + div + cg) / close.shift(1) - 1.0
    r_px = close / close.shift(1) - 1.0

    out = pd.DataFrame(index=df.index)
    out["close"] = close
    out["adj_close"] = df["Adj Close"].astype(float)
    out["open"] = df["Open"].astype(float)
    out["high"] = df["High"].astype(float)
    out["low"] = df["Low"].astype(float)
    out["volume"] = df["Volume"].astype(float)
    out["dividend"] = div
    out["capital_gain"] = cg
    out["split"] = df["Stock Splits"].astype(float).fillna(0.0)
    out["ret_price"] = r_px
    out["ret_total"] = r_div
    out["ret_total_incl_cg"] = r_divcg
    out["tr_index"] = (1.0 + r_div.fillna(0.0)).cumprod()
    out["tr_index_incl_cg"] = (1.0 + r_divcg.fillna(0.0)).cumprod()
    out["adj_index"] = out["adj_close"] / out["adj_close"].iloc[0]
    return out


def main():
    force = "--force" in sys.argv
    RAW.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    pull_ts = datetime.now(timezone.utc).isoformat()
    coverage, manifest, panels, failed = [], [], [], []

    for i, t in enumerate(TICKERS, 1):
        try:
            df, status = pull_one(t, force)
        except Exception as exc:  # noqa: BLE001
            df, status = None, f"error: {type(exc).__name__}: {exc}"
        if df is None or len(df) == 0:
            failed.append((t, status))
            coverage.append(dict(ticker=t, group=GROUP_OF[t], status=status,
                                 rows=0, first_date="", last_date="",
                                 n_dividends=0, n_splits=0, n_capital_gains=0,
                                 n_missing_close=0))
            print(f"[{i:2d}/{len(TICKERS)}] {t:5s} FAILED {status}")
            continue

        path = RAW / f"{t}.parquet"
        first, last = df.index.min(), df.index.max()
        coverage.append(dict(
            ticker=t, group=GROUP_OF[t], status=status, rows=len(df),
            first_date=first.date().isoformat(), last_date=last.date().isoformat(),
            n_dividends=int((df["Dividends"].fillna(0) > 0).sum()),
            n_splits=int((df["Stock Splits"].fillna(0) > 0).sum()),
            n_capital_gains=int((df["Capital Gains"].fillna(0) > 0).sum()),
            n_missing_close=int(df["Close"].isna().sum()),
        ))
        manifest.append(dict(
            ticker=t, sha256=sha256_file(path), bytes=path.stat().st_size,
            rows=len(df), first_date=first.date().isoformat(),
            last_date=last.date().isoformat(), pull_timestamp_utc=pull_ts,
            yfinance_version=yf.__version__, file=str(path.relative_to(ROOT)),
        ))
        p = build_total_return(df)
        p.insert(0, "ticker", t)
        p = p.reset_index().rename(columns={"Date": "date"})
        panels.append(p)
        print(f"[{i:2d}/{len(TICKERS)}] {t:5s} {status:7s} {len(df):6d} rows  "
              f"{first.date()} -> {last.date()}  div={coverage[-1]['n_dividends']:3d} "
              f"spl={coverage[-1]['n_splits']:2d} cg={coverage[-1]['n_capital_gains']:2d}")
        if status == "pulled":
            time.sleep(0.4)

    pd.DataFrame(coverage).to_csv(OUT / "panel-coverage.csv", index=False)
    pd.DataFrame(manifest).to_csv(OUT / "etf-manifest.csv", index=False)

    panel = pd.concat(panels, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None)
    panel = panel.sort_values(["ticker", "date"]).reset_index(drop=True)
    panel.to_parquet(INTERIM / "etf-panel.parquet", engine="pyarrow", index=False)

    meta = dict(
        session="00C", pull_timestamp_utc=pull_ts,
        pull_date_local=datetime.now().date().isoformat(),
        yfinance_version=yf.__version__, pandas_version=pd.__version__,
        numpy_version=np.__version__, python_version=sys.version.split()[0],
        start_requested=START, n_tickers=len(TICKERS),
        n_failed=len(failed), failed=[dict(ticker=t, reason=r) for t, r in failed],
        auto_adjust=False, actions=True,
    )
    (OUT / "pull-metadata.json").write_text(json.dumps(meta, indent=2))

    print(f"\npanel rows: {len(panel):,}  tickers: {panel['ticker'].nunique()}")
    print(f"failed: {failed if failed else 'none'}")
    print(f"yfinance {yf.__version__}  pull {pull_ts}")


if __name__ == "__main__":
    main()
