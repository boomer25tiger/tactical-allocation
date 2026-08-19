# Session 13.9 — final repairs and pre-ladder closure

Run 2026-08-18. Scripts: `scripts/s13_9_rerun.py`, `s13_9_controls.py`;
literature and volume verification by bounded agents (sources in the
CSVs). Finding labels carried: **[A]** explains without changing; **[B]**
number wrong or unreliable; **[C]** register or code defect. Ordering
respected: tiers and premium (1–2) → re-run (3) → dependents (4–10) →
register (11–12).

## The re-tiered canonical and the headline cell

**The headline cell (step 8, designated, gate satisfied):** open-to-open,
realized panel, primary window (2011-10-03+), class-tiered slippage with
the 2.0× opening-auction premium at the 10 bp anchor, commission Arm S,
Lo-corrected Sharpe — **value 1.37** (annualised return 52.9%,
volatility 51.1%, maximum drawdown −53.1%). Recorded as 4.1b with the
full history: open-to-open was the original specification, displaced by
4.1's synthetic-validation objection, which equal panel weighting and
the primary window dissolve; the designation was made after the
measurement existed and is post-hoc under 9.10. Close-to-close is
reported at equal prominence throughout.

**Primary window at the anchor (tiered-class, Arm S):** synthetic c2c
31.7% / 0.98; realized c2c 30.0% / 0.94; realized o2o with premium
**52.9% / 1.37**, without premium 59.9% / 1.49 — the premium's cost is
cleanly separable: **−9.6 pp annualised, −0.15 Lo-Sharpe**. Full-window
c2c: synthetic 18.3% / 0.700, realized 21.5% / 0.722 (Arm S).

**Deltas vs 13.8:** the class re-tiering costs the c2c combos −1.6 pp
(synthetic) and −1.3 pp (realized) annualised against the volume-based
tiers — the direction expected when UVXY moves from 2 bp to 15 bp on
18.5% of dollar exposure; per-instrument drag tables make it visible
(UVXY slippage 2.0 → 15.0 bp round-turn; BIL 15.0 → 2.0). The uniform
sweep carries forward from 13.8 unchanged. All sanity checks pass on
every combination.

## Step 1 — tier reassignment [B→repaired]

Class-based map fixed before the arm ran (tier 1 unlevered 0.2×; tier 2
large levered index 0.5×; tier 3 levered sector/vol/BTAL 1.5×), with
anchors (DiLellio & Stanley 8–10 bp for SSO/SH; UVXY's measured ~15 bp
median; penny-quoting BIL). The three-way table shows class drove it:
UVXY tier 1→3 despite the highest median volume; BIL 3→1 despite low
volume; PSQ (1×) and TQQQ (3×) share tier 2 while SOXL (3×) sits in
tier 3 — neither volume nor leverage ordering reproduces the map.

## Step 2 — the opening-auction premium [A; 4.4a]

Literature retrieved before any value was set (seven sources,
`auction-premium.csv`): Goyal-Jegadeesh-Wu (JFQA 2026) — opening
auctions carry the largest price impact, closing the smallest,
continuous ≈ 2× closing at large-cap sizes (snippet-verified);
Bacidore-Lipson (2001) — 1990s NYSE opens ~20% cheaper (opposite sign,
recorded); McInish-Wood reverse-J; the 744-ETF 2017 intraday study
(spreads highest in the first hour); Challet-Gourianov volume
asymmetry; NYSE 2023 closing TCA. **Premium: central 2.0×, swept
1.0–4.0×, uniform across tiers** (no source measures tier variation —
recorded as unmeasured rather than assumed), applied to the o2o arm
only. Derivation and caveats (snippet-verified magnitudes; the
conservative implication that un-premiumed tiers overcharge c2c) are in
the register entry.

## Step 4 — the volatility passive control [A; gate PASSED]

Buy-and-hold on the primary window, both conventions: UVXY gap −0.24 pp
annualised, SVXY +0.66, SOXL −1.74, SQQQ +0.22 — **negligible on every
class the strategy holds**. Session 13.7's verdict extends to the
previously uncontrolled 22.5% of dollar exposure; the o2o advantage is
a property of when the strategy trades, and the step-8 designation
proceeded. VIX-open signed deviation remains unmeasured (no validated
VX open index; exclusion restated).

## Step 5 — the UVXY entry reconciliation [A→resolved]

The −91 bp (13.6) and +23 bp (13.8) figures **both survive — they
measure different populations on different windows**, not different
units and not different panels: for 100%-UVXY states the sleeve-unit
and instrument bases are identical by construction, and the
repaired-vs-unrepaired panels differ by basis points (raw-price repairs
never touch returns). The full grid (`entry-reconciliation.csv`) shows
S3:100%UVXY entries on 2012+ reproducing the negative first-day figure,
while the all-entries full-sample mean is pulled positive by 2008–2011
vol-spike entries and tier-1-basket entries. No artifact; the timing
property's load-bearing figure stands for its stated population.

