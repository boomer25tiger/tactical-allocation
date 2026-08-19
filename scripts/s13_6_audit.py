"""Session 13.6 step 8 — validation-window audit (D11 generalised).

For every construction-validation statistic: recorded value, session,
window, whether the window crosses 2021-07-30, and where it crosses an
in-window recomputation beside the recorded figure. Repairs nothing.

Method positive control: each recomputation is first run over the
recorded (full) window and compared to the recorded value; a match
validates the reimplementation before the in-window figure is read.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt

OUT = ROOT / "outputs" / "session-13.6"
B = pd.Timestamp("2021-07-30")
rows = []


def add(**kw):
    rows.append(kw)


def syn_ret(t):
    f = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")
    f.index = pd.to_datetime(f.index).normalize()
    return f["syn_ret"].astype(float)


def real_ret(t):
    return bt.build_ticker_frame(t, _raw_full(t)).ret_total


def _raw_full(t):
    raw = pd.read_parquet(ROOT / "data" / "raw" / "etf" / f"{t}.parquet")
    idx = pd.to_datetime(raw.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_localize(None)
    raw.index = idx.normalize()
    return raw


def stats_pair(s, r, end=None):
    j = pd.DataFrame({"s": s, "r": r}).dropna()
    if end is not None:
        j = j.loc[:end]
    n = len(j)
    if n < 60:
        return None
    corr = float(j["s"].corr(j["r"]))
    ann_s = float((1 + j["s"]).prod() ** (252 / n) - 1) * 100
    ann_r = float((1 + j["r"]).prod() ** (252 / n) - 1) * 100
    cs = (1 + j["s"]).rolling(252).apply(np.prod, raw=True)
    cr = (1 + j["r"]).rolling(252).apply(np.prod, raw=True)
    mx = float((cs / cr - 1).abs().max())
    return {"n": n, "corr": corr, "ann_td_pct": ann_s - ann_r,
            "max_roll252_div": mx,
            "window": f"{j.index.min().date()}..{j.index.max().date()}"}


print("== per-fund validation set (session 12 final-validation.csv) ==")
fv = pd.read_csv(ROOT / "outputs" / "session-12" / "final-validation.csv")
fv = fv[fv.layer == "primary"]
for _, r0 in fv.iterrows():
    t = r0["fund"]
    try:
        s = syn_ret(t)
        if str(r0.get("target")) == "NAV":
            navf = pd.read_parquet(ROOT / "data" / "raw" / "nav" / f"{t}_nav.parquet")
            rr = navf.set_index(pd.to_datetime(navf["date"]).dt.normalize())["nav"] \
                .astype(float).pct_change()
        else:
            rr = real_ret(t)
    except FileNotFoundError:
        continue
    full = stats_pair(s, rr)
    inw = stats_pair(s, rr, end=B)
    crosses = str(r0["window"]).split("..")[-1] > "2021-07-30"
    if inw is None:
        add(statistic=f"{t} synthetic-vs-real corr / annTD / maxroll",
            session="12", recorded=f"corr {r0['corr']:.4f}; TD {r0['ann_td_pct']:+.2f}%/yr; "
            f"maxroll {r0['max_roll252_div']:.3f}",
            window=r0["window"], crosses_boundary=crosses,
            method_control_full_window="n/a",
            in_window="NO IN-WINDOW OVERLAP: fund lists 2022-03, entirely post-boundary",
            breach_statement="validation exists only outside the boundary")
        print(f"  {t}: no in-window overlap (lists 2022-03)")
        continue
    add(statistic=f"{t} synthetic-vs-real corr / annTD / maxroll",
        session="12", recorded=f"corr {r0['corr']:.4f}; TD {r0['ann_td_pct']:+.2f}%/yr; "
        f"maxroll {r0['max_roll252_div']:.3f}",
        window=r0["window"], crosses_boundary=crosses,
        method_control_full_window=f"corr {full['corr']:.4f}; TD {full['ann_td_pct']:+.2f}; "
        f"maxroll {full['max_roll252_div']:.3f}",
        in_window=f"corr {inw['corr']:.4f}; TD {inw['ann_td_pct']:+.2f}%/yr; "
        f"maxroll {inw['max_roll252_div']:.3f} [{inw['window']}]",
        breach_statement="construction validation, run before any strategy result "
        "existed; 2.10 as registered governs strategy-result computation on price "
        "series — crossing recorded, breach determination is a register call")
    print(f"  {t}: recorded corr {r0['corr']:.4f} TD {r0['ann_td_pct']:+.2f} "
          f"maxroll {r0['max_roll252_div']:.2f} | full-recompute corr {full['corr']:.4f} "
          f"TD {full['ann_td_pct']:+.2f} maxroll {full['max_roll252_div']:.2f} | "
          f"in-window corr {inw['corr']:.4f} TD {inw['ann_td_pct']:+.2f} "
          f"maxroll {inw['max_roll252_div']:.2f}")

print("\n== regime gradient (session 12: D1 1.71% -> D10 9.13%, 5.4x) ==")
EQ = ["TQQQ", "SQQQ", "QLD", "PSQ", "SH", "SPXL", "TECL", "TECS",
      "SOXL", "SOXS", "FAS", "LABU"]
UND = {"TQQQ": "QQQ", "SQQQ": "QQQ", "QLD": "QQQ", "PSQ": "QQQ", "SH": "SPY",
       "SPXL": "SPY", "TECL": "XLK", "TECS": "XLK", "SOXL": "SOXX",
       "SOXS": "SOXX", "FAS": "XLF", "LABU": "XBI"}
und_cache = {u: real_ret(u) for u in set(UND.values())}
recs = []
for t in EQ:
    s = syn_ret(t)
    rr = real_ret(t)
    u = und_cache[UND[t]]
    j = pd.DataFrame({"s": s, "r": rr, "u": u}).dropna()
    j["vol"] = j["u"].rolling(60).std() * math.sqrt(252)
    j["dev"] = j["s"] - j["r"]
    recs.append(j[["vol", "dev"]].dropna())
pool = pd.concat(recs)

def gradient(df):
    dec = pd.qcut(df["vol"], 10, labels=False, duplicates="drop")
    te = df.groupby(dec)["dev"].std() * math.sqrt(252) * 100
    return float(te.iloc[0]), float(te.iloc[-1]), float(te.iloc[-1] / te.iloc[0])

d1f, d10f, ratf = gradient(pool)
d1i, d10i, rati = gradient(pool[pool.index <= B])
add(statistic="equity tracking-error regime gradient D1 -> D10",
    session="12 (method: pooled syn-minus-real daily dev, underlying trailing "
    "60-session vol deciles, sd annualised; this session's reimplementation)",
    recorded="D1 1.71% -> D10 9.13%, ratio 5.4x",
    window="listing..2026-08-14 per fund", crosses_boundary=True,
    method_control_full_window=f"D1 {d1f:.2f}% -> D10 {d10f:.2f}%, ratio {ratf:.1f}x",
    in_window=f"D1 {d1i:.2f}% -> D10 {d10i:.2f}%, ratio {rati:.1f}x (..2021-07-30)",
    breach_statement="as above; the gradient is cited as a limitation on every "
    "crisis-window result and survives in-window recomputation or not as reported")
print(f"  full-window reimplementation: D1 {d1f:.2f} -> D10 {d10f:.2f} ({ratf:.1f}x); "
      f"in-window: D1 {d1i:.2f} -> D10 {d10i:.2f} ({rati:.1f}x)")

print("\n== volatility NAV validations (sessions 11-12) ==")
vn = pd.read_csv(ROOT / "outputs" / "session-12" / "volatility-nav-validation.csv")
for _, r0 in vn[vn.target == "NAV"].iterrows():
    t = r0["fund"]
    navf = pd.read_parquet(ROOT / "data" / "raw" / "nav" / f"{t}_nav.parquet")
    nav = navf.set_index(pd.to_datetime(navf["date"]).dt.normalize())["nav"].astype(float)
    nav = nav[~nav.index.duplicated(keep="last")]
    nr = nav.pct_change()
    s = syn_ret(t)
    j = pd.DataFrame({"s": s, "n": nr}).dropna()
    a, b_ = str(r0["window"]).split("..")
    jw = j.loc[a:b_]
    full_corr = float(jw["s"].corr(jw["n"]))
    inw = jw.loc[:B]
    crosses = b_ > "2021-07-30"
    add(statistic=f"{t} synthetic vs issuer NAV corr ({r0['era']})", session="12",
        recorded=f"corr {r0['corr']:.5f}", window=r0["window"],
        crosses_boundary=crosses,
        method_control_full_window=f"corr {full_corr:.5f}",
        in_window=(f"corr {float(inw['s'].corr(inw['n'])):.5f} "
                   f"[{inw.index.min().date()}..{inw.index.max().date()}]"
                   if crosses and len(inw) > 50 else "window already inside boundary"),
        breach_statement="construction validation pre-result; crossing recorded "
        "where present")
    print(f"  {t} {r0['era']}: recorded {r0['corr']:.5f}, control {full_corr:.5f}, "
          f"in-window {float(inw['s'].corr(inw['n'])):.5f}" if len(inw) > 50 else
          f"  {t} {r0['era']}: inside boundary")

print("\n== VX construction B vs VIXY NAV (2.3/2.22, session 11 stage A) ==")
vx = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30-b.parquet")
vx = vx.set_index(pd.to_datetime(vx["trade_date"]).dt.normalize())
lvl = vx["index_level"].astype(float)
lvl = lvl[~lvl.index.duplicated(keep="last")]
vxr = lvl.pct_change()
vy = pd.read_parquet(ROOT / "data" / "interim" / "vixy-nav-proshares-s00b.parquet")
vy_idx = pd.to_datetime(vy["trade_date"]).dt.normalize()
vyr = pd.Series(pd.to_numeric(vy["etp_ret"], errors="coerce").to_numpy(), index=vy_idx)
vyr = vyr[~vyr.index.duplicated(keep="last")]
j = pd.DataFrame({"b": vxr, "v": vyr}).dropna()
full_corr = float(j["b"].corr(j["v"]))
inw = j.loc[:B]
add(statistic="VX construction B daily return corr vs VIXY", session="00B/11",
    recorded="0.99991 (min yearly 0.99926)",
    window=f"{j.index.min().date()}..{j.index.max().date()}",
    crosses_boundary=j.index.max() > B,
    method_control_full_window=f"corr {full_corr:.5f}",
    in_window=f"corr {float(inw['b'].corr(inw['v'])):.5f} "
              f"[..{inw.index.max().date()}]",
    breach_statement="construction validation pre-result; crossing recorded")
print(f"  recorded 0.99991, control {full_corr:.5f}, in-window "
      f"{float(inw['b'].corr(inw['v'])):.5f}")

print("\n== entries not recomputed, with reasons ==")
sib = pd.read_csv(ROOT / "outputs" / "session-10" / "sibling-validation.csv")
for _, r0 in sib.iterrows():
    add(statistic=f"sibling validation {r0['fund']} ({r0['family']})", session="10",
        recorded=f"corr {r0['corr']:.4f}; TD {r0['ann_td_pct']:+.2f}%/yr",
        window=r0["window"], crosses_boundary=str(r0["window"]).split("..")[-1] > "2021-07-30",
        method_control_full_window="n/a", in_window="window entirely pre-boundary",
        breach_statement="no crossing")
px = pd.read_csv(ROOT / "outputs" / "session-09" / "proxy-accuracy.csv")
for _, r0 in px.iterrows():
    add(statistic=f"proxy accuracy {r0['pair']}", session="09",
        recorded=f"TD {r0['ann_tracking_diff_pct']:+.2f}%/yr; corr "
        f"{r0['return_correlation']:.4f}",
        window=r0["window"],
        crosses_boundary=str(r0["window"]).split("..")[-1] > "2021-07-30",
        method_control_full_window="not recomputed",
        in_window="NOT RECOMPUTED: comparator index series (e.g. ^SP500TR) were "
        "measured at pull time in session 09 and are not frozen in data/; "
        "re-pulling is prohibited (1.1)",
        breach_statement="crossing recorded; construction validation pre-result")
for stat, ses, rec, note in [
    ("Direxion FY2025 expense ratios (2.13)", "11",
     "TECL 0.83 .. LABU 0.92 costs-paid ratios",
     "FY2025 filings are post-boundary DOCUMENTS applied as constants across the "
     "whole sample; no in-window (FY<=2021) harvest exists"),
    ("financing anchor 75/70 bp (2.14)", "09/10",
     "SOFR +28..+99 median ~75; shorts receive bills -62..-77",
     "FY2025/FY2026 filings, as above; the constancy-through-time assumption is "
     "already flagged [A] in the register"),
    ("expense arithmetic expected==measured to the bp", "12", "exact",
     "arithmetic identity of the build, window-independent"),
]:
    add(statistic=stat, session=ses, recorded=rec, window="post-boundary documents",
        crosses_boundary=True, method_control_full_window="n/a", in_window=note,
        breach_statement="post-boundary corporate documents used as construction "
        "constants; whether document-sourced constants fall under 2.10 (registered "
        "as a price-series holdout) is a register question the writeup must state; "
        "no strategy-performance information flows through an expense or financing "
        "constant")

pd.DataFrame(rows).to_csv(OUT / "validation-audit.csv", index=False)
print(f"\n[wrote validation-audit.csv: {len(rows)} rows]")
