# Session 12 report — SOXX adoption, NAV revalidation, expense refinement, final construction

The three session 11 fixes executed and the full validation suite rerun on
the final construction. No portfolio, no position, no performance
statistic; nothing committed. Suite unchanged at 199 passing.

## Step 1 — series frozen (`acquisition-manifest.csv`)

- **SOXX**: 6,309 rows, 2001-07-13 → 2026-08-14, zero interior nulls, sha
  `3480ccefdf3f…`. **The vendor record shows a single 3-for-1 split on
  2024-03-07** (boundary-consistent, 0 failures) — the session brief's
  stated 2016 3:1 and 2021 2:1 splits are not in the vendor record; the
  discrepancy is flagged rather than reconciled, and the split-boundary
  check passed on what is actually there.
- **UVXY NAV and SVXY NAV — obtained**: ProShares' historical-NAV endpoint
  (the same source session 00B used for VIXY) served both in full,
  2011-10-03 → 2026-08-14, 3,738 rows each, frozen under
  `data/raw/nav/` (sha `0b686222d08c…`, `833e8bac7c55…`).
- **SVIX/UVIX NAV — not obtainable** (bounded single attempt at the
  issuer's site): their validation stays against exchange closes with the
  known dislocation class; disclosed limitation.

## Step 2 — semiconductor rebuild (`semiconductor-rebuild.csv`)

| | SOXL before (SMH) | SOXL after (SOXX) | SOXS before | SOXS after |
|---|---|---|---|---|
| Correlation | 0.9823 | **0.9971** | 0.9618 | **0.9784** |
| Ann TD | +3.75%/yr | **+1.06%/yr** | +3.10%/yr | +6.21%/yr |
| Max roll-252 | 89.7% | **17.8%** | 2845% | 1394% |

**SOXL: the proxy was the cause** — correlation to 0.997, tracking
difference to +1.1%/yr, maximum divergence from 89.7% to 17.8%. The
basket mismatch previously entering the construction is now quantified
directly: **SOXX vs SMH correlate 0.9714 with 7.98%/yr tracking sd and a
23.6% maximum rolling divergence** — that was inside every semiconductor
synthetic before this session.

**SOXS: partially — a recorded diagnostic, not a clean win.** Correlation
and maximum divergence improved, but the mean TD worsened to +6.2%/yr and
the maximum divergence remains enormous (1394%). At −3× across fourteen
validated years, small residual frictions in the real fund (short
financing beyond the 70 bp haircut, stress-era borrow, close-print noise)
compound into large level divergence even on the exact benchmark. Recorded
with diagnostics per the failure-handling rule.

**Benchmark misalignment window (2021-04-22 → 2021-08-24, 87 sessions):**
SOXX tracked ICE while the funds still tracked PHLX. Measurable but
modest: correlation stayed 0.996–0.997 through the window with TD
+6.3%/yr (SOXL) / −5.9%/yr (SOXS) annualized over those 87 sessions —
recorded as a known misalignment, not smoothed.

## Step 3 — volatility NAV revalidation (`volatility-nav-validation.csv`)

**The dislocation hypothesis is confirmed as directly as it can be:**

| Fund | Era | vs exchange close (S11) | vs NAV (this session) |
|---|---|---|---|
| UVXY | pre-2018 | +23.6%/yr, corr 0.906 | **−1.06%/yr, corr 0.9998** |
| UVXY | post-2018 | +4.3%/yr, corr 0.986 | **+1.63%/yr, corr 1.0000** |
| SVXY | pre-2018 | +12.4%/yr, corr 0.738 | −23.7%/yr, corr 0.808 |
| SVXY | post-2018 | +1.1%/yr, corr 0.982 | **+1.34%/yr, corr 0.9999** |

February 2018, day by day:

| Date | Synthetic | NAV | Exchange close |
|---|---|---|---|
| 2018-02-02 | −13.99% | −14.00% | −13.21% |
| 2018-02-05 | **−96.09%** | **−96.18%** | −31.99% |
| 2018-02-06 | +25.96% | **+187.10%** | −82.96% |
| 2018-02-07 | +4.49% | +4.56% | +0.74% |

**On the crisis day itself the synthetic matched NAV to nine basis points
(−96.09 vs −96.18) while the exchange close said −32.** UVXY resolves
completely against NAV in both eras. SVXY resolves everywhere except one
session: 2018-02-06, when the real fund's NAV rebounded +187% against the
index-implied +26% — the fund's actual portfolio departed from its index
that day (intraday de-risking during the termination-scale event), a
single-session portfolio divergence that dominates the pre-2018 NAV-basis
TD (−23.7%/yr ≈ that one day spread over the era). Every other day in the
window matches to within decimals.

**SVIX/UVIX (NAV unobtainable, validated against closes):** built from the
Cboe index family per session 11's measurement. One mis-specification
caught in-session: the first build added collateral yield on top of the
Cboe indices and the TD rose by almost exactly the bill yield (+7.6 →
+13.2%/yr) — evidence the indices are total-return-like; corrected to a
no-ref build. Final: **SVIX corr 0.9888, TD +8.87%/yr, maxroll 13.2%;
UVIX corr 0.9912, TD +7.54%/yr, maxroll 23.9%.** The measured index-family
gap stands in the writeup: construction B negated correlates 0.926 with
^SHORTVOL, annualized vol 71.3% vs 66.6%.

## Step 4 — expense refinement (`expense-refinement.csv`)

Stated FY2025 Direxion ratios applied; expected change (ER enters at 1×)
against measured change:

| Fund | Old→new ER | Expected ΔTD | Measured ΔTD | New TD |
|---|---|---|---|---|
| TECL | 1.00→0.83 | +0.17pp | **+0.17pp** | −0.06%/yr |
| TECS | 1.00→0.92 | +0.08pp | **+0.08pp** | +1.11%/yr |
| SPXL | 1.00→0.81 | +0.19pp | **+0.19pp** | +0.08%/yr |
| FAS | 1.00→0.86 | +0.14pp | **+0.14pp** | +1.23%/yr |
| LABU | 1.00→0.92 | +0.08pp | **+0.08pp** | +1.45%/yr |

**Expected equals measured to the basis point on all five** — the build
arithmetic is verified. SOXL/SOXS are marked confounded (underlying
changed simultaneously); all non-Direxion funds stay carried and marked.

## Step 5 — final validation, all nineteen (`final-validation.csv`)

Primary (target stated per fund): the index-family funds sit at corr
0.993–0.999 with |TD| ≤ 1.3%/yr; TECL/TECS/LABU at 0.995–0.998 with |TD|
≤ 1.5%; SOXL 0.9971/+1.06%; FAS 0.9886/+1.23%; UVXY-vs-NAV 0.9998/+0.47%;
the recorded exceptions are SOXS (+6.21%, maxroll 1394%), SVXY-vs-NAV full
(−9.45%/yr, the single 2018-02-06 session), and SVIX/UVIX against closes
(+8.9/+7.5%/yr). Sibling validation 2006–2010 and multiple invariance
reproduce session 10 (unchanged inputs there). Financing sensitivity
unchanged.

**The regime gradient did NOT flatten: D1 1.71% → D10 9.13%, ratio 5.4×
(session 10: 5.3×).** The SOXX adoption removed the semiconductor proxy
artifact without touching the gradient — the gradient is a property of the
construction-vs-exchange-close comparison at high volatility, not of the
semiconductor proxy. **The writeup's concession stands: the construction
is weakest in exactly the high-volatility regimes where the strategy's
bear branches operate, and the 2007–2010 extrapolation is the weak case.**

## Per-fund status, one line each

- **TQQQ QLD SQQQ PSQ QID** — validated vs closes 2006/2010→2026 (QQQ
  underlying, wedge quantified); pre-inception 2007–2010 covered by
  PSQ/QID sibling mechanism validation.
- **SH SSO SDS SPXL** — validated vs closes 2006/2008→2026 (SPY exact);
  same sibling coverage incl. 2008.
- **TECL TECS** — validated vs closes 2008-12→2026 on the exact benchmark
  ETF; pre-inception unvalidated (no sector sibling; disclosed).
- **SOXL** — validated vs closes 2010-03→2026 on SOXX (exact both
  periods); 87-session index misalignment recorded; pre-inception
  unvalidated.
- **SOXS** — same window; recorded exception (TD +6.2%, maxroll 1394%) —
  −3× compounding of residual real-fund frictions.
- **FAS** — validated vs closes 2008-11→2026; underlying exact only from
  2022-08; Russell-era basket mismatch disclosed and unfixable.
- **LABU** — validated vs closes 2015-05→2026 on the exact benchmark ETF.
- **UVXY** — validated vs issuer NAV 2011-10→2026, corr 0.9998, both
  multiple eras; pre-inception (2007–2011) rests on construction B's
  00A/00B validation.
- **SVXY** — validated vs issuer NAV except the single 2018-02-06
  portfolio-departure session, which is disclosed; same pre-inception
  basis.
- **SVIX UVIX** — validated vs exchange closes only (NAV unobtainable),
  +7.5–8.9%/yr residual of the close-timing class; LONGVOL proxied by
  −SHORTVOL for UVIX (flagged).

## Proposed 2.7 band — for confirmation, not written, not applied

A stipulation, two tiers, expressed as daily-return correlation and
annualized tracking difference against the stated validation target:

- **Tier 1 — exact or near-exact underlying** (all Nasdaq-100 and S&P 500
  funds; TECL/TECS on XLK; SOXL/SOXS on SOXX; LABU on XBI; FAS from
  2022-08-01; UVXY/SVXY against NAV): **correlation ≥ 0.98 and |annualized
  tracking difference| ≤ 2.0%.**
- **Tier 2 — approximate underlying** (FAS before 2022-08-01, and any
  future fund whose exact benchmark is unobtainable): **correlation ≥ 0.95
  and |annualized tracking difference| ≤ 4.0%.**

Stated as a stipulation. Information for the confirmer, not applied here:
against the final table, SOXS (+6.2%), SVXY-full-window-vs-NAV (−9.5%/yr,
one-session-driven), and SVIX/UVIX (+7.5–8.9% vs closes) would sit outside
Tier 1 as measured, and the register would need to decide era/target
qualifications (e.g., SVXY excluding the 2018-02-06 session, SVIX/UVIX
pending NAV) rather than have this session decide them.

## What did not match expectation

1. SOXX's vendor split record (one 3:1 in 2024) contradicts the session
   brief's stated 2016/2021 splits — flagged, not reconciled.
2. SOXS worsened on mean TD under the exact benchmark even as correlation
   and divergence improved — the residual is real-fund friction at −3×,
   not basket mismatch.
3. The SVIX/UVIX collateral double-count — caught by the TD moving by
   exactly the bill yield, corrected in-session and recorded.
4. SVXY's one-day portfolio departure (2018-02-06, NAV +187% vs index
   +26%) — the only session in seven pre-2018 years the NAV-basis
   validation cannot match, and it dominates that era's TD.
5. The regime gradient's indifference to the SOXX adoption (5.4× vs 5.3×)
   — the concession about 2008 extrapolation survives the best fix
   available.

## Stop condition

Halted after step 7. No backtest, no performance statistic, no commit.
Session writes: SOXX and two NAV parquets + manifest, rebuilt synthetics,
`scripts/s10_build.py` edits, `scripts/s12_validate.py`, five CSVs and
this report under `outputs/session-12/`. Working tree left dirty.
