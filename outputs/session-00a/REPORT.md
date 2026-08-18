# Session 00a report — VX constant-maturity feasibility

Decision addressed: **2.18**, VX early liquidity inspection. Gates **2.9**, sample
start. Written 2026-08-17. Data pulled 2026-08-17.

No strategy return, Sharpe ratio, allocation, signal or performance statistic is
computed anywhere in this session. Everything below is a count, a distribution or
a data property.

---

## 0. Register file

`docs/DECISIONS-OPEN-v2.md` — **found**. Read at the start of the session. It
records 2.18 as blocking and open, with the recommendation "Inspect before fixing
2.9", and lists 2.9 as "Pending 2.18". The stated order of resolution places 2.18
and 2.20 after 3.1 and 2.5. `docs/CRITICAL-PATH.md` was also present in the
working directory root; both were moved into `docs/` during scaffolding.

---

## 1. Decision rule outcome (step 7)

The rule was applied mechanically. No threshold was changed.

### Result

**First year satisfying all four conditions: 2004.**
**Sample start date: 2004-03-26** — the first constant-maturity session, which is
also the VX inception session.

Years before 2009 **do** pass. The contingency described in step 8 — "if no year
before 2009 passes" — did not occur, so the ragged-sample fallback is not
triggered by this rule.

### Per-condition pass and fail by year

C1 two monthly contracts listed on >= 99% of sessions.
C2 both front contracts nonzero volume on >= 80% of sessions.
C3 nonzero volume in the entered contract on 100% of roll dates.
C4 daily return correlation with VXX >= 0.95, where overlap exists.

| year | c1_frac_two_contracts | c1_pass | c2_frac_both_nonzero_volume | c2_pass | c3_frac_rolls_nonzero_volume | c3_pass | c4_vxx_correlation | c4_pass | all_pass | binding_failures |
|---|---|---|---|---|---|---|---|---|---|---|
| 2004 | 1.0000 | True | 0.9485 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2005 | 1.0000 | True | 0.9167 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2006 | 1.0000 | True | 0.9363 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2007 | 1.0000 | True | 0.9482 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2008 | 1.0000 | True | 0.9526 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2009 | 1.0000 | True | 0.9524 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2010 | 1.0000 | True | 0.9524 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2011 | 1.0000 | True | 0.9563 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2012 | 1.0000 | True | 0.9520 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2013 | 1.0000 | True | 0.9524 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2014 | 1.0000 | True | 0.9603 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2015 | 1.0000 | True | 1.0000 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2016 | 1.0000 | True | 1.0000 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2017 | 1.0000 | True | 1.0000 | True | 1.0000 | True | - | NA (no overlap) | True | - |
| 2018 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.7860 | False | False | C4 VXX correlation |
| 2019 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9596 | True | True | - |
| 2020 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9670 | True | True | - |
| 2021 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9930 | True | True | - |
| 2022 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.8797 | False | False | C4 VXX correlation |
| 2023 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9917 | True | True | - |
| 2024 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9932 | True | True | - |
| 2025 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9925 | True | True | - |
| 2026 | 1.0000 | True | 1.0000 | True | 1.0000 | True | 0.9912 | True | True | - |

### Which condition binds

No year fails on C1, C2 or C3. The only failures anywhere in the sample are C4 in
**2018** (correlation 0.7860) and **2022** (0.8797). Both fall after the first
passing year, so neither affects the start date under a "first year satisfying"
rule.

### Two results that should be flagged rather than smoothed over

**(a) C4 is vacuous for 2004 to 2017.** The rule anticipates VXX overlap from
2009. It does not exist. `yfinance` for ticker `VXX` returns data beginning
**2018-01-25** only, 2,150 rows. The ticker now carries the iPath Series B ETN;
the original 2009-2019 iPath ETN is not served under it. The pull was made
exactly as specified — `auto_adjust=False`, `actions=True`, start 2009 — and
returned nothing before 2018. So for every year from 2004 to 2017 the phrase
"where VXX overlap exists" is not met and C4 imposes no constraint. The start
date is therefore determined by C1, C2 and C3 alone.

