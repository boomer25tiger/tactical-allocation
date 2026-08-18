"""Session 12, steps 2-5: semiconductor rebuild comparison, NAV
revalidation, expense refinement accounting, and the full validation suite
on the final construction. Instrument-series comparisons only."""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.data import build_ticker_frame
from scripts.s10_build import UNDERLYING, VOL_FUNDS, ER_PCT

OUT = ROOT / "outputs" / "session-12"
SYN = ROOT / "data" / "interim" / "synthetics"
SIXTEEN = ["TQQQ", "QLD", "SQQQ", "PSQ", "SH", "TECL", "TECS", "SOXL",
           "SOXS", "SPXL", "FAS", "LABU", "UVXY", "SVXY", "SVIX", "UVIX"]
SIBLINGS = ["QID", "SSO", "SDS"]

NAV = {}
for t in ("UVXY", "SVXY"):
    n = pd.read_parquet(ROOT / f"data/raw/nav/{t}_nav.parquet")
    NAV[t] = n.set_index(pd.to_datetime(n["date"]))["nav"].astype(float).pct_change().dropna()


def real_ret(fund: str, target="close") -> pd.Series:
    if target == "nav" and fund in NAV:
        return NAV[fund]
    tf = build_ticker_frame(fund, pd.read_parquet(
        ROOT / f"data/raw/etf/{fund}.parquet"))
    return tf.ret_total.dropna()


def metrics(a, b, start=None, end=None):
    j = pd.concat({"a": a, "b": b}, axis=1, sort=True).dropna()
    if start: j = j.loc[pd.Timestamp(start):]
    if end: j = j.loc[:pd.Timestamp(end)]
    if len(j) < 60: return {}
    d = j["a"] - j["b"]
    lr = np.log1p(j["a"]) - np.log1p(j["b"])
    roll = lr.rolling(252).sum()
    yearly = j.groupby(j.index.year).apply(
        lambda g: g["a"].corr(g["b"]) if len(g) > 60 else np.nan).dropna()
    return dict(n=len(j), window=f"{j.index.min().date()}..{j.index.max().date()}",
                corr=float(j["a"].corr(j["b"])),
                min_yearly_corr=float(yearly.min()) if len(yearly) else np.nan,
                ann_td_pct=float(d.mean() * 252 * 100),
                td_sd_ann_pct=float(d.std(ddof=1) * np.sqrt(252) * 100),
                max_roll252_div=float(np.exp(roll.abs().max()) - 1)
                if roll.notna().any() else np.nan)


def syn_ret(fund):
    return pd.read_parquet(SYN / f"SYN_{fund}.parquet")["syn_ret"]


# ===== STEP 2: semiconductor rebuild =====
print("=== STEP 2: semiconductor rebuild (SOXX underlying) ===")
S10_BEFORE = {"SOXL": dict(corr=0.9823, ann_td_pct=3.75, max_roll252_div=0.897),
              "SOXS": dict(corr=0.9618, ann_td_pct=3.10, max_roll252_div=28.45)}
rows2 = []
for f in ("SOXL", "SOXS"):
    m = metrics(syn_ret(f), real_ret(f))
    mis = metrics(syn_ret(f), real_ret(f), "2021-04-22", "2021-08-24")
    rows2.append(dict(fund=f, basis="AFTER (SOXX)", **m))
    rows2.append(dict(fund=f, basis="BEFORE (SMH, session 10)", **S10_BEFORE[f]))
    rows2.append(dict(fund=f, basis="misalignment window 2021-04-22..08-24",
                      **({k: mis[k] for k in ("n", "corr", "ann_td_pct")} if mis else {})))
    print(f"  {f}: corr {m['corr']:.4f} (was {S10_BEFORE[f]['corr']:.4f})  "
          f"TD {m['ann_td_pct']:+.2f}%/yr (was {S10_BEFORE[f]['ann_td_pct']:+.2f})  "
          f"maxroll {m['max_roll252_div']:.1%} (was {S10_BEFORE[f]['max_roll252_div']:.1%})")
    if mis:
        print(f"    misalignment window: {mis['n']} sessions, corr {mis['corr']:.4f}, "
              f"TD {mis['ann_td_pct']:+.2f}%/yr")
