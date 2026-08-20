# Session 21 report

Provenance, representativeness, and the beta decomposition. Phases A through F all
ran, gate A and gate C both cleared, and no phase was skipped. The 2021-08-01 holdout
boundary is untouched, no grid was re-executed, no grid point was adopted, and
nothing phase A diagnoses was repaired.

**The machine has not been rebooted since session 20.** Uptime is fourteen days from
a 2026-08-06 boot, so every ceiling below derives from current state rather than from
session 19's outputs/session-19/pbo.csv, cited with attribution GB figure. No phase in this session loads the moment array, and
the heaviest load is the 70 MB metric shard set.

Every figure below is read from an emitted CSV in `outputs/session-21/`.

## The three openers

**The unwired-config verdict.** Of 57 parameters defined in `src/config.py`,
10 have no consumer outside config.py and 2 more carry a read that is
never invoked.
**Gate A clears**, since all nine grid axis attributes are read by the engine, so
the 121,500 count stands.

**The canonical provenance verdict.** Eight of the nine axes carry a value fixed
before any comparison on that axis. One does not. `crash_threshold` at
-15.0 moved from the source value
of minus 12 to minus 10 at session 04 and to its present value at session 09, after
measurements at sessions 03 and 06, and the register marks it a stipulation. The
percentile claim is supported on eight axes and weakened on one.

**The beta decomposition's residual Sharpe.** Hedging out QQQ beta leaves a residual
stream at a naive Sharpe of **0.655836** and a
Lo-corrected Sharpe of **0.864915**, against the
strategy's own 1.0911 and 1.3817.

## Phase A, the unwired-config sweep

A read is detected on the abstract syntax tree rather than by regex, since docstring
prose naming a parameter is not a read, and dynamic `getattr(config, ...)` resolution
is detected separately, since no attribute walk sees it.

| classification | count |
|---|---|
| engine | 34 |
| harness | 13 |
| validate_only | 7 |
| none | 3 |

The 10 with no consumer.

| parameter | classification |
|---|---|
| FINANCING_SPREAD_SWEEP_BP | none |
| INTERIOR_GAP_TREATMENT | validate_only |
| N_SLEEVES | validate_only |
| LABEL_ROUNDING_PERCENT | none |
| SLIPPAGE_MODEL | validate_only |
| SLIPPAGE_MODELS | validate_only |
| GRID_TOTAL_SPECIFICATIONS | validate_only |
| GRID_SEARCHED_SPECIFICATIONS | validate_only |
| GRID_UNSEARCHED_AXES | none |
| N_RSI_FUNCTION_TIED_PERIODS | validate_only |

**Two parameters carry a read that is never invoked.** `SIZING_MODE` and
`EXECUTION_MODE` are read by `src/execution.py` as default arguments of
`size_position`, and no module in the return-generating path calls `size_position`.
The engine hardcodes `math.trunc` at `scripts/s13_backtest.py:528`, so both have a
read site and no influence on any result.

**`FINANCING_SPREAD_BP` is read by the harness and not by the engine.** Its readers
are the synthetics builder and validator plus session scripts, so the financing
spread enters results only through the pre-built reconstructions on the synthetic
arm. On the realized arm, which is the designated cell, no financing model applies at
all, since the levered funds carry the issuer's own financing inside their price
history. D16 records the spread as assumed and treated by the cost sweep, and this
establishes that the engine never reads it.

**The completion rule is not a config parameter.** It is hardcoded in the fill path
and `scripts/s13_backtest.py` lines 18 to 24 mark it provisional and not a register
closure, so it is unregistered rather than unread.

**One unread parameter sits on the specification curve.** `SLIPPAGE_MODEL` and
`SLIPPAGE_MODELS` have no consumer, while `slippage_model` is a curve axis in
`outputs/session-19/specification-curve.csv`. The axis was varied through function
selection in the cost sweep rather than through the config value, so the curve is
real and the config parameter is inert. No grid axis is affected, which is why gate A
clears.

## Phase B, canonical axis provenance

| axis | canonical | register | state |
|---|---|---|---|
| sma_long | 200 | 6.5 / 6.6 | before |
| crash_threshold | -15.0 | 6.10, with 7.7 fixing the swept levels | after |
| rsi_exhaustion | 14 | 6.1 | before |
| rsi_dip | 14 | 6.1 | before |
| rsi_rs | 14 | 6.1 | before |
| overbought_t1 | 70 | 6.2 / 6.3 / 6.4 | before |
| oversold | 30 | 6.4 | before |
| sma_short | 20 | 6.5 / 6.6 | before |
| vote | 3 | 6.7 | before |

