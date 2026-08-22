# Session 25, the figures

2026-08-22. Six phases. One commit, at phase F.

## Opening

**The 8.2 argument holds as stated and fails if generalised.** 2 of the 5 rows outranking the strategy sit inside their own null, being long_legs_only and vol_targeted_QQQ_matched, so outranking the strategy does not imply sitting outside the null. 8.2 names buy-and-hold QQQ specifically, and on that pairing it stands. 8.2 is not amended here.

**Claim 4's wording spans all five block counts while its two quoted figures do not.** The range's numeric endpoints are S equal to 8 at 0.11428571428571428 and S equal to 12 at 0.170995670995671, both re-emitted on repaired code at session 24, and the scope phrase names block counts 8 through 48, which includes the unre-emitted S equal to 48.

**8 figures drawn**, each with the exact series it plots emitted as a CSV beside it in `outputs/session-25/figures/`.

**No figure disagrees with the claim it illustrates.** 27 numeric checks ran, 25 exact and 2 agreeing within the stated tolerance rather than exactly.

## Machine

At the start, load average 25.35 one minute, 11.4 five minutes and 8.61 fifteen minutes on eight cores, compressor 2.901 GiB, swap used 11784.06 MB and swap free 1527.94 MB. Nothing in phases A through E loads the moment array, so no contention gate applied. At phase F, load average 5.88, compressor 3.011 GiB, swap used 11475.44 MB and swap free 812.56 MB.

**The standing positive control passed.** Annualised return 0.5218447451814521 against the target 0.521845, Lo-corrected Sharpe 1.3817013060244996 against 1.381701, 2472 sessions against 2472, inside the tolerance 5e-07 stated before comparing.

## Phase A1, the Lo null argument

5 ladder rows outrank the strategy on the Lo-corrected Sharpe, the strategy placing 6 of 12.

| row | observed Lo-corrected Sharpe | own null 5th percentile | own null 95th percentile | inside |
|---|---|---|---|---|
| buy_hold_TQQQ | 1.8057440502648456 | 0.8233761527592989 | 1.4834802306081902 | no |
| buy_hold_QQQ | 1.8033205778849906 | 0.820220296843908 | 1.47866235794891 | no |
| matched_exposure_levered_QQQ_1.70 | 1.8017816270863776 | 0.8234552740076613 | 1.483349422403496 | no |
| long_legs_only | 1.4695627600234846 | 0.8300481461907913 | 1.5153672392519424 | yes |
| vol_targeted_QQQ_matched | 1.4304523894100714 | 0.8306618122953046 | 1.5159596470316377 | yes |
| **STRATEGY** | 1.3817011382923612 | 0.8106119182519183 | 1.5045050578577397 | yes |

The inside flag agrees with the percentile bounds on every row, so the emitted flag and the emitted bounds are consistent.

**As stated, the argument holds.** 8.2 names buy-and-hold QQQ specifically. buy_hold_QQQ sits outside its own null and the strategy sits inside its own, so the sentence as written is true.

**Narrowed to the top three, it holds.** The three outside are buy_hold_TQQQ, buy_hold_QQQ and matched_exposure_levered_QQQ_1.70, being Lo ranks 1 to 3.

**Generalised to every row above the strategy, it fails.** 2 of the 5 rows outranking the strategy sit inside their own null, being long_legs_only and vol_targeted_QQQ_matched, so outranking the strategy does not imply sitting outside the null.

The grounds as they should read.

> The strategy's own Lo factor sits inside its own no-autocorrelation null while the three rows ranked highest on the Lo-corrected Sharpe sit outside theirs, and two further rows outranking the strategy sit inside theirs, so the property separates the top three rather than separating every row above the strategy from every row below it.

The current register text at 8.2, for comparison.

> The grounds are that session 20's D1 measured the strategy's own Lo factor sitting inside its own no-autocorrelation null while buy-and-hold QQQ's sits outside, and that nine of twelve ladder rows change rank across the q sweep, so the Lo-corrected ordering is not stable under a parameter that was never registered.

## Phase A2, claim 4's block-count range

Claim 4 verbatim.

> Probability of backtest overfitting is 0.1578088578088578 at S equal to 16 over the full 12,870 combination enumeration, spanning 0.11428571428571428 to 0.170995670995671 across block counts 8 through 48.

Block counts re-emitted on repaired code at session 24, 8,12,16,24. Not re-emitted, 48.

**The two numeric endpoints are both re-emitted**, being 0.11428571428571428 at S equal to 8 and 0.170995670995671 at S equal to 12. **The wording spans all five block counts**, since the phrase naming block counts 8 through 48 gives the scope of the sweep rather than the two S values the endpoints come from, so the wording covers S equal to 48, which is not re-emitted, while the two numeric figures quoted do not depend on it.

