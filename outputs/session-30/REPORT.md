# Session 30, the class sweep, the disposition and the resumed phases

2026-08-23. Nine phases. One commit, at phase I. No specification is selected on any holdout observation, no frozen input is repaired and no canonical value moves.

## Opening

**The class sweep screened 43925 instrument-sessions across 17 held instruments and flagged 174, a selectivity of 0.00396130.** 3 price discontinuities carry no recorded split, of which 2 survive the residual screen as breaks, being SOXS 2026-05-26; SVXY 2018-02-06.

**Gate B reads PROCEED.** the gate as the scaffold states it, being a break in an instrument contributing materially. no break sits in a material instrument and no contaminated indicator session coincides with a terminal firing, so phases C through H proceed. The first implementation tested materiality without conjoining the break condition and would have read HALT, and both evaluations are recorded.

**The holdout nulls.**

| null | metric | holdout exceedances | primary exceedances |
|---|---|---|---|
| timing_shuffle_block_bootstrap | ann_return | 4 of 10000 | 7 of 10000 |
| timing_shuffle_block_bootstrap | sharpe_naive | 0 of 10000 | not reported for this metric at session 22 |
| timing_shuffle_block_bootstrap | sharpe_lo | 1 of 10000 | 0 of 10000 |
| turnover_matched_switching | ann_return | 3 of 10000 | 0 of 10000 |
| turnover_matched_switching | sharpe_naive | 0 of 10000 | not reported for this metric at session 22 |
| turnover_matched_switching | sharpe_lo | 2 of 10000 | 0 of 10000 |

**The multi-factor alpha survives.** The holdout annualised alpha falls from 0.5637941837318013 to 0.45868406085120844, absorbing 0.10511012288059288 or 0.18643349987199245 of it, with the Newey-West t moving from 3.4918970688555846 to 2.9859793219153783.

**The holdout result is capacity-bounded.** Across five starting NAV levels the naive Sharpe runs from 1.637799226672021 at the study anchor to 0.9817333726959366 at the terminal NAV, degrading smoothly and monotone in NAV.

## Machine and the positive control

At phase A, load average 8.47 one minute, 6.94 five minutes and 6.27 fifteen minutes on 8 cores, compressor 2.788 GiB, swap used 11848.69 MB and swap free 1463.31 MB. At phase B the one-minute figure read 3.28, at phase D 4.05, at phase E 3.83, at phase F 4.12, at phase G 2.4 and at phase H 4.23.

**The standing positive control passed** at 0.5218447451814521 annualised and 1.3817013060244996 Lo-corrected over 2472 sessions, inside the 5e-07 tolerance stated before comparing.

## Phase A, the ruling and the pre-registration

The session 28 ruling stands. The complete quantity list for phases B through H went into the register at 9.82 before any measurement ran, and it is closed. Every measurement is a disclosed post-hoc sensitivity under 9.10 with its motivation recorded first, and the class sweep's own motivation is recorded before the rest.

**Gate B was written before the check** and materiality was defined before the flags were seen, at 0.05 of the window's arithmetic return sum.

## Phase B, the corporate action class sweep

### The rule, stated before running

the tracking residual e equals the observed return minus the registered multiple times the proxy's return. A missing split of ratio R contributes about 1/R minus 1 to e, being -0.0476 at R equal to 1.05 and -0.1667 at R equal to 1.2, and it does not shrink as the underlying's move grows. The threshold catches ratios at and above about 1.053. RESIDUAL_TOL is 0.05.

below this the implied multiple is not computed, since its denominator is unstable. Those sessions are screened on absolute return instead, the floor being 0.005, and applied to the sessions the implied multiple cannot be computed on, so they are not silently dropped. A missing split of ratio 1.33 or larger shows as an absolute return above this on its own at 0.25.

### B1, the screen

