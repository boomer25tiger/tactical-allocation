# Session 13.6 — repairs, decode, and pre-registered arms

Run 2026-08-18. Scripts: `scripts/s13_6_run.py` (steps 1v, 3–7),
`scripts/s13_6_audit.py` (step 8). Binding order respected: the decode
and its positive controls ran before every downstream arm. Finding
labels carried from session 13.5: **[A]** explains a number without
changing it; **[B]** indicates a number is wrong or unreliable; **[C]**
register or code defect.

## The corrected canonical headline (step 4) — supersedes session 13

**This table supersedes session 13's headline.** Reason: it corrects a
defect rather than changing a specification — the raw price path now
carries true as-traded levels recovered by the split decode (step 3),
where session 13 ran on a stipulated $100 listing anchor. Every
parameter is unchanged. Synthetic (primary) arm, registered grid:

| bp | total ret | ann ret | ann vol | SR naive | SR Lo | max DD | Calmar | turnover | Δann vs s13 | ΔSR_lo |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 17.03x | 23.46% | 54.3% | 0.646 | 0.799 | −74.5% | 0.315 | 42.1 | −0.74pp | −0.013 |
| 5 | 12.47x | 20.86% | 54.3% | 0.607 | 0.751 | −75.8% | 0.275 | 42.2 | −0.73pp | −0.013 |
| **10** | **9.07x** | **18.33%** | **54.3%** | **0.567** | **0.702** | **−77.1%** | **0.238** | **42.3** | **−0.72pp** | **−0.014** |
| 20 | 4.63x | 13.41% | 54.4% | 0.489 | 0.605 | −79.4% | 0.169 | 42.5 | −0.70pp | −0.014 |
| 35 | 1.35x | 6.41% | 54.5% | 0.372 | 0.460 | −84.0% | 0.076 | 43.0 | −0.65pp | −0.014 |
| 50 | −0.02x | −0.18% | 54.5% | 0.256 | 0.315 | −88.1% | −0.002 | 43.6 | −0.60pp | −0.013 |

Realized arm at the anchor: 21.47% ann, SR Lo 0.721, MDD −69.3%
(−0.59pp / −0.011 vs session 13). Full table with all deltas:
`headline-corrected.csv`.

The deltas come from commission now being measured in true units:
portfolio commission is **1.73 bp of traded value = 1.46 pp/yr of
drag** (session 13 under the anchor convention: 0.97 bp), minimum-bound
on 17.5% of orders, cap-bound on 0.22%. Truncation stays immaterial:
cumulative residual $304k, forgone $337 = **0.15 bp/yr**, confirming
session 13.5's finding under corrected levels.

**Zero crossings, now measured** (extension points 60/75/100/150 bp
kept separate from the registered grid): synthetic annualised return
crosses zero at **49.6 bp — inside the registered range; the 50 bp
grid point is now slightly negative (−0.18%)** — and Lo-Sharpe at
82.5 bp. Realized: 65.6 and 93.2 bp. Session 13's extrapolations (50.9
/ 83.9 / 66.0 / 96.5) were accurate to ≤3.3 bp against the
corrected-price measurements.

## Step 1 — D1 repaired [C→repaired]

`S3_VOTE_THRESHOLD = 3` now lives in src/config.py (validate() bounds it
to 1..4), read by src/sleeves.py; the tracer follows. Positive control:
S3 terminal-state occupancy across all 3,460 sessions recorded before
the change (CASH 941, 100%SOXL 83, 100%UVXY 647, 50%TQQQ+50%SOXL 1,789)
and reproduced **exactly** after it. The 218,700-specification grid's
vote-threshold axis is no longer silently pinned.

## Step 2 — D9 repaired [C→repaired]

outputs/session-13/REPORT.md now reads +11.2 bp / +14.4 bp with a dated
correction note recording the original +3/+11, the pre-correction-path
provenance, session 13.5 as the measuring session, and the unchanged
verdict. Nothing else in that report was touched.

## Step 3 — the split decode [B→resolved; closes provisional value 4]

2.10 reasoning, recorded: the frozen panel was downloaded in 2026 and
its Close column already expresses every in-sample price in 2026 share
units, so post-boundary split history is already embedded in what the
backtest reads; reading the split ratios **removes** that embedding
rather than adding out-of-sample information, and a split ratio is a
corporate action carrying no strategy-performance information. Only the
`Stock Splits` column was read over the full span — no post-boundary
price or volume was retrieved, loaded, or computed on.

