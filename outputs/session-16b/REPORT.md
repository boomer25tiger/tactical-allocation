# Session 16b — grid axis enumeration and the placeholder defect class

Run 2026-08-19. Finding labels carried from sessions 13.5 through 16, being
**[A]** a finding that explains a number without changing it, **[B]** a number
wrong or unreliable, and **[C]** a register or code defect.

## Step 0, the pre-registered rule

The fallback rule was written to `outputs/session-16b/enumeration-rule.md` and
hashed **before any part of step 1 read the register on the axes**. Its SHA-256
is **702a6026972251ea83defa30817b97a49931c45450fbd14af34f1c1900d74f24**,
recorded in `enumeration-rule.sha256`. The hash is the evidence the rule
preceded the reading, which matters because the product test below turned on an
arithmetic the rule could otherwise have been shaped to satisfy.

## Step 1, the register read [C]

**The v3 register carries no entry headers for 7.2, 7.3, 7.5, 7.8, or 7.9**,
the five identifiers session 16's D24 named as the axis sources. Section 7
contains only 7.4, 7.6, 7.7, 7.10, 7.14, 7.14a, and 7.14b. The positive control
passed first, locating 7.4, 7.6, 7.7, 7.10, 6.1, and 6.2 as present entry
headers.

Values do exist for four of the eight, in `src/config.py` comments, which the
register's own preamble designates authoritative for values. Of ten axes in
total, **seven carry recorded values and three carry neither values nor a
cardinality anywhere**.

| axis | canonical | values | source |
|---|---|---|---|
| RSI period, exhaustion (6.1) | 14 | 7, 14, 28 | config 6.1 comment |
| RSI period, dip (6.1) | 14 | 7, 14, 28 | config 6.1 comment |
| RSI period, relative strength (6.1) | 14 | 7, 14, 28 | config 6.1 comment |
| Overbought tier one (6.2) | 70 | none recorded | — |
| Tier-two offset (7.4) | 10 | 5, 10, 15 | register 7.4, status **informed** |
| Oversold (6.4) | 30 | none recorded | — |
| Short SMA (6.6) | 20 | none recorded | — |
| S3 vote threshold (6.7) | 3 | 2, 3, 4 | config 6.7 comment |
| Long SMA (7.6) | 200 | 50, 100, 150, 200 | config tuple |
| Crash threshold (7.7) | −15 | −5, −10, −15, −20, −25 | config tuple |

7.4 is recorded as **informed rather than closed**, so its values are recorded
while its status is not a closure. Under the step 0 rule the first precedence
branch applies on the values, but whether an informed item is an axis at all is
a register question rather than a measurement one.

The oversold tuple at `scripts/s13_5_diagnostics.py` line 374 is a literal
inside a diagnostic script written to sweep branch reachability. **A literal in
a diagnostic script is not a registered axis and is not used as one here.**

## Step 2, the product test [B, mismatch]

**The product test fails, and 218,700 was never derivable from the register as
written.**

The v1/v2 ranges at `docs/HANDOFF.md` line 122 multiply to **273,375 exactly**,
matching what that document records under 7.10, so the axes were a genuine
product once and the placeholder is a recovery target rather than an arbitrary
stand-in. 7.6 dropping long-SMA 250 carries that to 218,700 correctly. **7.7
then swapped a three-point crash-quantile axis for a five-point crash-level
axis while asserting the total was unchanged**, which multiplies the product by
5/3 and cannot leave it fixed. The arithmetic gives **364,500**.

The placeholder itself does not survive inspection. `GRID_UNREPRESENTED_AXES_CARDINALITY`
holds 10,935, which is **218,700 divided by 20 exactly**, a residual obtained by
division rather than a product of inputs. Its factorisation is 3^7 × 5, whose
unique decomposition into eight integers each at least 2 is seven axes at three
values and one at five. The actual eight unrepresented axes multiply to
**18,225**, factoring as 3^6 × 5^2, being six axes at three and two at five.
**The decompositions differ, so the placeholder cannot be the product of these
axes under any assignment.**

## Step 3, the enumeration

Applying the step 0 rule with its precedence exactly as written gives an
**enumerated total of 131,220** across ten axes. **Seven axes resolved from
recorded values, zero from a recorded cardinality, and three from construction
alone.** The middle precedence branch never fired, since no axis recorded a
cardinality without values.

