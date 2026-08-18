"""Session 00b, step 7. Assemble REPORT.md from the artifacts on disk."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-00b"
INTERIM = ROOT / "data" / "interim"


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
    mat = pd.read_csv(OUT / "maturity-diagnostics.csv")
    val = pd.read_csv(OUT / "validation-extended.csv")
    ts = pd.read_csv(OUT / "timestamp-diagnostics.csv")
    top = pd.read_csv(OUT / "timestamp-top20-sessions.csv")
    term = pd.read_csv(OUT / "term-structure.csv")

    A = pd.read_parquet(INTERIM / "vx-cm30-a.parquet")
    B = pd.read_parquet(INTERIM / "vx-cm30-b.parquet")
    C = pd.read_parquet(INTERIM / "vx-cm30-c.parquet")

    f4, f5 = "0.4f", "0.5f"

    # ---- maturity pivots ----------------------------------------------------
    mp_mean = mat.pivot(index="year", columns="construction",
                        values="realized_dte_mean").reset_index()
    mp_sd = mat.pivot(index="year", columns="construction",
                      values="realized_dte_sd").reset_index()
    mp_out = mat.pivot(index="year", columns="construction",
                       values="frac_outside_25_35").reset_index()
    clip = mat[mat.construction == "A_interpolation"][
        ["year", "clipping_or_pinning_rate"]].rename(
        columns={"clipping_or_pinning_rate": "A_clipping_rate"})
    mp = (mp_mean.merge(mp_sd, on="year", suffixes=("_mean", "_sd"))
                 .merge(mp_out, on="year")
                 .merge(clip, on="year"))
    mp.columns = ["year", "A_mean", "B_mean", "C_mean", "A_sd", "B_sd", "C_sd",
                  "A_out", "B_out", "C_out", "A_clipping_rate"]

    def summ(df, lo=2004, hi=2026):
        d = df[(pd.to_datetime(df["trade_date"]).dt.year >= lo)
               & (pd.to_datetime(df["trade_date"]).dt.year <= hi)]["realized_dte"]
        return dict(mean=d.mean(), sd=d.std(), mn=d.min(), mx=d.max(),
                    out=((d < 25) | (d > 35)).mean(),
                    dev=(d - 30).abs().mean(), n=len(d))

    sA, sB, sC = summ(A), summ(B), summ(C)
    eA, eB, eC = summ(A, 2004, 2005), summ(B, 2004, 2005), summ(C, 2004, 2005)
    lA, lB, lC = summ(A, 2006, 2026), summ(B, 2006, 2026), summ(C, 2006, 2026)

    full = pd.DataFrame([
        {"construction": "A_interpolation", **{k: v for k, v in sA.items()}},
        {"construction": "B_sp_roll", **{k: v for k, v in sB.items()}},
        {"construction": "C_fixed_roll", **{k: v for k, v in sC.items()}},
    ])[["construction", "n", "mean", "sd", "mn", "mx", "out", "dev"]]
    full.columns = ["construction", "sessions", "mean_dte", "sd_dte", "min_dte",
                    "max_dte", "frac_outside_25_35", "mean_abs_dev_from_30"]

    early = pd.DataFrame([
        {"construction": "A_interpolation", "period": "2004-2005", **eA},
        {"construction": "B_sp_roll", "period": "2004-2005", **eB},
        {"construction": "C_fixed_roll", "period": "2004-2005", **eC},
        {"construction": "A_interpolation", "period": "2006-2026", **lA},
        {"construction": "B_sp_roll", "period": "2006-2026", **lB},
        {"construction": "C_fixed_roll", "period": "2006-2026", **lC},
    ])[["period", "construction", "n", "mean", "sd", "out", "dev"]]
    early.columns = ["period", "construction", "sessions", "mean_dte", "sd_dte",
                     "frac_outside_25_35", "mean_abs_dev_from_30"]

    # ---- validation pivots --------------------------------------------------
    def vpiv(bench, field):
        p = val[val.benchmark == bench].pivot(index="year",
                                              columns="construction",
                                              values=field).reset_index()
        return p

    corr_nav = vpiv("VIXY_NAV", "daily_return_correlation")
    corr_vixy = vpiv("VIXY", "daily_return_correlation")
    corr_vxx = vpiv("VXX", "daily_return_correlation")
    div_nav = vpiv("VIXY_NAV", "max_rolling_252_cumulative_divergence")
    div_vixy = vpiv("VIXY", "max_rolling_252_cumulative_divergence")

    fullcorr = {}
    for bench in ("VIXY", "VXX", "VIXY_NAV"):
        sub = val[val.benchmark == bench]
        w = sub.groupby("construction").apply(
            lambda g: np.average(g["daily_return_correlation"],
                                 weights=g["overlap_sessions"]),
            include_groups=False)
        fullcorr[bench] = w
    fc = pd.DataFrame(fullcorr).reset_index()

    # ---- timestamp ----------------------------------------------------------
    dec_all = ts[ts.block == "all"][
        ["decile", "n", "abs_vixy_ret_lo", "abs_vixy_ret_hi", "mean_diff",
         "sd_diff", "mean_abs_diff", "median_abs_diff", "p95_abs_diff",
         "max_abs_diff"]]
    dec_pre = ts[ts.block == "pre_20201026_settle_1615ET"][dec_all.columns]
    dec_post = ts[ts.block == "post_20201026_settle_1600ET"][dec_all.columns]

    topcols = ["trade_date", "regime", "cdr", "vixy_ret", "diff",
               "front_contract", "front_settle_prev", "front_settle_t",
               "second_contract", "second_settle_prev", "second_settle_t"]
    n_pre_top = int((top["regime"] == "pre_1615ET").sum())

    text = f"""# Session 00b report — production construction, VIXY validation, timestamp