Positive controls, all passed before any downstream step:

- **Known-level control** (tolerance ±35%, levels from general market
  knowledge): TQQQ 2021-07-30 reconstructed 132.74 vs ~120 (+10.6%);
  SOXL 2021-03-15: 35.57 vs ~40 (−11.1%); UVXY 2021-06-15: 31.50 vs ~27
  (+16.7%); SQQQ 2021-07-30: 8.34 vs ~9.5 (−12.2%). Both a heavy
  forward-splitter and heavy reverse-splitters covered.
- **Return consistency**: as-traded return x in-window split ratio
  equals the adjusted return to <1e−9 on every session of every fund
  (RYMFX compared pre-2.5a-lag to avoid a shifted-frame artifact).
- **UVXY yearly path**: listed era medians $10–32 (2011 listing at
  $34.30), matching its real trading band; the 2007–2009 segment
  ($683–$11,878) is the disclosed pre-listing back-extension.

**The old anchor's error, per fund** (reconstructed first listed
in-window price / 100): FAS 0.21, UVXY 0.34, LABU 0.39, SOXL 0.40, SVXY
0.42, SPXL 0.51, TECL 0.53, SH 0.62, PSQ 0.63, TECS 0.67, SQQQ 0.77,
QLD 0.81, TQQQ 0.83 — and **SOXS 6.04** (listed at $604). The $100
anchor was 6x too low for SOXS and 2–5x too high for most others.

**Remaining convention** (stated, applied consistently): pre-listing
synthetic segments have no listing price to anchor and are back-extended
from the first listed as-traded price with synthetic returns. Affected:
TQQQ/SQQQ before 2010-02, SOXL/SOXS before 2010-03, UVXY/SVXY before
2011-10, TECL/TECS before 2008-12, SPXL/FAS before 2008-11, LABU before
2015-05 (full ranges in `split-decode.csv`).

## Step 5 — the lag curve on the realized arm [A]; verdict: signal property

Matched 2012-01-01+ window, both arms, T+1..T+5 (annualised return,
0 bp):

| arm | T+1 | T+2 | T+3 | T+4 | T+5 |
|---|---|---|---|---|---|
| synthetic | 42.1% | 63.3% | 53.6% | 31.2% | 12.0% |
| realized | 40.3% | **62.8%** | 48.8% | 25.7% | 13.1% |

**Verdict: signal property.** The T+2 advantage persists on the
realized arm — real listed funds, real closes, no synthetic
construction — at +22.6 pp against the synthetic arm's +21.2 pp on the
identical window. The close-timing-residual hypothesis (a one-session
offset in the synthetic vol reconstruction) is not supported: the entry
effects match across arms almost state by state — S3→100%UVXY first-day
mean −91 bp realized vs −95 bp synthetic (n=113 each); T10→100%UVXY −44
vs −62 bp; S3 overall −36 vs −40 bp per sleeve unit. On this window the
Lo-Sharpe peaks at T+3 (full-sample: T+1), which is reported as
measured; the check's metric disagreement is already on the corrections
list. No halt condition was met. Acting on the timing property remains
a **specification change** (4.1).

## Step 6 — the open-to-open arm [A], pre-registered under 4.1/9.8

Realized panel, matched 2012+ window, signals unchanged (close-based),
fill at T+1 open, open-to-open accumulation, sizing at as-traded opens:

| bp | o2o ann | o2o SR Lo | o2o MDD | c2c ann | c2c SR Lo | Δann |
|---|---|---|---|---|---|---|
| 0 | 73.6% | 1.80 | −52.6% | 40.3% | 1.23 | +33.3pp |
| 10 | 66.5% | 1.69 | −52.9% | 34.6% | 1.12 | +31.9pp |
| 50 | 40.8% | 1.23 | −54.0% | 13.8% | 0.67 | +27.0pp |

Reported without interpretation; **close-to-close stands as primary
under 4.1 regardless.** Realized leverage deviation — the recorded
reason c2c is primary — measured for the first time: mean absolute
daily deviation of held levered funds against multiple x underlying
(open-to-open) runs 0.21% in the calmest underlying-vol decile to 0.45%
in the wildest (p95: 0.74% → 1.26%); UVXY/SVXY excluded for want of a
VX open series. Full tables: `open-to-open.csv`.

