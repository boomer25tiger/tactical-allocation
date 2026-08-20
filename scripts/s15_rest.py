"""Session 15 steps 5, 6, 7, 8."""
from __future__ import annotations

import math
import sys
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
from src.portfolio import SLEEVE_ORDER

import os as _os
OUT = ROOT / "outputs" / (_os.environ.get("S20_OUTDIR") or "session-15")
OUT.mkdir(parents=True, exist_ok=True)
env = L.build_env()
cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]
TICK = list(ra.TARGET_TICKERS)


def run(rows, panel, sig, conv, cap=True, lag=1, capfn=None):
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    return bt.run_account(sig["sig"], panel, rows, C.ANCHOR, fill_lag=lag,
                          commission_fn=C.ARMS[C.CANONICAL_ARM], slip_fn=sf,
                          cap_fn=(capfn if capfn is not None else cap_fn) if cap else None)


def weights_of(acc):
    return pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK}
                         for r in acc["raw_rows"]], index=acc["daily"].index)


def contrib_frame(acc, panel):
    rw = weights_of(acc).shift(1)
    out = {}
    for t in TICK:
        r = panel[t].ret_total.reindex(rw.index)
        out[t] = (rw[t] * r).fillna(0.0)
    return pd.DataFrame(out, index=rw.index)


# ===========================================================================
print("== STEP 5: per-instrument per-year contribution ==")
rows5 = []
for conv in ("c2c", "o2o"):
    panel = o2o if conv == "o2o" else panels["realized"]
    sig = sigs["realized"]
    for arm, capflag in (("capped", True), ("uncapped", False)):
        acc = run(sig["rows"], panel, sig, conv, cap=capflag)
        cf = contrib_frame(acc, panel)
        for wname in ("full", "primary", "early"):
            sl = C.window_slice(cf, wname) if wname != "full" else cf
            if wname == "primary":
                sl = cf[cf.index >= C.PRIMARY_START]
            elif wname == "early":
                sl = cf[cf.index <= C.EARLY_END]
            if not len(sl):
                continue
            for t in TICK:
                tot = float(sl[t].sum())
                if abs(tot) < 1e-9:
                    continue
                by_year = sl[t].groupby(sl.index.year).sum()
                for y, v in by_year.items():
                    rows5.append({"table": "contribution", "convention": conv,
                                  "cap_arm": arm, "window": wname, "instrument": t,
                                  "year": int(y), "arith_contribution": float(v)})
                pos = by_year.abs().sort_values(ascending=False)
                share_top = float(pos.iloc[0] / pos.sum()) if pos.sum() > 0 else np.nan
                cum = (pos / pos.sum()).cumsum()
                n80 = int((cum < 0.8).sum() + 1)
                rows5.append({"table": "concentration", "convention": conv,
                              "cap_arm": arm, "window": wname, "instrument": t,
                              "total_arith_contribution": tot,
                              "largest_year": int(pos.index[0]),
                              "largest_year_share_of_abs": share_top,
                              "years_to_80pct_of_abs": n80,
                              "n_years": int(len(by_year))})
        print(f"  [{conv} {arm}] contributions done")

# strategy and sleeve concentration on the same basis
for conv in ("c2c", "o2o"):
    panel = o2o if conv == "o2o" else panels["realized"]
    sig = sigs["realized"]
    acc = run(sig["rows"], panel, sig, conv)
    r = C.window_slice(acc["daily"]["ret"], "primary")
    by_year = r.groupby(r.index.year).sum()
    pos = by_year.abs().sort_values(ascending=False)
    cum = (pos / pos.sum()).cumsum()
    rows5.append({"table": "concentration", "convention": conv, "cap_arm": "capped",
                  "window": "primary", "instrument": "STRATEGY_TOTAL",
                  "total_arith_contribution": float(by_year.sum()),
                  "largest_year": int(pos.index[0]),
                  "largest_year_share_of_abs": float(pos.iloc[0] / pos.sum()),
                  "years_to_80pct_of_abs": int((cum < 0.8).sum() + 1),
                  "n_years": int(len(by_year))})
    for k in SLEEVE_ORDER:
        rws = L.make_lines(cal)[f"sleeve_{k}_standalone"][0](panel, sig["rows"], 0)
        acck = run(rws, panel, sig, conv)
        rk = C.window_slice(acck["daily"]["ret"], "primary")
        byk = rk.groupby(rk.index.year).sum()
        posk = byk.abs().sort_values(ascending=False)
        cumk = (posk / posk.sum()).cumsum()
        rows5.append({"table": "concentration", "convention": conv, "cap_arm": "capped",
                      "window": "primary", "instrument": f"SLEEVE_{k}",
                      "total_arith_contribution": float(byk.sum()),
                      "largest_year": int(posk.index[0]),
                      "largest_year_share_of_abs": float(posk.iloc[0] / posk.sum()),
                      "years_to_80pct_of_abs": int((cumk < 0.8).sum() + 1),
                      "n_years": int(len(byk))})

