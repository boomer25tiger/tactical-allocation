"""Session 30 phase G. The NAV sensitivity, on the D20 axis.

D20 is recorded as a curve axis rather than a grid axis, so varying it is a
recorded sensitivity rather than a new degree of freedom. The canonical starting
NAV is unchanged whatever this returns.

CONTENTION CHECK before launching, on the same terms as phase F.

THE FIVE LEVELS, stated before running and chosen for coverage rather than for
result. 1000000 is the study anchor. 51671728.47473126 is the NAV the strategy
inherited at the boundary. 1028029775.2491124 is the terminal NAV. 10000000 and
200000000 fill the two order-of-magnitude gaps between them.
"""
from __future__ import annotations

import csv
import math
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s14_common as C                         # noqa: E402
import scripts.s15_lines as L                          # noqa: E402
import scripts.s22_vm as VM                            # noqa: E402
from src import config                                 # noqa: E402

OUT = ROOT / "outputs" / "session-30"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
LEVELS = [1000000.0, 10000000.0, 51671728.47473126, 200000000.0, 1028029775.2491124]
GRID = list(config.SLIPPAGE_BASE_GRID_BP)
FIXED_NAV = 51671728.47473126
LADDER = ["buy_hold_QQQ", "buy_hold_TQQQ", "vol_targeted_QQQ_matched",
          "naive_fast_1d_momentum", "matched_exposure_levered_QQQ_1.70",
          "long_legs_only", "equal_weight_universe", "sleeve_T10_standalone",
          "sleeve_T11_standalone", "sleeve_S2_standalone", "sleeve_S3_standalone"]
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


cores = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True,
                           text=True).stdout)
l = [float(x) for x in subprocess.run(["sysctl", "-n", "vm.loadavg"],
     capture_output=True, text=True).stdout.strip().strip("{} ").split()]
s0 = VM.sample()
for k, v in (("load_1min", l[0]), ("cores", cores),
             ("compressor_gib", s0["compressor_gib"]),
             ("swap_used_mb", s0["swap_used_mb"]),
             ("swap_free_mb", s0["swap_free_mb"])):
    add("machine_at_phase_G", item=k, value=v)
add("contention_check", item="threshold", value=cores * 2)
add("contention_check", item="load_1min", value=l[0])
halt = l[0] > cores * 2
add("contention_check", item="verdict", value="HALT" if halt else "PROCEED")
if halt:
    with open(OUT / "nav-sensitivity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table", "item", "value", "note"],
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"phase G HALTED, load {l[0]} against {cores*2}")
    sys.exit(0)
add("preregistration", item="levels", value=",".join(repr(x) for x in LEVELS),
    note="stated before running and chosen for coverage rather than for result. "
         "1000000 is the study anchor, 51671728.47473126 the NAV inherited at the "
         "boundary and 1028029775.2491124 the terminal NAV, with the two remaining "
         "levels filling the order-of-magnitude gaps")
add("preregistration", item="axis", value="D20",
    note="a curve axis rather than a grid axis, so varying it is a recorded sensitivity "
         "and not a new degree of freedom. The canonical starting NAV is unchanged")
add("preregistration", item="fixed_nav_for_G4", value=FIXED_NAV,
    note="the NAV inherited at the boundary, held constant across all six cost levels "
         "so the cost effect is separated from the capacity effect")

print("building the environment")
env = C.build_env(verbose=False)
cal, sig, o2o, cap_fn = env["cal"], env["sigs"]["realized"], env["o2o"], env["cap_fn"]
panel, syn = env["panels"]["realized"], env["panels"]["synthetic"]
LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(PRIMARY)))
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
mult = {}
for t in TICK:
    fr = syn[t].frame
    mult[t] = (fr["multiple"] if "multiple" in fr.columns and fr["multiple"].notna().any()
               else pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index))
ORIG_NAV = bt.START_NAV


