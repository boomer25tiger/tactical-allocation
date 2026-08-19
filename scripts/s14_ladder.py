"""Session 14 steps 1, 3, 4, 5: benchmark ladder, segment decomposition,
premium sweep, cost sweep. Every line runs through the same run_account
with the same cost model as the strategy."""
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
INVERSE = {"SQQQ", "PSQ", "SH", "TECS", "SOXS"}
MEAN_EFF_EXPOSURE = 1.70          # 13.7/13.8 measurement, register 8.8 addition

env = C.build_env()
cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]
W = config.WARMUP_SESSIONS


def rows_from_weights(wseq: dict[int, dict], always_emit: bool = False) -> list[dict]:
    """Minimal signal rows: {calendar index: target dict} at each change.

    always_emit forces a target on every session, which is what a
    daily-rebalanced line means and which also lets a line retry after a
    session on which its target was unfillable.
    """
    out, prev = [], None
    for i in sorted(wseq):
        t = wseq[i]
        changed = always_emit or (prev is None) or (set(t) != set(prev)) or \
            any(abs(t[k] - prev.get(k, 0)) > 1e-12 for k in t)
        out.append({"i": i, "changed": changed, "targets": dict(t) if changed else None})
        if changed:
            prev = dict(t)
    return out


def first_fillable(panel, tickers, start_i: int) -> int:
    """First calendar index at or after start_i where every named instrument
    carries a raw price on the panel. A buy-and-hold line emitted before its
    instrument lists produces an unavailable fill that never retries, which
    silently converts the line into a cash holding."""
    arrs = {t: panel[t].raw_close.reindex(cal).to_numpy() for t in tickers}
    for i in range(max(start_i, W), len(cal)):
        if all(not math.isnan(arrs[t][i]) for t in tickers):
            return i
    return len(cal) - 1


def buy_and_hold(ticker: str, panel, start_i: int) -> list[dict]:
    i0 = first_fillable(panel, [ticker], start_i)
    return rows_from_weights({i0: {ticker: 1.0}})


def daily_constant(ticker: str, weight: float, panel, start_i: int) -> list[dict]:
    i0 = first_fillable(panel, [ticker], start_i)
    return rows_from_weights({i: {ticker: weight} for i in range(i0, len(cal))},
                             always_emit=True)


def vol_targeted_qqq(panel, start_i: int) -> list[dict]:
    """Vol-targeted QQQ scaled so mean effective exposure matches the
    strategy's measured 1.70, rebalanced daily, implemented in TQQQ so the
    gross cap holds (effective exposure = 3 x weight)."""
    i0 = first_fillable(panel, ["TQQQ"], start_i)
    r = panel["QQQ"].ret_total.reindex(cal)
    rv = r.rolling(60).std() * math.sqrt(252)
    raw = (1.0 / rv).replace([np.inf, -np.inf], np.nan).shift(1)
    scale = MEAN_EFF_EXPOSURE / raw.iloc[i0:].mean()
    eff = (raw * scale).clip(0.0, 3.0)
    return rows_from_weights({i: {"TQQQ": float(eff.iloc[i] / 3.0)}
                              for i in range(i0, len(cal))
                              if not math.isnan(eff.iloc[i])}, always_emit=True)


def naive_fast(panel, start_i: int) -> list[dict]:
    """One-session momentum rival: long TQQQ after an up session in QQQ,
    else sleeve cash. Defined once, not selected from a set; its realized
    transition rate is reported against the strategy's."""
    i0 = first_fillable(panel, ["TQQQ"], start_i)
    r = panel["QQQ"].ret_total.reindex(cal).shift(1)
    return rows_from_weights({i: ({"TQQQ": 1.0} if (r.iloc[i] or 0) > 0 else {})
                              for i in range(i0, len(cal))})


def equal_weight_universe(panel, start_i: int) -> list[dict]:
    tk = [t for t in ra.TARGET_TICKERS if t in panel.frames]
    i0 = first_fillable(panel, tk, start_i)
    w = 1.0 / len(tk)
    return rows_from_weights({i0: {t: w for t in tk}})


