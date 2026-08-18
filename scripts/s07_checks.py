"""Session 07, steps 2, 6, 7, 8: raw-close precision, synthetic-underlying
null audit, panel-wide split-boundary consistency, label transitions.

Step 8 counts signal-state changes only. Each sleeve's per-session state is
the identity of the branch terminal it lands in (including routed ticker
names), which maps one-to-one to the 5.1 label; a joint transition is a
change in the four-state tuple. No weight, position, or currency quantity
is computed.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src import config
from src.data import build_ticker_frame
from src.indicators import sma, wilder_rsi

OUT = ROOT / "outputs" / "session-07"
OUT.mkdir(parents=True, exist_ok=True)

CASCADE = ["QQQE", "VTV", "VOX", "TECL", "VOOG", "VOOV", "XLP",
           "TQQQ", "XLY", "FAS", "SPY"]
T10_DIPS = ["TQQQ", "SOXL", "SPXL", "LABU"]
T11_PANEL = ["SPY", "IOO", "TQQQ", "VTV", "XLF"]
NEEDED = sorted(set(CASCADE + T10_DIPS + T11_PANEL +
                    ["QQQ", "SMH", "TLT", "PSQ", "AGG", "SH", "IEF", "BND",
                     "XLK", "RYMFX", "BSV", "SQQQ"]))

frames = {t: build_ticker_frame(t, pd.read_parquet(
    ROOT / "data" / "raw" / "etf" / f"{t}.parquet")) for t in NEEDED}
CAL = frames["SPY"].index
print(f"calendar: {len(CAL):,} sessions\n")

# ---------------------------------------------------------------------------
# POSITIVE CONTROLS
# ---------------------------------------------------------------------------

def audit_series(s: pd.Series) -> dict:
    valid = s.notna().to_numpy()
    if not valid.any():
        return dict(first_date=None, last_date=None,
                    n_prelisting_null=int(len(s)), n_interior_null=0,
                    max_interior_null_run=0)
    i0 = int(np.argmax(valid))
    i1 = int(len(valid) - 1 - np.argmax(valid[::-1]))
    interior = ~valid[i0:i1 + 1]
    run = best = 0
    for x in interior:
        run = run + 1 if x else 0
        best = max(best, run)
    return dict(first_date=str(s.index[i0].date()),
                last_date=str(s.index[i1].date()),
                n_prelisting_null=i0, n_interior_null=int(interior.sum()),
                max_interior_null_run=best)

syn = pd.Series([np.nan, np.nan, 1.0, np.nan, 2.0, 3.0],
                index=pd.date_range("2020-01-01", periods=6))
r = audit_series(syn)
assert (r["n_prelisting_null"], r["n_interior_null"],
        r["max_interior_null_run"]) == (2, 1, 1), r
print("CONTROL PASSED: null-audit logic on synthetic series")

# ===========================================================================
# Step 2: raw close precision on post-2015 splitters
# ===========================================================================

s05 = pd.read_csv(ROOT / "outputs" / "session-05" / "split-audit.csv")
post15 = s05[s05.post_2015_split].ticker.tolist()
assert len(post15) == 20, post15

rows2 = []
for t in post15:
    df = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{t}.parquet")
    df.index = pd.to_datetime(df.index)
    sp = df["Stock Splits"].astype(float)
    ev = sp[sp != 0]
    d0 = df.index.min()
    stored = float(df["Close"].iloc[0])
    factor = float(ev[ev.index > d0].prod())
    recon = stored * factor
    cents_err = abs(recon - round(recon, 2))
    rows2.append(dict(
        ticker=t, earliest_date=str(d0.date()), stored_close=stored,
        cumulative_split_factor=factor, reconstructed_as_traded=recon,
        cents_rounding_error=cents_err,
        sub_cent_precision_lost=bool(cents_err > 0.005),
        implausible=bool(recon < 0.01 or recon > 100_000),
        stored_magnitude_note=("stored value itself outside 0.01-100000"
                               if (stored < 0.01 or stored > 100_000) else ""),
    ))
prec = pd.DataFrame(rows2)
prec.to_csv(OUT / "raw-close-precision.csv", index=False)
print("\n=== STEP 2: raw close precision (post-2015 splitters) ===")
print(prec[["ticker", "earliest_date", "stored_close",
            "cumulative_split_factor", "reconstructed_as_traded",
            "cents_rounding_error", "implausible"]].to_string(index=False))
print(f"float64 relative epsilon ~2.2e-16; largest relative rounding error "
      f"observed: {(prec.cents_rounding_error / prec.reconstructed_as_traded).max():.2e}")

# ===========================================================================
# Step 6: synthetic underlying null audit
# ===========================================================================

print("\n=== STEP 6: synthetic underlying series ===")
ENUM = [
    ("TQQQ/QLD/SQQQ/PSQ", "QQQ total return", "data/raw/etf/QQQ.parquet", "QQQ"),
    ("SOXL/SOXS", "semiconductor index (proxy: SMH)", "data/raw/etf/SMH.parquet", "SMH"),
    ("SPXL", "S&P 500 TR (proxy: SPY)", "data/raw/etf/SPY.parquet", "SPY"),
    ("TECL/TECS", "technology select (XLK)", "data/raw/etf/XLK.parquet", "XLK"),
    ("FAS", "financials (proxy: XLF)", "data/raw/etf/XLF.parquet", "XLF"),
    ("LABU", "S&P biotech select (XBI)", "data/raw/etf/XBI.parquet", "XBI"),
    ("UVXY/UVIX/SVIX/SVXY", "VX 30d constant maturity", "data/interim/vx-cm30.parquet", "VX_CM30"),
    ("BIL (2007-01..05 gap)", "T-bill rate", "data/raw/rates/DTB3.parquet", "DTB3"),
    ("KMLM signal role", "superseded by RYMFX under 2.5", "data/raw/etf/RYMFX.parquet", "RYMFX"),
    ("QQQE", "Nasdaq-100 Equal Weighted TR", None, None),
    ("VOOG/VOOV", "S&P 500 Growth / Value TR", None, None),
    ("BTAL", "DJ US Thematic Market Neutral Anti-Beta", None, None),
    ("BND/BSV (2007-04 gaps)", "aggregate / short-term bond index", None, None),
]
rows6 = []
for synth_for, series_name, path, key in ENUM:
    if path is None:
        rows6.append(dict(synthetic_for=synth_for, underlying=series_name,
                          status="NOT YET ACQUIRED", first_date=None,
                          last_date=None, n_prelisting_null=None,
                          n_interior_null=None, max_interior_null_run=None))
        continue
    p = ROOT / path
    if key == "VX_CM30":
        df = pd.read_parquet(p)
        s = df.set_index(pd.to_datetime(df["trade_date"]))["cm30_settle"]
        s = s.reindex(CAL[(CAL >= s.index.min()) & (CAL <= s.index.max())]
                      .union(s.index).sort_values())
        s = s.reindex(CAL)  # audit against the SPY calendar
    elif key == "DTB3":
        df = pd.read_parquet(p)
        s = df["DTB3"].astype(float)
        s.index = pd.to_datetime(s.index)
        s = s.reindex(CAL)
    else:
        s = frames[key].tr_index.reindex(CAL) if key in frames else \
            build_ticker_frame(key, pd.read_parquet(p)).tr_index.reindex(CAL)
    a = audit_series(s)
    rows6.append(dict(synthetic_for=synth_for, underlying=series_name,
                      status="present", **a))
aud6 = pd.DataFrame(rows6)
aud6.to_csv(OUT / "synthetic-underlying-null-audit.csv", index=False)
print(aud6.to_string(index=False))

# ===========================================================================
# Step 7: split-boundary consistency, panel-wide
# ===========================================================================

TOL = 0.25  # |implied-price-ratio / split-ratio - 1| bound; covers a 3x
            # fund's split-day market move. Stated in the report.
rows7 = []
for p in sorted((ROOT / "data" / "raw" / "etf").glob("*.parquet")):
    t = p.stem
    df = pd.read_parquet(p)
    df.index = pd.to_datetime(df.index)
    sp = df["Stock Splits"].astype(float)
    ev = sp[sp != 0]
    close = df["Close"].astype(float)
    for d, ratio in ev.items():
        i = df.index.get_indexer([d])[0]
        if i == 0:
            continue
        pre_d = df.index[i - 1]
        f_pre = float(ev[ev.index > pre_d].prod())
        f_post = float(ev[ev.index > d].prod()) if (ev.index > d).any() else 1.0
        implied_pre = close.loc[pre_d] * f_pre
        implied_post = close.loc[d] * f_post
        br = implied_pre / implied_post
        ok = abs(br / ratio - 1.0) < TOL
        rows7.append(dict(ticker=t, split_date=str(d.date()), ratio=ratio,
                          implied_pre=implied_pre, implied_post=implied_post,
                          boundary_ratio=br, rel_dev=br / ratio - 1.0,
                          consistent=ok))
bc = pd.DataFrame(rows7)
bc.to_csv(OUT / "split-boundary-consistency.csv", index=False)
n_fail = int((~bc.consistent).sum())
print(f"\n=== STEP 7: split boundaries: {len(bc)} events across "
      f"{bc.ticker.nunique()} tickers, tolerance {TOL:.0%} ===")
print(f"failures: {n_fail}")
if n_fail:
    print(bc[~bc.consistent].to_string(index=False))
print(f"largest |relative deviation|: {bc.rel_dev.abs().max():.3f} "
      f"({bc.loc[bc.rel_dev.abs().idxmax(), 'ticker']} "
      f"{bc.loc[bc.rel_dev.abs().idxmax(), 'split_date']})")

# ===========================================================================
# Step 8: label transitions
# ===========================================================================

PERIODS = [7, 14, 28]
TR = {t: frames[t].tr_index.reindex(CAL) for t in NEEDED}
RSI = {(t, n): wilder_rsi(TR[t].dropna(), n).reindex(CAL)
       for t in NEEDED for n in PERIODS}
# 2.5a: the trend series is read at a one-session lag
for n in PERIODS:
    RSI[("RYMFX", n)] = RSI[("RYMFX", n)].shift(1)
SMA200 = {t: sma(TR[t].dropna(), config.SMA_LONG).reindex(CAL)
          for t in ["SPY", "QQQ", "SMH", "SOXL", "TQQQ"]}
SMA20 = {t: sma(TR[t].dropna(), config.SMA_SHORT).reindex(CAL)
         for t in ["TQQQ", "RYMFX"]}
QQQ_R60 = ((TR["QQQ"] / TR["QQQ"].shift(config.CRASH_HORIZON_SESSIONS) - 1.0)
           * 100.0)
CRASH = QQQ_R60.notna() & (QQQ_R60 < config.CRASH_THRESHOLD_PCT)

def gt(s, b):
    return s.notna() & (s > b)

def lt(s, b):
    return s.notna() & (s < b)

def above(px, ma):
    return px.notna() & ma.notna() & (px > ma)

def below(px, ma):
    return px.notna() & ma.notna() & (px < ma)

NA = "~NA~"

def pair_route(a, b, if_a, if_b):
    """Pairwise a>b with NA where indeterminate."""
    out = np.where(a.notna() & b.notna(),
                   np.where(a > b, if_a, if_b), NA)
    return pd.Series(out, index=CAL, dtype=object)

def states(n, os_thr):
    ex = {t: RSI[(t, n)] for t in set(CASCADE + T11_PANEL + ["TQQQ", "QQQ", "SMH", "SOXL"])}
    # T10
    ob = pd.Series(False, index=CAL)
    for t in CASCADE:
        ob |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_1)
    trend = pair_route(RSI[("XLK", n)], RSI[("RYMFX", n)],
                       "RISKON_SVXY", "BEAR_SQQQ_TLT")
    t10 = trend.copy()
    for t, name in [("LABU", "DIP_LABU"), ("SPXL", "DIP_SPXL"),
                    ("SOXL", "DIP_SOXL"), ("TQQQ", "DIP_TECL")]:
        t10[lt(RSI[(t, n)], os_thr)] = name  # reverse order: earlier wins
    t10[ob] = "OB_UVXY"

    # T11
    t1 = pd.Series(False, index=CAL)
    t2 = pd.Series(False, index=CAL)
    for t in T11_PANEL:
        t1 |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_1)
        t2 |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_2)
    spy_above = above(TR["SPY"], SMA200["SPY"])
    xlk_vs_trend = pair_route(RSI[("XLK", n)], RSI[("RYMFX", n)], "L", "T")
    trend_below = below(TR["RYMFX"], SMA20["RYMFX"])
    bull = np.where(xlk_vs_trend == "L", "LONG3",
                    np.where(xlk_vs_trend == NA, NA,
                             np.where(trend_below, "LONG3", "SHORT3")))
    # bear sub-model routing (RS period = n)
    tqqq_up = above(TR["TQQQ"], SMA20["TQQQ"])
    psq_dip = lt(RSI[("PSQ", n)], os_thr)
    agg = pair_route(RSI[("AGG", n)], RSI[("SH", n)], "TQQQ", "PSQ")
    ief = pair_route(RSI[("IEF", n)], RSI[("PSQ", n)], "PSQ", "SQQQ")
    tail = pd.Series(np.where(tqqq_up, np.where(psq_dip, "PSQ", agg), ief),
                     index=CAL, dtype=object)
    tlt = pair_route(RSI[("TLT", n)], RSI[("PSQ", n)], "QQQ", "")
    bond = pd.Series(np.where(tlt == "QQQ", "QQQ",
                              np.where(tlt == NA, NA, tail)),
                     index=CAL, dtype=object)
    bnd = pair_route(RSI[("BND", n)], RSI[("QQQ", n)], "QLD", "BTAL")
    feaver = pd.Series(np.where(CRASH, bnd, tail), index=CAL, dtype=object)
    bear = pd.Series(np.where((bond == NA) | (feaver == NA), NA,
                              "BEAR_" + bond.astype(str) + "_" + feaver.astype(str)),
                     index=CAL, dtype=object)
    t11 = pd.Series(np.where(spy_above, bull, bear), index=CAL, dtype=object)
    t11[lt(RSI[("SPY", n)], os_thr)] = "DIP_SPXL"
    t11[lt(RSI[("TQQQ", n)], os_thr)] = "DIP_TQQQ"
    t11[t1] = "T1_HEDGE"
    t11[t2] = "T2_UVXY"

    # S2
    sqqq_bsv = pair_route(RSI[("SQQQ", n)], RSI[("BSV", n)], "SQQQ", "BSV")
    s2 = pd.Series(np.where(below(TR["TQQQ"], SMA20["TQQQ"]), sqqq_bsv,
                            "TQQQ"), index=CAL, dtype=object)
    s2[lt(RSI[("SOXL", n)], os_thr)] = "SOXL"
    s2[lt(RSI[("TQQQ", n)], os_thr)] = "TECL"
    gate = above(TR["TQQQ"], SMA200["TQQQ"])
    s2[gate & gt(RSI[("TQQQ", n)], config.OVERBOUGHT_TIER_1)] = "UVXY"
    s2[gate & ~gt(RSI[("TQQQ", n)], config.OVERBOUGHT_TIER_1)] = "TQQQ"

    # S3 (UVIX unavailable in panel -> vol leg is UVXY constantly; noted)
    votes = sum(above(TR[t], SMA200[t]).astype(int)
                for t in ["SPY", "QQQ", "SMH", "SOXL"])
    bull3 = votes >= 3
    ob3 = pd.Series(False, index=CAL)
    for t in ["SPY", "QQQ", "SMH", "SOXL"]:
        ob3 |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_1)
    s3 = pd.Series("CASH", index=CAL, dtype=object)
    s3[lt(RSI[("QQQ", n)], os_thr) | lt(RSI[("SMH", n)], os_thr)] = "SOXL"
    s3[bull3 & ob3] = "VOL_UVXY"
    s3[bull3 & ~ob3] = "TS_SPLIT"
    return t10, t11, s2, s3

rows8 = []
detail_rows = []
print("\n=== STEP 8: label transitions ===")
for n, os_thr in [(14, 30), (7, 40), (28, 20)]:
    t10, t11, s2, s3 = states(n, os_thr)
    joint = t10 + "|" + t11 + "|" + s2 + "|" + s3
    valid = ~(t10.eq(NA) | t11.str.contains(NA, regex=False) |
              s2.eq(NA) | s3.eq(NA))
    # measurement window: the contiguous fully-determinate span, i.e. every
    # session after the LAST indeterminate one. Earlier sporadically-valid
    # sessions (an override branch firing before the trend inputs exist)
    # would join non-adjacent sessions and manufacture spurious transitions.
    inv = (~valid).to_numpy().nonzero()[0]
    start_i = int(inv.max()) + 1 if len(inv) else 0
    excluded = start_i
    span = joint.iloc[start_i:]
    interior_invalid = 0  # by construction
    years = (span.index[-1] - span.index[0]).days / 365.25

    trans = (span != span.shift()).to_numpy().copy()
    trans[0] = False
    n_trans = int(trans.sum())
    lengths = np.diff(np.flatnonzero(np.concatenate(
        ([True], trans, [True]))))
    per_sleeve = {}
    for name, s in [("T10", t10), ("T11", t11), ("S2", s2), ("S3", s3)]:
        sv = s.loc[span.index]
        tv = (sv != sv.shift()).to_numpy().copy(); tv[0] = False
        per_sleeve[name] = int(tv.sum())
    rows8.append(dict(
        rsi_period=n, oversold=os_thr,
        window_start=str(span.index[0].date()),
        window_end=str(span.index[-1].date()),
        sessions=len(span), sessions_excluded_before_span=excluded,
        interior_indeterminate=interior_invalid,
        joint_transitions=n_trans,
        transitions_per_year=n_trans / years,
        median_hold_sessions=float(np.median(lengths)),
        max_hold_sessions=int(lengths.max()),
        p90_hold_sessions=float(np.percentile(lengths, 90)),
        **{f"transitions_{k}": v for k, v in per_sleeve.items()},
    ))
    for L in np.unique(lengths):
        detail_rows.append(dict(rsi_period=n, oversold=os_thr,
                                hold_sessions=int(L),
                                count=int((lengths == L).sum())))
    r = rows8[-1]
    print(f"  ({n},{os_thr}): {r['sessions']} sessions from "
          f"{r['window_start']}; joint {n_trans} transitions "
          f"({r['transitions_per_year']:.1f}/yr); median hold "
          f"{r['median_hold_sessions']:.0f}, max {r['max_hold_sessions']}; "
          f"per-sleeve {per_sleeve}; interior indeterminate "
          f"{interior_invalid}")

pd.DataFrame(rows8).to_csv(OUT / "label-transitions.csv", index=False)
pd.DataFrame(detail_rows).to_csv(OUT / "label-transitions-holdlengths.csv",
                                 index=False)
print("\nDONE")
