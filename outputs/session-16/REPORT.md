# Session 16 — pre-grid closures, and the grid blocked

Run 2026-08-19. Scripts: `s16_pregrid.py`, `s16_step3.py`, `s16_step4.py`.
Finding labels carried from sessions 13.5 through 15.5, being **[A]** a finding
that explains a number without changing it, **[B]** a number wrong or
unreliable, and **[C]** a register or code defect.

## The grid did not run, and steps 6 through 9 did not run with it [C, D24]

**The grid is not runnable as registered.** The session prompt directs that the
axis tuples are pinned in config and that no grid may be constructed here.
Reading them out, `src/config.py` enumerates two axes, being `SMA_LONG_GRID` at
four values and `CRASH_THRESHOLD_GRID` at five, which is **20 of the 218,700
specifications, or 0.009145 percent**. The remaining factor of 10,935 is
`GRID_UNREPRESENTED_AXES_CARDINALITY`, a placeholder whose own comment in
config states that no decision in hand enumerates those axes' values.

The positive control passed before the negative finding was reported, with the
enumerator locating both known-present tuples. Eight axes the register names
are not enumerated anywhere, being the three function-tied RSI periods under
6.1 and 7.2, overbought tier one under 6.2 and 7.3, the tier-two offset under
7.4 which the register records as informed rather than closed, oversold under
6.4 and 7.5, short SMA under 6.6 and 7.8, and the S3 vote threshold under 6.7
and 7.9. The one oversold tuple that exists in the repository is a local
literal inside `scripts/s13_5_diagnostics.py` at line 374, which is a
diagnostic script rather than a registered axis. `validate()` passes because
7.10 pins the product against the placeholder rather than against the axes.

Enumerating them here would be constructing a grid, which the prompt prohibits,
and would also be a specification act, since what a study searches over
determines N in 8.7 and the shape of the specification curve under 9.11. **PBO,
the deflated Sharpe, the specification curve, and the PBO report all depend on
the grid and are unrun.** There was no panel to hash in step 10, none to delete
in step 11, and the manifest records that. Evidence:
`outputs/session-16/grid-blocker.csv`.

## Step 1, the 7.14 boundary moved to 2011-10-04 [C, repaired]

7.14 defines the primary window by containing no unavailable realized fills,
and the boundary was taken inclusive of the last such fill, which made the
definition false by one event. **Zero unavailable fills remain from 2011-10-04
on either panel or convention**, against one SVXY event at weight 0.0833 on
2011-10-03, whose cause is that SVXY's first priced session on the frozen panel
is 2011-10-04.

| cell | 2011-10-03 start | 2011-10-04 start |
|---|---|---|
| designated, open-to-open | 0.5226 and 1.3846 | **0.5218 and 1.3817** |
| realized close-to-close | 0.2971 and 0.9286 | **0.2962 and 0.9251** |

Both reproduce session 15's predicted figures to four decimals. Classified as a
correctness repair under the 7.14 precedent rather than a specification choice,
since the window's defining property was false as written. Pre-correction
figures carry forward for continuity and never as the anchor.

## Step 3, the effective exposure reconciliation [B, resolved]

Session 15.5's figures reproduce and session 13.5's do not. Measuring across
both panels, both conventions, both cap settings, and both windows, with the
conditioning statistics computed on full history and then sliced:

| claim | closest combination | values | distance |
|---|---|---|---|
| session 15.5, 1.776 / 1.042 / 1.490 | realized, open-to-open, cap on, primary | 1.777 / 1.051 / 1.499 | **0.013** |
| session 13.5, 1.70 / 0.78 / 1.06 | realized, open-to-open, cap on, full sample | 1.772 / 0.863 / 1.443 | 0.399 |

**Session 13.5's figures are superseded** and corrected in place. They were
measured before the SOXS split patch, the expense corrections, the
participation cap, and the boundary move, and no combination reproduces them.
The material consequence is for the strategy's description rather than for any
headline figure. Against a mean effective exposure of 1.777, the strategy does
de-exposure into the worst trailing-return decile at 1.051, a reduction of 41
percent, but the wildest volatility decile reads **1.499 rather than the 1.06
session 13.5 recorded**, a reduction of 16 percent. The de-exposure-into-stress
claim holds on the return axis and is substantially weaker on the volatility
axis than the standing figure stated.

