"""Session 11, step 4: staged volatility roll diagnosis.

Instrument-series comparisons only; no portfolio, no position. ^SHORTVOL is
read at run time and not frozen.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import yfinance as yf

from src.data import build_ticker_frame
from src.schedule import fund_terms

OUT = ROOT / "outputs" / "session-11"
OUT.mkdir(parents=True, exist_ok=True)

# frozen inputs
b = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30-b.parquet")
rB = (b.set_index(pd.to_datetime(b["trade_date"]))["index_level"]
      .sort_index().pct_change().dropna())
vixy = pd.read_parquet(ROOT / "data" / "interim" / "vixy-nav-proshares-s00b.parquet")
r_vixy = (vixy.set_index(pd.to_datetime(vixy["trade_date"]))["etp_ret"]
          .astype(float).dropna())
dtb3 = pd.read_parquet(ROOT / "data" / "raw" / "rates" / "DTB3.parquet")["DTB3"]
dtb3.index = pd.to_datetime(dtb3.index)
dtb3 = dtb3.ffill()


def ref_returns(idx: pd.DatetimeIndex) -> pd.Series:
    days = idx.to_series().diff().dt.days
    rate = dtb3.reindex(idx, method="ffill") / 100.0
    return (rate.shift(1) * days / 360.0).fillna(0.0)


def real_ret(fund: str) -> pd.Series:
    tf = build_ticker_frame(fund, pd.read_parquet(
        ROOT / "data" / "raw" / "etf" / f"{fund}.parquet"))
    return tf.ret_total.dropna()


def stats(a: pd.Series, bser: pd.Series, label: str, start=None, end=None) -> dict:
    j = pd.concat({"a": a, "b": bser}, axis=1, sort=True).dropna()
    if start:
        j = j.loc[pd.Timestamp(start):]
    if end:
        j = j.loc[:pd.Timestamp(end)]
    d = j["a"] - j["b"]
    lr = np.log1p(j["a"]) - np.log1p(j["b"])
    roll = lr.rolling(252).sum()
    yearly = j.groupby(j.index.year).apply(
        lambda g: g["a"].corr(g["b"]) if len(g) > 60 else np.nan).dropna()
    return dict(stage=label, n=len(j),
                window=f"{j.index.min().date()}..{j.index.max().date()}",
                corr=float(j["a"].corr(j["b"])),
                min_yearly_corr=float(yearly.min()) if len(yearly) else np.nan,
                ann_td_pct=float(d.mean() * 252 * 100),
                td_sd_ann_pct=float(d.std(ddof=1) * np.sqrt(252) * 100),
                max_roll252_div=float(np.exp(roll.abs().max()) - 1)
                if roll.notna().any() else np.nan)


rows = []
print("=== Stage A: VIXY synthetic (construction B + collateral - ER) vs frozen VIXY NAV ===")
ER_VIXY = 0.0085
syn_vixy = rB + ref_returns(rB.index) - ER_VIXY / 252.0
sA = stats(syn_vixy, r_vixy, "A: syn VIXY vs NAV")
rows.append(sA)
jj = pd.concat({"s": syn_vixy, "r": r_vixy}, axis=1, sort=True).dropna()
yearly_corr = jj.groupby(jj.index.year).apply(lambda g: g["s"].corr(g["r"]))
print(f"  full corr {sA['corr']:.5f}  min yearly {sA['min_yearly_corr']:.5f}  "
      f"TD {sA['ann_td_pct']:+.2f}%/yr  sd {sA['td_sd_ann_pct']:.2f}%")
print("  yearly corr:", {int(y): round(c, 5) for y, c in yearly_corr.items()})

# sigma wedge: construction B vs real VIXY daily-return vol
sigB = float(jj["s"].std(ddof=1) * np.sqrt(252))
sigR = float(jj["r"].std(ddof=1) * np.sqrt(252))
print(f"  ann vol: construction-B synthetic {sigB:.1%} vs real VIXY {sigR:.1%} "
      f"(Δσ² = {sigR**2 - sigB**2:+.4f})")
rows.append(dict(stage="A: sigma wedge", corr=np.nan,
                 ann_td_pct=np.nan,
                 note=f"syn ann vol {sigB:.4f}, real {sigR:.4f}, "
                      f"dsigma2 {sigR**2 - sigB**2:+.5f}"))

print("\n=== Stage B: UVXY = M(t) x base ===")
idx = rB.index
M_u = pd.Series([fund_terms("UVXY", d).multiple
                 if d.date() >= pd.Timestamp("2011-10-03").date()
                 else 2.0 for d in idx], index=idx)
syn_uvxy = M_u * rB + ref_returns(idx) - 0.0095 / 252.0
sBst = stats(syn_uvxy, real_ret("UVXY"), "B: syn UVXY vs fund")
rows.append(sBst)
print(f"  corr {sBst['corr']:.4f} minY {sBst['min_yearly_corr']:.4f} "
      f"TD {sBst['ann_td_pct']:+.2f}%/yr maxroll {sBst['max_roll252_div']:.1%}")
# per-era TD to see whether +TD persists across the multiple change
for w0, w1, lab in [("2011-10-04", "2018-02-27", "2x era"),
                    ("2018-02-28", "2026-08-14", "1.5x era")]:
    s = stats(syn_uvxy, real_ret("UVXY"), f"B: UVXY {lab}", w0, w1)
    rows.append(s)
    print(f"    {lab}: TD {s['ann_td_pct']:+.2f}%/yr corr {s['corr']:.4f}")

print("\n=== Stage C: SVXY = M(t) x base ===")
M_s = pd.Series([fund_terms("SVXY", d).multiple
                 if d.date() >= pd.Timestamp("2011-10-03").date()
                 else -1.0 for d in idx], index=idx)
syn_svxy = M_s * rB + ref_returns(idx) - 0.0095 / 252.0
sC = stats(syn_svxy, real_ret("SVXY"), "C: syn SVXY vs fund")
rows.append(sC)
print(f"  corr {sC['corr']:.4f} minY {sC['min_yearly_corr']:.4f} "
      f"TD {sC['ann_td_pct']:+.2f}%/yr maxroll {sC['max_roll252_div']:.1%}")
for w0, w1, lab in [("2011-10-04", "2018-02-27", "-1x era"),
                    ("2018-02-28", "2026-08-14", "-0.5x era"),
                    ("2019-01-01", "2026-08-14", "post-2018 only")]:
    s = stats(syn_svxy, real_ret("SVXY"), f"C: SVXY {lab}", w0, w1)
    rows.append(s)
    print(f"    {lab}: TD {s['ann_td_pct']:+.2f}%/yr corr {s['corr']:.4f}")

print("\n  SVXY February 2018, day by day (real vs synthetic):")
rs = real_ret("SVXY")
for d in ("2018-02-02", "2018-02-05", "2018-02-06", "2018-02-07"):
    dd = pd.Timestamp(d)
    r_r = rs.loc[dd] if dd in rs.index else np.nan
    r_s = syn_svxy.loc[dd] if dd in syn_svxy.index else np.nan
    print(f"    {d}: real {r_r:+.2%}  synthetic {r_s:+.2%}")
    rows.append(dict(stage=f"C: SVXY {d}", ann_td_pct=np.nan,
                     note=f"real {r_r:+.4f} syn {r_s:+.4f}"))

print("\n=== Stage D: SVIX vs ^SHORTVOL (runtime read) and vs fund ===")
sv = yf.Ticker("^SHORTVOL").history(period="max")["Close"]
sv.index = pd.to_datetime(sv.index).tz_localize(None).normalize()
r_sv = sv.pct_change().dropna()
# D1: construction-B negation vs the Cboe index itself
sD1 = stats(-rB, r_sv, "D1: -1 x constrB vs ^SHORTVOL")
rows.append(sD1)
print(f"  -1x constrB vs ^SHORTVOL: corr {sD1['corr']:.4f} "
      f"TD {sD1['ann_td_pct']:+.2f}%/yr sd {sD1['td_sd_ann_pct']:.2f}%")
# D2: session-10-style synthetic vs the real fund
syn_svix_B = -1.0 * rB + ref_returns(rB.index) - 0.0149 / 252.0
sD2 = stats(syn_svix_B, real_ret("SVIX"), "D2: constrB-based syn SVIX vs fund")
rows.append(sD2)
# D3: SHORTVOL-based synthetic vs the real fund
syn_svix_SV = r_sv - 0.0149 / 252.0
sD3 = stats(syn_svix_SV, real_ret("SVIX"), "D3: SHORTVOL-based syn SVIX vs fund")
rows.append(sD3)
print(f"  constrB-based syn vs fund:  TD {sD2['ann_td_pct']:+.2f}%/yr "
      f"corr {sD2['corr']:.4f} maxroll {sD2['max_roll252_div']:.1%}")
print(f"  SHORTVOL-based syn vs fund: TD {sD3['ann_td_pct']:+.2f}%/yr "
      f"corr {sD3['corr']:.4f} maxroll {sD3['max_roll252_div']:.1%}")
sigB2 = float(rB.reindex(r_sv.index).dropna().std(ddof=1) * np.sqrt(252))
sigSV = float(r_sv.std(ddof=1) * np.sqrt(252))
print(f"  ann vol: constrB {sigB2:.1%} vs ^SHORTVOL {sigSV:.1%} on overlap")
rows.append(dict(stage="D: sigma constrB vs SHORTVOL",
                 note=f"{sigB2:.4f} vs {sigSV:.4f}"))

pd.DataFrame(rows).to_csv(OUT / "vol-roll-diagnosis.csv", index=False)
print("\nWROTE outputs/session-11/vol-roll-diagnosis.csv")