btal = [r for r in rows5 if r["table"] == "concentration"
        and r["instrument"] == "BTAL" and r["cap_arm"] == "capped"
        and r["window"] == "primary" and r["convention"] == "o2o"]
if btal:
    b = btal[0]
    rows5.append({"table": "btal_verdict",
                  "largest_year": b["largest_year"],
                  "largest_year_share_of_abs": b["largest_year_share_of_abs"],
                  "years_to_80pct": b["years_to_80pct_of_abs"],
                  "note": "capped BTAL contribution concentration on the designated "
                          "cell's convention and window"})
    print(f"  BTAL capped: largest year {b['largest_year']} carries "
          f"{b['largest_year_share_of_abs']:.1%} of absolute contribution")
pd.DataFrame(rows5).to_csv(OUT / "contribution-by-year.csv", index=False)
print(f"[wrote contribution-by-year.csv: {len(rows5)} rows]")

# ===========================================================================
print("\n== STEP 6: NAV sweep ==")
rows6 = []
NAVS = [100_000, 250_000, 1_000_000, 5_000_000, 25_000_000]
raw_px = {t: panels["realized"][t].raw_close.reindex(cal).to_numpy() for t in TICK}
base_nav = bt.START_NAV
try:
    for nav0 in NAVS:
        bt.START_NAV = float(nav0)
        for conv in ("c2c", "o2o"):
            panel = o2o if conv == "o2o" else panels["realized"]
            sig = sigs["realized"]
            acc = run(sig["rows"], panel, sig, conv)
            m = L.standalone_metrics(C.window_slice(acc["daily"]["ret"], "primary"),
                                     acc["daily"]["nav"], acc["orders"])
            rows6.append({"table": "cell", "nav": nav0, "convention": conv,
                          "window": "primary", "canonical": nav0 == 1_000_000,
                          **{k: m[k] for k in ("ann_return", "ann_vol", "sharpe_lo",
                                               "max_drawdown", "ann_turnover")}})
            if conv != "o2o":
                continue
            # channel 1: integer truncation, recomputed as the engine sizes
            od = acc["orders"]
            ce = acc["cap_events"]
            daily = acc["daily"]
            cost_by_date = od.groupby("date").apply(
                lambda g: g["commission"].sum() + g["slippage"].sum()) if len(od) else pd.Series(dtype=float)
            cur = {}
            tgt_dollars = trunc_lost = 0.0
            capd = float(ce["dollars_to_cash"].sum()) if len(ce) else 0.0
            by_i = {r["i"]: r for r in sig["rows"]}
            for d in daily.index[daily["transition"]]:
                i_f = int(np.searchsorted(cal.to_numpy(), np.datetime64(d)))
                sr = by_i.get(i_f - 1)
                if sr is None or not sr["changed"] or sr["targets"] is None:
                    continue
                navp = float(daily.loc[d, "nav"]) + float(cost_by_date.get(d, 0.0))
                for t, w in sr["targets"].items():
                    px = raw_px[t][i_f]
                    if math.isnan(px) or px <= 0:
                        continue
                    alloc = navp * w
                    lim = cap_fn(i_f, t)
                    if lim is not None and lim < alloc:
                        alloc = lim
                    tgt_dollars += navp * w
                    trunc_lost += alloc - math.trunc(alloc / px) * px
            minbind = float(((np.isclose(od["commission"], config.COMMISSION_F_MINIMUM)) &
                             (config.COMMISSION_F_PER_SHARE * od["shares"] <
                              config.COMMISSION_F_MINIMUM)).mean()) if len(od) else 0.0
            caps = sorted(ce["ticker"].unique()) if len(ce) else []
            rows6.append({"table": "channels", "nav": nav0, "convention": conv,
                          "truncation_frac_of_target_dollars":
                              trunc_lost / tgt_dollars if tgt_dollars else np.nan,
                          "commission_min_bind_frac_of_orders": minbind,
                          "cap_frac_of_target_dollars":
                              capd / tgt_dollars if tgt_dollars else np.nan,
                          "cap_binding_instruments": ";".join(caps),
                          "cap_events": int(len(ce))})
            if len(ce):
                for t, g in ce.groupby("ticker"):
                    rows6.append({"table": "cap_by_instrument", "nav": nav0,
                                  "convention": conv, "instrument": t,
                                  "binding_transitions": int(len(g)),
                                  "mean_frac_capped":
                                      float((g["dollars_to_cash"] / g["target_dollars"]).mean())})
            print(f"  NAV {nav0:>10,}: trunc {trunc_lost/tgt_dollars:.5%}, "
                  f"min-bind {minbind:.1%}, cap {capd/tgt_dollars:.3%}, "
                  f"cap names {len(caps)}")
