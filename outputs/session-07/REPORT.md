# Session 07 report — verifications and structural checks

Ten steps: four network verifications, four local measurements, one stated
limitation, this report. No strategy return, allocation, weight, turnover,
or performance statistic; no position formed; nothing committed. Positive
controls ran before every negative finding (null-audit synthetic control,
SPY cent-match vendor control, EDGAR known-present-filing control, grep
controls).

## Step 1 — closing price provenance (`close-provenance.md`)

**18 of 18 cross-vendor comparisons match to the cent** (Alpha Vantage raw
closes vs frozen Yahoo closes; SPY, QQQ, LABU, QQQE, BTAL, KMLM on
2026-04-15 / 2026-06-30 / 2026-08-14; UVIX has no frozen file — the
volatility legs are not in the panel — so KMLM substituted at the thin
end). No difference by liquidity. **But both vendors redistribute the
consolidated tape, so the official closing auction print cannot be
distinguished from the consolidated last sale with the sources available —
that indistinguishability is the finding**, stated per the instruction
rather than concluding a match. Historical stress dates were unreachable
(Alpha Vantage full history is premium; Stooq blocks scripted access).
4.2's "official closing print" remains an assumption about the feed.

## Step 2 — raw close precision (`raw-close-precision.csv`)

All 20 post-2015-split tickers reconstruct cleanly: earliest-date as-traded
closes land between **$23.31 (XLF) and $604.20 (SOXS)** — none below 0.01,
none above 100,000, **no implausible value anywhere**. The extreme stored
magnitudes (SOXS stored 5.8e11, TQQQ stored 0.216) reconstruct exactly;
the largest relative rounding error against cent-precision is **1.07e-4**
(TECL), five orders of magnitude above float64's 2.2e-16 epsilon — the
precision limit is the vendor's stored decimals, not float arithmetic, and
it does not degrade the result anywhere.

## Step 3 — fractional shares on MOC orders

From IBKR's published **Fractional Share Trading Disclosure** (IBKR LLC,
served via Lynx as an IBKR-authored document; IBKR's own site returns 403
to non-browser fetchers):

- "Available Order Types — IBKR will only accept certain types of orders
  for fractional Shares (e.g., market orders, limit orders, stop orders,
  stop limit orders, etc.)... Please contact us if you have any questions
  about order types available for fractional trading."
- "In connection with any fractional Share component of any purchase or
  sale transaction, **IBKR or its affiliate will act as a counterparty and
  will execute that portion of the trade as principal or riskless
  principal.**"

**The documentation does not address the fractional+MOC combination
explicitly** — on-close order types are absent from the enumerated list,
and the document defers to support for the full list. Reported as such
rather than inferred. Two things the documentation does establish:

1. The enumerated fractional order types are market/limit/stop/stop-limit;
   MOC and LOC are not named.
2. **A fractional component is never routed to the exchange closing
   auction** — it executes against IBKR as principal. So even where a
   fractional order fills at the close, the fractional part is by
   construction not the official closing auction print.

**Consequence, stated as the step requires:** if fractional and MOC are
incompatible, 4.7's primary specification is unexecutable as written, the
truncation arm becomes the only implementable version, and **4.6 reopens**
because truncation reintroduces the size dependence fractional sizing
removed. On the evidence, the combination is unaddressed-by-documentation
rather than confirmed-incompatible — but the principal-execution mechanism
already places the fractional component outside the 4.1/4.2 closing-auction
fill model regardless of order-type support. Both facts go to whoever
closes this.

## Step 4 — RYMFX changes after 2013 (`rymfx-schedule.md`)

