# Session 03 report — QQQ decline distribution, measurement only

Measures the distribution of trailing total returns on QQQ and the behaviour
of the rolling-percentile crash threshold. States results only; recommends
no threshold, no horizon, no estimator form. No strategy return, allocation,
weight, or performance statistic was computed; no sleeve function was
called; nothing was committed.

Script: `scripts/s03_declines.py`. Outputs: five specified CSVs plus one
intermediate (`rolling-threshold-stats.csv`) under `outputs/session-03/`.

## Conventions

- Adjusted total return per 1.2/1.4 via the session 01 loader's 1.11
  construction (`tr_index`), full available history, read-only.
- Trailing N-session return at t is TR_t / TR_{t−N} − 1, matching source's
  61-close `c[-1]/c[0]` shape at N = 60. All outputs in percent.
- "Below" and percentile ranks use strict less-than, matching source's
  `qqq_60d < -12`.
- Rolling thresholds at t are estimated on the window ending at t inclusive
  (time-consistent with a signal stamped at the t close). The expanding
  estimator runs from the first evaluable date with min_periods = 1, per
  the step wording; its early degeneracy is reported below.
- Episode = maximal run of consecutive evaluable sessions below threshold;
  gap = sessions strictly between consecutive episodes.

## Controls

Episode detection, percentile rank, and the rolling-quantile interpolation
each passed a synthetic positive control before any measurement was read.
Data checks: QQQ parquet has exactly **6,901 rows (matches the prompt),
1999-03-10 → 2026-08-14**, no nulls (consistent with the session 01 audit).
The 1.11 construction against Yahoo's Adj Close on the 60-session return:
max abs difference **0.0084 pp**, mean 0.0010 pp — consistent; tr_index used
throughout per convention.

## Step 1 — panel

| Horizon | First evaluable | Observations |
|---|---|---|
| 20 | 1999-04-08 | 6,881 |
| 40 | 1999-05-06 | 6,861 |
| 60 | 1999-06-04 | 6,841 |
| 90 | 1999-07-19 | 6,811 |
| 120 | 1999-08-30 | 6,781 |

Overlapping windows retained by design; episodes handle the overlap.

## Step 2 — distribution (percent)

| h | min | p1 | p5 | p10 | p25 | p50 | p75 | p95 | max | mean | sd |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | −31.10 | −19.78 | −10.54 | −6.95 | −2.24 | 1.64 | 4.84 | 10.54 | 41.32 | 1.04 | 6.66 |
| 40 | −44.72 | −28.06 | −14.39 | −9.02 | −2.31 | 3.08 | 7.32 | 14.98 | 46.92 | 2.09 | 9.49 |
| 60 | −45.27 | −31.92 | **−18.45** | −10.92 | −2.28 | 4.28 | 9.50 | 19.47 | 56.50 | 3.16 | 11.67 |
| 90 | −50.87 | −37.59 | −24.00 | −12.39 | −1.31 | 6.44 | 12.40 | 23.75 | 82.01 | 4.78 | 14.65 |
| 120 | −55.82 | −41.32 | −28.82 | −13.20 | −1.19 | 8.44 | 15.20 | 28.94 | 92.66 | 6.38 | 17.21 |

### The inverse question: what percentile is a given decline?

Full history, percentile rank of r < threshold:

| Decline | h=20 | h=40 | h=60 | h=90 | h=120 |
|---|---|---|---|---|---|
| −8% | 8.12 | 11.82 | 13.36 | 14.48 | 14.04 |
| −10% | 5.54 | 8.64 | 10.92 | 12.24 | 12.30 |
| **−12%** | 3.79 | 6.79 | **9.09** | 10.32 | 10.66 |
| −15% | 2.22 | 4.59 | 7.03 | 8.22 | 9.19 |
| −20% | 0.97 | 2.64 | 4.28 | 6.27 | 7.76 |

**Source's −12 over 60 sessions is the 9.1st percentile of the full
history** — roughly one session in eleven, not a tail event. The 5th
percentile at 60 sessions — the level 6.10's rolling-p5 form targets — is
**−18.45%**, materially deeper than source's −12. The re-specification and
the source constant do not describe the same event depth.

