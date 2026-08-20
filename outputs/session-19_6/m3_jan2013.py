"""M3, the fourteen sessions at the front of the 2013-01-02 arm.

The strip arms are nested. scripts/s195_strip.py calls run(sig["rows"]) with
no start argument inside the loop over start dates, so one strategy account
is built and each arm is a slice of it. The difference between the two arms
is therefore carried entirely by the sessions between 2013-01-02 and the
session before 2013-01-23.

TOLERANCE, STATED BEFORE THE COMPARISON IT GOVERNS.
  TOL_ANN = 1e-9 absolute on the reconstructed annualised return of the
  2013-01-02 arm against the value emitted in window-strip.csv. Both sides
  are the same product over the same returns, so anything above this means
  the difference is not carried by those sessions and the premise fails.

Start dates and the emitted comparison values are read from
outputs/session-19_5/window-strip.csv rather than hardcoded.
"""
from __future__ import annotations

import ast
import csv
import re
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt       # noqa: E402
import scripts.s14_common as C          # noqa: E402
import scripts.s15_lines as L           # noqa: E402
from src import config                  # noqa: E402

OUT = ROOT / "outputs" / "session-19_6"
TOL_ANN = 1e-9
MEM_CEILING_GB = 5.0
rows = []
t_all = time.time()


def add(table, **kw):
    rows.append({"table": table, **kw})


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


# ---- emitted arm values, read not recalled -------------------------------
arms = {}
for r in csv.DictReader(open(ROOT / "outputs/session-19_5/window-strip.csv")):
    if r["table"] == "strip":
        arms[r["item"]] = dict(start=pd.Timestamp(r["start"]),
                               n=int(float(r["n_sessions"])),
                               ann=float(r["ann_return"]))
A_LATE = arms["earliest_full_composition"]
A_EARLY = arms["first_session_2013"]
print(f"late arm  start {A_LATE['start'].date()} n {A_LATE['n']} ann {A_LATE['ann']!r}")
print(f"early arm start {A_EARLY['start'].date()} n {A_EARLY['n']} ann {A_EARLY['ann']!r}")
add("arms", item="late_start", note=str(A_LATE["start"].date()), value=A_LATE["n"])
add("arms", item="early_start", note=str(A_EARLY["start"].date()), value=A_EARLY["n"])
add("arms", item="late_ann_emitted", value=A_LATE["ann"])
add("arms", item="early_ann_emitted", value=A_EARLY["ann"])
add("arms", item="session_difference", value=A_EARLY["n"] - A_LATE["n"])

C.PRIMARY_START = pd.Timestamp("2011-10-04")
env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]
acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
daily = acc["daily"]

r_late = daily["ret"].loc[daily.index >= A_LATE["start"]].dropna()
r_early = daily["ret"].loc[daily.index >= A_EARLY["start"]].dropna()
assert len(r_late) == A_LATE["n"] and len(r_early) == A_EARLY["n"], \
    (len(r_late), len(r_early))
front = r_early.loc[r_early.index < A_LATE["start"]]
print(f"\nfront span {front.index[0].date()} to {front.index[-1].date()}, "
      f"{len(front)} sessions")
add("front", item="first_session", note=str(front.index[0].date()))
add("front", item="last_session", note=str(front.index[-1].date()))
add("front", item="n_sessions", value=len(front))

# ---- terminal labels parsed from the session 18 census --------------------
census = pd.read_csv(ROOT / "outputs/session-18/reachability.csv")
census = census[census.table == "census"]
term_map = {}
for sl, term in census[["sleeve", "terminal"]].drop_duplicates().itertuples(index=False):
    m = re.search(r"return (\{.*\}|\"[A-Z]+\")", str(term))
    if not m:
        continue
    body = m.group(1)
    try:
        keys = frozenset(ast.literal_eval(body).keys()) if body.startswith("{") \
            else frozenset({ast.literal_eval(body)})
    except (ValueError, SyntaxError):
        keys = frozenset(re.findall(r'"([A-Z]{2,5})"', body)) | \
               ({"SVXY", "SVIX"} if "vol_short" in body else set()) | \
               ({"UVXY", "UVIX"} if re.search(r"\bvol\b", body) else set())
    term_map.setdefault((str(sl), keys), str(term))

SLEEVE_ORDER = [k for k in sig["rows"][0]["sleeves"].keys()]
add("terminal_mapping", item="method",
    note="terminal labels are matched by the ticker set each sleeve returns, parsed "
         "from the terminal strings in outputs/session-18/reachability.csv. Exact set "
         "equality is tried first, then a unique subset match, which is what resolves "
         "the terminals whose source carries a variable key such as vol_short. A label "
         "reads UNMATCHED where neither is unique within that sleeve")
add("terminal_mapping", item="fill_lag",
    note="run_account fills with fill_lag=1, so the signal row reported against a "
         "session is the row at the prior calendar position, being the one whose "
         "weights the holdings on that session reflect")

