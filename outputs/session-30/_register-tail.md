- **9.82 the session 30 pre-registration (session 30, 2026-08-23), written BEFORE any
  measurement in that session ran.** The session 28 ruling at 9.70 stands, being that
  describing a committed holdout result is permitted while selecting against it is not.

  **The enumerated list**, complete at the time of writing and closed. Phase B sweeps
  the corporate action class on the implied-multiple screen and runs first, since every
  downstream phase reads price series it screens. Phase C records the disposition and
  restates session 28's G2 on one convention. Phase D runs the holdout nulls. Phase E
  runs the multi-factor decomposition. Phase F runs the block bootstrap. Phase G runs
  the NAV sensitivity. Phase H runs the instrument attribution. The full enumeration is
  outputs/session-30/preregistration.csv.

  **The class sweep's own motivation, recorded first.** Session 29 found a discontinuity
  in SOXS on 2026-05-26 where the close moves from 1159.5 to 62.900001525878906 against
  SMH at 0.04480151130636223, implying a multiple of -21.109834258353413 against a
  registered -3.0, while the frozen record's Stock Splits column reads zero. **A split
  column that misses one corporate action cannot establish the absence of others**, and
  the 50 percent absolute-return threshold that found it catches ratios of 2 or larger
  while levered products split at smaller ratios routinely. The screen that worked is
  the implied-multiple comparison, so the class is swept on that.

  The motivations for phases D through H are carried forward from 9.79 unchanged. **Every
  measurement is a disclosed post-hoc sensitivity under 9.10** and none can change the
  canonical.

  **Gate B was written before the check**, being that a break in an instrument
  contributing materially to either window's return, or a contaminated indicator session
  coinciding with a terminal firing, halts before phase C. **Materiality was defined
  before the flags were seen**, at an absolute cumulative flagged contribution above 5
  percent of the window's arithmetic return sum.

  **No frozen input is repaired, no hashed file is edited and no manifest entry
  changes**, since the disposition is recorded as open.

- **9.83 the corporate action class sweep (session 30, 2026-08-23).** The rule, the
  tolerance and the floor were stated before running and are in
  outputs/session-30/corporate-action-sweep.csv.

  **The rule.** The discriminator is the tracking residual, being the observed return
  less the registered multiple times a frozen proxy for the registered underlying, both
  read from src/schedule.py. RESIDUAL_TOL is 0.05, since a missing split of ratio R
  contributes about one over R minus one to the residual, being -0.0476 at R equal to
  1.05 and -0.1667 at R equal to 1.2, and since that contribution does not shrink as the
  underlying's move grows. The threshold catches ratios at and above about 1.053, well
  below the 2 the session 29 return threshold required. The implied multiple is reported
  as well and is not the discriminator, its denominator being unstable, and it is not
  computed where the underlying's absolute return falls below 0.005, those sessions
  being screened on absolute return at 0.25 instead so none is silently dropped.

  **43925 instrument-sessions screened across 17 held instruments over the full
  combined window, 174 flagged, a selectivity of 0.00396130.** 15006 sessions fell below
  the underlying floor and were screened on absolute return.

  **The split column's reliability.** 66 recorded splits carry no matching price
  discontinuity, which is the expected state for an already-adjusted series. **3 price
  discontinuities carry no recorded split**, being SOXS on 2025-04-09 and 2026-05-26 and
  SVXY on 2018-02-06.

  **Only one of those three is a break.** SOXS on 2025-04-09 is cleared by the residual
  screen, SMH having returned 0.171603 that session so that a registered multiple of
  -3.0 carries the fund's close-to-close step to 0.4402381965121225 without any
  adjustment artifact. The band alone gives that false positive for any 3x fund whenever
  the underlying moves beyond about 13 percent, which is why the two screens are
  conjoined. **SOXS on 2026-05-26 is the break**, its residual reading
  -0.8113452842932015. **SVXY on 2018-02-06 is classified a break by the conjunction
  while the underlying event is the February 2018 volatility spike**, and the frozen
  constant-maturity thirty-day series understates a front-month move, so the volatility
  proxy cannot discriminate there. That limitation was recorded before the run.

  **No contaminated indicator session coincides with a terminal firing.** No indicator
  reads SOXS or SVXY, so no indicator window spans either break. The relative-strength
  reads with a literal ticker are XLK, TLT, PSQ, AGG, SH, IEF, BND, QQQ, BSV and SQQQ,
  and none of the flagged instruments is among them.

