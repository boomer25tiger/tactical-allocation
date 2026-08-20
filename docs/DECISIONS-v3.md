# DECISIONS v3 — the register as of session 12.6

Reissued 2026-08-18 by session 12.5, amended 2026-08-18 by session 12.6
(conversation-only closures added: 2.7 final form, SOXS sourcing, SVXY
2018-02-06 exclusion, 8.8 full specification, 4.4 range retention, 4.6
restatement), replacing the stale v2 (archived as
ARCHIVE-DECISIONS-OPEN-v2-STALE.md, which predates session 00A and carries
wrong values). Reconstructed from the session reports under `outputs/` and
the session conversation. Where a decision was closed, reversed, and
re-closed, the sequence is recorded, not only the final value.

Canonical numeric values live in `src/config.py` with decision IDs in
comments; this register carries status, provenance, and history. Where the
two could ever disagree, config is what the code runs and this file says
why.

**[A] marks a closure resting on a stated assumption or stipulation rather
than a measurement** (9.10 provenance requirement).

---

## 1. Data conventions

- **1.1 — closed.** Pull once, hash, record pull date and library version,
  never re-pull. Every freeze script refuses overwrite. Manifests under
  `outputs/session-*/`.
- **1.2 / 1.3 — closed.** Total return for signals and for accumulation.
- **1.4 — closed.** Back-adjusted total return for signals/returns; raw
  close retained on a parallel path for share counts and commission
  (two-path loader, `src/data.py`).
- **1.5 — closed.** AdjOpen = Open × (AdjClose / Close), pulled with
  `auto_adjust=False, actions=True`.
- **1.6 — closed.** Wilder RSI, alpha = 1/n, SMA seed of the first n
  changes (`src/indicators.py`, lifted from 00C with the null-handling
  defect fixed — see corrections).
- **1.8 — closed, REDEFINED (history).** Originally a ±50% single-session
  return bound. That test fires on legitimate moves (UVXY +96%, SVXY −90%
  on 2018-02-06) and would not have caught either session 04 factor
  defect. **Session 07 redefined it as the memory-free split-boundary
  consistency check** (adjusted = raw ÷ cumulative split factor on the
  sessions either side of every boundary, tolerance 25%): applied
  panel-wide, 69 boundaries, zero failures.
- **1.9/2.11 unavailable-fill completion — closed (session 13.7,
  2026-08-18).** A target whose fill-session price does not exist sits in
  sleeve cash accruing DTB3. Provisional status (session 13's operating
  value 3) closed. The rule governs 40 primary-arm events and 774
  realized-arm events, all before 2011-10-03; the primary evaluation
  window under 7.14 excludes every one of them.
- **1.9 — closed in two halves (history).** Forward-fill prohibited;
  threshold test with unavailable input reads false; pairwise comparison
  with unavailable side raises (session 01). Interior-gap treatment left
  open until real gaps existed; session 08's ^NETR freeze surfaced the
  first three; **session 09 closed interior gaps as "skip"** — the missing
  observation is removed, the next session carries a multi-day return, and
  the recursion continues on the compressed series (`INTERIOR_GAP_TREATMENT`,
  validate-pinned). Session 01's interim segment-reseeding implementation
  was replaced; regression tests pin skip.
- **1.11 — closed.** Total return = (Close_t + Div_t)/Close_{t−1} − 1,
  reinvestment at the ex-date close.
- **1.14 — closed.** All series truncated at 2026-08-14. (Session 00E
  applied this to the original panel; every later freeze applies it at
  pull time.)

## 2. Construction

- **2.1 / 2.2 — closed.** All leveraged/inverse exposures reconstructed
  from underlying returns; synthetics under `data/interim/synthetics/`,
  built by `scripts/s10_build.py`:
  r_syn = M·r_u + (1−M)·ref − k·spread − ER/252, daily reset.
- **2.3 / 2.22 — closed.** VX construction B (the investable S&P-roll
  index, `vx-cm30-b.parquet` `index_level`), validated in 00A/00B and
  re-confirmed session 11 stage A at correlation 0.99991 vs VIXY NAV
  (minimum yearly 0.99926).
- **2.5 — closed, REVERSED ONCE (history).** Originally the KFA MLM Index
  (history from 1988) behind the trend leg. Session 00-era work assumed
  it; the index proved unobtainable without licensing and only the KMLM
  ETF (2020-12) existed on disk. **Rewritten before session 01 to a daily
  managed-futures trend series; RYMFX selected** (2007-02-22+, 4,901 rows,
  gap-free). **2.5a:** RYMFX is NAV-priced with a one-session posting lag;
  the lag is applied once at load (`src/data.py`), asserted once-only.
  EDGAR review (session 07): no strategy change after 2013-01-29; the 2015
  Class H→P redesignation kept the same share class and ticker; the 2.10
  holdout is not contaminated.
- **2.6 — closed.** BTAL has no multiple (anti-beta long/short);
  validation routed to the AQR BAB factor; excluded from synthetics.
- **2.7 — closed as report-without-threshold, REVERSED TWICE (history;
  final closure recorded session 12.6).** (i) Original: validate synthetics against benchmark
  indices, banded by exposure class. (ii) Session 09 measured index-level
  validation impossible for six funds (indices gated at every resolution;
  SMH 19.3% max divergence from PHLX) → **revised to validate against the
  real fund's frozen price history**, bands unchanged. (iii) Session 10
  exposed the equity band as near-circular (the objective must be proxied
  by the same underlying the synthetic builds on; objTE equalled synthetic
  TE to two decimals; 12/12 "passed" a band that cannot fail). (iv)
  Session 11 found no issuer-published tracking error exists against the
  levered daily objective. (v) **Closed as report-without-threshold
  (conversation, recorded session 12.6). No pass-fail band.** Report
  correlation, annualised tracking difference, and maximum rolling
  divergence per fund, with the validation target and window stated. Two
  external anchors were sought and neither exists: issuers publish no
  tracking error against the levered daily objective, only against the
  unlevered index, which under daily-reset compounding is a different
  quantity (session 11); and a separate search established that Direxion
  and ProShares prospectuses describe index correlation risk
  qualitatively with no numeric target. The two-tier band session 12
  proposed was rejected because its thresholds fell in the empty gap
  between the eleven passing funds at 0.993–0.999 correlation and the
  three exceptions at 6.2–8.9%/yr tracking difference, so any value in
  that gap produces the same partition and the threshold does no work.
  [A — rests on the absence of an anchor rather than on a measurement]
- **2.8 — hierarchy removed (session 13.8, 2026-08-18; post-hoc under
  9.10).** The panels carry EQUAL weight: synthetic and realized are
  reported side by side wherever both fill, and neither is described as
  primary. The change removes a hierarchy rather than promoting a
  figure; for the record, the realized arm read 21.47 percent against
  the synthetic's 18.33 in session 13.6 before the change was made, and
  in the 13.8 canonical the panels sit within 1.7 pp of each other on
  the primary window. History: all-synthetic primary was closed
  pre-result on implementability grounds; 7.14's primary window
  (2011-10-03+) contains no unavailable realized-arm fills, so that
  reason does not bind inside it. The early window (2007..2011-10) is
  synthetic-only with realized coverage reported instead of a return.
- **2.9 — closed.** Sample starts 2007-01-01.
- **2.10 — closed.** Holdout boundary 2021-08-01, untouched. No
  post-boundary quantity has been computed anywhere.
- **2.11 — closed (history).** Warm-up: v2 carried 292 (sum-based);
  re-derived as max(longest SMA, RSI seed convergence) + 10 = **210**
  (session 01 continuation). The "unavailable input" half: threshold-false
  / pairwise-raise (settled session 01); the pairwise raise marks where
  the once-open half lands (RYMFX seeds ~2007-03, so roughly the first
  sixty sample sessions raise at the XLK>TREND sites).
- **2.12 — closed.** Proxy underlyings per family: QQQ (NDX funds), SPY
  (SPX funds), XLK (exact), **SOXX (exact both semiconductor periods,
  adopted session 12; replaced SMH)**, XLF (exact from 2022-08 only), XBI
  (exact). Proxy errors quantified session 09; see limitations in
  STATE.md.
- **2.12a SOXS sourcing — closed (conversation, recorded session 12.6;
  exception re-scoped session 13.7; metric corrected session 13.8).**
  Keep the synthetic. **Canonical in-window exception figures:
  correlation 0.997, annualised ratio drift +2.32 percent per year
  (the +0.78 previously recorded was the compressed geometric-difference
  form; TECS reads +2.01 under the same metric — an inverse-sector-fund
  class effect, not SOXS-specific), maximum rolling divergence 14
  percent (window ≤ 2021-07-30).** The previously recorded 6.21 percent and
  1394 percent are full-window figures (2010-03..2026-08) dominated by
  post-boundary sessions — real-fund frictions compounding at −3× in
  the 2021+ semiconductor cycle — retained with that label. The
  alternative, listed SOXS from 2010-03, was rejected because it would
  remove T11's bull-branch inverse basket across 2008.
- **2.7a validation-statistic scoping — closed (session 13.7, 2026-08-18,
  resolving D11/D12).** Every construction-validation statistic whose
  window crosses 2021-07-30 is re-scoped: the in-window value is
  canonical; the full-window value is retained labeled as such
  (outputs/session-13.7/validation-rescope.csv carries the complete
  list). The regime gradient's canonical value is **6.2× (D1 2.26% →
  D10 14.03%)** under the documented method: pooled synthetic-minus-real
  daily return deviations across the twelve equity levered synthetics,
  deciles of the underlying's trailing 60-session volatility
  (annualised), SD of deviations annualised per decile, ratio D10/D1,
  window ≤ 2021-07-30. Session 12's recorded 5.4× (D1 1.71% → D10
  9.13%) could not be reproduced under stated reimplementations and is
  retained as a full-window historical figure; the qualitative
  limitation survives under every method tried. The annualised
  tracking-difference definition is fixed as the geometric annualised
  return difference, synthetic minus real, over the joint window
  (session 12's TD column does not reproduce under this definition and
  its own definition is not recoverable from the session record).
  **Amended (session 13.8, 2026-08-18): the canonical tracking metric is
  the ANNUALISED RATIO DRIFT, (prod(1+r_syn)/prod(1+r_real))^(252/n) − 1
  over the joint in-window session set. Reason: the geometric-difference
  form's sensitivity scales with one plus the real fund's annualised
  return, so on a steep decliner it reports a small fraction of true
  divergence (measured: an injected 0.95 pp/yr error surfaced as 0.148
  pp under the difference form and 0.949 pp under ratio drift — the
  13.7a/13.8 mis-specification controls). Compression follows the sign
  of each fund's return: most lenient on inverse and volatility funds,
  mildly amplifying on risers. Geometric-difference values are retained
  beside the canonical figures, labeled. All 23 re-scoped statistics are
  recomputed under ratio drift in
  outputs/session-13.8/metric-correction.csv.**
- **2.12b SVXY 2018-02-06 — closed (conversation, recorded session
  12.6).** Excluded from validation, as a stated exclusion with the
  reason: the fund's NAV rebounded 187 percent against an index-implied
  26 percent during the termination-scale event, which is a portfolio
  departure from the index rather than a construction failure. Every
  other session in the pre-2018 window matches to decimals.
- **2.13 — partially closed.** Expense schedule: stated FY2025 costs-paid
  ratios for the seven Direxion funds (TECL 0.83, TECS 0.92, SOXL 0.71,
  SOXS 0.87, SPXL 0.81, FAS 0.86, LABU 0.92); everything else CARRIED
  constants, marked in `outputs/session-11/expense-schedule.csv`. Build
  arithmetic verified: expected ΔTD = measured ΔTD to the basis point
  (session 12).
- **2.14 — closed (history).** v2: 50 bp constant, open pending 3.11.
  Session 08: no prospectus states a spread; year-end per-swap rates live
  in shareholder-report schedules. Session 09 harvested them: Direxion
  states SOFR +28..+99 bp (median ≈ 75) per swap; ProShares publishes
  flat rates implying longs ≈ bills +107–110 bp, shorts RECEIVE ≈ bills
  −62..−77 bp. **Closed at 75 bp long anchor / 70 bp short haircut
  (`FINANCING_SPREAD_BP`, `FINANCING_SHORT_HAIRCUT_BP`), swept around; the
  anchor is a single-fiscal-year snapshot and that is disclosed.** [A —
  the level is measured, its constancy through time is assumed]
  **Amended (session 13.8, 2026-08-18): the financing charge is
  explicitly split into an OBSERVABLE BASE — DTB3, time-varying, already
  what scripts/s10_build.py accrues per session — and the ASSUMED SPREAD
  above; the 2025-anchoring concern (D14) attaches to the spread alone.
  The sweep is widened to `FINANCING_SPREAD_SWEEP_BP` = (25, 50, 75,
  100, 150, 200) bp: a spread negotiated in 2008-2009 funding stress was
  almost certainly wider than the FY2025 median, fund-level historical
  terms are unrecoverable (D16), and the 200 bp cap brackets the stress
  case without asserting a measured level. Prospectuses state no such
  terms (session 08; reconfirmed as the bounded check in
  outputs/session-13.8/financing-base.csv). Per-year all-in rates under
  the split are tabulated there.**
