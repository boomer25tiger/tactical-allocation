# STATE, read this first

Refreshed 2026-08-23 by session 29. Supersedes the session 28 version.

**The claim set is frozen.** `docs/CLAIMS.md` carries 15 claims with the
limitations written beside each, and `docs/WITHDRAWN.md` carries 11 withdrawals.
No claim is added without a dated register entry recording the addition and its
grounds. Registered at 9.51 and 9.52. Claim 4's scope phrase was narrowed on
2026-08-22 as a wording repair at 9.59, with no quoted figure moved.

**The holdout has been READ, once, on 2026-08-22.** All three gates passed
first. The span runs 2021-08-01 to 2026-08-14, being 1265 sessions against the
primary window's 2472, and it runs entirely on the 339 hashed frozen inputs.
Registered at 9.66. **The read is not repeated.**

**All four falsifiable prediction components are falsified**, at 9.67. The
strategy ranks 2 of 12 on the naive Sharpe and 1 of 12 on the Lo-corrected over
the holdout, at 1.637799226672021 and 2.7585227658215015.

**The holdout is decomposed**, at 9.70 through 9.78, under a ruling written
before any measurement that permits describing a committed result and forbids
selecting against it. **No specification was selected on any holdout
observation.**

**The dedicated lookahead test has run**, at 9.71, closing the gap the
corrections list item 12 recorded. Under one additional session of lag the
holdout rank holds at 2 of 12 while the annualised return falls from
0.8287111594113898 to 0.4284098105559164. **The rank survives and the level does
not.** Corrections item 12's own pattern does not reproduce on the designated
open-to-open cell and is convention-specific.

**The holdout Lo factor sits inside its own permutation null** at holdout sample
length, at 9.72, and the Lo-corrected rank of 1 of 12 occurs at q equal to 252
alone.

**The turnover fall is a capacity effect**, at 9.73. Rebalancing events per
session rose while the participation cap bound on 0.9406631762652705 of holdout
events against 0.4909274193548387 of primary-window events.

**A DATA DEFECT SITS INSIDE THE HOLDOUT SPAN**, at 9.80. SOXS returns
-0.9457524782010531 on 2026-05-26 with no corporate action in the frozen record,
its close running 1159.5 on 2026-05-22 against 62.900001525878906 on 2026-05-26
while SMH rose 0.04480151130636223 across the same gap. **It contributes exactly
0.0 to holdout return**, since SOXS carries zero weight across the whole of
2026-05-18 to 2026-06-05, and it cannot enter through the signal path since SOXS
appears in `src/sleeves.py` at line 266 alone as a position.

**Session 29's gate B fired on that defect and its measurement phases did not
run.** The holdout nulls, the multi-factor decomposition, the interval estimates,
the NAV sensitivity and the instrument attribution were pre-registered at 9.79 and
none was computed. **The gate's disposition is not decided.** Repairing a frozen
input changes a hashed file, its manifest entry and the input-integrity check
every session runs.

**`docs/HOLDOUT-PREDICTION.md` is frozen at 9.64 and is not amended after the
read.** It stands as written.

**No frozen claim is contradicted and none is amended**, at 9.68. The holdout
bears on 8 of the 15 claims, 1 of which was evaluated in this session.

**The measurement phase is closed.** One measurement remains outstanding, being
S equal to 48 of the B1 re-emission, and it is not load-bearing.

## What this project is

A daily multi-model tactical allocation study, four sleeves at 25% budget each,
reconstructed from a QuantConnect source with every numeric parameter
re-specified and registered. The register is `docs/DECISIONS-v3.md`; canonical
values live in `src/config.py` (validate() runs on import).

## Custody and machine

`/Users/GualyCr/Downloads/tactical-allocation`, private remote at
`https://github.com/boomer25tiger/tactical-allocation`. `http.postBuffer` is
524288000 locally.

**The constraint on this machine is CPU contention, not memory.** Load average
reached 39.57 on eight cores with Chrome taking four of them, and a measured
pass received a mean of 6.25 percent CPU. Session 24 added the first supporting
completion observation, four of five stages completing at a load-to-core ratio
of 1.90 at launch against 4.9463 when session 22's pass failed, at 9.50. Report
compressor size, swap used, swap free and page-outs. **Do not quote free memory
as headroom**, since macOS holds free near zero by design.

## Position

- **Designated headline cell**, 0.521845 annualised and 1.381701 Lo-corrected
  Sharpe over 2,472 sessions, confirmed by positive control every session.
- **Holdout cell**, 0.8287111594113898 annualised and 2.7585227658215015
  Lo-corrected over 1265 sessions, read once at 9.66.
- **Combined window**, 3737 sessions, the strategy placing 2 of 12 on the naive
  Sharpe and 1 of 12 on the Lo-corrected. **Descriptive only**, since the
  combined window contains the sample the specification was chosen on.
- **The boundary is 2011-10-04** and session 15's outputs are rebuilt.
- **PBO 0.1578** at S equal to 16. **N is 121,500.** The figure re-emits
  exactly on repaired code, as do S equal to 8, 12 and 24, at 9.48.
- **The canonical ranks 6,834 of 121,500** on Lo-corrected Sharpe, with eight of
  nine axis values fixed before any comparison on that axis.

## The two claim-wording questions, settled

**The 8.2 grounds are recorded in the narrowed form at 9.61.** Buy-and-hold QQQ
sits outside its own null while the strategy sits inside its own, which holds.
The general form fails, since long_legs_only and vol_targeted_QQQ_matched both
outrank the strategy from inside their own nulls. 8.2 stands on the narrowed form
together with the q sweep moving nine of twelve rows in rank, the second being
independent of the null finding.

**Claim 4's scope phrase is narrowed at 9.59** to name only the block counts
re-emitted on repaired code. No quoted figure moved.