EDGAR full-text search over the trust (positive control passed; 424
fund-mentioning filings screened; every relevant 497 read):
**no change to the fund's investment objective or principal investment
strategies after 2013-01-29.** The post-August-2021 filings touching the
fund are portfolio-manager changes only (2022-03-31 addition, 2022-07-08
departure, 2023-09-29 addition), and the 2022-07-08 supplement states
verbatim that they "will not affect the Funds' investment objectives or
principal investment strategies." **The 2.10 holdout consequence is not
triggered.** The April 2015 Class H → Class P redesignation renamed the
same share class (C000038557; ticker RYMFX throughout) — the series in use
is continuous. Caveat: the method keys on 497 supplements; a silent
rewording inside an annual 485BPOS would need year-over-year prospectus
diffing to exclude.

## Step 5 — QQQE underlying index (`qqqe-index-availability.md`)

**Reachable free: `^NETR` (Nasdaq-100 Equal Weighted Total Return) is
served by Yahoo**, 2006-08-21 → present, 92 sessions of headroom before the
sample start. **3.9 dissolves the way 3.8 did**; neither fallback (time-
varying panel, membership change) arises. One material property: the series
carries **3 interior one-day gaps** (2007-02-26, 2008-10-27, 2010-07-14) —
the first genuine interior gaps in any series the study has audited, which
**re-opens the practical relevance of 1.9's interior-gap treatment** if the
series is acquired. Nothing was acquired.

## Step 6 — synthetic-underlying null audit (`synthetic-underlying-null-audit.csv`)

Enumeration of what the 2.1/2.2 synthetic build requires, with the session
01 audit run on each series already held (positive control passed):

- **Present and clean (zero post-listing interior nulls):** QQQ, SMH, SPY,
  XLK, XLF, XBI (leveraged-fund underlyings/proxies), the VX 30-day
  constant-maturity series (`vx-cm30.parquet`, 2004-03-26 →, zero gaps
  against the SPY calendar), and RYMFX.
- **Present with interior nulls, different semantics:** DTB3 shows **60
  interior null sessions (max run 1)** against the SPY calendar — bond-
  market holidays on which equities trade (Columbus Day, Veterans Day).
  These are governed by 5.5a's carry convention for rates, not by the
  price-series reseeding question; recorded so nobody rediscovers them.
- **Not yet acquired (reported, not pulled):** Nasdaq-100 Equal Weighted TR
  (step 5 found it reachable), S&P 500 Growth/Value TR (VOOG/VOOV),
  DJ US Thematic Market Neutral Anti-Beta (BTAL), aggregate/short-term
  bond index history for the BND/BSV April-2007 listing gaps.

The reseeding question stays moot for every series currently on disk; it
becomes live with `^NETR`'s three gaps if acquired.

## Step 7 — 1.8 as a boundary-consistency check (`split-boundary-consistency.csv`)

