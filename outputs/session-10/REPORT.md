# Session 10 report — synthetic construction and validation

Seven series frozen; nineteen synthetics built from the schedule module,
the 2.14 financing anchor, and the 2.19/2.3 substitutions; five validation
layers run with every failure recorded and none halted on. No portfolio,
no position, no performance statistic; nothing committed. Suite unchanged
at 199 passing.

## Step 1 — series frozen (`etf-manifest-additions.csv`)

| Ticker | Rows | Window | Interior nulls | Boundaries | SHA-256 (prefix) |
|---|---|---|---|---|---|
| SVXY | 3,737 | 2011-10-04 → 2026-08-14 | 0 | 5/5 pass | 043e1f0cf342 |
| UVXY | 3,737 | 2011-10-04 → 2026-08-14 | 0 | 13/13 pass | 12eda3265db6 |
| SVIX | 1,098 | 2022-03-30 → 2026-08-14 | 0 | 0 | 39d6bb4fca8e |
| UVIX | 1,098 | 2022-03-30 → 2026-08-14 | 0 | 4/4 pass | e2de90e5a6c8 |
| QID | 5,054 | 2006-07-13 → 2026-08-14 | 0 | 5/5 pass | 22cb96a495df |
| SSO | 5,069 | 2006-06-21 → 2026-08-14 | 0 | 4/4 pass | dbdcb3907bd9 |
| SDS | 5,054 | 2006-07-13 → 2026-08-14 | 0 | 4/4 pass | 0b01c79b3e46 |

Full hashes in the manifest. Every file passed the session 07
split-boundary check and the interior-null audit before use. Siblings
pulled: QID, SSO, SDS (pre-2010 windows on the two index families,
including 2008). Judged unnecessary and not pulled: ROM, USD, UYG — they
track Dow Jones U.S. sector indices, not the Select Sector/PHLX/Biotech
families, and no underlying proxy for those is frozen; the sector residual
stays a disclosed limitation exactly as the brief anticipated.

## Step 2 — the builds (`synthetics-manifest.csv`)

Nineteen synthetics under `data/interim/synthetics/` (derived, rebuildable;
1.1 does not apply): r_syn = M·r_u + (1−M)·ref − k·spread − ER/252, daily
reset compounding, multiples exclusively from `src/schedule.py`, DTB3
reference accrued at rate/360 on calendar days (5.5a), financing per 2.14/
2.15 (long swap k=M−1 at 75 bp; short swap k=|M| at 70 bp haircut; vol
funds k=0 with collateral yield on full NAV).

**Boundary confirmations:** UVXY 2.0→1.5 and SVXY −1.0→−0.5 landed exactly
on 2018-02-28, the session after the stated close-of-business change. The
SOXL/SOXS (2021-08-25) and FAS (2022-02-28, 2022-08-01) benchmark
boundaries were crossed with the build input unchanged by design — the
proxy (SMH, XLF) spans both sides, so the switch changes interpretation,
not the input series.

**Two flagged approximations in the build:** (1) decision 2.13's expense
schedule is not among the register materials available; constant
current-prospectus net ERs were used (listed per fund in the manifest) — a
mis-set ER is indistinguishable from a financing mis-set of equal annual
size, and step 7 bounds that class. (2) The first build of this session
used the constant-maturity price level (`vx-cm30.parquet`) as the vol
underlying; its change omits the roll yield, and the vol synthetics
overshot by roughly the roll drag (long +131%/yr, short −45 to −51%/yr).
Caught by the sign pattern, rebuilt on construction B's investable
`index_level` (`vx-cm30-b.parquet`) per 2.3/2.22. The mistake and the fix
are both recorded.

## Step 3 — primary validation (`synthetic-validation-primary.csv`)

**Equity funds — twelve of twelve PASS the 2.7 band; the numbers that
matter are beside the band:**

