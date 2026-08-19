# Session 13 — canonical in-sample backtest

Run 2026-08-18. First strategy result in the project. Scripts:
`scripts/s13_backtest.py` (engine), `scripts/s13_runall.py` (pipeline).
Sample 2007-01-03 to 2021-07-30, 3,670 sessions, 3,460 evaluated after
warm-up, 13.73 years traded.

**A pre-registered sanity check failed.** The no-lookahead check (step 7)
fails: the result improves under one additional session of execution lag.
Per the session rule — report any failure and stop rather than continuing
to interpretation — every table this session produced is reported below
with its diagnostics, and interpretation of the headline is withheld.
The failure is described under Sanity checks.

## Provisional operating values, stated before any statistic

No later session may read any of these as a closure.

1. **Starting NAV 1,000,000** — provisional operating value under
   decision **4.6, which remains OPEN** pending a liquidity check against
   the realized NAV path. Not canonical. The daily NAV path this value
   seeds is retained at full daily frequency in `daily-series.csv` as the
   input that check requires.
2. **IBKR Fixed commission** at 0.005 per share, 1.00 minimum, 1 percent
   of trade value cap — **v2 decision 4.5, carried inline; the port into
   DECISIONS-v3.md and src/config.py is outstanding.** Closed in
   conversation on the grounds that Fixed is the only schedule
   continuously available 2007–2026, conservative on level since a
   post-2019 zero-commission account would pay less.
3. **Unavailable-fill completion rule** — a target whose fill-session
   price does not exist (BTAL before its 2011-09-13 listing, in both
   arms; every unlisted fund in the realized arm) is recorded as an
   unavailable-fill event and the slice stays in sleeve cash at DTB3.
   The register's 1.9/2.11 answer to an unavailable fill is a raise with
   no default chosen; running the backtest at all requires a completion
   rule, so this one is adopted PROVISIONALLY, disclosed here, with every
   event dated in `_unavailable-fills-*.csv`. 40 events in the primary
   arm, all BTAL, 2008-10-31 to 2011-04-29.
4. **Raw-path price reconstruction and normalization** — the frozen
   files' `Close` is Yahoo split-adjusted to 2026 share units (verified:
   continuous across all 21 in-window split boundaries; UVXY's 2012 close
   reads 8.3e10). As-traded prices were reconstructed with in-window
   split factors only (post-holdout split rows are post-boundary
   observations under 2.10 and were not touched), which leaves each
   fund's level scaled by an unknowable constant — for the heavy
   reverse-splitters so large that truncation sized whole basket slices
   to zero shares and silently deleted the SOXS leg of T11's bull-short
   basket. Each levered fund's raw path is therefore rescaled so its
   first listed in-window price is 100.00; real in-window splits keep the
   band shape, only the level is stipulated. Share counts, commission,
   and truncation residuals depend on this convention; returns and
   signals do not. Pending the 4.5 port and 4.6 closure.
5. **Negative cash convention** — commission and slippage are paid at the
   fill on top of fully invested targets, so portfolio cash can go
   slightly negative between transitions; it accrues DTB3 symmetrically
   (no financing spread — the 2.14 constants belong to synthetic
   construction, not account margin). At the anchor: minimum cash
   −87,871, 1,376 sessions negative, maximum realized gross 1.0278.

## Resolved configuration (all from src/config.py)

| Parameter | Value | ID |
|---|---|---|
| RSI periods (exhaustion / dip / relative strength) | 14 / 14 / 14 | 6.1 |
| Overbought tier one / tier two | 70 / 80 | 6.2, 6.3 |
| Oversold | 30 | 6.4 |
| SMA long / short | 200 / 20 | 6.5, 6.6 |
| Crash threshold / horizon / reference | −15.0% / 60 sessions / QQQ, strict less-than | 6.10 |
| Warm-up | 210 sessions | 2.11 |
| Trend series / lag | RYMFX / 1 session at load | 2.5, 2.5a |
| Sleeves x budget / gross cap / label rounding | 4 x 25% / 100% proportional truncation / whole percent | 5.4, 5.3, 5.1 |
| Execution | signal T close, fill T+1 close, close-to-close | 4.1 |
| Sizing | truncation, residual to sleeve cash | 4.7 |
| Slippage | uniform, swept (0, 5, 10, 20, 35, 50) bp round-turn, half per side | 4.3, 4.4 |
| Risk-free | DTB3, rate/360 per calendar day, null-day carry | 8.1, 5.5a |
| SMH pre-2013 accrual | 1.5%/yr on 252-day basis, applied before 2012-12-24 | 3.12 |
| Interior gaps | skip | 1.9 |
| Sharpe | naive and Lo-corrected, corrected as headline | 8.2 |