- **9.84 gate B, PROCEED, with the first implementation corrected (session 30,
  2026-08-23).** The gate as the scaffold states it is conjunctive, being a break IN an
  instrument contributing materially.

  **Instruments with a break, SOXS and SVXY. Instruments material by flagged
  contribution, UVXY alone. The intersection is empty.** UVXY carries 137 of the 174
  flags and a cumulative flagged contribution of 0.752798 against the primary window's
  arithmetic return sum, which is material, and it carries no discrete discontinuity at
  all. Its flags are the volatility proxy's own mismatch. SOXS carries the only
  unexplained break and its holdout flagged contribution is -0.028670619145405107
  against a window sum of 3.4218690114239116.

  **The first implementation tested materiality without conjoining the break condition
  and would have halted on UVXY.** Both evaluations are recorded. **The 5 percent
  materiality threshold fixed at 9.82 before the flags were seen is not moved**, and
  only the conjunction the scaffold states was added to the implementation.

- **9.85 the disposition, OPEN and adopted by none (session 30, 2026-08-23).**

  **Option one, repair the frozen input.** data/raw/etf/SOXS.parquet changes, its entry
  in 2 manifests changes, and the integrity check every measuring session runs would no
  longer reproduce until those manifests are rewritten. The repair would change an input
  after the single read the study's design permits.

  **Option two, disclose unrepaired.** A known-defective series stays inside the study,
  with the impact bounded by the cumulative flagged contribution of
  -0.041841805663843774 across the holdout.

  **Option three, register the defect and add the implied-multiple screen as a permanent
  pipeline check.** The screen is one script and one call site, sitting beside
  scripts/s195_verify_inputs.py, and it answers a question the hash check cannot, being
  whether a series the hash confirms unchanged is also internally consistent with its own
  registered terms. No hash changes.

  **The measured facts.** The defect contributes exactly 0.0 to holdout return through
  the position path, no break sits in a material instrument, and no contaminated
  indicator session coincides with a terminal firing. **Nothing is adopted here.**

- **9.86 the holdout nulls (session 30, 2026-08-23).** The constructions are read from
  scripts/s14_nulls.py rather than rewritten, its definitions executed up to its own
  driver loop so the RNG carries the session 22 seed convention of 20260818 unchanged.
  10,000 replications.

  | null | metric | holdout exceedances | primary exceedances |
  |---|---|---|---|
  | timing shuffle | annualised return | 4 of 10000 | 7 of 10000 |
  | timing shuffle | naive Sharpe | 0 of 10000 | not reported at session 22 |
  | timing shuffle | Lo-corrected Sharpe | 1 of 10000 | 0 of 10000 |
  | turnover matched | annualised return | 3 of 10000 | 0 of 10000 |
  | turnover matched | naive Sharpe | 0 of 10000 | not reported at session 22 |
  | turnover matched | Lo-corrected Sharpe | 2 of 10000 | 0 of 10000 |

  **Both nulls are centred near zero on annualised return**, the timing shuffle's mean
  reading -0.015298422196856545 and the turnover-matched null's -0.020289910208086697,
  so the strategy sits above a null centred at zero rather than above a high one.

  **The statistic drops the first session**, scripts/s14_nulls.py make_stats evaluating
  on r[1:], so the observed naive Sharpe here reads 1.6195085580131883 against the
  1.637799226672021 at outputs/session-27/holdout-ladder.csv. The null and the observed
  value are computed the same way, so the exceedance counts are internally consistent.