- **2.15 — closed.** Borrow absorbed into the swap interest leg for the
  five swap-based inverse equity funds (filings' own language); SVXY/SVIX
  are futures-based with no swap borrow (economics in the futures basis
  under 2.3). Two treatments by structure, not one class.
- **2.19 — closed.** Pre-inception substitutions: 3-month bill TR for BIL,
  1–3y Treasury index for BSV, AGG for BND.

## 3. Instruments and indices

- **3.9 — dissolved and executed.** Nasdaq-100 Equal Weighted TR (^NETR)
  is free; frozen session 08 (`data/raw/index/NETR.parquet`, 3 interior
  gaps retained as explicit nulls — the study's only interior gaps).
- **3.11 — closed.** Complete per-date multiple and benchmark schedule at
  filing grade: `outputs/session-08/fund-schedule.csv`, encoded as
  `src/schedule.py` with contiguity tests and the "on or about" qualifier
  carried on the SOXL/SOXS and FAS boundaries.
- **3.12 — closed provisionally.** SMH pre-2013 return basis: constant
  accrual 1.5%/yr (measured 1.31% net basket yield 2007–2012 is a lower
  bound — nine of twenty tickers returned no dividend history);
  sensitivity arm (0, 1, 2). [A — the 1.5 central value interpolates a
  lower-bound measurement]

## 4. Execution

- **4.1 — closed.** Signal at T close, fill at T+1 close, close-to-close
  accumulation; open-to-open arm retained (degenerate for RYMFX, detected
  generally).
- **4.1a open-to-open promotion — recorded (session 13.7a, 2026-08-18;
  post-hoc under 9.10).** 4.1 closed with close-to-close primary and
  open-to-open as a specification-curve arm under 9.8, so open-to-open
  was pre-registered before any result existed. Session 13.6 measured it
  at +33.3 percentage points annualised at zero cost against
  close-to-close on a matched realized panel; session 13.7's passive
  control found accumulation-convention gaps of −0.34 and −0.09
  percentage points, confirming the advantage is not accumulation
  arithmetic; signed leverage deviation at −1.3 basis points daily runs
  against the arm rather than inflating it. **Promotion was decided
  after those measurements and is therefore post-hoc. Both arms are
  reported at equal prominence in the writeup, with the pre-registration
  provenance stated.** Unresolved consequence, recorded without
  resolving it: the synthetic reconstruction is close-to-close by
  construction, and an open-to-open backtest on synthetic funds requires
  an intraday leverage model with no clean validation target — 4.1's
  recorded objection — so under open-to-open primary the canonical
  result must come from the realized panel, which makes **2.8's
  all-synthetic primary designation a decision the user has not yet
  closed. OPEN.** 7.14's primary window from 2011-10-03 contains no
  unavailable fills in the realized arm, so the original reason for
  synthetic primary does not bind inside that window. **Amended
  (session 13.8, 2026-08-18): open-to-open reports in the crossed
  headline table restricted to 2011-10-03 onward; the synthetic
  open-to-open cell is structurally empty — the synthetic
  reconstruction is close-to-close by construction, and an open-to-open
  synthetic requires an intraday leverage model with no validation
  target (4.1's recorded objection). The 2.8 question this entry left
  open is resolved by 2.8's equal-weight amendment of the same date.**
- **4.1b headline designation — recorded (session 13.9, 2026-08-18;
  post-hoc under 9.10).** The paper's abstract figure is the cell:
  **open-to-open, realized panel, primary window (2011-10-03+), tiered
  class-based slippage with the opening-auction premium at the 10 bp
  anchor, commission Arm S, Lo-corrected Sharpe.** Designated value at
  recording: **Lo-Sharpe 1.37 (annualised return 52.9%, volatility
  51.1%, maximum drawdown −53.1%)**. Conditional gate satisfied: the
  step-4 volatility passive-convention control returned negligible gaps
  (UVXY −0.24 pp, SVXY +0.66 pp, SOXL −1.74 pp, SQQQ +0.22 pp
  annualised), extending 13.7's verdict to the previously uncontrolled
  22.5% of dollar exposure. Full history: open-to-open was the ORIGINAL
  specification; 4.1 closed with close-to-close primary because the
  synthetic reconstruction is exact close-to-close and an o2o synthetic
  needs an intraday leverage model with no validation target; equal
  panel weighting (2.8) and the 7.14 primary window — where every fund
  is listed and the realized panel carries actual opening prices —
  dissolve that objection. Session 13.6 measured +33.3 pp and session
  13.8 measured 60.0 vs 30.0 before the designation was made; 13.8's
  execution-lag check passes outright under o2o and fails under c2c.
  The designation RESTORES the original specification after the
  objection that displaced it ceased to apply, and it was made after
  the measurement existed — post-hoc, recorded as such. The headline
  loses close-to-close's panel-agreement support (o2o exists on the
  realized panel alone); the c2c panel agreement within 1.7 pp is
  reported alongside instead, and close-to-close is reported at equal
  prominence throughout per 4.1 and 2.8.
  **Gate amendment (session 14, 2026-08-18).** The session 13.9 step-4
  gate was written as negligible against material with **no numeric
  boundary fixed before the measurement**, which is disclosed here as
  post-hoc under 9.10. Two arguments support the pass and neither was
  stated in the 13.9 report. First, the four measured convention gaps
  carry mixed signs at −0.24, +0.66, −1.74, and +0.22 percentage points
  with a mean near −0.28, which is the signature of estimation noise
  rather than of systematic accumulation arithmetic, since a genuine
  arithmetic asymmetry would carry a consistent sign. Second, the
  largest single gap of 1.74 percentage points accounts for 7.6 percent
  of the 22.9-point convention effect being explained, so the effect
  survives even if that gap is treated as real and signed against the
  arm. The control is not re-run and the gate is not reversed.
- **4.1c segment decomposition — recorded (session 14, 2026-08-18).**
  The open-to-open advantage is decomposed into an overnight component
  (previous close to open) and an intraday component (open to close) on
  the designated cell. **Verdict: TRADE TIMING, not segment selection.**
  The strategy's overnight leg contributes 3.582 in arithmetic sum
  against an intraday leg of 2.621, an overnight share of 0.577, against
  0.557 for an equal-weight buy-and-hold of the traded universe and
  0.685 for passive QQQ over the same window. The strategy's overnight
  share sits between the two passive references rather than materially
  above either, so the open-to-open advantage is not located in
  systematic exposure to the overnight segment and the paper describes
  it as a property of when the strategy trades. Recorded alongside: an
  overnight-only hold of the traded universe returns 8.50 percent
  annualised at a Lo-corrected Sharpe of 1.60 while an intraday-only
  hold returns −6.48 percent at −2.03, so the universe's return is
  concentrated overnight for passive and active holders alike, and the
  segment split is an attribution of a held position rather than a
  separately tradeable line, since capturing it would require a daily
  round trip the cost model would charge. The first computation of this
  decomposition paired the lagged weight with the current session's
  intraday move rather than the prior session's, which inverted the
  verdict; the reconciliation control against the traded return caught
  it, the mean absolute gap falling from 63 to 7 basis points per
  session on correction.
  **Amended (session 15, 2026-08-19): the segment hold lines are
  relabelled and charged.** A benchmark line carrying zero turnover for a
  position requiring a daily round trip is mislabelled in the
  deliverable, so both lines now carry `line_kind` of **attribution** for
  the uncharged figure and **benchmark_tradeable** for the charged one.
  Charged under the session 14 cost model, being class tiers, commission
  Arm S, and the 10 basis point anchor, with one round trip per session
  carrying the class tier figure once because that figure is already a
  round-turn cost, and the 4.4a opening-auction premium applied to the
  leg executing at the open: the **overnight line falls from +8.49
  percent annualised at a Lo-corrected Sharpe of 1.597 uncharged to
  −28.69 percent at −4.999 charged**, and the **intraday line from −6.48
  percent at −2.026 to −38.54 percent at −12.264**. Neither segment is
  tradeable at the cost model the strategy is charged, which is why the
  4.1c verdict rests on the share comparison rather than on the segment
  lines. Figures: outputs/session-15/segment-lines-charged.csv.
- **4.4a opening-auction premium — recorded (session 13.9, 2026-08-18;
  post-hoc under 9.10).** A multiplier on the tiered slippage applied
  to the OPEN-TO-OPEN arm only: **central 2.0x, swept 1.0–4.0x,
  uniform across tiers.** Derived, not chosen: opening auctions carry
  the largest price impact and closing the smallest, with continuous ≈
  2x closing at large-cap sizes (Goyal-Jegadeesh-Wu, JFQA 2026,
  snippet-verified figures), so opening/closing ≥ 2 anchors the
  central; the 1.0 sweep floor carries Bacidore-Lipson (2001), where
  1990s NYSE opening trades were ~20% CHEAPER; 4.0 covers the
  unmeasured upside. Uniform because no retrieved source measures the
  open-vs-rest ratio by liquidity tier. Supporting: McInish-Wood
  reverse-J; the 744-ETF 2017 intraday study (spreads highest in the
  first hour); Challet-Gourianov auction-volume asymmetry; NYSE 2023
  closing TCA. Full sourcing:
  outputs/session-13.9/auction-premium.csv. Also recorded: closing ≈
  0.5x continuous implies the un-premiumed tier levels OVERCHARGE the
  close-to-close arm — a conservative direction, unchanged.
  **Amended (session 14, 2026-08-18): the Bacidore and Lipson
  measurement of roughly 0.8x sits below the sweep floor of 1.0 and is
  EXCLUDED rather than silently truncated.** Reason: their sample is
  1997 to 1998 NYSE specialist openings, which precedes decimalization
  in 2001 and precedes the electronic opening auctions introduced with
  the Nasdaq and NYSE Arca crosses in 2004, so the roughly 0.8 multiple
  describes an opening mechanism that no longer exists over a sample
  beginning in 2007. The direction is disclosed: were the 1990s
  relationship to hold, the premium would be a discount and the
  open-to-open cell would read higher than every figure reported. The
  sweep was measured at every registered point rather than inferred
  from linearity, and the open-to-open cell exceeds the close-to-close
  comparison cell on both annualised return and Lo-corrected Sharpe at
  the 4.0x ceiling (41.90 percent and 1.196 against 29.71 percent and
  0.929).
- **2.13a expense finding status — recorded (session 13.7a,
  2026-08-18).** Session 13.7 step 4 reported UVXY/SVXY charging
  1.32–1.90 percent all-in against the 0.95 constant; an independent
  source gives the ProShares Trust II statutory management fee at 0.95
  percent across 2011–2021. Sessions 13.7a steps 1–4 resolved it:
  **definitional artifact.** The 1.32–1.90 figures are Trust II's
  unqualified "Expense ratio" line, which is brokerage-commission-
  inclusive; the same tables print "Expense ratio, excluding brokerage
  commissions" at 0.95 in every sampled year, while the ProShares Trust
  (TQQQ/SQQQ) tables carry no brokerage-inclusive variant at all — the
  comparison crossed line families. The decisive tracking test: with the
  0.95 constant, synthetic UVXY drifts −0.67 percent per year BELOW
  issuer NAV (inside the TQQQ/SQQQ baseline band of −0.73/−1.25), the
  opposite direction of an understated expense, with the detector
  validated on a deliberately mis-specified 1.90-percent control
  (measured shift −0.949 pp against −0.95 expected). The construction is
  validated against realized NAV, which embeds brokerage; applying the
  brokerage-inclusive ratio would double-count. **D14's expense
  component is closed; session 13.7's direction confirmation does not
  survive; the financing component of D14 stays open under D16.**
  Residuals recorded: SVXY drifts +1.60 percent per year above NAV
  excluding the 2.12b day — larger than its filing gap and inside the
  recorded SVXY residual class, not cleanly attributable to expenses;
  the Direxion sampled cells (0.95–1.06 net-with-interest against
  FY2025 constants 0.71–0.87) and TQQQ (actual 0.95 against build 0.86 —
  session 13.7's table misstated the build constant as 0.95, corrected
  in outputs/session-13.7a/expense-provenance.csv) are real
  fiscal-year-level differences of order 0.1–0.24 pp/yr per fund,
  inside the measured baseline noise, recorded and not applied.
  **Amended (session 13.8, 2026-08-18): the residual constants are now
  APPLIED as an authorized correction — TQQQ 0.95, SH 0.89, and the
  Direxion seven at 0.95, all from the like-for-like measured line
  (ProShares "Expenses net of waivers"; Direxion "Net Expenses"
  excluding interest/extraordinary, financing being modeled separately
  under 2.14 — the incl-interest line would double-count). UVXY/SVXY
  confirmed 0.95, unchanged. D14's expense component is closed for
  every measured fund. scripts/s10_build.py ER_PCT updated; the engine
  bridges the on-disk panel with an exact additive layer. Measured
  cells and accessions: outputs/session-13.8/expense-constants.csv.**
- **4.2 — closed with a stated limitation.** Both available vendors
  redistribute the consolidated tape; the official closing auction print
  cannot be distinguished from the consolidated last sale without licensed
  exchange data (session 07: 18/18 cent-exact cross-vendor agreement).
  [A — assumption about the feed, recorded as such]
- **4.3 — closed, REVERSED TWICE (history).** (i) v2/session 05: per-
  liquidity-tier slippage schedule, tiers estimated from spread
  estimators. (ii) Session 05's composite tiering produced a sub-unity
  thinnest-tier multiplier; session 06's DV-only tiering did too (both
  treatments), because the Corwin-Schultz bias is leverage-correlated
  while leverage sorts by tier — and an auction fill does not cross the
  spread, so the apparatus proxied the wrong cost. (iii) **Session 09:
  uniform swept cost.** No tiers, no multipliers; base sweep
  (0, 5, 10, 20, 35, 50 bp round-turn, Zarattini anchor 10) applied
  uniformly; spread estimates move to data characterisation.
- **4.5 — ported and amended (session 13.7, 2026-08-18; v2 decision,
  resolving D2).** Commission is reported as a RANGE bounded by IBKR
  Fixed above and zero below rather than as a single figure. Four arms,
  constants in src/config.py: **F** Fixed throughout (0.005/share, 1.00
  minimum, 1% cap — retained for comparability with sessions 13–13.6);
  **T** Tiered throughout (0.0035/share, 0.35 minimum, 1% cap, plus
  pass-throughs held at current published values, disclosed); **S**
  spliced — Fixed through 2019-09-30, zero from **2019-10-01**, the
  month US retail commissions went to zero industry-wide (Schwab
  announced 2019-10-01; peers followed within the month; IBKR Lite
  launched October 2019); **Z** zero throughout. **Corrected
  reasoning**: the original closure chose Fixed on continuity; applying
  a schedule that ceased to be available in 2019 across the post-2019
  window models a counterfactual account rather than a conservative
  one, and the 2019 discontinuity is a property of the retail brokerage
  market, not an artifact of the model. Arm S's explicit zero is not a
  total execution cost of zero — zero commission accompanies wholesaler
  routing and payment for order flow, and slippage carries that cost.
  **Amended (session 13.8, 2026-08-18): Arm S is CANONICAL — the
  spliced schedule is the measured history of what a retail account
  paid. Arm F is reported alongside as the conservative bound and for
  comparability with sessions 13–13.7. Arm T is a disclosed sensitivity
  with its pass-through anachronism stated (current published
  pass-through rates held constant across the sample). Post-2019 zero
  commission is a FEE of zero, not a COST of zero — wholesaler routing
  moves the cost into the spread, which the slippage axis carries.**
- **4.4 — closed.** The base sweep above; cost is a headline axis (105
  signal transitions/yr, median holding one session — session 07).
  **Amended (session 13.7, 2026-08-18): the uniform sweep remains the
  registered sensitivity surface. A measured per-instrument slippage
  profile was attempted as a post-hoc parallel cost model under 9.10 on
  accuracy grounds; the construction HALTED per its own pre-condition —
  the Corwin-Schultz levels reproduce failure mode (ii) in level form
  (leverage-correlated volatility-as-spread bias: QQQ reads 5.6–38
  bp/yr against a ~1 bp true spread; 2020 levels sort by leverage on
  one underlying; negative-estimate fractions 40–50%; the Abdi-Ranaldo
  cross-check disagrees rather than confirms). No parallel cost model
  was added; the measurements are retained as evidence in
  outputs/session-13.7/slippage-profile.csv.**
  **Range retained at 0–50 bp (conversation, recorded session 12.6).**
  Session 05's stress-window spread estimates (SOXS at 401 bp and SOXL
  at 288 bp in COVID) were not used to extend the range, because the
  Corwin-Schultz variance-scaling assumption is violated on daily-reset
  funds, so those figures substantially read volatility as spread.
  Recorded as a limitation: the cost model proxies auction cost with a
  continuous-market spread estimator and does not cover crisis
  conditions.
  **Amended (session 13.8, 2026-08-18): a TIERED slippage arm is added
  at the 10 bp anchor — multipliers 0.2x / 0.5x / 1.5x, tier boundaries
  from measured median dollar volume terciles across the sample (NOT
  from leverage; the assignment against both criteria is reported in
  outputs/session-13.8/headline-canonical.csv, and volume drove it —
  e.g. 2x UVXY sits in tier one on volume while 3x SOXL sits in tier
  three). Three caveats, all running in the strategy's favor:
  calibration on modern spread levels applied to a sample beginning in
  2007; no stress widening; a fixed multiplier. Stored-volume artifact
  flags (session 05: SOXS/TECS/UVXY/BTAL) carry into the tier
  boundaries and are disclosed.**
  **Amended again (session 13.9, 2026-08-18, post-hoc under 9.10): the
  volume-based tier map is SUPERSEDED by assignment BY INSTRUMENT CLASS
  AND UNDERLYING LIQUIDITY. Volume is a rejected proxy — published ETF
  liquidity guidance identifies underlying-security liquidity as the
  spread determinant, and the volume map demonstrated the failure
  directly (UVXY in tier one at 2 bp against its measured ~15 bp median
  spread on 18.5 percent of dollar exposure; BIL in tier three on an
  instrument quoting a penny). Class anchors: unlevered broad
  equity/short-duration bonds 1–2 bp; large levered index funds 5–10 bp
  (DiLellio & Stanley's 8 and 10 bp for SSO and SH on 2013 volumes);
  levered sector funds 10–20 bp; volatility products ~15 bp (UVXY's
  measured median); BTAL tiered with them on both spread and capacity
  grounds. Tiers, fixed before the arm ran: tier one 0.2x — every
  unlevered instrument; tier two 0.5x — TQQQ, SQQQ, QLD, QID, SSO,
  SDS, PSQ, SH; tier three 1.5x — SOXL, SOXS, TECL, TECS, SPXL, FAS,
  LABU, UVXY, SVXY, BTAL. Assignment against volume, leverage, and
  anchor: outputs/session-13.9/tier-reassignment.csv.**
  **Stacking rule recorded (session 15, 2026-08-19, pre-registered before
  the step-4 run): the uniform round-turn sweep REPLACES the tiered
  slippage and the opening-auction premium rather than stacking on top of
  them.** The uniform arm exists to bound sensitivity to an assumed cost
  level, so adding it to a calibrated model would double-charge.
  Commission Arm S and the participation cap are unchanged across the
  sweep. Applied consistently in
  outputs/session-15/cost-sweep-designated.csv, which reports the sweep on
  the designated open-to-open cell, where session 14's step 5 had run it
  on the close-to-close cell only.
- **4.6c NAV sweep — measured (session 15, 2026-08-19; register decision
  on axis membership left OPEN).** The canonical NAV is unchanged at
  1,000,000 and every other level is a sensitivity arm. Designated cell
  by NAV: 53.16 percent and 1.3804 at 100,000; 53.27 and 1.3849 at
  250,000; **52.26 and 1.3846 at the canonical 1,000,000**; 37.80 and
  1.2392 at 5,000,000; 22.60 and 0.9643 at 25,000,000. The relationship
  is not log-linear, being flat from 100,000 to 1,000,000 and steep
  above it, so the summary elasticity of −0.127 annualised return and
  −0.174 Lo-corrected Sharpe per decade of NAV understates the upper
  range and overstates the lower. The three channels separate cleanly.
  Integer truncation falls from 0.027 percent of target dollars at
  100,000 to 0.0004 percent at 25,000,000 and is immaterial throughout.
  The Arm S commission minimum binds on 31.1 percent of orders at
  100,000 and 7.9 percent at 25,000,000. **The participation cap is the
  channel that carries the effect**, routing 1.15 percent of target
  dollars to cash at 100,000 and 36.2 percent at 25,000,000, with the
  count of cap-binding instruments rising from 2 to 14. Whether NAV joins
  the specification-curve axes and whether the grid must span it is the
  open decision this measurement informs.
- **9.11 decision audit — recorded (session 13.9, 2026-08-18).** 121
  register/corrections/defect items classified: 55 pre-result choices,
  22 post-result choices, 17 post-result repairs, 16 measurements
  (outputs/session-13.9/decision-audit.csv). Eleven post-result
  choice-closures lack an explicit 9.10 flag (defect D17). **The
  deflated Sharpe under 8.7 covers the parameter search only — N stays
  at grid size (218,700), not inflated by the register**: repairs were
  not trials, most decisions were made with no result visible, and the
  post-result choices largely declined to select (equal weighting
  removed a hierarchy rather than promoting the higher-reading panel).
  Specification uncertainty is addressed by a reported SPECIFICATION
  CURVE spanning the choice axes: panel, convention, window, commission
  arm, slippage model (uniform level / class tiers / auction premium),
  financing spread, SMH accrual, sizing mode, and the unavailable-fill
  completion rule. No judgement is made about whether the count is
  acceptable.
  **Reconciled (session 14, 2026-08-18).** The 13.9 summary's four
  figures sum to 110 against a stated 121; the **eleven unreported items
  are the pre-result repairs**, being corrections-list entries 1 through
  11, which the summary omitted by listing three of the six occupied
  cells plus a measurement total. The full three-axis cross-tabulation
  is outputs/session-14/decision-audit-reconciled.csv and sums to 121.
  The alternative explanation, that the eleven were D17's unflagged
  items, is **ruled out by zero item overlap**: D17's items are
  post-result choices and pre-result choices closed post-result, while
  the missing eleven are pre-result repairs, which carry no 9.10
  requirement because no result existed when they were made. The
  coincident count is arithmetic accident. **Axis coverage: seven of the
  22 post-result choices do not lie on any of the nine recorded
  specification-curve axes.** The seven, read from
  outputs/session-14/decision-audit-reconciled.csv, are the 4.6 NAV
  close, the 5.7 per-year covariance, the Sharpe numerator registration,
  and the D5, D6, D7, and D10 dispositions; six are reporting or
  diagnostic conventions that do not enter the return series. (Corrected
  session 15, 2026-08-19: the original text named the 2.7a validation
  scoping, which the CSV does not carry as off-axis, and omitted the
  4.6, D6, and D7 items.) **Starting NAV under 4.6
  is the consequential one**, since it enters the return series through
  integer truncation, the commission minimum, and now the session 14
  participation cap, whose bite scales with NAV, and the nine axes do
  not span it. Reported without recommendation.
- **D17 — CLOSED (session 14, 2026-08-18).** The eleven items are
  retro-tagged with explicit 9.10 disclosures naming when each decision
  was made and what it governs
  (outputs/session-14/decision-audit-reconciled.csv). Composition
  correction: the eleven are **eight post-result choices plus three
  pre-result choices whose closure came after results existed**, not
  eleven post-result choice-closures as 13.9 recorded. **Ordering,
  stated rather than claimed**: the tags were written before any ladder
  line comparison was read, but not before the session-14 run began, so
  the ladder, the segment decomposition, and the premium sweep had
  executed and their strategy-side figures were visible. The ordering
  the session-14 prompt specified was therefore partially achieved and
  the shortfall is recorded. The tags carry no judgement a benchmark
  result could influence.
- **4.6 — closed (session 13.7, 2026-08-18): starting NAV 1,000,000.**
  The liquidity check runs against the realized NAV path rather than the
  starting figure: maximum position dollars per instrument over the
  compounded path against the instrument's median daily dollar volume
  across its in-window listed sessions. **Binding instrument: BTAL, at
  4.9x its median daily dollar volume** (maximum position ~$895k against
  a ~$183k median; the stored-volume record for BTAL is artifact-flagged
  per session 05, so the ratio's level is indicative, its ordering
  decisive — every other instrument is at or below 0.18x). Computed from
  session 13's daily series (position dollars are weight x NAV and hence
  independent of the raw-price convention); the 13.6/13.7 corrections do
  not alter it materially. The truncation size-dependence is dissolved by
  measurement: residual drag 0.15 bp/yr at this NAV (sessions 13.5/13.6).
  **Amended (session 13.9, 2026-08-18): BTAL's capacity verified against
  an independent source (FactSet-sourced archived snapshots: median
  daily dollar volume $11.7K as of 2018-07, average $74.6K; $1.26M
  average by mid-2019 — the stored record is consistent with, and in
  2018 generous to, the independent one, so the artifact flag is
  resolved in the HARSHER direction). Capacity limit, reported not
  applied: the NAV at which every instrument's maximum position stays
  inside 5 percent of contemporaneous average daily volume is bounded
  by **BTAL at approximately $45,000** (TECL $84K in 2008; every other
  instrument ≥ $800K; full table
  outputs/session-13.9/capacity-limit.csv). The 1,000,000 result
  stands with this capacity note attached; no position is capped and no
  impact charge is added.**
  **Amended (session 14, 2026-08-18): the capacity note becomes an
  IMPLEMENTED PARTICIPATION CAP, classified as a correctness repair
  under the 7.14 precedent rather than as a specification choice.** 7.14
  set the primary-window boundary at the last unavailable realized fill
  on the standard that a position which cannot be filled is not a
  result; a position requiring 6.08 times median daily dollar volume
  fails the same standard. Denominator: trailing median daily dollar
  volume over a 21-session lookback, lagged one session, computed
  point-in-time, expanding over available history where fewer than 21
  sessions exist, and excluding zero-volume sessions, which session 05
  established are a stored-record truncation artifact on the extreme
  reverse-splitters rather than a measurement of liquidity. Session
  13.8's same-year median is not admissible for a cap that enters
  position sizing, since it reads up to a year of future data. Cap: the
  target dollar position is capped at 5 percent of the trailing
  denominator, canonical; the capped remainder routes to sleeve cash
  accruing DTB3 through the existing unfilled-slice path under 1.9 and
  2.11, so no new accounting path is created. Application is universal,
  on identical terms for every instrument, so BTAL's position as the
  binding constraint is shown rather than asserted: BTAL is capped on
  189 transitions with a mean 89.8 percent of its target routed to
  cash, and seven other instruments are capped on 91 transitions
  between them in thin early years. Arms: uncapped runs alongside for
  continuity with sessions 13 through 13.9; 10 and 20 percent levels
  run on the canonical specification only and do not carry through the
  ladder or the nulls. **Instrument substitution was considered and
  rejected**: selecting a BTAL replacement in 2026 with the 2011 to
  2021 outcome visible is a look-ahead that no disclosure repairs.