def sleeve_standalone(sleeve: str, srows) -> list[dict]:
    seq = {}
    for r in srows:
        wd = r["sleeves"][sleeve]
        if wd is not None:
            seq[r["i"]] = dict(wd)          # sleeve fractions == full budget
    return rows_from_weights(seq)


def long_legs_only(srows) -> list[dict]:
    seq = {}
    cur = {}
    for r in srows:
        if r["changed"] and r["targets"] is not None:
            cur = {t: w for t, w in r["targets"].items() if t not in INVERSE}
        seq[r["i"]] = dict(cur)
    return rows_from_weights(seq)


def strategy_rows(srows):
    return srows


LINES = {}


def register_line(name, builder, kind):
    """kind 'window_entry' lines are held positions that enter at the window
    start; kind 'strategy_stream' lines follow the strategy's own signal
    sequence over the whole calendar and are sliced like the strategy."""
    LINES[name] = {"builder": builder, "kind": kind}


register_line("buy_hold_QQQ", lambda p, s, i0: buy_and_hold("QQQ", p, i0), "window_entry")
register_line("buy_hold_TQQQ", lambda p, s, i0: buy_and_hold("TQQQ", p, i0), "window_entry")
register_line("vol_targeted_QQQ_matched",
              lambda p, s, i0: vol_targeted_qqq(p, i0), "window_entry")
register_line("naive_fast_1d_momentum", lambda p, s, i0: naive_fast(p, i0), "window_entry")
for k in SLEEVE_ORDER:
    register_line(f"sleeve_{k}_standalone",
                  (lambda kk: (lambda p, s, i0: sleeve_standalone(kk, s)))(k),
                  "strategy_stream")
register_line("matched_exposure_levered_QQQ_1.70",
              lambda p, s, i0: daily_constant("TQQQ", MEAN_EFF_EXPOSURE / 3.0, p, i0),
              "window_entry")
register_line("long_legs_only", lambda p, s, i0: long_legs_only(s), "strategy_stream")
register_line("equal_weight_universe",
              lambda p, s, i0: equal_weight_universe(p, i0), "window_entry")


def run_line(rows, panel, sig, conv, slip_fn=None, cap=True, bp=None):
    sf = slip_fn if slip_fn is not None else (
        C.slip_class_premium() if conv == "o2o" else C.slip_class)
    if bp is not None:
        sf = C.slip_uniform(bp)
    return bt.run_account(sig["sig"], panel, rows, C.ANCHOR,
                          commission_fn=C.ARMS[C.CANONICAL_ARM], slip_fn=sf,
                          cap_fn=cap_fn if cap else None)


PANEL_FOR = {"c2c": ("realized", lambda: panels["realized"]),
             "o2o": ("realized", lambda: o2o)}

print("== STEP 1: benchmark ladder ==")
rows1 = []
strat_ret = {}
line_ret = {}
WSTART = {"full": W, "early": W,
          "primary": int(np.searchsorted(cal.to_numpy(),
                                         np.datetime64(C.PRIMARY_START)))}
COMBOS_LADDER = [("realized", "c2c", "full"), ("realized", "c2c", "primary"),
                 ("realized", "o2o", "primary"), ("synthetic", "c2c", "early")]
