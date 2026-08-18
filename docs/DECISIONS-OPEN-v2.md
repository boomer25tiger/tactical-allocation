# Open decision register, v2

Supersedes DECISIONS-OPEN.md. Section 1 records decisions closed since v1.
Section 2 onward lists what remains. New items added during discussion are
numbered continuing from the v1 scheme.

---

# Part 1. Closed

| # | Decision | Value fixed |
|---|---|---|
| 0.1 | Primary hypothesis | Strategy thesis as stated. Equity momentum in technology and semiconductors harvested aggressively in constructive regimes, with RSI exhaustion, trend breaks, and cross-asset relative strength rotating exposure into volatility, inverse equity, bonds, cash substitutes, or managed futures proxies |
| 0.2 | Deliverable | Fully backtested strategy at QR standard, five-page paper plus repo |
| 0.3 | Project A stop note | Dropped |
| 1.1 | Pull freeze protocol | Pull once to parquet, SHA-256, record pull date and yfinance version in SPEC, never re-pull |
| 1.2 | Return basis for signals | Total return |
| 1.3 | Return basis for accumulation | Total return |
| 1.4 | Adjustment convention | Back-adjusted, equivalent to point-in-time under total return since both indicators are scale-invariant. Two-path structure required, adjusted total return for signals and returns, raw close retained for share counts and commission |
| 1.5 | Adjusted open derivation | `AdjOpen = Open × (AdjClose / Close)`, verified against raw open-to-close ratio. Pull with `auto_adjust=False`, `actions=True` |
| 1.6 | RSI smoothing | Wilder, alpha equal 1/n |
| 1.7 | Cross-check source | Stooq at 500 ticker-days |
| 1.10 | Early close and half-day | Include |
| 1.11 | Reinvestment timing | Assume reinvestment at ex-date close, disclose as assumption, no lag modelled |
| 2.1 | Synthetic ETP reconstruction | Build, empirically, replicating current fund construction as closely as available data permits |
| 2.3 | Volatility source | CBOE VX settlement files, constant-maturity 30-day from front two contracts weighted by days to expiry |
| 2.4 | Financing and collateral rate | FRED DFF everywhere financing or collateral yield is required |
| 2.6 | Anti-beta leg | AQR published daily BAB factor, BTAL as validation arm |
| 2.16 | Residual injection | Deterministic as primary, conditional on 2.21 passing |
| 2.21 | Residual validation run | Run on the overlap window. Canonical parameters three ways, real fund returns, deterministic synthetic, stochastic synthetic at 100 draws. Compare Sharpe, turnover, signal transition count |
| 6.1 | Canonical RSI period | 14 |
| 6.2 | Canonical overbought tier one | 70 |
| 6.3 | Canonical overbought tier two | 80 |
| 6.4 | Canonical oversold | 30, single tier |
| 6.5 | Canonical long SMA | 200 |
| 6.6 | Canonical short SMA | 20 |
| 6.7 | Vote threshold | Simple majority |
| 6.10 | Crash threshold | Rolling 5th percentile of trailing 60-day QQQ total returns |
| 6.21 | Two-tier structure | Retained |
| 7.1 | Tying scheme | Eight tied dimensions |
| 7.2 to 7.9 | Grid ranges | As specified in v1 |
| 7.10 | Full cross | 50,625 specifications, confirmed |
| 8.6 | PSR | Headline canonical specification, threshold set to benchmark Sharpe rather than zero |
| 8.7 | DSR | Grid maximum only, N equal to 50,625 |
| 9.3 | Methods distinction language | Explicit statement required that the grid characterizes rather than selects |

Note on 6.1 through 6.7. Fixed by general acceptance of the canonical set rather
than item by item. Flagged for review before the freeze.

---

# Part 2. Open

