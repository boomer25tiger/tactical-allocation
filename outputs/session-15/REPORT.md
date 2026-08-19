# Session 15 — metrics completion and integrity pass

Run 2026-08-19. Scripts: `s15_step12.py`, `s15_lines.py`, `s15_metrics.py`,
`s15_rest.py`, `check_report_figures.py`. Finding labels carried from
sessions 13.5 through 14, being **[A]** a finding that explains a number
without changing it, **[B]** a number wrong or unreliable, and **[C]** a
register or code defect. The three standing corrections to session 14's
report were verified against the CSVs before use and are applied
throughout.

## Steps 1 and 2, the integrity checks, both clean

**D18, the object-dtype negation defect class [C, bounded].** The
detector was validated first, flagging the object-dtype control where the
negation returns −1 and −2 and passing the bool-dtype control where it
returns True and False. **78 negation sites were scanned and none lies in
the return-generating path**, which carries no negation of any kind
across src/config.py, src/data.py, src/indicators.py, src/sleeves.py,
src/portfolio.py, src/schedule.py, src/execution.py,
scripts/s13_backtest.py, and scripts/s14_common.py. The halt condition
was not met and no canonical figure is affected.

Two defective sites exist, both in diagnostic scripts and both confirmed
object-dtype at runtime, being scripts/s13_7_mechanism.py line 114 which
produced session 13.8's entry-split rows, and scripts/s13_9_controls.py
line 137 which produced session 13.9's entry reconciliation.
**Session 13.8's ablation-mechanism conclusions survive.** The overlay
decomposition is built from a comparison-derived bool mask rather than
the defective entry mask, and recomputation returns +5.5830 directional
against a published +5.5838, −4.8240 roll against −4.8242, and −0.0086
reset against −0.0086, with the residual differences arising from the
session 14 participation cap rather than from the mask. Only the
entry-split rows are wrong, at a published +0.00234 on 469 observations
against a corrected −0.00869 on 167.

**D19, silent fill failures [C, none found].** The detector was validated
by injecting an unfillable LABU target into 2013 against a 2015-05-28
listing, confirming detection and the absence of a false positive on the
unmodified series. **Zero silent shortfalls were found on any window or
convention.** At fill sessions the target dollars minus deployed position
value minus recorded cap remainder minus recorded unavailable-fill weight
leaves a residual whose maximum is 0.3 percent of NAV and whose content
is integer truncation. The cap and unavailable-fill paths do not
double-count, with zero events routing more to cash than the target
carried across 362 close-to-close and 574 open-to-open cap events.

Recorded as a detector-design note, the first implementation compared
carried-forward target gross against realized gross on every session and
flagged 16.5 percent of the primary window, which is drift that 5.2
permits with no calendar reset rather than a fill failure, so the
detector runs at fill sessions only.

**New finding [B/C], the 7.14 boundary is off by one session.** 7.14 sets
the primary window at the last unavailable realized fill and the boundary
was taken inclusive of that session, so the window's defining property
that it contains no unavailable fills is false by one event. SVXY's first
priced session on the frozen panel is 2011-10-04, so a 2011-10-03 target
on it at weight 0.0833 cannot fill. Starting the window at 2011-10-04
moves the designated cell from 52.26 percent and 1.3846 to 52.18 percent
and 1.3817, and the close-to-close cell from 29.71 percent and 0.9286 to
29.62 percent and 0.9251. The boundary is not changed here.

## Step 3, metrics completion

The positive control reproduced all eight session-14 statistics for the
designated cell and for buy-and-hold QQQ with **zero mismatches at four
decimals** before any new metric was emitted. The metric set is fixed at
**41 standalone metrics the grid emitter carries per specification** and
**12 benchmark-relative metrics the emitter carries only for the ladder
lines 8.8 fixes**.

**The information ratio placed beside every alpha**, designated cell,
open-to-open realized primary window, ordered by Lo-corrected Sharpe:

