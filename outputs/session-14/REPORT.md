# Session 14 — benchmark ladder and nulls

Run 2026-08-18. Scripts: `s14_common.py`, `s14_step0.py`, `s14_ladder.py`,
`s14_nulls.py`, `s14_misc.py`. Finding labels carried from sessions 13.5
through 13.9, being **[A]** explains a number without changing it, **[B]**
indicates a number is wrong or unreliable, and **[C]** a register or code
defect. The three standing corrections to session 13.9's report are used
throughout and the originals are not propagated.

## Step 0, the anchor verified [A]

**The cost model bound correctly in session 13.9 and no re-run was
needed.** Neither candidate explanation holds as stated. No column is
byte-identical between the 13.9 class-tier Arm S rows and the 13.8
uniform Arm F rows, the differences being 0.035 and 0.042 percentage
points on annualised return and 0.0049 and 0.0057 on Lo-corrected Sharpe,
and both pairs round to the same displayed figure, which is what produced
the apparent four-way match in the 13.9 summary prose. The commission arm
varies inside 13.9's own rows by 1.99 and 1.95 percentage points between
Arms F and Z, and the class tier map moves the level 2.03 percentage
points against the volume map on both panels.

What was wrong is the delta rows. The 13.9 delta loop selected the full
window for close-to-close while the levels quoted beside them were
primary-window, so full-window deltas of 1.63 and 1.31 percentage points
were printed against primary-window levels whose true delta is 2.03. The
inference that the true cells sit near 32.1 and 30.7 is what results from
applying those full-window deltas to 13.8's primary-window levels.
Corrected primary-window close-to-close Arm S levels are 31.66 percent
and 0.9774 on the synthetic panel and 29.98 percent and 0.9361 on the
realized panel.

## Step 0b, the participation cap [C, repaired]

Implemented as a correctness repair under the 7.14 precedent, with the
denominator a trailing 21-session median daily dollar volume lagged one
session and computed point-in-time, expanding where history is shorter
and excluding zero-volume sessions as the session 05 stored-record
artifact. The cap is 5 percent of that denominator, the capped remainder
routes to sleeve cash at DTB3 through the existing unfilled-slice path,
and the machinery applies to every instrument on identical terms.

BTAL binds on 189 transitions with a mean 89.8 percent of its target
routed to cash, running from 96 percent capped in 2012 to 66 percent in
2020 as its volume rose, and seven other instruments bind on 91
transitions between them in thin early years, being TECS 43, TECL 21,
SVXY 10, SOXL 8, PSQ 5, BSV 3, and TQQQ 1. BTAL's mean weight when held
falls from 8.48 to 0.86 percent and its arithmetic return contribution
from 2.47 to 1.03 percent. Held-session count is unchanged at 473,
because a capped position still admits whole shares. **The capped arm and
a full BTAL exclusion do not converge**, since the cap admits roughly a
tenth of the uncapped position and retains 42 percent of its
contribution. Instrument substitution was considered and rejected on
look-ahead grounds.

## Step 0c, the capped canonical and the positive control

**The uncapped arm reproduces session 13.9 exactly**, with deltas of
0.0000 on every panel, window, convention, and commission arm, which
establishes that the environment is the same one before the cap is
applied. The designated headline cell under 4.1b reads **52.26 percent
and 1.3846 capped, which is the canonical figure**, against **52.86
percent and 1.3742 uncapped, which is the continuity arm** and matches
13.9 to four decimals. The cap costs 0.60 percentage points of
annualised return and adds 0.0104 to the Lo-corrected Sharpe. Cap
sensitivity on the canonical specification only: 53.97 percent and 1.3930
at 10 percent, 53.31 percent and 1.3861 at 20 percent. All 48 sanity
checks pass across every panel, convention, and cap arm; the
execution-lag sensitivity check is reported rather than treated as
halting, per the 13.6 verdict and corrections item 12.

Capped canonical, commission Arm S, class tiers at the 10 basis point
anchor:

| panel | convention | window | ann return | vol | SR Lo | max DD | turnover |
|---|---|---|---|---|---|---|---|
| realized | o2o | primary | 52.26% | 48.8% | 1.385 | −53.1% | 37.9 |
| synthetic | c2c | primary | 31.64% | 52.9% | 0.972 | −66.5% | 40.8 |
| realized | c2c | primary | 29.71% | 50.7% | 0.929 | −64.6% | 40.7 |
| synthetic | c2c | full | 18.12% | 54.1% | 0.689 | −77.5% | 41.3 |
| realized | c2c | full | 21.36% | 44.8% | 0.716 | −68.9% | 37.5 |
| synthetic | c2c | early | −10.00% | 56.9% | 0.130 | −64.5% | 43.9 |

