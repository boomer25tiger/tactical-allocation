# Session 27, the holdout read

2026-08-22. Eight phases. One commit, at phase H. The holdout is read once and no quantity is recomputed.

## Opening

**All three gates pass.** The prediction hook exits 0 with the committed blob reading 3a3d150e986bcedfb9946deeb299373efac7026e7ccc7ca45625b9553fbecb2f at commit 35466c2131f24e35a5ce7fed13c4ed8c821ca45b. 339 hashed frozen inputs verify with 0 mismatches. The standing positive control reproduces 0.5218447451814521 annualised and 1.3817013060244996 Lo-corrected over 2472 sessions inside the 5e-07 tolerance stated before comparing.

**The holdout span the frozen data supports runs 2021-08-01 to 2026-08-14**, being 1265 sessions against the primary window's 2472, a ratio of 0.511731. The branch taken is proceed, the frozen inputs cover the span.

**The strategy ranks 2 of 12 on the naive Sharpe and 1 of 12 on the Lo-corrected**, at 1.637799226672021 and 2.7585227658215015.

| component | verdict |
|---|---|
| P1 | **falsified** |
| P2 | **falsified** |
| P3 part one | **falsified** |
| P3 part two | **falsified** |
| P4 | not a prediction, so it carries no verdict |
| P5 | evaluated because P1 is falsified, reported below |

## Phase A, the gates

**A1.** The hook exits 0. Commit 35466c2131f24e35a5ce7fed13c4ed8c821ca45b, blob 1282cf989cecbcedf9908f0cda0787377455d9ca, author timestamp 2026-08-22T11:25:54+02:00 and commit timestamp 2026-08-22T11:25:54+02:00. The working copy hash 3a3d150e986bcedfb9946deeb299373efac7026e7ccc7ca45625b9553fbecb2f matches the committed blob's, so the prediction predates this read.

**A3.** 347 files under data/, of which 339 carry a manifest row and were checked, with 0 mismatches and 8 unmanifested derived artifacts. Run before the rebuild, so no holdout quantity was computed on unverified input.

**A2.** Annualised return 0.5218447451814521 against 0.521845, Lo-corrected Sharpe 1.3817013060244996 against 1.381701, 2472 sessions against 2472, primary start 2011-10-04 read from the module.

## Phase B, what the data covers

347 frozen inputs surveyed for their first and last observation. The loaded universe holds 35 tickers and every one of them runs to 2026-08-14. The risk-free series, the index files and the NAV files all run to the same date, so the canonical specification is computable end to end through 2026-08-14.

The span runs 2021-08-02 to 2026-08-14, being 1265 sessions.

**The branch taken.** Proceed, the frozen inputs cover the span. Every input read is one of the 339 verified at gate A3, and no input is fetched in this session.

**SVIX and UVIX both list 2022-03-30, inside the span, and the loader excludes both.** Neither appears in bt.LEVERED or bt.UNLEVERED, exactly as the disposition at 9.43 recorded, and bt.LEVERED is not modified.

## Phase C, the read

One pass. The specification was read from `src/config.py` and `scripts/s14_common.py` rather than typed.

| parameter | value |
|---|---|
| convention | open-to-open |
| panel | realized |
| slippage | class-tiered at the 10 basis point anchor with the 2.0x opening auction premium |
| commission_arm | S |
| participation_cap_level | 0.05 |
| starting_nav | 1000000.0 |
| anchor_bp | 10 |
| premium_multiple | 2.0 |
| gross_cap | 1.0 |

The truncation at 2.10 was lifted for this process alone through an explicit environment variable read by `scripts/s13_backtest.py`. **The module default is unchanged at 2021-07-31 and the boundary is unchanged at 2021-08-01**, so every other context still loads nothing past the boundary.

### The holdout ladder

