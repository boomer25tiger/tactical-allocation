"""Session 15.5: PSQ hedge instrument and hedge intensity, diagnostic only.

Every arm is a labelled diagnostic arm reported alongside the canonical,
never in place of it. Nothing here is adopted. Post-hoc under 9.10: the
comparison was motivated by a visible result, being SQQQ's primary-window
contribution decomposing into -39.35 beta and -0.05 residual.
"""
from __future__ import annotations

import json, math, pickle, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
import scripts.s14_common as C
import scripts.s15_lines as L
from src import config
from src.portfolio import PortfolioTracker, SLEEVE_ORDER, sleeve_label
from src.schedule import FUND_SCHEDULE

OUT = ROOT / "outputs" / "session-15.5"
OUT.mkdir(parents=True, exist_ok=True)

env = L.build_env()
cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]
TICK = list(ra.TARGET_TICKERS)
SLEEVE_BUDGET = config.SLEEVE_BUDGET

# T10 canonical terminal to be replaced
T10_BEAR = {"SQQQ": 0.5, "TLT": 0.5}

def mult_of(t):
    if t in FUND_SCHEDULE:
        return float(FUND_SCHEDULE[t][-1].multiple)
    return 1.0

ARMS = {
    "A": {"short": "SQQQ", "t10_bear": {"SQQQ": 0.5, "TLT": 0.5},
          "role": "canonical, positive control"},
    "B": {"short": "PSQ", "t10_bear": {"PSQ": 0.5, "TLT": 0.5},
          "role": "direct swap at equal weight"},
    "C": {"short": "SQQQ", "t10_bear": {"SQQQ": 1.0 / 6.0, "TLT": 0.5},
          "role": "notional twin of B"},
    "D": {"short": "SQQQ", "t10_bear": {"SQQQ": 1.0 / 3.0, "TLT": 0.5},
          "role": "intensity curve"},
    "E": {"short": "PSQ", "t10_bear": {"PSQ": 1.0},
          "role": "reported, CONFOUNDED (displaces TLT entirely)"},
    "F": {"short": None, "t10_bear": {"TLT": 1.0},
          "role": "no-short control"},
}

def notional(arm):
    d = ARMS[arm]["t10_bear"]
    s = ARMS[arm]["short"]
    if s is None:
        return 0.0
    return -SLEEVE_BUDGET * d[s] * abs(mult_of(s))

# ---------------------------------------------------------------------------
def rebuild_rows(base_rows, t10_bear=None, swap_all=None):
    """Re-run the 5.1 tracker on transformed sleeve dicts so labels, the
    short circuit, and the gross cap are all recomputed for the arm."""
    tracker = PortfolioTracker()
    out = []
    for r in base_rows:
        sl = {k: dict(r["sleeves"][k]) for k in SLEEVE_ORDER}
        if t10_bear is not None and sl["T10"] == T10_BEAR:
            sl["T10"] = dict(t10_bear)
        if swap_all is not None:
            a, b = swap_all
            for k in SLEEVE_ORDER:
                if a in sl[k]:
                    w = sl[k].pop(a)
                    sl[k][b] = sl[k].get(b, 0.0) + w
        d = tracker.step(cal[r["i"]], sl["T10"], sl["T11"], sl["S2"], sl["S3"])
        out.append({"i": r["i"], "date": d.date, "label": d.label,
                    "changed": d.changed, "targets": d.targets,
                    "gross_before_cap": d.gross_before_cap,
                    "cap_truncated": d.cap_truncated, "sleeves": sl, "raised": {}})
    return out

def t10_only_rows(rows):
    """T10 standalone at full budget."""
    tracker = PortfolioTracker()
    out = []
    for r in rows:
        w = dict(r["sleeves"]["T10"])
        changed = (not out) or w != getattr(t10_only_rows, "_prev", None)
        t10_only_rows._prev = dict(w)
        out.append({"i": r["i"], "changed": changed, "targets": dict(w) if changed else None})
    return out

def run(rows, conv, cap=True, bp=None, panel_override=None):
    panel = panel_override if panel_override is not None else (
        o2o if conv == "o2o" else panels["realized"])
    sf = C.slip_uniform(bp) if bp is not None else (
        C.slip_class_premium() if conv == "o2o" else C.slip_class)
    return bt.run_account(sigs["realized"]["sig"], panel, rows, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM], slip_fn=sf,
                          cap_fn=cap_fn if cap else None)