Decision addressed: **2.22**, production construction methodology for the
constant-maturity VX series. Gates **2.9**. Written {pd.Timestamp.now('UTC').date()}.
Data pulled 2026-08-17.

No strategy return, Sharpe ratio, allocation, signal or performance statistic is
computed anywhere in this session. Everything below is a construction, a
correlation between data series, or a distribution.

No Session 00A artifact was modified. `data/interim/vx-panel.parquet`,
`data/interim/vx-cm30.parquet` and everything under `outputs/session-00a/` were
opened read-only.

---

## 1. Headline measurements

**Realized maturity closest to 30 days with least variability: construction A,
the interpolation.** Mean {sA['mean']:.2f} days, standard deviation {sA['sd']:.2f},
mean absolute deviation from 30 of {sA['dev']:.2f} days, and {sA['out']:.2%} of
sessions outside the 25-35 band. B and C are further out and more variable on
every one of those measures.

**Highest validation correlation: construction B, the S&P roll — but only the NAV
comparison separates B from C.** Against VIXY **NAV**, B reaches
**{fc.loc[fc['construction'] == 'B_sp_roll', 'VIXY_NAV'].iloc[0]:.5f}** against
C's {fc.loc[fc['construction'] == 'C_fixed_roll', 'VIXY_NAV'].iloc[0]:.5f} and A's
{fc.loc[fc['construction'] == 'A_interpolation', 'VIXY_NAV'].iloc[0]:.5f}.
Against VIXY **market price** B and C are indistinguishable — they differ in the
fourth decimal, and C is marginally ahead. A is last on every benchmark.

These two answers point at different constructions. That is the substantive
result of this session and is not resolved here.

Three further findings, each of which changes a premise carried into this session:

1. **The 2004-2005 problem is not caused by interpolation.** It is worse under B
   and C. See section 3.
2. **The 16:15 versus 16:00 mismatch is real, and it ended on 2020-10-26**, when
   Cboe moved VX daily settlement from 15:15 to 15:00 CT. It cannot explain 2022.
   See section 5.
3. **The 2022 correlation failure against VXX is a VXX-specific market-price
   dislocation**, not a futures-data or construction problem. VIXY, tracking the
   same index over the same days, correlates at 0.998. See section 4.3.

---

## 2. Methodology extract (step 1)

Full extract with quoted text in [`methodology-notes.md`](methodology-notes.md).
Condensed:

| Item | As documented |
|---|---|
| Contracts | 1st and 2nd month. Roll out m = 1st, roll in n = 2nd (Table 1) |
| Roll Period | Starts after the close on the Tuesday prior to the monthly Cboe VIX Futures Settlement Date, runs through the Tuesday prior to the next one |
| Weights | `CRW_m,t = 100*(dr/dt)`, `CRW_n,t = 100*((dt-dr)/dt)` |
| `dt` | Business days in the Roll Period, **including** the starting settlement date, **excluding** the next one. Held constant through new holidays and unscheduled closures |
| `dr` | Business days from **the following business day** to, but excluding, the next settlement date |
| Daily return | `CDR_t = Σ CRW_{{i,t-1}}·DCRP_{{i,t}} / Σ CRW_{{i,t-1}}·DCRP_{{i,t-1}} - 1` |
| Settlement price | Named `DCRP`, "Daily Contract Reference Price". **Not defined anywhere in the document** |
| Index struck at | **4:00 PM New York time** (Oct 2021 edition). Was **4:25 PM EST** in the Oct 2017 edition |
| Settlement-day treatment | On the settlement date `dr = dt-1`, so `CRW_m = (dt-1)/dt`. On the Tuesday before the next settlement date `dr = 0`, `CRW_m = 0` |

The single most important structural point is that both sides of the daily-return
ratio use `CRW_{{i,t-1}}`, *yesterday's* weights. The index return is the return on
a position actually held overnight. The Session 00A interpolation is not: its
daily change mixes the price move with the change in interpolation weights. That
difference is what section 4.2 measures.

### Sources that could not be retrieved

| Source | Result |
|---|---|
| `spglobal.com/spdji/.../methodology-sp-vix-futures-indices.pdf` (March 2026 edition) | **HTTP 403**, WebFetch and `requests`, with and without full browser headers |
| `spglobal.com/spdji/en/methodology/article/sp-vix-futures-indices-methodology/` | **HTTP 403**, same |
| Barclays iPath VXX product page (`ipathetn.barclays`) | DNS failure on `www.`; the redirect target returns a 4 KB JavaScript shell with no data |
| VXX daily NAV / indicative value, any free source | **Not obtained.** See section 4.4 |
| Cboe regulatory circular archive (`cdn.cboe.com/resources/regulation/circulars/`) | HTTP 403 in Session 00A, not re-attempted |

The S&P methodology **was** obtained — the document itself, two editions, from
third-party hosts. That is a primary document from a secondary host, not a
secondary source: the formulas quoted are S&P's own text. What is unverified is
whether the March 2026 edition still reads the same.

---

## 3. Maturity diagnostics (step 3)

Realized maturity is the weight-weighted days to expiry of the two legs,
`w1·d1 + w2·d2`, in calendar days.

### Full sample

{md(full, floats={"mean_dte": "0.2f", "sd_dte": "0.2f", "min_dte": "0.2f",
                   "max_dte": "0.2f", "frac_outside_25_35": f4,
                   "mean_abs_dev_from_30": "0.2f"})}

### Split at the listing-cycle break

{md(early, floats={"mean_dte": "0.2f", "sd_dte": "0.2f",
                    "frac_outside_25_35": f4, "mean_abs_dev_from_30": "0.2f"})}

### By year

`*_out` is the fraction of sessions with realized maturity outside 25-35 days.

{md(mp, floats={"A_mean": "0.2f", "B_mean": "0.2f", "C_mean": "0.2f",
                 "A_sd": "0.2f", "B_sd": "0.2f", "C_sd": "0.2f",
                 "A_out": f4, "B_out": f4, "C_out": f4,
                 "A_clipping_rate": f4})}

### Clipping and pinning

- **A**: clipping applies and is reported above. {A['clipped'].mean():.4f} over the
  full sample, {mat[(mat.construction=='A_interpolation') & (mat.year==2004)]['clipping_or_pinning_rate'].iloc[0]:.4f}
  in 2004 and {mat[(mat.construction=='A_interpolation') & (mat.year==2005)]['clipping_or_pinning_rate'].iloc[0]:.4f}
  in 2005, against roughly 0.09-0.10 from 2006.