# SOXX vs SMH direct
soxx = build_ticker_frame("SOXX", pd.read_parquet(ROOT / "data/raw/etf/SOXX.parquet")).ret_total
smh = build_ticker_frame("SMH", pd.read_parquet(ROOT / "data/raw/etf/SMH.parquet")).ret_total
mm = metrics(soxx, smh)
rows2.append(dict(fund="SOXX vs SMH", basis="basket mismatch quantified", **mm))
print(f"  SOXX vs SMH: corr {mm['corr']:.4f}  TD {mm['ann_td_pct']:+.2f}%/yr  "
      f"sd {mm['td_sd_ann_pct']:.2f}%  maxroll {mm['max_roll252_div']:.1%}")
pd.DataFrame(rows2).to_csv(OUT / "semiconductor-rebuild.csv", index=False)

# ===== STEP 3: volatility NAV revalidation =====
print("\n=== STEP 3: volatility revalidation ===")
rows3 = []
for f in ("UVXY", "SVXY"):
    for tgt in ("nav", "close"):
        for w0, w1, lab in [(None, "2018-02-27", "pre-2018"),
                            ("2018-02-28", None, "post-2018"),
                            (None, None, "full")]:
            m = metrics(syn_ret(f), real_ret(f, tgt), w0, w1)
            if m:
                rows3.append(dict(fund=f, target=tgt.upper(), era=lab, **m))
    n_pre = [r for r in rows3 if r["fund"] == f and r["target"] == "NAV" and r["era"] == "pre-2018"][0]
    n_post = [r for r in rows3 if r["fund"] == f and r["target"] == "NAV" and r["era"] == "post-2018"][0]
    print(f"  {f} vs NAV: pre-2018 TD {n_pre['ann_td_pct']:+.2f}%/yr corr {n_pre['corr']:.4f}  |  "
          f"post-2018 TD {n_post['ann_td_pct']:+.2f}%/yr corr {n_post['corr']:.4f}")

print("\n  SVXY February 2018 day-by-day, synthetic vs NAV vs exchange close:")
sv_syn = syn_ret("SVXY")
sv_nav = real_ret("SVXY", "nav")
sv_cls = real_ret("SVXY", "close")
for d in ("2018-02-02", "2018-02-05", "2018-02-06", "2018-02-07"):
    dd = pd.Timestamp(d)
    row = dict(fund="SVXY", target="feb2018", era=d,
               syn=float(sv_syn.get(dd, np.nan)), nav=float(sv_nav.get(dd, np.nan)),
               close=float(sv_cls.get(dd, np.nan)))
    rows3.append(row)
    print(f"    {d}: syn {row['syn']:+.2%}  NAV {row['nav']:+.2%}  close {row['close']:+.2%}")

for f in ("SVIX", "UVIX"):
    m = metrics(syn_ret(f), real_ret(f))
    rows3.append(dict(fund=f, target="CLOSE (NAV unobtainable)", era="full", **m))
    print(f"  {f} (Cboe-index build) vs close: corr {m['corr']:.4f} "
          f"TD {m['ann_td_pct']:+.2f}%/yr maxroll {m['max_roll252_div']:.1%}")
rows3.append(dict(fund="constrB vs ^SHORTVOL", target="index-family gap",
                  era="session 11", corr=0.926,
                  ann_td_pct=0.47, td_sd_ann_pct=26.89,
                  max_roll252_div=np.nan))
pd.DataFrame(rows3).to_csv(OUT / "volatility-nav-validation.csv", index=False)

# ===== STEP 4: expense refinement accounting =====
print("\n=== STEP 4: expense refinement (expected vs measured dTD) ===")
S10_TD = {"TECL": -0.23, "TECS": 1.03, "SOXL": 3.75, "SOXS": 3.10,
          "SPXL": -0.11, "FAS": 1.09, "LABU": 1.37}
