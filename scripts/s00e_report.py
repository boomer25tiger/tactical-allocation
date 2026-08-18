"""Session 00e, step 4. Assemble REPORT.md from the artifacts on disk."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s00c_indicators import load_panel, sma, tr_series      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-00e"


def md(df, floats=None, na="-"):
    d = df.copy()
    for c, spec in (floats or {}).items():
        if c in d.columns:
            d[c] = d[c].map(lambda v: na if pd.isna(v) else format(v, spec))
    d = d.astype(object).where(d.notna(), na)
    head = "| " + " | ".join(str(c) for c in d.columns) + " |"
    rule = "|" + "|".join("---" for _ in d.columns) + "|"
    body = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in d.itertuples(index=False)]
    return "\n".join([head, rule] + body)


def main():
    man = pd.read_csv(OUT / "manifest-truncated.csv")
    smh = pd.read_csv(OUT / "smh-return-basis.csv")
    loo = pd.read_csv(OUT / "vote-leave-one-out.csv")

    M = ["SPY", "QQQ", "SMH", "SOXL"]
    tr = tr_series(load_panel())
    cols = {t: (tr[t] > sma(tr[t], 200))[sma(tr[t], 200).notna()] for t in M}
    j = pd.concat(cols, axis=1, join="inner").dropna().astype(bool)
    V = j[M].to_numpy(bool)
    counts = V.sum(axis=1)
    bullfrac = pd.DataFrame({"member": M,
                             "bull_fraction_sma200": [V[:, i].mean()
                                                      for i in range(4)]})
    dist = pd.DataFrame({"bullish_votes": list(range(5)),
                         "sessions": [int((counts == c).sum())
                                      for c in range(5)]})

    mtab = man[["filename", "old_sha256", "new_sha256", "old_rows", "new_rows",
                "old_last_date", "new_last_date"]]
    already = man[man.status == "already_at_or_before_cutoff"]
    multi = man[man.rows_dropped > 1]
    trunc = man[man.status == "truncated"]

    rsi_mean = smh[smh.metric == "mean_abs_rsi_difference"].pivot(
        index="rsi_period", columns="assumed_yield_pct",
        values="value").reset_index()
    rsi_max = smh[smh.metric == "max_abs_rsi_difference"].pivot(
        index="rsi_period", columns="assumed_yield_pct",
        values="value").reset_index()
    rsi_agr = smh[smh.metric == "rsi_threshold_crossing_agreement"].pivot_table(
        index=["rsi_period", "threshold"], columns="assumed_yield_pct",
        values="value").reset_index()
    rsi_dis = smh[smh.metric == "rsi_threshold_crossing_agreement"].pivot_table(
        index=["rsi_period", "threshold"], columns="assumed_yield_pct",
        values="disagree_sessions").astype(int).reset_index()
    sma_agr = smh[smh.metric == "sma_above_below_agreement"].pivot(
        index="sma_length", columns="assumed_yield_pct",
        values="value").reset_index()
    sma_dis = smh[smh.metric == "sma_above_below_agreement"].pivot(
        index="sma_length", columns="assumed_yield_pct",
        values="disagree_sessions").astype(int).reset_index()
    vote = smh[smh.metric.str.startswith("s3_")].pivot(
        index="assumed_yield_pct", columns="metric", values="value").reset_index()
    vote_n = int(smh[smh.metric == "s3_vote_bull_differs"].n_sessions.iloc[0])

    loo_held = loo[loo.threshold_treatment == "held_at_3_unanimity"].pivot(
        index="sma_length", columns="removed_vote", values="flip_count")[M].reset_index()
    loo_moved = loo[loo.threshold_treatment == "moved_to_2_of_3"].pivot(
        index="sma_length", columns="removed_vote", values="flip_count")[M].reset_index()
    loo_heldf = loo[loo.threshold_treatment == "held_at_3_unanimity"].pivot(
        index="sma_length", columns="removed_vote", values="flip_fraction")[M].reset_index()
    loo_movedf = loo[loo.threshold_treatment == "moved_to_2_of_3"].pivot(
        index="sma_length", columns="removed_vote", values="flip_fraction")[M].reset_index()
    win = loo.groupby("sma_length").agg(
        n_sessions=("n_sessions", "first"), first_date=("first_date", "first"),
        last_date=("last_date", "first"),
        frac_bull_full=("frac_bull_full", "first")).reset_index()

    f4, f5 = "0.4f", "0.5f"

    text = f"""# Session 00e report — panel truncation, SMH return basis, vote leave-one-out