| Fund | Corr | Ann TD | TD sd | Max roll-252 | Proxy context (session 09) |
|---|---|---|---|---|---|
| TQQQ | 0.9989 | +0.06% | 2.96% | 5.0% | QQQ wedge quantified |
| QLD | 0.9960 | −0.09% | 3.96% | 5.2% | " |
| SQQQ | 0.9987 | −0.80% | 3.16% | 4.2% | " |
| PSQ | 0.9928 | −0.44% | 2.64% | 3.8% | " |
| SH | 0.9936 | −0.84% | 2.19% | 4.8% | SPY exact |
| SPXL | 0.9971 | −0.11% | 4.28% | 7.7% | SPY exact |
| TECL | 0.9951 | −0.23% | 6.61% | 26.8% | XLK benchmark unmeasurable |
| TECS | 0.9948 | +1.03% | 6.79% | 39.6% | " |
| SOXL | 0.9823 | +3.75% | 17.21% | **89.7%** | SMH max div 19.3% |
| SOXS | 0.9618 | +3.10% | 26.37% | **2845%** | " |
| FAS | 0.9886 | +1.09% | 14.44% | 40.4% | XLF benchmarks unmeasurable |
| LABU | 0.9980 | +1.37% | 6.21% | 13.0% | XBI benchmark unmeasurable |

**A circularity in the equity band, stated plainly:** 2.7's leveraged-
equity band is syn-TE ≤ 1.5× the real fund's TE against its stated
objective, but the objective must be proxied by the SAME underlying the
synthetic is built from, so the two TEs are nearly identical by
construction and the band is close to self-satisfying (objTE column equals
the TD sd column to two decimals throughout). The PASS flags carry little
information for equity funds; the correlations, tracking differences, and
maximum divergences are the evidence. On those, the index-fund synthetics
(NDX, SPX) are tight; the sector synthetics inherit the proxy: SOXS's
2845% maximum rolling divergence is the −3× compounding of the SMH-vs-PHLX
basket mismatch through the 2021–22 semiconductor swings, and FAS/TECS
divergences of ~40% are the same mechanism smaller.

**Volatility funds — four of four FAIL the 2.7 band, diagnostics
recorded:**

| Fund | Corr | Min yearly corr | Ann TD | Max roll-252 | Band |
|---|---|---|---|---|---|
| UVXY | 0.9375 | 0.8085 | +12.6% | 91.8% | FAIL (needs ≥0.995 / ≤0.10) |
| SVXY | 0.7967 | **0.2444** | +6.0% | 1644% | FAIL |
| SVIX | 0.9937 | 0.9885 | +10.9% | 19.2% | FAIL |
| UVIX | 0.9958 | 0.9923 | +13.6% | 33.3% | FAIL |

Diagnostics, not recommendations: (1) the systematic **positive** TD on
all four — synthetic outrunning the real fund on longs AND shorts alike —
points at construction-B's roll differing from the funds' actual S&P VIX
Short-Term Futures index mechanics (roll weights/timing) plus fee/basis
under-modelling, an index-level mismatch rather than a mechanism failure;
(2) SVXY's 0.24 minimum yearly correlation is 2018 — the February 5
termination-scale collapse (real −90% day against a −1× synthetic move of
different size) destroys that year and the pre-2018 −1× era carries the
2.7 failure; (3) the 2022+ funds (SVIX/UVIX) correlate at 0.99+ and fail
on level drift, not shape. The volatility legs enter the strategy only
through UVXY/UVIX/SVIX routing states, and what a failed band means for
them is a register decision.

**Validated vs unvalidated windows, per fund:** validation covers each
fund's listing history (2010+ for TQQQ/SQQQ/SOXL/SOXS, 2008-11+ SPXL,
2008-12+ TECL/TECS, 2015+ LABU, 2011-10+ UVXY/SVXY, 2022-03+ SVIX/UVIX,
2006+ QLD/PSQ/SH). The unvalidated pre-inception windows against the
2007-01-01 sample start are exactly where steps 4–6 aim.

## Step 4 — sibling validation 2006–2010 (`sibling-validation.csv`)

All five siblings PASS on same-window bands across the crisis window:

