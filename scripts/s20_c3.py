"""C3. The matched-exposure levered QQQ row at 1.777 rather than 1.70."""
from __future__ import annotations
import csv, sys, os
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
OUT = ROOT / "outputs" / "session-20" / "rebuilt"
env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(C.PRIMARY_START)))
rows = []
rows.append({"table": "convention", "item": "financing",
             "note": "the row holds the TQQQ ticker at weight exposure/3 rebalanced "
                     "daily through daily_constant in scripts/s15_lines.py line 118. On "
                     "the realized arm TQQQ loads from the frozen fund parquet, so "
                     "financing and daily reset are the issuer's own and no separate "
                     "financing model applies. Read from code rather than assumed"})
for label, expo in (("1.70_registered_8_8", 1.70), ("1.777_D25_superseded", 1.777)):
    L.MEAN_EFF_EXPOSURE = expo
    lines = L.make_lines(cal)
    rws = lines["matched_exposure_levered_QQQ_1.70"][0](o2o, sig["rows"], i0)
    acc = bt.run_account(sig["sig"], o2o, rws, C.ANCHOR,
                         commission_fn=C.ARMS[C.CANONICAL_ARM],
                         slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
    d = acc["daily"]
    r = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
    m = L.standalone_metrics(r, d["nav"], acc["orders"])
    rows.append({"table": "matched_exposure", "item": label, "exposure": expo,
                 "tqqq_weight": expo / 3.0, "ann_return": m["ann_return"],
                 "ann_vol": m["ann_vol"], "sharpe_naive": m["sharpe_naive"],
                 "sharpe_lo": m["sharpe_lo"], "n_sessions": len(r)})
    print(f"  exposure {expo}: weight {expo/3:.4f} ann {m['ann_return']:.6f} "
          f"vol {m['ann_vol']:.6f} naive {m['sharpe_naive']:.6f} lo {m['sharpe_lo']:.6f}")
a, b = [r for r in rows if r["table"] == "matched_exposure"]
for k in ("ann_return", "ann_vol", "sharpe_naive", "sharpe_lo"):
    rows.append({"table": "delta", "item": k, "ann_return": b[k] - a[k],
                 "note": "1.777 minus 1.70, both on the corrected boundary"})
with open(OUT / "matched-exposure-1777.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["table", "item", "exposure", "tqqq_weight",
                                       "ann_return", "ann_vol", "sharpe_naive",
                                       "sharpe_lo", "n_sessions", "note"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'matched-exposure-1777.csv'}")
