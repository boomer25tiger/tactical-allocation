"""Session 19 step 2: inventory and integrity after relocation.

Read-only. Confirms the completed grid is intact and that the canonical
specification still reproduces the designated cell, before any figure in
this session rests on it. A mismatch halts the session.
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S           # noqa: E402
import scripts.s17_grid_worker as W      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
G = ROOT / "outputs" / "session-17" / "grid"
S18 = ROOT / "outputs" / "session-18"
OUT = ROOT / "outputs" / "session-19"
OUT.mkdir(parents=True, exist_ok=True)

NSESS, NSHARD, NBLK = 2472, 8, 48
TOTAL = S.grid_size()
SF_DATALESS = 0x40000000
rows = []
fail = []


def add(table, item, value="", note=""):
    rows.append({"table": table, "item": item, "value": value, "note": note})


# --- volume ----------------------------------------------------------------
st = os.statvfs(ROOT)
free = st.f_bavail * st.f_frsize
total = st.f_blocks * st.f_frsize
used_pct = 100.0 * (1.0 - st.f_bavail / st.f_blocks)
add("volume", "free_bytes", free)
add("volume", "free_gb", f"{free/1e9:.1f}")
add("volume", "total_gb", f"{total/1e9:.1f}")
add("volume", "percent_used", f"{used_pct:.1f}")
print(f"volume {free/1e9:.1f} GB free of {total/1e9:.1f} GB, {used_pct:.1f} percent used")

# --- dataless --------------------------------------------------------------
n_files = 0
dataless = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".venv" in dirnames:
        dirnames.remove(".venv")
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        try:
            stt = os.lstat(p)
        except OSError:
            continue
        n_files += 1
        if getattr(stt, "st_flags", 0) & SF_DATALESS:
            dataless.append(p)
add("dataless", "files_scanned_excluding_venv", n_files)
add("dataless", "dataless_count", len(dataless))
print(f"dataless outside .venv: {len(dataless)} of {n_files} files")
if dataless:
    fail.append(f"{len(dataless)} dataless files outside .venv")

# --- fsck ------------------------------------------------------------------
r = subprocess.run(["git", "fsck", "--no-dangling"], cwd=ROOT,
                   capture_output=True, text=True)
add("git", "fsck_exit", r.returncode, (r.stdout + r.stderr).strip()[:200])
print(f"git fsck --no-dangling exit {r.returncode}")
if r.returncode != 0:
    fail.append("git fsck non-zero")

# --- shards ----------------------------------------------------------------
ids_all = []
for k in range(NSHARD):
    mo = np.fromfile(G / f"moments-{k:02d}.f64", dtype=np.float64)
    me = np.fromfile(G / f"metrics-{k:02d}.f64", dtype=np.float64)
    ix = np.fromfile(G / f"index-{k:02d}.i64", dtype=np.int64)
    assert mo.size % (2 * NBLK) == 0 and me.size % W.N_MET == 0
    mo = mo.reshape(-1, 2 * NBLK)
    me = me.reshape(-1, W.N_MET)
    # Session 20 B2 repair. An empty shard gave 0 == 0 == 0 and reported
    # consistent. A positive row count is required before consistency counts.
    SHARD_ROW_FLOOR = 1
    ok = (ix.size >= SHARD_ROW_FLOOR and mo.shape[0] == me.shape[0] == ix.size)
    add("shard", f"shard_{k}", ix.size,
        f"moments {mo.shape} metrics {me.shape} index {ix.size} consistent={ok}")
    if not ok:
        fail.append(f"shard {k} width mismatch")
    ids_all.append(ix)
ids = np.sort(np.concatenate(ids_all))
uniq = np.unique(ids)
contiguous = bool(ids.size == TOTAL and uniq.size == TOTAL
                  and ids[0] == 0 and ids[-1] == TOTAL - 1)
add("integrity", "total_specifications", int(ids.size))
add("integrity", "unique_specifications", int(uniq.size))
add("integrity", "duplicates", int(ids.size - uniq.size))
add("integrity", "gaps", int(TOTAL - uniq.size))
add("integrity", "covers_0_to_121499", int(contiguous))
print(f"identifier space {ids[0]} to {ids[-1]}, {uniq.size:,} unique, "
      f"{ids.size - uniq.size} duplicates, {TOTAL - uniq.size} gaps")
if not contiguous:
    fail.append("identifier space not contiguous")

blk = np.load(G / "block-sizes.npy")
add("layout", "n_base_blocks", int(blk.size))
add("layout", "block_size_min_max", f"{int(blk.min())} to {int(blk.max())}")
add("layout", "block_size_sum", int(blk.sum()))
add("layout", "moments_per_spec", 2 * NBLK,
    "48 blocks x 2 moments, being sum of excess returns and sum of squares")
add("layout", "metrics_per_spec", W.N_MET,
    "1 identifier, 9 axis values, 40 standalone metrics, 22 per-calendar-year figures")
add("layout", "prompt_assumption_deviation", "48x2 stored, not 48x5",
    "the session 19 scaffold repeats the session 18 assumption of 48 x 5 with cubes, "
    "fourth powers and a per-block count; the stored layout is 48 x 2 with the count "
    "held once in block-sizes.npy. Naive Sharpe is reconstructible, skewness and "
    "excess kurtosis are not and come from the metric set")
if int(blk.sum()) != NSESS:
    fail.append("block sizes do not sum to 2472")

# --- positive control ------------------------------------------------------
BOUNDS = [(k * TOTAL // NSHARD, (k + 1) * TOTAL // NSHARD) for k in range(NSHARD)]
cv = S.canonical_values()
canon = S.index_of(cv)
add("positive_control", "canonical_spec_id", canon)
shard = next(k for k, (lo, hi) in enumerate(BOUNDS) if lo <= canon < hi)
lo, _ = BOUNDS[shard]
mm = np.memmap(G / f"metrics-{shard:02d}.f64", dtype=np.float64,
               mode="r").reshape(-1, W.N_MET)
rec = np.array(mm[canon - lo])
assert int(rec[0]) == canon, "metric row identifier does not match"
axis_vals = tuple(rec[1:1 + len(S.AXES)])
axis_ok = all(float(a) == float(b) for a, b in zip(axis_vals, cv))
add("positive_control", "canonical_shard", shard)
add("positive_control", "canonical_row", canon - lo)
add("positive_control", "axis_values_match_config", int(axis_ok),
    "axis values read from the metric row against config, no literal")
if not axis_ok:
    fail.append("canonical axis values do not match config")

base = 1 + len(S.AXES)
ann = float(rec[base + W.METRIC_ORDER.index("ann_return")])
slo = float(rec[base + W.METRIC_ORDER.index("sharpe_lo")])
TARGET_ANN, TARGET_SLO = 0.521845, 1.381701
d_ann, d_slo = abs(ann - TARGET_ANN), abs(slo - TARGET_SLO)
m_ann, m_slo = d_ann < 5e-7, d_slo < 5e-7
add("positive_control", "ann_return", repr(ann), f"target {TARGET_ANN}, gap {d_ann:.3e}")
add("positive_control", "sharpe_lo", repr(slo), f"target {TARGET_SLO}, gap {d_slo:.3e}")
add("positive_control", "matches_to_6dp", int(m_ann and m_slo))
print(f"canonical spec {canon:,} shard {shard} row {canon-lo}")
print(f"  ann_return {ann:.12f} against {TARGET_ANN}  gap {d_ann:.3e}")
print(f"  sharpe_lo  {slo:.12f} against {TARGET_SLO}  gap {d_slo:.3e}")
if not (m_ann and m_slo):
    fail.append("canonical positive control mismatch")

# --- engine changes --------------------------------------------------------
import scripts.s13_backtest as bt  # noqa: E402
import inspect  # noqa: E402
sig = inspect.signature(bt.run_account)
has_rf = "rf_factors" in sig.parameters
rf_default_none = has_rf and sig.parameters["rf_factors"].default is None
src = (ROOT / "scripts" / "s17_grid_worker.py").read_text()
cache_called = "s17_enable_engine_cache(True)" in src
bt_src = (ROOT / "scripts" / "s13_backtest.py").read_text()
# runtime state on a fresh import, stronger than a string match: the worker
# turns the cache on explicitly, so a module whose default is on would show
# True here before any enable call is made in this process
cache_default_off = (bt._S17_CACHE["on"] is False)
add("engine_change", "rf_factor_array_parameter_present", int(has_rf))
add("engine_change", "rf_factor_array_default_none", int(rf_default_none),
    "default None restores the label slice, so prior behaviour is the default")
add("engine_change", "panel_cache_enabled_in_worker", int(cache_called),
    "s17_enable_engine_cache(True) called by the grid worker")
add("engine_change", "panel_cache_module_default_off", int(cache_default_off))
print(f"engine changes: rf_factors param {has_rf}, default None {rf_default_none}, "
      f"cache enabled in worker {cache_called}, module default off {cache_default_off}")
if not (has_rf and rf_default_none and cache_called):
    fail.append("engine change verification incomplete")

# --- session 18 artifacts --------------------------------------------------
for name in ("reachability.csv", "additivity-check.csv", "spec-index-augmented.csv",
             "subsample-ids.npy", "subsample-returns.npy", "axis-classification.json"):
    p = S18 / name
    present = p.exists()
    sz = p.stat().st_size if present else 0
    readable = False
    if present:
        with open(p, "rb") as fh:
            readable = len(fh.read()) == sz
    add("session18_artifact", name, sz, f"present={present} fully_readable={readable}")
    if not (present and readable):
        fail.append(f"session 18 artifact {name} missing or short")

cls = json.load(open(S18 / "axis-classification.json"))
n_struct = sum(1 for v in cls.values() if v == "structural")
n_smooth = sum(1 for v in cls.values() if v == "smooth")
add("axis_classification", "n_axes", len(cls))
add("axis_classification", "n_structural", n_struct)
add("axis_classification", "n_smooth", n_smooth)
add("axis_classification", "structural",
    " ".join(sorted(a for a, c in cls.items() if c == "structural")))
add("axis_classification", "smooth",
    " ".join(sorted(a for a, c in cls.items() if c == "smooth")))
print(f"axis classification {n_struct} structural, {n_smooth} smooth of {len(cls)}")
if not (n_struct == 6 and n_smooth == 3):
    fail.append(f"axis classification is {n_struct}/{n_smooth}, expected 6/3")

verdict = "PASS" if not fail else "FAIL"
add("verdict", "step2", verdict, "; ".join(fail))
with open(OUT / "inventory.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "item", "value", "note"])
    w.writeheader()
    w.writerows(rows)
print(f"\nSTEP 2: {verdict}")
if fail:
    for f in fail:
        print("  FAIL", f)
print(f"wrote {OUT/'inventory.csv'} with {len(rows)} rows")
sys.exit(0 if verdict == "PASS" else 1)
