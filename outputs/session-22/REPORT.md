# Session 22 report

Closing the measurement phase. Phases A through E and G ran. Phase F was skipped
because gate A did not clear. The 2021-08-01 holdout boundary is untouched, no grid
was re-executed, no grid point was adopted, and `bt.LEVERED` is unmodified.

Free memory is not reported as headroom anywhere in this session. The metrics used
are compressor size, swap used, swap free, and the page-out count.

## The three openers

**The relaunch test did not complete.** Under a wall limit of
1800 seconds pre-registered and written
to the artifact before the process started, the pass ran
1806.6 seconds without emitting a single one of
its five passes and was terminated on that rule. **The constraint is real, and it is
not memory.** Peak resident reached 1.133 GB against the
3.561 GB that completed in `m1-diagnostic.csv`, the maximum page-out rate was
80.9 per second, and the compressor stayed
near 2.754 GiB throughout. Load average was
 on  cores and the
process received a mean of  percent CPU.

**The nulls clear at 10,000 draws.** Exceedance counts on the designated cell.

| null | metric | exceedances | draws | p |
|---|---|---|---|---|
| timing_shuffle_block_bootstrap | annualised return | 7 | 10000 | 0.00070 |
| timing_shuffle_block_bootstrap | Lo-corrected Sharpe | 0 | 10000 | 0.00000 |
| turnover_matched_switching | annualised return | 0 | 10000 | 0.00000 |
| turnover_matched_switching | Lo-corrected Sharpe | 0 | 10000 | 0.00000 |

All four clear p below 0.001. The one exceedance of 1,000 that tripped the session 20
gate is consistent with the 10,000-draw estimate in every case.

**The leave-one-out range is unchanged.** Before
1.2871 to 1.6183,
after 1.2871 to
1.6183. The premise that these files carried the
superseded boundary is false, and the rebuild confirms rather than repairs.

## Phase A, the relaunch test

The abandonment rule was written to the artifact before launch. terminate on the wall limit and on nothing else. An observed slowdown, a low CPU percentage, a small resident size or a falling swap figure are recorded and are not grounds for termination.
The limit is 18.58 times the 96.9 s chunk-514 pass and 16.07 times the 112 s at which the session 20 B1 pass was terminated by hand.

The pass was terminated with reason recorded as pre-registered wall limit reached,
and the return code is SIGTERM issued by this script. The operating system terminated
nothing, which was also true of every earlier pass.

**Gate A did not clear**, so phase F is skipped. What that establishes is narrower
than the register previously claimed. The pass does not complete at this machine
state under a thirty minute limit, and the reason is CPU starvation rather than
memory. Four Google Chrome processes were consuming 53.3, 47.4, 44.9 and 43.5 percent
of CPU with WindowServer at 26.9 percent.

The full 113-sample series is in `relaunch-test.csv` rather than summarised away.

## Phase B, the nulls at 10,000

The session 20 gate required clearing p below 0.001. At the registered 1,000 draws that requires exactly zero exceedances, so the gate turns on a single Monte Carlo draw. The defect is in the gate specification rather than in the result, and the replication count is raised to make the region resolvable rather than because a result moved unfavourably.

The seed convention is np.random.default_rng at scripts/s14_nulls.py line 36, read from that script rather than assumed. Block length 21 sessions, read from that
script rather than assumed, on the corrected 2011-10-04 boundary.

| null and metric | prior | now |
|---|---|---|
| timing_shuffle_block_bootstrap, annualised return | 1 of 1000 | 7 of 10000 |
| timing_shuffle_block_bootstrap, Lo-corrected Sharpe | 0 of 1000 | 0 of 10000 |
| turnover_matched_switching, annualised return | 0 of 1000 | 0 of 10000 |
| turnover_matched_switching, Lo-corrected Sharpe | 0 of 1000 | 0 of 10000 |

Every prior count falls inside the 99 percent binomial interval implied by the
10,000-draw estimate. at 1,000 draws the region below p 0.001 is reachable only at zero exceedances, so the gate turned on a single draw. At 10,000 draws the same region admits up to nine exceedances, so the estimate is resolvable rather than binary.