## Step 1, the benchmark ladder

Every line carries the identical cost model, being class tiers,
commission Arm S, the 10 basis point anchor, and the opening auction
premium on open-to-open lines only. Held-position lines enter at the
first session on or after the window start on which every named
instrument carries a price. **That entry rule is a repair made inside
this session**: emitting a held line at the warm-up boundary instead
produced an unavailable fill that never retried, which silently converted
buy-and-hold TQQQ and the matched-exposure line into cash holdings
reading 0.61 percent annualised at 0.0006 volatility on the first run.

Designated cell's window and convention, being the realized panel,
open-to-open, primary window, ordered by Lo-corrected Sharpe:

| line | ann return | vol | SR Lo | max DD | turnover | strategy alpha | beta |
|---|---|---|---|---|---|---|---|
| buy-and-hold TQQQ | 62.69% | 56.3% | **1.794** | −69.4% | 0.0 | +29.1% | 0.38 |
| buy-and-hold QQQ | 23.44% | 19.1% | **1.792** | −27.6% | 0.0 | +28.7% | 1.10 |
| matched-exposure levered QQQ 1.70 | 37.39% | 31.9% | **1.790** | −46.5% | 0.9 | +29.2% | 0.67 |
| long-legs-only | 61.13% | 48.5% | 1.461 | −51.5% | 28.1 | −4.3% | 0.98 |
| vol-targeted QQQ matched | 31.19% | 28.1% | 1.435 | −33.0% | 1.3 | +34.0% | 0.63 |
| **STRATEGY** | **52.26%** | **48.8%** | **1.385** | **−53.1%** | **37.9** | | |
| sleeve S2 standalone | 71.55% | 58.4% | 1.356 | −58.5% | 13.0 | +6.5% | 0.67 |
| sleeve S3 standalone | 60.82% | 61.2% | 1.195 | −60.0% | 21.6 | +9.6% | 0.67 |
| naive fast 1-day momentum | 26.57% | 38.6% | 1.075 | −56.1% | 64.7 | +43.0% | 0.34 |
| sleeve T11 standalone | 34.40% | 53.4% | 0.974 | −61.7% | 53.5 | +23.1% | 0.70 |
| equal-weight universe | 15.01% | 32.0% | 0.590 | −58.6% | 0.0 | +42.9% | 0.56 |
| sleeve T10 standalone | 4.84% | 70.4% | 0.507 | −86.6% | 52.7 | +38.2% | 0.53 |

The strategy ranks sixth of twelve on Lo-corrected Sharpe in its own
designated cell. Its alpha against every passive line is positive and
large, and its Sharpe sits below three passive lines and two
active ones. Close-to-close, primary window, the strategy ranks seventh
of twelve at 0.929 against buy-and-hold QQQ at 1.776 and buy-and-hold
TQQQ at 1.740. On the full window it ranks sixth of twelve at 0.716. On
the early window, synthetic panel, it ranks third of twelve at 0.130,
where only sleeve T11 standalone at 0.804 and sleeve S2 standalone at
0.248 read higher, with five lines negative on Lo-corrected Sharpe and
nine negative on annualised return, excluding the strategy from both
counts. *(Corrected 2026-08-19, session 15 step 9, from ladder.csv; the
original prose stated eight negative lines without naming the statistic.)*

The equal-weight universe line first fills 2015-05-29 on every window,
because LABU lists 2015-05-28 and the line requires every universe member
to be priced; that is recorded in the output rather than papered over.

## Step 2, the nulls

Two nulls per 8.9, 1,000 draws each as the register fixed before any
result existed, on the identical cost model. The timing shuffle permutes
the strategy's own 1,370 episodes, so the composition distribution and
the holding-period structure are preserved exactly and only placement in
time is randomised; the turnover-matched switching null draws
compositions at the measured rate of 99.7 transitions per year. Each
draw is charged the strategy's measured mean per-transition cost fraction
rather than re-deriving integer share counts, which is disclosed as the
one approximation.

