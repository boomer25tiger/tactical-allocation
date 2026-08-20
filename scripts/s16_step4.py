"""Session 16 step 4: leave-one-calendar-year-out robustness."""
from __future__ import annotations
import math, sys, pickle
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt, scripts.s13_runall as ra
import scripts.s14_common as C, scripts.s15_lines as L
from src import config
from src.portfolio import SLEEVE_ORDER
import os as _os
OUT = ROOT / "outputs" / (_os.environ.get("S20_OUTDIR") or "session-16")
OUT.mkdir(parents=True, exist_ok=True)
NEW_START = pd.Timestamp("2011-10-04")
env = L.build_env(); cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]; TICK = list(ra.TARGET_TICKERS)
LINES = L.make_lines(cal)
rows = []

def acc_of(rows_in, conv="o2o"):
    panel = o2o if conv == "o2o" else panels["realized"]
    return bt.run_account(sigs["realized"]["sig"], panel, rows_in, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM],
                          slip_fn=C.slip_class_premium() if conv == "o2o" else C.slip_class,
                          cap_fn=cap_fn)

accS = acc_of(sigs["realized"]["rows"])
r_full = accS["daily"]["ret"]; r_full = r_full[r_full.index >= NEW_START].dropna()
# benchmark for the information ratio
lad = pickle.load(open(ROOT / "outputs" / "session-14" / "_ladder_returns.pkl", "rb"))
bench = lad["lines"][("buy_hold_QQQ", "o2o", "primary")]
bench = bench[bench.index >= NEW_START]

def loo_metrics(r, b=None):
    m = L.standalone_metrics(r)
    out = {k: m[k] for k in ("ann_return", "sharpe_lo", "max_drawdown", "ann_vol")}
    if b is not None:
        rel = L.relative_metrics(r, b.reindex(r.index).dropna())
        out["information_ratio_vs_buy_hold_QQQ"] = rel.get("information_ratio", np.nan)
    return out

base = loo_metrics(r_full, bench)
rows.append({"table": "loo", "series": "STRATEGY", "dropped_year": "none (base)", **base})
years = sorted(set(r_full.index.year))
for y in years:
    r = r_full[r_full.index.year != y]
    rows.append({"table": "loo", "series": "STRATEGY", "dropped_year": int(y),
                 **loo_metrics(r, bench)})
sd = pd.DataFrame([r for r in rows if r["table"] == "loo" and r["series"] == "STRATEGY"
                   and r["dropped_year"] != "none (base)"])
rng = {k: (float(sd[k].min()), float(sd[k].max())) for k in
       ("ann_return", "sharpe_lo", "max_drawdown")}
worst = sd.loc[(sd.sharpe_lo - base["sharpe_lo"]).abs().idxmax()]
rows.append({"table": "loo_range", "series": "STRATEGY",
             "ann_return_min": rng["ann_return"][0], "ann_return_max": rng["ann_return"][1],
             "sharpe_lo_min": rng["sharpe_lo"][0], "sharpe_lo_max": rng["sharpe_lo"][1],
             "max_drawdown_min": rng["max_drawdown"][0], "max_drawdown_max": rng["max_drawdown"][1],
             "base_sharpe_lo": base["sharpe_lo"],
             "year_moving_sharpe_most": int(worst.dropped_year),
             "sharpe_when_that_year_dropped": float(worst.sharpe_lo),
             "n_estimates": int(len(sd))})
print(f"  STRATEGY base SR {base['sharpe_lo']:.4f}; LOO range "
      f"{rng['sharpe_lo'][0]:.4f}..{rng['sharpe_lo'][1]:.4f}; "
      f"largest move on dropping {int(worst.dropped_year)} -> {worst.sharpe_lo:.4f}")
# 2020-excluded equity curve summary
r_ex = r_full[r_full.index.year != 2020]
g = (1 + r_ex).cumprod()
rows.append({"table": "ex_2020_curve", "series": "STRATEGY",
             "total_growth": float(g.iloc[-1]), "ann_return": base["ann_return"],
             "ann_return_ex_2020": float(g.iloc[-1] ** (252/len(r_ex)) - 1),
             "max_drawdown_ex_2020": float((g / g.cummax() - 1).min()),
             "max_drawdown_with_2020": base["max_drawdown"]})
# per sleeve
for k in SLEEVE_ORDER:
    rws = LINES[f"sleeve_{k}_standalone"][0](o2o, sigs["realized"]["rows"], 0)
    a = acc_of(rws)
    rs = a["daily"]["ret"]; rs = rs[rs.index >= NEW_START].dropna()
    bs = loo_metrics(rs, bench)
    rows.append({"table": "loo", "series": f"SLEEVE_{k}", "dropped_year": "none (base)", **bs})
    vals = []
    for y in years:
        m = loo_metrics(rs[rs.index.year != y], bench)
        vals.append(m["sharpe_lo"])
        rows.append({"table": "loo", "series": f"SLEEVE_{k}", "dropped_year": int(y), **m})
    rows.append({"table": "loo_range", "series": f"SLEEVE_{k}",
                 "sharpe_lo_min": float(np.min(vals)), "sharpe_lo_max": float(np.max(vals)),
                 "base_sharpe_lo": bs["sharpe_lo"],
                 "year_moving_sharpe_most": int(years[int(np.argmax(np.abs(np.array(vals)-bs["sharpe_lo"])))]),
                 "n_estimates": len(vals)})
    print(f"  SLEEVE_{k} base SR {bs['sharpe_lo']:.4f}; LOO range "
          f"{np.min(vals):.4f}..{np.max(vals):.4f}")
# short leg through the 2020 crash
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK}
                   for r in accS["raw_rows"]], index=accS["daily"].index)
sq = (rw["SQQQ"].shift(1) * o2o["SQQQ"].ret_total.reindex(rw.index)).fillna(0.0)
w = rw["SQQQ"]
seg = slice(pd.Timestamp("2020-02-01"), pd.Timestamp("2020-04-30"))
held = (w > 0)
entries = w.index[held & ~held.shift(1).fillna(False).astype(bool)]
exits = w.index[(~held) & held.shift(1).fillna(False).astype(bool)]
for d in sq.loc[seg].index:
    rows.append({"table": "short_leg_2020", "date": str(d.date()),
                 "sqqq_weight_lagged": float(rw["SQQQ"].shift(1).loc[d]),
                 "daily_contribution": float(sq.loc[d]),
                 "is_entry": bool(d in set(entries)), "is_exit": bool(d in set(exits))})
rows.append({"table": "short_leg_2020_summary",
             "feb_apr_2020_total_contribution": float(sq.loc[seg].sum()),
             "n_entries": int(sum(1 for d in entries if seg.start <= d <= seg.stop)),
             "n_exits": int(sum(1 for d in exits if seg.start <= d <= seg.stop)),
             "full_2020_contribution": float(sq[sq.index.year == 2020].sum()),
             "primary_window_total": float(sq[sq.index >= NEW_START].sum())})
print(f"  SQQQ Feb-Apr 2020 contribution {sq.loc[seg].sum():+.4f}, "
      f"full 2020 {sq[sq.index.year==2020].sum():+.4f}, "
      f"primary window {sq[sq.index>=NEW_START].sum():+.4f}")
pd.DataFrame(rows).to_csv(OUT / "leave-one-out.csv", index=False)
print(f"[wrote leave-one-out.csv: {len(rows)} rows]")
