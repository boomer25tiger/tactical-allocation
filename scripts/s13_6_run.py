"""Session 13.6 — steps 1 (verify), 3, 4, 5, 6, 7.

Binding order: the split decode and its positive controls run before any
downstream arm. Writes only under outputs/session-13.6/.
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
from src.portfolio import SLEEVE_ORDER, sleeve_label

OUT = ROOT / "outputs" / "session-13.6"
OUT.mkdir(parents=True, exist_ok=True)
ANCHOR = 10
EXT = (60, 75, 100, 150)
pd.set_option("display.width", 250)


def wcsv(name, rows):
    pd.DataFrame(rows).to_csv(OUT / name, index=False)
    print(f"[wrote {name}: {len(rows)} rows]")


# ===========================================================================
print("== STEP 3: split decode and positive controls (before anything else) ==")
panels = {a: bt.load_arm_panel(a) for a in ("synthetic", "realized")}
for a, p in panels.items():
    ok, mx = bt.assert_holdout(p)
    print(f"holdout [{a}]: PASS max {mx.date()}")
cal = panels["synthetic"]["SPY"].index
W = config.WARMUP_SESSIONS
years_traded = (len(cal) - W) / 252.0

rows3 = []
# control 1: four funds against independently known trading levels
KNOWN = [
    ("TQQQ", "2021-07-30", 120.0, "forward splitter (2:1 x4, 3:1); traded ~$120 late Jul 2021"),
    ("SOXL", "2021-03-15", 40.0, "forward splitter (15:1 Mar 2021); traded ~$40 after it"),
    ("UVXY", "2021-06-15", 27.0, "reverse splitter (x10); traded ~$25-30 after May 2021 1:10"),
    ("SQQQ", "2021-07-30", 9.5, "reverse splitter; traded ~$9-10 summer 2021"),
]
TOL = 0.35
for t, ds, known, note in KNOWN:
    fr = panels["realized"][t].frame if t in ("TQQQ", "SOXL", "UVXY", "SQQQ") else None
    px = panels["realized"][t].raw_close
    d_ = px.index[px.index >= ds][0]
    rec = float(px.loc[d_])
    ok = abs(rec / known - 1) <= TOL
    rows3.append({"table": "known_level_control", "ticker": t, "date": str(d_.date()),
                  "known_level": known, "reconstructed": round(rec, 2),
                  "rel_gap": rec / known - 1, "tolerance": TOL,
                  "result": "PASS" if ok else "FAIL", "note": note})
    print(f"  {t} {d_.date()}: reconstructed {rec:.2f} vs known ~{known} "
          f"({rec/known-1:+.1%}) {'PASS' if ok else 'FAIL'}")
    assert ok, f"known-level control failed for {t}"

# control 2: return consistency, every fund every session. Frames are
# rebuilt directly (pre-2.5a-lag) so the lagged RYMFX panel frame does not
# misalign the comparison; the panel's lag shifts all columns together and
# does not alter the decode itself.
bad_funds = []
for t in list(bt.LEVERED) + list(bt.UNLEVERED):
    fr = bt._frozen_frame(t).frame
    close_adj = bt._load_raw(t)["Close"].astype(float)
    at = fr["close"].dropna()
    if len(at) < 2:
        continue
    ca = close_adj.reindex(at.index)
    ratio_eff = bt._load_raw(t)["Stock Splits"].astype(float).fillna(0.0).replace(0.0, 1.0).reindex(at.index)
    lhs = (at / at.shift(1)) * ratio_eff
    rhs = ca / ca.shift(1)
    gap = (lhs - rhs).abs().max()
    if not (gap < 1e-9 or math.isnan(gap)):
        bad_funds.append((t, gap))
rows3.append({"table": "return_consistency", "ticker": "ALL",
              "result": "PASS" if not bad_funds else f"FAIL {bad_funds}",
              "note": "as-traded return x in-window split ratio == adjusted return, "
                      "max abs gap < 1e-9 per fund per session"})
assert not bad_funds, f"return consistency failed: {bad_funds}"
print("  return-consistency control: PASS (all funds, all sessions)")

# per-fund ratio of reconstructed first in-window listed price to old anchor 100
for t in bt.LEVERED:
    px = panels["synthetic"][t].raw_close.dropna()
    fr_real = bt._load_raw(t)
    first_listed = fr_real.index.min()
    listed_px = px.loc[px.index >= first_listed]
    p0 = float(listed_px.iloc[0]) if len(listed_px) else np.nan
    rows3.append({"table": "anchor_error", "ticker": t,
                  "first_listed_in_window": str(first_listed.date()),
                  "reconstructed_first_price": round(p0, 4),
                  "ratio_to_old_100_anchor": round(p0 / 100.0, 4)})
# UVXY yearly path
pxu = panels["synthetic"]["UVXY"].raw_close
for y, g in pxu.groupby(pxu.index.year):
    rows3.append({"table": "uvxy_path", "year": int(y), "px_min": float(g.min()),
                  "px_median": float(g.median()), "px_max": float(g.max())})
# pre-listing convention
for t in bt.LEVERED:
    first_listed = bt._load_raw(t).index.min()
    if first_listed > cal[0]:
        rows3.append({"table": "prelisting_convention", "ticker": t,
                      "range": f"{cal[0].date()}..{(first_listed - pd.Timedelta(days=1)).date()}",
                      "note": "back-extended from first listed as-traded price with "
                              "synthetic returns; no listing price exists to anchor"})
wcsv("split-decode.csv", rows3)

# ===========================================================================
print("\n== STEP 1 verify: S3 occupancy identical after D1 refactor ==")
sigs = {}
for a in ("synthetic", "realized"):
    s = bt.ArmSignals(panels[a], cal)
    sigs[a] = {"sig": s, **bt.run_signals(s)}
occ_after = {}
for r in sigs["synthetic"]["rows"]:
    s_ = sleeve_label(r["sleeves"]["S3"])
    occ_after[s_] = occ_after.get(s_, 0) + 1
before = json.load(open(OUT / "_s3_occupancy_before.json"))
assert occ_after == before["occupancy"], \
    f"D1 refactor changed S3 behaviour: {before['occupancy']} -> {occ_after}"
print(f"  S3_VOTE_THRESHOLD = {config.S3_VOTE_THRESHOLD}; occupancy after refactor "
      f"identical on all {before['n_sessions']} sessions: PASS")

# ===========================================================================
print("\n== STEP 4: canonical result under corrected prices ==")
srows = {a: sigs[a]["rows"] for a in sigs}
accs: dict = {"synthetic": {}, "realized": {}}
rows4 = []
old = pd.read_csv(ROOT / "outputs" / "session-13" / "headline-results.csv")
for a in ("synthetic", "realized"):
    for bp in list(config.SLIPPAGE_BASE_GRID_BP) + list(EXT):
        acc = bt.run_account(sigs[a]["sig"], panels[a], srows[a], bp)
        accs[a][bp] = acc
        m = bt.headline_metrics(acc["daily"], acc["orders"])
        row = {"table": "headline_corrected", "arm": a, "slippage_bp": bp,
               "in_registered_grid": bp in config.SLIPPAGE_BASE_GRID_BP, **{
                   k: m[k] for k in ("total_return", "ann_return", "ann_vol",
                                     "sharpe_naive", "sharpe_lo", "max_drawdown",
                                     "calmar", "ann_turnover_one_sided")}}
        o = old[(old.arm == a) & (old.slippage_bp == bp)]
        if len(o):
            for k in ("total_return", "ann_return", "ann_vol", "sharpe_naive",
                      "sharpe_lo", "max_drawdown", "calmar"):
                row[f"delta_vs_s13_{k}"] = m[k] - float(o.iloc[0][k])
        rows4.append(row)
    print(f"  [{a}] done")

def crossing(pts, col):
    d = pd.DataFrame(pts).sort_values("slippage_bp")
    x, y = d["slippage_bp"].to_numpy(float), d[col].to_numpy()
    for i in range(len(x) - 1):
        if y[i] > 0 >= y[i + 1]:
            return x[i] + (x[i + 1] - x[i]) * y[i] / (y[i] - y[i + 1])
    return np.nan

for a in ("synthetic", "realized"):
    pts = [r for r in rows4 if r.get("arm") == a and r["table"] == "headline_corrected"]
    for col in ("ann_return", "sharpe_lo"):
        rows4.append({"table": "crossings_corrected", "arm": a, "metric": col,
                      "measured_bp": crossing(pts, col)})

# commission diagnostics at the anchor, corrected prices
orders = accs["synthetic"][ANCHOR]["orders"]
d10 = accs["synthetic"][ANCHOR]["daily"]
nav = d10["nav"]
orders["min_bound"] = (np.isclose(orders["commission"], bt.COMMISSION_MINIMUM)
                       & (bt.COMMISSION_PER_SHARE * orders["shares"] < bt.COMMISSION_MINIMUM))
orders["cap_bound"] = np.isclose(orders["commission"],
                                 bt.COMMISSION_CAP_FRAC * orders["value"])
comm_bp = orders["commission"].sum() / orders["value"].sum() * 1e4
comm_drag = orders["commission"].sum() / nav.mean() / years_traded
rows4.append({"table": "commission", "metric": "portfolio_bp_of_traded", "value": comm_bp})
rows4.append({"table": "commission", "metric": "annualised_drag_pp", "value": comm_drag * 100})
rows4.append({"table": "commission", "metric": "frac_orders_min_bound",
              "value": float(orders["min_bound"].mean())})
rows4.append({"table": "commission", "metric": "frac_orders_cap_bound",
              "value": float(orders["cap_bound"].mean())})
for t, g in orders.groupby("ticker"):
    rows4.append({"table": "commission_by_instrument", "ticker": t,
                  "bp_of_traded": g["commission"].sum() / g["value"].sum() * 1e4,
                  "frac_min_bound": float(g["min_bound"].mean()),
                  "frac_cap_bound": float(g["cap_bound"].mean()),
                  "n_orders": len(g)})
print(f"  commission: {comm_bp:.2f} bp of traded, {comm_drag*100:.3f} pp/yr drag, "
      f"min {orders['min_bound'].mean():.1%}, cap {orders['cap_bound'].mean():.2%}")

# truncation residual + forgone under corrected prices (13.5 method)
raw10 = {t: panels["synthetic"][t].raw_close.reindex(cal).to_numpy()
         for t in ra.TARGET_TICKERS}
by_i = {r["i"]: r for r in srows["synthetic"]}
cost_by_date = orders.groupby("date").apply(lambda g: g["commission"].sum() + g["slippage"].sum())
fill_dates = d10.index[d10["transition"]]
resid_by_fill = {}
tot_resid = 0.0
for f in fill_dates:
    i_f = cal.get_indexer([f])[0]
    sr_ = by_i.get(i_f - 1)
    if sr_ is None or not sr_["changed"]:
        continue
    nav_pre = float(d10.loc[f, "nav"]) + float(cost_by_date.get(f, 0.0))
    tot = 0.0
    for t, w_ in sr_["targets"].items():
        px = raw10[t][i_f]
        if math.isnan(px) or px <= 0:
            continue
        alloc = nav_pre * w_
        tot += alloc - math.trunc(alloc / px) * px
    resid_by_fill[f] = tot
    tot_resid += tot
rfs10 = bt.rf_per_session(d10.index).fillna(0.0)
holds = list(fill_dates) + [d10.index[-1]]
forgone = 0.0
for a_, b_ in zip(holds[:-1], holds[1:]):
    seg = d10["ret"].loc[a_:b_].iloc[1:]
    rf_seg = rfs10.loc[a_:b_].iloc[1:]
    forgone += resid_by_fill.get(a_, 0.0) * float((1 + seg).prod() - (1 + rf_seg).prod())
rows4.append({"table": "truncation", "metric": "cumulative_residual_dollars", "value": tot_resid})
rows4.append({"table": "truncation", "metric": "forgone_dollars", "value": forgone})
rows4.append({"table": "truncation", "metric": "forgone_bp_per_year",
              "value": forgone / nav.mean() / years_traded * 1e4})
print(f"  truncation residual ${tot_resid:,.0f}; forgone ${forgone:,.0f} "
      f"({forgone/nav.mean()/years_traded*1e4:.2f} bp/yr)")
wcsv("headline-corrected.csv", rows4)

# ===========================================================================
print("\n== STEP 5: lag curve on the realized arm, matched 2012+ window ==")
rows5 = []
CUT = pd.Timestamp("2012-01-01")

def sliced_metrics(daily):
    r_ = daily["ret"][daily.index >= CUT].dropna()
    rf_ = bt.rf_per_session(daily.index)[daily.index >= CUT]
    n = len(r_)
    navseg = (1 + r_).cumprod()
    ex = (r_ - rf_).dropna()
    return {"ann_return": float(navseg.iloc[-1] ** (252 / n) - 1),
            "ann_vol": float(r_.std(ddof=1) * math.sqrt(252)),
            "sharpe_naive": float(ex.mean() / ex.std(ddof=1) * math.sqrt(252)),
            "sharpe_lo": bt.lo_sharpe(ex),
            "max_drawdown": float((navseg / navseg.cummax() - 1).min())}

lagres = {}
for a in ("synthetic", "realized"):
    for lag in range(1, 6):
        for bp in (0, ANCHOR):
            acc = (accs[a][bp] if lag == 1 and bp in accs[a] else
                   bt.run_account(sigs[a]["sig"], panels[a], srows[a], bp, fill_lag=lag))
            m = sliced_metrics(acc["daily"])
            lagres[(a, lag, bp)] = m
            rows5.append({"table": "lag_curve_2012on", "arm": a, "lag": lag, "bp": bp, **m})
            if lag == 1 and bp == 0:
                lag1_acc = acc
    print(f"  [{a}] lag curve done")
for a in ("synthetic", "realized"):
    for bp in (0, ANCHOR):
        v = {lag: lagres[(a, lag, bp)]["ann_return"] for lag in range(1, 6)}
        s = {lag: lagres[(a, lag, bp)]["sharpe_lo"] for lag in range(1, 6)}
        rows5.append({"table": "lag_peaks_2012on", "arm": a, "bp": bp,
                      "ann_return_by_lag": "; ".join(f"T+{k}={x:.4f}" for k, x in v.items()),
                      "sharpe_lo_by_lag": "; ".join(f"T+{k}={x:.4f}" for k, x in s.items()),
                      "ann_peak_lag": max(v, key=lambda k: v[k]),
                      "sharpe_lo_peak_lag": max(s, key=lambda k: s[k])})

# entry effect by sleeve/state, both arms, matched window (0 bp paths)
for a in ("synthetic", "realized"):
    acc0 = accs[a][0]
    dl = acc0["daily"]
    msk = dl.index >= CUT
    r_ = dl["ret"]
    fh = dl["transition"].shift(1).fillna(False).astype(bool)
    rows5.append({"table": "entry_effect_2012on", "arm": a, "group": "PORTFOLIO",
                  "first_day_mean": float(r_[fh & msk].mean()),
                  "uncond_mean": float(r_[msk].mean()),
                  "n_first": int((fh & msk).sum())})
    ret_a = {t: panels[a][t].ret_total.reindex(cal).to_numpy() for t in ra.TARGET_TICKERS}
    lab_sig_a = pd.Series({cal[r["i"]]: r["label"] for r in srows[a]})
    for k in SLEEVE_ORDER:
        st_sig = pd.Series({cal[r["i"]]: sleeve_label(r["sleeves"][k]) for r in srows[a]})
        dicts = {cal[r["i"]]: r["sleeves"][k] for r in srows[a]}
        dates_sig = pd.Series(st_sig.index, index=st_sig.index).reindex(dl.index).shift(2)
        vals = np.zeros(len(dl))
        for j in range(len(dl)):
            ds = dates_sig.iloc[j]
            if pd.isna(ds):
                continue
            wd = dicts.get(ds)
            if not wd:
                continue
            i_t = W + j
            vals[j] = sum(wv * ret_a[x][i_t] for x, wv in wd.items()
                          if not math.isnan(ret_a[x][i_t]))
        sret = pd.Series(vals, index=dl.index)
        changed = (st_sig != st_sig.shift(1))
        changed.iloc[0] = True
        fh_idx = [cal.get_indexer([d])[0] + 2 for d in st_sig.index[changed.to_numpy()]]
        fh_dates = [cal[i] for i in fh_idx if i < len(cal)]
        fhk = pd.Series(False, index=dl.index)
        fhk.loc[[d for d in fh_dates if d in fhk.index]] = True
        ent_state = pd.Series({cal[i]: st_sig.iloc[jj] for jj, i in
                               enumerate(np.array(fh_idx)[changed[changed].index.argsort().argsort()])
                               if i < len(cal)}) if False else \
            pd.Series({cal[i]: st_sig.loc[d] for d, i in
                       zip(st_sig.index[changed.to_numpy()], fh_idx) if i < len(cal)})
        cont = (~fhk) & (sret != 0)
        rows5.append({"table": "entry_effect_2012on", "arm": a, "group": k,
                      "first_day_mean": float(sret[fhk & msk].mean()),
                      "continuing_mean": float(sret[cont & msk].mean()),
                      "n_first": int((fhk & msk).sum())})
        for state in st_sig.value_counts().head(5).index:
            fhs = fhk & (ent_state.reindex(dl.index) == state) & msk
            cts = cont & (pd.Series(st_sig.reindex(dl.index).shift(2)) == state) & msk
            if fhs.sum() >= 10:
                rows5.append({"table": "entry_effect_state_2012on", "arm": a,
                              "group": f"{k}:{state}",
                              "first_day_mean": float(sret[fhs].mean()),
                              "continuing_mean": float(sret[cts].mean()),
                              "n_first": int(fhs.sum())})
# verdict
sy = lagres[("synthetic", 2, 0)]["ann_return"] - lagres[("synthetic", 1, 0)]["ann_return"]
re_ = lagres[("realized", 2, 0)]["ann_return"] - lagres[("realized", 1, 0)]["ann_return"]
verdict = ("signal_property" if re_ > 0.02 else
           "construction_defect" if sy > 0.02 and re_ <= 0.005 else "mixed")
rows5.append({"table": "verdict", "synthetic_T2_minus_T1_ann_2012on": sy,
              "realized_T2_minus_T1_ann_2012on": re_, "verdict": verdict})
print(f"  T+2 minus T+1 ann (2012+, 0bp): synthetic {sy:+.4f}, realized {re_:+.4f} "
      f"-> {verdict}")
wcsv("lag-realized.csv", rows5)

# ===========================================================================
print("\n== STEP 6: open-to-open arm (realized panel, 2012+ reporting) ==")
rows6 = []
o2o_frames = {}
for t, tf in panels["realized"].frames.items():
    fr = tf.frame.copy()
    ao = fr["adj_open"]
    fr["ret_total"] = ao / ao.shift(1) - 1.0
    fr["close"] = fr["open"]          # as-traded open for sizing/commission
    o2o_frames[t] = TickerFrame(t, fr)
o2o_panel = bt.Panel()
o2o_panel.frames = o2o_frames
o2o_panel._lagged = {config.TREND_SIGNAL_SERIES}
for bp in config.SLIPPAGE_BASE_GRID_BP:
    acc_o = bt.run_account(sigs["realized"]["sig"], o2o_panel, srows["realized"], bp)
    mo = sliced_metrics(acc_o["daily"])
    mc = sliced_metrics(accs["realized"][bp]["daily"])
    rows6.append({"table": "open_to_open_2012on", "bp": bp, **{f"o2o_{k}": v for k, v in mo.items()},
                  **{f"c2c_{k}": v for k, v in mc.items()},
                  "delta_ann_return": mo["ann_return"] - mc["ann_return"],
                  "delta_sharpe_lo": mo["sharpe_lo"] - mc["sharpe_lo"]})
    if bp == ANCHOR:
        acc_o_anchor = acc_o
print("  o2o vs c2c at anchor (2012+): ann "
      f"{[r for r in rows6 if r['bp']==ANCHOR][0]['o2o_ann_return']:.4f} vs "
      f"{[r for r in rows6 if r['bp']==ANCHOR][0]['c2c_ann_return']:.4f}")
# leverage deviation by trailing-vol decile
UND = {"TQQQ": ("QQQ", 3), "SQQQ": ("QQQ", -3), "QLD": ("QQQ", 2), "PSQ": ("QQQ", -1),
       "SPXL": ("SPY", 3), "TECL": ("XLK", 3), "TECS": ("XLK", -3),
       "SOXL": ("SOXX", 3), "SOXS": ("SOXX", -3), "LABU": ("XBI", 3)}
extra = {u: bt._frozen_frame(u) for u in ("SOXX", "XBI")}
def o2o_ret(tf):
    ao = tf.frame["adj_open"]
    return (ao / ao.shift(1) - 1.0).reindex(cal)
und_ret = {}
for u in ("QQQ", "SPY", "XLK"):
    und_ret[u] = o2o_ret(panels["realized"][u])
for u in ("SOXX", "XBI"):
    und_ret[u] = o2o_ret(extra[u])
rw_o = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                     for r in acc_o_anchor["raw_rows"]], index=acc_o_anchor["daily"].index)
devs = []
for t, (u, M) in UND.items():
    held = rw_o[t].shift(1) > 0
    held = held[held.index >= CUT]
    if held.sum() < 20:
        continue
    rf_ = o2o_ret(o2o_frames[t]).reindex(rw_o.index)
    wait = o2o_frames[t].frame["ret_total"].reindex(rw_o.index)
    ru = und_ret[u].reindex(rw_o.index)
    vol = ru.rolling(60).std() * math.sqrt(252)
    dd_ = pd.DataFrame({"dev": (wait - M * ru).abs(), "vol": vol})
    dd_ = dd_[held.reindex(dd_.index).fillna(False)]
    devs.append(dd_.assign(ticker=t))
alldev = pd.concat(devs)
dec = pd.qcut(alldev["vol"], 10, labels=False, duplicates="drop")
for di in sorted(dec.dropna().unique()):
    g = alldev[dec == di]
    rows6.append({"table": "leverage_deviation", "vol_decile": int(di),
                  "mean_abs_dev_daily": float(g["dev"].mean()),
                  "p95_abs_dev_daily": float(g["dev"].quantile(.95)),
                  "n": len(g),
                  "note": "UVXY/SVXY excluded: no VX open series exists in the panel"})
print("  leverage deviation by vol decile computed "
      f"(D1 {rows6[-10]['mean_abs_dev_daily']:.5f} -> D10 {rows6[-1]['mean_abs_dev_daily']:.5f})")
wcsv("open-to-open.csv", rows6)

# ===========================================================================
print("\n== STEP 7: volatility-overlay ablation (post-hoc, 2026-08-18, 9.10) ==")
rows7 = []
UVXY_STATES = ["T10:100%UVXY (overbought cascade)",
               "T11:100%UVXY (tier two)",
               "T11:33%UVXY+33%BIL+33%BTAL (tier one, UVXY slice only)",
               "S2:100%UVXY (gate overbought)",
               "S3:100%UVXY (bull overbought; UVIX availability switch resolves to UVXY)"]
for s_ in UVXY_STATES:
    rows7.append({"table": "armA_affected_states", "state": s_})
INVERSE = {"SQQQ", "PSQ", "SH", "TECS", "SOXS"}
rows7.append({"table": "armB_scope", "note": "SQQQ, PSQ, TECS, SOXS are held targets; "
              "SH is never a target (signal side of AGG>SH only) — removal is a no-op for SH"})

def ablate(rows_in, remove: set):
    out = []
    for r in rows_in:
        r2 = dict(r)
        if r["targets"] is not None:
            r2["targets"] = {t: w for t, w in r["targets"].items() if t not in remove}
        out.append(r2)
    return out

mult_cache = {}
for t in ra.TARGET_TICKERS:
    fr = panels["synthetic"][t].frame
    if "multiple" in fr.columns and fr["multiple"].notna().any():
        mult_cache[t] = fr["multiple"].reindex(cal[W:]).to_numpy()
    else:
        mult_cache[t] = np.zeros(len(cal) - W) if t == "BTAL" else np.ones(len(cal) - W)

def eff_mean(acc):
    rw_ = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                        for r in acc["raw_rows"]])
    v = np.zeros(len(rw_))
    for t in ra.TARGET_TICKERS:
        v += rw_[t].to_numpy() * mult_cache[t]
    return float(np.mean(v))

for arm_name, remove in (("A_no_UVXY", {"UVXY"}), ("B_no_inverse_equity", INVERSE)):
    for pa in ("synthetic", "realized"):
        rows_ab = ablate(srows[pa], remove)
        acc_ab = bt.run_account(sigs[pa]["sig"], panels[pa], rows_ab, ANCHOR)
        m_ab = bt.headline_metrics(acc_ab["daily"], acc_ab["orders"])
        m_base = bt.headline_metrics(accs[pa][ANCHOR]["daily"], accs[pa][ANCHOR]["orders"])
        rows7.append({"table": "ablation_headline_anchor", "ablation": arm_name,
                      "panel": pa, **{k: m_ab[k] for k in
                      ("ann_return", "ann_vol", "sharpe_naive", "sharpe_lo",
                       "max_drawdown", "calmar", "ann_turnover_one_sided")},
                      **{f"delta_{k}": m_ab[k] - m_base[k] for k in
                         ("ann_return", "sharpe_lo", "max_drawdown")},
                      "delta_mean_eff_exposure": eff_mean(acc_ab) - eff_mean(accs[pa][ANCHOR])})
        r_ab = acc_ab["daily"]["ret"].dropna()
        r_b = accs[pa][ANCHOR]["daily"]["ret"].dropna()
        for y in sorted(set(r_ab.index.year)):
            ya = float((1 + r_ab[r_ab.index.year == y]).prod() - 1)
            yb = float((1 + r_b[r_b.index.year == y]).prod() - 1)
            rows7.append({"table": "ablation_yearly", "ablation": arm_name, "panel": pa,
                          "year": int(y), "ablated_return": ya, "base_return": yb,
                          "difference": ya - yb})
        print(f"  {arm_name} [{pa}]: ann {m_ab['ann_return']:.4f} "
              f"(base {m_base['ann_return']:.4f}), SR_lo {m_ab['sharpe_lo']:.3f} "
              f"(base {m_base['sharpe_lo']:.3f})")
wcsv("ablation.csv", rows7)
print("\nDONE steps 1v, 3, 4, 5, 6, 7")