The two candidate repairs, with no change made and no recommendation.

1. Narrow the wording. Restate the scope as the block counts re-emitted on repaired code, so the sentence carries no figure and no scope that S equal to 48 could move.
2. Leave the item open. Leave the wording and carry the item open at 9.48 until S equal to 48 re-emits, since the two quoted figures already stand on repaired code.

## Phase B, the figure inventory

**Both session 24 undrawable findings are confirmed against the current artifacts.** CONFIRMED. outputs/session-22/rebuilt/nulls.csv at n_draws ['10000.0'] carries 8 summary columns, being null_ann_mean, null_ann_p05, null_ann_p50, null_ann_p95, null_ann_max, null_sharpe_mean, null_sharpe_p95, null_sharpe_max, and 1 per-draw columns. The distribution shape is unavailable and retaining the draws is a new measurement rather than a read. CONFIRMED. outputs/session-16/exposure-reconciliation.csv carries mean_effective_exposure with 2 named decile columns, being worst_trailing_return_decile, wildest_vol_decile, rather than a ten-decile series. outputs/session-15.5/short-leg-decomposition.csv carries the same two named deciles and no series, and no other committed CSV carries effective exposure at all.

A five-point quantile marker plot is drawable from the null summary columns and is not substituted for a histogram, since it would not show the distribution shape the figure exists to show.

13 candidates, 2 excluded as undrawable and 3 excluded because the PBO report already carries them, leaving 8 against a target of 8.

**The drop rule was not needed.** the final set equals the target, so the rule that a figure illustrating a supporting claim yields to one illustrating a primary claim was not needed. Had it been applied, the three figures illustrating no frozen claim would have ranked below the one illustrating a supporting claim, being drawdown, hedge-intensity, nav-capacity and rolling-beta-dispersion.

| figure | claims illustrated | tier | carries the claim's literal | source |
|---|---|---|---|---|
| equity-curve | 1 | primary | no | `outputs/session-20/rebuilt/_ladder_returns.pkl` |
| drawdown | none | none | no | `outputs/session-20/rebuilt/_ladder_returns.pkl` |
| cost-sweep | 15 | supporting | yes | `outputs/session-20/rebuilt/cost-sweep-designated.csv and outputs/session-21/reads.csv` |
| leave-one-out | 13 | primary | yes | `outputs/session-22/rebuilt/leave-one-out.csv` |
| hedge-intensity | none | none | no | `outputs/session-15.5/hedge-intensity.csv` |
| nav-capacity | none | none | no | `outputs/session-20/rebuilt/nav-sweep.csv` |
| lo-factor-vs-null | 14,1 | primary | yes | `outputs/session-20/lo-q-sweep.csv` |
| rolling-beta-dispersion | none | none | no | `outputs/session-21/beta-decomposition.csv and outputs/session-22/beta-window-sensitivity.csv` |

**4 of the eight illustrate no frozen claim**, being drawdown, hedge-intensity, nav-capacity and rolling-beta-dispersion. Each is retained because the set is at target without dropping any, and each is recorded here rather than carried silently.

**3 of the eight plot a value the claim quotes.** The other five illustrate a claim's subject or a register finding without plotting any figure the claim carries, which is what phase E can and cannot check.

**7 claims have no figure anywhere**, being 2, 3, 7, 9, 10, 11, 12. Claim 2 is among them because its figure is undrawable rather than because it was passed over.

## Phase C, the figures as drawn

Each figure carries axis labels with units, the source file in a caption line and the sample period, and no title states a conclusion. Each is written with its plotted series as a CSV at full round-trip precision.

| figure | SVG bytes | plotted rows |
|---|---|---|
| `equity-curve.svg` | 107820 | 2472 |
| `drawdown.svg` | 102885 | 2472 |
| `cost-sweep.svg` | 10139 | 28 |
| `leave-one-out.svg` | 6634 | 12 |
| `hedge-intensity.svg` | 4903 | 4 |
| `nav-capacity.svg` | 5722 | 5 |
| `lo-factor-vs-null.svg` | 11291 | 12 |
| `rolling-beta-dispersion.svg` | 5675 | 4 |

Plotting used `scripts/s19_svg.py`, extended by `scripts/s25_svg.py` for the marks this session needed. `scripts/s19_svg.py` is unmodified so session 19's four figures stay byte-identical under the regenerability check. matplotlib was not installed.

## Phase D, the paper's two