Prompt-versus-config discrepancies: none — every value the prompt lists
matches config. One config gap: the **S3 vote threshold (3 of 4) is a
hardcoded literal in src/sleeves.py** (`votes >= 3`) and appears in no
config constant, contrary to config's own no-literals rule. Reported;
not changed. The value used matches the prompt's canonical 3-of-4.

## Holdout enforcement (2.10)

Every input series is truncated at 2021-07-31 inside the loader before
any strategy code runs. Post-load assertion across every frame in both
arms: **PASS — maximum loaded date 2021-07-30** in each arm. No
post-boundary quantity was computed, plotted, or referenced. Post-holdout
split rows were likewise excluded (see provisional value 4).

## Instrument sourcing (2.8)

Primary arm all-synthetic: 14 levered/inverse exposures from
`data/interim/synthetics/` (TQQQ, SQQQ, QLD, PSQ, SH, SPXL, TECL, TECS,
SOXL, SOXS, FAS, LABU, UVXY, SVXY); 21 unlevered instruments from frozen
files. Realized arm: listed funds wherever they existed, the unavailable
rule (provisional completion above) where they did not.

- **SOXS uses the synthetic. In-window (canonical, re-scoped by session
  13.7 per D11): corr 0.997, tracking difference +0.78%/yr, maximum
  rolling divergence 14% — the recorded full-window exception (+6.21%/yr,
  1394%, labeled full-window 2010-03..2026-08) is almost entirely a
  post-boundary phenomenon.** Every result below that touches T11's
  bull-short state (14.8% of sessions; SOXS 1.5% of dollar exposure)
  depends on it. Listed SOXS from 2010-03 was rejected because it would
  remove T11's bull-branch inverse basket across 2008 (2.12a).
- **SVIX and UVIX list 2022-03-28, outside this sample entirely; the T10
  short-volatility and S3 volatility legs resolve to SVXY and UVXY
  throughout**, via the sleeves' availability switches.
- RYMFX raises (2.11): the pairwise sites raise on **50 distinct
  sessions, 2007-01-03 to 2007-03-19** in the primary arm (81 sleeve-
  events: T10 XLK>TREND 44, S2 SQQQ>BSV 23, T11 sites 14 — early-January
  events reflect RSI seeding of both sides, not only RYMFX). Realized
  arm: 47 sessions to 2007-03-14. **All inside warm-up; zero raises in
  the traded window in either arm.** Dates in `_raises-*.csv`.

## Headline — the cost curve (primary object)

Lo-corrected Sharpe is the headline per 8.2; the naive figure sits
beside it. Note the Lo correction RAISES the Sharpe here (daily returns
carry negative autocorrelation). Turnover is one-sided (sells+buys)/2 as
a multiple of average NAV per year. Full table: `headline-results.csv`.

**Synthetic (primary) arm:**

| bp | total ret | ann ret | ann vol | SR naive | SR Lo | max DD | Calmar | turnover |
|---|---|---|---|---|---|---|---|---|
| 0 | 18.57x | 24.19% | 54.3% | 0.657 | 0.813 | −74.1% | 0.326 | 42.1 |
| 5 | 13.63x | 21.59% | 54.3% | 0.618 | 0.764 | −75.4% | 0.286 | 42.2 |
| **10** | **9.95x** | **19.05%** | **54.3%** | **0.579** | **0.716** | **−76.7%** | **0.248** | **42.3** |
| 20 | 5.12x | 14.11% | 54.4% | 0.501 | 0.619 | −79.0% | 0.179 | 42.5 |
| 35 | 1.55x | 7.06% | 54.4% | 0.384 | 0.474 | −83.6% | 0.084 | 42.9 |
| 50 | 0.06x | 0.41% | 54.5% | 0.266 | 0.329 | −87.8% | 0.005 | 43.5 |

