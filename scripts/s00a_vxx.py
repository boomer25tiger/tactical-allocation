"""Session 00a, step 6. Validate the constructed CM30 series against VXX.

Return correlation is the measurement of interest. VXX carries fees and roll
costs the raw futures series does not, so a level difference is expected and is
not treated as a failure.

No strategy return, Sharpe ratio or performance statistic is computed. These are
correlations and divergences between two data series.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00a"

WINDOW = 252


def main():
    cm = pd.read_parquet(INTERIM / "vx-cm30.parquet")
    cm = cm[["trade_date", "cm30_settle"]].sort_values("trade_date")

    raw = yf.download("VXX", start="2009-01-01", end="2026-08-16",
                      auto_adjust=False, actions=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    raw = raw.reset_index()
    raw.columns = [str(c) for c in raw.columns]
    print("yfinance VXX columns:", list(raw.columns))
    print(f"yfinance VXX rows={len(raw)} "
          f"{raw['Date'].min().date()} .. {raw['Date'].max().date()}")
    raw.to_parquet(INTERIM / "vxx-yfinance-raw.parquet", index=False)

    px = raw[["Date", "Adj Close"]].rename(columns={"Date": "trade_date",
                                                    "Adj Close": "vxx_adj"})
    px["trade_date"] = pd.to_datetime(px["trade_date"]).dt.tz_localize(None)

    m = cm.merge(px, on="trade_date", how="inner").sort_values("trade_date")
    m["cm30_ret"] = m["cm30_settle"].pct_change()
    m["vxx_ret"] = m["vxx_adj"].pct_change()
    m = m.dropna(subset=["cm30_ret", "vxx_ret"])
    m["year"] = m["trade_date"].dt.year
    print(f"overlap sessions={len(m)} "
          f"{m['trade_date'].min().date()} .. {m['trade_date'].max().date()}")

    # rolling 252-session cumulative divergence
    lc = np.log1p(m["cm30_ret"])
    lv = np.log1p(m["vxx_ret"])
    cum_c = lc.rolling(WINDOW).sum()
    cum_v = lv.rolling(WINDOW).sum()
    m["cum_div_252"] = (np.expm1(cum_c) - np.expm1(cum_v)).abs()

    g = m.groupby("year")
    val = pd.DataFrame({
        "overlap_sessions": g.size(),
        "daily_return_correlation": g.apply(
            lambda x: x["cm30_ret"].corr(x["vxx_ret"]), include_groups=False),
        "max_rolling_252_cumulative_divergence": g["cum_div_252"].max(),
        "cm30_mean_abs_daily_ret": g["cm30_ret"].apply(lambda s: s.abs().mean()),
        "vxx_mean_abs_daily_ret": g["vxx_ret"].apply(lambda s: s.abs().mean()),
    })
    val.index.name = "year"
    val = val.reset_index()
    val.to_csv(OUT / "vxx-validation.csv", index=False)
    m[["trade_date", "cm30_settle", "vxx_adj", "cm30_ret", "vxx_ret",
       "cum_div_252"]].to_parquet(INTERIM / "vxx-cm30-overlap.parquet", index=False)

    with pd.option_context("display.width", 200):
        print(val.to_string(index=False))
    print(f"\nfull-overlap correlation: {m['cm30_ret'].corr(m['vxx_ret']):.6f}")


if __name__ == "__main__":
    main()