| convention | window | null | observed | null p50 | null p95 | null max | p |
|---|---|---|---|---|---|---|---|
| o2o | primary | timing shuffle | 52.26% | −5.85% | 19.38% | 43.12% | 0.000 |
| o2o | primary | turnover-matched | 52.26% | −8.04% | 12.91% | 39.62% | 0.000 |
| c2c | primary | timing shuffle | 29.71% | −2.66% | 22.64% | 49.42% | 0.020 |
| c2c | primary | turnover-matched | 29.71% | −5.11% | 18.51% | 36.78% | 0.004 |
| c2c | full | timing shuffle | 21.36% | −2.15% | 15.15% | 31.96% | 0.011 |
| c2c | full | turnover-matched | 21.36% | −2.97% | 12.74% | 25.91% | 0.006 |

On Lo-corrected Sharpe the pattern holds, with one-sided p of 0.000 on
the designated cell and 0.005 to 0.013 on the close-to-close windows.
Both nulls place the strategy above the 98th percentile everywhere and at
the 100th on the designated cell, so **the ordering of the state sequence
in time carries the result**: holding the same compositions for the same
durations in a different order destroys it.

**The 8.10 Romano-Wolf family**, one-sided, stationary block bootstrap at
a 21-session block, 1,000 draws, on the designated cell:

| hypothesis | t | family-wise adjusted p |
|---|---|---|
| strategy − equal-weight universe | +2.29 | **0.033** |
| strategy − buy-and-hold QQQ | +2.20 | 0.052 |
| strategy − sleeve T10 standalone | +1.68 | 0.219 |
| strategy − vol-targeted QQQ | +1.53 | 0.240 |
| strategy − naive fast momentum | +1.34 | 0.324 |
| strategy − matched-exposure levered QQQ | +1.18 | 0.411 |
| strategy − sleeve T11 standalone | +0.91 | 0.563 |
| strategy − buy-and-hold TQQQ | −0.61 | 0.960 |
| strategy − sleeve S3 standalone | −1.14 | 0.983 |
| strategy − sleeve S2 standalone | −1.51 | 0.983 |
| strategy − long-legs-only | −1.55 | 0.983 |

After family-wise correction one comparison sits below 0.05. The
ensemble against the best single sleeve, being S2 standalone at a
Lo-corrected Sharpe of 1.356 against the strategy's 1.385, carries an
adjusted p of 0.983 and is disclosed as post-hoc under 9.10, joining the
family rather than standing as a separate test. Pairwise correlations of
the four standalone tracks run 0.354 to 0.717, the highest being S2
against S3.

## Step 3, the segment decomposition [A]

**Verdict: trade timing, not segment selection.** The strategy's
overnight leg contributes 3.582 in arithmetic sum against an intraday leg
of 2.621, an overnight share of 0.577, against 0.557 for an equal-weight
buy-and-hold of the traded universe and 0.685 for passive QQQ over the
same window. The strategy's share sits between the two passive
references rather than materially above either, so the open-to-open
advantage is not located in systematic overnight exposure and the paper
describes it as a property of when the strategy trades.

Recorded alongside, an overnight-only hold of the traded universe returns
8.50 percent annualised at a Lo-corrected Sharpe of 1.603 while an
intraday-only hold returns −6.48 percent at −2.026, so the universe's
return is concentrated overnight for passive and active holders alike.
The segment split is an attribution of a held position rather than a
separately tradeable line, since capturing it would require a daily round
trip the cost model would charge.

**The first computation of this decomposition returned the opposite
verdict** by pairing the lagged weight with the current session's
intraday move rather than the prior session's, which under open-to-open
attributes a segment the position did not hold. The reconciliation
control against the traded return caught it, with the mean absolute gap
falling from 63 to 7 basis points per session on correction.

## Step 4, the premium sweep [A]

| premium | ann return | SR Lo | above c2c on return | above c2c on Sharpe |
|---|---|---|---|---|
| 1.0x | 56.16% | 1.467 | yes | yes |
| 2.0x central | 52.26% | 1.385 | yes | yes |
| 3.0x | 47.54% | 1.295 | yes | yes |
| 4.0x ceiling | 41.90% | 1.196 | yes | yes |

