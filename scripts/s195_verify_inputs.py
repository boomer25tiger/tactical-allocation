"""Session 19.5 precondition: verify the frozen inputs against their manifests.

The session 17 panel is deleted, so every measurement in this session runs
from the frozen raw inputs. If any of them fails its manifest hash the
session halts before any measurement runs.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-19_5"
OUT.mkdir(parents=True, exist_ok=True)
TRUNC = ROOT / "outputs" / "session-00e" / "manifest-truncated.csv"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()


# Collect every manifest row across the acquisition manifests, with the 1.14
# truncation manifest superseding the acquisition hash for the files it touched.
# The manifests do not share a schema. Path lives in "file" or "filename", and
# the digest in "sha256" except in the truncation manifest where the post-
# truncation digest is "new_sha256".
ACQUISITION = [
    "outputs/session-00a/vx-manifest.csv",
    "outputs/session-00c/etf-manifest.csv",
    "outputs/session-01/etf-manifest.csv",
    "outputs/session-02/rates-manifest.csv",
    "outputs/session-08/index-manifest.csv",
    "outputs/session-10/synthetics-manifest.csv",
]


def path_of(row):
    for k in ("file", "filename", "path", "relpath"):
        v = row.get(k)
        if v:
            return v.strip()
    return None


# The VX manifest records a bare basename rather than a repository-relative
# path, so an unresolved entry is looked up by basename under data/.
_BY_NAME: dict[str, Path] = {}
for _p in (ROOT / "data").rglob("*"):
    if _p.is_file():
        _BY_NAME.setdefault(_p.name, _p)


def resolve(rel: str):
    p = ROOT / rel
    if p.exists() and p.is_file():
        return p
    return _BY_NAME.get(Path(rel).name)


expected: dict[str, tuple[str, str]] = {}
seen_manifests = []
for rel in ACQUISITION:
    m = ROOT / rel
    if not m.exists():
        continue
    seen_manifests.append(rel)
    with open(m) as fh:
        for row in csv.DictReader(fh):
            path, digest = path_of(row), (row.get("sha256") or "").strip().lower()
            if not path or not digest:
                continue
            p = resolve(path)
            if p is not None:
                expected[str(p.resolve())] = (digest, rel)

# also pick up any NAV or other manifest carrying a sha256 and a file column
for m in sorted(ROOT.glob("outputs/session-*/*manifest*.csv")):
    rel = str(m.relative_to(ROOT))
    if rel in ACQUISITION or m == TRUNC:
        continue
    with open(m) as fh:
        rdr = csv.DictReader(fh)
        if not rdr.fieldnames or "sha256" not in rdr.fieldnames:
            continue
        added = 0
        for row in rdr:
            path, digest = path_of(row), (row.get("sha256") or "").strip().lower()
            if not path or not digest:
                continue
            p = resolve(path)
            if p is not None and str(p.resolve()) not in expected:
                expected[str(p.resolve())] = (digest, rel)
                added += 1
        if added:
            seen_manifests.append(rel)

if TRUNC.exists():
    seen_manifests.append(str(TRUNC.relative_to(ROOT)) + " (1.14, supersedes)")
    with open(TRUNC) as fh:
        for row in csv.DictReader(fh):
            path = path_of(row)
            digest = (row.get("new_sha256") or "").strip().lower()
            if not path or not digest:
                continue
            p = resolve(path)
            if p is not None:
                expected[str(p.resolve())] = (
                    digest, str(TRUNC.relative_to(ROOT)) + " (1.14 truncation, supersedes)")

print("manifests read:")
for m in seen_manifests:
    print("  ", m)
print(f"manifest rows resolving to an existing file: {len(expected)}")

data_files = sorted(p for p in (ROOT / "data").rglob("*") if p.is_file()
                    and not p.name.startswith("."))
rows, bad, unmanifested = [], [], []
for p in data_files:
    key = str(p.resolve())
    got = sha(p)
    if key in expected:
        want, src = expected[key]
        ok = got == want
        rows.append({"table": "verified", "path": str(p.relative_to(ROOT)),
                     "bytes": p.stat().st_size, "sha256": got,
                     "manifest_sha256": want, "match": int(ok), "manifest_source": src})
        if not ok:
            bad.append(str(p.relative_to(ROOT)))
    else:
        unmanifested.append(str(p.relative_to(ROOT)))
        rows.append({"table": "unmanifested", "path": str(p.relative_to(ROOT)),
                     "bytes": p.stat().st_size, "sha256": got, "match": "",
                     "manifest_source": "no manifest row"})

n_ver = sum(1 for r in rows if r["table"] == "verified")
rows.append({"table": "summary", "path": "files_under_data", "bytes": len(data_files)})
rows.append({"table": "summary", "path": "manifested_and_checked", "bytes": n_ver})
rows.append({"table": "summary", "path": "mismatches", "bytes": len(bad)})
rows.append({"table": "summary", "path": "unmanifested", "bytes": len(unmanifested),
             "manifest_source": "derived interim artifacts that were never manifested"})
verdict = "PASS" if (not bad and n_ver >= 300) else "FAIL"
rows.append({"table": "verdict", "path": "frozen_inputs", "bytes": n_ver,
             "manifest_source": verdict + (" (vacuous, too few files checked)"
                                           if n_ver < 300 else "")})

with open(OUT / "input-verification.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "path", "bytes", "sha256",
                                       "manifest_sha256", "match", "manifest_source"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)

print(f"files under data/: {len(data_files)}")
print(f"carrying a manifest row and checked: {n_ver}")
print(f"mismatches: {len(bad)}")
for b in bad:
    print("  MISMATCH", b)
print(f"unmanifested: {len(unmanifested)}")
print(f"\nFROZEN INPUTS: {verdict}")
sys.exit(0 if verdict == "PASS" else 1)