| instrument | flagged | screened | below the floor | proxy | registered multiple |
|---|---|---|---|---|---|
| BIL | 0 | 0 | 0 | none |  |
| BSV | 0 | 0 | 0 | none |  |
| BTAL | 0 | 0 | 0 | none |  |
| LABU | 1 | 2820 | 642 | XBI | 3.0 |
| PSQ | 0 | 3737 | 1575 | QQQ | -1.0 |
| QLD | 0 | 3737 | 1575 | QQQ | 2.0 |
| QQQ | 0 | 0 | 0 | none |  |
| SOXL | 8 | 3737 | 1055 | SMH,SOXX | 3.0 |
| SOXS | 7 | 3737 | 1055 | SMH,SOXX | -3.0 |
| SPXL | 0 | 3737 | 1920 | SPY | 3.0 |
| SQQQ | 0 | 3737 | 1575 | QQQ | -3.0 |
| SVXY | 17 | 3736 | 519 | vx-cm30 | -1.0 |
| TECL | 2 | 3737 | 1498 | XLK | 3.0 |
| TECS | 1 | 3737 | 1498 | XLK | -3.0 |
| TLT | 0 | 0 | 0 | none |  |
| TQQQ | 1 | 3737 | 1575 | QQQ | 3.0 |
| UVXY | 137 | 3736 | 519 | vx-cm30 | 2.0 |

15006 instrument-sessions fell below the underlying floor and were screened on absolute return instead. 0 registered benchmarks lack a frozen proxy.

**The three session 29 volatility flags under this sweep's rule.**

- SVXY 2018-02-06, remains flagged under the sweep's rule.
- UVXY 2018-02-05, remains flagged under the sweep's rule.
- UVXY 2020-03-16, remains flagged under the sweep's rule.

### B2, ordering by contribution

| instrument | window | rank | contribution | flagged sessions | flagged contribution |
|---|---|---|---|---|---|
| TQQQ | holdout | 1 | 0.951556253095966 | 1 | 0.0 |
| SOXL | holdout | 2 | 0.9487899220608594 | 8 | -0.013171184372326755 |
| SQQQ | holdout | 3 | 0.2896712920331235 | 0 | 0.0 |
| UVXY | holdout | 4 | 0.1350964817698338 | 137 | 0.0 |
| TECL | holdout | 5 | 0.11282071433845367 | 2 | 0.0 |
| QLD | holdout | 6 | 0.07038963122854404 | 0 | 0.0 |
| TQQQ | primary | 1 | 2.152772082139501 | 1 | 0.0 |
| SOXL | primary | 2 | 1.4555486425919377 | 8 | -0.03216081285910056 |
| SQQQ | primary | 3 | -0.7676845366846142 | 0 | 0.0 |
| UVXY | primary | 4 | 0.6949195804794077 | 137 | 0.7527988192268535 |
| TECL | primary | 5 | 0.4630496070477503 | 2 | -0.03013653577064414 |
| SVXY | primary | 6 | 0.2160505499895108 | 17 | -0.02143727273358001 |

**Holdout.** Cumulative flagged contribution -0.041841805663843774, against the window's arithmetic return sum of 3.4218690114239116, a share of 0.012227763694096672. Instruments material under the gate, none. Materiality was fixed at 5 percent of the window's arithmetic return sum before the flags were seen.

**Primary.** Cumulative flagged contribution 0.6690641978635289, against the window's arithmetic return sum of 5.284814143474101, a share of 0.1266012729491568. Instruments material under the gate, UVXY.

**TQQQ named explicitly.** It contributes 0.951556253095966 across the holdout and 2.152772082139501 across the primary window, with 1 flagged sessions.

### B3, indicator contamination

174 flagged sessions examined. 0 is the longest contaminated span, since no indicator reads any flagged instrument. sma_long at 200 sessions sets the outer bound for any instrument an SMA reads.

**0 contaminated indicator sessions coincide with a terminal firing**, which is the condition gate B tests. The relative-strength reads carrying a literal ticker are AGG, BND, BSV, IEF, PSQ, QQQ, RYMFX, SH, SQQQ, TLT, XLK, and no flagged instrument is among them.

### B4, the split column's reliability

66 recorded splits carry no matching price discontinuity, the price series is already adjusted for these, which is the expected state for an adjusted series rather than a defect. 3 price discontinuities carry no recorded split.

