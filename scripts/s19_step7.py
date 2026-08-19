"""Session 19 step 7: the specification curve.

Three parts. The grid marginals of the Lo-corrected Sharpe across the nine
searched axes, with the six structural axes reported as separated strata
rather than as a single sweep. The canonical point's rank within the grid.
The specification curve spanning the 9.11 choice axes plus NAV as closed by
session 16's D20.

Figures are read from the emitted CSVs of the sessions that measured them,
per 9.12, rather than recomputed here. Where no emitted CSV in this
repository carries a comparison for a curve axis, the axis is recorded with
that status rather than filled in.
"""
from __future__ import annotations

import csv
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
NSHARD = 8
TOTAL = S.grid_size()
rows = []

met = np.concatenate([
    np.fromfile(G / f"metrics-{k:02d}.f64", dtype=np.float64).reshape(-1, W.N_MET)
    for k in range(NSHARD)])
met = met[np.argsort(met[:, 0].astype(np.int64))]
base = 1 + len(S.AXES)
sh_lo = met[:, base + W.METRIC_ORDER.index("sharpe_lo")]
ann = met[:, base + W.METRIC_ORDER.index("ann_return")]
idx = pd.read_csv(S18 / "spec-index-augmented.csv")
CANON = S.index_of(S.canonical_values())
CV = S.canonical_values()

# --- 1. marginals ----------------------------------------------------------
print("== marginal distribution of the Lo-corrected Sharpe by axis ==")
for k, axis in enumerate(S.AXIS_NAMES):
    cls = idx[f"class_{axis}"].iloc[0]
    col = met[:, 1 + k]
    print(f"-- {axis} ({cls}) --")
    for v in S.AXIS_VALUES[k]:
        m = col == float(v)
        s = sh_lo[m]
        rows.append({"table": "axis_marginal", "axis": axis, "classification": cls,
                     "reported_as": "separated stratum" if cls == "structural" else "sweep",
                     "axis_value": v, "is_canonical_value": int(float(v) == float(CV[k])),
                     "n_specifications": int(m.sum()),
                     "sharpe_lo_mean": float(s.mean()),
                     "sharpe_lo_sd": float(s.std(ddof=1)),
                     "sharpe_lo_p05": float(np.percentile(s, 5)),
                     "sharpe_lo_p50": float(np.percentile(s, 50)),
                     "sharpe_lo_p95": float(np.percentile(s, 95)),
                     "sharpe_lo_min": float(s.min()), "sharpe_lo_max": float(s.max())})
        print(f"   {v!s:>6}  n={int(m.sum()):>6,}  mean {s.mean():.4f}  "
              f"p05 {np.percentile(s,5):.4f}  p50 {np.percentile(s,50):.4f}  "
              f"p95 {np.percentile(s,95):.4f}")

# --- 2. canonical rank -----------------------------------------------------
r_sh = int((sh_lo > sh_lo[CANON]).sum()) + 1
r_an = int((ann > ann[CANON]).sum()) + 1
for nm, r, val in (("sharpe_lo", r_sh, sh_lo[CANON]), ("ann_return", r_an, ann[CANON])):
    rows.append({"table": "canonical_rank", "axis": nm, "axis_value": float(val),
                 "n_specifications": TOTAL, "rank": r,
                 "percentile": 100.0 * (1.0 - (r - 1) / TOTAL),
                 "note": "rank 1 is the highest of the 121,500 evaluated"})
print(f"\ncanonical rank on Lo-corrected Sharpe {r_sh:,} of {TOTAL:,}")
print(f"canonical rank on annualised return    {r_an:,} of {TOTAL:,}")

# --- 3. the specification curve -------------------------------------------
CANON_CELL = dict(panel="realized", convention="o2o", commission_arm="S",
                  cap_arm="cap5", window="primary")


def add_curve(axis, arm, a, s, source, note="", is_canon=0):
    rows.append({"table": "specification_curve", "axis": axis, "arm": str(arm),
                 "ann_return": a, "sharpe_lo": s, "source": source,
                 "is_canonical_arm": is_canon, "note": note})


cc = pd.read_csv(ROOT / "outputs/session-14/canonical-capped.csv")
SRC_CC = "outputs/session-14/canonical-capped.csv"


def cc_pick(**over):
    q = dict(CANON_CELL); q.update(over)
    m = np.ones(len(cc), dtype=bool)
    for k, v in q.items():
        if k in cc.columns:
            m &= (cc[k].astype(str) == str(v))
    sub = cc[m]
    return sub


