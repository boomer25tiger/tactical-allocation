# Session 15.5 — PSQ hedge instrument and hedge intensity, diagnostic only

Run 2026-08-19. Script: `scripts/s155_arms.py` with the step 7 correction in
`scripts/s155_step7fix.py`. Finding labels carried from sessions 13.5 through
15, being **[A]** a finding that explains a number without changing it,
**[B]** a number wrong or unreliable, and **[C]** a register or code defect.

**Nothing measured here is adopted.** The canonical specification is unchanged
and every arm is a labelled diagnostic arm reported alongside the canonical,
never in place of it. Post-hoc under 9.10, since the comparison was motivated
by a visible result, being SQQQ's primary-window contribution decomposing into
−39.35 beta and −0.05 residual in session 13.5.

The three standing corrections to session 15's report were verified against the
CSVs before use. On the designated cell the strategy trails five ladder lines
on Lo-corrected Sharpe, the information ratio's sign tracks active return in
eleven of eleven cases and the Sharpe lead in six of eleven, `strategy_leads_at_0bp_sharpe`
is False for buy-and-hold QQQ, buy-and-hold TQQQ, the matched-exposure line and
long-legs-only and True for S2 with a Sharpe crossing at 44.165732 basis points
and True for S3, and the cap at the canonical NAV on the open-to-open convention
binds ten instruments across 574 events routing 5.2285 percent of target dollars
to sleeve cash.

## Step 3, the positive control

Arm A reproduces the session 15 canonical exactly on the designated cell at
**0.5226 annualised and 1.3846 Lo-corrected Sharpe**, and T10 standalone at
**0.0484 and 0.5070**, both matching to four decimals. Every figure below is
read as a delta against arm A.

## Step 2, the arm registration, fixed before any arm ran

| arm | short leg | branch weights | short notional | role |
|---|---|---|---|---|
| A | SQQQ | 50% SQQQ, 50% TLT | −0.375 | canonical, positive control |
| B | PSQ | 50% PSQ, 50% TLT | −0.125 | direct swap at equal weight |
| C | SQQQ | 16.667% SQQQ, 50% TLT, 33.333% cash | −0.125 | notional twin of B |
| D | SQQQ | 33.333% SQQQ, 50% TLT, 16.667% cash | −0.25 | intensity curve |
| E | PSQ | 100% PSQ | −0.25 | reported, CONFOUNDED |
| F | none | 100% TLT | 0.0 | no-short control |
| B_all | PSQ | as B, sleeve-wide | −0.125 | SECONDARY |

Notional matching above −0.25 is unreachable with PSQ, since the canonical
−0.375 would need 150 percent of the branch and breach the 5.3 gross cap,
recorded as a structural constraint of the −1x expression. Arm E reaches −0.25
only by displacing TLT entirely, so it changes two things at once and is
excluded from the instrument comparison.

## Step 1, the short-leg sites [A]

SQQQ appears in **four sites across three sleeves**, being T10's rs-bear
terminal at weight 0.5, T11's bull-short basket at 0.3333, both T11 bear
sub-model terminals at 0.5, and S2's defensive state at 1.0, with primary-window
firing rates of 20.74, 19.29, 19.29 and 2.99 percent of sleeve-sessions. PSQ
appears only in T11's bear sub-model terminals at 0.5, firing on 3.6 percent.
**SH appears in no weight dictionary anywhere in the return-generating path**
and enters only as the right side of the AGG>SH pairwise comparison. Leverage
multiples read from src/schedule.py are −3.0 for SQQQ and −1.0 for PSQ and SH.
Because a T10-only substitution leaves SQQQ in three other sites, arm B_all
applies the swap sleeve-wide and is reported separately.

## Step 5, the instrument effect at fixed notional [A]

Arms B and C both carry −0.125 short notional with identical TLT exposure, and
on the designated cell arm B minus arm C reads:

| metric | arm B | arm C | B − C |
|---|---|---|---|
| annualised return | 0.54681 | 0.5493 | **−0.00249** |
| annualised volatility | 0.48776 | 0.48789 | −0.00013 |
| Lo-corrected Sharpe | 1.40067 | 1.40747 | **−0.0068** |
| maximum drawdown | −0.53282 | −0.5328 | −0.00002 |
| annual turnover | 36.59268 | 35.47137 | **+1.12131** |
| information ratio vs buy-and-hold QQQ | 0.74784 | 0.75142 | −0.00359 |

Arm C holds **0.083333 of NAV in sleeve cash** that arm B does not, across 513
sessions where the branch is active, and the DTB3 accrual on it is
**0.01022 percentage points annualised**, which is near nil because policy
rates sat near zero across most of the window. **The residual after netting the
cash accrual is −0.002389**, so the capital-efficiency component explains about
four percent of the gap and does not account for it.

**A residual of roughly a quarter point per year survives**, and step 8 locates
its mechanism rather than leaving it unattributed. Arm B turns over 1.12131
more per year than arm C because reaching the same notional through the −1x
expression deploys three times the capital, and the participation cap binds
PSQ on 38 transitions at a mean 0.303513 fraction capped while never binding
SQQQ under arms A, C, or D. So the −1x and −3x expressions are **not** cleanly
interchangeable at matched notional at the canonical NAV, and the difference
is a turnover and capacity property of the −1x expression rather than a
tracking-quality property of either fund.

## Step 7, decomposition, corrected [B, repaired in-session]

The decomposition is run on the T10 standalone series, where the branch is the
only holder. **The portfolio-level series does not answer the instrument
question**, because SQQQ is also held by T11's bull-short basket, both T11 bear
terminals, and S2's defensive state, so arms B and C are not notional-matched
there. The matched-notional control requires the beta components of B and C to
agree and reports a relative gap of **2.412 percent**, which the cap explains
rather than a measurement error, since B's mean weight when held is 0.4096
against a 0.5 target while C's 0.1656 sits at its target.

| arm | short leg | M | mean weight held | total | beta | residual | corr vs rest of sleeve |
|---|---|---|---|---|---|---|---|
| A | SQQQ | −3.0 | 0.4974 | −1.0742 | −1.0847 | +0.0104 | −0.5619 |
| B | PSQ | −1.0 | 0.4096 | −0.3635 | −0.3712 | +0.0077 | −0.4216 |
| C | SQQQ | −3.0 | 0.1656 | −0.3586 | −0.3623 | +0.0036 | −0.4292 |
| D | SQQQ | −3.0 | 0.3314 | −0.7166 | −0.7237 | +0.0071 | −0.5296 |
| E | PSQ | −1.0 | 0.6954 | −0.6526 | −0.6698 | +0.0172 | −0.6338 |

The residual component is positive and small on every arm, so neither
expression carries a tracking penalty at this horizon. Diversification at
portfolio level moves little across arms, with the effective number of
constituents between 2.894 and 3.026 and the effective number of
minimum-torsion bets between 8.577 and 8.678. **Mean effective market exposure
rises as the hedge is removed**, from 1.776 under arm A to 1.864 under arm F,
with the worst trailing-return decile rising from 1.042 to 1.140 and the
wildest volatility decile from 1.490 to 1.589. *(Reconciled 2026-08-19,
session 16 step 3: arm A's 1.776, 1.042 and 1.490 reproduce on the realized
open-to-open panel with the cap over the primary window at a distance of 0.013,
and are canonical. Session 13.5's standing 1.70, 0.78 and 1.06 do not reproduce
on any panel, convention, cap setting, or window and are superseded, having been
measured before the SOXS split patch, the expense corrections, the participation
cap, and the boundary move.)*

## Step 6, the hedge intensity curve [A]

Designated cell, arms ordered from most to least hedge:

| arm | short notional | ann return | vol | SR Lo | max DD | Ulcer | IR vs QQQ |
|---|---|---|---|---|---|---|---|
| A | −0.375 | 0.5226 | 0.4881 | 1.3846 | −0.5306 | 14.9763 | 0.7036 |
| D | −0.25 | 0.536 | 0.4878 | 1.3971 | −0.531 | 14.8555 | 0.7276 |
| C | −0.125 | 0.5493 | 0.4879 | 1.4075 | −0.5328 | 14.7765 | 0.7514 |
| F | 0.0 | 0.5608 | 0.4877 | 1.4238 | −0.5348 | 14.6104 | 0.7716 |

