# Session 09 report — interior-gap treatment, financing harvest, proxy accuracy

Register updates applied and the gap treatment migrated to skip; financing
rates harvested from annual-report schedules for seven of twelve funds at
one fiscal year each; proxy accuracy measured wherever an index is actually
served; the fund schedule encoded as code with tests. No strategy return,
allocation, weight, or performance statistic; no sleeve function called
against real data; nothing acquired or frozen; nothing committed. Suite:
**199 tests passing** (189 after the gap migration + 10 schedule tests).

## Step 1 — register and code updates

| Constant | Change | Decision |
|---|---|---|
| `INTERIOR_GAP_TREATMENT` | added, `"skip"`, with the proportionality reasoning and the three disclosed ^NETR sessions in the comment; `validate()` pins it | 1.9 closed |
| `CRASH_THRESHOLD_PCT` | −10.0 → **−15.0**, with the stipulation reasoning (drawdown conventions vs point-to-point estimator) and session 06's 37.9% conditional-rate finding in the comment; −15 sits on `CRASH_THRESHOLD_GRID` so the membership guard holds | 6.10 re-closed |
| `SLIPPAGE_MODEL` | `"tier"` → `"uniform"`; `SLIPPAGE_TIER_MULTIPLIERS` and its guarded accessor and the non-decreasing validate() guard **removed entirely** (grep-verified config-internal) | 4.3 re-closed |
| `SIZING_MODE` | `"fractional"` → `"truncate"`, fractional retained as the alternative arm; the 4.6-reopens consequence recorded in the comment | 4.7 re-closed |

**The 7.10 product guard is unaffected**: none of these changes touches a
grid axis, and `validate()` — which runs on import in every test — passes
throughout. Confirmed.

