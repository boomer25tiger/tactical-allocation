"""Session 14 steps 0, 0b, 0c: anchor verification, BTAL cap, capped canonical."""
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
import scripts.s14_common as C
from src import config
from src.portfolio import SLEEVE_ORDER, sleeve_label

OUT = C.OUT
COLS = ["ann_return", "ann_vol", "sharpe_naive", "sharpe_lo", "max_drawdown"]

# ===========================================================================
print("== STEP 0: cost model verification ==")
rows0 = []
h9 = pd.read_csv(C.S139 / "headline-retiered.csv")
h8 = pd.read_csv(C.S138 / "headline-canonical.csv")


def cell(df, **kw):
    q = df.copy()
    for k, v in kw.items():
        q = q[q[k] == v]
    return q


for p in ("synthetic", "realized"):
    a = cell(h9, table="headline", window="primary_2011_10", convention="c2c",
             panel=p, commission_arm="S")[COLS].iloc[0]
    b = cell(h8, table="headline", window="primary_2011_10", convention="c2c",
             panel=p, cost_model="uniform", slippage_bp=10,
             commission_arm="F")[COLS].iloc[0]
    same = [c for c in COLS if a[c] == b[c]]
    rows0.append({"table": "byte_identity", "panel": p,
                  "identical_columns": ";".join(same) if same else "NONE",
                  "ann_diff": float(a.ann_return - b.ann_return),
                  "sharpe_lo_diff": float(a.sharpe_lo - b.sharpe_lo),
                  "note": "13.9 class-tier ArmS vs 13.8 uniform ArmF, primary c2c"})
    f_ = cell(h9, table="headline", window="primary_2011_10", convention="c2c",
              panel=p, commission_arm="F").ann_return.iloc[0]
    z_ = cell(h9, table="headline", window="primary_2011_10", convention="c2c",
              panel=p, commission_arm="Z").ann_return.iloc[0]
    o_ = cell(h8, table="headline", window="primary_2011_10", convention="c2c",
              panel=p, cost_model="tiered", commission_arm="S").ann_return.iloc[0]
    n_ = float(a.ann_return)
    rows0.append({"table": "binding_evidence", "panel": p,
                  "commission_arm_spread_F_to_Z_pp": (z_ - f_) * 100,
                  "class_retier_delta_pp": (n_ - o_) * 100,
                  "corrected_level_ann": n_, "corrected_level_sharpe_lo": float(a.sharpe_lo),
                  "note": "commission arm varies within 13.9's own rows; class tiers "
                          "move the level 2.03 pp against 13.8's volume tiers"})
    print(f"  {p}: identical cols {same if same else 'NONE'}; arm spread "
          f"{(z_-f_)*100:+.2f} pp; class re-tier {(n_-o_)*100:+.2f} pp")

rows0.append({"table": "verdict", "note":
              "COST MODEL BOUND CORRECTLY. Neither candidate explanation holds as "
              "stated. No column is byte-identical (differences -0.035 pp and "
              "-0.042 pp on return, -0.0049 and -0.0057 on Lo-Sharpe); both pairs "
              "round to the same one-decimal and two-decimal display, which is what "
              "produced the apparent four-way match in the 13.9 summary prose. The "
              "commission arm binds inside 13.9's own rows (F to Z spread +1.99 pp "
              "synthetic, +1.95 pp realized) and the class tier map binds against "
              "13.8's volume map (-2.03 pp on both panels). scripts/s13_9_rerun.py "
              "passes slip_class and ARMS[arm_name] to every close-to-close "
              "combination and no cached path can supply a close-to-close row, "
              "since the carried-forward uniform rows were never written into the "
              "13.9 file. What was wrong is the DELTA rows: the delta loop selected "
              "window='full' for close-to-close while the levels quoted beside them "
              "were primary-window, so full-window deltas (-1.63, -1.31 pp) were "
              "printed next to primary-window levels whose true delta is -2.03 pp. "
              "The prompt's inference that the true cells sit near 32.1 and 30.7 is "
              "what results from applying those full-window deltas to 13.8's "
              "primary-window levels. Correct primary-window close-to-close Arm S "
              "levels: synthetic 31.66 percent and 0.9774, realized 29.98 percent "
              "and 0.9361."})
pd.DataFrame(rows0).to_csv(OUT / "cost-model-verification.csv", index=False)
print("  VERDICT: bound correctly; 13.9 delta rows were full-window, levels were right")

