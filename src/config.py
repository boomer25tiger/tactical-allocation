"""Single configuration module for the tactical allocation study.

Every tunable quantity lives here as a named constant carrying its decision ID
and status. No numeric parameter of the strategy may appear as a literal
anywhere else in src/.

Status vocabulary:
    closed   the decision is settled and the value is final
    open     the decision is not settled; the value is a provisional default

Session 01 note. The register on disk (docs/DECISIONS-OPEN-v2.md, last modified
2026-08-17 12:06) predates session 00A and does not carry decisions 1.14, 3.12
or 2.22. Values here come from the session 01 prompt, which governs.
"""

# ---------------------------------------------------------------------------
# Provisional configuration constants
# ---------------------------------------------------------------------------

# Decision 2.11 -- closed.
# Sessions required before any sleeve is permitted to emit a weight. The
# requirement is the maximum of the longest moving average and RSI seed
# convergence, not their sum: a moving average of length n is exactly defined
# at bar n and needs no buffer, while Wilder RSI at the grid maximum period
# of 28 carries under a tenth of a percent of seed weight by roughly bar 190
# ((27/28)^k drops below 0.001 near k = 190). max(200, ~190) = 200, plus a
# stated ten-session margin, gives 210.
WARMUP_SESSIONS = 210

# Decisions 6.11 and 6.12 -- closed as not applicable (session 04).
# The rolling-quantile crash estimator was withdrawn when 6.10 was reversed;
# nothing is estimated and nothing needs to fill. CRASH_QUANTILE_WINDOW and
# CRASH_BEFORE_WINDOW_FILLS are removed.

# Decision 2.5 -- closed.
# Daily managed-futures trend return series. Originally specified as the KFA
# MLM Index with history from 1988; no such series exists in data/ and the
# index is not obtainable without a licensing request, so 2.5 was rewritten to
# specify a daily managed-futures trend series and RYMFX was selected.
TREND_SIGNAL_SERIES = "RYMFX"

# Decision 2.5a -- closed.
# RYMFX is NAV-priced with a one-session posting lag, so a signal stamped at
# the T close reads the T-1 NAV. Applied once, at load time, in src/data.py.
TREND_SIGNAL_LAG = 1

# Decision 2.14 -- closed (session 10). Financing anchored at approximately
# 75 bp over the reference rate for swap-based LONG exposure, from session
# 09's harvest: Direxion FY2025 schedules state SOFR +28 to +99 bp with a
# median near 75. Short-side exposure is treated separately: ProShares'
# short funds RECEIVE roughly bills minus 62-77 bp, carried here as a
# haircut. Swept around the anchor. The anchor is a single-fiscal-year
# snapshot and that is disclosed wherever it is used.
FINANCING_SPREAD_BP = 75
FINANCING_SHORT_HAIRCUT_BP = 70

# Decision 4.1 -- closed, both arms required.
# "close_to_close": signal at T close, fill at T+1 close.
# "open_to_open":   signal at T close, fill at T+1 open, on AdjOpen.
EXECUTION_MODE = "close_to_close"
EXECUTION_MODES = ("close_to_close", "open_to_open")

# Decision 4.7 -- re-closed with truncation primary (session 09).
# Session 07 established that a fractional component executes against IBKR
# as principal rather than routing to the exchange closing auction, so the
# fractional portion cannot receive the official closing print by
# construction, independent of whether MOC accepts fractional quantities.
# Fractional drops to the alternative arm. Consequence: 4.6 reopens and
# cannot resolve before a first result exists, since its sweep needs
# terminal rather than starting NAV.
# "truncate":   integer share truncation, residual to sleeve cash at DTB3.
# "fractional": fractional share sizing (alternative arm).
SIZING_MODE = "truncate"
SIZING_MODES = ("fractional", "truncate")

# Decision 1.9 interior-gap treatment -- closed as "skip" (session 09).
# A missing observation is removed from the series rather than triggering a
# reseed: the return across the gap is computed from the last available
# observation, the next available session carries a multi-day return, and
# the recursion proceeds on the compressed series. Reseeding would discard
# 200 sessions of moving average for a one-day gap, which is not
# proportionate to the defect. The three affected ^NETR sessions
# (2007-02-26, 2008-10-27, 2010-07-14) are disclosed rather than corrected.
# Implemented in src/indicators.py and src/data.py; validate() pins it.
INTERIOR_GAP_TREATMENT = "skip"