Recorded as a method note: the decile conditioning is sensitive to whether the
rolling statistic is computed before or after the window slice, and slicing
first discards the 60 sessions of history the estimator needs and moves the
wildest-volatility figure by roughly 0.23.

## Step 4, leave-one-year-out [A]

Eleven leave-one-out estimates on the corrected primary window, against a base
Lo-corrected Sharpe of 1.3817:

| dropped | ann return | SR Lo | max DD | IR vs QQQ |
|---|---|---|---|---|
| none (base) | 0.5218 | 1.3817 | −0.5306 | 0.7023 |
| 2011 | 0.5809 | 1.5636 | −0.5306 | 0.7997 |
| 2012 | 0.5598 | 1.3042 | −0.5306 | 0.7667 |
| 2013 | 0.5142 | 1.4100 | −0.5306 | 0.7203 |
| 2014 | 0.4965 | 1.3323 | −0.5306 | 0.6536 |
| 2015 | 0.5422 | 1.3856 | −0.5306 | 0.6970 |
| 2016 | 0.5715 | 1.4799 | −0.5306 | 0.7317 |
| 2017 | 0.5547 | 1.4471 | −0.5306 | 0.7767 |
| 2018 | 0.4869 | 1.2871 | −0.5306 | 0.5885 |
| 2019 | 0.4956 | 1.3287 | −0.5775 | 0.6873 |
| **2020** | **0.4350** | **1.6183** | **−0.4469** | 0.6205 |
| 2021 | 0.5052 | 1.3248 | −0.5306 | 0.6805 |

**The Lo-corrected Sharpe range across the eleven estimates is 1.2871 to
1.6183**, and the year whose removal moves it most is **2020, which raises it
to 1.6183**. Dropping 2020 lowers annualised return from 0.5218 to 0.4350 and
improves maximum drawdown from −0.5306 to −0.4469, so 2020 supplied return and
drawdown together and was a net drag on the risk-adjusted figure rather than
its driver. That runs against what four separate concentration measurements
implied, and it is the reading that bears on the holdout, whose bear market is
of a different character.

Per sleeve the ranges are wider, being 0.3645 to 0.8760 for T10 against a base
of 0.5189, 0.7771 to 1.3905 for T11 against 0.9739, 1.2079 to 1.5569 for S2
against 1.3271, and 1.0287 to 1.5454 for S3 against 1.1959, and no sleeve's
most-influential year is 2020.

The short leg through the crash contributes **−0.1649 across February to April
2020 on seven entries and six exits**, against −0.253 for the full year and
−0.4826 across the primary window, so the crash quarter carries 65 percent of
the short leg's worst year and 34 percent of its whole-window loss.

## Step 0, documentation debt cleared [C, closed]

`docs/STATE.md` is refreshed to the session 16 position and **D22 is closed**.
It previously stated that the backtest had never been run and named session 13
as the immediate next step, so sessions 13 through 15.5 each opened on a stale
entry point. A dated erratum row was appended to
`outputs/session-13.8/ablation-mechanism.csv` under **D18**, naming the cause at
`scripts/s13_7_mechanism.py` line 114 and recording the published +0.00234 on
469 observations against the corrected −0.00869 on 167, with the historical rows
retained unedited.

## Step 2, register closures

**D20 NAV** joins the specification curve and not the grid axes, on the grounds
that the curve is a reported sensitivity surface already measured at five levels
while the grid is a search over strategy specifications and NAV is an account
property whose addition would multiply the grid fivefold and inflate 8.7's N
with an axis nobody selected on. **The early-window form** reports coverage
tables and the availability timeline only, with no return figure at any
prominence. **SH** is recorded as a signal input rather than a tradeable
universe member, since it appears in no weight dictionary and enters only
through the AGG against SH comparison.

## Step 10, corrections