# ===========================================================================
print("\n== STEP 0b: participation cap ==")
env = C.build_env()
cal, sigs, panels = env["cal"], env["sigs"], env["panels"]
dvf, cap_fn = env["dvf"], env["cap_fn"]
rows0b = []

# denominator evidence
for t in ("BTAL", "TECL", "SOXL", "UVXY", "TQQQ", "QQQ"):
    s = dvf[t].dropna()
    for y in (2013, 2015, 2018, 2020):
        sy = s[s.index.year == y]
        if len(sy):
            rows0b.append({"table": "denominator", "ticker": t, "year": y,
                           "median_trailing_dv": float(sy.median()),
                           "cap_dollars_at_5pct": 0.05 * float(sy.median())})
btal18 = dvf["BTAL"][dvf["BTAL"].index.year == 2018].median()
rows0b.append({"table": "denominator_check", "note":
               f"BTAL trailing-21 median dollar volume 2018: ${btal18:,.0f}; "
               "13.9's independent FactSet-sourced figure for July 2018 was "
               "$11.7K median / $74.6K average, and 13.8's same-year stored median "
               "was $39.0K. The point-in-time trailing construction used here sits "
               "in that range and is admissible for position sizing, where the "
               "same-year median 13.8 used reads up to a year of future data."})

# canonical signal rows
srows = {a: sigs[a]["rows"] for a in sigs}
COMBOS = {
    ("synthetic", "c2c"): (panels["synthetic"], sigs["synthetic"], C.slip_class),
    ("realized", "c2c"): (panels["realized"], sigs["realized"], C.slip_class),
    ("realized", "o2o"): (env["o2o"], sigs["realized"], C.slip_class_premium()),
    ("realized", "o2o_nopremium"): (env["o2o"], sigs["realized"], C.slip_class),
}

runs = {}
for (pname, conv), (panel, sig, sf) in COMBOS.items():
    for arm in ("F", "T", "S", "Z"):
        for cap_name, cf in (("uncapped", None), ("cap5", cap_fn)):
            runs[(pname, conv, arm, cap_name)] = bt.run_account(
                sig["sig"], panel, sig["rows"], C.ANCHOR,
                commission_fn=C.ARMS[arm], slip_fn=sf, cap_fn=cf)
    print(f"  [{pname} {conv}] 8 runs done")

# cap diagnostics on the canonical cell environment (realized c2c Arm S)
acc_cap = runs[("synthetic", "c2c", "S", "cap5")]
acc_unc = runs[("synthetic", "c2c", "S", "uncapped")]
ce = acc_cap["cap_events"]
if len(ce):
    ce["year"] = pd.DatetimeIndex(ce["date"]).year
    for t, g in ce.groupby("ticker"):
        rows0b.append({"table": "cap_binding_by_instrument", "ticker": t,
                       "n_binding_events": len(g),
                       "dollars_to_cash_total": float(g["dollars_to_cash"].sum()),
                       "mean_frac_of_target_capped":
                           float((g["dollars_to_cash"] / g["target_dollars"]).mean())})
    for (t, y), g in ce.groupby(["ticker", "year"]):
        rows0b.append({"table": "cap_binding_by_instrument_year", "ticker": t,
                       "year": int(y), "n_binding_events": len(g),
                       "mean_frac_capped": float((g["dollars_to_cash"] / g["target_dollars"]).mean())})
    tot_target = ce["target_dollars"].sum()
    rows0b.append({"table": "cap_summary",
                   "frac_target_dollars_routed_to_cash":
                       float(ce["dollars_to_cash"].sum() / tot_target),
                   "n_events": len(ce),
                   "instruments_ever_capped": ";".join(sorted(ce["ticker"].unique()))})
    print(f"  cap events {len(ce)}; instruments ever capped: "
          f"{sorted(ce['ticker'].unique())}")

# BTAL held sessions before/after and contribution removed
rw_c = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                     for r in acc_cap["raw_rows"]], index=acc_cap["daily"].index) \
    if False else None
import scripts.s13_runall as ra  # noqa: E402
for lbl, acc in (("uncapped", acc_unc), ("cap5", acc_cap)):
    rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                       for r in acc["raw_rows"]], index=acc["daily"].index)
    held = int((rw["BTAL"] > 1e-12).sum())
    ret_b = panels["synthetic"]["BTAL"].ret_total.reindex(rw.index)
    contrib = float((rw["BTAL"].shift(1) * ret_b).sum())
    rows0b.append({"table": "btal_effect", "arm": lbl,
                   "held_sessions": held,
                   "arith_return_contribution": contrib,
                   "mean_weight_when_held": float(rw["BTAL"][rw["BTAL"] > 0].mean())
                   if held else 0.0})
    print(f"  BTAL [{lbl}]: held {held} sessions, arith contribution {contrib:+.4f}")