## The 8.2 decision, made

**Both Sharpe conventions are reported throughout, with the naive Sharpe
leading.** The grounds are that the strategy's Lo factor sits inside its own
no-autocorrelation null while buy-and-hold QQQ's sits outside, and that nine of
twelve ladder rows change rank across the unregistered q sweep. Registered at
8.2 as decided.

## Gate C of session 20, resolved

At 10,000 draws on the designated cell all four null and metric combinations
clear p below 0.001, the timing-shuffle annualised-return arm at seven
exceedances being p 0.00070 and the other three at zero. Every 1,000-draw count
is consistent with the new estimate. The earlier trip was a property of the
gate's resolution, since clearing p below 0.001 at 1,000 draws requires exactly
zero exceedances. Registered at 9.40.

## Statistics removed or withdrawn

The deflated Sharpe at 8.7, the degradation slope at 9.35, and the session 19.5
window strip at 9.36. The recentred comparison replaces the first.

## Findings that overturned prior sessions

- **The leave-one-out artifacts were already on the corrected boundary.** Base
  estimate identical to ten decimals. Session 21's F2 finding overturned, at
  9.41.
- **The 1.5636 agreement is structural, not coincidental**, at a gap of
  8.326e-07, since dropping calendar 2011 and starting at the first 2012 session
  remove very nearly the same sessions. Session 21 overturned, at 9.41.
- **The rolling beta extremes are estimation noise.** The standard deviation
  falls monotonically from 1.164612 at a 60-session window to 0.209 at 504. The
  timing component changes sign and the exposure-matched line beats the strategy
  only at the shortest window. Session 21 qualified, at 9.42.
- **The register's blocked-on-memory claims were wrong in mechanism**, corrected
  at 9.35 and 8.12.

## What remains before the paper

**The holdout is read and decomposed. Six robustification measurements remain
uncomputed**, being the holdout nulls, the multi-factor decomposition, the
interval estimates, the NAV sensitivity, the instrument attribution and the
leave-one-year-out convention restatement, all pre-registered at 9.79 and all
halted by gate B at 9.80. **The gate's disposition is the open question.**

What otherwise remains is writing, being the paper itself from the frozen claim
set, the withdrawn set, the prediction as written, the verdicts at 9.67 and the
decomposition at 9.70 through 9.78.

Seven claims bear on the holdout and were not evaluated at 9.68, being 2, 3, 11,
12, 13, 14 and 15. Claims 11 and 12 now have holdout counterparts from the beta
decomposition and claim 13 has one from leave-one-year-out, and whether those
counterparts are turned into evaluations against the frozen claims is a decision
that has not been taken.

**The outperformance is spread rather than concentrated**, all six calendar years
in the span carrying a positive arithmetic gap against buy-and-hold QQQ. One
observation over one macro regime remains the principal limitation.

## Formerly open before the holdout ran

**One measurement remains outstanding and it is not load-bearing.** Session 24
ran the B1 re-emission on a quiet machine and reached four of five block counts
before its wall limit fired, leaving S equal to 48 alone. **All four re-emitted
PBO values reproduce the reported figures exactly**, so the chunk-first-element
defect did not touch PBO and S equal to 48 sets neither endpoint of the reported
range. The corrected degradation null at 9.46 is not run and its slope is
withdrawn at 9.35 regardless. Registered at 9.48.

**The wall limit was mis-derived**, at 969 seconds taken from a single-chunk
pass against a sweep measuring 2424.37 seconds when first run, so the halt
reflects the limit rather than the machine. A wall limit for a multi-stage pass
is derived from that pass's own stage times. Registered at 9.49.
- **Ten config parameters have no consumer** and two more are read but never
  invoked, at 9.31.
- **`crash_threshold` was fixed after measurement on its own axis**, at 9.32.
- **SVIX and UVIX leave a code path that will not execute at the holdout read**,
  at 9.43. The loader is left unchanged deliberately.
- **D16 and D23 stand.**

## Defect register

D1 through D12, D14, D15, D17 through D22, D24 closed, repaired, or swept. D13
never assigned. D25 applied. D26 and D27 recorded. Open: **D16**, **D23**.

## Size convention

Repository size, working tree size and free space are read **before** the commit
and reported with the expected delta stated. No figure is read after the commit,
so no session ends with a dirty file carrying a post-commit reading. Adopted at
9.62 and applying from session 26 forward.

## Environment

Python 3.13.13, numpy 2.5.2, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1.
matplotlib deliberately absent.

## Figures

**The paper's figure cap is six and it is now reached**, fixed at 9.60 and
filled by the two at 9.69 in `outputs/session-27/figures/`. **No further figure
is drawn.** Eight further candidates are drawn, in `outputs/session-25/figures/`, each carrying the exact
series it plots as a committed CSV of the same name. Two candidates remain
undrawable, being the null distribution histograms and effective exposure by
decile, and three were excluded because the PBO report already carries them.
Plotting used `scripts/s19_svg.py` extended by `scripts/s25_svg.py`, with
`s19_svg.py` unmodified so session 19's four figures stay byte-identical.
matplotlib remains absent. Registered at 9.55 and 9.58.

**Seven claims have no figure anywhere**, being 2, 3, 7, 9, 10, 11 and 12, and
four of the eight figures illustrate no frozen claim. **The paper's two-figure
cap is analysed and not decided**, the one pair covering the most distinct
primary claims being leave-one-out with lo-factor-vs-null at three.

## What is frozen

44 ETF/fund parquets, 268 CFE VX CSVs, DTB3, NETR, and UVXY/SVXY issuer NAV, all
SHA-256 verified and truncated at 2026-08-14. 339 of 339 verified by session 19.5.
