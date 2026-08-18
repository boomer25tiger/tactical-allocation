# Session 06 report — tier reassignment and section D structural measurements

Tier assignment redone on dollar volume alone; four structural
branch-condition measurements taken. Conditions were evaluated directly on
indicator series with 1.9 semantics (unavailable threshold input reads
false); no sleeve function was called, no weight formed, no performance
statistic computed; nothing committed. Positive controls: the episode
counter on a synthetic mask, and SPY RSI14 > 70 confirmed to hold on 708
sessions before any zero co-occurrence was trusted.

**The proposed SLIPPAGE_TIER_MULTIPLIERS are at the end and were NOT
written to config.**

## Step 1 — tier reassignment v2 (`tier-assignment-v2.csv`)

Assignment by median dollar volume alone, terciles of the 33 rankable
names. Exclusions, recorded with reasons:

- **RYMFX** — excluded from tiering entirely: never held (signal input
  only, 2.5), so it takes no slippage; no volume and no intraday range.
- **SOXS, TECS** — excluded from the dollar-volume computation (stored
  volume is rounding-destroyed on 57.7% / 28.6% of sessions), assigned
  directly to the thinnest tier, matching what either criterion said in
  session 05.

| Tier | Members | Boundary |
|---|---|---|
| 1 | SPY QQQ XLF TLT TQQQ SMH XLY SQQQ XLK XBI XLP | ≥ ~$237M median daily |
| 2 | SPXL QLD AGG BND IBB FAS IEF LABU SH BSV SOXL | ~$88M – $225M |
| 3 | VTV BIL TECL PSQ VOOG VOX IOO VOOV KMLM QQQE BTAL + SOXS TECS (direct) | ≤ ~$71M |

Tier1/2 boundary falls between $236.9M and $225.0M; tier2/3 between $87.9M
and $71.4M.

Multipliers as tier-median CS spread ratios, both treatments, no flooring
and no hand-setting:

| Treatment | Tier medians (bp) | Multipliers unrounded | Rounded |
|---|---|---|---|
| zero | 20.04 / 24.26 / 7.06 | 1.0000 / 1.2105 / 0.3524 | 1.0 / 1.2 / 0.4 |
| exclude | 57.43 / 70.19 / 35.03 | 1.0000 / 1.2223 / 0.6099 | 1.0 / 1.2 / 0.6 |

**Collapse test:** tier 2 sits 21.1% (zero) and 22.2% (exclude) above tier
1 — *outside* "roughly 20 percent" under both treatments, by one to two
percentage points on a deliberately rough threshold. Under the stated rule
the data keeps three tiers; the marginality is flagged for the confirmer
rather than resolved here.

**The measured tier-3 multiplier is below 1 under both treatments.** This
is the session-05 estimator structure resurfacing under the new
assignment: tier 1 now contains the high-volume leveraged complex (TQQQ,
SQQQ, plus SMH/XBI), whose CS estimates are inflated by the violated
variance-scaling assumption, while tier 3 collects the thin vanilla funds
whose estimates the zero treatment collapses and whose sparse trading the
estimator underestimates. The premise that the estimator's bias is roughly
common across tiers — the reason ratios were preferred to levels — fails
when tier composition differs systematically by fund type: the bias is
leverage-correlated, and leverage now sorts into tier 1. The numbers are
reported as measured; what they imply is stated in the closing section.

## Step 2 — T10 cascade co-occurrence (`t10-cascade-cooccurrence.csv`, informs 6.13)

Canonical (RSI 14, oversold 30), 7,957-session calendar:

| Dips holding | Sessions | Fraction |
|---|---|---|
| 0 | 6,051 | 97.39% (of evaluable-window sessions incl. pre-listing zeros by 1.9) |
| 1 | 97 | 1.56% |
| 2 | 33 | 0.53% |
| 3 | 20 | 0.32% |
| 4 | 12 | 0.19% |

Conditional on the overbought disjunction not firing — the figure that
bears on 6.13 — **two or more oversold conditions hold on 65 sessions,
1.05% of not-overbought sessions**. Pair co-occurrence (canonical, joint
sessions; diagonal = solo totals): TQQQ∩SPXL 41, SPXL∩LABU 30, SOXL∩SPXL
29, TQQQ∩SOXL 23, SOXL∩LABU 21, TQQQ∩LABU 21 — against solo totals TQQQ
52, SOXL 56, SPXL 78, LABU 86. Reach rates: overbought 100%, TQQQ dip
78.1%, SOXL 77.4%, SPXL 77.0%, LABU 76.7%, trend switcher 76.1% — the
cascade's lower steps are evaluated on three quarters of sessions.

