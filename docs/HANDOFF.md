# Project handoff

Paste this at the start of the new conversation. Written 2026-08-17.
Supersedes DECISIONS-OPEN.md, DECISIONS-OPEN-v2.md, and CRITICAL-PATH.md.

---

## 1. What the project is

A daily multi-model tactical allocation strategy, four sleeves at equal 25 percent
budgets, traded on US equity index and sector ETFs, leveraged long and inverse
ETFs, volatility ETPs, Treasury and aggregate bond ETFs, and defensive cash
substitutes.

**Thesis, fixed as decision 0.1.** Equity momentum in technology and semiconductors
can be harvested aggressively in constructive regimes, while RSI based exhaustion,
trend breaks, and cross asset relative strength can shift exposure into volatility,
inverse equity, bonds, cash like instruments, or managed futures proxies.

**Deliverable, fixed as decision 0.2.** A fully backtested strategy at quant
researcher standard. Five-page paper plus public repo.

**Sleeves as supplied.** S1 is a flat priority cascade on RSI. T11
(FeaverFrontrunner) is a deeper tree with a graded overbought response and a bear
sub-model containing `_t11_bond_baller` and `_t11_feaver_bear`. S2 (HolyGrail) is
gated on TQQQ's own long moving average. S3 (DailyRegimeRotation) uses four
boolean SMA votes plus an overbought screen.

**Repo.** `tactical-allocation`, local. Nothing committed.

---

## 2. Session status

| Session | Purpose | Status |
|---|---|---|
| 00A | VX feasibility, listing coverage, roll, spread proxy | Complete, report read |
| 00B | Roll methodology, VIXY validation, timestamp | Complete, report read |
| 00C | Equity panel, indicator relationships, continuity | Complete, report read |
| 00D | Signal-source audit, warm-up availability | Running, report not yet read |
| 00E | Panel truncation, SMH basis, vote leave-one-out | Prompt written, not yet run |

Session prompts follow a fixed pattern. Scaffold, task, explicit prohibition on
computing any return or performance statistic before SPEC freeze, numbered steps
with named output files, stop condition, no commit.

---

## 3. Closed decisions

### Framing
- **0.1** Thesis as stated above
- **0.2** Fully backtested strategy, QR standard, five-page paper plus repo
- **0.3** Project A stop note dropped

### Data
- **1.1** Pull once to parquet, SHA-256, record pull date and yfinance version, never re-pull. Amended: pulls execute after the settled close of the prior session
- **1.2** Total return for signals
- **1.3** Total return for accumulation
- **1.4** Back-adjusted, equivalent to point-in-time under total return since both indicators are scale-invariant. Two-path structure required, adjusted total return for signals and returns, raw close retained for share counts and commission
- **1.5** `AdjOpen = Open × (AdjClose / Close)`, verified against raw open-to-close ratio. Pull with `auto_adjust=False`, `actions=True`
- **1.6** RSI uses Wilder smoothing, alpha equal 1/n
- **1.7** Stooq cross-check at 500 ticker-days
- **1.10** Early closes and half-days included
- **1.11** Reinvestment assumed at ex-date close, disclosed as assumption
- **1.12** Closed by measurement. No ticker exceeds 4.05 bp per annum against a 10 bp threshold
- **1.13** Same-date split and distribution cases inspected individually
- **1.14** Truncate all panels to 2026-08-14, re-hash, retain original hashes

### Sample and construction
- **2.1** Build synthetics empirically, replicating current fund construction
- **2.2** All five exposures reconstructed from underlying returns across the test period
- **2.3** CBOE VX settlement files, 30-day constant maturity
- **2.4** FRED DFF as base rate wherever financing or collateral yield is required
- **2.5** KFA MLM Index series used directly for the trend leg. History from 1988. Methodology break at 2005-01-01 recorded as a schedule entry
- **2.6** AQR published daily BAB factor, BTAL as validation arm
- **2.7** Three validation bands by exposure class. Volatility legs, correlation against issuer NAV at or above 0.995 yearly and max rolling 252-session divergence at or below 0.10. Leveraged equity, deviation no greater than 1.5x the real fund's own tracking error against its stated objective. Trend and anti-beta, correlation at or above 0.99 with no divergence bound. Signal fidelity common across classes at 97 percent identical allocation output, pre-registered as convention and flagged as unmeasured
- **2.8** All-synthetic primary, realized-instrument arm as implementability check
- **2.9** Sample start 2007-01-01
- **2.10** Holdout boundary August 2021
- **2.13** Per-fund per-date expense schedule from 497 and N-1A filings
- **2.16** Deterministic residual injection, conditional on 2.21 passing
- **2.17** N-PORT validation run
- **2.19** Pre-inception substitutions. 3-month bill total return for BIL, 1-to-3-year Treasury index for BSV, AGG for BND
- **2.20** Closed by measurement. SMH is stitched with no price discontinuity
- **2.21** Residual validation run on the overlap window, three ways, comparing Sharpe, turnover, signal transition count
- **2.22** Construction B, the S&P roll. Interpolation discarded entirely
- **2.23** Synthetic targets NAV rather than market price. NAV-to-market deviation feeds slippage

