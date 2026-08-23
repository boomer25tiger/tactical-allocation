- **9.70 the descriptive-decomposition ruling and the session 28 pre-registration
  (session 28, 2026-08-23), written BEFORE any measurement in that session ran.**

  **The distinction.** docs/HOLDOUT-PREDICTION.md states that the holdout is read once.
  Re-running specifications against the holdout would destroy the read. Describing a
  result already committed changes nothing. **Descriptive decomposition of the committed
  holdout result is permitted. Selection against the holdout is not.** No canonical value
  moves on any holdout observation, no specification is chosen on holdout performance,
  and the frozen claim set is not amended.

  **The enumerated list**, complete at the time of writing and closed, so a quantity not
  on it is not added later in the session. Phase B reads the committed ladder without a
  pass. Phase C re-runs the Lo permutation null at holdout sample length, needing no
  holdout data. Phase D runs one deterministic decomposition pass over the holdout,
  persisting the per-session sleeve dictionaries session 27 phase C did not. Phase E
  splits that pass by calendar year. Phase F sweeps cost over the holdout. Phase G runs
  the lookahead test, the concentration figures, leave-one-year-out and rolling
  stability. Phase H mirrors session 21's beta decomposition. Phase I reconciles. The
  full enumeration is outputs/session-28/preregistration.csv.

  **Two measurements vary a specification and both are recorded under 9.10 as disclosed
  post-hoc sensitivities.** The phase F cost sweep is motivated by the primary-window
  attribution of the shortfall to cost of carry at an annualised turnover of
  37.87437898045862 against a holdout figure of 21.026206485079. The phase G1 lag shift
  is motivated by the register's corrections list item 12 recording that no dedicated
  lookahead test has run anywhere in the project. **Neither can change the canonical
  whatever it returns**, since the cost model and the canonical one-session fill lag are
  both fixed and each measurement is reported as a sensitivity rather than as a choice.

- **9.71 the dedicated lookahead test, RUN (session 28, 2026-08-23), closing the gap
  the corrections list item 12 records.** Recorded under 9.10 at 9.70 as a disclosed
  post-hoc sensitivity. **The canonical fill lag stays at one session.**

  | window | fill lag | annualised return | naive Sharpe | Lo-corrected Sharpe | ladder rank |
  |---|---|---|---|---|---|
  | primary | 1 | 0.5218447451814521 | 1.0910863648060856 | 1.3817013060244996 | 6 of 12 |
  | primary | 2 | 0.3150488651993313 | 0.7836795580531645 | 0.7381523120792618 | 7 of 12 |
  | holdout | 1 | 0.8287111594113898 | 1.637799226672021 | 2.7585227658215015 | 2 of 12 |
  | holdout | 2 | 0.4284098105559164 | 0.9301170365074822 | 1.8044351487441768 | 2 of 12 |

  **The rank survives and the level does not.** Under one additional session of lag the
  holdout rank holds at 2 of 12 while the annualised return falls by
  0.4003013488554734 and the naive Sharpe by 0.7076821901645387. The primary window
  moves from 6 to 7 with the return falling by 0.2067958799821208. An edge which
  disappears under one session of additional lag is consistent with the signal using
  information not available at execution time, and an edge that survives is not. Stated
  as measured and not further interpreted.

  **A negative shift is NOT computable without forward information and was not run.** A
  fill lag of zero fills at the same session's open under the open-to-open convention,
  which precedes the close the signal was evaluated at, so it would trade on information
  the signal could not yet carry.

  **Corrections item 12 does not reproduce on the designated cell and is
  convention-specific.** Item 12 records annualised return improving under one extra
  session of lag while the Lo-corrected Sharpe degrades. On the designated open-to-open
  cell BOTH degrade. The close-to-close figures item 12 rests on, at
  outputs/session-15/lag-anomaly.csv, read 0.2971065884533939 at one session against
  0.4723877298801684 at two, where the return does improve. **Item 12's finding holds
  close-to-close and not open-to-open.**