**Realized-instrument arm** (implementability check; early years hold
forced cash — see Both arms below):

| bp | total ret | ann ret | ann vol | SR naive | SR Lo | max DD | Calmar | turnover |
|---|---|---|---|---|---|---|---|---|
| 0 | 23.93x | 26.40% | 45.2% | 0.730 | 0.810 | −68.0% | 0.388 | 39.9 |
| 10 | 14.44x | 22.06% | 45.3% | 0.652 | 0.732 | −69.1% | 0.319 | 39.1 |
| 50 | 1.26x | 6.11% | 45.4% | 0.343 | 0.399 | −73.2% | 0.084 | 33.5 |

**Zero crossings (linear interpolation on the six-point curve):**
primary-arm annualised return crosses zero at **≈ 50.9 bp round-turn**
(just past the 50 bp grid edge — extrapolated from the last segment);
Lo-corrected Sharpe crosses zero at **≈ 83.9 bp (extrapolation well
beyond the swept range)**. Realized arm: ≈ 66.0 bp and ≈ 96.5 bp, both
extrapolated.

**At the 10 bp anchor the strategy's mechanical figures are positive**
(19.05% annualised, Lo Sharpe 0.716) and annualised return remains
positive across the whole swept range, reaching ≈ 0.4% at 50 bp. Under
the pre-registered protocol this is reported but **not interpreted**,
because the timing-defect check below failed: the cost curve of a
strategy that improves under additional lag cannot be read as evidence
about the strategy until the defect question is resolved. Cost is a
headline axis regardless: 4.2 pp of the 5.1 pp annualised drop from 0 to
10 bp is slippage arithmetic (42x turnover x 10 bp), the rest commission
and compounding interaction.

## Sanity checks (step 7) — one failure

Full table: `sanity-checks.csv`.

| Check | Result | Detail |
|---|---|---|
| NAV reconciles | PASS | cumulative product of daily returns matches ending NAV, relative gap 2e−15 |
| **No lookahead** | **FAIL** | **see below** |
| Cash accounts | PASS | max abs(positions + cash − NAV) = 0.0 on every session |
| Gross ≤ 100% after truncation | PASS | max target gross 1.000000; realized gross max 1.0278 arises only from cost-induced negative cash (provisional value 5) |
| Sleeve weights sum to budget | PASS | 0 of 13,840 sleeve-sessions off budget |
| Warm-up boundary | PASS | first loaded 2007-01-03, first signal 2007-11-01 (index 210), first fill 2007-11-02; indicators return unavailable until defined |
| Commission cap | PASS | 0 of 8,657+ orders exceed 1% of trade value, across all 13 runs |

**The lookahead check.** Shifting every fill one additional session
forward (T+2 close instead of T+1 close, same signals, same labels):

| | ann return | ann vol | SR naive | SR Lo | max DD |
|---|---|---|---|---|---|
| T+1, 10 bp | 19.05% | 54.3% | 0.579 | 0.716 | −76.7% |
| T+2, 10 bp | 27.51% | 55.0% | 0.725 | 0.649 | −79.2% |
| T+1, 0 bp | 24.19% | 54.3% | 0.657 | 0.813 | −74.1% |
| T+2, 0 bp | 33.02% | 55.0% | 0.795 | 0.739 | −77.1% |

Annualised return **improves by 8–9 pp under one extra session of lag,
cost-free included**, which is the pre-registered timing-defect flag; the
Lo-corrected Sharpe moves the other way (0.716 → 0.649 at the anchor),
so the defect is in return timing, not uniformly in risk-adjusted terms.
Decomposition: the mean portfolio return on a new position's first held
session is +11.2 bp against a +14.4 bp unconditional session mean — the
strategy systematically enters one session before short-term reversal,
and a one-session-later entry catches it.