### Universe
- **3.1** Exposure targets, defined as an ordered pair of underlying index and signed multiple, plus named non-index exposures for anti-beta, trend, and cash. Mapping table resolves to whichever instrument the strategy would actually have traded on that date
- **3.2** Closed by 2.5. KFA MLM history removes the KMLM unready period entirely
- **3.3** Moot with 3.2
- **3.4, 3.5** Closed by all-synthetic construction. Multiple changes become schedule entries
- **3.6** Closed. No splice occurs, both are the same construction at different multiples
- **3.7** Closed. Synthetic short volatility has no survivorship

### Portfolio construction, section complete
- **5.1** Global concatenated label across all four sleeves, all four `_weights()` calls execute, equality test on the joint string, short-circuit before summation. Rounding precision in the label must be stated, since it sets an implicit no-trade band
- **5.2** Drift permitted, reset on label transition only. No calendar reset. The 25 percent cap binds on targets at the moment they are set, and realized weight moves between transitions. Sleeve budget described as a target cap rather than a portfolio constraint
- **5.3** Gross fixed at 100 percent maximum, no portfolio leverage. Proportional truncation if it binds. 4.9 closed as not applicable
- **5.4** Equal 25 percent per sleeve
- **5.5** Idle sleeve cash accrues DTB3. BIL as an allocated position accrues BIL total return with pre-2007 substitution per 2.19
- **5.6** Four sleeves retained, effective breadth reported
- **5.7** Four concentration metrics. Effective number of constituents (1/HHI) on tickers and on underlyings. Effective number of minimum-torsion bets, Meucci et al. 2015, using minimum-torsion rather than PCA. Effective market exposure as sum of weight times signed multiple. Maximum single-ticker and single-underlying weight with top-three sum. All reported as daily series plus distributions conditional on drawdown quintile, target and realized both
- **5.8** Concentration cap sweep at 40, 50, 60, 75 percent. Hybrid truncation with pro-rata absorption. Each contributing sleeve absorbs its share of the excess in proportion to its contribution, then redistributes internally if it holds other positions, or routes to DTB3 cash if it holds only the capped position. No cap is primary

### Signals
- **6.1** Three RSI periods tied by function (exhaustion, dip, relative strength), each swept over 7, 14, 28. Canonical headline sets all three to 14. Geometric spacing chosen so the grid spans a factor of four. Lower bound of 7 justified by RSI instability below roughly 5
- **6.2** Overbought tier one at 70
- **6.3** Overbought tier two at 80
- **6.4** Oversold at 30, single tier
- **6.5** Long SMA at 200
- **6.6** Short SMA at 20
- **6.10** Crash threshold as rolling 5th percentile of trailing 60-day QQQ total returns
- **6.19** Closed with 6.1. The bond_baller RSI(20) against RSI(60) mismatch resolves into the relative-strength period applied to both sides
- **6.20** Closed by measurement
- **6.21** Two-tier structure retained

### Parameter grid
- **7.1** Eight tied dimensions
- **7.2 to 7.9** Grid ranges. RSI period 7/14/28 across three function-tied periods. Overbought tier one 60/65/70/75/80. Tier two offset 5/10/15. Oversold 20/25/30/35/40. Long SMA 50/100/150/200/250. Short SMA 10/20/50. Crash quantile 1st/5th/10th. Vote threshold 2/3/4
- **7.10** Full cross confirmed at 273,375 specifications after the RSI period change

### Metrics
- **8.6** PSR for the canonical headline, threshold set to benchmark Sharpe rather than zero
- **8.7** DSR for the grid maximum only, N equal to grid size

### Governance
- **9.3** Methods section must state explicitly that the grid characterizes rather than selects. Draft language exists

