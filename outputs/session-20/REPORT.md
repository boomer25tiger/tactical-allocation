# Session 20 report

Consolidated repair, audit, and search-space accounting. Phases A through C ran,
phase C's gate tripped, and phases D through G were not reached. Partial completion
through a completed phase is the state this session ends in. The 2021-08-01 holdout
boundary is untouched, no grid was re-executed, and no grid point was adopted or
promoted. Session 15 and session 14 outputs are preserved alongside their rebuilds.

Every figure below is read from an emitted CSV in `outputs/session-20/`.

## SVIX and UVIX, resolved

Both are held in code and load on neither panel. The availability switch at
`src/sleeves.py` resolves them away, since `State.available` at
`scripts/s13_backtest.py:344` reads `self.sig.avail.get(t)` and returns False for a
ticker absent from the panel. Across the primary window the two terminals that could
select them fired 1,114 times for
T10 and 519 times for S3, while SVIX
was selected 0 times and UVIX
0 times.

**What the engine does with an unlisted held ticker is raise.** The fill path at
`scripts/s13_backtest.py:500` reads `px = raw[t][i]` where `raw` is built only over
`panel.frames`, so an absent ticker raises KeyError rather than being silently
dropped, renormalised across survivors, or routed to cash. Register 1.9 covers
threshold reads and is silent on weight dictionaries, and the traced behaviour is an
exception.

**Gate A2 does not trip.** The gate halts the session only if the engine raises AND
the terminal can fire inside the holdout. It cannot, because the availability switch
cannot select a ticker the loader excludes, so the branch is unreachable rather than
merely unfired.

The consequence stands regardless. SVIX and UVIX list 2022-03-30 on the frozen
files, inside the holdout span beginning 2021-08-01, and the source strategy's
SVIX_LIVE and UVIX_LIVE guards would activate there while this implementation will
not. **The branch executed zero times in sample and will execute zero times at the
holdout read under the current loader.** A session that adds the two tickers to
`bt.LEVERED` activates them for the first time inside the holdout.

## The canonical positive control, before and after

Before the boundary repair, run at the top of phase A from the 339 frozen inputs,
the canonical returned 0.521845 annualised and
1.381701 Lo-corrected Sharpe over
2472 sessions, inside a
5e-07 tolerance stated before comparing.

After the repair, the rebuilt session 14 ladder reproduces
0.521845 against the pre-repair
0.522592, which is register
7.14a's corrected value. The control passes on both sides.

## The boundary delta

`scripts/s14_common.py` line 29 read 2011-10-03 and no session 15 script overrode
it, so every session 15 primary-window row carried
2473 sessions against the corrected
2472.

| quantity | before | after |
|---|---|---|
| strategy ann_return | 0.522592 | 0.521845 |
| strategy sharpe_naive | 1.092220 | 1.091086 |
| strategy sharpe_lo | 1.384621 | 1.381701 |
| buy-and-hold QQQ information ratio | 0.703614 | 0.709366 |
| buy-and-hold QQQ tracking error | 0.440999 | 0.440754 |
| buy-and-hold QQQ Newey-West alpha t | 2.347007 | 2.364283 |
| buy-and-hold QQQ annualised alpha | 0.287263 | 0.288744 |

All twelve ladder rows on the Lo-corrected Sharpe.

| line | before | after | rank before | rank after |
|---|---|---|---|---|
| STRATEGY | 1.3846 | 1.3817 | 6 | 6 |
| buy_hold_QQQ | 1.7924 | 1.8033 | 2 | 2 |
| buy_hold_TQQQ | 1.7937 | 1.8057 | 1 | 1 |
| vol_targeted_QQQ_matched | 1.4353 | 1.4305 | 5 | 5 |
| naive_fast_1d_momentum | 1.0754 | 1.0756 | 9 | 9 |
| matched_exposure_levered_QQQ_1.70 | 1.7899 | 1.8018 | 3 | 3 |
| long_legs_only | 1.4614 | 1.4696 | 4 | 4 |
| equal_weight_universe | 0.5903 | 0.5904 | 11 | 11 |
| sleeve_T10_standalone | 0.5070 | 0.5189 | 12 | 12 |
| sleeve_T11_standalone | 0.9736 | 0.9739 | 10 | 10 |
| sleeve_S2_standalone | 1.3558 | 1.3271 | 7 | 7 |
| sleeve_S3_standalone | 1.1951 | 1.1959 | 8 | 8 |

