"""Session 28 phases D and E. One deterministic decomposition pass over the holdout.

Every quantity in phases D and E is computed in this single pass. The per-session
sleeve dictionaries ARE persisted this time, since session 27 phase C did not and
its phase D had to re-execute.

Nothing here selects a specification. Every figure describes the committed result.
"""
from __future__ import annotations

import csv
import math
import os
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s14_common as C                         # noqa: E402
import scripts.s15_lines as L                          # noqa: E402
from src import config                                 # noqa: E402
from src.portfolio import SLEEVE_ORDER                 # noqa: E402

OUT = ROOT / "outputs" / "session-28"
OUT.mkdir(parents=True, exist_ok=True)
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
SHORTS = ("SQQQ", "TECS", "SOXS", "PSQ", "SH")
rows, yrows = [], []


def add(t, **kw):
    rows.append({"table": t, **kw})


def yadd(t, **kw):
    yrows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


print("building the environment")
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
o2o, cap_fn, cal = env["o2o"], env["cap_fn"], env["cal"]
panel = env["panels"]["realized"]
acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
ret_panel = pd.DataFrame({t: panel[t].ret_total for t in TICK})
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK} for r in acc["raw_rows"]],
                  index=d.index)
srows = {r["date"]: r for r in sig["rows"]}
HOLD = d.index[d.index >= BOUNDARY]
PRIM = d.index[(d.index >= PRIMARY) & (d.index < BOUNDARY)]
WIN = {"holdout": HOLD, "primary": PRIM}
print(f"  holdout {len(HOLD)} sessions, primary {len(PRIM)} sessions")

# ---- persist the sleeve dictionaries ----------------------------------------------
budget = config.SLEEVE_BUDGET
sw = {}
for sl in SLEEVE_ORDER:
    sw[sl] = pd.DataFrame(
        [{t: (srows[dt]["sleeves"].get(sl) or {}).get(t, 0.0) * budget
          if dt in srows else 0.0 for t in TICK} for dt in d.index], index=d.index)
    sw[sl].to_parquet(OUT / f"_sleeve_weights_{sl}.parquet")
pd.DataFrame({"label": [srows[dt]["label"] if dt in srows else "" for dt in d.index],
              "changed": [int(srows[dt]["changed"]) if dt in srows else 0
                          for dt in d.index],
              "gross_before_cap": [srows[dt]["gross_before_cap"] if dt in srows else None
                                   for dt in d.index],
              "cap_truncated": [int(bool(srows[dt]["cap_truncated"]))
                                if dt in srows else 0 for dt in d.index]},
             index=d.index).to_parquet(OUT / "_signal_rows.parquet")
term = {sl: pd.Series(
    [("|".join(f"{t}={v:g}" for t, v in sorted((srows[dt]["sleeves"].get(sl) or {}).items()))
      or "CASH") if dt in srows else "" for dt in d.index], index=d.index)
    for sl in SLEEVE_ORDER}
pd.DataFrame(term).to_parquet(OUT / "_terminals.parquet")
print("  persisted the per-session sleeve dictionaries and terminals")

# ---- sleeve and instrument attribution -----------------------------------------------
def contrib(weights, idx):
    w = weights.shift(1).reindex(idx).fillna(0.0)
    r = ret_panel.reindex(idx).fillna(0.0)
    return (w * r).sum()


for wname, idx in WIN.items():
    tot = float(d["ret"].reindex(idx).dropna().sum())
    add("window", item=f"{wname}_arithmetic_return_sum", value=q(tot),
        note="the arithmetic sum of daily returns, which the attribution figures sum "
             "toward without reconciling exactly, since compounding and cash are not "
             "attributed")
    for sl in SLEEVE_ORDER:
        c = contrib(sw[sl], idx)
        add("sleeve", item=sl, window=wname, value=q(c.sum()),
            n_sessions=len(idx),
            note="the arithmetic sum of the lagged portfolio weight times the realised "
                 "return, across every instrument the sleeve held")
        for t in sorted(c.index, key=lambda x: -abs(c[x])):
            if abs(c[t]) > 1e-12:
                add("sleeve_instrument", item=f"{sl}:{t}", window=wname, value=q(c[t]))
    ic = contrib(rw, idx)
    ordered = sorted(ic.index, key=lambda x: -ic[x])
    for rk, t in enumerate(ordered, 1):
        if abs(ic[t]) > 1e-12:
            add("instrument", item=t, window=wname, value=q(ic[t]), rank=rk)
    add("instrument_summary", item="largest_positive", window=wname,
        value=q(ic[ordered[0]]), note=ordered[0])
    add("instrument_summary", item="largest_negative", window=wname,
        value=q(ic[ordered[-1]]), note=ordered[-1])
    add("instrument_summary", item="short_sleeve_total", window=wname,
        value=q(sum(ic[t] for t in SHORTS if t in ic)),
        note="the arithmetic sum across " + ", ".join(SHORTS))