*Correction, 2026-08-18 (session 13.6, defect D9).* This paragraph
originally stated the decomposition as +3 bp against +11 bp. Those
figures were measured on the pre-correction engine path (before the
raw-path split repair described under "Engine corrections" below) and
were carried into this report in error. Session 13.5 measured the
corrected-path values at +11.2 bp and +14.4 bp, now shown above. The
check's verdict is unchanged. The engine itself was
positive-controlled (a constant 100% SPY target reproduces SPY's total
return over the window to 0.004%), so the effect is a property of the
strategy's signal timing as specified, not of the accounting. Under the
session rule, this failure stops interpretation; whether T+1 execution
stands, or the defect is investigated further, is a register decision
for the user, not this session.

## Diagnostics (step 6) — full table in `diagnostics.csv`

**Transitions and holding lengths.** 1,425 signal transitions =
**103.8/yr** (session 07 signal-level count: 105/yr — consistent; the
label short-circuit and drift rule behave in the full pipeline as in the
label computation). All 1,425 filled (none fell on the final session).
Holding lengths: median 1 session, mean 2.43, 56.1% of holds are one
session, 90th percentile 5, maximum 40. Realized arm: 1,369 transitions
= 99.7/yr (fewer states reachable while instruments are unlisted).

**Concentration (5.7), target / realized at the anchor.** ENC by 1/HHI
on tickers 3.12 / 3.01 mean; on underlyings 2.60 / 2.54. Effective
number of minimum-torsion bets (Meucci et al. 2015, minimum-torsion not
PCA; covariance fixed over the full-overlap window 2011-09-14 to
2021-07-30 — BTAL-bounded, disclosed convention) 8.17 / 8.19 mean, 9.48
/ 9.48 median. Effective market exposure (sum of weight x signed
multiple, per-date schedule multiples, BTAL counted 0) mean 1.70 / 1.74,
5th percentile −0.25 / −0.03, 95th 2.75 / 2.73. Maximum single-ticker
weight mean 0.464 / 0.461; single-underlying 0.518 / 0.513; top-three
sum 0.809 / 0.803. By drawdown quintile (quintile 0 = deepest): ENC and
ENB are nearly flat across quintiles (3.08–3.20, 7.7–8.8); effective
exposure is lowest in quintile 1 (1.37) and highest in quintile 4
(1.92). All-cash sessions: 0% target, 0.03% realized.

**Breadth (5.6).** Sleeve terminal-state occupancy (share of 3,460
sessions): T10 — rs-bull basket 44.4%, UVXY 27.2%, SQQQ/TLT 23.2%, four
dip states 1.8/1.5/1.1/0.8%. T11 — bull basket 44.3%, tier-1 basket
16.9%, bull-short basket 14.8%, bear pairs 19.6% across 13 observed
combinations, tier-2 UVXY 1.7%, dips 2.5%. S2 — TQQQ 73.7% (gate 62.6%
+ default 11.1%), UVXY 11.2%, BSV 7.7%, SQQQ 4.7%, TECL/SOXL 2.7%. S3 —
TQQQ/SOXL 51.7%, cash 27.2%, UVXY 18.7%, SOXL 2.4%. Two or more sleeves
hold the same ticker simultaneously on **92.2%** of sessions.

**T10 cascade reach rates (6.13).** Overbought scan 100%, dip-TQQQ
72.8%, dip-SOXL 71.3%, dip-SPXL 69.5%, dip-LABU 68.7%, XLK>TREND site
67.6%.

**Branches that never fire in-sample:** T11 bond_baller's PSQ-dip
terminal and T11 feaver_bear's PSQ-dip terminal (both sit behind
TQQQ>SMA20 with PSQ RSI<30 — states that never co-occur). The
writeup must not claim they do anything. T11's crash→BTAL terminal fires
on only 4 sessions (0.12%), crash→QLD on 81 (2.3%). Branch-firing
positive control: an independent branch tracer reproduced all four
sleeves' recorded outputs on every one of 3,460 sessions.

**Time in instrument (fraction of sessions held / of dollar exposure,
anchor).** TQQQ 77.4%/36.6%, SOXL 73.4%/18.3%, TECL 56.6%/9.0%, SVXY
44.3%/4.0%, UVXY 29.0%/18.5%, SQQQ 28.5%/5.9%, TLT 23.2%/3.4%, BIL
16.9%/2.0%, TECS and SOXS 14.8%/1.5% each, QQQ 13.5%/1.2%, BTAL
13.7%/1.9%, BSV 7.7%/1.4%, PSQ 6.6%/0.7%, QLD 2.3%/0.2%, SPXL
1.1%/0.5%, LABU 1.1%/0.2%.

