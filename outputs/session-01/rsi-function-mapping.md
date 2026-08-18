# RSI function mapping — session 01, step 3

Decision 6.1 ties three RSI periods by function: **exhaustion** (overbought
test routing to a hedge or volatility position), **dip** (oversold test
routing to a long entry), and **relative strength** (pairwise comparison of
one instrument's RSI against another's). Source
(`docs/source-quantconnect.py`, sha256 `0532b0cf…`, 353 lines) uses periods
8, 10, 15, 20 and 60 without labelling which function each serves. This file
records the mapping. Under the canonical spec all three functions take period
14, so nothing in this session changes however the ambiguities resolve; the
mapping determines what the grid sweeps at 7 and 28.

Classification rule: sites are classified by the **structure of the
comparison** the RSI value feeds (threshold-overbought, threshold-oversold,
pairwise). Where the economic reading of a site conflicts with its structure,
the site was marked **ambiguous** rather than resolved.

**Amendment, session 01 continuation.** All three ambiguities are resolved:
A1 to dip (structure wins), A2 and A3 to relative strength (closed by
decision 6.19). **This file now contains no open ambiguities.** Section 3
records each resolution with its resolving decision.

Completeness: every line of source was read, and every line containing an
`rsi` token (57 lines, grep with positive control) was reconciled against
this inventory. Every registered RSI is consumed at least once; there are no
orphan registrations. Comparison sites addressed through the dict aliases
`r`, `r10`, `r20` are captured via the dict constructions at lines 186 and
210–212.

## 1. Registrations

| Lines | Sleeve | Period | Tickers |
|---|---|---|---|
| 65, 67–71 | T10 | 10 | QQQE VTV VOX TECL VOOG VOOV XLP TQQQ XLY FAS SPY SOXL SPXL LABU XLK KMLM |
| 74–77 | T11 | 10 | SPY IOO TQQQ VTV XLF XLK KMLM PSQ BND QQQ IEF |
| 78–79 | T11 | 20 | TLT PSQ AGG |
| 80 | T11 | 60 | SH |
| 89–92 | S2 | 10 | TQQQ SOXL SQQQ BSV |
| 99, 101–102 | S3 | 8 | QQQ SMH |
| 100, 103–106 | S3 | 15 | SPY QQQ SMH SOXL |

## 2. Consumption sites

One row per comparison leg. "Routes to" is the effect of the leg reading true.

### T10 — `_t10_weights`

| # | Line | Ticker | Period | Comparison | Routes to | Function |
|---|---|---|---|---|---|---|
| 1 | 188 | QQQE | 10 | RSI > 79 | UVXY (disjunction) | exhaustion |
| 2 | 188 | VTV | 10 | RSI > 79 | UVXY | exhaustion |
| 3 | 188 | VOX | 10 | RSI > 79 | UVXY | exhaustion |
| 4 | 189 | TECL | 10 | RSI > 79 | UVXY | exhaustion |
| 5 | 189 | VOOG | 10 | RSI > 79 | UVXY | exhaustion |
| 6 | 189 | VOOV | 10 | RSI > 79 | UVXY | exhaustion |
| 7 | 190 | XLP | 10 | RSI > 75 | UVXY | exhaustion |
| 8 | 190 | TQQQ | 10 | RSI > 79 | UVXY | exhaustion |
| 9 | 190 | XLY | 10 | RSI > 80 | UVXY | exhaustion |
| 10 | 191 | FAS | 10 | RSI > 80 | UVXY | exhaustion |
| 11 | 191 | SPY | 10 | RSI > 80 | UVXY | exhaustion |
| 12 | 193 | TQQQ | 10 | RSI < 30 | TECL | dip |
| 13 | 194 | SOXL | 10 | RSI < 30 | SOXL | dip |
| 14 | 195 | SPXL | 10 | RSI < 30 | SPXL | dip |
| 15 | 196 | LABU | 10 | RSI < 25 | LABU | dip |
| 16 | 200 | XLK vs KMLM | 10 v 10 | RSI(XLK) > RSI(KMLM) | risk-on basket / bear split | relative strength |

### T11 — `_t11_weights`

