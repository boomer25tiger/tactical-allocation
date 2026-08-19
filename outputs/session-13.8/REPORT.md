# Session 13.8 — repairs, rebuild, and the first canonical result

Run 2026-08-18. Scripts: `scripts/s13_8_steps12.py`, `s13_8_steps3456.py`,
`s13_8_canonical.py`, `s13_8_steps89.py`, `s13_7_mechanism.py` (staged in
13.7, executed here). Finding labels carried: **[A]** explains without
changing; **[B]** number wrong or unreliable; **[C]** register or code
defect. Binding order respected: repairs (1–5) → rebuild (6) → canonical
(7) → dependents (8–10) → register (11).

## The canonical result (step 7) — supersedes session 13.6's headline

Panels carry **equal weight** (2.8 hierarchy removed, post-hoc 9.10;
neither panel is primary). Repairs active: SOXS split patch (D15),
measured expense constants (step 3), 2.7a ratio-drift metric, corrected
prices throughout. All sanity checks pass on every combination.

**Primary window (2011-10-03 → 2021-07-30), 10 bp anchor:**

| panel | convention | cost model | comm | ann ret | vol | SR Lo | max DD | Calmar |
|---|---|---|---|---|---|---|---|---|
| synthetic | c2c | uniform | F | 31.7% | 53.1% | 0.98 | −66.6% | 0.48 |
| synthetic | c2c | tiered | **S** | **33.7%** | 53.1% | **1.01** | −66.5% | 0.51 |
| realized | c2c | uniform | F | 30.0% | 51.2% | 0.94 | −64.7% | 0.46 |
| realized | c2c | tiered | **S** | **32.0%** | 51.2% | **0.97** | −64.5% | 0.50 |
| realized | o2o | uniform | F | 60.0% | 51.2% | 1.50 | −52.9% | 1.13 |
| realized | o2o | tiered | **S** | **62.5%** | 51.2% | **1.52** | −52.8% | 1.18 |

The synthetic open-to-open cell is **structurally empty** (the
reconstruction is close-to-close by construction; an o2o synthetic needs
an intraday leverage model with no validation target — 4.1's recorded
objection). The panels agree within 1.7 pp on the primary window under
c2c, the fact that carried the equal-weight decision.

**Full sample (2007-01-03 → 2021-07-30), uniform × F:** synthetic c2c
18.16% ann / SR Lo 0.700 / MDD −77.1% at the anchor (0 bp: 23.28%;
50 bp: −0.34%); realized c2c 21.41% / 0.721 / −69.3%. **Early window
(2007-01-03 → 2011-10-02): synthetic-only, −9.97% ann, SR Lo 0.14, MDD
−63.7%**; the realized arm carries step 5's coverage instead of a
return: 2007–2009 have **zero** fully-fillable sessions (21–29% of
target dollars fillable), 2010 15.1% / 62.7%, 2011 36.0% / 82.0%.

**Zero crossings (uniform × F, measured):** synthetic c2c 49.2 bp
return / 82.0 bp Lo-Sharpe; realized c2c 65.4 / 93.0; realized o2o
(primary window) 122.7 bp return, Lo-Sharpe crossing beyond the 150 bp
extension range. Extension points stay outside the registered grid.

**Deltas vs 13.6 and attribution:** synthetic −0.16 pp ann / −0.003
SR Lo across the curve; realized −0.06 pp. At the anchor: 18.33% →
18.27% (SOXS patch, −0.06 pp) → 18.16% (expense corrections, −0.11 pp
against the −0.09 analytic estimate). The repairs moved the headline by
less than a fifth of a point; the window and cost-model structure moved
the reported picture far more.

**Commission arms (tiered@anchor, synthetic c2c, full window):** F
1.82 bp of traded / 1.54 pp-yr drag / 15.2% min-bound; T 1.87 bp /
1.58 pp; **S (canonical) 0.94 bp / 0.80 pp**; Z 0. By-year table in the
CSV shows the 2019-10 splice: Arm S equals F through 2019 and zero
after. Tier assignment (by measured median dollar volume, NOT
leverage): QQQ/TLT/UVXY/TQQQ/QLD tier 1 (0.2×), SPXL/SQQQ/SVXY/LABU/
SOXS/BSV tier 2 (0.5×), BIL/TECL/PSQ/SOXL/TECS/BTAL tier 3 (1.5×) —
2× UVXY in tier 1 on volume while 3× SOXL sits in tier 3 shows volume
drove it; SOXS/TECS/UVXY/BTAL medians carry session 05's stored-volume
artifact flag, disclosed.

**Sanity checks:** 6/6 hard checks PASS on all three combos.
Execution-lag sensitivity (reported per the 13.6 verdict, not a halting
failure): c2c combos again improve under T+2 on annualised return while
degrading on Lo-Sharpe — **but under open-to-open the check PASSES
outright** (T+1 38.3% ann / 0.93 SR Lo against T+2 29.5% / 0.70): the
one-session-early entry drag is specific to close fills; the next-open
fill already captures the turn. **[A]** — this localizes the timing
property to the fill convention.

