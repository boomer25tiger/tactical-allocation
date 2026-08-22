"""Session 24 phase F. The B1 re-emission, with the launch scripts/s23_phaseA.py lacks.

The session 23 script carries the pre-registered rule and the halt check but has
no branch that launches a pass, so running it unchanged on a quiet machine
writes a passed positive control and no measurement. The rule below is taken
from that script verbatim rather than restated.

  WALL_LIMIT_S = 969.0 seconds, ten times the 96.9 second chunk-514 pass in
  outputs/session-19_6/m1-diagnostic.csv which completed at a larger working
  set of 3.561 GB.
  CHUNK = 257, which completed at a 1.824 GB peak in 63.1 seconds.
  Terminate on the wall limit and on nothing else.
  HALT if the one-minute load average exceeds twice the core count at launch.
"""
from __future__ import annotations
import csv, os, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path("/Users/GualyCr/Downloads/tactical-allocation"); sys.path.insert(0,str(ROOT))
import scripts.s22_vm as VM   # noqa: E402
OUT=ROOT/"outputs"/"session-24"; OUT.mkdir(parents=True,exist_ok=True)
WALL_LIMIT_S, CHUNK, SAMPLE_S = 969.0, 257, 30
rows=[]
def add(t,**kw): rows.append({"table":t,**kw})
def flush():
    with open(OUT/"phaseF-relaunch.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=["table","item","t_seconds","load_1min",
            "cpu_percent","rss_gb","compressor_gib","swap_used_mb","swap_free_mb",
            "value","note"],extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
def load(): 
    a=subprocess.run(["sysctl","-n","vm.loadavg"],capture_output=True,text=True).stdout
    return [float(x) for x in a.strip().strip("{}").split()]
cores=int(subprocess.run(["sysctl","-n","hw.ncpu"],capture_output=True,text=True).stdout)
l=load(); s0=VM.sample()
add("script_defect",item="s23_phaseA_has_no_launch_branch",value=1,
    note="scripts/s23_phaseA.py contains only an 'if halt' branch, so run unchanged on a "
         "quiet machine it writes a passed positive control and no pass. The scaffold's "
         "instruction to run it unchanged cannot close the measurement, and the rule it "
         "pre-registered is reused here verbatim")
add("orphans",item="multiprocessing_workers_found",value=0,
    note="session 23 identified four Python workers aged over one day at 0.0 percent "
         "CPU. None is present now, so the kill step had nothing to terminate")
add("orphans",item="compressor_gib_before",value=s0["compressor_gib"])
add("preregistration",item="wall_limit_seconds",value=WALL_LIMIT_S,
    note="ten times the 96.9 second chunk-514 pass, taken from scripts/s23_phaseA.py")
add("preregistration",item="chunk",value=CHUNK)
add("preregistration",item="termination_rule",
    note="terminate on the wall limit and on nothing else")
add("machine_at_launch",item="cores",value=cores)
add("machine_at_launch",item="halt_threshold",value=cores*2)
add("machine_at_launch",item="load_1min",value=l[0])
add("machine_at_launch",item="load_5min",value=l[1])
add("machine_at_launch",item="load_15min",value=l[2])
add("machine_at_launch",item="compressor_gib",value=s0["compressor_gib"])
add("machine_at_launch",item="swap_used_mb",value=s0["swap_used_mb"])
add("machine_at_launch",item="swap_free_mb",value=s0["swap_free_mb"])
halt = l[0] > cores*2
add("halt_condition",item="load_exceeds_twice_cores",value=int(halt),
    note=f"load {l[0]} against threshold {cores*2}")
flush()
print(f"cores {cores} threshold {cores*2} load {l}")
if halt:
    add("result",item="launched",value=0)
    add("result",item="verdict",note="HALTED ON CONTENTION")
    flush(); print("HALTED"); sys.exit(2)

env=dict(os.environ); env["S24_OUTDIR"]="session-24"
log=open(OUT/"b1.log","w")
p=subprocess.Popen([str(ROOT/".venv/bin/python"),"-u",str(ROOT/"scripts/s22_b1.py"),
                    str(CHUNK)],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT,env=env)
t0=time.time(); peak=0.0; terminated=None
print(f"launched pid {p.pid}")
while True:
    time.sleep(SAMPLE_S)
    el=time.time()-t0; s=VM.sample(); ll=load()
    cpu=rss=float("nan")
    if p.poll() is None:
        o=subprocess.run(["ps","-o","%cpu=,rss=","-p",str(p.pid)],
                         capture_output=True,text=True).stdout.split()
        if len(o)>=2:
            cpu,rss=float(o[0]),float(o[1])*1024/1e9; peak=max(peak,rss)
    add("sample",t_seconds=round(el,1),load_1min=ll[0],cpu_percent=cpu,
        rss_gb=round(rss,3) if rss==rss else "",compressor_gib=s["compressor_gib"],
        swap_used_mb=s["swap_used_mb"],swap_free_mb=s["swap_free_mb"])
    flush()
    print(f"  t={el:6.1f}s load={ll[0]:5.2f} cpu={cpu:5.1f} rss={rss:.3f}GB",flush=True)
    if p.poll() is not None: break
    if el>=WALL_LIMIT_S:
        terminated="pre-registered wall limit reached"
        os.kill(p.pid,signal.SIGTERM); p.wait(timeout=30); break
el=time.time()-t0; log.close(); rc=p.returncode
completed=(rc==0) and terminated is None
s1=VM.sample()
add("result",item="launched",value=1)
add("result",item="completed",value=int(completed))
add("result",item="wall_clock_seconds",value=round(el,1))
add("result",item="return_code",value=rc)
add("result",item="peak_rss_gb",value=round(peak,3))
add("result",item="termination_reason",
    note=terminated if terminated else "none, the process exited on its own")
add("machine_at_end",item="compressor_gib",value=s1["compressor_gib"])
add("machine_at_end",item="swap_used_mb",value=s1["swap_used_mb"])
add("machine_at_end",item="load_1min",value=load()[0])
flush()
print(f"\ncompleted {completed} wall {el:.1f}s rc {rc} peak {peak:.3f} GB")
