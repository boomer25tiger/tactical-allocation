"""Session 13.7 step 9 — ablation mechanism decomposition.

Reads the rebuilt anchor run (_anchor_run.pkl). Decomposes:
  UVXY:  r_syn = M x r_index + reset/fee residual, and r_index =
         constant-maturity price change (cdr) + roll yield — so each held
         episode splits into directional (M x cm30 price change), roll
         (M x (index - price change)), and reset/fee residual.
  Short equity: per instrument, beta component (M x underlying while
         held) vs residual (fee/decay/tracking), plus timing (underlying
         return on held vs all sessions).
"""
from __future__ import annotations

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

# Staged in session 13.7 (halted before step 6 produced an anchor run);
# executed by session 13.8 step 10 against the 13.8 canonical anchor.
OUT = ROOT / "outputs" / "session-13.8"
rows = []

st = pickle.load(open(OUT / "_anchor_run.pkl", "rb"))
daily = st["daily"]
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                   for r in st["raw_rows"]], index=daily.index)

# --- VX decomposition inputs ------------------------------------------------
vx = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30-b.parquet")
vx = vx.set_index(pd.to_datetime(vx["trade_date"]).dt.normalize())
vx = vx[~vx.index.duplicated(keep="last")]
idx_ret = vx["index_level"].astype(float).pct_change()
# constant-maturity PRICE (interpolated settle, construction A file): its
# change omits the roll yield, so roll = index return - price change.
cma = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30.parquet")
cma = cma.set_index(pd.to_datetime(cma["trade_date"]).dt.normalize())
cma = cma[~cma.index.duplicated(keep="last")]
cm30 = cma["cm30_settle"].astype(float)
cm_price_ret = cm30.pct_change().reindex(vx.index)
syn_u = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / "SYN_UVXY.parquet")
syn_u.index = pd.to_datetime(syn_u.index).normalize()

# positive control: the synthetic's stored underlying_ret must equal the
# construction-B index return on overlapping sessions.
j = pd.DataFrame({"u": syn_u["underlying_ret"], "i": idx_ret}).dropna()
ctrl_gap = float((j["u"] - j["i"]).abs().max())
assert ctrl_gap < 1e-9, f"positive control failed: underlying_ret vs index ret gap {ctrl_gap}"
print(f"positive control: SYN_UVXY underlying_ret == construction-B index return "
      f"(max gap {ctrl_gap:.1e}) PASS")

M_u = syn_u["multiple"].astype(float)
r_syn = syn_u["syn_ret"].astype(float)
dir_comp = (M_u * cm_price_ret.reindex(syn_u.index)).rename("directional")
roll_comp = (M_u * (idx_ret.reindex(syn_u.index) - cm_price_ret.reindex(syn_u.index))).rename("roll")
reset_comp = (r_syn - M_u * idx_ret.reindex(syn_u.index)).rename("reset_fee")

held_u = (rw["UVXY"].shift(1) > 0)
w_u = rw["UVXY"].shift(1)
comp = pd.DataFrame({"dir": dir_comp, "roll": roll_comp, "reset": reset_comp,
                     "syn": r_syn}).reindex(daily.index)
comp_h = comp[held_u.fillna(False)]
wcomp = comp.multiply(w_u, axis=0)[held_u.fillna(False)]

# episodes
h = held_u.fillna(False).astype(int)
ep_id = (h.diff() == 1).cumsum() * h
episodes = []
for eid, g in comp[h == 1].groupby(ep_id[h == 1]):
    tot = float((1 + g["syn"]).prod() - 1)
    episodes.append({"start": g.index[0], "len": len(g), "total": tot,
                     "dir": float(g["dir"].sum()), "roll": float(g["roll"].sum()),
                     "reset": float(g["reset"].sum())})
ep = pd.DataFrame(episodes)
rows.append({"table": "uvxy_overlay", "metric": "n_episodes", "value": len(ep)})
rows.append({"table": "uvxy_overlay", "metric": "mean_episode_len", "value": float(ep["len"].mean())})
rows.append({"table": "uvxy_overlay", "metric": "median_episode_len", "value": float(ep["len"].median())})
for q in (0.1, 0.25, 0.5, 0.75, 0.9):
    rows.append({"table": "uvxy_overlay", "metric": f"episode_return_q{q}",
                 "value": float(ep["total"].quantile(q))})
# loss split: decay (roll+reset) vs directional, arithmetic on weighted comps
tot_dir = float(wcomp["dir"].sum())
tot_roll = float(wcomp["roll"].sum())
tot_reset = float(wcomp["reset"].sum())
tot_all = tot_dir + tot_roll + tot_reset
rows.append({"table": "uvxy_overlay", "metric": "portfolio_contrib_directional_arith", "value": tot_dir})
rows.append({"table": "uvxy_overlay", "metric": "portfolio_contrib_roll_arith", "value": tot_roll})
rows.append({"table": "uvxy_overlay", "metric": "portfolio_contrib_reset_fee_arith", "value": tot_reset})
rows.append({"table": "uvxy_overlay", "metric": "decay_share_of_total",
             "value": (tot_roll + tot_reset) / tot_all if tot_all else np.nan,
             "note": "decay = roll + reset/fee; directional = M x cm30 price change"})
