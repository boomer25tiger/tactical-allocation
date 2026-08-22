# CLAIMS

The frozen set of claims this project makes, together with the limitations that
qualify them. Frozen means no claim is added after 2026-08-20 without a dated
register entry recording the addition and its grounds.

Every figure below is the literal value in the emitted CSV named beside it. The
claim-to-artifact map is `outputs/session-24/claim-sources.csv`, so each claim is
traceable to a committed file. Claims withdrawn during the project are in
`docs/WITHDRAWN.md` rather than removed silently.

Both Sharpe conventions are reported throughout with the naive figure leading, per
the 8.2 decision, on the grounds recorded in claim 14 as narrowed at 9.61.

**Amendments since the freeze.** Claim 4's scope phrase was narrowed on 2026-08-22 to
name only the block counts re-emitted on repaired code, recorded at 9.59 as a wording
repair. No quoted figure moved and no claim was added or removed.

**15 claims**, being 11 primary and 4 supporting. 6 concern the strategy and 5 the grid, while 4 concern the measurement apparatus. **The contribution sits mostly in that last group.**

## Claim 1, primary, about the strategy

In the designated cell the strategy places sixth of twelve on both Sharpe conventions, trailing buy-and-hold QQQ on the naive Sharpe by 0.0650226373237004 and on the Lo-corrected Sharpe by 0.42161920118337926.

- Source `outputs/session-20/rebuilt/metrics-full.csv`
- Emitted STRATEGY naive 1.0910863648060856 lo 1.3817013060244996; buy_hold_QQQ naive 1.156109002129786 lo 1.8033205072078788; ranks 6 and 6 of 12
- Register 8.8, rebuilt at 9.23
- Overturned by a ladder line rebuilt on a different cost model or a corrected benchmark construction that moves the strategy's rank

## Claim 2, primary, about the strategy

Against two randomization nulls at 10,000 draws on the designated cell, the strategy is exceeded on 7 of 10,000 draws by the timing shuffle on annualised return and on 0 of 10,000 in the other three combinations.

- Source `outputs/session-22/rebuilt/nulls.csv`
- Emitted timing_shuffle_block_bootstrap|annualised return 7 of 10000; timing_shuffle_block_bootstrap|Lo-corrected Sharpe 0 of 10000; turnover_matched_switching|annualised return 0 of 10000; turnover_matched_switching|Lo-corrected Sharpe 0 of 10000
- Register 8.9, re-run at 9.40
- Overturned by a null construction that preserves a feature of the strategy the current two do not

## Claim 3, primary, about the strategy

Romano-Wolf across eleven comparisons leaves one below 0.05, being the equal-weight universe with the strategy above it.

- Source `outputs/session-20/rebuilt/nulls.csv`
- Emitted comparisons 11, below 0.05 1, equal_weight_universe p 0.046 sign above; buy_hold_QQQ p 0.052
- Register 8.10
- Overturned by re-running the family at a higher replication count, since this ran at 1,000 draws where the two randomization nulls were raised to 10,000

## Claim 4, primary, about the grid

Probability of backtest overfitting is 0.1578088578088578 at S equal to 16 over the full 12,870 combination enumeration, spanning 0.11428571428571428 to 0.170995670995671 across the block counts 8, 12, 16 and 24 re-emitted on repaired code.

- Source `outputs/session-19/pbo.csv and outputs/session-24/phaseF-relaunch.csv`
- Emitted S16 0.1578088578088578, S8 0.11428571428571428, S12 0.170995670995671, S24 0.1646, S48 0.154; re-emitted on repaired code at chunk 257 the four reached reproduce exactly, S48 not reached
- Register 8.12, re-emitted in part at 9.48, wording repaired at 9.59
- Overturned by a CSCV variant that changes the selection rule rather than the block count

## Claim 5, supporting, about the apparatus

An estimator control puts the same harness at a PBO of 0.9919283331048036 when selection is driven purely by idiosyncratic noise.

