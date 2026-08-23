# Session 28, the holdout decomposition

2026-08-23. Ten phases. One commit, at phase J. No specification is selected on any holdout observation and no canonical value moves.

## Opening

**The dedicated lookahead test ran, closing the gap the corrections list item 12 records.** Under one additional session of signal-to-execution lag the holdout annualised return falls from 0.8287111594113898 to 0.4284098105559164 and the naive Sharpe from 1.637799226672021 to 0.9301170365074822, while the ladder rank holds at 2 of 12. Over the primary window the rank moves from 6 to 7. **The rank survives and the level does not.**

**One ladder line beats the strategy on the naive Sharpe over the holdout**, being sleeve_T11_standalone by 0.053051873058643784. The strategy's advantage over buy-and-hold QQQ is return, carrying 5.2570 times its annualised return at 1.7102 times its annualised volatility.

**The holdout Lo factor sits inside its own null.** The observed factor of 1.6842862793547475 lies between the null's 5th and 95th percentiles, whose upper bound is 1.8097895567618085 against the session 20 figure at n equal to 2472 of 1.4783. **The Lo-corrected rank of 1 of 12 occurs at q equal to 252 alone**, the strategy ranking 2 of 12 at every other swept q.

**The outperformance is spread rather than concentrated.** All 6 calendar years in the span carry a positive arithmetic gap against buy-and-hold QQQ, totalling 2.5540068916506895, with 2022 the largest single year at 1.1362267456041104.

## Machine and the positive control

Load average 9.93 one minute, 6.65 five minutes and 6.81 fifteen minutes on eight cores, compressor 2.93 GiB, swap used 13397.19 MB and swap free 938.81 MB.

**The standing positive control passed** at 0.5218447451814521 annualised and 1.3817013060244996 Lo-corrected over 2472 sessions, inside the 5e-07 tolerance stated before comparing. It runs with the truncation default in force at 2021-07-31, so it reads no post-boundary session.

## Phase A, the ruling and the pre-registration

**Permitted.** docs/HOLDOUT-PREDICTION.md states that the holdout is read once. The distinction drawn is between re-running specifications against the holdout, which would destroy the read, and describing a result already committed, which changes nothing. Describing is permitted.

**Not permitted.** no canonical value moves on any holdout observation, no specification is chosen on holdout performance, and the frozen claim set is not amended.

The complete quantity list was written to `outputs/session-28/preregistration.csv` and to the register at 9.70 before any measurement ran, and it is closed, so no quantity outside it was added later.

Two measurements vary a specification and both are recorded under 9.10 as disclosed post-hoc sensitivities, being the phase F cost sweep and the phase G1 lag shift. **Neither can change the canonical whatever it returns.**

## Phase B, the ladder

Read from `outputs/session-27/holdout-ladder.csv` and `outputs/session-20/rebuilt/metrics-full.csv`. No pass ran.

| line | holdout naive | primary naive | holdout Lo | primary Lo | holdout rank | primary rank | move |
|---|---|---|---|---|---|---|---|
| sleeve_T11_standalone | 1.6908510997306647 | 0.8076997809430698 | 2.7247782925407056 | 0.9739130998405515 | 1 | 9 | 8 |
| STRATEGY | 1.637799226672021 | 1.0910863648060856 | 2.7585227658215015 | 1.3817013060244996 | 2 | 6 | 4 |
| sleeve_T10_standalone | 1.5337658933089617 | 0.41344628111495507 | 1.1113265475176035 | 0.5189279758734306 | 3 | 12 | 9 |
| long_legs_only | 1.4186980765107986 | 1.2165434859927253 | 2.6317016722108373 | 1.4695629013667943 | 4 | 1 | -3 |
| sleeve_S2_standalone | 0.9011603129601938 | 1.1969195612756722 | 1.4945981218587112 | 1.327085322938575 | 5 | 2 | -3 |
| sleeve_S3_standalone | 0.8331655729834205 | 1.0723144437609193 | 1.0621260466751712 | 1.1958839875578076 | 6 | 8 | 2 |
| vol_targeted_QQQ_matched | 0.6127370762969571 | 1.0785419656409494 | 0.8346302118441822 | 1.4304524548933715 | 7 | 7 | 0 |
| equal_weight_universe | 0.6026665018822145 | 0.5806744766261789 | 0.7363520341847385 | 0.5904389961374447 | 8 | 11 | 3 |
| buy_hold_QQQ | 0.5900079739660359 | 1.156109002129786 | 0.7438002112188974 | 1.8033205072078788 | 9 | 3 | -6 |
| buy_hold_TQQQ | 0.5565614254276027 | 1.1269308726398495 | 0.7020549626450708 | 1.8057440257389181 | 10 | 4 | -6 |
| matched_exposure_levered_QQQ_1.70 | 0.5564319475300712 | 1.1241159893163706 | 0.7020177681359031 | 1.801781584473704 | 11 | 5 | -6 |
| naive_fast_1d_momentum | -0.11299625825558965 | 0.7904119196378823 | -0.10387976457665896 | 1.075592724199963 | 12 | 10 | -2 |