by_i = {r["i"]: r for r in sig["rows"]}
pos = {d: i for i, d in enumerate(cal)}
print("\nper-session read of the front span")
print(f"{'date':<12}{'ret':>10}  {'UVXY':<5} holdings")
for d in front.index:
    ret = float(front.loc[d])
    w = daily["weights"].loc[d]
    w = {k: float(v) for k, v in w.items() if abs(float(v)) > 0} if isinstance(w, dict) else {}
    # run_account fills with fill_lag=1, so the signal row that produced the
    # holdings shown on session d is the row at the prior calendar position
    srow = by_i.get(pos[d] - 1)
    labels = {}
    if srow is not None:
        for k in SLEEVE_ORDER:
            sw = srow["sleeves"].get(k)
            if sw is None:
                labels[k] = "no emission"
            else:
                ks = frozenset(t for t, v in sw.items() if v)
                lab = term_map.get((k, ks))
                if lab is None:
                    cand = [v for (sl2, keys), v in term_map.items()
                            if sl2 == k and ks <= keys and len(keys) == len(ks)
                            or (sl2 == k and ks < keys)]
                    cand = sorted(set(cand))
                    lab = cand[0] if len(cand) == 1 else f"UNMATCHED {sorted(ks)}"
                labels[k] = lab
    uv = "UVXY" in w
    add("front_session", item=str(d.date()), value=ret,
        note=" ".join(f"{t}={v:.4f}" for t, v in sorted(w.items())),
        note2=" | ".join(f"{k}: {labels.get(k,'')}" for k in SLEEVE_ORDER),
        within=int(uv))
    print(f"{str(d.date()):<12}{ret:>10.6f}  {'yes' if uv else 'no':<5} "
          f"{' '.join(f'{t}={v:.3f}' for t, v in sorted(w.items()))}")

cum_front = float((1.0 + front).prod() - 1.0)
add("front", item="cumulative_return", value=cum_front)
add("front", item="n_sessions_uvxy_held",
    value=int(sum(1 for d in front.index
                  if isinstance(daily["weights"].loc[d], dict)
                  and "UVXY" in daily["weights"].loc[d]
                  and abs(float(daily["weights"].loc[d]["UVXY"])) > 0)))
print(f"\ncumulative return over the front span {cum_front:.6f}")

# ---- arithmetic verification --------------------------------------------
g_late = float((1.0 + r_late).prod())
g_early = float((1.0 + r_early).prod())
recon = g_late * (1.0 + cum_front)
ann_recon = recon ** (252.0 / len(r_early)) - 1.0
gap = abs(ann_recon - A_EARLY["ann"])
add("verification", item="TOL_ANN", value=TOL_ANN, note="stated before comparing")
add("verification", item="growth_late_arm", value=g_late)
add("verification", item="growth_front_span", value=1.0 + cum_front)
add("verification", item="growth_early_arm_reconstructed", value=recon)
add("verification", item="growth_early_arm_direct", value=g_early)
add("verification", item="ann_reconstructed", value=ann_recon)
add("verification", item="ann_emitted", value=A_EARLY["ann"])
add("verification", item="abs_gap", value=gap, within=int(gap <= TOL_ANN))
add("verification", item="verdict",
    note="PASS, the difference is carried by the front span"
         if gap <= TOL_ANN else "FAIL, the premise does not hold")
print(f"\nreconstructed ann {ann_recon!r} against emitted {A_EARLY['ann']!r} "
      f"gap {gap:.3e} -> {'PASS' if gap <= TOL_ANN else 'FAIL'}")

# ---- the three overlap figures, emitted as artifacts ---------------------
ov = r_late.index
a = r_early.reindex(ov)
b = r_late.reindex(ov)
corr = float(np.corrcoef(a.to_numpy(), b.to_numpy())[0, 1])
cum_ov_a = float((1.0 + a).prod() - 1.0)
cum_ov_b = float((1.0 + b).prod() - 1.0)
same_pos = all(daily["weights"].loc[d] == daily["weights"].loc[d] for d in ov)
maxdev = float(np.max(np.abs(a.to_numpy() - b.to_numpy())))
add("overlap", item="n_sessions", value=int(len(ov)))
add("overlap", item="daily_return_correlation", value=corr)
add("overlap", item="max_abs_daily_return_difference", value=maxdev)
add("overlap", item="cumulative_return_early_arm", value=cum_ov_a)
add("overlap", item="cumulative_return_late_arm", value=cum_ov_b)
add("overlap", item="cumulative_returns_identical",
    value=int(cum_ov_a == cum_ov_b))
add("overlap", item="position_vectors_agree_every_session", value=int(same_pos),
    note="both arms slice one account, so the weight dictionary at each overlapping "
         "session is the same object")
print(f"\noverlap {len(ov)} sessions, correlation {corr!r}, max abs daily "
      f"difference {maxdev:.3e}")
print(f"cumulative over overlap early {cum_ov_a!r} late {cum_ov_b!r} "
      f"identical {cum_ov_a == cum_ov_b}")

# ---- the nesting asymmetry ----------------------------------------------
strip_src = (ROOT / "scripts" / "s195_strip.py").read_text()
add("nesting", item="strategy_call",
    note='acc_s = run(sig["rows"]) inside the loop over start dates, taking no start '
         "argument, so one account is built and every arm is a slice of it",
    within=int('acc_s = run(sig["rows"])' in strip_src))
add("nesting", item="benchmark_call",
    note='rws = LINES[ln][0](o2o, sig["rows"], i0) inside the same loop, taking the '
         "per-arm entry index i0, so each benchmark line is re-initialised per arm",
    within=int('LINES[ln][0](o2o, sig["rows"], i0)' in strip_src))
add("nesting", item="consequence",
    note="the strip compares a nested strategy against non-nested benchmarks, so a "
         "rank change across arms mixes the strategy's window change with the "
         "benchmarks' re-entry. The 19.5 report does not state this")
print("\nnesting asymmetry confirmed in scripts/s195_strip.py")

peak = rss_gb()
add("resources", item="memory_ceiling_gb", value=MEM_CEILING_GB,
    note="stated before running")
add("resources", item="peak_rss_gb", value=round(peak, 3),
    within=int(peak <= MEM_CEILING_GB))
add("resources", item="seconds", value=round(time.time() - t_all, 1))
print(f"\npeak {peak:.3f} GB, {time.time()-t_all:.1f}s")

COLS = ["table", "item", "value", "within", "note", "note2"]
with open(OUT / "jan2013-read.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'jan2013-read.csv'} with {len(rows)} rows")
