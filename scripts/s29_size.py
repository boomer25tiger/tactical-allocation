"""Session 29 phase H. Sizes read BEFORE the commit with the expected delta stated,
under the convention at 9.62. Nothing is read after the commit."""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-29"


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True,
                          cwd=ROOT).stdout.strip()


rows = []
def add(t, **kw): rows.append({"table": t, **kw})

sh("git add -A")
names = [n for n in sh("git diff --cached --name-only").split("\n") if n]
delta = sum((ROOT / n).stat().st_size for n in names if (ROOT / n).exists())
new = [n for n in names if sh(f"git log --oneline -1 -- '{n}'") == ""]
newb = sum((ROOT / n).stat().st_size for n in new if (ROOT / n).exists())
add("commit_contents", item="files_in_the_commit", value=len(names))
add("commit_contents", item="bytes_of_those_files", value=delta)
add("commit_contents", item="files_new_to_the_repository", value=len(new))
add("commit_contents", item="bytes_new_to_the_repository", value=newb)

big = sh("git ls-files -z | xargs -0 stat -f '%z %N' | sort -rn | head -1").split(None, 1)
add("size", item="largest_tracked_file_bytes", value=big[0], note=big[1])
add("size", item="largest_tracked_file_mb", value=f"{int(big[0])/1048576:.2f}",
    note="against the 100 megabyte limit")
add("size", item="tracked_files_over_100mb",
    value=int(sh("git ls-files -z | xargs -0 stat -f '%z %N' | "
                 "awk '$1>104857600' | wc -l")))
gk = int(sh("du -sk .git | cut -f1")); wk = int(sh("du -sk . | cut -f1"))
fk = int(sh("df -k . | tail -1").split()[3])
add("size", item="git_directory_kib_before_commit", value=gk)
add("size", item="working_tree_kib_before_commit", value=wk)
add("space", item="free_kib_before_commit", value=fk)
add("space", item="free_gib_before_commit", value=f"{fk/1048576:.2f}")
add("expected_delta", item="working_tree_kib", value="+0",
    note="every file the commit touches is already written to disk, so the working "
         "tree reading above already includes them")
add("expected_delta", item="git_directory_kib", value=f"+{newb/1024:.0f} or less",
    note=f"the commit writes objects for {len(names)} files totalling {delta} bytes on "
         f"disk, of which {newb} bytes are new. Objects are zlib compressed, and the "
         f"parquet series files here compress less than text does")
add("expected_delta", item="free_space_gib", value="0.00 to -0.01",
    note="the commit adds well under one gibibyte")
with open(OUT / "size.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["table", "item", "value", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote size.csv, {len(rows)} rows")
for r in rows:
    print(f"  {r['table']:18s} {r['item']:36s} {r['value']}")