**(b) C1, C2 and C3 are satisfied from VX inception.** They are not close calls.
C1 is 1.0000 in every year. C2's minimum across the whole sample is 0.9167 in
2005, against a 0.80 threshold. C3 is 1.0000 in every year, on every one of the
250 roll dates in the sample. On the measurements this rule specifies, 2004 and
2005 are not distinguishable from 2015 or 2024.

This is reported, not adjusted. It is a materially different answer from the
"2006 for VX liquidity" option carried in 2.9, and the gap is worth noting: the
rule tests **whether** trading occurred, not **how much**. Median front-contract
volume in 2004 is 98.5 contracts per day against 88,570 in 2024, roughly three
orders of magnitude, and the rule as written is insensitive to that.

---

## 2. Diagnostic table (step 4)

### 2.1 Listing coverage

Sessions are the distinct trade dates present in the VX panel. For every full
year that count falls in the 250-253 band standard for the US equity calendar,
including 250 in the Sandy-shortened 2012, which indicates no missing sessions.
2004 is partial from inception on 2004-03-26; 2026 is partial to 2026-08-14.

A contract counts as listed on a session when it carries a settlement price
above zero and has not passed its expiry.

| year | sessions | frac_sessions_two_contracts | frac_sessions_three_contracts | n_contracts_median | n_contracts_min | first_date_begins_60_session_2contract_run |
|---|---|---|---|---|---|---|
| 2004 | 194 | 1.0000 | 1.0000 | 4.0 | 3 | 2004-03-26 |
| 2005 | 252 | 1.0000 | 1.0000 | 4.0 | 3 | 2005-01-03 |
| 2006 | 251 | 1.0000 | 1.0000 | 7.0 | 3 | 2006-01-03 |
| 2007 | 251 | 1.0000 | 1.0000 | 9.0 | 8 | 2007-01-03 |
| 2008 | 253 | 1.0000 | 1.0000 | 10.0 | 8 | 2008-01-02 |
| 2009 | 252 | 1.0000 | 1.0000 | 8.0 | 7 | 2009-01-02 |
| 2010 | 252 | 1.0000 | 1.0000 | 8.0 | 7 | 2010-01-04 |
| 2011 | 252 | 1.0000 | 1.0000 | 8.0 | 7 | 2011-01-03 |
| 2012 | 250 | 1.0000 | 1.0000 | 9.0 | 8 | 2012-01-03 |
| 2013 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2013-01-02 |
| 2014 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2014-01-02 |
| 2015 | 253 | 1.0000 | 1.0000 | 9.0 | 8 | 2015-01-02 |
| 2016 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2016-01-04 |
| 2017 | 251 | 1.0000 | 1.0000 | 9.0 | 8 | 2017-01-03 |
| 2018 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2018-01-02 |
| 2019 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2019-01-02 |
| 2020 | 253 | 1.0000 | 1.0000 | 9.0 | 8 | 2020-01-02 |
| 2021 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2021-01-04 |
| 2022 | 251 | 1.0000 | 1.0000 | 9.0 | 8 | 2022-01-03 |
| 2023 | 250 | 1.0000 | 1.0000 | 9.0 | 8 | 2023-01-03 |
| 2024 | 252 | 1.0000 | 1.0000 | 9.0 | 8 | 2024-01-02 |
| 2025 | 251 | 1.0000 | 1.0000 | 9.0 | 8 | 2025-01-02 |
| 2026 | 155 | 1.0000 | 1.0000 | 8.0 | 5 | 2026-01-02 |

First date on which two monthly contracts are continuously available for 60
consecutive sessions: **2004-03-26**, the inception session itself. Two
contracts were available without a break from the first day of trading.

### 2.2 Trading versus marking

Front two contracts. Volume and open interest in contracts.

