# S&P 500 VIX Short-Term Futures Index — methodology extract

Fetch date: **2026-08-17**.

---

## 1. Provenance and what could not be retrieved

### Attempted, primary host — FAILED

| URL | Result |
|---|---|
| `https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-vix-futures-indices.pdf` | **HTTP 403** via WebFetch and via `requests` |
| `https://www.spglobal.com/spdji/en/methodology/article/sp-vix-futures-indices-methodology/` | **HTTP 403** via WebFetch and via `requests` |

Retried with a full browser header set (User-Agent, Accept, Accept-Language,
Referer, Sec-Fetch-*). Still 403. spglobal.com refuses automated access
regardless of headers. Search results indicate the current primary edition is
**March 2026**; that edition was **not** obtained and is **not** the basis for
anything below.

### Obtained — the S&P document itself, from third-party hosts

Two genuine S&P Dow Jones Indices editions were retrieved in full:

| Edition | Pages | Host | SHA-256 (first 16) |
|---|---|---|---|
| **October 2021** (primary basis for implementation) | 25 | `https://www.globalx.ca/wp-content/uploads/2024/08/VIX-Index-Methodology.pdf` | `c2a1a5e0fb62e0ae` |
| **October 2017** (used to date the calculation-window change) | 17 | `http://xqdoc.imedao.com/16168ab738b3a1693fee55ed.pdf` | `c89bd3ae125ed51c` |

Both carry the S&P cover block "S&P Dow Jones Indices: Index Methodology / S&P
VIX Futures Indices Methodology" and the S&P copyright disclaimer.

**Status classification.** This is the **primary document obtained from a
secondary host**, which is not the same thing as a secondary source. The text and
formulas below are quoted from the S&P document itself, not from a third party's
description of it. What is *not* verified is that the March 2026 edition still
says the same thing. Everything below should be read as "as documented in the
October 2021 edition".

---

## 2. Index objective and contracts

> "The indices measure the return from a rolling long position in two VIX futures
> contracts with adjacent maturities. Each index rolls daily throughout each
> month from the shorter-term VIX futures contract into the longer-term VIX
> futures contract."

Table 1 of the document:

| Index | Underlying Contracts | Roll Out (m) | Roll In (n) |
|---|---|---|---|
| S&P 500 VIX Short-Term Futures Index | 1st, 2nd | 1st | 2nd |

So the Short-Term index holds only the first and second month contracts, rolling
from the 1st into the 2nd.

---

## 3. Roll Period definition

Quoted:

> "For all the indices except for the S&P 500 VIX Front Month Futures Index, the
> Roll Period starts after the close on the Tuesday prior to the monthly Cboe VIX
> Futures Settlement Date (the Wednesday falling 30 calendar days before the S&P
> 500 option expiration for the following month), and runs through the Tuesday
> prior to the subsequent month's Cboe VIX Futures Settlement Date. Thus, the
> indices are rolling on a continual basis. On the business date after the current
> Roll Period ends the following Roll Period begins."

---

## 4. Daily weight formulas

Quoted, for the S&P 500 VIX Short-Term / 2M / 3M / 4M Futures Index:

```
CRW_m,t = 100 * (dr / dt)
CRW_n,t = 100 * ((dt - dr) / dt)
```

> "**dt** = The total number of business days in the current Roll Period beginning
> with, and including, the starting Cboe VIX Futures Settlement Date and ending
> with, but excluding, the following Cboe VIX Futures Settlement Date. The number
> of business days stays constant in cases of a new holiday introduced intra-month
> or an unscheduled market closure."
>
> "**dr** = The total number of business days within a Roll Period beginning with,
> and including, the following business day and ending with, but excluding, the
> following Cboe VIX Futures Settlement Date. The number of business days includes
> a new holiday introduced intra-month up to the business day preceding such a
> holiday."

Note that `dr` is counted from **the following business day**, i.e. from t+1.

### Index level and daily return

Quoted equations (1)-(4):

```
IndexER_t   = IndexER_{t-1} * (1 + CDR_t)                        (1)
CDR_t       = TDWO_t / TDWI_{t-1} - 1                            (2)
TDWO_t      = Σ_{i=m..n}  CRW_{i,t-1} * DCRP_{i,t}               (3)
TDWI_{t-1}  = Σ_{i=m..n}  CRW_{i,t-1} * DCRP_{i,t-1}             (4)
```

where `CRW_{i,t}` is the Contract Roll Weight of the ith contract on date t and
`DCRP_{i,t}` is the **Daily Contract Reference Price** of the ith contract on
date t.

**This is the single most important structural point.** Both the numerator and
the denominator use `CRW_{i,t-1}` — *yesterday's* weights. The daily return is
therefore the return on a position actually held overnight. It is **not** the
change in the level of a re-interpolated price. The Session 00A interpolation
series differs precisely here: its daily change mixes the price move with the
change in interpolation weights.