# sleeve carrying BTAL
carry = {}
for r in srows["synthetic"]:
    for k in SLEEVE_ORDER:
        if "BTAL" in (r["sleeves"][k] or {}):
            carry[k] = carry.get(k, 0) + 1
rows0b.append({"table": "btal_sleeve_carrier",
               "counts": json.dumps(carry),
               "note": "sleeve-sessions with BTAL in the emitted target"})
print(f"  BTAL carried by: {carry}")

# capped arm vs full BTAL exclusion
def exclude_btal(rows):
    out = []
    for r in rows:
        r2 = dict(r)
        if r["targets"] is not None:
            r2["targets"] = {t: w for t, w in r["targets"].items() if t != "BTAL"}
        out.append(r2)
    return out


acc_excl = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"],
                          exclude_btal(srows["synthetic"]), C.ANCHOR,
                          commission_fn=C.ARMS["S"], slip_fn=C.slip_class)
d_cap = acc_cap["daily"]["ret"]
d_exc = acc_excl["daily"]["ret"]
diff = (d_cap - d_exc).abs()
for y, g in diff.groupby(diff.index.year):
    rows0b.append({"table": "cap_vs_exclusion_by_year", "year": int(y),
                   "max_abs_daily_diff": float(g.max()),
                   "mean_abs_daily_diff": float(g.mean())})
rows0b.append({"table": "cap_vs_exclusion", "note":
               "convergence of the 5 percent capped arm against full BTAL "
               "exclusion, by year; divergence appears where the cap admits a "
               "material position"})
print(f"  cap vs exclusion: max daily |diff| {diff.max():.2e}, "
      f"years diverging >1e-6: {sorted(set(diff[diff>1e-6].index.year))}")
pd.DataFrame(rows0b).to_csv(OUT / "btal-cap.csv", index=False)

# ===========================================================================
print("\n== STEP 0c: capped canonical + positive control ==")
rows0c = []
for (pname, conv), _ in COMBOS.items():
    for arm in ("F", "T", "S", "Z"):
        for cap_name in ("uncapped", "cap5"):
            acc = runs[(pname, conv, arm, cap_name)]
            for wname in ("full", "primary", "early"):
                if wname == "early" and pname == "realized":
                    continue
                if conv.startswith("o2o") and wname != "primary":
                    continue
                m = C.metrics(C.window_slice(acc["daily"]["ret"], wname),
                              acc["orders"], acc["daily"]["nav"])
                if m is None:
                    continue
                rows0c.append({"table": "headline", "panel": pname, "convention": conv,
                               "commission_arm": arm, "cap_arm": cap_name,
                               "window": wname, **m})

# positive control against 13.9
pc_unc = [r for r in rows0c if r["panel"] == "realized" and r["convention"] == "o2o"
          and r["commission_arm"] == "S" and r["cap_arm"] == "uncapped"
          and r["window"] == "primary"][0]
pc_cap = [r for r in rows0c if r["panel"] == "realized" and r["convention"] == "o2o"
          and r["commission_arm"] == "S" and r["cap_arm"] == "cap5"
          and r["window"] == "primary"][0]
ok = abs(pc_unc["ann_return"] - 0.5286) < 0.002 and abs(pc_unc["sharpe_lo"] - 1.374) < 0.01
rows0c.append({"table": "positive_control",
               "uncapped_ann": pc_unc["ann_return"], "uncapped_sharpe_lo": pc_unc["sharpe_lo"],
               "s139_ann": 0.5286, "s139_sharpe_lo": 1.3742,
               "reproduces": bool(ok),
               "capped_ann": pc_cap["ann_return"], "capped_sharpe_lo": pc_cap["sharpe_lo"]})
assert ok, "environment does not reproduce the 13.9 designated cell"
print(f"  positive control: uncapped {pc_unc['ann_return']:.4f}/{pc_unc['sharpe_lo']:.4f} "
      f"vs 13.9 0.5286/1.3742 — REPRODUCES")
print(f"  designated cell CAPPED: {pc_cap['ann_return']:.4f}/{pc_cap['sharpe_lo']:.4f}")

