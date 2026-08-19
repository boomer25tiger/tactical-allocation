"""Session 13.8 step 7 — the canonical result under the repaired register.

Panels carry equal weight (2.8 hierarchy removed, post-hoc 9.10; neither
described as primary). Combos: {synthetic c2c, realized c2c, realized
o2o} x {uniform 6pts x Arm F + tiered@anchor x Arms F/T/S/Z}, extension
points for crossings, windows full / primary (2011-10-03+) / early
(synthetic only). SOXS split patch active in the raw path; synthetic
panel carries the step-3 expense layer.
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

OUT = ROOT / "outputs" / "session-13.8"
ANCHOR = 10
EXT = (60, 75, 100, 150)
PRIMARY_START = pd.Timestamp("2011-10-03")
EARLY_END = pd.Timestamp("2011-10-02")
SPLICE = pd.Timestamp(config.COMMISSION_SPLICE_DATE)

er = json.load(open(OUT / "_er_new.json"))
ER_OLD, ER_NEW = er["ER_OLD"], er["ER_NEW"]

# commission arms (13.7 definitions, constants from config)
SEC_FEE = 27.80 / 1e6
TAF = 0.000166
TAF_CAP = 8.30
PASSTHRU = 0.0012  # clearing 0.0002 + exchange 0.0010 per share

def arm_F(date, t, side, sh, v):
    return min(max(config.COMMISSION_F_MINIMUM, config.COMMISSION_F_PER_SHARE * sh),
               config.COMMISSION_F_CAP_FRAC * v)

def arm_T(date, t, side, sh, v):
    c = min(max(config.COMMISSION_T_MINIMUM, config.COMMISSION_T_PER_SHARE * sh),
            config.COMMISSION_T_CAP_FRAC * v) + PASSTHRU * sh
    if side == "sell":
        c += SEC_FEE * v + min(TAF * sh, TAF_CAP)
    return c

def arm_S(date, t, side, sh, v):
    return arm_F(date, t, side, sh, v) if date < SPLICE else 0.0

def arm_Z(date, t, side, sh, v):
    return 0.0

ARMS = {"F": arm_F, "T": arm_T, "S": arm_S, "Z": arm_Z}

# tiered slippage from measured median dollar volume (sample-wide, 13.7)
dv = json.load(open(ROOT / "outputs" / "session-13.7" / "_dollar_volume.json"))
order = sorted(dv, key=lambda t: dv[t]["median_dollar_volume"], reverse=True)
n = len(order)
TIER = {t: (1 if i < n // 3 else 2 if i < 2 * n // 3 else 3)
        for i, t in enumerate(order)}
TIER_MULT = {1: 0.2, 2: 0.5, 3: 1.5}

def tiered_slip(date, t):
    return ANCHOR * TIER_MULT[TIER.get(t, 3)]

MULT_ABS = {"UVXY": 2, "SVXY": 1, "TECL": 3, "TECS": 3, "SOXL": 3, "SOXS": 3,
            "SPXL": 3, "LABU": 3, "SQQQ": 3, "TQQQ": 3, "QLD": 2, "PSQ": 1,
            "QQQ": 1, "TLT": 1, "BIL": 1, "BTAL": 0, "BSV": 1}


def adjusted_syn_panel() -> bt.Panel:
    p = bt.load_arm_panel("synthetic")
    for t in ER_NEW:
        if t not in p.frames:
            continue
        d = (ER_NEW[t] - ER_OLD[t]) / 100.0 / 252.0
        if d == 0:
            continue
        fr = p[t].frame.copy()
        fr["ret_total"] = fr["ret_total"] - d
        r = fr["ret_total"].copy()
        if len(r):
            r.iloc[0] = 0.0
        fr["tr_index"] = (1.0 + r).cumprod()
        fr["adj_close"] = fr["tr_index"]
        p.frames[t] = TickerFrame(t, fr)
    return p


def o2o_panel_from(p: bt.Panel) -> bt.Panel:
    frames = {}
    for t, tf in p.frames.items():
        fr = tf.frame.copy()
        ao = fr["adj_open"]
        fr["ret_total"] = ao / ao.shift(1) - 1.0
        fr["close"] = fr["open"]
        frames[t] = TickerFrame(t, fr)
    out = bt.Panel()
    out.frames = frames
    out._lagged = {config.TREND_SIGNAL_SERIES}
    return out


def win_metrics(daily, orders, start=None, end=None):
    r = daily["ret"]
    if start is not None:
        r = r[r.index >= start]
    if end is not None:
        r = r[r.index <= end]
    r = r.dropna()
    if len(r) < 60:
        return None
    n = len(r)
    nav = (1 + r).cumprod()
    rf = bt.rf_per_session(r.index).fillna(0.0)
    ex = (r - rf).dropna()
    od = orders[(orders["date"] >= (start or orders["date"].min())) &
                (orders["date"] <= (end or orders["date"].max()))] if len(orders) else orders
    navd = daily["nav"].reindex(r.index)
    return {"total_return": float(nav.iloc[-1] - 1),
            "ann_return": float(nav.iloc[-1] ** (252 / n) - 1),
            "ann_vol": float(r.std(ddof=1) * math.sqrt(252)),
            "sharpe_naive": float(ex.mean() / ex.std(ddof=1) * math.sqrt(252)),
            "sharpe_lo": bt.lo_sharpe(ex),
            "max_drawdown": float((nav / nav.cummax() - 1).min()),
            "calmar": float((nav.iloc[-1] ** (252 / n) - 1) /
                            abs((nav / nav.cummax() - 1).min())),
            "ann_turnover": float(od["value"].sum() / 2 / navd.mean() / (n / 252))
            if len(od) else 0.0}


def main():
    rows = []
    print("== panels ==")
    panels = {"synthetic": adjusted_syn_panel(), "realized": bt.load_arm_panel("realized")}
    for a, p in panels.items():
        ok, mx = bt.assert_holdout(p)
        print(f"holdout [{a}]: PASS max {mx.date()}")
    cal = panels["synthetic"]["SPY"].index
    sigs = {a: {"sig": bt.ArmSignals(panels[a], cal)} for a in panels}
    for a in sigs:
        sigs[a].update(bt.run_signals(sigs[a]["sig"]))
    o2o = o2o_panel_from(panels["realized"])

    COMBOS = [("synthetic", "c2c", panels["synthetic"], sigs["synthetic"]),
              ("realized", "c2c", panels["realized"], sigs["realized"]),
              ("realized", "o2o", o2o, sigs["realized"])]
    rows.append({"table": "tier_assignment", "note": "; ".join(
        f"{t}:T{TIER[t]}(mdv ${dv[t]['median_dollar_volume']/1e6:.1f}M,|M|={MULT_ABS.get(t)})"
        for t in order)})
    print("tiers:", {t: TIER[t] for t in order})

    accs = {}
    for pname, conv, panel, sig in COMBOS:
        key0 = (pname, conv)
        accs[key0] = {}
        cost_list = ([("uniform", "F", bp) for bp in
                      list(config.SLIPPAGE_BASE_GRID_BP) + list(EXT)] +
                     [("tiered", a_, ANCHOR) for a_ in ("F", "T", "S", "Z")])
        for model, arm_name, bp in cost_list:
            acc = bt.run_account(sig["sig"], panel, sig["rows"], bp,
                                 commission_fn=ARMS[arm_name],
                                 slip_fn=tiered_slip if model == "tiered" else None)
            accs[key0][(model, arm_name, bp)] = acc
            for wname, ws, we in (("full", None, None),
                                  ("primary_2011_10", PRIMARY_START, None),
                                  ("early_synthetic_only", None, EARLY_END)):
                if wname == "early_synthetic_only" and pname == "realized":
                    continue
                if conv == "o2o" and wname != "primary_2011_10":
                    continue  # 4.1a: o2o reports in the primary window
                m = win_metrics(acc["daily"], acc["orders"], ws, we)
                if m is None:
                    continue
                rows.append({"table": "headline", "panel": pname, "convention": conv,
                             "cost_model": model, "commission_arm": arm_name,
                             "slippage_bp": bp, "window": wname,
                             "in_registered_grid": model == "tiered" or
                             bp in config.SLIPPAGE_BASE_GRID_BP, **m})
        print(f"  [{pname} {conv}] {len(cost_list)} runs done")
    rows.append({"table": "structural_empty", "panel": "synthetic",
                 "convention": "o2o", "note":
                 "structurally empty: the synthetic reconstruction is "
                 "close-to-close by construction; an open-to-open synthetic "
                 "requires an intraday leverage model with no validation "
                 "target (4.1's recorded objection)"})

    # crossings (uniform x F), per combo, full window (and primary for o2o)
    def crossing(pts, col):
        d = pd.DataFrame(pts).sort_values("slippage_bp")
        x, y = d["slippage_bp"].to_numpy(float), d[col].to_numpy()
        for i in range(len(x) - 1):
            if y[i] > 0 >= y[i + 1]:
                return x[i] + (x[i + 1] - x[i]) * y[i] / (y[i] - y[i + 1])
        return np.nan
    for pname, conv, _, _ in COMBOS:
        wname = "primary_2011_10" if conv == "o2o" else "full"
        pts = [r for r in rows if r["table"] == "headline" and r["panel"] == pname
               and r["convention"] == conv and r["cost_model"] == "uniform"
               and r["window"] == wname]
        for col in ("ann_return", "sharpe_lo"):
            rows.append({"table": "crossings", "panel": pname, "convention": conv,
                         "window": wname, "metric": col,
                         "measured_bp": crossing(pts, col)})

    # deltas vs 13.6 standing headline (full window, uniform x F)
    old = pd.read_csv(ROOT / "outputs" / "session-13.6" / "headline-corrected.csv")
    old = old[old.table == "headline_corrected"]
    for pname in ("synthetic", "realized"):
        for bp in config.SLIPPAGE_BASE_GRID_BP:
            new = [r for r in rows if r["table"] == "headline" and r["panel"] == pname
                   and r["convention"] == "c2c" and r["cost_model"] == "uniform"
                   and r["slippage_bp"] == bp and r["window"] == "full"][0]
            o = old[(old.arm == pname) & (old.slippage_bp == bp)]
            if len(o):
                rows.append({"table": "delta_vs_s136", "panel": pname, "slippage_bp": bp,
                             "d_ann_return": new["ann_return"] - float(o.iloc[0]["ann_return"]),
                             "d_sharpe_lo": new["sharpe_lo"] - float(o.iloc[0]["sharpe_lo"]),
                             "d_max_drawdown": new["max_drawdown"] - float(o.iloc[0]["max_drawdown"])})

    # attribution: patch-only run (old ER) vs 13.6 vs final, syn c2c anchor
    p_old_er = bt.load_arm_panel("synthetic")   # patch active, ER old
    sig_old = bt.ArmSignals(p_old_er, cal)
    srows_old = bt.run_signals(sig_old)["rows"]
    acc_patch = bt.run_account(sig_old, p_old_er, srows_old, ANCHOR, commission_fn=arm_F)
    m_patch = win_metrics(acc_patch["daily"], acc_patch["orders"])
    m_final = [r for r in rows if r["table"] == "headline" and r["panel"] == "synthetic"
               and r["convention"] == "c2c" and r["cost_model"] == "uniform"
               and r["slippage_bp"] == ANCHOR and r["window"] == "full"][0]
    o136 = old[(old.arm == "synthetic") & (old.slippage_bp == ANCHOR)].iloc[0]
    rows.append({"table": "attribution", "point": "syn c2c uniform 10bp full",
                 "s136_ann": float(o136["ann_return"]),
                 "patch_only_ann": m_patch["ann_return"],
                 "final_ann": m_final["ann_return"],
                 "soxs_patch_effect_pp": (m_patch["ann_return"] - float(o136["ann_return"])) * 100,
                 "expense_effect_pp": (m_final["ann_return"] - m_patch["ann_return"]) * 100})
    print(f"attribution: 13.6 {float(o136['ann_return']):.4f} -> patch-only "
          f"{m_patch['ann_return']:.4f} -> final {m_final['ann_return']:.4f}")

    # commission reporting per arm, by year (tiered@anchor runs, syn c2c)
    for arm_name in ("F", "T", "S", "Z"):
        acc = accs[("synthetic", "c2c")][("tiered", arm_name, ANCHOR)]
        od = acc["orders"]
        nav = acc["daily"]["nav"]
        yrs = (len(nav)) / 252
        if len(od) and od["value"].sum() > 0:
            rows.append({"table": "commission_arm", "arm": arm_name,
                         "bp_of_traded": od["commission"].sum() / od["value"].sum() * 1e4,
                         "drag_pp_yr": od["commission"].sum() / nav.mean() / yrs * 100,
                         "min_bound_frac": float(((np.isclose(od["commission"], 1.00)) &
                                                  (0.005 * od["shares"] < 1.00)).mean())
                         if arm_name in ("F", "S") else np.nan,
                         "cap_bound_frac": float(np.isclose(
                             od["commission"], 0.01 * od["value"]).mean())})
            od2 = od.copy()
            od2["year"] = pd.DatetimeIndex(od2["date"]).year
            for y, g in od2.groupby("year"):
                rows.append({"table": "commission_by_year", "arm": arm_name, "year": int(y),
                             "bp_of_traded": g["commission"].sum() / g["value"].sum() * 1e4
                             if g["value"].sum() else 0.0})

    # SOXS effect of the patch (step 2 deliverable)
    od_new = accs[("synthetic", "c2c")][("uniform", "F", ANCHOR)]["orders"]
    g = od_new[od_new.ticker == "SOXS"]
    rows.append({"table": "soxs_patch_effect",
                 "n_orders": len(g), "mean_shares": float(g["shares"].mean()),
                 "commission_bp_of_traded": g["commission"].sum() / g["value"].sum() * 1e4,
                 "note": "13.6 (unpatched): mean shares 15x lower pre-2021-03, "
                         "commission 0.28 bp, min-bound 51%"})

    # sanity checks per combo at the anchor (uniform x F)
    for pname, conv, panel, sig in COMBOS:
        acc = accs[(pname, conv)][("uniform", "F", ANCHOR)]
        d10, od = acc["daily"], acc["orders"]
        recon = abs(float((1 + d10["ret"].fillna(0)).prod()) * d10["nav"].iloc[0]
                    / d10["nav"].iloc[-1] - 1)
        cashgap = (d10["pos_value"] + d10["cash"] - d10["nav"]).abs().max()
        tgross = max((r["gross_before_cap"] or 0) for r in sig["rows"] if r["changed"])
        bad_budget = sum(1 for r in sig["rows"] for k in ("T10", "T11", "S2", "S3")
                         if not (abs(sum(r["sleeves"][k].values())) < 1e-9 or
                                 abs(sum(r["sleeves"][k].values()) - 1) < 1e-9))
        first_fill = d10.index[d10["transition"]].min()
        viol = (od["commission"] > 0.01 * od["value"] + 1e-9).sum()
        lag2 = bt.run_account(sig["sig"], panel, sig["rows"], ANCHOR,
                              fill_lag=2, commission_fn=arm_F)
        m1 = win_metrics(d10, od)
        m2 = win_metrics(lag2["daily"], lag2["orders"])
        checks = {"nav_reconciles": recon < 1e-9,
                  "cash_accounts": cashgap < 1e-6,
                  "gross_target_leq_100pct": tgross <= 1 + 1e-9,
                  "sleeve_budget_sums": bad_budget == 0,
                  "warmup_boundary": first_fill == cal[config.WARMUP_SESSIONS + 1],
                  "commission_cap": viol == 0}
        for name, ok in checks.items():
            rows.append({"table": "sanity", "panel": pname, "convention": conv,
                         "check": name, "result": "PASS" if ok else "FAIL"})
            assert ok, f"sanity {name} failed on {pname}/{conv}"
        rows.append({"table": "sanity", "panel": pname, "convention": conv,
                     "check": "execution_lag_sensitivity",
                     "result": "REPORTED (not a halting failure per the 13.6 "
                               "verdict and corrections item 12)",
                     "detail": f"T+1 ann {m1['ann_return']:.4f} SR_lo "
                               f"{m1['sharpe_lo']:.4f} | T+2 ann {m2['ann_return']:.4f} "
                               f"SR_lo {m2['sharpe_lo']:.4f}"})
        print(f"  sanity [{pname} {conv}]: 6/6 PASS; exec-lag reported")

    pd.DataFrame(rows).to_csv(OUT / "headline-canonical.csv", index=False)
    print(f"[wrote headline-canonical.csv: {len(rows)} rows]")

    # persist anchor run for steps 8-10
    a_ = accs[("synthetic", "c2c")][("uniform", "F", ANCHOR)]
    with open(OUT / "_anchor_run.pkl", "wb") as fh:
        pickle.dump({"daily": a_["daily"], "raw_rows": a_["raw_rows"],
                     "orders": a_["orders"], "signal_rows": sigs["synthetic"]["rows"]}, fh)
    r_ = accs[("realized", "c2c")][("uniform", "F", ANCHOR)]
    with open(OUT / "_anchor_run_realized.pkl", "wb") as fh:
        pickle.dump({"daily": r_["daily"], "raw_rows": r_["raw_rows"]}, fh)


if __name__ == "__main__":
    main()