- **D18 defect class swept — recorded (session 15, 2026-08-19).** The
  object-dtype boolean negation defect, where Python's integer bitwise
  negation applied to an object-dtype series makes every element truthy,
  was swept across the repository against a detector validated on both an
  object-dtype and a bool-dtype control before any repository finding was
  reported. **78 negation sites were scanned and ZERO lie in the
  return-generating path**, which contains no negation of any kind:
  src/config.py, src/data.py, src/indicators.py, src/sleeves.py,
  src/portfolio.py, src/schedule.py, src/execution.py,
  scripts/s13_backtest.py, and scripts/s14_common.py carry none. The halt
  condition was therefore not met and no canonical figure is affected.
  Two defective sites exist, both in diagnostic scripts and both confirmed
  object-dtype at runtime: scripts/s13_7_mechanism.py line 114, which
  produced session 13.8's entry-split rows, and scripts/s13_9_controls.py
  line 137, which produced session 13.9's entry reconciliation. **Session
  13.8's ablation-mechanism conclusions survive**: the overlay
  decomposition is built from a comparison-derived bool mask rather than
  the defective entry mask, and recomputation returns +5.5830 directional
  against a published +5.5838, −4.8240 roll against −4.8242, and −0.0086
  reset against −0.0086, the residual differences arising from the
  session 14 participation cap rather than from the mask. Only the
  entry-split rows are wrong, at a published +0.00234 on 469 observations
  against a corrected −0.00869 on 167. Evidence:
  outputs/session-15/d18-sweep.csv.
- **D19 silent fill failures swept — recorded (session 15, 2026-08-19).**
  A detector was validated by injecting an unfillable target into the
  primary window, being LABU in 2013 against a 2015-05-28 listing, and
  confirming both detection and the absence of a false positive on the
  unmodified series. **Zero silent fill failures were found on any window
  or convention.** At fill sessions the target dollars minus deployed
  position value minus recorded cap remainder minus recorded
  unavailable-fill weight leaves a residual whose maximum is 0.3 percent
  of NAV and whose content is integer truncation. The cap path and the
  unavailable-fill path do not double-count, with zero events routing
  more to cash than the target carried across 362 close-to-close and 574
  open-to-open cap events. Recorded alongside as a detector-design note:
  the first implementation compared carried-forward target gross against
  realized gross on every session and flagged 16.5 percent of the primary
  window, which is drift that 5.2 permits with no calendar reset rather
  than a fill failure, so the detector runs at fill sessions only.
- **7.14 boundary, off by one session — recorded (session 15,
  2026-08-19).** 7.14 sets the primary window at the last unavailable
  realized fill and the boundary was taken INCLUSIVE of that session, so
  the window's defining property that it contains no unavailable fills is
  false by one event: SVXY's first priced session on the frozen panel is
  2011-10-04, and a 2011-10-03 target on it at a weight of 0.0833 cannot
  fill. Starting the window at 2011-10-04 removes the event and moves the
  designated cell from 52.26 percent and 1.3846 to 52.18 percent and
  1.3817, and the close-to-close cell from 29.71 percent and 0.9286 to
  29.62 percent and 0.9251. The boundary is NOT changed here; the
  correction is a register decision left open.