**No rank changes.** The strategy holds sixth of twelve on both metrics.

## Gate C, tripped

The gate halts the session before phase D if the rebuilt canonical fails its control
or if either randomization null ceases to clear p below 0.001 on the designated cell.
The control passes. The nulls do not both clear.

| null | metric | p before | p after | clears p below 0.001 |
|---|---|---|---|---|
| timing_shuffle_block_bootstrap | annualised return | 0.000 | 0.001 | no |
| timing_shuffle_block_bootstrap | Lo-corrected Sharpe | 0.000 | 0.000 | yes |
| turnover_matched_switching | annualised return | 0.000 | 0.000 | yes |
| turnover_matched_switching | Lo-corrected Sharpe | 0.000 | 0.000 | yes |

The timing-shuffle null on annualised return moves from p 0.000 to p 0.001, and the
strategy's percentile on that arm moves from 100.0 to
99.9.
On the Lo-corrected Sharpe, which 8.2 designates as headline, both nulls remain at p
0.000 with the strategy at the 100th percentile. The session halts here as
instructed rather than absorbing the change.

Romano-Wolf across eleven comparisons keeps one below 0.05, the equal-weight
universe moving from 0.033
to 0.046 with the
strategy above. Buy-and-hold QQQ moves from
0.052 to
0.052.

## Phase A, the derived universe

Derived from the AST of `src/sleeves.py` with no list written by hand,
**19 held** and
**13 signal-only**, which
reconciles exactly with session 19.6. `outputs/session-20/held-universe.csv` carries
the sleeve, terminal, line number, and weight expression for every held ticker and
supersedes every hardcoded list in the repository.

QQQ is held rather than a signal input, on
195 of
2,472 sessions at a mean conditional weight
of 0.1244 and a mean unconditional weight
of 0.0098. The arithmetic share of the
strategy's summed daily return attributable to that position is
0.007405, so the gap against buy-and-hold
QQQ is partly a comparison of the strategy against a component of itself.

Coverage recomputed on the derived set gives
916 realized-panel
sessions and 0 synthetic-panel
sessions carrying a held ticker unlisted, against
0.0 unavailable fills in
`outputs/session-16/boundary-correction.csv`. The two are different quantities and
are named separately here. Strict full composition is unreachable on any date, since
SVIX and UVIX load on neither panel.

## Phase B, three class sweeps

**B1, the chunk-first-element class.** The sweep found the shape at four files
rather than the two the scaffold named, being `s19_step4.py`, `s18_step3.py`,
`s19_draws.py`, and `s19_step5.py`, the last of which is the stratified pass. All
four are repaired to a per-combination count. Two further hits in
`s13_5_diagnostics.py` are tuple indexing and are recorded as false positives.

**The re-emission halted on the memory gate.** Free plus inactive memory stood at
1.33 GiB with the ceiling stated at
0.65 GB and the chunk at
48 against session 19's 514. The pass fell to zero
percent CPU with 400 KB resident and was killed rather than allowed to continue into
swap, with free swap down to 560.56 MB. No
regression figure was re-emitted. The known magnitude of the outstanding shift is
3.176e-04 on the S equal to 16 slope, measured by
session 19.6 at chunk 514.

PBO and the stratified PBO are immune and were not re-run. Within a chunk the
substituted count is one scalar applied to every specification, so it scales every
Sharpe identically and preserves the ordering the rank and the argmax read, and PBO
is a function of that ordering alone. Session 19.6 measured a PBO gap of exactly
0.0e+00 at chunk 128, 257, and 514, which is the empirical half of the same argument.