- **9.72 the Lo estimator at holdout sample length (session 28, 2026-08-23).** The
  session 20 D1 permutation null re-run at n equal to 1265 with q equal to 252 at 300
  draws on the same seed 20260820, so the only difference from the primary-window null
  is the sample.

  **The holdout Lo factor of 1.6842862793547475 sits INSIDE its own null**, whose mean
  is 1.1936683522118854 and whose 95th percentile is 1.8097895567618085, against the
  session 20 figures at n equal to 2472 of 1.1129 and 1.4783. The observed factor sits
  1.527796336289892 standard deviations above the null mean. **10 of 12 ladder rows sit
  inside their own nulls at holdout length**, against 9 of 12 at primary length.

  **The Lo-corrected rank of 1 of 12 does not survive the q sweep.** The strategy ranks
  2 of 12 at q equal to 1, 5, 21, 63 and 126, and 1 of 12 only at q equal to 252, so the
  rank of 1 occurs at a single value of an unregistered parameter. q over n rose from
  252 over 2472 to 252 over 1265, and the null widened accordingly.

- **9.73 the turnover mechanism, resolved as a CAPACITY effect (session 28,
  2026-08-23).** Annualised turnover fell from 37.87437898045862 to 21.026206485079, a
  fall of 0.444843531403445.

  **The behaviour did not change and the book grew.** Rebalancing events per session
  ROSE from 0.40129449838187703 to 0.45296442687747035, so the strategy traded more
  often rather than less. The mean trade value as a share of NAV fell from
  0.7668753781235466 to 0.4259900699427347. **The participation cap bound on
  0.4909274193548387 of primary-window rebalancing events and on 0.9406631762652705 of
  holdout events.** NAV ran from 816441.3464029437 to 49668246.28810794 across the
  primary window and from 51671728.47473126 to 1028029775.2491124 across the holdout.

  **The figures support the capacity reading rather than the behavioural one**, since a
  larger book binds the 5 percent participation cap on nearly every transition and
  therefore trades a smaller share of NAV per event while transitioning more often.

- **9.74 the sleeve attribution, the year split and the concentration figures (session
  28, 2026-08-23).**

  **Sleeve attribution**, arithmetic sums of the lagged portfolio weight times the
  realised return. Holdout T10 1.6408333525813386, T11 1.7840150264456724, S2
  0.9318151458475786, S3 0.851150147828876. Primary window T10 1.4028996195526637, T11
  1.7166810512825552, S2 2.035524487757279, S3 2.2412534538458315.

  **Instrument attribution.** TQQQ is the largest positive contributor in both windows,
  at 0.951556253095966 across the holdout and 2.152772082139501 across the primary
  window. **The short sleeve flips sign**, contributing 0.31605803257245435 across the
  holdout against -0.9887171219871639 across the primary window. The largest negative
  holdout contributor is LABU at -0.051504161994962085 and the largest negative
  primary-window contributor is SQQQ at -0.7676845366846142.

  **Mean effective exposure fell from 1.7769723457408557 to 0.9681564510351294**, with
  the share of sessions above 1.7 falling from 0.6812297734627831 to
  0.31778656126482213. The primary-window figure reproduces the committed value at
  outputs/session-16/exposure-reconciliation.csv exactly.

  **The year split shows the outperformance SPREAD rather than concentrated.** All 6
  calendar years in the span carry a positive arithmetic gap against buy-and-hold QQQ,
  totalling 2.5540068916506895, and 2022 carries the largest single-year share at
  1.1362267456041104, being 0.444880 of the total. The strategy's naive-Sharpe rank by
  year runs 3, 3, 2, 4, 4 and 3 of 12.

  **2022 separately.** The strategy returns 0.7791325142954327 arithmetically against
  buy-and-hold QQQ's -0.3570942313086777, with the short sleeve contributing
  0.5495980771396922 across the 251 sessions.

  **Concentration.** The best 25 holdout sessions carry 0.6007601013561109 of the
  arithmetic return against 0.6585596295464436 in the primary window, and 20 sessions
  account for half the holdout return against 18 in the primary window. Removing the
  best 10 sessions takes the holdout naive Sharpe from 1.637799226672021 to
  1.216555933902445 and the primary-window figure from 1.0910863648060856 to
  0.7910800073030204.

