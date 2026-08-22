# WITHDRAWN

Every claim this project made and then withdrew, with the grounds and the session
that overturned it. A negative-result paper is judged partly on whether its authors
can show what they stopped believing.

**10 withdrawals**, of which 7 followed from a measurement and 3 from an argument about construction. The map is `outputs/session-24/withdrawn-sources.csv`.

## 1. The deflated Sharpe, reported at 0.000660 for the canonical at N equal to 364,500 and later at 0.001979 at N equal to 121,500.

The statistic assumes every trial has true Sharpe zero while the grid's cross-sectional naive mean is 0.6199013071365644, so the null is misspecified at every N. The incoherence is visible at the participation-ratio count where the expected maximum falls below the mean of the draws it maximises over.

- Withdrawn by argument, from the construction rather than from a result
- Session 21, at 8.7
- Source `outputs/session-20/deflated-sharpe-corrected.csv and outputs/session-21/recentred-comparison.csv`
- Emitted deflated_sharpe_N_121500 0.001978908395299017; deflated_sharpe_N_364500 0.0006598462023542639; grid_sharpe_naive_mean 0.6199013071365644; participation_ratio_expected_max_z 0.9481287926640676

## 2. The performance degradation slope, reported at -1.0663023854544191 and corrected to -1.0666200132036998.

No valid null exists for it. Session 19.6's null permuted block ordering independently per specification, which destroyed the common time structure every specification shares, so its z-scores tested that structure rather than overfitting. The corrected construction was never run.

- Withdrawn by argument, with the corrected null still unrun
- Session 21, at 9.35
- Source `outputs/session-19_6/m1-nis-correction.csv`
- Emitted corrected slope -1.0666200132036998

## 3. The session 19.5 window strip, reporting the strategy's rank as unstable across six start dates.

The strip compared a nested strategy against re-initialised benchmarks, since the strategy was built once and sliced while each benchmark line was rebuilt per arm. Seven of the eleven benchmark lines carry state, so the comparison is not like for like.

- Withdrawn by argument, from the construction
- Session 21, at 9.36
- Source `outputs/session-20/jan2013-attribution.csv`
- Emitted seven of eleven lines carry state

## 4. The exposure-matched line reaching a higher naive Sharpe than the strategy at 1.108581.

Measured at a single 60-session window. Across 120, 252 and 504 sessions the matched line reads lower at each step and falls below the strategy, so the finding holds only at the shortest and noisiest window.

- Withdrawn by measurement
- Session 22, at 9.42
- Source `outputs/session-22/beta-window-sensitivity.csv`
- Emitted 120 1.0337970102854044; 252 0.965584223695077; 504 0.9177696057575306

## 5. January 2013 as an exceptional event.

The 69 overlapping fourteen-session windows below minus 0.15 collapse to 16 distinct non-overlapping episodes, and January 2013 ranks 11 among them rather than being singular.

- Withdrawn by measurement
- Session 21 phase F5 and 20 phase F
- Source `outputs/session-21/reads.csv`
- Emitted distinct episodes 16, rank 11

## 6. The handoff's section 4 inference about 2022 holdout behaviour.

The inference rested on the SVIX and UVIX branches activating from their 2022-03-30 listing. Those tickers load on neither panel and the availability switch resolves them away, so the branch will not execute at the holdout read under the current loader and no 2022 inference follows from it.

- Withdrawn by measurement, by tracing the code path
- Session 20 at 9.20 and 22 at 9.43
- Source `outputs/session-22/volatility-terminal-resolution.csv`
- Emitted SVIX and UVIX in bt.LEVERED: 0

## 7. The resource diagnosis in its first form, being that passes were blocked on memory.

Every terminated pass was killed by hand after slowing, with no completion attempt allowed and no operating-system kill. Peak resident reached 1.133 GB against 3.561 GB that had completed, with page-outs low and the compressor flat.

- Withdrawn by measurement, under a pre-registered rule
- Session 22, correcting 9.35 and 8.12
- Source `outputs/session-23/resource-record.csv`
- Emitted peak_rss_gb 1.133 against 3.561 that completed; max_pageouts_per_second 80.9; compressor_gib 2.7 flat; process_cpu_mean_percent 6.25 across 113 samples

## 8. The resource diagnosis in its second form, being that the passes would have completed had they not been killed.

A pre-registered 1800 second attempt did not complete, so the passes genuinely do not finish under contention. The claim ran ahead of the evidence in the opposite direction to the first.

- Withdrawn by measurement
- Session 22, and again at 23
- Source `outputs/session-23/resource-record.csv`
- Emitted load_average 39.57 on eight cores; the pre-registered 1800 second attempt did not complete; session_23 passes_completed 0

## 9. The concern that the leave-one-out artifacts carried the superseded 2011-10-03 boundary.

The rebuild produced a base estimate identical to the original at 1.3817013060, which is the corrected value, because session 16 made the correction and the leave-one-out script ran after it. The rebuild confirmed rather than repaired.

- Withdrawn by measurement
- Session 22, at 9.41
- Source `outputs/session-22/loo-rebuilt.csv`
- Emitted abs_gap 0.0

## 10. The claim that the 1.5636 agreement between the 2011 leave-one-out estimate and the 2012-start strip arm was coincidental.

The two operations are not independent. The primary window begins 2011-10-04, so dropping calendar 2011 removes very nearly the sessions that starting at the first 2012 session removes, and the estimates agree to 8.326e-07 rather than to four decimals.

- Withdrawn by measurement
- Session 22, at 9.41
- Source `outputs/session-22/loo-rebuilt.csv`
- Emitted abs_gap 8.326e-07

## A note on the pattern

Three of the ten withdrawals concern the measurement apparatus rather than the
strategy, and two of those, being the resource diagnosis in its first and second
forms, were successive wrong answers to the same question in opposite directions. The
register records the class at 9.47 as an inference stated as a measurement, which has
produced three register corrections across the project.