| year | front_median_volume | second_median_volume | front_median_open_interest | second_median_open_interest | frac_sessions_both_nonzero_volume |
|---|---|---|---|---|---|
| 2004 | 98.5 | 73.0 | 1909.0 | 1661.5 | 0.9485 |
| 2005 | 139.0 | 50.5 | 3572.5 | 970.5 | 0.9167 |
| 2006 | 240.0 | 149.0 | 6782.0 | 5487.0 | 0.9363 |
| 2007 | 1206.0 | 585.0 | 12709.0 | 11858.0 | 0.9482 |
| 2008 | 1731.0 | 897.0 | 16023.0 | 11012.0 | 0.9526 |
| 2009 | 1437.0 | 1165.0 | 8501.5 | 7249.0 | 0.9524 |
| 2010 | 6841.0 | 4798.5 | 27503.5 | 26444.0 | 0.9524 |
| 2011 | 17333.5 | 12287.0 | 51111.5 | 36455.5 | 0.9563 |
| 2012 | 34928.0 | 28850.5 | 93378.0 | 85799.0 | 0.9520 |
| 2013 | 56126.5 | 46102.5 | 130079.5 | 101266.0 | 0.9524 |
| 2014 | 68524.5 | 51799.5 | 130431.5 | 105996.5 | 0.9603 |
| 2015 | 85334.0 | 59836.0 | 121380.0 | 98418.0 | 1.0000 |
| 2016 | 98243.0 | 76861.0 | 151941.0 | 134420.0 | 1.0000 |
| 2017 | 116168.0 | 91276.0 | 221868.0 | 196410.0 | 1.0000 |
| 2018 | 107813.0 | 94971.0 | 145802.5 | 136023.5 | 1.0000 |
| 2019 | 96671.5 | 84394.0 | 134874.5 | 141119.0 | 1.0000 |
| 2020 | 65552.0 | 58397.0 | 96018.0 | 101495.0 | 1.0000 |
| 2021 | 85511.0 | 71449.0 | 114581.5 | 119201.0 | 1.0000 |
| 2022 | 78398.0 | 69561.0 | 100282.0 | 101712.0 | 1.0000 |
| 2023 | 84049.0 | 69795.5 | 133152.5 | 116076.5 | 1.0000 |
| 2024 | 88570.0 | 72240.0 | 132657.0 | 114852.5 | 1.0000 |
| 2025 | 85533.0 | 74177.0 | 126886.0 | 124721.0 | 1.0000 |
| 2026 | 90843.0 | 76108.0 | 144437.0 | 127819.0 | 1.0000 |

The ceiling on "both nonzero" before 2015 is structural, not a liquidity signal.
Until 2015 the expiring contract did not trade on its final settlement session,
so the front leg shows zero volume on roughly 12 sessions a year, which caps the
fraction near 1 - 12/252 = 0.952. From 2015 the expiring contract trades on its
final session and the fraction is exactly 1.000 in every year. The regime change
is visible in the final-settlement signature in section 6: 96.8% of pre-2015
final rows carry the zero-OHLC-zero-volume signature against 0% from 2015.

### 2.3 Roll feasibility

Roll date is the session on which the front contract expires and the second
becomes front. Entered contract is the second.

| year | n_roll_dates | roll_entered_median_volume | frac_rolls_entered_nonzero_volume |
|---|---|---|---|
| 2004 | 7 | 186.0 | 1.0000 |
| 2005 | 9 | 170.0 | 1.0000 |
| 2006 | 12 | 494.5 | 1.0000 |
| 2007 | 12 | 1635.5 | 1.0000 |
| 2008 | 12 | 1892.5 | 1.0000 |
| 2009 | 12 | 2240.5 | 1.0000 |
| 2010 | 12 | 7107.0 | 1.0000 |
| 2011 | 12 | 23358.0 | 1.0000 |
| 2012 | 12 | 48294.5 | 1.0000 |
| 2013 | 12 | 109027.5 | 1.0000 |
| 2014 | 12 | 96124.5 | 1.0000 |
| 2015 | 12 | 107844.0 | 1.0000 |
| 2016 | 12 | 122617.5 | 1.0000 |
| 2017 | 12 | 164421.5 | 1.0000 |
| 2018 | 12 | 136470.5 | 1.0000 |
| 2019 | 12 | 118406.5 | 1.0000 |
| 2020 | 12 | 71316.5 | 1.0000 |
| 2021 | 12 | 103434.0 | 1.0000 |
| 2022 | 12 | 97040.5 | 1.0000 |
| 2023 | 12 | 93416.5 | 1.0000 |
| 2024 | 12 | 144065.0 | 1.0000 |
| 2025 | 12 | 113361.5 | 1.0000 |
| 2026 | 7 | 110329.0 | 1.0000 |

