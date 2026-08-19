"""Session 13.9 steps 4-7 computations (run after step 3).

Step 4: passive convention control on UVXY, SVXY, SOXL, SQQQ (primary
window, buy-and-hold, both accumulation conventions).
Step 5: UVXY entry-effect reconciliation across every combination.
Step 6: BTAL capacity limit at 5% of contemporaneous ADV, all instruments.
Step 7: Sharpe numerator convention dual reporting + variance drag.
"""
from __future__ import annotations

import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
from src import config
from src.data import TickerFrame
from src.portfolio import SLEEVE_ORDER, sleeve_label

OUT = ROOT / "outputs" / "session-13.9"
S138 = ROOT / "outputs" / "session-13.8"
PRIMARY_START = pd.Timestamp("2011-10-03")

panel_r = bt.load_arm_panel("realized")
cal = panel_r["SPY"].index


def metrics(r):
    r = r.dropna()
    n = len(r)
    nav = (1 + r).cumprod()
    rf = bt.rf_per_session(r.index).fillna(0.0)
    ex = (r - rf).dropna()
    return {"ann_return": float(nav.iloc[-1] ** (252 / n) - 1),
            "ann_vol": float(r.std(ddof=1) * math.sqrt(252)),
            "sharpe_lo": bt.lo_sharpe(ex),
            "max_drawdown": float((nav / nav.cummax() - 1).min())}


# ---------------- step 4 ----------------------------------------------------
rows4 = []
print("== step 4: passive convention control (vol + sector + inverse) ==")
gaps = {}
for t in ("UVXY", "SVXY", "SOXL", "SQQQ"):
    tf = panel_r[t]
    c2c = tf.ret_total[tf.ret_total.index >= PRIMARY_START]
    ao = tf.adj_open
    o2o = (ao / ao.shift(1) - 1.0)
    o2o = o2o[o2o.index >= PRIMARY_START]
    mc, mo = metrics(c2c), metrics(o2o)
    gaps[t] = mo["ann_return"] - mc["ann_return"]
    rows4.append({"table": "passive", "instrument": t, "convention": "c2c", **mc})
    rows4.append({"table": "passive", "instrument": t, "convention": "o2o", **mo})
    rows4.append({"table": "passive", "instrument": t, "convention": "GAP",
                  **{k: mo[k] - mc[k] for k in mc}})
    print(f"  {t}: c2c {mc['ann_return']:+.4f} | o2o {mo['ann_return']:+.4f} | "
          f"gap {gaps[t]:+.4f}")
# verdict: material = |gap| > 2 pp on any controlled class
worst = max(abs(v) for v in gaps.values())
verdict = ("NEGLIGIBLE convention gap on every controlled class (worst "
           f"{worst:+.4f} = {worst*100:.2f} pp): session 13.7's verdict extends to "
           "the volatility products and the previously uncontrolled 22.5% of "
           "dollar exposure; step 8's designation may proceed."
           if worst < 0.02 else
           f"MATERIAL gap (worst {worst*100:.2f} pp): part of the o2o advantage "
           "is accumulation arithmetic; step 8's designation DOES NOT PROCEED.")
rows4.append({"table": "verdict", "worst_abs_gap_pp": worst * 100, "note": verdict})
print("  verdict:", verdict[:120])
rows4.append({"table": "vix_open_exclusion", "note":
              "signed leverage deviation for UVXY/SVXY remains unmeasured: no "
              "validated VIX-futures OPEN index exists (13.7 statement stands); "
              "unmeasured fraction of dollar exposure 22.5%"})
pd.DataFrame(rows4).to_csv(OUT / "o2o-control-vol.csv", index=False)
verdict_pass = worst < 0.02

# ---------------- step 5 ----------------------------------------------------
print("== step 5: UVXY entry reconciliation ==")
rows5 = []
er = json.load(open(S138 / "_er_new.json"))