- Source `outputs/session-19_6/degradation-null.csv`
- Emitted 0.9919283331048036
- Register 9.30
- Overturned by a control construction that preserves cross-specification structure the current permutation destroys

## Claim 6, primary, about the grid

The full-grid PBO exceeds none of the six within-stratum ranges, lying inside five and below one, which indicates search across strategy shapes adds nothing beyond parameter search.

- Source `outputs/session-19/pbo-strata.csv`
- Emitted sma_long 0.10334110334110334 to 0.1881895881895882 inside 1; crash_threshold 0.16876456876456877 to 0.18073038073038072 inside 0; rsi_dip 0.06674436674436675 to 0.1874125874125874 inside 1; rsi_rs 0.12315462315462315 to 0.23030303030303031 inside 1; overbought_t1 0.010023310023310023 to 0.4672882672882673 inside 1; oversold 0.07311577311577312 to 0.20264180264180265 inside 1
- Register 8.13
- Overturned by a stratification on an axis not currently classified structural that places the full-grid figure above its range

## Claim 7, supporting, about the grid

The canonical's own stratum PBO on each structural axis ranges from 0.13916083916083916 on oversold to 0.2355089355089355 on overbought tier one.

- Source `outputs/session-19/pbo-strata.csv`
- Emitted sma_long=0.14553224553224553; crash_threshold=0.1707070707070707; rsi_dip=0.15944055944055943; rsi_rs=0.17195027195027196; overbought_t1=0.2355089355089355; oversold=0.13916083916083916
- Register 8.13
- Overturned by the same condition as claim 6

## Claim 8, primary, about the grid

The canonical ranks 6,834 of 121,500 on the Lo-corrected Sharpe and 8,237 on annualised return, with eight of its nine axis values fixed before any comparison on that axis.

- Source `outputs/session-19/specification-curve.csv and outputs/session-21/canonical-provenance.csv`
- Emitted rank lo 6834 pct 94.3761316872428; rank ann 8237; axes before 8, after 1
- Register 9.32
- Overturned by establishing that a further axis was fixed after a comparison on that axis

## Claim 9, primary, about the apparatus

Against the grid's own cross-sectional distribution the canonical sits 1.0424959653759258 standard deviations above the mean at the 89.27654320987655 percentile, and it exceeds the expected maximum of an equivalent independent search only at the participation-ratio effective count and at none of the other three, so the two correlation-accounting methods disagree.

- Source `outputs/session-21/recentred-comparison.csv`
- Emitted z 1.0424959653759258; pct 89.27654320987655; exceeds at PR 1, SE 0, VT95 0, nominal 0
- Register 8.7 as amended
- Overturned by an accounting method that resolves the disagreement between the two reported here

## Claim 10, supporting, about the grid

Across the pre-registered 2,001-series subsample the effective number of independent trials is 3.4279931063515994 under the participation ratio, 6.719710164987509 under spectral entropy and 17 under a 95 percent variance threshold, with 0.4677702078080885 of variance in the first principal component.

- Source `outputs/session-20/effective-n.csv`
- Emitted PR 3.4279931063515994; SE 6.719710164987509; VT95 17; PC1 0.4677702078080885
- Register 9.28 under 9.10
- Overturned by a subsample shown non-representative, which session 21 phase C tested and did not find

## Claim 11, primary, about the strategy

Regressing the canonical on the investable buy-and-hold QQQ line gives a beta of 1.108672858112171 at an R-squared of 0.18679426851145753, with annualised alpha 0.28874420661558875 at a Newey-West t of 2.364283243646891, and the beta-hedged residual carries a naive Sharpe of 0.6558362612960221 and a Lo-corrected Sharpe of 0.8649152595612315.

- Source `outputs/session-21/beta-decomposition.csv`
- Emitted beta=1.108672858112171; r_squared=0.18679426851145753; alpha_annualised=0.28874420661558875; alpha_t_newey_west=2.364283243646891; residual_sharpe_naive=0.6558362612960221; residual_sharpe_lo=0.8649152595612315
- Register 9.34
- Overturned by a benchmark other than buy-and-hold QQQ that absorbs more of the return

