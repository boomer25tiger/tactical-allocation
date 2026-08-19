"""Session 19 step 9: the manifest.

Written BEFORE the step 10 panel deletion, since the canonicalised panel
hash can only be taken while the panel exists. Everything the manifest
records is either a hash of a committed artifact or a fact about how the
grid was produced.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S           # noqa: E402
import scripts.s17_grid_worker as W      # noqa: E402
import scripts.verify_panel as VP        # noqa: E402
from src import config                   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
P = ROOT / "outputs" / "session-17" / "panel"
S18 = ROOT / "outputs" / "session-18"
OUT = ROOT / "outputs" / "session-19"
NSESS, NSHARD, NBLK = 2472, 8, 48
TOTAL = S.grid_size()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


print("hashing committed inputs")
inputs = {}
for rel in sorted([p.relative_to(ROOT) for p in G.iterdir() if p.is_file()]):
    inputs[str(rel)] = sha(ROOT / rel)
for name in ("spec-index-augmented.csv", "subsample-ids.npy", "subsample-returns.npy",
             "reachability.csv", "additivity-check.csv", "axis-classification.json"):
    inputs[f"outputs/session-18/{name}"] = sha(S18 / name)
for name in ("pbo.csv", "pbo-strata.csv", "deflated-sharpe.csv",
             "specification-curve.csv", "inventory.csv", "additivity-check.csv",
             "remote-status.csv", "cscv-draws-s16.npz"):
    p = OUT / name
    if p.exists():
        inputs[f"outputs/session-19/{name}"] = sha(p)
print(f"  {len(inputs)} files hashed")

print("hashing the canonicalised panel, streamed shard by shard")
panel_hash, panel_n = VP.canonical_hash(P)
print(f"  {panel_hash}  over {panel_n:,} specifications")

# block boundary dates, from the calendar the grid used
import scripts.s14_common as C           # noqa: E402
C.PRIMARY_START = pd.Timestamp("2011-10-04")
env = C.build_env(verbose=False)
cal = env["cal"]
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))
pidx = cal[i0:]
assert len(pidx) == NSESS
blk = np.load(G / "block-sizes.npy")
bounds, off = [], 0
for n in blk:
    bounds.append({"block": len(bounds), "n_sessions": int(n),
                   "first": str(pidx[off].date()),
                   "last": str(pidx[off + int(n) - 1].date())})
    off += int(n)
assert off == NSESS

per_shard = {}
for k in range(NSHARD):
    ix = np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
    per_shard[str(k)] = {"n_specifications": int(ix.size),
                         "first_id": int(ix.min()), "last_id": int(ix.max())}

cfg_src = (ROOT / "src" / "config.py").read_bytes()
manifest = {
    "session": "19",
    "written": "2026-08-19",
    "purpose": "identifies every committed artifact the PBO report rests on and "
               "records how the deleted panel is regenerated",
    "commit_parent": git("rev-parse", "HEAD"),
    "commit_note": "the session 19 commit is the immediate child of commit_parent on "
                   "main. A manifest cannot carry the hash of the commit that contains "
                   "it, so the parent is recorded and the session commit is identified "
                   "by the branch head after this session",
    "remote": git("remote", "get-url", "origin"),
    "config_sha256": hashlib.sha256(cfg_src).hexdigest(),
    "config_bytes": len(cfg_src),
    "canonicalised_panel_sha256": panel_hash,
    "canonicalised_panel_form": {
        "specification_order": "ascending identifier 0..121499",
        "session_order": "calendar order over the primary window",
        "dtype": "float64 cast from the stored float32",
        "precision_decimals": VP.PRECISION,
        "streamed": "hashed shard by shard so the whole panel is never resident",
        "tolerance_for_regeneration": VP.TOL,
        "tolerance_reason": "float reduction order varies with thread count and BLAS "
                            "version and the run was sharded across eight processes, so "
                            "verify_panel.py reports maximum absolute deviation against "
                            "this tolerance rather than asserting bit-identical equality",
    },
    "grid": {
        "n_evaluated": TOTAL,
        "n_enumerated": S.enumerated_size(),
        "searched_axes": list(S.AXIS_NAMES),
        "axis_values": {a: list(map(float, S.AXIS_VALUES[i]))
                        for i, a in enumerate(S.AXIS_NAMES)},
        "unsearched_axis": {"name": "tier_two_offset", "register": "7.4",
                            "status": "informed",
                            "held_at_canonical": S.CANONICAL_TIER_TWO_OFFSET},
        "canonical_spec_id": S.index_of(S.canonical_values()),
        "shard_count": NSHARD,
        "per_shard": per_shard,
        "sharded_across_processes": NSHARD,
        "sharding_note": "the run was sharded across eight processes and reduction order "
                         "under sharding is part of what the panel tolerance accommodates",
        "n_base_blocks": NBLK,
        "moments_per_spec": 2 * NBLK,
        "moment_layout": "48 blocks x 2 moments, being the sum of excess returns and the "
                         "sum of squares per block; the per-block count is held once in "
                         "block-sizes.npy",
        "metrics_per_spec": W.N_MET,
        "block_boundaries": bounds,
    },
    "cscv": {
        "S_primary": 16,
        "S_sensitivity": [8, 12, 24, 48],
        "combination_seed": 20260821,
        "combination_cap": 20000,
        "memory_ceiling_gb": 2.0,
        "performance_metric": "naive Sharpe",
        "performance_metric_reason": "autocovariance is not additive across disjoint "
                                     "blocks and the cross-boundary terms are missing "
                                     "from a union, so a Lo correction on a union would "
                                     "be wrong rather than approximate",
    },
    "seeds": {
        "grid_subsample_seed": int(config.GRID_SUBSAMPLE_SEED),
        "grid_subsample_size": int(config.GRID_SUBSAMPLE_SIZE),
        "combination_seed": 20260821,
        "additivity_draw_seed": 20260820,
    },
    "environment": {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "thread_count_note": "the grid ran as eight independent single-process shards "
                             "rather than a threaded run; BLAS thread count was left at "
                             "the library default and is not pinned",
        "rebuild_note": "the environment was rebuilt in session 18s from a freeze "
                        "captured before removal rather than from an authoritative "
                        "requirements.txt, which does not exist in this repository. The "
                        "zero version divergence that rebuild reported is therefore "
                        "partly a construction of that method rather than independent "
                        "confirmation, since installing from a freeze reproduces the "
                        "recorded versions by definition",
        "declared_requirements_file": "requirements-session-00a.txt",
        "declared_pins": 24,
        "installed_packages": 30,
        "packages_beyond_declared": ["pytest", "iniconfig", "packaging", "pluggy",
                                     "Pygments", "pypdf"],
    },
    "regenerate_panel_command":
        "for k in 0 1 2 3 4 5 6 7; do .venv/bin/python scripts/s17_grid_worker.py "
        "$k 8 & done; wait   # writes outputs/session-17/panel/panel-0{k}.f32 and the "
        "grid shards; verify with .venv/bin/python scripts/verify_panel.py "
        "outputs/session-17/panel outputs/session-19/MANIFEST.json",
    "verify_panel_script": "scripts/verify_panel.py",
    "input_sha256": inputs,
}

(OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=False) + "\n")
sz = (OUT / "MANIFEST.json").stat().st_size
print(f"wrote {OUT/'MANIFEST.json'} {sz/1024:.1f} KB with {len(inputs)} input hashes")