| Fund | Family | Corr | Ann TD | TD sd | Max roll-252 |
|---|---|---|---|---|---|
| PSQ | Nasdaq-100 | 0.9807 | −0.44% | 5.14% | 3.8% |
| QID | Nasdaq-100 | 0.9877 | +0.72% | 8.19% | 10.4% |
| SH | S&P 500 | 0.9874 | −1.20% | 4.10% | 4.8% |
| SSO | S&P 500 | 0.9909 | +1.15% | 7.16% | 3.6% |
| SDS | S&P 500 | 0.9921 | −1.27% | 6.66% | 9.8% |

**The mechanism — daily reset, financing treatment, expense schedule —
reproduces real funds through 2008 on both index families at |M| ∈ {1, 2},
long and short.** (First pass of this table showed five FAILs from a
window mismatch — sub-window TD sd against full-window baseline — fixed to
same-window bands before results were read.) Families gaining
pre-inception mechanism validation: Nasdaq-100 and S&P 500. Sector
families gain none; disclosed limitation, as expected.

## Step 5 — multiple invariance (`multiple-invariance.csv`)

Tracking error grows with |M|, roughly linearly:

- Nasdaq-100, all-members window 2010+: |M|=1: 1.17%; |M|=2: 1.61/1.66%;
  |M|=3: 2.96/3.16%.
- S&P 500, 2008-11+: |M|=1: 1.54%; |M|=2: 2.38/2.49%; |M|=3: 4.28%.

**A 3× construction extrapolated into a window validated only by a 1×
sibling carries roughly 2.5–3× that sibling's tracking error** — the
extrapolation is quantified, not assumed.

## Step 6 — regime-conditional error (`regime-conditional-error.csv`)

**The error profile is NOT flat.** Median equity-fund TD sd by underlying
realized-vol decile: D1 1.71% → D5 2.27% → D7 4.37% → **D10 9.13%** — a
5.3× rise from calmest to wildest decile. By DTB3 bucket: <1% 4.37%,
1–3% 3.25%, >3% 2.87% (the ZIRP bucket coincides with the high-vol era, so
the rate conditioning largely re-reads the vol conditioning). **The
construction is weakest exactly where the strategy's bear branches
operate, and extrapolating into 2008 is the weak case, not the modest
one** — the writeup states this rather than assuming otherwise.

## Step 7 — financing sensitivity (`financing-sensitivity.csv`)

Analytic: a spread mis-set by Δ produces k·Δ of annualized tracking error
(k = M−1 long, |M| short). Empirical rebuilds confirm exactly (the 365/360
day-count factor visible): QLD (k=1) +25/50/100 bp → 25.4/50.8/101.6 bp;
TQQQ (k=2) → 50.8/101.6/203.3 bp; PSQ (k=1) → 25.4/50.8/101.6 bp; SQQQ
(k=3) → 76.2/152.4/304.9 bp. **Worst case in the study universe: a 100 bp
financing error on a 3× short costs ~305 bp/yr of level error; on the
anchor's own harvest range (28–99 bp around the 75 bp median) the
plausible mis-set is ≤ ~25 bp, i.e. ≤ ~76 bp/yr even at k=3.** The anchor
is a single-fiscal-year snapshot; that stays disclosed.

## What did not match expectation

1. The vol-underlying mistake (CM price level vs investable roll index) —
   caught by the sign pattern of the first validation pass, rebuilt on
   construction B, both recorded above.
2. The equity-band circularity — the 2.7 band as revised is nearly
   self-satisfying for equity funds when the objective is proxied by the
   build's own underlying; flagged so the PASS column is not over-read.
3. SOXS's 2845% maximum rolling divergence — the arithmetic consequence of
   −3× compounding on a proxy with 19.3% basket divergence; expected in
   kind, striking in size.
4. The sibling table's first pass failed on a window-mismatch of my own,
   fixed before reading results.
5. The regime gradient (5.3×) is steeper than a flat-profile hope; stated.

## Stop condition

Halted after step 8. No backtest, no performance statistic, no commit.
Session writes: seven frozen parquets + manifest, nineteen synthetics +
manifest, `src/config.py` (2.14 closure), three scripts, five validation
CSVs, and this report. Working tree left dirty.
