"""Session 03. QQQ trailing-return distribution, measurement only.

Measures the distribution of trailing total returns on one price series and
the behaviour of the rolling-percentile crash threshold (6.10, under review;
6.11 and 6.12 open behind it). Source hardcoded qqq_60d < -12 at the top of
_t11_feaver_bear; this session establishes what that threshold and horizon
actually are empirically. No strategy return, allocation, weight, or
performance statistic is computed. No sleeve function is called. No
parameter is selected and no decision is recommended.

Conventions, stated once:
  * Returns are adjusted total return per 1.2/1.4, built by the session 01
    loader's 1.11 construction (tr_index), full available history.
  * Trailing N-session return at session t is TR_t / TR_{t-N} - 1, matching
    source's 61-close c[-1]/c[0] shape at N = 60.
  * All return values in outputs are in PERCENT.
  * "Below threshold" and percentile ranks both use strict less-than,
    matching source's qqq_60d < -12.
  * Rolling thresholds at session t are estimated on the window ENDING AT t
    inclusive - time-consistent with a signal stamped at the t close.
  * An episode is a maximal run of consecutive evaluable sessions below
    threshold. Gap between episodes is the count of sessions strictly
    between one episode's end and the next one's start.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.data import build_ticker_frame

OUT = ROOT / "outputs" / "session-03"
OUT.mkdir(parents=True, exist_ok=True)

HORIZONS = [20, 40, 60, 90, 120]
THRESHOLDS = [-8.0, -10.0, -12.0, -15.0, -20.0]  # percent
BLOCKS = [("1999-2004", 1999, 2004), ("2005-2009", 2005, 2009),
          ("2010-2014", 2010, 2014), ("2015-2019", 2015, 2019),
          ("2020-2026", 2020, 2026)]
KEY_DATES = [pd.Timestamp(d) for d in (
    "2008-01-02", "2008-09-15", "2009-03-09", "2015-08-24",
    "2018-12-24", "2020-02-19", "2020-03-23", "2022-06-16")]
ROLL_WINDOWS = {"roll_1260": 1260, "roll_2520": 2520}


def episodes_from_mask(mask: np.ndarray) -> list[tuple[int, int]]:
    """Inclusive (start, end) index pairs of maximal True runs."""
    out = []
    i, n = 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def pct_rank(values: np.ndarray, thr: float) -> float:
    """Percentile rank of thr: 100 * P(r < thr), strict."""
    return 100.0 * float(np.mean(values < thr))


# ---------------------------------------------------------------------------
# Positive controls, before anything is trusted
# ---------------------------------------------------------------------------

_eps = episodes_from_mask(np.array([False, True, True, False, True, False]))
assert _eps == [(1, 2), (4, 4)], _eps
_r = pct_rank(np.arange(1.0, 101.0), 50.5)
assert _r == 50.0, _r
assert pct_rank(np.arange(1.0, 101.0), 0.0) == 0.0
_q = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0]).rolling(3).quantile(0.05)
assert abs(_q.iloc[2] - 1.1) < 1e-12, _q.iloc[2]  # linear interpolation
print("CONTROLS PASSED: episode detection, percentile rank, rolling quantile")

# ---------------------------------------------------------------------------
# Load QQQ, build total return, cross-check against Adj Close
# ---------------------------------------------------------------------------

raw = pd.read_parquet(ROOT / "data" / "raw" / "etf" / "QQQ.parquet")
tf = build_ticker_frame("QQQ", raw)
tr = tf.tr_index
adj = tf.adj_close

print(f"\nQQQ rows: {len(tr):,}   {tr.index.min().date()} -> {tr.index.max().date()}")
print(f"prompt stated 6,901 rows: {'MATCH' if len(tr) == 6901 else 'MISMATCH - FLAG'}")
assert tr.notna().all(), "unexpected null in QQQ tr_index (audit said none)"
assert tr.index.is_monotonic_increasing and not tr.index.has_duplicates

# control: 1.11 construction against Yahoo's Adj Close on the 60-session return
r60_tr = (tr / tr.shift(60) - 1.0) * 100.0
r60_adj = (adj / adj.shift(60) - 1.0) * 100.0
diff = (r60_tr - r60_adj).abs().dropna()
print(f"tr_index vs Adj Close 60-session return: max abs diff "
      f"{diff.max():.6f} pp, mean {diff.mean():.6f} pp "
      f"({'consistent' if diff.max() < 0.05 else 'DIVERGENT - FLAG'})")

rets = {h: ((tr / tr.shift(h) - 1.0) * 100.0).dropna() for h in HORIZONS}

# ---------------------------------------------------------------------------
# Step 1 + 2: panel and distribution
# ---------------------------------------------------------------------------

dist_rows = []
print("\n=== STEP 1: panel ===")
for h in HORIZONS:
    r = rets[h]
    print(f"  h={h:3d}: first evaluable {r.index[0].date()}, n={len(r):,}")
    dist_rows.append(dict(
        horizon=h, n_obs=len(r), first_evaluable=str(r.index[0].date()),
        min=r.min(), p1=r.quantile(0.01), p5=r.quantile(0.05),
        p10=r.quantile(0.10), p25=r.quantile(0.25), p50=r.quantile(0.50),
        p75=r.quantile(0.75), p95=r.quantile(0.95), max=r.max(),
        mean=r.mean(), sd=r.std(ddof=1),
    ))
dist = pd.DataFrame(dist_rows)
dist.to_csv(OUT / "trailing-return-distribution.csv", index=False)
print("\n=== STEP 2: distribution (percent) ===")
print(dist.round(2).to_string(index=False))

tp_rows = []
for h in HORIZONS:
    r = rets[h]
    windows = [("full", r)] + [
        (name, r[(r.index.year >= y0) & (r.index.year <= y1)])
        for name, y0, y1 in BLOCKS
    ]
    for wname, rw in windows:
        for thr in THRESHOLDS:
            tp_rows.append(dict(
                horizon=h, threshold_pct=thr, window=wname, n_obs=len(rw),
                n_below=int((rw < thr).sum()),
                pct_rank=pct_rank(rw.to_numpy(), thr) if len(rw) else np.nan,
            ))
tp = pd.DataFrame(tp_rows)
tp.to_csv(OUT / "threshold-percentiles.csv", index=False)

print("\n=== STEP 2 inverse: percentile rank of each decline, full history ===")
piv = tp[tp.window == "full"].pivot(index="threshold_pct", columns="horizon",
                                    values="pct_rank")
print(piv.round(2).to_string())
print("\n=== -12 percent by block (pct rank) ===")
p12 = tp[(tp.threshold_pct == -12.0) & (tp.window != "full")].pivot(
    index="window", columns="horizon", values="pct_rank")
print(p12.round(2).to_string())

# ---------------------------------------------------------------------------
# Step 3: firing rates and episodes
# ---------------------------------------------------------------------------

ep_rows = []
agg_rows = []
episodes_by = {}
for h in HORIZONS:
    r = rets[h]
    for thr in THRESHOLDS:
        mask = (r < thr).to_numpy()
        eps = episodes_from_mask(mask)
        episodes_by[(h, thr)] = [
            (r.index[s], r.index[e]) for s, e in eps
        ]
        lengths = [e - s + 1 for s, e in eps]
        gaps = [eps[i + 1][0] - eps[i][1] - 1 for i in range(len(eps) - 1)]
        for k, (s, e) in enumerate(eps):
            seg = r.iloc[s:e + 1]
            ep_rows.append(dict(
                horizon=h, threshold_pct=thr, episode=k + 1,
                start=str(r.index[s].date()), end=str(r.index[e].date()),
                length_sessions=e - s + 1,
                trough_pct=seg.min(), trough_date=str(seg.idxmin().date()),
            ))
        agg_rows.append(dict(
            horizon=h, threshold_pct=thr,
            sessions_below=int(mask.sum()),
            frac_of_evaluable=float(mask.mean()),
            episodes=len(eps),
            median_len=float(np.median(lengths)) if lengths else np.nan,
            max_len=max(lengths) if lengths else 0,
            mean_gap=float(np.mean(gaps)) if gaps else np.nan,
        ))
pd.DataFrame(ep_rows).to_csv(OUT / "firing-episodes.csv", index=False)
agg = pd.DataFrame(agg_rows)

print("\n=== STEP 3: episode counts (rows thresholds, cols horizons) ===")
print(agg.pivot(index="threshold_pct", columns="horizon",
                values="episodes").to_string())
print("\n=== sessions below as % of evaluable ===")
print((agg.pivot(index="threshold_pct", columns="horizon",
                 values="frac_of_evaluable") * 100).round(2).to_string())
print("\n=== per-combo detail ===")
print(agg.round(2).to_string(index=False))
print("\n=== episode start dates, 60-session horizon ===")
for thr in THRESHOLDS:
    starts = [str(s.date()) for s, _ in episodes_by[(60, thr)]]
    print(f"  60 @ {thr:+.0f}%: {len(starts)} episodes: {starts}")

# ---------------------------------------------------------------------------
# Step 4: rolling 5th percentile, three estimators, 60-session horizon
# ---------------------------------------------------------------------------

r60 = rets[60]
thr_series = {}
for name, w in ROLL_WINDOWS.items():
    thr_series[name] = r60.rolling(w, min_periods=w).quantile(0.05)
thr_series["expanding"] = r60.expanding(min_periods=1).quantile(0.05)

roll = pd.DataFrame({"ret60_pct": r60, **thr_series})
roll.index.name = "date"
roll.to_csv(OUT / "rolling-threshold-series.csv")

print("\n=== STEP 4: threshold value at key dates (percent) ===")
missing_dates = [d for d in KEY_DATES if d not in r60.index]
assert not missing_dates, f"key dates absent from index: {missing_dates}"
key = roll.loc[KEY_DATES].round(3)
print(key.to_string())

print("\n=== threshold series stats over non-null span ===")
stat_rows = []
for name, s in thr_series.items():
    sv = s.dropna()
    eff = (ROLL_WINDOWS[name] / 60 if name in ROLL_WINDOWS
           else len(r60) / 60)
    stat_rows.append(dict(
        estimator=name,
        first_value=str(sv.index[0].date()) if len(sv) else None,
        n=len(sv), min=sv.min(), max=sv.max(), sd=sv.std(ddof=1),
        effective_obs=(f"{eff:.0f} (fixed)" if name in ROLL_WINDOWS
                       else f"1 -> {eff:.0f} (grows with span)"),
    ))
    fires = ((r60 < s) & s.notna()).to_numpy()
    eps = episodes_from_mask(fires)
    starts = [str(r60.index[a].date()) for a, _ in eps]
    stat_rows[-1]["episodes"] = len(eps)
    stat_rows[-1]["episode_starts"] = "; ".join(starts)
stats = pd.DataFrame(stat_rows)
print(stats.drop(columns="episode_starts").round(3).to_string(index=False))
print("\n=== firing episodes per estimator ===")
for row in stat_rows:
    print(f"  {row['estimator']}: {row['episodes']} episodes")
    print(f"    starts: {row['episode_starts']}")
stats.to_csv(OUT / "rolling-threshold-stats.csv", index=False)

# ---------------------------------------------------------------------------
# Step 5: horizon overlap at -12
# ---------------------------------------------------------------------------

base = episodes_by[(60, -12.0)]
others = {h: episodes_by[(h, -12.0)] for h in (20, 40, 90, 120)}


def overlaps(a0, a1, b0, b1) -> bool:
    return a0 <= b1 and b0 <= a1


ov_rows = []
for k, (s, e) in enumerate(base):
    row = dict(episode=k + 1, start=str(s.date()), end=str(e.date()))
    matched_any = False
    for h, eps in others.items():
        hits = [str(bs.date()) for bs, be in eps if overlaps(s, e, bs, be)]
        row[f"fires_{h}"] = bool(hits)
        row[f"match_starts_{h}"] = "; ".join(hits)
        matched_any |= bool(hits)
    row["unique_to_60"] = not matched_any
    ov_rows.append(row)
ov = pd.DataFrame(ov_rows)
ov.to_csv(OUT / "horizon-overlap.csv", index=False)

print("\n=== STEP 5: 60-session -12%% episodes vs neighbouring horizons ===")
show = ["episode", "start", "end"] + [f"fires_{h}" for h in (20, 40, 90, 120)] + ["unique_to_60"]
print(ov[show].to_string(index=False))

print("\n=== context: -12%% episodes at other horizons NOT overlapping any 60-session episode ===")
for h, eps in others.items():
    unmatched = [str(bs.date()) for bs, be in eps
                 if not any(overlaps(s, e, bs, be) for s, e in base)]
    print(f"  h={h:3d}: {len(unmatched)} of {len(eps)}: {unmatched}")

print("\nDONE - five CSVs written to outputs/session-03/")