**Buy-and-hold QQQ.** Naive Sharpe 0.5900079739660359 over the holdout against 1.156109002129786 over the primary window, and Lo-corrected 0.7438002112188974 against 1.8033205072078788. It falls from rank 3 to 9. the scaffold names a primary-window naive Sharpe of 1.1699 for this line and the emitted figure is quoted here instead. The scaffold's Lo figure of 1.8033 matches the emitted 1.8033205072078788 to four decimals.

**The matched-exposure line** places 11 of 12 on the naive Sharpe over the holdout against 5 over the primary window.

**The advantage is a return effect.** the strategy carries 5.2570 times buy-and-hold QQQ's annualised return at 1.7102 times its annualised volatility over the holdout, against 2.2594 and 2.5655 over the primary window. The advantage is a higher return carried at a higher volatility rather than a lower volatility, so it is a return effect and not a volatility effect.

## Phase C, the Lo estimator at holdout length

The session 20 D1 permutation null re-run at n equal to 1265 with q equal to 252 at 300 draws on seed 20260820, the same seed session 20 used. q over n rose to 0.1992094861660079.

| quantity | holdout | session 20 at n equal to 2472 |
|---|---|---|
| observed factor | 1.6842862793547475 | 1.2664 |
| null mean | 1.1936683522118854 | 1.1129 |
| null 95th percentile | 1.8097895567618085 | 1.4783 |
| inside its own null | 1 | 1 |

The observed factor sits 1.527796336289892 standard deviations above the null mean. **10 of 12 ladder rows sit inside their own nulls at holdout length**, against 9 of 12 at primary length.

**The strategy's rank across q runs 1 to 2.** q values q1=2 q5=2 q21=2 q63=2 q126=2 q252=1, against a primary-window range of 6 to 7 at 9.37. 8 of 12 rows change rank across the sweep.

The Lo variance turns non-positive at a weighted autocorrelation sum of -126.0. the Lo scale q plus twice the weighted autocorrelation sum turns non-positive at this value. It depends on q alone and not on n, so it is the same threshold the primary window carried.

## Phase D, the decomposition

### Sleeve attribution

| sleeve | holdout | primary window |
|---|---|---|
| T10 | 1.6408333525813386 | 1.4028996195526637 |
| T11 | 1.7840150264456724 | 1.7166810512825552 |
| S2 | 0.9318151458475786 | 2.035524487757279 |
| S3 | 0.851150147828876 | 2.2412534538458315 |

**The short sleeve flips sign**, contributing 0.31605803257245435 across the holdout against -0.9887171219871639 across the primary window. TQQQ is the largest positive contributor in both windows, at 0.951556253095966 and 2.152772082139501. The largest negative contributor is LABU at -0.051504161994962085 over the holdout and SQQQ at -0.7676845366846142 over the primary window.

### Terminals

**2 terminals executed for the first time inside the holdout**, being T11 BTAL=0.5|PSQ=0.5; T11 BTAL=0.5|QQQ=0.5. 1 fired in the primary window and never in the holdout, being T11 QQQ=0.5|SQQQ=0.5.

### Exposure

| quantity | holdout | primary window |
|---|---|---|
| mean | 0.9681564510351294 | 1.7769723457408557 |
| sd | 1.1784430216279307 | 0.9111563758271118 |
| min | -1.958625000762561 | -1.831910320620685 |
| max | 2.848257470714799 | 3.0049021648338914 |
| share_above_1.0 | 0.5296442687747036 | 0.7673948220064725 |
| share_above_1.7 | 0.31778656126482213 | 0.6812297734627831 |

The primary-window mean reproduces the committed 1.7769723457408557 at `outputs/session-16/exposure-reconciliation.csv` exactly.

### Turnover, with the mechanism