Grid endpoints (2+ co-occurrence, conditional on not-overbought):

| (RSI, oversold) | Sessions | Fraction |
|---|---|---|
| (7, 20) | 49 | 1.04% |
| (7, 40) | **809** | **17.15%** |
| (28, 20) | **0** | **0.00%** |
| (28, 40) | 218 | 2.91% |

The co-occurrence rate is a property of the grid point, not the design: at
(28, 20) the ordering is exactly inert (nothing ever co-occurs), at (7, 40)
one in six not-overbought sessions has multiple dips live and the ordering
decides among them routinely.

## Step 3 — dip ladders in the other sleeves (`dip-ladder-cooccurrence.csv`, informs 6.14)

**Source verification first.** Every `<`-comparison oversold site outside
T10's cascade (grep with positive control on the known L193 site): the
PSQ < 35 checks at L158/L175 (single tests inside the bear helpers, not
ladders), T11's pair at L230–231, S2's at L266–267, and S3's at L294. **The
register's three-pair reading is complete** — no other dip ladder exists in
source — with one structural nuance the register misses: **S3's "pair" is a
short-circuit disjunction routing both conditions to the same ticker
(SOXL), so its ordering can never matter, by construction.** Only T11's
(TQQQ→TQQQ vs SPY→SPXL) and S2's (TQQQ→TECL vs SOXL→SOXL) pairs have
distinct targets for 6.14 to order.

Canonical co-occurrence, conditional on the branch being reached (T11:
tier-1 not fired; S2: TQQQ below its 200-session SMA; S3: bear state,
votes < 3):

| Sleeve | Pair | Both hold | Frac of all | Both ∧ reached | Frac of reached |
|---|---|---|---|---|---|
| T11 | TQQQ & SPY | 39 | 0.49% | 39 | 0.58% |
| S2 | TQQQ & SOXL | 23 | 0.29% | 21 | 0.43% |
| S3 | QQQ & SMH | 52 | 0.65% | 51 | 1.30% |

Grid endpoints (fraction of reached): the same pattern as step 2 — (28,20)
is identically zero for all three pairs; (7,40) reaches 11.4% (T11), 6.2%
(S2), 17.7% (S3).

## Step 4 — T11 bear sub-model agreement (`t11-submodel-agreement.csv`, informs 6.18)

**Source verification: the stated premise is wrong in one respect.** The
lower bodies below the crash test are verbatim identical (the
TQQQ-above-SMA20 block and the IEF/PSQ else block match line for line),
**but bond_baller opens with `if r20["TLT"] > r20["PSQ"]: return "QQQ"`,
which has no counterpart in feaver_bear** (source L156 vs L165–180). Two
separations exist, not one: the crash test (feaver-only) and the TLT/PSQ
head (bond-only). Duplication requires both to be quiet.

Measurement at canonical parameters (evaluable where SPY's SMA200 exists;
routing determinate where the taken path's pairwise inputs exist — PSQ/SH
availability makes determinate-bear effectively start mid-2006):

- Bear branch reached: **1,682 sessions (21.1% of calendar)**; routing
  determinate on 963, indeterminate on 719 (pre-2006 pairwise
  unavailability).
- **The sub-models agree on 242 of 963 determinate-bear sessions — 25.1%.
  They differ on 74.9%.** The "50/50 split that holds one position while
  appearing to hold two" is the minority case on this history.
- Disagreement pairs (bond, feaver): (QQQ, PSQ) 232, (QQQ, TQQQ) 178,
  (QQQ, QLD) 114, (SQQQ, QLD) 100, (SQQQ, BTAL) 46, (PSQ, QLD) 23,
  (QQQ, SQQQ) 14, (QQQ, BTAL) 6, (PSQ, BTAL) 6, (TQQQ, BTAL) 2. The QQQ
  rows — 544 sessions, 75% of disagreements — are the TLT/PSQ head firing.