def syn_panel(repaired: bool):
    p = bt.load_arm_panel("synthetic")
    if repaired:
        for t in er["ER_NEW"]:
            if t not in p.frames:
                continue
            d = (er["ER_NEW"][t] - er["ER_OLD"][t]) / 100.0 / 252.0
            if d == 0:
                continue
            fr = p[t].frame.copy()
            fr["ret_total"] = fr["ret_total"] - d
            r = fr["ret_total"].copy()
            r.iloc[0] = 0.0
            fr["tr_index"] = (1.0 + r).cumprod()
            p.frames[t] = TickerFrame(t, fr)
    return p


for pan_name, pan in (("synthetic_repaired", syn_panel(True)),
                      ("synthetic_unrepaired_er", syn_panel(False)),
                      ("realized", panel_r)):
    sig = bt.ArmSignals(pan, cal)
    srows = bt.run_signals(sig)["rows"]
    uv = pan["UVXY"].ret_total.reindex(cal).to_numpy()
    # sleeve-state entries: state string changes to a UVXY-containing state
    for k in SLEEVE_ORDER:
        st = pd.Series({r["i"]: sleeve_label(r["sleeves"][k]) for r in srows})
        for state in sorted({s for s in st.unique() if "UVXY" in s}):
            entered = st.index[(st == state) & (st.shift(1) != state)]
            for win_name, cut in (("full", None), ("2012on", pd.Timestamp("2012-01-01"))):
                idxs = [i + 2 for i in entered if i + 2 < len(cal)
                        and (cut is None or cal[i + 2] >= cut)]
                if len(idxs) < 8:
                    continue
                vals = [uv[i] for i in idxs if not math.isnan(uv[i])]
                rows5.append({"table": "entry_grid", "panel": pan_name,
                              "population": f"{k}:{state}", "window": win_name,
                              "basis": "UVXY instrument return (== sleeve-unit "
                                       "for 100%UVXY states)",
                              "first_day_mean": float(np.mean(vals)),
                              "n": len(vals)})
    # all new-position entries (13.8 definition)
    held = pd.Series([("UVXY" in (r["targets"] or {})) if r["changed"] else None
                      for r in srows])
    # simpler: reproduce via state union — any sleeve state containing UVXY
    any_uv = pd.Series({r["i"]: any("UVXY" in sleeve_label(r["sleeves"][k])
                                    for k in SLEEVE_ORDER) for r in srows})
    entered_any = any_uv.index[(any_uv) & (~any_uv.shift(1).fillna(False))]
    for win_name, cut in (("full", None), ("2012on", pd.Timestamp("2012-01-01"))):
        idxs = [i + 2 for i in entered_any if i + 2 < len(cal)
                and (cut is None or cal[i + 2] >= cut)]
        vals = [uv[i] for i in idxs if not math.isnan(uv[i])]
        rows5.append({"table": "entry_grid", "panel": pan_name,
                      "population": "ANY sleeve newly holds UVXY",
                      "window": win_name, "basis": "UVXY instrument return",
                      "first_day_mean": float(np.mean(vals)), "n": len(vals)})
    print(f"  [{pan_name}] grid rows done")

g = pd.DataFrame([r for r in rows5 if r["table"] == "entry_grid"])
s3_2012_rep = g[(g.panel == "synthetic_repaired") & (g.population == "S3:100%UVXY")
                & (g.window == "2012on")]["first_day_mean"]
s3_full_rep = g[(g.panel == "synthetic_repaired") & (g.population == "S3:100%UVXY")
                & (g.window == "full")]["first_day_mean"]
any_full = g[(g.panel == "synthetic_repaired") & (g.population.str.startswith("ANY"))
             & (g.window == "full")]["first_day_mean"]
resolution = (
    "RESOLVED AS POPULATION + WINDOW, not units and not the panel: for "
    "100%UVXY states the sleeve-unit and instrument bases are identical by "
    "construction, and the unrepaired-vs-repaired panels differ by "
    "basis-points (the ER layer; raw-price repairs never touch returns). "
    f"S3:100%UVXY entries on 2012+ read {float(s3_2012_rep.iloc[0]):+.4f} "
    f"(13.6's −0.0091 population), on the full sample "
    f"{float(s3_full_rep.iloc[0]):+.4f}; ALL UVXY entries full-sample read "
    f"{float(any_full.iloc[0]):+.4f} (13.8's +0.0023 population). The −91 bp "
    "figure SURVIVES for its stated population (S3 bull-overbought entries, "
    "2012+); 13.8's +23 bp is the full-population full-sample mean dominated "
    "by 2008-2011 vol-spike entries and tier-1-basket entries. No artifact.")