| axis | values | n | source |
|---|---|---|---|
| RSI period, exhaustion | 7, 14, 28 | 3 | recorded |
| RSI period, dip | 7, 14, 28 | 3 | recorded |
| RSI period, relative strength | 7, 14, 28 | 3 | recorded |
| Overbought tier one | 65, 70, 75 | 3 | **DISCRETIONARY** |
| Tier-two offset | 5, 10, 15 | 3 | recorded |
| Oversold | 25, 30, 35 | 3 | **DISCRETIONARY** |
| Short SMA | 19, 20, 21 | 3 | **DISCRETIONARY** |
| S3 vote threshold | 2, 3, 4 | 3 | recorded |
| Long SMA | 50, 100, 150, 200 | 4 | recorded |
| Crash threshold | −5, −10, −15, −20, −25 | 5 | recorded |

**Three discretionary axes is the measure of how much discretion entered**, and
each carries a 9.10 disclosure, since the canonical result was visible when the
rule was applied. Every axis carries its canonical value and the canonical point
is unchanged.

Three things are recorded rather than resolved. **The pre-registered rule has a
gap**, specifying how to build values given a cardinality of 3 or 5 without
saying which applies when neither is recorded; 3 was taken as the smaller of the
two it names, and at 5 for all three discretionary axes the total would be
607,500. **The short-SMA sweep of 19, 20, 21 is degenerate** beside the recorded
long-SMA sweep at 50-session steps, which is what the rule's one-session
granularity produces on a moving-average length, reported rather than silently
widened. **HANDOFF.md carries candidate values for all three discretionary
axes**, being tier one at 60/65/70/75/80, oversold at 20/25/30/35/40, and short
SMA at 10/20/50, which give **364,500**, the same total the v3 amendments
produce arithmetically; adopting them is a register decision and is not taken
here.

**Branch reachability changes along the oversold axis.** Session 13.5 measured
the two T11 PSQ-dip terminals firing zero times at oversold 20, 25, and 30, then
1 and 23 times at 35 and 10 and 113 at 40. Two of the three enumerated oversold
points leave both terminals dead and the third brings them alive, so a third of
that axis runs a structurally different strategy.

## Step 4, the product guard repaired [C]

`validate()` now computes the product from the enumerated axis tuples and
compares it against the registered total. Confirmed by control in both
directions, the repaired guard **rejects** the pre-repair total of 218,700 with
the message that the axes multiply to 131,220, and **accepts** 131,220.
`GRID_UNREPRESENTED_AXES_CARDINALITY` is removed, and its five other references
were reported before removal, all in documentation rather than code. Canonical
values are additionally guarded to lie on their own axes. **Zero constants
outside the grid definition differ** between the pre-repair and post-repair
modules.

## Step 5, the placeholder and unported-literal sweep [C]

The detector was validated first on a constructed placeholder, a constructed
unported literal, and a config-read parameter, flagging the first two and
leaving the third alone. The sweep found **zero remaining placeholder-shaped
constants**, the only member of that class having been removed in step 4, and
**207 bare comparison literals of which seven lie in the return-generating
path**.

Six of the seven are not strategy parameters, being minimum-sample guards at
`len(r) < 60` in three metric functions and `len(exs) > 260` in the split-half
Sharpe, and float tolerances at 1e-12 in two places. **One was a genuine
unported literal**, the `4` bounding `S3_VOTE_THRESHOLD` in `validate()`, which
is the S3 voter count and was hardcoded rather than derived. The vote membership
now lives in `config.S3_VOTE_MEMBERSHIP` under 6.8, `src/sleeves.py` reads it,
and the bound derives from `len()`.

**Behaviour identity confirmed.** After the step 4 guard repair and the step 5
port, the canonical designated cell reproduces session 16's corrected figures at
**0.5218 and 1.3817**, matching to four decimals, and `S3_VOTES` is the
identical tuple.

## Step 6, session 16 report corrections [B]

Three items corrected in place with dated notes.

**The leave-one-out maximum-drawdown column is partly a splice artifact.**
Removing sessions cannot deepen a drawdown, yet dropping 2019 deepens it from
−0.5306 to −0.5775, because excision joins a late-2018 decline directly to a
2020 decline into a path that never occurred. Return and Sharpe are averages
over retained sessions and survive splicing; path-dependent statistics do not.
The caveat now travels with the column.

**The 2011 figure sits on a stub.** Session counts and sample percentages are
now in the table. 2011 contributes **62 of 2,472 sessions at 2.51 percent**
while its removal moves the Sharpe by **+0.1819 at 13.2 percent**, since the
corrected window starts 2011-10-04.