- **9.87 the multi-factor decomposition (session 30, 2026-08-23).** Five factors, all
  standing for instruments already inside the frozen inputs, being QQQ, SMH, XBI, TLT
  and UVXY. Nothing was fetched.

  **The factor returns are open to open**, matching the designated cell. A
  close-to-close factor set correlates only 0.2704559414562822 with the traded
  open-to-open QQQ line and would not span the strategy's own returns, which is why the
  first construction produced a multi-factor R-squared below the single-factor one.

  **Semiconductor absorbs almost all of what is absorbed.** Entering in the
  pre-registered economic order the holdout R-squared runs 0.12086490 with equity market
  alone, 0.19782424 with semiconductor added, 0.20317677 with biotechnology,
  0.20318004 with long Treasury and 0.21044365972605372 with volatility, so
  semiconductor's incremental R-squared of 0.07695934 is more than ten times the other
  three together.

  **The alpha survives.** The holdout annualised alpha falls from 0.5637941837318013 to
  0.45868406085120844, absorbing 0.10511012288059288 or 0.18643349987199245 of it, with
  the Newey-West t at the 8.11 lag of 21 moving from 3.4918970688555846 to
  2.9859793219153783. **Over the primary window the extra factors absorb almost
  nothing**, 0.0033835244195382893 or 0.011718068595027593.

  **The equity market loading changes sign between the windows**, reading
  1.4175774214644519 over the primary window and -0.3998086287867097 over the holdout
  with semiconductor at 0.6608610878426954. The variance inflation on equity market is
  7.35171925889059 and on semiconductor 5.332198903158704 over the holdout, so the two
  loadings are collinear and neither is sharply identified on its own.

  **The multi-factor residual carries a naive Sharpe of 1.3117491651976525** against the
  single-factor residual's 1.527991674661622.

- **9.88 the interval estimates (session 30, 2026-08-23). The study previously reported
  point estimates with no interval anywhere.** The stationary block bootstrap of Politis
  and Romano at a mean block length of 21 sessions, being the Newey-West lag 8.11
  already fixes, so the bootstrap carries the dependence horizon the register already
  records rather than a second one chosen here. 10,000 replications at seed 20260823
  fixed before drawing. The contention check passed at a one-minute load of 4.21 against
  a threshold of 16, and the pass ran in 20.9 seconds at a peak resident 0.199 GB against
  a 3.0 GB ceiling stated before launching.

  | quantity | point | 5th | 95th |
  |---|---|---|---|
  | holdout naive Sharpe | 1.637799226672021 | 0.9929195886104111 | 2.2821599669578414 |
  | holdout Lo-corrected Sharpe | 2.7585227658215015 | 1.1865869286107612 | 3.8601196922066376 |
  | holdout gap against buy-and-hold QQQ | 1.0477912527059852 | 0.3284274858286137 | 1.7779358770268246 |
  | primary naive Sharpe | 1.0910863648060856 | 0.6251134137096785 | 1.5640856869140016 |
  | primary gap against buy-and-hold QQQ | -0.0650226373237004 | -0.5401197472054891 | 0.38408042878289455 |
  | holdout single-factor alpha | 0.5637941837318013 | 0.2913621185383241 | 0.8174425734211889 |
  | holdout multi-factor alpha | 0.45868406085120844 | 0.20140632409937676 | 0.7162501573200948 |

  **The holdout gap against buy-and-hold QQQ excludes zero at the 5th percentile and the
  primary-window gap does not.** The bootstrap standard deviation on the holdout naive
  Sharpe is 0.39007792546862184 against an iid approximate standard error of
  0.043020293946101064, so the iid form understates it by about a factor of nine.

  Every statistic is computed on the EXCESS return series, which is why the annualised
  return point estimates read below the total-return figures the ladder carries.

