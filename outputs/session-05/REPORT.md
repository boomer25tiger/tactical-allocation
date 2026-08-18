# Session 05 report — spread estimation, tier assignment, register updates

Config constants for 3.12/4.3/4.4 added; every ticker's entity verified; the
full panel audited for split-adjustment hazards with three as-traded
cross-checks; dollar volume and two spread estimators measured; tiers
assigned by a stated rule. No strategy return, allocation, weight, or
performance statistic; no sleeve function called against real data; nothing
committed. Suite: **187 tests passing** (174 entering + 13 for
`src/spread.py`).

**The proposed SLIPPAGE_TIER_MULTIPLIERS are at the end of this report and
were NOT written into config.**

## Step 1 — config (src/config.py)

| Constant | Value | Decision | Status |
|---|---|---|---|
| `SMH_PRE2013_ACCRUAL_PCT` | 1.5 | 3.12 | closed provisionally; comment records the measured 1.31% net as a lower bound |
| `SMH_ACCRUAL_GRID` | (0.0, 1.0, 2.0) | 3.12 | sensitivity arm |
| `SLIPPAGE_BASE_GRID_BP` | (0, 5, 10, 20, 35, 50) | 4.4 | closed; Zarattini 2025 anchor at 10 noted; validate() requires the anchor present |
| `SLIPPAGE_TIER_MULTIPLIERS` | None | 4.3 | placeholder; `get_slippage_tier_multipliers()` is the only sanctioned read path and raises while unset (validate() cannot intercept attribute reads, so the guarded accessor is the enforcement mechanism; validate() checks well-formedness once set) |
| `SLIPPAGE_MODEL` | "tier" | 4.3 | closed; "volatility_scaled" pre-registered alternative |

**Product guard confirmation:** the slippage base grid and the SMH accrual
grid are implementation/sensitivity dimensions under 9.8 and are
deliberately absent from the 7.10 product. validate() passes unchanged:
`4 × 5 × 10,935 = 218,700`. Confirmed by import and by the full suite.

## Step 2 — ticker entity verification