250 roll dates across the sample. The entered contract traded on every one of
them, in every year, including 2004 and 2005. Per-roll detail is in
`vx-roll-dates.csv`.

### 2.4 Spread proxy

On sessions with nonzero volume, median of (high - low) / settle. On zero-volume
sessions, median of |settle change| / settle, computed within contract. The last
two columns give the number of zero-volume sessions behind the second measure.

| year | front_spread_proxy_range_over_settle | second_spread_proxy_range_over_settle | front_spread_proxy_settlechg_over_settle | second_spread_proxy_settlechg_over_settle | n_front_zero_volume_sessions | n_second_zero_volume_sessions |
|---|---|---|---|---|---|---|
| 2004 | 0.0214 | 0.0131 | 0.0488 | 0.0125 | 9 | 3 |
| 2005 | 0.0203 | 0.0126 | 0.0354 | 0.0046 | 9 | 12 |
| 2006 | 0.0275 | 0.0164 | 0.0386 | 1.0000 | 13 | 3 |
| 2007 | 0.0440 | 0.0309 | 0.0133 | 0.0000 | 13 | 1 |
| 2008 | 0.0555 | 0.0433 | 0.0171 | - | 12 | 0 |
| 2009 | 0.0454 | 0.0357 | 0.0192 | - | 12 | 0 |
| 2010 | 0.0478 | 0.0353 | 0.0236 | - | 12 | 0 |
| 2011 | 0.0554 | 0.0438 | 0.0281 | - | 11 | 0 |
| 2012 | 0.0579 | 0.0455 | 0.0301 | - | 12 | 0 |
| 2013 | 0.0433 | 0.0333 | 0.0328 | - | 12 | 0 |
| 2014 | 0.0482 | 0.0352 | 0.0577 | - | 10 | 0 |
| 2015 | 0.0634 | 0.0491 | - | - | 0 | 0 |
| 2016 | 0.0624 | 0.0438 | - | - | 0 | 0 |
| 2017 | 0.0469 | 0.0314 | - | - | 0 | 0 |
| 2018 | 0.0686 | 0.0494 | - | - | 0 | 0 |
| 2019 | 0.0570 | 0.0379 | - | - | 0 | 0 |
| 2020 | 0.0781 | 0.0575 | - | - | 0 | 0 |
| 2021 | 0.0670 | 0.0462 | - | - | 0 | 0 |
| 2022 | 0.0665 | 0.0503 | - | - | 0 | 0 |
| 2023 | 0.0537 | 0.0407 | - | - | 0 | 0 |
| 2024 | 0.0507 | 0.0384 | - | - | 0 | 0 |
| 2025 | 0.0548 | 0.0385 | - | - | 0 | 0 |
| 2026 | 0.0601 | 0.0404 | - | - | 0 | 0 |

**Flagged as an input to later slippage specification (decisions 4.3 and 4.4).**
Reading notes that bear on that use:

- The range-over-settle proxy is available for every year for both legs. It is
  lowest in 2004-2005 (front 0.0214, 0.0203) and rises with liquidity to
  0.045-0.078 later. It is a range measure, not a spread measure, and a *lower*
  value in the illiquid early years reflects fewer trades per session rather
  than a tighter market, so it should not be read as evidence that early
  execution was cheap.
- The zero-volume settle-change proxy rests on very small samples and is not
  usable in most years. The second leg has 3 or fewer zero-volume sessions from
  2006 and none at all from 2008, so the 2006 value of 1.0000 and the 2007 value
  of 0.0000 are single- or triple-observation artifacts. The front leg has about
  a dozen a year until 2014 and none from 2015.
- Neither proxy is a bid-ask spread. Anchoring 4.4's 0-to-50 basis point sweep on
  either would require a separate justification not established here.

### 2.5 Contract specification stability

Reported in `source-notes.md` section 3, with dates and source URLs. Summary:

- **Multiplier and quotation, changed 2007-03-26.** Detected in the data first:
  the cross-contract median settlement price falls by a factor 0.100745 on that
  single date, simultaneously across every listed contract, and on no other date
  in the sample. Corroborated by Cboe DataShop, which states the multiplier went
  from $100 to $1,000 with the display price divided by 10, citing circular
  CFE-IC-2007-003. The primary circular PDF returned HTTP 403 to automated fetch
  and could not be read directly.
- **Listing cycle, expanded repeatedly.** Cboe rule filings SR-CFE-2006-007 and
  SR-CFE-2006-014 confirm contract-month expansions in 2006. Exact effective
  dates for the full sequence could not be confirmed against primary circulars.
- **Weekly expirations, added 2015-07-23.** Confirmed by Cboe investor relations
  and a CFTC rule submission, and consistent with the first weekly contract in
  the data expiring 2015-08-05.
- **The search was not exhaustive and is inconclusive on the full set of
  listing-cycle change dates.** It is not concluded that no further
  specification changes occurred.

---

## 3. VXX validation summary (step 6)

Pull: `yfinance`, ticker VXX, `auto_adjust=False`, `actions=True`, start 2009-01-01.
Returned 2150 rows spanning
**2018-01-25 to 2026-08-14**. Nothing before 2018 was returned. Three 1-for-4
reverse splits are present (2021-04-23, 2023-03-07, 2024-07-24); returns computed
from `Adj Close` and from `Close` agree to within 1e-6 on every session, so the
split adjustment is internally consistent.

Overlap with the constructed series: 2,149 sessions, 2018-01-26 to 2026-08-14.

| year | overlap_sessions | daily_return_correlation | max_rolling_252_cumulative_divergence | cm30_mean_abs_daily_ret | vxx_mean_abs_daily_ret |
|---|---|---|---|---|---|
| 2018 | 234 | 0.7860 | - | 0.03646 | 0.03460 |
| 2019 | 252 | 0.9596 | 0.5083 | 0.02860 | 0.02716 |
| 2020 | 253 | 0.9670 | 2.2678 | 0.04260 | 0.04163 |
| 2021 | 252 | 0.9930 | 0.8089 | 0.03539 | 0.03464 |
| 2022 | 251 | 0.8797 | 0.9487 | 0.03239 | 0.02744 |
| 2023 | 250 | 0.9917 | 0.5154 | 0.02734 | 0.02742 |
| 2024 | 252 | 0.9932 | 0.9433 | 0.03019 | 0.02931 |
| 2025 | 250 | 0.9925 | 0.6070 | 0.03011 | 0.02891 |
| 2026 | 155 | 0.9912 | 0.6318 | 0.02830 | 0.02802 |

Full-overlap daily return correlation: **0.9274**.

Correlation is at or above 0.99 in 2021 and in 2023 through 2026, and fails the
0.95 threshold in 2018 and 2022. The 2018 failure is dominated by 2018-02-05,
where the constructed series returns +96.7% against VXX +33.5%. The construction
was checked arithmetically on the worst days and is correct: on 2022-05-05 the
front contract settled 25.762 then 31.327 and the second 26.985 then 31.372, and
the interpolation reproduces the reported move exactly.

The residual is a timing mismatch, not a construction error. VX settlement is
struck at 16:15 ET while VXX is an exchange-listed note closing at 16:00 ET, so
the two series are sampled 15 minutes apart. In years with violent closes the
mismatch dominates the daily correlation, which is why 2018 and 2022 sit well
below neighbouring years. Level divergence is expected on top of this because
VXX carries fees and roll costs the raw futures series does not; the maximum
rolling 252-session cumulative divergence reaches 2.27 in 2020.

---

## 4. Weekly contracts excluded, by year

449 weekly contracts excluded in total. Identified by `duration_type == "W"` in
the CFE product API and independently by the `VX+VXT<NN>/<code>` form of
`product_display`, against `VX+VXT/<code>` for monthlies. None exist before 2015,
consistent with the 2015-07-23 launch. The archive pattern used for 2004-2013 is
monthly-only by construction. Full list in `vx-weeklies-excluded.csv`.

