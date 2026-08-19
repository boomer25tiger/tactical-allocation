# Session 13.5 — diagnostic pass on the canonical session-13 result

Run 2026-08-18. Script: `scripts/s13_5_diagnostics.py`. Explains the
session-13 result; changes nothing. Nothing under outputs/session-13/
was modified; no parameter, threshold, instrument, cost, or branch was
changed anywhere. The step-3 oversold sweep varied config.OVERSOLD in
memory only, restored and re-validated, with a θ=30 positive control
reproducing the canonical zero.

Positive controls this session: residual reconstruction re-derived every
fresh-entry share count against the order ledger (0 mismatches / 2,561);
the θ=30 sweep point reproduced canonical zero firings; the TQQQ rolling-
divergence control read 0.050 against session 12's recorded 0.050; the
weekday distributions sum to one; the branch tracer underlying steps 1–3
is the one already asserted against all 3,460 × 4 sleeve outputs.

Finding labels: **[A] explains a session-13 number without changing it;
[B] indicates a session-13 number is wrong or unreliable; [C] register or
code defect.** For each, the change that would act on it is stated with
its class (correctness repair vs specification change). No
recommendation is made.

---

## Step 1 — the timing defect (`lag-diagnostics.csv`)

**[A] The lag curve is single-peaked, not monotone.** Annualised return:
T+1 24.2%, T+2 33.0%, T+3 18.0%, T+4 9.5%, T+5 1.0% (cost-free; the
10 bp curve is parallel: 19.1 / 27.5 / 13.1 / 5.0 / −3.2%). Peaks: ann
return and naive Sharpe at **T+2**; Lo-corrected Sharpe and max drawdown
at **T+1** (SR_lo 0.813 / 0.722 / 0.518 / 0.417 / 0.387). This is a
one-session effect that reverses and then decays — the signal's
information is nearly exhausted by T+3 — not a monotone improvement.

**[A] The entry effect is concentrated, not uniform.** On the corrected
0 bp path the portfolio's first-held-session mean is +11.2 bp against a
+14.4 bp unconditional mean (n = 1,425). By sleeve (sleeve-slice units,
first day vs continuing): T10 +9.5 vs +16.0 bp; T11 +12.8 vs +15.4 bp;
S2 **+31.8 vs +18.7 bp** (entries help); S3 **−35.0 vs +24.2 bp**
(entries hurt). By terminal state, the drag sits in the volatility-long
and short entries: S3→100%UVXY **−87.5 bp** first day vs +22.4
continuing (n=137); T10→100%UVXY −50.1 vs +15.2 (n=157); T11 bull-short
basket −34.5 vs −14.3 (n=175); T11→SQQQ −51.6 vs +12.0 (n=45). Dip-buy
entries are strongly positive on day one (T10→TECL +151 bp, T10→LABU
+315 bp, T11→TQQQ +119 bp, small n). By instrument, UVXY is bought into
a −16 bp average first day against its +12 bp mean on held sessions.
The overbought→UVXY family enters one session before the move it
anticipates; a one-session-later entry catches it.

**[A] By era, the drag is late-sample.** 2007–2011: first-day +19.3 bp
vs +1.9 unconditional (entries helped). 2012–2021: first-day +7.3 vs
+19.8 (entries hurt). Yearly table in the CSV.

**[A] The effect is not the instruments' mechanical autocorrelation.**
Portfolio ρ1 = −0.043; a constant-weight mix of the same instruments at
the strategy's mean realized weights has ρ1 = **−0.123** (constituents:
TECL/TECS −0.154, UVXY −0.052, SVXY −0.051). The switching portfolio
carries *less* negative autocorrelation than its constituents would
produce at fixed weights, so the entry-timing drag is signal-driven, not
a daily-reset artifact.

**[A] No weekday or month-end concentration.** Fill weekday shares match
session shares within 1.4 pp; last-3-sessions-of-month share 14.4% vs
14.3% expected; first-3 17.1% vs 14.3%.

To act on the timing defect would be a **specification change**
(execution timing is closed under 4.1); nothing here repairs it.

## Step 2 — 2010–2012 (`year-attribution.csv`)

Attribution convention: instrument rows are arithmetic w·r sums on
lagged realized weights at the 10 bp anchor; sleeve/state rows are
target-weight slices × 25% budget; costs and compounding sit in stated
residual lines (2010: arithmetic −53.5 pp vs compounded −49.2%, cost
drag −4.3 pp).