| quantity | holdout | primary window |
|---|---|---|
| ann_turnover_committed | 21.026206485079 | 37.87437898045862 |
| rebalancing_events | 573 | 992 |
| rebalancing_events_per_session | 0.45296442687747035 | 0.40129449838187703 |
| mean_trade_value_share_of_nav | 0.4259900699427347 | 0.7668753781235466 |
| transitions_with_the_participation_cap_binding | 539 | 487 |
| cap_binding_share_of_events | 0.9406631762652705 | 0.4909274193548387 |
| nav_at_window_start | 51671728.47473126 | 816441.3464029437 |
| nav_at_window_end | 1028029775.2491124 | 49668246.28810794 |

Turnover fell by 0.444843531403445. **Rebalancing events per session rose**, so the strategy transitioned more often rather than less, while the mean trade value as a share of NAV fell and the participation cap bound on nearly every holdout event. **The figures support the capacity reading**, since a larger book binds the cap on more transitions and trades a smaller share of NAV per event by construction.

### Drawdown

| line | maximum drawdown | peak, trough and duration |
|---|---|---|
| STRATEGY | -0.34468314755389173 | peak 2022-10-13, trough 2023-01-09, 59 sessions from peak to trough, recovered 2023-05-19 |
| buy_hold_QQQ | -0.36694214173860695 | peak 2021-11-22, trough 2022-10-13, 224 sessions from peak to trough, recovered 2023-12-14 |
| matched_exposure_levered_QQQ_1.70 | -0.5751006880169329 | peak 2021-11-22, trough 2022-10-13, 224 sessions from peak to trough, recovered 2024-03-04 |

The strategy's drawdown is shallower than buy-and-hold QQQ's and shallower than the matched-exposure line's.

### Panel source and the return distribution

Every loaded ticker is simultaneously available on 1.0 of holdout sessions against 0.6294498381877023 of primary-window sessions, which reproduces the 0.629 the scaffold names. Restricted to the tickers actually held, both windows read 1.0.

| quantity | holdout | primary window |
|---|---|---|
| n_sessions | 1265 | 2472 |
| daily_mean | 0.0027050347916394556 | 0.0021378697991400086 |
| daily_sd | 0.0247881612877428 | 0.030754976178934808 |
| skewness | 0.00044220578416748354 | 0.4172032530478573 |
| excess_kurtosis | 5.223157724383093 | 8.22583208183826 |

## Phase E, the year split

| year | sessions | annualised return | naive Sharpe | Lo-corrected Sharpe | maximum drawdown | naive rank |
|---|---|---|---|---|---|---|
| 2021 | 107 | 1.1156326016953626 | 1.9776200870416587 | 13.0288211831166 | -0.12261297976716301 | 3 of 12 |
| 2022 | 251 | 0.9400297160446782 | 1.5565253165054413 | 2.999443023101402 | -0.3260389118952054 | 3 of 12 |
| 2023 | 250 | 1.2856742576101032 | 2.6254060122875424 | 4.6553640102793175 | -0.1564943023765475 | 2 of 12 |
| 2024 | 252 | 0.5660153366191458 | 1.3082117505851494 | 2.7434738259100473 | -0.3159729418563342 | 4 of 12 |
| 2025 | 250 | 0.6308553049713606 | 1.3424808918915578 | 3.2004116681137393 | -0.2446771375409038 | 4 of 12 |
| 2026 | 155 | 0.6231483470135881 | 1.3558833998990316 | 5.5358086315762645 | -0.24015061126346082 | 3 of 12 |

| year | arithmetic gap against buy-and-hold QQQ |
|---|---|
| 2021 | 0.2505170645912995 |
| 2022 | 1.1362267456041104 |
| 2023 | 0.40150436289128166 |
| 2024 | 0.26191195326605865 |
| 2025 | 0.3437141195837342 |
| 2026 | 0.16013264571420482 |

**The outperformance is spread.** 6 of 6 years carry a positive gap, totalling 2.5540068916506895, and the largest single year is 2022 at 1.1362267456041104, a share of 0.444880 of the total gap. **One observation over one macro regime remains the principal limitation, and the year split is how it is stated.**

**2022 separately.** The strategy returns 0.7791325142954327 arithmetically against buy-and-hold QQQ's -0.3570942313086777, with the short sleeve contributing 0.5495980771396922 across 251 sessions.

## Phase F, the cost sweep

A disclosed post-hoc sensitivity under 9.10. The range is read from `src/config.SLIPPAGE_BASE_GRID_BP`, read rather than assumed, being [0, 5, 10, 20, 35, 50] basis points round turn. the uniform round-turn sweep replaces the tiered slippage and the opening-auction premium rather than stacking on them, as session 20 pre-registered. Commission Arm S and the participation cap are unchanged.

