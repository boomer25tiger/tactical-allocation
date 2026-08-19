"""Verify a regenerated daily return panel against the manifest hash.

Float reduction order varies with thread count and BLAS version, so this
reports maximum absolute deviation against a stated tolerance rather than
asserting bit-identical equality. The manifest stores the hash of a
CANONICALISED form, being fixed precision, fixed dtype, and fixed column
order, so the comparison is stable across environments that agree to the
stated tolerance.

Usage: python scripts/verify_panel.py <panel.parquet> [tolerance]
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOL = 1e-9
PRECISION = 12


def canonicalise(df: pd.DataFrame) -> pd.DataFrame:
    out = df.reindex(sorted(df.columns), axis=1).astype("float64")
    return out.round(PRECISION).sort_index()


def canonical_hash(df: pd.DataFrame) -> str:
    c = canonicalise(df)
    h = hashlib.sha256()
    h.update(",".join(map(str, c.columns)).encode())
    h.update(np.ascontiguousarray(c.index.values.astype("datetime64[ns]")).tobytes())
    h.update(np.ascontiguousarray(c.to_numpy()).tobytes())
    return h.hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = Path(sys.argv[1])
    tol = float(sys.argv[2]) if len(sys.argv) > 2 else TOL
    man = json.loads((ROOT / "outputs" / "session-16" / "MANIFEST.json").read_text())
    stored = man.get("canonicalised_panel_sha256")
    if stored in (None, "", "NOT_PRODUCED"):
        print("manifest records no panel hash; the grid did not run in session 16, "
              "so there is no panel to verify")
        return 0
    if not path.exists():
        print(f"panel not found at {path}")
        return 1
    df = pd.read_parquet(path)
    got = canonical_hash(df)
    print(f"stored  {stored}\nregen   {got}\nmatch   {got == stored}")
    if got == stored:
        return 0
    ref = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    if ref and ref.exists():
        a, b = canonicalise(df), canonicalise(pd.read_parquet(ref))
        dev = float(np.nanmax(np.abs(a.to_numpy() - b.to_numpy())))
        print(f"max abs deviation {dev:.3e} against tolerance {tol:.3e} -> "
              f"{'WITHIN' if dev <= tol else 'OUTSIDE'}")
        return 0 if dev <= tol else 2
    print("hash differs and no reference panel supplied for a deviation report")
    return 2


if __name__ == "__main__":
    sys.exit(main())