| # | Line | Ticker | Period | Comparison | Routes to | Function |
|---|---|---|---|---|---|---|
| 17 | 220 | SPY | 10 | RSI > 79 | tier-1 branch | exhaustion |
| 18 | 220 | IOO | 10 | RSI > 79 | tier-1 branch | exhaustion |
| 19 | 220 | TQQQ | 10 | RSI > 79 | tier-1 branch | exhaustion |
| 20 | 221 | VTV | 10 | RSI > 79 | tier-1 branch | exhaustion |
| 21 | 221 | XLF | 10 | RSI > 79 | tier-1 branch | exhaustion |
| 22 | 223 | SPY | 10 | RSI > 81 | UVXY (tier 2) | exhaustion |
| 23 | 223 | IOO | 10 | RSI > 81 | UVXY | exhaustion |
| 24 | 223 | TQQQ | 10 | RSI > 81 | UVXY | exhaustion |
| 25 | 224 | VTV | 10 | RSI > 81 | UVXY | exhaustion |
| 26 | 224 | XLF | 10 | RSI > 81 | UVXY | exhaustion |
| 27 | 230 | TQQQ | 10 | RSI < 30 | TQQQ | dip |
| 28 | 231 | SPY | 10 | RSI < 30 | SPXL | dip |
| 29 | 235 | XLK vs KMLM | 10 v 10 | RSI(XLK) > RSI(KMLM) | long-tech basket / trend check | relative strength |

### T11 — `_t11_bond_baller` (bear sub-model 1)

| # | Line | Ticker | Period | Comparison | Routes to | Function |
|---|---|---|---|---|---|---|
| 30 | 156 | TLT vs PSQ | 20 v 20 | RSI(TLT) > RSI(PSQ) | QQQ | relative strength |
| 31 | 158 | PSQ | 10 | RSI < 35 | PSQ | dip (A1, resolved) |
| 32 | 159 | AGG vs SH | 20 v 60 | RSI20(AGG) > RSI60(SH) | TQQQ, else PSQ | relative strength (A2, closed by 6.19) |
| 33 | 162 | IEF vs PSQ | 10 v 20 | RSI10(IEF) > RSI20(PSQ) | PSQ, else SQQQ | relative strength (A3, closed by 6.19) |

### T11 — `_t11_feaver_bear` (bear sub-model 2)

| # | Line | Ticker | Period | Comparison | Routes to | Function |
|---|---|---|---|---|---|---|
| 34 | 172 | BND vs QQQ | 10 v 10 | RSI(BND) > RSI(QQQ) | QLD, else BTAL (crash branch) | relative strength |
| 35 | 175 | PSQ | 10 | RSI < 35 | PSQ | dip (A1, resolved) |
| 36 | 176 | AGG vs SH | 20 v 60 | RSI20(AGG) > RSI60(SH) | TQQQ, else PSQ | relative strength (A2, closed by 6.19) |
| 37 | 179 | IEF vs PSQ | 10 v 20 | RSI10(IEF) > RSI20(PSQ) | PSQ, else SQQQ | relative strength (A3, closed by 6.19) |

Sites 35–37 are textual duplicates of 31–33 in a second helper; they are
distinct call sites in code and are listed as such.

### S2 — `_s2_weights`

| # | Line | Ticker | Period | Comparison | Routes to | Function |
|---|---|---|---|---|---|---|
| 38 | 264 | TQQQ | 10 | RSI > 79 | UVXY, else TQQQ | exhaustion |
| 39 | 266 | TQQQ | 10 | RSI < 31 | TECL | dip |
| 40 | 267 | SOXL | 10 | RSI < 30 | SOXL | dip |
| 41 | 269 | SQQQ vs BSV | 10 v 10 | RSI(SQQQ) > RSI(BSV) | SQQQ, else BSV | relative strength |

### S3 — `_s3_weights`