## Step 7 — the volatility-overlay ablation [A], post-hoc under 9.10

Recorded before running: specified in conversation on 2026-08-18 after
session 13.5 attributed −39.6 pp of 2010, −35.6 of 2012, +21.7 of 2013,
and +17.6 of 2019 to UVXY through the same branches; post-hoc, dated,
not a candidate specification. Affected states (arm A): T10:100%UVXY,
T11:100%UVXY (tier 2), the UVXY third of T11's tier-1 basket,
S2:100%UVXY, S3:100%UVXY. Arm B removes SQQQ, PSQ, TECS, SOXS (SH is
never a target; its removal is a no-op). Cash at DTB3 replaces each
removed slice; no reallocation.

At the anchor, corrected prices, full sample:

| ablation | panel | ann ret | SR Lo | max DD | Δann | ΔSR_lo | ΔMDD | Δmean eff exp |
|---|---|---|---|---|---|---|---|---|
| A no-UVXY | synthetic | 19.03% | 0.860 | −68.6% | +0.70pp | +0.158 | +8.4pp | −0.30 |
| A no-UVXY | realized | 20.57% | 0.898 | −66.8% | −0.90pp | +0.177 | +2.5pp | −0.24 |
| B no-inverse | synthetic | 24.75% | 0.725 | −78.0% | +6.42pp | +0.023 | −0.9pp | +0.27 |
| B no-inverse | realized | 31.33% | 0.814 | −66.1% | +9.86pp | +0.092 | +3.2pp | +0.21 |

Yearly differences (synthetic, arm A) confirm the attribution's shape:
removing UVXY adds +29.6pp in 2010, +52.6pp in 2012, +26.8pp in 2009,
and costs −68.3pp in 2020, −57.5pp in 2018, −26.0pp in 2013, −22.5pp
in 2021. Reported as: over this sample, the volatility overlay's losses
and gains are both large and concentrated, and its removal raises the
Lo-Sharpe while cutting mean effective exposure; the short-equity
component's removal raises annualised return in both panels. **Neither
arm is a candidate specification; adopting either would be selecting a
specification on results and is prohibited here and in every later
session.** Full yearly tables: `ablation.csv`.

## Step 8 — the validation-window audit [B]/[C] (`validation-audit.csv`, 50 rows)

Method control: every recomputation was first run over the recorded
window — correlations and max-roll divergences reproduce the recorded
values exactly (e.g. TQQQ 0.9989/0.05; UVXY-vs-NAV 0.99985); the
annualised-TD column does not reproduce under a geometric-difference
definition, so session 12's TD definition is under-documented (new
defect D12) and TD comparisons below are within this session's own
definition.

Key results:

- **SOXS [B]**: recorded corr 0.9784, TD +6.21%/yr, max-roll 13.94 over
  2010-03..2026-08. **In-window: corr 0.9970, TD +0.78%/yr, max-roll
  0.14.** The recorded exception is almost entirely a post-boundary
  (2021+) phenomenon; within the sample the SOXS synthetic validates
  like the other sector funds.
- **The other 13 funds + QID/SSO/SDS [A]**: in-window correlations
  0.988–0.999, within 0.003 of recorded; max-rolls essentially
  unchanged. The validation standard survives the window restriction
  everywhere except SOXS's exception, which shrinks.
- **Regime gradient [B]/[C]**: reimplemented (pooled syn-minus-real
  deviations, underlying 60-session vol deciles), full-window gives D1
  2.50% → D10 20.58% (8.2x) against the recorded 1.71%→9.13% (5.4x) —
  the method is under-documented and does not reproduce (folded into
  D12). Under this session's method the **in-window gradient is D1
  2.26% → D10 14.03% (6.2x)**: the qualitative limitation survives the
  window restriction; its magnitude is method-dependent.
- **Volatility NAV validations [A]**: reproduce exactly and hold
  in-window (UVXY full 0.99981 vs recorded 0.99985; pre-2018 rows are
  entirely pre-boundary). VIXY/construction-B: control 0.99991 exact;
  in-window 0.99988.
- **SVIX/UVIX**: no in-window overlap exists (funds list 2022-03);
  their validation is entirely post-boundary — already immaterial to
  the sample since both resolve to SVXY/UVXY throughout.