The criterion is the scaffold's, being which two illustrate the largest number of primary claims between them, applied by enumerating all 28 pairs.

**The maximum coverage by any pair is 3 distinct primary claims, and 1 pair reaches it.**

> leave-one-out + lo-factor-vs-null, covering primary claims 1,13,14.

| figure | primary claims | supporting claims |
|---|---|---|
| cost-sweep | none | 15 |
| drawdown | none | none |
| equity-curve | 1 | none |
| hedge-intensity | none | none |
| leave-one-out | 13 | none |
| lo-factor-vs-null | 1,14 | none |
| nav-capacity | none | none |
| rolling-beta-dispersion | none | none |

A second ordering is available if a tie ever needs breaking. three of the eight carry a claim's literal emitted value in the series they plot, being cost-sweep, leave-one-out and lo-factor-vs-null. The other five illustrate a claim's subject or a register finding without plotting any figure the claim quotes, which is a second ordering available if the primary count leaves a tie.

**The PBO report carries four figures and none of the eight duplicates one.** none. The three candidates that would have duplicated one were excluded at phase B, being logit-histogram, is-vs-oos-scatter and specification-curve, so the eight and the report's four are disjoint.

**One correction to the session 24 specification.** degradation-scatter.svg carries a fitted line for the degradation slope withdrawn at 9.35. The logit histogram carries the PBO, which is claim 4 and stands, so the session 24 specification's note that two of the four support a statistic since removed overstates it by one.

**No selection is made.** the scaffold requires the analysis and leaves the choice.

## Phase E, the figure-to-claim check

27 numeric checks against the tolerance 5e-07 stated before comparing. 25 agree exactly, 2 agree within tolerance rather than exactly, and 0 disagree.

| claim | figure | quantity | claim value | figure value | deviation |
|---|---|---|---|---|---|
| 1 | lo-factor-vs-null | strategy Lo-corrected Sharpe | 1.3817013060244996 | 1.3817011382923612 | 1.6773213840082235e-07 |
| 1 | lo-factor-vs-null | Lo gap to buy-and-hold QQQ | 0.42161920118337926 | 0.4216194395926294 | 2.3840925011953118e-07 |

**Both non-exact checks have the same cause.** The `lo-factor-vs-null` figure plots `outputs/session-20/lo-q-sweep.csv` while claim 1 quotes `outputs/session-20/rebuilt/metrics-full.csv`, so the comparison is between two emitted files rather than between a figure and its own source. The two differ at the seventh decimal, below the tolerance the positive control uses, and neither is changed here.

The derived series were checked against the emitted scalars rather than assumed. The equity curve's final growth reproduces each line's emitted total return and the drawdown series minimum reproduces each line's emitted maximum drawdown, all exactly.

## What acting on each finding would be

| finding | acting on it would be |
|---|---|
| the 8.2 grounds fail if generalised beyond buy-and-hold QQQ | a register decision |
| claim 4's wording spans a block count not re-emitted | a specification change, or a register decision to leave it open |
| seven claims have no figure | documentation |
| four figures illustrate no frozen claim | documentation |
| the lo-q-sweep and ladder Lo values differ at the seventh decimal | a correctness repair if the difference has a cause worth removing, documentation if it does not |
| the session 24 note that two report figures support a removed statistic overstates it by one | documentation |
| the null histograms and the decile curve remain undrawable | a specification change, since drawing either needs a new measurement |

No recommendation is made on any of them.

## What remains before the holdout can run

S equal to 48 of the B1 re-emission, which sets neither endpoint of claim 4's quoted range, and the corrected degradation null, whose slope is withdrawn at 9.35 regardless. Neither is load-bearing. The two claim-wording questions this session raises are decisions rather than blockers, since neither changes a figure. The SVIX and UVIX path that will not execute at the holdout read stands as disclosed at 9.43 with the loader unchanged.

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count of tracked files above the limit is 0.

| reading | before the commit | after the commit |
|---|---|---|
| git directory, kilobytes | 205336 | not yet read |
| working tree, kilobytes | 825688 | not yet read |
| free space, GiB | 18.63 | not yet read |

## Register

9.55 the figure set as drawn. 9.56 the Lo null argument, with 8.2 left unamended. 9.57 claim 4's wording. 9.58 the claims without a figure and the figures excluded.

## Artifacts

- `outputs/session-25/claim-checks.csv`
- `outputs/session-25/figure-inventory.csv`
- `outputs/session-25/paper-figure-analysis.csv`
- `outputs/session-25/figure-claim-check.csv`
- `outputs/session-25/figures/`, 8 SVG files with 8 series CSVs