| # | Line | Ticker | Period | Comparison | Routes to | Function |
|---|---|---|---|---|---|---|
| 42 | 280 | SPY | 15 | RSI > 72 | vol position (disjunction) | exhaustion |
| 43 | 281 | QQQ | 15 | RSI > 72 | vol position | exhaustion |
| 44 | 282 | SMH | 15 | RSI > 72 | vol position | exhaustion |
| 45 | 283 | SOXL | 15 | RSI > 72 | vol position | exhaustion |
| 46 | 294 | QQQ | 8 | RSI < 29 | SOXL (disjunction) | dip |
| 47 | 294 | SMH | 8 | RSI < 31 | SOXL | dip |

## 3. Ambiguous sites — all resolved

**A1 — `RSI10(PSQ) < 35`, lines 158 and 175. Resolved to dip.** By structure
this is an oversold threshold routing to a long entry in the tested
instrument, which is the dip shape. The call site is a threshold test with a
less-than comparison, so decision 6.4's oversold value governs its threshold
under the re-specification and 35 becomes 30. Assigning its period to
exhaustion while its threshold comes from the oversold decision would split
one call site across two functions and make the grid incoherent at that node:
structure wins. The economic reading — that an inverse ETF at a low RSI is
fading a rally in the underlying, and by 00C's measured identity
RSI(inverse) ≈ 100 − RSI(underlying) the site is approximately
RSI(QQQ) > 65 — is retained as an observation for the writeup, not as a
taxonomy assignment. At the grid extremes the site sweeps with dip.

**A2 — `RSI20(AGG) > RSI60(SH)`, lines 159 and 176. Closed by decision
6.19: relative strength, both sides at 14.** The original flag stands as
history: the 60-session side is six times the period of every other RS leg,
suggesting a slow regime gauge, and the two sides disagree on period, so
"the" RS period was not well defined at this site in source. Decision 6.19's
recorded text resolves exactly this call site — the bond_baller RSI(20)
against RSI(60) mismatch resolves into the relative-strength period applied
to both sides. Not an open ambiguity.

**A3 — `RSI10(IEF) > RSI20(PSQ)`, lines 162 and 179. Closed by decision
6.19: relative strength, both sides at 14.** Same shape as A2, a pairwise
comparison with mismatched periods on the two sides; 6.19's resolution
applies. The observation that the `r20["PSQ"]` side reuses the registration
created for the TLT comparison at line 156, so the asymmetry may be
implementation convenience rather than intent, stands as history.

## 4. Function → period summary

| Function | Source periods observed | Spec (6.1) | Grid |
|---|---|---|---|
| exhaustion | 10 (T10, T11, S2), 15 (S3) | 14 | 7 / 28 |
| dip | 10 (T10, T11, S2), 8 (S3) | 14 | 7 / 28 |
| relative strength | 10, 20, 60 (incl. mixed-period pairs) | 14 | 7 / 28 |

Source is internally inconsistent on period *within* every function (S3 runs
exhaustion at 15 while the other sleeves run it at 10; S3 runs dip at 8; RS
spans 10/20/60). Collapsing each function to a single period is therefore a
re-specification, not a relabelling; the per-site divergences are recorded in
step 7 (`parameter-divergence.csv`). At every pairwise site both sides take
the single RS period, so the mixed-period asymmetries of A2/A3 do not survive
the spec.

## 5. Excluded from the mapping

- **Readiness sites** (lines 116–151, 186–187, 196, 199, 210–212, 234):
  `is_ready` checks and ready-filtered dict constructions. These are
  readiness conventions, which this session does not take from source; the
  spec's unavailable-input rule replaces them (threshold unavailable → false,
  pairwise unavailable → raise).
- **Unavailability defaults at consumption** (lines 188–193): `r.get(t, 0)`
  makes an unready overbought leg read false, `r.get("TQQQ", 50)` makes an
  unready dip leg read false. Same observable effect as the spec's threshold
  rule, achieved by sentinel defaults; replaced, not carried.
- **KMLM substitution.** Sites 16 and 29 read KMLM; under step 4 these become
  `TREND_SIGNAL_SERIES` (RYMFX) per decision 2.5. The third, fourth and fifth
  KMLM sites (SMA-20 registration at line 84 and the price/SMA test feeding
  line 239) are SMA sites, not RSI sites, and fall outside this mapping.
- **Thresholds.** Recorded verbatim in the comparison column; their
  divergences from the 70/80/30 tiers are step 7 material, not period
  mapping.