| round-turn cost, bp | naive Sharpe | Lo-corrected Sharpe | rank on the naive |
|---|---|---|---|
| 0 | 1.6315236073244241 | 2.5373135704115186 | 3 of 12 |
| 5 | 1.627837987070995 | 2.5858374692230535 | 2 of 12 |
| 10 | 1.6217530831644835 | 2.6413537977373887 | 2 of 12 |
| 20 | 1.6177324353366955 | 2.7602479112997704 | 2 of 12 |
| 35 | 1.556539469995808 | 2.6461182448887213 | 2 of 12 |
| 50 | 1.4354803238074518 | 2.4530086719847097 | 2 of 12 |

| crossing | convention | basis points | inside the range |
|---|---|---|---|
| rank_falls_to_6 | sharpe_naive | nan | extrapolation, the rank does not reach the target inside the range |
| rank_falls_to_8 | sharpe_naive | nan | extrapolation, the rank does not reach the target inside the range |
| falls_below_buy_hold_QQQ | sharpe_naive | nan | extrapolation, the strategy leads buy-and-hold QQQ at every swept level |
| rank_falls_to_6 | sharpe_lo | nan | extrapolation, the rank does not reach the target inside the range |
| rank_falls_to_8 | sharpe_lo | nan | extrapolation, the rank does not reach the target inside the range |
| falls_below_buy_hold_QQQ | sharpe_lo | nan | extrapolation, the strategy leads buy-and-hold QQQ at every swept level |

Over the primary window 10 crossings fall inside the same range, of 22 across the eleven lines and both conventions, the rest being extrapolations, at outputs/session-20/rebuilt/cost-sweep-designated.csv and outputs/session-21/reads.csv.

## Phase G, robustness

### G1, the lookahead test

| window | fill lag | annualised return | naive Sharpe | Lo-corrected Sharpe | rank |
|---|---|---|---|---|---|
| primary | 1 | 0.5218447451814521 | 1.0910863648060856 | 1.3817013060244996 | 6 of 12 |
| primary | 2 | 0.3150488651993313 | 0.7836795580531645 | 0.7381523120792618 | 7 of 12 |
| holdout | 1 | 0.8287111594113898 | 1.637799226672021 | 2.7585227658215015 | 2 of 12 |
| holdout | 2 | 0.4284098105559164 | 0.9301170365074822 | 1.8044351487441768 | 2 of 12 |

**The holdout advantage survives one additional session of lag on rank and not on level.** an edge which disappears under one session of additional lag is consistent with the signal using information not available at execution time, while an edge that survives is not. Stated as measured and not further interpreted. The holdout annualised return changes by -0.4003013488554734 and the primary window's by -0.2067958799821208.

**A negative shift is not computable without forward information.** a fill lag of zero fills at the SAME session's open under the open-to-open convention, which precedes the close the signal was evaluated at, so it would trade on information the signal could not yet carry. It is mechanically runnable and is NOT run, since a lookahead test that itself looks ahead measures nothing.

**Corrections item 12 does not reproduce on the designated cell.** item 12 records annualised return improving under one extra session of lag while the Lo-corrected Sharpe degrades. On the designated open-to-open cell over the primary window the return moves from 0.5218447451814521 to 0.3150488651993313 and the Lo-corrected Sharpe from np.float64(1.3817013060244996) to np.float64(0.7381523120792618), so BOTH degrade and the recorded pattern does not reproduce. outputs/session-15/lag-anomaly.csv records close-to-close annualised return 0.2971065884533939 at one session of lag against 0.4723877298801684 at two, with the Lo-corrected Sharpe moving from 0.928624610696173 to 0.8601102920915699. The return improves there, so item 12's pattern holds on the close-to-close convention and not on the designated open-to-open cell.

### G2, concentration

| quantity | holdout | primary window |
|---|---|---|
| share_from_the_best_1_sessions | 0.04187191017347265 | 0.038526964394835404 |
| share_from_the_best_5_sessions | 0.16902815276903652 | 0.17609825102997434 |
| share_from_the_best_10_sessions | 0.29299239950833256 | 0.31762546959463517 |
| share_from_the_best_25_sessions | 0.6007601013561109 | 0.6585596295464436 |
| share_from_the_worst_5_sessions | -0.16718278328923694 | -0.1644559543002491 |
| share_from_the_worst_25_sessions | -0.5790103591885034 | -0.5437970553928859 |
| naive_sharpe_unmodified | 1.637799226672021 | 1.0910863648060856 |
| naive_sharpe_with_the_best_5_removed | 1.4095131731335688 | 0.9323989955534449 |
| naive_sharpe_with_the_best_10_removed | 1.216555933902445 | 0.7910800073030204 |
| sessions_accounting_for_half_the_return | 20 | 18 |