| line | SR Lo | information ratio | alpha ann | alpha t (NW 21) | tracking error | R² | up-capture | down-capture |
|---|---|---|---|---|---|---|---|---|
| buy-and-hold TQQQ | 1.794 | **−0.194** | +0.291 | 2.42 | 0.562 | 0.189 | 0.363 | 0.255 |
| buy-and-hold QQQ | 1.792 | +0.704 | +0.287 | 2.35 | 0.441 | 0.185 | 1.078 | 0.767 |
| matched-exposure levered QQQ | 1.790 | +0.376 | +0.292 | 2.42 | 0.452 | 0.189 | 0.640 | 0.450 |
| long-legs-only | 1.461 | **−0.494** | −0.043 | −1.25 | 0.112 | 0.947 | 0.935 | 0.942 |
| vol-targeted QQQ | 1.435 | +0.489 | +0.340 | 2.61 | 0.466 | 0.133 | 0.713 | 0.493 |
| **STRATEGY** | **1.385** | | | | | | | |
| sleeve S2 standalone | 1.356 | **−0.483** | +0.065 | 0.76 | 0.355 | 0.632 | 0.628 | 0.596 |
| sleeve S3 standalone | 1.195 | **−0.365** | +0.096 | 1.10 | 0.337 | 0.698 | 0.663 | 0.626 |
| naive fast momentum | 1.075 | +0.427 | +0.430 | 3.19 | 0.535 | 0.072 | 0.391 | 0.116 |
| sleeve T11 standalone | 0.974 | +0.291 | +0.231 | 2.47 | 0.351 | 0.590 | 0.746 | 0.668 |
| equal-weight universe | 0.590 | +0.730 | +0.429 | 3.42 | 0.475 | 0.135 | 0.716 | 0.373 |
| sleeve T10 standalone | 0.507 | +0.538 | +0.382 | 4.48 | 0.460 | 0.579 | 0.583 | 0.481 |

The strategy trails five lines on Lo-corrected Sharpe, and the
information ratio's sign tracks active return rather than the Sharpe
ordering, matching active return in eleven of eleven cases and the Sharpe
lead in six of eleven, which follows from the definition since the ratio's
numerator is mean active return. *(Corrected 2026-08-19, session 16 step
10, from metrics-full.csv.)* Against buy-and-hold
TQQQ the alpha is +0.291 at a Newey-West t of 2.42 while the information
ratio is −0.194, at a tracking error of 56.2 percent.

Strategy distributional and drawdown figures on the designated cell:
Sortino at a DTB3 minimum acceptable return 1.531, downside deviation
34.8 percent, skewness +0.417, excess kurtosis 8.230, daily value at risk
−4.2 percent at 95 and −7.5 percent at 99 with conditional value at risk
−6.7 and −11.5 percent. Maximum drawdown duration 70 sessions and 99
calendar days, **recovered inside the window in 59 sessions**, 13
drawdowns exceeding 20 percent, Ulcer index 14.98, pain ratio 3.49.
Stability: rolling twelve-month Sharpe from −0.237 to 2.944 with 1.8
percent of windows below zero, 59.3 percent positive months, and
split-half Lo-corrected Sharpe of 1.449 and 1.481 on the two halves of
the primary window.

## Step 4, cost sweep on the designated cell

Stacking rule pre-registered before the run: the uniform sweep replaces
the tiered slippage and the auction premium rather than stacking on them,
since the uniform arm bounds sensitivity to an assumed cost level and
adding it to a calibrated model would double-charge. Commission Arm S and
the cap are unchanged across the sweep.

The strategy runs from 59.59 percent and 1.5605 at 0 basis points to
37.02 percent and 1.0924 at 50, so **neither the return nor the
Lo-corrected Sharpe crosses zero inside the registered sweep**. Session
14's break-even figures of 24 basis points against buy-and-hold QQQ and
13 against the vol-targeted line described the close-to-close cell and do
not describe the headline. On the designated cell the strategy does not
lead buy-and-hold QQQ, buy-and-hold TQQQ, the matched-exposure line, or
long-legs-only at 0 basis points on Lo-corrected Sharpe, so no crossing
exists against those four; it does lead S2 standalone, whose Sharpe
crossing is at 44.165732 basis points, and S3 standalone. *(Corrected
2026-08-19, session 16 step 10, from cost-sweep-designated.csv, whose
`strategy_leads_at_0bp_sharpe` column carries the four False values named
here; the original prose omitted buy-and-hold QQQ and wrongly included S2
and S3.)*