**The sleeve ranges are the diversification argument and were not labelled as
such.** Against each base, the ensemble's range is 0.3313 at **23.97 percent**,
against 98.58 percent for T10, 62.99 for T11, 43.20 for S3, and 26.30 for S2, so
the ensemble is the most stable of the five under year removal. The margin over
S2 standalone is small at 23.97 against 26.30 percent, and the finding sits
alongside session 14's Romano-Wolf result placing the ensemble against S2
standalone at a family-wise adjusted p of 0.983 rather than superseding it.

## Register updates

- **7.2 through 7.9 enumerated**, with the axis table, the source of each axis,
  the step 0 hash, the three 9.10 disclosures, the rule gap, the degenerate
  short-SMA sweep, the HANDOFF alternative, and the oversold reachability
  change.
- **7.10 repaired**, with the guard computing the product from the axes, the
  placeholder removed, and the 273,375 to 218,700 to 364,500 history recorded.
- **8.7 amended**, with N set to 131,220 and 218,700 superseded.
- **9.13 defect-class rule closed**, being that a defect found in one location
  triggers a sweep for the class rather than a repair of the instance, with D18
  and D24 named as the two precedents.
- **D25 recorded as documentation**, with the superseding exposure figures, the
  weakened volatility-stress claim, and the full-history conditioning
  requirement.
- **D24 closed** by the enumeration.

## The 9.12 report-figure check

`scripts/check_report_figures.py outputs/session-16b` returns **15 unmatched
figures out of 35**, every one confirmed by hand and falling into two groups.
**Fourteen are register identifiers**, being 6.1, 6.2, 6.4, 6.6, 6.7, 7.2, 7.3,
7.4, 7.5, 7.6, 7.8, 7.9, 9.10, and 9.13, which are prose tokens shaped like
decimal figures and which this report necessarily names more often than most,
since its subject is which register entries exist. **One is a prior-session
figure cited with attribution**, being the 0.983 family-wise adjusted p that
session 14's `nulls.csv` records for the ensemble against the best single
sleeve, confirmed against that file.

The high unmatched ratio here is a property of the subject rather than a
symptom, and it illustrates the mechanism's known limit, which is that it
compares decimal tokens without knowing whether a token is a measurement or a
name.

## Defect register

| id | status |
|---|---|
| D1–D12, D14, D15, D17–D19, D21, D22 | closed, repaired, or swept |
| D13 | never assigned |
| D16 | open, financing spread assumed and swept 25 to 200 basis points |
| D20 | closed session 16, NAV on the curve and not the grid axes |
| D23 | open, portfolio-level per-instrument attribution confound, corrected in place session 15.5 |
| D24 | **CLOSED** step 3, axes enumerated, three by construction alone |
| D25 | **recorded as documentation** step 7 |
| **D26 new [B]** | the register's 7.7 amendment asserted a five-point crash axis left the 218,700 total unchanged, which is arithmetically impossible; 218,700 stood in the register and in config for four sessions and N in 8.7 was wrong throughout |
| **D27 new [C]** | the pre-registered enumeration rule underdetermines the cardinality when neither values nor a cardinality are recorded, and its one-session granularity produces a degenerate short-SMA sweep; both are properties of the rule rather than of the register |

## What would have to change to act on each finding

- **The three discretionary axes** are a **register decision**, being whether to
  adopt HANDOFF's candidate values, keep the construction, or enumerate afresh.
  The total moves to 364,500 under the first and stays at 131,220 under the
  second.
- **D27**, the rule's gap and the degenerate short-SMA sweep, is a **register
  decision** on the granularity, since widening it after seeing the enumeration
  would be choosing the rule to suit the output.
- **7.4's informed status**, being whether an informed item is an axis, is a
  **register decision**.
- **D26** is **documentation**, already corrected in 7.10 and 8.7.
- **D25** is **documentation**, already corrected in place.
- **D16** is a **register decision**, treated by the widened sweep.

No recommendation is made on any of them.

## What remains open before the grid can run

**Nothing blocks it mechanically.** The axes are enumerated, `validate()`
computes the product from them and passes at 131,220, and the canonical point
reproduces to four decimals. What remains is a register decision on whether
131,220 is the intended search space, since three of its ten axes were resolved
by construction rather than by a recorded decision and a fourth rests on an item
the register marks informed. Running the grid on 131,220 and later adopting
HANDOFF's values would require rerunning it at 364,500 and recomputing the
deflated Sharpe, since N enters that statistic directly.

## Stop condition

Halted after step 8. No grid executed. No PBO, deflated Sharpe, or
specification curve computed. No holdout executed and the 2021-08-01 boundary
untouched. No specification run and no performance statistic computed on any
grid point other than the step 5 canonical reproduction. No canonical value
changed on any axis. Nothing committed and the working tree left dirty.