for pname, conv, wname in COMBOS_LADDER:
    panel = env["o2o"] if conv == "o2o" else panels[pname]
    sig = sigs[pname]
    acc_s = run_line(sig["rows"], panel, sig, conv)
    strat_ret[(conv, wname)] = acc_s["daily"]["ret"]
    ms = C.metrics(C.window_slice(acc_s["daily"]["ret"], wname),
                   acc_s["orders"], acc_s["daily"]["nav"])
    rows1.append({"table": "ladder", "line": "STRATEGY", "panel": pname,
                  "convention": conv, "window": wname, **ms})
    for name, spec in LINES.items():
        rws = spec["builder"](panel, sig["rows"], WSTART[wname])
        acc = run_line(rws, panel, sig, conv)
        if spec["kind"] == "window_entry":
            entry = acc["daily"].index[acc["daily"]["transition"]].min()
        else:
            entry = None
        line_ret[(name, conv, wname)] = acc["daily"]["ret"]
        m = C.metrics(C.window_slice(acc["daily"]["ret"], wname),
                      acc["orders"], acc["daily"]["nav"])
        if m is None:
            continue
        ab = C.alpha_beta(C.window_slice(acc_s["daily"]["ret"], wname),
                          C.window_slice(acc["daily"]["ret"], wname))
        rows1.append({"table": "ladder", "line": name, "panel": pname,
                      "convention": conv, "window": wname, **m,
                      "line_kind": spec["kind"],
                      "first_fill": str(entry.date()) if entry is not None else "",
                      "strategy_alpha_ann_vs_line": ab["alpha_ann"],
                      "strategy_beta_vs_line": ab["beta"]})
    print(f"  [{pname} {conv} {wname}] {len(LINES)} lines + strategy done")
rows1.append({"table": "line_entry_note", "note":
              "Held-position lines enter at the first session on or after the "
              "window start on which every named instrument carries a price. "
              "Emitting such a line at the warm-up boundary instead produces an "
              "unavailable fill that never retries, which silently converts the "
              "line into a cash holding; that failure mode was present on the "
              "first run of this step and is recorded rather than left implicit. "
              "Strategy-stream lines follow the strategy's own signal sequence "
              "across the whole calendar and are sliced like the strategy."})
rows1.append({"table": "convention_note", "note":
              "every ladder line admits both conventions on the realized panel; "
              "the early window runs on the synthetic panel alone, since 7.14 and "
              "session 13.9 step 10 establish the realized panel carries coverage "
              "reporting only before 2011-10-03, and the synthetic panel is "
              "close-to-close by construction so it admits no open-to-open cell"})

# ===========================================================================
print("\n== STEP 3: overnight / intraday decomposition ==")
rows3 = []
pr = panels["realized"]


def seg_returns(ticker_frames, weights_df, seg):
    """Segment attribution for an open-to-open holding period.

    A position established at the open of session t-1 is held to the open
    of session t, so the open-to-open return booked at t factors as
    (1 + intraday_{t-1}) (1 + overnight_t). The overnight leg pairs the
    lagged weight with the current session's close-to-open move; the
    intraday leg pairs it with the PRIOR session's open-to-close move.
    Pairing the lagged weight with the current intraday move would
    attribute a segment the position did not hold.
    """
    out = pd.Series(0.0, index=weights_df.index)
    for t in weights_df.columns:
        fr = ticker_frames[t].frame
        ac, ao = fr["adj_close"], fr["adj_open"]
        if seg == "overnight":
            r = (ao / ac.shift(1) - 1.0).reindex(weights_df.index)
            out = out + weights_df[t].shift(1).fillna(0.0) * r.fillna(0.0)
        else:
            r = (ac / ao - 1.0).reindex(weights_df.index)
            out = out + (weights_df[t].shift(1) * r.shift(1)).fillna(0.0)
    return out


acc_head = run_line(sigs["realized"]["rows"], o2o, sigs["realized"], "o2o")
rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                   for r in acc_head["raw_rows"]], index=acc_head["daily"].index)
rw_p = rw[rw.index >= C.PRIMARY_START]
ov = seg_returns(pr.frames, rw_p, "overnight")
itd = seg_returns(pr.frames, rw_p, "intraday")
tot = C.window_slice(acc_head["daily"]["ret"], "primary")
for nm, s in (("overnight", ov), ("intraday", itd)):
    n = len(s)
    rows3.append({"table": "strategy_segments", "segment": nm,
                  "ann_contribution": float((1 + s).prod() ** (252 / n) - 1),
                  "sum_arith": float(s.sum()),
                  "share_of_total_arith": float(s.sum() / (ov.sum() + itd.sum())),
                  "ann_vol": float(s.std(ddof=1) * math.sqrt(252))})

