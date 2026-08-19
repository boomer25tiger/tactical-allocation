"""Session 18 step 1: the augmented specification index.

Joins the step 1 classification onto the grid's specification index by
specification identifier and carries the metrics steps 4 and 5 need, so
both remain computable after the step 8 panel deletion.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S           # noqa: E402
import scripts.s17_grid_worker as W      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
OUT = ROOT / "outputs" / "session-18"

CARRY = ["n_sessions", "ann_return", "ann_vol", "sharpe_naive", "sharpe_lo",
         "max_drawdown", "calmar", "skewness", "excess_kurtosis", "ann_turnover"]

met = np.concatenate([
    np.fromfile(G / f"metrics-{k:02d}.f64", dtype=np.float64).reshape(-1, W.N_MET)
    for k in range(8)])
order = np.argsort(met[:, 0].astype(np.int64))
met = met[order]
ids = met[:, 0].astype(np.int64)
assert np.array_equal(ids, np.arange(S.grid_size())), "index is not 0..N-1 after sort"

df = pd.DataFrame({"spec_id": ids})
for k, axis in enumerate(S.AXIS_NAMES):
    df[axis] = met[:, 1 + k]
base = 1 + len(S.AXES)
for name in CARRY:
    df[name] = met[:, base + W.METRIC_ORDER.index(name)]

cls = json.load(open(OUT / "axis-classification.json"))
cv = S.canonical_values()
structural = [a for a, c in cls.items() if c == "structural"]
smooth = [a for a, c in cls.items() if c == "smooth"]
for axis in S.AXIS_NAMES:
    df[f"class_{axis}"] = cls[axis]

at_canon_struct = np.ones(len(df), dtype=bool)
for a in structural:
    at_canon_struct &= (df[a].to_numpy() == cv[S.AXIS_NAMES.index(a)])
df["on_structural_axis_away_from_canonical"] = ~at_canon_struct
df["all_structural_axes_at_canonical"] = at_canon_struct

n_away = int(df["on_structural_axis_away_from_canonical"].sum())
n_smooth_only = int(at_canon_struct.sum())
canon_id = S.index_of(cv)
print(f"augmented index rows {len(df):,}")
print(f"  structural axes {structural}")
print(f"  smooth axes     {smooth}")
print(f"  specifications on a structural axis value away from canonical: {n_away:,} "
      f"({n_away/len(df)*100:.2f}%)")
print(f"  specifications with every structural axis at canonical:        {n_smooth_only:,}")
print(f"    that is the smooth-axis restricted subset for step 3, being "
      f"{' x '.join(str(len(S.AXIS_VALUES[S.AXIS_NAMES.index(a)])) for a in smooth)} = {n_smooth_only}")
print(f"  canonical spec_id {canon_id:,} in the restricted subset: "
      f"{bool(at_canon_struct[canon_id])}")
df.to_csv(OUT / "spec-index-augmented.csv", index=False, float_format="%.10g")
sz = (OUT / "spec-index-augmented.csv").stat().st_size
print(f"wrote {OUT/'spec-index-augmented.csv'} {sz/1e6:.1f} MB")
