# Session 20 report, phases D through G

`REPORT.md` covers phases A through C. This document covers D through G, resumed
after phase C's gate tripped. **Phase C is recorded as failed.** The gate condition
was that both randomization nulls clear p below 0.001 on the designated cell, and
the timing-shuffle null on annualised return did not. D through G ran on the
corrected boundary regardless, since the boundary repair itself succeeded.

The holdout boundary is untouched, no grid was re-executed, and no grid point was
adopted. Every figure is read from an emitted CSV in `outputs/session-20/`.

## The headline of this half

**The 121,500 specifications are not 121,500 independent trials.** Across the
pre-registered 2,000-specification subsample the correlation spectrum puts
46.8 percent of total
variance in the first principal component, and the effective count is
3.43 under the participation
ratio, 17 under a 95 percent
variance threshold, and 6.72 under
spectral entropy. The canonical's deflated Sharpe moves from
0.001979 at the pre-registered N to 0.981787 at the participation-ratio
count. Recorded as a disclosed post-hoc sensitivity under 9.10 with the primary
remaining N equal to 121,500.

## D1, the Lo lag count

`lo_sharpe(excess, q=252)` is a Python default parameter, absent from `config.py`,
absent from every curve axis, and never swept until now.

| q | strategy Lo Sharpe | strategy rank |
|---|---|---|
| 1 | 1.0911 | 6 |
| 5 | 1.1491 | 7 |
| 21 | 1.2291 | 7 |
| 63 | 1.2740 | 7 |
| 126 | 1.3931 | 7 |
| 252 | 1.3817 | 6 |

The strategy's rank spans 6 to 7
across the sweep, and **9
of twelve rows change rank**. q equal to 1 is the naive Sharpe limit.

### Every row against its own no-autocorrelation null

300 permutations per row at seed
20260820 fixed before drawing.

| line | observed factor | null 5th | null 95th | inside own null |
|---|---|---|---|---|
| STRATEGY | 1.2664 | 0.8106 | 1.5045 | yes |
| buy_hold_QQQ | 1.5598 | 0.8202 | 1.4787 | no |
| buy_hold_TQQQ | 1.6024 | 0.8234 | 1.4835 | no |
| vol_targeted_QQQ_matched | 1.3263 | 0.8307 | 1.5160 | yes |
| naive_fast_1d_momentum | 1.3608 | 0.8185 | 1.4787 | yes |
| matched_exposure_levered_QQQ_1.70 | 1.6028 | 0.8235 | 1.4833 | no |
| long_legs_only | 1.2080 | 0.8300 | 1.5154 | yes |
| equal_weight_universe | 1.0168 | 0.8351 | 1.4818 | yes |
| sleeve_T10_standalone | 1.2551 | 0.8259 | 1.4723 | yes |
| sleeve_T11_standalone | 1.2058 | 0.8151 | 1.4660 | yes |
| sleeve_S2_standalone | 1.1088 | 0.8164 | 1.4819 | yes |
| sleeve_S3_standalone | 1.1152 | 0.8145 | 1.5249 | yes |

**9 of twelve rows
fall inside their own null**, meaning their Lo factor is indistinguishable from what
a series with no autocorrelation produces at this sample length. The three that fall
outside are exactly the three rows that outrank the strategy on the Lo-corrected
Sharpe, being buy-and-hold TQQQ, buy-and-hold QQQ, and matched-exposure levered QQQ.
The strategy's own factor is inside its null.

The Lo variance estimate turns non-positive at a weighted autocorrelation sum of
-126.0. Every row
sits above it, with the three outside-null rows closest at 1.16 to 1.23 null standard
deviations and the rest between 1.60 and 2.98.

## D2, the deflated Sharpe corrected to N equal to 121,500

N equal to 364,500 counts the 7.4 tier-two offset axis, which was held at its canonical value of 10 on every specification and across which no maximum was ever taken. Selection operates only over trials actually drawn, so the evaluated count of 121,500 is the count the statistic requires. Recorded as a correctness repair with the grounds stated, not as a post-hoc sensitivity, and no 9.10 entry is opened