- **B and C**: **the concept does not apply.** Weights are `dr/dt` and
  `remaining/cycle` respectively, both ratios of non-negative business-day counts
  with numerator no greater than denominator, so both lie in [0,1] by construction.
  No clipping is possible and none occurred. Observed `w1` ranges
  {B['w1'].min():.3f} to {B['w1'].max():.3f} for B and {C['w1'].min():.3f} to
  {C['w1'].max():.3f} for C.

### Does 2004-2005 remain problematic under B and C?

**Yes, and more so.** Sessions outside the 25-35 band in 2004-2005: A
{eA['out']:.1%}, B {eB['out']:.1%}, C {eC['out']:.1%}. Mean absolute deviation
from 30 days: A {eA['dev']:.2f}, B {eB['dev']:.2f}, C {eC['dev']:.2f}.

The cause is the listing cycle, not the construction. Gaps between consecutive VX
expiries averaged 44.3 days in 2005 against 30.3 days in every year from 2006,
reaching 63 days at the widest. No two-contract construction can hold a 30-day
maturity when the two contracts available straddle a 63-day gap.

The high clipping rate that motivated this session is therefore a **symptom**
rather than the disease, and it is the mechanism by which A degrades *least*
badly: clipping pins the series to the front contract and bounds the maturity
error, where B and C hold whatever the calendar offers and drift to a mean of
{eB['mean']:.1f} and {eC['mean']:.1f} days.

A further consequence, found while implementing B: on **48 sessions in 2004-2006**
the true 2nd-month contract required by S&P Table 1 **had not yet been listed**.
B is not computable on those sessions from listed contracts alone. All 48 were
filled using the interpolation the S&P document specifies for exactly this case,
and each is flagged `price_fill` in `data/interim/vx-cm30-b.parquet`. The last
such session is 2006-08-18.

---

## 4. Extended validation (step 4)

### 4.1 The pulls

| Series | Rows | First | Last | Note |
|---|---|---|---|---|
| VIXY (yfinance, `auto_adjust=False`, `actions=True`, start 2010-01-01) | 3,926 | **2011-01-04** | 2026-08-14 | 6 reverse splits; `ret(Close)` and `ret(Adj Close)` agree to 0.0e+00 |
| VXX (yfinance, same settings, start 2009-01-01) | 2,150 | 2018-01-25 | 2026-08-14 | 3 reverse splits; iPath Series B only, as in Session 00A |
| VIXY NAV (ProShares, issuer) | 3,927 | **2011-01-03** | 2026-08-14 | stated `NAV Change (%)` matches `NAV / Prior NAV - 1` to 5.0e-08 |

VIXY requested from 2010-01-01 returns nothing before **2011-01-04**; the fund
launched in January 2011. As anticipated, VIXY carries no share-class
discontinuity — it extends the validation window from 8 years to **15 years and 7
months**, more than doubling it.

### 4.2 Correlation, session-weighted over the full overlap

{md(fc, floats={"VIXY": "0.6f", "VXX": "0.6f", "VIXY_NAV": "0.6f"})}

### 4.3 Daily return correlation by year

**Against VIXY NAV** — this isolates construction from market-price noise,
because NAV is struck from the same futures settlement prices the constructions use:

{md(corr_nav, floats={"A_interpolation": "0.5f", "B_sp_roll": "0.5f",
                       "C_fixed_roll": "0.5f"})}

B reproduces VIXY NAV at 0.99999 or better in nine of sixteen years and never
below 0.99926. This is the cleanest evidence in the session: **construction B is
a correct implementation of the index VIXY tracks.** A sits near 0.995 — visibly
and consistently below, in every single year.

**Against VIXY market price:**

{md(corr_vixy, floats={"A_interpolation": f4, "B_sp_roll": f4,
                        "C_fixed_roll": f4})}

**Against VXX market price:**

{md(corr_vxx, floats={"A_interpolation": f4, "B_sp_roll": f4,
                       "C_fixed_roll": f4})}

Two features of these tables matter.

**A regime break at 2020-2021.** Against VIXY market price every construction
jumps from roughly 0.93-0.96 to roughly 0.998 and stays there. The break
coincides with the Cboe settlement-time change of 2020-10-26. Section 5 measures
it directly.