- **9.75 terminals firing for the first time inside the holdout (session 28,
  2026-08-23).** **Two T11 terminals executed for the first time inside the sealed
  span**, being the BTAL and PSQ pairing and the BTAL and QQQ pairing, each at half
  weight. **One terminal fired in the primary window and never in the holdout**, being
  the T11 QQQ and SQQQ pairing. A code path executing for the first time inside a
  holdout is recorded here rather than left implicit. Source
  outputs/session-28/holdout-decomposition.csv.

- **9.76 two premises the prediction carried that the measurement does not support
  (session 28, 2026-08-23).** Both belong in the paper's account of what was predicted
  against what happened. **docs/HOLDOUT-PREDICTION.md is not edited**, since it is
  frozen at 9.64.

  **The SQQQ and TLT correlation.** P3 part one rested on the pair being negatively
  correlated in the primary window and predicted a flip to positive. Session 27 measured
  the direct pair at 0.16448233204452256 over the primary window, so it was already
  positive there, and at -0.07884210926185957 over the holdout, so the realised move was
  from positive to negative. The committed -0.5618926986740371 the prediction named is
  the short leg against the rest of its own sleeve rather than the direct pair, which
  the prediction itself flagged.

  **The turnover premise.** P1's mechanism stated that nothing in the holdout reduces
  turnover. Turnover fell by 0.444843531403445, from 37.87437898045862 to
  21.026206485079, so the premise is contradicted by the measurement. The mechanism at
  9.73 is a capacity effect rather than a change in the strategy's behaviour.

- **9.77 the two disclosed post-hoc sensitivities, BOTH CHANGED NOTHING (session 28,
  2026-08-23), under 9.10 and pre-registered at 9.70.**

  **The cost sweep over the holdout.** Across the pre-registered range read from
  src/config.SLIPPAGE_BASE_GRID_BP, being 0, 5, 10, 20, 35 and 50 basis points round
  turn, the strategy's naive Sharpe runs from 1.6315236073244241 at 0 basis points to
  1.4354803238074518 at 50, and its rank runs 3, 2, 2, 2, 2 and 2 of 12. **No crossing
  falls inside the swept range** on either convention, so the round-turn cost at which
  the rank falls to sixth, to eighth, or below buy-and-hold QQQ is an extrapolation in
  every case. Over the primary window 10 of 22 crossings fall inside the same range.

  **The lag shift.** Recorded at 9.71.

  **Neither selected a specification and neither moved any canonical value.** The cost
  model, the canonical one-session fill lag, the primary window at 2011-10-04 and the
  holdout boundary at 2021-08-01 are all unchanged.

- **9.78 a correction to session 27's P4 effective-exposure figures (session 28,
  2026-08-23).** Session 27 phase D read the leverage multiple from the REALIZED panel,
  where scripts/s13_backtest.py load_arm_panel sets it to NaN for every levered fund, so
  its effective-exposure figures are gross portfolio weights rather than
  leverage-adjusted exposure.

  Session 28 reads the multiple from the synthetic panel as scripts/s16_step3.py does,
  and **reproduces the committed primary-window canonical figure of 1.7769723457408557
  exactly**, which the realized-panel reading does not. The P4 interval's mean effective
  exposure reads 1.759214343454632 rather than the 0.9277520939003893 session 27
  reported. **outputs/session-27/REPORT.md is not edited** and the correction stands
  here. The P4 guard is unaffected, since P4 carries no verdict either way.

- **The beta decomposition over the holdout (session 28, 2026-08-23), recorded under
  9.74.** Static beta 0.5946975667115855 against the primary window's 1.108672858112171,
  annualised alpha 0.5637941837318013 against 0.28874420661558875, R-squared
  0.12086286064363738 against 0.18679426851145753, and the Newey-West t at the 8.11 lag
  of 21 reading 3.4918970688555846 against 2.364283243646891. The beta-hedged residual
  carries a naive Sharpe of 1.527991674661622 against 0.6558362612960221.

  **The timing component is positive at all four windows over the holdout and does not
  change sign**, reading 0.12727498849055022 at 60 sessions down to 0.051111599234742566
  at 504, against a primary-window range of -0.0077512681113622505 to
  0.027230151692897046 with a sign change at 252. **This is a different result from the
  primary window's**, where timing contributed essentially nothing at any window. The
  exposure-matched line does not beat the strategy on the naive Sharpe at any of the
  four windows, reading between 0.5654 and 0.7843 against 1.637799226672021.