Written {pd.Timestamp.now('UTC').date()}. Applies decision **1.14**, informs
**3.12**, informs **6.7**.

No strategy return, Sharpe ratio, allocation, portfolio weight or performance
statistic is computed anywhere in this session. RSI values, SMA comparisons and
vote classifications are properties of individual price series.

---

## 0. Two blocking-adjacent facts established before any work

Both are reported rather than worked around.

### 0.1 `outputs/session-00d/REPORT.md` does not exist

The prompt directs that it be read for context. The directory
`outputs/session-00d/` **exists but is completely empty** — no REPORT.md, no CSVs,
no artifacts of any kind. A filesystem search for anything matching `*00d*`
outside `.venv` and `.git` returns only the empty directory itself, and no file
under `docs/` or `scripts/` references a Session 00D.

Consequence for the Step 1 instruction "if Session 00D wrote any artifact derived
from the equity panel, list it in the report as carrying the partial bar":
**Session 00D wrote no artifact of any kind**, so there is nothing to list. This
session was therefore run without the 00D context the prompt assumes.

### 0.2 Three of the four decisions cited are not in the register

`docs/DECISIONS-OPEN-v2.md` was read. It is unmodified since 2026-08-17 12:06,
which predates Session 00A. Enumerating every decision ID it contains:

| Decision cited by this prompt | Present in register? | Status in register |
|---|---|---|
| **1.14** panel truncation | **No.** Highest 1.x present is 1.13 | — |
| **3.12** SMH return basis | **No.** Highest 3.x present is 3.11 | — |
| **6.7** vote threshold | Yes | **Part 1, Closed**: "Vote threshold — Simple majority" |
| 2.22 (closed by Session 00B) | **No.** Highest 2.x present is 2.21 | — |

So the register on disk is stale relative to the session sequence: it does not
carry 1.14, 3.12 or 2.22, and it records 6.7 as already closed rather than open.
The work below is fully specified by the prompt independently of the register, so
it proceeded. But the instruction to "flag any result contradicting an expectation
in `docs/DECISIONS-OPEN-v2.md`" can only be applied against the expectations the
file actually contains. Section 3.4 does that for the one place it bites.

---

## 1. Panel truncation (step 1, applies 1.14)

Cutoff: **2026-08-14**. Rows dropped, never adjusted. VX files untouched.

Original manifests were copied to `outputs/session-00e/pre-truncation-hashes/`
**before** anything was modified:

- `session-00c__etf-manifest.csv`
- `session-00c__pull-metadata.json`
- `session-00a__vx-manifest.csv`

with their at-copy hashes in `_copied-manifests.csv`. The pre-truncation ETF
manifest records `last_date = 2026-08-17` for all 35 tickers, confirming the
partial bar was present.

A file was rewritten **only** where rows were actually removed, so files needing
no truncation keep their original bytes and therefore their original hash. Where
`old_sha256 == new_sha256`, the file was not touched.

**Result: 39 target files. 36 truncated, 3 needed no truncation, 1 dropped more
than one row.** Every file now ends 2026-08-14.

### 1.1 Anomaly A — three files were already at or before the cutoff

{md(already[["filename", "old_last_date", "old_rows", "rows_dropped"]])}

The prompt states "Sessions 00A and 00B pulled VXX and VIXY at the same time and
carry the same defect." **They do not.** All three Session 00B series already
ended 2026-08-14 and contained no partial bar:

- The Session 00B yfinance pulls for VIXY and VXX were issued with
  `end="2026-08-16"`, which excludes 2026-08-17 entirely, so no 2026-08-17 bar was
  ever ingested.
- `vixy-nav-proshares-s00b.parquet` is issuer end-of-day NAV from ProShares, which
  only publishes a settled NAV; its last row was 2026-08-14.