- **4.4b cost-model binding verification — recorded (session 14,
  2026-08-18).** Session 13.9's re-tiered close-to-close cells and
  session 13.8's uniform Arm F cells matched at the precision the 13.9
  report printed, which is the signature of a setting that failed to
  bind. Verified: **the class tier map and commission Arm S both bound
  correctly.** No column is byte-identical between the two runs
  (differences of 0.035 and 0.042 percentage points on annualised return
  and 0.0049 and 0.0057 on Lo-corrected Sharpe, both pairs rounding to
  the same displayed figure); the commission arm varies inside session
  13.9's own rows by 1.99 and 1.95 percentage points between Arms F and
  Z; and the class tier map moves the level 2.03 percentage points
  against session 13.8's volume map on both panels. What was wrong is
  session 13.9's DELTA rows, which selected the full window for
  close-to-close while the levels quoted beside them were primary-window,
  so full-window deltas of 1.63 and 1.31 percentage points were printed
  against primary-window levels whose true delta is 2.03. Corrected
  primary-window close-to-close Arm S levels: synthetic 31.66 percent
  and 0.9774, realized 29.98 percent and 0.9361. Evidence:
  outputs/session-14/cost-model-verification.csv.
- **4.7 — closed, REVERSED ONCE (history).** (i) Session 01: fractional
  primary. (ii) Session 07: IBKR executes fractional components as
  principal — never routed to the closing auction — so the fractional
  portion cannot receive the official closing print by construction.
  **Session 09: truncation primary, fractional the arm.** Consequence:
  4.6 reopened.

## 5. Portfolio

- **5.1 — closed.** All four sleeves execute every date; label at whole
  percent of sleeve budget; equality on the joint string; short circuit
  after the calls, before summation. Implied no-trade band ±0.125% of NAV
  per component — inert given discrete sleeve terminals.
- **5.2 — closed.** Drift permitted; reset on label transition only.
- **5.3 — closed.** Gross cap 100%, proportional truncation.
- **5.4 — closed.** Four sleeves, 25% each.
- **5.5 / 5.5a — closed.** Idle sleeve cash and truncation residual accrue
  DTB3 at rate/360 per CALENDAR day (weekends and holidays accrue);
  implemented in `src/data.py` factors + `src/execution.py` accrual.
  Null rate days carry the last published rate for accrual only (stated
  departure from 1.9, rates are not prices).
- **5.6 / 5.7 — closed (5.7 estimation registered session 13.8,
  2026-08-18, post-hoc under 9.10).** Breadth and concentration
  diagnostics computed from session 13 onward. **5.7's minimum-torsion
  ENB covariance is estimated PER CALENDAR YEAR (canonical)** — the
  metric asks how many independent risk sources the portfolio holds at a
  point in time and correlations moved substantially across the sample;
  the fixed-window figures (2011-09-14..2021-07-30) are retained as
  comparison. Canonical mean ENB 9.06 against 8.17 fixed
  (outputs/session-13.8/concentration.csv).

## 6. Signals

- **6.1 — closed.** Three function-tied RSI periods (exhaustion, dip,
  relative strength), all 14 canonical; the call-site mapping with all
  ambiguities resolved is `outputs/session-01/rsi-function-mapping.md`
  (A1 → dip by structure; A2/A3 → RS both sides by 6.19).
- **6.2 / 6.3 / 6.4 — closed.** Overbought tier one 70, tier two 80,
  oversold 30. Every source per-name exception collapsed.
- **6.5 / 6.6 — closed.** SMA long 200, short 20.
- **6.8 — closed.** S3 vote membership SPY, QQQ, SMH, SOXL as supplied.
- **6.9 — closed.** Both overbought panels as supplied.
- **6.10 — closed, REVERSED TWICE (history).** (i) Source: qqq_60d < −12
  hardcoded. (ii) Pre-session-01: rolling 5th percentile of trailing
  60-session QQQ returns (quantile form). (iii) Session 03 measured all
  three estimator forms failing (expanding missed COVID entirely at −19.4
  vs −20.7; rolling-2520 absent across 2008; rolling-1260 fired on Aug
  2015 at −5.4) and −12 sitting at the 9.1st percentile → **session 04:
  absolute threshold, −10.** (iv) **Session 09: re-closed at −15**, a
  stipulation interpolating the correction convention (10) and the
  bear-market convention (20), with the disclosure that both describe
  peak drawdowns while this estimator is point-to-point; session 06
  measured −12 firing on 37.9% of bear-reached sessions (4× its
  unconditional rate), so a deeper level shifts the branch toward an
  override. [A — stipulation, disclosed as such]
  **6.11 / 6.12 — closed as not applicable** (no estimator, nothing fills).
- **6.13 / 6.14 — measured, open as ordering decisions.** T10 cascade
  co-occurrence 1.05% of not-overbought sessions at canonical; identically
  zero at (28,20); 17.15% at (7,40). S3's "pair" is order-inert by
  construction (both route to SOXL).
- **6.17 — closed.** T11 panel overbought read as the maximum RSI across
  the five names (TQQQ usually supplies it).
- **6.18 — measured.** The two bear sub-models differ more than the
  register assumed: bond_baller carries a TLT>PSQ head feaver lacks;
  agreement only 25.1% of determinate-bear sessions; crash fires on 37.9%
  of bear sessions.
- **6.19 — closed.** Mixed-period pairwise sites resolve to the RS period
  on both sides.
- **6.22 — closed.** T11 is the only sleeve with a graded overbought
  response.

## 7. Grid

- **7.4 — informed.** Tier-two offset sweep (+5/+10/+15): live at
  canonical and period 7; at period 28 the +15 point NEVER fires and +10
  fires 6 episodes in 27 years (session 06).
- **7.6 — closed.** Long SMA grid (50, 100, 150, 200); 250 dropped; 200 is
  a boundary point so long-end sensitivity is one-sided.
- **7.7 — closed.** Crash axis sweeps levels (−5, −10, −15, −20, −25).
- **7.10 — REPAIRED (session 16b, 2026-08-19).** validate() now computes the
  product from the ENUMERATED axis tuples and compares it against
  `GRID_TOTAL_SPECIFICATIONS`, so a grid that cannot be constructed fails.
  The placeholder `GRID_UNREPRESENTED_AXES_CARDINALITY` is REMOVED. Confirmed
  by control: the repaired guard rejects the pre-repair total of 218,700 and
  accepts 131,220, and no constant outside the grid definition changed.
  **The product test failed and 218,700 is superseded.** The v1/v2 ranges at
  docs/HANDOFF.md line 122 multiply to 273,375 exactly, matching what that
  document records, so the axes were a real product once. 7.6 dropping
  long-SMA 250 carried it to 218,700 correctly. **7.7 then swapped a
  three-point crash-quantile axis for a five-point crash-level axis while
  asserting the total was unchanged, which multiplies the product by 5/3 and
  cannot leave it fixed.** The placeholder 10,935 equals 218,700 divided by
  20 exactly, a residual obtained by division rather than a product of
  inputs, and its factorisation 3^7 x 5 does not match the axes' 3^6 x 5^2
  under any assignment. Evidence: outputs/session-16b/product-test.csv.
- **7.14 — closed (session 13.7, 2026-08-18; boundary CORRECTED session
  16, 2026-08-19).** Sub-period definitions:
  **primary evaluation window 2011-10-04 to 2021-07-30**, boundary set by
  the last unavailable fill in the realized arm — the specification is
  not implementable as written before that date. **Secondary window
  2007-01-03 to 2011-10-02, labeled the synthetic-only extension**,
  reported separately and never merged into headline figures. **Full
  sample 2007-01-03 to 2021-07-30 retained and reported.** Every
  benchmark and null runs on all three. Justification is
  implementability rather than performance, and the boundary was set
  before any benchmark ladder existed.

- **7.14a boundary correction — recorded (session 16, 2026-08-19;
  correctness repair under the 7.14 precedent, resolving D21).** 7.14
  defines the primary window by containing no unavailable realized fills,
  and taking the boundary inclusive of the last such fill made the
  definition false by one event, being SVXY at weight 0.0833 on
  2011-10-03, since SVXY's first priced session on the frozen panel is
  2011-10-04. The window start moves to **2011-10-04**. Classified as a
  correctness repair rather than a specification choice, since the
  window's defining property was false as written. Verified: **zero
  unavailable fills remain on either panel or convention from
  2011-10-04**. Effect on the canonical, reproducing session 15's
  prediction to four decimals: the designated cell moves from 52.26
  percent and 1.3846 to **52.18 percent and 1.3817**, and the realized
  close-to-close primary cell from 29.71 percent and 0.9286 to **29.62
  percent and 0.9251**. Pre-correction figures carry forward for
  continuity and never as the anchor. Evidence:
  outputs/session-16/boundary-correction.csv.
- **D20 NAV — closed (session 16, 2026-08-19).** Starting NAV under 4.6
  **joins the specification curve and does not join the grid axes.** The
  specification curve is a reported sensitivity surface and session 15's
  step 6 already measured the five levels, so the addition costs nothing
  further. The grid is a search over strategy specifications and NAV is
  an account property, so adding it would multiply the grid fivefold and
  inflate 8.7's N with an axis nobody selected on. The measured shape
  supports the split, with the designated cell flat from 100,000 through
  1,000,000 at a Lo-corrected Sharpe of 1.3804 to 1.3849 while cap
  intervention quadruples from 1.15 to 5.23 percent of target dollars.
  **The capacity curve above 1,000,000 is a separate paper deliverable**,
  with volatility falling from 48.8 to 34.0 percent, maximum drawdown
  improving from −53.1 to −46.3 percent, and turnover falling from 37.9
  to 22.8 by 25,000,000. The canonical cap-binding table for the headline
  convention is reported alongside it, being ten instruments across 574
  events routing 5.2285 percent of target dollars to sleeve cash at the
  canonical NAV.
- **7.14b early-window reporting form — closed (session 16,
  2026-08-19).** The 2007-01-03 to 2011-10-03 extension reports
  **coverage tables and the per-instrument availability timeline only,
  with no return figure at any prominence**, on the grounds session 13.9
  established that 106 non-contiguous fully fillable sessions across 16
  discontinuities carry no return interpretation. Synthetic-panel figures
  for that window keep their separate label under 7.14 and sit in the
  appendix.
- **3.13 SH — recorded (session 16, 2026-08-19).** Session 15.5
  established that SH appears in **no weight dictionary anywhere in the
  return-generating path** and enters only as the right side of the AGG
  against SH pairwise comparison. SH is recorded as a **signal input
  rather than a tradeable universe member**, so the stated universe
  matches the holdings. No behaviour changes.
- **D24 the grid axes are not enumerated — OPEN (session 16,
  2026-08-19).** The grid could not run. 7.10 pins the product at 218,700
  as len(SMA_LONG_GRID) x len(CRASH_THRESHOLD_GRID) x
  GRID_UNREPRESENTED_AXES_CARDINALITY, and only the first two are
  enumerated in src/config.py, giving **20 of 218,700 specifications, or
  0.0091 percent**. The remaining factor of 10,935 is a placeholder whose
  own comment states that no decision in hand enumerates those axes'
  values. The unenumerated axes are the three function-tied RSI periods
  under 6.1 and 7.2, overbought tier one under 6.2 and 7.3, the tier-two
  offset under 7.4 which the register records as informed rather than
  closed, oversold under 6.4 and 7.5, short SMA under 6.6 and 7.8, and
  the S3 vote threshold under 6.7 and 7.9. validate() passes because it
  pins the product against the placeholder rather than against the axes.
  **Enumerating them inside a measurement session would be a
  specification act**, since what a study searches over determines N in
  8.7 and the shape of the specification curve under 9.11, so the closure
  belongs in the register. PBO, the deflated Sharpe, and the
  specification curve all depend on the grid and are unrun. Evidence:
  outputs/session-16/grid-blocker.csv.

- **7.2 through 7.9 — ENUMERATED (session 16b, 2026-08-19, closing D24).**
  The grid axes, their values, and the source of each. Seven axes carry
  values recorded in the register or in config, which the register's preamble
  designates authoritative for values; **three carry neither values nor a
  cardinality anywhere and are resolved by the pre-registered construction
  alone, which is a post-result specification choice disclosed under 9.10**
  and marked DISCRETIONARY. The fallback rule was written and hashed to
  SHA-256 702a6026972251ea83defa30817b97a49931c45450fbd14af34f1c1900d74f24
  before any part of the register was read on the axes, which is the evidence
  the rule preceded the reading.

  | axis | values | n | source |
  |---|---|---|---|
  | RSI period, exhaustion (6.1) | 7, 14, 28 | 3 | recorded, config 6.1 comment |
  | RSI period, dip (6.1) | 7, 14, 28 | 3 | recorded, config 6.1 comment |
  | RSI period, relative strength (6.1) | 7, 14, 28 | 3 | recorded, config 6.1 comment |
  | Overbought tier one (6.2) | 65, 70, 75 | 3 | **DISCRETIONARY**, construction |
  | Tier-two offset (7.4) | 5, 10, 15 | 3 | recorded, register 7.4 (status informed) |
  | Oversold (6.4) | 25, 30, 35 | 3 | **DISCRETIONARY**, construction |
  | Short SMA (6.6) | 19, 20, 21 | 3 | **DISCRETIONARY**, construction |
  | S3 vote threshold (6.7) | 2, 3, 4 | 3 | recorded, config 6.7 comment |
  | Long SMA (7.6) | 50, 100, 150, 200 | 4 | recorded, config tuple |
  | Crash threshold (7.7) | −5, −10, −15, −20, −25 | 5 | recorded, config tuple |

  **Enumerated total 131,220.** Every axis carries its canonical value and the
  canonical point is unchanged. Three items are recorded rather than resolved.
  First, the rule specifies how to build values given a cardinality of 3 or 5
  but does not say which applies when neither is recorded, and 3 was taken as
  the smaller of the two it names; at 5 for all three discretionary axes the
  total would be 607,500. Second, the rule's one-session granularity gives a
  short-SMA sweep of 19, 20, 21, which is degenerate beside the recorded
  long-SMA sweep at 50-session steps, and it is reported rather than silently
  widened. Third, docs/HANDOFF.md line 122 records candidate values for all
  three discretionary axes, being tier one at 60/65/70/75/80, oversold at
  20/25/30/35/40, and short SMA at 10/20/50, which would give **364,500**, the
  same total the v3 amendments produce arithmetically; **HANDOFF.md is
  superseded and is not the register, so adopting those values is a register
  decision and is not taken here.**

  **Branch reachability changes along the oversold axis.** Session 13.5
  measured the two T11 PSQ-dip terminals firing zero times at oversold 20, 25
  and 30, then 1 and 23 times at 35 and 10 and 113 at 40. Two of the three
  enumerated oversold points leave both terminals dead and the third brings
  them alive, so a third of that axis runs a structurally different strategy.