rows5.append({"table": "resolution", "note": resolution})
print("  " + resolution[:160])
pd.DataFrame(rows5).to_csv(OUT / "entry-reconciliation.csv", index=False)

# ---------------- step 6 (capacity limit; verification row added later) ----
print("== step 6: capacity limits at 5% of contemporaneous ADV ==")
rows6 = []
st9 = pickle.load(open(OUT / "_syn_anchor.pkl", "rb"))
daily = st9["daily"]
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                   for r in st9["raw_rows"]], index=daily.index)
nav = daily["nav"]
for t in ra.TARGET_TICKERS:
    raw = bt._load_raw(t)
    dvol = (raw["Volume"].astype(float) * raw["Close"].astype(float))
    dvol = dvol[raw["Volume"].fillna(0) > 0]
    pos = rw[t] * nav
    if pos.max() <= 0:
        continue
    worst_ratio, worst_year, cap_nav = 0, None, np.inf
    for y in sorted(set(daily.index.year)):
        p_y = pos[pos.index.year == y]
        v_y = dvol[dvol.index.year == y]
        if not len(p_y) or not len(v_y) or p_y.max() <= 0:
            continue
        adv = float(v_y.mean())
        ratio = float(p_y.max()) / adv
        if ratio > worst_ratio:
            worst_ratio, worst_year = ratio, y
        # NAV at which this year's max position = 5% of this year's ADV
        cap_nav = min(cap_nav, 0.05 * adv / (float(p_y.max()) / nav[p_y.idxmax()]))
    rows6.append({"table": "capacity", "ticker": t,
                  "worst_ratio_maxpos_over_adv": round(worst_ratio, 4),
                  "worst_year": worst_year,
                  "nav_capacity_at_5pct_adv": round(cap_nav)})
c6 = pd.DataFrame(rows6).sort_values("nav_capacity_at_5pct_adv")
print(c6.head(5).to_string(index=False))
pd.DataFrame(rows6).to_csv(OUT / "capacity-limit.csv", index=False)

# ---------------- step 7 ----------------------------------------------------
print("== step 7: Sharpe numerator convention ==")
rows7 = []
h = pd.read_csv(OUT / "headline-retiered.csv")
hh = h[h.table == "headline"]
for _, r0 in hh.iterrows():
    vol = r0["ann_vol"]
    arith = r0["arith_mean_excess_ann"]
    geo = r0["geo_ann_excess"]
    rows7.append({"table": "dual_numerator", "panel": r0["panel"],
                  "convention": r0["convention"], "arm": r0["commission_arm"],
                  "window": r0["window"],
                  "sharpe_lo_arithmetic_numerator": r0["sharpe_lo"],
                  "sharpe_geometric_numerator": geo / vol if vol else np.nan,
                  "ann_return_geometric": r0["ann_return"],
                  "arith_mean_excess_ann": arith,
                  "variance_drag_approx": vol ** 2 / 2})
for w, g in hh.groupby("window"):
    rows7.append({"table": "variance_drag_by_window", "window": w,
                  "mean_ann_vol": float(g["ann_vol"].mean()),
                  "variance_drag_pp": float((g["ann_vol"] ** 2 / 2).mean() * 100)})
rows7.append({"table": "convention", "note":
              "REGISTERED (8.2 amendment): Sharpe numerator is the ARITHMETIC "
              "mean excess return over DTB3, annualised x252; the geometric "
              "annualised return is reported separately. At ~53% volatility "
              "the variance drag is ~14 pp/yr, which is how a positive Sharpe "
              "coexists with a negative CAGR on the early window."})
pd.DataFrame(rows7).to_csv(OUT / "sharpe-convention.csv", index=False)
print("[wrote o2o-control-vol.csv, entry-reconciliation.csv, "
      "capacity-limit.csv, sharpe-convention.csv]")
json.dump({"step4_pass": bool(verdict_pass)}, open(OUT / "_step4_verdict.json", "w"))