# passive equal-weight universe, same window
tk = [t for t in ra.TARGET_TICKERS if t in pr.frames]
wpass = pd.DataFrame(1.0 / len(tk), index=rw_p.index, columns=tk)
ov_p = seg_returns(pr.frames, wpass, "overnight")
itd_p = seg_returns(pr.frames, wpass, "intraday")
for nm, s in (("overnight", ov_p), ("intraday", itd_p)):
    n = len(s)
    rows3.append({"table": "passive_segments", "segment": nm,
                  "ann_contribution": float((1 + s).prod() ** (252 / n) - 1),
                  "sum_arith": float(s.sum()),
                  "share_of_total_arith": float(s.sum() / (ov_p.sum() + itd_p.sum())),
                  "ann_vol": float(s.std(ddof=1) * math.sqrt(252))})

# reconciliation control: the two legs must rebuild the traded return
recon = (ov + itd)
tot_p = C.window_slice(acc_head["daily"]["ret"], "primary")
gap = float((recon - tot_p).abs().mean())
rows3.append({"table": "reconciliation_control", "mean_abs_gap_vs_traded_return": gap,
              "note": "legs rebuild the open-to-open portfolio return up to cost "
                      "charges and cross-product terms, which the traded series "
                      "carries and the segment attribution does not"})
print(f"  reconciliation: mean |ov+itd - traded| = {gap:.5f}")

# QQQ passive reference, since the equal-weight universe total is dominated by
# the volatility fund's decay and its ratio denominator is near zero
w_qqq = pd.DataFrame(1.0, index=rw_p.index, columns=["QQQ"])
ov_q = seg_returns(pr.frames, w_qqq, "overnight")
itd_q = seg_returns(pr.frames, w_qqq, "intraday")
for nm, s in (("overnight", ov_q), ("intraday", itd_q)):
    n = len(s)
    rows3.append({"table": "passive_qqq_segments", "segment": nm,
                  "ann_contribution": float((1 + s).prod() ** (252 / n) - 1),
                  "sum_arith": float(s.sum()),
                  "ann_vol": float(s.std(ddof=1) * math.sqrt(252))})


def share(a, b):
    """Overnight share on an absolute-magnitude basis, which stays bounded
    when the two legs carry opposite signs and the net is near zero."""
    return float(abs(a) / (abs(a) + abs(b))) if (abs(a) + abs(b)) > 0 else np.nan


strat_share = share(ov.sum(), itd.sum())
pass_share = share(ov_p.sum(), itd_p.sum())
qqq_share = share(ov_q.sum(), itd_q.sum())
rows3.append({"table": "exposure", "metric": "mean_gross_exposure",
              "value": float(rw_p.sum(axis=1).mean())})
rows3.append({"table": "exposure", "metric": "mean_overnight_dollar_exposure",
              "value": float(rw_p.shift(1).sum(axis=1).mean())})
rows3.append({"table": "exposure", "metric": "mean_intraday_dollar_exposure",
              "value": float(rw_p.shift(1).sum(axis=1).shift(1).mean())})
rows3.append({"table": "shares", "strategy_overnight_share_abs": strat_share,
              "passive_universe_overnight_share_abs": pass_share,
              "passive_qqq_overnight_share_abs": qqq_share,
              "strategy_overnight_arith": float(ov.sum()),
              "strategy_intraday_arith": float(itd.sum()),
              "passive_universe_overnight_arith": float(ov_p.sum()),
              "passive_universe_intraday_arith": float(itd_p.sum())})