## Step 1 — 2.7a metric correction [B→resolved]

Ratio drift is canonical (definition and mis-specification control in
the register; control recovered −0.949 pp of an injected −0.95).
All 23 re-scoped statistics recomputed (`metric-correction.csv`).
Largest revisions are the steep decliners: **SOXS +0.78 → +2.32%/yr;
TECS +0.83 → +2.01; SQQQ −0.55 → −1.25; SDS −1.14 → −1.54**; risers
compress slightly (TQQQ −1.13 → −0.73). **SOXS verdict: the 13.7
conclusion survives in its scope** — SOXS sits inside the sector-fund
band under the same metric — **with the honest addendum that the band's
upper edge is itself the inverse-sector class effect** (SOXS +2.32 and
TECS +2.01 drift above their real funds by ~2 pp/yr in-window: real-fund
frictions at −3× the construction does not model). Citing locations
updated (session 13 limitations, STATE.md, register 2.12a/2.7a).

## Step 2 — D15 SOXS patch [C→repaired]

Engine-level patch (frozen file untouched, 1.1): SOXS 2021-03-02 ratio
1/15. Controls: reconstructed 2017-10-31 = **16.24 vs SEC-sourced 16.25
(−0.06%)**; all 33 other instruments unmoved (worst unlevered 0.006%,
worst levered 0.586%); returns identical to 1e−9 on every session.
Effect: SOXS share counts ×15 where applicable (mean 8,104/order);
commission 3.08 bp of its traded value (was 0.28 under the wrong level).

## Step 3 — expense constants [B→repaired]

Gate **resolved with no extrapolation**: the build's ER is the net
operating ratio excluding interest (financing separate under 2.14), and
the like-for-like line was measured for every moved fund — Direxion
"Net Expenses 3,6" (excl-interest) reads **0.94–0.95 in every sampled
year for all seven funds**; ProShares "Expenses net of waivers" gives
TQQQ 0.95 and SH 0.89–0.90. Moved: TQQQ 0.86→0.95, SH 0.88→0.89,
Direxion seven → 0.95. UVXY/SVXY confirmed 0.95 (13.7a). Approximate
portfolio effect −0.09 pp/yr; measured −0.11 pp at the anchor.
`scripts/s10_build.py` updated; the engine bridges the on-disk panel
with an exact additive layer.

## Step 4 — financing base [A/C]

The split already exists structurally: the build accrues **DTB3
(observable, time-varying)** as the base; 2.14's constants are the
spread alone, so the 2025-anchoring concern attaches to the spread. The
bounded prospectus check is answered by the register's own history (no
prospectus states swap terms; D16: not derivable from statements of
operations). Sweep widened to **(25, 50, 75, 100, 150, 200) bp** with
the 2008–2009 funding-stress basis disclosed as an assumed bound.
Per-year all-in table in `financing-base.csv` (2007: ~5.2% all-in at
the 75 bp anchor; 2015: ~0.8%). Canonical anchor unchanged.

## Step 5 — early-window coverage [A]

`early-coverage.csv`: 106 of 987 evaluated sessions (10.7%) fully
fillable on the realized panel; by year as quoted above; per-instrument
availability timeline and per-sleeve unfillable fractions included
(T10/T11 worst — their targets lean on the 2008-12..2011-10 listings).
No return figure computed for this window; the reporting-form decision
stays open, now with its measurements in hand.

## Step 6 — panel rebuild [A]

Exact additive ER layer. Controls: **SQQQ shifted 0.000 pp** (constant
unchanged); **TQQQ shifted −0.089 pp, exactly its −0.09 correction** —
nothing but the injected constants changed. Every moved fund shifts by
its ER delta to ±0.001. Regime gradient unmoved: **6.2× (D1 2.28 → D10
14.08)**. SVXY residual unmoved: **+1.60%/yr above issuer NAV excl the
2.12b day** — still unattributed, still in the direction that helps the
strategy. TQQQ's drift vs real close moves −0.73 → −0.82 (the measured
constant is applied regardless; close-basis noise spans ±0.7–1.2).

## Step 8 — BTAL capacity [B]

Under **contemporaneous** (same-year) median dollar volume the
constraint sharpens: **worst ratio 6.08× in 2018**, 198 sessions with
position above the same-year median daily dollar volume, dates and
sizes in `capacity.csv`. Every other instrument's worst year is ≤0.55×
(TECL 2008). No cap applied, no impact charge; BTAL enters through
T11's tier-1 basket and crash terminal. The 4.6 closure's
sample-wide 4.9× was, if anything, understated for the thin years.

## Step 9 — concentration under per-year covariance [A; 5.7 registered]