# ---- states and terminals ------------------------------------------------------------
allt = {}
for sl in SLEEVE_ORDER:
    for wname, idx in WIN.items():
        vc = term[sl].reindex(idx).value_counts()
        for k, v in vc.items():
            if not k:
                continue
            allt.setdefault((sl, k), {})[wname] = int(v)
        add("sleeve_states", item=sl, window=wname, value=int(vc[vc.index != ""].size),
            n_sessions=len(idx),
            note="distinct terminals the sleeve emitted across the window")
for (sl, k), cnt in sorted(allt.items()):
    h, p = cnt.get("holdout", 0), cnt.get("primary", 0)
    add("terminal", item=f"{sl}:{k}", window="both", value=h,
        primary_count=p, holdout_count=h,
        primary_rate=q(p / len(PRIM)), holdout_rate=q(h / len(HOLD)),
        note=("fired in the holdout and NEVER in the primary window" if p == 0 and h > 0
              else "fired in the primary window and NEVER in the holdout"
              if h == 0 and p > 0 else ""))
first_h = [k for k, c in allt.items() if c.get("primary", 0) == 0 and c.get("holdout", 0)]
only_p = [k for k, c in allt.items() if c.get("holdout", 0) == 0 and c.get("primary", 0)]
add("terminal_summary", item="fired_first_in_the_holdout", value=len(first_h),
    note="; ".join(f"{sl} {k}" for sl, k in first_h) or "none. Every terminal the "
    "holdout exercised had already fired inside the primary window")
add("terminal_summary", item="fired_only_in_the_primary_window", value=len(only_p),
    note="; ".join(f"{sl} {k}" for sl, k in only_p) or "none")

# ---- exposure -------------------------------------------------------------------------
# The leverage multiple lives on the SYNTHETIC panel. The realized loader sets
# multiple to NaN for every levered fund, so reading it from the realized panel
# silently returns gross weight rather than leverage-adjusted exposure. Session 16
# step 3 reads the synthetic panel and this mirrors it.
mult = {}
for t in TICK:
    fr = env["panels"]["synthetic"][t].frame
    mult[t] = (fr["multiple"] if "multiple" in fr.columns and fr["multiple"].notna().any()
               else pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index))
eff = pd.Series(sum(rw[t].to_numpy() * mult[t].reindex(rw.index).fillna(0.0).to_numpy()
                    for t in TICK), index=rw.index)
eff.to_frame("eff_exposure").to_parquet(OUT / "_effective_exposure.parquet")
for wname, idx in WIN.items():
    e = eff.reindex(idx)
    for k, v in (("mean", e.mean()), ("sd", e.std(ddof=1)), ("min", e.min()),
                 ("max", e.max()), ("share_above_1.0", (e > 1.0).mean()),
                 ("share_above_1.7", (e > 1.7).mean())):
        add("exposure", item=k, window=wname, value=q(v),
            note="against the committed primary-window canonical figure of "
                 "1.7769723457408557 at outputs/session-16/exposure-reconciliation.csv"
                 if k == "mean" else "")

# ---- turnover with the mechanism --------------------------------------------------------
orders = acc["orders"].copy()
orders["date"] = pd.to_datetime(orders["date"])
caps = acc["cap_events"].copy()
if len(caps):
    caps["date"] = pd.to_datetime(caps["date"])
nav = d["nav"]
for wname, idx in WIN.items():
    o = orders[(orders["date"] >= idx.min()) & (orders["date"] <= idx.max())]
    ev = sorted(set(o["date"]))
    tv = o.groupby("date")["value"].sum()
    navd = nav.reindex(tv.index).ffill()
    m = L.standalone_metrics(d["ret"].reindex(idx).dropna(), nav.reindex(idx),
                             acc["orders"])
    add("turnover", item="ann_turnover_committed", window=wname,
        value=q(37.87437898045862 if wname == "primary" else 21.026206485079),
        note="from outputs/session-20/rebuilt/metrics-full.csv for the primary window "
             "and outputs/session-27/holdout-ladder.csv for the holdout")
    add("turnover", item="rebalancing_events", window=wname, value=len(ev),
        n_sessions=len(idx))
    add("turnover", item="rebalancing_events_per_session", window=wname,
        value=q(len(ev) / len(idx)))
    add("turnover", item="mean_trade_value_share_of_nav", window=wname,
        value=q((tv / navd).mean()))
    add("turnover", item="median_trade_value_share_of_nav", window=wname,
        value=q((tv / navd).median()))
    add("turnover", item="orders", window=wname, value=len(o))
    if len(caps):
        cw = caps[(caps["date"] >= idx.min()) & (caps["date"] <= idx.max())]
        nt = len(set(cw["date"]))
    else:
        cw, nt = caps, 0
    add("turnover", item="transitions_with_the_participation_cap_binding", window=wname,
        value=nt, n_sessions=len(ev),
        note=f"of {len(ev)} rebalancing events, a share of "
             f"{nt/len(ev) if ev else float('nan'):.6f}")
    add("turnover", item="cap_binding_share_of_events", window=wname,
        value=q(nt / len(ev)) if ev else "")
    add("turnover", item="cap_events", window=wname, value=len(cw))
    add("turnover", item="nav_at_window_start", window=wname,
        value=q(nav.reindex(idx).iloc[0]))
    add("turnover", item="nav_at_window_end", window=wname,
        value=q(nav.reindex(idx).iloc[-1]))
