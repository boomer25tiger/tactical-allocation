"""M2, composition on held tickers only.

The 19.5 step 5 date of 2013-01-23 was bound by QQQE, which src/sleeves.py
consumes only as an RSI-exhaustion signal input inside T10_CASCADE and never
holds. That date therefore measures signal coverage rather than what the
strategy can hold. The classification in coverage-early.csv came from a
hardcoded list inside scripts/s195_strip.py, which is the convention breach
this measurement removes.

DERIVATION, stated before running. The held universe is read from the
abstract syntax tree of src/sleeves.py. A ticker is HELD if it appears as a
key carrying a non-zero weight in any dictionary returned by any function, or
as a bare string returned by a terminal helper. A ticker is a SIGNAL INPUT if
it is passed to one of the IndicatorState accessors or appears in a named
panel tuple, and is not held. No ticker list is written by hand.

The warmup requirement is derived from the lookbacks in src/config.py rather
than assumed.
"""
from __future__ import annotations

import ast
import csv
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s14_common as C          # noqa: E402
from src import config                  # noqa: E402

OUT = ROOT / "outputs" / "session-19_6"
SLEEVES = ROOT / "src" / "sleeves.py"
rows = []


def add(table, **kw):
    rows.append({"table": table, **kw})


tree = ast.parse(SLEEVES.read_text())
ACCESSORS = {"rsi_exhaustion", "rsi_dip", "rsi_rs", "price", "sma",
             "trailing_return_pct", "available"}
held, signal, name_keys = {}, {}, {}

