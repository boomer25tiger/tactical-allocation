"""Session 18 step 0: inventory, integrity, and the canonical positive control.

Reads the completed session 17 grid. Nothing is regenerated and nothing is
written into outputs/session-17/.
"""
from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S            # noqa: E402
import scripts.s17_grid_worker as W       # noqa: E402
from src import config                    # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
S17 = ROOT / "outputs" / "session-17"
G, P = S17 / "grid", S17 / "panel"
OUT = ROOT / "outputs" / "session-18"
OUT.mkdir(parents=True, exist_ok=True)

TARGET_ANN, TARGET_LO = 0.5218, 1.3817
NSHARD = 8
rows = []


def add(table, **kw):
    rows.append({"table": table, **kw})


# --- inventory --------------------------------------------------------------
print("== inventory ==")
for p in sorted(S17.rglob("*")):
    if p.is_file():
        rel = p.relative_to(ROOT)
        add("inventory", path=str(rel), bytes=p.stat().st_size,
            kind="file", note="")
dirs = sorted({p.parent for p in S17.rglob("*") if p.is_file()} | {S17})
for d in dirs:
    tot = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
    add("inventory_dir", path=str(d.relative_to(ROOT)), bytes=tot, kind="dir", note="")
    print(f"  {str(d.relative_to(ROOT)):48s} {tot/1e6:10.1f} MB")

# --- shard integrity --------------------------------------------------------
print("\n== shard integrity ==")
all_idx = []
per_shard = []
for k in range(NSHARD):
    idx = np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
    n = len(idx)
    met = os.path.getsize(G / f"metrics-{k:02d}.f64") // 8
    mom = os.path.getsize(G / f"moments-{k:02d}.f64") // 8
    pan = os.path.getsize(P / f"panel-{k:02d}.f32") // 4
    per_shard.append(n)
    all_idx.append(idx)
    ok = (met == n * W.N_MET and mom == n * 96 and pan == n * 2472)
    add("shard", shard=k, n_specs=n, first=int(idx[0]), last=int(idx[-1]),
        metrics_width=met // n, moments_width=mom // n, panel_width=pan // n,
        widths_consistent=ok)
    print(f"  shard {k}: {n:,} specs, ids {idx[0]:,}..{idx[-1]:,}, widths consistent {ok}")

cat = np.concatenate(all_idx)
total = len(cat)
uniq = len(np.unique(cat))
expected = np.arange(S.grid_size(), dtype=np.int64)
covers = np.array_equal(np.sort(cat), expected)
print(f"\n  total {total:,}  unique {uniq:,}  duplicates {total - uniq}")
print(f"  covers 0..{S.grid_size() - 1:,} with no gap: {covers}")
add("integrity", metric="total_specifications", value=total)
add("integrity", metric="unique_specifications", value=uniq)
add("integrity", metric="duplicates", value=total - uniq)
add("integrity", metric="gaps", value=int(S.grid_size() - uniq))
add("integrity", metric="covers_full_id_space", value=int(covers))

# --- moment shard layout ----------------------------------------------------
bs = np.load(G / "block-sizes.npy")
print(f"\n== moment shard layout ==")
print(f"  dtype float64, C order, per specification 96 values")
print(f"  = 48 blocks x 2 moments, ordered block 0 sum, block 0 sum of squares,")
print(f"    block 1 sum, block 1 sum of squares, and so on to block 47")
print(f"  block sizes from block-sizes.npy, {bs.min()} to {bs.max()}, summing {bs.sum()}")
print(f"  NOTE the session 18 prompt assumed 48 x 5 carrying cubes, fourth")
print(f"  powers, and a per-block count. The run stored 48 x 2 and the count")
print(f"  is the shared block-sizes vector, identical for every specification.")
add("layout", metric="dtype", value_text="float64")
add("layout", metric="per_spec_values", value=96)
add("layout", metric="shape_per_spec", value_text="48 blocks x 2 moments")
add("layout", metric="moment_order", value_text="sum of excess returns, then sum of squares, per block")
add("layout", metric="block_order", value_text="contiguous calendar order, numpy array_split of 2472 sessions into 48")
add("layout", metric="block_sizes", value_text=f"{bs.min()} to {bs.max()}, sum {bs.sum()}")
add("layout", metric="count_source", value_text="block-sizes.npy, shared across all specifications")
add("layout", metric="prompt_assumption_deviation",
    value_text="prompt assumed 48 x 5 with cubes, fourth powers and per-block count; "
               "stored is 48 x 2 with a shared count vector; naive Sharpe is still "
               "reconstructible, skewness and kurtosis are not and come from the metric set")