The close-to-close comparison cell reads 29.71 percent and 0.929. The
convention gap survives the whole registered range on both statistics,
measured at every point rather than inferred from linearity. Bacidore and
Lipson's roughly 0.8x is **excluded rather than silently truncated**,
because their 1997 to 1998 NYSE specialist sample precedes decimalization
in 2001 and the electronic opening crosses introduced in 2004, so it
describes a mechanism that does not exist over a sample beginning in
2007. The direction is disclosed: were that relationship to hold, the
premium would be a discount and the cell would read higher.

## Step 5, the cost sweep [A]

The strategy under the capped canonical on the realized panel,
close-to-close, primary window, runs from 35.07 percent and 1.021 at
0 basis points to 10.80 percent and 0.548 at 50, so **neither the return
nor the Sharpe crosses zero inside the registered sweep**, which is a
change from the full-window crossings of 49 and 82 basis points that
sessions 13.8 and 13.9 measured.

The cost at which the strategy's advantage over a line vanishes is the
more informative object. Against buy-and-hold QQQ the return advantage
vanishes at 24 basis points and against vol-targeted QQQ at 13, while
against buy-and-hold TQQQ, the matched-exposure line, long-legs-only,
S2 standalone, and T11 standalone there is no crossing because the
strategy does not lead them at 0 basis points. On Lo-corrected Sharpe the
only crossings are against S2 standalone at 28.5 basis points and the
equal-weight universe at 45.

## Step 6, the entry reconciliation [B, resolved]

**There is no sign disagreement to reconcile, and session 13.8's positive
figure is a measurement artifact.** Session 13.6's figures reproduce
exactly on the realized panel and primary window, at −91.2 basis points
on 113 S3 observations and −43.8 on 131 T10 observations, against the −91
and −44 that session recorded. Every UVXY entry population is negative on
both panels and both windows, the all-entries population reading −79.6
basis points on the realized panel.

Session 13.8's +23 basis point figure came from an entry mask that
negated an object-dtype boolean series, where Python's integer bitwise
negation makes every element truthy, so the mask admitted held sessions
rather than entry sessions and inflated the count from 167 to 469.
Reproducing that mask returns the published +0.00234 at n=469 and
correcting it returns −0.00869 at n=167, which identifies the cause
rather than inferring it. **Session 13.9's step-5 resolution, that the
disagreement was a population and window difference, was derived from the
defective figure and is superseded.** The same defect class was found and
fixed inside this session in step 6's own first implementation.

## Step 7, the gate threshold recorded [C]

Recorded in the register at 4.1b: the session 13.9 step-4 gate was
written as negligible against material with no numeric boundary fixed
before the measurement, disclosed as post-hoc under 9.10. Two arguments
support the pass and neither was stated in the 13.9 report. The four
measured gaps carry mixed signs at −0.24, +0.66, −1.74, and +0.22
percentage points with a mean near −0.28, which is the signature of
estimation noise rather than of a systematic accumulation asymmetry,
which would carry a consistent sign. The largest single gap accounts for
7.6 percent of the 22.9-point convention effect being explained. The
control is not re-run and the gate is not reversed.

## Step 8, the decision audit reconciled [C]

**The eleven unreported items are the pre-result repairs**, being
corrections-list entries 1 through 11. The 13.9 summary listed three of
the six occupied cells plus a measurement total, which sums to 110; the
full three-axis cross-tabulation sums to 121.

| class | pre-result | post-result |
|---|---|---|
| choice | 55 | 22 |
| repair | **11** | 17 |
| measurement | 13 | 3 |

**The alternative explanation is ruled out by zero item overlap.** D17's
items are post-result choices and pre-result choices closed post-result;
the missing eleven are pre-result repairs, which carry no 9.10
requirement because no result existed when they were made. The coincident
count is arithmetic accident.

**Seven of the 22 post-result choices do not lie on any of the nine
recorded specification-curve axes.** The seven, read from
decision-audit-reconciled.csv, are the 4.6 NAV close, the 5.7 per-year
covariance, the Sharpe numerator registration, and the D5, D6, D7, and
D10 dispositions. Six are reporting or diagnostic conventions that do
not enter the return series. **Starting NAV under 4.6 is the
consequential one**, since it enters the return series through integer
truncation, the commission minimum, and now the step-0b cap, whose bite
scales with NAV, and the nine axes do not span it. *(Corrected
2026-08-19, session 15 step 9, from decision-audit-reconciled.csv; the
original prose named the 2.7a validation scoping, which the CSV does not
carry as off-axis, and omitted the 4.6, D6, and D7 items.)*