def run(rws, nav=None, slip=None, start=None):
    """One pass. The starting NAV is the module constant, restored after the run,
    so no canonical value is left changed."""
    if nav is not None:
        bt.START_NAV = nav
    try:
        return bt.run_account(sig["sig"], o2o, rws, C.ANCHOR,
                              commission_fn=C.ARMS[C.CANONICAL_ARM],
                              slip_fn=slip or C.slip_class_premium(), cap_fn=cap_fn)
    finally:
        bt.START_NAV = ORIG_NAV


def holdout_stats(a):
    d = a["daily"]
    idx = d.index[d.index >= BOUNDARY]
    r = d["ret"].reindex(idx).dropna()
    m = L.standalone_metrics(r, d["nav"].reindex(idx), a["orders"])
    o = a["orders"].copy()
    o["date"] = pd.to_datetime(o["date"])
    o = o[(o["date"] >= idx.min()) & (o["date"] <= idx.max())]
    ev = sorted(set(o["date"]))
    tv = o.groupby("date")["value"].sum()
    navd = d["nav"].reindex(tv.index).ffill()
    caps = a["cap_events"].copy()
    nt = 0
    if len(caps):
        caps["date"] = pd.to_datetime(caps["date"])
        cw = caps[(caps["date"] >= idx.min()) & (caps["date"] <= idx.max())]
        nt = len(set(cw["date"]))
    rw = pd.DataFrame([{t: rr["weights"].get(t, 0.0) for t in TICK}
                       for rr in a["raw_rows"]], index=d.index).reindex(idx)
    eff = pd.Series(sum(rw[t].to_numpy() * mult[t].reindex(idx).fillna(0.0).to_numpy()
                        for t in TICK), index=idx)
    return {**m, "n_sessions": len(r), "events": len(ev),
            "events_per_session": len(ev) / len(idx),
            "mean_trade_share_of_nav": float((tv / navd).mean()),
            "cap_binding_events": nt,
            "cap_binding_share": nt / len(ev) if ev else float("nan"),
            "eff_mean": float(eff.mean()), "eff_sd": float(eff.std(ddof=1))}


# ============================== G1, the capacity curve ==========================
t0 = time.time()
base_ladder = {}
for ln in LADDER:
    base_ladder[ln] = holdout_stats(run(LINES[ln][0](o2o, sig["rows"], i0)))
print(f"  ladder baseline at {time.time()-t0:.1f}s")
curve = {}
for nav in LEVELS:
    st = holdout_stats(run(sig["rows"], nav=nav))
    curve[nav] = st
    vals = {**{k: v["sharpe_naive"] for k, v in base_ladder.items()},
            "STRATEGY": st["sharpe_naive"]}
    rank = sorted(vals, key=lambda k: -vals[k]).index("STRATEGY") + 1
    add("G1", item="nav", value=q(nav), ann_return=q(st["ann_return"]),
        sharpe_naive=q(st["sharpe_naive"]), sharpe_lo=q(st["sharpe_lo"]),
        ann_turnover=q(st["ann_turnover"]),
        events_per_session=q(st["events_per_session"]),
        mean_trade_share_of_nav=q(st["mean_trade_share_of_nav"]),
        cap_binding_share=q(st["cap_binding_share"]), rank_naive=rank,
        note="the ladder lines are run once at the canonical NAV and the strategy's "
             "rank is taken against them, so the rank isolates the strategy's own NAV "
             "sensitivity")
    print(f"  NAV {nav:>18,.0f} naive {st['sharpe_naive']:.6f} "
          f"cap {st['cap_binding_share']:.4f} rank {rank}")
ns = sorted(curve)
sh = [curve[n]["sharpe_naive"] for n in ns]
diffs = [sh[i + 1] - sh[i] for i in range(len(sh) - 1)]
smooth = max(abs(d) for d in diffs) < 2 * (abs(sum(diffs)) / max(len(diffs), 1) + 1e-12) \
    if diffs else True
add("G1_summary", item="monotone_in_nav", value=int(all(d <= 0 for d in diffs)),
    note="the naive Sharpe across the five levels in ascending NAV order is " +
         ", ".join(f"{v!r}" for v in sh))