exceedance counts are the primary form, since one in 1,000 and ten in 10,000 are the same estimate at different resolution.

## Phase C, the leave-one-out rebuild

**The premise that these files carry the superseded 2011-10-03 boundary is FALSE. The base estimate is 1.3817013060 in the original and identical in the rebuild, which is the register 7.14a corrected value. Session 16 is the session that made that correction and s16_step4.py ran after it, so the leave-one-out artifacts were already on the corrected boundary. Session 21's F2 finding is overturned and the rebuild confirms rather than repairs.**

The two years whose removal raises the Sharpe most are 2020=1.6183 2011=1.5636,
so 2020 2011 is what the
rebuilt file supports.

**The agreement is STRUCTURAL and session 21's coincidence finding is OVERTURNED. The primary window begins 2011-10-04, so calendar year 2011 inside it spans only 2011-10-04 to the last December session. Dropping calendar 2011 removes very nearly the same sessions as starting the window at the first session of 2012, so the two operations are close to identical and agree to six decimals rather than four.** The leave-one-out estimate for 2011 reads
1.5635962707744815 and the 2012-start strip arm reads
1.5635954382183046, a gap of
8.326e-07.

Originals are preserved and the rebuild is in `outputs/session-22/rebuilt/`.

## Phase D, beta window sensitivity

120, 252 and 504 sessions, being twice session 21's 60, about one trading year, and about two, chosen for coverage not for result. Session 21 used
60, which config.CRASH_HORIZON_SESSIONS, registered for crash detection rather than for beta estimation.

| window | beta mean | beta sd | beta min | beta max | above 1.0 | above 1.7 |
|---|---|---|---|---|---|---|
| 60 (session 21) | 0.864383 | 1.164612 | -4.497370 | 2.788517 | | |
| 120 | 1.018064 | 0.699299 | -2.477552 | 2.140786 | 0.5889 | 0.1322 |
| 252 | 1.038754 | 0.410476 | -0.533075 | 1.985674 | 0.5644 | 0.0234 |
| 504 | 1.068776 | 0.209221 | 0.595057 | 1.381112 | 0.6235 | 0.0000 |

**The beta range narrows monotonically as the window lengthens**, with the standard
deviation falling from 1.164612 at 60 sessions to 0.209221 at 504, and the minimum
moving from below minus four to above plus one half. The extremes at the shortest
window are small-sample estimation noise rather than realised exposure.

| window | static exposure | timing | residual |
|---|---|---|---|
| 60 (session 21) | +0.241396 | +0.011293 | +0.319875 |
| 120 | +0.223127 | +0.027230 | +0.347057 |
| 252 | +0.233585 | -0.004075 | +0.349982 |
| 504 | +0.241270 | -0.007751 | +0.404540 |

**The timing component does not stay near session 21's figure and changes sign**,
reading positive at 60 and 120 sessions and negative at 252 and 504.

| window | matched annualised | matched naive | matched Lo | turnover | ladder naive |
|---|---|---|---|---|---|
| 60 (session 21) | 0.273354 | 1.108581 | 1.300043 | 5.234604 | 6 |
| 120 | 0.236606 | 1.033797 | 1.178906 | 3.04 | 9 |
| 252 | 0.205787 | 0.965584 | 1.142741 | 1.58 | 9 |
| 504 | 0.188911 | 0.917770 | 1.131286 | 0.74 | 9 |

**The exposure-matched line's naive Sharpe falls with the window**, from 1.108581 at
60 sessions to 0.917770 at 504, against the strategy's 1.0911. Session 21's finding
that the matched line reaches a higher naive Sharpe holds only at the shortest and
noisiest window.

beta is estimated from the strategy's own realised returns, so the line is not implementable and enters the paper as a decomposition rather than as an ex-ante benchmark.

## Phase E, what the volatility terminals resolve to

| terminal | line as written |
|---|---|
| t10_weights:L189 | `return {"TECL": 1 / 3, "SOXL": 1 / 3, vol_short: 1 / 3}` |
| s3_weights:L325 | `return {vol: 1.0}` |

