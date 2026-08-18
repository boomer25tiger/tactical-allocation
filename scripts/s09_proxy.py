"""Session 09, step 3: proxy accuracy (informs 2.12 and 2.7).

Measures tracking differences between frozen proxy ETF total-return series
and their benchmark indices wherever both are obtainable, at the finest
resolution each index is served. Free index symbols are read at run time and
NOT frozen. A tracking difference between two series is a property of the
series; no position is formed and no strategy quantity is computed.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import yfinance as yf

from src.data import build_ticker_frame

OUT = ROOT / "outputs" / "session-09"
OUT.mkdir(parents=True, exist_ok=True)


def frozen_tr(ticker: str) -> pd.Series:
    tf = build_ticker_frame(ticker, pd.read_parquet(
        ROOT / "data" / "raw" / "etf" / f"{ticker}.parquet"))
    return tf.tr_index


def index_close(sym: str):
    """(series, status). Daily closes if served; None + reason otherwise."""
    try:
        h = yf.Ticker(sym).history(period="max", auto_adjust=False)
    except Exception as e:
        return None, f"error: {type(e).__name__}"
    if h.empty:
        return None, "no daily history served"
    s = h["Close"]
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    return s, f"daily, {len(s):,} rows from {s.index.min().date()}"


def weekly_probe(sym: str) -> str:
    """Settle whether a 5d-gated symbol serves ANY history at weekly bars."""
    try:
        h = yf.Ticker(sym).history(period="max", interval="1wk")
        if h.empty:
            return "weekly probe: empty"
        return f"weekly probe: {len(h)} rows from {h.index.min().date()}"
    except Exception as e:
        return f"weekly probe refused: {str(e)[:80]}"


def measure(proxy_tr: pd.Series, idx: pd.Series, start=None, end=None) -> dict:
    j = pd.concat({"p": proxy_tr, "i": idx}, axis=1).dropna()
    if start:
        j = j.loc[start:]
    if end:
        j = j.loc[:end]
    rp = j["p"].pct_change().dropna()
    ri = j["i"].pct_change().dropna()
    d = (rp - ri).dropna()
    log_ratio = np.log1p(rp) - np.log1p(ri)
    roll = log_ratio.rolling(252).sum()
    return dict(
        n_sessions=len(d),
        window=f"{j.index.min().date()}..{j.index.max().date()}",
        ann_tracking_diff_pct=float(d.mean() * 252 * 100),
        ann_td_sd_pct=float(d.std(ddof=1) * np.sqrt(252) * 100),
        max_roll252_divergence_pct=float(
            (np.exp(roll.abs().max()) - 1) * 100) if roll.notna().any() else np.nan,
        return_correlation=float(rp.corr(ri)),
    )


rows = []

def add(pair, proxy, comparator, comparator_type, resolution, status,
        metrics=None, note=""):
    row = dict(pair=pair, proxy=proxy, comparator=comparator,
               comparator_type=comparator_type, resolution=resolution,
               status=status, note=note)
    if metrics:
        row.update(metrics)
    rows.append(row)
    m = (f"  TD {metrics['ann_tracking_diff_pct']:+.3f}%/yr sd "
         f"{metrics['ann_td_sd_pct']:.3f}% maxroll "
         f"{metrics['max_roll252_divergence_pct']:.2f}% corr "
         f"{metrics['return_correlation']:.5f} [{metrics['window']}]"
         if metrics else "")
    print(f"{pair:28s} {status:22s} {m} {note}")


# --- POSITIVE CONTROL: SPY vs ^SP500TR ------------------------------------
# The control asserts the MACHINERY: the mean tracking difference must sit
# near the fee, and the modern era must correlate near-perfectly. Full-window
# daily noise is era-structured (early-era ETF closing prints deviate from
# index closes) and is itself a finding, not a machinery failure.
sp500tr, st = index_close("^SP500TR")
assert sp500tr is not None, "CONTROL FAILED: ^SP500TR not served"
spy = frozen_tr("SPY")
m_full = measure(spy, sp500tr)
m_modern = measure(spy, sp500tr, start="2015-01-01")
assert abs(m_full["ann_tracking_diff_pct"]) < 0.35, m_full
# 0.995 catches machinery breakage (misalignment craters correlation) while
# accommodating Yahoo's 2dp index rounding (~2bp on a ~5,000 level) plus
# genuine close-print basis; observed modern-era corr is ~0.9984.
assert m_modern["return_correlation"] > 0.995, m_modern
assert m_modern["ann_td_sd_pct"] < 2.0, m_modern
print(f"CONTROL PASSED: mean TD {m_full['ann_tracking_diff_pct']:+.3f}%/yr "
      f"(≈ fee); 2015+ corr {m_modern['return_correlation']:.5f}\n")

add("SPXL/SH proxy: SPY", "SPY tr_index", "^SP500TR", "total-return index",
    "daily", "MEASURED EXACT (full)", m_full,
    "true benchmark, TR form; mean TD isolates fee + replication drag; "
    "daily sd is dominated by early-era ETF-close-vs-index-close prints")
add("SPXL/SH proxy: SPY 2010+", "SPY tr_index", "^SP500TR",
    "total-return index", "daily", "MEASURED EXACT (2010+)",
    measure(spy, sp500tr, start="2010-01-01"),
    "modern era: close-print noise an order of magnitude smaller")
add("SPXL/SH proxy: SPY pre-2010", "SPY tr_index", "^SP500TR",
    "total-return index", "daily", "MEASURED EXACT (pre-2010)",
    measure(spy, sp500tr, end="2009-12-31"),
    "early era: 25-33bp/day close-print noise; bears on 2.7 band widths")

# --- QQQ vs price index and (attempted) TR index ---------------------------
ndx, st = index_close("^NDX")
qqq = frozen_tr("QQQ")
m = measure(qqq, ndx)
add("TQQQ/QLD/SQQQ/PSQ: QQQ", "QQQ tr_index", "^NDX", "PRICE index",
    "daily", "MEASURED (price basis)", m,
    "TD = dividend yield minus fee; the dividend wedge the step asked for")
add("TQQQ/QLD/SQQQ/PSQ: QQQ 2010+", "QQQ tr_index", "^NDX", "PRICE index",
    "daily", "MEASURED (price basis, 2010+)",
    measure(qqq, ndx, start="2010-01-01"),
    "era split isolates the wedge from early-era close-print noise")

xndx, st_x = index_close("^XNDX")
if xndx is not None:
    m = measure(frozen_tr("QQQ"), xndx)
    add("TQQQ/QLD/SQQQ/PSQ: QQQ", "QQQ tr_index", "^XNDX", "total-return index",
        "daily", "MEASURED EXACT", m)
else:
    add("TQQQ/QLD/SQQQ/PSQ: QQQ", "QQQ tr_index", "^XNDX", "total-return index",
        "none", "NOT MEASURABLE", None,
        f"{st_x}; {weekly_probe('^XNDX')}")

# --- SMH vs ^SOX over the PHLX period --------------------------------------
sox, st = index_close("^SOX")
m = measure(frozen_tr("SMH"), sox, end="2021-08-24")
add("SOXL/SOXS pre-switch: SMH", "SMH tr_index", "^SOX", "PRICE index",
    "daily", "MEASURED (price basis)", m,
    "SMH tracks MVIS 25 while funds tracked PHLX to 2021-08-25; TD mixes "
    "basket mismatch WITH the dividend wedge")
add("SOXL/SOXS post-switch: SMH", "SMH tr_index", "ICE Semiconductor Index",
    "total-return index", "none", "NOT MEASURABLE", None,
    "ICE index effectively gated (^ICESEMI serves 204 rows from 2025-10)")

# --- gated Select Sector / biotech benchmarks ------------------------------
for pair, proxy, sym, note in [
    ("TECL/TECS: XLK", "XLK tr_index", "^IXT",
     "exact benchmark (Technology Select Sector Index) gated"),
    ("FAS 2022-08+: XLF", "XLF tr_index", "^IXM",
     "exact benchmark (Financials Select Sector Index) gated"),
    ("LABU: XBI", "XBI tr_index", "^SPSIBI",
     "exact benchmark (S&P Biotech Select Industry) gated"),
]:
    s, st_g = index_close(sym)
    if s is not None:
        m = measure(frozen_tr(proxy.split()[0]), s)
        add(pair, proxy, sym, "index", "daily", "MEASURED", m, note)
    else:
        add(pair, proxy, sym, "index", "none", "NOT MEASURABLE", None,
            f"{note}; {st_g}; {weekly_probe(sym)}")

add("FAS 2008..2022-02: XLF", "XLF tr_index",
    "Russell 1000 Financial Services Index", "index", "none",
    "NOT MEASURABLE", None, "no free source found (session 08 inventory)")
add("FAS 2022-02..07: XLF", "XLF tr_index",
    "Russell 1000 Financials 40 Act 15/22.5 Daily Capped Index", "index",
    "none", "NOT MEASURABLE", None, "no free source found")

# --- nearest-free-comparator context rows (explicitly NOT the benchmark) ---
sp45, _ = index_close("^SP500-45")
m = measure(frozen_tr("XLK"), sp45)
add("context: XLK vs S&P500 IT", "XLK tr_index", "^SP500-45",
    "PRICE index, RELATED-NOT-IDENTICAL", "daily", "MEASURED (context only)",
    m, "S&P 500 IT sector index is not the Select Sector index (capping "
       "differs) and is price-form; bounding context, not benchmark accuracy")
sp40, _ = index_close("^SP500-40")
m = measure(frozen_tr("XLF"), sp40)
add("context: XLF vs S&P500 Fin", "XLF tr_index", "^SP500-40",
    "PRICE index, RELATED-NOT-IDENTICAL", "daily", "MEASURED (context only)",
    m, "same caveats as XLK context row")

df = pd.DataFrame(rows)
df.to_csv(OUT / "proxy-accuracy.csv", index=False)
print(f"\nWROTE outputs/session-09/proxy-accuracy.csv ({len(df)} rows)")
print("symbols read at run time, not frozen: ^SP500TR ^NDX ^XNDX(attempt) "
      "^SOX ^IXT(attempt) ^IXM(attempt) ^SPSIBI(attempt) ^SP500-45 ^SP500-40")
