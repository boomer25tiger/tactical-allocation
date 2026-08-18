# Step 4 — RYMFX strategy changes after 2013

**Question.** 2.5 recorded three Guggenheim strategy changes (2011-07-11,
2012-09-27, 2013-01-29), all in-sample. Did the fund change again after
2013 — and in particular after August 2021, which would place a
construction break inside the 2.10 holdout?

**Method.** SEC EDGAR full-text search (efts.sec.gov, coverage 2001+)
restricted to Rydex Series Funds (CIK 899148), phrase
"Managed Futures Strategy Fund", 2013-08-01 through 2026-08-17, plus the
connected EDGAR MCP tools for entity/filing resolution. Positive control:
the search machinery first had to find the trust's known-present 497 of
2026-08-04 (2 hits in the date window) before any negative was read.
424 trust filings mention the fund in the period; every 497 supplement
among them was fetched and classified by body content.

## Findings — every relevant filing, with dates

| Filing date | Form | Accession | What it does to the Managed Futures Strategy Fund |
|---|---|---|---|
| 2015-03-26 | 497 | 0001628280-15-001973 | **Class H redesignated Class P** effective after close of business 2015-04-30. Share class C000038557 keeps ticker **RYMFX** across the redesignation (headers show "C000038557 H-Class Shares RYMFX" before, "C000038557 Class P RYMFX" after; the 2016 SAI states "Class H shares of each Fund were re-designated as Class P shares"). A relabeling of the same share class — **the series in use is continuous; no effect on the data.** |
| 2015-05-06 | 497 | 0001628280-15-003810 | Annual statutory prospectus restatement (routine; contains the standard Principal Investment Strategies sections, not changes) |
| 2016-02-19 | 497 | 0001628280-16-011438 | Annual SAI restatement (also documents the H→P redesignation retrospectively) |
| 2016-07-07 | 497 | 0001628280-16-017515 | 12(d)(1) exemptive-order eligibility for OTHER trust funds; Managed Futures explicitly listed among the "Ineligible Funds" — no change to it |
| 2018-03-07 | 497 | 0001628280-18-002831 | SAI supplement: trustee holdings tables; fund named in tables only |
| 2018-06-01 | 497 | 0001628280-18-007514 | Advisory-fee breakpoints added for other funds; Managed Futures explicitly **excluded** |
| 2018-11-02 | 497 | 0001628280-18-013370 | Annual prospectus restatement (routine) |
| 2022-03-31 | 497 | 0001683863-22-002839 | **Portfolio manager added** (John Marchelya joins Byrum and Harder). Personnel only. |
| 2022-07-08 | 497 | 0001193125-22-190295 | **Portfolio manager departs** (Ryan Harder). The supplement states verbatim: "The portfolio management changes described in this supplement **will not affect the Funds' investment objectives or principal investment strategies** and are not expected to affect the day-to-day management of the Funds." |
| 2023-09-29 | 497 | 0001683863-23-006766 | **Portfolio manager added** (Adrian Bachman). Personnel only. |

## Verdict

**No change to the fund's investment objective or principal investment
strategies was found after 2013-01-29** in the trust's EDGAR record through
2026-08. The three post-August-2021 filings that touch the fund are
portfolio-manager personnel changes, one of which carries the trust's own
explicit statement that objectives and principal strategies are unaffected.

**The 2.10 holdout consequence is not triggered on this evidence.** Had a
strategy change appeared after August 2021 it would have placed a
construction break inside the holdout; none did. Personnel changes inside
the holdout (2022-03, 2022-07, 2023-09) are noted for completeness — the
fund's own filings classify them as non-strategy.

**The April 2015 redesignation does not affect the series being used**: it
renamed the same share class (C000038557), the ticker RYMFX carried
through, and the session 05 entity check resolves RYMFX to "Guggenheim
Managed Futures Strategy P" — the post-redesignation name of the same
class.

## Bounded-effort caveats

- The search keys on the exact phrase "Managed Futures Strategy Fund" in
  EDGAR FTS. A strategy rewording folded silently into an annual 485BPOS
  restatement (rather than flagged by a 497 supplement) would not surface
  under this method without diffing successive prospectuses year by year,
  which was not done.
- EDGAR FTS coverage starts 2001; irrelevant here since the window is
  2013+.