---

## 5. Settlement price used

The document names the input `DCRP_{i,t}`, "Daily Contract Reference Price of the
ith VIX Futures Contract on date t".

**The October 2021 edition does not define DCRP further.** It is referenced on
pages 5 and 14 and defined nowhere in the document. There is no statement in the
retrieved text of the form "the daily settlement price published by CFE". This is
recorded as a gap, not as a resolved fact. The Index Policy section does refer to
"the most recent prior closing futures price published by the Cboe Futures
Exchange" in the context of unexpected exchange closures, which indicates the
input is the CFE published price, but that is an inference from an adjacent
clause rather than a definition.

For implementation, `settle_idx` from the Session 00A panel — the CFE published
daily settlement price, normalised for the 2007 quotation change — is used as
DCRP. Flagged as an implementation assumption.

### Missing-contract interpolation

The document specifies a square-root-of-time interpolation for historical periods
when a required contract was not listed, of the form

```
DCRP²_{i,t} = DCRP²_{i-1,t} + (BDays(T_i - T_{i-1}) / BDays(T_{i+1} - T_{i-1})) * (DCRP²_{i+1,t} - DCRP²_{i-1,t})
```

with variants for two and three consecutive unlisted contracts, where `T_i` is the
last trade day of the ith contract. It also states, for the mid-term portfolio:

> "For the purpose of the historical mid-term portfolio calculations, when the ith
> future was not listed on day t, the closing price on the previous day, t-1, was
> used."

Relevant here because the Session 00A panel shows an incomplete listing cycle in
2004-2005.

---

## 6. Timestamp at which the index is struck

### Current (October 2021 edition)

> "Holiday Schedule — The indices are calculated daily from 7:00 PM (day prior) to
> **4:00 PM New York Time**, excluding holidays and weekends."

### Previous (October 2017 edition)

> "Holiday Schedule — The index is calculated daily from 3:00 AM EST to **4:25 PM
> EST**, excluding holidays and weekends."

### The documented change

Appendix I of the October 2021 edition, "Methodology Changes", lists exactly two
entries, both effective **10/23/2020 (after close)**:

| Change | Previous | Updated |
|---|---|---|
| Index Name | S&P 500 VIX Short-Term Futures Index **(0930-1615 ET)** (USD) ER | S&P 500 VIX Short-Term Futures Index **(0930-1600 ET)** (USD) ER |
| **Change in VIX Settlement Times** | **4:15 PM ET stop time** | **4:00 PM ET stop time** |

This is the S&P side of a Cboe change. See section 7.

### Real-time variants

The document also describes a separate index, "S&P 500 VIX Short-Term Futures
Index (0930-1600 ET) (USD) ER", which

> "follows the same methodology as the S&P 500 VIX Short Term Futures Index ER,
> with the exception of real-time calculation hours. For real-time calculation,
> the index follows the U.S. equity trading schedule, opening at 9:30am ET. **The
> official final closing index levels will be the same** as the S&P 500 VIX Short
> Term Futures Index ER."

So the closing level is common across the real-time and end-of-day variants; only
intraday dissemination hours differ. Tickers: `SPVXSP` (ER end-of-day),
`SPVXSTR` (TR end-of-day), `VXXIDSPE` (the 0930-1600 ET variant).

---

## 7. Cboe settlement time — primary sources (Step 5)

Two primary Cboe documents were retrieved in full.

**Cboe notice, Reference ID C2020092202**, "Adjustment of Daily Marking and
Settlement Price Reference Time for Proprietary Index Products":
https://cdn.cboe.com/resources/release_notes/2020/Adjustment-of-Daily-Settlement-Time-for-Proprietary-Index-Products-Notice.pdf

> "Effective **October 26, 2020**, subject to regulatory review, Cboe will
> transition the daily marking time and daily settlement price calculation for
> various proprietary index options and futures, respectively, from **3:15 p.m. to
> 3:00 p.m. CT** (noon CT on early market close days)."
>
> "Cboe Futures Exchange ("CFE") will transition the time in relation to which
> daily settlement prices are calculated for the following products from 3:15 p.m.
> to 3:00 p.m. CT ... Cboe Volatility Index ("VX") futures ... Mini Cboe Volatility
> Index ("VXM") futures. These daily settlement prices will be disseminated
> immediately following confirmation of the values by the CFE Trade Desk which will
> generally be prior to the 3:15 p.m. CT close."

**CFE rule certification CFE-2020-028**, filed with the CFTC 2020-09-23:
https://cdn.cboe.com/resources/regulation/rule_filings/pending/2020/20-028-Daily-Settlement-Determination-Time.pdf