The redefined structural test applied panel-wide: **69 split boundaries
across 23 tickers, tolerance |implied-price-ratio / split-ratio − 1| <
25%, zero failures.** Largest deviation 10.4% (SOXL's 15:1 on 2021-03-02 —
the fund's genuine −9.4% market move that session). **The check is
memory-free**: it uses only stored closes, stored split ratios, and the
adjusted = raw / cumulative-factor identity on the sessions either side of
each boundary; no externally recalled price level enters. (The three
session 05 cross-checks against recalled anchors remain as a separate,
memory-dependent spot check; this panel-wide test supersedes the ±50%
single-session return bound that 1.8 originally proposed, which would have
fired on UVXY's legitimate +96% and SVXY's −90% on 2018-02-06 and caught
neither session 04 factor error.)

## Step 8 — label transition frequency (`label-transitions.csv`, `label-transitions-holdlengths.csv`)

Joint concatenated label across all four sleeves, counted on the contiguous
fully-determinate span (which begins when the lagged RYMFX RSI seeds —
March/April 2007 — exactly as the trend-input availability implies; earlier
sporadically-determinate sessions are excluded so no transition is counted
across a gap):

| Grid point | Span | Joint transitions | Per year | Median hold | Max hold | T10 | T11 | S2 | S3 |
|---|---|---|---|---|---|---|---|---|---|
| canonical (14, 30) | 2007-03-15 →, 4,886 sess. | 2,041 | **105.1** | 1 | 39 | 1,102 | 1,231 | 454 | 593 |
| (7, 40) | 2007-03-06 →, 4,893 | 2,804 | **144.2** | 1 | 16 | 1,513 | 2,009 | 672 | 926 |
| (28, 20) | 2007-04-04 →, 4,872 | 1,126 | **58.2** | 2 | 141 | 495 | 680 | 237 | 242 |

**The strategy changes signal state about 105 times per year at canonical
parameters — roughly every 2.4 sessions, with a median holding length of
one session.** Even the slowest grid corner re-trades 58 times a year. The
joint rate exceeds every per-sleeve rate as expected (any sleeve change
transitions the joint label); T11 is the churn leader at every grid point.
Two known omissions, each worth exactly one transition: SVIX and UVIX have
no frozen series, so the T10 vol-short and S3 vol legs resolve to
SVXY/UVXY throughout and the single 2022 availability-flip label change per
switch is not counted. This is a count of signal-state changes; no weight,
position, or currency quantity was computed.

**What it implies for 4.4, stated without recommending:** at ~105
transitions per year the cost sweep is a headline axis of the study, not a
footnote.

## Step 9 — cash accrual asymmetry between the 4.7 arms (stated limitation)

Under fractional sizing there is no truncation residual, so idle sleeve
cash arises only when a sleeve returns an empty weight dictionary — which
among the four sleeves only S3's terminal cash branch does. Under the
truncation arm, every position leaves a residual accruing at DTB3 per
5.5/5.5a. **The two arms therefore differ not only in share quantization
but in how much cash accrues interest, so the fractional-vs-truncation
comparison is not clean: part of any difference between the arms will be
DTB3 accrual on residuals, not sizing per se.** Quantifying the wedge
requires positions and is out of scope; it is stated here so it is not
discovered later.

## Step 10 — what each finding unblocks or blocks

- **4.2** (official closing print): stays an assumption — unverifiable from
  available vendors; blocked on licensed exchange data if anyone insists on
  verifying it. Vendor-consistency itself is clean.
- **1.4 raw-close path**: unblocked — precision verified panel-wide.
- **4.7 / 4.6**: the fractional+MOC combination is unaddressed by IBKR's
  published documentation, and fractional components are internalized as
  principal rather than routed to the auction. 4.7's primary-arm
  executability is the open question this evidence sharpens; if it closes
  as incompatible, 4.6 reopens. Blocked on a decision (or on an answer
  from IBKR support, which the disclosure itself invites).
- **2.5 / 2.10**: unblocked — no post-2013 strategy change; holdout intact;
  the 2015 redesignation is benign.
- **3.9**: dissolves — the index is reachable free; an acquisition session
  can freeze `^NETR` under 1.1, at which point **1.9's interior-gap
  treatment becomes live** for its three gap sessions.
- **1.8**: redefined test applied panel-wide, zero failures — closes clean
  as a boundary-consistency check.
- **4.4**: the sweep is a headline axis at ~105 transitions/year; the
  transition counts are on disk for the writeup.
- **4.7-arm comparison**: carries the step 9 asymmetry as a stated
  limitation.

## Anything that did not match expectation

- Stooq's data endpoint blocks scripted access outright — an independent
  free vendor lost; Alpha Vantage's free tier covers only recent sessions.
- The `^NETR` interior gaps: every other audited series in the study is
  gap-free, and the first acquisition candidate to break that pattern is
  the one 3.9 was waiting on.
- The label-transition rate: median holding length of ONE session at
  canonical parameters is faster churn than anything in the register
  anticipated in writing.
- Step 8's first implementation started the measurement window at the
  first sporadically-determinate session (1995) rather than the contiguous
  span; transitions would have been counted across availability gaps. Fixed
  before results were read.

## Stop condition

Halted after this report. No backtest, no performance statistic, no
commit. Session writes: `scripts/s07_checks.py`, six CSVs and three MDs
plus this report under `outputs/session-07/`. The working tree stays
dirty.
