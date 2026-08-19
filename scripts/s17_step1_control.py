"""Session 17 step 1 positive control.

The canonical specification is evaluated through the grid worker's own
code path. It must reproduce the designated cell (4.1b) at 52.18%
annualised and Lo-corrected Sharpe 1.3817 to four decimal places. A
mismatch halts the grid.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s13_backtest as bt      # noqa: E402
import scripts.s14_common as C         # noqa: E402
import scripts.s15_lines as L          # noqa: E402
import scripts.s17_common as S         # noqa: E402
import scripts.s17_grid_worker as W    # noqa: E402
from src import config                 # noqa: E402

TARGET_ANN, TARGET_LO = 0.5218, 1.3817

C.PRIMARY_START = W.PRIMARY_START
S.install_rf_cache()
bt.s17_enable_engine_cache(True)
env = C.build_env(verbose=False)
cal = env["cal"]
sig = S.fat_signals(env["panels"]["realized"], cal)
rfa = S.rf_factor_array(cal)

cv = S.canonical_values()
ci = S.index_of(cv)
print(f"canonical values {cv}")
print(f"canonical index  {ci:,} of {S.grid_size():,}, decode roundtrip {S.spec_at(ci) == cv}")

S.apply_spec(S.spec_at(ci))
print("config after apply_spec: SMA_LONG %s CRASH %s RSI %s/%s/%s T1 %s T2 %s OS %s SMA_S %s VOTE %s"
      % (config.SMA_LONG, config.CRASH_THRESHOLD_PCT, config.RSI_PERIOD_EXHAUSTION,
         config.RSI_PERIOD_DIP, config.RSI_PERIOD_RELATIVE_STRENGTH,
         config.OVERBOUGHT_TIER_1, config.OVERBOUGHT_TIER_2, config.OVERSOLD,
         config.SMA_SHORT, config.S3_VOTE_THRESHOLD))

rows = bt.run_signals(sig)["rows"]
acc = bt.run_account(sig, env["o2o"], rows, C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"],
                     rf_factors=rfa)
r = C.window_slice(acc["daily"]["ret"], "primary")
m = L.standalone_metrics(r, acc["daily"]["nav"], acc["orders"])

ga, gl = abs(m["ann_return"] - TARGET_ANN), abs(m["sharpe_lo"] - TARGET_LO)
print(f"\nprimary window sessions {len(r)}, {r.index[0].date()} to {r.index[-1].date()}")
print(f"ann_return {m['ann_return']:.6f}  target {TARGET_ANN}  gap {ga:.2e}  match4dp {ga < 5e-5}")
print(f"sharpe_lo  {m['sharpe_lo']:.6f}  target {TARGET_LO}  gap {gl:.2e}  match4dp {gl < 5e-5}")
missing = [k for k in W.METRIC_ORDER if k not in m]
extra = [k for k in m if k not in W.METRIC_ORDER]
print(f"metric order covers standalone_metrics exactly: {not missing and not extra}"
      f"  missing {missing} extra {extra}")
print(f"record width {W.N_MET} = 1 index + {len(S.AXES)} axes + {len(W.METRIC_ORDER)} metrics"
      f" + {2 * len(W.YEARS)} calendar-year")

ok = ga < 5e-5 and gl < 5e-5 and not missing and not extra
print(f"\nSTEP 1 POSITIVE CONTROL: {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