print(f"UVXY overlay: {len(ep)} episodes, contribs dir {tot_dir:+.4f} "
      f"roll {tot_roll:+.4f} reset {tot_reset:+.4f}")
# per year
for y, g in wcomp.groupby(wcomp.index.year):
    ge = ep[pd.DatetimeIndex(ep["start"]).year == y]
    rows.append({"table": "uvxy_by_year", "year": int(y),
                 "directional": float(g["dir"].sum()), "roll": float(g["roll"].sum()),
                 "reset_fee": float(g["reset"].sum()),
                 "carry_cost": float(g["roll"].sum() + g["reset"].sum()),
                 "n_episodes": len(ge),
                 "full_detail": y in (2018, 2020)})
# entry-day split
fills = daily["transition"]
first_day = fills.shift(1).fillna(False).astype(bool)
entry_u = first_day & held_u.fillna(False) & (~held_u.shift(1).fillna(False))
eh = comp[entry_u]
rows.append({"table": "uvxy_entry_split", "metric": "first_day_mean_total",
             "value": float(eh["syn"].mean()), "n": int(len(eh))})
for c, lbl in (("dir", "directional"), ("roll", "roll"), ("reset", "reset_fee")):
    rows.append({"table": "uvxy_entry_split", "metric": f"first_day_mean_{lbl}",
                 "value": float(eh[c].mean())})
print(f"UVXY entries: first-day total {eh['syn'].mean():+.5f} = dir {eh['dir'].mean():+.5f} "
      f"+ roll {eh['roll'].mean():+.5f} + reset {eh['reset'].mean():+.5f} (n={len(eh)})")

# --- short-equity decomposition --------------------------------------------
SHORTS = {"SQQQ": ("QQQ", -3), "PSQ": ("QQQ", -1), "TECS": ("XLK", -3),
          "SOXS": ("SOXX", -3)}
und_frames = {"QQQ": bt._frozen_frame("QQQ"), "XLK": bt._frozen_frame("XLK"),
              "SOXX": bt._frozen_frame("SOXX")}
port_ret = daily["ret"]
for t, (u, M) in SHORTS.items():
    syn = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")
    syn.index = pd.to_datetime(syn.index).normalize()
    r_f = syn["syn_ret"].astype(float).reindex(daily.index)
    r_u = und_frames[u].ret_total.reindex(daily.index)
    w = rw[t].shift(1)
    held = (w > 0).fillna(False)
    beta = (w * M * r_u)[held]
    resid = (w * (r_f - M * r_u))[held]
    tot = (w * r_f)[held]
    und_held = float(r_u[held].mean())
    und_all = float(r_u.mean())
    rows.append({"table": "short_equity", "ticker": t,
                 "total_contrib_arith": float(tot.sum()),
                 "beta_component": float(beta.sum()),
                 "residual_fee_decay": float(resid.sum()),
                 "timing_underlying_mean_held_vs_all": f"{und_held:+.5f} vs {und_all:+.5f}",
                 "n_held_sessions": int(held.sum())})
    for y, g in tot.groupby(tot.index.year):
        if abs(g.sum()) > 0.002:
            rows.append({"table": "short_equity_by_year", "ticker": t, "year": int(y),
                         "total": float(g.sum()),
                         "beta": float(beta[beta.index.year == y].sum()),
                         "residual": float(resid[resid.index.year == y].sum())})
    print(f"{t}: total {tot.sum():+.4f} = beta {beta.sum():+.4f} + resid {resid.sum():+.4f}; "
          f"underlying held-mean {und_held:+.5f} vs all {und_all:+.5f}")

# --- hedge correlation ------------------------------------------------------
uvxy_slice = (rw["UVXY"].shift(1) * comp["syn"].reindex(daily.index)).fillna(0.0)
short_slice = pd.Series(0.0, index=daily.index)
for t, (u, M) in SHORTS.items():
    syn = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")
    syn.index = pd.to_datetime(syn.index).normalize()
    short_slice = short_slice + (rw[t].shift(1).fillna(0.0) *
                                 syn["syn_ret"].astype(float).reindex(daily.index).fillna(0.0))
rest_u = port_ret - uvxy_slice
rest_s = port_ret - short_slice
m_u = uvxy_slice != 0
m_s = short_slice != 0
rows.append({"table": "hedge_correlation", "component": "UVXY_overlay",
             "corr_vs_rest_of_portfolio": float(uvxy_slice[m_u].corr(rest_u[m_u])),
             "n": int(m_u.sum())})
rows.append({"table": "hedge_correlation", "component": "short_equity",
             "corr_vs_rest_of_portfolio": float(short_slice[m_s].corr(rest_s[m_s])),
             "n": int(m_s.sum())})
print("hedge correlations:",
      float(uvxy_slice[m_u].corr(rest_u[m_u])),
      float(short_slice[m_s].corr(rest_s[m_s])))

pd.DataFrame(rows).to_csv(OUT / "ablation-mechanism.csv", index=False)
print(f"[wrote ablation-mechanism.csv: {len(rows)} rows]")