**Interior-gap code change.** `src/indicators.py` (`wilder_rsi`, `sma`) and
`src/data.py` (`build_ticker_frame`'s return/tr_index construction) moved
from segment reseeding to skip: missing observations are dropped, the
recursion/window runs on the compressed series, the post-gap session
carries a multi-day return/change, and the gap date itself stays
unavailable. On null-free series the arithmetic is unchanged (the 00C
fidelity test still passes).

Tests changed, per the step's reporting requirement:

- **Replaced** `test_rsi_reseeds_after_a_gap` → `test_rsi_skips_gap_next_session_available`
- **Replaced** `test_rsi_segment_shorter_than_period_yields_nothing` → `test_rsi_short_tail_after_gap_stays_available`
- **Added** `test_rsi_multiday_change_enters_recursion_once` (holed series must equal the same series with the gap row physically deleted)
- **Replaced** `test_sma_null_propagates_through_the_window` → `test_sma_skips_gap_window_spans_it`
- **Added** `test_sma_200_one_day_gap_available_next_session` — the mandated 200-session case, asserting availability on the session after the gap
- **Replaced** (data) `test_interior_hole_propagates_through_tr_index` → `test_interior_hole_skipped_multiday_return`; `test_tr_index_does_not_use_the_s00c_zero_fill` → `test_tr_index_skip_differs_from_s00c_zero_fill`
- Unchanged and still passing under skip: leading-null seed placement, all-null input, 00C-defect pin, values-before-gap invariance, no-fill assertions.

One stated limitation recorded in the loader comment: a dividend whose
ex-date falls on a missing-close session would be dropped by the skip
construction; no held series has such a case (the only interior gaps on
disk are three ^NETR index sessions with no distributions).

## Step 2 — financing rate harvest (`financing-rates.csv`, `financing-coverage.csv`)

**81 unique swap rows harvested, seven funds, one fiscal year per trust.**
Extraction controls passed (synthetic schedule-line parse; every row
carries its provenance accession).

**Direxion, FY ending 2025-10-31** (N-CSR `0001133228-26-000012`):
- SPXL: 26 swaps, **stated rates "SOFR + 0.28%" to "SOFR + 0.99%", median
  +75bp**, across BNP, Goldman, BofA/Merrill, J.P. Morgan, UBS, Citibank,
  Barclays.
- FAS: 8 swaps, SOFR +65 to +80bp, median +75bp.
- The schedule's own footnote pins SOFR at 4.27% on the fiscal date.
- TECL, TECS, SOXL, SOXS, LABU: **present in the same document** (the
  narrative sections and the trust's 116 "Financing Rate" hits imply their
  schedules carry rates), but their schedule sections eluded the parser's
  header matching within bounded effort — recorded as a parser limitation,
  not an absence of disclosure.

**ProShares Trust, FY ending 2026-05-31** (N-CSR `0001398344-26-013617`):
a different disclosure convention — **flat rates with no reference rate
named** ("Rate Paid (Received)" column, footnoted as the floating financing
rate at fiscal date): TQQQ 8 rows, QLD 13, SQQQ 8, PSQ 11, SH 7.
Implied spread against the frozen DTB3 series (3.60% at 2026-05-29, the
step's bill-rate proxy, reported as such since no reference is named):
**long funds pay ~ bills +107–110bp median (TQQQ +109.5, QLD +107); short
funds RECEIVE ~ bills −62 to −77bp median (SH −62, PSQ −72, SQQQ −77)** —
the receive-side haircut being where the absorbed short borrow shows up,
consistent with 2.15's absorption finding.

**Coverage grid**: the two harvested fiscal years are in
`financing-coverage.csv` fund-by-fund; every earlier fiscal year for all
twelve funds is recorded as "not harvested (bounded effort)". Gaps are the
expected finding.

**What this implies for 2.14, stated without recommending**: usable
numbers exist — the disclosures are real, per-swap, and (at Direxion)
carry stated spreads over a named reference. But what this session
assembled is a **one-year snapshot per trust**, not a time series; the
ProShares side needs a reference-rate assumption to become a spread; and
five Direxion funds plus all earlier years remain unharvested. Whether a
usable time-varying anchor exists at annual resolution is therefore
"demonstrated in principle, one year deep in practice" — the closure call
is the register's.

## Step 3 — proxy accuracy (`proxy-accuracy.csv`, 15 rows)

Read at run time, not frozen: ^SP500TR, ^NDX, ^SOX, ^SP500-45, ^SP500-40
(daily history); ^XNDX, ^IXT, ^IXM, ^SPSIBI attempted and **not served at
any resolution — the weekly probes returned empty**, settling that the
"five-day" symbols provide no history at all (the session brief's hope that
weekly bars would bound the error is empirically closed off).

| Pair | Resolution | Ann TD | TD sd | Max roll-252 div | Corr | Status |
|---|---|---|---|---|---|---|
| SPY vs ^SP500TR (full 1995–2026) | daily | −0.06%/yr | 3.24% | 2.93% | 0.985 | **exact** |
| SPY vs ^SP500TR (2010+) | daily | −0.12%/yr | 0.98% | 1.03% | 0.998 | **exact** |
| SPY vs ^SP500TR (pre-2010) | daily | −0.01%/yr | 4.59% | 2.93% | 0.975 | **exact**, noisy prints |
| QQQ vs ^NDX (full) | daily | +0.40%/yr | 5.41% | 6.36% | 0.980 | price-basis |
| QQQ vs ^NDX (2010+) | daily | **+0.76%/yr** | 1.10% | 1.88% | 0.999 | price-basis: the dividend wedge |
| QQQ vs ^XNDX | — | — | — | — | — | **not measurable** |
| SMH vs ^SOX (2000–2021-08) | daily | −0.38%/yr | 7.89% | **19.34%** | 0.977 | price-basis + basket mismatch |
| SOXL/SOXS post-switch (ICE) | — | — | — | — | — | **not measurable** |
| XLK vs Tech Select Sector | — | — | — | — | — | **not measurable** |
| XLF vs all three FAS benchmarks | — | — | — | — | — | **not measurable** (all periods) |
| XBI vs ^SPSIBI | — | — | — | — | — | **not measurable** |
| context: XLK vs ^SP500-45 | daily | −0.36%/yr | 5.25% | 14.83% | 0.982 | related-not-identical |
| context: XLF vs ^SP500-40 | daily | +1.84%/yr | 5.05% | 8.05% | 0.984 | related-not-identical |

**Exact, approximation, and magnitude — the step's closing question:**

- **Exact and verified**: SPY for SPXL/SH — mean TD equals the fee; the
  only caveat is era-dependent daily close-print noise (25–33bp/day
  pre-2010 vs 5–9bp after), which is a floor on how tight 2.7's
  daily-resolution bands can be in the early sample.
- **Quantified approximation**: QQQ for the four NDX funds — the modern-era
  price-index wedge is +0.76%/yr (dividends minus fee); with ^XNDX
  unserved, the TR-index comparison is impossible free, but the wedge
  itself is measured and steady.
- **The problem pair, now with a number**: SMH for SOXL/SOXS — **max
  rolling-252 divergence 19.3%** against the PHLX price index across the
  pre-switch period. A 2.7 band on a synthetic built from SMH cannot
  distinguish construction failure from proxy artifact below roughly that
  scale on the worst windows; and after 2021-08-25 the true index is
  unmeasurable entirely.
- **Unmeasurable**: XLK, XLF, XBI against their exact benchmarks — the fee
  add-back cannot be verified for TECL/TECS, FAS (any period), or LABU with
  free sources; the related-sector context rows bound the neighbourhood
  (0.4–1.8%/yr TD, 8–15% max divergence) without being the benchmark.

## Step 4 — schedule encoding (`src/schedule.py`, `tests/test_schedule.py`)

The session 08 schedule is now code: `FUND_SCHEDULE` with one `Period` per
fund-term (all seventeen funds), `fund_terms(fund, date)` lookup, and the
**"on or about" qualifier carried as a field** on the SOXL/SOXS boundary
and both FAS boundaries (UVXY/SVXY boundaries are exact close-of-business
dates from the 8-K). Ten tests assert: contiguity and non-overlap from
inception to present (each period starts exactly one day after its
predecessor ends, only the final period open-ended), the multiple
boundaries land on the right sides of 2018-02-27/28, qualifiers survive
into the data, BTAL has no multiple, pre-inception lookups raise, and the
module agrees row-for-row with the frozen session 08 CSV.

## Anything that did not match expectation

1. **ProShares' N-CSR does not name a reference rate** — flat "Rate Paid
   (Received)" percentages only, unlike Direxion's explicit "SOFR + x%"
   and unlike ProShares' own Trust II 10-K wording. Disclosure practice
   differs by trust, which any 2.14 anchor must accommodate.
2. **Direxion's 48MB combined shareholder-report document** defeated two
   parser passes (schedules buried beyond caps; multi-page continuation
   headers; five funds' sections still unlocated despite their rates being
   demonstrably present). The harvest is honest-partial.
3. **The gated index symbols serve nothing at any interval** — the weekly
   fallback the session brief hoped for does not exist.
4. **SPY-vs-index daily noise is era-structured** (25–33bp/day pre-2010):
   even the exact pair constrains 2.7's early-sample band widths.
5. The proxy-control first fired on this era structure and then on Yahoo's
   2dp index rounding — both thresholds were recalibrated to assert
   machinery rather than data properties, and both recalibrations are
   visible in the script.

## Stop condition

Halted after this report. Nothing acquired or frozen; no backtest, no
performance statistic, no commit. Session writes: `src/config.py`,
`src/indicators.py`, `src/data.py`, `src/schedule.py`, test updates in
`tests/test_indicators.py` and `tests/test_data.py`, new
`tests/test_schedule.py`, `scripts/s09_proxy.py`, `scripts/s09_financing.py`,
and four CSVs plus this report under `outputs/session-09/`. Working tree
left dirty.