**The curve is monotone toward less hedge on every convention and window
tested**, on both annualised return and Lo-corrected Sharpe, with no interior
maximum. Close-to-close primary runs 0.2971 to 0.3354 on return and 0.9286 to
0.973 on Sharpe, and close-to-close full runs 0.2136 to 0.2409 and 0.7161 to
0.748. Maximum drawdown moves the other way and worsens slightly as the hedge
is removed, from −0.5306 to −0.5348, while the Ulcer index improves from
14.9763 to 14.6104.

Conditioning on market state, **the hedge does not pay in the deciles it exists
for**. In the worst trailing-return decile the mean daily return is −0.00177
under arm A against −0.00172 under arm F, and in the wildest volatility decile
it is 0.00173 under arm A against 0.00217 under arm F, so more hedge reads
lower in both. This is a statement about 2011 to 2021 rather than about the
instrument, and the sample contains one crash of the kind the branch is built
for.

## Step 4, the metric slate and deltas against arm A

Designated cell, portfolio level:

| arm | Δ ann return | Δ vol | Δ SR Lo | Δ max DD | Δ turnover | Δ Ulcer | Δ Sortino |
|---|---|---|---|---|---|---|---|
| B | +0.0242 | −0.0004 | +0.0161 | −0.0022 | −1.2814 | −0.1712 | +0.0458 |
| C | +0.0267 | −0.0002 | +0.0228 | −0.0022 | −2.4027 | −0.1998 | +0.0502 |
| D | +0.0134 | −0.0003 | +0.0125 | −0.0004 | −1.1879 | −0.1207 | +0.0249 |
| E | +0.0147 | +0.0004 | **−0.0106** | −0.0013 | −2.2942 | +0.0518 | +0.0289 |
| F | +0.0382 | −0.0005 | +0.0391 | −0.0042 | −1.2604 | −0.3659 | +0.0721 |
| B_all | +0.0378 | −0.0014 | +0.0048 | **+0.02** | −3.32 | −0.4388 | +0.0735 |

Arm E, the confounded one, is the only arm reading below arm A on Lo-corrected
Sharpe. **Arm B_all separates the T10-only effect from the portfolio-wide
swap**: it gains as much annualised return as arm F at +0.0378 but keeps only
+0.0048 of Sharpe, so removing SQQQ from all three sleeves is not the same
trade as reducing it in T10. *(Corrected 2026-08-19, session 16 step 10: the
original prose read the maximum-drawdown delta of +0.02 as worsening. Maximum
drawdown is negative, so +0.02 against arm A's −0.5306 gives −0.5106, an
improvement of two percentage points, confirmed independently by the cost sweep
at −0.5084 against −0.5281 at the anchor.)*

At T10 standalone the same ordering holds with larger magnitudes, arm F reading
+0.1538 on annualised return and +0.2075 on Lo-corrected Sharpe against arm A,
which is the sleeve-level effect before the other three sleeves dilute it.

## Step 8, cost and cap interaction [A]

Under the session 15 stacking rule, where the uniform sweep replaces the tiered
slippage and the auction premium rather than stacking on them, **the arm
ordering is stable across the whole registered sweep**. Arm F leads on
Lo-corrected Sharpe at every point from 1.6365 at 0 basis points to 1.1383 at
50, and arm A trails at every point from 1.5605 to 1.0924. No crossing occurs
inside the sweep.

Annual turnover runs from 32.37 under arm B_all to 36.26 under arm A. The cap
interaction is the asymmetry the step anticipated. **PSQ binds the cap on 38
transitions under arm B at a mean 0.303513 fraction capped, 126 under arm E,
and 106 under arm B_all, while SQQQ never binds under arms A, C, or D.**
Holding the −1x expression at three times the weight for the same notional
moves it into the cap.

## Step 9, per-year contribution of the short leg [A]