| instrument | date | is a break | reason |
|---|---|---|---|
| SOXS | 2025-04-09 | no | market move. The price step is outside the band because the underlying moved far enough that the registered multiple carries the fund past it, and the residual screen clears the session, so no adjustment artifact is present |
| SOXS | 2026-05-26 | yes | BREAK. The price step is outside the band and the residual screen also flags it, so the registered multiple times the underlying's move does not account for it |
| SVXY | 2018-02-06 | yes | BREAK. The price step is outside the band and the residual screen also flags it, so the registered multiple times the underlying's move does not account for it |

### Gate B

| test | result |
|---|---|
| instruments_with_a_break | 2 being SOXS, SVXY |
| instruments_material_by_flagged_contribution | 1 being UVXY |
| instruments_with_both | 0 being none, so no break sits in a material instrument |
| contaminated_session_coinciding_with_a_firing | 0  |
| verdict_materiality_alone | HALT being the first implementation tested materiality without conjoining the break condition and would have halted on UVXY |
| verdict | PROCEED being the gate as the scaffold states it, being a break in an instrument contributing materially. no break sits in a material instrument and no contaminated indicator session coincides with a terminal firing, so phases C through H proceed |

the 5 percent threshold fixed at 9.82 before the flags were seen is not moved. Only the conjunction the scaffold states was added to the implementation.

## Phase C, the disposition and one restatement

### C1, the three options, adopted by none

**Option one, repair the frozen input.**

- file_that_changes, data/raw/etf/SOXS.parquet. its current SHA-256 is b66d2a7012c307214d47aeb19528071e4bc9650f28b5ad0e22fe83cbddde77d8
- manifest_entries_that_change, 3. outputs/session-00c/etf-manifest.csv; outputs/session-00e/manifest-truncated.csv; outputs/session-10/synthetics-manifest.csv
- prior_sessions_whose_integrity_check_would_not_reproduce, 2. session-19_5; session-27. Each verified 339 hashed inputs against the manifests and each would fail on the repaired file until its manifest is rewritten too
- the_holdout_has_already_been_read, 1. the repair would change an input after the single read the study's design permits, so the holdout figures would no longer be the ones the frozen record produced
- measured_effect_on_the_holdout, 0.0. SOXS carries zero weight across 2026-05-18 to 2026-06-05, so the repaired series changes no holdout return through the position path

**Option two, disclose unrepaired.**

- impact_bound, -0.041841805663843774. the cumulative contribution of every flagged session in the window, which bounds the whole class rather than the one instance
- known_defective_series_remains, 1. SOXS stays inside the study with a session the record cannot explain
- no_hash_changes, 1. 

**Option three, register the defect and add a permanent check.**

- what_implementing_it_involves, one script and one call site. the screen is scripts/s30_phaseB.py section B1, which reads src/schedule.py for the registered multiple and a frozen proxy for the underlying and compares the tracking residual against a fixed tolerance. Lifting it into a standalone module and calling it beside scripts/s195_verify_inputs.py is the whole of the work
- where_it_would_sit, beside the input-integrity check. scripts/s195_verify_inputs.py runs as a precondition in every session that measures. The implied-multiple screen answers a question the hash check cannot, being whether a series the hash confirms unchanged is also internally consistent with its own registered terms
- no_hash_changes, 1. 
- cost_per_session_seconds, . the sweep screened 43925 instrument-sessions in this session inside the same environment build every measuring session already performs, so the marginal cost is the screen itself rather than a new environment build

**The measured facts bearing on the choice.**

- breaks_found  2. SOXS 2026-05-26; SVXY 2018-02-06
- SVXY_2018-02-06_is_a_proxy_limitation  1. it is classified a break by the conjunction of the two screens while the underlying event is the February 2018 volatility spike. The frozen constant-maturity thirty-day series understates a front-month move, so the volat
- the_only_unexplained_break  SOXS 2026-05-26. the residual reads -0.8113452842932015 against a registered multiple of -3.0 and an SMH return of 0.04480151130636223, with no corporate action in the frozen record
- cumulative_flagged_contribution holdout -0.041841805663843774. against the window's arithmetic return sum of 3.4218690114239116, a share of 0.012227763694096672
- instruments_material holdout 0. none. Materiality was fixed at 5 percent of the window's arithmetic return sum before the flags were seen
- cumulative_flagged_contribution primary 0.6690641978635289. against the window's arithmetic return sum of 5.284814143474101, a share of 0.1266012729491568
- instruments_material primary 1. UVXY
- contaminated_sessions_coinciding_with_a_firing  0. 
- gate_B_verdict  PROCEED. the gate as the scaffold states it, being a break in an instrument contributing materially. no break sits in a material instrument and no contaminated indicator session coincides with a terminal firing, so phases C throu