Eight of the nine axes carry a canonical value fixed before any comparison on that axis, so the rank of 6,834 of 121,500 on the Lo-corrected Sharpe and 8,237 on annualised return is supported on those eight. It is weakened on crash_threshold alone, where the value moved twice after measurement and settled at a stipulation. The weakening is reported per axis rather than as a single verdict, and no canonical value is changed.

**A documentation caveat travels with it.** Seven of the nine closures carry no session attribution in the register, so their ordering relative to any measurement rests on the entries' source-derived phrasing rather than on a dated record. That is a documentation gap rather than evidence of tuning.

## Phase C, subsample representativeness

| quantity | subsample | full grid |
|---|---|---|
| naive Sharpe mean | 0.634114 | 0.619901 |
| naive Sharpe sd | 0.454626 | 0.451978 |
| naive Sharpe p05 | -0.271983 | -0.265967 |
| naive Sharpe p50 | 0.773218 | 0.744166 |
| naive Sharpe p95 | 1.158431 | 1.159682 |

The primary test is a resampling null of 2000 random
subsets at seed 20260821 fixed before drawing, which makes
no distributional assumption and respects the finite population exactly. The observed
subsample mean of 0.634114 sits at the
90.80 percentile of that null, a
two-sided p of 0.1840.

The Kolmogorov-Smirnov distance is 0.028798 and is reported as a
distance rather than a test, since both of its assumptions fail here.

Axis balance holds at 34 of
34 axis values inside a 99
percent binomial interval, and the canonical is present.

**Gate C clears.** a representative subsample licenses session 20's effective-N figures and this session's phase E recentred comparison. A non-representative one would invalidate both

## Phase D, the beta decomposition

The positive control passes, with the benchmark regressed on itself returning beta
1.000000 and an alpha whose absolute value is below
the tolerance, inside a
1e-09 tolerance stated before comparing.

### Static

| quantity | value |
|---|---|
| beta | 1.108673 |
| alpha annualised | 0.288744 |
| R-squared | 0.186794 |
| Newey-West alpha t | 2.364283 |
| hedged residual annualised return | 0.213587 |
| hedged residual annualised volatility | 0.440269 |
| hedged residual naive Sharpe | 0.655836 |
| hedged residual Lo-corrected Sharpe | 0.864915 |

the beta-hedged excess return ys minus beta times yq, retaining the intercept. The fitted OLS residual has mean zero by construction and its Sharpe is identically zero, which is a property of the estimator rather than a result.

The Newey-West lag is 21, which 8.11 fixes before
the run for every alpha t-statistic in this project rather than being chosen here.

### Rolling

The window is 60 sessions, read from
`config.CRASH_HORIZON_SESSIONS`, the only rolling lookback the register records for a
return-based estimator.

| quantity | value |
|---|---|
| rolling beta mean | 0.864383 |
| rolling beta standard deviation | 1.164612 |
| rolling beta minimum | -4.497370 |
| rolling beta maximum | 2.788517 |
| rolling beta share of sessions above 1.0 | 0.566750 |
| rolling beta share of sessions above 1.7 | 0.215589 |

### Timing against selection

Excess return decomposes as a static exposure component, a timing component, and a
residual, with the rolling beta lagged one session so no session uses its own data.

| component | annualised contribution | naive Sharpe | Lo Sharpe |
|---|---|---|---|
| static exposure | +0.241396 | 1.144457 | 1.790655 |
| timing | +0.011293 | 0.058958 | 0.078719 |
| residual | +0.319875 | 0.684366 | 1.208893 |
| total | +0.572563 | | |

**Timing contributes the smallest of the three components.** The residual is the
largest and the static exposure component is between them.

### The exposure-matched null

QQQ held at the canonical's own rolling realised beta lagged one session, rebalanced daily, charged the identical cost model.

| quantity | value |
|---|---|
| annualised return | 0.273354 |
| annualised volatility | 0.238551 |
| naive Sharpe | 1.108581 |
| Lo-corrected Sharpe | 1.300043 |
| annualised turnover | 5.234604 |
| ladder position on naive Sharpe | 6 of thirteen |
| ladder position on Lo-corrected Sharpe | 8 of thirteen |

The exposure-matched line reaches a naive Sharpe of
1.108581 against the strategy's 1.0911 and a
Lo-corrected Sharpe of 1.300043 against 1.3817.
Reported as measured, with no characterisation.

## Phase E, the recentred comparison

The deflated Sharpe assumes every trial has true Sharpe zero while the grid's cross-sectional naive mean is 0.6199013071365644, so the null is misspecified at every N. The incoherence is visible at the participation-ratio count, where session 20 reported an expected maximum of 0.4285 that falls below the mean of the draws it maximises over. Removed on the misspecified null rather than on an unfavourable result. Effective N is retained as its own finding, since it is the reason for the removal