---

## 4. Open decisions

### Awaiting session results
- **2.11** Warm-up per indicator. Expected moot pending 00D, since no sleeve computes an indicator on a volatility instrument. Equity warm-up is 292 sessions, being SMA 250 plus a 42-session buffer
- **3.12** SMH pre-2013 total return handling. Deferred to measurement in 00E. SMH records zero distributions across the HOLDRS era, first on 2012-12-24, so total return equals price return for six of twenty years
- **6.7** Vote threshold. Blocked on the 00E leave-one-out threshold clarification

### Informed by measurement, ready to decide
- **6.8** Vote membership. Recommendation is keep SPY, QQQ, SMH, SOXL as supplied. See section 5 for what the measurement showed
- **6.9** Overbought panel membership. S1 eleven names carry 1.77 effective independent signals, T11 five names carry 1.39. Window mismatch between the two panels blocks direct comparison
- **6.16** S2 trend filter series. Recommendation is TQQQ as supplied with QQQ as matched arm, now supported by measurement

### Section B, execution, entirely open and blocked on 4.1
- **4.1** Timing. Close-to-close or open-to-open. Recommendation is close-to-close primary with open-to-open as a specification-curve dimension, on the grounds that the synthetic reconstruction is exact under close-to-close and requires an intraday leverage model under open-to-open
- **4.2** Fill price. Official print or modelled auction price
- **4.3** Slippage schedule. Per-instrument basis points, fixed or scaling with realized volatility. The 00A spread proxy was flagged as not a bid-ask measure and cannot anchor this. The 2.23 NAV-to-market deviation is a measured input
- **4.4** Slippage sweep range. Proposed 0 to 50 basis points round-turn, anchored at 10 per Zarattini 2025
- **4.5** Commission plan. IBKR Fixed at 0.005 per share with 1.00 minimum and 1 percent cap, or Tiered at 0.0035 plus pass-through. Note that IBKR Lite's commission-free treatment does not apply, since every order is market-on-open or market-on-close
- **4.6** Starting NAV, point value plus sweep, since the per-order minimum makes results size-dependent
- **4.7** Share sizing. Integer truncation, integer rounding, or fractional
- **4.8** Sizing reference price. Follows 4.1
- **1.8** Reverse split outlier bound
- **1.9** Missing bar handling

### Remaining section A and universe items
- **2.12** Index total return source per fund, with proxy fee add-back rule
- **2.14** Financing spread specification. Recommendation is time-varying, since a constant spread understates 2008 and March 2020
- **2.15** Inverse-leg borrow treatment, absorbed or modelled separately
- **3.8** LABU. XBI starts 2006-02-06, giving under 292 sessions before the 2007-01-01 start
- **3.9** QQQE. Listed from 2012-03-21, no pre-2007 history
- **3.10** VIX term structure variable, as replacement, fifth sleeve, or separate arm. Recommendation is separate arm
- **3.11** Per-fund multiple and benchmark schedule from 497 filings, including the Direxion change effective after close 2020-03-31 affecting ten funds. List not yet retrieved

### Remaining section D
- **6.11** Crash quantile estimation window. Proposed 1,260 sessions expanding, estimated on QQQ from 1999
- **6.12** Crash branch treatment before the window fills. Unavailable or false
- **6.13** Cascade ordering. As supplied, with reach rate per step reported
- **6.15** TQQQ-signals-TECL crossover. Keep with matched arm
- **6.17** T11 graded band reading. Maximum RSI across panel, or the name that crossed first
- **6.22** Two-tier scope, which overbought branches receive the graded band

### Section E and governance
- **7.11** CSCV adaptive selection arm
- **7.14** Sub-period definition for temporal stability
- **8.1** Risk-free source. DTB3 recommended, distinct variable name from the financing rate
- **8.2** Annualization, naive and Lo-corrected, corrected as headline
- **8.3** Alpha factor model. Market, market squared, constant-maturity VIX futures excess, duration excess
- **8.4** Timing regression. Treynor-Mazuy primary, Henriksson-Merton arm
- **8.5** Second alpha regression against vol-targeted QQQ
- **8.8** Benchmark ladder. Candidates are buy-and-hold QQQ, buy-and-hold TQQQ, 60/40, vol-targeted QQQ at matched exposure, 12-month TSMOM on QQQ, random allocation at matched turnover and leverage. Buy-and-hold TQQQ is required because the thesis claims rotation improves on aggressive exposure
- **8.9** Block bootstrap block length from measured holding period distribution
- **8.10** Romano-Wolf family definition
- **8.14** Headline metric order. Sharpe, alpha, then PSR, with DSR reserved for the grid maximum
- **9.1** Null abstracts, minimum three
- **9.2** Test family enumeration
- **9.4** Provenance registry with value, source, classification, treatment
- **9.7** SPEC freeze date
- **9.8** Specification curve scope. Must run at canonical parameters rather than crossed against the full grid, since layering implementation dimensions on 273,375 is infeasible
- **9.9** Diagnostic prohibition definition
- **9.10** Provenance flag for decisions reasoned from mechanism rather than measured