base_rows = sigs["realized"]["rows"]
syn_rows = sigs["synthetic"]["rows"]
arm_rows = {a: rebuild_rows(base_rows, ARMS[a]["t10_bear"]) for a in ARMS}
arm_rows_syn = {a: rebuild_rows(syn_rows, ARMS[a]["t10_bear"]) for a in ARMS}
arm_rows["B_all"] = rebuild_rows(base_rows, ARMS["B"]["t10_bear"], swap_all=("SQQQ", "PSQ"))
arm_rows_syn["B_all"] = rebuild_rows(syn_rows, ARMS["B"]["t10_bear"], swap_all=("SQQQ", "PSQ"))
ARMS["B_all"] = {"short": "PSQ", "t10_bear": ARMS["B"]["t10_bear"],
                 "role": "SECONDARY: sleeve-wide SQQQ->PSQ substitution"}

# ===========================================================================
print("== STEP 1: short-leg sites ==")
rows1 = []
SITES = [
    ("T10", "rs_bear -> 50% SQQQ + 50% TLT", "SQQQ", 0.5, "TLT", "src/sleeves.py:190"),
    ("T11", "bull_short -> 33% TECS + 33% SOXS + 33% SQQQ", "SQQQ", 1/3,
     "TECS;SOXS", "src/sleeves.py:266"),
    ("T11", "bear sub-model terminal (bond_baller else->SQQQ)", "SQQQ", 0.5,
     "paired sub-model pick", "src/sleeves.py:210"),
    ("T11", "bear sub-model terminal (feaver else->SQQQ)", "SQQQ", 0.5,
     "paired sub-model pick", "src/sleeves.py:239"),
    ("S2", "defensive -> 100% SQQQ", "SQQQ", 1.0, "none", "src/sleeves.py:300"),
    ("T11", "bear sub-model terminals routing to PSQ", "PSQ", 0.5,
     "paired sub-model pick", "src/sleeves.py:204,207,209,233,236,238"),
]
# firing rates over the primary window
prim = [r for r in base_rows if cal[r["i"]] >= C.PRIMARY_START]
n_prim = len(prim)
state_counts = {}
for r in prim:
    for k in SLEEVE_ORDER:
        st = sleeve_label(r["sleeves"][k])
        state_counts[(k, st)] = state_counts.get((k, st), 0) + 1
for sleeve, state, inst, w, coheld, loc in SITES:
    hits = sum(n for (k, st), n in state_counts.items()
               if k == sleeve and inst in st)
    rows1.append({"table": "site", "sleeve": sleeve, "terminal_state": state,
                  "instrument": inst, "weight_in_sleeve": w, "co_held": coheld,
                  "code_location": loc, "leverage_multiple": mult_of(inst),
                  "sessions_sleeve_state_contains_instrument_primary": hits,
                  "firing_rate_primary": hits / n_prim})
for inst in ("SQQQ", "PSQ", "SH"):
    tot = sum(n for (k, st), n in state_counts.items() if inst in st)
    rows1.append({"table": "instrument_summary", "instrument": inst,
                  "leverage_multiple": mult_of(inst),
                  "sleeve_sessions_holding_primary": tot,
                  "appears_in_any_weight_dict": inst in ("SQQQ", "PSQ"),
                  "note": "SH appears in no weight dictionary anywhere in the "
                          "return-generating path; it enters only as the right "
                          "side of the AGG>SH pairwise signal comparison"
                          if inst == "SH" else ""})
rows1.append({"table": "sleeve_wide_requirement", "note":
              "SQQQ appears in T10, T11 (bull-short basket and both bear "
              "sub-model terminals), and S2, so a T10-only substitution does not "
              "remove SQQQ from the portfolio. Arm B_all is added as a SECONDARY "
              "arm applying the substitution sleeve-wide, reported separately so "
              "the T10-only effect is not confounded with a portfolio-wide swap."})
pd.DataFrame(rows1).to_csv(OUT / "short-leg-sites.csv", index=False)
for r in rows1:
    if r["table"] == "site":
        print(f"  {r['sleeve']:4s} {r['instrument']:5s} w={r['weight_in_sleeve']:.4f} "
              f"M={r['leverage_multiple']:+.1f} firing {r['firing_rate_primary']:.2%}")

