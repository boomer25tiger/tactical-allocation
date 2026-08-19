"""Session 18 step 1: the reachability classification.

Signals only. For every value on every searched axis, all other axes held
at canonical, count the firing of every terminal state in all four
sleeves across the corrected primary window from 2011-10-04 on the
realized panel, which is the panel of the designated cell 4.1b.

An axis is SMOOTH when the set of reachable terminals is identical across
all its values, and STRUCTURAL when at least one terminal switches
between reachable and unreachable, so its specification curve spans
strategies of different shape rather than a parameter sweep.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s14_common as C          # noqa: E402
import scripts.s17_common as S          # noqa: E402
import scripts.s18_terminals as T       # noqa: E402
from src import config                  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-18"
OUT.mkdir(parents=True, exist_ok=True)
PRIMARY_START = pd.Timestamp("2011-10-04")
rows = []

env = C.build_env(verbose=False)
cal = env["cal"]
sig_real = S.fat_signals(env["panels"]["realized"], cal)
sig_syn = S.fat_signals(env["panels"]["synthetic"], cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(PRIMARY_START)))
W = config.WARMUP_SESSIONS
cv = list(S.canonical_values())

# ---------------------------------------------------------------------------
# Positive control, on session 13.5's own basis and on this session's basis
# ---------------------------------------------------------------------------
BB, FB = "_t11_bond_baller:L204", "_t11_feaver_bear:L233"
K_OS = S.AXIS_NAMES.index("oversold")
EXPECT = [(20, 0, 0), (25, 0, 0), (30, 0, 0), (35, 1, 23), (40, 10, 113)]


def psq_sweep(sig, i_from):
    out = []
    for v in S.AXIS_VALUES[K_OS]:
        alt = list(cv); alt[K_OS] = v; S.apply_spec(tuple(alt))
        c = T.count_terminals(sig, i_from, len(cal))
        bb = sum(n for (_s, nm), n in c.items() if nm.startswith(BB))
        fb = sum(n for (_s, nm), n in c.items() if nm.startswith(FB))
        out.append((v, bb, fb))
    S.apply_spec(tuple(cv))
    return out


print("== step 1 positive control ==")
basis_13_5 = psq_sweep(sig_syn, W)
basis_here = psq_sweep(sig_real, i0)
ctrl_pass = basis_13_5 == EXPECT
print(f"  session 13.5 recorded                       {EXPECT}")
print(f"  synthetic panel, full window from warm-up   {basis_13_5}   reproduces {ctrl_pass}")
print(f"  realized panel, primary window 2011-10-04   {basis_here}")
for lab, got, basis in (("session_13_5_basis", basis_13_5,
                         "synthetic panel, full window from warm-up, "
                         "as scripts/s13_5_diagnostics.py line 374 measured it"),
                        ("session_18_basis", basis_here,
                         "realized panel, primary window from 2011-10-04, "
                         "the panel and window of the designated cell 4.1b")):
    for v, bb, fb in got:
        rows.append({"table": "positive_control", "basis": lab, "axis": "oversold",
                     "axis_value": v, "terminal": BB, "count": bb, "note": basis})
        rows.append({"table": "positive_control", "basis": lab, "axis": "oversold",
                     "axis_value": v, "terminal": FB, "count": fb, "note": basis})
rows.append({"table": "positive_control", "basis": "verdict",
             "note": ("reproduces session 13.5 exactly on that session's own basis; the "
                      "session 18 prompt named the primary window, on which the figures "
                      "differ because session 13.5 measured the synthetic panel over the "
                      "full window from warm-up"),
             "count": int(ctrl_pass)})
assert ctrl_pass, "step 1 positive control failed on session 13.5's own basis"

# ---------------------------------------------------------------------------
# The sweep
# ---------------------------------------------------------------------------
print("\n== nine-axis terminal census, realized panel, primary window ==")
S.apply_spec(tuple(cv))
canon_counts = T.count_terminals(sig_real, i0, len(cal))
universe = set(canon_counts)

census = {}
for k, axis in enumerate(S.AXIS_NAMES):
    for v in S.AXIS_VALUES[k]:
        alt = list(cv); alt[k] = v; S.apply_spec(tuple(alt))
        c = T.count_terminals(sig_real, i0, len(cal))
        census[(axis, v)] = c
        universe |= set(c)
    print(f"  {axis} done")
S.apply_spec(tuple(cv))
universe = sorted(universe)
print(f"  {len(universe)} distinct terminals across all axis values")

for (axis, v), c in census.items():
    for key in universe:
        rows.append({"table": "census", "axis": axis, "axis_value": v,
                     "sleeve": key[0], "terminal": key[1], "count": int(c.get(key, 0)),
                     "is_canonical_value": int(v == cv[S.AXIS_NAMES.index(axis)])})

# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------
print("\n== classification ==")
classification = {}
for k, axis in enumerate(S.AXIS_NAMES):
    vals = S.AXIS_VALUES[k]
    reach = {v: {key for key in universe if census[(axis, v)].get(key, 0) > 0} for v in vals}
    sets = list(reach.values())
    structural = any(s != sets[0] for s in sets[1:])
    switching = sorted({key for key in universe
                        if any(census[(axis, v)].get(key, 0) > 0 for v in vals)
                        and any(census[(axis, v)].get(key, 0) == 0 for v in vals)})
    # order-of-magnitude movers among values where the terminal is live
    movers = []
    for key in universe:
        live = [census[(axis, v)].get(key, 0) for v in vals]
        nz = [x for x in live if x > 0]
        if len(nz) >= 2 and max(nz) > 10 * min(nz):
            movers.append((key, min(nz), max(nz)))
    classification[axis] = "structural" if structural else "smooth"
    print(f"  {axis:16s} {classification[axis]:11s} "
          f"{len(switching)} terminals switch reachability, {len(movers)} order-of-magnitude movers")
    rows.append({"table": "classification", "axis": axis,
                 "classification": classification[axis],
                 "n_values": len(vals),
                 "n_terminals_switching_reachability": len(switching),
                 "n_order_of_magnitude_movers": len(movers),
                 "terminals_switching": "; ".join(t[1] for t in switching),
                 "canonical_value": cv[k]})
    for key, lo_, hi_ in movers:
        rows.append({"table": "order_of_magnitude_mover", "axis": axis,
                     "sleeve": key[0], "terminal": key[1],
                     "min_nonzero": lo_, "max_count": hi_,
                     "ratio": round(hi_ / lo_, 2)})
    for key in switching:
        live = {v: census[(axis, v)].get(key, 0) for v in vals}
        rows.append({"table": "reachability_switch", "axis": axis,
                     "sleeve": key[0], "terminal": key[1],
                     "counts_by_value": "; ".join(f"{v}={n}" for v, n in live.items()),
                     "dead_at": "; ".join(str(v) for v, n in live.items() if n == 0),
                     "live_at": "; ".join(str(v) for v, n in live.items() if n > 0)})

# terminals dead at some axis value anywhere
dead_any = sorted({key for key in universe
                   for (axis, v) in census
                   if census[(axis, v)].get(key, 0) == 0})
for key in dead_any:
    where = [f"{a}={v}" for (a, v) in census if census[(a, v)].get(key, 0) == 0]
    rows.append({"table": "dead_terminal", "sleeve": key[0], "terminal": key[1],
                 "n_axis_values_dead": len(where),
                 "dead_at": "; ".join(where[:40]),
                 "canonical_count": int(canon_counts.get(key, 0))})

# S3 vote threshold explicit note
nmem = len(config.S3_VOTE_MEMBERSHIP)
for v in S.AXIS_VALUES[S.AXIS_NAMES.index("vote")]:
    c = census[("vote", v)]
    s3 = {key[1]: c.get(key, 0) for key in universe if key[0] == "S3"}
    rows.append({"table": "s3_vote", "axis": "vote", "axis_value": v,
                 "member_count": nmem, "is_unanimity": int(v == nmem),
                 "note": "; ".join(f"{k2.split()[0]}={n}" for k2, n in sorted(s3.items()))})

cols = ["table", "basis", "axis", "axis_value", "sleeve", "terminal", "count",
        "is_canonical_value", "classification", "n_values",
        "n_terminals_switching_reachability", "n_order_of_magnitude_movers",
        "terminals_switching", "canonical_value", "counts_by_value", "dead_at",
        "live_at", "min_nonzero", "max_count", "ratio", "n_axis_values_dead",
        "canonical_count", "member_count", "is_unanimity", "note"]
with open(OUT / "reachability.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"\nwrote {OUT / 'reachability.csv'} with {len(rows)} rows")

import json
json.dump(classification, open(OUT / "axis-classification.json", "w"), indent=1)
print("structural axes:", [a for a, c in classification.items() if c == "structural"])
print("smooth axes:    ", [a for a, c in classification.items() if c == "smooth"])
