"""Session 13.7 — steps 2, 5, 6: commission arms, panel adjustment, rebuilt
canonical result.

Step 3 halted (cost model B not built — see slippage-profile.csv verdict),
so step 6 runs cost model A (the registered uniform sweep) crossed with
commission Arm F, plus the three other commission arms at the anchor.
Canonical remains cost model A with Arm F; Arm S is the measured-
commission comparison. Step 5's panel adjustment applies whatever step 4
recovered (file outputs/session-13.7/_expense_recovered.json; empty ->
no adjustment, every cell flagged).
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
import scripts.s13_runall as ra
from src import config
from src.data import TickerFrame

OUT = ROOT / "outputs" / "session-13.7"
ANCHOR = 10
EXT = (60, 75, 100, 150)
SPLICE = pd.Timestamp("2019-10-01")

# ---------------------------------------------------------------------------
# Step 2 — commission arms
# ---------------------------------------------------------------------------
# Arm T pass-throughs: IBKR's published page returned HTTP 403 to retrieval,
# so CURRENT published schedule values are stated from record and held
# constant across the sample, disclosed: SEC transaction fee $27.80 per $1M
# of SALE proceeds; FINRA TAF $0.000166/share SOLD capped $8.30/order; NSCC
# clearing $0.00020/share; exchange (closing-cross class) $0.0010/share.
SEC_FEE_PER_DOLLAR_SOLD = 27.80 / 1_000_000
TAF_PER_SHARE_SOLD = 0.000166
TAF_CAP = 8.30
CLEARING_PER_SHARE = 0.00020
EXCHANGE_PER_SHARE = 0.0010


def arm_F(date, ticker, side, shares, value):
    return min(max(1.00, 0.005 * shares), 0.01 * value)


def arm_T(date, ticker, side, shares, value):
    c = min(max(0.35, 0.0035 * shares), 0.01 * value)
    c += (CLEARING_PER_SHARE + EXCHANGE_PER_SHARE) * shares
    if side == "sell":
        c += SEC_FEE_PER_DOLLAR_SOLD * value
        c += min(TAF_PER_SHARE_SOLD * shares, TAF_CAP)
    return c


def arm_S(date, ticker, side, shares, value):
    return arm_F(date, ticker, side, shares, value) if date < SPLICE else 0.0


def arm_Z(date, ticker, side, shares, value):
    return 0.0


ARMS = {"F": arm_F, "T": arm_T, "S": arm_S, "Z": arm_Z}

# ---------------------------------------------------------------------------
# Step 5 — panel adjustment layer from step-4 recovered expense data
# ---------------------------------------------------------------------------
REC_PATH = OUT / "_expense_recovered.json"
recovered: dict = {}
if REC_PATH.exists():
    recovered = json.load(open(REC_PATH))
CURRENT_ER = {  # constants currently baked into the synthetics (session 11)
    "TQQQ": 0.95, "SQQQ": 0.95, "QLD": 0.95, "PSQ": 0.95, "SH": 0.89,
    "UVXY": 0.95, "SVXY": 0.95,
    "TECL": 0.83, "TECS": 0.92, "SOXL": 0.71, "SOXS": 0.87, "SPXL": 0.81,
    "FAS": 0.86, "LABU": 0.92,
}


def build_er_adjust() -> dict[str, dict[int, float]]:
    """Per fund-year daily return adjustment: (ER_current - ER_year)/100/252.

    Interpolates between recovered fiscal years; years outside the
    recovered range carry the nearest recovered year (flagged); funds with
    nothing recovered get no adjustment (flagged)."""
    adj: dict[str, dict[int, float]] = {}
    for fund, cells in recovered.items():
        if fund not in CURRENT_ER or not cells:
            continue
        yrs = sorted(int(y) for y in cells)
        per_year = {}
        for y in range(2007, 2022):
            if y <= yrs[0]:
                er = float(cells[str(yrs[0])])
            elif y >= yrs[-1]:
                er = float(cells[str(yrs[-1])])
            else:
                lo = max(v for v in yrs if v <= y)
                hi = min(v for v in yrs if v >= y)
                er = (float(cells[str(lo)]) if lo == hi else
                      float(cells[str(lo)]) + (float(cells[str(hi)]) - float(cells[str(lo)]))
                      * (y - lo) / (hi - lo))
            per_year[y] = (CURRENT_ER[fund] - er) / 100.0 / 252.0
        adj[fund] = per_year
    return adj


def adjusted_panel(arm: str, er_adj: dict) -> bt.Panel:
    panel = bt.load_arm_panel(arm)
    if arm != "synthetic" or not er_adj:
        return panel
    for t, per_year in er_adj.items():
        if t not in panel.frames:
            continue
        fr = panel[t].frame.copy()
        yrs = fr.index.year
        delta = np.array([per_year.get(int(y), 0.0) for y in yrs])
        fr["ret_total"] = fr["ret_total"] + delta
        r = fr["ret_total"].copy()
        if len(r):
            r.iloc[0] = 0.0
        fr["tr_index"] = (1.0 + r).cumprod()
        fr["adj_close"] = fr["tr_index"]
        panel.frames[t] = TickerFrame(t, fr)
    return panel


def main():
    rows = []
    er_adj = build_er_adjust()
    n_cells = sum(len(v) for v in recovered.values()) if recovered else 0
    print(f"step 5: expense cells recovered {n_cells}; funds adjusted: "
          f"{sorted(er_adj) if er_adj else 'NONE (all constants carried, flagged)'}")

    panels = {a: adjusted_panel(a, er_adj) for a in ("synthetic", "realized")}
    for a, p in panels.items():
        ok, mx = bt.assert_holdout(p)
        print(f"holdout [{a}]: PASS max {mx.date()}")
    cal = panels["synthetic"]["SPY"].index
    W = config.WARMUP_SESSIONS
    years = (len(cal) - W) / 252.0

    sigs = {a: {"sig": bt.ArmSignals(panels[a], cal),
                } for a in panels}
    for a in sigs:
        sigs[a].update(bt.run_signals(sigs[a]["sig"]))

    # step 5 revalidation happens in s13_7_panelcheck.py when an adjustment
    # exists; with no adjustment the 13.6 in-window values stand unchanged.

    old = pd.read_csv(ROOT / "outputs" / "session-13.6" / "headline-corrected.csv")
    old = old[old.table == "headline_corrected"]

    accs = {}
    print("== step 6: cost model A x Arm F (registered) + extension ==")
    for a in ("synthetic", "realized"):
        accs[a] = {}
        for bp in list(config.SLIPPAGE_BASE_GRID_BP) + list(EXT):
            acc = bt.run_account(sigs[a]["sig"], panels[a], sigs[a]["rows"], bp,
                                 commission_fn=arm_F)
            accs[a][("A", "F", bp)] = acc
            m = bt.headline_metrics(acc["daily"], acc["orders"])
            row = {"table": "headline", "cost_model": "A_uniform", "commission_arm": "F",
                   "arm": a, "slippage_bp": bp,
                   "in_registered_grid": bp in config.SLIPPAGE_BASE_GRID_BP,
                   **{k: m[k] for k in ("total_return", "ann_return", "ann_vol",
                                        "sharpe_naive", "sharpe_lo", "max_drawdown",
                                        "calmar", "ann_turnover_one_sided")}}
            o = old[(old.arm == a) & (old.slippage_bp == bp)]
            if len(o):
                for k in ("ann_return", "sharpe_lo", "max_drawdown"):
                    row[f"delta_vs_s136_{k}"] = m[k] - float(o.iloc[0][k])
            rows.append(row)
        print(f"  [{a}] A x F done")

    print("== step 6: commission arms T, S, Z at the anchor ==")
    for a in ("synthetic", "realized"):
        for arm_name in ("T", "S", "Z"):
            acc = bt.run_account(sigs[a]["sig"], panels[a], sigs[a]["rows"], ANCHOR,
                                 commission_fn=ARMS[arm_name])
            accs[a][("A", arm_name, ANCHOR)] = acc
            m = bt.headline_metrics(acc["daily"], acc["orders"])
            rows.append({"table": "headline", "cost_model": "A_uniform",
                         "commission_arm": arm_name, "arm": a, "slippage_bp": ANCHOR,
                         "in_registered_grid": True,
                         **{k: m[k] for k in ("total_return", "ann_return", "ann_vol",
                                              "sharpe_naive", "sharpe_lo", "max_drawdown",
                                              "calmar", "ann_turnover_one_sided")}})
        print(f"  [{a}] arms done")

    # step 2 reporting: per-arm commission stats, by year (synthetic, anchor)
    for arm_name in ("F", "T", "S", "Z"):
        acc = accs["synthetic"][("A", arm_name, ANCHOR)]
        od = acc["orders"]
        nav = acc["daily"]["nav"]
        if len(od) and od["value"].sum() > 0:
            bp_traded = od["commission"].sum() / od["value"].sum() * 1e4
            drag = od["commission"].sum() / nav.mean() / years * 100
            fixed_like = od["commission"] > 0
            minb = float(((np.isclose(od["commission"].where(fixed_like), 1.00)) &
                          (0.005 * od["shares"] < 1.00)).mean()) if arm_name in ("F", "S") else np.nan
        else:
            bp_traded = drag = 0.0
            minb = 0.0
        rows.append({"table": "commission_arm_summary", "commission_arm": arm_name,
                     "bp_of_traded": bp_traded, "annualised_drag_pp": drag,
                     "frac_orders_min_bound": minb})
        od2 = od.copy()
        od2["year"] = pd.DatetimeIndex(od2["date"]).year
        for y, g in od2.groupby("year"):
            navy = nav[nav.index.year == y]
            rows.append({"table": "commission_by_year", "commission_arm": arm_name,
                         "year": int(y),
                         "bp_of_traded": (g["commission"].sum() / g["value"].sum() * 1e4)
                         if g["value"].sum() else 0.0,
                         "drag_pp": g["commission"].sum() / navy.mean() /
                         (len(navy) / 252.0) * 100 if len(navy) else np.nan})
        print(f"  arm {arm_name}: {bp_traded:.2f} bp of traded, {drag:.3f} pp/yr")

    # order aggregation check (Arm F, anchor): the engine already submits one
    # order per instrument per session (merged-portfolio delta trading) —
    # the canonical run IS the aggregated case. Counterfactual: split each
    # order into per-sleeve suborders proportional to that ticker's sleeve
    # target weights at the transition.
    acc = accs["synthetic"][("A", "F", ANCHOR)]
    od = acc["orders"]
    by_i = {r["i"]: r for r in sigs["synthetic"]["rows"]}
    cal_ix = {d: i for i, d in enumerate(cal)}
    agg_comm = od["commission"].sum()
    unagg_comm = 0.0
    n_sub = 0
    n_sub_min = 0
    for _, o in od.iterrows():
        i_f = cal_ix[o["date"]]
        sr = by_i.get(i_f - 1)
        shares_split = []
        if sr is not None:
            t = o["ticker"]
            sleeve_w = [sr["sleeves"][k].get(t, 0.0) for k in ("T10", "T11", "S2", "S3")]
            tot = sum(sleeve_w)
            if tot > 0:
                shares_split = [o["shares"] * w / tot for w in sleeve_w if w > 0]
        if not shares_split:
            shares_split = [o["shares"]]
        for sh in shares_split:
            v = o["value"] * sh / o["shares"]
            c = min(max(1.00, 0.005 * sh), 0.01 * v)
            unagg_comm += c
            n_sub += 1
            if 0.005 * sh < 1.00 and c <= 0.01 * v:
                n_sub_min += 1
    nav = acc["daily"]["nav"]
    rows.append({"table": "aggregation_check",
                 "aggregated_commission": agg_comm,
                 "unaggregated_commission": unagg_comm,
                 "aggregated_drag_pp": agg_comm / nav.mean() / years * 100,
                 "unaggregated_drag_pp": unagg_comm / nav.mean() / years * 100,
                 "aggregated_min_bound_frac": float(
                     ((np.isclose(od["commission"], 1.00)) & (0.005 * od["shares"] < 1.00)).mean()),
                 "unaggregated_min_bound_frac": n_sub_min / n_sub,
                 "note": "the engine merges sleeves before trading, so the canonical "
                         "run already uses aggregated one-order-per-instrument "
                         "submission; the unaggregated figure is the counterfactual"})
    print(f"  aggregation: agg ${agg_comm:,.0f} vs unagg ${unagg_comm:,.0f} "
          f"(min-bound {rows[-1]['aggregated_min_bound_frac']:.1%} vs "
          f"{rows[-1]['unaggregated_min_bound_frac']:.1%})")

    # crossings under model A
    def crossing(pts, col):
        d = pd.DataFrame(pts).sort_values("slippage_bp")
        x, y = d["slippage_bp"].to_numpy(float), d[col].to_numpy()
        for i in range(len(x) - 1):
            if y[i] > 0 >= y[i + 1]:
                return x[i] + (x[i + 1] - x[i]) * y[i] / (y[i] - y[i + 1])
        return np.nan
    for a in ("synthetic", "realized"):
        pts = [r for r in rows if r["table"] == "headline" and r["arm"] == a
               and r["commission_arm"] == "F"]
        for col in ("ann_return", "sharpe_lo"):
            rows.append({"table": "crossings", "arm": a, "metric": col,
                         "measured_bp": crossing(pts, col)})

    pd.DataFrame(rows).to_csv(OUT / "headline-rebuilt.csv", index=False)
    pd.DataFrame(rows).to_csv(OUT / "commission-arms.csv", index=False)
    print("[wrote headline-rebuilt.csv / commission-arms.csv]")

    # persist the anchor run for step 9
    import pickle
    d10 = accs["synthetic"][("A", "F", ANCHOR)]
    with open(OUT / "_anchor_run.pkl", "wb") as fh:
        pickle.dump({"daily": d10["daily"], "raw_rows": d10["raw_rows"],
                     "orders": d10["orders"],
                     "signal_rows": sigs["synthetic"]["rows"]}, fh)
    return rows


if __name__ == "__main__":
    main()
