# Session 11 report — expense schedule, tracking anchors, sector search, volatility diagnosis

Four independent closings run to completion; failures recorded, none
halting. Nothing acquired or frozen; no backtest, no performance statistic,
no commit. Suite unchanged at 199 passing.

## Step 4 — staged volatility diagnosis (`vol-roll-diagnosis.csv`) — run first, most decisive

**Stage A — the roll is exonerated.** The VIXY synthetic (construction B +
collateral − ER) against VIXY's frozen NAV reproduces session 00A exactly:
full correlation **0.99991**, minimum yearly **0.99926** (2015), TD
+0.39%/yr, and the volatility wedge is nil (75.7% vs 75.7% annualized).
Nothing session 10 changed sits upstream of this.

**Stages B/C — the failure is era-structured, not construction-layered:**

| Window | UVXY TD | UVXY corr | SVXY TD | SVXY corr |
|---|---|---|---|---|
| pre-2018 (2x / −1x) | **+23.6%/yr** | 0.906 | **+12.4%/yr** | 0.738 |
| post-2018 (1.5x / −0.5x) | +4.3%/yr | 0.986 | +1.1%/yr | 0.982 |

**Diagnosis: the frozen real-fund price series, not the synthetic.** The
February 2018 day-by-day shows it directly: real SVXY printed −13.2%,
−32.0%, −83.0%, +0.7% across Feb 2–7 while the −1× synthetic printed
−14.0%, **−96.1%, +26.0%**, +4.5% — the fund's 4:00 pm exchange close
lagged its 4:15 pm futures-settle NAV by a session at the crisis peak, then
converged. Exchange-close-vs-NAV dislocations on VIX-spike days add
variance to the real close-to-close series; compounding drag from added
variance is sign-independent, which is exactly the **positive-TD-on-both-
longs-and-shorts signature** that ruled out leverage and financing errors.
Session 00A validated against NAV and passed; session 10 validated against
exchange closes and failed. Reverse-split price quantization was probed and
exonerated (pre-2018 stored prices are large, tick/price ≤ 0.01%).
Post-2018 residuals of +1–4%/yr are fee/timing-scale, not failures of the
mechanism.

**Stage D — SVIX/UVIX are an index-family gap plus the same close-timing
class.** Construction B negated correlates 0.926 with ^SHORTVOL (read at
run time, not frozen) with a 4.7-point volatility gap (71.3% vs 66.6%) —
the Cboe roll differs measurably from construction B in weighting/timing.
Building SVIX from ^SHORTVOL itself tightens the fund validation from TD
+10.9%/yr (corr 0.9937, maxroll 19.2%) to **+7.6%/yr (corr 0.9891, maxroll
13.2%)** — better, still outside the 0.10 band, with the residual bearing
the same 4:00-close-vs-4:15-settle character as B/C.

**What this closes/leaves open:** the 2.3/2.22 roll construction stands
validated; the 2.7 volatility band failures are attributable to validating
against exchange closes rather than NAV, plus (for SVIX/UVIX) an index-
family difference now measured. Whether 2.7's volatility validation should
target NAV series, and whether the SVIX/UVIX synthetics should build from
the Cboe indices, are register decisions — diagnostics reported, no
recommendation.

## Step 1 — expense schedule (`expense-schedule.csv`, `expense-coverage.csv`)

Harvested, stated rows: **Direxion FY2025 costs-paid ratios from the
tailored shareholder reports** — TECL 0.83%, TECS 0.92%, SOXL 0.71%,
SOXS 0.87%, SPXL 0.81%, FAS 0.86%, LABU 0.92% — all **8–29 bp below the
1.00% constant session 10 built with** (a quantified refinement; by
session 10's step 7 equivalence, a 25 bp ER error ≈ 25–75 bp/yr of level
error depending on k).

Carried rows, marked as such: everything else. ProShares' financial-
statements document does not yield financial-highlights expense ratios to
the patterns tried, and their 485BPOS fee tables did not parse either
(different table wording); PT2 (UVXY/SVXY), Volatility Shares, and BTAL
registration documents were not parsed (bounded). Every carried row is
labelled CARRIED with its provenance; the coverage grid
(`expense-coverage.csv`) shows stated coverage only for the seven Direxion
funds in FY2025 and carried everywhere else. **2.13 moves from "never
retrieved" to "partially retrieved, one fiscal year, one trust" — the gap
is the finding.** Gross/net/waiver decomposition was not recoverable from
the tailored-report format (it publishes a single costs-paid ratio); the
schedule carries net only.

## Step 2 — published tracking error (`published-tracking-error.csv`)

**The issuers do not publish a tracking error against the levered daily
objective — the revised 2.7 band has no direct anchor from disclosure.**
What exists, by convention:

