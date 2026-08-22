"""Session 27 phase C. The holdout read. ONE PASS.

The read is authorised by the prediction committed at 9.64 and gated by phase A.
The truncation at 2.10 is lifted for this process alone by setting
READ_HOLDOUT_THROUGH before scripts.s13_backtest is imported. The boundary itself
is not moved, the default in the module is unchanged, and no strategy parameter
reads the variable.

Every quantity the prediction requires is computed here. Nothing is recomputed
after seeing another and no specification is varied. The ladder, the canonical and
the combined window are written to disk before any component is evaluated.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))

# The single-read lift. Set before the import that reads it.
READ_THROUGH = "2026-08-14"          # phase B established this from the frozen inputs
os.environ["READ_HOLDOUT_THROUGH"] = READ_THROUGH

import numpy as np                                    # noqa: E402
import pandas as pd                                   # noqa: E402
import scripts.s13_backtest as bt                     # noqa: E402
import scripts.s14_common as C                        # noqa: E402
import scripts.s15_lines as L                         # noqa: E402
from src import config                                # noqa: E402

OUT = ROOT / "outputs" / "session-27"
OUT.mkdir(parents=True, exist_ok=True)
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY_START = C.PRIMARY_START

LADDER = ["buy_hold_QQQ", "buy_hold_TQQQ", "vol_targeted_QQQ_matched",
          "naive_fast_1d_momentum", "matched_exposure_levered_QQQ_1.70",
          "long_legs_only", "equal_weight_universe", "sleeve_T10_standalone",
          "sleeve_T11_standalone", "sleeve_S2_standalone", "sleeve_S3_standalone"]

assert bt.HOLDOUT_LAST_DATE == pd.Timestamp(READ_THROUGH), "the lift did not take"
print(f"read window extends to {bt.HOLDOUT_LAST_DATE.date()}, boundary "
      f"{BOUNDARY.date()} unchanged")

# ---- the canonical specification, every parameter read from config ------------
print("building the environment")
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
o2o, cap_fn, cal = env["o2o"], env["cap_fn"], env["cal"]
spec = {
    "convention": "open-to-open",
    "panel": "realized",
    "slippage": f"class-tiered at the {C.ANCHOR} basis point anchor with the "
                f"{C.PREMIUM_CENTRAL}x opening auction premium",
    "commission_arm": C.CANONICAL_ARM,
    "participation_cap_level": C.CAP_LEVEL,
    "starting_nav": bt.START_NAV,
    "anchor_bp": C.ANCHOR,
    "premium_multiple": C.PREMIUM_CENTRAL,
    "gross_cap": config.GROSS_CAP,
}
print("  " + "; ".join(f"{k}={v}" for k, v in spec.items()))

acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
daily = acc["daily"]
print(f"  canonical account runs {daily.index.min().date()} to "
      f"{daily.index.max().date()}")

LINES = L.make_lines(cal)
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(PRIMARY_START)))
line_acc = {"STRATEGY": acc}
for ln in LADDER:
    print(f"  running {ln}")
    line_acc[ln] = bt.run_account(
        sig["sig"], o2o, LINES[ln][0](o2o, sig["rows"], i0), C.ANCHOR,
        commission_fn=C.ARMS[C.CANONICAL_ARM],
        slip_fn=C.slip_class_premium(), cap_fn=cap_fn)


def window(a, lo, hi=None):
    d = a["daily"]
    m = d.index >= lo
    if hi is not None:
        m = m & (d.index <= hi)
    return d["ret"].loc[m].dropna(), d["nav"].loc[m]


def stats(a, lo, hi=None):
    r, nav = window(a, lo, hi)
    m = L.standalone_metrics(r, nav, a["orders"])
    x = r.to_numpy()
    n = len(x)
    mu, sd = float(x.mean()), float(x.std(ddof=1))
    z = (x - mu) / sd
    return {**m,
            "n_sessions": n,
            "daily_mean": mu,
            "daily_sd": sd,
            "skewness": float((z ** 3).mean() * n * n / ((n - 1) * (n - 2))),
            "excess_kurtosis": float(
                (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * (z ** 4).sum()
                - 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))),
            "first_session": str(r.index.min().date()),
            "last_session": str(r.index.max().date())}


COLS = ["ann_return", "ann_vol", "sharpe_naive", "sharpe_lo", "max_drawdown",
        "ann_turnover", "n_sessions", "daily_mean", "daily_sd", "skewness",
        "excess_kurtosis", "first_session", "last_session"]


def emit(span_name, lo, hi, path):
    rows, vals = [], {}
    for ln, a in line_acc.items():
        s = stats(a, lo, hi)
        vals[ln] = s
        rows.append({"table": "line", "span": span_name, "line": ln,
                     **{k: s.get(k) for k in COLS}})
    for conv in ("sharpe_naive", "sharpe_lo"):
        order = sorted(vals, key=lambda k: -vals[k][conv])
        for rk, ln in enumerate(order, 1):
            rows.append({"table": "rank", "span": span_name, "line": ln,
                         "convention": conv, "rank": rk, "of": len(order),
                         "value": vals[ln][conv]})
    rows.append({"table": "span", "span": span_name, "line": "",
                 "note": f"{lo.date()} to {hi.date() if hi is not None else 'end'}, "
                         f"{vals['STRATEGY']['n_sessions']} sessions"})
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table", "span", "line", "convention",
                                          "rank", "of", "value", "note"] + COLS,
                           extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"wrote {path.name}, {len(rows)} rows")
    return vals


print("\n== holdout span ==")
hold = emit("holdout", BOUNDARY, None, OUT / "holdout-ladder.csv")
print("\n== combined window ==")
comb = emit("combined", PRIMARY_START, None, OUT / "combined-window.csv")

# ---- the canonical's own record --------------------------------------------------
rows = []
def add(t, **kw): rows.append({"table": t, **kw})
for k, v in spec.items():
    add("specification", item=k, value=v, note="read from src/config.py and "
        "scripts/s14_common.py rather than typed")
add("read_control", item="read_holdout_through", value=READ_THROUGH,
    note="the single-read lift, set in this process only. The module default is "
         "unchanged at 2021-07-31 and the boundary is unchanged at "
         f"{BOUNDARY.date()}")
add("read_control", item="holdout_boundary", value=str(BOUNDARY.date()))
add("read_control", item="primary_start", value=str(PRIMARY_START.date()))
for span_name, vals in (("holdout", hold), ("combined", comb)):
    s = vals["STRATEGY"]
    for k in COLS:
        add(f"canonical_{span_name}", item=k, value=s.get(k))
    for conv in ("sharpe_naive", "sharpe_lo"):
        order = sorted(vals, key=lambda x: -vals[x][conv])
        add(f"canonical_{span_name}", item=f"rank_{conv}",
            value=order.index("STRATEGY") + 1, note=f"of {len(order)}")
with open(OUT / "holdout-canonical.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["table", "item", "value", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote holdout-canonical.csv, {len(rows)} rows")

# ---- the raw material later phases need, written now so the read is not repeated --
np.save(OUT / "_holdout_returns.npy",
        np.array([1.0]))          # placeholder replaced below
store = {}
for ln, a in line_acc.items():
    r, _ = window(a, BOUNDARY, None)
    store[ln] = r
pd.DataFrame(store).to_parquet(OUT / "_holdout_line_returns.parquet")
store_c = {}
for ln, a in line_acc.items():
    r, _ = window(a, PRIMARY_START, None)
    store_c[ln] = r
pd.DataFrame(store_c).to_parquet(OUT / "_combined_line_returns.parquet")
(OUT / "_holdout_returns.npy").unlink()
pd.DataFrame({"nav": acc["daily"]["nav"], "ret": acc["daily"]["ret"]}).to_parquet(
    OUT / "_canonical_daily.parquet")
acc["orders"].to_parquet(OUT / "_canonical_orders.parquet")
print("wrote the retained series for phases D through G")

s = hold["STRATEGY"]
print(f"\nSTRATEGY holdout  naive {s['sharpe_naive']:.6f}  lo {s['sharpe_lo']:.6f}  "
      f"ann {s['ann_return']:.6f}  n {s['n_sessions']}")
for conv in ("sharpe_naive", "sharpe_lo"):
    order = sorted(hold, key=lambda k: -hold[k][conv])
    print(f"  rank on {conv}: {order.index('STRATEGY')+1} of {len(order)}")