| point | metric | N=121,500 | N=364,500 superseded |
|---|---|---|---|
| canonical | naive Sharpe | 0.001979 | 0.000660 |
| in_sample_best | naive Sharpe | 0.048847 | 0.023736 |

The propagation sweep found 29 sites
carrying the figure, of which 13
designate N and require correction. The remainder state the size of the enumerated
space, which remains true, including `MANIFEST.json`'s `grid.n_enumerated` field.

## D3, the degradation slope

**Status UNRESOLVED.** no valid null exists for the degradation slope. Session 19.6's null permuted block ordering independently per specification, which destroys the common time structure every specification shares, so its four z-scores measure the presence of that shared structure rather than overfitting.
The corrected value carried forward is -1.0666200132036998
against the emitted -1.0663023854544191, since
the phase B1 re-emission halted on the memory gate. The statistic is a candidate for
removal from the paper and no recommendation is made on whether to remove it.

Session 19.6's PBO null is retained as an **estimator control** rather than as a
test. A harness fed selection driven purely by idiosyncratic noise returned a PBO of
0.991928 against the observed
0.157809, which is a validation the
observed figure never carried on its own.

## E1, the axis census

**The authoritative count of searched degrees of freedom is
9**, being the
nine grid axes. The curve axes are reported sensitivities rather than a search over
which a maximum was taken, so they do not enter N.

| discrepancy | resolution |
|---|---|
| participation_cap | session 19 added it to the curve axis list without recording the addition, giving eleven where 9.11 plus NAV gives ten. Searched as a sensitivity, not part of N |
| ladder_fourteen_to_twelve | session 14's ladder carried fourteen lines and the twelve-row ladder dropped the intraday-only and overnight-only hold universes. Recorded nowhere and never run through Romano-Wolf at thirteen. Not part of N, since the ladder is a comparison set rather than a search |
| lo_q | on no axis, a Python default at scripts/s13_backtest.py:609, never swept before phase D1. Belongs in N only if the paper reports a figure selected across q, which it does not |
| tier_two_offset | held at 10 on every specification, no maximum taken across it, so it does not enter N |

## E2, sourcing the three open axes

| arm | annualised | naive Sharpe | Lo Sharpe |
|---|---|---|---|
| canonical | 0.521845 | 1.091086 | 1.381701 |
| smh_accrual 0.0 | 0.520120 | 1.088906 | 1.374755 |
| smh_accrual 1.0 | 0.520910 | 1.090240 | 1.378240 |
| smh_accrual 2.0 | 0.523787 | 1.093911 | 1.394313 |

**Two of the three cannot be sourced by measurement.**

- **sizing_mode**, NOT SOURCED, the axis is unwired. config.SIZING_MODE is defined at src/config.py:78 and validated at line 333, but the engine hardcodes math.trunc(alloc / px) at scripts/s13_backtest.py:528 and never calls src.execution.size_position nor reads config.SIZING_MODE. Setting the config to fractional changes nothing in the return-generating path, so the axis cannot be measured without a code change, which is a specification change rather than a measurement. This is a new instance of the phase B3 hardcoded-literal class
- **completion_rule**, NOT SOURCED, no alternative arm exists. scripts/s13_backtest.py lines 18 to 24 record the unavailable-fill completion rule as PROVISIONAL and explicitly not a register closure, and no switch implements an alternative. Sourcing it requires implementing a second arm, which is a specification change rather than a measurement

The sizing-mode finding is a new instance of the phase B3 hardcoded-literal class and
was not known before this phase.

## E3, effective N

The subsample carries 2001 series and
the canonical sits inside it, reproducing session 19 step 3's positive control.

| definition | effective count | expected maximum Sharpe | canonical deflated Sharpe |
|---|---|---|---|
| participation_ratio | 3.43 | 0.4285 | 0.981787 |
| spectral_entropy | 6.72 | 0.6166 | 0.932982 |
| variance_threshold_95 | 17.00 | 0.8263 | 0.798492 |
| preregistered_121500 | 121500.00 | 2.0036 | 0.001979 |

The canonical's naive Sharpe is 1.0911, which sits
above the expected maximum at every effective count and below it at the
pre-registered N. **Primary remains N equal to 121,500.**