# ---------------------------------------------------------------------------
# Closed strategy parameters
#
# These are settled. They are named here rather than written as literals in
# src/sleeves.py so that the grid sweep has a single place to vary them and so
# that no threshold is duplicated across call sites.
# ---------------------------------------------------------------------------

# Decision 1.6 -- closed. Wilder smoothing, alpha = 1/n, seeded with an SMA of
# the first n values. Implemented in src/indicators.py.

# Decision 6.1 -- closed. Three RSI periods tied by function. All three take 14
# under the canonical spec; the grid sweeps them at 7 and 28. The function
# split is recorded in outputs/session-01/rsi-function-mapping.md.
RSI_PERIOD_EXHAUSTION = 14
RSI_PERIOD_DIP = 14
RSI_PERIOD_RELATIVE_STRENGTH = 14

# Decision 6.2 -- closed. Overbought tier one.
OVERBOUGHT_TIER_1 = 70

# Decision 6.3 -- closed. Overbought tier two.
OVERBOUGHT_TIER_2 = 80

# Decision 6.4 -- closed. Oversold, single tier.
OVERSOLD = 30

# Decision 6.5 -- closed. Long simple moving average.
SMA_LONG = 200

# Decision 6.6 -- closed. Short simple moving average.
SMA_SHORT = 20

# Decision 6.10 -- reversed and re-closed (session 04). The rolling 5th
# percentile is withdrawn; the crash test is an absolute threshold on the
# trailing 60-session QQQ total return. Session 03 established that all
# three estimator forms failed on this history (the expanding form missed
# the COVID crash entirely at -19.4 against a threshold of -20.7; rolling
# 2,520 did not exist until June 2009 and was absent across the 2008
# crisis; rolling 1,260 fired on August 2015 after its threshold shallowed
# to -5.4) and that source's -12 sat at the 9.1st percentile of full
# history, so the percentile form targeted -18.45 and made the branch rarer
# than the rule it replaced. Threshold is in PERCENT; the comparison is
# strict less-than, matching source.
#
# Re-closed at -15 (session 09). Recorded as a STIPULATION interpolating
# the correction convention at 10 and the bear-market convention at 20,
# with the disclosure that both conventions describe drawdowns from a peak
# while this estimator is a point-to-point return between fixed dates, so
# the interpolation is a stipulation rather than a borrowed standard.
# Session 06 measured -12 firing on 37.9 percent of bear-reached sessions
# (four times its unconditional rate), so a deeper level shifts the branch
# from a co-equal state toward an override.
CRASH_THRESHOLD_PCT = -15.0

# Decision 6.10 -- closed. Horizon of the trailing return the crash test
# reads, in sessions. A supplied value rather than a measured optimum:
# session 03 found only 7 of 66 firing episodes unique to the 60-session
# horizon (all 1-8 session edge-grazes containing no major event), and
# neighbouring horizons caught stress that 60 missed outright, including
# August 2024 at the 20-session horizon.
CRASH_HORIZON_SESSIONS = 60

CRASH_REFERENCE_TICKER = "QQQ"

# Decision 5.4 -- closed. Four sleeves, 25 percent budget each.
SLEEVE_BUDGET = 0.25
N_SLEEVES = 4

# Decision 5.3 -- closed. Gross cap, proportional truncation if it binds.
GROSS_CAP = 1.00

# Decision 5.1 -- closed. Label rounding, whole percent of sleeve budget.
LABEL_ROUNDING_PERCENT = 1

# Decision 8.1 -- closed.
# Risk-free source. Deliberately named distinct from the financing constants
# (FINANCING_SPREAD_BP, decision 2.14), as 8.1 requires. Idle sleeve cash and
# sizing residuals accrue at this series per 5.5. Supersedes the session 01
# constant CASH_RATE_SERIES, which carried the same value under 5.5 and had
# no references outside this module.
RISK_FREE_SERIES = "DTB3"

# Decision 5.5a -- closed.
# DTB3 accrues at rate / RISK_FREE_DAY_COUNT per CALENDAR day, earned on
# every day the position is held including weekends and holidays -- not
# rate / 252 on trading days. DTB3 is quoted on a discount basis as an
# annualized figure, so the conversion to a daily return is a stated
# convention rather than an arithmetic identity, and 360 with calendar-day
# accrual is what a money market position actually earns.
RISK_FREE_DAY_COUNT = 360
RISK_FREE_ACCRUAL_BASIS = "calendar"