| line | annualised return | annualised volatility | naive Sharpe | Lo-corrected Sharpe | maximum drawdown | annualised turnover |
|---|---|---|---|---|---|---|
| sleeve_T11_standalone | 1.313012720487563 | 0.570075291654565 | 1.6908510997306647 | 2.7247782925407056 | -0.4305667326615191 | 34.109057155197675 |
| STRATEGY | 0.8287111594113898 | 0.3934998613555563 | 1.637799226672021 | 2.7585227658215015 | -0.34468314755389173 | 21.02620648507965 |
| sleeve_T10_standalone | 0.9461055789243662 | 0.4868654554974534 | 1.5337658933089617 | 1.1113265475176035 | -0.4957910031896602 | 41.02040500189913 |
| long_legs_only | 0.6265336305815792 | 0.3637294538968133 | 1.4186980765107986 | 2.6317016722108373 | -0.3281707657776073 | 15.238815402588331 |
| sleeve_S2_standalone | 0.402648310411285 | 0.4440416412710884 | 0.9011603129601938 | 1.4945981218587112 | -0.5749924155273771 | 7.322576943406229 |
| sleeve_S3_standalone | 0.43957094973070543 | 0.6363464320477087 | 0.8331655729834205 | 1.0621260466751712 | -0.5140030793237094 | 14.284325152736836 |
| vol_targeted_QQQ_matched | 0.1945673888317121 | 0.3067051755445477 | 0.6127370762969571 | 0.8346302118441822 | -0.41179118100023615 | 1.3997366604134576 |
| equal_weight_universe | 0.24176959544981536 | 0.6508260749446413 | 0.6026665018822145 | 0.7363520341847385 | -0.7545429227938443 | 0.0 |
| buy_hold_QQQ | 0.157638543940549 | 0.2300897914442293 | 0.5900079739660359 | 0.7438002112188974 | -0.36694214173860695 | 0.0 |
| buy_hold_TQQQ | 0.20005691436855488 | 0.6909352827577188 | 0.5565614254276027 | 0.7020549626450708 | -0.8157208038838037 | 0.0 |
| matched_exposure_levered_QQQ_1.70 | 0.19555435441853186 | 0.3933639019553852 | 0.5564319475300712 | 0.7020177681359031 | -0.5751006880169329 | 0.9083201266384529 |
| naive_fast_1d_momentum | -0.11596775095781109 | 0.4618979811353646 | -0.11299625825558965 | -0.10387976457665896 | -0.8100333273384939 | 63.98876460719003 |

**The canonical's daily series over the holdout.** Mean 0.0027050347916394556, standard deviation 0.0247881612877428, skewness 0.00044220578416748354, excess kurtosis 5.223157724383093, across 1265 sessions from 2021-08-02 to 2026-08-14.

## Phase D, the components

Phase D re-executed the identical deterministic pass to obtain the per-session sleeve dicts phase C did not persist. **The re-execution reproduces phase C exactly**, naive gap 0.0, Lo gap 0.0, sessions 1265. The re-execution varies no specification and exists only because phase C did not persist the per-session sleeve dicts.

### P1

The condition as the prediction states it.

> In the holdout, on the designated cell, the strategy ranks no better than sixth of twelve on the naive Sharpe. Falsified by any rank of fifth or better.

| quantity | value | verdict |
|---|---|---|
| rank on the naive Sharpe | 2 of 12 | falsified |
| rank on the Lo-corrected Sharpe | 1 of 12 | reported alongside |
| the two ranks diverge | 1 | reportable |
| strategy naive Sharpe | 1.637799226672021 |  |
| strategy Lo-corrected Sharpe | 2.7585227658215015 |  |

### P2

The condition as the prediction states it.

> The strategy's holdout naive Sharpe lands between 0.25 and 0.85, against 1.0910863648060856 over the primary window at outputs/session-20/rebuilt/metrics-full.csv. Falsified above 0.85 or below 0.25.

| quantity | value | verdict |
|---|---|---|
| holdout naive Sharpe | 1.637799226672021 | falsified |
| distance to the nearer bound, being 0.85 | 0.787799226672021 |  |

### P3 part one

The condition as the prediction states it.

> Part one. SQQQ and TLT realise positive daily return correlation over the holdout. Falsified by a negative realised correlation.

| quantity | value | verdict |
|---|---|---|
| SQQQ and TLT daily return correlation, holdout | -0.07884210926185957 of 1265 | falsified |
| the same pair over the primary window | 0.16448233204452256 of 3737 |  |
| committed sleeve-level baseline | -0.5618926986740371 |  |
| sign flips from the primary window | 0 |  |

### P3 part two

The condition as the prediction states it.

> Part two. T10's risk-off branch contributes negatively to holdout return. Falsified by a positive contribution.