**the choice is a research decision and this session records the three options with their measured consequences without adopting any.**

### C2, session 28's G3 restated on one convention at a time

| window | convention | range | mover |
|---|---|---|---|
| holdout | naive | 1.4608187196166473 to 1.7121151693407555 | 2023 |
| holdout | lo | 2.372321248555297 to 3.5010323864321666 | 2024 |
| primary | naive | 1.0224291150162947 to 1.1763811969058335 | 2012 |
| primary | lo | 1.2947908486900495 to 1.6185369513800767 | 2020 |

session 28's G3 compared the holdout's naive range of 1.4608187196166473 to 1.7121151693407555 against the primary window's Lo range of 1.287076427656795 to 1.6183359759194622, which are different conventions. Both windows are restated on each convention above. outputs/session-28/REPORT.md is not edited and the correction stands here.

each estimate here removes the calendar year's sessions from the committed return series. The primary-window Lo range session 28 quoted, being 1.287076427656795 to 1.6183359759194622, comes from session 22's leave-one-out REBUILD at outputs/session-22/rebuilt/leave-one-out.csv, which re-ran the strategy with the year dropped. The two constructions are not the same quantity, which is a second reason the session 28 comparison does not hold.

## Phase D, the holdout nulls

the module's definitions are executed up to its own driver loop, so the constructions are the pre-registered ones rather than rewritten. the session 22 seed convention, unchanged. scripts/s14_nulls.py sets RNG = np.random.default_rng(20260818) at module level, at 10000 replications.

| null | metric | exceedances | p value | percentile | null mean | null sd |
|---|---|---|---|---|---|---|
| timing_shuffle_block_bootstrap | ann_return | 4 of 10000 | 0.0004 | 99.96000000000001 | -0.015298422789583321 | 0.1755550014452398 |
| timing_shuffle_block_bootstrap | sharpe_naive | 0 of 10000 | 0.0 | 100.0 | 0.10183682433124347 | 0.35803030824219095 |
| timing_shuffle_block_bootstrap | sharpe_lo | 1 of 10000 | 0.0001 | 99.99 | 0.14381138320236322 | 0.48410021216550614 |
| turnover_matched_switching | ann_return | 3 of 10000 | 0.0003 | 99.97 | -0.02028991086005031 | 0.16651426880136763 |
| turnover_matched_switching | sharpe_naive | 0 of 10000 | 0.0 | 100.0 | 0.061021420651143424 | 0.37172661395421025 |
| turnover_matched_switching | sharpe_lo | 2 of 10000 | 0.0002 | 99.98 | 0.09669225552628022 | 0.4947430625199215 |

**Both nulls are centred near zero on annualised return**, so the strategy sits above a null centred at zero rather than above a high one.

scripts/s14_nulls.py make_stats evaluates on r[1:], so the statistic runs on 1264 sessions rather than 1265. That is the pre-registered construction and it is why the observed naive Sharpe here reads 1.6195086580237787 against the 1.637799226672021 at outputs/session-27/holdout-ladder.csv, and the annualised return 0.8152169801601323 against 0.8287111594113898. The null and the observed value are computed the same way, so the exceedance counts are internally consistent.

## Phase E, the multi-factor decomposition

| factor | instrument | present | source |
|---|---|---|---|
| equity_market | QQQ | 1 | the open-to-open panel built from the loaded universe |
| semiconductor | SMH | 1 | the open-to-open panel built from the loaded universe |
| biotechnology | XBI | 1 | frozen input at data/raw/etf, open-to-open built with the loader's own adjustment ratio |
| long_treasury | TLT | 1 | the open-to-open panel built from the loaded universe |
| volatility | UVXY | 1 | the open-to-open panel built from the loaded universe |

matching the designated cell. A close-to-close factor set correlates only 0.2704559414562822 with the traded open-to-open QQQ line and would not span the strategy's own returns.