## Step 5, per-instrument per-year contribution

**BTAL's capped contribution concentrates in 2020, which carries 43.1
percent of its absolute contribution**, and four years account for 80
percent of it. Per unit of weight the capped position is more productive
than the uncapped one because the cap is near-total in the thin years
from 2012 to 2019 and near-inert in 2020, when BTAL's trailing median
dollar volume reached 2.36 million against 22 to 32 thousand earlier.

Against the portfolio, BTAL's concentration is high but not extreme. The
strategy as a whole carries 21.7 percent of its absolute contribution in
its largest year, also 2020, and needs seven years to reach 80 percent.
Sleeve concentration runs from 16.4 percent for T10, largest year 2014,
to 24.0 percent for S2, largest year 2020. Instruments more concentrated
than BTAL include QLD at 72.3 percent, SPXL at 57.6, and LABU at 51.0,
each on a small total contribution. UVXY, the largest single contributor
at +1.955 arithmetic, carries 37.5 percent in 2020 and needs five years
to reach 80 percent. No judgement is made about whether the
concentration is acceptable.

## Step 6, the NAV sweep

| NAV | designated cell ann | SR Lo | c2c ann | c2c SR Lo |
|---|---|---|---|---|
| 100,000 | 53.16% | 1.3804 | 29.93% | 0.9350 |
| 250,000 | 53.27% | 1.3849 | 30.13% | 0.9383 |
| **1,000,000 canonical** | **52.26%** | **1.3846** | **29.71%** | **0.9286** |
| 5,000,000 | 37.80% | 1.2392 | 23.24% | 0.7604 |
| 25,000,000 | 22.60% | 0.9643 | 14.29% | 0.5427 |

The summary elasticity is **−0.127 annualised return and −0.174
Lo-corrected Sharpe per decade of NAV**, and the relationship is not
log-linear, being flat from 100,000 to 1,000,000 and steep above it, so
that figure understates the upper range and overstates the lower.

The three channels separate cleanly and only one carries the effect.
Integer truncation falls from 0.027 percent of target dollars at 100,000
to 0.0004 percent at 25,000,000 and is immaterial throughout. The Arm S
commission minimum binds on 31.1 percent of orders at 100,000 and 7.9
percent at 25,000,000. **The participation cap carries the effect**,
routing 1.15 percent of target dollars to cash at 100,000 and 36.2
percent at 25,000,000, with cap-binding instruments rising from 2 names
to 14. At the canonical NAV on the open-to-open convention the cap binds
**ten instruments across 574 events routing 5.2285 percent of target
dollars** to sleeve cash. *(Canonical figures added 2026-08-19, session 16
step 10, from nav-sweep.csv; the original prose reported the sweep
endpoints only.)* No register decision is made; whether NAV joins the
specification-curve axes is decided in conversation from this output.

## Step 7, the close-to-close execution-lag anomaly

| convention | T+1 | T+2 | T+3 |
|---|---|---|---|
| close-to-close ann return | 29.71% | 47.24% | 35.32% |
| close-to-close Lo Sharpe | 0.9286 | 0.8601 | 0.9068 |
| open-to-open ann return | 52.26% | 31.53% | 34.04% |
| open-to-open Lo Sharpe | 1.3846 | 0.7389 | 0.7843 |

The effect is convention-dependent and **non-monotone under
close-to-close**, where T+2 exceeds both T+1 and T+3, while open-to-open
falls at T+2 and stays near that level at T+3.