# Decision 3.12 -- closed provisionally (session 05).
# SMH pre-2013 return basis: constant accrual at this annual percent on a
# 252-day basis. Session 04 measured the basket's mean net dividend yield at
# 1.31 percent across 2007-2012 (gross 1.59, fee drag 0.25-0.44 pp) with
# nine of twenty tickers returning nothing, five of them known
# window-period payers -- so 1.31 is a LOWER BOUND and 1.5 is the central
# estimate. The provisional flag stays until someone decides whether to
# chase the nine missing dividend histories.
SMH_PRE2013_ACCRUAL_PCT = 1.5

# Decision 3.12 -- pre-registered sensitivity arm. An implementation /
# sensitivity dimension, NOT a specification-grid axis: it does not enter
# the 7.10 product (see 9.8 note below).
SMH_ACCRUAL_GRID = (0.0, 1.0, 2.0)

# Decision 4.4 -- closed (session 05).
# Slippage base sweep in basis points, round-turn, anchored at 10 bp per
# Zarattini 2025. Results are reported as a curve in the base with tier
# multipliers applied on top. Under decision 9.8 implementation dimensions
# run at canonical parameters rather than crossed against the full grid, so
# this grid does NOT enter the 218,700 specification count and the 7.10
# product guard is unaffected.
SLIPPAGE_BASE_GRID_BP = (0, 5, 10, 20, 35, 50)

# Decision 4.3 -- re-closed as uniform swept cost (session 09). No tiers,
# no multipliers. Session 06 found both negativity treatments pricing the
# thinnest tier cheapest, because the Corwin-Schultz bias is
# leverage-correlated while leverage sorts by tier, so the ratio premise
# that justified using a biased estimator fails. Separately, an order
# filling in a closing auction does not cross the spread, so the tier
# apparatus proxied the wrong cost. The base sweep (SLIPPAGE_BASE_GRID_BP)
# applies uniformly; the spread estimates and stress-window figures move to
# data characterisation in the writeup. Volatility scaling remains the
# pre-registered alternative arm.
SLIPPAGE_MODEL = "uniform"
SLIPPAGE_MODELS = ("uniform", "volatility_scaled")


# ---------------------------------------------------------------------------
# Grid ranges (specification sweep)
# ---------------------------------------------------------------------------

# Decision 7.6 -- closed.
# Long-SMA grid. 250 is dropped, so the sweep is 50, 100, 150, 200. The
# canonical value 200 is now the grid boundary rather than an interior point,
# which makes the long-end sensitivity claim one-sided.
SMA_LONG_GRID = (50, 100, 150, 200)

# Decision 7.7 -- revised (session 04).
# The crash axis sweeps levels rather than quantiles. Five points, so 7.10
# stays at 218,700.
CRASH_THRESHOLD_GRID = (-5.0, -10.0, -15.0, -20.0, -25.0)

# Decision 7.10 -- closed.
# Full cross of the specification grid. Dropping 250 removed one of five
# long-SMA values: 273,375 x 4/5 = 218,700. The 7.7 revision swapped the
# five-point quantile axis for a five-point level axis, leaving the total
# unchanged.
GRID_TOTAL_SPECIFICATIONS = 218_700

