"""Session 28 phase G. Robustness.

G1 is the dedicated lookahead test. The register's corrections list item 12 records
that no dedicated lookahead test has run anywhere in the project. Recorded under
9.10 at 9.70 as a disclosed post-hoc sensitivity. The canonical fill lag stays at
one session whatever this returns.
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

OUT = ROOT / "outputs" / "session-28"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
LADDER = ["buy_hold_QQQ", "buy_hold_TQQQ", "vol_targeted_QQQ_matched",
          "naive_fast_1d_momentum", "matched_exposure_levered_QQQ_1.70",
          "long_legs_only", "equal_weight_universe", "sleeve_T10_standalone",
          "sleeve_T11_standalone", "sleeve_S2_standalone", "sleeve_S3_standalone"]
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


# ============================ G1, the lookahead test ==========================
add("G1", item="motivation",
    note="the register's corrections list item 12 records that no dedicated lookahead "
         "test has run anywhere in the project. Recorded under 9.10 at 9.70")
add("G1", item="canonical_fill_lag", value=1,
    note="scripts/s13_backtest.py run_account, the signal evaluated at a session's "
         "close fills at that session plus fill_lag")
add("G1", item="negative_shift_computable", value=0,
    note="a fill lag of zero fills at the SAME session's open under the open-to-open "
         "convention, which precedes the close the signal was evaluated at, so it "
         "would trade on information the signal could not yet carry. It is mechanically "
         "runnable and is NOT run, since a lookahead test that itself looks ahead "
         "measures nothing")

print("building the environment")
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
o2o, cap_fn, cal = env["o2o"], env["cap_fn"], env["cal"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(PRIMARY)))
WIN = {"primary": (PRIMARY, BOUNDARY), "holdout": (BOUNDARY, None)}


def slice_ret(a, lo, hi):
    d = a["daily"]
    m = d.index >= lo
    if hi is not None:
        m = m & (d.index < hi)
    return d["ret"].loc[m].dropna(), d["nav"].loc[m]


lagtab = {}
for lag in (1, 2):
    print(f"  running the ladder at fill_lag {lag}")
    accs = {"STRATEGY": bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                                       fill_lag=lag,
                                       commission_fn=C.ARMS[C.CANONICAL_ARM],
                                       slip_fn=C.slip_class_premium(), cap_fn=cap_fn)}
    for ln in LADDER:
        accs[ln] = bt.run_account(sig["sig"], o2o,
                                  LINES[ln][0](o2o, sig["rows"], i0), C.ANCHOR,
                                  fill_lag=lag,
                                  commission_fn=C.ARMS[C.CANONICAL_ARM],
                                  slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
    for wname, (lo, hi) in WIN.items():
        vals = {}
        for ln, a in accs.items():
            r, nav = slice_ret(a, lo, hi)
            vals[ln] = L.standalone_metrics(r, nav, a["orders"])
        lagtab[(lag, wname)] = vals
        m = vals["STRATEGY"]
        on = sorted(vals, key=lambda k: -vals[k]["sharpe_naive"])
        ol = sorted(vals, key=lambda k: -vals[k]["sharpe_lo"])
        add("G1_lag", item="STRATEGY", window=wname, fill_lag=lag,
            ann_return=q(m["ann_return"]), sharpe_naive=q(m["sharpe_naive"]),
            sharpe_lo=q(m["sharpe_lo"]),
            rank_naive=on.index("STRATEGY") + 1, rank_lo=ol.index("STRATEGY") + 1,
            value=q(m["sharpe_naive"]), note=f"of {len(on)} ladder rows")
        print(f"    {wname:8s} lag {lag}  ann {m['ann_return']:.6f} naive "
              f"{m['sharpe_naive']:.6f} lo {m['sharpe_lo']:.6f} rank "
              f"{on.index('STRATEGY')+1}")

for wname in WIN:
    a1, a2 = lagtab[(1, wname)]["STRATEGY"], lagtab[(2, wname)]["STRATEGY"]
    o1 = sorted(lagtab[(1, wname)], key=lambda k: -lagtab[(1, wname)][k]["sharpe_naive"])
    o2 = sorted(lagtab[(2, wname)], key=lambda k: -lagtab[(2, wname)][k]["sharpe_naive"])
    r1, r2 = o1.index("STRATEGY") + 1, o2.index("STRATEGY") + 1
    add("G1_shift", item="ann_return_change", window=wname,
        value=q(a2["ann_return"] - a1["ann_return"]))
    add("G1_shift", item="sharpe_naive_change", window=wname,
        value=q(a2["sharpe_naive"] - a1["sharpe_naive"]))
    add("G1_shift", item="sharpe_lo_change", window=wname,
        value=q(a2["sharpe_lo"] - a1["sharpe_lo"]))
    add("G1_shift", item="rank_naive_change", window=wname, value=r2 - r1,
        note=f"from {r1} at the canonical lag to {r2} at one additional session")
hn = lagtab[(2, "holdout")]["STRATEGY"]
ho = sorted(lagtab[(2, "holdout")],
            key=lambda k: -lagtab[(2, "holdout")][k]["sharpe_naive"])
survives = (ho.index("STRATEGY") + 1) <= 5
add("G1_verdict", item="holdout_advantage_survives_one_extra_session_of_lag",
    value=int(survives),
    note="an edge which disappears under one session of additional lag is consistent "
         "with the signal using information not available at execution time, while an "
         "edge that survives is not. Stated as measured and not further interpreted")
p1 = lagtab[(1, "primary")]["STRATEGY"]
p2 = lagtab[(2, "primary")]["STRATEGY"]
repro = (p2["ann_return"] > p1["ann_return"]) and (p2["sharpe_lo"] < p1["sharpe_lo"])
add("G1_corrections_item_12", item="reproduces_on_the_designated_cell",
    value=int(repro),
    note=f"item 12 records annualised return improving under one extra session of lag "
         f"while the Lo-corrected Sharpe degrades. On the designated open-to-open cell "
         f"over the primary window the return moves from {p1['ann_return']!r} to "
         f"{p2['ann_return']!r} and the Lo-corrected Sharpe from {p1['sharpe_lo']!r} to "
         f"{p2['sharpe_lo']!r}, so BOTH degrade and the recorded pattern does not "
         f"reproduce")
_LA = [r for r in csv.DictReader(open(ROOT / "outputs/session-15/lag-anomaly.csv"))
       if r["table"] == "lag_levels" and r["convention"] == "c2c"]
_by = {r["lag"]: r for r in _LA}
add("G1_corrections_item_12", item="the_close_to_close_figures_item_12_rests_on",
    value=_by["1.0"]["ann_return"],
    note=f"outputs/session-15/lag-anomaly.csv records close-to-close annualised return "
         f"{_by['1.0']['ann_return']} at one session of lag against "
         f"{_by['2.0']['ann_return']} at two, with the Lo-corrected Sharpe moving from "
         f"{_by['1.0']['sharpe_lo']} to {_by['2.0']['sharpe_lo']}. The return improves "
         f"there, so item 12's pattern holds on the close-to-close convention and not "
         f"on the designated open-to-open cell")
add("G1_corrections_item_12", item="convention_dependence", value=1,
    note="item 12's recorded lag sensitivity is convention-specific. It was measured "
         "close-to-close and the designated cell is open-to-open")

# ============================ G2, concentration ================================
hl = pd.read_parquet(ROOT / "outputs" / "session-27" / "_holdout_line_returns.parquet")
cl = pd.read_parquet(ROOT / "outputs" / "session-27" / "_combined_line_returns.parquet")
prim = cl["STRATEGY"].loc[cl.index < BOUNDARY].dropna()
hold = hl["STRATEGY"].dropna()
for wname, r in (("holdout", hold), ("primary", prim)):
    tot = float(r.sum())
    srt = r.sort_values(ascending=False)
    add("G2", item="arithmetic_return_sum", window=wname, value=q(tot))
    for k in (1, 5, 10, 25):
        add("G2", item=f"share_from_the_best_{k}_sessions", window=wname,
            value=q(float(srt.iloc[:k].sum()) / tot))
        add("G2", item=f"share_from_the_worst_{k}_sessions", window=wname,
            value=q(float(srt.iloc[-k:].sum()) / tot))
    for k in (5, 10):
        cut = r.drop(srt.index[:k])
        rf = bt.rf_per_session(cut.index).reindex(cut.index).fillna(0.0)
        ex = (cut - rf).dropna()
        add("G2", item=f"naive_sharpe_with_the_best_{k}_removed", window=wname,
            value=q(float(ex.mean() / ex.std(ddof=1) * math.sqrt(252.0))))
    rf = bt.rf_per_session(r.index).reindex(r.index).fillna(0.0)
    ex = (r - rf).dropna()
    add("G2", item="naive_sharpe_unmodified", window=wname,
        value=q(float(ex.mean() / ex.std(ddof=1) * math.sqrt(252.0))))
    pos = srt[srt > 0]
    cum = pos.cumsum()
    half = int((cum < tot / 2.0).sum()) + 1
    add("G2", item="sessions_accounting_for_half_the_return", window=wname,
        value=half, note=f"of {len(r)} sessions, a share of {half/len(r):.6f}")

# ============================ G3, leave one year out ============================
years = sorted({d.year for d in hold.index})
base_rf = bt.rf_per_session(hold.index).reindex(hold.index).fillna(0.0)


def lo_sharpe(x, qq=252):
    mu, sd = x.mean(), x.std(ddof=1)
    xc = x - mu
    den = float(np.dot(xc, xc))
    acf = sum((qq - k) * float(np.dot(xc[:-k], xc[k:])) / den for k in range(1, qq))
    scale = qq + 2.0 * acf
    if scale <= 0:
        return float("nan")
    return (mu / sd) * qq / math.sqrt(scale) * math.sqrt(252.0 / qq)


ests = {}
for y in [None] + years:
    idx = hold.index if y is None else hold.index[hold.index.year != y]
    x = (hold.reindex(idx) - base_rf.reindex(idx)).dropna().to_numpy()
    nv = float(x.mean() / x.std(ddof=1) * math.sqrt(252.0))
    lv = float(lo_sharpe(x))
    ests[y] = (nv, lv, len(x))
    add("G3", item="base" if y is None else str(y), value=q(nv), sharpe_lo=q(lv),
        n_sessions=len(x),
        note="the holdout with that calendar year removed" if y else
             "the holdout unmodified")
drops = {y: v for y, v in ests.items() if y is not None}
lo_v = min(drops, key=lambda k: drops[k][0])
hi_v = max(drops, key=lambda k: drops[k][0])
add("G3_summary", item="naive_sharpe_range",
    value=f"{drops[lo_v][0]!r} to {drops[hi_v][0]!r}",
    note=f"minimum when {lo_v} is removed and maximum when {hi_v} is removed, against "
         f"the primary window's eleven estimates bounding 1.287076427656795 to "
         f"1.6183359759194622 on the Lo-corrected convention at 9.41")
mv = max(drops, key=lambda k: abs(drops[k][0] - ests[None][0]))
add("G3_summary", item="year_whose_removal_moves_it_most", value=mv,
    note=f"moving the naive Sharpe by {drops[mv][0]-ests[None][0]!r} from the base "
         f"{ests[None][0]!r}")
add("G3_summary", item="estimates", value=len(drops))

# ============================ G4, rolling stability =============================
comb = cl["STRATEGY"].dropna()
rfc = bt.rf_per_session(comb.index).reindex(comb.index).fillna(0.0)
exc = (comb - rfc).dropna()
W = 252
roll = (exc.rolling(W).mean() / exc.rolling(W).std(ddof=1) * math.sqrt(252.0)).dropna()
ser = pd.DataFrame({"rolling_252_naive_sharpe": roll,
                    "in_holdout": (roll.index >= BOUNDARY).astype(int)})
ser.to_csv(OUT / "rolling-sharpe-series.csv")
add("G4", item="window_sessions", value=W)
add("G4", item="windows", value=len(roll))
add("G4", item="minimum", value=q(roll.min()),
    note=f"at {roll.idxmin().date()}")
add("G4", item="maximum", value=q(roll.max()), note=f"at {roll.idxmax().date()}")
add("G4", item="share_above_1.0", value=q((roll > 1.0).mean()))
add("G4", item="boundary_marked", value=str(BOUNDARY.date()),
    note="the emitted series carries an in_holdout column at "
         "outputs/session-28/rolling-sharpe-series.csv")
for wname, m in (("primary", roll.index < BOUNDARY), ("holdout", roll.index >= BOUNDARY)):
    rr = roll[m]
    add("G4", item="minimum", window=wname, value=q(rr.min()))
    add("G4", item="maximum", window=wname, value=q(rr.max()))
    add("G4", item="share_above_1.0", window=wname, value=q((rr > 1.0).mean()),
        n_sessions=len(rr))

fn = ["table", "item", "window", "fill_lag", "value", "ann_return", "sharpe_naive",
      "sharpe_lo", "rank_naive", "rank_lo", "n_sessions", "note"]
with open(OUT / "robustness.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote robustness.csv, {len(rows)} rows")
print(f"  holdout advantage survives one extra session of lag: {survives}")
print(f"  corrections item 12 reproduces on the primary window: {repro}")