add("turnover", item="turnover_fall_share", window="both",
    value=q(1 - 21.026206485079 / 37.87437898045862),
    note="the holdout annualised turnover against the primary window's")

# ---- drawdown ---------------------------------------------------------------------------
LINES3 = ["STRATEGY", "buy_hold_QQQ", "matched_exposure_levered_QQQ_1.70"]
hl = pd.read_parquet(ROOT / "outputs" / "session-27" / "_holdout_line_returns.parquet")
for ln in LINES3:
    r = hl[ln].dropna()
    g = (1.0 + r).cumprod()
    pk = g.cummax()
    dd = g / pk - 1.0
    tr = dd.idxmin()
    pkdt = g.loc[:tr].idxmax()
    rec = dd.loc[tr:]
    recd = rec[rec >= -1e-12]
    add("drawdown", item=ln, window="holdout", value=q(dd.min()),
        note=f"peak {pkdt.date()}, trough {tr.date()}, "
             f"{int((r.index > pkdt).sum() - (r.index > tr).sum())} sessions from peak "
             f"to trough, {'recovered ' + str(recd.index[0].date()) if len(recd) else 'not recovered inside the span'}")
s_dd = float(hl["STRATEGY"].dropna().pipe(lambda r: ((1+r).cumprod()/(1+r).cumprod().cummax()-1).min()))
q_dd = float(hl["buy_hold_QQQ"].dropna().pipe(lambda r: ((1+r).cumprod()/(1+r).cumprod().cummax()-1).min()))
m_dd = float(hl["matched_exposure_levered_QQQ_1.70"].dropna().pipe(lambda r: ((1+r).cumprod()/(1+r).cumprod().cummax()-1).min()))
add("drawdown_summary", item="strategy_against_buy_hold_QQQ", window="holdout",
    value="deeper" if s_dd < q_dd else "shallower" if s_dd > q_dd else "matched",
    note=f"strategy {s_dd!r} against buy-and-hold QQQ {q_dd!r}")
add("drawdown_summary", item="strategy_against_matched_exposure", window="holdout",
    value="deeper" if s_dd < m_dd else "shallower" if s_dd > m_dd else "matched",
    note=f"strategy {s_dd!r} against the matched-exposure line {m_dd!r}")

# ---- panel availability ------------------------------------------------------------------
av = {}
for t in TICK:
    arr = sig["sig"].avail.get(t)
    ser = (pd.Series(arr, index=cal) if arr is not None
           else pd.Series(False, index=cal))
    av[t] = ser.reindex(d.index).fillna(False).astype(bool)
avdf = pd.DataFrame(av)
for wname, idx in WIN.items():
    a = avdf.reindex(idx)
    add("availability", item="share_of_sessions_every_loaded_ticker_available",
        window=wname, value=q(a.all(axis=1).mean()), n_sessions=len(idx),
        note="every ticker in bt.UNLEVERED plus bt.LEVERED simultaneously available")
    held = rw.reindex(idx) != 0.0
    ok = ((~held) | a).all(axis=1)
    add("availability", item="share_of_sessions_every_held_ticker_available",
        window=wname, value=q(ok.mean()), n_sessions=len(idx),
        note="restricted to the tickers actually held on each session")
add("availability", item="scaffold_figure_0.629", window="primary",
    value=q(avdf.reindex(PRIM).all(axis=1).mean()),
    note="the scaffold names a primary-window realized-available share of 0.629 and the "
         "first definition above reproduces it, so the figure the scaffold quotes is the "
         "share of sessions on which every ticker in the loaded universe is "
         "simultaneously available")

# ---- return distribution --------------------------------------------------------------
for wname, idx in WIN.items():
    x = d["ret"].reindex(idx).dropna().to_numpy()
    nn = len(x); mu, sd = float(x.mean()), float(x.std(ddof=1))
    z = (x - mu) / sd
    add("distribution", item="n_sessions", window=wname, value=nn)
    add("distribution", item="daily_mean", window=wname, value=q(mu))
    add("distribution", item="daily_sd", window=wname, value=q(sd))
    add("distribution", item="skewness", window=wname,
        value=q((z ** 3).mean() * nn * nn / ((nn - 1) * (nn - 2))))
    add("distribution", item="excess_kurtosis", window=wname,
        value=q((nn * (nn + 1) / ((nn - 1) * (nn - 2) * (nn - 3))) * (z ** 4).sum()
                - 3 * (nn - 1) ** 2 / ((nn - 2) * (nn - 3))))

