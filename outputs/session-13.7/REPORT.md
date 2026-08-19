# Session 13.7 — cost model reconstruction, controls, and register closures

Run 2026-08-18. Scripts: `scripts/s13_7_slippage.py`, `s13_7_o2o_control.py`,
`s13_7_run.py` (staged, not run — see below), `s13_7_mechanism.py` (staged,
not run). Finding labels carried from 13.5/13.6: **[A]** explains without
changing; **[B]** number wrong or unreliable; **[C]** register or code
defect.

## THE SESSION HALTED AT ITS STEP-1 GATE — no rebuilt canonical exists

**Step 1's sourced price control failed for SOXS at +1399%** (reconstructed
$243.60 against an SEC-sourced $16.25 NAV on 2017-10-31), and per the
step's rule — a decode failure for any fund halts every step that uses
prices — **steps 5 (panel rebuild), 6 (rebuilt canonical), and 9 (ablation
mechanism) did not run.** Session 13.6's corrected headline remains the
standing canonical result, now carrying the D15 caveat below. There is no
new headline in this session, and no combination was promoted; the step-6
canonical designation (cost model B with Arm S) was doubly unmet — step 3
also halted on its own condition.

**The diagnosis [B][C — new defect D15], with the positive controls that
isolate it.** 19 of 19 unlevered instruments match an independent vendor
(Alpha Vantage non-adjusted monthly closes) to ≤0.006%; 13 of 14 levered
funds match SEC-filing NAV/market-value figures to ≤0.59% (NAV-vs-close
basis ~1%); the decode's return-consistency control passed at 1e−9 in
13.6. SOXS alone fails, by a factor of exactly 15. The vendor's split
column for SOXS carries ten splits including the 2017-05-01 1:5 the SEC
filing documents, but **omits the 2021-03-02 1:15 reverse split** —
Direxion's documented companion to SOXL's 15:1 forward split of the same
date, which IS present in SOXL's record (and anchored 13.6's passing SOXL
control). The adjusted closes are continuous through 2021-03-02 with
daily factors matching the synthetic's returns, so the vendor adjusted
the price series through the split and dropped the row. Consequence:
every reconstructed SOXS price before 2021-03-02 is 15× too high; dates
after are unaffected; returns and signals are untouched. Bearing on
13.6's standing headline: SOXS is 1.5% of dollar exposure and its
commission/truncation ran at the wrong level — bounded and small, flagged,
not repaired. **The repair is one split-table patch sourced from the SEC
filing — a correctness repair requiring authorization; nothing in this
session's authorized set covers it.** Tightened tolerance the sourced
comparison supports: ±0.01% unlevered, ±1% levered (NAV basis), SOXS
excluded as failed. Full table: `price-control.csv`.

## What completed, in step order