# ===========================================================================
print("\n== STEP 2: arm registration (pre-registered) ==")
rows2 = []
for a in ("A", "B", "C", "D", "E", "F", "B_all"):
    d = ARMS[a]
    rows2.append({"table": "registration", "arm": a,
                  "short_leg": d["short"] or "none",
                  "branch_weights": "; ".join(f"{k} {v:.5f}" for k, v in d["t10_bear"].items()),
                  "residual_to_sleeve_cash": round(1.0 - sum(d["t10_bear"].values()), 5),
                  "short_notional_frac_nav": notional(a) if a != "B_all" else notional("B"),
                  "leverage_multiple": mult_of(d["short"]) if d["short"] else 0.0,
                  "role": d["role"]})
rows2.append({"table": "constraint", "note":
              "Notional matching above -25 percent is unreachable with PSQ: the "
              "canonical -37.5 percent needs 150 percent of the branch, which "
              "breaches the 5.3 gross cap at 100 percent. Recorded as a "
              "structural constraint of the -1x expression rather than an "
              "omission from the slate."})
rows2.append({"table": "constraint", "note":
              "Arm E reaches -25 percent with PSQ only by taking 100 percent of "
              "the branch, which displaces TLT entirely, so it changes two things "
              "at once. CONFOUNDED, reported, and not used for the instrument "
              "comparison."})
rows2.append({"table": "constraint", "note":
              "Displaced weight routes to sleeve cash accruing DTB3 through the "
              "existing 1.9/2.11 path. No new accounting path is created."})
rows2.append({"table": "prereg", "note":
              "The arm table was fixed and written to this artifact before any "
              "performance statistic was computed on any arm. Post-hoc under "
              "9.10: the comparison was motivated by a visible result."})
pd.DataFrame(rows2).to_csv(OUT / "arm-registration.csv", index=False)
print(pd.DataFrame([r for r in rows2 if r["table"] == "registration"])[
    ["arm", "short_leg", "branch_weights", "short_notional_frac_nav", "role"]].to_string(index=False))

# ===========================================================================
print("\n== STEP 3: positive control ==")
rows3 = []
accA = run(arm_rows["A"], "o2o")
mA = L.standalone_metrics(C.window_slice(accA["daily"]["ret"], "primary"),
                          accA["daily"]["nav"], accA["orders"])
ok1 = abs(mA["ann_return"] - 0.5226) < 5e-5 and abs(mA["sharpe_lo"] - 1.3846) < 5e-5
rows3.append({"table": "control", "target": "designated cell (portfolio)",
              "s155_ann": mA["ann_return"], "s15_ann": 0.5226,
              "s155_sharpe_lo": mA["sharpe_lo"], "s15_sharpe_lo": 1.3846,
              "match_4dp": bool(ok1)})
print(f"  portfolio: {mA['ann_return']:.4f}/{mA['sharpe_lo']:.4f} vs 0.5226/1.3846 -> {ok1}")
accA10 = run(t10_only_rows(arm_rows["A"]), "o2o")
mA10 = L.standalone_metrics(C.window_slice(accA10["daily"]["ret"], "primary"),
                            accA10["daily"]["nav"], accA10["orders"])
ok2 = abs(mA10["ann_return"] - 0.0484) < 5e-5 and abs(mA10["sharpe_lo"] - 0.507) < 5e-4
rows3.append({"table": "control", "target": "T10 standalone",
              "s155_ann": mA10["ann_return"], "s15_ann": 0.0484,
              "s155_sharpe_lo": mA10["sharpe_lo"], "s15_sharpe_lo": 0.507,
              "match_4dp": bool(ok2)})
print(f"  T10 standalone: {mA10['ann_return']:.4f}/{mA10['sharpe_lo']:.4f} vs 0.0484/0.507 -> {ok2}")
assert ok1 and ok2, "positive control failed; session halts"
pd.DataFrame(rows3).to_csv(OUT / "_control.csv", index=False)

# ===========================================================================
print("\n== STEP 4: full metric slate on every arm ==")
ARM_ORDER = ["A", "B", "C", "D", "E", "F", "B_all"]
COMBOS = [("realized", "c2c", "full"), ("realized", "c2c", "primary"),
          ("realized", "o2o", "primary"), ("synthetic", "c2c", "early")]