**[A] 2010 (−49.2%) is a long-volatility loss, not a crash loss.**
Instrument level: UVXY −39.6 pp of the −53.5 arithmetic; SOXL −15.5;
everything else small. State level: T10→100%UVXY −24.7 pp,
S3→100%UVXY −10.8, S3 bull basket −13.4, T10 rs-bull basket −6.7.
The overbought→UVXY branches fired repeatedly through 2010's grinding
rally and bled the vol carry; the ten worst sessions are −7.1% to
−10.6% days holding either the bull basket (~46% TQQQ + 29% SOXL) on
selloff days or **80%+ UVXY** on vol-collapse days (2010-10-20,
2010-11-03, 2010-11-04). The flash-crash window itself is in the
timeline table: the sleeves rotated through UVXY/tier states around
2010-05-04..05-14 and the losses there are of the same two kinds.

**[A] 2011 (−14.4%):** UVXY contributed **+19.9 pp** (August spike);
the loss came from whipsaw in SQQQ (−11.7), TQQQ (−5.6), SOXL (−3.8),
TECL (−3.1); by sleeve, S2 −14.1 pp (its TQQQ gate chopped), while S3
was +7.9. **2012 (−19.8%):** UVXY again, −35.6 pp, against positive
equity legs (SOXL +12.6, TQQQ +8.9, TECL +7.2) — the tier-1/overbought
states kept buying vol into the 2012 rally.

**[A] 2013 (+74.5%) and 2019 (+81.1%), the like-construction
comparison:** gains concentrate in TQQQ (+39.9 / +25.6 pp), SOXL
(+20.1 / +24.5), UVXY (**+21.7 / +17.6** — the same branches that lost
2010/2012), TECL (+5.9 / +10.1); shorts cost −21 / −14 pp across
SQQQ/SOXS/TECS. All four sleeves positive in both years.

**[A→B boundary, stated precisely:** −35.2 pp of 2010's −53.5 arithmetic
(65.8%) sits in instruments whose reconstruction carries a recorded
exception — but that is almost entirely UVXY (−39.6; SVXY +2.7, SOXS
+1.8), whose exception is the close-timing residual class at 7.5–8.9%
**per year**. The exception bounds the construction-artifact share of
the 2010 UVXY loss at a few pp; the loss itself is the instrument's
carry economics at the pre-2018 2.0× multiple. The 2010 figure is
explained, not impeached, by the exception — while resting on the
least-validated construction era (regime-gradient limitation).]

## Step 3 — the unreachable terminals (`unreachable-terminals.csv`)

**[A] Unreachable by construction at canonical thresholds.** PSQ dip-RSI
< 30 occurs on 444 of 3,460 sessions — and on **all 444** TQQQ sits
above its 20-SMA (the conjunction equals the PSQ condition). PSQ RSI and
QQQ RSI are mirror images: correlation **−0.998**, mean sum 99.2. So
PSQ oversold ⟺ QQQ RSI ≈ 70+ ⟺ a strong rally — exactly the sessions
the T11 cascade resolves upstream: tier-1 basket 370, tier-2 42,
bull-rs basket 30, bull-short 2. The bear side (where the PSQ-dip
terminals live) is never reached with PSQ oversold, because PSQ
oversold implies conditions that fire the overbought or bull branches
first.

**[A] Reachability elsewhere in the registered oversold grid** (cascade
property, not a performance statistic): oversold 20 / 25 / 30 → 0 / 0 /
0 sessions reach either terminal; **35 → bond_baller 1, feaver 23; 40 →
bond_baller 10, feaver 113.** Grid runs at the upper oversold points
will exercise these terminals; ablation reads at canonical would not.
Neither terminal was removed. Acting on this in any direction is a
**specification change**.

## Step 4 — negative cash (`cash-diagnostics.csv`)

**[A] Small and bounded by identity.** Negative-cash sessions: 1,376.
As a fraction of contemporaneous NAV: mean 0.145%, median 0.069%, p99
1.53%, max 2.78%. Negative cash / NAV equals realized gross − 1 exactly
(measured identity gap 0.0), so the 2.78% gross overshoot bounds every
session by construction — no session exceeds it. Calendar-day-weighted
borrowing averages 0.071% of NAV. Charging a margin spread over DTB3 on
negative balances: 100 bp → −0.0007 pp annualised return, −0.00001
SR_lo; 300 bp → −0.002 pp, −0.00003; total dollar charge at 300 bp is
$461 over 13.7 years. Reported, not applied. The negative-cash
convention is immaterial at three orders of magnitude below the
headline.