exceeds = strat_share > max(pass_share, qqq_share) + 0.10
verdict3 = (
    f"SEGMENT SELECTION. The strategy's overnight leg contributes "
    f"{ov.sum():+.2f} in arithmetic sum against an intraday leg of "
    f"{itd.sum():+.2f}, an overnight share of {strat_share:.3f} against "
    f"{pass_share:.3f} for the equal-weight traded universe and "
    f"{qqq_share:.3f} for passive QQQ. The overnight share materially exceeds "
    "passive on both references, which locates the open-to-open advantage in "
    "overnight-return capture rather than in trade timing, so the "
    "overnight-hold line is the relevant comparison and the paper reports "
    "overnight capture as the mechanism."
    if exceeds else
    f"TRADE TIMING. The strategy's overnight share is {strat_share:.3f} against "
    f"{pass_share:.3f} passive-universe and {qqq_share:.3f} passive-QQQ, close "
    "enough that the open-to-open advantage is not located in systematic "
    "overnight exposure.")
rows3.append({"table": "verdict", "note": verdict3})
print(f"  strategy overnight {ov.sum():+.3f} vs intraday {itd.sum():+.3f}; "
      f"abs-share {strat_share:.3f} vs passive-universe {pass_share:.3f}, "
      f"passive-QQQ {qqq_share:.3f}")
print("  " + verdict3[:130])

# overnight-only and intraday-only holds as ladder lines, primary window only,
# since every universe member is listed from 2011-10-03 and the equal-weight
# construction is not defined before that.
for seg in ("overnight", "intraday"):
    s_seg = seg_returns(pr.frames, wpass, seg)
    m = C.metrics(s_seg)
    if m is None:
        continue
    rows1.append({"table": "ladder", "line": f"{seg}_only_hold_universe",
                  "panel": "realized", "convention": "segment", "window": "primary",
                  **m, "line_kind": "window_entry",
                  "note": "equal-weight traded universe, segment return only, one "
                          "entry so the turnover charge is nil by construction; "
                          "the segment split is an attribution of a held position "
                          "and not a separately tradeable line, since capturing it "
                          "would require a daily round trip the cost model would "
                          "charge"})
    rows3.append({"table": "segment_hold_line", "segment": seg, "window": "primary", **m})

pd.DataFrame(rows3).to_csv(OUT / "segment-decomposition.csv", index=False)
pd.DataFrame(rows1).to_csv(OUT / "ladder.csv", index=False)
print("[wrote ladder.csv, segment-decomposition.csv]")

# ===========================================================================
print("\n== STEP 4: premium sweep ==")
rows4 = []
c2c_cell = None
acc_c = run_line(sigs["realized"]["rows"], panels["realized"], sigs["realized"], "c2c")
c2c_cell = C.metrics(C.window_slice(acc_c["daily"]["ret"], "primary"),
                     acc_c["orders"], acc_c["daily"]["nav"])
rows4.append({"table": "sweep", "premium": None, "cell": "c2c_comparison",
              **c2c_cell})
for mult in C.PREMIUM_SWEEP:
    acc = run_line(sigs["realized"]["rows"], o2o, sigs["realized"], "o2o",
                   slip_fn=C.slip_class_premium(mult))
    m = C.metrics(C.window_slice(acc["daily"]["ret"], "primary"),
                  acc["orders"], acc["daily"]["nav"])
    rows4.append({"table": "sweep", "premium": mult, "cell": "o2o_designated", **m,
                  "exceeds_c2c_return": m["ann_return"] > c2c_cell["ann_return"],
                  "exceeds_c2c_sharpe_lo": m["sharpe_lo"] > c2c_cell["sharpe_lo"]})
    print(f"  premium {mult:.1f}x: ann {m['ann_return']:.4f} SR {m['sharpe_lo']:.4f} "
          f"(c2c {c2c_cell['ann_return']:.4f}/{c2c_cell['sharpe_lo']:.4f})")
ceil_row = [r for r in rows4 if r.get("premium") == max(C.PREMIUM_SWEEP)][0]
rows4.append({"table": "ceiling_verdict",
              "o2o_above_c2c_on_return_at_ceiling": bool(ceil_row["exceeds_c2c_return"]),
              "o2o_above_c2c_on_sharpe_at_ceiling": bool(ceil_row["exceeds_c2c_sharpe_lo"])})
