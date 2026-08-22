"""Session 25 phase F. Machine, repository size and free space, measured not recalled."""
from __future__ import annotations
import csv, subprocess, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM   # noqa: E402
when = sys.argv[1]
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True,
                                 cwd=ROOT).stdout.strip()
rows = []
def add(t, **kw): rows.append({"table": t, "when": when, **kw})
l = [float(x) for x in sh("sysctl -n vm.loadavg").strip("{} ").split()]
s = VM.sample()
for k, v in (("load_1min", l[0]), ("load_5min", l[1]), ("load_15min", l[2]),
             ("compressor_gib", s["compressor_gib"]), ("swap_used_mb", s["swap_used_mb"]),
             ("swap_free_mb", s["swap_free_mb"])):
    add("machine", item=k, value=v)
big = sh("git ls-files -z | xargs -0 stat -f '%z %N' | sort -rn | head -1").split(None, 1)
add("size", item="largest_tracked_file_bytes", value=big[0], note=big[1])
add("size", item="largest_tracked_file_mb", value=f"{int(big[0])/1048576:.2f}",
    note="against the 100 megabyte limit")
over = sh("git ls-files -z | xargs -0 stat -f '%z %N' | awk '$1>104857600' | wc -l")
add("size", item="tracked_files_over_100mb", value=int(over))
add("size", item="git_dir_bytes", value=sh("du -sk .git | cut -f1").strip())
add("size", item="working_tree_bytes", value=sh("du -sk . | cut -f1").strip(),
    note="kilobytes as du reports them")
df = sh("df -k . | tail -1").split()
add("space", item="free_kilobytes", value=df[3])
add("space", item="free_gib", value=f"{int(df[3])/1048576:.2f}")
p = ROOT/"outputs"/"session-25"/"machine-and-size.csv"
old = list(csv.DictReader(open(p))) if p.exists() else []
fn = ["table", "when", "item", "value", "note"]
with open(p, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
    for r in old + rows: w.writerow({k: r.get(k, "") for k in fn})
print(f"{when}: load {l[0]}, compressor {s['compressor_gib']} GiB, "
      f"largest tracked file {int(big[0])/1048576:.2f} MB, over 100 MB {over}, "
      f"free {int(df[3])/1048576:.2f} GiB")