# The cell grid in canonical-capped.csv is not complete. The synthetic panel
# exists only at close-to-close, and the realized open-to-open arm exists only
# on the primary window. Each axis is therefore compared at the most canonical
# cell in which every arm of that axis exists, and the cell used is recorded on
# each row rather than left implicit.
AXIS_CELLS = [
    ("panel", "panel", ["realized", "synthetic"],
     dict(convention="c2c", commission_arm="S", cap_arm="cap5", window="primary"),
     "realized"),
    ("convention", "convention", ["o2o", "o2o_nopremium", "c2c"],
     dict(panel="realized", commission_arm="S", cap_arm="cap5", window="primary"),
     "o2o"),
    ("window", "window", ["primary", "full", "early"],
     dict(panel="synthetic", convention="c2c", commission_arm="S", cap_arm="cap5"),
     "primary"),
    ("commission_arm", "commission_arm", ["F", "S", "T", "Z"],
     dict(panel="realized", convention="o2o", cap_arm="cap5", window="primary"),
     "S"),
    ("participation_cap", "cap_arm", ["cap5", "uncapped"],
     dict(panel="realized", convention="o2o", commission_arm="S", window="primary"),
     "cap5"),
]
for axis, colname, arms, cell, canon_arm in AXIS_CELLS:
    got = 0
    cellstr = " ".join(f"{k}={v}" for k, v in sorted(cell.items()))
    for arm in arms:
        q = dict(cell); q[colname] = arm
        m = cc.ann_return.notna()
        for k, v in q.items():
            if k in cc.columns:
                m &= (cc[k].astype(str) == str(v))
        sub = cc[m]
        if len(sub):
            r0 = sub.iloc[0]
            add_curve(axis, arm, float(r0.ann_return), float(r0.sharpe_lo), SRC_CC,
                      note=f"held at {cellstr}",
                      is_canon=int(str(arm) == str(canon_arm)))
            got += 1
    rows.append({"table": "curve_axis_status", "axis": axis,
                 "arm": f"{got} of {len(arms)}", "source": SRC_CC,
                 "note": f"sourced from an emitted CSV, compared at {cellstr}"})
    print(f"curve axis {axis}: {got} of {len(arms)} arms sourced at {cellstr}")

nav = pd.read_csv(ROOT / "outputs/session-15/nav-sweep.csv")
nav = nav[(nav.table == "cell") & (nav.convention == "o2o") & (nav.window == "primary")]
for _, r0 in nav.iterrows():
    add_curve("starting_nav", r0.nav, float(r0.ann_return), float(r0.sharpe_lo),
              "outputs/session-15/nav-sweep.csv",
              note="joined the specification curve and not the grid axes, D20 session 16",
              is_canon=int(float(r0.nav) == 1_000_000.0))
rows.append({"table": "curve_axis_status", "axis": "starting_nav",
             "arm": f"{len(nav)} arms", "source": "outputs/session-15/nav-sweep.csv",
             "note": "sourced from an emitted CSV; added to the curve by D20 session 16"})
print(f"curve axis starting_nav: {len(nav)} arms sourced")

cs = pd.read_csv(ROOT / "outputs/session-15/cost-sweep-designated.csv")
n_slip = 0
for _, r0 in cs.iterrows():
    if pd.notna(r0.get("slippage_bp")) and pd.notna(r0.get("ann_return")):
        add_curve("slippage_model", f"uniform_{r0.slippage_bp:g}bp",
                  float(r0.ann_return), float(r0.sharpe_lo),
                  "outputs/session-15/cost-sweep-designated.csv")
        n_slip += 1
ref = cs[cs.table == "reference"]
for _, r0 in ref.iterrows():
    if pd.notna(r0.get("ann_return")):
        add_curve("slippage_model", str(r0.line), float(r0.ann_return),
                  float(r0.sharpe_lo), "outputs/session-15/cost-sweep-designated.csv",
                  note="the designated tiered plus premium model", is_canon=1)
        n_slip += 1
rows.append({"table": "curve_axis_status", "axis": "slippage_model",
             "arm": f"{n_slip} arms", "source": "outputs/session-15/cost-sweep-designated.csv",
             "note": "sourced from an emitted CSV; the uniform sweep REPLACES the tiered "
                     "model rather than stacking on it"})
