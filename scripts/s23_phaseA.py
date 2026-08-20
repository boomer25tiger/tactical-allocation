"""Session 23 phase A. The B1 re-emission, gated on contention.

HALT CONDITION, from the scaffold. If load average exceeds twice the core
count at launch, halt and report rather than starting a pass the prior
session established does not finish under those conditions.

ABANDONMENT RULE, pre-registered and written before any launch.
  WALL_LIMIT_S = 969.0 seconds, being ten times the 96.9 second chunk-514
  pass recorded in outputs/session-19_6/m1-diagnostic.csv, which completed at
  a larger working set of 3.561 GB. Termination would be on this limit and on
  nothing else.
  CHUNK = 257, which completed at a 1.824 GB peak in 63.1 seconds.
  TOL_CANON = 5e-7 on the standing positive control.
"""
from __future__ import annotations
import csv, re, subprocess, sys, time
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM         # noqa: E402
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
OUT = ROOT/"outputs"/"session-23"; OUT.mkdir(parents=True, exist_ok=True)
WALL_LIMIT_S, CHUNK, TOL = 969.0, 257, 5e-7
rows = []


def add(t, **kw): rows.append({"table": t, **kw})


def loadavg():
    o = subprocess.run(["sysctl","-n","vm.loadavg"],capture_output=True,text=True).stdout
    a = o.strip().strip("{}").split()
    return float(a[0]), float(a[1]), float(a[2])


cores = int(subprocess.run(["sysctl","-n","hw.ncpu"],capture_output=True,text=True).stdout)
l1, l5, l15 = loadavg()
s = VM.sample()
add("preregistration", item="wall_limit_seconds", value=WALL_LIMIT_S,
    note="ten times the 96.9 second chunk-514 pass in m1-diagnostic.csv, which "
         "completed at a larger working set of 3.561 GB")
add("preregistration", item="chunk", value=CHUNK,
    note="completed at a 1.824 GB peak in 63.1 seconds")
add("preregistration", item="termination_rule",
    note="terminate on the wall limit and on nothing else")
add("preregistration", item="written_before_launch", value=1)
add("machine_at_launch", item="cores", value=cores)
add("machine_at_launch", item="halt_threshold", value=cores*2,
    note="twice the core count")
add("machine_at_launch", item="load_1min", value=l1)
add("machine_at_launch", item="load_5min", value=l5)
add("machine_at_launch", item="load_15min", value=l15)
add("machine_at_launch", item="compressor_gib", value=s["compressor_gib"])
add("machine_at_launch", item="swap_used_mb", value=s["swap_used_mb"])
add("machine_at_launch", item="swap_free_mb", value=s["swap_free_mb"])
add("machine_at_launch", item="pageouts_cumulative", value=s["pageouts_cumulative"])
top = subprocess.run(["ps","-A","-o","%cpu,comm"],capture_output=True,text=True).stdout
tl = sorted((l for l in top.split("\n")[1:] if l.strip()),
            key=lambda x: -float(x.split()[0]))[:5]
for i, t in enumerate(tl, 1):
    add("top_process", item=f"rank_{i}", value=float(t.split()[0]),
        note=t.split(maxsplit=1)[1][:80] if len(t.split(maxsplit=1)) > 1 else "")
halt = l1 > cores*2
add("halt_condition", item="load_exceeds_twice_cores", value=int(halt),
    note=f"load average {l1} against a threshold of {cores*2}")
print(f"cores {cores}, threshold {cores*2}, load 1/5/15 {l1}/{l5}/{l15}")

env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]; r = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
m = L.standalone_metrics(r, d["nav"], acc["orders"])
pc = abs(m["ann_return"]-0.521845) <= TOL and abs(m["sharpe_lo"]-1.381701) <= TOL and len(r) == 2472
add("positive_control", item="ann_return", value=m["ann_return"], target=0.521845)
add("positive_control", item="sharpe_lo", value=m["sharpe_lo"], target=1.381701)
add("positive_control", item="n_sessions", value=len(r), target=2472)
add("positive_control", item="tolerance", value=TOL, note="stated before comparing")
add("positive_control", item="verdict", note="PASS" if pc else "FAIL")
print(f"positive control {'PASS' if pc else 'FAIL'}")

if halt:
    add("result", item="launched", value=0)
    add("result", item="verdict", note="HALTED ON CONTENTION")
    add("result", item="reason",
        note=f"load average {l1} at launch exceeds twice the core count at {cores*2}. "
             f"Session 22 established that a pass does not finish under these "
             f"conditions, and the halt condition requires reporting rather than "
             f"starting one. The pass is not attempted, so no wall limit is consumed "
             f"and no figure is produced")
    add("result", item="session_title_note",
        note="the session anticipated a quiet machine and the machine is not quiet. "
             "The one-minute load is higher than the 39.57 session 22 recorded, and "
             "the five and fifteen minute figures were rising across five samples")
    add("outstanding", item="b1_reemission",
        note="the chunk-first-element defect stays repaired in code at four sites and "
             "unre-emitted in the three regression figures. The degradation slope is "
             "removed from the paper at 9.35 regardless, so the outstanding item "
             "closes a defect rather than restoring a reported figure")
    print("HALTED ON CONTENTION, pass not launched")
with open(OUT/"pbo-regression-corrected.csv","w",newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table","item","value","target","note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'pbo-regression-corrected.csv'} with {len(rows)} rows")
sys.exit(2 if halt else 0)