rows4.append({"table": "bacidore_lipson_exclusion", "measured_multiple": 0.8,
              "sweep_floor": min(C.PREMIUM_SWEEP), "disposition": "EXCLUDED",
              "reason":
              "Bacidore and Lipson measure 1997-1998 NYSE specialist openings, "
              "before decimalization in 2001 and before the electronic opening "
              "auctions the Nasdaq and NYSE Arca crosses introduced in 2004, so "
              "their roughly 0.8 multiple describes an opening mechanism that no "
              "longer exists over a sample beginning in 2007. The exclusion is "
              "recorded rather than left as a silent truncation of the sweep floor "
              "at 1.0, and the direction is disclosed: were the 1990s relationship "
              "to hold, the premium would be a discount and the open-to-open cell "
              "would read higher than every figure reported here."})
pd.DataFrame(rows4).to_csv(OUT / "premium-sweep-ladder.csv", index=False)

# ===========================================================================
print("\n== STEP 5: cost sweep on the ladder ==")
rows5 = []
for bp in config.SLIPPAGE_BASE_GRID_BP:
    acc_s = run_line(sigs["realized"]["rows"], panels["realized"], sigs["realized"],
                     "c2c", bp=bp)
    ms = C.metrics(C.window_slice(acc_s["daily"]["ret"], "primary"),
                   acc_s["orders"], acc_s["daily"]["nav"])
    rows5.append({"table": "cost_sweep", "line": "STRATEGY", "slippage_bp": bp, **ms})
    for name, spec in LINES.items():
        rws = spec["builder"](panels["realized"], sigs["realized"]["rows"],
                              WSTART["primary"])
        acc = run_line(rws, panels["realized"], sigs["realized"], "c2c", bp=bp)
        m = C.metrics(C.window_slice(acc["daily"]["ret"], "primary"),
                      acc["orders"], acc["daily"]["nav"])
        if m is None:
            continue
        rows5.append({"table": "cost_sweep", "line": name, "slippage_bp": bp, **m,
                      "strategy_minus_line_ann": ms["ann_return"] - m["ann_return"],
                      "strategy_minus_line_sharpe_lo": ms["sharpe_lo"] - m["sharpe_lo"]})
    print(f"  {bp} bp done")


def crossing(xs, ys):
    for i in range(len(xs) - 1):
        if ys[i] > 0 >= ys[i + 1]:
            return xs[i] + (xs[i + 1] - xs[i]) * ys[i] / (ys[i] - ys[i + 1])
    return np.nan


df5 = pd.DataFrame([r for r in rows5 if r["table"] == "cost_sweep"])
for name in LINES:
    g = df5[df5.line == name].sort_values("slippage_bp")
    if not len(g):
        continue
    rows5.append({"table": "advantage_crossing", "line": name,
                  "return_crossing_bp": crossing(g["slippage_bp"].to_list(),
                                                 g["strategy_minus_line_ann"].to_list()),
                  "sharpe_crossing_bp": crossing(g["slippage_bp"].to_list(),
                                                 g["strategy_minus_line_sharpe_lo"].to_list())})
gs = df5[df5.line == "STRATEGY"].sort_values("slippage_bp")
rows5.append({"table": "strategy_zero_crossing_capped",
              "return_crossing_bp": crossing(gs["slippage_bp"].to_list(),
                                             gs["ann_return"].to_list()),
              "sharpe_crossing_bp": crossing(gs["slippage_bp"].to_list(),
                                             gs["sharpe_lo"].to_list()),
              "note": "recomputed under the capped canonical, realized panel, "
                      "close-to-close, primary window"})
pd.DataFrame(rows5).to_csv(OUT / "cost-sweep-ladder.csv", index=False)
print("[wrote premium-sweep-ladder.csv, cost-sweep-ladder.csv]")

with open(OUT / "_ladder_returns.pkl", "wb") as fh:
    pickle.dump({"strategy": strat_ret, "lines": line_ret}, fh)