## F, the January 2013 event

The span runs 2013-01-02 to 2013-01-22, 14
sessions, cumulative -0.190783.

| sleeve | arithmetic contribution |
|---|---|
| T10 | -0.063276 |
| T11 | -0.047584 |
| S2 | +0.030385 |
| S3 | +0.044738 |

**Attribution established rather than asserted.** UVXY is carried by
3 sleeves during the span,
being S3 T10 T11, and
2 sleeves
lose, being T10 T11. Both
conditions hold together. The worst single instrument is UVXY at
-0.0849.
S2 and S3 both contribute positively, so the loss is not portfolio-wide.

### The event is not singular

**69 overlapping
fourteen-session windows across the primary window fall below
-0.15, and January 2013 ranks
42 among them.** The worst is
2020-02-27 to
2020-03-17 at
-0.503239. The
premise that the event appears in no session report because it is exceptional does
not hold; it is unexceptional among this strategy's fourteen-session drawdowns.

### The tie to the strata and to the strip

Overbought tier one carries 0.0100 to 0.4673, the widest within-axis range of the six structural axes, and
the canonical value on that axis carries a stratum PBO of
0.235509. The same axis
controls the tier-one terminal that returns UVXY at full sleeve weight.

Arms starting after the span exclude the event and arms starting before include it.

| arm | start | annualised | event |
|---|---|---|---|
| earliest_full_composition | 2013-01-23 | 0.6749 | excludes the event |
| pre_D21_boundary | 2011-10-03 | 0.5226 | includes the event |
| canonical | 2011-10-04 | 0.5218 | includes the event |
| first_session_2012 | 2012-01-03 | 0.5809 | includes the event |
| first_session_2013 | 2013-01-02 | 0.6286 | includes the event |
| first_session_2014 | 2014-01-02 | 0.6336 | excludes the event |

**The strip's asymmetry.** nested through run(sig["rows"]) which takes no start argument, so every arm slices one account, while
each built through LINES[ln][0](o2o, sig["rows"], i0) with the per-arm entry index.
7 of the eleven
benchmark lines carry state and are therefore affected by re-entry rather than only
repriced, being vol_targeted_QQQ_matched naive_fast_1d_momentum long_legs_only sleeve_T10_standalone sleeve_T11_standalone sleeve_S2_standalone sleeve_S3_standalone. The other
4 are buy-and-hold or
daily-constant and move only their entry price.

## G, skipped on the budget gate

Free memory stands at 0.06 GiB genuinely unused with
1.29 GiB available including inactive, against
3.07 GiB held by the compressor and
760.25 MB of free swap.

The corrected null needs about 0.717 GB
before Python and BLAS overhead, being the moment array, a per-specification residual
array, a permutation index, and six chunk-sized arrays. **The gate fails on the RAM
condition and the phase is skipped rather than run partially.** The precedent is
direct, since phase B1's strictly lighter pass, without the residual and permutation
arrays, already fell to 0.0 percent CPU and was killed at this machine state.

The construction is recorded in `degradation-null-corrected.csv` so a later session
can run it unchanged.

## Findings and the class of change each would need

| finding | class |
|---|---|
| nine of twelve ladder rows change rank across the Lo q sweep | register decision on whether 8.2 keeps the Lo-corrected Sharpe as headline |
| nine of twelve rows' Lo factors are inside their own no-autocorrelation null | register decision, same 8.2 question |
| N corrected to 121,500 for the deflated Sharpe | correctness repair, applied |
| the effective count is 3 to 17 rather than 121,500 | post-hoc sensitivity under 9.10, primary unchanged |
| config.SIZING_MODE is unwired from the engine | correctness repair to wire it, specification change to vary it |
| the completion rule has no alternative arm | specification change |
| the January 2013 event ranks 42nd of 69 comparable windows | documentation |
| the strip compares a nested strategy against seven stateful re-initialised benchmarks | correctness repair |
| the degradation slope has no valid null | register decision on removal |

No recommendation is made on any of these.

## Stop

Phases D through F complete, phase G skipped on the budget gate. Phase C recorded as
failed. Holdout untouched, grid not re-executed, no grid point adopted, no canonical
value changed.