fn = ["table", "item", "window", "value", "rank", "n_sessions", "primary_count",
      "holdout_count", "primary_rate", "holdout_rate", "note"]
with open(OUT / "holdout-decomposition.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote holdout-decomposition.csv, {len(rows)} rows")

# =========================== PHASE E, the year split =====================================
rf_all = bt.rf_per_session(hl.index).reindex(hl.index).fillna(0.0)
years = sorted({dt.year for dt in HOLD})
for y in years:
    idx = hl.index[hl.index.year == y]
    vals = {}
    for ln in hl.columns:
        r = hl[ln].reindex(idx).dropna()
        if len(r) < 2:
            continue
        nav_y = (1.0 + r).cumprod()
        m = L.standalone_metrics(r, nav_y, None)
        dd = float((nav_y / nav_y.cummax() - 1.0).min())
        vals[ln] = m
        yadd("year_line", item=ln, year=y, n_sessions=len(r),
             ann_return=q(m["ann_return"]), sharpe_naive=q(m["sharpe_naive"]),
             sharpe_lo=q(m["sharpe_lo"]), max_drawdown=q(dd))
    order = sorted(vals, key=lambda k: -vals[k]["sharpe_naive"])
    yadd("year_rank", item="STRATEGY", year=y,
         value=order.index("STRATEGY") + 1, n_sessions=len(order),
         note="rank on the naive Sharpe among the twelve ladder rows")
    ordl = sorted(vals, key=lambda k: -vals[k]["sharpe_lo"])
    yadd("year_rank_lo", item="STRATEGY", year=y,
         value=ordl.index("STRATEGY") + 1, n_sessions=len(ordl))
    yadd("year_meta", item="partial", year=y,
         value=int(y in (years[0], years[-1])),
         note=f"{len(hl.index[hl.index.year == y])} sessions in the span")

# concentration of the outperformance by year
sy = {}
for y in years:
    idx = hl.index[hl.index.year == y]
    s_r = float(hl["STRATEGY"].reindex(idx).dropna().sum())
    q_r = float(hl["buy_hold_QQQ"].reindex(idx).dropna().sum())
    sy[y] = s_r - q_r
    yadd("year_gap", item="strategy_minus_buy_hold_QQQ", year=y, value=q(s_r - q_r),
         ann_return=q(s_r), sharpe_naive=q(q_r),
         note="arithmetic sums of daily returns across the calendar year, the strategy "
              "first and buy-and-hold QQQ second")
tot_gap = sum(sy.values())
top = max(sy, key=lambda k: sy[k])
yadd("year_summary", item="total_gap", value=q(tot_gap))
yadd("year_summary", item="largest_single_year_gap", year=top, value=q(sy[top]),
     note=f"a share of {sy[top]/tot_gap:.6f} of the total gap" if tot_gap else "")
yadd("year_summary", item="years_with_a_positive_gap",
     value=sum(1 for v in sy.values() if v > 0), n_sessions=len(years))
yadd("year_summary", item="concentration",
     value="concentrated" if tot_gap and sy[top] / tot_gap > 0.5 else "spread",
     note="concentrated is recorded when one calendar year carries more than half the "
          "total arithmetic gap against buy-and-hold QQQ")

# 2022 separately
i22 = hl.index[hl.index.year == 2022]
s22 = float(hl["STRATEGY"].reindex(i22).dropna().sum())
q22 = float(hl["buy_hold_QQQ"].reindex(i22).dropna().sum())
sc22 = float(contrib(rw, i22)[list(SHORTS)].sum())
yadd("year_2022", item="strategy_arithmetic_return", year=2022, value=q(s22))
yadd("year_2022", item="buy_hold_QQQ_arithmetic_return", year=2022, value=q(q22))
yadd("year_2022", item="short_sleeve_contribution", year=2022, value=q(sc22),
     note="the arithmetic sum across " + ", ".join(SHORTS))
yadd("year_2022", item="sessions", year=2022, value=len(i22))

fn2 = ["table", "item", "year", "value", "n_sessions", "ann_return", "sharpe_naive",
       "sharpe_lo", "max_drawdown", "note"]
with open(OUT / "holdout-by-year.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn2, extrasaction="ignore")
    w.writeheader(); w.writerows(yrows)
print(f"wrote holdout-by-year.csv, {len(yrows)} rows")
print(f"  terminals firing first in the holdout: {len(first_h)}")
print(f"  years: {years}, largest gap in {top}")