- **Crash fires on 37.9% of bear-reached sessions** (637 of 1,682) —
  against session 03's ~9% unconditional rate: bear regimes and 60-session
  drawdowns co-occur heavily, so the crash separation is four times more
  live conditionally than the unconditional figure suggested.
- The TLT/PSQ head fires on 32.3% of bear-reached sessions.

## Step 5 — tier-two overbought firing (`t11-tier2-firing.csv`, informs 6.3 and 7.4)

Panel maximum RSI across SPY/IOO/TQQQ/VTV/XLF per 6.17, strict
greater-than, fractions of evaluable sessions:

| Threshold | RSI 7 | RSI 14 | RSI 28 |
|---|---|---|---|
| >70 | 2,579 (567 ep) | 1,252 / 15.8% (292 ep) | 345 (76 ep) |
| >75 | 1,645 (455 ep) | 435 / 5.5% (123 ep) | 72 (15 ep) |
| >80 | 837 (275 ep) | 114 / 1.4% (46 ep) | 16 (6 ep) |
| >85 | 322 (136 ep) | 23 / 0.29% (8 ep) | **0 (0 ep)** |

Argmax attribution at period 14: **TQQQ supplies the panel maximum most
often** (394 of 1,252 firing sessions at 70; 49 of 114 at 80), SPY second
(344; 33), then VTV, XLF, IOO — IOO nearly never drives it (132; 5). The
6.17 max-reading writeup should name TQQQ as the usual driver, with the
caveat that TQQQ only exists from 2010.

## What the measurements make moot, stated without recommending

- **T10 ordering (6.13):** live but thin at canonical — 65 conditional
  sessions in 27 years — identically inert at (28, 20), and routinely
  decisive at (7, 40). Any closure of 6.13 is a statement about the grid
  region, not a single rate.
- **Dip ladders (6.14):** S3's pair is order-inert by construction and can
  be dropped from 6.14's scope; T11's and S2's pairs order real but rare
  conflicts at canonical (0.4–0.6% of reached sessions), zero at (28, 20).
- **Tier two (6.3 / 7.4):** live at canonical (46 episodes at 80) and at
  period 7 everywhere; at period 28 the +15 offset (85) **never fires** —
  a dead parameter at that grid edge — and +10 (80) fires 6 episodes in 27
  years. The 7.4 sweep spans live-to-decoration depending on the period
  axis.
- **6.18:** the premise "identical below the crash test" is false as
  stated (TLT/PSQ head); with both separations live, duplication is 25%,
  not the norm. Conditional crash incidence (37.9%) is the governing
  figure, not session 03's unconditional 9%.

## Anything else that did not match expectation

- Step 5's argmax needed guarding against all-NaN early rows (pre-2000
  panel sessions) — a mechanical fix, no measurement effect.
- The tier-3 sub-unity multiplier under both treatments (structure
  explained in step 1) — the sharpest surprise of the session, and the
  second consecutive tiering scheme in which the CS estimator's
  leverage/thinness biases dominate the tier medians.
- Step 4's indeterminate count (719 of 1,682 bear sessions) — the
  measurement window for sub-model agreement is effectively 2006-07
  onward, not the full calendar.

## Proposed SLIPPAGE_TIER_MULTIPLIERS — for confirmation, not written

Measured, unfloored, both treatments, three tiers retained by the stated
20-percent rule (marginally — 21.1% / 22.2%):

- **Zero treatment: (1.0, 1.2, 0.4)** — unrounded (1.0000, 1.2105, 0.3524)
- **Exclude treatment: (1.0, 1.2, 0.6)** — unrounded (1.0000, 1.2223, 0.6099)

Both carry a tier-3 multiplier below tier 1's — the thinnest tier priced as
the cheapest to trade — produced by leverage-correlated estimator bias
sorting into tier 1 and thin-name collapse sorting into tier 3. Reported as
measured per the no-hand-set instruction. Note for the confirmer:
`config.validate()` as written requires non-decreasing multipliers with
tier 1 at 1.0, so **writing either measured tuple into config would fail
validation as it stands** — resolving that conflict (relaxing the guard,
or revisiting what the multiplier schedule should be estimated from) is a
decision, not a measurement, and is left open.

## Stop condition

Halted after this report. No backtest, no performance statistic, no
commit. Session writes: `scripts/s06_structure.py` and six files under
`outputs/session-06/`.