Designated cell, primary window:

| arm | short leg | total | 2020 | largest year | share of absolute |
|---|---|---|---|---|---|
| A | SQQQ | −0.465 | −0.253 | 2020 | 26.4% |
| B | PSQ | −0.1011 | −0.0268 | 2011 | 17.0% |
| C | SQQQ | −0.2645 | −0.1821 | 2020 | 26.5% |
| D | SQQQ | −0.3648 | −0.2176 | 2020 | 26.4% |
| E | PSQ | −0.169 | −0.0508 | 2020 | 16.7% |
| B_all | PSQ | −0.1633 | −0.072 | 2020 | 23.8% |

Every SQQQ arm concentrates in 2020 at roughly 26 percent of absolute
contribution, against the strategy's own 21.7 percent, and the PSQ arms are
less concentrated with arm B's largest year being 2011.

## The 9.12 report-figure check

`scripts/check_report_figures.py outputs/session-15.5` returns **five unmatched
figures out of 187**, each confirmed by hand. Three are figures legitimately
carried from earlier sessions rather than computed here, being the S2 Sharpe
crossing at 44.165732 basis points and the cap fraction of 5.2285 percent, both
read from session 15's cost-sweep-designated.csv and nav-sweep.csv and entering
this report only as the standing corrections the session prompt supplied, and
the −39.35 beta figure, which is session 13.5's SQQQ decomposition cited with
that attribution in the prose that motivates the arms. The remaining two are an
artefact of this section itself, since a paragraph that documents unmatched
figures necessarily contains them, one being the full-precision restatement of
the same S2 crossing and one being the register identifier 9.12 in the heading.

The checker was extended in this session to compare at six decimal places, since
three figures this report carries from its own CSVs, being 0.002389, 0.083333,
and 0.303513, were reported as unmatched at the previous five-place limit. That
is a change to the checking mechanism and not to any measurement.

## Defect register

| id | status |
|---|---|
| D1 through D12, D14, D15, D17, D18, D19 | closed, repaired, or swept |
| D13 | never assigned |
| D16 | open, financing spread assumed and swept 25 to 200 basis points |
| D20 | open, NAV not spanned by the nine specification-curve axes |
| D21 | open, 7.14 primary window boundary inclusive of the last unavailable fill |
| D22 | open, docs/STATE.md stale as of session 12.5 |
| **D23 new [C]** | a portfolio-level per-instrument decomposition attributes an instrument held by several sleeves to whichever sleeve is under study. Caught in this session by a matched-notional control and corrected to the isolated T10 series; the same pattern would silently confound any future per-sleeve instrument attribution. |

## What would have to change to act on each finding

- The instrument comparison, the intensity curve, and the cap asymmetry are
  **measurements**. Acting on any of them is a **specification change** to the
  canonical instrument set or branch weights, which this session does not make.
- D23 is a **correctness repair**, already applied here to the step 7 output.
- D21 and D20 are **register decisions**, unchanged by this session.
- D22 is **documentation**, unchanged by this session.

No recommendation is made on any of them. **Acting on any of this before the
grid and the holdout have run would convert a mostly pre-registered study into
a fitted one**, since every arm here was defined after the result that
motivated it was visible, which is why all of it is disclosed under 9.10 and
none of it is adopted.

## What remains open before session 16 can run

Unchanged by this session, being D20 whether NAV joins the specification-curve
axes, D21 the 7.14 boundary, the early-window reporting form, D16 the financing
spread, the D18 documentation correction to session 13.8's ablation-mechanism
entry-split rows, and D22 refreshing STATE.md. **Nothing in this session
changes that list**, and D23 is added to it as a documentation item rather than
a blocker, since the affected output was corrected in place.

## Stop condition

Halted after step 11. No arm adopted. No canonical figure changed. No
specification, parameter, threshold, instrument, weight, cost model, cap level,
NAV, or window boundary changed. No grid, null, benchmark ladder, or holdout
executed, and the 2021-08-01 boundary untouched. No deflated or probabilistic
Sharpe computed. Nothing committed and the working tree left dirty.