| expiry_year | weeklies_excluded |
|---|---|
| 2004 | 0 |
| 2005 | 0 |
| 2006 | 0 |
| 2007 | 0 |
| 2008 | 0 |
| 2009 | 0 |
| 2010 | 0 |
| 2011 | 0 |
| 2012 | 0 |
| 2013 | 0 |
| 2014 | 0 |
| 2015 | 17 |
| 2016 | 40 |
| 2017 | 40 |
| 2018 | 40 |
| 2019 | 41 |
| 2020 | 40 |
| 2021 | 40 |
| 2022 | 40 |
| 2023 | 40 |
| 2024 | 41 |
| 2025 | 40 |
| 2026 | 30 |

---

## 5. Download failures and absent contracts

**Genuine download failures: 0.** `vx-download-failures.csv` contains
its header and no rows. Every contract that exists was retrieved on the first
pass; no retry budget was exhausted.

268 contract files were downloaded and hashed. `vx-manifest.csv` carries
filename, SHA-256, byte size, row count and download timestamp for each, plus the
source and the URL used.

**Absent URLs: 8.** The Cboe CDN returns HTTP 403, not 404, for
objects that do not exist. These eight are read as contracts that were never
listed rather than as failures, which is consistent with an initial listing cycle
of only four to six contract months. They are recorded in `vx-absent-urls.csv`.

| expiry_year | month_code | http_status | url |
|---|---|---|---|
| 2004 | F | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_F04_VX.csv |
| 2004 | G | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_G04_VX.csv |
| 2004 | H | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_H04_VX.csv |
| 2004 | J | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_J04_VX.csv |
| 2004 | Z | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_Z04_VX.csv |
| 2005 | J | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_J05_VX.csv |
| 2005 | N | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_N05_VX.csv |
| 2005 | U | 403 | https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_U05_VX.csv |

---

## 6. Data quality flags (step 3)

Panel: **47,158 rows**, 268 contracts, 2004-03-26 to 2026-08-14,
written to `data/interim/vx-panel.parquet`.

| Check | Count | Note |
|---|---|---|
| Duplicate (trade_date, contract) pairs | **0** | none found |
| Non-positive settle rows | **361** | all 2004-2013; 341 also have zero volume and zero open interest |
| Rows with high below low | **425** | **all 425 have zero volume** |
| Final settlement rows | **268** | one per contract |
| Final rows with zero-OHLC, zero-volume signature | **120** | 96.8% of pre-2015 finals, 0% from 2015 |
| Expiry derived vs rule disagreements | **14** | detailed in section 7 |

Notes on each:

- **Non-positive settle.** Concentrated in 2009-2012. 341 of 361 carry
  zero volume and zero open interest simultaneously, the signature of placeholder
  rows written for a listed but not-yet-active contract. Rows with settle at or
  below zero are excluded from the listing-coverage count and from front/second
  selection, so they do not enter any measurement above.
- **High below low.** Every one of the 425 rows occurs on a zero-volume session,
  and only one is a final settlement row. On no-trade sessions the High and Low
  fields do not carry a traded range and can be inverted, for example VXU2013 on
  2012-12-24 with high 22.50 and low 23.40. The pre-registered spread proxy
  already restricts the range measure to nonzero-volume sessions, so these rows
  are excluded from it by construction.
- **Final settlement rows.** Flagged with a boolean column rather than dropped,
  as specified. The flag is anchored to the contract's expiry session. A second
  boolean records the zero-OHLC-zero-volume signature separately, because that
  signature also appears on ordinary no-trade sessions mid-life and therefore
  cannot be used on its own to identify the final row.
- **Quotation rescale.** 3,942 rows before 2007-03-26 are flagged
  `scale_normalised`. Raw `settle` is retained unmodified; `settle_idx` carries
  the value in index points. All measurements use `settle_idx`.

---

## 7. Expiry mismatches

Expiry is derived per contract from the last row of its file, then cross-checked
against the pre-registered rule "30 days before the third Friday of the following
month", applied mechanically with no holiday adjustment.