### G3, leave one year out over the holdout

6 estimates. The naive Sharpe range is 1.4608187196166473 to 1.7121151693407555, minimum when 2023 is removed and maximum when 2024 is removed, against the primary window's eleven estimates bounding 1.287076427656795 to 1.6183359759194622 on the Lo-corrected convention at 9.41. The year whose removal moves it most is 2023, moving the naive Sharpe by -0.1769805070553736 from the base 1.637799226672021.

### G4, rolling stability

3486 rolling 252-session windows across the combined span. The minimum is -0.23724927017259576 at 2020-04-13 and the maximum is 3.4173898213134275 at 2024-03-06, with 0.6970740103270223 of windows above 1.0. Split at the boundary, the primary window carries 0.5844214317874831 above 1.0 and the holdout 0.8948616600790514. The series is emitted at `outputs/session-28/rolling-sharpe-series.csv` with the boundary marked.

## Phase H, the beta decomposition

**The positive control passed**, buy-and-hold QQQ regressed on itself returning a beta of 0.9999999999999998 and a daily alpha of 9.754724061761486e-20 inside the 1e-10 tolerance.

| quantity | holdout | primary window |
|---|---|---|
| beta | 0.5946975667115855 | 1.108672858112171 |
| alpha_annualised | 0.5637941837318013 | 0.28874420661558875 |
| r_squared | 0.12086286064363738 | 0.18679426851145753 |
| alpha_t_newey_west | 3.4918970688555846 | 2.364283243646891 |
| residual_ann_return | 0.6412066989548881 |  |
| residual_ann_vol | 0.36897726151332266 |  |
| residual_sharpe_naive | 1.527991674661622 | 0.6558362612960221 |
| residual_sharpe_lo | 1.930075216384835 | 0.8649152595612315 |

| window | beta mean | beta sd | primary sd | timing contribution | primary timing |
|---|---|---|---|---|---|
| 60 | 0.9663019637383276 | 0.9097117526295763 | 1.1646116827038935 | 0.12727498849055022 | 0.011293050910284682 |
| 120 | 0.8880540107328023 | 0.8411148924824693 | 0.6992985332538183 | 0.11621725925748441 | 0.027230151692897046 |
| 252 | 0.8683265704743323 | 0.7564014846176441 | 0.41047564557798377 | 0.07533456901020892 | -0.004075416692355631 |
| 504 | 0.8894077220069633 | 0.6204291853738693 | 0.20922149429810166 | 0.051111599234742566 | -0.0077512681113622505 |

**The timing component is material over the holdout and does not change sign**, reading 0.051111599234742566 to 0.12727498849055022 across the four windows, against a primary-window range of -0.0077512681113622505 to 0.027230151692897046 across the same four windows. The sign-change flag reads 0 and the materiality flag 1, material is recorded when any window's timing contribution exceeds 0.05 annualised in absolute value, against a strategy annualised excess mean of np.float64(0.6445126075841863). The primary-window finding was that timing contributes essentially nothing at any window.

| window | exposure-matched naive Sharpe | beats the strategy |
|---|---|---|
| 60 | 0.6478021636114607 | 0 |
| 120 | 0.7842645892692112 | 0 |
| 252 | 0.7205573215722426 | 0 |
| 504 | 0.5654454773479913 | 0 |

QQQ held at the canonical's own rolling realised beta lagged one session, rebalanced daily, charged the identical cost model. It uses beta estimated from the strategy's own realised returns, so it is a decomposition rather than an ex-ante benchmark.

## Phase I, reconciliation

**I1.** the 0.5127 the scaffold quotes is a geometric annualised rate minus an arithmetic sum over 1265 sessions, so the two terms are not comparably defined and the figure should not be read as a residual annualised return. recomputed with both quantities in the same units the residual reads 0.5257545196845275 against the primary window's 0.5218447451814521, a gap of 0.003909774503075392, which is closer than the 0.5126531268389355 the scaffold's arithmetic produced. Nothing in the construction forces two non-overlapping spans to agree, so the proximity is a coincidence in the sense of being unimplied rather than an artifact of the units mix.

