"""Session 13 — full pipeline: run, headline, diagnostics, sanity, sub-periods.

Produces every output file the session prompt names. Imports the engine
from scripts/s13_backtest.py; computes everything in one process.
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
from src import config
from src.portfolio import SLEEVE_ORDER, sleeve_label, merge, apply_gross_cap

OUT = bt.OUT
ANCHOR_BP = 10  # 4.4 Zarattini anchor; a member of SLIPPAGE_BASE_GRID_BP
assert ANCHOR_BP in config.SLIPPAGE_BASE_GRID_BP

TARGET_TICKERS = ("UVXY", "SVXY", "TECL", "TECS", "SOXL", "SOXS", "SPXL",
                  "LABU", "SQQQ", "TQQQ", "QLD", "PSQ", "QQQ", "TLT", "BIL",
                  "BTAL", "BSV")

# ---------------------------------------------------------------------------
# Branch tracer: mirrors src/sleeves.py branch-by-branch, and is asserted
# equal to the recorded sleeve outputs on EVERY session (positive control).
# ---------------------------------------------------------------------------

def _a(v):  # available
    return v is not None and not (isinstance(v, float) and math.isnan(v))

def _gt(v, b): return _a(v) and v > b
def _lt(v, b): return _a(v) and v < b

def _pas(st, t, n):
    p, m = st.price(t), st.sma(t, n)
    return _a(p) and _a(m) and p > m

def _pbs(st, t, n):
    p, m = st.price(t), st.sma(t, n)
    return _a(p) and _a(m) and p < m


def trace_t10(st):
    from src.sleeves import T10_CASCADE
    ex, dip, rs = st.rsi_exhaustion, st.rsi_dip, st.rsi_rs
    reach = ["cascade"]
    if any(_gt(ex(t), config.OVERBOUGHT_TIER_1) for t in T10_CASCADE):
        return "overbought->UVXY", {"UVXY": 1.0}, reach
    reach.append("dip_TQQQ")
    if _lt(dip("TQQQ"), config.OVERSOLD):
        return "dip_TQQQ->TECL", {"TECL": 1.0}, reach
    reach.append("dip_SOXL")
    if _lt(dip("SOXL"), config.OVERSOLD):
        return "dip_SOXL->SOXL", {"SOXL": 1.0}, reach
    reach.append("dip_SPXL")
    if _lt(dip("SPXL"), config.OVERSOLD):
        return "dip_SPXL->SPXL", {"SPXL": 1.0}, reach
    reach.append("dip_LABU")
    if _lt(dip("LABU"), config.OVERSOLD):
        return "dip_LABU->LABU", {"LABU": 1.0}, reach
    reach.append("rs_XLK_TREND")
    vol_short = "SVIX" if st.available("SVIX") else "SVXY"
    a, b = rs("XLK"), rs(config.TREND_SIGNAL_SERIES)
    if not (_a(a) and _a(b)):
        return "RAISE", None, reach
    if a > b:
        return "rs_bull->TECL/SOXL/volshort", \
            {"TECL": 1 / 3, "SOXL": 1 / 3, vol_short: 1 / 3}, reach
    return "rs_bear->SQQQ/TLT", {"SQQQ": 0.5, "TLT": 0.5}, reach


def _trace_bb(st):
    dip, rs = st.rsi_dip, st.rsi_rs
    if not (_a(rs("TLT")) and _a(rs("PSQ"))):
        return "RAISE", None
    if rs("TLT") > rs("PSQ"):
        return "bb:TLT>PSQ->QQQ", "QQQ"
    if _pas(st, "TQQQ", config.SMA_SHORT):
        if _lt(dip("PSQ"), config.OVERSOLD):
            return "bb:PSQ_dip->PSQ", "PSQ"
        if not (_a(rs("AGG")) and _a(rs("SH"))):
            return "RAISE", None
        if rs("AGG") > rs("SH"):
            return "bb:AGG>SH->TQQQ", "TQQQ"
        return "bb:else->PSQ", "PSQ"
    if not (_a(rs("IEF")) and _a(rs("PSQ"))):
        return "RAISE", None
    if rs("IEF") > rs("PSQ"):
        return "bb:IEF>PSQ->PSQ", "PSQ"
    return "bb:else->SQQQ", "SQQQ"


def _trace_fb(st):
    dip, rs = st.rsi_dip, st.rsi_rs
    crash = st.trailing_return_pct(config.CRASH_REFERENCE_TICKER,
                                   config.CRASH_HORIZON_SESSIONS)
    if _lt(crash, config.CRASH_THRESHOLD_PCT):
        if not (_a(rs("BND")) and _a(rs("QQQ"))):
            return "RAISE", None
        if rs("BND") > rs("QQQ"):
            return "fb:crash_BND>QQQ->QLD", "QLD"
        return "fb:crash->BTAL", "BTAL"
    if _pas(st, "TQQQ", config.SMA_SHORT):
        if _lt(dip("PSQ"), config.OVERSOLD):
            return "fb:PSQ_dip->PSQ", "PSQ"
        if not (_a(rs("AGG")) and _a(rs("SH"))):
            return "RAISE", None
        if rs("AGG") > rs("SH"):
            return "fb:AGG>SH->TQQQ", "TQQQ"
        return "fb:else->PSQ", "PSQ"
    if not (_a(rs("IEF")) and _a(rs("PSQ"))):
        return "RAISE", None
    if rs("IEF") > rs("PSQ"):
        return "fb:IEF>PSQ->PSQ", "PSQ"
    return "fb:else->SQQQ", "SQQQ"


def trace_t11(st):
    from src.sleeves import T11_PANEL
    ex, dip, rs = st.rsi_exhaustion, st.rsi_dip, st.rsi_rs
    if any(_gt(ex(t), config.OVERBOUGHT_TIER_1) for t in T11_PANEL):
        if any(_gt(ex(t), config.OVERBOUGHT_TIER_2) for t in T11_PANEL):
            return "tier2->UVXY", {"UVXY": 1.0}, None
        return "tier1->UVXY/BIL/BTAL", \
            {"UVXY": 1 / 3, "BIL": 1 / 3, "BTAL": 1 / 3}, None
    if _lt(dip("TQQQ"), config.OVERSOLD):
        return "dip_TQQQ->TQQQ", {"TQQQ": 1.0}, None
    if _lt(dip("SPY"), config.OVERSOLD):
        return "dip_SPY->SPXL", {"SPXL": 1.0}, None
    if _pas(st, "SPY", config.SMA_LONG):
        a, b = rs("XLK"), rs(config.TREND_SIGNAL_SERIES)
        if not (_a(a) and _a(b)):
            return "RAISE", None, None
        if a > b:
            return "bull_rs->TECL/SOXL/TQQQ", \
                {"TECL": 1 / 3, "SOXL": 1 / 3, "TQQQ": 1 / 3}, None
        if _pbs(st, config.TREND_SIGNAL_SERIES, config.SMA_SHORT):
            return "bull_trend_discounted->TECL/SOXL/TQQQ", \
                {"TECL": 1 / 3, "SOXL": 1 / 3, "TQQQ": 1 / 3}, None
        return "bull_short->TECS/SOXS/SQQQ", \
            {"TECS": 1 / 3, "SOXS": 1 / 3, "SQQQ": 1 / 3}, None
    bbb, bb_t = _trace_bb(st)
    fbb, fb_t = _trace_fb(st)
    if bb_t is None or fb_t is None:
        return "RAISE", None, (bbb, fbb)
    w = {}
    w[bb_t] = w.get(bb_t, 0.0) + 0.5
    w[fb_t] = w.get(fb_t, 0.0) + 0.5
    return f"bear[{bbb}|{fbb}]", w, (bbb, fbb)


def trace_s2(st):
    ex, dip, rs = st.rsi_exhaustion, st.rsi_dip, st.rsi_rs
    if _pas(st, "TQQQ", config.SMA_LONG):
        if _gt(ex("TQQQ"), config.OVERBOUGHT_TIER_1):
            return "gate_overbought->UVXY", {"UVXY": 1.0}
        return "gate->TQQQ", {"TQQQ": 1.0}
    if _lt(dip("TQQQ"), config.OVERSOLD):
        return "dip_TQQQ->TECL", {"TECL": 1.0}
    if _lt(dip("SOXL"), config.OVERSOLD):
        return "dip_SOXL->SOXL", {"SOXL": 1.0}
    if _pbs(st, "TQQQ", config.SMA_SHORT):
        a, b = rs("SQQQ"), rs("BSV")
        if not (_a(a) and _a(b)):
            return "RAISE", None
        if a > b:
            return "defensive->SQQQ", {"SQQQ": 1.0}
        return "defensive->BSV", {"BSV": 1.0}
    return "default->TQQQ", {"TQQQ": 1.0}


def trace_s3(st):
    from src.sleeves import S3_VOTES
    ex, dip = st.rsi_exhaustion, st.rsi_dip
    votes = sum(_pas(st, t, config.SMA_LONG) for t in S3_VOTES)
    bull = votes >= config.S3_VOTE_THRESHOLD   # D1 repair: read from config
    overbought = any(_gt(ex(t), config.OVERBOUGHT_TIER_1) for t in S3_VOTES)
    if bull:
        if overbought:
            vol = "UVIX" if st.available("UVIX") else "UVXY"
            return f"bull_overbought->{vol}", {vol: 1.0}
        return "bull->TQQQ/SOXL", {"TQQQ": 0.5, "SOXL": 0.5}
    if _lt(dip("QQQ"), config.OVERSOLD) or _lt(dip("SMH"), config.OVERSOLD):
        return "bear_dip->SOXL", {"SOXL": 1.0}
    return "bear->CASH", {}


# ---------------------------------------------------------------------------
# Minimum-torsion effective number of bets (Meucci-Deguest 2015)
# ---------------------------------------------------------------------------

def _sqrtm_sym(M):
    w, V = np.linalg.eigh(M)
    w = np.clip(w, 0.0, None)
    return (V * np.sqrt(w)) @ V.T


def min_torsion(Sigma, max_iter=20000, tol=1e-12):
    n = Sigma.shape[0]
    sigma = np.sqrt(np.diag(Sigma))
    C = Sigma / np.outer(sigma, sigma)
    c = _sqrtm_sym(C)
    d = np.ones(n)
    for _ in range(max_iter):
        M = (d[:, None] * C) * d[None, :]
        u = _sqrtm_sym(M)
        u_inv = np.linalg.pinv(u)
        g = np.diag(u_inv @ (d[:, None] * C))
        if np.max(np.abs(g - d)) < tol:
            d = g
            break
        d = g
    A = c @ np.diag(d)
    U, _, Vt = np.linalg.svd(A)
    O = Vt.T @ U.T
    b = np.diag(d) @ O @ np.linalg.pinv(c)
    t = np.diag(sigma) @ b @ np.diag(1.0 / sigma)
    return t


def enb_series(weights_df: pd.DataFrame, Sigma: np.ndarray, t: np.ndarray) -> pd.Series:
    t_inv_T = np.linalg.pinv(t).T
    fac_var = np.diag(t @ Sigma @ t.T)
    W = weights_df.to_numpy()
    out = np.full(len(W), np.nan)
    for i in range(len(W)):
        w = W[i]
        if not np.any(w != 0):
            continue
        e = t_inv_T @ w
        v = e ** 2 * fac_var
        s = v.sum()
        if s <= 0:
            continue
        p = v / s
        p = p[p > 0]
        out[i] = float(np.exp(-(p * np.log(p)).sum()))
    return pd.Series(out, index=weights_df.index)


def enc(weights_df: pd.DataFrame) -> pd.Series:
    W = weights_df.to_numpy()
    g = W.sum(axis=1)
    out = np.full(len(W), np.nan)
    nz = g > 0
    Wn = W[nz] / g[nz, None]
    out[nz] = 1.0 / (Wn ** 2).sum(axis=1)
    return pd.Series(out, index=weights_df.index)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("== load & run ==")
    panels = {a: bt.load_arm_panel(a) for a in ("synthetic", "realized")}
    for a, p in panels.items():
        ok, mx = bt.assert_holdout(p)
        print(f"holdout [{a}]: PASS max {mx.date()}")
    cal = panels["synthetic"]["SPY"].index

    sigs, accs = {}, {}
    for a in ("synthetic", "realized"):
        s = bt.ArmSignals(panels[a], cal)
        sigs[a] = {"sig": s, **bt.run_signals(s)}
        accs[a] = {bp: bt.run_account(s, panels[a], sigs[a]["rows"], bp)
                   for bp in config.SLIPPAGE_BASE_GRID_BP}
    lag2 = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"],
                          sigs["synthetic"]["rows"], ANCHOR_BP, fill_lag=2)
    lag2_0 = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"],
                            sigs["synthetic"]["rows"], 0, fill_lag=2)
    print("runs complete")

    # ---- positive control: branch tracer must reproduce every sleeve output
    tracers = {"T10": lambda st: trace_t10(st)[:2],
               "T11": lambda st: trace_t11(st)[:2],
               "S2": trace_s2, "S3": trace_s3}
    branch_counts = {k: {} for k in SLEEVE_ORDER}
    reach_counts = {}
    bear_sub = {}
    mismatches = 0
    srows = sigs["synthetic"]["rows"]
    for r in srows:
        st = sigs["synthetic"]["sig"].state_at(r["i"])
        b10, w10, reach = trace_t10(st)
        b11, w11, sub = trace_t11(st)
        b2, w2 = trace_s2(st)
        b3, w3 = trace_s3(st)
        for k, (b, w) in {"T10": (b10, w10), "T11": (b11, w11),
                          "S2": (b2, w2), "S3": (b3, w3)}.items():
            rec = r["sleeves"].get(k)
            if w is None:
                ok = k in r["raised"]
            else:
                ok = rec is not None and \
                    set(w) == set(rec) and \
                    all(abs(w[t] - rec[t]) < 1e-12 for t in w)
            if not ok:
                mismatches += 1
            branch_counts[k][b] = branch_counts[k].get(b, 0) + 1
        for step in reach:
            reach_counts[step] = reach_counts.get(step, 0) + 1
        if sub is not None:
            bear_sub[sub] = bear_sub.get(sub, 0) + 1
    assert mismatches == 0, f"branch tracer mismatches: {mismatches}"
    print("branch tracer positive control: PASS (0 mismatches on "
          f"{len(srows)} sessions x 4 sleeves)")

    n_eval = len(srows)
    years = (accs["synthetic"][ANCHOR_BP]["daily"].shape[0]) / 252.0

    # ---- headline with zero crossings ------------------------------------
    hrows = []
    for a in ("synthetic", "realized"):
        for bp in config.SLIPPAGE_BASE_GRID_BP:
            m = bt.headline_metrics(accs[a][bp]["daily"], accs[a][bp]["orders"])
            hrows.append({"arm": a, "slippage_bp": bp, **m})
    hl = pd.DataFrame(hrows)

    def crossing(df, col):
        d = df.sort_values("slippage_bp")
        x, y = d["slippage_bp"].to_numpy(dtype=float), d[col].to_numpy()
        for i in range(len(x) - 1):
            if y[i] > 0 >= y[i + 1]:
                return x[i] + (x[i + 1] - x[i]) * y[i] / (y[i] - y[i + 1])
        if y[-1] > 0:  # extrapolate from the last segment, flagged
            slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
            return x[-1] - y[-1] / slope if slope < 0 else np.inf
        return np.nan

    cross = {}
    for a in ("synthetic", "realized"):
        sub = hl[hl["arm"] == a]
        cross[a] = {"ann_return_zero_bp": crossing(sub, "ann_return"),
                    "sharpe_lo_zero_bp": crossing(sub, "sharpe_lo")}
    hl.to_csv(OUT / "headline-results.csv", index=False)

    # ---- daily series (anchor path, both arms' NAV, all cost NAVs) -------
    d_anchor = accs["synthetic"][ANCHOR_BP]["daily"]
    lab = pd.DataFrame([{"date": r["date"], "label": r["label"],
                         "signal_transition": r["changed"],
                         **{f"target_{k}": sleeve_label(r["sleeves"][k])
                            for k in SLEEVE_ORDER}}
                        for r in srows]).set_index("date")
    ds = d_anchor.join(lab, how="left")

    # carried-forward merged target weights (post-cap) per session
    tw = {}
    cur = {}
    for r in srows:
        if r["changed"] and r["targets"] is not None:
            cur = r["targets"]
        tw[r["date"]] = dict(cur)
    tw_df = pd.DataFrame({t: {d: w.get(t, 0.0) for d, w in tw.items()}
                          for t in TARGET_TICKERS}).reindex(ds.index).fillna(0.0)

    rw_df = pd.DataFrame(
        [{t: r["weights"].get(t, 0.0) for t in TARGET_TICKERS}
         for r in accs["synthetic"][ANCHOR_BP]["raw_rows"]],
        index=d_anchor.index)

    mult = {}
    for t in TARGET_TICKERS:
        fr = panels["synthetic"][t].frame
        if "multiple" in fr.columns and fr["multiple"].notna().any():
            mult[t] = fr["multiple"].reindex(ds.index).to_numpy()
        elif t == "BTAL":
            mult[t] = np.zeros(len(ds))       # no multiple (2.6)
        else:
            mult[t] = np.ones(len(ds))
    def eff_exposure(wdf):
        v = np.zeros(len(wdf))
        for t in TARGET_TICKERS:
            v += wdf[t].to_numpy() * mult[t]
        return pd.Series(v, index=wdf.index)

    ds["gross_realized"] = rw_df.sum(axis=1)
    ds["gross_target"] = tw_df.sum(axis=1)
    ds["eff_mkt_exposure_realized"] = eff_exposure(rw_df)
    ds["eff_mkt_exposure_target"] = eff_exposure(tw_df)
    for t in TARGET_TICKERS:
        ds[f"w_{t}"] = rw_df[t]
    for bp in config.SLIPPAGE_BASE_GRID_BP:
        if bp != ANCHOR_BP:
            ds[f"nav_{bp}bp"] = accs["synthetic"][bp]["daily"]["nav"]
    ds["nav_realized_arm_10bp"] = accs["realized"][ANCHOR_BP]["daily"]["nav"]
    ds = ds.rename(columns={"nav": f"nav_{ANCHOR_BP}bp_anchor", "ret": "ret_anchor"})
    ds.to_csv(OUT / "daily-series.csv")
    print(f"daily-series.csv: {len(ds)} sessions")

    # ---- diagnostics ------------------------------------------------------
    diag = []
    def add(section, metric, value, note=""):
        diag.append({"section": section, "metric": metric,
                     "value": value, "note": note})

    # transitions & holding lengths
    for a in ("synthetic", "realized"):
        ch = [r for r in sigs[a]["rows"] if r["changed"]]
        n_tr = len(ch)
        idxs = [r["i"] for r in ch]
        holds = np.diff(idxs)
        add("transitions", f"{a}_signal_transitions_total", n_tr)
        add("transitions", f"{a}_transitions_per_year", n_tr / years,
            "session 07 signal-level count: 105/yr")
        fills = accs[a][ANCHOR_BP]["daily"]["transition"].sum()
        add("transitions", f"{a}_realized_fill_sessions", int(fills),
            "last signal transition has no T+1 session and never fills"
            if n_tr != fills else "")
        if len(holds):
            add("transitions", f"{a}_holding_median_sessions", float(np.median(holds)))
            add("transitions", f"{a}_holding_mean_sessions", float(np.mean(holds)))
            add("transitions", f"{a}_holding_p90_sessions", float(np.percentile(holds, 90)))
            add("transitions", f"{a}_holding_max_sessions", int(holds.max()))
            for L in (1, 2, 3, 5, 10):
                add("transitions", f"{a}_holding_frac_<= {L}",
                    float((holds <= L).mean()))

    # 5.7 concentration
    tick_cols = list(TARGET_TICKERS)
    ret_panel = pd.DataFrame({t: panels["synthetic"][t].ret_total for t in tick_cols})
    cov_win = ret_panel.dropna()
    Sigma = cov_win.cov().to_numpy() * 252.0
    tmat = min_torsion(Sigma)
    # torsion positive controls
    I = np.eye(4)
    assert abs(enb_series(pd.DataFrame([[.25]*4]), I, min_torsion(I)).iloc[0] - 4.0) < 1e-6
    w1 = pd.DataFrame([[1.0, 0, 0, 0]])
    assert abs(enb_series(w1, I, min_torsion(I)).iloc[0] - 1.0) < 1e-6
    print("minimum-torsion positive controls: PASS")

    for name, wdf in (("target", tw_df), ("realized", rw_df)):
        enc_t = enc(wdf)
        ug = {}
        for t in tick_cols:
            grp = bt.UNDERLYING[t]
            ug.setdefault(grp, []).append(t)
        u_df = pd.DataFrame({g: wdf[cols].sum(axis=1) for g, cols in ug.items()})
        enc_u = enc(u_df)
        enb = enb_series(wdf[tick_cols], Sigma, tmat)
        gross = wdf.sum(axis=1)
        mx_t = wdf.max(axis=1)
        mx_u = u_df.max(axis=1)
        top3 = pd.Series(np.sort(wdf.to_numpy(), axis=1)[:, -3:].sum(axis=1),
                         index=wdf.index)
        eff = eff_exposure(wdf)
        add("concentration", f"{name}_enc_tickers_mean", float(enc_t.mean()))
        add("concentration", f"{name}_enc_tickers_median", float(enc_t.median()))
        add("concentration", f"{name}_enc_underlyings_mean", float(enc_u.mean()))
        add("concentration", f"{name}_enb_mintorsion_mean", float(enb.mean()),
            "Sigma: full-overlap window "
            f"{cov_win.index.min().date()}..{cov_win.index.max().date()} (BTAL-bounded), annualised")
        add("concentration", f"{name}_enb_mintorsion_median", float(enb.median()))
        add("concentration", f"{name}_eff_mkt_exposure_mean", float(eff.mean()))
        add("concentration", f"{name}_eff_mkt_exposure_p5", float(eff.quantile(.05)))
        add("concentration", f"{name}_eff_mkt_exposure_p95", float(eff.quantile(.95)))
        add("concentration", f"{name}_max_single_ticker_mean", float(mx_t.mean()))
        add("concentration", f"{name}_max_single_underlying_mean", float(mx_u.mean()))
        add("concentration", f"{name}_top3_sum_mean", float(top3.mean()))
        add("concentration", f"{name}_frac_sessions_all_cash",
            float((gross <= 1e-12).mean()))
        # conditional on drawdown quintile of the anchor NAV path
        nav = d_anchor["nav"]
        dd = nav / nav.cummax() - 1.0
        q = pd.qcut(dd, 5, labels=False, duplicates="drop")
        cond = pd.DataFrame({"enc_t": enc_t, "enb": enb, "eff": eff,
                             "mx_t": mx_t, "dd_q": q}).groupby("dd_q").mean()
        for qi, row in cond.iterrows():
            add("concentration_dd", f"{name}_ddq{int(qi)}_enc_tickers", float(row["enc_t"]),
                "quintile 0 = deepest drawdowns")
            add("concentration_dd", f"{name}_ddq{int(qi)}_enb", float(row["enb"]))
            add("concentration_dd", f"{name}_ddq{int(qi)}_eff_exposure", float(row["eff"]))

    # 5.6 breadth: sleeve terminal states, overlap
    for k in SLEEVE_ORDER:
        states = pd.Series([sleeve_label(r["sleeves"][k]) for r in srows])
        vc = states.value_counts()
        for s, n in vc.items():
            add("breadth_states", f"{k}:{s}", int(n), f"{n / n_eval:.4%} of sessions")
    overlap = 0
    for r in srows:
        held = {}
        for k in SLEEVE_ORDER:
            for t in r["sleeves"][k]:
                held[t] = held.get(t, 0) + 1
        if any(v >= 2 for v in held.values()):
            overlap += 1
    add("breadth", "sessions_with_ticker_shared_by_2plus_sleeves", overlap,
        f"{overlap / n_eval:.4%} of evaluated sessions")

    # 6.13 reach rates and branch firing
    for step, n in reach_counts.items():
        add("t10_reach", step, int(n), f"{n / n_eval:.4%}")
    for k in SLEEVE_ORDER:
        for b, n in sorted(branch_counts[k].items(), key=lambda x: -x[1]):
            add("branch_firing", f"{k}:{b}", int(n), f"{n / n_eval:.4%}")
    never = []
    known_terminals = {
        "T10": ["overbought->UVXY", "dip_TQQQ->TECL", "dip_SOXL->SOXL",
                "dip_SPXL->SPXL", "dip_LABU->LABU",
                "rs_bull->TECL/SOXL/volshort", "rs_bear->SQQQ/TLT"],
        "S2": ["gate_overbought->UVXY", "gate->TQQQ", "dip_TQQQ->TECL",
               "dip_SOXL->SOXL", "defensive->SQQQ", "defensive->BSV",
               "default->TQQQ"],
        "S3": ["bull_overbought->UVXY", "bull->TQQQ/SOXL", "bear_dip->SOXL",
               "bear->CASH"],
    }
    for k, terms in known_terminals.items():
        for t in terms:
            if branch_counts[k].get(t, 0) == 0:
                never.append(f"{k}:{t}")
    bb_terms = ["bb:TLT>PSQ->QQQ", "bb:PSQ_dip->PSQ", "bb:AGG>SH->TQQQ",
                "bb:else->PSQ", "bb:IEF>PSQ->PSQ", "bb:else->SQQQ"]
    fb_terms = ["fb:crash_BND>QQQ->QLD", "fb:crash->BTAL", "fb:PSQ_dip->PSQ",
                "fb:AGG>SH->TQQQ", "fb:else->PSQ", "fb:IEF>PSQ->PSQ",
                "fb:else->SQQQ"]
    sub_flat = {}
    for (b1, b2), n in bear_sub.items():
        sub_flat[b1] = sub_flat.get(b1, 0) + n
        sub_flat[b2] = sub_flat.get(b2, 0) + n
    for t in bb_terms + fb_terms:
        add("t11_bear_submodel", t, int(sub_flat.get(t, 0)),
            f"{sub_flat.get(t, 0) / n_eval:.4%}")
        if sub_flat.get(t, 0) == 0:
            never.append(f"T11:{t}")
    add("branch_firing", "branches_never_fired", "; ".join(never) if never else "none")

    # time in instrument
    pos_val_total = d_anchor["pos_value"].sum()
    for t in TARGET_TICKERS:
        held_frac = float((rw_df[t] > 0).mean())
        dollar = float((rw_df[t] * d_anchor["nav"]).sum() / pos_val_total)
        add("time_in_instrument", f"{t}_frac_sessions_held", held_frac)
        add("time_in_instrument", f"{t}_frac_dollar_exposure", dollar)

    # gross cap (5.3)
    n_cap = sum(1 for r in srows if r["changed"] and r["cap_truncated"])
    add("gross_cap", "transitions_where_cap_fired", n_cap,
        "proportional truncation events")
    add("gross_cap", "max_gross_before_cap",
        float(max((r["gross_before_cap"] or 0) for r in srows if r["changed"])))

    # 2.11 raises
    for a in ("synthetic", "realized"):
        ev = pd.DataFrame(sigs[a]["raises"])
        ev["idx"] = [cal.get_indexer([d])[0] for d in ev["date"]]
        pre = ev[ev["idx"] < config.WARMUP_SESSIONS]
        post = ev[ev["idx"] >= config.WARMUP_SESSIONS]
        add("pairwise_raises", f"{a}_pre_warmup_sessions", int(pre["date"].nunique()),
            f"{pre['date'].min().date()}..{pre['date'].max().date()}; all pre-warm-up")
        add("pairwise_raises", f"{a}_post_warmup_sessions", int(post["date"].nunique()),
            "traded window")
        add("pairwise_raises", f"{a}_frac_of_all_sessions",
            float(ev["date"].nunique() / len(cal)))
        ev.to_csv(OUT / f"_raises-{a}.csv", index=False)

    # unavailable fills (provisional completion rule)
    for a in ("synthetic", "realized"):
        uf = accs[a][ANCHOR_BP]["unavailable_fills"]
        add("unavailable_fills", f"{a}_events", len(uf))
        if len(uf):
            uf.to_csv(OUT / f"_unavailable-fills-{a}.csv", index=False)
            for t, g in uf.groupby("ticker"):
                add("unavailable_fills", f"{a}_{t}", len(g),
                    f"{g['date'].min().date()}..{g['date'].max().date()}")

    # commission by instrument (amended step 6)
    orders = accs["synthetic"][ANCHOR_BP]["orders"]
    orders["min_bound"] = (np.isclose(orders["commission"], bt.COMMISSION_MINIMUM)
                           & (bt.COMMISSION_PER_SHARE * orders["shares"] < bt.COMMISSION_MINIMUM))
    orders["cap_bound"] = np.isclose(orders["commission"],
                                     bt.COMMISSION_CAP_FRAC * orders["value"])
    add("commission", "orders_total", len(orders))
    add("commission", "frac_orders_minimum_bound", float(orders["min_bound"].mean()))
    add("commission", "frac_orders_cap_bound", float(orders["cap_bound"].mean()))
    add("commission", "portfolio_commission_bp_of_traded",
        float(orders["commission"].sum() / orders["value"].sum() * 1e4))
    for t, g in orders.groupby("ticker"):
        add("commission_by_instrument", f"{t}_bp_of_traded",
            float(g["commission"].sum() / g["value"].sum() * 1e4),
            f"n_orders={len(g)}, min_bound={g['min_bound'].mean():.2%}, "
            f"cap_bound={g['cap_bound'].mean():.2%}")

    pd.DataFrame(diag).to_csv(OUT / "diagnostics.csv", index=False)
    print(f"diagnostics.csv: {len(diag)} rows")

    # ---- sanity checks ----------------------------------------------------
    sc = []
    def check(name, passed, detail):
        sc.append({"check": name, "result": "PASS" if passed else "FAIL",
                   "detail": detail})

    d10 = accs["synthetic"][ANCHOR_BP]["daily"]
    recon = abs(float((1.0 + d10["ret"].fillna(0)).prod()) * d10["nav"].iloc[0]
                / d10["nav"].iloc[-1] - 1.0)
    check("nav_reconciles", recon < 1e-9, f"relative gap {recon:.2e}")

    m1 = bt.headline_metrics(d10, accs["synthetic"][ANCHOR_BP]["orders"])
    m2 = bt.headline_metrics(lag2["daily"], lag2["orders"])
    m1_0 = bt.headline_metrics(accs["synthetic"][0]["daily"], accs["synthetic"][0]["orders"])
    m2_0 = bt.headline_metrics(lag2_0["daily"], lag2_0["orders"])
    degrades = (m2["ann_return"] < m1["ann_return"]) and (m2["sharpe_lo"] < m1["sharpe_lo"])
    # Renamed by session 13.6 (step 9): this check measures execution-lag
    # sensitivity, not lookahead — lookahead makes lag hurt, and the check
    # fired on the opposite condition to the one the old name implied.
    check("execution_lag_sensitivity", degrades,
          f"T+1@10bp ann {m1['ann_return']:.4f} SR_lo {m1['sharpe_lo']:.4f}; "
          f"T+2@10bp ann {m2['ann_return']:.4f} SR_lo {m2['sharpe_lo']:.4f}; "
          f"cost-free T+1 ann {m1_0['ann_return']:.4f} vs T+2 ann {m2_0['ann_return']:.4f} "
          "— the result IMPROVES under one extra session of lag")

    gap = (d10["pos_value"] + d10["cash"] - d10["nav"]).abs().max()
    check("cash_accounts", gap < 1e-6, f"max |pos+cash-nav| = {gap:.2e}")

    tg = tw_df.sum(axis=1).max()
    check("gross_target_leq_100pct", tg <= 1.0 + 1e-9, f"max target gross {tg:.6f}")
    rg = float(ds["gross_realized"].max())
    add_note = ("realized gross can exceed 1 only through cost-induced negative cash; "
                f"min cash {d10['cash'].min():.2f}, "
                f"negative-cash sessions {(d10['cash'] < 0).sum()}")
    check("gross_realized_max_reported", True, f"max realized gross {rg:.6f}; {add_note}")

    bad_budget = 0
    for r in srows:
        for k in SLEEVE_ORDER:
            s = sum(r["sleeves"][k].values())
            if not (abs(s) < 1e-9 or abs(s - 1.0) < 1e-9):
                bad_budget += 1
    check("sleeve_weights_sum_to_budget", bad_budget == 0,
          f"{bad_budget} sleeve-sessions off budget")

    first_sig = cal[config.WARMUP_SESSIONS]
    first_fill = d10.index[d10["transition"]].min()
    check("warmup_boundary",
          first_fill == cal[config.WARMUP_SESSIONS + 1],
          f"first loaded {cal[0].date()}, first signal {first_sig.date()} "
          f"(index {config.WARMUP_SESSIONS}), first fill {first_fill.date()} "
          "(signal T close, fill T+1 close); indicators return None until defined")

    all_orders = pd.concat([accs[a][bp]["orders"]
                            for a in accs for bp in accs[a]])
    viol = (all_orders["commission"] >
            bt.COMMISSION_CAP_FRAC * all_orders["value"] + 1e-9).sum()
    check("commission_cap", viol == 0,
          f"{viol} orders exceed 1% of trade value across all runs")

    scdf = pd.DataFrame(sc)
    scdf.to_csv(OUT / "sanity-checks.csv", index=False)
    print(scdf.to_string(index=False))

    # ---- sub-periods -------------------------------------------------------
    sp = []
    for a in ("synthetic", "realized"):
        dd_ = accs[a][ANCHOR_BP]["daily"]
        r_ = dd_["ret"].dropna()
        for y, g in r_.groupby(r_.index.year):
            navy = (1 + g).prod() - 1.0
            sp.append({"arm": a, "period": str(y), "sessions": len(g),
                       "total_return": navy,
                       "ann_vol": g.std(ddof=1) * math.sqrt(252),
                       "max_drawdown": float(((1 + g).cumprod() /
                                              (1 + g).cumprod().cummax() - 1).min()),
                       "note": ("wildest construction-error decile; least reliable "
                                "construction (session 12 regime gradient)"
                                if y == 2008 else "")})
    sp_df = pd.DataFrame(sp)
    sp_df.to_csv(OUT / "subperiod.csv", index=False)
    print("subperiod.csv written; 7.14 sub-period definitions remain OPEN — "
          "calendar years reported, no definitions invented")

    # ---- summary json for the report --------------------------------------
    summary = {
        "calendar": {"first": str(cal[0].date()), "last": str(cal[-1].date()),
                     "sessions": len(cal), "evaluated": n_eval, "years": years},
        "crossings": cross,
        "lag_check": {"anchor": {"t1": m1, "t2": m2},
                      "costfree": {"t1": m1_0, "t2": m2_0}},
        "min_cash": float(d10["cash"].min()),
    }
    with open(OUT / "_summary.json", "w") as fh:
        json.dump(summary, fh, indent=1, default=str)
    print("crossings:", cross)


if __name__ == "__main__":
    main()