−12% at 60 sessions by block (percentile rank):

| Block | h=20 | h=40 | h=60 | h=90 | h=120 |
|---|---|---|---|---|---|
| 1999–2004 | 11.92 | 19.33 | **26.02** | 29.35 | 31.94 |
| 2005–2009 | 3.65 | 6.12 | 10.64 | 13.82 | 13.82 |
| 2010–2014 | 0.40 | 0.08 | **0.48** | 0.24 | 0.16 |
| 2015–2019 | 0.16 | 1.11 | 1.75 | 1.51 | 0.72 |
| 2020–2026 | 2.16 | 5.95 | 5.71 | 6.25 | 6.55 |

The same absolute threshold was a **once-in-four-sessions condition in
1999–2004 and a once-in-two-hundred-sessions condition in 2010–2014** — a
54-fold swing in incidence across blocks. Whether −12/60 is "a crash rule or
a correction rule" has no era-independent answer.

## Step 3 — firing rates and episodes

Full detail in `firing-episodes.csv` (one row per episode with start, end,
length, trough, trough date). Episode counts:

| Decline | h=20 | h=40 | h=60 | h=90 | h=120 |
|---|---|---|---|---|---|
| −8% | 126 | 108 | 83 | 78 | 67 |
| −10% | 83 | 84 | 79 | 69 | 50 |
| −12% | 69 | 59 | **66** | 55 | 46 |
| −15% | 41 | 56 | 52 | 42 | 27 |
| −20% | 15 | 32 | 31 | 30 | 31 |

At 60 sessions and −12: **622 firing sessions (9.1% of evaluable) forming 66
episodes** — about 2.4 per year on average, median length 2 sessions,
maximum **129 sessions (2000-11-08 → 2001-05-15)**, mean gap 87 sessions.
The average is misleading: episodes cluster. 23 of the 66 start in
2000–2003, 14 in 2022, and 17 in 2008–2009; **twelve full calendar years
show zero episodes** (2004–05, 2007, 2012–15, 2017, 2019, 2021, 2023–24).
The branch is a burst phenomenon: quiet for years, then firing repeatedly
for months.

Two structural observations, expected once seen but worth stating:

- Session counts and episode counts order horizons differently. Sessions
  below −12 rise with horizon (3.8% at 20 → 10.7% at 120) while episodes
  fall (69 → 46): longer horizons hold below threshold longer per event.
  The episode count is the meaningful figure, as the step anticipated.
- Episode counts are not monotone in threshold everywhere (h=120: 27
  episodes at −15 but 31 at −20; h=40: 56 at −15, 59 at −12). A deeper
  threshold can fragment one long shallow episode into several short deep
  ones. Counts alone do not order severities.

## Step 4 — rolling 5th percentile, three estimators, 60-session horizon

Daily series in `rolling-threshold-series.csv`; summary in
`rolling-threshold-stats.csv`.

Threshold values at the key dates (percent; return shown for reference):

| Date | ret60 | roll 1260 | roll 2520 | expanding |
|---|---|---|---|---|
| 2008-01-02 | −4.47 | −7.51 | **n/a** | −26.24 |
| 2008-09-15 | −13.66 | −11.65 | **n/a** | −25.76 |
| 2009-03-09 | −14.10 | −19.22 | **n/a** | −28.04 |
| 2015-08-24 | −10.33 | −5.39 | −12.46 | −23.84 |
| 2018-12-24 | −22.55 | −7.28 | −7.39 | −21.51 |
| 2020-02-19 | +17.48 | −8.10 | −7.14 | −20.74 |
| 2020-03-23 | −19.39 | −8.82 | −7.21 | −20.72 |
| 2022-06-16 | −23.97 | −12.56 | −9.52 | −19.79 |

Series properties and firing behaviour:

