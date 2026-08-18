"""Session 05, steps 3-6: split audit, dollar volume, spread estimation,
tier assignment.

Reads the 36 frozen parquets; writes CSVs under outputs/session-05/ only.
No strategy return, allocation, weight, or performance statistic; no sleeve
function is called. Spread and dollar-volume distributions are properties of
individual price series.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.spread import abdi_ranaldo, corwin_schultz

OUT = ROOT / "outputs" / "session-05"
OUT.mkdir(parents=True, exist_ok=True)

STRESS = {
    "GFC_2008H2": ("2008-09-01", "2009-03-31"),
    "COVID_2020": ("2020-02-15", "2020-04-30"),
}

LEVERAGED_OR_INVERSE = {"TQQQ", "SOXL", "SPXL", "TECL", "FAS", "LABU",
                        "QLD", "SQQQ", "TECS", "SOXS"}

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

frames = {}
for p in sorted((ROOT / "data" / "raw" / "etf").glob("*.parquet")):
    df = pd.read_parquet(p)
    df.index = pd.to_datetime(df.index)
    frames[p.stem] = df
assert len(frames) == 36, len(frames)
print(f"loaded {len(frames)} parquets")

# ---------------------------------------------------------------------------
# Step 3: split audit
# ---------------------------------------------------------------------------

YEARS = list(range(1995, 2027))
split_rows = []
for t, df in frames.items():
    sp = df["Stock Splits"].astype(float)
    ev = sp[sp != 0]
    events = "; ".join(f"{d.date()}:{r:g}" for d, r in ev.items())
    row = dict(
        ticker=t,
        n_splits=len(ev),
        split_events=events,
        post_2015_split=bool((ev.index >= "2016-01-01").any()),
    )
    for y in YEARS:
        after = ev[ev.index >= f"{y}-01-01"]
        row[f"cum_factor_from_{y}"] = float(after.prod()) if len(after) else 1.0
    split_rows.append(row)
splits = pd.DataFrame(split_rows)
splits.to_csv(OUT / "split-audit.csv", index=False)

flagged = splits[splits.post_2015_split]
print("\n=== STEP 3: split audit ===")
print(f"tickers with any split: {(splits.n_splits > 0).sum()} of 36")
print(f"tickers with a post-2015 split (stored history diverges from "
      f"as-traded): {len(flagged)}")
show = flagged[["ticker", "n_splits", "split_events", "cum_factor_from_2015"]]
print(show.to_string(index=False))

# cross-checks: three tickers with post-2015 splits against known as-traded
# levels. Anchors are approximate levels from contemporaneous split
# coverage; the check is a band, exactly the class of plausibility test
# that caught the session 04 defects.
CHECKS = [
    # ticker, date, expected as-traded close, +/- band, source note
    ("SMH", "2023-05-04", 249.0, 15.0,
     "final pre-split session of the 2023-05-05 2:1; SMH traded ~ $250"),
    ("TQQQ", "2021-01-20", 198.0, 15.0,
     "final pre-split session of the 2021-01-21 2:1; contemporaneous "
     "coverage put TQQQ near $99-100 immediately AFTER the split, so "
     "~ $198 before it. (An earlier draft anchored ~ $100, the post-split "
     "level misremembered as pre-split; recorded in the session report.)"),
    ("SOXL", "2021-02-26", 610.0, 60.0,
     "late Feb 2021, ahead of the 2021-03-02 15:1 at ~ $600-650"),
]
print("\ncross-checks (stored close x cumulative future splits vs anchor):")
xchk = []
for t, d, anchor, band, src in CHECKS:
    df = frames[t]
    d = pd.Timestamp(d)
    stored = float(df.loc[d, "Close"])
    sp = df["Stock Splits"].astype(float)
    ev = sp[sp != 0]
    factor = float(ev[ev.index > d].prod()) if (ev.index > d).any() else 1.0
    implied = stored * factor
    ok = abs(implied - anchor) <= band

    # memory-free internal check: across the next split boundary the
    # implied as-traded price must fall by ~the split ratio (within a
    # generous daily-move band), i.e. the stored series is continuous
    # while the as-traded series jumps.
    nxt = ev[ev.index > d].index[0]
    ratio = float(ev.loc[nxt])
    pre_i = df.index.get_indexer([nxt])[0] - 1
    pre_d = df.index[pre_i]
    f_pre = float(ev[ev.index > pre_d].prod())
    f_post = float(ev[ev.index > nxt].prod()) if (ev.index > nxt).any() else 1.0
    implied_pre = float(df.loc[pre_d, "Close"]) * f_pre
    implied_post = float(df.loc[nxt, "Close"]) * f_post
    # as-traded falls BY the split ratio across the boundary, so
    # implied_pre / implied_post ~ 1/ratio for reverse splits (ratio < 1)
    # and ~ ratio for forward splits -- in both cases boundary/split ~ 1,
    # off by the session's genuine market move (up to ~20% for a 3x fund).
    boundary_ratio = implied_pre / implied_post
    boundary_ok = abs(boundary_ratio / ratio - 1.0) < 0.20
    xchk.append(dict(ticker=t, date=str(d.date()), stored_close=stored,
                     future_split_factor=factor, implied_as_traded=implied,
                     anchor=anchor, band=band, within_band=ok,
                     boundary_split=f"{nxt.date()}:{ratio:g}",
                     boundary_price_ratio=round(boundary_ratio, 4),
                     boundary_consistent=boundary_ok, source=src))
    print(f"  {t:5s} {d.date()}  stored {stored:9.3f} x {factor:g} = "
          f"{implied:9.2f}  vs anchor {anchor:.0f} +/- {band:.0f} -> "
          f"{'PASS' if ok else 'FAIL'}   boundary {nxt.date()} ratio "
          f"{boundary_ratio:.3f} (split {ratio:g}) -> "
          f"{'CONSISTENT' if boundary_ok else 'INCONSISTENT'}")
pd.DataFrame(xchk).to_csv(OUT / "split-crosschecks.csv", index=False)

# ---------------------------------------------------------------------------
# Step 4: dollar volume (raw close x volume; split-basis cancels in the
# product since price and volume are adjusted in opposite directions)
# ---------------------------------------------------------------------------

dv_rows = []
for t, df in frames.items():
    dv = (df["Close"].astype(float) * df["Volume"].astype(float)).dropna()
    windows = [("full", dv)] + [(str(y), dv[dv.index.year == y])
                                for y in sorted(dv.index.year.unique())]
    for wname, w in windows:
        if len(w) == 0:
            continue
        dv_rows.append(dict(
            ticker=t, window=wname, n_sessions=len(w),
            first_date=str(w.index.min().date()),
            last_date=str(w.index.max().date()),
            median_dollar_volume=float(w.median()),
            p10_dollar_volume=float(w.quantile(0.10)),
            p90_dollar_volume=float(w.quantile(0.90)),
        ))
dv_table = pd.DataFrame(dv_rows)
dv_table.to_csv(OUT / "dollar-volume.csv", index=False)

full_dv = dv_table[dv_table.window == "full"].set_index("ticker")
print("\n=== STEP 4: median daily dollar volume, full history ===")
print((full_dv["median_dollar_volume"].sort_values(ascending=False) / 1e6)
      .round(1).to_string())

# ---------------------------------------------------------------------------
# Step 5: spread estimation
# ---------------------------------------------------------------------------

def cs_stats(sub: pd.DataFrame) -> dict:
    """Statistics for one window of CS output, all three treatments."""
    v = sub.dropna(subset=["spread"])
    if len(v) == 0:
        return {}
    out = dict(n=len(v), neg_rate=float(v["negative"].mean()))
    for name, series in (
        ("zero", v["spread_zero"]),
        ("unchanged", v["spread"]),
        ("exclude", v.loc[~v["negative"], "spread"]),
    ):
        if len(series):
            out[f"median_bp_{name}"] = float(series.median()) * 1e4
            out[f"p10_bp_{name}"] = float(series.quantile(0.10)) * 1e4
            out[f"p90_bp_{name}"] = float(series.quantile(0.90)) * 1e4
        else:
            out[f"median_bp_{name}"] = np.nan
            out[f"p10_bp_{name}"] = np.nan
            out[f"p90_bp_{name}"] = np.nan
    return out


def ar_stats(sub: pd.DataFrame) -> dict:
    v = sub.dropna(subset=["s2"])
    if len(v) == 0:
        return {}
    return dict(
        ar_n=len(v),
        ar_neg_rate=float(v["negative"].mean()),
        ar_median_bp=float(v["spread"].median()) * 1e4,
        ar_p10_bp=float(v["spread"].quantile(0.10)) * 1e4,
        ar_p90_bp=float(v["spread"].quantile(0.90)) * 1e4,
    )


est_rows = []
ts_frames = {}
for t, df in frames.items():
    cs = corwin_schultz(df["High"], df["Low"], df["Close"])
    ar = abdi_ranaldo(df["High"], df["Low"], df["Close"])
    ts_frames[t] = pd.DataFrame({
        "cs_spread": cs["spread"], "cs_negative": cs["negative"],
        "ar_spread": ar["spread"], "ar_negative": ar["negative"],
    })

    windows = [("full", None)]
    windows += [(str(y), (f"{y}-01-01", f"{y}-12-31"))
                for y in sorted(df.index.year.unique())]
    windows += list(STRESS.items())
    for wname, span in windows:
        sub_cs = cs if span is None else cs.loc[span[0]: span[1]]
        sub_ar = ar if span is None else ar.loc[span[0]: span[1]]
        s = cs_stats(sub_cs)
        if not s:
            continue
        s.update(ar_stats(sub_ar))
        est_rows.append(dict(ticker=t, window=wname, **s))

est = pd.DataFrame(est_rows)
est.to_csv(OUT / "spread-estimates.csv", index=False)

ts_long = pd.concat(
    {t: f for t, f in ts_frames.items()}, names=["ticker", "date"]
).reset_index()
ts_long.to_csv(OUT / "spread-timeseries.csv", index=False)

full_est = est[est.window == "full"].set_index("ticker")
print("\n=== STEP 5: CS median spread bp (zero treatment), full history ===")
print(full_est["median_bp_zero"].sort_values().round(2).to_string())
print("\nnegative-estimate rate (CS), full history:")
print(full_est["neg_rate"].sort_values(ascending=False).round(3).to_string())

print("\nstress windows, CS zero-treatment median bp (tickers alive then):")
for wname in STRESS:
    sub = est[est.window == wname].set_index("ticker")
    if len(sub):
        print(f"  {wname}: n={len(sub)}")
        print("    " + sub["median_bp_zero"].sort_values().round(2)
              .to_string().replace("\n", "\n    "))

# ---------------------------------------------------------------------------
# Step 6: tier assignment
# ---------------------------------------------------------------------------
# RULE (one sentence): Rank the 36 tickers by median daily dollar volume
# (descending) and by CS zero-treatment median spread (ascending), and
# assign each ticker to the tercile -- 12/12/12 -- of the AVERAGE of those
# two ranks, ties broken by the dollar-volume rank.

rank_dv = full_dv["median_dollar_volume"].rank(ascending=False)
rank_sp = full_est["median_bp_zero"].rank(ascending=True)
combo = (rank_dv + rank_sp) / 2.0
order = pd.DataFrame({"rank_dv": rank_dv, "rank_spread": rank_sp,
                      "rank_avg": combo}).sort_values(["rank_avg", "rank_dv"])
order["tier"] = [1] * 12 + [2] * 12 + [3] * 12

def tercile(r: pd.Series) -> pd.Series:
    s = r.sort_values()
    out = pd.Series(index=s.index, dtype=int)
    out.iloc[:12], out.iloc[12:24], out.iloc[24:] = 1, 2, 3
    return out

t_dv = tercile(rank_dv)
t_sp = tercile(rank_sp)
order["tier_by_dv"] = t_dv
order["tier_by_spread"] = t_sp
order["criteria_disagree"] = order.tier_by_dv != order.tier_by_spread
order["median_spread_bp"] = full_est["median_bp_zero"]
order["median_dollar_volume"] = full_dv["median_dollar_volume"]
order.index.name = "ticker"
order.to_csv(OUT / "tier-assignment.csv")

tier_median = order.groupby("tier")["median_spread_bp"].median()
mult_raw = tier_median / tier_median.loc[1]
mult = mult_raw.round(1)

# sensitivity: same tier membership, exclude-treatment medians instead of
# zero-treatment, since zero-range days pull the zero-treatment medians of
# thinly traded names to zero (bias-visibility per step 5)
order["median_spread_bp_exclude"] = full_est["median_bp_exclude"]
tier_median_ex = order.groupby("tier")["median_spread_bp_exclude"].median()
mult_ex = (tier_median_ex / tier_median_ex.loc[1]).round(4)

print("\n=== STEP 6: tier assignment ===")
print(order[["rank_dv", "rank_spread", "rank_avg", "tier", "tier_by_dv",
             "tier_by_spread", "criteria_disagree",
             "median_spread_bp"]].round(2).to_string())
print(f"\ntier median spreads bp: {tier_median.round(3).to_dict()}")
print(f"multipliers unrounded : {mult_raw.round(4).to_dict()}")
print(f"multipliers rounded   : {mult.to_dict()}")
print(f"\nsensitivity, exclude-treatment tier medians bp: "
      f"{tier_median_ex.round(3).to_dict()}")
print(f"sensitivity, exclude-treatment multipliers   : {mult_ex.to_dict()}")
print(f"\nexact low-DV medians: SOXS "
      f"${full_dv.loc['SOXS', 'median_dollar_volume']:,.0f}, RYMFX "
      f"${full_dv.loc['RYMFX', 'median_dollar_volume']:,.0f}")
print(f"\ncriteria disagreements: "
      f"{order[order.criteria_disagree].index.tolist()}")
print("\nWROTE split-audit, split-crosschecks, dollar-volume, "
      "spread-estimates, spread-timeseries, tier-assignment CSVs")