## Step 6 — BTAL capacity [B→verified, harsher]

Independent verification (FactSet-sourced archived snapshots): median
daily dollar volume **$11.7K as of July 2018** (avg $74.6K), $1.26M avg
by mid-2019 — the stored record is consistent with the independent one
in the liquid era and *generous* in 2018 (stored median $39.0K), so the
artifact flag resolves in the harsher direction. Capacity limit at 5%
of contemporaneous ADV, reported not applied: **binding NAV ≈ $45K
(BTAL)**, TECL $84K (2008), every other instrument ≥ $800K. The
1,000,000 result stands with the capacity note; no cap, no impact
charge, no NAV change.

## Step 7 — Sharpe numerator convention [A; 8.2 amended]

Registered: arithmetic mean excess over DTB3 in the numerator,
geometric annualised return reported separately, every headline figure
dual-reported (`sharpe-convention.csv`). Variance drag ~14 pp/yr at
~53% volatility — the early window's −9.97% CAGR with +0.14 Lo-Sharpe
is the convention, not an error.

## Step 9 — the decision audit [A; 9.11]

**121 items: 55 pre-result choices, 22 post-result choices, 17
post-result repairs, 16 measurements.** Eleven post-result
choice-closures lack an explicit 9.10 flag — **new defect D17** (list
in `decision-audit.csv`; several are formalizations of pre-result
operating rules, recorded without judgement). N for the deflated Sharpe
stays at grid size (218,700): repairs were not trials, and the
post-result choices largely declined to select. The specification curve
spans: panel, convention, window, commission arm, slippage model
(uniform / class tiers / premium 1–4×), financing spread (25–200 bp),
SMH accrual, sizing mode, and the completion rule.

## Step 10 — early-window forms [A]

The 106 fully-fillable sessions stitch to −51.65% total across **16
discontinuities over 5 days (max gap 55 days)** — demonstrative only:
a product over non-contiguous sessions has no return interpretation,
so the realized-panel early window supports **coverage reporting
only**. Paper-form coverage and availability tables are in
`early-window-forms.csv`. The reporting-form decision stays open for
conversation.

## Step 11 — documentation backlog [C→repaired]

D3: the six audit IDs re-registered with dispositions and source
sessions (register section "Backlog dispositions"). D4: sleeves.py
docstring corrected to −15-via-config; import and config-read
confirmed; comment-only, no behaviour change. The TQQQ 0.86/0.95
erratum: dated correction added to session 13.7's report naming the
authoritative table.

## Step 12 — register updates (final text in DECISIONS-v3.md)

4.4 class-tier amendment (9.10-tagged); **4.4a** opening-auction
premium; **8.2** Sharpe-numerator amendment; **4.1b** headline
designation with full history; **9.11** decision-audit record; **4.6**
BTAL capacity amendment; plus the step-11 backlog entries.

## Provisional operating values — status

All five closed or superseded as of 13.8; unchanged this session. The
surviving conventions: pre-listing raw-price back-extension; negative
cash at DTB3 symmetric (measured immaterial).

## Defect register

| id | status |
|---|---|
| D1–D2, D5–D12, D14–D15 | closed/repaired (13.6–13.8) |
| D3, D4 | **CLOSED** (step 11) |
| D13 | never assigned |
| D16 | open — financing spread remains assumed, swept 25–200 bp |
| **D17 (new)** | eleven post-result choice-closures lack explicit 9.10 flags (decision-audit.csv); documentation — retro-tagging is a later documentation pass |
| **new [A]** | the volume-based tier map (13.8) mispriced by class and is superseded; retained in outputs for comparability |

## What remains open before session 14

1. **The early-window reporting form** — register decision, made in
   conversation from step 10's forms.
2. **D16 / financing spread** — swept, not resolved; the sweep is the
   treatment.
3. **D17 retro-tagging** — documentation pass.
4. Session 14 itself is fully specified: the 8.8 ladder (including the
   two 13.7 additions at mean effective exposure 1.70) and the 8.9/8.10
   nulls, all three 7.14 windows, identical cost model on every line,
   against this session's canonical and headline cell.

## What would have to change to act on each finding

- Premium value or tier variation: new measurement (**specification
  change** with sources).
- BTAL capacity: any cap/charge is a **specification change**; the note
  travels with the result.
- D17: **documentation**.
- Headline designation: it is recorded post-hoc; undoing it is a
  **register decision**.

No recommendation is made.

## Stop condition

Halted after step 13. No arm promoted beyond the step-8 designation and
step-12 records; no ablated specification adopted; no position capped,
no impact charge, no NAV change; no benchmark, null, grid, or holdout
executed. Nothing committed; working tree left dirty.