finally:
    bt.START_NAV = base_nav

cells = pd.DataFrame([r for r in rows6 if r["table"] == "cell" and r["convention"] == "o2o"])
cells = cells.sort_values("nav")
lo, hi = cells.iloc[0], cells.iloc[-1]
decades = math.log10(hi["nav"] / lo["nav"])
rows6.append({"table": "elasticity", "convention": "o2o",
              "d_ann_return_per_decade": (hi["ann_return"] - lo["ann_return"]) / decades,
              "d_sharpe_lo_per_decade": (hi["sharpe_lo"] - lo["sharpe_lo"]) / decades,
              "range_low_nav": float(lo["nav"]), "range_high_nav": float(hi["nav"]),
              "decades": decades})
print(f"  elasticity: {(hi['ann_return']-lo['ann_return'])/decades:+.4f} ann return "
      f"and {(hi['sharpe_lo']-lo['sharpe_lo'])/decades:+.4f} Lo-Sharpe per decade of NAV")
pd.DataFrame(rows6).to_csv(OUT / "nav-sweep.csv", index=False)
print(f"[wrote nav-sweep.csv: {len(rows6)} rows]")

# ===========================================================================
print("\n== STEP 7: execution-lag anomaly ==")
rows7 = []
for conv in ("c2c", "o2o"):
    panel = o2o if conv == "o2o" else panels["realized"]
    sig = sigs["realized"]
    accs = {}
    for lag in (1, 2, 3):
        a = run(sig["rows"], panel, sig, conv, lag=lag)
        accs[lag] = a
        m = L.standalone_metrics(C.window_slice(a["daily"]["ret"], "primary"),
                                 a["daily"]["nav"], a["orders"])
        rows7.append({"table": "lag_levels", "convention": conv, "lag": lag,
                      **{k: m[k] for k in ("ann_return", "ann_vol", "sharpe_lo",
                                           "max_drawdown", "ann_turnover")}})
        print(f"  [{conv}] T+{lag}: ann {m['ann_return']:.4f} SR {m['sharpe_lo']:.4f}")
    c1 = contrib_frame(accs[1], panel)
    c2 = contrib_frame(accs[2], panel)
    c1p = c1[c1.index >= C.PRIMARY_START]
    c2p = c2[c2.index >= C.PRIMARY_START]
    for t in TICK:
        d = float(c2p[t].sum() - c1p[t].sum())
        if abs(d) > 1e-6:
            rows7.append({"table": "lag_diff_by_instrument", "convention": conv,
                          "instrument": t, "t2_minus_t1_arith": d})
    for y in sorted(set(c1p.index.year)):
        d = float(c2p[c2p.index.year == y].sum().sum() -
                  c1p[c1p.index.year == y].sum().sum())
        rows7.append({"table": "lag_diff_by_year", "convention": conv,
                      "year": int(y), "t2_minus_t1_arith": d})
    r1 = C.window_slice(accs[1]["daily"]["ret"], "primary")
    r2 = C.window_slice(accs[2]["daily"]["ret"], "primary")
    diff = (r2 - r1).dropna()
    tot = float(diff.sum())
    top = diff.abs().sort_values(ascending=False).head(20)
    share20 = float(diff.loc[top.index].sum() / tot) if tot else np.nan
    rows7.append({"table": "lag_concentration", "convention": conv,
                  "total_t2_minus_t1_arith": tot,
                  "top20_sessions_share_of_total": share20,
                  "n_sessions": int(len(diff))})
    for d_, v in top.head(10).items():
        held = weights_of(accs[1]).shift(1).loc[d_]
        held = held[held > 0.01].sort_values(ascending=False)
        rows7.append({"table": "lag_top_sessions", "convention": conv,
                      "date": str(d_.date()), "t2_minus_t1": float(diff.loc[d_]),
                      "t1_holdings": "; ".join(f"{k}={v_:.2f}" for k, v_ in held.items())})
    print(f"  [{conv}] top-20 sessions carry {share20:.1%} of the T+2 minus T+1 sum")
    # sleeve decomposition
    for k in SLEEVE_ORDER:
        rws = L.make_lines(cal)[f"sleeve_{k}_standalone"][0](panel, sig["rows"], 0)
        a1 = run(rws, panel, sig, conv, lag=1)
        a2 = run(rws, panel, sig, conv, lag=2)
        x1 = C.window_slice(a1["daily"]["ret"], "primary").sum()
        x2 = C.window_slice(a2["daily"]["ret"], "primary").sum()
        rows7.append({"table": "lag_diff_by_sleeve", "convention": conv, "sleeve": k,
                      "t2_minus_t1_arith": float(x2 - x1)})