Five prose errors corrected in place, each with a dated note naming the CSV it
was read from. In `outputs/session-15/REPORT.md`, the step 4 lead-set list now
names buy-and-hold QQQ, buy-and-hold TQQQ, the matched-exposure line, and
long-legs-only rather than omitting the first and wrongly including S2 and S3;
the step 3 information-ratio claim now states that the strategy trails five
lines and that the ratio's sign tracks active return in eleven of eleven cases;
and the step 6 cap channel now carries the canonical figures. In
`outputs/session-15.5/REPORT.md`, arm B_all's maximum-drawdown delta of +0.02 is
corrected from worsening to an improvement of two percentage points, since
maximum drawdown is negative and +0.02 against −0.5306 gives −0.5106, confirmed
independently by the cost sweep at −0.5084 against −0.5281; and the arm A
exposure figures now carry the step 3 reconciliation.

## The 9.12 report-figure check

`scripts/check_report_figures.py` was run against every report this session
touched. This report returns **18 unmatched figures out of 104**, session 15's
returns 5 of 216, and session 15.5's returns 4 of 193. Every unmatched figure
here was confirmed by hand and falls into three groups, being register
identifiers, which are prose tokens shaped like figures and are 7.10, 7.14, 7.5,
7.8, 7.9 and 8.7, path fragments from the directory names `session-13.8` and
`session-15.5`, and figures carried from earlier sessions with attribution,
being the D18 pair 0.00234 and 0.00869, the two exposure claims 1.70, 1.06,
1.776 and 1.042 that step 3 reconciles, the session 15.5 cost-sweep drawdowns
0.5084, 0.5281 and the derived 0.5106, and the SVXY event weight 0.0833 from
session 15's D19 sweep.

Recorded per the session prompt: the checker's comparison threshold moved from
five to six decimal places in session 15.5, and that threshold is **a post-hoc
choice, disclosed**, made after three figures from that session's own CSVs were
reported unmatched at the five-place limit. The mechanism remains partial, since
it catches numeric drift between prose and the emitted CSVs and does not catch a
miscounted or misnamed claim, which is how four of the five errors corrected in
step 10 reached publication.

## Provisional operating values

All are closed or superseded as of session 13.8 and none changed here. The
surviving conventions are the pre-listing raw-price back-extension, negative
cash accruing DTB3 symmetrically, and the exclusion of zero-volume sessions from
the cap denominator, all measured immaterial.

## Defect register

| id | status |
|---|---|
| D1–D12, D14, D15, D17, D18, D19 | closed, repaired, or swept |
| D13 | never assigned |
| D16 | open, financing spread assumed and swept 25 to 200 basis points |
| D20 | **CLOSED** step 2, NAV on the curve and not the grid |
| D21 | **CLOSED** step 1, boundary moved to 2011-10-04 |
| D22 | **CLOSED** step 0, STATE.md refreshed |
| D23 | open, portfolio-level per-instrument attribution confound, corrected in place session 15.5 |
| **D24 new [C]** | the grid axes are not enumerated. 20 of 218,700 specifications are constructible from config; the closure belongs in the register under 7.2 through 7.9 |
| **D25 new [B]** | session 13.5's effective-exposure figures do not reproduce on any combination and are superseded; the de-exposure-into-volatility-stress claim is weaker than recorded |

## What would have to change to act on each finding

- **D24** is a **register decision**, being the enumeration of the grid axes
  under 7.2 through 7.9, and it blocks the grid, PBO, the deflated Sharpe, and
  the specification curve.
- **D25** is **documentation**, already corrected in place, with the
  consequence for the strategy's written description carried into the paper.
- The leave-one-out range and the 2020 reading are **measurements** and need no
  change to act on.
- **D16** is a **register decision**, treated by the widened sweep.
- **D23** is a **correctness repair**, applied in session 15.5.

No recommendation is made on any of them.

## What remains open before the holdout can run

1. **D24**, the grid axis enumeration, which blocks the grid and everything
   downstream of it.
2. **PBO, the deflated Sharpe, and the specification curve**, all of which
   require the grid.
3. **D16**, the financing spread.

The holdout stays untouched and the 2021-08-01 boundary under 2.10 is not
approached by anything in this session.

## Stop condition

Halted after step 13. No holdout executed and the 2021-08-01 boundary
untouched. No grid point adopted or promoted, since the grid did not run. No
strategy parameter, threshold, instrument, weight, sleeve budget, cost model,
cap level, premium, or NAV changed. The step 12 commit is the only commit.