| contract | expiry_year | month_code | source | derived_expiry | rule_expiry | diff_days | expired | n_rows |
|---|---|---|---|---|---|---|---|---|
| VXN2004 | 2004 | N | archive | 2004-07-14 | 2004-07-21 | -7 | True | 36 |
| VXV2004 | 2004 | V | archive | 2004-10-13 | 2004-10-20 | -7 | True | 38 |
| VXG2008 | 2008 | G | archive | 2008-02-19 | 2008-02-20 | -1 | True | 253 |
| VXH2014 | 2014 | H | api | 2014-03-18 | 2014-03-19 | -1 | True | 186 |
| VXH2019 | 2019 | H | api | 2019-03-19 | 2019-03-20 | -1 | True | 185 |
| VXH2022 | 2022 | H | api | 2022-03-15 | 2022-03-16 | -1 | True | 186 |
| VXM2024 | 2024 | M | api | 2024-06-18 | 2024-06-19 | -1 | True | 185 |
| VXH2025 | 2025 | H | api | 2025-03-18 | 2025-03-19 | -1 | True | 185 |
| VXK2026 | 2026 | K | api | 2026-05-19 | 2026-05-20 | -1 | True | 185 |
| VXQ2026 | 2026 | Q | api | 2026-08-14 | 2026-08-19 | -5 | False | 181 |
| VXU2026 | 2026 | U | api | 2026-08-14 | 2026-09-16 | -33 | False | 162 |
| VXV2026 | 2026 | V | api | 2026-08-14 | 2026-10-21 | -68 | False | 140 |
| VXX2026 | 2026 | X | api | 2026-08-14 | 2026-11-18 | -96 | False | 121 |
| VXZ2026 | 2026 | Z | api | 2026-08-14 | 2026-12-16 | -124 | False | 101 |

Three distinct groups:

- **Five 2026 contracts with large negative differences.** These have not expired
  yet. Their last row is simply the last session in the pull, 2026-08-14, not a
  settlement. Not a data error. For the constant-maturity construction these
  contracts use the rule expiry, carried in the panel as `expiry_effective` and
  flagged by `expired`; the specified last-row derivation is retained unchanged
  in `expiry_date`.
- **Six contracts off by exactly one day**, VXG2008, VXH2014, VXH2019, VXH2022,
  VXM2024, VXH2025, VXK2026. In each case the third Friday of the following month
  falls on a holiday, most often Good Friday, and settlement moves one session
  earlier. The pre-registered rule carries no holiday adjustment, so it is
  expected to miss these. Not a data error.
- **VXN2004 and VXV2004, off by exactly seven days.** Derived 2004-07-14 against
  rule 2004-07-21, and derived 2004-10-13 against rule 2004-10-20. **Unresolved.**
  The evidence points both ways. Against the files being correct: other contracts
  trade normally through 2004-07-15 to 07-21 and 2004-10-14 to 10-20, so the
  exchange was open and these two files stop a week early while their neighbours
  do not. For the files being correct: both final rows carry the usual settlement
  signature, zero OHLC with a populated settle that gaps down from the prior
  close, and the next contract in the cycle is first listed within days of the
  early date. Every other 2004 and 2005 contract matches the rule exactly. This
  is reported rather than resolved; Cboe's VIX settlement series page exposes no
  machine-readable file that would settle it, and no adjustment was made.

---

## 8. Constant-maturity construction and clipping

Written to `data/interim/vx-cm30.parquet`, columns `trade_date`, `cm30_settle`,
`front_contract`, `second_contract`, `d1`, `d2`, `w1`, `clipped`.
5,635 sessions, 2004-03-26 to 2026-08-14. cm30_settle ranges 11.26 to 70.47.
d1 spans 0 to 62 days, d2 spans 27 to 153 days.

Weights are w1 = (d2 - 30) / (d2 - d1), w2 = 1 - w1, both clipped to [0, 1], with
every clipped session flagged. Overall clipping rate **0.1083**,
610 of 5,635 sessions.