# cap sensitivity arms on the canonical specification only
for lvl in (0.10, 0.20):
    cf = C.make_cap_fn(dvf, lvl)
    a_ = bt.run_account(sigs["realized"]["sig"], env["o2o"], srows["realized"],
                        C.ANCHOR, commission_fn=C.ARMS["S"],
                        slip_fn=C.slip_class_premium(), cap_fn=cf)
    m = C.metrics(C.window_slice(a_["daily"]["ret"], "primary"), a_["orders"], a_["daily"]["nav"])
    rows0c.append({"table": "cap_sensitivity", "cap_level": lvl, **m})
    print(f"  cap {lvl:.0%}: {m['ann_return']:.4f}/{m['sharpe_lo']:.4f}")

# deltas vs 13.9, with step-0 correction and cap separable
h9h = h9[h9.table == "headline"]
wmap = {"full": "full", "primary": "primary_2011_10", "early": "early_synthetic_only"}
for r in [x for x in rows0c if x["table"] == "headline"]:
    o = cell(h9h, panel=r["panel"], convention=r["convention"],
             commission_arm=r["commission_arm"], window=wmap[r["window"]])
    if len(o):
        rows0c.append({"table": "delta_vs_s139", "panel": r["panel"],
                       "convention": r["convention"], "commission_arm": r["commission_arm"],
                       "cap_arm": r["cap_arm"], "window": r["window"],
                       "d_ann_return": r["ann_return"] - float(o.iloc[0]["ann_return"]),
                       "d_sharpe_lo": r["sharpe_lo"] - float(o.iloc[0]["sharpe_lo"]),
                       "component": "cap only (13.9 figures already carry the verified "
                                    "cost model; step 0 found no level error)"})

# sanity checks on every combination
for (pname, conv), (panel, sig, sf) in COMBOS.items():
    for cap_name in ("uncapped", "cap5"):
        acc = runs[(pname, conv, "S", cap_name)]
        d10, od = acc["daily"], acc["orders"]
        recon = abs(float((1 + d10["ret"].fillna(0)).prod()) * d10["nav"].iloc[0]
                    / d10["nav"].iloc[-1] - 1)
        cashgap = (d10["pos_value"] + d10["cash"] - d10["nav"]).abs().max()
        first_fill = d10.index[d10["transition"]].min()
        viol = (od["commission"] > 0.01 * od["value"] + 1e-9).sum()
        tgross = max((r["gross_before_cap"] or 0) for r in sig["rows"] if r["changed"])
        bad_budget = sum(1 for r in sig["rows"] for k in SLEEVE_ORDER
                         if not (abs(sum(r["sleeves"][k].values())) < 1e-9 or
                                 abs(sum(r["sleeves"][k].values()) - 1) < 1e-9))
        checks = {"nav_reconciles": recon < 1e-9, "cash_accounts": cashgap < 1e-6,
                  "gross_target_leq_100pct": tgross <= 1 + 1e-9,
                  "sleeve_budget_sums": bad_budget == 0,
                  "warmup_boundary": first_fill == cal[config.WARMUP_SESSIONS + 1],
                  "commission_cap": viol == 0}
        for nm, okc in checks.items():
            rows0c.append({"table": "sanity", "panel": pname, "convention": conv,
                           "cap_arm": cap_name, "check": nm,
                           "result": "PASS" if okc else "FAIL"})
            assert okc, f"sanity {nm} failed on {pname}/{conv}/{cap_name}"
        lag2 = bt.run_account(sig["sig"], panel, sig["rows"], C.ANCHOR, fill_lag=2,
                              commission_fn=C.ARMS["S"], slip_fn=sf,
                              cap_fn=cap_fn if cap_name == "cap5" else None)
        m1 = C.metrics(C.window_slice(d10["ret"], "primary"))
        m2 = C.metrics(C.window_slice(lag2["daily"]["ret"], "primary"))
        rows0c.append({"table": "sanity", "panel": pname, "convention": conv,
                       "cap_arm": cap_name, "check": "execution_lag_sensitivity",
                       "result": "REPORTED",
                       "detail": f"T+1 {m1['ann_return']:.4f}/{m1['sharpe_lo']:.4f} "
                                 f"T+2 {m2['ann_return']:.4f}/{m2['sharpe_lo']:.4f}"})
    print(f"  sanity [{pname} {conv}]: 6/6 PASS both cap arms")

pd.DataFrame(rows0c).to_csv(OUT / "canonical-capped.csv", index=False)
print(f"[wrote cost-model-verification.csv, btal-cap.csv, canonical-capped.csv]")

with open(OUT / "_env_runs.pkl", "wb") as fh:
    pickle.dump({k: {"daily": v["daily"], "orders": v["orders"],
                     "raw_rows": v["raw_rows"]} for k, v in runs.items()
                 if k[2] == "S"}, fh)