| Estimator | First value | Min | Max | SD | Effective obs (window/60) | Episodes |
|---|---|---|---|---|---|---|
| Rolling 1,260 | 2004-06-08 | −29.26 | −4.40 | 6.92 | **21** (fixed) | **40** |
| Rolling 2,520 | 2009-06-10 | −27.90 | −6.59 | 5.99 | **42** (fixed) | **22** |
| Expanding | 1999-06-04 | −33.99 | **+3.09** | 6.28 | 1 → 114 (grows) | **31** |

Episode start dates per estimator are in the script output and CSV; the
divergence between the three is the finding:

- **Rolling 1,260** spans −29.3 to −4.4. After the calm 2010–2014 block its
  p5 shallowed to −5.4, so **August 2015's −10.3% fired** — a decline that
  sits at the 10.9th percentile of full history. After 2000–2002 it sat
  near −29, so nothing in 2003–2007 fired at all. Same estimator, same
  parameter: a correction rule in 2015 and a depression rule in 2004. 21
  effective observations put the p5 estimate near the first order statistic
  of the window — the estimate rides on one or two events.
- **Rolling 2,520 does not exist until 2009-06-10**: it is unavailable at
  all three 2008–2009 key dates and cannot have fired through the entire
  financial crisis on this history. Mechanically expected — the window is
  half the sample — but it means the estimator with the most stable
  threshold has no value during the deepest event in the sample.
- **Expanding** anchors on the dot-com bust and stays between −20 and −28
  for the following two decades. Consequences on this history: it fired 22
  times in 1999–2001, then **did not fire at Lehman** (2008-09-15 return
  −13.7 vs threshold −25.8; its first 2008 episode starts 2008-10-07), **did
  not fire at all in the COVID crash** (2020-03-23 return −19.4 vs
  threshold −20.7, a 1.3 pp miss), and fired in 2022 only from June. Its
  early values are degenerate under min_periods = 1: the series' maximum is
  **+3.09%** — a "5th percentile" computed from a handful of early
  observations, positive during the first weeks.

## Step 5 — does the 60-session horizon detect anything its neighbours miss?

`horizon-overlap.csv`, overlap = calendar interval intersection at the same
−12 threshold.

Of the 66 episodes at 60 sessions, **59 overlap an episode at one or more of
the neighbouring horizons; 7 are unique to 60** (2000-06-12, 2002-03-05,
2003-02-26, 2006-08-01, 2010-06-30, 2011-10-03, 2022-03-23). Every unique
episode is 1–8 sessions long and none contains a major event: the unique
detections are edge grazes where the 60-session return dipped just under
−12 while neighbours sat just above.

Context in the other direction (counts only, from the same CSV inputs):
neighbouring horizons at −12 catch episodes that 60 misses entirely — 21 of
69 at h=20 (including 2018-10-29, 2022-09, and **2024-08-05**, the one
post-2022 stress the 60-session horizon never registered at −12), 14 of 59
at h=40, 27 of 55 at h=90, 23 of 46 at h=120. The 60-session horizon is not
privileged in either direction on this history; it is one point on a smooth
tradeoff.

## Flags — anything that did not match expectation

1. **Rolling-2,520 unavailability at the 2008 key dates.** Mechanically
   implied by the window length, but the step asked for values at those
   dates and none exist; reported as n/a rather than imputed.
2. **Expanding-estimator COVID miss.** That the expanding form skips
   Lehman-week was foreseeable from anchoring; that it misses the entire
   COVID crash by 1.3 pp was not obvious in advance and is the sharpest
   single divergence between estimator forms on this history.
3. **Non-monotone episode counts in threshold** (h=120 and h=40), the
   fragmentation artifact described in step 3.
4. **The 129-session episode** (Nov 2000 → May 2001): an "episode" under
   overlapping windows can persist for half a year, and at h=120/−12 the
   maximum run is 252 sessions — a full year below threshold.
5. The expanding estimator's positive early values (max +3.09%) under
   min_periods = 1, the literal reading of "expanding from the first
   evaluable date". Values at the requested key dates are unaffected (the
   earliest is nine years in).

## Stop condition

Halted after this report. No sleeve code called, no backtest, no
performance statistic, no commit. Working tree left dirty; the only writes
are `scripts/s03_declines.py` and the six files under `outputs/session-03/`.