| point | naive Sharpe | z from grid mean | percentile | rank |
|---|---|---|---|---|
| canonical | 1.091086 | 1.042496 | 89.28 | 13030 |
| in_sample_best | 1.472349 | 1.886039 | 100.00 | 1 |

Two correlation-accounting methods are reported so the choice is visible.

**Method one.** the grid's own empirical distribution already embeds the correlation among specifications, so the percentile needs no adjustment. This method makes no independence assumption at all.

**Method two.** compare the canonical's z against the expected maximum z of that many independent standard normal draws, using session 20's effective counts from the subsample eigenvalue spectrum.

| effective count | value | expected maximum z | canonical exceeds |
|---|---|---|---|
| participation_ratio | 3.43 | 0.9481 | yes |
| spectral_entropy | 6.72 | 1.3642 | no |
| variance_threshold_95 | 17.00 | 1.8281 | no |
| nominal_121500 | 121500.00 | 4.4330 | no |

The canonical exceeds the expected maximum only at the participation-ratio count and
not at the other three. The two methods disagree, which is the point of reporting
both rather than one.

## Phase F, reads and confirmations

**F1, cost crossings.** The sweep spans 0 to 50 bp across
6 points. Crossings against each of the eleven
benchmark lines under both conventions are in `reads.csv`, each marked as inside the
swept range or as an extrapolation.

**F2, leave-one-out provenance.** outputs/session-16/leave-one-out.csv outputs/session-16b/loo-session-counts.csv outputs/session-16b/loo-sleeve-ranges.csv. These were **not**
rebuilt by session 20 phase C, which covered `s14_ladder`, `s14_nulls`, `s15_metrics`
and `s15_rest` only, so they carry the superseded boundary. the 2011 leave-one-out estimate and the 2012-start strip arm both read 1.5636. They are computed differently, since a leave-one-out drops one calendar year from the return series while a strip arm starts the window later and keeps every subsequent year, so the agreement at four decimals is coincidental rather than structural

**F3, the 8.7 reconciliation.** 273,375 is the superseded v1/v2 enumerated space, 364,500 is the current enumerated space across ten axes, and 121,500 is both the evaluated count and, since session 20, N.

**F4, the null replication count.** clearing p below 0.001 at 1,000 draws requires zero exceedances, so the gate turns on a single draw. The session 20 gate specification carries that defect and the gate outcome is unresolved rather than settled. No null is re-run in this session.

**F5, distinct episodes.** The 69
overlapping fourteen-session windows collapse to
**16 distinct non-overlapping
episodes**, and January 2013 ranks
11 among them, against the 42nd of
69 that session 20 reported on the overlapping count.

## Findings and the class of change each would need

| finding | class |
|---|---|
| ten config parameters have no consumer | documentation, or a correctness repair to remove them |
| SIZING_MODE and EXECUTION_MODE are read but never invoked | correctness repair to wire, specification change to vary |
| FINANCING_SPREAD_BP is never read by the engine | documentation, and it bears on how D16 is described |
| SLIPPAGE_MODEL is inert while slippage_model is a curve axis | documentation |
| crash_threshold was fixed after measurement on its own axis | register decision on how the percentile claim is stated |
| the subsample is representative | documentation, and it licenses phase E |
| the beta-hedged residual Sharpe is below the headline | documentation |
| the exposure-matched line reaches a higher naive Sharpe than the strategy | register decision on what the ladder claims |
| the deflated Sharpe rests on a misspecified null | correctness repair, applied by removal |
| the two correlation-accounting methods disagree | register decision on which is reported |
| the session 20 gate turns on a single draw at 1,000 replications | specification change to raise the replication count |

No recommendation is made on any of these.

## What remains open before the holdout can run

- **The session 20 gate C outcome is unresolved**, since clearing p below 0.001 at
  1,000 draws requires zero exceedances and turns on a single draw.
- **The session 20 B1 re-emission and phase G are still outstanding**, both halted on
  memory, and the machine has not been rebooted since.
- **The Lo q remains unregistered**, and the 8.2 question of whether the Lo-corrected
  Sharpe stays headline is open.
- **The leave-one-out artifacts carry the superseded boundary.**
- **SVIX and UVIX leave a code path that will not execute at the holdout read.**
- **D16 stands**, and phase A establishes the engine never reads the spread.

## Resources

| phase | peak resident | wall clock |
|---|---|---|
| A | 0.191 GB | 10.5 s |
| B | 0.0 GB | under a second |
| C | 0.263 GB | 0.5 s |
| D | 0.201 GB | 7.8 s |
| E and F | documentary, no array load | 6.6 s |

## Stop

Halted after phase G. No holdout executed, no grid re-executed, no grid point
adopted, no canonical value changed, no null re-run, and nothing phase A diagnoses
was repaired.

