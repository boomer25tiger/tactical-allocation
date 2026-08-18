# DECISIONS v3 — the register as of session 12.5

Reissued 2026-08-18 by session 12.5, replacing the stale v2 (archived as
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
- **2.7 — closed, REVERSED TWICE, final form OPEN at the band level
  (history).** (i) Original: validate synthetics against benchmark
  indices, banded by exposure class. (ii) Session 09 measured index-level
  validation impossible for six funds (indices gated at every resolution;
  SMH 19.3% max divergence from PHLX) → **revised to validate against the
  real fund's frozen price history**, bands unchanged. (iii) Session 10
  exposed the equity band as near-circular (the objective must be proxied
  by the same underlying the synthetic builds on; objTE equalled synthetic
  TE to two decimals; 12/12 "passed" a band that cannot fail). (iv)
  Session 11 found no issuer-published tracking error exists against the
  levered daily objective. **A two-tier stipulated band is PROPOSED at the
  end of session 12's report (Tier 1 exact underlying: corr ≥ 0.98 and
  |ann TD| ≤ 2.0%; Tier 2 approximate: ≥ 0.95 and ≤ 4.0%) — awaiting
  confirmation, not written to config, not applied.** [A]
- **2.8 — closed.** All-synthetic is the primary arm; realized-instrument
  is the comparison arm (the implementability check). Neither has run.
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
- **4.4 — closed.** The base sweep above; cost is a headline axis (105
  signal transitions/yr, median holding one session — session 07).
- **4.6 — reopened.** Truncation reintroduces the size dependence
  fractional sizing removed; cannot resolve before a first result exists.
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
- **5.6 / 5.7 — open.** Breadth and concentration diagnostics: defined for
  the backtest session's diagnostics; no values yet.

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
- **7.10 — closed.** 218,700 specifications; validate() pins
  len(SMA_LONG_GRID) × len(CRASH_THRESHOLD_GRID) ×
  GRID_UNREPRESENTED_AXES_CARDINALITY (10,935) — axes not yet represented
  as tuples must divide out of the remainder when added.
- **7.14 — open.** Sub-period definitions for the backtest report.

## 8. Evaluation (not yet run)

- **8.1 — closed.** Risk-free is DTB3 (`RISK_FREE_SERIES`), distinct from
  financing constants.
- **8.2 — closed.** Lo-corrected Sharpe as headline beside the naive one.
- **8.8 / 8.9 / 8.10 — closed (design).** Benchmark ladder (buy-and-hold
  QQQ, TQQQ, vol-targeted QQQ, one fast naive rival, each sleeve
  standalone), block-bootstrap timing-shuffle nulls plus a turnover-
  matched switching null at 105/yr, 1,000 draws, identical cost model on
  every line; ensemble-vs-best-sleeve disclosed post-hoc into the
  Romano-Wolf family. Nothing executed.
- **9.8 — closed.** Implementation dimensions run at canonical parameters,
  not crossed into the grid (slippage base sweep, SMH accrual arm).
- **9.10 — closed.** Assumption-based closures must carry provenance —
  the [A] flags in this register.

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

## Open decisions with blockers

- **2.7 band** — proposed two-tier stipulation awaits user confirmation
  (end of session 12 report).
- **4.6 sizing size-dependence** — blocked on a first backtest result.
- **5.6 / 5.7** — computed in the backtest session.
- **6.13 / 6.14 orderings** — measurements complete; closure is a register
  call.
- **7.14 sub-periods** — needed by the backtest report.
- **SVIX/UVIX representation residual** — validated only against exchange
  closes (+7.5–8.9%/yr residual of the close-timing class); issuer NAV
  unobtainable at bounded effort.
