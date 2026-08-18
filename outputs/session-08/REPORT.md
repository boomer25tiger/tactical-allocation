# Session 08 report — fund schedule, index inventory, NETR acquisition

Two-pass fund retrieval completed with every change confirmed from primary
filings; benchmark/underlying inventory with reachability flags; financing
disclosure recorded; one series acquired and frozen (^NETR). No strategy
return, allocation, weight, or performance statistic; nothing committed.
Positive controls: EDGAR FTS had to find a known-present filing (the Rydex
497 of 2022-03-31) before any negative was read; the Yahoo symbol probe had
to find known-served ^NETR before any EMPTY was trusted.

## Pass A — current terms (`fund-current-terms.csv`)

All seventeen funds resolved: issuer, frozen first-trade date (13 in the
panel; the four VIX funds are not), stated inception, current multiple,
current benchmark, and the source filing. Highlights: the five ProShares
1940-Act funds (TQQQ 3x, QLD 2x, SQQQ −3x, PSQ −1x on Nasdaq-100; SH −1x
on S&P 500) from the 2026-07-23 485BPOS; the seven Direxion funds from the
2026-08-10 485BPOS plus their change 497s; UVXY 1.5x / SVXY −0.5x on the
S&P 500 VIX Short-Term Futures Index from the 8-K and the 2026 10-K; SVIX
−1x Short VIX Futures Index / UVIX 2x Long VIX Futures Index from
Volatility Shares' 2026-06-26 485BPOS; **BTAL has no multiple** — an
anti-beta long/short strategy on the Dow Jones U.S. Thematic Market
Neutral Anti-Beta Index, recorded as such (2.6 routes its validation to
the AQR BAB factor).

## Step 2 — which funds changed

**The Direxion action effective after the close on 2020-03-31 touched none
of the seventeen.** The 497 of 2020-03-20 (`0001193125-20-080736`) and the
restated prospectus of 2020-04-01 (`0001193125-20-092983`) identify the
ten funds from their SGML series lists: **BRZU, DRIP, DUST, ERX, ERY,
GUSH, JDST, JNUG, NUGT, RUSL** — gold miners, energy, oil & gas, Brazil,
Russia — all 3x/−3x to 2x/−2x. The effective date is confirmed from the
filing itself: the April 1 prospectus states performance "prior to
April 1, 2020, reflects the Fund's previous daily leveraged investment
objective ... of 300% of the Index." One wrinkle the filings expose that
secondary sources miss: the March 20 supplement had projected an effective
date of **May 19, 2020**, and the change was then accelerated to the
March 31 close. **No reversal found**: a probe for post-2020 filings
reinstating "Bull 3X" names for those funds returns only backward-looking
NPORT/N-CEN period documents.

**SVXY and UVXY, confirmed from the 8-K** (`0001193125-18-059052`, dated
2018-02-26): effective **as of close of business on February 27, 2018**,
UVXY moved from 2x to 1.5x and SVXY from −1x to −0.5x of the S&P 500 VIX
Short-Term Futures Index.