- **Not recomputed, with reasons**: session 09 proxy-accuracy
  (comparator index series measured at pull time, not frozen;
  re-pulling prohibited under 1.1); sibling validations (windows
  entirely pre-boundary, no crossing); expense arithmetic (identity,
  window-independent).
- **Breach statement**, as the prompt requires explicitly: every
  crossing statistic is construction validation performed before any
  strategy result existed; 2.10 as registered governs strategy-result
  computation on price series. The crossings are recorded; whether
  post-boundary validation windows — and separately the FY2025/FY2026
  filing-sourced expense and financing constants, which are
  post-boundary *documents* applied across the whole sample (new item
  D14) — fall under 2.10 is a register question for the user, not
  obviously a breach, and now stated rather than silent.

## Step 9 — the check rename [C→repaired]

`no_lookahead_extra_lag_degrades` → **`execution_lag_sensitivity`** in
scripts/s13_runall.py and in outputs/session-13/sanity-checks.csv
(rename verified with a positive-control read-back). Corrections list
item 12 added to DECISIONS-v3.md recording: the check fired on the
opposite condition to the one its name implied; it was specified
without a metric or direction; annualised return and Lo-corrected
Sharpe disagree on its verdict; 8.2 designated the Lo-corrected figure
as headline before any result existed; **no dedicated lookahead test
has run**, and the SPY positive control covers engine accounting, not
signal construction.

## Provisional operating values (updated)

1. **Starting NAV 1,000,000** — provisional under OPEN 4.6. Unchanged.
2. **IBKR Fixed 0.005/share, 1.00 min, 1% cap** — v2 4.5, still
   unported (D2). Unchanged.
3. **Unavailable-fill completion rule** — unfilled slices in sleeve
   cash at DTB3 (1.9/2.11 open half). Unchanged.
4. **REPLACED by the step-3 decode.** Raw prices are now true as-traded
   levels for every listed period. The surviving convention is only the
   pre-listing back-extension (funds and ranges in split-decode.csv).
5. **Negative cash accrues DTB3 symmetrically.** Unchanged (measured
   immaterial in session 13.5).

## Defect register, updated

| id | status after 13.6 |
|---|---|
| D1 vote-threshold literal | **REPAIRED** (step 1, control exact); grid unblocked |
| D2 4.5 unported | open — documentation port outstanding |
| D3 six absent audit IDs | open — documentation |
| D4 sleeves.py −10 docstring | open — documentation (not in this session's authorized set) |
| D5 7.14 open | open — specification |
| D6 unavailable-fill rule provisional | open — specification (2.11 open half) |
| D7 4.6 / starting NAV | open — specification, liquidity check now feedable from corrected daily NAV |
| D8 price anchor convention | **RESOLVED by the step-3 decode**; commission figures now measured, not stipulated; residual: pre-listing back-extension convention |
| D9 stale entry-effect figures | **REPAIRED** (step 2, dated note in place) |
| D10 ENB covariance window | open — specification (5.7 window unregistered) |
| D11 SOXS exception window | in-window values now on record (step 8); register re-scoping outstanding — documentation |
| **D12 (new)** | session 12's annualised-TD and regime-gradient methods are under-documented: correlations and max-rolls reproduce exactly, TD and the 5.4x do not reproduce under stated reimplementations — documentation defect |
| **D14 (new)** | FY2025/FY2026 filing-sourced expense and financing constants are post-boundary documents applied across the sample; whether document-sourced constants fall under 2.10 is an open register question — specification |

(D13 not assigned; the gradient item is folded into D12.)

## What would have to change to act on each finding

- Timing property (step 5 verdict): execution timing is closed under
  4.1 — any change is a **specification change**.
- o2o arm, ablation arms: pre-registered / post-hoc arms respectively;
  adopting any is a **specification change** (prohibited selection on
  results for the ablations).
- SOXS exception re-scoping, D3, D4, D11, D12: **documentation**.
- D2 port: **documentation** (decision exists).
- D5, D6, D7, D10, D14: **register decisions (specification)**.
- The corrected headline itself required no decision: a **correctness
  repair**, executed here under explicit authorization.

No recommendation is made on any of them.

## Stop condition

Halted after step 10. No arm promoted; no ablated specification
adopted; no holdout, grid, benchmarks, or nulls. outputs/session-13/
touched only by the authorized step-2 correction and step-9 rename.
Nothing committed; working tree left dirty.