**2022 is VXX-specific.** In 2022 the constructions correlate with VIXY at
0.995-0.998 but with VXX at 0.880-0.884. VIXY and VXX track the same S&P index
and both close at 16:00 ET, so no futures-timestamp effect can separate them —
yet **VIXY and VXX correlate with each other at only 0.8847 in 2022**, against
0.996-0.999 in every other year. Monthly correlation between VIXY and VXX in 2022:

| Month | corr(VIXY, VXX) |
|---|---|
| Jan | 0.9995 |
| Feb | 0.9995 |
| Mar | 0.9216 |
| Apr | 0.8426 |
| May | 0.9073 |
| Jun | 0.9342 |
| Jul | 0.8912 |
| **Aug** | **0.3951** |
| Sep | 0.7963 |
| Oct | 0.9985 |
| Nov | 0.9989 |
| Dec | 0.9976 |

The dislocation runs March to September 2022 and is bounded on both sides by
normal months. Barclays **suspended further sales and issuances of VXX on
2022-03-14** for want of shelf capacity, and **resumed on 2022-08-01**; a
suspended ETN cannot be arbitraged to indicative value and trades at an
uncontrolled premium.

- https://www.businesswire.com/news/home/20220314005483/en/Barclays-Suspends-Until-Further-Notice-Further-Sales-and-Issuances-of-Two-Series-of-iPath
- https://www.businesswire.com/news/home/20220725005471/en/Barclays-Resumes-Further-Issuances-and-Sales-of-Certain-iPath%C2%AE-ETNs
- https://www.sec.gov/Archives/edgar/data/312070/000095010322004469/dp169097_424b2-vxxetns.htm

The suspension and resumption dates bracket the measured dislocation. The
Session 00A attribution of the 2022 shortfall to a settlement-timestamp mismatch
is not supported: the mismatch had already been removed in October 2020, and the
2022 effect is absent from VIXY over the identical sessions.

### 4.4 Maximum rolling 252-session cumulative divergence

**Against VIXY NAV:**

{md(div_nav, floats={"A_interpolation": f4, "B_sp_roll": f4,
                      "C_fixed_roll": f4})}

This is the sharpest separation in the session. B stays within 0.0012 to 0.0500
of VIXY NAV over any rolling year. A reaches **2.2495** in 2020 and exceeds 0.35
in every year. A's daily changes are not held-position returns, so its level
drifts away from any tradeable position; the drift is largest when the term
structure is steepest.

**Against VIXY market price:**

{md(div_vixy, floats={"A_interpolation": f4, "B_sp_roll": f4,
                       "C_fixed_roll": f4})}

### 4.5 NAV retrieval

**VIXY NAV: obtained.** ProShares publishes a complete daily NAV history at
`https://accounts.profunds.com/etfdata/ByFund/VIXY-historical_nav.csv`, 3,927
rows from 2011-01-03. Saved to `data/interim/vixy-nav-proshares-s00b.parquet`.
The file's `NAV Change (%)` column was verified split-neutral against
`NAV / Prior NAV - 1` to 5.0e-08 across all rows; a naive `pct_change` of the NAV
column disagrees with it on zero sessions, so the series carries no reverse-split
discontinuity. Correlations against NAV are reported above alongside market price.

**VXX NAV or indicative value: not obtained.** Attempted:
`https://www.ipathetn.barclays/` (DNS failure), `https://ipathetn.barclays/details.app?instrumentId=341408`
(redirects to `ipathetn.cib.barclays`, returns a 4 KB JavaScript shell with no
embedded data), `https://stooq.com/q/d/l/?s=vxx.iv&i=d` (796-byte error page).
No free daily historical indicative-value series for VXX was located. The VXX
comparisons above are therefore market price only, which is precisely the
limitation that section 4.3 exposes.

---

## 5. Timestamp investigation (step 5)

### 5.1 Findings from Cboe sources

**The VX daily settlement time changed.** Primary sources, both retrieved in full:

- Cboe notice **C2020092202**, "Adjustment of Daily Marking and Settlement Price
  Reference Time for Proprietary Index Products":
  https://cdn.cboe.com/resources/release_notes/2020/Adjustment-of-Daily-Settlement-Time-for-Proprietary-Index-Products-Notice.pdf
  > "Effective **October 26, 2020** ... CFE will transition the time in relation to
  > which daily settlement prices are calculated for the following products from
  > **3:15 p.m. to 3:00 p.m. CT** (noon CT on early market close days): Cboe
  > Volatility Index ("VX") futures, Mini Cboe Volatility Index ("VXM") futures."

- CFE rule certification **CFE-2020-028**, filed with the CFTC 2020-09-23:
  https://cdn.cboe.com/resources/regulation/rule_filings/pending/2020/20-028-Daily-Settlement-Determination-Time.pdf
  > "The time in relation to which the daily settlement price of a VX futures
  > contract is currently determined is the close of regular trading hours in VX
  > futures ... Accordingly, the time in relation to which the daily settlement
  > price of a VX futures contract is currently determined is **3:15 p.m.**" (CT)

Corroborated independently by S&P: Appendix I of the October 2021 methodology
lists a "Change in VIX Settlement Times" effective **10/23/2020 after close**,
from a "4:15 PM ET stop time" to a "4:00 PM ET stop time", and renames the index
variant from `(0930-1615 ET)` to `(0930-1600 ET)`. Friday close, Monday live —
the same event.

**So: 16:15 ET from inception through 2020-10-23; 16:00 ET from 2020-10-26.**
From 2020-10-26 the VX settlement reference time and the US equity close coincide.

**Does CFE publish a separate 16:00 ET mark alongside the 16:15 settlement?** No
evidence of one was found. C2020092202 describes a *transition* of the single
daily settlement reference time, not the addition of a second mark. The "Daily
Final Indicative Prices" file described in the same notice covers index
**options**, not VX futures.

**Was there any earlier change, 2004 to 2020?** **Inconclusive.** CFE-2020-028
establishes that the reference time was the close of regular trading hours and
that this was 3:15 p.m. CT in 2020, but it does not say when regular trading
hours were last altered. The Cboe regulatory circular archive returned HTTP 403
in Session 00A and was not re-attempted. It is **not** concluded that the time
was unchanged from 2004 to 2020.

### 5.2 Direct measurement of the mismatch

Construction B against VIXY market price, split at 2020-10-26:

| Regime | Sessions | Correlation | Mean abs daily difference |
|---|---|---|---|
| Pre 2020-10-26, VX settle 16:15 ET | 2,468 | 0.924702 | 0.00892 |
| Post 2020-10-26, VX settle 16:00 ET | 1,457 | **0.997558** | **0.00226** |

Mean absolute daily difference falls by a factor of **3.9** at the documented
change. This is the clearest single measurement in the session, and it dates the
15-minute mismatch precisely rather than treating it as a standing property.

### 5.3 Difference conditional on decile of absolute VIXY return

**All sessions:**

{md(dec_all, floats={"abs_vixy_ret_lo": f4, "abs_vixy_ret_hi": f4,
                      "mean_diff": f5, "sd_diff": f5, "mean_abs_diff": f5,
                      "median_abs_diff": f5, "p95_abs_diff": f5,
                      "max_abs_diff": f5})}

**Pre 2020-10-26 (VX settle 16:15 ET):**

{md(dec_pre, floats={"abs_vixy_ret_lo": f4, "abs_vixy_ret_hi": f4,
                      "mean_diff": f5, "sd_diff": f5, "mean_abs_diff": f5,
                      "median_abs_diff": f5, "p95_abs_diff": f5,
                      "max_abs_diff": f5})}

**Post 2020-10-26 (VX settle 16:00 ET):**

{md(dec_post, floats={"abs_vixy_ret_lo": f4, "abs_vixy_ret_hi": f4,
                       "mean_diff": f5, "sd_diff": f5, "mean_abs_diff": f5,
                       "median_abs_diff": f5, "p95_abs_diff": f5,
                       "max_abs_diff": f5})}

**Is the difference concentrated in large-move days? Partly, but it is not
primarily a large-move phenomenon.**

- The top decile of `|VIXY return|` holds **21.8%** of the total absolute
  difference while holding 10% of the sessions — a concentration factor of about
  2.2, not the 5 or 10 that "concentrated in large moves" would imply.