- **9.89 the NAV sensitivity, the holdout result IS capacity-bounded (session 30,
  2026-08-23).** On the D20 curve axis. The five levels were stated before running and
  scripts/s13_backtest.py START_NAV is restored in a finally block after every run, so no
  canonical value is left changed.

  | starting NAV | naive Sharpe | annualised turnover | cap-binding share | rank |
  |---|---|---|---|---|
  | 1000000.0 | 1.637799226672021 | 21.02620648507965 | 0.9406631762652705 | 2 of 12 |
  | 10000000.0 | 1.4700294082281424 | 15.484415758278117 | 0.9633507853403142 | 3 of 12 |
  | 51671728.47473126 | 1.3545290719046939 | 14.024286213786864 | 0.9755671902268761 | 4 of 12 |
  | 200000000.0 | 1.1988554486241455 | 11.888070527018647 | 0.9930191972076788 | 4 of 12 |
  | 1028029775.2491124 | 0.9817333723461858 | 7.617929397698159 | 1.0 | 4 of 12 |

  **Performance degrades smoothly rather than breaking at a threshold**, the largest
  adjacent step being -0.21712206986430982 against a total change of
  -0.6560658543258352 across the whole range, and the curve is monotone in NAV.

  **The cap-binding share already exceeds both 0.75 and 0.90 at the study anchor**, so
  throttling is not something the holdout introduced. **By calendar year it first
  exceeds 0.75 in 2021 and 0.90 in 2023.**

  **Resetting NAV to the study anchor at the boundary barely moves the Sharpe and moves
  everything else.** The reset reads a naive Sharpe of 1.642191290482138 against the
  inherited 1.637799226672021 at the same rank of 2, while annualised turnover rises
  from 21.02620648507965 to 41.08922178480395, mean effective exposure from
  0.9681564510351294 to 1.3018299643734321 and the cap-binding share falls from
  0.9406631762652705 to 0.2949389179755672.

  **The cost sweep at fixed NAV.** Holding NAV at 51671728.47473126 across all six
  levels the naive Sharpe runs 1.3617719274045747 at zero basis points to
  1.2921155830452756 at fifty, monotone decreasing. **Session 28's coupled sweep is
  already monotone on the naive Sharpe**, so there is no non-monotonicity to disappear.
  What was non-monotone there is the RANK, reading 3 at zero basis points and 2 at every
  higher level.

- **9.90 the instrument attribution and the k equal to zero share (session 30,
  2026-08-23).** Contributions read the lagged realised portfolio weight and exposure
  reads the contemporaneous one, which is what session 28 does, and the exposure figures
  reproduce 0.9681564510351294 over the holdout and 1.7769723457408557 over the primary
  window exactly.

  **The three largest holdout contributors are SOXL at 1.1440491386340664, TQQQ at
  1.1325743766387948 and SQQQ at 0.5631314688211664**, carrying variance shares of
  0.3689889340581915, 0.3741530836359437 and 0.20978610350518583. SQQQ's correlation
  with buy-and-hold QQQ is -0.9980843449617947 and TQQQ's is 0.9994553571304274.

  **The k equal to zero instruments are UVXY, SVXY and BTAL.** They contribute
  0.30042881489693153 of holdout return and 0.017772126937489096 of holdout variance,
  against 2.260897261407411 and 0.44765819686400177 over the primary window.

  **The exposure figure barely moves under a non-zero k.** Carrying the volatility
  instruments at an illustrative k of 1 moves the holdout mean from 0.9681564510351294
  to 0.9734733792725769 and the primary-window mean from 1.7769723457408557 to
  1.6920818243411098. The illustrative value was stated before computing and is **NOT
  adopted**, register 2.15 being unchanged. The realised volatility ratio against
  buy-and-hold QQQ over the holdout is 1.7102013039589175, and the gap between that and
  a mean effective exposure below one is not closed by the k convention.

- **9.91 a correction to session 28's G3 convention mismatch (session 30, 2026-08-23).**
  Session 28's G3 compared the holdout's leave-one-year-out naive range of
  1.4608187196166473 to 1.7121151693407555 against the primary window's Lo range of
  1.287076427656795 to 1.6183359759194622, which are different conventions.

  Restated on each convention separately, the holdout naive range is 1.4608187196166473
  to 1.7121151693407555 and its Lo range 2.372321248555297 to 3.5010323864321666, while
  the primary window's naive range is 1.0224291150162947 to 1.1763811969058335 and its
  Lo range 1.2947908486900495 to 1.6185369513800767.

  **A second reason the session 28 comparison does not hold.** Each estimate above
  removes the calendar year's sessions from the committed return series, while the
  primary-window Lo range session 28 quoted comes from session 22's leave-one-out
  REBUILD, which re-ran the strategy with the year dropped. The two constructions are not
  the same quantity. **outputs/session-28/REPORT.md is not edited and the correction
  stands here.**
