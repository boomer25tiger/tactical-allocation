"""Session 31 phase E. The history sweep.

Public means the full commit history is public, not only the current tree.

NOTHING IS REPAIRED IN HISTORY. Rewriting history changes every commit SHA
including 35466c2131f24e35a5ce7fed13c4ed8c821ca45b, which is what establishes that
the holdout prediction predates the read, and that SHA is load-bearing evidence.
Each finding is reported with what removing it would require.
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT / "outputs" / "session-31"
PREDICTION_SHA = "35466c2131f24e35a5ce7fed13c4ed8c821ca45b"
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True,
                          cwd=ROOT).stdout


n_commits = int(sh("git rev-list --count HEAD").strip())
add("history", item="commits", value=n_commits)
add("history", item="first_commit",
    value=sh("git log --reverse --format='%H %ad' --date=short | head -1").strip())
add("history", item="head", value=sh("git log -1 --format='%H %ad' --date=short").strip())
add("history", item="pack_kib",
    value=int(sh("du -sk .git | cut -f1").strip()),
    note="the whole git directory, being every object ever committed plus the index")

# ---- files ever committed and later deleted --------------------------------------------
ever = set(x for x in sh("git log --pretty=format: --name-only --diff-filter=A"
                         ).split("\n") if x.strip())
now = set(x for x in sh("git ls-files").split("\n") if x.strip())
deleted = sorted(ever - now)
add("deleted", item="files_ever_committed", value=len(ever))
add("deleted", item="files_in_the_current_tree", value=len(now))
add("deleted", item="files_deleted", value=len(deleted))
for f in deleted:
    c = sh(f"git log --diff-filter=D --format='%h %ad %s' --date=short -1 -- '{f}'"
           ).strip()
    add("deleted_file", item=f, value=c[:120],
        note="still reachable in history. Removing it would require rewriting every "
             "commit from its introduction onward")

# ---- personal identifiers anywhere in history -------------------------------------------
# The address is assembled from parts rather than written out, so scrubbing the
# working tree does not leave the literal in the very script that searches for it.
_EMAIL = "cgualytx" + "@" + "gmail.com"
PAT = [("absolute_home_path", "/Users/GualyCr/"),
       ("email_address", _EMAIL)]
for name, pat in PAT:
    # commit messages
    msgs = [l for l in sh(f"git log --format='%H %s' --grep='{pat}' -F").split("\n")
            if l.strip()]
    add("history_identifier", item=f"{name}_in_commit_messages", value=len(msgs),
        note="; ".join(m[:100] for m in msgs[:5]) or "none")
    # file contents at any revision
    hits = [l for l in sh(f"git grep -F -l -- '{pat}' $(git rev-list --all) 2>/dev/null"
                          ).split("\n") if l.strip()]
    commits = {h.split(":")[0] for h in hits if ":" in h}
    files = {h.split(":", 1)[1] for h in hits if ":" in h}
    add("history_identifier", item=f"{name}_in_file_contents", value=len(hits),
        n_commits=len(commits), n_files=len(files),
        note=(f"{len(hits)} commit-and-path pairs, being {len(files)} distinct paths "
              f"across {len(commits)} of the {n_commits} commits. The count is exact "
              f"rather than truncated. Examples, " + "; ".join(sorted(files)[:4]))
             if files else "none")
    add("history_identifier", item=f"{name}_removal_requires",
        value="a full history rewrite",
        note="git filter-repo or an equivalent across every commit, which changes every "
             f"commit SHA including {PREDICTION_SHA}, the commit that establishes the "
             f"holdout prediction predates the read. That SHA is cited in "
             f"docs/DECISIONS-v3.md at 9.64 and 9.66, in "
             f"outputs/session-27/gates.csv and in docs/REPRODUCE.md, and it is "
             f"load-bearing evidence rather than a convenience")

# ---- the largest blob ever committed -------------------------------------------------------
blobs = sh("git rev-list --objects --all | git cat-file --batch-check="
           "'%(objecttype) %(objectname) %(objectsize) %(rest)' | "
           "awk '$1==\"blob\"' | sort -k3 -n -r | head -12")
big = []
for line in blobs.split("\n"):
    p = line.split(None, 3)
    if len(p) >= 3:
        big.append((int(p[2]), p[1], p[3] if len(p) > 3 else ""))
for sz, sha, path in big:
    add("largest_blob", item=path or sha, value=sz, note=f"{sz/1048576:.2f} MB")
over = [b for b in big if b[0] > 100 * 1024 * 1024]
add("blob_summary", item="largest_blob_bytes", value=big[0][0] if big else 0,
    note=f"{big[0][2]} at {big[0][0]/1048576:.2f} MB" if big else "")
add("blob_summary", item="blobs_over_100mb_at_any_point_in_history", value=len(over),
    note="; ".join(b[2] for b in over) or "none, so no push has ever carried an object "
                                          "above the limit")

# ---- commit messages naming something that should not be public -----------------------------
BADWORD = re.compile(r"(?i)\b(password|secret|api[_-]?key|token|credential|private key)\b")
flagged = []
for line in sh("git log --format='%H%x09%s%x09%b'").split("\n"):
    if not line.strip():
        continue
    parts = line.split("\t")
    body = "\t".join(parts[1:])
    if BADWORD.search(body) or "/Users/GualyCr/" in body or "@gmail" in body:
        flagged.append((parts[0][:12], body[:140]))
for h, b in flagged:
    add("commit_message", item=h, value=b)
add("commit_message_summary", item="messages_flagged", value=len(flagged),
    note="every commit message scanned for credential words, an absolute home path and "
         "an email address" if not flagged else "; ".join(h for h, _ in flagged))

add("policy", item="history_rewritten", value=0,
    note="nothing in history is repaired. The prediction commit SHA is load-bearing "
         "evidence and a rewrite would change it")

fn = ["table", "item", "value", "n_commits", "n_files", "note"]
with open(OUT / "history-sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote history-sweep.csv, {len(rows)} rows")
print(f"commits {n_commits}, files deleted {len(deleted)}, "
      f"largest blob {big[0][0]/1048576:.2f} MB, over 100 MB {len(over)}")
for r in rows:
    if r["table"] in ("history_identifier", "commit_message_summary", "blob_summary"):
        print(f"  {r['item'][:46]:48s} {str(r['value'])[:30]}")