> "The time in relation to which the daily settlement price of a VX futures
> contract is **currently** determined is the close of regular trading hours in VX
> futures. On a normal business day, VX futures have extended trading hours from
> 5:00 p.m. (previous day) to 8:30 a.m., regular trading hours from 8:30 a.m. to
> 3:15 p.m., and extended trading hours from 3:30 p.m. to 4:00 p.m. Accordingly,
> the time in relation to which the daily settlement price of a VX futures contract
> is **currently** determined is **3:15 p.m.**" (all times CT)
>
> "The Amendment will become effective on or after October 7, 2020, on an
> implementation date to be announced by the Exchange through the issuance of an
> Exchange notice."

Also relevant to settlement-day treatment:

> "TAS transactions are not permitted in an expiring VX futures contract on the
> business day of its final settlement date, and all trading in an expiring VX
> futures contract ends at **8:00 a.m.** on its final settlement date."

### Conclusion on the timestamp question

**3:15 p.m. CT = 4:15 p.m. ET** was the VX daily settlement reference time up to
and including **2020-10-23**. **3:00 p.m. CT = 4:00 p.m. ET** applies from
**2020-10-26**. The S&P effective date (10/23/2020 after close) and the Cboe
effective date (10/26/2020) are the same event: Friday close, Monday live.

**From 2020-10-26 the VX settlement reference time and the US equity close
coincide at 16:00 ET.** The 15-minute mismatch invoked in Session 00A therefore
**cannot** apply to 2022. It can apply to 2018. This is tested empirically in
`timestamp-diagnostics.csv` and reported in `REPORT.md`.

### Does CFE publish a separate 16:00 ET mark?

No evidence was found that CFE published a *separate* VX mark struck at 16:00 ET
alongside the 16:15 ET settlement before 2020-10-26. The C2020092202 notice
describes a *transition* of the single daily settlement price reference time, not
the addition of a second mark. The "Daily Final Indicative Prices" file described
in the same notice covers index **options** (SPX/SPXW, DJX, RUT, VIX/VIXW, ESG),
not VX futures.

**Whether the settlement reference time changed at any point between 2004 and
2020 is inconclusive.** The CFE-2020-028 filing establishes the pre-change time
as the close of regular trading hours and states that this was 3:15 p.m. CT as of
2020, but it does not state when regular trading hours were last altered. Cboe's
regulatory circular archive under `cdn.cboe.com/resources/regulation/circulars/`
returned HTTP 403 in Session 00A and was not re-attempted here. It is **not**
concluded that the time was unchanged from 2004 to 2020.

---

## 8. Treatment of settlement days

Assembled from the roll-period and dr/dt definitions:

- The Roll Period boundary is the **Cboe VIX Futures Settlement Date**, the
  monthly Wednesday. `dt` counts that date **inclusive**; the next settlement date
  is **excluded**.
- On the settlement date itself, `dr = dt - 1`, so `CRW_m = 100(dt-1)/dt` and
  `CRW_n = 100/dt`. The contract labels have already advanced: the contract that
  settled that morning is out of the index, the old 2nd month is the new 1st.
- On the Tuesday before the next settlement date, `dr = 0`, so `CRW_m = 0` and
  `CRW_n = 100`. The position is fully in the second contract by that close, which
  is what makes the label shift on the following Wednesday continuous.
- Note a tension between prose and formula: the prose says "After the close on the
  Tuesday, corresponding to the start of the Roll Period, **all** of the weight is
  allocated to the shorter-term (i.e. mth month) contract", while the formula gives
  `(dt-1)/dt` — about 0.95 for a 21-business-day period — on the settlement date.
  **The formula is implemented**, since it is the operative specification.
- Unscheduled closures: the roll for that day is carried to the next Cboe business
  day, the daily roll percentage is fixed when the index is fully rolled and stays
  constant through the month, and `dt` does not change. A worked example for the
  October 2012 Sandy closure is given in the document.

---

## 9. What this session implements

Construction **B** implements sections 3, 4 and 8 exactly as quoted, with:

- `DCRP` = `settle_idx` from `data/interim/vx-panel.parquet` (implementation
  assumption, see section 5).
- Business days = the VX session calendar observed in the panel.
- Roll-period boundaries = the observed monthly expiry dates in the panel, which
  are the Cboe VIX Futures Settlement Dates.
- Contract-level weight carry, so that `CRW_{i,t-1}` attaches to the same physical
  contract on both sides of equation (2) across a label change.

The missing-contract interpolation of section 5 **is** implemented, because it is
needed: on **48 sessions in 2004-2006** the true 2nd-month contract required by
Table 1 had not yet been listed. All 48 were resolved by the primary documented
case (a listed contract on each side, variance-linear in business days between
last trade days); none required the extrapolation variants. Every filled session
is flagged `price_fill` in `data/interim/vx-cm30-b.parquet`.

Not implemented: the total-return overlay (equation 5, 91-day T-bill accrual). It
is recorded and is not needed for the excess-return comparison performed here.