| quantity | value | verdict |
|---|---|---|
| T10 risk-off branch contribution, holdout | 0.06250008813584088 of 416 | falsified |
| the SQQQ leg alone | 0.09966091314902041 |  |
| the TLT leg alone | -0.037160825013179535 |  |
| the SQQQ leg over the primary window | -0.0848435348504287 |  |
| the part predicts persistence rather than change | 1 |  |
| sessions the branch fired, holdout | 416 |  |
| sessions the branch fired, primary window | 928 |  |

### P4

The condition as the prediction states it.

> State-classification latency in a slow bear is not measurable from the primary window and is not predicted.

| quantity | value | verdict |
|---|---|---|
| the 2022 peak, taken as buy-and-hold QQQ's 2022 high | 2022-01-03 | not a prediction |
| the strategy's own 2022 NAV peak | 2022-10-13 |  |
| first risk-off state after the peak | 2022-01-10 |  |
| sessions from the peak to the first risk-off state | 5 |  |
| mean effective exposure across that interval | 0.9277520939003893 of 5 |  |
| minimum effective exposure across that interval | 0.9022991359297223 |  |
| maximum effective exposure across that interval | 1.0006645933510157 |  |
| sessions in that interval with exposure above 1.0 | 1 of 5 |  |
| the guard |  |  |

### P5

The condition as the prediction states it.

> If P1 fails, the most likely reason is that 2022 gave the short-equity sleeve its only sustained tailwind in either window, carrying the strategy past passive in the one period its hedges exist for.

| quantity | value | verdict |
|---|---|---|
| short-equity sleeve holdout contribution | 0.3160580325724543 | positive |
| the SQQQ contribution | 0.2896712920331235 |  |
| the TECS contribution | 0.014551358900689083 |  |
| the SOXS contribution | -0.0006734763885016953 |  |
| the PSQ contribution | 0.012508858027143454 |  |
| the SH contribution | 0.0 |  |
| naive Sharpe with the short contribution removed | 1.333724053273868 |  |
| rank the strategy would hold on that series | 4 of 12 |  |
| the short sleeve accounts for the rank | 0 |  |

## Phase E, the frozen claims against the holdout

**The holdout bears on 8 of the 15 claims, 1 of which was evaluated in this session, and does not bear on 7.** 0 claims are contradicted. **No claim is amended.**

| claim | tier | bears on the holdout | holdout value | contradicted |
|---|---|---|---|---|
| 1 | primary | yes | rank 2 of 12 on the naive Sharpe and 1 of 12 on the Lo-corrected; STRATEGY naive 1.637799226672021 lo 2.7585227658215015; buy_hold | no |
| 2 | primary | yes | not evaluated | not evaluated |
| 3 | primary | yes | not evaluated | not evaluated |
| 4 | primary | no | not applicable | no |
| 5 | supporting | no | not applicable | no |
| 6 | primary | no | not applicable | no |
| 7 | supporting | no | not applicable | no |
| 8 | primary | no | not applicable | no |
| 9 | primary | no | not applicable | no |
| 10 | supporting | no | not applicable | no |
| 11 | primary | yes | not evaluated | not evaluated |
| 12 | primary | yes | not evaluated | not evaluated |
| 13 | primary | yes | not evaluated | not evaluated |
| 14 | primary | yes | not evaluated | not evaluated |
| 15 | supporting | yes | not evaluated | not evaluated |

**Claim 1 is the one evaluated.** The claim is scoped to the designated cell over the primary window, so a forward span does not contradict it as written. The holdout value differs from the claim's value on both conventions and on the sign of both gaps, and that difference is reported here rather than resolved.

## Phase F, the combined window

The primary window and the holdout together, being 3737 sessions from 2011-10-04 to 2026-08-14. **Descriptive only**, since the combined window contains the sample the specification was chosen on and is not an out-of-sample measurement.

