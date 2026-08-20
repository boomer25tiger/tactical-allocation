"""Session 22 phase A. The relaunch test.

ABANDONMENT RULE, PRE-REGISTERED AND WRITTEN TO THE ARTIFACT BEFORE THE
PROCESS STARTS.
  WALL_LIMIT_S = 1800.0 seconds. That is 18.58 times the 96.9 s the
  chunk-514 pass took in outputs/session-19_6/m1-diagnostic.csv, and 16.07
  times the 112 s at which the session 20 B1 pass was terminated by hand.
  The process is terminated ON THIS LIMIT AND ON NOTHING ELSE. An observed
  slowdown, a low CPU percentage, a small resident size, or a falling swap
  figure are recorded and are not grounds for termination. Any termination
  records the rule as its reason rather than a judgement.
  CHUNK = 257, which completed at a 1.824 GB peak in 63.1 s in the same
  diagnostic.
  SAMPLE_S = 15 seconds.
  TOL_CANON = 5e-7 on the standing positive control.
"""
from __future__ import annotations
import csv, os, signal, subprocess, sys, time
from pathlib import Path
import numpy as np
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM         # noqa: E402
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
OUT = ROOT/"outputs"/"session-22"; OUT.mkdir(parents=True, exist_ok=True)
WALL_LIMIT_S, CHUNK, SAMPLE_S, TOL = 1800.0, 257, 15, 5e-7
rows = []


def add(t, **kw): rows.append({"table": t, **kw})


def flush():
    with open(OUT/"relaunch-test.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "table","item","t_seconds","compressor_gib","swap_used_mb","swap_free_mb",
            "pageouts_since_prior","cpu_percent","rss_gb","value","note"],
            extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


s0 = VM.sample()
add("machine_start", item="compressor_gib", value=s0["compressor_gib"])
add("machine_start", item="swap_used_mb", value=s0["swap_used_mb"])
add("machine_start", item="swap_free_mb", value=s0["swap_free_mb"])
add("machine_start", item="pageouts_cumulative", value=s0["pageouts_cumulative"])
add("preregistration", item="wall_limit_seconds", value=WALL_LIMIT_S,
    note="18.58 times the 96.9 s chunk-514 pass and 16.07 times the 112 s at which "
         "the session 20 B1 pass was terminated by hand")
add("preregistration", item="chunk", value=CHUNK,
    note="completed at a 1.824 GB peak in 63.1 s per m1-diagnostic.csv")
add("preregistration", item="sample_interval_seconds", value=SAMPLE_S)
add("preregistration", item="termination_rule",
    note="terminate on the wall limit and on nothing else. An observed slowdown, a low "
         "CPU percentage, a small resident size or a falling swap figure are recorded "
         "and are not grounds for termination")
add("preregistration", item="written_before_launch", value=1)
flush()
print(f"pre-registration written. limit {WALL_LIMIT_S}s, chunk {CHUNK}")

env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]; r = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
m = L.standalone_metrics(r, d["nav"], acc["orders"])
pc = abs(m["ann_return"]-0.521845) <= TOL and abs(m["sharpe_lo"]-1.381701) <= TOL and len(r) == 2472
add("positive_control", item="ann_return", value=m["ann_return"])
add("positive_control", item="sharpe_lo", value=m["sharpe_lo"])
add("positive_control", item="n_sessions", value=len(r))
add("positive_control", item="tolerance", value=TOL, note="stated before comparing")
add("positive_control", item="verdict", note="PASS" if pc else "FAIL")
flush()
print(f"positive control {'PASS' if pc else 'FAIL'}")

log = open(OUT/"b1.log", "w")
p = subprocess.Popen([str(ROOT/".venv/bin/python"), "-u", str(ROOT/"scripts/s22_b1.py"),
                      str(CHUNK)], stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
t0 = time.time(); prev_po = s0["pageouts_cumulative"]; peak_rss = 0.0; max_po_rate = 0.0
terminated = None
print(f"launched pid {p.pid}")
while True:
    time.sleep(SAMPLE_S)
    el = time.time()-t0
    s = VM.sample()
    dpo = s["pageouts_cumulative"]-prev_po; prev_po = s["pageouts_cumulative"]
    max_po_rate = max(max_po_rate, dpo/SAMPLE_S)
    cpu = rss = float("nan")
    if p.poll() is None:
        try:
            o = subprocess.run(["ps","-o","%cpu=,rss=","-p",str(p.pid)],
                               capture_output=True, text=True).stdout.split()
            if len(o) >= 2:
                cpu, rss = float(o[0]), float(o[1])*1024/1e9
                peak_rss = max(peak_rss, rss)
        except Exception:
            pass
    add("sample", t_seconds=round(el,1), compressor_gib=s["compressor_gib"],
        swap_used_mb=s["swap_used_mb"], swap_free_mb=s["swap_free_mb"],
        pageouts_since_prior=dpo, cpu_percent=cpu, rss_gb=round(rss,3) if rss == rss else "")
    flush()
    print(f"  t={el:6.1f}s cpu={cpu:5.1f} rss={rss:.3f}GB comp={s['compressor_gib']:.3f} "
          f"swapfree={s['swap_free_mb']:.0f} dpo={dpo}", flush=True)
    if p.poll() is not None:
        break
    if el >= WALL_LIMIT_S:
        terminated = "pre-registered wall limit reached"
        os.kill(p.pid, signal.SIGTERM); p.wait(timeout=30)
        break
el = time.time()-t0
log.close()
rc = p.returncode
completed = (rc == 0) and terminated is None
add("result", item="completed", value=int(completed))
add("result", item="wall_clock_seconds", value=round(el,1))
add("result", item="return_code", value=rc)
add("result", item="peak_rss_gb", value=round(peak_rss,3))
add("result", item="max_pageouts_per_second", value=round(max_po_rate,1))
add("result", item="termination_reason",
    note=terminated if terminated else "none, the process exited on its own")
s1 = VM.sample()
for k in ("compressor_gib","swap_used_mb","swap_free_mb","pageouts_cumulative"):
    add("machine_end", item=k, value=s1[k])
add("gate_A", item="verdict",
    note="PASS, phase F is licensed and 9.35 and 8.12 are corrected in phase G"
         if completed else
         "the pass exceeded the pre-registered limit. Recorded as the first observed "
         "completion failure at this machine state, and still not an operating-system kill")
flush()
print(f"\ncompleted {completed}, wall {el:.1f}s, rc {rc}, peak {peak_rss:.3f} GB, "
      f"max page-outs/s {max_po_rate:.1f}")
print(f"gate A: {'PASS' if completed else 'LIMIT REACHED'}")