# resolve Name keys such as vol_short to the string constants they can take
assign_strings = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and len(node.targets) == 1 \
            and isinstance(node.targets[0], ast.Name):
        vals = [n.value for n in ast.walk(node.value)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        vals = [v for v in vals if re.fullmatch(r"[A-Z]{2,5}", v)]
        if vals:
            assign_strings.setdefault(node.targets[0].id, set()).update(vals)

for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
    for node in ast.walk(fn):
        # held, dictionary returns
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                nonzero = True
                if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)):
                    nonzero = v.value != 0
                if not nonzero:
                    continue
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    held.setdefault(k.value, set()).add(fn.name)
                elif isinstance(k, ast.Name):
                    name_keys.setdefault(k.id, set()).add(fn.name)
                    for t in assign_strings.get(k.id, set()):
                        held.setdefault(t, set()).add(f"{fn.name} via {k.id}")
        # held, bare string returns from terminal helpers
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str) \
                and re.fullmatch(r"[A-Z]{2,5}", node.value.value):
            held.setdefault(node.value.value, set()).add(fn.name)
        # signal inputs, accessor arguments
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ACCESSORS:
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    signal.setdefault(a.value, set()).add(f"{fn.name}.{node.func.attr}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in ACCESSORS:
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    signal.setdefault(a.value, set()).add(f"{fn.name}.{node.func.id}")

# named panel tuples are signal inputs by construction
import src.sleeves as SL                # noqa: E402
for nm, tup in (("T10_CASCADE", SL.T10_CASCADE), ("T11_PANEL", SL.T11_PANEL),
                ("S3_VOTES", tuple(SL.S3_VOTES))):
    for t in tup:
        signal.setdefault(t, set()).add(nm)
signal.setdefault(config.TREND_SIGNAL_SERIES, set()).add("config.TREND_SIGNAL_SERIES")

HELD = sorted(held)
SIGNAL_ONLY = sorted(t for t in signal if t not in held)
print(f"HELD tickers, {len(HELD)}: {HELD}")
print(f"SIGNAL-ONLY tickers, {len(SIGNAL_ONLY)}: {SIGNAL_ONLY}")
print(f"unresolved Name keys: {sorted(name_keys)}")
add("derivation", item="method",
    note="abstract syntax tree of src/sleeves.py; held is a non-zero weight key in a "
         "returned dict or a bare ticker string returned by a terminal helper; "
         "signal-only is an IndicatorState accessor argument or a named panel member "
         "that is never held")
add("counts", item="n_held", value=len(HELD))
add("counts", item="n_signal_only", value=len(SIGNAL_ONLY))
for t in HELD:
    add("held", item=t, note=" ; ".join(sorted(held[t])))
for t in SIGNAL_ONLY:
    add("signal_only", item=t, note=" ; ".join(sorted(signal[t])))

# --- disagreement with the hardcoded list in s195_strip.py -----------------
strip_src = (ROOT / "scripts" / "s195_strip.py").read_text()
m = re.search(r'held = \[t for t in tokens if t in real\.frames and t not in\s*\((.*?)\)\]',
              strip_src, re.S)
hard_excluded = set(re.findall(r'"([A-Z]{2,5})"', m.group(1))) if m else set()
tokens = sorted(set(re.findall(r'"([A-Z]{2,5})"', SLEEVES.read_text())))
hard_held = [t for t in tokens if t not in hard_excluded]
add("hardcoded_list", item="excluded_by_hand",
    note=" ".join(sorted(hard_excluded)))
add("hardcoded_list", item="implied_held", note=" ".join(hard_held),
    value=len(hard_held))
diff = sorted(set(hard_held) ^ set(HELD))
print(f"\nhardcoded list implied {len(hard_held)} held; derived {len(HELD)}")
for t in diff:
    cls_d = "held" if t in held else ("signal-only" if t in signal else "neither")
    cls_h = "held" if t in hard_held else "signal input"
    add("classification_differs", item=t, note=f"derived {cls_d}, hardcoded {cls_h}")
    print(f"  differs: {t:<6} derived {cls_d:<12} hardcoded {cls_h}")
add("classification_differs", item="count", value=len(diff))

# --- warmup, derived ------------------------------------------------------
sma_max = max(max(config.SMA_LONG_GRID), max(config.SMA_SHORT_GRID))
rsi_max = max(config.RSI_PERIOD_GRID)
rsi_conv = int(np.ceil(np.log(0.001) / np.log((rsi_max - 1) / rsi_max)))
derived = max(sma_max, rsi_conv)
add("warmup", item="max_sma_lookback", value=sma_max,
    note="max over SMA_LONG_GRID and SMA_SHORT_GRID in src/config.py")
add("warmup", item="max_rsi_period", value=rsi_max, note="max over RSI_PERIOD_GRID")
add("warmup", item="rsi_seed_convergence_sessions", value=rsi_conv,
    note="sessions for Wilder seed weight ((n-1)/n)^k to fall below 0.001")
add("warmup", item="derived_requirement", value=derived,
    note="max of the two, before the stated margin")
add("warmup", item="config_WARMUP_SESSIONS", value=config.WARMUP_SESSIONS)
add("warmup", item="stated_margin", value=config.WARMUP_SESSIONS - derived)
add("warmup", item="binding_lookback",
    note=f"the moving average at {sma_max} sessions binds, since it exceeds RSI seed "
         f"convergence at {rsi_conv}")
print(f"\nwarmup derived: sma {sma_max}, rsi convergence {rsi_conv}, "
      f"max {derived}, config {config.WARMUP_SESSIONS}, margin "
      f"{config.WARMUP_SESSIONS - derived}")

# --- availability ---------------------------------------------------------
C.PRIMARY_START = pd.Timestamp("2011-10-04")
env = C.build_env(verbose=False)
cal, panels = env["cal"], env["panels"]


def first_avail(panel, t):
    if t not in panel.frames:
        return None
    tr = panel[t].tr_index.reindex(cal)
    i = np.flatnonzero(tr.notna().to_numpy())
    return cal[i[0]] if len(i) else None


print("\nheld ticker first availability")
firsts = {}
for t in HELD:
    fs, fr = first_avail(panels["synthetic"], t), first_avail(panels["realized"], t)
    firsts[t] = (fs, fr)
    add("availability", item=t,
        note=f"synthetic {fs.date() if fs is not None else 'never'}",
        note2=f"realized {fr.date() if fr is not None else 'never'}")
    print(f"  {t:<6} synthetic {str(fs.date()) if fs is not None else 'never':<12} "
          f"realized {str(fr.date()) if fr is not None else 'never'}")

CANON_START = pd.Timestamp("2011-10-04")
for arm, k in (("synthetic", 0), ("realized", 1)):
    vals = [v[k] for v in firsts.values() if v[k] is not None]
    latest = max(vals)
    binder = [t for t, v in firsts.items() if v[k] == latest]
    j = int(np.searchsorted(cal.to_numpy(), np.datetime64(latest)))
    full = cal[j + config.WARMUP_SESSIONS]
    add("full_composition", item=arm, note=str(full.date()),
        note2=f"bound by {' '.join(binder)} first available {latest.date()} plus "
              f"{config.WARMUP_SESSIONS} warmup sessions",
        within=int(full < CANON_START))
    print(f"\n{arm} arm full composition on held tickers only: {full.date()}, "
          f"bound by {' '.join(binder)} at {latest.date()}")
    print(f"  before the canonical 2011-10-04: {full < CANON_START}")

# --- the two measures side by side ----------------------------------------
avail = pd.DataFrame({t: panels["realized"][t].tr_index.reindex(cal).notna()
                      for t in HELD if t in panels["realized"].frames}, index=cal)
win = cal[(cal >= CANON_START) & (cal <= pd.Timestamp("2021-08-01"))]
all_ok = avail.all(axis=1).reindex(win)
n_missing = int((~all_ok).sum())
add("two_measures", item="window_sessions", value=int(len(win)))
add("two_measures", item="sessions_any_held_ticker_unavailable", value=n_missing,
    note="listing coverage on the realized panel over the canonical window, counting "
         "sessions where a held ticker is unlisted whether or not it was targeted")
add("two_measures", item="share", value=float(n_missing / len(win)))
bc = pd.read_csv(ROOT / "outputs/session-16/boundary-correction.csv")
uf = bc[bc.table == "boundary_fills"]["unavailable_fills_from_2011_10_04"]
halt = bc[bc.table == "halt_check"]["remaining_unavailable_fills_on_corrected_boundary"]
add("two_measures", item="unavailable_fills_from_2011_10_04",
    value=float(uf.iloc[0]),
    note="outputs/session-16/boundary-correction.csv, both conventions, counting "
         "fills the strategy actually attempted and could not make, which is what "
         "7.14 defines the window by")
add("two_measures", item="remaining_unavailable_fills_on_corrected_boundary",
    value=float(halt.iloc[0]), note="same file, halt_check row")
add("two_measures", item="distinction",
    note="the two are different quantities and the 19.5 report conflated them; "
         "listing coverage counts sessions where a ticker was unlisted, the 7.14 "
         "measure counts fills attempted and failed")
print(f"\ncanonical window {len(win)} sessions, any held ticker unlisted on the "
      f"realized panel: {n_missing} ({n_missing/len(win):.4f})")
print(f"unavailable fills from 2011-10-04 per session-16: {float(uf.iloc[0])}, "
      f"remaining on the corrected boundary: {float(halt.iloc[0])}")

COLS = ["table", "item", "value", "within", "note", "note2"]
with open(OUT / "held-composition.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"\nwrote {OUT/'held-composition.csv'} with {len(rows)} rows")