**The close-to-close difference is highly concentrated: the top twenty
sessions carry 85.7 percent of the T+2 minus T+1 arithmetic sum.** The
largest is 2020-03-16 at +0.448 while the strategy held TECL, TQQQ, and
SOXL through the COVID crash, followed by 2014-07-17 at +0.214 and
2020-02-24 at +0.194. By year the difference is +1.030 in 2020 and +0.636
in 2014 against −0.635 in 2017 and −0.200 in 2016. By instrument it sits
in SQQQ at +0.370, TQQQ at +0.325, and SOXL at +0.262. By sleeve under
close-to-close it is positive for S3 at +2.315, S2 at +1.315, and T11 at
+0.763 and negative for T10 at −0.278, while under open-to-open the signs
largely reverse, with T11 at −2.882 and S3 at −2.088. No disposition is
made and the 13.6 verdict and corrections item 12 stand.

## Step 8, the segment hold lines relabelled and charged

| line | variant | line_kind | ann return | SR Lo |
|---|---|---|---|---|
| overnight-only hold | uncharged | attribution | +8.49% | 1.597 |
| overnight-only hold | charged | benchmark_tradeable | **−28.69%** | **−4.999** |
| intraday-only hold | uncharged | attribution | −6.48% | −2.026 |
| intraday-only hold | charged | benchmark_tradeable | **−38.54%** | **−12.264** |

One round trip per session carries the class tier figure once, that
figure already being a round-turn cost, with the 4.4a premium applied to
the leg executing at the open and Arm S commission on both legs of every
position at the canonical NAV. **Neither segment is tradeable at the cost
model the strategy is charged**, which is why the 4.1c verdict rests on
the share comparison rather than on these lines. The `line_kind` values
are **attribution** and **benchmark_tradeable**.

## Step 9, report generation from data

Three session 14 prose figures were corrected in place, each with a dated
note naming the CSV it was read from.

1. The early-window negative-line count, at outputs/session-14/REPORT.md
   line 121, from eight to five negative on Lo-corrected Sharpe and nine
   negative on annualised return, excluding the strategy from both
   counts, read from ladder.csv.
2. The off-axis item list, at outputs/session-14/REPORT.md lines 296 to
   303 and mirrored in the register at 9.11, from a list naming the 2.7a
   validation scoping and the D5 and D10 dispositions to the seven items
   decision-audit-reconciled.csv carries, being the 4.6 NAV close, the
   5.7 per-year covariance, the Sharpe numerator registration, and the
   D5, D6, D7, and D10 dispositions.
3. The positive-control figures, at outputs/session-14/REPORT.md lines 61
   to 63, reordered so the capped 52.26 percent and 1.3846 is named as
   the canonical figure and the uncapped 52.86 percent and 1.3742 as the
   continuity arm.

The enforcement mechanism is `scripts/check_report_figures.py`, which
re-derives every decimal figure in a session report and reports those it
cannot locate in that session's own CSVs in level or percentage form. On
this report it returns **three unmatched figures out of 212**, being the
uncapped continuity-arm pair 52.86 and 1.3742 carried from session 14's
canonical-capped.csv and confirmed against it by hand at 0.528636 and
1.374174, and one register identifier its context filter missed.

**The mechanism is partial and the limitation is recorded rather than
left implicit.** Run retrospectively against session 14 it returns
thirteen unmatched figures, none of which is one of the three errors that
session actually carried, because two of those three were not decimal
figures at all, one being a count spelled as a word and one being a list
of item names. The mechanism catches numeric drift between prose and the
emitted CSVs and does not catch a miscounted or misnamed claim, so
non-numeric claims still require the hand check that found these three.

## Register updates, final text in DECISIONS-v3.md

- **D18 defect class swept**, recording 78 sites, zero in the
  return-generating path, the two defective diagnostic sites, and the
  survival of session 13.8's ablation-mechanism conclusions.
- **D19 silent fill failures swept**, recording zero occurrences, the
  cap and unavailable-fill paths not double-counting, and the
  detector-design note about drift.
- **7.14 boundary off by one session**, recording the SVXY event, the
  effect of moving the start to 2011-10-04, and that the boundary is not
  changed here.