pd.DataFrame(rows7).to_csv(OUT / "lag-anomaly.csv", index=False)
print(f"[wrote lag-anomaly.csv: {len(rows7)} rows]")

# ===========================================================================
print("\n== STEP 8: segment hold lines charged ==")
rows8 = []
pr = panels["realized"]
tk = [t for t in TICK if t in pr.frames]
w = 1.0 / len(tk)
idx = cal[cal >= C.PRIMARY_START]
gross = {}
for seg in ("overnight", "intraday"):
    s = pd.Series(0.0, index=idx)
    for t in tk:
        fr = pr[t].frame
        ac, ao = fr["adj_close"], fr["adj_open"]
        r = (ao / ac.shift(1) - 1.0) if seg == "overnight" else (ac / ao - 1.0)
        s = s + w * r.reindex(idx).fillna(0.0)
    gross[seg] = s
# one round trip per session: the tier bp is already a round-turn figure, and
# the leg executing at the open carries the 4.4a premium
half_rt = {t: C.ANCHOR * C.TIER_MULT[C.TIER_CLASS.get(t, 3)] / 2.0 / 1e4 for t in tk}
slip_cost = sum(w * (half_rt[t] * (1.0 + C.PREMIUM_CENTRAL)) for t in tk)
comm = pd.Series(0.0, index=idx)
for t in tk:
    px = pr[t].raw_close.reindex(idx)
    for d in idx:
        pass
navc = 1_000_000.0
comm_series = pd.Series(0.0, index=idx)
for t in tk:
    px = pr[t].raw_close.reindex(idx).to_numpy()
    val = w * navc
    sh = np.where((px > 0) & ~np.isnan(px), val / np.where(px > 0, px, np.nan), np.nan)
    c_side = np.minimum(np.maximum(config.COMMISSION_F_MINIMUM,
                                   config.COMMISSION_F_PER_SHARE * sh),
                        config.COMMISSION_F_CAP_FRAC * val)
    c_side = np.nan_to_num(c_side)
    comm_series += pd.Series(2.0 * c_side / navc, index=idx)
splice = pd.Timestamp(config.COMMISSION_SPLICE_DATE)
comm_series[comm_series.index >= splice] = 0.0
for seg in ("overnight", "intraday"):
    g = gross[seg]
    net = g - slip_cost - comm_series
    for lbl, s in (("uncharged_attribution", g), ("charged_tradeable", net)):
        m = L.standalone_metrics(s)
        rows8.append({"table": "segment_line", "segment": seg, "variant": lbl,
                      "line_kind": "attribution" if lbl.startswith("uncharged")
                                   else "benchmark_tradeable",
                      "window": "primary",
                      **{k: m[k] for k in ("ann_return", "ann_vol", "sharpe_lo",
                                           "max_drawdown")}})
    print(f"  {seg}: uncharged ann {L.standalone_metrics(g)['ann_return']:+.4f} "
          f"SR {L.standalone_metrics(g)['sharpe_lo']:+.3f} | charged ann "
          f"{L.standalone_metrics(net)['ann_return']:+.4f} SR "
          f"{L.standalone_metrics(net)['sharpe_lo']:+.3f}")
rows8.append({"table": "charge_construction",
              "daily_round_turn_slippage_frac": slip_cost,
              "mean_daily_commission_frac": float(comm_series.mean()),
              "premium_applied_to_open_leg": C.PREMIUM_CENTRAL,
              "line_kind_values": "attribution | benchmark_tradeable",
              "note": "one round trip per session. The class tier figure is a "
                      "round-turn cost, so a single round trip carries it once, "
                      "with the 4.4a opening-auction premium applied to the leg "
                      "that executes at the open, being the sell for the overnight "
                      "line and the buy for the intraday line. Commission is Arm S "
                      "on both legs of every position at the canonical NAV, which "
                      "goes to zero from the 2019-10-01 splice."})
pd.DataFrame(rows8).to_csv(OUT / "segment-lines-charged.csv", index=False)
print(f"[wrote segment-lines-charged.csv: {len(rows8)} rows]")