**D17 is closed.** All eleven items are retro-tagged with explicit 9.10
disclosures naming when each decision was made and what it governs. Its
composition is corrected: the eleven are eight post-result choices plus
three pre-result choices whose closure came after results existed.
**Ordering, stated rather than claimed**: the tags were written before
any ladder line comparison was read, but not before the session began,
so the ladder, the segment decomposition, and the premium sweep had
executed and their strategy-side figures were visible. The ordering the
prompt specified was partially achieved and the shortfall is recorded.

## Register updates, final text in DECISIONS-v3.md

- **4.6 amended** from a capacity note to an implemented cap, carrying the
  trailing point-in-time denominator, the 5 percent canonical level, the
  10 and 20 percent sensitivity arms, the uncapped continuity arm, the
  routing of capped remainder to sleeve cash under 1.9 and 2.11, the
  classification as a correctness repair under the 7.14 precedent, and
  the rejection of instrument substitution on look-ahead grounds.
- **4.4b** records the step 0 verification outcome with its evidence.
- **4.4a amended** with the Bacidore and Lipson exclusion and its reason.
- **4.1b amended** with the gate's post-hoc threshold status and the
  noise-signature and magnitude-share arguments.
- **4.1c** records the segment decomposition verdict and its consequence
  for how the open-to-open advantage is described.
- **9.11 reconciled** with the three-axis cross-tabulation, the ruled-out
  coincidence, and the seven off-axis post-result choices.
- **D17 closed** with the retro-tagging and the ordering statement.

## Provisional operating values

All five are closed or superseded as of session 13.8 and none changed
here. The surviving conventions are the pre-listing raw-price
back-extension and negative cash accruing DTB3 symmetrically, both
measured immaterial. The step-0b cap adds one operating convention, being
the exclusion of zero-volume sessions from the cap denominator as a
stored-record artifact under session 05.

## Defect register

| id | status |
|---|---|
| D1 through D12, D14, D15, D17 | closed or repaired |
| D13 | never assigned |
| D16 | open, financing spread remains assumed and swept 25 to 200 basis points |
| **D18 new [C]** | object-dtype boolean negation defect: session 13.8's ablation-mechanism entry rows are wrong and its +23 basis point UVXY entry figure is an artifact; the same class was found in this session's own first implementation of step 6. Documentation correction to 13.8's output plus a code-review pass for the pattern elsewhere. |
| **D19 new [C]** | held-position benchmark lines emitted before their instrument lists produce an unavailable fill that never retries, silently converting the line to cash. Repaired inside this session; the pattern would recur in any later session building benchmark lines. |
| **D20 new [C]** | starting NAV under 4.6 enters the return series but is not spanned by the nine recorded specification-curve axes. |

## What would have to change to act on each finding

- The strategy's Sharpe ranking against passive lines is a measurement,
  not a defect, and nothing needs to change to act on it; interpreting it
  is the paper's work.
- The Romano-Wolf outcome is a measurement under the registered family
  definition; changing the family is a **register decision**.
- D18 and D19 are **correctness repairs** already applied here, with the
  13.8 output correction outstanding as **documentation**.
- D20 is a **register decision**, being whether NAV joins the
  specification curve.
- The cap level, the premium value, and the tier anchors are
  **specification changes** requiring new measurement.
- The early-window reporting form remains a **register decision**.

No recommendation is made on any of them.

## What remains open before the 218,700-specification grid can run

1. The early-window reporting form, which 13.9 step 10 left to
   conversation and which this session did not revisit.
2. D16, the financing spread, treated by the widened sweep rather than
   resolved.
3. D20, whether starting NAV joins the specification-curve axes, which
   bears on what the curve is required to span.
4. The D18 documentation correction to session 13.8's ablation-mechanism
   output.
5. Confirmation that 8.7's N stays at grid size given the step 8
   reconciliation, which the register records and which no measurement in
   this session disturbs.

Nothing in the grid's own specification is open. The 7.10 product guard,
the axis tuples, and the canonical point are all pinned in config, and
`validate()` passes.

## Stop condition

Halted after step 10. No grid executed. No holdout executed and the
2021-08-01 boundary untouched. No deflated or probabilistic Sharpe
computed. No ablated specification adopted. No strategy parameter
changed. No instrument substituted. No impact charge added beyond the
step 0b cap. Nothing committed and the working tree is left dirty.
