"""Session 18: draw the pre-registered subsample session 17 did not write.

The seed and the size were fixed in src/config.py before the grid ran, so
drawing at that seed now yields the set that was pre-registered. Only the
execution of the draw was missing. The subsample must exist before the
step 8 panel deletion, since it is the retained daily-return evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S      # noqa: E402
from src import config              # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "outputs" / "session-17" / "panel"
OUT = ROOT / "outputs" / "session-18"
NSESS, NSHARD = 2472, 8

total = S.grid_size()
rng = np.random.default_rng(config.GRID_SUBSAMPLE_SEED)
draw = np.sort(rng.choice(total, size=config.GRID_SUBSAMPLE_SIZE, replace=False))
canon = S.index_of(S.canonical_values())
in_draw = bool(np.isin(canon, draw))
print(f"seed {config.GRID_SUBSAMPLE_SEED}, size {config.GRID_SUBSAMPLE_SIZE}, "
      f"drawn without replacement from 0..{total-1}")
print(f"canonical spec_id {canon:,} present in the draw: {in_draw}")
ids = draw if in_draw else np.sort(np.append(draw, canon))
if not in_draw:
    print(f"  canonical appended as an additional row rather than displacing a drawn "
          f"member; subsample size {len(ids):,}")

bounds = [(k * total // NSHARD, (k + 1) * total // NSHARD) for k in range(NSHARD)]
out = np.empty((len(ids), NSESS), dtype=np.float32)
for k, (lo, hi) in enumerate(bounds):
    sel = np.flatnonzero((ids >= lo) & (ids < hi))
    if not len(sel):
        continue
    mm = np.memmap(P / f"panel-{k:02d}.f32", dtype=np.float32, mode="r").reshape(-1, NSESS)
    out[sel] = mm[ids[sel] - lo]
    del mm
    print(f"  shard {k}: pulled {len(sel):,} series")

np.save(OUT / "subsample-ids.npy", ids.astype(np.int64))
np.save(OUT / "subsample-returns.npy", out)
print(f"wrote subsample-ids.npy {len(ids):,} ids and subsample-returns.npy "
      f"{out.shape} float32, {out.nbytes/1e6:.1f} MB")
print(f"NOTE the panel is float32, so the retained series carry the panel's own "
      f"quantisation and are not the float64 series the moments were computed from")