**Changes found beyond the two named events** (the "change nobody
expected" clause):

1. **SOXL/SOXS benchmark change**: PHLX Semiconductor Sector Index → ICE
   Semiconductor Index, effective on or about **2021-08-25** (497 of
   2021-06-21, `0001193125-21-195149`). Multiples unchanged.
2. **FAS changed benchmark twice in six months**: Russell 1000 Financial
   Services Index (restyled "Russell 1000 Index – Financials" by the
   provider's ICB migration) → **Russell 1000 Financials 40 Act 15/22.5
   Daily Capped Index** on or about **2022-02-28** (497 of 2021-12-30,
   `0001193125-21-370635`), then → **Financials Select Sector Index** on
   or about **2022-08-01** (497 of 2022-06-02, `0001193125-22-166266`).
   Multiple 3x throughout.
3. Verified constant against the suspicion of parallel changes: TECL/TECS
   on the Technology Select Sector Index and SOXL on PHLX/ICE and SPXL on
   the S&P 500, spot-checked at the 2013, 2016, and 2019–2023 annuals —
   the "Russell 1000 Technology Index" hits in Direxion filings belong to
   other funds, not TECL.

## Pass B — the schedule (`fund-schedule.csv`)

Long form, one row per fund-period, 24 rows: multi-period rows for SOXL,
SOXS (2 each), FAS (3), UVXY, SVXY (2 each), and single-period rows for
the other twelve. **Contiguity holds: every fund's periods are contiguous
and non-overlapping from inception to the present with no gaps.** Two
stated conventions: period boundaries at the filing-stated effective date
(close-of-business boundaries noted in the notes column), and the two
Direxion index switches carry the filings' own "on or about" qualifier.
FAS's first period notes the provider-side ICB renaming inside an
unchanged index family, distinct from the two fund-side switches.

## Step 4 — index inventory (`index-inventory.csv`)

20 entries covering every benchmark in the schedule plus every missing
underlying from session 07's enumeration. Reachability, checked
symbol-first per the ^NETR lesson:

- **Free with full history**: ^SP500TR (S&P 500 TR, 1988+), ^NDX (price,
  1985+), ^SOX (PHLX price, 1994+), **^SHORTVOL (Cboe Short VIX Futures
  Index, 2005-12-20+** — SVIX's underlying with sixteen years of
  pre-inception history, a notable find), ^SP500-45/-40 (S&P 500 IT and
  Financials sector price indices, 1993+ — related to but NOT identical to
  the Select Sector indices).
- **Symbol exists, daily history not served (effectively gated)**: ^XNDX,
  ^IXT, ^IXM, ^SPSIBI, ^SPVXSP, ^LONGVOL, ^DJTMNAB, ^SP500G, ^SP500V,
  ^SP500PG, ^SP500PV — all confirmed alive at 5-day resolution only.
- **Gated or useless**: ICE Semiconductor (^ICESEMI serves 204 rows from
  2025-10), the Russell financials indices, Bloomberg bond indices.
- **Proxy paths already frozen or freely pullable, recorded without
  acquiring**: XLK/XLF/XBI/SMH for the sector and semiconductor
  benchmarks (2.7's proxy framework), AGG for the BND gap, IVW/IVE (2000
  listings) as VOOG/VOOV proxy candidates, SHY for the BSV gap.
- **SVIX/UVIX representation** (no frozen series; session 07 showed their
  absence pins the T10 and S3 vol legs to SVXY/UVXY): options recorded —
  2.3's VX construction from the held vx-cm30 series, or listed pulls with
  2022+ history, with ^SHORTVOL available free for SVIX validation.

## Step 5 — financing disclosure (`financing-disclosure.md`)

**No prospectus states a numeric financing spread** (zero matches in the
ProShares Trust 485BPOS; qualitative-only mentions in Direxion's).
**Year-end per-swap floating financing rates ARE disclosed** — but only in
shareholder-report schedules (read directly in the PT2 10-K; the same
convention exists in N-CSRs). **Borrow on short swaps is absorbed into the
swap interest leg by the filings' own language** ("will also include the
cost of borrowing for short swaps") — not separately visible. And 2.15's
class premise fails structurally: the five inverse-equity funds are
swap-based (borrow absorbed) while SVXY/SVIX are futures-based (no swap
borrow exists; the economics live in the futures basis the 2.3
construction models). Reported without inferring any figure.

## Step 6 — ^NETR acquired and frozen

- Pulled `^NETR` (yfinance 1.6.0), 5,024 rows 2006-08-21 → 2026-08-14;
  the 1.14 truncation dropped the 2026-08-15+ tail from the raw pull.
- Gates passed before writing: first observation 2006-08-21 (≤ required),
  last ≥ 2026-08-14, zero rows off the SPY calendar.
- **Interior gaps: exactly the three sessions session 07 found —
  2007-02-26, 2008-10-27, 2010-07-14 — and no others.** Retained as
  explicit null rows (the frozen frame is reindexed to the SPY-calendar
  span, so the gaps are visible nulls rather than absent dates), per 1.9.
- `data/raw/index/NETR.parquet`: 5,027 rows, 3 nulls, 228,965 bytes,
  SHA-256
  `61b575112ca246144feedc36aec3fc2fbe419cc5de5296a3ccff7f574ef44f8f`
  (shell cross-checked). Manifest row in
  `outputs/session-08/index-manifest.csv` (00C format with null_count and
  library_version, as established in session 02). The freeze script
  refuses overwrite per 1.1.

**1.9 is now live — stated prominently.** These are the first genuine
interior gaps in any series the study holds. Session 01's audit found zero
across the ETF panel, which made the reseeding-versus-skip question moot;
it no longer is. QQQE's synthetic reconstruction under 2.2 depends on this
series, and the segment-reseeding behaviour currently implemented in
`src/indicators.py` and `src/data.py` would blank indicator windows after
each gap if invoked as-is. **A 1.9 interior-gap decision is required
before the synthetic build runs.** Not decided here.

## Decision ledger

- **3.11 — unblocked.** The complete per-date multiple and benchmark
  schedule exists with filing-grade sources, which is what 3.11 needed;
  its dependents 2.12, 2.14, and 2.15 stop being blocked on it.
- **2.12 — unblocked** on the schedule (date-dependent multiples for the
  synthetic build: the 2018-02-27 close boundary for UVXY/SVXY is the only
  multiple change in the seventeen; benchmark boundaries for SOXL/SOXS and
  FAS are in the file).
- **2.14 — evidence in.** No stated spread exists in prospectuses;
  year-end schedule snapshots are the only numbers. The finding the step
  anticipated ("filings do not disclose usable financing terms") holds at
  the prospectus level, with the schedule-harvest caveat recorded. Closure
  not recommended here.
- **2.15 — evidence in.** Absorption confirmed by filing language for the
  swap-based five; the short-vol funds are structurally a different class
  (futures, no swap borrow). Closure not recommended here.
- **3.9 — dissolved and executed.** The index is frozen.
- **1.9 — reopened in practice** by the three explicit nulls now on disk;
  blocks the synthetic build until decided.
- **2.7 — sharpened.** Validation windows for synthetic SOXL/SOXS and FAS
  must respect the benchmark boundaries (2021-08-25; 2022-02-28 and
  2022-08-01), and UVXY/SVXY synthetics must switch multiple at the
  2018-02-27 close, or the bands will register failures whose cause is the
  schedule, not the construction.

## Flags — unreachable or ambiguous, not papered over

- The four VIX funds' stated inception dates (2011-10-03; 2022-03-28) come
  from issuer/annual-report context, not re-verified line-by-line from
  original registration statements this session.
- Direxion's two index-switch dates carry the filings' own "on or about"
  qualifier; the exact first trading session on the new index is not
  independently confirmed.
- SAI documents and N-CSR schedules were not separately harvested
  (bounded); see the financing memo's caveats.
- TECL/TECS constancy rests on annual spot-checks (2013, 2016, 2019–2023)
  rather than a year-by-year sweep of every annual since 2008.

## Stop condition

Halted after this report. Acquired nothing beyond ^NETR. No backtest, no
performance statistic, no commit. Session writes: four CSVs, two MDs, the
manifest, `data/raw/index/NETR.parquet`, and this report. Working tree
left dirty.