## 1. Data acquisition

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 1.8 | Reverse split outlier bound | Absolute single-day adjusted return threshold triggering issuer cross-check | 50 percent | No |
| 1.9 | Missing bar handling | Forward fill, drop day, or treat instrument as unavailable | Unavailable, never forward fill | Yes |
| 1.12 | Distribution coverage diagnostic | Compare cumulative adjusted return against price return plus summed distributions per instrument, with a tolerance | Run, tolerance to be set | No |
| 1.13 | Split-and-distribution same-date handling | Factor ordering is ambiguous, inspect individually or apply a fixed convention | Inspect, cases are rare | No |

## 2. Sample construction and synthetics

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 2.2 | Which exposures reconstructed | Leveraged equity, long volatility, short volatility, trend, anti-beta | All five | Yes |
| 2.5 | Trend leg construction | Constructed futures TSMOM, published managed futures index, or KMLM only | Constructed TSMOM | Yes |
| 2.7 | Synthetic validation pass threshold | Daily return correlation and rolling cumulative divergence bounds | Correlation above 0.99, divergence bound to be set | Yes |
| 2.8 | Tier structure | Tier 1 synthetic from 2004, tier 2 listed from 2010, tier 3 listed from 2022 | All three, tier 1 headline | Yes |
| 2.9 | Sample start | Mid-2004 at VX inception, or 2006 for VX liquidity | Pending 2.18 | Yes |
| 2.10 | Holdout boundary | Proposed 1 January 2021 | Confirm or revise | Yes |
| 2.11 | Warm-up length | Resolved in principle, indicators estimated from underlying index history so warm-up consumes no tradeable sample. Exact per-indicator start dates still to be stated | State per indicator | Yes |
| 2.12 | Index total return source per fund | Direct index total return, or ETF proxy with expense add-back | Direct where available, add-back rule where not | Yes |
| 2.13 | Expense ratio schedule | Per-fund per-date from 497 and N-1A filings | Required | Yes |
| 2.14 | Financing spread specification | Constant fitted, rolling, or piecewise with breakpoints at the LIBOR transition | Time-varying, since a constant spread understates 2008 and March 2020 | Yes |
| 2.15 | Inverse-leg borrow treatment | Absorbed in fitted spread, or modelled separately | Absorbed, with the time-varying spread carrying the stress widening | Yes |
| 2.17 | N-PORT validation | Pull actual swap notionals and terms from EDGAR 2019 onward to check the fitted spread | Run | No |
| 2.18 | VX early liquidity inspection | Determine whether 2004 to 2006 supports constant-maturity construction, and whether a wider early slippage assumption is required | Inspect before fixing 2.9 | Yes |
| 2.19 | Cash and bond substitutions pre-inception | 3-month bill total return for BIL, 1-to-3-year Treasury index for BSV, AGG for BND | As stated | Yes |
| 2.20 | SMH 2011 conversion continuity | Inspect the HOLDRS to VanEck boundary in yfinance | Inspect | Yes |

## 3. Universe

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 3.1 | Specification level | Exposure targets mapped to instruments at time T, or literal tickers | Exposure targets | Yes |
| 3.2 | KMLM fallback resolution | Reverse to risk-off, start at KMLM readiness, or replace with constructed TSMOM | Replace with constructed TSMOM, follows 2.5 | Yes |
| 3.3 | Unresolved fallback arms | Which of the other two run as sensitivity | Both | No |
| 3.4 | SVXY leverage change Feb 2018 | Scale to constant effective exposure, or splice raw | Scale, raw as sensitivity | Yes |
| 3.5 | UVXY leverage change Feb 2018 | Same | Same | Yes |
| 3.6 | SVXY to SVIX splice 2022-03-30 | Keep, drop, or replace with synthetic short volatility | Replace with synthetic | Yes |
| 3.7 | XIV survivorship | Include as a terminated instrument in the synthetic construction, or ignore | Include and disclose | No |
| 3.8 | LABU | Keep with synthetic pre-2015 from XBI, or drop | Keep with synthetic | No |
| 3.9 | QQQE | Keep in vote set, or replace | Keep | No |
| 3.10 | VIX term structure variable | Replace regime variable, add as fifth sleeve, or separate arm | Separate arm | Yes |
| 3.11 | Per-fund multiple schedule | Source dated multiples from 497 supplements, including the Direxion 31 March 2020 change affecting ten funds | Required, list not yet retrieved | Yes |