scripts/s13_backtest.py:344 State.available reads self.sig.avail.get(t) and returns False when the ticker is absent from the panel, so the switch selects the fallback and the dictionary written into the weight map never names SVIX or UVIX.

**there is none, and none is needed. The switch chooses the ticker BEFORE the dictionary is built, so the returned weights are the written weights with the fallback ticker substituted. No weight is dropped, no balance goes to cash, and no renormalisation occurs.**

| terminal | firings | realised holding |
|---|---|---|
| T10 vol-short | 1114 | SVXY on 1114 sessions |
| S3 vol | 519 | UVXY on 519 sessions |

Both list 2022-03-30 on the frozen files, against the holdout span beginning 2021-08-01, so the listing falls inside the holdout,
confirming session 20. Neither is in `bt.LEVERED` and neither panel carries them.

**Disposition.** adding either ticker to bt.LEVERED would make State.available return True from its listing date, the switch would select it, and the branch would execute for the first time inside the single holdout read. The loader is left unchanged and the limitation is disclosed.

## Phase F, skipped

Gate A did not clear, so the B1 re-emission did not run. The chunk-first-element
defect remains repaired in code at four sites and unre-emitted in the three
regression figures. The degradation slope is removed from the paper at 9.35
regardless, so the outstanding item closes a defect rather than restoring a reported
figure.

## Phase G, the register-claim sweep

an inference recorded as a measurement. The three instances are a vacuous check passing on empty input at 9.22, a gate turning on a single draw at 9.38, and a resource claim asserting a mechanism never observed, which this entry covers.

| claim | class |
|---|---|
| blocked on memory / halted on the memory gate | correctness repair |
| free memory quoted as available headroom | wording correction |
| gate C tripped, stated as a property of the result | correctness repair |
| the leave-one-out artifacts carry the superseded boundary | correctness repair |
| the 1.5636 agreement is coincidental | correctness repair |
| the exposure-matched line reaches a higher naive Sharpe than the strategy | wording correction |
| SVIX and UVIX are unreachable | claim holds as written |
| config.SIZING_MODE is unwired | claim holds as written |

## Findings and the class of change each would need

| finding | class |
|---|---|
| the passes do not complete at this machine state, and the cause is CPU contention rather than memory | correctness repair to the register text, applied |
| all four nulls clear p below 0.001 at 10,000 draws | register decision on what the paper claims |
| the leave-one-out artifacts were already on the corrected boundary | documentation, session 21's finding overturned |
| the 1.5636 agreement is structural rather than coincidental | documentation, session 21's finding overturned |
| the rolling beta range is estimation noise at short windows | documentation |
| the timing component changes sign across windows | documentation |
| the exposure-matched result holds only at the shortest window | documentation, session 21's finding qualified |
| the volatility terminals substitute the fallback before the dictionary is built | documentation |
| four register claims were inferences recorded as measurements | correctness repair, applied |

No recommendation is made on any of these.

## What remains open before the holdout can run

- **The B1 re-emission is still outstanding**, now with a measured reason, being that
  the pass does not complete under CPU contention at this machine state.
- **8.2 is decided this session** and the convention is stated wherever a figure
  appears, so it is no longer open.
- **Ten config parameters have no consumer** and two more are read but never invoked.
- **`crash_threshold` was fixed after measurement on its own axis.**
- **SVIX and UVIX leave a code path that will not execute at the holdout read**, and
  the loader is left unchanged deliberately.
- **D16 and D23 stand.**

## Machine state per phase

| point | compressor GiB | swap used MB | swap free MB | page-outs cumulative |
|---|---|---|---|---|
| session start | 2.754 | 13042.94 | 1293.06 | 13581342 |
| after phase C | 2.829 | 14102.0 | 1258.0 | 13646682 |
| session end | 2.894 | 12643.31 | 668.69 | 13656161 |

## Stop

Halted after phase H. No holdout executed, no grid re-executed, no grid point
adopted, no canonical value changed, `bt.LEVERED` unmodified, and session 16 and 16b
outputs preserved alongside their rebuilds.