These three files were left byte-identical. This is an assumption failure in the
prompt's premise, reported rather than worked around.

### 1.2 Anomaly B — one file dropped 35 rows, not 1

{md(multi[["filename", "old_rows", "new_rows", "rows_dropped", "old_last_date", "new_last_date"]])}

`etf-panel.parquet` is a **long** panel, one row per (date, ticker) pair across 35
tickers. A single partial session is therefore 35 rows, not 1. Verified: every
date in the truncated panel now carries exactly 35 rows, the panel holds exactly
35 distinct tickers, and the new final date is 2026-08-14.

This is a layout artifact, not a data defect. The check as the prompt states it —
"any where more than one row was dropped ... would indicate an assumption
failure" — does not distinguish long-format from wide-format files. Reported as
instructed rather than reconciled.

### 1.3 Full truncation manifest

Also written to `manifest-truncated.csv` with the `status`, `date_carrier` and
`rows_dropped` columns omitted here for width.

{md(mtab)}

### 1.4 Statistics in earlier reports were not recomputed

No CSV under `outputs/session-00a/`, `outputs/session-00b/`, `outputs/session-00c/`
or `outputs/session-00d/` was modified. Those record what was measured at the time.

**Statistics in the 00B, 00C and 00D reports include the partial 2026-08-17 bar
and were not recomputed.** Concretely, every Session 00C table carries
`last_date = 2026-08-17`, and the Session 00B VIXY/VXX validation windows end
2026-08-14 already (section 1.1) so those are unaffected. Session 00D wrote
nothing, so it has no affected artifact (section 0.1).

---

## 2. SMH pre-2013 return basis (step 2, informs 3.12)

### 2.1 The yields are assumptions, not measurements

**Stated plainly: the 1.0, 1.5 and 2.0 percent figures are assumptions. They are
not measured distributions. No actual pre-2013 SMH distribution data was
located.**

The feed records **zero** distributions for SMH before **2012-12-24**, which is
the first of 14 in its whole history. Within the 2006-01-01 to 2013-12-31 build
window there are exactly two actual distributions, 2012-12-24 and 2013-12-23, and
only the first falls inside the 2007-2012 measurement window.

Attempts made to locate a pre-2013 distribution record, all unsuccessful:

| # | Attempt | Result |
|---|---|---|
| 1 | Web search for Semiconductor HOLDRS Trust distribution history 2007-2012 | Returned the trust's structure, the 2011-11-10 Merrill Lynch early-termination notice and the VanEck asset purchase, but **no distribution schedule** |
| 2 | `slickcharts.com/symbol/SMH/dividend` | **HTTP 403** |
| 3 | SEC EDGAR company browse for CIK 0001110511 (SEMICONDUCTOR HOLDRS TRUST) | **HTTP 403** |
| 4 | SEC filing tool, entity resolved as CIK 1110511 "SEMICONDUCTOR HOLDRS TRUST", filing history requested at the maximum 730-day lookback | Entity resolves and reports **87 total filings**, but **0 within reach** — the trust terminated in 2011, roughly 15 years outside the tool's maximum window |

Session 00C had already established the same negative result from the feed side:
14 distributions in full history, first 2012-12-24, and no dividend or split
within 200 calendar days either side of the 2011 HOLDRS-to-VanEck conversion.

### 2.2 Construction

Build window **2006-01-03 to 2013-12-31**, 2,013 sessions. Measurement window
**2007-01-03 to 2012-12-31**, **1,510 sessions**. The 2006 lead-in is sufficient
for every SMA length including 250 — all five lengths report the full 1,510
sessions, with no warm-up loss inside the measurement window.

- **PR**, price return: the series as the feed provides it, `ret_price`
  compounded. Since SMH paid nothing before 2012-12-24 this is also its realised
  total return over almost the whole window.
- **TR(y)**, estimated total return: `ret_tr = ret_price + y/252`, compounded.
  That is a constant annual yield `y` accrued daily on a 252-day basis, which is
  the standard identity `TR_t/TR_{{t-1}} = P_t/P_{{t-1}} + d_t/P_{{t-1}}` with
  `d_t/P_{{t-1}} = y/252`.