## Claim 12, primary, about the apparatus

The timing component of the return decomposition changes sign across the estimation window, reading positive at 60 and 120 sessions and negative at 252 and 504, so it is not stable.

- Source `outputs/session-21/beta-decomposition.csv and outputs/session-22/beta-window-sensitivity.csv`
- Emitted 60 0.011293050910284682; 120 0.027230151692897046; 252 -0.004075416692355631; 504 -0.0077512681113622505
- Register 9.42
- Overturned by a window-selection rule fixed in advance that makes one window authoritative

## Claim 13, primary, about the strategy

Across eleven leave-one-out estimates the Lo-corrected Sharpe ranges from 1.287076427656795 to 1.6183359759194622, and the two years whose removal raises it most are 2020 and 2011.

- Source `outputs/session-22/rebuilt/leave-one-out.csv`
- Emitted min 1.287076427656795 max 1.6183359759194622; 2020 1.6183359759194622; 2011 1.5635962707744815
- Register 9.41
- Overturned by a rebuild on a different boundary, which session 22 ran and found identical

## Claim 14, primary, about the apparatus

Nine of twelve ladder rows carry a Lo factor inside their own no-autocorrelation null, the three outside being the three rows ranked highest on the Lo-corrected Sharpe, all of which outrank the strategy, and nine of twelve rows change rank across a sweep of the unregistered lag parameter q.

- Source `outputs/session-20/lo-q-sweep.csv`
- Emitted inside own null 9 of 12; outside are buy_hold_TQQQ, buy_hold_QQQ and matched_exposure_levered_QQQ_1.70, being lo ranks 1 to 3; rows_changing_rank_across_q 9; STRATEGY_rank_range 6 to 7
- Register 9.37, with 8.2 decided
- Overturned by registering q as an axis and sweeping it before any figure is selected

## Claim 15, supporting, about the strategy

Over a round-turn cost sweep spanning 0 to 50 bp, 10 of the 22 benchmark crossings fall inside the swept range and 12 are extrapolations, with the strategy crossing buy-and-hold QQQ on the naive Sharpe at 10.084002378357239 bp and not crossing it on the Lo-corrected Sharpe inside the range.

- Source `outputs/session-21/reads.csv`
- Emitted inside 10, extrapolations 12; buy_hold_QQQ naive 10.084002378357239; buy_hold_QQQ lo nan
- Register 4.4
- Overturned by widening the sweep so the twelve extrapolated crossings become measured

# LIMITATIONS

Each limitation sits beside the claim it qualifies rather than in a section a reader
skips.

## On the percentile claim, claim 8

**One of the nine axis values was fixed after a measurement on its own axis.** `crash_threshold` carried the source value of minus 12, session 04 closed an absolute threshold at minus 10 after session 03 measured all three estimator forms failing, and session 09 re-closed at the canonical value citing session 06's firing-rate measurement. The register marks it a stipulation. What those measurements compared was estimator form and firing rate rather than performance across levels, and the percentile claim is weakened on that axis alone.

**Seven of the nine closures carry no session attribution in the register**, so their ordering relative to any measurement rests on the entries' source-derived phrasing rather than on a dated record. That is a documentation gap rather than evidence of tuning. Source `outputs/session-21/canonical-provenance.csv`, register 9.32.

## On every claim that reads a config parameter

**Ten parameters defined in `src/config.py` have no consumer outside it**, being FINANCING_SPREAD_SWEEP_BP, INTERIOR_GAP_TREATMENT, N_SLEEVES, LABEL_ROUNDING_PERCENT, SLIPPAGE_MODEL, SLIPPAGE_MODELS, GRID_TOTAL_SPECIFICATIONS, GRID_SEARCHED_SPECIFICATIONS, GRID_UNSEARCHED_AXES, N_RSI_FUNCTION_TIED_PERIODS. **Two more carry a read that is never invoked**, being SIZING_MODE and EXECUTION_MODE, each read by `src/execution.py` as a default argument of a `size_position` the return-generating path never calls, while the engine hardcodes `math.trunc`. Source `outputs/session-21/unwired-config.csv`, register 9.31.