| entering factor | window | R-squared | incremental | alpha | t |
|---|---|---|---|---|---|
| equity_market | holdout | 0.12086490377356474 | 0.12086490377356474 | 0.5637935306553864 | 3.491895761576768 |
| semiconductor | holdout | 0.1978242491462059 | 0.07695934537264115 | 0.4660932272045664 | 3.0581940351401493 |
| biotechnology | holdout | 0.20317677390570643 | 0.005352524759500543 | 0.46219954696765186 | 3.0765864003855765 |
| long_treasury | holdout | 0.20318004248131194 | 3.268575605508417e-06 | 0.46166995721092513 | 3.013313498512811 |
| volatility | holdout | 0.21044365972605372 | 0.007263617244741782 | 0.45868406085120844 | 2.9859793219153783 |
| equity_market | primary | 0.1847796714444918 | 0.1847796714444918 | 0.2903836469464326 | 2.3788427467432167 |
| semiconductor | primary | 0.18666416081314252 | 0.0018844893686507103 | 0.28679912786493617 | 2.3439941709624548 |
| biotechnology | primary | 0.18742480280759222 | 0.0007606419944496956 | 0.28579607372994276 | 2.3372654160868453 |
| long_treasury | primary | 0.18904486398399978 | 0.0016200611764075612 | 0.2703489358642575 | 2.2299201575492567 |
| volatility | primary | 0.2254662179646324 | 0.03642135398063262 | 0.28536068219605043 | 2.429602755645417 |

| loading | holdout | primary | holdout variance inflation |
|---|---|---|---|
| equity_market | -0.3998086287867097 | 1.4175774214644519 | 7.35171925889059 |
| semiconductor | 0.6608610878426954 | 0.21895808860931762 | 5.332198903158704 |
| biotechnology | -0.13726090874524807 | -0.0044012049738858675 | 1.7114902693270648 |
| long_treasury | 0.03272199138520437 | 0.009782273827371834 | 1.0375762344452537 |
| volatility | -0.04604630228496218 | 0.11182061241329179 | 2.3535503316832704 |

**Semiconductor absorbs almost all of what is absorbed**, its incremental R-squared over the holdout being 0.07695934537264115 against the three that follow it. **The alpha survives**, the single-factor annualised alpha 0.5637941837318013 against the multi-factor 0.45868406085120844. A multi-factor alpha materially below the single-factor figure means the single-factor figure was measuring sector exposure the benchmark omits, and an alpha that survives means it was not.

The multi-factor residual carries a naive Sharpe of 1.3117491651976525 against the single-factor residual's 1.527991674661622.

## Phase F, interval estimates

The contention check passed at a one-minute load of 4.12 against a threshold of 16. the Newey-West lag 8.11 already fixes for this study's serial dependence, so the bootstrap carries the same dependence horizon the register already records rather than a second one chosen here. Block lengths are geometric with that mean, being the stationary bootstrap of Politis and Romano, at 10000 replications on seed 20260823. The pass ran in 20.867775917053223 seconds against a 1800.0 second limit at a peak resident 0.198967296 GB against a 3.0 GB ceiling.