Canonical ENB (per-year covariance, minimum-torsion) mean **9.06**
against 8.17 fixed-window; per-year gaps +0.9..+1.7 in most years.
Full set in `concentration.csv`: ENC tickers 3.1, underlyings 2.6,
effective exposure 1.71 mean; all five drawdown quintiles present (deepest
quintile: ENB 9.03, exposure 1.82; shallowest: 8.59 / 1.91); market-state
conditionals — exposure 0.78 in the worst trailing-return decile, 1.06
in the wildest vol decile, ~2.0 in calm regimes.

## Step 10 — ablation mechanism [A]

`ablation-mechanism.csv`. **Volatility overlay:** 167 episodes (mean
5.9 sessions, median 3); weighted contributions across the sample:
**directional +5.58, roll −4.82, reset/fee −0.01** — the overlay's
directional gains are nearly consumed by roll decay; decay is 46% of
gross positive magnitude. Carry cost is ever-present (worst weighted
years: 2017 −0.83, 2010 −0.60, 2012 −0.59); the paying years are
big-directional years (2020: directional +1.05 vs carry −0.30; 2018:
+0.73 vs −0.18; 2011: +0.43 vs −0.23). Entry decomposition (first held
day of each new UVXY position, n=469): total +0.23% = **directional
+1.07% + roll −0.84%** — entries do catch rising vol on day one; roll
bleeds from the first session. **Short equity:** the loss is almost
pure beta drag — SQQQ −39.4 pp arithmetic (beta −39.35, residual
−0.05), TECS −9.6, SOXS −9.0, PSQ −2.4; timing is mildly favorable
(underlying's held-day mean below unconditional for SQQQ/PSQ) but far
from enough. **Both components hedge in the correlation sense**: UVXY
slice vs rest −0.27; short-equity slice vs rest −0.52.

## Step 11 — register updates (final text in DECISIONS-v3.md)

- **2.8**: hierarchy removed, equal weight, post-hoc 9.10, with the
  13.6 figures on record and the early window synthetic-only.
- **4.1a**: o2o in the crossed table from 2011-10-03; synthetic o2o
  cell structurally empty with reason; the 2.8 open item resolved.
- **2.7a**: ratio drift canonical with the full definition and control;
  geometric-difference retained labeled.
- **5.7**: per-year covariance canonical (post-hoc 9.10), fixed-window
  retained as comparison.
- **4.4**: tiered arm added (0.2/0.5/1.5×, volume-tercile boundaries,
  assignment-vs-leverage reported) with its three
  strategy-favoring caveats and the artifact-flag disclosure.
- **4.5**: **Arm S canonical**; F the conservative bound and
  comparability arm; T a disclosed sensitivity with its pass-through
  anachronism; fee-of-zero ≠ cost-of-zero stated.
- **2.14**: DTB3 base / assumed spread split; sweep widened to
  (25..200) bp; config constant added.
- **2.13a**: expense corrections applied and recorded per fund with
  accessions; D14 expense component closed for every measured fund.

## Provisional operating values — final status

1. Starting NAV — **closed** (4.6, session 13.7).
2. Commission — **closed** (4.5 ported 13.7; Arm S canonical 13.8).
3. Unavailable-fill completion — **closed** (13.7; primary window
   excludes all events).
4. Split decode — closed (13.6), D15 patched here; **remaining
   convention: pre-listing back-extension of raw prices** (unchanged).
5. Negative cash at DTB3 symmetric — stands, measured immaterial.

## Defect register, final state through D16

| id | status |
|---|---|
| D1, D2, D5–D9, D11, D12 | closed/repaired in 13.6–13.7 |
| D3 six absent audit IDs | open — documentation |
| D4 sleeves.py −10 docstring | open — documentation |
| D10 ENB window | **CLOSED** (5.7 registered, step 9) |
| D14 | expense component **CLOSED for all measured funds** (13.7a artifact finding + 13.8 corrections); financing component narrowed to the spread and bounded by the widened sweep; the post-boundary-documents register question stands for constants generally |
| D15 SOXS split gap | **REPAIRED** (step 2, controls exact) |
| D16 financing derivability | open — spread remains assumed, swept (25..200 bp) |
| **new [A]** | the inverse-sector class drift (~+2 pp/yr SOXS/TECS above real funds in-window) is now visible under the sensitive metric — a construction limitation candidate for the writeup, documentation |

## What would have to change to act on remaining findings

- Inverse-sector class drift, SVXY +1.60 residual: attribution would be
  a **measurement session**; any construction change a **specification
  change**.
- BTAL capacity (6.08× in 2018): any cap or impact charge is a
  **specification change**; the measurement is on record for the
  writeup.
- Early-window reporting form: a **register decision**, now with its
  coverage measurements in hand.
- Timing property (c2c-specific per the o2o lag result): execution
  convention questions are **specification changes** under 4.1/4.1a.
- D3/D4: **documentation**.

No recommendation is made on any of them.

## Stop condition

Halted after step 12. No arm promoted beyond the step-11 register
updates; no ablated specification adopted; no benchmark, null, grid, or
holdout executed. Nothing committed; working tree left dirty.
