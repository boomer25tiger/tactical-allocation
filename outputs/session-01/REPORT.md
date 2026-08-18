# Session 01 report — implementation of the four sleeves

Code-writing session. No strategy return, Sharpe, Calmar, drawdown,
allocation against real prices, turnover, or any other performance statistic
was computed. Apart from step 0 (RYMFX acquisition) and the interior-null
audit added by the session continuation — both counts of data properties —
no parquet under data/ was opened. Nothing was committed; the working tree
is dirty as required.

The register on disk (docs/DECISIONS-OPEN-v2.md, modified 2026-08-17 12:06)
predates session 00A and was not read for parameters. Every parameter came
from the session prompt and its continuation.

Structural reference: docs/source-quantconnect.py, 353 lines, sha256
`0532b0cfb4914d98bc7fb02083d9d08344e006646b0d51313fb86565401204bf`.
Naming correction applied throughout: the register's S1 is source's T10, the
eleven-name overbought cascade; session 00C's measurements under the S1
label stand, since the ticker list matches.

## Step 0 — RYMFX acquired and frozen

Pulled with `auto_adjust=False, actions=True` (yfinance 1.6.0), truncated at
2026-08-14 per 1.14, written to `data/raw/etf/RYMFX.parquet`, never to be
re-pulled per 1.1 (the write script refuses if the file exists).

- SHA-256 `0898d65147c79ec4a947d24974bf49b296b7792f35c7dc2460ec74d3b4a3ed98`
  (recorded in the manifest and cross-checked by shell after write)
- 4,901 rows, 2007-02-22 → 2026-08-14, 119,006 bytes
- Manifest row in session 00C format: `outputs/session-01/etf-manifest.csv`
- Pull timestamp 2026-08-17T23:00:08 UTC

Eight verification gates ran before the write, all PASS: first date
2007-02-22 exactly; pre-truncation last ≥ 2026-08-14; post-truncation last
== 2026-08-14; zero missing sessions against the SPY calendar; no dates
outside the SPY calendar; **Open == Close on every one of 4,901 rows**;
column schema matches the 35 siblings; no null Close. Post-write round-trip
and hash verification passed.

## What was written

| File | Purpose |
|---|---|
| `src/config.py` | Every constant with decision ID and status; `validate()` on import |
| `src/indicators.py` | Wilder RSI + SMA lifted from 00C, nulls propagate (1.9) |
| `src/data.py` | Two-path loader (1.4), AdjOpen (1.5), trend lag once (2.5a) |
| `src/sleeves.py` | t10/t11/s2/s3 weight functions, structure from source |
| `src/portfolio.py` | Merge, label, short-circuit, gross cap, drift (5.1–5.4) |
| `src/execution.py` | T+1 fills, mode arm, sizing arm, degeneracy detection (4.1/4.7/5.5) |
| `tests/` (5 files) | 155 tests, all passing, all on hand-constructed input |
| `outputs/session-01/rsi-function-mapping.md` | Step 3 deliverable, amended per continuation |
| `outputs/session-01/interior-null-audit.csv` | Continuation §3 deliverable |
| `outputs/session-01/parameter-divergence.csv` | Step 7 deliverable, 30 rows |
| `outputs/session-01/etf-manifest.csv` | Step 0 manifest row |

`src/config.py` was written during step 1 rather than step 4 because the
indicators and loader already needed it. Continuation amendments applied:
WARMUP_SESSIONS is 210 (2.11 closed — max of longest SMA and RSI seed
convergence, not their sum, plus a ten-session margin; note source's own
warm-up was 215, so the 292→210 change lands near source's value by a
different derivation); SMA_LONG_GRID is (50, 100, 150, 200) per 7.6 and
GRID_TOTAL_SPECIFICATIONS is 218,700 per 7.10 (273,375 × 4/5 — dropping 250
removes one of five long-SMA values, which cross-checks the stated total).
**Grid note: 200 is now the boundary of the long-SMA grid rather than an
interior point, so the long-end sensitivity claim is one-sided.**

## RSI function mapping

47 consumption legs enumerated with completeness reconciled against all 57
`rsi`-token lines in source (positive-controlled grep). Confirmed with three
amendments, now recorded in the mapping file, which contains **no open
ambiguities**:

- A1 `RSI10(PSQ) < 35` → **dip** (structure wins; threshold governed by 6.4,
  35→30; the inverse-ETF economic reading is retained as writeup context)
- A2 `RSI20(AGG) > RSI60(SH)` → **relative strength, closed by 6.19**, both
  sides at 14
- A3 `RSI10(IEF) > RSI20(PSQ)` → **relative strength, closed by 6.19**, both
  sides at 14

## Interior-null audit (continuation §3)

`outputs/session-01/interior-null-audit.csv`, 71 rows (36 raw parquets
including RYMFX; 35 panel series). Two positive controls before any zero was
trusted: a synthetic series with known pre-listing count 3, interior count
2, max run 2, detected exactly; and KMLM's 6,526 pre-listing nulls matched
an independently computed count of union-calendar sessions before
2020-12-02. Union calendar over the 36 raw files equals the SPY calendar and
the panel calendar exactly (7,957 sessions, 1995-01-03 → 2026-08-14).

**Result: zero post-listing interior nulls in every series on both paths.**
Longest interior run 0 everywhere. Pre-listing nulls exist for 35 raw / 34
panel series (all but SPY, which defines the calendar start), as expected
for staggered inceptions.

Consequence: the segment-reseeding choice in `src/indicators.py` and
`src/data.py` is **moot on this panel** — no interior hole exists for it to
act on. The choice remains flagged as an implementation decision belonging
to the open half of 2.11, but it currently has no observable effect.
Per the continuation's instruction, the session continued to step 4 without
stopping.

## Scoping the 00C RSI defect (continuation §4)

The 00C `wilder_rsi` read a null bar as a zero change (NaN fails both
`np.where` tests), so a missing bar was silently treated as a flat session —
forward-fill in effect, against 1.9. The lift preserves the Wilder
arithmetic exactly on null-free input (asserted test-for-test against the
00C implementation) and propagates nulls; a regression test pins the 00C
behaviour so the defect cannot be re-lifted.

Exposure scoping: the defect can only have influenced a measurement if a
null fell inside a measured window. The audit shows **zero interior nulls on
the panel 00C measured**, so the defect never triggered. Findings resting on
RSI — the panel effective-independence figures behind 6.9 (S1 1.77, T11
1.39), the PSQ-against-SH redundancy result, and the leveraged-fund RSI
scale-invariance measurement — **stand as measured**. Findings resting on
SMA comparisons (the vote work behind 6.8, the TQQQ/QQQ crossover behind
6.16, the S3 vote-set measurements) were never exposed: the 00C SMA already
propagated nulls correctly. Exposure was code-level only, with no measured
consequence.

## Sleeves — structure and substitutions

Structure taken from source and preserved exactly: T10 cascade order, T11
two-tier overbought and 50/50 bear split across `_t11_bond_baller` /
`_t11_feaver_bear` (get-accumulate merge, so agreement concentrates 1.0 on
one ticker), S2's TQQQ 200-SMA gate, S3's four-vote count with
three-of-four threshold. Sleeve weights are fractions of sleeve budget
(source QUARTER ≡ 1.0); scaling to the 25 percent budget happens once, in
the portfolio layer.

The four substitutions, implemented and tested:

1. **KMLM → TREND_SIGNAL_SERIES (RYMFX)** at all five signal sites (two RSI
   relative-strength comparisons; the price, the SMA-20 registration, and
   the price-below-SMA test in T11). Confirmed in-session with a
   positive-controlled grep: **KMLM appears in no weight dictionary anywhere
   in source** (the allocation-line pattern finds five TECL allocations;
   zero KMLM allocations), so no held position changes. The 2.5a lag is
   applied once at load time in `src/data.py`; no sleeve code knows the
   trend series is lagged.
