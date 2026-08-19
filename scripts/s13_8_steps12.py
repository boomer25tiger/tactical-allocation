"""Session 13.8 steps 1-2: 2.7a metric correction and the D15 SOXS patch.

Step 1: annualised ratio drift becomes 2.7a's canonical tracking metric
        ((prod(1+syn)/prod(1+real))^(252/n) - 1); the geometric-difference
        values are retained labeled. All 23 re-scoped statistics
        recomputed in-window; mis-specification control reproduced.
Step 2: SOXS split patch (engine-level, frozen file untouched) with the
        full sourced-price re-control across all 33 instruments and the
        return-consistency identity.
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

OUT = ROOT / "outputs" / "session-13.8"
OUT.mkdir(parents=True, exist_ok=True)
B = pd.Timestamp("2021-07-30")


def syn_ret(t):
    f = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")
    f.index = pd.to_datetime(f.index).normalize()
    return f["syn_ret"].astype(float)


def real_close_ret(t):
    return bt.build_ticker_frame(t, bt._load_raw(t)).ret_total


def nav_ret(t):
    f = pd.read_parquet(ROOT / "data" / "raw" / "nav" / f"{t}_nav.parquet")
    s = f.set_index(pd.to_datetime(f["date"]).dt.normalize())["nav"].astype(float)
    s = s[~s.index.duplicated(keep="last")]
    return s.pct_change()


def pair_stats(s, r, exclude=None):
    j = pd.DataFrame({"s": s, "r": r}).dropna().loc[:B]
    if exclude:
        j = j.drop(index=[d for d in exclude if d in j.index])
    n = len(j)
    cum_s = float((1 + j["s"]).prod())
    cum_r = float((1 + j["r"]).prod())
    ann_s = cum_s ** (252 / n) - 1
    ann_r = cum_r ** (252 / n) - 1
    return {"n": n, "corr": float(j["s"].corr(j["r"])),
            "geo_diff_pct": (ann_s - ann_r) * 100,
            "ratio_drift_pct": ((cum_s / cum_r) ** (252 / n) - 1) * 100,
            "real_ann_ret_pct": ann_r * 100}


rows1 = []
print("== STEP 1: ratio drift recompute, in-window ==")
# mis-specification control first (must pass before any verdict is read)
mis = syn_ret("UVXY") - (1.90 - 0.95) / 100.0 / 252.0
b_ = pair_stats(syn_ret("UVXY"), nav_ret("UVXY"))
m_ = pair_stats(mis, nav_ret("UVXY"))
shift = m_["ratio_drift_pct"] - b_["ratio_drift_pct"]
rows1.append({"table": "misspec_control", "shift_pp": shift, "expected": -0.95,
              "result": "PASS" if abs(shift + 0.95) < 0.05 else "FAIL"})
assert abs(shift + 0.95) < 0.05
print(f"  mis-spec control: {shift:+.3f} pp vs -0.95 expected — PASS")

FUNDS = ["TQQQ", "QLD", "SQQQ", "PSQ", "SH", "TECL", "TECS", "SOXL", "SOXS",
         "SPXL", "FAS", "LABU", "QID", "SSO", "SDS"]
audit = pd.read_csv(ROOT / "outputs" / "session-13.6" / "validation-audit.csv")
for t in FUNDS:
    st = pair_stats(syn_ret(t), real_close_ret(t))
    rows1.append({"table": "rescope_ratio_drift", "pair": f"{t} syn vs real close",
                  **st, "delta_new_minus_old_pp": st["ratio_drift_pct"] - st["geo_diff_pct"]})
    print(f"  {t}: geo-diff {st['geo_diff_pct']:+.2f} -> ratio drift "
          f"{st['ratio_drift_pct']:+.2f} %/yr (fund ann {st['real_ann_ret_pct']:+.0f}%)")
for t, r_, lbl, ex in [("UVXY", nav_ret("UVXY"), "UVXY syn vs NAV", None),
                       ("SVXY", nav_ret("SVXY"), "SVXY syn vs NAV excl 2.12b",
                        [pd.Timestamp("2018-02-06")])]:
    st = pair_stats(syn_ret(t), r_, ex)
    rows1.append({"table": "rescope_ratio_drift", "pair": lbl, **st,
                  "delta_new_minus_old_pp": st["ratio_drift_pct"] - st["geo_diff_pct"]})

soxs = [r for r in rows1 if r.get("pair", "").startswith("SOXS")][0]
sector = [r for r in rows1 if r.get("pair", "").split(" ")[0] in
          ("TECL", "TECS", "SOXL", "SPXL", "FAS", "LABU")]
band = [r["ratio_drift_pct"] for r in sector if not r["pair"].startswith("SOXS")]
verdict = (f"SOXS in-window ratio drift {soxs['ratio_drift_pct']:+.2f}%/yr "
           f"(was +0.78 under the compressed geometric-difference metric; fund "
           f"annualised return {soxs['real_ann_ret_pct']:+.0f}%/yr). Sector-fund "
           f"band under the same metric: {min(band):+.2f}..{max(band):+.2f}%/yr. "
           + ("The 13.7 conclusion SURVIVES: SOXS sits inside the sector band."
              if min(band) - 0.5 <= soxs['ratio_drift_pct'] <= max(band) + 0.5
              else "The 13.7 conclusion WEAKENS: SOXS sits outside the sector "
                   "band under the sensitive metric; the in-window exception is "
                   "smaller than the recorded full-window one but not at parity."))
rows1.append({"table": "soxs_verdict", "note": verdict})
print("  " + verdict)
pd.DataFrame(rows1).to_csv(OUT / "metric-correction.csv", index=False)
print(f"[wrote metric-correction.csv: {len(rows1)} rows]")

# ===========================================================================
print("\n== STEP 2: D15 SOXS patch controls ==")
rows2 = []
px = bt._frozen_frame("SOXS").raw_close
d = px.index[px.index <= pd.Timestamp("2017-10-31")][-1]
rec = float(px.loc[d])
gap = rec / 16.25 - 1
rows2.append({"table": "soxs_control", "date": str(d.date()),
              "sec_sourced_nav": 16.25, "reconstructed": round(rec, 4),
              "pct_diff": round(gap * 100, 3),
              "result": "PASS" if abs(gap) <= 0.01 else "FAIL"})
print(f"  SOXS {d.date()}: reconstructed {rec:.2f} vs 16.25 ({gap:+.2%}) "
      f"{'PASS' if abs(gap) <= 0.01 else 'FAIL'}")
assert abs(gap) <= 0.01, "SOXS patch control failed"

# all-33 re-control
AV = {'SPY': 211.14, 'QQQ': 110.05, 'XLK': 43.37, 'SMH': 59.81, 'TLT': 122.71,
      'AGG': 110.17, 'IEF': 106.92, 'BND': 82.34, 'BSV': 80.38, 'BIL': 45.71,
      'BTAL': 19.20, 'IOO': 79.16, 'VTV': 85.765, 'VOX': 88.00, 'VOOG': 104.38,
      'VOOV': 91.17, 'XLP': 48.79, 'XLY': 76.30, 'XLF': 24.60}
SEC = [("TQQQ", "2017-05-31", 106.12), ("SQQQ", "2017-05-31", 30.36),
       ("UVXY", "2017-12-29", 10.21), ("SVXY", "2016-12-30", 90.98),
       ("SOXL", "2017-10-31", 148.00), ("TECL", "2017-10-31", 107.62),
       ("TECS", "2017-10-31", 7.36), ("SPXL", "2017-05-01", 32.44),
       ("FAS", "2017-10-31", 60.31), ("QLD", "2016-05-31", 75.03),
       ("PSQ", "2017-05-31", 39.55), ("SH", "2017-05-31", 33.69),
       ("LABU", "2017-10-31", 76.45)]
worst_u = worst_l = 0.0
for t, srcv in AV.items():
    p_ = bt._frozen_frame(t).raw_close
    d_ = p_.index[p_.index <= pd.Timestamp("2015-05-29")][-1]
    g_ = float(p_.loc[d_]) / srcv - 1
    worst_u = max(worst_u, abs(g_))
for t, ds, srcv in SEC:
    p_ = bt._frozen_frame(t).raw_close
    d_ = p_.index[p_.index <= pd.Timestamp(ds)][-1]
    g_ = float(p_.loc[d_]) / srcv - 1
    worst_l = max(worst_l, abs(g_))
rows2.append({"table": "all33_recontrol", "worst_unlevered_abs_pct": worst_u * 100,
              "worst_levered_abs_pct": worst_l * 100,
              "result": "PASS" if worst_u < 0.0001 and worst_l < 0.0059 * 1.001 else "FAIL"})
print(f"  all-33 re-control: unlevered worst {worst_u:.4%}, levered worst "
      f"{worst_l:.3%} — {'PASS' if worst_u < 0.0001 and worst_l < 0.006 else 'FAIL'}")
assert worst_u < 0.0001 and worst_l < 0.006, "patch moved a fund it should not have"

# return consistency incl patched SOXS
bad = []
for t in list(bt.LEVERED) + list(bt.UNLEVERED):
    fr = bt._frozen_frame(t).frame
    close_adj = bt._load_raw(t)["Close"].astype(float)
    at = fr["close"].dropna()
    if len(at) < 2:
        continue
    ca = close_adj.reindex(at.index)
    ratio_eff = fr["split"].reindex(at.index).fillna(0.0).replace(0.0, 1.0)
    gapmax = ((at / at.shift(1)) * ratio_eff - ca / ca.shift(1)).abs().max()
    if not (gapmax < 1e-9 or math.isnan(gapmax)):
        bad.append((t, float(gapmax)))
rows2.append({"table": "return_consistency", "result": "PASS" if not bad else f"FAIL {bad}"})
assert not bad
print("  return consistency (patched): PASS all funds")
rows2.append({"table": "patch_record", "note":
              "Patch: SOXS 2021-03-02 ratio 1/15, applied at load "
              "(scripts/s13_backtest.py SPLIT_PATCHES); frozen file untouched "
              "(1.1). Source: Direxion corporate action effective 2021-03-02 "
              "(companion to SOXL 15:1 same date, present in the vendor record); "
              "evidenced by the SEC-sourced NAV control (Direxion FY2017 N-CSR, "
              "accession 0001104659-18-000153 family) recovering at exactly "
              "x1/15, and adjusted-close continuity through the date. Effect on "
              "share counts/commission/truncation reported from the step-7 run."})
pd.DataFrame(rows2).to_csv(OUT / "soxs-patch.csv", index=False)
print(f"[wrote soxs-patch.csv: {len(rows2)} rows]")
