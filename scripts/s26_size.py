"""Session 26 phase E. Sizes read BEFORE the commit with the expected delta stated.

The convention adopted at 9.62. Nothing is read after the commit, so no file is
left dirty carrying a post-commit reading.
"""
from __future__ import annotations
import csv, hashlib, subprocess, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT/"outputs"/"session-26"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True,
                                 cwd=ROOT).stdout.strip()
rows = []
def add(t, **kw): rows.append({"table": t, **kw})

# staged and untracked content this commit will add
sh("git add -A")
names = [n for n in sh("git diff --cached --name-only").split("\n") if n]
delta = 0
for n in names:
    p = ROOT/n
    if p.exists(): delta += p.stat().st_size
add("commit_contents", item="files_in_the_commit", value=len(names))
add("commit_contents", item="bytes_of_those_files", value=delta,
    note="the on-disk size of every file the commit touches, which bounds the working "
         "tree delta above since most are rewrites of existing files rather than "
         "additions")
new = [n for n in names if sh(f"git log --oneline -1 -- '{n}'") == ""]
newb = sum((ROOT/n).stat().st_size for n in new if (ROOT/n).exists())
add("commit_contents", item="files_new_to_the_repository", value=len(new))
add("commit_contents", item="bytes_new_to_the_repository", value=newb,
    note="the expected working tree delta, being the files that did not exist before")

big = sh("git ls-files -z | xargs -0 stat -f '%z %N' | sort -rn | head -1").split(None, 1)
add("size", item="largest_tracked_file_bytes", value=big[0], note=big[1])
add("size", item="largest_tracked_file_mb", value=f"{int(big[0])/1048576:.2f}",
    note="against the 100 megabyte limit")
add("size", item="tracked_files_over_100mb",
    value=int(sh("git ls-files -z | xargs -0 stat -f '%z %N' | awk '$1>104857600' | wc -l")))
gk = int(sh("du -sk .git | cut -f1")); wk = int(sh("du -sk . | cut -f1"))
fk = int(sh("df -k . | tail -1").split()[3])
add("size", item="git_directory_kib_before_commit", value=gk)
add("size", item="working_tree_kib_before_commit", value=wk)
add("space", item="free_kib_before_commit", value=fk)
add("space", item="free_gib_before_commit", value=f"{fk/1048576:.2f}")
add("expected_delta", item="working_tree_kib", value="+0",
    note="every file the commit touches is already written to disk, so the working tree "
         "reading above already includes them and committing adds no working tree bytes")
add("expected_delta", item="git_directory_kib", value=f"+{newb/1024:.0f} or less",
    note=f"the commit writes objects for {len(names)} files totalling {delta} bytes on "
         f"disk, of which {newb} bytes are new to the repository. Objects are zlib "
         f"compressed and these are text files that compress well, so the git directory "
         f"is expected to grow by rather less than that")
add("expected_delta", item="free_space_gib", value="0.00 to -0.01",
    note="the commit adds well under one gibibyte, so free space is expected to read "
         "unchanged at two decimals or one hundredth lower")

# the verification hook as run pre-commit
r = subprocess.run([sys.executable, str(ROOT/"scripts"/"verify_prediction_precedes_read.py")],
                   capture_output=True, text=True, cwd=ROOT)
add("verification_hook", item="exit_code_pre_commit", value=r.returncode,
    note="non-zero as expected, since the commit happens after this reading")
for line in r.stdout.strip().split("\n"):
    if line.strip().startswith(("working copy", "FAIL", "PASS", "commit", "blob")):
        k, _, val = line.strip().partition("  ")
        add("verification_hook", item=k.strip(), value=val.strip())
P = ROOT/"docs"/"HOLDOUT-PREDICTION.md"
add("prediction", item="sha256", value=hashlib.sha256(P.read_bytes()).hexdigest())
add("prediction", item="bytes", value=P.stat().st_size)

fn = ["table", "item", "value", "note"]
with open(OUT/"size-and-verification.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
    for x in rows: w.writerow({k: x.get(k, "") for k in fn})
print(f"wrote size-and-verification.csv, {len(rows)} rows")
for x in rows:
    if x["table"] in ("commit_contents", "size", "space", "expected_delta", "verification_hook"):
        print(f"  {x['table']:18s} {x['item']:34s} {x['value']}")
