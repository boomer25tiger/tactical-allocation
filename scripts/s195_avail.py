"""Session 19.5: earliest date at which all sleeves reach full composition."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scripts.s13_backtest as bt      # noqa: E402
import scripts.s14_common as C         # noqa: E402
from src import config                 # noqa: E402

C.PRIMARY_START = pd.Timestamp("2011-10-04")
env = C.build_env(verbose=False)
cal = env["cal"]
for arm in ("synthetic", "realized"):
    p = env["panels"][arm]
    print(f"=== {arm} arm, first available session per ticker ===")
    firsts = {}
    for t, tf in sorted(p.frames.items()):
        tr = tf.tr_index.reindex(cal)
        idx = np.flatnonzero(tr.notna().to_numpy())
        firsts[t] = cal[idx[0]] if len(idx) else None
    latest = max(v for v in firsts.values() if v is not None)
    for t, v in sorted(firsts.items(), key=lambda kv: (kv[1] is None, kv[1])):
        mark = "  <== latest" if v == latest else ""
        print(f"   {t:<6} {str(v.date()) if v is not None else 'never'}{mark}")
    print(f"  all tickers available from {latest.date()}")
    print(f"  with warmup {config.WARMUP_SESSIONS} sessions, full composition at "
          f"{cal[min(len(cal)-1, int(np.searchsorted(cal.to_numpy(), np.datetime64(latest))) + config.WARMUP_SESSIONS)].date()}")
    print()