## 4. Execution

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 4.1 | Timing | Signal at close T with fill at close T+1, or fill at open T+1 | Close-to-close primary, open-to-open robustness arm | Yes |
| 4.2 | Fill price | Official print, or modelled auction price | Modelled | Yes |
| 4.3 | Slippage schedule | Per-instrument basis points scaling with realized volatility | Required, values to be set | Yes |
| 4.4 | Slippage sweep range | Pre-registered bounds | 0 to 50 basis points round-turn, anchored at 10 | Yes |
| 4.5 | Commission plan | Commission confirmed as required. Plan not fixed. IBKR Fixed at 0.005 per share with 1.00 minimum and 1 percent cap, or Tiered at 0.0035 plus pass-through | Fixed as base, Tiered as arm | Yes |
| 4.6 | Starting NAV | Per-order minimum makes results size-dependent | 100,000 with a sweep across 25k to 10M | Yes |
| 4.7 | Share sizing | Integer truncation, integer rounding, or fractional | Fractional, integer as sensitivity | Yes |
| 4.8 | Sizing reference price | Close T, or modelled fill price | Close T, with realized-minus-target weight reported | Yes |
| 4.9 | Margin financing on gross above 100 percent | Applicable or not | Resolve with 5.3 | No |

## 5. Portfolio construction and merge

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 5.1 | State-change gate placement | Per-sleeve short-circuit before summation, or evaluate on summed target | Summed target, otherwise shared tickers hold stale weights | Yes |
| 5.2 | Rebalance policy | Drift permitted, or calendar reset | Calendar monthly primary, drift as arm | Yes |
| 5.3 | Gross cap behavior | Proportional truncation, ordered truncation, or no cap | Proportional | Yes |
| 5.4 | Sleeve budget | Equal 25 percent, or volatility-scaled | Equal 25 percent with realized weights reported | Yes |
| 5.5 | Cash convention on empty sleeve | Zero return, or bill total return | Bill total return | Yes |
| 5.6 | Sleeve count | Keep four, or consolidate on measured collinearity | Keep four, report effective breadth | No |

## 6. Signal specification

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 6.8 | Vote membership set | Current four, or add a non-equity leg | Add a non-equity leg, since SOXL and SMH votes are near-duplicates | Yes |
| 6.9 | Overbought panel membership | S1 eleven names, T11 five names, or a reduced common panel | Reduce, report firing rate against original | Yes |
| 6.11 | Crash quantile estimation window | 1,260 trading days expanding until available, estimated on QQQ from 1999 | 1,260 | Yes |
| 6.12 | Crash branch before window fills | Unavailable, or false | Unavailable, recorded distinctly | Yes |
| 6.13 | Cascade ordering | As supplied, or swept | As supplied, report reach rate per step | Yes |
| 6.14 | Dip ladder ordering | As supplied | As supplied, report joint firing distribution | No |
| 6.15 | TQQQ signals TECL crossover | Keep, fix, or keep with matched arm | Keep with matched arm | Yes |
| 6.16 | S2 trend filter series | TQQQ own price, or QQQ | TQQQ as supplied, QQQ as matched arm | Yes |
| 6.17 | T11 graded band reading | Maximum RSI across panel, or the name that crossed first | Maximum across panel | Yes |
| 6.18 | T11 bear sub-model duplication | Keep both at 50/50, or collapse | Keep, report separation rate | No |
| 6.19 | Mismatched RSI lookbacks in bond_baller | Tie to a common period, or keep | Tie | Yes |
| 6.20 | PSQ and SH inverse redundancy | Test and replace if redundant, or keep | Test first | No |
| 6.22 | Two-tier scope | Which sleeves receive the graded band | All overbought branches | Yes |