- **8.7 — amended (session 16b, 2026-08-19).** **N is the enumerated total,
  131,220, not 218,700.** 218,700 is superseded, having never been derivable
  from the register as written once 7.7 changed the crash axis from three
  points to five. N remains uninflated for register decisions, per the session
  14 audit establishing that repairs were not trials and that the post-result
  choices largely declined to select. If the three discretionary axes are
  later resolved from docs/HANDOFF.md or by a register decision, N moves with
  them and the deflated Sharpe must be recomputed.

  **Amended again (session 19, 2026-08-19), superseding the 131,220 above.**
  Session 17 adopted the docs/HANDOFF.md ranges for the three discretionary
  axes, which is the register decision the 16b amendment named as the trigger
  for N to move, so **N is 364,500**, the enumerated total across the ten axes.
  The grid **evaluated 121,500** of them, with 7.4's tier-two offset held at
  its canonical value of 10 on every specification rather than sampled, on the
  grounds that the register marks 7.4 informed rather than closed. Both figures
  are recorded and N is the enumerated total rather than the evaluated count,
  since N is the size of the search space the study enumerated and a grid
  running on a disclosed subset does not shrink it.

  **Deflated Sharpe, computed session 19.** On the naive Sharpe, which is what
  the Bailey and Lopez de Prado formula is defined on since it carries its own
  skewness and excess kurtosis adjustment while the Lo correction addresses
  autocorrelation instead, the deflated Sharpe at N equal to 364,500 is
  **0.000660 for the canonical** and **0.023736 for the grid's
  in-sample-best** specification. At N equal to 121,500 as the sensitivity the
  two read 0.001979 and 0.048847. The expected maximum Sharpe
  under the no-skill null is 2.1082 annualised, which exceeds both the
  canonical's 1.0911 and the in-sample-best's 1.4723, and that
  is what produces deflated figures below one half. The same quantities
  computed on the Lo-corrected Sharpe are carried as a disclosed sensitivity at
  0.010884 and 0.085737. Reported as measured, with no
  recommendation and no adoption.

  **Estimation caveat, stated rather than implied.** The cross-sectional
  standard deviation of Sharpe entering the expected maximum is
  0.4520 annualised, estimated from the 121,500 evaluated specifications
  rather than from the 364,500 enumerated. The dispersion of the unevaluated
  remainder is assumed equal to that of the evaluated subset and is not
  measured. The evaluated grid also spans structurally different strategies,
  since six of the nine searched axes change which terminals are reachable, so
  the dispersion carries structural variation alongside parameter variation.
  Evidence: outputs/session-19/deflated-sharpe.csv.
- **9.13 defect-class rule — closed (session 16b, 2026-08-19).** **A defect
  found in one location triggers a sweep for the class rather than a repair of
  the instance.** Two precedents. **D18**, the object-dtype boolean negation,
  was found in one script, repaired, and then appeared again in the next
  session's own first implementation, and only a repository-wide sweep in
  session 15 established that no site lay in the return-generating path.
  **D24**, the unenumerated grid axes, was visible as the single S3
  vote-threshold literal before session 14, which recorded it as blocking for
  the grid and repaired it as a one-off, when seven further axes carried the
  same defect and the placeholder that concealed them sat in the same file.
  Every repair session from here reports the class swept, the sites found, and
  which lie in the return-generating path.
- **D25 — recorded as documentation (session 16b, 2026-08-19).** Session
  13.5's effective-exposure figures are superseded by **1.777 mean, 1.051 in
  the worst trailing-return decile, and 1.499 in the wildest volatility
  decile**, measured on the realized open-to-open panel with the cap over the
  corrected primary window. **The de-exposure-into-volatility-stress claim is
  weaker than the standing figure stated**, being a 16 percent reduction from
  the mean rather than the 38 percent implied by 13.5's 1.06 against 1.70,
  while the return-axis claim holds at a 41 percent reduction. Recorded as a
  method requirement: **the decile conditioning statistic is computed on full
  history before the window slice**, since slicing first discards the 60
  sessions the rolling estimator needs and moves the wildest-volatility figure
  by roughly 0.23.
- **D24 — CLOSED (session 16b, 2026-08-19)** by the 7.2 through 7.9
  enumeration above, with three axes resolved by construction alone and
  carrying a 9.10 disclosure. The grid is constructible and validate() proves
  it by computing the product from the axes.

## 8. Evaluation (not yet run)

- **8.1 — closed.** Risk-free is DTB3 (`RISK_FREE_SERIES`), distinct from
  financing constants.
- **8.2 — closed.** Lo-corrected Sharpe as headline beside the naive one.
  **Amended (session 13.9, 2026-08-18): the Sharpe NUMERATOR is the
  arithmetic mean excess return over DTB3 (annualised ×252), the
  standard convention; the geometric annualised return is reported
  separately, and every headline figure is dual-reported under both
  numerator definitions (outputs/session-13.9/sharpe-convention.csv).
  At ~53 percent volatility the variance drag runs ~14 pp/yr, which is
  how a positive Sharpe coexists with a negative CAGR on the early
  window — a reader comparing the two sees the convention rather than
  inferring an error.**
- **8.8 / 8.9 / 8.10 — closed (design; full specification recorded
  session 12.6).** Benchmarks: buy-and-hold QQQ, buy-and-hold TQQQ,
  vol-targeted QQQ at matched exposure, one fast-rebalancing naive rival
  at comparable trading frequency, and each of the four sleeves run
  standalone at full budget. Nulls: a timing shuffle preserving state
  distribution and holding-period structure via block bootstrap under
  8.9, and a turnover-matched switching null at the measured transition
  rate. All at canonical parameters per 9.8, 1,000 draws, every line
  bearing the identical cost model. Ensemble against the best single
  sleeve is disclosed as post-hoc and joins 8.10's Romano-Wolf family.
  Pairwise correlation of the four standalone tracks reported alongside.
  Rationale: buy-and-hold comparisons confound the signal with a trading
  frequency of 105 transitions per year. Nothing executed.
  **Amended (session 13.7, 2026-08-18; pre-registered before the ladder
  runs): two benchmarks added.** (i) **Matched-exposure levered
  benchmark**: a constant levered QQQ position at the strategy's mean
  effective market exposure — 1.70 as measured by session 13.6 at the
  anchor (step 6's rebuilt measurement was halted by the step-1 SOXS
  gate; the value is to be refreshed when the rebuilt run exists) —
  rebalanced daily, run through the same cost model as the strategy.
  Tests whether the strategy adds anything over levered beta. (ii)
  **Long-legs-only benchmark**: the strategy with every inverse-equity
  destination routed to sleeve cash at DTB3, otherwise unchanged.
  Separates long selection from short selection; specification identical
  to ablation arm B (session 13.6), entering the ladder as a comparison
  rather than a structural test, so the figures may be shared. Neither
  has run.
- **8.11 metric set — closed (session 15, 2026-08-19).** The grid emits
  per-specification statistics across 218,700 specifications, so a metric
  absent from the emitter cannot be added later without re-running the
  grid, and the set is fixed here. **41 STANDALONE metrics the emitter
  carries per specification**: the eight session-14 figures (annualised
  return, annualised volatility, naive Sharpe, Lo-corrected Sharpe,
  maximum drawdown, Calmar, arithmetic mean excess return, annual
  turnover), the distributional set (Sortino at a minimum acceptable
  return fixed at the DTB3 rate, downside deviation, skewness, excess
  kurtosis, value at risk and conditional value at risk at 95 and 99
  percent in daily and annualised terms), the drawdown set (maximum
  drawdown duration in sessions and calendar days, time to recovery or
  the statement that recovery did not occur inside the window, count of
  drawdowns exceeding 20 percent and their mean duration, Ulcer index,
  pain ratio), the stability set (per-calendar-year return and
  Lo-corrected Sharpe, rolling twelve-month Sharpe minimum and maximum
  and fraction of windows below zero, percentage of positive months,
  split-half Sharpe on the primary window split at the median session),
  and the implementation set (return per unit of annual turnover,
  turnover-adjusted Sharpe as a raw ratio). **12 BENCHMARK-RELATIVE
  metrics the emitter carries only for the ladder lines 8.8 fixes**:
  information ratio, tracking error, alpha, beta, R-squared, alpha
  t-statistic with Newey-West standard errors at a **lag of 21 sessions
  fixed before the run** with the Andrews automatic bandwidth reported
  alongside as a check, up-capture, down-capture, and their supporting
  counts. **The information ratio is reported wherever an alpha is
  reported and an alpha is never reported alone**, since session 14
  reported annualised alpha with no denominator, which reads as a large
  positive number alongside a sixth-place Sharpe: on the designated cell
  the strategy's alpha against buy-and-hold TQQQ is +0.291 at a
  Newey-West t of 2.42 while its information ratio against the same line
  is −0.194. Full set: outputs/session-15/grid-emitter-metric-set.csv;
  values: outputs/session-15/metrics-full.csv.
- **9.12 report generation — closed (session 15, 2026-08-19).** Report
  prose figures are read from the emitted CSVs rather than restated from
  a separate computation. Prose-versus-data drift appeared in two
  consecutive sessions, three figures in session 13.9 and three in
  session 14, so the rule carries an enforcement mechanism:
  `scripts/check_report_figures.py <session-dir>` re-derives every
  decimal figure appearing in a session report and reports those it
  cannot locate in that session's own CSVs at two, three, or four decimal
  places, in level or percentage form. The check runs on every session
  report from session 15 onward. Figures a report legitimately carries
  from an earlier session or from an external source are expected to
  appear in the unmatched list and are confirmed by hand against their
  stated source; on session 15's own report the mechanism returned three
  unmatched figures, being the uncapped continuity-arm pair 52.86 and
  1.3742 carried from session 14's canonical-capped.csv and confirmed
  against it by hand, and one register identifier its context filter
  missed. **Stated limitation: the mechanism is partial.** Run
  retrospectively against session 14 it returns thirteen unmatched
  figures, of which none is one of the three errors that session
  actually carried, because two of those three were not decimal figures
  at all, one being a count spelled as a word and one being a list of
  item names. The mechanism catches numeric drift between prose and the
  emitted CSVs and does not catch a miscounted or misnamed claim, so a
  report's non-numeric claims still require the hand check that found
  these three. **Extended session 15.5, 2026-08-19: the comparison runs
  to six decimal places**, since three figures session 15.5 carried from
  its own emitted CSVs were reported unmatched at the previous five-place
  limit; that is a change to the checking mechanism and not to any
  measurement.
- **6.23 short-leg instrument and hedge intensity — DIAGNOSTIC ONLY, no
  arm adopted (session 15.5, 2026-08-19; post-hoc under 9.10).** The
  canonical specification is unchanged, every arm below is a labelled
  diagnostic arm reported alongside the canonical and never in place of
  it, and **nothing measured is adopted**. The 9.10 disclosure: the
  comparison was motivated by a visible result, being SQQQ's
  primary-window contribution decomposing into −39.35 beta and −0.05
  residual in session 13.5. **The arm table was fixed and written to
  outputs/session-15.5/arm-registration.csv before any performance
  statistic was computed on any arm.** T10's budget is 25 percent of NAV
  and short notional is the sleeve budget times the branch weight times
  the leverage multiple, with SQQQ at −3.0 and PSQ at −1.0 read from
  src/schedule.py.

  | arm | short leg | branch weights | short notional | role |
  |---|---|---|---|---|
  | A | SQQQ | 50% SQQQ, 50% TLT | −37.5% | canonical, positive control |
  | B | PSQ | 50% PSQ, 50% TLT | −12.5% | direct swap at equal weight |
  | C | SQQQ | 16.667% SQQQ, 50% TLT, 33.333% cash | −12.5% | notional twin of B |
  | D | SQQQ | 33.333% SQQQ, 50% TLT, 16.667% cash | −25.0% | intensity curve |
  | E | PSQ | 100% PSQ | −25.0% | reported, CONFOUNDED |
  | F | none | 100% TLT | 0% | no-short control |
  | B_all | PSQ | as B, applied sleeve-wide | −12.5% | SECONDARY |

  **Structural constraint recorded rather than omitted**: notional
  matching above −25 percent is unreachable with PSQ, since the canonical
  −37.5 percent would need 150 percent of the branch and breach the 5.3
  gross cap at 100 percent. Arm E reaches −25 percent only by displacing
  TLT entirely, so it changes two things at once and is labelled
  confounded and excluded from the instrument comparison. Displaced
  weight routes to sleeve cash accruing DTB3 through the existing
  1.9/2.11 path with no new accounting path. **Arm B_all is required as a
  secondary arm** because SQQQ appears in four sites across three sleeves,
  being T10's rs-bear terminal, T11's bull-short basket, both T11 bear
  sub-model terminals, and S2's defensive state, so a T10-only
  substitution does not remove SQQQ from the portfolio. SH appears in no
  weight dictionary anywhere and enters only as the right side of the
  AGG>SH pairwise comparison.

  **No arm is adopted, the canonical instrument set, sleeve weights,
  thresholds, cost model, cap level, NAV, and window boundary are
  unchanged, and acting on any of this before the grid and the holdout
  have run would convert a mostly pre-registered study into a fitted
  one.** Measurements: outputs/session-15.5/.

- **9.8 — closed.** Implementation dimensions run at canonical parameters,
  not crossed into the grid (slippage base sweep, SMH accrual arm).
- **9.10 — closed.** Assumption-based closures must carry provenance —
  the [A] flags in this register.

## Backlog dispositions re-registered (session 13.9, D3)

- **1.12 — closed by measurement (session 00C).** Distribution coverage:
  worst ticker 4.05 bp/yr internal inconsistency, median 0.06.
- **2.18 — addressed (session 00A).** VX early-liquidity inspection;
  2004–2005 unusable under construction B, gating 2.9's start.
- **2.20 — closed by measurement (session 00C).** SMH stitched across the
  December 2011 HOLDRS conversion with no price discontinuity.
- **6.7 — informed (session 00E), value canonical at 3-of-4.** The vote
  threshold; the leave-one-out clarification ran in 00E; the literal was
  moved to config.S3_VOTE_THRESHOLD by session 13.6 (D1).
- **6.16 — closed (session 00D).** S2 trend filter series: TQQQ as
  supplied, QQQ as matched arm.
- **6.20 — closed by measurement (session 00C).** RSI(inverse) equals
  100 minus RSI(underlying) to ~1.1–1.3 points mean absolute difference.

## Corrections list — claims made and later overturned

1. **00C RSI null handling** read a missing bar as zero change
   (forward-fill in effect). Fixed in the session 01 lift; audit showed
   zero interior nulls so no 00C measurement was affected.
2. **Session 01's segment-reseeding** for interior gaps was replaced by
   skip (1.9 closure, session 09).
3. **00C manifest hashes** were invalidated by 00E's truncation;
   00E's manifest-truncated.csv is authoritative (session 01 flag,
   session 04 confirmation).
4. **Session 04's first SMH yield figures were 2× inflated** (split-
   adjusted price used as as-traded) and **KLAC dividends 10× understated**
   (post-window split) — both corrected in-session; the panel-wide
   boundary check (1.8 redefinition) now guards the class.