Indicators use the Session 00C library unchanged: Wilder RSI with alpha = 1/n and
an SMA seed (decision 1.6), SMA with `min_periods = n`.

### 2.3 Mean absolute RSI difference, PR against TR(y)

{md(rsi_mean, floats={"1.0": f4, "1.5": f4, "2.0": f4})}

Maximum absolute RSI difference over the same window:

{md(rsi_max, floats={"1.0": f4, "1.5": f4, "2.0": f4})}

The mean difference is essentially flat across RSI period — 0.159 to 0.161 points
at 1.0 percent, 0.319 to 0.321 at 2.0 percent — and scales almost exactly linearly
in the assumed yield. The maximum difference does fall with period, from 1.14
points at RSI 7 to 0.61 at RSI 28 under the 2.0 percent assumption.

### 2.4 RSI threshold-crossing agreement

Agreement fraction. Thresholds 70 and 80 are read as `RSI >= t`, thresholds 30 and
20 as `RSI <= t`.

{md(rsi_agr, floats={"1.0": f5, "1.5": f5, "2.0": f5})}

Sessions on which the two bases disagree, out of 1,510:

{md(rsi_dis)}

Worst case anywhere in the grid is **9 sessions of 1,510**, at RSI 7 / threshold
70 / 2.0 percent. RSI 28 disagrees on at most 2 sessions at any threshold or
yield, and never at 20, 30 or 80.

### 2.5 SMA above-or-below agreement

Agreement fraction:

{md(sma_agr, floats={"1.0": f5, "1.5": f5, "2.0": f5})}

Sessions on which the two bases disagree, out of 1,510:

{md(sma_dis)}

The SMA comparison is the more sensitive of the two. Disagreement rises with SMA
length to a peak at 200 — 20, 35 and 47 sessions at 1.0, 1.5 and 2.0 percent — and
eases slightly at 250. This is the expected direction: an accrual applied to the
price makes it drift above its own trailing average, and the longer the average
the longer the lag it has to overcome.

### 2.6 S3 vote outcome, SPY / QQQ / SMH / SOXL, SMA 200, three of four

{md(vote, floats={"s3_vote_bull_differs": "0.0f",
                   "s3_vote_bull_frac_PR": f5,
                   "s3_vote_bull_frac_TR": f5})}

| Assumed yield | Sessions where bull classification differs | Of |
|---|---|---|
| 1.0 % | **6** | {vote_n} |
| 1.5 % | **16** | {vote_n} |
| 2.0 % | **19** | {vote_n} |

**Window limitation, flagged.** The prompt asks for "the number of sessions in
2007 through 2012". That window is **not attainable for the four-member S3 vote**.
SOXL's first session in the panel is **2010-03-11**, and the SMA 200 warm-up
pushes the first evaluable vote session to **2010-12-22**. The vote comparison
therefore covers **2010-12-22 to 2012-12-31, {vote_n} sessions**, which is the last
two years of the requested six, not the whole of it. The RSI and SMA measurements
in 2.3 to 2.5 are unaffected — those are SMH alone and do cover the full 1,510
sessions.

Truncation from Step 1 removed only 2026-08-17 and therefore cannot influence any
measurement in this section, all of which end 2012-12-31.

---

## 3. Vote leave-one-out (step 3, informs 6.7)

### 3.1 Which treatment Session 00C applied — determined

**Session 00C held the threshold constant.** Stated plainly, and established two
independent ways.

**From the code.** `scripts/s00c_structure.py`, in `_vote_rows`:

```python
for thr in range(1, k + 1):
    bull = counts >= thr
    for a in range(k):
        drop = (counts - V[:, a].astype(int)) >= thr    # same thr
```

The reduced three-vote count is compared against the **same** `thr` used for the
full four-vote set. At `thr = 3` that makes the three-vote set require unanimity.

**From reproduction.** Recomputing under the held treatment returns
{int(loo_held.loc[loo_held.sma_length==200,'SPY'].iloc[0])} for SPY,
{int(loo_held.loc[loo_held.sma_length==200,'QQQ'].iloc[0])} for QQQ,
{int(loo_held.loc[loo_held.sma_length==200,'SMH'].iloc[0])} for SMH and
{int(loo_held.loc[loo_held.sma_length==200,'SOXL'].iloc[0])} for SOXL at SMA 200 —
exactly the 408 / 404 / 412 / 12 Session 00C reported.