| quantity | window | point | 5th | 50th | 95th | bootstrap sd | iid standard error |
|---|---|---|---|---|---|---|---|
| naive_sharpe | holdout | 1.637799226672021 | 0.9929195170218649 | 1.637792307531051 | 2.2821600447939803 | 0.390077789607612 | 0.04302029260529093 |
| lo_sharpe | holdout | 2.758522765821501 | 1.1865866798515843 | 2.2378989939127667 | 3.8601197003586423 | 0.8373252035736385 | none |
| ann_return | holdout | 0.7621310929144585 | 0.37209994356077475 | 0.7584017793440334 | 1.2380172185585112 | 0.2656259460419004 | 0.01106435563524277 |
| gap_vs_buy_hold_QQQ | holdout | 1.0477912527059852 | 0.3284274858286137 | 1.0247093373760472 | 1.777935616024335 | 0.44043353049102396 | none |
| gap_vs_matched_exposure | holdout | 1.0813672791419497 | 0.3669357162610955 | 1.0567352860182369 | 1.815241771965525 | 0.4399619391314106 | none |
| single_factor_alpha | holdout | 0.5637944783875491 | 0.291362473531032 | 0.5495013211291294 | 0.817442953711603 | 0.15949723786621764 | none |
| multi_factor_alpha | holdout | 0.458684966492575 | 0.20140576122592446 | 0.45375245003762493 | 0.7162496447883718 | 0.15540045300756433 | none |
| naive_sharpe | primary | 1.0910863648060856 | 0.6251134091230913 | 1.0985147793858503 | 1.56408605941694 | 0.283510258422312 | 0.025403178773557585 |
| lo_sharpe | primary | 1.3817013060245 | 0.7420445103469738 | 1.3402645622784468 | 2.145423686927412 | 0.4332428277665335 | none |
| ann_return | primary | 0.5126738106139874 | 0.2056760530903768 | 0.5148980494423844 | 0.8892723189716257 | 0.20922488020270802 | 0.009819591151366538 |
| gap_vs_buy_hold_QQQ | primary | -0.0650226373237004 | -0.54012012773405 | -0.07073011574586163 | 0.3840804971488868 | 0.2823512789348429 | none |
| gap_vs_matched_exposure | primary | -0.033029624510285016 | -0.4959158144572925 | -0.035488947539688454 | 0.4060431952792486 | 0.27739816969392445 | none |
| single_factor_alpha | primary | 0.2887442018017539 | 0.09837771841081142 | 0.29041761295579915 | 0.48924323124014135 | 0.1195172320194636 | none |

**The holdout gap against buy-and-hold QQQ excludes zero at the 5th percentile**, the 5th percentile reads 0.3284274858286137 against a point estimate of 1.0477912527059852. The primary-window gap does not.

every statistic here is computed on the excess return series, so the annualised return reported below is an annualised EXCESS return. That is why the holdout point estimate reads lower than the 0.8287111594113898 at outputs/session-27/holdout-ladder.csv and the primary one lower than 0.5218447451814521, both of which are total annualised returns. The interval and the point estimate are computed the same way, so the interval is internally consistent.

## Phase G, the NAV sensitivity

The contention check passed at a one-minute load of 2.4 against 16. a curve axis rather than a grid axis, so varying it is a recorded sensitivity and not a new degree of freedom. The canonical starting NAV is unchanged.

### G1, the capacity curve

| starting NAV | annualised return | naive Sharpe | Lo-corrected | turnover | events per session | mean trade share of NAV | cap-binding share | rank |
|---|---|---|---|---|---|---|---|---|
| 1000000.0 | 0.8287111594113898 | 1.637799226672021 | 2.7585227658215015 | 21.02620648507965 | 0.45296442687747035 | 0.4259900699427347 | 0.9406631762652705 | 2 of 12 |
| 10000000.0 | 0.6113253896674531 | 1.470029407714543 | 2.41045082511403 | 15.484416968429413 | 0.45296442687747035 | 0.31205710318865104 | 0.9633507853403142 | 3 of 12 |
| 51671728.47473126 | 0.5133218074573589 | 1.3545290711149274 | 2.4058099147729357 | 14.024284395194687 | 0.45296442687747035 | 0.2755487781991789 | 0.9755671902268761 | 4 of 12 |
| 200000000.0 | 0.38313068677513873 | 1.1988554425602465 | 2.516363461850663 | 11.888076570503655 | 0.45296442687747035 | 0.22537530106405607 | 0.9930191972076788 | 4 of 12 |
| 1028029775.2491124 | 0.20644199149770004 | 0.9817333726959366 | 2.2424965373708323 | 7.617929370545249 | 0.45296442687747035 | 0.1370788555032445 | 1.0 | 4 of 12 |

**Performance degrades smoothly**, the largest adjacent step being -0.21712206986430982 and the curve monotone in NAV. The cap-binding share first exceeds 0.75 at a starting NAV of 1000000.0 and 0.90 at 1000000.0, so throttling is not something the holdout introduced.

### G2, NAV reset at the boundary

