"""Session 00b, step 4. Validate constructions A, B, C against VIXY and VXX.

VIXY is an ETF and should not carry the share-class discontinuity that truncates
yfinance's VXX history at the 2018 iPath Series B launch.

No strategy return, Sharpe ratio or performance statistic is computed. These are
correlations and divergences between data series.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00b"

WINDOW = 252


def pull(ticker, start):
    raw = yf.download(ticker, start=start, end="2026-08-16",
                      auto_adjust=False, actions=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    raw = raw.reset_index()
    raw.columns = [str(c) for c in raw.columns]
    raw["Date"] = pd.to_datetime(raw["Date"]).dt.tz_localize(None)
    print(f"{ticker}: rows={len(raw)} first={raw['Date'].min().date()} "
          f"last={raw['Date'].max().date()}")
    splits = raw[raw.get("Stock Splits", pd.Series(0, index=raw.index)) != 0]
    if len(splits):
        print(f"  splits: {[(str(d.date()), float(s)) for d, s in zip(splits['Date'], splits['Stock Splits'])]}")
    rc = raw["Close"].pct_change()
    ra = raw["Adj Close"].pct_change()
    gap = (rc - ra).abs().max()
    print(f"  max |ret(Close) - ret(AdjClose)| = {gap:.3e}")
    raw.to_parquet(INTERIM / f"{ticker.lower()}-yfinance-raw-s00b.parquet",
                   index=False)
    return raw[["Date", "Adj Close"]].rename(
        columns={"Date": "trade_date", "Adj Close": f"{ticker.lower()}_px"})


def pull_vixy_nav():
    """ProShares publishes VIXY daily NAV. The stated 'NAV Change (%)' column is
    split-neutral and was verified against NAV / Prior NAV - 1 to 5e-8."""
    import requests
    import io
    url = "https://accounts.profunds.com/etfdata/ByFund/VIXY-historical_nav.csv"
    H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
    r = requests.get(url, headers=H, timeout=90)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    d["trade_date"] = pd.to_datetime(d["Date"], format="%m/%d/%Y")
    d = d.sort_values("trade_date").reset_index(drop=True)
    d["etp_ret"] = d["NAV Change (%)"] / 100.0
    chk = (d["etp_ret"] - (d["NAV"] / d["Prior NAV"] - 1.0)).abs().max()
    print(f"VIXY NAV (issuer): rows={len(d)} first={d['trade_date'].min().date()} "
          f"last={d['trade_date'].max().date()}  "
          f"max|stated - NAV/PriorNAV-1|={chk:.2e}")
    d.to_parquet(INTERIM / "vixy-nav-proshares-s00b.parquet", index=False)
    return d[["trade_date", "etp_ret"]]


def compare(cons_df, tag, etp_px, etp_tag):
    m = cons_df[["trade_date", "cdr"]].merge(etp_px, on="trade_date", how="inner")
    m = m.sort_values("trade_date")
    if "etp_ret" not in m.columns:
        m["etp_ret"] = m[f"{etp_tag.lower()}_px"].pct_change()
    m = m.dropna(subset=["cdr", "etp_ret"])
    if m.empty:
        return pd.DataFrame()
    lc = np.log1p(m["cdr"].clip(lower=-0.999))
    lv = np.log1p(m["etp_ret"].clip(lower=-0.999))
    m["cum_div"] = (np.expm1(lc.rolling(WINDOW).sum())
                    - np.expm1(lv.rolling(WINDOW).sum())).abs()
    m["year"] = m["trade_date"].dt.year
    g = m.groupby("year")
    out = pd.DataFrame({
        "overlap_sessions": g.size(),
        "daily_return_correlation": g.apply(
            lambda x: x["cdr"].corr(x["etp_ret"]), include_groups=False),
        "max_rolling_252_cumulative_divergence": g["cum_div"].max(),
        "construction_mean_abs_daily_ret": g["cdr"].apply(lambda s: s.abs().mean()),
        "etp_mean_abs_daily_ret": g["etp_ret"].apply(lambda s: s.abs().mean()),
    }).reset_index()
    out.insert(0, "benchmark", etp_tag)
    out.insert(0, "construction", tag)
    full = m["cdr"].corr(m["etp_ret"])
    print(f"  {tag:18s} vs {etp_tag}: n={len(m)} full-overlap corr={full:.6f}")
    return out


def main():
    vixy = pull("VIXY", "2010-01-01")
    vxx = pull("VXX", "2009-01-01")

    cons = {
        "A_interpolation": pd.read_parquet(INTERIM / "vx-cm30-a.parquet"),
        "B_sp_roll": pd.read_parquet(INTERIM / "vx-cm30-b.parquet"),
        "C_fixed_roll": pd.read_parquet(INTERIM / "vx-cm30-c.parquet"),
    }

    try:
        vixy_nav = pull_vixy_nav()
    except Exception as e:
        print(f"VIXY NAV pull FAILED: {type(e).__name__}: {e}")
        vixy_nav = None

    parts = []
    benches = [("VIXY", vixy), ("VXX", vxx)]
    if vixy_nav is not None:
        benches.append(("VIXY_NAV", vixy_nav))
    for etp_tag, etp in benches:
        print(f"\n--- vs {etp_tag} ---")
        for tag, df in cons.items():
            parts.append(compare(df, tag, etp, etp_tag))

    res = pd.concat([p for p in parts if len(p)], ignore_index=True)
    res = res.sort_values(["benchmark", "construction", "year"])
    res.to_csv(OUT / "validation-extended.csv", index=False)

    print("\n=== mean correlation by construction and benchmark ===")
    piv = res.pivot_table(index="construction", columns="benchmark",
                          values="daily_return_correlation", aggfunc="mean")
    print(piv.round(4).to_string())

    print("\n=== VIXY correlation by year ===")
    p2 = res[res.benchmark == "VIXY"].pivot(
        index="year", columns="construction", values="daily_return_correlation")
    print(p2.round(4).to_string())

    print("\n=== VXX correlation by year ===")
    p3 = res[res.benchmark == "VXX"].pivot(
        index="year", columns="construction", values="daily_return_correlation")
    print(p3.round(4).to_string())


if __name__ == "__main__":
    main()