**B2, the vacuous-check class.** Five checks are repaired with an explicit
cardinality floor asserted before the predicate.

| check | floor | basis |
|---|---|---|
| required-artifact check | 8 per shard class, 1 or 2 otherwise | the shard count the grid emitter writes, and the file count each class carries |
| regenerability figure count | 4 | the four figures scripts/s19_report.py writes |
| prose figure check | 10 prose figures and 10 CSV numerics | a session report carrying fewer than ten decimal figures is not a report the check can meaningfully screen |
| additivity accumulator | 21 | the canonical plus the twenty drawn specifications the step specifies |
| per-shard parse consistency | 1 | a shard carrying zero specifications is not a shard that parsed |

**B3, the hardcoded literal class.** The sweep covers
62 numeric literal sites and
35 ticker-list sites, of which
28 diverge from their authoritative
source. Divergent ticker lists are reported against the derived held set rather than
repaired wholesale, since replacing every list is a specification change rather than
a correctness repair, and the single divergence that entered an emitted measurement
was `s195_strip.py`, already superseded by the phase A artifact.

## Phases not reached

| phase | status | reason |
|---|---|---|
| B1 re-emission | halted | memory gate, machine in swap |
| C, s15_step12 rebuild | not run | session ended at the gate C halt |
| D, metric audit | not reached | gate C halts before phase D |
| E, search-space accounting | not reached | gate C halts before phase D |
| F, January 2013 event | not reached | gate C halts before phase D |
| G, corrected degradation null | not reached | gate C, and the budget gate would have failed independently on the memory state |

## Findings and the class of change each would need

| finding | class |
|---|---|
| the primary window boundary was superseded in every session 15 output | correctness repair, applied |
| the chunk-first-element count at four sites | correctness repair, code applied and re-emission outstanding |
| five checks passing on empty input | correctness repair, applied |
| the timing-shuffle null on annualised return no longer clears p below 0.001 | register decision on what the paper claims |
| SVIX and UVIX are unreachable in sample and at the holdout read | register decision on whether the loader should carry them |
| QQQ is held and also a ladder benchmark | documentation |
| divergent hardcoded ticker lists across the repository | specification change to refactor, documentation as diagnosed |
| the matched-exposure row was built at the registered exposure where D25 gives 1.777 | correctness repair, rebuilt |

No recommendation is made on any of these.

## Machine state and resources

Measured before any moment-array load. Free plus inactive
1.33 GiB on an 8 GiB machine, with
swap reading total = 12288.00M  used = 11767.44M  free = 520.56M  (encrypted). The derived ceiling was
0.65 GB.

| phase | peak resident | wall clock |
|---|---|---|
| A | 0.151 GB | 4.7 s |
| B sweeps | under 0.2 GB | seconds |
| B1 re-emission | halted | killed on the memory gate |
| C rebuilds | single-specification engine runs | several minutes per script |

## What remains open before the holdout can run

- **Gate C is unresolved.** The timing-shuffle null on annualised return sits at p
  0.001 rather than below it, and what the paper claims from that is a register
  decision this session does not make.
- **The B1 re-emission is outstanding**, so the three regression figures in
  `outputs/session-19/pbo.csv` and the regression columns of `pbo-strata.csv` still
  carry the chunk-dependent count.
- **Phases D through G are unrun**, so the Lo q sweep, the deflated Sharpe
  correction to N equal to 121,500, the axis census, the three unsourced 9.11 axes,
  effective N, the January 2013 attribution, and the corrected degradation null all
  remain open.
- **A2 leaves one code path untested at the holdout read.** The SVIX and UVIX
  branches will not execute inside the holdout under the current loader, so the
  holdout measures a strategy that differs from the source over the span from
  2022-03-30.
- **D16**, the financing spread, remains assumed.

## Stop

Halted after phase H with gate C tripped. No holdout executed, no grid re-executed,
no grid point adopted, no canonical value changed on any axis, and the primary window
remains 2011-10-04. One commit.

