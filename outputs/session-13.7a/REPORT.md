# Session 13.7a — expense definition resolution and o2o promotion record

Run 2026-08-18. Scripts: `scripts/s13_7a_tracking.py`; EDGAR retrievals
by bounded agent (accessions in every table). Read-only measurement plus
one register recording. Nothing rebuilt, nothing re-run, no canonical
result produced. Finding labels carried from 13.5–13.7: **[A]** explains
without changing; **[B]** number wrong or unreliable; **[C]** register
or code defect.

## The step-3 verdict, first — and what it means for session 13.8

**DEFINITIONAL ARTIFACT. There is no expense correction in session
13.8's scope.** With the 0.95% constant, synthetic UVXY drifts **−0.67%
per year BELOW issuer NAV** over its full in-window listed period
(2011-10..2021-07, 2,472 sessions) — the opposite direction of the
+0.87–0.95 pp/yr drift an understated expense would force, and inside
the TQQQ/SQQQ baseline noise band (−0.73 / −1.25%/yr). The detector was
validated before the verdict was read: a deliberately mis-specified
synthetic carrying 1.90% shifts by **−0.949 pp/yr against −0.95
expected**. Session 13.7's analytic bound ("the standing result
overstates return by 0.22–0.28 pp/yr", dominated by the UVXY term)
**does not survive**. Session 13.8's remaining scope is the D15 SOXS
split patch and the halted reruns — expense inputs stand as built.

A first-run methodological finding worth the record [A]: the 2.7a
geometric-difference TD metric is insensitive on steeply declining funds
(the mis-specified control shifted it only −0.148 pp, because
sensitivity scales with 1+annualised return ≈ 0.15 at UVXY's −85%/yr).
The verdict metric is the annualised ratio drift, which carries full
sensitivity; both are reported in `tracking-verdict.csv`.

## Step 1 — provenance of the 21 cells [B→explained]

Complete table in `expense-provenance.csv`, per cell: fund, fiscal year,
form, accession, exact line label, value, filing section, definition
class, and the build constant. The decisive fact: **ProShares Trust II
(UVXY/SVXY) Financial Highlights print exactly two expense lines — the
unqualified "Expense ratio" (brokerage-commission-inclusive: 1.82, 1.90,
1.65 / 1.53, 1.51, 1.32) and "Expense ratio, excluding brokerage
commissions [and fees]", which reads 0.95 in every sampled year** —
while the ProShares Trust (TQQQ/SQQQ) tables carry no brokerage-
inclusive variant at all ("brokerage" is absent from their Financial
Highlights region); their 0.95 came from "Expenses net of waivers, if
any". **The positive control resolves the discrepancy directly: session
13.7 compared different line families across the two trusts.** The
like-for-like line equals the constant and matches the independent
source's 0.95 statutory management fee.

Erratum recorded [C]: session 13.7's expense-financing.csv listed
TQQQ's build constant as 0.95; the build carries TQQQ 0.86 (and SH
0.88). Corrected in this session's table; TQQQ actual 0.95 vs build
0.86 is a real 9 bp/yr gap inside baseline noise.

## Step 2 — denominator check [A; closes]

Every one of the 21 cells was read directly from issuer-stated ratios;
nothing was computed by session 13.7 or here. The filings are silent on
how average net assets is constructed (daily vs period average — the
only methodological note is annualization), so the declining-denominator
concern cannot arise for any recovered cell. Step closed.
`denominator-check.csv`.

## Step 3 — the tracking difference test [B→resolved]

`tracking-verdict.csv`: headline, by-year, and both controls. In-window
annualised ratio drift (2.7a difference beside):

| pair | ratio drift | cumulative | sign |
|---|---|---|---|
| UVXY syn vs issuer NAV | **−0.67%/yr** | −6.4% | below |
| SVXY syn vs NAV (incl 2018-02-06) | −6.59%/yr | −48.8% | below |
| SVXY syn vs NAV (excl per 2.12b) | **+1.60%/yr** | +16.8% | above |
| TQQQ baseline (0.95 confirmed) | −0.73%/yr | −8.1% | below |
| SQQQ baseline (0.95 confirmed) | −1.25%/yr | −13.4% | below |

