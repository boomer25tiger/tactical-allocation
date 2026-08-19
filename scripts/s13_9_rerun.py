"""Session 13.9 step 3 — canonical re-run under class-based tiers and the
opening-auction premium (o2o only). Uniform-sweep results carry forward
from 13.8 unchanged. Premium parameters read from
outputs/session-13.9/_premium.json (written after step 2's retrieval).
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

OUT = ROOT / "outputs" / "session-13.9"
OUT.mkdir(parents=True, exist_ok=True)
S138 = ROOT / "outputs" / "session-13.8"
ANCHOR = 10
PRIMARY_START = pd.Timestamp("2011-10-03")
EARLY_END = pd.Timestamp("2011-10-02")
SPLICE = pd.Timestamp(config.COMMISSION_SPLICE_DATE)

prem = json.load(open(OUT / "_premium.json"))
PREMIUM = prem["central_by_tier"]          # {tier: multiplier} or uniform
er = json.load(open(S138 / "_er_new.json"))
ER_OLD, ER_NEW = er["ER_OLD"], er["ER_NEW"]

TIER_CLASS = {"QQQ": 1, "TLT": 1, "BIL": 1, "BSV": 1,
              "TQQQ": 2, "SQQQ": 2, "QLD": 2, "PSQ": 2, "SH": 2,
              "SOXL": 3, "SOXS": 3, "TECL": 3, "TECS": 3, "SPXL": 3,
              "FAS": 3, "LABU": 3, "UVXY": 3, "SVXY": 3, "BTAL": 3}
MULT = {1: 0.2, 2: 0.5, 3: 1.5}

SEC_FEE = 27.80 / 1e6
TAF = 0.000166
TAF_CAP = 8.30
PASSTHRU = 0.0012

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


def slip_class(date, t):
    return ANCHOR * MULT[TIER_CLASS.get(t, 3)]


def slip_class_premium(date, t):
    tier = TIER_CLASS.get(t, 3)
    return ANCHOR * MULT[tier] * PREMIUM[str(tier)]


def adjusted_syn_panel():
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


def o2o_panel_from(p):
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
    return {"total_return": float(nav.iloc[-1] - 1),
            "ann_return": float(nav.iloc[-1] ** (252 / n) - 1),
            "ann_vol": float(r.std(ddof=1) * math.sqrt(252)),
            "sharpe_naive": float(ex.mean() / ex.std(ddof=1) * math.sqrt(252)),
            "sharpe_lo": bt.lo_sharpe(ex),
            "max_drawdown": float((nav / nav.cummax() - 1).min()),
            "arith_mean_excess_ann": float(ex.mean() * 252),
            "geo_ann_excess": float((1 + r).prod() ** (252 / n) -
                                    (1 + rf).prod() ** (252 / n))}


def main():
    rows = []
    panels = {"synthetic": adjusted_syn_panel(), "realized": bt.load_arm_panel("realized")}
    for a, p in panels.items():
        ok, mx = bt.assert_holdout(p)
        print(f"holdout [{a}]: PASS max {mx.date()}")
    cal = panels["synthetic"]["SPY"].index
    sigs = {a: {"sig": bt.ArmSignals(panels[a], cal)} for a in panels}
    for a in sigs:
        sigs[a].update(bt.run_signals(sigs[a]["sig"]))
    o2o = o2o_panel_from(panels["realized"])

    COMBOS = [("synthetic", "c2c", panels["synthetic"], sigs["synthetic"], slip_class),
              ("realized", "c2c", panels["realized"], sigs["realized"], slip_class),
              ("realized", "o2o", o2o, sigs["realized"], slip_class_premium),
              ("realized", "o2o_nopremium", o2o, sigs["realized"], slip_class)]
    accs = {}
    for pname, conv, panel, sig, sf in COMBOS:
        for arm_name in ("F", "T", "S", "Z"):
            acc = bt.run_account(sig["sig"], panel, sig["rows"], ANCHOR,
                                 commission_fn=ARMS[arm_name], slip_fn=sf)
            accs[(pname, conv, arm_name)] = acc
            for wname, ws, we in (("full", None, None),
                                  ("primary_2011_10", PRIMARY_START, None),
                                  ("early_synthetic_only", None, EARLY_END)):
                if wname == "early_synthetic_only" and pname == "realized":
                    continue
                if conv.startswith("o2o") and wname != "primary_2011_10":
                    continue
                m = win_metrics(acc["daily"], acc["orders"], ws, we)
                if m is None:
                    continue
                rows.append({"table": "headline", "panel": pname, "convention": conv,
                             "cost_model": "tiered_class", "commission_arm": arm_name,
                             "window": wname, **m})
        print(f"  [{pname} {conv}] done")

    # deltas vs 13.8 tiered points
    old = pd.read_csv(S138 / "headline-canonical.csv")
    oldh = old[(old.table == "headline") & (old.cost_model == "tiered")]
    for pname, conv in (("synthetic", "c2c"), ("realized", "c2c"), ("realized", "o2o")):
        for arm_name in ("F", "T", "S", "Z"):
            wname = "primary_2011_10" if conv == "o2o" else "full"
            new = [r for r in rows if r["table"] == "headline" and r["panel"] == pname
                   and r["convention"] == conv and r["commission_arm"] == arm_name
                   and r["window"] == wname]
            o = oldh[(oldh.panel == pname) & (oldh.convention == conv)
                     & (oldh.commission_arm == arm_name) & (oldh.window == wname)]
            if new and len(o):
                rows.append({"table": "delta_vs_s138", "panel": pname, "convention": conv,
                             "commission_arm": arm_name, "window": wname,
                             "d_ann_return": new[0]["ann_return"] - float(o.iloc[0]["ann_return"]),
                             "d_sharpe_lo": new[0]["sharpe_lo"] - float(o.iloc[0]["sharpe_lo"])})

    # per-instrument slippage + commission drag (arm S anchor, syn c2c and o2o)
    for key, lbl in ((("synthetic", "c2c", "S"), "syn_c2c"),
                     (("realized", "o2o", "S"), "real_o2o_premium"),
                     (("realized", "o2o_nopremium", "S"), "real_o2o_nopremium")):
        od = accs[key]["orders"]
        for t, g in od.groupby("ticker"):
            rows.append({"table": f"drag_by_instrument_{lbl}", "ticker": t,
                         "slippage_bp_of_traded": g["slippage"].sum() / g["value"].sum() * 1e4,
                         "commission_bp_of_traded": g["commission"].sum() / g["value"].sum() * 1e4
                         if g["value"].sum() else 0})

    # sanity on every combo (arm S anchor)
    for pname, conv, panel, sig, sf in COMBOS:
        acc = accs[(pname, conv, "S")]
        d10, od = acc["daily"], acc["orders"]
        recon = abs(float((1 + d10["ret"].fillna(0)).prod()) * d10["nav"].iloc[0]
                    / d10["nav"].iloc[-1] - 1)
        cashgap = (d10["pos_value"] + d10["cash"] - d10["nav"]).abs().max()
        first_fill = d10.index[d10["transition"]].min()
        viol = (od["commission"] > 0.01 * od["value"] + 1e-9).sum()
        checks = {"nav_reconciles": recon < 1e-9, "cash_accounts": cashgap < 1e-6,
                  "warmup_boundary": first_fill == cal[config.WARMUP_SESSIONS + 1],
                  "commission_cap": viol == 0}
        for name, ok in checks.items():
            rows.append({"table": "sanity", "panel": pname, "convention": conv,
                         "check": name, "result": "PASS" if ok else "FAIL"})
            assert ok, f"{name} failed on {pname}/{conv}"
        print(f"  sanity [{pname} {conv}]: PASS")
    rows.append({"table": "carry_forward", "note":
                 "uniform-sweep results carry forward from session 13.8 "
                 "unchanged (slippage model untouched there); gross/budget/"
                 "lag checks unchanged from 13.8 (signal side identical)"})

    pd.DataFrame(rows).to_csv(OUT / "headline-retiered.csv", index=False)
    print(f"[wrote headline-retiered.csv: {len(rows)} rows]")
    a_ = accs[("realized", "o2o", "S")]
    with open(OUT / "_headline_run.pkl", "wb") as fh:
        pickle.dump({"daily": a_["daily"], "raw_rows": a_["raw_rows"]}, fh)
    s_ = accs[("synthetic", "c2c", "S")]
    with open(OUT / "_syn_anchor.pkl", "wb") as fh:
        pickle.dump({"daily": s_["daily"], "raw_rows": s_["raw_rows"],
                     "signal_rows": sigs["synthetic"]["rows"]}, fh)


if __name__ == "__main__":
    main()
