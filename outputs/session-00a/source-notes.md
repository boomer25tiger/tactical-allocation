# Session 00a source notes

Fetch date: 2026-08-17 (all pages fetched and all contract files downloaded on
this date, UTC timestamps per contract in `vx-manifest.csv`).

---

## 1. Discovery of the download pattern

### Page inspected

`https://www.cboe.com/us/futures/market_statistics/historical_data/`

The page is a Next.js application. It exposes **no** per-contract links in the
served HTML. The product and year selectors are client-side, so the per-contract
URLs had to be recovered from the application bundle rather than from anchors.

Inspecting the emitted chunks, `/_next/static/chunks/01r6_tccc.gfx.js` contains
the fetch used by the product selector:

```
https://www-api.cboe.com/us/futures/market_statistics/historical_data/product/list/${product}/
```

### Pattern A — current per-contract CSVs

Calling that endpoint for `VX` returns a JSON object keyed by year. Each element
carries `expire_date`, `duration_type`, `futures_root`, `product_display` and a
`path`, for example:

```json
{"product_display": "VX+VXT/F3", "expire_date": "2013-01-16",
 "futures_root": "VX", "duration_type": "M",
 "path": "data/us/futures/market_statistics/historical_data/VX/VX_2013-01-16.csv"}
```

The resolved download pattern is therefore

```
https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_<EXPIRY YYYY-MM-DD>.csv
```

keyed by **expiry date**, not by month code. The API returned years 2013 through
2027, 621 contracts in total. Paths were used verbatim as returned; they were not
reconstructed from a template.

Verification: `VX_2013-01-16.csv` was downloaded first and parsed before any bulk
download. It returned `text/csv` with the header
`Trade Date,Futures,Open,High,Low,Close,Settle,Change,Total Volume,EFP,Open Interest`.

### Pattern B — archive per-contract CSVs

The page links to an archive at
`/us/futures/market_statistics/historical_data/archive/`, which redirects to

`https://www.cboe.com/markets/us/futures/market-statistics/historical-data/settlement-archive`

That page is an accordion with year headings **2004 through 2013**. Only the open
2013 section is server-rendered, exposing twelve links of the form

```
https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_<MONTHCODE><YY>_VX.csv
```

The pattern and the 2004-2013 year range are both taken from that page. The
pre-2013 URLs implied by it were then verified by download rather than assumed.

### Why two patterns were needed

The API pattern is **not usable before 2014**. Compared directly on the same
contract:

| Source | File | Rows | First row | Settle populated |
|---|---|---|---|---|
| Archive | `CFE_F13_VX.csv` | 193 | 2012-04-11 | 185 of 193 |
| Current | `VX_2013-01-16.csv` | 11 | 2013-01-02 | 0 of 11 |

The current-pattern files for 2013 begin at 2013-01-02 and carry an unpopulated
`Settle` column. The archive file for the same contract carries the full life of
the contract and a populated settlement price. From expiry year 2014 onward the
current-pattern files are complete and `Settle` is fully populated.

Probing the archive further showed it extends past the years the page advertises,
but is a frozen snapshot: `CFE_M18_VX.csv` stops at 2018-02-23 mid-contract, and
`CFE_M19_VX.csv` onward return HTTP 403.

**Source policy adopted, fixed before bulk download:**

| Expiry year | Source | Pattern |
|---|---|---|
| 2004-2013 | archive | `CFE_<MONTHCODE><YY>_VX.csv` |
| 2014-2026 | current API | `VX_<EXPIRY>.csv` |

Each source is used only in the range where it was verified complete.

### Weekly exclusion

Weeklies are identified by two independent markers in the API response:
`duration_type == "W"`, and a `product_display` of the form `VX+VXT<NN>/<code>`
where `NN` is a week number, against `VX+VXT/<code>` for monthlies. Only
`duration_type == "M"` was downloaded. The archive pattern is monthly-only by
construction, one file per month code. 449 weekly contracts were excluded; the
full list is in `vx-weeklies-excluded.csv`, counts by year in `REPORT.md`.

### HTTP semantics

The Cboe CDN returns **403, not 404**, for objects that do not exist. Eight
archive URLs returned 403 and are recorded in `vx-absent-urls.csv`. These are
treated as contracts that were never listed, not as download failures; the
distinction is supported by the listing-cycle history in section 3 below. Zero
genuine download failures occurred (`vx-download-failures.csv` is empty apart
from its header).

---

## 2. File format variation

Three variations were found and are handled in `scripts/s00a_parse.py`:

1. Some archive files carry a one-line CFE disclaimer **above** the header row.
   Six of the 2013 archive files do (`CFE_N13`, `Q13`, `U13`, `V13`, `X13`,
   `Z13`). The parser locates the header within the first lines rather than
   assuming line 1.
2. Trade dates appear as `M/D/YYYY` (2004 files), `MM/DD/YYYY` (later archive
   files) and `YYYY-MM-DD` (current files).
3. The `Futures` label appears as `K (May 04)` and as `M (Jun 2016)`.

Rows with zero OHLC and a populated `Settle` occur on ordinary no-trade sessions,
not only on the final settlement day. The final-settlement flag is therefore
anchored to the contract's expiry session, not to the zero-OHLC signature; both
are reported separately.

---

## 3. Contract specification stability, 2004-2026 (step 4 item 5)

### 3.1 Multiplier and price quotation — CHANGE FOUND, 2007-03-26

**Measured in the data first.** The cross-contract median settlement price falls
by a factor of 10 on exactly one date across the whole 2004-2026 sample:

| Trade date | Cross-contract median settle |
|---|---|
| 2007-03-22 | 141.45 |
| 2007-03-23 | 140.85 |
| **2007-03-26** | **14.19** |
| 2007-03-27 | 14.28 |

The measured one-day ratio is 0.100745. No other date in the sample shows a
ratio outside [0.2, 5.0]. The break is simultaneous across every listed contract,
which is the signature of a quotation change rather than a market move. Example,
`VXK2007`: settle 138.70 on 2007-03-23, 13.79 on 2007-03-26.

**Documentary corroboration.** Cboe DataShop's VIX futures product page states:
"Prior to 3/23/2007, VIX had a $100x multiplier. On 3/26/2007 we changed this
multiplier to $1000x and divided the display price by 10," and cites circular
`CFE-IC-2007-003`.

- https://datashop.cboe.com/cfe-vix-volatility-index-futures-trades-quotes

Caveat on sourcing: the primary circular PDF
`https://cdn.cboe.com/resources/regulation/circulars/regulatory/CFE-IC-2007-003.pdf`
returned **HTTP 403** to automated fetch and could not be read directly in this
session. The change is nonetheless established independently by the measurement
above; the documentary reference corroborates the date and gives the mechanism.

**Treatment.** Settlement prices before 2007-03-26 are divided by 10 to put the
whole sample on index points. This is a quotation-convention normalisation, not a
model choice. Every affected row is flagged `scale_normalised` in the panel and
the boundary date is recorded. Note that the decision rule in step 7 is unaffected
by this: listing coverage, volume, roll volume and return correlation are all
scale-invariant or post-2009.

### 3.2 Listing cycle — CHANGES FOUND, several

The number of contract months listed was expanded repeatedly. Cboe rule filings
retrieved from the CFE rule filings index:

- `SR-CFE-2006-007`, 2006-07-03, "VIX Futures Contract Months"
- `SR-CFE-2006-014`, 2006-09-28, "Expansion of Contract Months for VIX & VXD"
- https://www.cboe.com/us/futures/regulation/rule_filings/cfe/2006

A secondary account dates the expansions as four contracts to six on 2006-03-09,
to seven on 2006-04-24, to nine on 2006-10-23 and to ten on 2008-04-22
(https://www.mdpi.com/1911-8074/12/3/113). The exact dates in that account are
**not** confirmed against a primary Cboe circular here and should be treated as
indicative. The direction and rough timing are independently consistent with the
measured simultaneous-listing counts reported in `vx-diagnostics.csv`, which is
the quantity the decision rule actually uses.

This also explains the eight absent archive URLs: January, February, March, April
and December 2004, and April, July and September 2005 were never listed, which is
consistent with an initial cycle of only four to six contract months.

### 3.3 Weekly expirations — CHANGE FOUND, 2015-07-23

CFE listed VIX Weeklys futures from Thursday 2015-07-23.

- https://ir.cboe.com/news/news-details/2015/CBOE-Futures-Exchange-To-List-VIX-Weeklys-Futures-July-23-07-06-2015/default.aspx
- https://www.cftc.gov/sites/default/files/filings/ptc/15/05/ptc052415cfedcm001.pdf

Consistent with the data: the first weekly contract returned by the API expires
2015-08-05, and no weeklies appear before 2015.

### 3.4 Completeness of this search

This search was **not exhaustive**. It covered the multiplier, the listing cycle
and the weekly expirations, which are the specification dimensions that bear on a
constant-maturity construction. Cboe's primary regulatory circular archive is not
machine-readable from this session — circular PDFs under
`cdn.cboe.com/resources/regulation/circulars/` returned HTTP 403 — so the review
rests on the Cboe rule-filings index, Cboe investor-relations releases, Cboe
DataShop product documentation, a CFTC rule submission, and one secondary
academic source, plus direct measurement of the panel.

**Statement required by step 4 item 5:** for the multiplier change and the weekly
listing the search is conclusive and a change was found. For the full set of
listing-cycle changes the search is **inconclusive on exact dates**; changes
certainly occurred, but the precise effective dates could not all be confirmed
against primary Cboe circulars in this session. It is not concluded that no
further specification changes occurred.

---

## 4. Constant-maturity construction (step 5)

The series in `data/interim/vx-cm30.parquet` is a **linear interpolation between
the front two monthly contracts' settlement prices**, weighted by calendar days
to expiry:

```
w1 = (d2 - 30) / (d2 - d1)
w2 = 1 - w1
```

with both weights clipped to [0, 1] and every clipped session flagged.

This is **not** the S&P 500 VIX Short-Term Futures Index roll methodology. That
index holds a rolling long position in the first and second month contracts and
shifts weight by a fixed daily fraction of the roll period, which is a different
construction with different roll behaviour and different transaction-cost
implications. The two will not agree.

Methodology selection for the production volatility series is a separate open
decision and is **not** made in this session. This construction exists here only
to support decision 2.18 and to gate 2.9.

---

## 5. Files written

| File | Contents |
|---|---|
| `vx-manifest.csv` | filename, SHA-256, bytes, row count, download timestamp, source, URL |
| `vx-absent-urls.csv` | URLs returning 403, treated as never-listed |
| `vx-download-failures.csv` | genuine failures (empty) |
| `vx-weeklies-excluded.csv` | all 449 excluded weekly contracts |
| `vx-product-list-raw.json` | raw API response, as fetched |
| `vx-contract-meta.csv` | per-contract span, derived vs rule expiry |
| `vx-diagnostics.csv` | step 4 measurements by year |
| `vxx-validation.csv` | step 6 validation |
| `vx-decision-rule.csv` | step 7 per-condition pass/fail by year |