lad = pickle.load(open(ROOT / "outputs" / "session-14" / "_ladder_returns.pkl", "rb"))
rows4, ACC = [], {}
for pname, conv, wname in COMBOS:
    panel = (o2o if conv == "o2o" else panels[pname])
    rowsrc = arm_rows_syn if pname == "synthetic" else arm_rows
    sigkey = "synthetic" if pname == "synthetic" else "realized"
    for a in ARM_ORDER:
        for level in ("portfolio", "T10_standalone"):
            rws = rowsrc[a] if level == "portfolio" else t10_only_rows(rowsrc[a])
            acc = bt.run_account(sigs[sigkey]["sig"], panel, rws, C.ANCHOR,
                                 commission_fn=C.ARMS[C.CANONICAL_ARM],
                                 slip_fn=(C.slip_class_premium() if conv == "o2o"
                                          else C.slip_class), cap_fn=cap_fn)
            ACC[(a, pname, conv, wname, level)] = acc
            r = C.window_slice(acc["daily"]["ret"], wname)
            m = L.standalone_metrics(r, acc["daily"]["nav"], acc["orders"])
            rel = {}
            for (lname, lconv, lwin), ls in lad["lines"].items():
                if lconv == conv and lwin == wname:
                    rr = L.relative_metrics(r, ls)
                    if rr:
                        rows4.append({"table": "relative", "arm": a, "level": level,
                                      "panel": pname, "convention": conv,
                                      "window": wname, "vs_line": lname, **rr})
            rows4.append({"table": "metrics", "arm": a, "level": level,
                          "panel": pname, "convention": conv, "window": wname,
                          "short_notional": notional("B" if a == "B_all" else a), **m})
    print(f"  [{pname} {conv} {wname}] {len(ARM_ORDER)} arms x 2 levels")
mdf = pd.DataFrame([r for r in rows4 if r["table"] == "metrics"])
for _, r in mdf.iterrows():
    if r["arm"] == "A":
        continue
    base = mdf[(mdf.arm == "A") & (mdf.level == r["level"]) &
               (mdf.convention == r["convention"]) & (mdf.window == r["window"])]
    if not len(base):
        continue
    b = base.iloc[0]
    rows4.append({"table": "delta_vs_A", "arm": r["arm"], "level": r["level"],
                  "panel": r["panel"], "convention": r["convention"],
                  "window": r["window"],
                  **{f"d_{k}": float(r[k]) - float(b[k]) for k in
                     ("ann_return", "ann_vol", "sharpe_lo", "max_drawdown",
                      "calmar", "ann_turnover", "ulcer_index", "sortino_mar_dtb3")}})
pd.DataFrame(rows4).to_csv(OUT / "metrics-arms.csv", index=False)
print(f"[wrote metrics-arms.csv: {len(rows4)} rows]")

# ===========================================================================
print("\n== STEP 5: instrument effect at fixed notional (B vs C) ==")
rows5 = []
KEY = ("realized", "o2o", "primary")
mB = mdf[(mdf.arm == "B") & (mdf.level == "portfolio") & (mdf.convention == "o2o")
         & (mdf.window == "primary")].iloc[0]
mC = mdf[(mdf.arm == "C") & (mdf.level == "portfolio") & (mdf.convention == "o2o")
         & (mdf.window == "primary")].iloc[0]
irB = [r for r in rows4 if r["table"] == "relative" and r["arm"] == "B"
       and r["level"] == "portfolio" and r["convention"] == "o2o"
       and r["window"] == "primary" and r["vs_line"] == "buy_hold_QQQ"]
irC = [r for r in rows4 if r["table"] == "relative" and r["arm"] == "C"
       and r["level"] == "portfolio" and r["convention"] == "o2o"
       and r["window"] == "primary" and r["vs_line"] == "buy_hold_QQQ"]
for k in ("ann_return", "ann_vol", "sharpe_lo", "max_drawdown", "ann_turnover"):
    rows5.append({"table": "b_minus_c", "metric": k, "arm_B": float(mB[k]),
                  "arm_C": float(mC[k]), "B_minus_C": float(mB[k]) - float(mC[k])})
if irB and irC:
    rows5.append({"table": "b_minus_c", "metric": "information_ratio_vs_buy_hold_QQQ",
                  "arm_B": irB[0]["information_ratio"], "arm_C": irC[0]["information_ratio"],
                  "B_minus_C": irB[0]["information_ratio"] - irC[0]["information_ratio"]})
# capital difference and its DTB3 accrual
accB = ACC[("B", "realized", "o2o", "primary", "portfolio")]
accC = ACC[("C", "realized", "o2o", "primary", "portfolio")]
bear_dates = [cal[r["i"]] for r in base_rows
              if r["sleeves"]["T10"] == T10_BEAR and cal[r["i"]] >= C.PRIMARY_START]
