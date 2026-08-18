# Step 5 — Nasdaq-100 Equal Weighted index availability

**Question.** QQQE lists 2012-03-21; the sample starts 2007-01-01; under
2.2 the synthetic requires the underlying index total-return history. Is
the Nasdaq-100 Equal Weighted total-return index obtainable without a
licensing request or purchase?

## What was checked and what each source returned

1. **Stooq** (as part of step 1's vendor work): scripted access blocked —
   returns an HTML interstitial. Not usable.
2. **Yahoo Finance index symbols via yfinance** (the study's existing,
   free, already-frozen-elsewhere source):
   - `^NDXE` — Nasdaq-100 Equal Weighted **price** index: **served.**
     5,098 rows, 2006-05-02 → 2026-08-17.
   - `^NETR` — Nasdaq-100 Equal Weighted **Total Return** index:
     **served.** 5,025 rows, 2006-08-21 → 2026-08-17.

No further sources were tried; the second returned the required series and
the effort bound applied.

## Quality of the reachable series (measured in memory; nothing acquired)

- **Coverage**: `^NETR` from 2006-08-21 gives **92 sessions of headroom
  before the 2007-01-01 sample start** — enough to seed RSI at the grid
  maximum period of 28 before the first sample session.
- **Gaps**: against the SPY session calendar, `^NETR` is missing **3
  interior sessions** in twenty years: 2007-02-26, 2008-10-27, 2010-07-14.
  These are the first genuine post-listing interior gaps encountered in any
  series this study has audited — the session 01 / session 07 null audits
  found zero everywhere else. **If this series is acquired, decision 1.9's
  interior-gap treatment (the reseeding question closed as moot in session
  01) becomes live again for exactly these three sessions.**
- **Sanity**: the TR/price ratio (`^NETR`/`^NDXE`) drifts upward 20.7%
  over 2006–2026 (≈1%/yr, consistent with the index's dividend yield),
  with 4 sessions showing small (>0.1%) ratio drops — index-vendor noise
  at the margin, noted.

## Consequences

**3.9 dissolves the way 3.8 did.** The total-return index is reachable
without a licensing request or purchase, from the same vendor the study
already freezes from. The two fallback consequences the step named — a
time-varying T10 overbought panel with the distortion disclosed, or
dropping QQQE from the panel against an unambiguous source — do not arise.

Not acquired in this session (this session acquires nothing). An
acquisition session would freeze `^NETR` under the 1.1 pull-once protocol,
handle the 3 interior gaps under whatever 1.9 treatment is decided, and
note the 4 ratio-drop sessions in verification.