**I2.** The combined window carries 3737 sessions against 3737, 2472 plus 1265, and the session count reconciles. The two spans compounded give 1273.1897941783186 against the combined window's 1273.1897941783204, a relative gap of 1.4286867612850912e-15.

**I3.** 1 quantity disagrees with session 27, being the P4 effective-exposure figures. session 27 read the leverage multiple from the REALIZED panel, where the loader sets it to NaN for every levered fund, so its figure is the gross portfolio weight rather than leverage-adjusted exposure. Session 28 reads it from the synthetic panel as session 16 step 3 does, and reproduces the committed primary-window canonical figure of 1.7769723457408557 exactly, which the realized-panel reading does not. The session 27 figure is the one in error and is corrected here rather than in that report, which is not edited. Session 27 reported 0.9277520939003893 and the corrected figure is 1.759214343454632.

## What each finding is

| finding | what acting on it would be |
|---|---|
| the lookahead test result | documentation, since the canonical fill lag is unchanged and the result is reported whatever it shows |
| corrections item 12 not reproducing on the designated cell | a register decision, applied at 9.71 |
| the holdout Lo factor sitting inside its own null | documentation |
| the Lo rank of 1 of 12 occurring at q equal to 252 alone | documentation |
| the turnover fall being a capacity effect | a register decision, applied at 9.73 |
| two terminals firing first inside the holdout | documentation |
| the two prediction premises the measurement contradicts | documentation, since the prediction is frozen at 9.64 and is not edited |
| session 27's P4 effective-exposure figures | a correctness repair, applied at 9.78 in the register rather than by editing that report |
| the holdout timing component being material and single-signed | documentation |
| the cost sweep showing no crossing inside the swept range | documentation |

**No recommendation is made on any of them.**

## What remains before the paper

**No measurement remains outstanding for the holdout account.** Every quantity on the phase A list is computed and emitted. S equal to 48 of the B1 re-emission remains open at 9.48 and sets neither endpoint of any quoted range, and the corrected degradation null remains unrun at 9.46 with its slope withdrawn at 9.35, so neither is load-bearing.

Seven claims bear on the holdout and were not evaluated at 9.68, being 2, 3, 11, 12, 13, 14 and 15. Claims 11 and 12 now have holdout counterparts from phase H and claim 13 has one from G3, and whether those counterparts are turned into evaluations against the frozen claims is a decision that has not been taken. **No claim in docs/CLAIMS.md is added or amended and docs/HOLDOUT-PREDICTION.md is not edited.**

What remains is writing.

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count above the limit is 0.

| reading | before the commit | expected delta |
|---|---|---|
| working tree, KiB | 831904 | +0 |
| git directory, KiB | 208224 | +754 or less |
| free space, GiB | 17.35 | 0.00 to -0.01 |

The commit touches 33 files totalling 960664 bytes on disk, of which 31 files and 772484 bytes are new. **Nothing is read after the commit**, under 9.62.

## Register

9.70 the ruling and the pre-registration, written before any measurement. 9.71 the lookahead test. 9.72 the Lo estimator at holdout length. 9.73 the turnover mechanism. 9.74 the sleeve attribution, the year split and the concentration figures, with the beta decomposition recorded under it. 9.75 the terminals firing first inside the holdout. 9.76 the two prediction premises. 9.77 the two disclosed sensitivities. 9.78 the correction to session 27's P4 effective-exposure figures.

## Artifacts

- `outputs/session-28/preregistration.csv`
- `outputs/session-28/ladder-comparison.csv`
- `outputs/session-28/lo-holdout-null.csv`
- `outputs/session-28/holdout-decomposition.csv`
- `outputs/session-28/holdout-by-year.csv`
- `outputs/session-28/holdout-cost-sweep.csv`
- `outputs/session-28/robustness.csv`
- `outputs/session-28/rolling-sharpe-series.csv`
- `outputs/session-28/holdout-beta.csv`
- `outputs/session-28/reconciliation.csv`
- `outputs/session-28/size.csv`
- the persisted sleeve dictionaries, being `_sleeve_weights_T10.parquet`, `_sleeve_weights_T11.parquet`, `_sleeve_weights_S2.parquet`, `_sleeve_weights_S3.parquet`, `_signal_rows.parquet`, `_terminals.parquet` and `_effective_exposure.parquet`

**No figure is drawn, since the cap at 9.60 is reached.**

