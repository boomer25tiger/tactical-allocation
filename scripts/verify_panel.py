"""Verify a regenerated daily return panel against the manifest hash.

Float reduction order varies with thread count and BLAS version, and the
session 17 grid ran sharded across eight processes, so this reports MAXIMUM
ABSOLUTE DEVIATION against a stated tolerance rather than asserting
bit-identical equality. The manifest stores the hash of a CANONICALISED
form, being fixed precision, fixed dtype and fixed ordering, so the hash is
the identity check and the deviation report is what a legitimate
environment difference is judged by.

CANONICAL FORM. Specifications in ascending identifier order 0..N-1,
sessions in calendar order, values cast to float64 and rounded to
PRECISION decimal places, hashed shard by shard so the whole panel is never
resident.

TOLERANCE. TOL is 1e-6 absolute on a daily return. The stored panel is
float32, which carries roughly 1e-9 absolute on a return of order 1e-2, and
reduction-order differences across a different shard count or BLAS build
move individual values by more than the float32 floor but far less than
1e-6.

Usage
  python scripts/verify_panel.py <panel-dir> [manifest.json] [tolerance]
  python scripts/verify_panel.py <panel-dir> --against <other-panel-dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-6
PRECISION = 10
NSESS, NSHARD = 2472, 8
DEFAULT_MANIFEST = ROOT / "outputs" / "session-19" / "MANIFEST.json"


def shard_paths(d: Path):
    return [d / f"panel-{k:02d}.f32" for k in range(NSHARD)]


def canonical_hash(panel_dir: Path):
    """SHA-256 of the canonicalised panel, streamed shard by shard."""
    h = hashlib.sha256()
    h.update(f"canonical-v1 precision={PRECISION} sessions={NSESS}".encode())
    total = 0
    for p in shard_paths(panel_dir):
        a = np.fromfile(p, dtype=np.float32).reshape(-1, NSESS)
        total += a.shape[0]
        c = np.ascontiguousarray(np.round(a.astype(np.float64), PRECISION))
        h.update(c.tobytes())
        del a, c
    h.update(str(total).encode())
    return h.hexdigest(), total


def max_deviation(a_dir: Path, b_dir: Path) -> float:
    worst = 0.0
    for pa, pb in zip(shard_paths(a_dir), shard_paths(b_dir)):
        a = np.fromfile(pa, dtype=np.float32).reshape(-1, NSESS).astype(np.float64)
        b = np.fromfile(pb, dtype=np.float32).reshape(-1, NSESS).astype(np.float64)
        if a.shape != b.shape:
            raise SystemExit(f"shape mismatch {pa.name} {a.shape} against {b.shape}")
        worst = max(worst, float(np.nanmax(np.abs(a - b))))
        del a, b
    return worst


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    panel = Path(sys.argv[1])
    if len(sys.argv) > 3 and sys.argv[2] == "--against":
        dev = max_deviation(panel, Path(sys.argv[3]))
        print(f"max abs deviation {dev:.3e} against tolerance {TOL:.3e} -> "
              f"{'WITHIN' if dev <= TOL else 'OUTSIDE'}")
        return 0 if dev <= TOL else 2

    man_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MANIFEST
    tol = float(sys.argv[3]) if len(sys.argv) > 3 else TOL
    man = json.loads(man_path.read_text())
    stored = man.get("canonicalised_panel_sha256")
    if stored in (None, "", "NOT_PRODUCED"):
        print(f"{man_path} records no panel hash")
        return 1
    missing = [p.name for p in shard_paths(panel) if not p.exists()]
    if missing:
        print(f"panel shards absent from {panel}: {', '.join(missing)}")
        print("regenerate with the command the manifest records under "
              "regenerate_panel_command, then re-run this check")
        return 1
    got, n = canonical_hash(panel)
    print(f"stored  {stored}")
    print(f"regen   {got}")
    print(f"specifications hashed {n:,}")
    print(f"match   {got == stored}")
    if got == stored:
        return 0
    print(f"hash differs; supply a reference panel with --against to get a maximum "
          f"absolute deviation against the {tol:.3e} tolerance")
    return 2


if __name__ == "__main__":
    sys.exit(main())