| year | cm30_sessions | clipping_rate | frac_sessions_three_contracts | n_contracts_min |
|---|---|---|---|---|
| 2004 | 194 | 0.2474 | 1.0000 | 3 |
| 2005 | 252 | 0.2976 | 1.0000 | 3 |
| 2006 | 251 | 0.0956 | 1.0000 | 3 |
| 2007 | 251 | 0.0956 | 1.0000 | 8 |
| 2008 | 253 | 0.0909 | 1.0000 | 8 |
| 2009 | 252 | 0.0952 | 1.0000 | 7 |
| 2010 | 252 | 0.0952 | 1.0000 | 7 |
| 2011 | 252 | 0.0952 | 1.0000 | 7 |
| 2012 | 250 | 0.0960 | 1.0000 | 8 |
| 2013 | 252 | 0.0952 | 1.0000 | 8 |
| 2014 | 252 | 0.0873 | 1.0000 | 8 |
| 2015 | 253 | 0.0949 | 1.0000 | 8 |
| 2016 | 252 | 0.0952 | 1.0000 | 8 |
| 2017 | 251 | 0.0956 | 1.0000 | 8 |
| 2018 | 252 | 0.0952 | 1.0000 | 8 |
| 2019 | 252 | 0.0873 | 1.0000 | 8 |
| 2020 | 253 | 0.0949 | 1.0000 | 8 |
| 2021 | 252 | 0.0952 | 1.0000 | 8 |
| 2022 | 251 | 0.1036 | 1.0000 | 8 |
| 2023 | 250 | 0.0960 | 1.0000 | 8 |
| 2024 | 252 | 0.0952 | 1.0000 | 8 |
| 2025 | 251 | 0.0876 | 1.0000 | 8 |
| 2026 | 155 | 0.0774 | 1.0000 | 5 |

Clipping runs near 9 to 10% in every year from 2006 onward. This is structural:
after each roll the new front contract can sit more than 30 days from expiry, so
w1 exceeds 1 and is clipped for the few sessions until it falls back inside the
target. 2004 at 0.2474 and 2005 at 0.2976 are roughly three times higher, because
the listing cycle was incomplete in those years and gaps between consecutive
expiries were wider, which pushes d1 above 30 for longer stretches. d1 reaches 62
days in that period against a maximum near 35 once all twelve months are listed.

**Three-contract construction as a fallback: available across the entire sample.**
At least three monthly contracts carry a settlement price on **100.00% of
sessions in every year including 2004 and 2005**. The minimum simultaneous count
is 3 in 2004-2006, 7 to 8 from 2007 onward, and 5 in the partial 2026. Median
simultaneous count rises from 4 in 2004-2005 to 7 in 2006 and 9 from 2012. So a
three-contract construction is feasible from inception on availability grounds.
Whether it would reduce the early-year clipping is not tested here.

As recorded in `source-notes.md` section 4, this is an interpolation construction
and does not replicate the S&P 500 VIX Short-Term Futures Index roll methodology.
Methodology selection for the production series is a separate open decision and
was not made in this session.

---

## 9. Artifacts written

| Path | Contents |
|---|---|
| `outputs/session-00a/source-notes.md` | discovery record, URL patterns, fetch date, spec-change search |
| `outputs/session-00a/vx-manifest.csv` | 268 files: name, SHA-256, bytes, rows, timestamp, source, URL |
| `outputs/session-00a/vx-diagnostics.csv` | step 4 measurements by year |
| `outputs/session-00a/vx-decision-rule.csv` | step 7 per-condition pass/fail by year |
| `outputs/session-00a/vxx-validation.csv` | step 6 correlation and divergence by year |
| `outputs/session-00a/vx-weeklies-excluded.csv` | 449 excluded weekly contracts |
| `outputs/session-00a/vx-absent-urls.csv` | 8 never-listed contracts with URLs |
| `outputs/session-00a/vx-download-failures.csv` | empty, header only |
| `outputs/session-00a/vx-contract-meta.csv` | per-contract span, derived vs rule expiry |
| `outputs/session-00a/vx-roll-dates.csv` | 250 roll dates with entered-contract volume |
| `outputs/session-00a/qc-*.csv` | duplicate, non-positive settle, high-below-low, expiry-mismatch detail |
| `data/interim/vx-panel.parquet` | 47,158-row long panel |
| `data/interim/vx-cm30.parquet` | 5,635-session constant-maturity series |
| `data/raw/vx/` | 268 raw CSVs, unmodified (gitignored) |

Working tree left dirty. Nothing committed.