| quantity | reset to the study anchor | inherited |
|---|---|---|
| ann_return | 1.092999588869573 | 0.8287111594113898 |
| sharpe_naive | 1.642191290482138 | 1.637799226672021 |
| sharpe_lo | 3.9839230017945937 | 2.7585227658215015 |
| ann_turnover | 41.08922178480395 | 21.02620648507965 |
| eff_mean | 1.3018299643734321 | 0.9681564510351294 |
| eff_sd | 1.3873664557178833 | 1.1784430216279307 |
| cap_binding_share | 0.2949389179755672 | 0.9406631762652705 |
| rank_naive | 2 | 2 |

the reset runs the holdout as its own account beginning at the boundary, so the book does not carry the primary window's compounding into it. The signal rows are unchanged.

### G3, cap binding by calendar year

| year | cap-binding share | events | NAV at year end | window |
|---|---|---|---|---|
| 2011 | 0.34285714285714286 | 35 | 621997.2982369242 | primary window |
| 2012 | 0.18811881188118812 | 101 | 759389.7268543746 | primary window |
| 2013 | 0.29292929292929293 | 99 | 1208350.425949178 | primary window |
| 2014 | 0.43617021276595747 | 94 | 2132506.0166284395 | primary window |
| 2015 | 0.5316455696202531 | 79 | 2886293.0024354327 | primary window |
| 2016 | 0.7314814814814815 | 108 | 3310123.885374278 | primary window |
| 2017 | 0.7452830188679245 | 106 | 4165953.019187809 | primary window |
| 2018 | 0.4796747967479675 | 123 | 7768922.743162607 | primary window |
| 2019 | 0.5384615384615384 | 104 | 13780512.568725497 | primary window |
| 2020 | 0.33695652173913043 | 92 | 35247996.93151197 | primary window |
| 2021 | 0.8631578947368421 | 95 | 68275012.70408444 | primary window |
| 2022 | 0.7181818181818181 | 110 | 132107682.82230437 | holdout |
| 2023 | 1.0 | 106 | 299980546.5266878 | holdout |
| 2024 | 1.0 | 117 | 469774136.5481864 | holdout |
| 2025 | 0.9920634920634921 | 126 | 763165443.1849234 | holdout |
| 2026 | 1.0 | 70 | 1028029775.2491124 | holdout |

Binding first exceeds 0.75 in 2021 and 0.90 in 2023.

### G4, the cost sweep at fixed NAV

| round-turn cost, bp | naive Sharpe at fixed NAV | session 28 coupled |
|---|---|---|
| 0 | 1.361772196136466 | 1.6315236073244241 |
| 5 | 1.3572952194497587 | 1.627837987070995 |
| 10 | 1.3517828312970106 | 1.6217530831644835 |
| 20 | 1.34067976833887 | 1.6177324353366955 |
| 35 | 1.326614750697517 | 1.556539469995808 |
| 50 | 1.2921156303896475 | 1.4354803238074518 |

the scaffold asks whether a non-monotonicity disappears once NAV is fixed. On the naive Sharpe session 28's coupled sweep is already monotone decreasing, so there is none to disappear. What was non-monotone there is the RANK, reading 3,2,2,2,2,2 across the six levels, which moves from 3 at zero basis points to 2 at every higher level.

## Phase H, instrument attribution

| instrument | contribution | variance share | own annualised volatility | correlation with buy-and-hold QQQ | k equal to zero |
|---|---|---|---|---|---|
| SOXL | 1.1440491386220595 | 0.3689889347815891 | 1.1301826537122164 | 0.8794997583815428 | 0 |
| TQQQ | 1.132574376644474 | 0.37415308536609504 | 0.6909290585037473 | 0.9994555879477693 | 0 |
| SQQQ | 0.5631314688171576 | 0.2097861092537085 | 0.6947690998858094 | -0.9980824359764943 | 0 |
| UVXY | 0.2487907258034977 | 0.011656935941652732 | 1.1174425892294084 | -0.7434127916963604 | 1 |
| TECL | 0.15267227598551386 | 0.029476849237394524 | 0.7863345420380556 | 0.9671694696932991 | 0 |
| LABU | 0.10753916493196276 | 0.002901316805631242 | 0.9484157529789167 | 0.6284671312115191 | 0 |
| SOXS | 0.054546596076858606 | -0.0051727144760300965 | 1.2182943226135265 | -0.8330526289483813 | 0 |
| SVXY | 0.05118509207657487 | 0.0061097847752686705 | 0.3615439068933997 | 0.7560108578233581 | 1 |
| QQQ | 0.04233199229832978 | 0.004556698871029031 | 0.23008188522122852 | 0.9999999999723108 | 0 |
| QLD | 0.038646410616101724 | -0.003263814874478974 | 0.4613613191352292 | 0.9997850825412978 | 0 |