5. **Session 05's tier apparatus** (and session 06's revision) were
   abandoned entirely — see 4.3 history.
6. **The rolling-quantile crash form** was withdrawn on session 03's
   evidence — see 6.10 history.
7. **Session 10's first vol synthetics** used the constant-maturity price
   level (omits roll yield); rebuilt on construction B same session.
8. **Session 10's equity-band passes** carry no information (circularity);
   the correlations/TDs are the evidence.
9. **The vol-fund "failures" were a validation-target artifact**: against
   issuer NAV, UVXY validates at 0.9998 and the synthetic matched SVXY's
   crisis-day NAV to 9 bp (−96.09 vs −96.18); the exchange close said −32
   that day. One session (2018-02-06, fund's actual book +187% vs index
   +26%) remains genuinely unmatched (sessions 11–12).
10. **Session 12's first SVIX/UVIX builds double-counted collateral**
    (the Cboe indices are total-return-like); corrected in-session.
11. **The session 12 brief's SOXX splits (2016 3:1, 2021 2:1)** are not in
    the vendor record, which shows a single 3:1 on 2024-03-07 —
    discrepancy flagged, boundary-consistent either way.
12. **Session 13's step-7 "no lookahead" check was misnamed and
    under-specified** (renamed "execution-lag sensitivity" by session
    13.6). Lookahead makes lag hurt, and T+1 was the worse arm on
    annualised return, so the check fired on the opposite condition to
    the one its name implied. The check was specified without naming a
    metric and without stating a direction; annualised return and
    Lo-corrected Sharpe disagree on its verdict (return improves under
    one extra session of lag, the Lo-corrected Sharpe degrades), and 8.2
    designated the Lo-corrected figure as headline before any result
    existed. No dedicated lookahead test has run; the SPY positive
    control covers engine accounting, not signal construction.

## Open decisions with blockers

- **4.6 sizing size-dependence** — blocked on a first backtest result
  (the sweep measures starting NAV; the account compounds, so the
  question applies to terminal size).
- **5.6 / 5.7** — computed in the backtest session.
- **6.13 / 6.14 orderings** — measurements complete; closure is a register
  call.
- **7.14 sub-periods** — needed by the backtest report.
- **SVIX/UVIX representation residual** — validated only against exchange
  closes (+7.5–8.9%/yr residual of the close-timing class); issuer NAV
  unobtainable at bounded effort.

## 10. Custody and environment

- **10.1 custody, environment, and the partial PBO, recorded (session 18s,
  2026-08-19).** A maintenance entry. No strategy parameter, config value,
  or prior register decision is touched by it, and no measurement was run.

  **Relocation.** The repository moved from `~/Desktop/tactical-allocation`
  to `/Users/GualyCr/Downloads/tactical-allocation` on 2026-08-19. The
  Desktop path sat inside iCloud Drive, which is what exposed the working
  tree to eviction. The Downloads path is outside that sync root. All
  earlier session reports referencing the Desktop path remain correct as of
  their own dates.

  **The eviction incident and its resolution.** During session 18 iCloud
  evicted files across the tree and reads returned zero bytes, which is
  indistinguishable from destruction without inspecting the dataless flag.
  Session 18 halted at step 3 on the conclusion that data had been
  destroyed. Session 18r superseded that conclusion. 339 of 339 manifested
  frozen inputs verify against their acquisition manifests, with the 1.14
  truncation manifest superseding the acquisition hash for the 39 files it
  touched. All 24 grid shards read and parse across 121,500 specifications
  with no gap and no duplicate in the identifier space, `git fsck` exits
  clean, and nothing was lost. The eviction was fully reversible. Session
  18s confirms zero dataless files across 1,740 files outside `.venv` at the
  new path.

  **Environment rebuild.** `.venv` crossed the relocation as evicted stubs
  across 3,751 files and caused an indefinite `import numpy` hang during
  session 18. It was removed and rebuilt from the system interpreter at
  `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`, which is
  Python 3.13.13, the same interpreter and the same version that built the
  environment session 17's grid ran under. **No package version diverges.**
  All 30 installed packages hold the versions recorded before the rebuild,
  and all 24 pins declared in `requirements-session-00a.txt` match. The six
  packages installed beyond that file are `pytest` with its four transitive
  dependencies plus `pypdf`. The rebuild installed from a freeze captured
  before removal rather than from the declared file alone, so that `pytest`
  survived and the environment reproduced exactly. Evidence is
  `outputs/session-18s/environment.csv`. Session 17's grid results therefore
  stand under an environment that is unchanged in every resolved version.

  **Object store packed.** The store held 886 loose objects and zero pack
  files at 202 MB. `git gc` packed 862 of them into a single pack, leaving
  24 loose and 197 MB. `git fsck --no-dangling` exits clean after packing
  and `HEAD` resolves unchanged. Packing consolidates and adds per-object
  checksums, and it does **not** create a second copy of anything. The
  repository still has no remote and no off-machine copy, so it remains
  single-copy and one storage failure from total loss.

  **The partial PBO output.** `outputs/session-18/pbo.csv` presented as a
  finished artifact while carrying only three of six planned passes, and the
  only record of that was a commit message. It is renamed to
  `outputs/session-18/pbo-partial.csv` with its content byte-identical,
  verified by SHA-256 across the rename. Completed are S equal to 8 at a PBO
  of 0.1143 over 70 combinations, S equal to 12 at 0.1710 over 924, and S
  equal to 16 at 0.1578 over 12,870, all on the full grid and all full
  enumerations, with S equal to 16 the preregistered primary. Not run are S
  equal to 24, S equal to 48, and the smooth-axis restriction. Per-pass
  status is at `outputs/session-18/pbo-partial-status.csv`. No PBO figure
  was recomputed and no missing pass was run.

  **Two items carried forward, neither actioned here.** D26 and D27 were
  raised in `outputs/session-16b/REPORT.md` and never written into this
  register, which currently ends its defect numbering at D25. The scaffold
  background for session 18s names `a90f352` as the commit carrying sessions
  16b through 18r, which is off by one, since `a90f352` is session 16 and
  `9e7aa47` carries 16b, 17, 18 steps 0 through 3, and 18r.

- **8.12 probability of backtest overfitting, RESULT (session 19, 2026-08-19).**
  Pre-registered before any result was read, being **S equal to 16** as primary
  under the Bailey, Borwein, Lopez de Prado and Zhu convention, a combination cap
  of 20,000 at seed 20260821, and a memory ceiling of 2.0 GB.

  **PBO is 0.1578** over 12,870 combinations, being the full
  enumeration of C(16,8), across the 121,500 evaluated specifications. Session
  18's interrupted run measured the same figure on the same construction and it
  reproduces exactly. The performance degradation regression of out-of-sample on
  in-sample Sharpe gives slope **-1.0663**, intercept
  2.7549, and R-squared 0.5469.
  The probability of loss is 0.000078. Neither first nor
  second order stochastic dominance of the selected specification over the median
  trial holds. The canonical point, which was pre-registered rather than selected,
  carries a mean out-of-sample rank of 0.8243
  expressed as a fraction of the specification count, and is reported separately
  from the in-sample-best for that reason.

  **The naive-Sharpe approximation, disclosed rather than implicit.** The CSCV
  performance metric is the naive Sharpe and not the Lo-corrected Sharpe that 8.2
  designates as headline. Autocovariance is not additive across disjoint blocks,
  so the cross-boundary terms are missing from any union of blocks and a Lo
  correction computed on a union would be wrong rather than approximate. The naive
  Sharpe is exactly reconstructible from the stored block sums, which is why it is
  used, and the PBO therefore measures overfitting of the naive Sharpe.

  **Block-count sensitivity.** PBO reads
  0.1143 at S equal to 8, 0.1710 at 12,
  0.1578 at 16, 0.1646 at 24, and 0.1540 at 48.
  S equal to 8, 12 and 16 are full enumerations. S equal to 24 and 48 exceed the
  20,000 combination cap fixed before the run and are random samples at the
  registered seed, which is disclosed per pass in the emitted file.

  **Moment additivity re-verified.** The maximum absolute deviation between
  statistics reconstructed from the 48 stored block moments and the same
  statistics in the per-specification metric set is 3.331e-16 against a 1e-10
  tolerance fixed before the comparison ran, recomputed this session rather than
  taken from the session 18 file that the eviction touched.

  **Peak memory exceeded the stated ceiling and that is recorded rather than
  absorbed.** The chunk size is derived from a 2.0 GB ceiling counting four large
  arrays, and observed peak resident memory reached 2.879 GB at S equal to 16 and
  3.355 GB at S equal to 48, because the working set carries the moment array and
  the merged block copies alongside the four the formula counts. The machine
  carries 8 GB, so the ceiling is not decorative. No pass was re-run and no figure
  changes, since the arithmetic is unaffected by the chunk size.
  Evidence: outputs/session-19/pbo.csv, outputs/session-19/PBO-REPORT.md.

- **8.13 PBO within structural strata, DESIGN AND RESULT (session 19,
  2026-08-19).** The session 18 prompt specified a smooth-axis restriction, being
  the PBO computed with all six structural axes held at canonical and only the
  three smooth axes varying. **That restriction is replaced rather than run.** It
  spans 3 by 3 by 3, being 27 specifications, and a 27-point PBO is not comparable
  to a 121,500-point figure.

  The purpose the restriction served was to separate overfitting arising from
  parameter search within one strategy shape from overfitting arising from search
  across shapes. **Stratification serves that purpose at usable sample sizes.**
  For each of the six structural axes and each value on that axis, the axis is
  held fixed and PBO is computed over the remaining specifications, being 121,500
  divided by the axis cardinality, which is 24,300 to 40,500 per stratum.

  | structural axis | PBO min | PBO max | full-grid inside |
  |---|---|---|---|
  | sma_long | 0.1033 | 0.1882 | yes |
  | crash_threshold | 0.1688 | 0.1807 | no |
  | rsi_dip | 0.0667 | 0.1874 | yes |
  | rsi_rs | 0.1232 | 0.2303 | yes |
  | overbought_t1 | 0.0100 | 0.4673 | yes |
  | oversold | 0.0731 | 0.2026 | yes |

  **Result as measured.** Against a full-grid reference of 0.1578,
  the full-grid PBO exceeds none of the 6 within-stratum ranges, lying inside 5 of them and below 1, which indicates search across strategy shapes does not contribute overfitting beyond parameter search, with the one range it falls below indicating the full grid overfits less than any single stratum of that axis. No recommendation follows and no grid point is
  adopted or promoted over the canonical.

  Each stratum is reported with the terminals that never fire at that value, drawn
  from outputs/session-18/reachability.csv, so a reader can see what structural
  difference each stratum represents. The widest range is overbought tier one, at
  0.0100 to 0.4673 across its five values. Evidence:
  outputs/session-19/pbo-strata.csv.

- **9.14 four-tier artifact scheme, EXECUTED (session 19, 2026-08-19).** The
  scheme as run. Tier one is the frozen raw inputs, committed and hash-verified.
  Tier two is the derived grid evidence, being the 48-block moment sums, the
  per-specification metric set and the specification index across eight shards,
  all committed. Tier three is the retained daily-return sample, being the 2,000
  specification subsample drawn at the config-fixed seed, committed. Tier four is
  the ephemeral daily return panel, which is not committed and is deleted once the
  tiers above it can carry every downstream figure.

  **The deletion ran this session.** 8 shards of the
  session 17 panel and 8 shards of the superseded
  ten-axis partial panel were removed, reclaiming 1256.8 MB and
  taking the working tree from 1764.7 MB to
  508.0 MB.
  The superseded directory was NOT removed wholesale, and its grid moments, block
  sizes, metrics and shard logs are preserved.

  **The regenerability check is the test that the deletion was safe.** The PBO
  report and its four figures are produced by a generator that never opens the
  panel directory, and the check is that generating the document before and after
  the deletion yields byte-identical output. It does, at SHA-256
  510868bf6c3bce31... across the report and all four figures. The
  manifest carries the canonicalised panel hash and the exact command that
  regenerates the panel, and scripts/verify_panel.py reports maximum absolute
  deviation against a 1e-6 tolerance rather than asserting bit-identical equality,
  since float reduction order varies with thread count and BLAS version and the
  run was sharded across eight processes. Evidence:
  outputs/session-19/deletion.csv, outputs/session-19/MANIFEST.json.

- **9.15 terminal counter positive control, BASIS CORRECTED (session 19,
  2026-08-19).** The session 18 prompt named the primary window as the basis for
  the step 1 terminal counter and that was wrong. **Session 13.5 measured the
  synthetic panel over the full window from warm-up**, at
  scripts/s13_5_diagnostics.py line 374, and on that basis the two T11 PSQ-dip
  terminals reproduce exactly, firing zero times at oversold 20, 25 and 30, then 1
  and 23 times at 35, then 10 and 113 at 40.

  **On the realized panel over the corrected primary window** the same terminals
  read zero, zero and zero at 20, 25 and 30, then 0 and 3 at 35, then 0 and 39 at
  40, and the bond-baller PSQ-dip terminal never fires at any oversold value.
  **Both bases are recorded and the primary-window figures are the ones that
  describe the study's actual window.** The counter is validated and the prompt
  named the wrong basis, so a session comparing against the primary window would
  have read a basis difference as a defect. Evidence:
  outputs/session-18/reachability.csv under table positive_control.

- **10.2 remote created, single-copy exposure CLOSED (session 19, 2026-08-19).**
  The repository had no remote and no off-machine copy through nineteen sessions,
  and one iCloud eviction incident had already occurred. A private GitHub
  repository was created at https://github.com/boomer25tiger/tactical-allocation and the full history pushed, with the
  remote main matching local HEAD and upstream tracking set.

  192.18 MB in 862 objects
  were pushed. The largest tracked file is outputs/session-18/spec-index-augmented.csv and nothing
  over 100 megabytes enters history. Both ephemeral panel directories and the
  virtual environment remain excluded by .gitignore.

  **The first push failed** with RPC error HTTP 400 and nothing reached the remote,
  which is the large-pack symptom over HTTPS. It succeeded after setting
  http.postBuffer to 524288000, which is local git configuration only and altered
  no history, no object and no tracked file.

  **Session 18s packed the object store on a premise stated wrongly in its own
  prompt.** Consolidating 886 loose objects into one pack adds per-object checksums
  and cheaper integrity checking, and it does not create a second copy of anything.
  This entry is what creates the second copy. Evidence:
  outputs/session-19/remote-status.csv.