Positive control passed: SPY resolves to "State Street SPDR S&P 500 ETF
Trust" before any other verdict was read. Result: **36 of 36 tickers
resolve to the expected entity** — the source universe funds plus RYMFX
("Guggenheim Managed Futures Strategy P") and KMLM ("KraneShares Mount
Lucas Managed Futures Index Strategy ETF"). No NSM/SNDK-class reuse exists
inside the frozen universe. Reference table:
`outputs/session-05/ticker-entity-check.csv`.

One false positive caught and fixed in-session: SPXL resolves to "Direxion
Daily **S&P500** Bull 3X Shares" (no space), which my keyword "S&P 500
Bull" missed. The keyword was widened; the entity was always correct.

## Step 3 — split-adjustment audit

`outputs/session-05/split-audit.csv`: per ticker, every split event with
date and ratio, and the cumulative factor from each year 1995–2026 to the
present. **23 of 36 tickers carry splits; 20 have a post-2015 split**, so
most of the panel's stored history diverges from as-traded levels. The
extremes: SOXS cumulative 2.08e-8 from 2015 (ten reverse splits), SQQQ
1e-4, TECS 5e-6, versus TQQQ 48×, SOXL 60×, TECL 40×, QLD 32× forward.
One pseudo-event: XLF's 1.231 "split" on 2016-09-19 is Yahoo's adjustment
for the real-estate sector spin-off, not a share split.

Cross-checks (`split-crosschecks.csv`), stored close × cumulative future
splits vs a stated as-traded anchor, plus a memory-free internal check that
the implied as-traded price falls by the split ratio across the next
boundary:

| Ticker | Date | Stored × factor | Implied | Anchor ± band | Verdict | Boundary |
|---|---|---|---|---|---|---|
| SMH | 2023-05-04 | 121.805 × 2 | 243.61 | 249 ± 15 | PASS | 1.959 vs 2 — consistent |
| TQQQ | 2021-01-20 | 24.745 × 8 | 197.96 | 198 ± 15 | PASS | 1.951 vs 2 — consistent |
| SOXL | 2021-02-26 | 38.711 × 15 | 580.66 | 610 ± 60 | PASS | 16.56 vs 15 — consistent (−9.4% split-day move) |

Anchor source: contemporaneous split coverage, approximate. **Two errors of
my own caught during this step, both reported rather than buried:** the
first TQQQ anchor (~$100) was the widely reported *post*-split level
misremembered as pre-split — the stored data was internally consistent all
along and the corrected anchor (~$198) passes; and the boundary-consistency
check's first formulation multiplied by the split ratio instead of dividing,
flagging all three tickers as inconsistent even while two agreed with
external anchors to 2% — the formula was corrected and all three read
consistent. Both are instances of the checker needing its own control.

Stored adjusted prices remain correct for return computation under 1.4; the
hazard is only in reading them as as-traded levels — which is exactly what
both session 04 defects did.

## Step 4 — dollar volume

`outputs/session-05/dollar-volume.csv`: median, p10, p90 of raw close ×
volume, full history and by calendar year, with session counts and date
ranges. Full-history medians span five orders of magnitude: SPY $16.7B,
QQQ $4.0B, XLF $1.06B … QQQE $1.7M, BTAL $0.6M, and RYMFX $0 (mutual fund,
no volume reported).

**A third split artifact, found here:** Yahoo scales historical *volume* by
the inverse split factor and stores integers, so heavy reverse-splitters
have early volumes rounded to literal zero — **SOXS has zero recorded
volume on 57.7% of its sessions and TECS on 28.6%** (SQQQ 0.7%; every other
ticker 0%). The claim that split basis cancels in the price × volume
product fails under integer truncation at extreme cumulative factors
(SOXS 2.08e-8). SOXS's $0 median and TECS's depressed median are artifacts
of the stored record, not measurements of liquidity; both names sit in tier
3 under both ranking criteria regardless, so the assignment is unaffected,
but their dollar-volume *numbers* should not be quoted.

## Step 5 — spread estimation

`src/spread.py` implements Corwin-Schultz 2012 with the three published-
methodology treatments stated in code and here: missing high/low carried
from the most recent good prior day; the overnight adjustment applied
(additive shift of day t+1's range by the gap beyond day t's close);
negative estimates reported under all three treatments — zeroed, unchanged,
excluded — with the treatment-independent negative rate alongside.
Abdi-Ranaldo 2017 (close/high/low) is the robustness arm. Both run on the
stored OHLC path, whose uniform split basis cancels in every ratio. 13 unit
tests pin the closed form: a pure bid-ask bounce series recovers the true
spread to 1e-10 across three spread levels; H=L=C gives zero; a strong
trend drives estimates negative; the overnight shift rule is matched
against a hand-computed closed form.

Outputs: `spread-estimates.csv` (per ticker × window × treatment, full,
by-year, and the two stress windows) and `spread-timeseries.csv` (daily CS
and AR series, all 36 tickers).

Full-history CS medians (zero treatment) run from BIL 1.3 bp / KMLM 2.0 /
QQQE 2.3 / BSV 2.4 through SPY 14.6 / QQQ 20.0 to the leveraged complex:
TQQQ 41.2, SQQQ 43.6, FAS 47.9, SOXS 55.2, SOXL 58.7, **LABU 113.2**.

**Negative-estimate rates are high and structural: 32–46% of windows for
most equity names** (VOOG 45.7%, IEF 45.1%, TLT 44.4%), consistent with the
published ~30% and concentrated, as published, on volatile days. Per-year
rates are in the CSV.

**The zero treatment collapses thin names to zero.** BTAL's zero-treatment
median is 0.0 bp while its exclude-treatment median is **15.2 bp**; KMLM
2.0 vs 25.5; QQQE 2.3 vs 32.6. The mechanism: thin early trading produces
many H = L sessions (zero range → zero estimate) and many negative windows;
flooring plus zero-range mass drags the median to zero. The downward bias
the prompt warned about is not a footnote here — it is first-order for
exactly the least liquid names the tiers exist to capture. Both treatments
are in the CSV; the tier construction below states which it used.

Stress windows behave as expected — spreads widen multiples: COVID window
(35 tickers alive) SPY 70.7 bp, SMH 111.7, TQQQ 188.2, SPXL 226.4, SOXL
288.4, SOXS 401.3 vs single-digit BIL/AGG; GFC window (26 alive) QLD 147.1,
SMH 108.4, TECS 97.4. AR agrees moderately with CS (rank correlation 0.69
on full-history medians), with the same zero-mass artifact on thin names.

## Step 6 — tier assignment

**Rule, stated before application:** rank the 36 tickers by median daily
dollar volume (descending) and by CS zero-treatment median spread
(ascending), and assign each ticker to the tercile — 12/12/12 — of the
average of those two ranks, ties broken by the dollar-volume rank.

`outputs/session-05/tier-assignment.csv` has the full table.

- Tier 1: TLT SPY BND QQQ AGG XLY XLF IEF BSV BIL XLK SMH
- Tier 2: XLP TQQQ BTAL XBI SH KMLM RYMFX VTV QQQE VOOG SQQQ SPXL
- Tier 3: QLD IBB VOX VOOV IOO PSQ FAS LABU TECL SOXL TECS SOXS

**The two ordering criteria disagree for 30 of 36 tickers** (all but SH,
VTV, IBB, TECL, TECS, SOXS). The disagreement has structure: high-volume
leveraged funds (TQQQ, SQQQ, SPXL) rank top-tercile on dollar volume and
bottom-tercile on estimated spread, while thin vanilla funds (VOOV, VOX,
QQQE, KMLM) do the reverse. That is the step 7 leveraged-fund limitation
made visible — the estimator reads a 3× fund's volatility as spread — plus
the zero-treatment collapse on thin names. Per instructions, disagreements
are reported and the rule decided; none was resolved by preference.

**RYMFX is a degenerate input on both criteria** — no reported volume
(rank 35.5 of 36) and an H = L = C NAV series giving a zero spread
(rank 1.5 of 36) — and the composite rule averages these into a tier 2
placement. That placement is an artifact of averaging two meaningless
ranks, flagged here; under the instructions it stands as the rule's output.

Multipliers from tier median spreads (zero treatment, the CS baseline):

| Tier | Median spread bp | Multiplier (unrounded) | Multiplier (rounded) |
|---|---|---|---|
| 1 | 11.78 | 1.0000 | **1.0** |
| 2 | 11.25 | 0.9546 | **1.0** |
| 3 | 34.60 | 2.9372 | **2.9** |

Tier 2's median sitting *below* tier 1's is the zero-collapse artifact
(BTAL/RYMFX/KMLM/QQQE zeros inside tier 2). Sensitivity under the exclude
treatment, same membership: tier medians 37.3 / 36.7 / 121.6 bp,
multipliers (1.0, 0.98, 3.26) — the same shape: tiers 1 and 2
indistinguishable, tier 3 roughly 3×.

## Step 7 — known limitations, stated

1. **Downward bias.** The CS estimator is downward biased, concentrated on
   assets that do not trade continuously, with underestimation increasing
   from the least to the most volatile assets. Validation against TAQ
   effective spreads gives average time-series correlations around 0.53
   (1993) and 0.46 (2006): moderately, not strongly, accurate.
2. **Leveraged and inverse funds violate the variance-scaling assumption.**
   The estimator separates volatility from spread via square-root-of-time
   scaling, and a daily-reset fund's two-day range is not the simple
   compounding of its one-day ranges. Violated on TQQQ, SOXL, SPXL, TECL,
   FAS, LABU, QLD, SQQQ, TECS, SOXS among the 36 (and on UVXY, UVIX, SVIX,
   SVXY when those series arrive — they are not yet in the panel).
   Estimates for the ten present names are reported WITH this caveat, not
   omitted; their "spreads" are inflated by unremoved volatility.
3. **Volatility ETPs gap overnight**; the CS overnight adjustment handles
   gaps by construction (the additive shift) rather than natively.
4. **Ratios survive the bias better than levels**, since the bias is
   roughly common across tiers — which is why the multipliers come from
   tier ratios while the base level remains swept (4.4).
5. Added by this session's findings: the zero treatment collapses thin
   names' medians toward zero (BTAL 0.0 vs 15.2 bp), the SOXS/TECS volume
   record is rounding-destroyed, and RYMFX is degenerate on both tiering
   criteria.

## Anything else that did not match expectation

- The 30-of-36 criteria disagreement rate — expected some, not five sixths.
  Its structure (leverage inflating spread ranks, zeros deflating them) is
  the informative part.
- The three self-caught errors: SPXL keyword false positive, the TQQQ
  anchor mis-recall, and the boundary-check formula bug.
- Tier 2's median spread below tier 1's, and the resulting 1.0 multiplier
  for tier 2 under both treatments.

## Proposed SLIPPAGE_TIER_MULTIPLIERS — for confirmation, not written

**Proposed: `SLIPPAGE_TIER_MULTIPLIERS = (1.0, 1.0, 2.9)`** — zero-
treatment tier-median ratios, rounded to one decimal per the step 6 rule
(unrounded 1.0000 / 0.9546 / 2.9372; tier 2 floored to tier 1's 1.0 since a
sub-unity multiplier for a less liquid tier is an artifact of the zero
treatment, and validate() requires non-decreasing multipliers).
Exclude-treatment sensitivity: (1.0, 0.98, 3.26). Config still carries
`SLIPPAGE_TIER_MULTIPLIERS = None`; the guarded accessor raises; nothing
was written. Tier membership as tabulated above, RYMFX flag attached.

## Stop condition

Halted after this report. No backtest, no performance statistic, no
commit. Session writes: `src/config.py` (step 1), `src/spread.py`,
`tests/test_spread.py`, `scripts/s05_entity.py`, `scripts/s05_liquidity.py`,
and seven CSVs plus this report under `outputs/session-05/`.