print(f"curve axis slippage_model: {n_slip} arms sourced")

fb = pd.read_csv(ROOT / "outputs/session-13.8/financing-base.csv")
ws = fb[fb.table == "widened_sweep"]
n_fin = 0
for _, r0 in ws.iterrows():
    if pd.notna(r0.get("sweep_bp")):
        add_curve("financing_spread", f"{r0.sweep_bp}bp", float("nan"), float("nan"),
                  "outputs/session-13.8/financing-base.csv",
                  note="D16 remains open and assumed; the sweep records the spread levels "
                       "rather than a strategy return per level in this CSV")
        n_fin += 1
rows.append({"table": "curve_axis_status", "axis": "financing_spread",
             "arm": f"{n_fin} levels", "source": "outputs/session-13.8/financing-base.csv",
             "note": "levels sourced; no per-level designated-cell return is carried in an "
                     "emitted CSV, and D16 is open"})
print(f"curve axis financing_spread: {n_fin} levels sourced, no per-level return")

for axis, why in (("smh_accrual",
                   "9.8 records the SMH accrual arm as an implementation dimension run at "
                   "canonical parameters and not crossed into the grid. No emitted CSV in "
                   "this repository carries a two-arm designated-cell comparison for it"),
                  ("sizing_mode",
                   "named as a 9.11 curve axis. No emitted CSV in this repository carries a "
                   "two-arm designated-cell comparison for it"),
                  ("completion_rule",
                   "the unavailable-fill completion rule, named as a 9.11 curve axis. No "
                   "emitted CSV in this repository carries a two-arm designated-cell "
                   "comparison for it")):
    rows.append({"table": "curve_axis_status", "axis": axis, "arm": "0 arms",
                 "source": "", "note": "NOT SOURCED. " + why})
    print(f"curve axis {axis}: NOT SOURCED")

rows.append({"table": "excluded_axis", "axis": "tier_two_offset",
             "arm": "5, 10, 15", "source": "outputs/session-17/axis-adoption.csv",
             "note": "NOT on the specification curve and NOT searched by the grid. The "
                     "register records 7.4 as informed rather than closed, so it is not a "
                     "decision the study made, and a curve spanning it would report "
                     "sensitivity to a parameter the register never fixed. Held at its "
                     "canonical value of 10 on every one of the 121,500 specifications, so "
                     "the canonical point is unchanged"})

SEVEN = [
    ("4.6 starting NAV", "closed session 13.7 at 1,000,000; joined the specification curve "
                         "by D20 session 16, so it is now ON the curve rather than off it. "
                         "The consequential one, since it enters the return series through "
                         "integer truncation, the commission minimum, and the participation cap"),
    ("5.7 per-year covariance", "reporting convention, does not enter the return series"),
    ("Sharpe numerator registration", "closed as the 8.2 amendment session 13.9, arithmetic "
                                      "mean excess annualised; dual-reported under both "
                                      "numerator definitions"),
    ("D5 disposition", "reporting or diagnostic convention, does not enter the return series"),
    ("D6 disposition", "reporting or diagnostic convention, does not enter the return series"),
    ("D7 disposition", "reporting or diagnostic convention, does not enter the return series"),
    ("D10 disposition", "reporting or diagnostic convention, does not enter the return series"),
]
for name, status in SEVEN:
    rows.append({"table": "off_axis_post_result_choice", "axis": name, "source":
                 "outputs/session-14/decision-audit-reconciled.csv", "note": status})
rows.append({"table": "off_axis_post_result_choice", "axis": "count",
             "arm": "7 of 22", "source": "register 9.11 as corrected session 15",
             "note": "seven of the 22 post-result choices do not lie on any of the nine "
                     "recorded specification-curve axes; six are reporting or diagnostic "
                     "conventions and 4.6 NAV is the consequential one, since closed onto "
                     "the curve by D20"})

COLS = ["table", "axis", "classification", "reported_as", "axis_value",
        "is_canonical_value", "n_specifications", "sharpe_lo_mean", "sharpe_lo_sd",
        "sharpe_lo_p05", "sharpe_lo_p50", "sharpe_lo_p95", "sharpe_lo_min",
        "sharpe_lo_max", "rank", "percentile", "arm", "ann_return", "sharpe_lo",
        "is_canonical_arm", "source", "note"]
with open(OUT / "specification-curve.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"\nwrote {OUT/'specification-curve.csv'} with {len(rows)} rows")