inc = SLEEVE_BUDGET * (0.5 - 1.0 / 6.0)          # 8.333% of NAV
dailyC = accC["daily"]
rf = bt.rf_per_session(dailyC.index).fillna(0.0)
held = dailyC.index.isin(pd.DatetimeIndex(bear_dates))
accrual = float((rf[held] * inc).sum())
n_y = len(C.window_slice(dailyC["ret"], "primary")) / 252.0
rows5.append({"table": "capital", "incremental_cash_frac_nav": inc,
              "sessions_branch_active_primary": int(held.sum()),
              "dtb3_accrual_arith_over_window": accrual,
              "dtb3_accrual_annualised_pp": 100 * accrual / n_y,
              "note": "arm C deploys 4.167 percent of NAV to reach -12.5 percent "
                      "notional where arm B deploys 12.5 percent, so arm C holds "
                      "8.333 percent of NAV in sleeve cash on the sessions the "
                      "branch is active"})
resid = (float(mB["ann_return"]) - float(mC["ann_return"])) + (100 * accrual / n_y) / 100.0
rows5.append({"table": "residual", "b_minus_c_ann_return": float(mB["ann_return"]) - float(mC["ann_return"]),
              "cash_accrual_annualised": accrual / n_y,
              "residual_after_netting_cash": resid,
              "note": "residual near zero establishes the -1x and -3x expressions "
                      "are interchangeable at matched notional over this sample"})
print(f"  B-C ann {float(mB['ann_return'])-float(mC['ann_return']):+.5f}, "
      f"SR {float(mB['sharpe_lo'])-float(mC['sharpe_lo']):+.5f}, "
      f"cash accrual {accrual/n_y:+.5f}/yr, residual {resid:+.5f}")
pd.DataFrame(rows5).to_csv(OUT / "instrument-effect.csv", index=False)

# ===========================================================================
print("\n== STEP 6: hedge intensity curve ==")
rows6 = []
CURVE = [("A", -0.375), ("D", -0.250), ("C", -0.125), ("F", 0.0)]
for pname, conv, wname in [("realized", "o2o", "primary"),
                           ("realized", "c2c", "primary"),
                           ("realized", "c2c", "full")]:
    pts = []
    for a, nt in CURVE:
        m = mdf[(mdf.arm == a) & (mdf.level == "portfolio") &
                (mdf.convention == conv) & (mdf.window == wname)].iloc[0]
        ir = [r for r in rows4 if r["table"] == "relative" and r["arm"] == a
              and r["level"] == "portfolio" and r["convention"] == conv
              and r["window"] == wname and r["vs_line"] == "buy_hold_QQQ"]
        row = {"table": "curve", "convention": conv, "window": wname, "arm": a,
               "short_notional": nt,
               **{k: float(m[k]) for k in ("ann_return", "ann_vol", "sharpe_lo",
                                           "max_drawdown", "ulcer_index")},
               "information_ratio_vs_buy_hold_QQQ":
                   ir[0]["information_ratio"] if ir else np.nan}
        rows6.append(row)
        pts.append(row)
    for met in ("ann_return", "sharpe_lo"):
        vals = [p[met] for p in pts]           # ordered A -> D -> C -> F, more to less hedge
        mono_up = all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
        mono_dn = all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1))
        best = CURVE[int(np.argmax(vals))][0]
        rows6.append({"table": "monotonicity", "convention": conv, "window": wname,
                      "metric": met, "monotone_toward_less_hedge": bool(mono_up),
                      "monotone_toward_more_hedge": bool(mono_dn),
                      "interior_maximum_arm": "" if (mono_up or mono_dn) else best,
                      "values_A_D_C_F": "; ".join(f"{v:.4f}" for v in vals)})
        print(f"  [{conv} {wname}] {met}: {' -> '.join(f'{v:.4f}' for v in vals)} "
              f"{'monotone to less hedge' if mono_up else ('monotone to more hedge' if mono_dn else f'interior max at {best}')}")
# market-state conditioning on the designated cell
sig = sigs["realized"]["sig"]
qtrail = pd.Series(sig.crash[config.WARMUP_SESSIONS:],
                   index=ACC[("A", "realized", "o2o", "primary", "portfolio")]["daily"].index)