- **9.16 window strip, POST-HOC SENSITIVITY under 9.10 (session 19.5,
  2026-08-19).** A strip of start dates run with every other axis held at canonical
  and every window ending at 2021-08-01. **The primary window remains 2011-10-04**
  and this entry changes no boundary.

  **Motivation, recorded before the results were read.** The ladder's buy-and-hold
  QQQ row reads 1.792 Lo-corrected Sharpe, and window arithmetic over the primary
  window supported a naive Sharpe near 1.25 with an autocorrelation that did not
  obviously support a Lo factor large enough to close the gap. Separately three
  ladder rows sat within 0.004 of each other, which is the pattern costless leverage
  produces. Both were arguments from arithmetic rather than measurements, and this
  session measured them.

  **Result.** The positive control reproduces the canonical at the canonical start
  to 2.55e-07 and
  3.06e-07. Across six start dates
  **the strategy's rank among twelve is not stable**, spanning
  3 to 6 under the naive Sharpe and
  5 to 7 under the Lo-corrected Sharpe, with the
  canonical start returning the lowest rank of any date tested under both metrics.
  Reported as measured, with no interpretation, no recommendation and no change to
  the primary window. Evidence: outputs/session-19_5/window-strip.csv.

  **The earliest full-composition start is later than canonical.** On the synthetic
  panel every ticker named in src/sleeves.py is available and past warmup only from
  2013-01-23, bound by
  QQQE first appearing
  2012-03-21 plus
  210 warmup sessions. The strip therefore
  has no arm reaching back before the canonical window, and the 2007 date the
  scaffold anticipated does not exist as a full-composition start.

- **9.17 ladder construction audit, NO DEFECT, with the 9.13 class sweep (session
  19.5, 2026-08-19).** Every levered and inverse line in the twelve-row ladder holds
  the live fund ticker taken from the frozen fund parquet on the realized arm through
  `_frozen_frame`, rather than a costless scaling of the underlying. Financing and
  daily reset apply to the reconstructions on the synthetic arm only, where the rate
  source is frozen DTB3 at rate over 360 per calendar day under 5.5a, the spread is
  `config.FINANCING_SPREAD_BP` for multiples above one with a haircut for inverse
  funds and k equal to zero for the volatility funds under 2.15, and the reset
  compounds daily at the close.

  **Decisive check, tolerance 5e-03 stated before comparing.** Annualised volatility
  discriminates where the naive Sharpe does not, being untouched by the risk-free
  subtraction and the account's cash accrual. The ladder's buy-and-hold TQQQ row sits
  0.001025 from the live fund and
  0.009650 from a costless daily-compounded
  3x QQQ, a factor of nine closer to the live fund. **No row is a costless scaling.**

  **Scope of the 9.13 sweep.** Run regardless of the gate. With no defect found there
  is no defect class to sweep, and the sweep instead records the construction of all
  fourteen levered and inverse instruments the strategy trades. **The canonical result
  at 0.521845 and 1.381701 does not depend on any instrument carrying a
  costless-scaling construction**, since the canonical runs on the realized arm where
  every one of them is the live fund's own frozen history. Nothing was repaired.
  Evidence: outputs/session-19_5/construction-audit.csv,
  outputs/session-19_5/defect-sweep.csv.

  **Two findings the audit surfaced that the gate does not cover, recorded rather
  than acted on.** First, **every ladder row carries the superseded 2011-10-03
  boundary**, its STRATEGY row reading 1.3846
  over 2473 sessions against the
  7.14a corrected 1.3817 over 2472, because session 15 ran before the correction and
  `s14_common.PRIMARY_START` still defaults to the superseded date. Session 20 step 5
  owns the ladder repair and 8.8 is deliberately not amended here.

  Second, **the Lo correction's scale factor is not separable from sampling noise at
  this sample length**. `bt.lo_sharpe` sums 251 weighted sample autocorrelations from
  2472 observations. Against a null of
  300 independent permutations of the same excess
  returns at a seed fixed before drawing, which destroys serial dependence entirely,
  QQQ's observed weighted sum of -74.213 sits
  1.417 standard deviations from a
  null mean of -12.382, and a series with no
  autocorrelation at all still produces a mean Lo factor of
  1.1129 reaching
  1.4783 at the 95th percentile against QQQ's
  observed 1.5598. The null mean exceeds one
  because each sample autocorrelation carries a small-sample bias of order minus one
  over n and 251 of them are summed with weights up to 251.

  **8 of the twelve rows change rank
  between the naive and the Lo-corrected Sharpe**, and the three rows the motivation
  flagged span 0.0038 on the Lo-corrected
  Sharpe against 0.0315 on the naive
  Sharpe, a factor of 8.23 wider, so their
  convergence is produced by the correction rather than by the construction. Whether
  8.2 keeps the Lo-corrected Sharpe as headline is a register decision this session
  does not make.

- **9.18 early-window reporting form, TENSION RECORDED AND LEFT OPEN (session 19.5,
  2026-08-19).** 7.14b fixed the early-window reporting form as coverage tables and
  the per-instrument availability timeline only, with no return figure at any
  prominence. The 9.16 strip emits return figures at its earliest start as a
  diagnostic, which is in tension with that form.

  The tension is narrower than it first appears, since the earliest full-composition
  start is 2013-01-23 rather than a 2007
  date, so no strip arm sits in the 2007-01-03 to 2011-10-02 extension 7.14b governs.
  Over that start's 2146 sessions,
  0.2749 of them lack at least one
  sleeve-held ticker on the realized panel, so a start there is confounded with panel
  source because the panel differs alongside the window. The confound is disclosed
  rather than resolved.

  **Whether any early-start figure enters the paper is a register decision. It is not
  made here and this entry does not pre-empt it.** Evidence:
  outputs/session-19_5/coverage-early.csv.

- **9.16 rank sentence, CORRECTED (session 20, 2026-08-20).** The sentence recorded
  above, that the canonical start returns the lowest rank of any start date tested
  under both metrics, is **false**. Under the naive Sharpe the canonical ties the
  pre-D21 boundary at rank 6, the worst of the six arms rather than uniquely so.
  Under the Lo-corrected Sharpe the 2013-01-02 arm falls below it at rank 7, so the
  canonical is not the worst on that metric. The same false sentence was committed in
  outputs/session-19_5/REPORT.md and docs/STATE.md and is corrected in all three.
  Correctness repair. Evidence: outputs/session-19_5/window-strip.csv.

- **8.12 amended (session 20, 2026-08-20), correctness repair.** The entry records
  that no arithmetic depends on the chunk size. **The sweep falsifies that.**
  `n_is = float(mc[0] @ nvec)` takes the in-sample session count from the first
  combination of each chunk and applies it chunk-wide, and merged super-block counts
  are unequal, so the three regression figures depend on where chunk boundaries fall.
  The class appears at four sites, being scripts/s19_step4.py, scripts/s18_step3.py,
  scripts/s19_draws.py, and scripts/s19_step5.py, the last being the stratified pass.
  All four are repaired. **The re-emission did not run**, halted on the memory gate
  with free plus inactive memory at 1.33 GiB,
  so the three regression figures in outputs/session-19/pbo.csv and the regression
  columns of pbo-strata.csv still carry the defect. The known magnitude is
  3.176e-04 on the S equal to 16 slope. PBO and the
  stratified PBO are immune, since within a chunk the substituted count scales every
  specification identically and preserves the ordering the rank and the argmax read.

- **8.8 amended (session 20, 2026-08-20), correctness repair.** The matched-exposure
  levered QQQ row was built at 1.70 where D25 superseded that with 1.777. Rebuilt at
  the corrected boundary from frozen inputs, holding TQQQ at exposure over three
  rebalanced daily, which is the convention read from scripts/s15_lines.py rather
  than assumed, and on the realized arm TQQQ carries the issuer's own financing and
  daily reset so no separate financing model applies.

  | exposure | TQQQ weight | annualised | volatility | naive Sharpe | Lo Sharpe |
  |---|---|---|---|---|---|
  | 1.7 | 0.5667 | 0.367317 | 0.318603 | 1.124116 | 1.801782 |
  | 1.777 | 0.5923 | 0.383126 | 0.333040 | 1.124271 | 1.802013 |

- **9.19 the derived held universe (session 20, 2026-08-20).** The held and signal
  sets are derived from the abstract syntax tree of src/sleeves.py, giving
  **19 held** and
  **13 signal-only** tickers, which
  reconciles exactly with session 19.6. **outputs/session-20/held-universe.csv is the
  artifact that supersedes every hardcoded ticker list in the repository**, carrying
  the sleeve, function, line number, and weight expression for every held ticker.
  The list in scripts/s195_strip.py carried four misclassifications, being FAS, SH,
  and KMLM treated as held when they are not, and QQQ treated as a signal input when
  it is held. Correctness repair for the artifact, specification change for any
  repository-wide refactor.

- **9.20 SVIX and UVIX, unreachable in sample and at the holdout read (session 20,
  2026-08-20).** Both are held in code and load on neither panel. `State.available`
  at scripts/s13_backtest.py:344 returns False for a ticker absent from the panel, so
  the availability switches resolve to SVXY and UVXY on every session. Across the
  primary window the T10 terminal fired 1114
  times and the S3 terminal 519 times, while
  SVIX and UVIX were selected zero times.

  **The engine raises on an unlisted held ticker.** The fill path at
  scripts/s13_backtest.py:500 reads px = raw[t][i] where raw is built only over
  panel.frames, so an absent ticker raises KeyError rather than being dropped,
  renormalised, or routed to cash. Register 1.9 covers threshold reads and is silent
  on weight dictionaries, and the traced behaviour is an exception.

  **The holdout consequence.** SVIX and UVIX list 2022-03-30 on the frozen files,
  inside the holdout span from 2021-08-01, so the source strategy's date guards would
  activate there while this implementation will not. The branch executed zero times
  in sample and will execute zero times at the holdout read under the current loader,
  so the holdout measures a strategy that differs from the source over that span.
  Whether the loader should carry the two tickers is a register decision this session
  does not make.

- **9.21 QQQ is held and is also a ladder benchmark (session 20, 2026-08-20).** QQQ
  is held on 195 of
  2472 primary-window sessions at a mean weight of
  0.1244 conditional on holding and
  0.0098 unconditional. The
  arithmetic share of the strategy's summed daily return attributable to that
  position is 0.007405, so the gap
  against the buy-and-hold QQQ ladder row is partly a comparison of the strategy
  against a component of itself. Documentation, reported without recommendation.

- **9.22 three defect class sweeps under 9.13 (session 20, 2026-08-20).** The
  chunk-first-element class at four sites, all repaired in code with the re-emission
  outstanding on the memory gate. The vacuous-check class at five checks, all
  repaired with an explicit cardinality floor asserted before the predicate, being
  eight per shard class for the required-artifact check, four for the regenerability
  figure count, ten prose figures and ten CSV numerics for check_report_figures.py,
  twenty-one comparisons for the additivity accumulator, and one row per shard for
  the parse consistency line. The hardcoded literal class swept across scripts and
  src, with divergent ticker lists reported against the derived held set rather than
  refactored, since replacing every list is a specification change.

- **9.23 the boundary repair (session 20, 2026-08-20), correctness repair.**
  scripts/s14_common.py line 29 read 2011-10-03 and no session 15 script overrode it,
  so every session 15 primary-window row carried
  2473 sessions against the corrected
  2472. The default is corrected and
  the affected outputs are rebuilt into outputs/session-20/rebuilt/ with the
  originals preserved.

  The strategy moves from 0.522592 to
  0.521845 annualised and from
  1.384621 to
  1.381701 Lo-corrected Sharpe, reproducing
  7.14a's corrected values. **No ladder rank changes on either metric** and the
  strategy holds sixth of twelve. The information ratio moves from
  0.703614 to
  0.709366 and the
  Newey-West alpha t from
  2.347007 to
  2.364283.

  **Gate C tripped.** On the designated cell the timing-shuffle null on annualised
  return moves from p 0.000
  to p 0.001,
  which does not clear p below 0.001, and the strategy's percentile on that arm moves
  from 100.0 to 99.9.
  On the Lo-corrected Sharpe both nulls remain at p 0.000 with the strategy at the
  100th percentile. Romano-Wolf keeps one of eleven below 0.05, the equal-weight
  universe moving from 0.033
  to 0.046 with
  the strategy above. **What the paper claims from the annualised-return arm is a
  register decision left open here.**

- **D26, recorded (session 20, 2026-08-20), previously absent from this register.**
  The 7.7 amendment asserted a five-point crash axis left the 218,700 total unchanged,
  which is arithmetically impossible, and 218,700 stood in the register and in config
  for four sessions with N in 8.7 wrong throughout. Raised in
  outputs/session-16b/REPORT.md and never written here until now. Documentation.

- **D27, recorded (session 20, 2026-08-20), previously absent from this register.**
  The pre-registered enumeration rule underdetermines the cardinality when neither
  values nor a cardinality are recorded, and its one-session granularity produces a
  degenerate short-SMA sweep. Both are properties of the rule rather than of the
  register. Raised in outputs/session-16b/REPORT.md. Register decision.

- **D25, APPLIED (session 20, 2026-08-20).** The superseding exposure figure of
  1.777 is now carried by the rebuilt matched-exposure row under the 8.8 amendment
  above, so D25 moves from recorded-as-documentation to applied.

- **9.24 the Lo estimator and the 8.2 question (session 20, 2026-08-20).** Session
  19.5 measured that the Lo scale factor's sampling dispersion is of the same order
  as the gaps between ladder rows, and session 19.6 established that q is a Python
  default parameter at scripts/s13_backtest.py:609, absent from config.py and from
  every specification-curve axis. **Whether the Lo-corrected Sharpe remains the
  headline metric under 8.2 is a register decision, left open here.** The q sweep
  that would inform it is phase D of session 20 and did not run, since gate C halts
  the session before phase D.

- **Phase C recorded as FAILED (session 20, 2026-08-20).** The gate condition at
  9.23 was that both randomization nulls clear p below 0.001 on the designated cell.
  The timing-shuffle null on annualised return did not, so phase C is recorded as
  failed rather than passed. The boundary repair itself succeeded and its outputs
  stand, and phases D through G were resumed on the corrected boundary by explicit
  instruction after the gate halt.

- **8.7 amended again (session 20, 2026-08-20), correctness repair.** **N is
  121,500, the evaluated count, not 364,500.** N equal to 364,500 counts the 7.4
  tier-two offset axis, which was held at its canonical value of 10 on every
  specification and across which no maximum was ever taken. Selection operates only
  over trials actually drawn, so the evaluated count is the count the statistic
  requires. 364,500 remains the correct size of the enumerated space and is retained
  wherever it is stated as such, including MANIFEST.json's grid.n_enumerated field.
  Recorded as a correctness repair with the grounds stated rather than as a post-hoc
  sensitivity, and no 9.10 entry is opened.

  The deflated Sharpe on the naive Sharpe reads **0.001979
  for the canonical** and 0.048847
  for the in-sample-best, against 0.000660
  and 0.023736 at the superseded N.
  The propagation sweep found 29 sites
  carrying the figure, of which 13
  designate N. Evidence: outputs/session-20/deflated-sharpe-corrected.csv.