**Step 2 — commission arms [C→D2 resolved].** Four arms defined and
ported into src/config.py with register IDs (4.5 amended with the
corrected reasoning: applying a schedule that ceased to exist in 2019
across the post-2019 window models a counterfactual account, not a
conservative one). Splice date 2019-10-01, basis recorded (the month US
retail commissions went to zero industry-wide; IBKR Lite launched
October 2019). Arm T pass-throughs held at current published values,
disclosed (IBKR's page refused retrieval with HTTP 403): SEC $27.80/$1M
sold, FINRA TAF $0.000166/share sold capped $8.30, clearing
$0.00020/share, exchange $0.0010/share. **Arm run-figures (bp of traded,
drag by year) are halted with step 6**; the aggregation check's
structural half is answered — the engine merges sleeves before trading,
so the canonical run already submits one order per instrument per
session, and the per-sleeve unaggregated case is the counterfactual —
with its numbers likewise awaiting the rerun.

**Step 3 — measured slippage [A; halted per its own pre-condition].**
The per-instrument Corwin-Schultz profile was built (per year, zero
treatment, session 05's median convention, AR cross-check, positive
controls reproducing session 05's per-year values to 0.00 bp) and then
**halted before becoming a cost model**: the levels reproduce failure
mode (ii) — the leverage-correlated volatility-as-spread bias — in level
form. QQQ, with a true spread near 1 bp, reads 5.6–38 bp/yr; 2020 levels
sort by leverage on one underlying (QQQ 16.5 → TQQQ 65.4 → SOXL 102.8);
negative-estimate fractions run 40–50% panel-wide; and the Abdi-Ranaldo
cross-check disagrees with CS rather than confirming it (UVXY 2016–2020:
CS 50–92 bp vs AR 0). The three recorded failure modes are restated in
the file header; no workaround (capping, flooring, estimator switching)
was applied. Cost model B was not built; 4.4 is amended accordingly.
`slippage-profile.csv` carries the measurements as evidence.

**Step 4 — expense and financing [B].** All 21 targeted cells recovered
from EDGAR (accessions in `expense-financing.csv`). The finding: **UVXY
and SVXY actually charged 1.32–1.90%/yr all-in (brokerage included)
against the 0.95% constant in the build — an understatement of 0.4 to
0.95 pp/yr on the fund carrying 18.5% of dollar exposure.** Direxion
funds ran 0.95–1.06% net-with-interest in FY2012–2020 against FY2025
constants of 0.71–0.87. TQQQ/SQQQ were exactly 0.95 in every sampled
year — that constant is right. *[Correction, 2026-08-18, session 13.9
(step 11): the build's TQQQ constant was 0.86, not 0.95 — "that constant
is right" was wrong for TQQQ; the constant was corrected to the measured
0.95 by session 13.8. This session's expense-financing.csv also lists
TQQQ's constant as 0.95 in error; the authoritative table is
outputs/session-13.7a/expense-provenance.csv.]* D14's predicted direction (early-period
cost understated) is confirmed by measurement. Analytic bound on the
canonical effect: **the standing result overstates annualised return by
roughly 0.22–0.28 pp/yr** (dominated by UVXY's gap × exposure).
Financing: not derivable — TQQQ's FY2020 statement of operations
discloses no separate swap financing line; it is embedded in swap
gain/loss, so the step's derivation is infeasible from these filings and
the 2.14 constants stand, flagged under D14. The step-5 rebuild that
would apply the recovered deltas is halted with the gate.

**Step 7 — the open-to-open control [A].** Passive buy-and-hold TQQQ and
QQQ under both accumulation conventions on the identical 2012+ window:
convention gaps −0.34 pp and −0.09 pp annualised — negligible, as the
telescoping arithmetic requires. **Verdict: the +32 pp open-to-open
advantage is a property of WHEN the strategy trades, not accumulation
arithmetic.** Signed leverage deviation (the bias the 13.6 absolute
figure could not see): mean −1.3 bp/day (SE 0.4 bp), ≈ −3.2%/yr
compounded against multiple×underlying, monotone-ish across volatility
deciles — a real friction on held levered funds, and its sign means no
reconstruction bias inflates the o2o result. UVXY/SVXY remain excluded
(raw CFE files carry opens, but no validated constant-maturity open
index exists and building one has no NAV validation target), leaving
22.5% of dollar exposure unmeasured. `o2o-control.csv`.

**Step 8 — validation re-scoping and D12 [B→resolved].** 23 statistics
re-scoped: in-window values are canonical, full-window retained labeled
(`validation-rescope.csv` lists old value, new value, and every citing
location updated — session 13's sourcing, limitations, and sub-period
text; docs/STATE.md items 1 and 4; DECISIONS-v3.md 2.12a and the new
2.7a). The regime gradient's canonical value is fixed in the register at
**6.2× (D1 2.26% → D10 14.03%)** under the fully documented method;
session 12's 5.4× is recorded as not reproducible, the qualitative
limitation surviving every method tried. The annualised-TD definition is
fixed (geometric annualised difference); session 12's TD column is
recorded as non-reproducing with its own definition unrecoverable.

**Step 10 — register closures (final text in DECISIONS-v3.md).**
- **7.14 closed**: primary evaluation window 2011-10-03..2021-07-30
  (implementability boundary — the last unavailable fill); secondary
  synthetic-only extension 2007-01-03..2011-10-02, never merged; full
  sample retained; every benchmark and null runs on all three.
- **4.6 closed at 1,000,000**, liquidity check against the realized NAV
  path: **binding instrument BTAL at 4.9× its median daily dollar
  volume** (max position ~$895k vs ~$183k median, artifact-flagged
  denominator; every other instrument ≤0.18×). Position dollars are
  weight×NAV and independent of the raw-price convention.
- **1.9/2.11 completion rule closed**: unfilled slices sit in sleeve
  cash at DTB3; 40 primary-arm and 774 realized-arm events, all before
  2011-10-03, every one excluded by the 7.14 primary window.
- **D2 resolved**: 4.5 ported to config with the four arms and corrected
  reasoning; commission reported as a range (Fixed above, zero below).
- **4.4 amended**: uniform sweep stays the registered surface; the
  measured-profile attempt and its halt are recorded with today's date.

**Step 11 — 8.8 ladder amendment (pre-registered, not run).** Two
benchmarks written into 8.8: the matched-exposure levered QQQ benchmark
at mean effective exposure 1.70 (13.6's measurement; to be refreshed
when the rebuilt run exists) under the strategy's cost model, and the
long-legs-only benchmark (identical specification to ablation arm B,
entering as a comparison; figures may be shared). Neither executed.

## Provisional operating values, current status

1. ~~Starting NAV~~ — **closed** (4.6, 1,000,000, liquidity check
   recorded).
2. ~~IBKR commission inline~~ — **closed** (4.5 ported; four arms; Arm F
   remains the comparability default).
3. ~~Unavailable-fill completion rule~~ — **closed** (1.9/2.11; primary
   window excludes all events).
4. Split decode — closed in 13.6, **now carrying D15**: the decode is
   only as good as the vendor split record, and one record (SOXS) is
   missing a split. Pre-listing back-extension convention unchanged.
5. Negative cash at DTB3 symmetric — stands (measured immaterial).

## Defect register, updated

| id | status |
|---|---|
| D1, D8, D9 | repaired/resolved (13.6) |
| D2 | **RESOLVED** (4.5 ported, step 10) |
| D3 six absent IDs | open — documentation |
| D4 sleeves.py docstring | open — documentation |
| D5 7.14 | **CLOSED** (step 10) |
| D6 completion rule | **CLOSED** (step 10) |
| D7 4.6 | **CLOSED** (step 10) |
| D10 ENB window | open — specification (5.7 window still unregistered) |
| D11 SOXS window scoping | **RESOLVED** (step 8 blanket re-scope, 2.7a) |
| D12 gradient/TD non-reproduction | **RESOLVED** (2.7a canonical values + documented methods) |
| D14 post-boundary documents | open — specification; step 4 CONFIRMS the direction by measurement (expenses understated 0.2–0.95 pp/yr for five of seven sampled funds) |
| **D15 (new)** | vendor SOXS split record omits the 2021-03-02 1:15 reverse split; reconstruction 15× high before that date; step-1 gate fired; repair = split-table patch from the SEC filing — **correctness repair, unauthorized here, blocking the rebuilt canonical** |
| **D16 (new)** | per-year financing rates are not derivable from fund statements of operations (no separate swap financing line); the 2.14 single-year constants have no measured historical replacement path from filings |

## What would have to change to act on each finding

- **D15**: patch the SOXS split table from the SEC-documented split and
  re-run steps 5–6 — a **correctness repair** awaiting authorization;
  until then 13.6's headline stands with the D15 and step-4 caveats.
- **Step 4 expense deltas**: applying the recovered per-year ratios to
  the synthetic build is a **correctness repair of construction inputs**
  (the adjustment layer is staged in `s13_7_run.py`), gated behind D15.
- **Step 3's failed profile**: any future measured slippage model needs
  a spread source that is not range-based — a **specification change**
  with new data.
- **o2o verdict, ablation arms**: acting on either is a **specification
  change**; both remain unpromoted.

## Stop condition

Halted after step 12 with steps 5, 6, and 9 unexecuted per the step-1
gate. No arm promoted, no ablated specification adopted, no benchmark or
null executed, no holdout, no grid. Nothing committed; working tree left
dirty.