- The difference is present at **every** decile. In the pre-change regime even the
  smallest-move decile carries a mean absolute difference of 0.0065, 65 basis
  points a day, against 0.0202 in the top decile — a factor of 3 across the whole
  range of market conditions.
- After the change the gradient flattens further: 0.00186 in decile 1 against
  0.00390 in decile 10, a factor of 2.1, and the maximum absolute difference over
  1,457 sessions falls to 0.0269 from 0.6187.
- Mean signed difference is close to zero in every decile in both regimes, so the
  mismatch is dispersion, not bias.

The reading consistent with all of this: the 15-minute gap injected a roughly
proportional error on every session, which naturally scales with the size of the
day's move but is not confined to tail days.

### 5.4 The twenty largest absolute differences

**All twenty fall in the pre-2020-10-26 regime** ({n_pre_top} of 20). The largest
post-change difference anywhere is 0.0269, which would not enter this table.

{md(top[topcols], floats={"cdr": f5, "vixy_ret": f5, "diff": f5,
                           "front_settle_prev": "0.3f", "front_settle_t": "0.3f",
                           "second_settle_prev": "0.3f",
                           "second_settle_t": "0.3f"})}

2018-02-05 is the extreme case: the front contract settled 15.625 then 33.225, a
move of +113% struck at 16:15, against VIXY's +34.2% struck at 16:00. Full file
including weights and days to expiry in `timestamp-top20-sessions.csv`; the same
rows are stacked into `timestamp-diagnostics.csv` under `block = top20_session`.

---

## 6. Term structure (step 6)

Front two contracts, nearest two listed carrying a settlement price, the same
convention used in Session 00A. Slope is `(second - front) / front`.

{md(term, floats={"frac_contango": f4, "frac_backwardation": f4,
                   "frac_flat": f4, "median_abs_slope": f4,
                   "median_signed_slope": f4, "mean_signed_slope": f4,
                   "frac_expiry_sessions": f4, "median_front_dte": "0.1f",
                   "median_second_dte": "0.1f"})}

Full sample: contango on **83.53%** of sessions, backwardation on **16.02%**, flat
on 0.44%, median absolute slope **0.0697**. Excluding the 250 expiry sessions, on
which the front contract has zero days to expiry and carries its final settlement
value, the figures are essentially unchanged: contango 83.60%, backwardation
15.93%, median absolute slope 0.0690.

Most backwardated year: 2008 at 47.83%. Most persistently in contango: 2012,
2021 and 2023, each at 98.80%. No inference is drawn.

---

## 7. Artifacts written

| Path | Contents |
|---|---|
| `outputs/session-00b/methodology-notes.md` | S&P extract with quoted formulas, provenance, Cboe timestamp sources |
| `outputs/session-00b/maturity-diagnostics.csv` | step 3, by construction and year |
| `outputs/session-00b/validation-extended.csv` | step 4, three constructions against VIXY, VXX and VIXY NAV |
| `outputs/session-00b/timestamp-diagnostics.csv` | step 5, decile blocks plus the top-20 sessions |
| `outputs/session-00b/timestamp-top20-sessions.csv` | step 5, the twenty sessions on their own |
| `outputs/session-00b/term-structure.csv` | step 6 |
| `data/interim/vx-cm30-a.parquet` | construction A, {len(A):,} sessions |
| `data/interim/vx-cm30-b.parquet` | construction B, {len(B):,} sessions |
| `data/interim/vx-cm30-c.parquet` | construction C, {len(C):,} sessions |
| `data/interim/vixy-nav-proshares-s00b.parquet` | issuer NAV, 3,927 rows |
| `data/interim/vixy-yfinance-raw-s00b.parquet`, `vxx-yfinance-raw-s00b.parquet` | raw pulls |
| `data/interim/vx-term-structure-s00b.parquet` | per-session term structure |

Session 00A artifacts unmodified. Working tree left dirty. Nothing committed.
No construction selected and no sample start date recommended.
"""
    (OUT / "REPORT.md").write_text(text)
    print(f"wrote {OUT/'REPORT.md'} ({len(text):,} chars)")


if __name__ == "__main__":
    main()