# --- artifact location ------------------------------------------------------
print("\n== required artifacts ==")
loc = [
    ("specification_index", "outputs/session-17/grid/index-*.i64 with axis values in "
     "metrics-*.f64 columns 1 to 9", "PRESENT",
     "no separate index CSV; the id-to-axis mapping is columns 0 to 9 of the metric shards"),
    ("per_specification_metric_set", "outputs/session-17/grid/metrics-*.f64", "PRESENT",
     f"{W.N_MET} columns per specification, being 1 id, 9 axis values, "
     f"{len(W.METRIC_ORDER)} standalone metrics, 22 per-calendar-year figures"),
    ("subsample_2000", "not written by session 17", "ABSENT",
     f"config carries GRID_SUBSAMPLE_SEED {config.GRID_SUBSAMPLE_SEED} and "
     f"GRID_SUBSAMPLE_SIZE {config.GRID_SUBSAMPLE_SIZE}; the worker never drew it. "
     "Constructible from the still-present panel at the config-fixed seed, which is "
     "what the subsample is for, and must be built before the step 8 deletion"),
]
for name, path, status, note in loc:
    print(f"  {name:32s} {status:8s} {path}")
    add("artifact", metric=name, value_text=path, status=status, note=note)

# --- engine changes during the run ------------------------------------------
print("\n== engine changes during the run ==")
src = (ROOT / "scripts" / "s17_grid_worker.py").read_text()
rf_on = "S.install_rf_cache()" in src and "rf_factors=rfa" in src
cache_on = "bt.s17_enable_engine_cache(True)" in src
print(f"  precomputed risk-free factor array ENABLED during the run: {rf_on}")
print(f"  panel array and rate-series cache ENABLED during the run:  {cache_on}")
print(f"  both default to off in scripts/s13_backtest.py and were switched on by the worker")
add("engine_change", metric="rf_factor_array", enabled_during_run=int(rf_on),
    note="run_account received rf_factors; default is None which restores the label slice")
add("engine_change", metric="panel_array_and_rate_cache", enabled_during_run=int(cache_on),
    note="s17_enable_engine_cache(True) called in the worker; module default is off")

# --- canonical positive control ---------------------------------------------
print("\n== canonical positive control against the completed grid ==")
cv = S.canonical_values()
ci = S.index_of(cv)
shard = None
for k in range(NSHARD):
    idx = all_idx[k]
    if idx[0] <= ci <= idx[-1]:
        shard = k
        pos = int(np.searchsorted(idx, ci))
        break
met = np.fromfile(G / f"metrics-{shard:02d}.f64", dtype=np.float64).reshape(-1, W.N_MET)
rec = met[pos]
assert int(rec[0]) == ci, f"metric row id {int(rec[0])} does not match {ci}"
axes_on_disk = tuple(rec[1:1 + len(S.AXES)].tolist())
col_ann = 1 + len(S.AXES) + W.METRIC_ORDER.index("ann_return")
col_lo = 1 + len(S.AXES) + W.METRIC_ORDER.index("sharpe_lo")
ann, lo = float(rec[col_ann]), float(rec[col_lo])
ga, gl = abs(ann - TARGET_ANN), abs(lo - TARGET_LO)
axes_match = all(abs(a - float(b)) < 1e-12 for a, b in zip(cv, axes_on_disk))
print(f"  canonical values {cv}")
print(f"  canonical id {ci:,} found in shard {shard} at row {pos:,}")
print(f"  axis values on disk match config canonical: {axes_match}")
print(f"  ann_return {ann:.6f} target {TARGET_ANN} gap {ga:.2e} match4dp {ga < 5e-5}")
print(f"  sharpe_lo  {lo:.6f} target {TARGET_LO} gap {gl:.2e} match4dp {gl < 5e-5}")
add("positive_control", metric="canonical_spec_id", value=ci)
add("positive_control", metric="canonical_shard", value=shard)
add("positive_control", metric="canonical_row", value=pos)
add("positive_control", metric="axis_values_match_config", value=int(axes_match))
add("positive_control", metric="ann_return", value=ann, target=TARGET_ANN,
    abs_gap=ga, match_4dp=int(ga < 5e-5))
add("positive_control", metric="sharpe_lo", value=lo, target=TARGET_LO,
    abs_gap=gl, match_4dp=int(gl < 5e-5))

ok = ga < 5e-5 and gl < 5e-5 and axes_match and covers and (total == uniq == S.grid_size())
print(f"\nSTEP 0 CONTROL: {'PASS' if ok else 'FAIL'}")
add("verdict", metric="step0", value_text="PASS" if ok else "FAIL")

cols = ["table", "path", "bytes", "kind", "shard", "n_specs", "first", "last",
        "metrics_width", "moments_width", "panel_width", "widths_consistent",
        "metric", "value", "value_text", "target", "abs_gap", "match_4dp",
        "status", "enabled_during_run", "note"]
with open(OUT / "inventory.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"wrote {OUT / 'inventory.csv'} with {len(rows)} rows")
sys.exit(0 if ok else 1)