**The k equal to zero instruments are BTAL, SVXY, UVXY. Register 2.15 carries k equal to zero for the volatility instruments and BTAL carries no multiple at all, being an anti-beta long and short strategy** They contribute 0.3004288148969315 of holdout return and 0.017772126937489096 of holdout variance, against 2.260897261407411 and 0.44765819686400177 over the primary window.

| exposure | holdout | primary |
|---|---|---|
| mean_at_register_k | 0.9681564510351294 | 1.7769723457408557 |
| mean_at_illustrative_k_1 | 0.9734733792725769 | 1.6920818243411098 |
| difference | 0.00531692823744756 | -0.08489052139974596 |

stated before computing. Register 2.15 carries k equal to zero for the volatility instruments and that is unchanged. A value of one is the smallest non-zero choice and is used only to show how far the exposure figure moves, so it is illustrative rather than adopted. the strategy's own realised volatility over buy-and-hold QQQ's across the holdout, against a mean effective exposure of 0.9681564510351294. The gap between the two is what the k convention bears on.

## What each finding is

| finding | what acting on it would be |
|---|---|
| the SOXS 2026-05-26 break | a correctness repair if option one is taken, documentation if option two, a specification change if option three |
| the split column carrying three discontinuities it does not record | documentation of the column's false-negative rate across this study's own instruments |
| the gate's first implementation testing materiality alone | a correctness repair, applied at 9.84 |
| the holdout null exceedance counts | documentation |
| the multi-factor alpha surviving | documentation |
| the factor set needing the open-to-open convention | a correctness repair, applied inside phase E before any figure was reported |
| the interval estimates | documentation, and a specification change if the paper adopts intervals in place of point estimates |
| the holdout result being capacity-bounded | documentation |
| session 28's G3 convention mismatch | a correctness repair, applied at 9.91 in the register rather than by editing that report |
| the k convention's small effect on the exposure figure | documentation |

**No recommendation is made on any of them.**

## What remains before the paper

**The disposition at 9.85 is the one open decision and it is a research decision rather than a measurement.** Every quantity on the phase A list is computed and emitted, and no phase was skipped.

S equal to 48 of the B1 re-emission remains open at 9.48 and sets neither endpoint of any quoted range, and the corrected degradation null remains unrun at 9.46 with its slope withdrawn at 9.35, so neither is load-bearing. Seven claims bear on the holdout and were not evaluated at 9.68, and whether the holdout counterparts this session and session 28 produced are turned into evaluations against the frozen claims is a decision that has not been taken.

What remains is writing.

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count above the limit is 0.

| reading | before the commit | expected delta |
|---|---|---|
| working tree, KiB | 833064 | +0 |
| git directory, KiB | 208760 | +344 or less |
| free space, GiB | 16.99 | 0.00 to -0.01 |

The commit touches 24 files totalling 568843 bytes on disk, of which 22 files and 352686 bytes are new. **Nothing is read after the commit**, under 9.62.

## Register

9.82 the pre-registration and the closed quantity list. 9.83 the class sweep. 9.84 gate B with the first implementation corrected. 9.85 the disposition, open. 9.86 the holdout nulls. 9.87 the multi-factor decomposition. 9.88 the interval estimates. 9.89 the NAV sensitivity. 9.90 the instrument attribution. 9.91 the correction to session 28's G3.

## Artifacts

- `outputs/session-30/preregistration.csv`
- `outputs/session-30/corporate-action-sweep.csv`
- `outputs/session-30/disposition.csv`
- `outputs/session-30/holdout-nulls.csv`
- `outputs/session-30/multi-factor.csv`
- `outputs/session-30/bootstrap-intervals.csv`
- `outputs/session-30/nav-sensitivity.csv`
- `outputs/session-30/instrument-attribution.csv`
- `outputs/session-30/size.csv`

**No figure is drawn, since the cap at 9.60 is reached.**