**Gross cap (5.3).** The cap fired on **0 transitions**; maximum gross
before cap 1.000. With four 25% sleeves emitting at most 1.0 the cap
cannot bind, as the register expects.

**Pairwise raises (2.11).** 50 sessions primary / 47 realized, 1.4% /
1.3% of all sessions, every one inside warm-up, dates 2007-01-03 to
2007-03-19 / -03-14; zero in the traded window.

**Commission (amended step 6; all figures under provisional value 4).**
Portfolio commission 0.97 bp of traded value; the 1.00 minimum bound on
18.0% of the 8,657 anchor-run orders, the 1% cap on 0.23%. By
instrument (bp of traded value, min-bound share): UVXY 0.02/75%, SQQQ
0.04/82%, TECS 0.06/100%, PSQ 0.27/22%, TLT 0.40/23%, LABU 0.44/4%,
TECL 0.57/20%, BSV 0.64/28%, QQQ 0.71/46%, BIL 0.71/18%, SOXL 0.73/10%,
SPXL 1.29/2%, QLD 1.74/20%, TQQQ 2.36/10%, SVXY 2.54/20%, BTAL 2.53/14%.
The per-share rate and the minimum produce drag differing by two orders
of magnitude across price levels; this split is the input a later 4.6
closure reads.

## Sub-period stability (step 8) — `subperiod.csv`

**7.14 sub-period definitions remain OPEN; no definitions were invented.
Calendar years are reported**, at the 10 bp anchor:

| Year | Synthetic | Realized | | Year | Synthetic | Realized |
|---|---|---|---|---|---|---|
| 2007* | −3.3% | +0.1% | | 2015 | −7.1% | −4.2% |
| **2008** | **+6.2%** | −1.5% | | 2016 | +13.5% | +25.1% |
| 2009 | +18.9% | +10.3% | | 2017 | +55.4% | +41.0% |
| 2010 | **−49.2%** | +6.2% | | 2018 | +40.8% | +29.3% |
| 2011 | −14.4% | −26.4% | | 2019 | +81.1% | +89.2% |
| 2012 | −19.8% | −15.1% | | 2020 | +60.4% | +69.5% |
| 2013 | +74.5% | +57.1% | | 2021† | +55.4% | +55.6% |
| 2014 | +41.5% | +25.0% | | | | |

*2007 is Nov–Dec only. †2021 through 07-30.

**2008 separately:** the synthetic arm returned +6.2% in 2008 (maximum
in-year drawdown −41.3%). The full-sample result is NOT concentrated in
2008 — the profitable mass sits in 2013–2014 and 2016–2021, while
2010–2012 is deeply negative (2010 −49.2%). The regime-gradient finding
stands regardless: construction tracking error rises steeply (canonical
in-window 6.2x, session 13.7 re-scope; session 12's recorded 5.4x
retained as full-window) from the calmest to the wildest volatility
decile, 2008 sits in the wildest, so the 2008 figure rests on the least
reliable part of the construction.

## Both arms of 2.8 — the implementability check

The strategy as specified was **not implementable with listed funds
before roughly 2011-10**: 774 target fills were unavailable in the
realized arm (TQQQ 210, SOXL 131, SVXY 130, SQQQ 128, UVXY 82, BTAL 33,
TECL 28, SOXS 19, SPXL 8, TECS 5; dates in
`_unavailable-fills-realized.csv`), each slice sitting in cash under the
provisional completion rule. The last unavailable fill is 2011-10-03
(SVXY listing eve); from Q4 2011 the realized arm fills everything.
Consequently the arms are not like-for-like before 2012: the realized
arm's +6.2% versus the synthetic arm's −49.2% in 2010 is mostly forced
cash, not tracking. From 2012 onward the yearly rows agree in sign every
year, with the synthetic arm higher in most up years — the direction a
synthetic construction that omits real-fund frictions beyond its expense
and financing model would be expected to show. Full-window figures at
the anchor: synthetic 19.05% annualised / Lo Sharpe 0.716; realized
22.06% / 0.732 — the realized arm's early forced-cash years lower its
volatility (45% vs 54%) more than its return.