---

## 5. Measured findings

### VX construction, sessions 00A and 00B
- Construction B, the S&P roll, reproduces VIXY NAV at 0.99999 or better in nine of sixteen years, never below 0.99926. Rolling annual divergence stays within 0.0012 to 0.0500
- Interpolation is not a tradeable series. Its daily change mixes price move with weight change. Rolling annual divergence against NAV reaches 2.2495 in 2020 and exceeds 0.35 every year
- B is not computable from listed contracts on 48 sessions in 2004 to 2006, last on 2006-08-18. 2004 and 2005 are unusable under B regardless, with mean realized maturity 42.42 days and 58.5 percent of sessions outside the 25 to 35 band. Expiry gaps averaged 44.3 days in 2005 against 30.3 from 2006
- VX daily settlement ran at 16:15 ET from inception until Cboe moved it to 16:00 effective 2020-10-26, documented in Cboe notice C2020092202 and CFE rule certification CFE-2020-028. Mean absolute daily difference against VIXY falls from 0.00892 to 0.00226 at the change. No signal is computed on a volatility instrument, so the mismatch affects return accumulation only, where it is faithful to what the real ETP's NAV did. Disclosed, not corrected
- The 2022 VXX divergence is issuer-specific. Barclays halted VXX creations 2022-03-14 after overissuing beyond its shelf registration, $20.8bn registered against roughly $15.2bn excess, and VXX reached a 33 percent premium to NAV. VIXY tracked the same index correctly throughout. This is the strongest available argument for synthetic over listed construction
- Term structure across the sample runs contango 83.5 percent, backwardation 16.0 percent, median absolute slope 0.0697. Most backwardated year 2008 at 47.8 percent
- VXX on yfinance returns nothing before 2018-01-25, since Yahoo serves only the iPath Series B note. VIXY runs from 2011-01-04 with no share-class break and is the correct validation target

### Equity panel, session 00C
- RSI on a long leveraged fund differs from RSI on its underlying by 0.75 to 2.85 points on average, agreeing on the 70 threshold on 96.8 to 99.2 percent of sessions. Scale-invariance holds approximately, not exactly
- RSI(inverse) equals 100 minus RSI(underlying) to 1.06 points mean absolute difference for PSQ against QQQ, 1.26 for SH against SPY, correlations 0.994 and 0.989. Threshold agreement is asymmetric, 99.5 percent at 70 against 98.1 percent at 30
- PSQ and SH are **not** redundant with each other. 4.05 points mean absolute difference, correlation 0.892, 423 disagreement sessions at threshold 30. T11's bond_baller uses both, and they carry distinct information. PSQ and SQQQ **are** near-duplicates at 0.89 points and correlation 0.996
- TQQQ and QQQ disagree on which side of the 200-session average they sit for 6.45 percent of sessions, in 84 runs, median 2 sessions, max 21. Crossovers match at median offset +1 session, only 6.5 percent simultaneous, 5th to 95th percentile spanning -26.9 to +33.7 sessions. Inside 60 sessions after a 20 percent QQQ drawdown, agreement falls from 93.6 to 87.1 percent and mean crossover offset rises from 0.86 to 11.1 sessions
- S3's vote set carries 1.66 to 1.74 effective independent votes out of four, stable across all average lengths. Vote distribution is bimodal, 66.4 percent unanimous bull and 11.7 percent unanimous bear at SMA 200
- **SOXL and SMH are the least duplicative equity pair, not the most.** At SMA 200 they agree 86.9 percent at correlation 0.709, while SPY and QQQ agree 94.5 percent at 0.789. Removing SOXL nonetheless changes the majority on only 12 of 3,935 sessions against 412 for SMH. SOXL is least correlated and nearly inert, which are different facts pointing to different remedies. Threshold treatment under removal is ambiguous and is being clarified in 00E
- Substituting TLT for SOXL raises effective independent votes to 2.29 to 2.38
- S1's eleven-name overbought panel carries 1.77 effective independent signals, T11's five-name panel 1.39. S1's disjunction fires on 29.9 percent of sessions at threshold 70 against a maximum individual rate of 10.8 percent. Sole-trigger contributions concentrate in XLP, VOX, XLY for S1 and TQQQ for T11. SPY is nearly inert in both at 0.56 and 1.92 percent
- Panel windows differ. S1's common window starts 2012-04-11 bounded by QQQE, T11's starts 2010-03-04 bounded by TQQQ. Firing rates are not measured on the same sample
- SMH is stitched across the December 2011 HOLDRS conversion with no price discontinuity and no missing sessions, but records zero distributions across the HOLDRS era, first on 2012-12-24. Median volume falls 81 percent across the boundary
- Distribution coverage passes everything. Worst ticker 4.05 bp per annum, median 0.06. The diagnostic measures internal consistency between two constructions from the same feed and cannot detect an omitted distribution, which is why the SMH defect was invisible to it