## Step 5 — price reconstruction sensitivity (`reconstruction-sensitivity.csv`)

**[A] Truncation is immaterial at the $100 anchor and 1,000,000 NAV.**
Cumulative truncation residual across all fills: $459,936 (mean ~$60
per instrument-fill, ≤0.1% of a sleeve slice for every fund); return
forgone by residuals earning DTB3 instead of the position return: $350
total = **0.15 bp/yr** of average NAV. Per-fund price paths and
residuals are tabulated; the widest prices are the back-extended
pre-listing segments (UVXY 2008 median $4,570, max $34,630 — residual
0.7% of slice on the 27 fills of 2008–2009; from 2010 its median is
$45–93 and residuals are ~$20–60 on 4,000–96,000-share fills).

**[B] The commission-by-instrument figures are NOT meaningful
independent of the anchoring convention.** Recomputing every order at a
0.1× and 10× anchor: portfolio commission 0.97 bp of traded value at 1×
becomes ~10× larger at 0.1× (min-bound orders dominate) and ~10×
smaller at 10×; per-instrument the band across the 100× anchor range is
0.05–33 bp (TECS 0.34→33.1, LABU 0.37→30.1, BTAL 0.26→25.2, SQQQ
0.21→19.8, UVXY 0.12→11.8). The *shape* (which names are min-bound vs
rate-bound) is anchor-driven. Acting on this requires either
registering the convention (**specification change**) or acquiring true
as-traded prices outside the frozen panel (**correctness repair**);
recorded as D8.

## Step 6 — concentration, completed (`concentration-extended.csv`)

**[A] Effective market exposure by drawdown quintile, all five (target /
realized):** q0 (deepest, dd −0.767..−0.490) 1.82 / 1.82; q1 1.53 /
1.52; q2 1.59 / 1.60; q3 1.68 / 1.69; q4 (shallowest) 1.89 / 1.89.
(Session 13's CSV carried all five; its report narrative cited only q1
and q4.)

**[A] On market-state axes the strategy de-exposes in stress:** by
trailing 60-session QQQ return decile, exposure runs 0.79 (worst
decile, −45..−6.4%) → ~2.0 (deciles 6–8) → 1.78 (strongest); by
trailing 60-session QQQ volatility decile, 2.03 (calmest) → 1.07
(wildest). Exposure is highest in its own deepest-drawdown quintile
(1.82) even though it is lowest in market stress — the deep-drawdown
bucket is dominated by the 2010–2012 self-inflicted UVXY losses in calm
markets, not by market crises.

**[B→C] The fixed-window ENB convention understates diversification in
most years.** ENB recomputed on within-year covariances exceeds the
fixed-window figure in 12 of 15 years, by +0.9 to +1.7 in eleven of
them (e.g. 2011: 10.19 vs 8.70; 2021: 9.27 vs 7.54); 2007, 2017, 2018
are within ±0.3. The 2007–2011 fixed-window figures were produced by a
covariance estimated entirely outside those years. Flagged as a
diagnostic defect (D10), not repaired; the fix is registering a 5.7
estimation window (**specification change**).

**[A] Sleeve overlap and breadth.** Pairwise fraction of sessions
holding a common ticker / mean overlapping exposure as a fraction of
NAV: T10–T11 0.686 / 9.0%; S2–S3 0.625 / 9.3%; T11–S2 0.640 / 6.3%;
T11–S3 0.515 / 7.6%; T10–S3 0.461 / 6.8%; T10–S2 0.162 / 3.8%.
Distinct tickers held: mode 4 (44.6% of sessions), 5–7 on 36.2%, ≤2 on
6.6%.

## Step 7 — turnover structure (`turnover-structure.csv`)

**[A] The turnover rise with cost is sizing-only; no feedback path
exists.** All six cost levels replay the identical signal stream (one
signal pass per arm feeds every account run, and signals never read
NAV). Dollar turnover and average NAV both fall with cost ($108M/yr on
$2.58M at 0 bp → $17.8M/yr on $0.41M at 50 bp); the ratio drifts 42.10
→ 43.50 purely through the NAV path reshaping integer share counts.

**[A] Reconciliation.** Mean one-sided turnover per transition is 40.8%
of NAV (median 39.6%, p10 11.5%, p90 71%): 0.408 × 103.8 fills/yr =
42.3×/yr, matching the headline. **[A] One-session holds concentrate in
the dip states** (T10→TECL 65.6%, T10→SOXL 58.8%, S2/S3→SOXL 57.7 /
56.8%) and the defensive pairs (T10 SQQQ/TLT 45.2%, T11 bull-short
49.1%), while the persistent states are S2→TQQQ (median run 7) and the
S3 states (median 3.5–4). By instrument, one-sided turnover/yr: UVXY
9.2, TQQQ 6.2, SOXL 6.0, SQQQ 4.7, TECL 4.2, TLT 2.3, rest ≤1.8.