- **9.25 the Lo lag count swept (session 20, 2026-08-20).** `lo_sharpe(excess,
  q=252)` at scripts/s13_backtest.py:609 is a Python default parameter, absent from
  config.py and from every specification-curve axis, and was never swept before this
  phase. Across q of 1, 5, 21, 63, 126 and 252 the strategy's rank spans
  6 to 7 and
  **9 of twelve rows
  change rank**.

  Against a permutation null of 300 draws per
  row at seed 20260820 fixed before drawing,
  **9 of twelve rows carry
  a Lo factor inside their own no-autocorrelation null**, meaning indistinguishable
  from what a series with no autocorrelation produces at this sample length. The
  three that fall outside are exactly the three rows that outrank the strategy on the
  Lo-corrected Sharpe. The strategy's own factor is inside its null. **Whether 8.2
  keeps the Lo-corrected Sharpe as headline remains an open register decision.**

- **9.26 the axis census (session 20, 2026-08-20).** **The authoritative count of
  searched degrees of freedom is 9**,
  being the nine grid axes. The specification-curve axes are reported sensitivities
  rather than a search over which a maximum was taken, so they do not enter N. Four
  discrepancies are resolved and each is recorded as previously unrecorded. The
  participation cap was added to the curve axis list in session 19 without record,
  giving eleven where 9.11 plus NAV gives ten. The ladder dropped from fourteen lines
  to twelve, removing the intraday-only and overnight-only hold universes, recorded
  nowhere and never run through Romano-Wolf at thirteen. The Lo q is on no axis. The
  tier-two offset was held rather than searched and does not enter N.

- **9.27 the three open 9.11 axes (session 20, 2026-08-20).** One is sourced and two
  cannot be sourced by measurement.

  **SMH accrual, sourced.** Three arms measured against the canonical with every
  other axis held.

  | arm | annualised | Lo Sharpe |
  |---|---|---|
  | canonical | 0.521845 | 1.381701 |
  | accrual 0.0 | 0.520120 | 1.374755 |
  | accrual 1.0 | 0.520910 | 1.378240 |
  | accrual 2.0 | 0.523787 | 1.394313 |

  **Sizing mode, NOT SOURCED and unwired.** config.SIZING_MODE is defined at
  src/config.py:78 and validated at line 333, but the engine hardcodes
  `math.trunc(alloc / px)` at scripts/s13_backtest.py:528 and never calls
  src.execution.size_position nor reads the config. **Setting the config changes
  nothing in the return-generating path.** This is a new instance of the
  hardcoded-literal class at 9.22 and was not known before this phase. Wiring it is a
  correctness repair and varying it is a specification change.

  **Completion rule, NOT SOURCED.** scripts/s13_backtest.py lines 18 to 24 record the
  unavailable-fill completion rule as provisional and explicitly not a register
  closure, and no switch implements an alternative. Sourcing it requires implementing
  a second arm, which is a specification change rather than a measurement.

- **9.28 effective N, POST-HOC SENSITIVITY under 9.10 (session 20, 2026-08-20).**
  **Motivation, stated.** The pre-registered N returned a deflated Sharpe near zero,
  and the independence assumption underlying the expected maximum is violated by
  construction, since specifications sharing eight of nine axis values share most of
  their return path.

  Across the pre-registered 2001
  specification subsample, with the canonical inside it, the correlation spectrum
  puts 46.8 percent
  of total variance in the first principal component. Three definitions are reported
  so the choice is visible.

  | definition | effective count | expected maximum Sharpe | canonical deflated Sharpe |
  |---|---|---|---|
  | participation_ratio | 3.43 | 0.4285 | 0.981787 |
  | spectral_entropy | 6.72 | 0.6166 | 0.932982 |
  | variance_threshold_95 | 17.00 | 0.8263 | 0.798492 |
  | preregistered_121500 | 121500.00 | 2.0036 | 0.001979 |

  **Primary remains N equal to 121,500.** This entry adopts nothing and changes no
  canonical value.

- **9.29 the January 2013 event (session 20, 2026-08-20).** Fourteen sessions from
  2013-01-02 to 2013-01-22 at a cumulative -0.190783,
  appearing in no session report across nineteen sessions.

  **Attribution established rather than asserted.** UVXY is carried by
  3 sleeves during the span, being
  S3 T10 T11, and
  2 sleeves lose,
  being T10 T11. Both
  conditions hold together. S2 and S3 contribute positively, so the loss is not
  portfolio-wide.

  **The event is not singular.** 69
  overlapping fourteen-session windows across the primary window fall below minus
  0.15, and January 2013 ranks 42 among
  them. The worst is the 2020 span at roughly minus 0.50. The premise that the event
  is exceptional does not hold.

  **The strip's asymmetry, recorded.** The strategy is nested through
  run(sig["rows"]) while each benchmark line is re-initialised through
  LINES[ln][0](o2o, sig["rows"], i0), and
  7 of the eleven benchmark
  lines carry state and are therefore affected by re-entry rather than only repriced.

- **9.30 the degradation slope, UNRESOLVED (session 20, 2026-08-20).** No valid null
  exists for it. Session 19.6's null permuted block ordering independently per
  specification, which destroys the common time structure every specification shares,
  so its z-scores measure the presence of that shared structure rather than
  overfitting. The corrected value carried forward is
  -1.0666200132036998 against the emitted
  -1.0663023854544191, since the phase B1 re-emission
  halted on the memory gate. **The statistic is a candidate for removal from the
  paper and no recommendation is made on whether to remove it.**

  Session 19.6's PBO null is retained as an **estimator control** rather than a test.
  A harness fed selection driven purely by idiosyncratic noise returned
  0.991928 against the observed
  0.157809, a validation the observed
  figure never carried on its own.

  **The corrected null did not run.** Phase G was skipped on its budget gate, with
  0.06 GiB genuinely free against a requirement of about
  0.717 GB before overhead. The construction is
  recorded in outputs/session-20/degradation-null-corrected.csv so a later session
  can run it unchanged.

- **9.31 the unwired-config sweep (session 21, 2026-08-20).** The inverse of 9.22's
  hardcoded-literal class, being a config value with no consumer. Of 57
  parameters defined in src/config.py, **10 have no consumer outside config.py**
  and two more carry a read that is never invoked. Detection is on the abstract
  syntax tree, since docstring prose naming a parameter is not a read, with dynamic
  getattr resolution detected separately.

  **SIZING_MODE and EXECUTION_MODE** are read by src/execution.py as default
  arguments of size_position, which no module in the return-generating path calls, so
  each has a read site and no influence on any result.

  **FINANCING_SPREAD_BP is never read by the engine.** Its readers are the synthetics
  builder and validator plus session scripts, so the financing spread enters results
  only through the pre-built reconstructions on the synthetic arm. On the realized
  arm, which is the designated cell, the levered funds carry the issuer's own
  financing inside their price history and no financing model applies. D16 describes
  the spread as assumed and treated by the cost sweep, and this entry establishes
  that the engine never reads it.

  **SLIPPAGE_MODEL and SLIPPAGE_MODELS have no consumer while slippage_model is a
  specification-curve axis.** The axis was varied through function selection in the
  cost sweep rather than through the config value, so the curve is real and the
  parameter is inert. No grid axis is affected. **Gate A cleared**, since all nine
  grid axis attributes are read by the engine and the 121,500 count stands.

  The completion rule is not a config parameter at all. It is hardcoded in the fill
  path and marked provisional at scripts/s13_backtest.py lines 18 to 24, so it is
  unregistered rather than unread. Nothing is repaired by this entry.

- **9.32 canonical axis provenance (session 21, 2026-08-20).** Each of the nine grid
  axes traced through this register rather than inferred from code.

  | axis | canonical | register | state |
  |---|---|---|---|
  | sma_long | 200 | 6.5 / 6.6 | before |
  | crash_threshold | -15.0 | 6.10, with 7.7 fixing the swept levels | after |
  | rsi_exhaustion | 14 | 6.1 | before |
  | rsi_dip | 14 | 6.1 | before |
  | rsi_rs | 14 | 6.1 | before |
  | overbought_t1 | 70 | 6.2 / 6.3 / 6.4 | before |
  | oversold | 30 | 6.4 | before |
  | sma_short | 20 | 6.5 / 6.6 | before |
  | vote | 3 | 6.7 | before |

  **Eight of nine were fixed before any comparison on that axis. crash_threshold was
  not.** Its source value was minus 12, session 04 closed an absolute threshold at
  minus 10 after session 03 measured all three estimator forms failing, and session 09
  re-closed at the present value citing session 06's firing-rate measurement. The
  register already marks it [A], a stipulation. What those measurements compared was
  estimator form and firing rate rather than performance across levels, which is
  recorded rather than smoothed over.

  **The percentile claim, stated as measured.** The canonical's rank of 6,834 of
  121,500 on the Lo-corrected Sharpe is supported on eight axes and weakened on
  crash_threshold alone. The weakening is per axis rather than a single verdict. A
  documentation caveat travels with it, since seven of the nine closures carry no
  session attribution, so their ordering rests on the entries' source-derived phrasing
  rather than on a dated record.

- **9.33 subsample representativeness (session 21, 2026-08-20).** The 2,001-series
  subsample is representative and **phase E and session 20's effective-N figures are
  licensed**. The primary test is a resampling null of 2,000 random subsets at a seed
  fixed before drawing, which makes no distributional assumption and respects the
  finite population exactly. The observed mean sits at the
  90.80 percentile, a two-sided p of
  0.1840. All
  34 axis values fall inside a 99
  percent binomial interval and the canonical is present. A Kolmogorov-Smirnov
  distance is reported alongside as a distance rather than a test, since both of its
  assumptions fail when the subsample is a subset of the population it is compared
  against and specifications are correlated by construction.

- **9.34 the beta decomposition (session 21, 2026-08-20).** Run on the canonical's
  daily series from the frozen inputs against the investable buy-and-hold QQQ ladder
  line. The positive control passes, with the benchmark regressed on itself returning
  beta 1.0 and alpha below tolerance.

  Static beta is 1.108673 at an R-squared of
  0.186794, with annualised alpha
  0.288744 at a Newey-West t of
  2.3643 on the lag 8.11 fixes. **The beta-hedged
  residual carries a naive Sharpe of 0.655836 and
  a Lo-corrected Sharpe of 0.864915**, against the
  strategy's own 1.0911 and 1.3817. The fitted OLS residual has mean zero by
  construction and its Sharpe is identically zero, which is a property of the
  estimator, so the hedged series retaining the intercept is what is reported.

  Rolling beta over 60 sessions, read from
  config.CRASH_HORIZON_SESSIONS rather than chosen, has mean
  0.8644 and standard deviation
  1.1646 across a range of -4.4974
  to 2.7885.

  The timing decomposition splits annualised excess return into a static exposure
  component of +0.241396,
  a timing component of +0.011293,
  and a residual of +0.319875.
  **Timing is the smallest of the three.**

  **The exposure-matched null.** A passive QQQ line held at the canonical's own
  rolling realised beta lagged one session, rebalanced daily and charged the identical
  cost model, returns 0.273354 annualised at a
  naive Sharpe of 1.108581 and a Lo-corrected
  Sharpe of 1.300043, placing
  6 of thirteen on the naive
  metric and 8 of thirteen on the
  Lo-corrected metric. Reported as measured, with no adoption and no recommendation.

- **8.7 amended again (session 21, 2026-08-20), the deflated Sharpe REMOVED.** The
  statistic assumes every trial has true Sharpe zero while the grid's cross-sectional
  naive mean is 0.6199013071365644, so the null is misspecified at every N. The
  incoherence is visible at the participation-ratio count, where session 20's expected
  maximum falls below the mean of the draws it maximises over. **Removed on the
  misspecified null rather than on an unfavourable result.** Effective N is retained
  as its own finding under 9.28, since it is the reason for the removal.

  **The recentred comparison replaces it.** Against the grid's own cross-sectional
  distribution the canonical's naive Sharpe sits
  1.0425 standard
  deviations above the grid mean at the
  89.28 percentile. Two
  correlation-accounting methods are reported so the choice is visible. The empirical
  method needs no adjustment, since the grid's own distribution already embeds the
  correlation. The effective-count method compares the canonical's z against the
  expected maximum z of that many independent draws, and **the canonical exceeds it
  only at the participation-ratio count and at none of the other three.** The two
  methods disagree, which is why both are reported.

- **9.35 the degradation slope REMOVED (session 21, 2026-08-20).** No valid null
  exists for it. Session 19.6's null destroyed the common time structure every
  specification shares, and session 20's phase G, which would have run the corrected
  construction, was blocked on memory and remains unrun. The statistic is removed
  rather than carried unresolved.

- **9.36 the session 19.5 window strip WITHDRAWN (session 21, 2026-08-20).** The
  strip compared a nested strategy against re-initialised benchmarks, since the
  strategy was built once through run(sig["rows"]) and sliced while each benchmark
  line was rebuilt per arm through LINES[ln][0](o2o, sig["rows"], i0). Seven of the
  eleven benchmark lines carry state and are therefore affected by re-entry rather
  than only repriced, so the rank comparison across arms is not like for like. The
  strip is withdrawn and 9.16's corrected sentence stands as the record of what it
  reported.

- **9.37 the Lo q as an unregistered parameter (session 21, 2026-08-20).** q is a
  Python default at scripts/s13_backtest.py:609, on no specification-curve axis and in
  no grid axis. Session 20's D1 swept it and found nine of twelve ladder rows changing
  rank and nine of twelve carrying a Lo factor inside their own no-autocorrelation
  null. **Its status is neither a searched axis nor outside the degrees-of-freedom
  census**, since it was never varied when any reported figure was selected, and it
  is recorded as discovered post hoc.

- **9.38 gate C of session 20 UNRESOLVED, with a defect in the gate itself (session
  21, 2026-08-20).** The gate required both randomization nulls to clear p below 0.001
  on the designated cell, and the timing-shuffle null on annualised return returned
  p equal to 0.001. **At the registered 1,000 draws, clearing p below 0.001 requires
  zero exceedances, so the gate turns on a single draw.** That is a defect in the gate
  specification rather than a property of the strategy. The outcome is recorded as
  unresolved pending a re-run at a higher replication count, and no null is re-run in
  this session.

  **8.2 remains open**, being whether the Lo-corrected Sharpe stays headline, with
  9.37's measurement recorded as its grounds.