add("G1_summary", item="largest_single_step_change", value=q(max(diffs, key=abs)),
    note="between adjacent levels, against a total change across the whole range of "
         f"{sh[-1]-sh[0]!r}")
add("G1_summary", item="degrades_smoothly_or_breaks",
    value="smoothly" if smooth else "breaks at a threshold",
    note="smoothly is recorded when no adjacent step exceeds twice the mean step")
for thr in (0.75, 0.90):
    hit = next((n for n in ns if curve[n]["cap_binding_share"] > thr), None)
    add("G1_summary", item=f"nav_at_which_cap_binding_first_exceeds_{thr}",
        value=q(hit) if hit else "none",
        note="" if hit else "the cap-binding share does not exceed this at any level "
                            "swept")

# ============================== G2, NAV reset at the boundary ====================
# The reset runs the holdout as a standalone account beginning at the boundary, so
# the book does not carry the primary window's compounding into it.
sub_rows = [r for r in sig["rows"] if r["date"] >= BOUNDARY]
acc_reset = run(sub_rows, nav=1000000.0)
st_reset = holdout_stats(acc_reset)
# The inherited case is the CANONICAL run, whose book compounds from the study
# anchor and reaches 51671728.47473126 at the boundary. curve[FIXED_NAV] is a
# different object, being a run whose STARTING NAV is that figure, so its book is
# about fifty times larger again at the boundary and it is not the comparison G2
# asks for.
inh = holdout_stats(run(sig["rows"]))
vals = {**{k: v["sharpe_naive"] for k, v in base_ladder.items()},
        "STRATEGY": st_reset["sharpe_naive"]}
rank_reset = sorted(vals, key=lambda k: -vals[k]).index("STRATEGY") + 1
for k in ("ann_return", "sharpe_naive", "sharpe_lo", "ann_turnover",
          "eff_mean", "eff_sd", "cap_binding_share"):
    add("G2", item=k, value=q(st_reset[k]), inherited=q(inh[k]),
        note="reset to the study anchor at the boundary against the inherited "
             f"{FIXED_NAV!r}")
add("G2", item="rank_naive", value=rank_reset,
    inherited=sorted({**{k: v["sharpe_naive"] for k, v in base_ladder.items()},
                      "STRATEGY": inh["sharpe_naive"]},
                     key=lambda k: -({**{k2: v2["sharpe_naive"]
                                         for k2, v2 in base_ladder.items()},
                                      "STRATEGY": inh["sharpe_naive"]})[k]
                     ).index("STRATEGY") + 1)
add("G2", item="construction", value="standalone account from the boundary",
    note="the reset runs the holdout as its own account beginning at the boundary, so "
         "the book does not carry the primary window's compounding into it. The signal "
         "rows are unchanged")
print(f"  G2 reset naive {st_reset['sharpe_naive']:.6f} against inherited "
      f"{inh['sharpe_naive']:.6f}")

# ============================== G3, cap binding by calendar year =================
acc_can = run(sig["rows"])
d = acc_can["daily"]
o = acc_can["orders"].copy(); o["date"] = pd.to_datetime(o["date"])
caps = acc_can["cap_events"].copy()
if len(caps):
    caps["date"] = pd.to_datetime(caps["date"])
comb = d.index[(d.index >= PRIMARY)]
first75 = first90 = None
for y in sorted({dt.year for dt in comb}):
    idx = comb[comb.year == y]
    ow = o[(o["date"] >= idx.min()) & (o["date"] <= idx.max())]
    ev = sorted(set(ow["date"]))
    nt = 0
    if len(caps):
        cw = caps[(caps["date"] >= idx.min()) & (caps["date"] <= idx.max())]
        nt = len(set(cw["date"]))
    share = nt / len(ev) if ev else float("nan")
    if first75 is None and share > 0.75:
        first75 = y
    if first90 is None and share > 0.90:
        first90 = y
    add("G3", item=str(y), value=q(share), events=len(ev), cap_binding_events=nt,
        nav_at_year_end=q(d["nav"].reindex(idx).iloc[-1]),
        note="holdout" if idx.min() >= BOUNDARY else "primary window")