OLD_ER = 1.00
rows4 = []
for f, er in [("TECL", 0.83), ("TECS", 0.92), ("SPXL", 0.81),
              ("FAS", 0.86), ("LABU", 0.92)]:
    m = metrics(syn_ret(f), real_ret(f))
    expected = OLD_ER - er  # ER enters at 1x: lower ER raises syn TD by delta
    measured = m["ann_td_pct"] - S10_TD[f]
    rows4.append(dict(fund=f, er_status="STATED FY2025", old_er=OLD_ER, new_er=er,
                      expected_dtd_pct=round(expected, 3),
                      measured_dtd_pct=round(measured, 3),
                      new_ann_td_pct=m["ann_td_pct"]))
    print(f"  {f}: expected +{expected:.2f}pp, measured {measured:+.2f}pp "
          f"(new TD {m['ann_td_pct']:+.2f}%/yr)")
for f in ("SOXL", "SOXS"):
    rows4.append(dict(fund=f, er_status="STATED FY2025 (confounded with SOXX adoption)",
                      old_er=OLD_ER, new_er=ER_PCT[f],
                      note="underlying changed simultaneously; dTD not attributable to ER alone"))
for f in ("TQQQ", "QLD", "SQQQ", "PSQ", "SH", "UVXY", "SVXY", "SVIX", "UVIX",
          "QID", "SSO", "SDS"):
    rows4.append(dict(fund=f, er_status="CARRIED (unchanged)", new_er=ER_PCT[f]))
pd.DataFrame(rows4).to_csv(OUT / "expense-refinement.csv", index=False)

# ===== STEP 5: full final validation suite =====
print("\n=== STEP 5: final validation, all nineteen ===")
rows5 = []
for f in SIXTEEN + SIBLINGS:
    tgt = "nav" if f in NAV else "close"
    m = metrics(syn_ret(f), real_ret(f, tgt))
    rows5.append(dict(layer="primary", fund=f, target=tgt.upper(),
                      underlying=UNDERLYING[f], **m))
    print(f"  {f:5s} vs {tgt.upper():5s}: corr {m['corr']:.4f} "
          f"TD {m['ann_td_pct']:+6.2f}%/yr sd {m['td_sd_ann_pct']:6.2f}% "
          f"maxroll {m['max_roll252_div']:8.1%}")
# siblings 2006-2010
for f in ("PSQ", "QID", "SH", "SSO", "SDS"):
    m = metrics(syn_ret(f), real_ret(f), "2006-01-01", "2010-12-31")
    rows5.append(dict(layer="sibling_2006_2010", fund=f, **m))
# multiple invariance (NDX 2010+ window)
for f, am in [("PSQ", 1), ("QLD", 2), ("QID", 2), ("TQQQ", 3), ("SQQQ", 3)]:
    m = metrics(syn_ret(f), real_ret(f), "2010-02-11")
    rows5.append(dict(layer="invariance_ndx_2010", fund=f, abs_multiple=am,
                      td_sd_ann_pct=m["td_sd_ann_pct"]))
# regime deciles after SOXX adoption (equity funds)
dec_rows = {}
for f in [x for x in SIXTEEN + SIBLINGS if x not in VOL_FUNDS]:
    sy = pd.read_parquet(SYN / f"SYN_{f}.parquet")
    j = pd.concat({"s": sy["syn_ret"], "r": real_ret(f), "u": sy["underlying_ret"]},
                  axis=1, sort=True).dropna()
    if len(j) < 500: continue
    d = j["s"] - j["r"]
    rv = j["u"].rolling(21).std() * np.sqrt(252)
    dec = pd.qcut(rv, 10, labels=False, duplicates="drop") + 1
    for k, g in d.groupby(dec):
        dec_rows.setdefault(int(k), []).append(float(g.std(ddof=1) * np.sqrt(252) * 100))
print("\n  regime deciles AFTER SOXX adoption (median equity TD sd):")
grad = {}
for k in sorted(dec_rows):
    grad[k] = float(np.median(dec_rows[k]))
    rows5.append(dict(layer="regime_decile", bucket=k, median_td_sd_ann_pct=grad[k]))
print("  " + "; ".join(f"D{k}: {v:.2f}%" for k, v in grad.items()))
print(f"  gradient D10/D1: {grad[10]/grad[1]:.1f}x (session 10: 5.3x)")
rows5.append(dict(layer="financing_sensitivity", fund="(unchanged)",
                  note="k x delta arithmetic unchanged by rebuild; session 10 figures stand"))
pd.DataFrame(rows5).to_csv(OUT / "final-validation.csv", index=False)
print("\nDONE - four CSVs written")