## Step 8 — the two arms and the crisis window (`arm-comparison.csv`)

**[A] The realized arm's early incomparability, sized.** Mean target
weight sitting unfillable (forced cash): 2007 58.2%, 2008 55.5%, 2009
**70.9%**, 2010 34.7%, 2011 12.6%.

**[A] Post-2012, the arms agree.** 2012-01 onward at the anchor:
synthetic 37.2% ann, 53.4% vol, SR_lo 1.174, MDD −66.6%; realized
35.4%, 51.4%, 1.132, −64.7%. The volatility gap collapses from 9 pp
(full window) to 2 pp, confirming session 13's attribution of the
realized arm's lower volatility to early forced cash. The residual
~1.8 pp/yr return gap is the construction-versus-real-fund tracking
direction.

**[A] The 40 BTAL events on record.** Two are crash-branch halves
(2008-10-31, 2008-11-03, weight 12.5%, QQQ trailing-60 at −28.9% and
−30.6%); the other 38 are tier-1 basket slices (8.33%) between 2009-05
and 2011-04 with QQQ trailing-60 between −5% and **+41.4%** — the
overbought basket firing into the 2009–2010 rebound. Full table in the
CSV.

**[B] The SOXS exception, re-scoped to the sample.** The recorded
1394% maximum rolling divergence is measured over 2010-03..2026-08 —
a window extending past the holdout. Recomputed in-window (ratio
definition, TQQQ control 0.050 matching session 12's 0.050), the
maximum through 2021-07-30 is **14.0%, dated 2011-03-16**, and SOXS was
held on 9.1% of that window's sessions. The exception disclosure as
quoted beside in-sample results describes a divergence that occurs
outside the sample (D11). Documentation re-scoping; the exception
itself is unchanged.

## Step 9 — measured zero crossings (`cost-extension.csv`)

Diagnostic extension at 60, 75, 100, 150 bp (never merged into
headline-results.csv; the 4.4 grid stands at its six points):

| arm | metric | measured | extrapolated | diff |
|---|---|---|---|---|
| synthetic | ann return | **51.0 bp** | 50.9 | +0.1 |
| synthetic | Lo Sharpe | **83.5 bp** | 83.9 | −0.4 |
| realized | ann return | **67.0 bp** | 66.0 | +1.0 |
| realized | Lo Sharpe | **94.4 bp** | 96.5 | −2.1 |

**[A] The session-13 extrapolations were accurate to ≤2.1 bp.**

## Step 10 — defect register (`defect-register.csv`)

Eleven entries, D1–D11, each with location, consequence, what it
affects, grid-blocking status, and repair class. Grid-blocking: **D1
only** — the S3 vote-threshold literal `votes >= 3` in src/sleeves.py
means the registered 2/3/4 grid axis will silently not vary; the grid
cannot run correctly until it is moved to config (a correctness repair
with no value change). Affecting canonical numbers: D2 (commission
terms inline), D6 (unavailable-fill rule), D7 (starting NAV), D8 (price
anchor — commission diagnostics only, returns immaterial). Affecting
session-13 text or diagnostics: D9 (stale pre-correction entry-effect
figures +3/+11 bp in the canonical report; corrected +11.2/+14.4 —
the FAIL verdict stands), D10 (ENB window), D11 (SOXS exception
window). Documentation: D3, D4; open specification: D5 (7.14). None
repaired.

## Provisional operating values every figure above depends on

Restated from session 13; none is a closure. (1) Starting NAV 1,000,000
under OPEN 4.6. (2) IBKR Fixed 0.005/share, 1.00 minimum, 1% cap — v2
4.5, unported, carried inline. (3) Unavailable-fill slices stay in
sleeve cash at DTB3 (1.9/2.11 open half). (4) Levered raw prices
anchored at $100 on the first listed in-window session; as-traded
levels are otherwise unrecoverable without post-boundary split rows.
(5) Negative cash accrues DTB3 symmetrically with no financing spread.

## Stop condition

Halted after this report. outputs/session-13/ untouched (verified: this
session wrote only under outputs/session-13.5/). No holdout, grid,
benchmarks, or nulls. Nothing committed; working tree left dirty.