- **Direxion (tailored reports):** average-annual-return tables of fund
  NAV against the **unlevered** index (SOXL 61.13% vs NYSE Semiconductor
  Index 42.03% at 1 year; TECL 81.00% vs 36.17%; FAS 17.19% vs 14.25%;
  LABU 10.53% vs 16.53%; SPXL parsed NAV only). Because a daily-reset 3×
  fund's annual return is path-dependent, fund-minus-index from these
  tables is **not** a tracking error against the objective and cannot feed
  the band arithmetic. For the six sector funds the printed index returns
  are themselves against indices this study cannot independently obtain —
  every such row is flagged issuer-stated, unverifiable.
- **ProShares:** the harvested document is financial statements without an
  MDFP fund-vs-index table; nothing usable retrieved (bounded).
- **PT2 / Volatility Shares / BTAL:** not retrieved (bounded); absence
  recorded.

**Finding for 2.7:** no issuer-published anchor exists in the retrieved
disclosure for any of the seventeen funds. The band either anchors on a
quantity the study computes itself (with the circularity session 10
exposed) or on NAV-based validation as the step 4 diagnosis suggests for
the volatility legs. Left open, as instructed.

## Step 3 — sector index and sibling search (`sector-index-search.csv`)

**The sector proxy problem shrinks from six funds to one period of one
fund:**

| Family | Exact-benchmark unlevered ETF | Status |
|---|---|---|
| Technology (TECL/TECS) | **XLK** — already the proxy | exact, fee-only error |
| Semiconductors (SOXL/SOXS) | **SOXX, inception 2001-07-13** | **NEW FIND, filing-confirmed**: tracked PHLX through 2020 (126 filing mentions) and switched to the ICE Semiconductor Index per its 497 of 2021-04-22 — the same transition Direxion made ~4 months later. Exact benchmark in BOTH schedule periods; replaces SMH (19.3% max basket divergence) at the source. Not frozen — this session acquires nothing. |
| Financials 2022-08+ (FAS) | **XLF** — already the proxy | exact for the current period |
| Financials 2008–2022 (FAS) | **none found** | negative (bounded); the basket-mismatch residual stands for FAS's Russell era |
| Biotech (LABU) | **XBI** — already the proxy | exact, fee-only error |

Second question: **no 2007-era leveraged fund tracks the right families.**
ROM's Dow Jones U.S. Technology benchmark is now confirmed from ProShares
497K filings (8 hits, 2010–2012) rather than carried from session 10's
judgment; USD/UYG are the same DJ family by the trust's naming, anchored by
ROM's confirmation. A DJ-family sibling would validate mechanism only and
do nothing for proxy error; none was adopted.

**Consequence, stated without recommending:** if SOXX is frozen and adopted
as the semiconductor underlying, the largest proxy artifact in session 10's
validation (SOXS's 2845% max divergence, SOXL's 89.7%) is removed at the
source, and the un-fixable residual reduces to FAS 2008–2022 plus the
disclosed absence of sector pre-inception siblings.

## What did not match expectation

1. The volatility failures had nothing to do with the layers the session
   brief listed as suspects (multiple, fee) — the breaking "layer" is the
   validation TARGET (exchange closes vs NAV), plus a measured index-family
   gap for the 2022 funds.
2. Direxion's actual FY2025 expense ratios run 8–29 bp below the constants
   session 10 assumed — small but now stated rather than assumed.
3. SOXX — an exact-benchmark semiconductor ETF with 2001 inception that
   made the same PHLX→ICE transition — was sitting one search away; the
   proxy problem for semis was solvable at source all along.
4. Issuer tracking disclosure turns out to be structurally unusable for the
   revised 2.7 band (unlevered-index tables under daily-reset compounding),
   which sends the band question back to the register rather than to more
   harvesting.

## Decision ledger

- **2.13**: partially closed — stated FY2025 schedule for the seven
  Direxion funds, carried elsewhere, coverage grid honest.
- **2.7 equity band**: still open — no published anchor exists; the
  circularity stands as session 10 stated it.
- **2.7 volatility band**: diagnosis complete — construction sound at 1×
  against NAV; failures attributable to close-vs-NAV validation targets and
  (SVIX/UVIX) index-family mismatch, both measured.
- **Sector construction**: semis solvable at source (SOXX, unfrozen);
  tech/biotech already exact; FAS pre-2022 residual disclosed.
- **Volatility construction for SVIX/UVIX**: ^SHORTVOL-based build measured
  as tighter (+7.6 vs +10.9%/yr); adoption is a register call.

## Stop condition

Halted after step 5. Nothing acquired or frozen; rebuilt diagnostics live
under outputs only. No backtest, no performance statistic, no commit.
Session writes: `scripts/s11_voldiag.py`, five CSVs and this report under
`outputs/session-11/`. Working tree left dirty.