The session count is **3,934** here against Session 00C's 3,935, because the
partial 2026-08-17 bar has now been truncated. That session changed none of the
four flip counts.

### 3.2 Windows

Native basis per SMA length, matching Session 00C.

{md(win, floats={"frac_bull_full": f5})}

### 3.3 Both treatments

**Treatment 1, threshold held at 3.** A three-vote set requires unanimity. Flip
counts:

{md(loo_held)}

As fractions:

{md(loo_heldf, floats={"SPY": f5, "QQQ": f5, "SMH": f5, "SOXL": f5})}

**Treatment 2, threshold moved to 2 of 3.** Flip counts:

{md(loo_moved)}

As fractions:

{md(loo_movedf, floats={"SPY": f5, "QQQ": f5, "SMH": f5, "SOXL": f5})}

### 3.4 The two treatments invert the ranking

This is the substantive result of Step 3.

At SMA 200, under the held treatment SOXL is by far the **least** consequential
vote to remove, 12 flips against 404 to 412 for the other three. Under the moved
treatment SOXL becomes the **most** consequential, 309 flips against 55, 63 and
213. The same inversion holds at every SMA length from 50 to 250.

The mechanism is exact, not approximate. With the full-set threshold at 3 of 4:

- **Held at 3.** Removing member `a` flips exactly when `a` is bullish and the
  vote count is exactly 3. If `a` is bearish the classification cannot change.
- **Moved to 2.** Removing member `a` flips exactly when `a` is bearish and the
  vote count is exactly 2. If `a` is bullish the classification cannot change.

The two treatments therefore measure disjoint, complementary session sets. Both
identities were verified to hold exactly at SMA 200.

The asymmetry follows from SOXL's much lower bullish rate:

{md(bullfrac, floats={"bull_fraction_sma200": f4})}

Vote count distribution at SMA 200, 3,934 sessions:

{md(dist)}

Of the 412 sessions with exactly three bullish votes, SOXL is the bullish
dissenter on only 12 — it is the odd one out on the other 400. Of the 320 sessions
with exactly two bullish votes, SOXL is bearish on 309. SOXL is simply the member
most often on the bearish side, so it is nearly absent from the set the held
treatment measures and nearly ubiquitous in the set the moved treatment measures.

**Flagged against the register.** `docs/DECISIONS-OPEN-v2.md` records decision 6.8
with the stated rationale "Add a non-equity leg, **since SOXL and SMH votes are
near-duplicates**". The leave-one-out evidence does not support that rationale
symmetrically: it supports it under the held treatment and contradicts it under
the moved treatment, where SOXL is the single most influential vote in the set.
Session 00C's separate pairwise-agreement measurement — SMH and SOXL agreeing on
0.9143 of sessions at SMA 50, the highest of the six pairs — is independent of any
threshold treatment and is not disturbed by this. The two lines of evidence point
in different directions and are reported, not reconciled.

---

## 4. Artifacts written

| Path | Contents |
|---|---|
| `outputs/session-00e/manifest-truncated.csv` | 39 files: old and new hash, rows, last dates, status |
| `outputs/session-00e/pre-truncation-hashes/` | original 00A and 00C manifests, copied before modification |
| `outputs/session-00e/smh-return-basis.csv` | step 2, 180 rows, long form |
| `outputs/session-00e/vote-leave-one-out.csv` | step 3, 40 rows, both treatments |
| `outputs/session-00e/REPORT.md` | this file |

Modified in place: 35 files under `data/raw/etf/` and `data/interim/etf-panel.parquet`.
Byte-identical, not rewritten: the three Session 00B interim files in section 1.1.
Untouched: all VX files, and every CSV under `outputs/session-00a/` through
`outputs/session-00d/`.

No decision is recommended and no parameter is selected. Working tree left dirty.
Nothing committed.
"""
    (OUT / "REPORT.md").write_text(text)
    print(f"wrote {OUT/'REPORT.md'} ({len(text):,} chars)")


if __name__ == "__main__":
    main()
