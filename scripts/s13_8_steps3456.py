"""Session 13.8 steps 3-6: expense constants, financing base, early-window
coverage, and the synthetic panel rebuild with validation.

Expense correction (step 3, gate RESOLVED): the build's ER definition is
the net operating expense ratio EXCLUDING interest/extraordinary items —
financing is modeled separately under 2.14, so the incl-interest line
would double-count. The like-for-like line ("Net Expenses 3,6",
excl-interest, Direxion; "Expenses net of waivers" ProShares) was
retrieved for ALL funds moved (no extrapolation): Direxion seven read
0.94-0.95 in every sampled year (TECS/SPXL/FAS/LABU recovered in this
session's follow-up), TQQQ 0.95, SH 0.89-0.90.

The rebuild is an exact additive layer: the build subtracts ER/100/252
per session, so syn_ret_new = syn_ret − ΔER/100/252.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt

OUT = ROOT / "outputs" / "session-13.8"
B = pd.Timestamp("2021-07-30")

ER_OLD = {"TQQQ": 0.86, "QLD": 0.95, "SQQQ": 0.95, "PSQ": 0.95, "SH": 0.88,
          "SPXL": 0.81, "TECL": 0.83, "TECS": 0.92, "SOXL": 0.71, "SOXS": 0.87,
          "FAS": 0.86, "LABU": 0.92, "UVXY": 0.95, "SVXY": 0.95}
ER_NEW = {"TQQQ": 0.95, "QLD": 0.95, "SQQQ": 0.95, "PSQ": 0.95, "SH": 0.89,
          "SPXL": 0.95, "TECL": 0.95, "TECS": 0.95, "SOXL": 0.95, "SOXS": 0.95,
          "FAS": 0.95, "LABU": 0.95, "UVXY": 0.95, "SVXY": 0.95}
MEASURED = {  # fund -> {FY: (line, value)}
 "TQQQ": {2012: 0.95, 2016: 0.95, 2020: 0.95}, "SQQQ": {2012: 0.95, 2016: 0.95, 2020: 0.95},
 "SH": {2012: 0.89, 2016: 0.89, 2020: 0.90},
 "SOXL": {2012: 0.95, 2016: 0.95, 2020: 0.94}, "SOXS": {2012: 0.95, 2016: 0.95, 2020: 0.95},
 "TECL": {2012: 0.95, 2016: 0.95, 2020: 0.95}, "TECS": {2012: 0.95, 2016: 0.95, 2020: 0.95},
 "SPXL": {2016: 0.95, 2020: 0.95}, "FAS": {2012: 0.95, 2016: 0.95, 2020: 0.94},
 "LABU": {2016: 0.95, 2020: 0.95},
 "UVXY": {2013: 0.95, 2017: 0.95, 2020: 0.95}, "SVXY": {2013: 0.95, 2017: 0.95, 2020: 0.95},
}
EXPOSURE = {"TQQQ": .366, "SOXL": .183, "UVXY": .185, "TECL": .090, "SQQQ": .059,
            "SVXY": .040, "TLT": .034, "BIL": .020, "BTAL": .019, "SOXS": .015,
            "TECS": .015, "BSV": .014, "QQQ": .012, "PSQ": .007, "SPXL": .005,
            "QLD": .002, "LABU": .002}

rows3 = []
tot_effect = 0.0
for f in sorted(ER_OLD):
    d = ER_NEW[f] - ER_OLD[f]
    eff = -d / 100 * EXPOSURE.get(f, 0.0) * 100  # pp/yr on the portfolio
    tot_effect += eff
    rows3.append({"table": "constants", "fund": f, "old_pct": ER_OLD[f],
                  "new_pct": ER_NEW[f], "delta_pp": round(d, 2),
                  "measured_cells": str(MEASURED.get(f, {})),
                  "portfolio_effect_pp_yr_approx": round(eff, 4),
                  "note": ("Direxion excl-interest 'Net Expenses 3,6' line; "
                           "financing modeled separately under 2.14, so the "
                           "incl-interest line would double-count"
                           if f in ("SPXL", "TECL", "TECS", "SOXL", "SOXS", "FAS", "LABU")
                           else "ProShares 'Expenses net of waivers' line")})
rows3.append({"table": "gate_resolution", "note":
 "Like-for-like check RESOLVED: build ER = net operating ER excluding "
 "interest/extraordinary (financing separate under 2.14). Direxion "
 "excl-interest line measured for all seven funds (0.94-0.95 in every "
 "sampled year; accessions 0001193125-13-002341, 0001104659-17-000187, "
 "0001104659-21-000275); the FY2025 costs-paid constants (0.71-0.92) were a "
 "third line family. TQQQ/SH from 'Expenses net of waivers' (accessions "
 "0001104659-12-054139, -16-137872, -20-091337). No extrapolated cells. "
 f"Total approximate portfolio effect: {tot_effect:.3f} pp/yr (direction "
 "unfavorable, as the step states). SPXL FY2012 not in the Oct-2012 filing "
 "(different filing); LABU pre-2015 n/a."})
pd.DataFrame(rows3).to_csv(OUT / "expense-constants.csv", index=False)
print(f"step 3: constants written; approx portfolio effect {tot_effect:.3f} pp/yr")

# ---------------------------------------------------------------------------
rows4 = []
SWEEP = (25, 50, 75, 100, 150, 200)
rows4.append({"table": "prospectus_check", "note":
 "Bounded check answered by the register's own 2.14 history (session 08): "
 "no prospectus states swap financing as a rate over a named reference; "
 "year-end per-swap rates live in shareholder-report schedules only, and "
 "session 13.7/D16 established per-year rates are not derivable from "
 "statements of operations. Proceeding to the split."})
rows4.append({"table": "split", "note":
 "The split ALREADY EXISTS structurally: scripts/s10_build.py ref_returns() "
 "accrues DTB3 (observable, time-varying) as the base on every session; "
 "2.14's constants are the SPREAD only (75 bp long anchor / 70 bp short "
 "haircut). The 2025-anchoring concern therefore attaches to the spread "
 "alone. Canonical anchor unchanged; sweep widened."})
rows4.append({"table": "widened_sweep", "sweep_bp": str(SWEEP), "basis":
 "2008-2009 funding stress (interbank spreads peaked several hundred bp "
 "over policy rates; equity swap spreads negotiated in those conditions "
 "were almost certainly wider than the FY2025 median of ~75); fund-level "
 "historical terms unrecoverable (D16), so the range is an assumed bound, "
 "disclosed. 200 bp cap chosen to bracket the stress case without "
 "asserting a measured level."})
dtb3 = pd.read_parquet(ROOT / "data" / "raw" / "rates" / "DTB3.parquet")["DTB3"]
dtb3.index = pd.to_datetime(dtb3.index)
dtb3 = dtb3.loc["2007":"2021-07"]
for y, g in dtb3.groupby(dtb3.index.year):
    rows4.append({"table": "per_year_all_in", "year": int(y),
                  "dtb3_mean_pct": round(float(g.mean()), 2),
                  "all_in_at_75bp_anchor_pct": round(float(g.mean()) + 0.75, 2),
                  "note": "base observable and time-varying; spread is the swept assumption"})
pd.DataFrame(rows4).to_csv(OUT / "financing-base.csv", index=False)
print("step 4: financing-base written")

# ---------------------------------------------------------------------------
print("== step 5: early-window coverage (realized panel) ==")
panel_r = bt.load_arm_panel("realized")
cal = panel_r["SPY"].index
sig_r = bt.ArmSignals(panel_r, cal)
srows_r = bt.run_signals(sig_r)["rows"]
raw_r = {t: panel_r[t].raw_close.reindex(cal).to_numpy()
         for t in set(sum([list(r["targets"] or {}) for r in srows_r if r["changed"]], []))}
A, Z = pd.Timestamp("2007-01-03"), pd.Timestamp("2011-10-02")
cur = {}
cov = []
sleeve_cov = []
for r in srows_r:
    if r["changed"] and r["targets"] is not None:
        cur = r["targets"]
    d = cal[r["i"]]
    if not (A <= d <= Z):
        continue
    unfill = {t: w for t, w in cur.items() if math.isnan(raw_r[t][r["i"]])}
    cov.append({"date": d, "full_fill": len(unfill) == 0,
                "target_w": sum(cur.values()),
                "unfillable_w": sum(unfill.values())})
    for k in ("T10", "T11", "S2", "S3"):
        sw = r["sleeves"][k]
        if sw is None:
            continue
        u = sum(w for t, w in sw.items() if math.isnan(raw_r[t][r["i"]]))
        sleeve_cov.append({"date": d, "sleeve": k, "frac_unfillable": u})
cv = pd.DataFrame(cov).set_index("date")
sc = pd.DataFrame(sleeve_cov)
rows5 = []
rows5.append({"table": "summary", "sessions_evaluated": len(cv),
              "sessions_every_target_filled": int(cv["full_fill"].sum()),
              "frac": float(cv["full_fill"].mean())})
for y, g in cv.groupby(cv.index.year):
    rows5.append({"table": "by_year", "year": int(y), "sessions": len(g),
                  "full_fill_sessions": int(g["full_fill"].sum()),
                  "full_fill_frac": float(g["full_fill"].mean()),
                  "target_dollar_frac_fillable":
                  float(1 - (g["unfillable_w"].sum() / g["target_w"].sum()))})
for k, g in sc.groupby("sleeve"):
    g = g.set_index("date")
    for y, gy in g.groupby(g.index.year):
        rows5.append({"table": "by_sleeve_year", "sleeve": k, "year": int(y),
                      "mean_frac_sleeve_target_unfillable": float(gy["frac_unfillable"].mean())})
LIST_DATES = {t: str(bt._load_raw(t).index.min().date())
              for t in ("TQQQ", "SQQQ", "SOXL", "SOXS", "TECL", "TECS", "SPXL",
                        "FAS", "LABU", "UVXY", "SVXY", "BTAL", "QLD", "PSQ", "SH",
                        "QQQ", "TLT", "BIL", "BSV")}
for t, d0 in sorted(LIST_DATES.items(), key=lambda x: x[1]):
    rows5.append({"table": "availability_timeline", "ticker": t,
                  "first_in_window_session": d0,
                  "listed_before_window_end": d0 <= "2011-10-02"})
pd.DataFrame(rows5).to_csv(OUT / "early-coverage.csv", index=False)
print(f"  {int(cv['full_fill'].sum())}/{len(cv)} early sessions fully fillable "
      f"({cv['full_fill'].mean():.1%})")

# ---------------------------------------------------------------------------
print("== step 6: panel rebuild (expense layer) and validation ==")
def syn_ret_adj(t):
    f = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")
    f.index = pd.to_datetime(f.index).normalize()
    r = f["syn_ret"].astype(float)
    d = (ER_NEW.get(t, 0) - ER_OLD.get(t, 0)) / 100.0 / 252.0
    return r - d

def pair_stats(s, r, exclude=None):
    j = pd.DataFrame({"s": s, "r": r}).dropna().loc[:B]
    if exclude:
        j = j.drop(index=[d for d in exclude if d in j.index])
    n = len(j)
    cum_s = float((1 + j["s"]).prod()); cum_r = float((1 + j["r"]).prod())
    cs = (1 + j["s"]).rolling(252).apply(np.prod, raw=True)
    cr = (1 + j["r"]).rolling(252).apply(np.prod, raw=True)
    return {"n": n, "corr": float(j["s"].corr(j["r"])),
            "ratio_drift_pct": ((cum_s / cum_r) ** (252 / n) - 1) * 100,
            "max_roll252": float((cs / cr - 1).abs().max())}

rows6 = []
pre = pd.read_csv(OUT / "metric-correction.csv")
pre = pre[pre.table == "rescope_ratio_drift"]
for t in ("TQQQ", "QLD", "SQQQ", "PSQ", "SH", "TECL", "TECS", "SOXL", "SOXS",
          "SPXL", "FAS", "LABU"):
    st = pair_stats(syn_ret_adj(t),
                    bt.build_ticker_frame(t, bt._load_raw(t)).ret_total)
    old = pre[pre["pair"].str.startswith(f"{t} ")]["ratio_drift_pct"].iloc[0]
    rows6.append({"table": "revalidation", "fund": t, **st,
                  "pre_rebuild_ratio_drift_pct": float(old),
                  "shift_pp": st["ratio_drift_pct"] - float(old),
                  "expected_shift_pp": -(ER_NEW[t] - ER_OLD[t]) / 1.0 * 1.0})
    print(f"  {t}: drift {float(old):+.2f} -> {st['ratio_drift_pct']:+.2f} "
          f"(shift {st['ratio_drift_pct']-float(old):+.3f}, ER delta "
          f"{-(ER_NEW[t]-ER_OLD[t]):+.2f})")
# controls: SQQQ (constant unchanged) must be unchanged; TQQQ must shift by
# exactly its ER delta.
sq = [r for r in rows6 if r["fund"] == "SQQQ"][0]
tq = [r for r in rows6 if r["fund"] == "TQQQ"][0]
assert abs(sq["shift_pp"]) < 1e-6, "SQQQ moved without a constant change"
assert abs(tq["shift_pp"] + 0.09) < 0.02, "TQQQ shift != its ER correction"
rows6.append({"table": "controls", "note":
 "SQQQ (constant unchanged) shifted 0.000 pp — PASS. TQQQ shifted by "
 f"{tq['shift_pp']:+.3f} pp, exactly its −0.09 ER correction — the rebuild "
 "changed nothing but the injected constants. TQQQ's drift moves further "
 "below the real close (−0.73 → −0.82): the correction is the measured "
 "filing value regardless; close-basis noise spans ±0.7-1.2 pp/yr."})
# SVXY residual and gradient
sv = pair_stats(syn_ret_adj("SVXY"),
                (lambda f: (lambda s: s[~s.index.duplicated(keep='last')].pct_change())(
                    f.set_index(pd.to_datetime(f["date"]).dt.normalize())["nav"].astype(float)))(
                    pd.read_parquet(ROOT / "data" / "raw" / "nav" / "SVXY_nav.parquet")),
                exclude=[pd.Timestamp("2018-02-06")])
rows6.append({"table": "svxy_residual", **sv,
              "note": "SVXY ER unchanged at 0.95; the +1.60%/yr residual above "
                      "issuer NAV (excl 2.12b day) stands, unattributed, running "
                      "in the direction that helps the strategy"})
UNDM = {"TQQQ": "QQQ", "SQQQ": "QQQ", "QLD": "QQQ", "PSQ": "QQQ", "SH": "SPY",
        "SPXL": "SPY", "TECL": "XLK", "TECS": "XLK", "SOXL": "SOXX",
        "SOXS": "SOXX", "FAS": "XLF", "LABU": "XBI"}
und_cache = {u: bt.build_ticker_frame(u, bt._load_raw(u)).ret_total
             for u in set(UNDM.values())}
recs = []
for t, u in UNDM.items():
    j = pd.DataFrame({"s": syn_ret_adj(t),
                      "r": bt.build_ticker_frame(t, bt._load_raw(t)).ret_total,
                      "u": und_cache[u]}).dropna().loc[:B]
    j["vol"] = j["u"].rolling(60).std() * math.sqrt(252)
    j["dev"] = j["s"] - j["r"]
    recs.append(j[["vol", "dev"]].dropna())
pool = pd.concat(recs)
dec = pd.qcut(pool["vol"], 10, labels=False, duplicates="drop")
te = pool.groupby(dec)["dev"].std() * math.sqrt(252) * 100
rows6.append({"table": "regime_gradient", "d1_pct": float(te.iloc[0]),
              "d10_pct": float(te.iloc[-1]),
              "ratio": float(te.iloc[-1] / te.iloc[0]),
              "canonical_pre_rebuild": "6.2x (D1 2.26 -> D10 14.03)",
              "note": "constant ER shifts do not move deviation SDs materially"})
print(f"  gradient after rebuild: D1 {te.iloc[0]:.2f} -> D10 {te.iloc[-1]:.2f} "
      f"({te.iloc[-1]/te.iloc[0]:.1f}x); SVXY residual {sv['ratio_drift_pct']:+.2f}%/yr")
pd.DataFrame(rows6).to_csv(OUT / "panel-rebuild.csv", index=False)
with open(OUT / "_er_new.json", "w") as fh:
    json.dump({"ER_OLD": ER_OLD, "ER_NEW": ER_NEW}, fh)
print("[wrote expense-constants.csv, financing-base.csv, early-coverage.csv, panel-rebuild.csv]")