## Limitations bearing on every number above

1. **Timing defect flag**: the failed lookahead check, above.
2. **SOXS exception, re-scoped (session 13.7; metric corrected session
   13.8)**: in-window corr 0.997, annualised ratio drift +2.32%/yr
   (canonical under the corrected 2.7a metric; the earlier +0.78%/yr was
   the compressed geometric-difference figure), max rolling divergence
   14%. TECS reads +2.01%/yr under the same metric — an inverse-sector-
   fund class effect, not SOXS-specific. The recorded +6.21%/yr and
   1394% are full-window figures dominated by post-boundary sessions.
   Touches every T11 bull-short session (14.8% of sessions).
3. **SVIX/UVIX absent** before 2022: short-vol and vol legs resolve to
   SVXY/UVXY throughout; the SVXY/UVXY synthetics themselves carry the
   close-timing residual class (+7.5–8.9%/yr against exchange closes).
4. **Regime-conditional construction weakness**: equity tracking error
   rises steeply from calmest to wildest volatility decile — canonical
   in-window figure 6.2x (D1 2.26% → D10 14.03%) under the documented
   session 13.7 method; session 12's recorded 5.4x could not be
   reproduced and is retained as a full-window historical figure. The
   bear branches operate where the construction is weakest; 2007–2010
   extrapolation is the weak case.
5. **Financing anchor** (75 bp long / 70 bp short) is a single-fiscal-
   year snapshot (Direxion FY2025 / ProShares FY2026).
6. **Expense schedule** stated for seven Direxion funds in FY2025 only;
   all other funds carry constants.
7. **Proxy underlyings**: QQQ (NDX funds), SPY (SPX), XLK, SOXX, XBI
   exact; XLF proxies FAS's Russell benchmark before 2022-08 with an
   undisclosed basket mismatch.
8. **Unvalidated pre-inception windows**: sector funds have no sibling
   validation before their listings; NDX/SPX families do through 2008.
9. **Provisional operating values 1–5** at the top of this report,
   including the raw-path price normalization every commission and
   truncation figure depends on.
10. **BTAL** has no synthetic (2.6) and no listing before 2011-09-13:
    40 primary-arm target events (2008-10-31 to 2011-04-29) sat in cash
    under the provisional rule — inside the window where T11's crash
    branch was active.
11. **Vote threshold** 3-of-4 is a literal in src/sleeves.py, absent
    from config (register gap, reported above).
12. **ENB covariance window** is fixed full-overlap 2011-09-14 to
    2021-07-30 (a diagnostic convention; no rolling estimate is
    registered).

## Engine corrections made during this session (transparency)

Two defects were found and repaired in the session's own engine before
the final run; both repairs are correctness fixes, not parameter
changes, and the intermediate (wrong) results were discarded:

1. The first run treated the frozen `Close` as as-traded and multiplied
   the share ledger at split boundaries while prices were in fact
   continuous (split-adjusted), producing phantom delta trades on holds
   spanning splits and commissions in wrong units.
2. The corrected as-traded reconstruction left reverse-split-heavy funds
   at price levels that sized SOXS basket slices to zero shares on every
   fill (a silent leg deletion). Resolved by the disclosed $100 listing
   anchor normalization (provisional value 4).

## Output files

`daily-series.csv` (3,460 sessions: joint label, per-sleeve target
states, realized per-ticker weights, gross and effective exposure for
target and realized, transition flag, anchor return, cash, NAV at the
anchor and at all six cost levels, realized-arm anchor NAV — full daily
frequency per the 4.6 amendment), `headline-results.csv`,
`diagnostics.csv` (247 rows), `sanity-checks.csv`, `subperiod.csv`,
`_raises-*.csv`, `_unavailable-fills-*.csv`, `_summary.json`.

## Stop condition

Halted after this report. Holdout untouched beyond the loader-level
truncation described. No grid, no benchmarks, no nulls, no alpha, PSR,
DSR, or test statistic. Nothing committed; working tree left dirty.