## 7. Parameter grid

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 7.11 | Adaptive selection arm | Run CSCV walk-forward selection as a second arm, or omit | Run | Yes |
| 7.12 | Ablation pass | One parameter to canonical at a time, ranked | Run | No |
| 7.13 | Branch ablation | One branch removed at a time, ranked | Run | No |
| 7.14 | Sub-period definition for temporal stability | Non-overlapping blocks, count and boundaries | To be set | Yes |

## 8. Metrics and inference

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 8.1 | Risk-free source for metrics | FRED DTB3, or DFF for consistency with financing | DTB3, distinct variable name from the financing rate | Yes |
| 8.2 | Annualization | Naive sqrt(252), Lo-corrected, or both | Both, corrected as headline | Yes |
| 8.3 | Alpha factor model | Market, market squared, constant-maturity VIX futures excess, duration excess | As stated | Yes |
| 8.4 | Timing regression | Treynor-Mazuy quadratic, or Henriksson-Merton option form | Treynor-Mazuy primary, Henriksson-Merton arm | Yes |
| 8.5 | Second alpha regression | Against vol-targeted QQQ | Required | Yes |
| 8.8 | Benchmark ladder | Under the thesis framing the ladder must isolate both halves of the claim. Candidates are buy-and-hold QQQ, buy-and-hold TQQQ, 60/40, vol-targeted QQQ at matched exposure, 12-month TSMOM on QQQ, random allocation at matched turnover and leverage | All six | Yes |
| 8.9 | Block bootstrap block length | From measured holding period distribution | As stated | Yes |
| 8.10 | Romano-Wolf family definition | Which comparisons enter the family | To be enumerated | Yes |
| 8.11 | Manipulation-proof measure | Include, or omit | Include | No |
| 8.12 | Beta reporting | Full-sample point, rolling 63-day series, or both | Both, plus fraction of days with negative beta | No |
| 8.13 | Gross and net reporting | Net as headline at every rung | As stated | Yes |
| 8.14 | Headline metric order | Sharpe, alpha, then PSR, with DSR reserved for the grid maximum | Confirm | No |

## 9. Governance

| # | Decision | Options | Rec | Blocking |
|---|---|---|---|---|
| 9.1 | Null abstract coverage | Minimum three, covering thesis failure against the benchmark ladder, synthetic validation failure, and data feasibility failure | Three at minimum | Yes |
| 9.2 | Test family enumeration | Stated count in SPEC before any run | Required | Yes |
| 9.4 | Provenance registry | Table with value, source, classification, treatment | Required deliverable | Yes |
| 9.5 | Session architecture | Narrowly scoped sessions with explicit stop conditions, outputs to disk | As stated | No |
| 9.6 | Repo structure and public timing | Private until paper complete, or public from start | Private until complete | No |
| 9.7 | SPEC freeze date | Fixed before any estimation | Required | Yes |

---

# Counts

Closed: 39.
Open blocking: 56.
Open deferrable: 18.
Open total: 74.

# Order of resolution

3.1 first, since exposure-versus-ticker specification collapses much of section 3
into mapping rules. 2.5 next, since the trend leg determines 3.2. Then 2.18 and
2.20, both inspections that gate 2.9 and the vote set in 6.8. Sections 4 and 5
are independent and can proceed in parallel. Section 6 depends on 3.1. Section 8
depends on the benchmark ladder in 8.8. Section 9 last.

Items 1.12, 2.18, 2.20, 6.9, 6.18, and 6.20 are answerable by measurement rather
than judgment. A pre-spec diagnostic session computing firing rates, joint
distributions, vote agreement, and data continuity, with no performance statistic
computed and no returns accumulated, would close them without contaminating the
freeze.