add("G3_summary", item="first_year_binding_exceeds_0.75", value=first75 or "none")
add("G3_summary", item="first_year_binding_exceeds_0.90", value=first90 or "none")
add("G3_summary", item="boundary_year", value=2021,
    note="throttling is established by the year it first exceeded each threshold "
         "rather than assumed to begin at the boundary")

# ============================== G4, the cost sweep at fixed NAV ==================
S28 = {r["slippage_bp"]: r for r in csv.DictReader(
    open(ROOT / "outputs" / "session-28" / "holdout-cost-sweep.csv"))
    if r["table"] == "sweep" and r["item"] == "STRATEGY"}
prev = None
non_mono_fixed = 0
for bp in GRID:
    st = holdout_stats(run(sig["rows"], nav=FIXED_NAV, slip=C.slip_uniform(bp)))
    s28 = S28.get(str(bp), {}).get("sharpe_naive", "")
    if prev is not None and st["sharpe_naive"] > prev:
        non_mono_fixed += 1
    prev = st["sharpe_naive"]
    add("G4", item="slippage_bp", value=bp, sharpe_naive=q(st["sharpe_naive"]),
        sharpe_lo=q(st["sharpe_lo"]), session_28_coupled=s28,
        note="NAV held at the stated constant across all six points, against session "
             "28's figures where NAV compounds from the inherited level")
    print(f"  G4 {bp:>3} bp fixed-NAV naive {st['sharpe_naive']:.6f} against coupled {s28}")
s28v = [float(S28[str(b)]["sharpe_naive"]) for b in GRID if str(b) in S28]
non_mono_coupled = sum(1 for i in range(len(s28v) - 1) if s28v[i + 1] > s28v[i])
add("G4_summary", item="non_monotone_steps_coupled", value=non_mono_coupled,
    note="session 28's sweep, where NAV compounds differently at each cost level")
add("G4_summary", item="non_monotone_steps_at_fixed_nav", value=non_mono_fixed)
add("G4_summary", item="non_monotonicity_disappears_at_fixed_nav",
    value=int(non_mono_fixed == 0 and non_mono_coupled > 0),
    note="a sweep in which a higher cost produces a higher Sharpe is non-monotone. "
         "Holding NAV constant separates the cost effect from the capacity effect")
_S28R = {r["slippage_bp"]: r["value"] for r in csv.DictReader(
    open(ROOT / "outputs" / "session-28" / "holdout-cost-sweep.csv"))
    if r["table"] == "rank" and r["convention"] == "sharpe_naive"}
_rk = [_S28R.get(str(b)) for b in GRID]
add("G4_summary", item="session_28_naive_sharpe_was_already_monotone",
    value=int(non_mono_coupled == 0),
    note="the scaffold asks whether a non-monotonicity disappears once NAV is fixed. "
         "On the naive Sharpe session 28's coupled sweep is already monotone "
         "decreasing, so there is none to disappear. What was non-monotone there is the "
         "RANK, reading " + ",".join(str(x) for x in _rk) + " across the six levels, "
         "which moves from 3 at zero basis points to 2 at every higher level")

add("canonical_unchanged", item="start_nav_restored", value=q(bt.START_NAV),
    note="every run restores scripts/s13_backtest.py START_NAV in a finally block, so "
         "no canonical value is left changed by this phase")

fn = ["table", "item", "value", "ann_return", "sharpe_naive", "sharpe_lo",
      "ann_turnover", "events_per_session", "mean_trade_share_of_nav",
      "cap_binding_share", "rank_naive", "inherited", "events", "cap_binding_events",
      "nav_at_year_end", "session_28_coupled", "note"]
with open(OUT / "nav-sensitivity.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote nav-sensitivity.csv, {len(rows)} rows in {time.time()-t0:.1f}s")