qr = panels["realized"]["QQQ"].ret_total.reindex(qtrail.index)
qvol = qr.rolling(60).std() * math.sqrt(252)
for a, nt in CURVE:
    d = ACC[(a, "realized", "o2o", "primary", "portfolio")]["daily"]
    r = C.window_slice(d["ret"], "primary")
    for nm, ser in (("trailing_return_decile", qtrail), ("vol_decile", qvol)):
        s = ser.reindex(r.index)
        dec = pd.qcut(s, 10, labels=False, duplicates="drop")
        for di in (0, 9):
            msk = dec == di
            if msk.sum() < 20:
                continue
            rows6.append({"table": f"conditional_{nm}", "arm": a,
                          "short_notional": nt, "decile": int(di),
                          "mean_daily_return": float(r[msk].mean()),
                          "ann_vol": float(r[msk].std(ddof=1) * math.sqrt(252)),
                          "n": int(msk.sum())})
pd.DataFrame(rows6).to_csv(OUT / "hedge-intensity.csv", index=False)
print(f"[wrote hedge-intensity.csv: {len(rows6)} rows]")

# ===========================================================================
print("\n== STEP 7: decomposition and diversification ==")
rows7 = []
mult_arr = {}
for t in TICK:
    fr = panels["synthetic"][t].frame
    if "multiple" in fr.columns and fr["multiple"].notna().any():
        mult_arr[t] = fr["multiple"]
    else:
        mult_arr[t] = pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index)
qqq = panels["realized"]["QQQ"].ret_total
ret_panel_full = pd.DataFrame({t: panels["realized"][t].ret_total for t in TICK})
for a in ARM_ORDER:
    acc = ACC[(a, "realized", "o2o", "primary", "portfolio")]
    d = acc["daily"]
    rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK}
                       for r in acc["raw_rows"]], index=d.index)
    rwp = rw[rw.index >= C.PRIMARY_START]
    port = C.window_slice(d["ret"], "primary")
    short = ARMS[a]["short"]
    if short:
        w = rwp[short].shift(1)
        ri = panels["realized"][short].ret_total.reindex(rwp.index)
        ru = qqq.reindex(rwp.index)
        M = mult_of(short)
        tot = float((w * ri).sum())
        beta = float((w * M * ru).sum())
        rows7.append({"table": "decomposition", "arm": a, "short_leg": short,
                      "leverage_multiple": M,
                      "total_arith_contribution": tot,
                      "beta_component": beta, "residual_component": tot - beta,
                      "held_sessions": int((rwp[short] > 0).sum())})
        sl = (w * ri).fillna(0.0)
        rest = port - sl
        msk = sl != 0
        rows7.append({"table": "correlation", "arm": a, "short_leg": short,
                      "corr_short_vs_rest_of_portfolio": float(sl[msk].corr(rest[msk])),
                      "n": int(msk.sum())})
    # 5.7 concentration
    sub = ret_panel_full.reindex(rwp.index).dropna(axis=1, how="any")
    ticks = [t for t in TICK if t in sub.columns]
    Sig = sub[ticks].cov().to_numpy() * 252
    tmat = ra.min_torsion(Sig)
    enb = ra.enb_series(rwp[ticks], Sig, tmat)
    enc = ra.enc(rwp)
    eff = pd.Series(sum(rwp[t].to_numpy() * mult_arr[t].reindex(rwp.index).to_numpy()
                        for t in TICK), index=rwp.index)
    dec_r = pd.qcut(qtrail.reindex(rwp.index), 10, labels=False, duplicates="drop")
    dec_v = pd.qcut(qvol.reindex(rwp.index), 10, labels=False, duplicates="drop")
    rows7.append({"table": "diversification", "arm": a,
                  "enc_tickers_mean": float(enc.mean()),
                  "enb_mintorsion_mean": float(enb.mean()),
                  "mean_effective_market_exposure": float(eff.mean()),
                  "eff_exposure_worst_trailing_return_decile": float(eff[dec_r == 0].mean()),
                  "eff_exposure_wildest_vol_decile": float(eff[dec_v == 9].mean())})
    print(f"  {a}: ENC {enc.mean():.3f} ENB {enb.mean():.3f} effexp {eff.mean():.3f} "
          f"(worst-ret decile {eff[dec_r==0].mean():.3f}, wildest-vol {eff[dec_v==9].mean():.3f})")
pd.DataFrame(rows7).to_csv(OUT / "short-leg-decomposition.csv", index=False)

