"""Session 13.5 — diagnostic pass on the canonical session-13 result.

Explains; changes nothing. Reads the session-13 engine read-only, writes
only under outputs/session-13.5/. No parameter, threshold, instrument,
cost-model, or branch change anywhere; the step-3 oversold sweep varies
config.OVERSOLD in memory only (restored in a finally, positive control:
theta=30 must reproduce the canonical zero firings), which the session
prompt explicitly directs as a cascade-reach count, not a performance
statistic.
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
import scripts.s13_runall as ra
from src import config
from src.portfolio import SLEEVE_ORDER, sleeve_label

OUT = ROOT / "outputs" / "session-13.5"
OUT.mkdir(parents=True, exist_ok=True)
ANCHOR = 10

pd.set_option("display.width", 250)


def wcsv(name: str, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(OUT / name, index=False)
    print(f"[wrote {name}: {len(rows)} rows]")


# ===========================================================================
print("== setup: panels, signals, base accounts ==")
panels = {a: bt.load_arm_panel(a) for a in ("synthetic", "realized")}
for a, p in panels.items():
    ok, mx = bt.assert_holdout(p)
    print(f"holdout [{a}]: PASS max {mx.date()}")
cal = panels["synthetic"]["SPY"].index
W = config.WARMUP_SESSIONS
years_traded = (len(cal) - W) / 252.0

sigs = {}
for a in ("synthetic", "realized"):
    s = bt.ArmSignals(panels[a], cal)
    sigs[a] = {"sig": s, **bt.run_signals(s)}
srows = sigs["synthetic"]["rows"]
by_i = {r["i"]: r for r in srows}

acc = {}
for key, (arm, bp, lag) in {
    "syn0": ("synthetic", 0, 1), "syn10": ("synthetic", ANCHOR, 1),
    "real10": ("realized", ANCHOR, 1),
}.items():
    acc[key] = bt.run_account(sigs[arm]["sig"], panels[arm], sigs[arm]["rows"], bp, fill_lag=lag)
print("base accounts done")

d10 = acc["syn10"]["daily"]
d0 = acc["syn0"]["daily"]
ret = {t: panels["synthetic"][t].ret_total.reindex(cal).to_numpy()
       for t in ra.TARGET_TICKERS}
raw10 = {t: panels["synthetic"][t].raw_close.reindex(cal).to_numpy()
         for t in ra.TARGET_TICKERS}

# realized weights (end-of-session), anchor path
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                   for r in acc["syn10"]["raw_rows"]], index=d10.index)

# label / sleeve state IN FORCE for return r_t: signal session t-2
# (fill at t-1 close from signal t-2; engine marks before trading at t).
lab_sig = pd.Series({cal[r["i"]]: r["label"] for r in srows})
sleeve_sig = {k: pd.Series({cal[r["i"]]: sleeve_label(r["sleeves"][k])
                            for r in srows}) for k in SLEEVE_ORDER}
sleeve_dict_sig = {k: {cal[r["i"]]: r["sleeves"][k] for r in srows}
                   for k in SLEEVE_ORDER}


def in_force(series: pd.Series, shift: int = 2) -> pd.Series:
    return series.reindex(d10.index).shift(shift)


lab_force = in_force(lab_sig)
sleeve_force = {k: in_force(sleeve_sig[k]) for k in SLEEVE_ORDER}

# ===========================================================================
print("\n== STEP 1: timing defect ==")
rows1 = []
lag_metrics = {}
for lag in range(1, 6):
    for bp in (0, ANCHOR):
        if lag == 1 and bp == 0:
            a_ = acc["syn0"]
        elif lag == 1 and bp == ANCHOR:
            a_ = acc["syn10"]
        else:
            a_ = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"],
                                srows, bp, fill_lag=lag)
        m = bt.headline_metrics(a_["daily"], a_["orders"])
        lag_metrics[(lag, bp)] = m
        rows1.append({"table": "lag_curve", "lag": lag, "bp": bp,
                      "ann_return": m["ann_return"], "ann_vol": m["ann_vol"],
                      "sharpe_naive": m["sharpe_naive"], "sharpe_lo": m["sharpe_lo"],
                      "max_drawdown": m["max_drawdown"]})
for bp in (0, ANCHOR):
    for met in ("ann_return", "sharpe_naive", "sharpe_lo", "max_drawdown"):
        vals = {lag: lag_metrics[(lag, bp)][met] for lag in range(1, 6)}
        peak = max(vals, key=lambda k: vals[k])
        rows1.append({"table": "lag_peaks", "bp": bp, "metric": met,
                      "peak_lag": peak, "values": "; ".join(
                          f"T+{k}={v:.4f}" for k, v in vals.items())})
        print(f"  bp={bp} {met}: peak at T+{peak} :: " +
              " ".join(f"{v:.3f}" for v in vals.values()))

# entry-session effect (0 bp path for purity)
r0 = d0["ret"]
first_held = d0["transition"].shift(1).fillna(False).astype(bool)
uncond = r0.mean()
rows1.append({"table": "entry_effect", "group": "ALL",
              "first_day_mean": r0[first_held].mean(), "uncond_mean": uncond,
              "n_first": int(first_held.sum())})
print(f"  portfolio: first-held mean {r0[first_held].mean():.5f} vs "
      f"uncond {uncond:.5f} (n={int(first_held.sum())})")
for era, msk in {"2007-2011": d0.index.year <= 2011,
                 "2012-2021": d0.index.year >= 2012}.items():
    rows1.append({"table": "entry_effect", "group": era,
                  "first_day_mean": r0[first_held & msk].mean(),
                  "uncond_mean": r0[msk].mean(),
                  "n_first": int((first_held & msk).sum())})
for y, g in r0.groupby(r0.index.year):
    fh = first_held.reindex(g.index)
    rows1.append({"table": "entry_effect_year", "group": str(y),
                  "first_day_mean": g[fh].mean(), "uncond_mean": g.mean(),
                  "n_first": int(fh.sum())})

# by sleeve and terminal state (target-weight sleeve slices)
for k in SLEEVE_ORDER:
    st_sig = sleeve_sig[k]
    changed = st_sig != st_sig.shift(1)
    changed.iloc[0] = True
    # first-held day for a change at signal s is s+2
    sret = pd.Series(0.0, index=d10.index)
    sf = sleeve_force[k]
    dicts = sleeve_dict_sig[k]
    dates_sig = in_force(pd.Series(st_sig.index, index=st_sig.index))
    vals = np.zeros(len(d10))
    for j, t in enumerate(d10.index):
        ds = dates_sig.iloc[j]
        if pd.isna(ds):
            continue
        wd = dicts.get(ds)
        if not wd:
            continue
        i_t = W + j
        vals[j] = sum(wv * ret[x][i_t] for x, wv in wd.items()
                      if not math.isnan(ret[x][i_t]))
    sret = pd.Series(vals, index=d10.index)
    ch_dates = st_sig.index[changed.to_numpy()]
    fh_idx = [cal.get_indexer([d])[0] + 2 for d in ch_dates]
    fh_dates = [cal[i] for i in fh_idx if i < len(cal)]
    fh_mask = pd.Series(False, index=d10.index)
    fh_mask.loc[[d for d in fh_dates if d in fh_mask.index]] = True
    cont = (~fh_mask) & (sret != 0)
    rows1.append({"table": "entry_effect_sleeve", "group": k,
                  "first_day_mean": sret[fh_mask].mean(),
                  "continuing_mean": sret[cont].mean(),
                  "n_first": int(fh_mask.sum())})
    print(f"  {k}: first-day {sret[fh_mask].mean():+.5f} vs continuing "
          f"{sret[cont].mean():+.5f} (sleeve units, n={int(fh_mask.sum())})")
    # by terminal state entered
    ent_state = pd.Series({cal[i]: st_sig.loc[d] for d, i in zip(ch_dates, fh_idx)
                           if i < len(cal)})
    held_state = sleeve_force[k]
    for state in st_sig.value_counts().head(8).index:
        fh_s = fh_mask & (ent_state.reindex(d10.index) == state)
        ct_s = (~fh_mask) & (held_state == state)
        if fh_s.sum() >= 10:
            rows1.append({"table": "entry_effect_state", "group": f"{k}:{state}",
                          "first_day_mean": sret[fh_s].mean(),
                          "continuing_mean": sret[ct_s].mean(),
                          "n_first": int(fh_s.sum())})

# by instrument (0 bp buy orders)
orders0 = acc["syn0"]["orders"]
buys = orders0[orders0["side"] == "buy"]
for t, g in buys.groupby("ticker"):
    idxs = cal.get_indexer(pd.DatetimeIndex(g["date"])) + 1
    idxs = idxs[idxs < len(cal)]
    fd = np.nanmean([ret[t][i] for i in idxs])
    arr = ret[t][W:]
    held = rw[t] > 0
    held_ret = np.nanmean([ret[t][W + j] for j in range(len(rw)) if held.iloc[j]])
    rows1.append({"table": "entry_effect_instrument", "group": t,
                  "first_day_mean": fd, "held_mean": held_ret,
                  "uncond_mean": np.nanmean(arr), "n_first": len(idxs)})

# autocorrelation
def acf(x: np.ndarray, k: int) -> float:
    x = x[~np.isnan(x)]
    xc = x - x.mean()
    return float(np.dot(xc[:-k], xc[k:]) / np.dot(xc, xc))

wbar = rw.mean()
rfs = bt.rf_per_session(d0.index).fillna(0.0)
mix = sum(wbar[t] * pd.Series(ret[t][W:], index=d0.index).fillna(0.0)
          for t in ra.TARGET_TICKERS) + (1 - wbar.sum()) * rfs
for name, series in [("portfolio_0bp", r0.dropna().to_numpy()),
                     ("constant_weight_mix", mix.iloc[1:].to_numpy())] + \
        [(t, ret[t][W:]) for t in ra.TARGET_TICKERS]:
    row = {"table": "autocorrelation", "group": name}
    for k in range(1, 11):
        row[f"rho{k}"] = acf(np.asarray(series, dtype=float), k)
    rows1.append(row)
print(f"  rho1 portfolio {acf(r0.dropna().to_numpy(),1):+.4f} vs "
      f"constant-weight mix {acf(mix.iloc[1:].to_numpy(),1):+.4f}")

# weekday / month-end
fills = d10.index[d10["transition"]]
wd_all = pd.Series(d10.index.dayofweek).value_counts(normalize=True).sort_index()
wd_f = pd.Series(fills.dayofweek).value_counts(normalize=True).sort_index()
assert abs(wd_f.sum() - 1) < 1e-9 and abs(wd_all.sum() - 1) < 1e-9  # positive control
for dow in range(5):
    rows1.append({"table": "weekday", "group": ["Mon", "Tue", "Wed", "Thu", "Fri"][dow],
                  "fill_frac": wd_f.get(dow, 0.0), "session_frac": wd_all.get(dow, 0.0)})
me = pd.Series(d10.index, index=d10.index).groupby(
    [d10.index.year, d10.index.month]).transform(
        lambda g: (g >= g.iloc[-3]) if len(g) >= 3 else True)
mb = pd.Series(d10.index, index=d10.index).groupby(
    [d10.index.year, d10.index.month]).transform(
        lambda g: (g <= g.iloc[2]) if len(g) >= 3 else True)
rows1.append({"table": "month_position", "group": "last3_sessions",
              "fill_frac": float(me.loc[fills].mean()),
              "session_frac": float(me.mean())})
rows1.append({"table": "month_position", "group": "first3_sessions",
              "fill_frac": float(mb.loc[fills].mean()),
              "session_frac": float(mb.mean())})
wcsv("lag-diagnostics.csv", rows1)

# ===========================================================================
print("\n== STEP 2: year attribution ==")
rows2 = []
r10 = d10["ret"]
w_lag = rw.shift(1)
contrib = pd.DataFrame({t: w_lag[t] * pd.Series(ret[t][W:], index=d10.index)
                        for t in ra.TARGET_TICKERS})
cost_ser = acc["syn10"]["orders"].assign(
    cost=lambda o: o["commission"] + o["slippage"]).groupby("date")["cost"].sum()
cost_frac = (cost_ser.reindex(d10.index).fillna(0.0) / d10["nav"].shift(1)).fillna(0.0)

for year in (2010, 2011, 2012, 2013, 2019):
    msk = d10.index.year == year
    comp = float((1 + r10[msk]).prod() - 1)
    arith = float(r10[msk].sum())
    inst = contrib[msk].sum()
    rows2.append({"table": "year_summary", "year": year,
                  "compounded_return": comp, "arithmetic_sum": arith,
                  "cost_drag_arith": -float(cost_frac[msk].sum()),
                  "residual_arith": arith - float(inst.sum()) })
    for t, v in inst.sort_values().items():
        if abs(v) > 0.001:
            rows2.append({"table": "instrument_contribution", "year": year,
                          "instrument": t, "arith_contribution": float(v)})
    # sleeve / state contribution at target weights x budget
    for k in SLEEVE_ORDER:
        dicts = sleeve_dict_sig[k]
        dates_sig = in_force(pd.Series(lab_sig.index, index=lab_sig.index))
        stot: dict[str, float] = {}
        ktot = 0.0
        for j, t_ in enumerate(d10.index):
            if not msk[j]:
                continue
            ds = dates_sig.iloc[j]
            if pd.isna(ds):
                continue
            wd = dicts.get(ds)
            if not wd:
                continue
            i_t = W + j
            v = sum(wv * ret[x][i_t] for x, wv in wd.items()
                    if not math.isnan(ret[x][i_t])) * config.SLEEVE_BUDGET
            ktot += v
            st = sleeve_force[k].iloc[j]
            stot[st] = stot.get(st, 0.0) + v
        rows2.append({"table": "sleeve_contribution", "year": year,
                      "sleeve": k, "arith_contribution": ktot})
        for st, v in sorted(stot.items(), key=lambda x: x[1]):
            if abs(v) > 0.002:
                rows2.append({"table": "state_contribution", "year": year,
                              "sleeve": k, "state": st, "arith_contribution": v})
    if year == 2010:
        exc = float(inst.get("SOXS", 0) + inst.get("SVXY", 0) + inst.get("UVXY", 0))
        rows2.append({"table": "exception_share", "year": 2010,
                      "soxs_svxy_uvxy_arith": exc, "arith_total": arith,
                      "share": exc / arith if arith else np.nan})
        print(f"  2010 exception-instrument contribution: {exc:+.4f} of "
              f"arithmetic {arith:+.4f}")

# worst sessions
def worst_rows(year, n):
    msk = d10.index.year == year
    worst = r10[msk].nsmallest(n)
    out = []
    for dt, rv in worst.items():
        wrow = rw.shift(1).loc[dt]
        top = "; ".join(f"{t}={v:.3f}" for t, v in
                        wrow[wrow > 0.01].sort_values(ascending=False).head(4).items())
        out.append({"table": "worst_sessions", "year": year, "date": str(dt.date()),
                    "ret": float(rv), "held_label": lab_force.loc[dt],
                    "top_weights": top})
    return out

rows2 += worst_rows(2010, 10) + worst_rows(2011, 5) + worst_rows(2012, 5)

# state timelines
for name, a, b in (("flash_crash_2010", "2010-04-15", "2010-06-15"),
                   ("august_2011", "2011-07-15", "2011-09-15")):
    for dt in d10.loc[a:b].index:
        rows2.append({"table": f"timeline_{name}", "date": str(dt.date()),
                      "ret": float(r10.loc[dt]), "nav": float(d10.loc[dt, "nav"]),
                      **{f"{k}_held": sleeve_force[k].loc[dt] for k in SLEEVE_ORDER},
                      "signal_label": lab_sig.reindex([dt]).iloc[0] if dt in lab_sig.index else ""})
wcsv("year-attribution.csv", rows2)

# ===========================================================================
print("\n== STEP 3: unreachable terminals ==")
rows3 = []
sig_s = sigs["synthetic"]["sig"]
psq = sig_s.rsi[config.RSI_PERIOD_DIP]["PSQ"][W:]
qqq_rsi = sig_s.rsi[config.RSI_PERIOD_DIP]["QQQ"][W:]
tq_p = sig_s.price["TQQQ"][W:]
tq_s20 = sig_s.smas[config.SMA_SHORT]["TQQQ"][W:]
psq30 = psq < config.OVERSOLD
tq_above = tq_p > tq_s20
conj = psq30 & tq_above
n_eval = len(srows)
rows3.append({"table": "conditions", "metric": "PSQ_RSI_below_30", "n": int(np.nansum(psq30)),
              "frac": float(np.nansum(psq30) / n_eval)})
rows3.append({"table": "conditions", "metric": "TQQQ_above_SMA20", "n": int(np.nansum(tq_above)),
              "frac": float(np.nansum(tq_above) / n_eval)})
rows3.append({"table": "conditions", "metric": "conjunction", "n": int(np.nansum(conj)),
              "frac": float(np.nansum(conj) / n_eval)})
print(f"  PSQ<30: {int(np.nansum(psq30))}; TQQQ>SMA20: {int(np.nansum(tq_above))}; "
      f"conjunction: {int(np.nansum(conj))}")

# where PSQ<30 (and conjunction) sessions resolve in T11
res_psq, res_conj = {}, {}
for j, r in enumerate(srows):
    st = sig_s.state_at(r["i"])
    b11, w11, sub = ra.trace_t11(st)
    key = b11 if sub is None else f"bear[{sub[0]}|{sub[1]}]"
    if psq30[j]:
        res_psq[key] = res_psq.get(key, 0) + 1
    if conj[j]:
        res_conj[key] = res_conj.get(key, 0) + 1
for name, d_ in (("psq30_resolved_by", res_psq), ("conjunction_resolved_by", res_conj)):
    for k_, n_ in sorted(d_.items(), key=lambda x: -x[1]):
        rows3.append({"table": name, "branch": k_, "n": n_})
print("  conjunction resolved by:", res_conj)

both = ~np.isnan(psq) & ~np.isnan(qqq_rsi)
rows3.append({"table": "psq_vs_qqq_rsi", "metric": "correlation",
              "value": float(np.corrcoef(psq[both], qqq_rsi[both])[0, 1])})
rows3.append({"table": "psq_vs_qqq_rsi", "metric": "mean_sum",
              "value": float(np.nanmean(psq[both] + qqq_rsi[both]))})
print(f"  corr(PSQ,QQQ RSI) {np.corrcoef(psq[both],qqq_rsi[both])[0,1]:+.4f}, "
      f"mean sum {np.nanmean(psq[both]+qqq_rsi[both]):.2f}")

OVERSOLD_GRID = (20, 25, 30, 35, 40)
orig = config.OVERSOLD
try:
    for theta in OVERSOLD_GRID:
        config.OVERSOLD = theta
        nbb = nfb = 0
        for r in srows:
            st = sig_s.state_at(r["i"])
            b11, w11, sub = ra.trace_t11(st)
            if sub is not None:
                if sub[0] == "bb:PSQ_dip->PSQ":
                    nbb += 1
                if sub[1] == "fb:PSQ_dip->PSQ":
                    nfb += 1
        rows3.append({"table": "oversold_sweep", "oversold": theta,
                      "bb_psq_dip_fired": nbb, "fb_psq_dip_fired": nfb})
        print(f"  oversold={theta}: bb PSQ-dip {nbb}, fb PSQ-dip {nfb}")
        if theta == orig:
            assert nbb == 0 and nfb == 0, "positive control failed: theta=30 must be 0"
finally:
    config.OVERSOLD = orig
config.validate()
wcsv("unreachable-terminals.csv", rows3)

# ===========================================================================
print("\n== STEP 4: negative cash ==")
rows4 = []
cash = d10["cash"]
nav = d10["nav"]
neg = cash < 0
negfrac = (-cash[neg] / nav[neg])
gross_over = (d10["pos_value"] / nav - 1.0)
identity_gap = float(((-cash / nav).where(neg, 0) - gross_over.where(neg, 0)).abs().max())
rows4.append({"table": "summary", "metric": "n_negative_sessions", "value": int(neg.sum())})
rows4.append({"table": "summary", "metric": "mean_negative_frac_of_nav", "value": float(negfrac.mean())})
rows4.append({"table": "summary", "metric": "median_negative_frac_of_nav", "value": float(negfrac.median())})
rows4.append({"table": "summary", "metric": "max_negative_frac_of_nav", "value": float(negfrac.max())})
rows4.append({"table": "summary", "metric": "identity_negcash_eq_grossover_gap", "value": identity_gap,
              "note": "negative cash / NAV == realized gross - 1, an accounting identity"})
for q in (0.5, 0.9, 0.99, 1.0):
    rows4.append({"table": "distribution", "metric": f"negfrac_q{q}",
                  "value": float(negfrac.quantile(q))})
days = pd.Series(d10.index).diff().dt.days.fillna(0).to_numpy()
borrow_daysdollar = float(np.sum(np.where(neg, -cash, 0.0) * days))
rows4.append({"table": "summary", "metric": "calendar_day_weighted_borrow_avg_frac",
              "value": borrow_daysdollar / float((nav * days).sum())})
for y, g in cash.groupby(cash.index.year):
    rows4.append({"table": "by_year", "year": int(y),
                  "mean_cash_frac": float((g / nav[g.index]).mean()),
                  "min_cash": float(g.min()),
                  "n_negative": int((g < 0).sum())})
rfs10 = bt.rf_per_session(d10.index).fillna(0.0)
for spr in (100, 150, 300):
    charge = np.where(cash.shift(1) < 0, -cash.shift(1) * (spr / 1e4) * days / 360.0, 0.0)
    r_adj = r10 - pd.Series(charge, index=d10.index) / nav.shift(1)
    n = r_adj.dropna().shape[0]
    ann_adj = float((1 + r_adj.dropna()).prod() ** (252.0 / n) - 1)
    sr_adj = bt.lo_sharpe((r_adj - rfs10).dropna())
    m1 = bt.headline_metrics(d10, acc["syn10"]["orders"])
    rows4.append({"table": "margin_spread", "spread_bp": spr,
                  "ann_return_reduction": m1["ann_return"] - ann_adj,
                  "sharpe_lo_reduction": m1["sharpe_lo"] - sr_adj,
                  "total_charge_dollars": float(charge.sum())})
    print(f"  spread {spr}bp: ann -{m1['ann_return']-ann_adj:.5f}, "
          f"SR_lo -{m1['sharpe_lo']-sr_adj:.5f}")
wcsv("cash-diagnostics.csv", rows4)

# ===========================================================================
print("\n== STEP 5: reconstruction sensitivity ==")
rows5 = []
orders10 = acc["syn10"]["orders"]
cost_by_date = orders10.groupby("date").apply(
    lambda g: g["commission"].sum() + g["slippage"].sum())
fill_dates = d10.index[d10["transition"]]
# residual reconstruction with positive control on fresh entries
resid_records = []
ctrl_checked = ctrl_bad = 0
buys10 = orders10[orders10["side"] == "buy"].set_index(["date", "ticker"])["shares"]
prev_pos: set = set()
for f in fill_dates:
    i_f = cal.get_indexer([f])[0]
    sigrow = by_i.get(i_f - 1)
    if sigrow is None or not sigrow["changed"]:
        continue
    targets = sigrow["targets"]
    nav_pre = float(d10.loc[f, "nav"]) + float(cost_by_date.get(f, 0.0))
    for t, w_ in targets.items():
        px = raw10[t][i_f]
        if math.isnan(px) or px <= 0:
            continue
        alloc = nav_pre * w_
        sh = math.trunc(alloc / px)
        resid = alloc - sh * px
        resid_records.append({"date": f, "ticker": t, "residual": resid,
                              "frac_of_sleeve_slice": resid / alloc if alloc else 0.0,
                              "shares": sh, "px": px})
        if t not in prev_pos and (f, t) in buys10.index:
            ctrl_checked += 1
            if abs(buys10.loc[(f, t)] - sh) > 0.5:
                ctrl_bad += 1
    prev_pos = set(targets)
assert ctrl_checked > 100 and ctrl_bad / ctrl_checked < 0.02, \
    f"residual reconstruction control: {ctrl_bad}/{ctrl_checked} mismatches"
print(f"  residual reconstruction positive control: {ctrl_bad}/{ctrl_checked} share mismatches")
rr = pd.DataFrame(resid_records)
for t in sorted(rr["ticker"].unique()):
    g = rr[rr["ticker"] == t]
    px = pd.Series(raw10[t][W:], index=d10.index).dropna()
    rows5.append({"table": "per_fund", "ticker": t,
                  "px_min": float(px.min()), "px_median": float(px.median()),
                  "px_max": float(px.max()),
                  "resid_mean": float(g["residual"].mean()),
                  "resid_max": float(g["residual"].max()),
                  "resid_mean_frac_slice": float(g["frac_of_sleeve_slice"].mean()),
                  "n_fills": len(g)})
tot_resid = float(rr["residual"].sum())
rows5.append({"table": "aggregate", "metric": "cumulative_truncation_residual_dollars",
              "value": tot_resid})
# forgone return: residual would have earned portfolio return over its hold
holds = list(fill_dates) + [d10.index[-1]]
resid_by_fill = rr.groupby("date")["residual"].sum()
forgone = 0.0
for a_, b_ in zip(holds[:-1], holds[1:]):
    Rres = float(resid_by_fill.get(a_, 0.0))
    seg = r10.loc[a_:b_].iloc[1:]
    rf_seg = rfs10.loc[a_:b_].iloc[1:]
    forgone += Rres * float((1 + seg).prod() - (1 + rf_seg).prod())
rows5.append({"table": "aggregate", "metric": "return_forgone_dollars_portfolio_vs_dtb3",
              "value": forgone})
rows5.append({"table": "aggregate", "metric": "forgone_bp_per_year_of_avg_nav",
              "value": forgone / float(nav.mean()) / years_traded * 1e4})
print(f"  cumulative residual ${tot_resid:,.0f}; forgone ${forgone:,.0f} "
      f"({forgone/float(nav.mean())/years_traded*1e4:.2f} bp/yr)")
# UVXY detail
gu = rr[rr["ticker"] == "UVXY"]
pxu = pd.Series(raw10["UVXY"][W:], index=d10.index)
for y, gy in pxu.groupby(pxu.index.year):
    gyf = gu[pd.DatetimeIndex(gu["date"]).year == y]
    rows5.append({"table": "uvxy_detail", "year": int(y),
                  "px_min": float(gy.min()), "px_median": float(gy.median()),
                  "px_max": float(gy.max()),
                  "n_fills": len(gyf),
                  "mean_shares_per_fill": float(gyf["shares"].mean()) if len(gyf) else np.nan,
                  "resid_mean": float(gyf["residual"].mean()) if len(gyf) else np.nan,
                  "resid_mean_frac_slice": float(gyf["frac_of_sleeve_slice"].mean()) if len(gyf) else np.nan})
# commission under anchor rescale
for k_scale in (0.1, 1.0, 10.0):
    tot = {}
    for _, o in orders10.iterrows():
        sh = o["value"] / (raw10[o["ticker"]][cal.get_indexer([o["date"]])[0]] * k_scale)
        c = min(max(bt.COMMISSION_MINIMUM, bt.COMMISSION_PER_SHARE * sh),
                bt.COMMISSION_CAP_FRAC * o["value"])
        tot[o["ticker"]] = tot.get(o["ticker"], [0.0, 0.0])
        tot[o["ticker"]][0] += c
        tot[o["ticker"]][1] += o["value"]
    for t, (c, v) in sorted(tot.items()):
        rows5.append({"table": "commission_anchor_sensitivity", "anchor_scale": k_scale,
                      "ticker": t, "commission_bp_of_traded": c / v * 1e4})
wcsv("reconstruction-sensitivity.csv", rows5)

# ===========================================================================
print("\n== STEP 6: concentration extended ==")
rows6 = []
tw = {}
cur: dict = {}
for r in srows:
    if r["changed"] and r["targets"] is not None:
        cur = r["targets"]
    tw[cal[r["i"]]] = dict(cur)
tw_df = pd.DataFrame({t: {d_: w_.get(t, 0.0) for d_, w_ in tw.items()}
                      for t in ra.TARGET_TICKERS}).reindex(d10.index).fillna(0.0)
mult = {}
for t in ra.TARGET_TICKERS:
    fr = panels["synthetic"][t].frame
    if "multiple" in fr.columns and fr["multiple"].notna().any():
        mult[t] = fr["multiple"].reindex(d10.index).to_numpy()
    else:
        mult[t] = np.zeros(len(d10)) if t == "BTAL" else np.ones(len(d10))

def effx(wdf):
    v = np.zeros(len(wdf))
    for t in ra.TARGET_TICKERS:
        v += wdf[t].to_numpy() * mult[t]
    return pd.Series(v, index=wdf.index)

eff_t, eff_r = effx(tw_df), effx(rw)
dd = nav / nav.cummax() - 1.0
q5 = pd.qcut(dd, 5, labels=False, duplicates="drop")
for qi in range(5):
    m_ = q5 == qi
    rows6.append({"table": "eff_exposure_dd_quintile", "quintile": qi,
                  "note": "0 = deepest drawdown",
                  "target_mean": float(eff_t[m_].mean()),
                  "realized_mean": float(eff_r[m_].mean()),
                  "dd_range": f"{dd[m_].min():.3f}..{dd[m_].max():.3f}"})
qtrail = pd.Series(sig_s.crash[W:], index=d10.index)
qqq_ret = pd.Series(ret["QQQ"][W:], index=d10.index)
qvol = qqq_ret.rolling(60).std() * math.sqrt(252)
for name, series in (("qqq_trailing60_return_decile", qtrail),
                     ("qqq_trailing60_vol_decile", qvol)):
    dec = pd.qcut(series, 10, labels=False, duplicates="drop")
    for di in sorted(dec.dropna().unique()):
        m_ = dec == di
        rows6.append({"table": name, "decile": int(di),
                      "range": f"{series[m_].min():.2f}..{series[m_].max():.2f}",
                      "target_mean": float(eff_t[m_].mean()),
                      "realized_mean": float(eff_r[m_].mean())})
# per-year covariance ENB (realized weights; tickers complete that year)
ret_panel = pd.DataFrame({t: pd.Series(ret[t][W:], index=d10.index)
                          for t in ra.TARGET_TICKERS})
cov_full = ret_panel.dropna().cov().to_numpy() * 252
t_full = ra.min_torsion(cov_full)
enb_full = ra.enb_series(rw[list(ra.TARGET_TICKERS)], cov_full, t_full)
for y in sorted(set(d10.index.year)):
    m_ = d10.index.year == y
    sub = ret_panel[m_].dropna(axis=1, how="any")
    ticks = [t for t in ra.TARGET_TICKERS if t in sub.columns]
    Sig_y = sub[ticks].cov().to_numpy() * 252
    t_y = ra.min_torsion(Sig_y)
    enb_y = ra.enb_series(rw.loc[m_, ticks], Sig_y, t_y)
    rows6.append({"table": "enb_per_year_cov", "year": int(y),
                  "n_tickers": len(ticks),
                  "enb_yearcov_mean": float(enb_y.mean()),
                  "enb_fixedcov_mean": float(enb_full[m_].mean()),
                  "gap": float(enb_y.mean() - enb_full[m_].mean())})
# pairwise sleeve overlap
held_states = {k: sleeve_force[k] for k in SLEEVE_ORDER}
held_dicts = {}
for k in SLEEVE_ORDER:
    dates_sig = in_force(pd.Series(lab_sig.index, index=lab_sig.index))
    held_dicts[k] = [sleeve_dict_sig[k].get(dates_sig.iloc[j]) if not pd.isna(dates_sig.iloc[j]) else None
                     for j in range(len(d10))]
for a_i in range(4):
    for b_i in range(a_i + 1, 4):
        ka, kb = SLEEVE_ORDER[a_i], SLEEVE_ORDER[b_i]
        n_share = 0
        dollar = 0.0
        for j in range(len(d10)):
            wa, wb = held_dicts[ka][j], held_dicts[kb][j]
            if not wa or not wb:
                continue
            common = set(wa) & set(wb)
            if common:
                n_share += 1
                dollar += sum(min(wa[x], wb[x]) for x in common) * config.SLEEVE_BUDGET
        rows6.append({"table": "sleeve_overlap", "pair": f"{ka}-{kb}",
                      "frac_sessions_common_ticker": n_share / len(d10),
                      "mean_overlap_exposure_frac_nav": dollar / len(d10)})
ntick = (rw > 1e-9).sum(axis=1)
for n_, c_ in ntick.value_counts().sort_index().items():
    rows6.append({"table": "distinct_tickers_held", "n_tickers": int(n_),
                  "n_sessions": int(c_), "frac": float(c_ / len(rw))})
wcsv("concentration-extended.csv", rows6)

# ===========================================================================
print("\n== STEP 7: turnover structure ==")
rows7 = []
for bp in config.SLIPPAGE_BASE_GRID_BP:
    a_ = acc["syn10"] if bp == ANCHOR else (acc["syn0"] if bp == 0 else
         bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"], srows, bp))
    m = bt.headline_metrics(a_["daily"], a_["orders"])
    rows7.append({"table": "turnover_vs_cost", "bp": bp,
                  "traded_per_year": float(a_["orders"]["value"].sum() / 2 / years_traded),
                  "avg_nav": float(a_["daily"]["nav"].mean()),
                  "turnover": m["ann_turnover_one_sided"],
                  "note": "identical signal stream shared across cost levels by construction; "
                          "signals never read NAV, so no feedback path exists"})
per_fill = orders10.groupby("date")["value"].sum() / 2.0
navpre = d10["nav"].reindex(per_fill.index) + cost_by_date.reindex(per_fill.index).fillna(0)
frac_fill = per_fill / navpre
rows7.append({"table": "per_transition", "metric": "mean_frac_turned", "value": float(frac_fill.mean())})
rows7.append({"table": "per_transition", "metric": "median_frac_turned", "value": float(frac_fill.median())})
for q in (0.1, 0.25, 0.75, 0.9):
    rows7.append({"table": "per_transition", "metric": f"q{q}", "value": float(frac_fill.quantile(q))})
rows7.append({"table": "per_transition", "metric": "reconciliation",
              "value": float(frac_fill.mean() * len(per_fill) / years_traded),
              "note": "mean fraction x fills/yr ~ annual turnover"})
print(f"  mean per-transition one-sided fraction {frac_fill.mean():.3f}; "
      f"x {len(per_fill)/years_traded:.1f}/yr = {frac_fill.mean()*len(per_fill)/years_traded:.1f}")
for k in SLEEVE_ORDER:
    st = sleeve_sig[k]
    runs = (st != st.shift(1)).cumsum()
    rl = st.groupby(runs).size()
    states_of_run = st.groupby(runs).first()
    rows7.append({"table": "holding_by_sleeve", "sleeve": k,
                  "median_run": float(rl.median()), "mean_run": float(rl.mean()),
                  "frac_1session": float((rl == 1).mean()), "n_runs": int(len(rl))})
    for state in st.value_counts().head(5).index:
        rls = rl[states_of_run == state]
        rows7.append({"table": "holding_by_state", "sleeve": k, "state": state,
                      "median_run": float(rls.median()), "mean_run": float(rls.mean()),
                      "frac_1session": float((rls == 1).mean()), "n_runs": int(len(rls))})
for t, g in orders10.groupby("ticker"):
    rows7.append({"table": "turnover_by_instrument", "ticker": t,
                  "one_sided_turnover_per_year": float(g["value"].sum() / 2 / nav.mean() / years_traded)})
ov = orders10.copy()
ov["year"] = pd.DatetimeIndex(ov["date"]).year
for y, g in ov.groupby("year"):
    nav_y = nav[nav.index.year == y].mean()
    rows7.append({"table": "turnover_by_year", "year": int(y),
                  "one_sided_turnover": float(g["value"].sum() / 2 / nav_y /
                                              (len(nav[nav.index.year == y]) / 252.0))})
wcsv("turnover-structure.csv", rows7)

# ===========================================================================
print("\n== STEP 8: arms and crisis window ==")
rows8 = []
rw_real = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                        for r in acc["real10"]["raw_rows"]],
                       index=acc["real10"]["daily"].index)
raw_real = {t: panels["realized"][t].raw_close.reindex(cal).to_numpy()
            for t in ra.TARGET_TICKERS}
tw_dates = list(tw_df.index)
# forced cash: target weight on tickers with no realized-arm price that session
sig_real_rows = sigs["realized"]["rows"]
cur = {}
forced = []
for r in sig_real_rows:
    if r["changed"] and r["targets"] is not None:
        cur = r["targets"]
    i_ = r["i"]
    f_ = sum(w_ for t_, w_ in cur.items() if math.isnan(raw_real[t_][i_]))
    forced.append({"date": cal[i_], "forced": f_})
fc = pd.DataFrame(forced).set_index("date")["forced"]
for y in range(2007, 2012):
    m_ = fc.index.year == y
    rows8.append({"table": "realized_forced_cash", "year": y,
                  "mean_target_weight_unfillable": float(fc[m_].mean()),
                  "max": float(fc[m_].max())})
    print(f"  realized forced-cash target weight {y}: mean {fc[m_].mean():.3f}")
for a in ("synthetic", "realized"):
    dd_ = acc["syn10" if a == "synthetic" else "real10"]["daily"]
    r_ = dd_["ret"][dd_.index >= "2012-01-01"].dropna()
    rf_ = bt.rf_per_session(dd_.index)[dd_.index >= "2012-01-01"]
    n = len(r_)
    navseg = (1 + r_).cumprod()
    rows8.append({"table": "arms_2012_onward", "arm": a,
                  "ann_return": float(navseg.iloc[-1] ** (252 / n) - 1),
                  "ann_vol": float(r_.std(ddof=1) * math.sqrt(252)),
                  "sharpe_lo": bt.lo_sharpe((r_ - rf_).dropna()),
                  "max_drawdown": float((navseg / navseg.cummax() - 1).min())})
uf = acc["syn10"]["unavailable_fills"]
crash_ser = pd.Series(sig_s.crash, index=cal)
for _, e in uf.iterrows():
    dt = e["date"]
    rows8.append({"table": "btal_events", "date": str(pd.Timestamp(dt).date()),
                  "target_weight": e["weight"],
                  "t11_state_in_force": sleeve_force["T11"].reindex([dt]).iloc[0]
                  if dt in sleeve_force["T11"].index else "",
                  "qqq_trailing60_pct": float(crash_ser.reindex([dt]).iloc[0])})
# SOXS rolling divergence vs real fund, in-window
def roll_div(syn_r, real_r, win=252):
    j = pd.DataFrame({"s": syn_r, "r": real_r}).dropna()
    cs = (1 + j["s"]).rolling(win).apply(np.prod, raw=True)
    cr = (1 + j["r"]).rolling(win).apply(np.prod, raw=True)
    return (cs / cr - 1).abs()

real_soxs = bt.build_ticker_frame("SOXS", bt._load_raw("SOXS")).ret_total
div_soxs = roll_div(panels["synthetic"]["SOXS"].ret_total, real_soxs)
real_tqqq = bt.build_ticker_frame("TQQQ", bt._load_raw("TQQQ")).ret_total
div_tqqq = roll_div(panels["synthetic"]["TQQQ"].ret_total, real_tqqq)
assert div_tqqq.max() < 0.25, "positive control failed: TQQQ divergence should be small"
mx_date = div_soxs.idxmax()
mx_win = div_soxs.loc[:mx_date].index[-252:]
held_soxs = rw["SOXS"] > 0
overlap = float(held_soxs.reindex(mx_win).fillna(False).mean())
rows8.append({"table": "soxs_divergence", "metric": "in_window_max_roll252_ratio_div",
              "value": float(div_soxs.max()), "date": str(mx_date.date()),
              "note": f"TQQQ control max {div_tqqq.max():.4f}; session 12's 13.94 was "
                      "measured over 2010-03..2026-08 and may sit post-holdout"})
rows8.append({"table": "soxs_divergence", "metric": "frac_of_max_window_sessions_soxs_held",
              "value": overlap})
print(f"  SOXS in-window max roll-252 divergence {div_soxs.max():.2f} at "
      f"{mx_date.date()}; held on {overlap:.1%} of that window "
      f"(TQQQ control {div_tqqq.max():.4f})")
wcsv("arm-comparison.csv", rows8)

# ===========================================================================
print("\n== STEP 9: cost extension ==")
rows9 = []
EXT = (60, 75, 100, 150)
curves = {}
for a in ("synthetic", "realized"):
    pts = []
    for bp in list(config.SLIPPAGE_BASE_GRID_BP) + list(EXT):
        if a == "synthetic" and bp == 0:
            m = bt.headline_metrics(d0, acc["syn0"]["orders"])
        elif a == "synthetic" and bp == ANCHOR:
            m = bt.headline_metrics(d10, orders10)
        elif a == "realized" and bp == ANCHOR:
            m = bt.headline_metrics(acc["real10"]["daily"], acc["real10"]["orders"])
        else:
            a_ = bt.run_account(sigs[a]["sig"], panels[a], sigs[a]["rows"], bp)
            m = bt.headline_metrics(a_["daily"], a_["orders"])
        pts.append({"arm": a, "slippage_bp": bp, "ann_return": m["ann_return"],
                    "sharpe_lo": m["sharpe_lo"], "sharpe_naive": m["sharpe_naive"],
                    "max_drawdown": m["max_drawdown"]})
        if bp in EXT:
            rows9.append({"table": "extension_points", **pts[-1]})
    curves[a] = pd.DataFrame(pts).sort_values("slippage_bp")

def crossing(df, col):
    x, y = df["slippage_bp"].to_numpy(float), df[col].to_numpy()
    for i in range(len(x) - 1):
        if y[i] > 0 >= y[i + 1]:
            return x[i] + (x[i + 1] - x[i]) * y[i] / (y[i] - y[i + 1])
    return np.nan

extrap = {"synthetic": {"ann_return": 50.94, "sharpe_lo": 83.93},
          "realized": {"ann_return": 65.98, "sharpe_lo": 96.55}}
for a in curves:
    for col in ("ann_return", "sharpe_lo"):
        meas = crossing(curves[a], col)
        rows9.append({"table": "crossings", "arm": a, "metric": col,
                      "measured_bp": meas, "extrapolated_bp": extrap[a][col],
                      "difference_bp": meas - extrap[a][col] if not np.isnan(meas) else np.nan})
        print(f"  {a} {col}: measured {meas:.1f} bp vs extrapolated {extrap[a][col]:.1f}")
wcsv("cost-extension.csv", rows9)
print("\nDONE — all step CSVs written")