Mis-specified control: −0.949 pp shift vs −0.95 expected — **the test
detects what it must detect**. Verdict as stated above. SVXY's +1.60%/yr
(excluding the termination day the register already excludes from
validation) is larger than its 0.37–0.58 pp filing gap and sits inside
the recorded SVXY residual class — not cleanly attributable to expenses,
recorded, not repaired.

## Step 4 — construction inputs [A]

`construction-inputs.csv`. Both funds build from **VXCM30** —
construction B, the investable S&P VX roll index from CFE settlement
prices — at the 3.11 schedule multiples, with exactly one expense
component (ER 0.95%/yr), no swap financing (k=0, futures-based, 2.15),
and a collateral credit at ref on full NAV. The validation target during
construction was **issuer NAV** (corr 0.9998). The case that holds: the
construction is validated against a NAV that already embeds the fund's
actual brokerage, and the measured drift at 0.95 is at baseline — so
applying the brokerage-inclusive filing ratio would double-count,
pushing synthetic UVXY ~0.9 pp/yr below the path it already matches.
The theoretical-index-needs-brokerage case would require the synthetic
to drift ABOVE NAV at the brokerage magnitude; it measures as not
holding.

## Step 5 — register recordings (final text in DECISIONS-v3.md)

**4.1a, open-to-open promotion (post-hoc under 9.10).** Records: the 4.1
pre-registration provenance; 13.6's +33.3 pp measurement; 13.7's passive
control (−0.34/−0.09 pp) and signed deviation (−1.3 bp/day, running
against the arm); that promotion was decided after those measurements
and is therefore post-hoc; both arms at equal prominence in the writeup.
The unresolved consequence is recorded without resolution: under
open-to-open primary the canonical result must come from the realized
panel, so **2.8's all-synthetic primary designation is OPEN** — with the
recorded fact that 7.14's primary window contains no unavailable
realized-arm fills, so the original reason for synthetic primary does
not bind inside that window.

**2.13a, expense finding status.** Records the 13.7 finding, the
independent 0.95 statutory-fee source, the steps 1–4 outcome
(definitional artifact, line-family crossing, tracking verdict with
controls), that **D14's expense component is closed and 13.7's
direction confirmation does not survive, leaving D14's financing
component open under D16**, and the residuals (SVXY +1.60%/yr inside
its recorded class; Direxion 0.1–0.24 pp/yr fiscal-year differences and
TQQQ's 9 bp gap inside baseline noise; the 13.7 constant erratum).

## Defect register, updated

| id | status |
|---|---|
| D14 | **expense component CLOSED** (definitional artifact, measured); financing component open under D16; the post-boundary-documents register question stands for constants generally |
| D16 | open — financing not derivable from statements of operations; unchanged |
| D15 | open — SOXS split patch awaits authorization (session 13.8) |
| D10 | open — ENB window |
| D3, D4 | open — documentation |
| **new [C]** | 13.7 expense-financing.csv misstated TQQQ's build constant (0.95 vs actual 0.86) — corrected in expense-provenance.csv, documentation only |
| **new [A]** | the 2.7a TD-difference metric is insensitive on steeply declining funds; ratio drift carries full sensitivity — a definition note for 2.7a's next amendment, documentation |

## What would have to change to act on each finding

- Expense correction: **nothing — the measurement closes it.** Applying
  the filing ratios would be a correctness ERROR (double-count).
- SVXY's +1.60%/yr residual: further attribution would be a
  **measurement session**; any construction change a **specification
  change**.
- 2.7a metric note, D3/D4, the 13.7 erratum: **documentation**.
- 2.8 primary-arm designation (opened by the o2o record): **register
  decision the user has not yet made**.
- D15 patch and reruns: **correctness repair**, session 13.8.

No recommendation is made.

## Stop condition

Halted after step 6. No panel rebuilt, no canonical run, no expense
correction applied, no SOXS patch, nothing promoted beyond the step-5
register recording, nothing committed. Working tree left dirty.
