"""Session 19 step 10: delete the ephemeral panel.

Runs only after the step 8 regenerability check passed and the step 9
manifest exists, since the manifest carries the canonicalised hash that
makes the deletion reversible by regeneration.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S17 = ROOT / "outputs" / "session-17"
PANEL = S17 / "panel"
SUP = S17 / "superseded-10axis"
S18 = ROOT / "outputs" / "session-18"
OUT = ROOT / "outputs" / "session-19"
rows = []


def add(table, item, value="", note=""):
    rows.append({"table": table, "item": item, "value": value, "note": note})


def dsize(p: Path) -> int:
    if not p.exists():
        return 0
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def free_bytes() -> int:
    st = os.statvfs(ROOT)
    return st.f_bavail * st.f_frsize


def pct_used() -> float:
    st = os.statvfs(ROOT)
    return 100.0 * (1.0 - st.f_bavail / st.f_blocks)


# --- preconditions ---------------------------------------------------------
man = OUT / "MANIFEST.json"
assert man.exists(), "step 9 manifest must exist before deletion"
m = json.loads(man.read_text())
assert m.get("canonicalised_panel_sha256"), "manifest carries no panel hash"
regen_hash_file = OUT / ".regen-hash-before-deletion"
assert regen_hash_file.exists(), "step 8 regenerability hash not recorded"
before_hash = regen_hash_file.read_text().strip()
add("precondition", "manifest_present", 1, str(man.relative_to(ROOT)))
add("precondition", "canonicalised_panel_sha256", m["canonicalised_panel_sha256"])
add("precondition", "regenerability_hash_before", before_hash)
print(f"manifest present, panel hash {m['canonicalised_panel_sha256'][:16]}...")

# --- before ----------------------------------------------------------------
repo_before = dsize(ROOT / "outputs") + dsize(ROOT / "data") + dsize(ROOT / "src") \
    + dsize(ROOT / "scripts") + dsize(ROOT / "docs") + dsize(ROOT / ".git")
panel_before = dsize(PANEL)
sup_panel_before = dsize(SUP / "panel")
sup_total_before = dsize(SUP)
free_before = free_bytes()
pct_before = pct_used()
add("before", "panel_bytes", panel_before)
add("before", "panel_mb", f"{panel_before/1e6:.1f}")
add("before", "superseded_panel_bytes", sup_panel_before)
add("before", "superseded_total_bytes", sup_total_before)
add("before", "repository_bytes", repo_before)
add("before", "repository_mb", f"{repo_before/1e6:.1f}")
add("before", "free_bytes", free_before)
add("before", "free_gb", f"{free_before/1e9:.1f}")
add("before", "percent_used", f"{pct_before:.1f}")
print(f"panel {panel_before/1e6:.1f} MB, superseded panel {sup_panel_before/1e6:.1f} MB")
print(f"repository {repo_before/1e6:.1f} MB, free {free_before/1e9:.1f} GB "
      f"at {pct_before:.1f} percent used")

# --- superseded directory, reported before anything is touched -------------
print("\nsuperseded-10axis contents, reported rather than removed wholesale")
for sub in sorted(p for p in SUP.iterdir() if p.is_dir()):
    n = len(list(sub.glob("*")))
    add("superseded_content", sub.name, dsize(sub), f"{n} files")
    print(f"  {sub.name}/  {dsize(sub)/1e6:.1f} MB  {n} files")

# --- delete ----------------------------------------------------------------
n_panel = len(list(PANEL.glob("*.f32"))) if PANEL.exists() else 0
for f in sorted(PANEL.glob("*.f32")):
    f.unlink()
add("deleted", "session17_panel_files", n_panel, str(PANEL.relative_to(ROOT)))
print(f"\ndeleted {n_panel} shards from {PANEL.relative_to(ROOT)}")

n_sup = 0
if (SUP / "panel").exists():
    n_sup = len(list((SUP / "panel").glob("*.f32")))
    shutil.rmtree(SUP / "panel")
add("deleted", "superseded_panel_files", n_sup,
    "only the panel directory; moments, block sizes, metrics and logs preserved")
print(f"deleted {n_sup} shards from {(SUP/'panel').relative_to(ROOT)}")

# --- after -----------------------------------------------------------------
repo_after = dsize(ROOT / "outputs") + dsize(ROOT / "data") + dsize(ROOT / "src") \
    + dsize(ROOT / "scripts") + dsize(ROOT / "docs") + dsize(ROOT / ".git")
free_after = free_bytes()
reclaimed = panel_before + sup_panel_before
add("after", "repository_bytes", repo_after)
add("after", "repository_mb", f"{repo_after/1e6:.1f}")
add("after", "reclaimed_bytes", reclaimed)
add("after", "reclaimed_mb", f"{reclaimed/1e6:.1f}")
add("after", "free_bytes", free_after)
add("after", "free_gb", f"{free_after/1e9:.1f}")
add("after", "percent_used", f"{pct_used():.1f}")
add("after", "superseded_remaining_bytes", dsize(SUP))
print(f"\nreclaimed {reclaimed/1e6:.1f} MB")
print(f"repository {repo_before/1e6:.1f} MB before, {repo_after/1e6:.1f} MB after")
print(f"free {free_before/1e9:.1f} GB before, {free_after/1e9:.1f} GB after, "
      f"{pct_used():.1f} percent used")

print("\nsuperseded-10axis after, moments and logs preserved")
for sub in sorted(p for p in SUP.iterdir() if p.is_dir()):
    add("superseded_remaining", sub.name, dsize(sub), f"{len(list(sub.glob('*')))} files")
    print(f"  {sub.name}/  {dsize(sub)/1e6:.1f} MB  {len(list(sub.glob('*')))} files")

# --- what must remain ------------------------------------------------------
print("\nrequired artifacts after deletion")
required = {
    "moment shards": sorted((S17 / "grid").glob("moments-*.f64")),
    "metric shards": sorted((S17 / "grid").glob("metrics-*.f64")),
    "index shards": sorted((S17 / "grid").glob("index-*.i64")),
    "block sizes": [S17 / "grid" / "block-sizes.npy"],
    "augmented specification index": [S18 / "spec-index-augmented.csv"],
    "subsample": [S18 / "subsample-ids.npy", S18 / "subsample-returns.npy"],
    "manifest": [man],
    "PBO report": [OUT / "PBO-REPORT.md"],
}
allok = True
for name, paths in required.items():
    ok = all(p.exists() and p.stat().st_size > 0 for p in paths)
    allok &= ok
    add("required_artifact", name, len(paths), "PRESENT" if ok else "MISSING")
    print(f"  {name:<32} {len(paths):>2} file(s)  {'PRESENT' if ok else 'MISSING'}")
add("required_artifact", "session REPORT.md", 0,
    "written at step 12, after this step, so it is absent here by design")
print("  session REPORT.md is written at step 12 and is absent here by design")

# --- regenerability after deletion ----------------------------------------
print("\nre-running the step 8 regenerability check after deletion")
r = subprocess.run([sys.executable, "scripts/s19_report.py"], cwd=ROOT,
                   capture_output=True, text=True)
import hashlib
h = hashlib.sha256()
h.update((OUT / "PBO-REPORT.md").read_bytes())
for f in sorted((OUT / "figures").glob("*.svg")):
    h.update(f.read_bytes())
after_hash = h.hexdigest()
match = after_hash == before_hash
add("regenerability_after", "exit_code", r.returncode)
add("regenerability_after", "hash_before_deletion", before_hash)
add("regenerability_after", "hash_after_deletion", after_hash)
add("regenerability_after", "byte_identical", int(match))
print(f"  generator exit {r.returncode}")
print(f"  before {before_hash}")
print(f"  after  {after_hash}")
print(f"  byte-identical {match}")

verdict = "PASS" if (allok and match and r.returncode == 0) else "FAIL"
add("verdict", "step10", verdict)
with open(OUT / "deletion.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "note"])
    w.writeheader(); w.writerows(rows)
print(f"\nSTEP 10: {verdict}")
print(f"wrote {OUT/'deletion.csv'} with {len(rows)} rows")
sys.exit(0 if verdict == "PASS" else 1)