| line | annualised return | naive Sharpe | Lo-corrected Sharpe | maximum drawdown |
|---|---|---|---|---|
| long_legs_only | 0.6181868058999644 | 1.262183478389011 | 1.6281378659260184 | -0.5153437730420118 |
| STRATEGY | 0.6194765048951141 | 1.2448587065882768 | 1.6423297853685075 | -0.5306024012913018 |
| sleeve_T11_standalone | 0.6152931891234881 | 1.1188133313136093 | 1.278051949267837 | -0.6166126119200541 |
| sleeve_S2_standalone | 0.5960641544716794 | 1.1056587000098452 | 1.2462712036231753 | -0.5848873576289952 |
| sleeve_S3_standalone | 0.549239118754669 | 0.9892214517564153 | 1.151689324912334 | -0.599863197073831 |
| buy_hold_QQQ | 0.20563612021706645 | 0.9358642965204582 | 1.2915236759630055 | -0.36694214173860606 |
| vol_targeted_QQQ_matched | 0.28103538566322084 | 0.915597177336106 | 1.1961152468210106 | -0.4117911810002369 |
| buy_hold_TQQQ | 0.4596008871936763 | 0.9022460404699733 | 1.2585173711934112 | -0.8157208038838035 |
| matched_exposure_levered_QQQ_1.70 | 0.30657482868269303 | 0.8996770340067696 | 1.25575424653672 | -0.5751006880169329 |
| sleeve_T10_standalone | 0.29704476498872756 | 0.6969287766524662 | 0.67731005380318 | -0.8661090614058048 |
| equal_weight_universe | 0.18037566211153155 | 0.5566604261947258 | 0.6228324956984008 | -0.7545429227938443 |
| naive_fast_1d_momentum | 0.12095872538560881 | 0.445426010220869 | 0.4509168277431732 | -0.8100333273384941 |

The strategy places 2 of 12 on the naive Sharpe and 1 of 12 on the Lo-corrected across the combined window.

## Phase G, the figures

| figure | SVG bytes | plotted rows |
|---|---|---|
| `combined-equity-curve.svg` | 161157 | 3737 |
| `combined-drawdown.svg` | 153977 | 3737 |

Both are drawn through `scripts/s19_svg.py` with the 2021-08-01 boundary marked, each carrying the exact series it plots as a CSV beside it. Both read the series phase C wrote, so neither recomputes any quantity. **These are the fifth and sixth figures under the cap at 9.60, so the cap is reached and no further figure is drawn.**

## What each finding is

| finding | what acting on it would be |
|---|---|
| all four falsifiable prediction components are falsified | documentation, since the prediction is frozen at 9.64 and is not amended after the read |
| the strategy's two holdout ranks diverge | documentation |
| claim 1's holdout value differs from its primary-window value | documentation, since the claim is scoped to the primary window and is not amended |
| P3 part one's primary-window direction is the opposite of the one the prediction assumed | documentation |
| the prediction's -1.074235187878671 baseline is portfolio-level while P3 part two is T10-only | documentation |
| seven claims bear on the holdout and were not evaluated | a specification change, since evaluating any would need a measurement outside this session's single pass |
| the READ_HOLDOUT_THROUGH override in scripts/s13_backtest.py | a specification change, recorded at 9.66, with the default and the boundary both unchanged |
| 2.10's second half no longer holds | a register decision, applied |

**No recommendation and no interpretation is made on any of them.**

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count above the limit is 0.

| reading | before the commit | expected delta |
|---|---|---|
| working tree, KiB | 830296 | +0 |
| git directory, KiB | 207616 | +2064 or less |
| free space, GiB | 18.91 | 0.00 to -0.01 |

The commit touches 30 files totalling 2319849 bytes on disk, of which 27 files and 2113919 bytes are new. **Nothing is read after the commit**, under 9.62.

## Register

9.66 the holdout as read, with the span, the branch and the gate output. 9.67 each component with its verdict. 9.68 the frozen claims against the holdout. 9.69 the fifth and sixth figures. 2.10 amended, since post-boundary quantities now exist.

## Artifacts

- `outputs/session-27/gates.csv`
- `outputs/session-27/holdout-coverage.csv`
- `outputs/session-27/holdout-ladder.csv`
- `outputs/session-27/holdout-canonical.csv`
- `outputs/session-27/prediction-verdicts.csv`
- `outputs/session-27/claims-vs-holdout.csv`
- `outputs/session-27/combined-window.csv`
- `outputs/session-27/size.csv`
- `outputs/session-27/figures/`, two SVG files with two series CSVs
- the retained series, being `_holdout_line_returns.parquet`, `_combined_line_returns.parquet`, `_canonical_daily.parquet`, `_canonical_orders.parquet` and `_state_series.parquet`

