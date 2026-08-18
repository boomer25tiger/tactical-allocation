# Critical path

Decisions that change the return series the backtest produces. Everything in
DECISIONS-OPEN-v2.md not listed here is either closed as a consequence of an
earlier choice, answerable by measurement, a sensitivity arm that runs regardless,
or governance that can be settled after the model runs.

31 items.

---

## Part 1. Closed as consequence

Recorded so a later reader does not reopen them.

| # | Closed by |
|---|---|
| 3.2 KMLM fallback | KFA MLM Index carries history from 1988, so no unready period exists and the fallback branch is unreachable |
| 3.3 Fallback sensitivity arms | Moot with 3.2 |
| 3.4 SVXY leverage change | All-synthetic construction makes the multiple a schedule entry rather than a price-series break |
| 3.5 UVXY leverage change | Same |
| 3.6 SVXY to SVIX splice | Both are the same construction at different stated multiples, so no splice occurs |
| 3.7 XIV survivorship | Synthetic short volatility has no survivorship, being modelled rather than listed |
| 6.20 PSQ and SH redundancy | RSI is scale-invariant under constant leverage and inverts under negative leverage, so RSI(PSQ) is approximately 100 minus RSI(QQQ). Established analytically |
| 6.18 T11 bear sub-model duplication | Keep as supplied, separation rate is a reported diagnostic rather than a design choice |
| 6.14 Dip ladder ordering | As supplied, joint firing distribution is a reported diagnostic |
| 5.6 Sleeve count | Keep four, effective breadth is a reported diagnostic |

---

## Part 2. Critical path

### A. Sample and construction (7)

| # | Decision | Options |
|---|---|---|
| 2.9 | Sample start | Mid-2004 at VX inception, or 2006 for VX liquidity. Gated by the 2.18 inspection |
| 2.12 | Index total return source per fund | Direct index total return where obtainable, or ETF proxy with per-date expense add-back. Decide the rule and the fallback |
| 2.14 | Financing spread specification | Constant fitted, rolling window, or piecewise with a breakpoint at the LIBOR transition |
| 2.7 | Validation pass thresholds | Two levels, anchored to real-fund tracking error and to measured strategy perturbation tolerance. Bands differ by exposure class |
| 3.11 | Per-fund multiple and benchmark schedule | Dated schedule from 497 filings, including the Direxion 31 March 2020 change and any benchmark index changes |
| 3.8 | LABU | Reconstruct from XBI at 3x with a 2006 start for that branch, or drop the rung |
| 3.9 | QQQE | Keep as listed with a 2012 start for the branches using it, reconstruct from an equal-weight NDX series, or drop from the panel |

### B. Execution (8)

| # | Decision | Options |
|---|---|---|
| 4.1 | Timing | Signal at close T with fill at close T+1, or signal at close T with fill at open T+1 |
| 4.2 | Fill price | Official print, or modelled auction price |
| 4.3 | Slippage schedule | Per-instrument basis points, fixed or scaling with realized volatility |
| 4.4 | Slippage sweep range | Pre-registered bounds and step |
| 4.5 | Commission plan | IBKR Fixed at 0.005 per share with 1.00 minimum and 1 percent cap, or Tiered at 0.0035 plus pass-through |
| 4.6 | Starting NAV | Point value plus sweep range, since the per-order minimum makes results size-dependent |
| 4.7 | Share sizing | Integer truncation, integer rounding, or fractional |
| 1.9 | Missing bar handling | Forward fill, drop day, or treat instrument as unavailable |

### C. Portfolio construction (5)

| # | Decision | Options |
|---|---|---|
| 5.1 | State-change gate placement | Per-sleeve short-circuit before summation, or evaluate on the summed target |
| 5.2 | Rebalance policy | Drift permitted while labels persist, or calendar reset to equal sleeve weight |
| 5.3 | Gross cap behavior | Proportional truncation, ordered truncation, or no cap |
| 5.4 | Sleeve budget | Equal 25 percent, or volatility-scaled |
| 5.5 | Cash convention on empty sleeve | Zero return, or bill total return |

### D. Signal specification (8)

| # | Decision | Options |
|---|---|---|
| 3.1 | Specification level | Exposure targets mapped to instruments at time T, or literal tickers |
| 6.1 | RSI period structure | Single tied period, three periods tied by function (exhaustion, dip, relative strength), or three tied by asset class |
| 6.7 | Vote threshold | Simple majority, unanimity, or swept only |
| 6.8 | Vote membership | Current four, or a set with a non-equity leg added given that SOXL duplicates SMH |
| 6.9 | Overbought panel membership | S1 eleven names and T11 five names as supplied, or a reduced panel after removing leveraged duplicates |
| 6.11 | Crash quantile estimation window | Length in trading days, and whether expanding or rolling |
| 6.17 | T11 graded band reading | Maximum RSI across the panel, or the specific name that crossed first |
| 6.22 | Two-tier scope | Which overbought branches receive the graded band |

### E. Evaluation structure (3)

| # | Decision | Options |
|---|---|---|
| 8.8 | Benchmark ladder | Which rungs. Candidates are buy-and-hold QQQ, buy-and-hold TQQQ, 60/40, vol-targeted QQQ at matched exposure, 12-month TSMOM on QQQ, random allocation at matched turnover and leverage |
| 9.8 | Specification curve scope | Which implementation decisions enter the curve as dimensions, and the resulting combination count |
| 7.14 | Sub-period definition | Block count and boundaries for temporal stability |

---

## Part 3. Deferred

Answerable after the model runs, or by measurement, or running regardless.

Measurement-answerable: 1.12, 2.18, 2.20, 6.19 (follows 6.1).
Sensitivity arms that run regardless: 4.8, 4.9, 6.13, 6.15, 6.16, 7.12, 7.13, 8.2, 8.4, 8.5, 8.11, 8.12.
Optional extensions: 3.10 VIX term structure arm, 7.11 CSCV adaptive arm.
Mechanical: 2.11, 2.15, 8.1, 8.9, 8.13, 8.14.
Governance, settle before freeze but not blocking implementation: 1.8, 9.1, 9.2, 9.4, 9.7, 9.9, 9.10, 9.5, 9.6, 8.10.

---

## Dependency order

3.1 first. Choosing exposure targets converts sections A and D from instrument
questions into mapping questions and reduces 3.8, 3.9, and 3.11 to schedule
lookups.

2.9 next, gated by the 2.18 inspection, since sample start determines which
branches have data and therefore constrains 3.8 and 3.9.

4.1 next, since execution timing determines 4.2, 4.8, and the sizing path, and
determines whether the synthetic leveraged reconstruction is exact or requires an
intraday leverage model.

Section C is independent of everything above and can be settled in parallel.

Section D after 3.1 and 6.1, since RSI period structure determines 6.19 and the
grid size.

Section E last, since 9.8 depends on how many items in sections B and C resolve
to a single value rather than to a pair worth curving.