---

## 6. Corrections on record

Recorded so they are not silently reintroduced.

- **Alpha absence.** I asserted the strategy has no alpha source. Corrected at the user's instruction. The correct statement is that no alpha source has been *identified* in the specification as written, which is a claim about what can be pointed to rather than about what the data will show. The alpha question is open and gets answered by the four-factor regression, the appraisal ratio, and the comparison against the vol-targeted benchmark
- **RSI scale-invariance overextended.** The invariance argument is correct for RSI and was wrongly generalized to SMA comparisons, producing a false claim that SOXL and SMH votes are near-duplicates. SMA comparison is not scale-invariant because the leveraged path is the compounded product of tripled returns and diverges from the underlying by variance drag. Measurement confirms SOXL is the least duplicative vote
- **PSQ and SH redundancy.** Closed analytically as settled, then reopened as approximate, then closed by measurement at 1.06 to 1.26 points. Both the original claim and its qualification were right
- **Maturity as a construction criterion.** Session 00B's step 3 asked which construction holds maturity closest to 30 days. Wrong criterion. Interpolation wins on maturity and is not a held-position return. Replicability of a tradeable position is the criterion
- **Sullivan, Timmermann, White transfer.** Their result concerns standalone index timing rules and does not transfer directly to routing logic across a leveraged and volatility instrument set
- **Unverified figures used in reasoning.** Leveraged fund tracking error stated as 10 to 20 basis points daily. Price-versus-total-return gap stated as roughly 1 percent for SPY and 2 percent for XLP and VTV over 200 days. BIL ex-date described as a 35-sigma move. All are estimates, none measured
- **Composer and Quantmage provenance.** Asserted without verification in the first response

---

## 7. Working conventions

- One decision at a time. The user pushes back directly when outputs drift or overstate, and expects corrections to hold
- Design, prior-art screening, spec drafting and null abstracts are settled before a measurement session opens. Measurement runs against local files and results return as text, with every intermediate artifact written under outputs/.
- Every pre-freeze session carries an explicit prohibition on computing any return, Sharpe, allocation, or performance statistic. Counts, distributions, indicator values on single instruments, and data properties are permitted
- Sessions have explicit stop conditions and a no-commit instruction
- Parameters frozen before results. DECISIONS.md logs post-freeze changes with dates and reasoning. Null abstracts written before any result is seen. Pre-registered sensitivity grids replace parameter optimization
- Writing conventions. No em-dashes, no colons as lead-ins, no three-item sentence lists. Qualifications travel in the same sentence as the result they qualify. Neutral tone, no flattery

---

## 8. Immediate next steps

1. Read the 00D report when it returns. Closes 2.11, validates the signal-source table, reports warm-up availability against the 2007-01-01 start
2. Run 00E. Applies the 1.14 truncation, measures SMH basis for 3.12, resolves the vote leave-one-out threshold for 6.7
3. Decide the four informed section D items. 6.8, 6.9, 6.16, and 6.7 once 00E returns
4. Open section B. 4.1 gates the rest and nothing measured so far bears on it
5. Reissue the register as v3 once 00D and 00E are absorbed

**Open count trajectory.** 113 at the first enumeration, 74 at v2, roughly 55 now.
Converging rather than diverging. Worth continuing to track, since starting faster
than finishing is a known pattern to manage.
