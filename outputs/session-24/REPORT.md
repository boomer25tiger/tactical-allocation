# Session 24, the claim freeze

2026-08-22. Seven phases. One commit, at phase G.

## What this session did

The claim set is frozen. `docs/CLAIMS.md` carries 15 claims with the limitations written into the same file, `docs/WITHDRAWN.md` carries 10 withdrawals, and `outputs/session-24/figure-spec.csv` specifies 10 figures without drawing any of them. The gated housekeeping pass ran and returned a substantive result the session did not expect.

## Phase A and C, the frozen claim set

15 claims, being 11 primary and 4 supporting. 6 concern the strategy and 5 the grid, while 4 concern the measurement apparatus. Each carries a statement, a source file, the literal emitted value, a register item and the condition that would overturn it.

Every figure was read from an emitted CSV with the path carried beside it. Two figures were corrected during the write. Claim 14 had said the three ladder rows outside their own no-autocorrelation null were the rows that outrank the strategy, and the file shows five rows outrank it while the three outside are its top three on the Lo-corrected Sharpe. Four values had been carried with a numpy repr wrapper around them rather than as the file emits them.

The limitations sit under the claim each qualifies. They cover the ten config parameters with no consumer and the two read but never invoked, `crash_threshold` fixed after a measurement on its own axis, the seven of nine axis closures with no session attribution, the SVIX and UVIX path that will not execute at the holdout read, D16, D23, the unregistered Lo lag parameter, the ladder drop from fourteen lines to twelve, and the outstanding measurement.

## Phase B, the withdrawn set

10 withdrawals, of which 7 followed from a measurement and 3 from an argument about construction. Three concern the measurement apparatus rather than the strategy, and two of those, being the resource diagnosis in its first and second forms, were successive wrong answers to the same question in opposite directions.

## Phase D, the figure specification

10 rows against the scaffold's eight. **No figure is drawn.** 2 are not drawable from committed artifacts, being the null distribution histograms, which need per-draw arrays the nulls file does not carry, and effective exposure by decile, which has the mean and two named deciles rather than a ten-decile series. Plotting will use the standard-library SVG path at `scripts/s19_svg.py`, since matplotlib is absent and the offline constraint rules out installing it.

## Phase E, the volatility terminal

The file existed from session 22 and was read rather than recomputed. The T10 terminal fires 1114 sessions holding SVXY and the S3 terminal 519 holding UVXY across the primary window, both tickers list 2022-03-30 inside the holdout span, and both load on neither panel. The finding is carried into the limitations. `bt.LEVERED` is not modified.

## Phase F, the gated housekeeping

`scripts/s23_phaseA.py` contains only a halt branch, so run unchanged on a quiet machine it would have written a passed positive control and no pass. `scripts/s24_phaseF.py` reuses its pre-registered rule verbatim and adds the launch branch. No orphaned worker was present, so the kill step had nothing to terminate.

The pass launched at a one-minute load of 15.2 against the halt threshold of 16 and ran to the wall limit at 994.2 seconds, peak resident 1.584 GB, return code -15. It reached 4 of five block counts.

| S | re-emitted PBO | reported PBO | reproduces | corrected slope | shift from the defective value |
|---|---|---|---|---|---|
| 8 | 0.1142857143 | 0.11428571428571428 | yes | -1.1504038735 | 1.080e-02 |
| 12 | 0.1709956710 | 0.170995670995671 | yes | -1.2618531502 | 2.910e-03 |
| 16 | 0.1578088578 | 0.1578088578088578 | yes | -1.0666200132 | 2.448e-04 |
| 24 | 0.1646000000 | 0.1646 | yes | -1.1476066760 | 3.034e-04 |

**The chunk-first-element defect did not touch PBO.** All four re-emitted values reproduce the reported figures exactly on repaired code at a chunk size of 257 rather than the 514 most were first run at, so claim 4 stands on repaired code at both of its stated range endpoints, which are S equal to 8 and S equal to 12. The degradation slope does move, and its removal at 9.35 makes that moot.

**The wall limit was mis-derived and the halt reflects the limit rather than the machine.** 969 seconds was taken as ten times a 96.9 second single-chunk pass, while the sweep it had to cover measured 2424.37 seconds across its five stages when first run. Load ran between 5.09 and 13.05 across 33 samples and each completed stage beat its original, S=16 at 417.4 seconds against 775.01 and S=24 at 506.1 against 598.24. Recording this as a contention halt would repeat the class at 9.47 of naming a mechanism the evidence does not reach.

**The contention diagnosis gains its first supporting completion observation.** Four stages completed at a load-to-core ratio of 1.90 at launch, against 4.9463 when session 22's pass failed to complete and 8.9288 when session 23 halted before launch. It is support rather than proof, since the three runs differ in wall limit as well as in load.

## What remains outstanding

S equal to 48 of the B1 re-emission, which sets neither endpoint of claim 4's stated range, and the corrected degradation null, whose slope is withdrawn at 9.35 regardless. Neither is load-bearing and no claim depends on either.

## Register

9.48 the partial re-emission and the amendment to 8.12. 9.49 the mis-derived wall limit. 9.50 the completion observation extending 9.47. 9.51 the frozen claim set. 9.52 the withdrawn set. 9.53 the figure specification and the plotting decision. 9.54 the volatility terminal read. The measurement-phase closure note is amended to one outstanding item from two.

## Artifacts

- `outputs/session-24/claim-sources.csv`
- `outputs/session-24/withdrawn-sources.csv`
- `outputs/session-24/figure-spec.csv`
- `outputs/session-24/phaseF-relaunch.csv`
- `outputs/session-24/f.log`
- `outputs/session-24/b1.log`
- `docs/CLAIMS.md`
- `docs/WITHDRAWN.md`