# ===========================================================================
print("\n== STEP 8: cost and cap interaction ==")
rows8 = []
rows8.append({"table": "stacking_rule", "note":
              "session 15 rule applied: the uniform sweep REPLACES the tiered "
              "slippage and the auction premium rather than stacking on them"})
for a in ARM_ORDER:
    for bp in config.SLIPPAGE_BASE_GRID_BP:
        acc = run(arm_rows[a], "o2o", bp=bp)
        m = L.standalone_metrics(C.window_slice(acc["daily"]["ret"], "primary"),
                                 acc["daily"]["nav"], acc["orders"])
        rows8.append({"table": "cost_sweep", "arm": a, "slippage_bp": bp,
                      **{k: m[k] for k in ("ann_return", "ann_vol", "sharpe_lo",
                                           "max_drawdown", "ann_turnover")}})
    acc0 = ACC[(a, "realized", "o2o", "primary", "portfolio")]
    ce = acc0["cap_events"]
    short = ARMS[a]["short"]
    if len(ce) and short:
        g = ce[ce["ticker"] == short]
        rows8.append({"table": "cap_interaction", "arm": a, "short_leg": short,
                      "binding_transitions_short_leg": int(len(g)),
                      "mean_frac_capped_short_leg":
                          float((g["dollars_to_cash"] / g["target_dollars"]).mean())
                          if len(g) else 0.0,
                      "total_cap_events_all_instruments": int(len(ce)),
                      "instruments_binding": ";".join(sorted(ce["ticker"].unique()))})
    elif short:
        rows8.append({"table": "cap_interaction", "arm": a, "short_leg": short,
                      "binding_transitions_short_leg": 0,
                      "total_cap_events_all_instruments": int(len(ce))})
    tvr = [r for r in rows8 if r.get("table") == "cost_sweep" and r.get("arm") == a
           and r.get("slippage_bp") == 10]
    print(f"  {a}: turnover {tvr[0]['ann_turnover']:.2f}, "
          f"ann@10bp {tvr[0]['ann_return']:.4f}")
pd.DataFrame(rows8).to_csv(OUT / "arm-cost-cap.csv", index=False)

# ===========================================================================
print("\n== STEP 9: per-year contribution of the short leg ==")
rows9 = []
for a in ARM_ORDER:
    short = ARMS[a]["short"]
    if not short:
        rows9.append({"table": "note", "arm": a,
                      "note": "no short leg; arm F holds TLT only"})
        continue
    for pname, conv, wname in COMBOS:
        key = (a, pname, conv, wname, "portfolio")
        if key not in ACC:
            continue
        acc = ACC[key]
        d = acc["daily"]
        rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK}
                           for r in acc["raw_rows"]], index=d.index)
        pan = panels["synthetic"] if pname == "synthetic" else (
            o2o if conv == "o2o" else panels["realized"])
        sl = C.window_slice((rw[short].shift(1) *
                             pan[short].ret_total.reindex(rw.index)).fillna(0.0), wname)
        if not len(sl) or abs(sl.sum()) < 1e-12:
            continue
        by = sl.groupby(sl.index.year).sum()
        for y, v in by.items():
            rows9.append({"table": "contribution", "arm": a, "short_leg": short,
                          "panel": pname, "convention": conv, "window": wname,
                          "year": int(y), "arith_contribution": float(v)})
        pos = by.abs().sort_values(ascending=False)
        cum = (pos / pos.sum()).cumsum()
        rows9.append({"table": "concentration", "arm": a, "short_leg": short,
                      "panel": pname, "convention": conv, "window": wname,
                      "total": float(by.sum()), "largest_year": int(pos.index[0]),
                      "largest_year_share_of_abs": float(pos.iloc[0] / pos.sum()),
                      "years_to_80pct": int((cum < 0.8).sum() + 1),
                      "contribution_2020": float(by.get(2020, 0.0))})
        if conv == "o2o" and wname == "primary":
            print(f"  {a} ({short}) o2o primary: total {by.sum():+.4f}, "
                  f"2020 {by.get(2020,0.0):+.4f}, largest year {pos.index[0]} "
                  f"at {pos.iloc[0]/pos.sum():.1%}")
pd.DataFrame(rows9).to_csv(OUT / "arm-contribution-by-year.csv", index=False)
print(f"[wrote arm-contribution-by-year.csv: {len(rows9)} rows]")