- **8.11 metric set**, fixing 41 standalone and 12 benchmark-relative
  metrics, the Newey-West lag of 21 sessions fixed before the run with
  the Andrews bandwidth alongside, and that the information ratio is
  reported wherever an alpha is reported and an alpha is never reported
  alone.
- **4.4 stacking rule**, recording that the uniform sweep replaces the
  tiered slippage and the premium rather than stacking on them.
- **4.6c NAV sweep**, recording the five levels, the three channels, the
  non-log-linear shape, and the axis-membership decision left open.
- **4.1c amended**, recording the segment hold lines relabelled to
  attribution and benchmark_tradeable with their charged figures.
- **9.12 report generation**, recording the rule and the enforcement
  mechanism.

## Provisional operating values

All five are closed or superseded as of session 13.8 and none changed
here. The surviving conventions are the pre-listing raw-price
back-extension, negative cash accruing DTB3 symmetrically, and the
exclusion of zero-volume sessions from the cap denominator as a
stored-record artifact under session 05, all measured immaterial.

## Defect register

| id | status |
|---|---|
| D1 through D12, D14, D15, D17 | closed or repaired |
| D13 | never assigned |
| D16 | open, financing spread assumed and swept 25 to 200 basis points |
| D18 | **swept and bounded**, zero sites in the return-generating path, two diagnostic sites confirmed, session 13.8's entry-split rows wrong and its overlay conclusions intact |
| D19 | **swept, zero occurrences** in the strategy's own series on any window or convention |
| D20 | open, NAV enters the return series and is not spanned by the nine axes; step 6 measures the magnitude |
| **D21 new [B/C]** | the 7.14 primary window boundary is inclusive of the last unavailable fill, so one SVXY event sits inside it; effect on the designated cell is −0.08 percentage points of return and −0.0029 Lo-corrected Sharpe |
| **D22 new [C]** | docs/STATE.md is stale as of session 12.5, still stating that the backtest has never been run and naming session 13 as the immediate next step, while carrying two updated limitation entries from session 13.7 |

## What would have to change to act on each finding

- D18's two diagnostic sites are **correctness repairs**, with the
  session 13.8 entry-split output correction outstanding as
  **documentation**.
- D21, the 7.14 boundary, is a **register decision**, being whether the
  window starts 2011-10-03 or 2011-10-04.
- D22, STATE.md, is **documentation**.
- D20, whether NAV joins the specification-curve axes, is a **register
  decision** that step 6 now measures.
- The metric set, the stacking rule, and the segment relabelling are
  **recorded** and require nothing further.
- The execution-lag anomaly is a measurement with no disposition; acting
  on it is a **register decision** left open.
- The cap level, the premium, and the tier anchors remain
  **specification changes** requiring new measurement.

No recommendation is made on any of them.

## What remains open before the 218,700-specification grid can run

1. **D20**, whether NAV joins the specification-curve axes. Step 6 shows
   the cap channel moves the designated cell's Lo-corrected Sharpe from
   1.3846 to 0.9643 across the swept range, so the answer changes what
   the grid must span.
2. **D21**, the 7.14 boundary, which fixes the primary window every grid
   specification reports on.
3. The early-window reporting form, which sessions 13.9 and 14 left to
   conversation and which this session did not revisit.
4. **D16**, the financing spread, treated by the widened sweep rather
   than resolved.
5. The D18 documentation correction to session 13.8's ablation-mechanism
   entry-split rows.
6. **D22**, refreshing STATE.md, which the next session reads first.

The grid's own specification is not open. The 7.10 product guard, the
axis tuples, and the canonical point are pinned in config, validate()
passes, and the metric set the emitter must carry is now fixed under
8.11.

## Stop condition

Halted after step 11. No grid executed. No holdout executed and the
2021-08-01 boundary untouched. No deflated or probabilistic Sharpe
computed. No specification changed, no strategy parameter changed, no
instrument substituted, no threshold moved. Canonical NAV unchanged at
1,000,000, and the cap level, tier map, and auction premium unchanged. No
ablated specification adopted. Nothing committed and the working tree
left dirty.
