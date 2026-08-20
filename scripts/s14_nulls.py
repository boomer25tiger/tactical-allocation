"""Session 14 step 2: the 8.9 nulls and the 8.10 Romano-Wolf family.

Two nulls per the register. The timing shuffle permutes the strategy's own
episode sequence, so the distribution of held compositions and the
holding-period structure are preserved exactly and only the placement in
time is randomised. The turnover-matched switching null draws compositions
from the strategy's empirical composition distribution at the measured
transition rate.

Cost treatment, disclosed: each null draw is charged the strategy's own
measured mean per-transition cost fraction rather than re-deriving integer
share counts per draw, so the cost model is identical in expectation and
the 1,000-draw budget stays tractable.
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
import scripts.s14_common as C
from src import config
from src.portfolio import SLEEVE_ORDER, sleeve_label

OUT = C.OUT
import os as _os
# Session 22. Both overrides are absent by default, so unset environment
# reproduces the registered behaviour exactly.
N_DRAWS = int(_os.environ.get("S22_NDRAWS") or 1000)   # register-fixed under 8.9
_NULLS_ONLY = bool(_os.environ.get("S22_NULLS_ONLY"))
RNG = np.random.default_rng(20260818)

env = C.build_env()
cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]
TICK = list(ra.TARGET_TICKERS)

rows = []
rows.append({"table": "draw_count", "n_draws": N_DRAWS,
             "register_fixed": True,
             "note": "8.8/8.9 as recorded in session 12.6 fix 1,000 draws; the "
                     "count was fixed in the register before any result existed "
                     "and is not chosen here"})


def run_strategy(conv):
    panel = o2o if conv == "o2o" else panels["realized"]
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    return bt.run_account(sigs["realized"]["sig"], panel, sigs["realized"]["rows"],
                          C.ANCHOR, commission_fn=C.ARMS[C.CANONICAL_ARM],
                          slip_fn=sf, cap_fn=cap_fn)


def ret_matrix(conv):
    panel = o2o if conv == "o2o" else panels["realized"]
    return np.column_stack([panel[t].ret_total.reindex(cal).fillna(0.0).to_numpy()
                            for t in TICK])


def episodes_and_cost(acc, conv):
    """Strategy episodes (composition vector, length) plus the measured mean
    per-transition cost fraction of NAV."""
    daily = acc["daily"]
    idx = {d: i for i, d in enumerate(cal)}
    comps, lens = [], []
    cur, run = None, 0
    rw = [{t: r["weights"].get(t, 0.0) for t in TICK} for r in acc["raw_rows"]]
    tr = daily["transition"].to_numpy()
    for j in range(len(daily)):
        vec = np.array([rw[j][t] for t in TICK])
        if tr[j] or cur is None:
            if cur is not None:
                comps.append(cur)
                lens.append(run)
            cur, run = vec, 1
        else:
            run += 1
    comps.append(cur)
    lens.append(run)
    od = acc["orders"]
    if len(od):
        cost = od.groupby("date").apply(lambda g: g["commission"].sum() + g["slippage"].sum())
        navp = daily["nav"].shift(1).reindex(cost.index)
        cost_frac = float((cost / navp).mean())
    else:
        cost_frac = 0.0
    return np.array(comps), np.array(lens), cost_frac


def draw_returns(comps, lens, R, n, cost_frac, mode, rate=None):
    """One null path of length n. mode 'shuffle' permutes the episode
    sequence; mode 'switch' draws compositions at the measured rate."""
    Wm = np.zeros((n, R.shape[1]))
    trans = np.zeros(n, dtype=bool)
    pos = 0
    if mode == "shuffle":
        order = RNG.permutation(len(comps))
        for k in order:
            L = lens[k]
            if pos >= n:
                break
            end = min(pos + L, n)
            Wm[pos:end] = comps[k]
            trans[pos] = True
            pos = end
        while pos < n:                      # top up if episodes run short
            k = RNG.integers(len(comps))
            end = min(pos + lens[k], n)
            Wm[pos:end] = comps[k]
            trans[pos] = True
            pos = end
    else:
        cur = comps[RNG.integers(len(comps))]
        for t in range(n):
            if t == 0 or RNG.random() < rate:
                cur = comps[RNG.integers(len(comps))]
                trans[t] = True
            Wm[t] = cur
    port = np.sum(Wm[:-1] * R[1:n], axis=1)
    port = np.concatenate([[0.0], port])
    port = port - trans * cost_frac
    return port


def lo_sharpe_fast(x: np.ndarray, q: int = 252) -> float:
    """Vectorised Lo (2002) correction, identical to bt.lo_sharpe.

    bt.lo_sharpe is used per draw in the loop below and its per-call cost is
    dominated by pandas work in the caller rather than the recursion here;
    this form takes a plain array so the 1,000-draw budget stays tractable.
    An equality control against bt.lo_sharpe runs before the loops.
    """
    mu, sd = x.mean(), x.std(ddof=1)
    if sd == 0:
        return float("nan")
    n = len(x)
    xc = x - mu
    denom = float(np.dot(xc, xc))
    ks = np.arange(1, q)
    acf_sum = 0.0
    for k in ks:
        acf_sum += (q - k) * float(np.dot(xc[:-k], xc[k:])) / denom
    scale_sq = q + 2.0 * acf_sum
    if scale_sq <= 0:
        return float("nan")
    return float(mu / sd * q / math.sqrt(scale_sq))


def make_stats(dates):
    """Bind the per-session risk-free series once for a window; recomputing
    it per draw reloads the rate file and re-slices it 2,500 times, which
    dominates the runtime."""
    rf = bt.rf_per_session(dates).fillna(0.0).to_numpy()[1:]
    n = len(dates) - 1

    def stats(r):
        s = np.asarray(r)[1:]
        ann = float(np.prod(1 + s) ** (252 / n) - 1)
        return ann, lo_sharpe_fast(s - rf)
    return stats


for conv in (("o2o",) if _NULLS_ONLY else ("o2o", "c2c")):
    acc = run_strategy(conv)
    R = ret_matrix(conv)
    comps, lens, cost_frac = episodes_and_cost(acc, conv)
    daily = acc["daily"]
    rate = float(daily["transition"].mean())
    rows.append({"table": "null_setup", "convention": conv,
                 "n_episodes": len(comps), "mean_episode_len": float(lens.mean()),
                 "median_episode_len": float(np.median(lens)),
                 "measured_transition_rate_per_session": rate,
                 "measured_transitions_per_year": rate * 252,
                 "mean_cost_frac_per_transition": cost_frac})
    off = len(cal) - len(daily)
    for wname in ("full", "primary"):
        if conv == "o2o" and wname != "primary":
            continue
        sl = C.window_slice(daily["ret"], wname)
        dates = sl.index
        n = len(dates)
        i0 = list(daily.index).index(dates[0]) + off
        Rw = R[i0:i0 + n]
        mo = C.metrics(sl)
        obs_ann, obs_sr = mo["ann_return"], mo["sharpe_lo"]
        stats = make_stats(dates)
        # equality control: the fast Lo form must reproduce bt.lo_sharpe on
        # the observed series before any null draw is read
        rf_ctl = bt.rf_per_session(dates).fillna(0.0)
        ctl_fast = lo_sharpe_fast((sl - rf_ctl).dropna().to_numpy())
        ctl_ref = bt.lo_sharpe((sl - rf_ctl).dropna())
        assert abs(ctl_fast - ctl_ref) < 1e-9, "fast Lo Sharpe diverges from bt.lo_sharpe"
        rows.append({"table": "lo_sharpe_control", "convention": conv, "window": wname,
                     "fast": ctl_fast, "reference": ctl_ref, "abs_gap": abs(ctl_fast - ctl_ref)})
        for mode, label in (("shuffle", "timing_shuffle_block_bootstrap"),
                            ("switch", "turnover_matched_switching")):
            anns, srs = [], []
            for _ in range(N_DRAWS):
                p = draw_returns(comps, lens, Rw, n, cost_frac, mode, rate)
                a, s_ = stats(p)
                anns.append(a)
                srs.append(s_)
            anns, srs = np.array(anns), np.array(srs)
            rows.append({"table": "null_distribution", "convention": conv,
                         "window": wname, "null": label, "n_draws": N_DRAWS,
                         "observed_ann_return": obs_ann, "observed_sharpe_lo": obs_sr,
                         "null_ann_mean": float(anns.mean()),
                         "null_ann_p05": float(np.percentile(anns, 5)),
                         "null_ann_p50": float(np.percentile(anns, 50)),
                         "null_ann_p95": float(np.percentile(anns, 95)),
                         "null_ann_max": float(anns.max()),
                         "strategy_percentile_ann": float((anns < obs_ann).mean() * 100),
                         "p_value_ann_one_sided": float((anns >= obs_ann).mean()),
                         "null_sharpe_mean": float(np.nanmean(srs)),
                         "null_sharpe_p95": float(np.nanpercentile(srs, 95)),
                         "null_sharpe_max": float(np.nanmax(srs)),
                         "strategy_percentile_sharpe": float((srs < obs_sr).mean() * 100),
                         "p_value_sharpe_one_sided": float((srs >= obs_sr).mean())})
            print(f"  [{conv} {wname} {label}] obs ann {obs_ann:.4f} "
                  f"pct {(anns < obs_ann).mean()*100:.1f}; obs SR {obs_sr:.3f} "
                  f"pct {(srs < obs_sr).mean()*100:.1f}")

# ---------------------------------------------------------------------------
# 8.10 Romano-Wolf family over the ladder differences, designated cell
# ---------------------------------------------------------------------------
print("== Romano-Wolf family ==")
lad = pickle.load(open(OUT / "_ladder_returns.pkl", "rb"))
strat = C.window_slice(lad["strategy"][("o2o", "primary")], "primary")
fam = {}
for key, s in lad["lines"].items():
    name, conv, wname = key
    if conv != "o2o" or wname != "primary":
        continue
    fam[name] = C.window_slice(s, "primary")
D = pd.DataFrame({k: (strat - v) for k, v in fam.items()}).dropna()
names = list(D.columns)
X = D.to_numpy()
n, k = X.shape
t_obs = X.mean(axis=0) / (X.std(axis=0, ddof=1) / math.sqrt(n))
BL = 21
nb = n // BL
Xc = X - X.mean(axis=0)
if not _NULLS_ONLY:
    tstar = np.zeros((N_DRAWS, k))
    for b in range(N_DRAWS):
        starts = RNG.integers(0, n - BL, size=nb)
        idx = np.concatenate([np.arange(s, s + BL) for s in starts])
        Xb = Xc[idx]
        tstar[b] = Xb.mean(axis=0) / (Xb.std(axis=0, ddof=1) / math.sqrt(len(idx)))
    order = np.argsort(-t_obs)
    remaining = list(order)
    adj = {}
    while remaining:
        maxstat = np.max(tstar[:, remaining], axis=1)
        j = remaining[0]
        p = float((maxstat >= t_obs[j]).mean())
        prev = max(adj.values()) if adj else 0.0
        adj[j] = max(p, prev)
        remaining = remaining[1:]
    for j in range(k):
        rows.append({"table": "romano_wolf", "hypothesis": f"strategy_minus_{names[j]}",
                     "mean_daily_diff": float(X[:, j].mean()),
                     "t_stat": float(t_obs[j]),
                     "rw_adjusted_p": adj[j],
                     "family_size": k,
                     "note": "one-sided, stationary block bootstrap, block 21 sessions, "
                             f"{N_DRAWS} draws, designated cell (o2o realized primary)"})
        print(f"  {names[j]}: t {t_obs[j]:+.2f}, RW-adj p {adj[j]:.3f}")

    # ensemble against the best single sleeve, post-hoc, joins the family
    sl_names = [nm for nm in names if nm.startswith("sleeve_")]
    if sl_names:
        best = max(sl_names, key=lambda nm: C.metrics(fam[nm])["sharpe_lo"])
        j = names.index(best)
        rows.append({"table": "ensemble_vs_best_sleeve", "best_sleeve_line": best,
                     "best_sleeve_sharpe_lo": C.metrics(fam[best])["sharpe_lo"],
                     "strategy_sharpe_lo": C.metrics(strat)["sharpe_lo"],
                     "rw_adjusted_p": adj[j],
                     "disclosure": "post-hoc under 9.10: the best single sleeve is "
                                   "identified after the sleeve tracks were measured, "
                                   "and the comparison joins the 8.10 Romano-Wolf "
                                   "family rather than standing as a separate test"})
        print(f"  best single sleeve: {best}")

    # pairwise correlation of the four standalone tracks
    corr_names = [nm for nm in fam if nm.startswith("sleeve_")]
    Cm = pd.DataFrame({nm: fam[nm] for nm in corr_names}).dropna().corr()
    for a in corr_names:
        for b in corr_names:
            if a < b:
                rows.append({"table": "sleeve_pairwise_correlation", "pair": f"{a}|{b}",
                             "correlation": float(Cm.loc[a, b])})
pd.DataFrame(rows).to_csv(OUT / "nulls.csv", index=False)
print(f"[wrote nulls.csv: {len(rows)} rows]")