# Combined cardinality of grid axes NOT yet represented as tuples in this
# module (RSI periods per function, threshold tiers, short SMA, and any
# further axes the 7.x register carries): 218,700 / (4 long-SMA x 5 crash)
# = 10,935. No decision in hand enumerates those axes' values, so the full
# product cannot be recomputed from tuples alone yet; validate() pins this
# remainder instead. A session that adds an axis tuple must divide its
# cardinality out of this constant in the same edit.
GRID_UNREPRESENTED_AXES_CARDINALITY = 10_935

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate() -> None:
    """Fail fast on an inconsistent configuration."""
    if EXECUTION_MODE not in EXECUTION_MODES:
        raise ValueError(f"EXECUTION_MODE {EXECUTION_MODE!r} not in {EXECUTION_MODES}")
    if SIZING_MODE not in SIZING_MODES:
        raise ValueError(f"SIZING_MODE {SIZING_MODE!r} not in {SIZING_MODES}")
    if not 0 < SLEEVE_BUDGET <= 1:
        raise ValueError(f"SLEEVE_BUDGET out of range: {SLEEVE_BUDGET}")
    if abs(SLEEVE_BUDGET * N_SLEEVES - GROSS_CAP) > 1e-12:
        raise ValueError(
            f"sleeve budgets {SLEEVE_BUDGET} x {N_SLEEVES} do not sum to "
            f"GROSS_CAP {GROSS_CAP}"
        )
    if CRASH_THRESHOLD_PCT not in CRASH_THRESHOLD_GRID:
        raise ValueError(
            f"canonical CRASH_THRESHOLD_PCT {CRASH_THRESHOLD_PCT} is not on "
            f"the grid {CRASH_THRESHOLD_GRID}"
        )
    if CRASH_THRESHOLD_PCT >= 0:
        raise ValueError("CRASH_THRESHOLD_PCT is a decline and must be negative")
    if CRASH_HORIZON_SESSIONS < 1:
        raise ValueError(f"CRASH_HORIZON_SESSIONS must be positive: {CRASH_HORIZON_SESSIONS}")
    if SLIPPAGE_MODEL not in SLIPPAGE_MODELS:
        raise ValueError(f"SLIPPAGE_MODEL {SLIPPAGE_MODEL!r} not in {SLIPPAGE_MODELS}")
    if INTERIOR_GAP_TREATMENT != "skip":
        raise ValueError(
            f"INTERIOR_GAP_TREATMENT {INTERIOR_GAP_TREATMENT!r} is not the "
            "closed 1.9 value 'skip'; src/indicators.py and src/data.py "
            "implement skip and must be revisited before this changes"
        )
    if list(SLIPPAGE_BASE_GRID_BP) != sorted(SLIPPAGE_BASE_GRID_BP) or any(
        b < 0 for b in SLIPPAGE_BASE_GRID_BP
    ):
        raise ValueError(f"SLIPPAGE_BASE_GRID_BP malformed: {SLIPPAGE_BASE_GRID_BP}")
    if 10 not in SLIPPAGE_BASE_GRID_BP:
        raise ValueError("SLIPPAGE_BASE_GRID_BP must contain the 10 bp anchor (4.4)")
    if SMH_PRE2013_ACCRUAL_PCT < 0:
        raise ValueError(f"SMH_PRE2013_ACCRUAL_PCT negative: {SMH_PRE2013_ACCRUAL_PCT}")
    # 9.8: implementation/sensitivity grids (SLIPPAGE_BASE_GRID_BP,
    # SMH_ACCRUAL_GRID) are deliberately absent from this product.
    grid_product = (
        len(SMA_LONG_GRID)
        * len(CRASH_THRESHOLD_GRID)
        * GRID_UNREPRESENTED_AXES_CARDINALITY
    )
    if grid_product != GRID_TOTAL_SPECIFICATIONS:
        raise ValueError(
            f"grid axes multiply to {grid_product:,}, but "
            f"GRID_TOTAL_SPECIFICATIONS is {GRID_TOTAL_SPECIFICATIONS:,}; "
            "an axis was edited without resynchronising the total (7.10)"
        )
    if TREND_SIGNAL_LAG < 0:
        raise ValueError(f"TREND_SIGNAL_LAG must be non-negative: {TREND_SIGNAL_LAG}")
    if not OVERSOLD < OVERBOUGHT_TIER_1 < OVERBOUGHT_TIER_2:
        raise ValueError("threshold tiers are not ordered oversold < tier1 < tier2")
    if SMA_LONG not in SMA_LONG_GRID:
        raise ValueError(
            f"canonical SMA_LONG {SMA_LONG} is not on the grid {SMA_LONG_GRID}"
        )
    if RISK_FREE_DAY_COUNT not in (360, 252):
        raise ValueError(
            f"RISK_FREE_DAY_COUNT must be 360 or 252, got {RISK_FREE_DAY_COUNT}"
        )
    if RISK_FREE_ACCRUAL_BASIS not in ("calendar", "trading"):
        raise ValueError(
            "RISK_FREE_ACCRUAL_BASIS must be 'calendar' or 'trading', "
            f"got {RISK_FREE_ACCRUAL_BASIS!r}"
        )


validate()