`SLIPPAGE_MODEL` and `SLIPPAGE_MODELS` have no consumer while `slippage_model` is a specification-curve axis, so the curve is real and was varied through function selection rather than through the config value, which 9.11 does not record. `GRID_TOTAL_SPECIFICATIONS` and `GRID_SEARCHED_SPECIFICATIONS` are read only inside `validate`, so the counts 7.10 relies on are checked but never consumed by a measurement.

## On the holdout

**SVIX and UVIX appear in weight dictionaries and load on neither panel.** `State.available` returns False for a ticker absent from the panel and the switch selects the fallback before the dictionary is built, so no weight is dropped, no balance goes to cash and no renormalisation occurs. The T10 terminal fires 1114 times holding SVXY and the S3 terminal 519 times holding UVXY across the primary window. Both list 2022-03-30, inside the holdout span, so the source strategy's guards would activate there while this implementation will not. **The loader is left unchanged deliberately**, since adding either ticker would execute the branch for the first time inside the single holdout read. Source `outputs/session-22/volatility-terminal-resolution.csv`, register 9.43.

## On the cost model, claim 15

**D16 stands.** The financing spread is assumed rather than measured, is treated by the cost sweep, and is **never read by the engine**. Its readers are the synthetics builder and validator, so the spread reaches results only through the pre-built reconstructions on the synthetic arm. On the realized arm, which is the designated cell, the levered funds carry the issuer's own financing inside their price history and no financing model applies. Register 9.31.

## On the ladder, claim 1

**The ladder dropped from fourteen lines to twelve**, removing the intraday-only and overnight-only hold universes. The drop is recorded nowhere and the Romano-Wolf family was never run at thirteen comparisons. Register 9.26.

**Romano-Wolf ran at 1,000 draws** while the two randomization nulls were raised to 10,000, so claim 3 and claim 2 rest on different replication counts.

## On every Sharpe figure, claim 14

**The Lo lag parameter q is a Python default at `scripts/s13_backtest.py:609`**, absent from `config.py`, on no specification-curve axis and on no grid axis, and it was discovered post hoc. It was never varied when any reported figure was selected. Register 9.37.

## On attribution, claim 11

**D23 stands**, being the portfolio-level per-instrument attribution confound, corrected in place at session 15.5.

## Outstanding measurements

**The B1 re-emission ran on a quiet machine and reached four of its five block counts**, being 8, 12, 16 and 24, before the pre-registered wall limit fired at 994.2 seconds with 48 unreached. **All four re-emitted PBO values reproduce the reported figures exactly**, so the chunk-first-element defect did not touch PBO and claim 4 stands on repaired code at both of its stated range endpoints. The degradation slope does move, by between 2.448e-04 and 1.080e-02, and it is withdrawn on separate grounds. Source `outputs/session-24/phaseF-relaunch.csv`, register 9.48.

**The wall limit was mis-derived and the halt reflects the limit rather than the machine.** 969 seconds came from ten times a single-chunk 96.9 second pass, while the sweep it had to cover measured 2424.37 seconds when first run. Load ran between 5.09 and 13.05 throughout and each completed stage beat its original, S=16 at 417.4 seconds against 775.01 and S=24 at 506.1 against 598.24. Register 9.49.

**One measurement remains outstanding and it is not load-bearing**, being S=48 of the B1 re-emission. The corrected degradation null is not run and its slope is withdrawn at 9.35 regardless. **No claim above depends on either.** Register 9.48 and 9.46.

## Figures

Two of the eight specified figures cannot be drawn from committed artifacts alone. The null distribution histograms need per-draw arrays the nulls file does not carry, and effective exposure by decile has only the mean and two named deciles rather than a ten-decile series. Source `outputs/session-24/figure-spec.csv`.

