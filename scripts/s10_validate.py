"""Session 10, steps 3-7: validation layers over the synthetics.

Instrument-level comparisons only: correlations, tracking differences,
divergences between two return series. No portfolio, no position, no
performance statistic. Failures are recorded with diagnostics and the run
continues (per the session's failure-handling rule).
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src import config
from src.data import build_ticker_frame
from scripts.s10_build import UNDERLYING, VOL_FUNDS, build, load_underlying

OUT = ROOT / "outputs" / "session-10"
SYN = ROOT / "data" / "interim" / "synthetics"

SIXTEEN = ["TQQQ", "QLD", "SQQQ", "PSQ", "SH", "TECL", "TECS", "SOXL",
           "SOXS", "SPXL", "FAS", "LABU", "UVXY", "SVXY", "SVIX", "UVIX"]
SIBLINGS = ["QID", "SSO", "SDS"]

# session 09 proxy-error context, placed beside each result in the report
PROXY_NOTE = {
    "QQQ": "price-basis wedge +0.76%/yr (2010+); exact TR gated",
    "SPY": "exact (^SP500TR): TD = fee; early-era print noise 25-33bp/day",
    "XLK": "true benchmark unmeasurable; sector-context max div 14.8%",
    "SMH": "vs ^SOX max roll-252 divergence 19.3%; ICE era unmeasurable",
    "XLF": "true benchmarks unmeasurable (all three periods)",
    "XBI": "true benchmark unmeasurable",
    "VXCM30": "construction B validated in 00A/00B",
}


def real_ret(fund: str) -> pd.Series:
    tf = build_ticker_frame(fund, pd.read_parquet(
        ROOT / "data" / "raw" / "etf" / f"{fund}.parquet"))
    return tf.ret_total.dropna()


def metrics(syn: pd.Series, real: pd.Series, start=None, end=None) -> dict:
    j = pd.concat({"s": syn, "r": real}, axis=1, sort=True).dropna()
    if start:
        j = j.loc[pd.Timestamp(start):]
    if end:
        j = j.loc[:pd.Timestamp(end)]
    if len(j) < 60:
        return {}
    d = j["s"] - j["r"]
    lr = np.log1p(j["s"]) - np.log1p(j["r"])
    roll = lr.rolling(252).sum()
    yearly = j.groupby(j.index.year).apply(
        lambda g: g["s"].corr(g["r"]) if len(g) > 60 else np.nan)
    return dict(
        n=len(j), window=f"{j.index.min().date()}..{j.index.max().date()}",
        corr=float(j["s"].corr(j["r"])),
        min_yearly_corr=float(yearly.dropna().min()),
        ann_td_pct=float(d.mean() * 252 * 100),
        td_sd_ann_pct=float(d.std(ddof=1) * np.sqrt(252) * 100),
        max_roll252_div=float(np.exp(roll.abs().max()) - 1)
        if roll.notna().any() else np.nan,
    )


def objective_te(fund: str, real: pd.Series, start=None, end=None) -> float:
    """Real fund's own ann. TE vs M x proxy underlying (stated-objective
    proxy; includes proxy error, disclosed). Windowable so a band applied
    to a sub-window compares like with like."""
    syn = pd.read_parquet(SYN / f"SYN_{fund}.parquet")
    obj = syn["multiple"] * syn["underlying_ret"]
    j = pd.concat({"o": obj, "r": real}, axis=1, sort=True).dropna()
    if start:
        j = j.loc[pd.Timestamp(start):]
    if end:
        j = j.loc[:pd.Timestamp(end)]
    d = j["r"] - j["o"]
    return float(d.std(ddof=1) * np.sqrt(252) * 100)


# =========================================================================
# Step 3: primary validation
# =========================================================================
rows = []
print("=== STEP 3: primary validation (synthetic vs real fund) ===")
for fund in SIXTEEN + SIBLINGS:
    syn = pd.read_parquet(SYN / f"SYN_{fund}.parquet")["syn_ret"]
    real = real_ret(fund)
    m = metrics(syn, real)
    if not m:
        rows.append(dict(fund=fund, status="no overlap"))
        continue
    te_obj = objective_te(fund, real)
    if fund in VOL_FUNDS:
        band = "vol: yearly corr >= 0.995 and max roll252 div <= 0.10"
        passed = (m["min_yearly_corr"] >= 0.995
                  and m["max_roll252_div"] <= 0.10)
    else:
        band = "equity: syn TE <= 1.5 x real fund's objective TE"
        passed = m["td_sd_ann_pct"] <= 1.5 * te_obj
    pre_start = pd.Timestamp("2007-01-01")
    first_real = real.index.min()
    unval = (f"{pre_start.date()}..{first_real.date()}"
             if first_real > pre_start else "none")
    rows.append(dict(fund=fund, underlying=UNDERLYING[fund], **m,
                     real_objective_te_pct=te_obj, band=band,
                     band_pass=passed, unvalidated_preinception=unval,
                     proxy_context=PROXY_NOTE[UNDERLYING[fund]]))
    print(f"  {fund:5s} corr {m['corr']:.4f} minY {m['min_yearly_corr']:.4f} "
          f"TD {m['ann_td_pct']:+6.2f}%/yr sd {m['td_sd_ann_pct']:6.2f}% "
          f"maxroll {m['max_roll252_div']:6.1%} objTE {te_obj:5.2f}% "
          f"{'PASS' if passed else 'FAIL'}")
prim = pd.DataFrame(rows)
prim.to_csv(OUT / "synthetic-validation-primary.csv", index=False)

# =========================================================================
# Step 4: sibling validation, pre-inception window 2006-2010
# =========================================================================
print("\n=== STEP 4: sibling validation 2006..2010 ===")
rows4 = []
for fund in ["PSQ", "SH", "QID", "SSO", "SDS"]:
    syn = pd.read_parquet(SYN / f"SYN_{fund}.parquet")["syn_ret"]
    m = metrics(syn, real_ret(fund), start="2006-01-01", end="2010-12-31")
    if not m:
        rows4.append(dict(fund=fund, status="no overlap"))
        continue
    te_obj = objective_te(fund, real_ret(fund),
                          start="2006-01-01", end="2010-12-31")
    passed = m["td_sd_ann_pct"] <= 1.5 * te_obj
    fam = "Nasdaq-100" if UNDERLYING[fund] == "QQQ" else "S&P 500"
    rows4.append(dict(fund=fund, family=fam, **m,
                      real_objective_te_same_window_pct=te_obj,
                      band_pass=passed))
    print(f"  {fund:4s} [{fam:10s}] corr {m['corr']:.4f} "
          f"TD {m['ann_td_pct']:+6.2f}%/yr sd {m['td_sd_ann_pct']:5.2f}% "
          f"maxroll {m['max_roll252_div']:6.1%} "
          f"{'PASS' if passed else 'FAIL'}")
sib = pd.DataFrame(rows4)
sib.to_csv(OUT / "sibling-validation.csv", index=False)
print("  families gaining pre-inception mechanism validation: Nasdaq-100 "
      "(PSQ -1x, QID -2x incl. 2008), S&P 500 (SH -1x, SSO +2x, SDS -2x "
      "incl. 2008). Sector families gain none (disclosed limitation).")

# =========================================================================
# Step 5: multiple invariance
# =========================================================================
print("\n=== STEP 5: multiple invariance ===")
rows5 = []
FAMS = {
    "Nasdaq-100": [("QLD", "2006-07-13"), ("PSQ", "2006-07-13"),
                   ("QID", "2006-07-13"), ("TQQQ", "2010-02-11"),
                   ("SQQQ", "2010-02-11")],
    "S&P 500": [("SH", "2006-07-13"), ("SSO", "2006-07-13"),
                ("SDS", "2006-07-13"), ("SPXL", "2008-11-05")],
}
for fam, members in FAMS.items():
    for wname, wstart in [("from 2006-07-13", "2006-07-13"),
                          ("all-members window", max(w for _, w in members))]:
        for fund, inc in members:
            if pd.Timestamp(inc) > pd.Timestamp(wstart):
                continue
            syn = pd.read_parquet(SYN / f"SYN_{fund}.parquet")["syn_ret"]
            m = metrics(syn, real_ret(fund), start=wstart)
            if not m:
                continue
            M = (config and None) or None
            mult = pd.read_parquet(SYN / f"SYN_{fund}.parquet")["multiple"].iloc[-1]
            rows5.append(dict(family=fam, window=wname, window_start=wstart,
                              fund=fund, abs_multiple=abs(float(mult)),
                              td_sd_ann_pct=m["td_sd_ann_pct"],
                              corr=m["corr"], n=m["n"]))
inv = pd.DataFrame(rows5).drop_duplicates(
    subset=["family", "window_start", "fund"])
inv.to_csv(OUT / "multiple-invariance.csv", index=False)
for (fam, w), g in inv.groupby(["family", "window_start"]):
    g = g.sort_values("abs_multiple")
    print(f"  {fam} from {w}: " + "; ".join(
        f"{r.fund}(|M|={r.abs_multiple:.0f}) sd={r.td_sd_ann_pct:.2f}%"
        for r in g.itertuples()))

# =========================================================================
# Step 6: regime-conditional error
# =========================================================================
print("\n=== STEP 6: regime-conditional error ===")
dtb3 = pd.read_parquet(ROOT / "data" / "raw" / "rates" / "DTB3.parquet")["DTB3"]
dtb3.index = pd.to_datetime(dtb3.index)
dtb3 = dtb3.ffill()
rows6 = []
for fund in SIXTEEN + SIBLINGS:
    syn = pd.read_parquet(SYN / f"SYN_{fund}.parquet")
    real = real_ret(fund)
    j = pd.concat({"s": syn["syn_ret"], "r": real,
                   "u": syn["underlying_ret"]}, axis=1, sort=True).dropna()
    if len(j) < 500:
        continue
    d = j["s"] - j["r"]
    rv = j["u"].rolling(21).std() * np.sqrt(252)
    dec = pd.qcut(rv, 10, labels=False, duplicates="drop") + 1
    rate = dtb3.reindex(j.index, method="ffill")
    rbucket = pd.cut(rate, [-1, 1, 3, 100], labels=["<1%", "1-3%", ">3%"])
    for label, key in [("vol_decile", dec), ("rate_bucket", rbucket)]:
        for k, g in d.groupby(key, observed=True):
            if len(g) < 40:
                continue
            rows6.append(dict(fund=fund, conditioning=label, bucket=str(k),
                              n=len(g),
                              td_sd_ann_pct=float(g.std(ddof=1) * np.sqrt(252) * 100),
                              mean_abs_td_bp=float(g.abs().mean() * 1e4)))
reg = pd.DataFrame(rows6)
reg.to_csv(OUT / "regime-conditional-error.csv", index=False)
eq = reg[(reg.conditioning == "vol_decile")
         & ~reg.fund.isin(VOL_FUNDS)]
if len(eq):
    piv = eq.pivot_table(index="bucket", values="td_sd_ann_pct",
                         aggfunc="median")
    piv.index = piv.index.map(lambda x: int(float(x)))
    print("  equity funds, median TD sd by underlying-vol decile:")
    print("  " + "; ".join(f"D{i}: {v:.2f}%" for i, v in
                           piv.sort_index()["td_sd_ann_pct"].items()))
rt = reg[(reg.conditioning == "rate_bucket") & ~reg.fund.isin(VOL_FUNDS)]
if len(rt):
    piv = rt.pivot_table(index="bucket", values="td_sd_ann_pct", aggfunc="median")
    print("  by DTB3 bucket: " + "; ".join(
        f"{i}: {v:.2f}%" for i, v in piv["td_sd_ann_pct"].items()))

# =========================================================================
# Step 7: financing sensitivity
# =========================================================================
print("\n=== STEP 7: financing sensitivity ===")
rows7 = []
for dbp in (25, 50, 100):
    for M, k in [(1, 0), (2, 1), (3, 2)]:
        rows7.append(dict(kind="analytic", side="long", multiple=M,
                          delta_bp=dbp, ann_td_bp=k * dbp))
    for M, k in [(-1, 1), (-2, 2), (-3, 3)]:
        rows7.append(dict(kind="analytic", side="short", multiple=M,
                          delta_bp=dbp, ann_td_bp=k * dbp))
# empirical: rebuild representative synthetics at perturbed spreads
for fund, side, kw in [("QLD", "long", "spread_long_bp"),
                       ("TQQQ", "long", "spread_long_bp"),
                       ("PSQ", "short", "haircut_bp"),
                       ("SQQQ", "short", "haircut_bp")]:
    base = pd.read_parquet(SYN / f"SYN_{fund}.parquet")["syn_ret"]
    anchor = (config.FINANCING_SPREAD_BP if side == "long"
              else config.FINANCING_SHORT_HAIRCUT_BP)
    for dbp in (25, 50, 100):
        pert = build(fund, **{kw: anchor + dbp})["syn_ret"]
        d = (base - pert).dropna()
        rows7.append(dict(kind="empirical", side=side, fund=fund,
                          multiple=float(pd.read_parquet(
                              SYN / f"SYN_{fund}.parquet")["multiple"].iloc[-1]),
                          delta_bp=dbp,
                          ann_td_bp=float(d.mean() * 252 * 1e4)))
        print(f"  {fund:4s} {side:5s} +{dbp:3d}bp -> ann TD "
              f"{d.mean() * 252 * 1e4:6.1f}bp")
fin = pd.DataFrame(rows7)
fin.to_csv(OUT / "financing-sensitivity.csv", index=False)
print("\nDONE - five validation CSVs written")
