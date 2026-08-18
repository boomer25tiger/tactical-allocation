# SMH continuity at the 2011 HOLDRS to VanEck conversion

Session 00C, Step 3. Closes decision 2.20. Nothing is adjusted here.

## Series extent

- First date returned by yfinance: **2000-06-05**
- Last date returned: **2026-08-17**
- Sessions returned: **6,589**
- Nominal conversion reference date used for the window: 2011-12-20 (Merrill Lynch Semiconductor HOLDRS exchanged into the VanEck fund in December 2011)

## Daily total return distribution, 60 sessions either side of the boundary

| window | sessions | first | last | mean % | sd % | min % | p05 % | p95 % | max % |
|---|---|---|---|---|---|---|---|---|---|
| 60 sessions before | 60 | 2011-09-26 | 2011-12-19 | -0.026 | 2.080 | -4.355 | -3.145 | 3.159 | 5.577 |
| 60 sessions after | 60 | 2011-12-20 | 2012-03-16 | 0.341 | 1.231 | -2.133 | -1.553 | 2.327 | 3.984 |
| full history | 6588 | 2000-06-05 | 2026-08-17 | 0.065 | 2.207 | -14.412 | -3.510 | 3.452 | 17.160 |

## Single-day absolute total return above 25 percent, full history

None. Maximum absolute single-day total return over the full history is **17.16 percent** on 2025-04-09.

Largest ten absolute daily moves in the +/- 60 session boundary window:

| date | total return % | close | dividend | split |
|---|---|---|---|---|
| 2011-11-30 | 5.577 | 15.3350 | 0.0000 | 0.00 |
| 2011-11-09 | -4.355 | 15.3750 | 0.0000 | 0.00 |
| 2012-01-18 | 3.984 | 16.4450 | 0.0000 | 0.00 |
| 2011-12-20 | 3.946 | 15.0150 | 0.0000 | 0.00 |
| 2011-11-17 | -3.508 | 15.4050 | 0.0000 | 0.00 |
| 2011-10-27 | 3.403 | 16.2550 | 0.0000 | 0.00 |
| 2011-09-30 | -3.199 | 14.2200 | 0.0000 | 0.00 |
| 2011-10-24 | 3.165 | 15.8100 | 0.0000 | 0.00 |
| 2011-11-11 | 3.158 | 16.0050 | 0.0000 | 0.00 |
| 2011-12-12 | -3.142 | 14.9500 | 0.0000 | 0.00 |

## Trading date gaps

- Reference calendar: SPY sessions over the SMH window, 6,589 sessions.
- SMH sessions over the same window: 6,589.
- Sessions present in SPY and absent in SMH: **0**.
- Sessions present in SMH and absent in SPY: **0**.

No missing sessions. The SMH trading calendar matches SPY exactly over the common window.

- Maximum calendar gap between consecutive SMH sessions: **7 days** ending 2001-09-17.

## Corporate actions near the boundary

No dividend and no split recorded within 200 calendar days either side of the conversion date.

Full history: 14 distributions, 1 splits.

All recorded splits:

| date | split factor | close | prior close | raw close ratio |
|---|---|---|---|---|
| 2023-05-05 | 2.0000 | 124.3800 | 121.8050 | 1.0211 |


### Distribution stream, before and after the conversion

- Distributions recorded **before** 2011-12-20: **0**
- Distributions recorded **on or after** 2011-12-20: **14**
- First recorded distribution anywhere in the series: **2012-12-24**, which is 12.55 years after the first bar.

This is the material finding of Step 3, and it is not a price discontinuity. yfinance records **no distribution at all** across the entire HOLDRS era, 2000-06-05 to 2012-12-24. The HOLDRS was a grantor trust that passed underlying constituent dividends through to holders, so distributions did occur and are simply absent from the feed. Both the total return series built in Step 1 and Yahoo's own adjusted close inherit that absence, which is why the Step 2 diagnostic cannot see it: the two constructions agree with each other while both omit the same cash flows. SMH total return before December 2012 is therefore a price return, and is understated by the semiconductor dividend yield of the period.

## Price and volume level either side of the boundary

| date | close | adj close | volume |
|---|---|---|---|
| 2011-12-13 | 14.6850 | 12.4700 | 15,853,600 |
| 2011-12-14 | 14.4300 | 12.2535 | 16,297,200 |
| 2011-12-15 | 14.5600 | 12.3639 | 5,654,600 |
| 2011-12-16 | 14.5600 | 12.3639 | 5,694,800 |
| 2011-12-19 | 14.4450 | 12.2662 | 3,109,600 |
| 2011-12-20 | 15.0150 | 12.7503 | 1,939,600 |
| 2011-12-21 | 14.8400 | 12.6016 | 1,304,800 |
| 2011-12-22 | 15.2150 | 12.9201 | 2,530,200 |
| 2011-12-23 | 15.3250 | 13.0135 | 621,400 |
| 2011-12-27 | 15.3250 | 13.0135 | 912,400 |
| 2011-12-28 | 15.1400 | 12.8564 | 1,074,800 |

Median volume, 60 sessions before: 15,201,800. 60 sessions after: 2,871,700. Ratio after/before: 0.19.

## Verdict

**Stitched, on price. Discontinuous, on distributions.**

The price series is continuous across the December 2011 conversion: it starts in 2000 during the HOLDRS era, has no missing session relative to the SPY calendar, records no single-day absolute return above 25 percent anywhere in its history, and carries no split or distribution at the conversion boundary. yfinance presents one unbroken price series across the vehicle change, with no marker identifying the conversion.

The distribution series is not continuous. It begins in December 2012, twelve and a half years after the first bar. Everything before that is price return carrying a total return label. Two secondary markers also sit at the boundary and are consistent with a vehicle change rather than a price break: median volume falls by about four fifths across the conversion, and the distribution stream switches on shortly after it.

Nothing was adjusted. The observation that the series is presented as continuous is a statement about what yfinance returns, not a claim that the pre-2011 HOLDRS return stream is economically comparable to the post-2011 fund. The HOLDRS was a fixed basket of grantor-trust receipts with no rebalancing and a shrinking constituent count; the VanEck fund tracks a rebalanced index. That difference is not visible as a price discontinuity and cannot be detected by this test.