2. **Crash test** `qqq_60d < -12` → return below the rolling 5th percentile
   of trailing 60-session QQQ total returns (6.10), window/gate from config
   (6.11, 6.12). Tested both ways: a return of −14 percent with a quantile
   at −20 percent does not fire (source's rule would have); an unavailable
   quantile reads false, so the branch cannot fire before the window fills.
3. **Permissive fallback removed.** `(not kmlm_ready) or (XLK > KMLM)`
   routed risk-on whenever the trend series was unready — a directional
   assumption covering eleven of the sixty months source ran. A test
   asserts the unready case raises rather than defaulting risk-on.
4. **Threshold collapse.** All single-tier overbought sites take tier one
   70 (T10 cascade 79/75/80, S2 79, S3 72); T11's pair takes 70/80 (79/81);
   every oversold site takes 30 (31, 29, 25, and A1's 35). Boundary tests
   pin the collapsed values (e.g. LABU at 29.5 fires under spec, would not
   under source's 25; PSQ at 32 does not fire under spec, would under
   source's 35).

### Unavailable inputs — the settled half of 2.11

Threshold tests read false on unavailable input (RSI-vs-constant,
price-vs-own-SMA including the four S3 votes, and the crash test). Pairwise
RSI-vs-RSI comparisons raise `NotImplementedError` naming the call site.
**Every NotImplementedError location:**

| # | Site string | Module |
|---|---|---|
| 1 | `t10_weights:XLK>TREND` | src/sleeves.py |
| 2 | `t11_weights:XLK>TREND` | src/sleeves.py |
| 3 | `t11_bond_baller:TLT>PSQ` | src/sleeves.py |
| 4 | `t11_bond_baller:AGG>SH` | src/sleeves.py |
| 5 | `t11_bond_baller:IEF>PSQ` | src/sleeves.py |
| 6 | `t11_feaver_bear:BND>QQQ` | src/sleeves.py |
| 7 | `t11_feaver_bear:AGG>SH` | src/sleeves.py |
| 8 | `t11_feaver_bear:IEF>PSQ` | src/sleeves.py |
| 9 | `s2_weights:SQQQ>BSV` | src/sleeves.py |
| 10 | fill price unavailable at T+1, per instrument | src/execution.py |

The tenth is the execution-layer analogue: a missing bar at the fill session
is 1.9-unavailable, and what execution does about it is the same open half
of 2.11, so it raises rather than defaulting. The driver propagates these
raises deliberately. With RYMFX history from 2007-02-22, sleeves evaluated
before its RSI seeds (~mid-March 2007 at period 14) raise at the XLK>TREND
sites — expected, not suppressed, no date guard added.

## Portfolio — merge, label, drift

All four weight functions execute on every post-warm-up session; the label
is the concatenation across sleeves at whole-percent rounding of sleeve
budget; equality is tested on the joint string; and the short circuit sits
after the calls and before the summation (a monkeypatch test asserts merge
runs exactly once across three identical sessions). Gross cap 100 percent
with proportional truncation, applied after the label so truncation never
feeds the label. Drift resets on label transition only — a hundred-session
test emits exactly one set of targets.

**No-trade band implied by 5.1:** half a percent of sleeve budget per
component either side, which at a 25 percent budget is ±0.125 percent of
portfolio value. In practice the band is **inert**: the sleeves emit weights
only from {1, 1/2, 1/3}, which round to 100/50/33 — no two distinct terminal
states share a label, so transitions are exactly composition changes. The
band would bind only if a sleeve ever emitted near-continuous weights.

## Execution — modes, sizing, degeneracy

Signal at T close, fill at T+1 close, close-to-close accumulation; the
open-to-open arm switches the fill/accumulation series to AdjOpen inside one
parameterised path (`fill_series` selects the series; nothing downstream
branches on mode again). Sizing arm: fractional exact; truncate rounds
toward zero with the residual accruing to sleeve cash at DTB3 per 5.5.

**Degenerate-series detection result:** implemented as a general scan
(`degenerate_open_to_open`) — every ticker whose AdjOpen equals AdjClose on
all jointly-available rows is reported, so a second NAV-priced series cannot
pass silently. Not run against data/ this session per the prohibition;
synthetic tests cover single and multiple degenerate frames, null tolerance,
and near-miss defeat. For RYMFX specifically, degeneracy is already
established by the step 0 gate: Open == Close on all 4,901 rows, so
AdjOpen = Open × (AdjClose/Close) = AdjClose identically and the open-to-open
arm is degenerate for that one series. A test asserts the two modes coincide
exactly on such a frame.

Two flags:

- **DTB3 day-count convention is unspecified** in the register. Implemented
  provisionally as simple per-session compounding at rate/252, named
  constant, flagged here for a decision.
- **DTB3 is not present under data/.** Acquisition belongs to a later
  session; the execution layer takes the rate as an input.

## Parameter divergence record

`outputs/session-01/parameter-divergence.csv`: 30 rows, columns call_site /
source_value / spec_value / decision_id / classification / mapping_sites /
notes. Every row is classified deliberate re-specification (verified
programmatically: zero rows otherwise). **Nothing was found that looks like
an unrecorded difference.** The KMLM→RYMFX substitution is recorded as an
instrument change under 2.5, with the read-timing lag as its own row under
2.5a.

## Constructs in source not expressible under the spec

- **Date guards on instrument availability** (SVIX_LIVE, UVIX_LIVE,
  2022-03-30). Excluded from what may be taken from source. Implemented as
  availability switches on the state object — use SVIX/UVIX when its bar is
  available at the signal date, else SVXY/UVXY. This is source's own
  `has_data` logic (present in its UVIX branch) minus the hardcoded date,
  expressed through 1.9 availability. Flagged as the one place the
  implementation had to choose a mechanism the prompt did not dictate.
- **QuantConnect readiness semantics** (`is_ready`, `_T10_LATE`/`_T11_LATE`
  exemptions, `.get(t, 0)` / `.get(t, 50)` sentinel defaults). Replaced by
  the unavailable-input rule. The sentinels had the same observable effect
  as the threshold rule (unready reads false); the mechanism, not the
  behaviour, changed.
- **Market-on-open orders** and order-time `int()` share truncation.
  Replaced by the 4.1 execution arms and the 4.7 sizing arms.
- **Run configuration** (start 2020-01-01, $10,000 cash, IB margin model,
  SPY benchmark, five-day price-check logging). Backtest-window and
  brokerage properties, not strategy parameters; out of scope for the
  divergence CSV by design.

## Manifest staleness (continuation §5 — no action)

Verified in-session: `outputs/session-00e/manifest-truncated.csv` exists
with 39 rows carrying old and new hashes for all truncated files, and
`outputs/session-00e/pre-truncation-hashes/` preserves the original 00A and
00C manifests. **The authoritative hash record for current on-disk state is
00E's manifest-truncated.csv; the 00C manifest describes pre-truncation
state.** Nothing was repaired and nothing needed repair.

## Corrections carried forward (continuation §6)

- `src/config.py` was written during step 1, not step 4; the indicators and
  loader already needed it.
- The first `tr_index` implementation used pandas `cumprod`, whose
  `skipna=True` steps over a NaN and resumes the running level — an
  unavailable return silently read as a flat session, the same class of
  defect as the 00C zero-fill. Caught by a failing test, replaced with
  segment-wise restart (each contiguous run rebases to 1.0; safe because
  1.4 records the indicators as scale-invariant), and the test now pins the
  fix.
- Environment modification: pytest 9.1.1 installed into `.venv`; run
  byproducts under `.pytest_cache/` and `src/__pycache__/`. Probe and
  verification scripts live in the session scratchpad outside the repo.

## Test coverage

155 tests, all passing, all on hand-constructed synthetic input.

| File | Tests | Covers |
|---|---|---|
| test_indicators.py | 25 | Analytic RSI/SMA answers, 00C fidelity on clean input, null propagation, reseeding, input validation |
| test_data.py | 20 | 1.5 AdjOpen, 1.11 total return, 1.9 hole propagation and segment restart, 2.5a lag exactly once, loader validation |
| test_sleeves.py | 66 | Every branch of every sleeve to every terminal, threshold collapse boundaries, all nine pairwise raises by name, availability switches, crash-quantile semantics, budget sums |
| test_portfolio.py | 20 | Label format and order, 5.1 call-every-date and short-circuit ordering, 5.3 proportional truncation, 5.2 drift, warm-up skip, raise propagation |
| test_execution.py | 24 | Mode selection in one path, T+1 timing, fractional/truncate math, DTB3 accrual, raw-vs-fill price separation, degeneracy detection |

## Stop condition

Halted after this report. No backtest run, no performance statistic
computed, no commit made; the working tree is left dirty. The next
session's entry points: a concrete IndicatorState builder over the loader
(deliberately not written here, since constructing it invites running it),
DTB3 acquisition, and the day-count decision for 5.5.
