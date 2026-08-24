#!/usr/bin/env python3
"""Reproduce the study's canonical figure from the frozen inputs.

Path-independent. ROOT resolves from this file's own location, so the script runs
from any clone directory without editing. It imports only the engine modules, all
of which resolve their own paths the same way.

Expected output, being the designated headline cell over the primary window from
2011-10-04:

    annualised return      0.521845
    Lo-corrected Sharpe    1.381701
    sessions               2472

The tolerance is 5e-07 on each of the two figures and exact on the session count.
Bit-identical output is NOT asserted, since float reduction order varies with
thread count and BLAS version.

Exit code 0 on reproduction and 1 on any deviation beyond tolerance.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TOL = 5e-7
TARGETS = {"ann_return": 0.521845, "sharpe_lo": 1.381701, "n_sessions": 2472}


def main() -> int:
    t0 = time.time()
    print(f"root {ROOT}")
    print(f"python {sys.version.split()[0]}")

    import scripts.s13_backtest as bt
    import scripts.s14_common as C
    import scripts.s15_lines as L

    print(f"holdout truncation in force at {bt.HOLDOUT_LAST_DATE.date()}, "
          f"boundary {bt.HOLDOUT_BOUNDARY.date()}")
    # The REALIZED arm alone. scripts/s14_common.py build_env also builds the
    # synthetic arm, whose reconstructions live under data/interim/synthetics/ and
    # are gitignored as rebuildable, so a clean clone does not carry them and the
    # rebuild of two of them reads a network series. The designated cell is the
    # realized arm, so this path needs neither. The calendar is taken from the
    # realized SPY frame, which is the same frozen frame the synthetic panel carries
    # for an unlevered ticker.
    print("building the realized-arm environment from the frozen inputs")
    panel = bt.load_arm_panel("realized")
    bt.assert_holdout(panel)
    cal = panel["SPY"].index
    _s = bt.ArmSignals(panel, cal)
    sig = {"sig": _s, **bt.run_signals(_s)}
    o2o = C.o2o_panel_from(panel)
    cap_fn = C.make_cap_fn(C.dollar_volume_frame(cal, sorted(C.TIER_CLASS)))
    env = {"o2o": o2o, "cap_fn": cap_fn}

    print("running the designated cell, open to open, realized panel, "
          f"class-tiered slippage at the {C.ANCHOR} basis point anchor with the "
          f"{C.PREMIUM_CENTRAL}x opening auction premium, commission arm "
          f"{C.CANONICAL_ARM}, participation cap {C.CAP_LEVEL}")
    acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                         commission_fn=C.ARMS[C.CANONICAL_ARM],
                         slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
    d = acc["daily"]
    ret = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
    m = L.standalone_metrics(ret, d["nav"], acc["orders"])

    got = {"ann_return": float(m["ann_return"]),
           "sharpe_lo": float(m["sharpe_lo"]),
           "n_sessions": len(ret)}
    ok = True
    print()
    print(f"{'quantity':22s} {'observed':>22s} {'target':>12s} {'deviation':>14s}")
    for k, tgt in TARGETS.items():
        v = got[k]
        dev = abs(v - tgt)
        good = (v == tgt) if k == "n_sessions" else (dev <= TOL)
        ok &= good
        print(f"{k:22s} {v!r:>22s} {tgt:>12} {dev:>14} {'' if good else '  FAIL'}")
    print()
    print(f"window {ret.index.min().date()} to {ret.index.max().date()}")
    print(f"tolerance {TOL} on each figure, exact on the session count")
    print(f"wall clock {time.time() - t0:.1f} seconds")
    print("REPRODUCED" if ok else "DEVIATION BEYOND TOLERANCE")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
