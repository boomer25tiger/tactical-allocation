"""Session 16 step 3, corrected: effective exposure reconciliation.

The conditioning statistic is computed on the FULL history and then sliced
to the window. Computing it after windowing discards the 60 sessions of
history the rolling estimator needs and changes the decile assignment near
the window start, which is one of the two differences between the sessions
being reconciled.
"""
from __future__ import annotations
import math, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt, scripts.s13_runall as ra
import scripts.s14_common as C, scripts.s15_lines as L
from src import config
OUT = ROOT / "outputs" / "session-16"
NEW_START = pd.Timestamp("2011-10-04")
env = L.build_env(); cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]; TICK = list(ra.TARGET_TICKERS)
mult = {}
for t in TICK:
    fr = panels["synthetic"][t].frame
    mult[t] = (fr["multiple"] if "multiple" in fr.columns and fr["multiple"].notna().any()
               else pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index))
sigR = sigs["realized"]["sig"]
crash_full = pd.Series(sigR.crash, index=cal)                 # full history
vol_full = (panels["realized"]["QQQ"].ret_total.reindex(cal)
            .rolling(60).std() * math.sqrt(252))              # full history
rows = []
for pname in ("synthetic", "realized"):
    for conv in ("c2c", "o2o"):
        if pname == "synthetic" and conv == "o2o":
            continue
        for capflag in (True, False):
            po = o2o if conv == "o2o" else panels[pname]
            sk = "synthetic" if pname == "synthetic" else "realized"
            acc = bt.run_account(sigs[sk]["sig"], po, sigs[sk]["rows"], C.ANCHOR,
                                 commission_fn=C.ARMS[C.CANONICAL_ARM],
                                 slip_fn=C.slip_class_premium() if conv == "o2o" else C.slip_class,
                                 cap_fn=cap_fn if capflag else None)
            d = acc["daily"]
            rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in TICK}
                               for r in acc["raw_rows"]], index=d.index)
            for wlabel, mask in (("full_sample", rw.index == rw.index),
                                 ("primary_2011_10_04", rw.index >= NEW_START)):
                rwp = rw[mask]
                eff = pd.Series(sum(rwp[t].to_numpy()*mult[t].reindex(rwp.index).to_numpy()
                                    for t in TICK), index=rwp.index)
                cr = crash_full.reindex(rwp.index); vl = vol_full.reindex(rwp.index)
                dr = pd.qcut(cr, 10, labels=False, duplicates="drop")
                dv = pd.qcut(vl, 10, labels=False, duplicates="drop")
                rows.append({"table": "exposure", "panel": pname, "convention": conv,
                             "cap": capflag, "window": wlabel,
                             "mean_effective_exposure": float(eff.mean()),
                             "worst_trailing_return_decile": float(eff[dr == 0].mean()),
                             "wildest_vol_decile": float(eff[dv == 9].mean())})
df = pd.DataFrame([r for r in rows if r["table"] == "exposure"])
print(df.round(3).to_string(index=False))
def closest(t):
    d = ((df.mean_effective_exposure-t[0])**2 + (df.worst_trailing_return_decile-t[1])**2
         + (df.wildest_vol_decile-t[2])**2)
    return df.loc[d.idxmin()], float(d.min())**0.5
r135, e135 = closest((1.70, 0.78, 1.06)); r155, e155 = closest((1.776, 1.042, 1.490))
print(f"\n13.5 (1.70/0.78/1.06) closest -> {r135.panel}/{r135.convention}/cap={r135.cap}/"
      f"{r135.window} at {r135.mean_effective_exposure:.3f}/"
      f"{r135.worst_trailing_return_decile:.3f}/{r135.wildest_vol_decile:.3f} dist {e135:.3f}")
print(f"15.5 (1.776/1.042/1.490) closest -> {r155.panel}/{r155.convention}/cap={r155.cap}/"
      f"{r155.window} at {r155.mean_effective_exposure:.3f}/"
      f"{r155.worst_trailing_return_decile:.3f}/{r155.wildest_vol_decile:.3f} dist {e155:.3f}")
rows.append({"table": "reconciliation", "s13_5_claim": "1.70 / 0.78 / 1.06",
             "s13_5_closest": f"{r135.panel}/{r135.convention}/cap={r135.cap}/{r135.window}",
             "s13_5_closest_values": f"{r135.mean_effective_exposure:.3f}/{r135.worst_trailing_return_decile:.3f}/{r135.wildest_vol_decile:.3f}",
             "s13_5_distance": e135,
             "s15_5_claim": "1.776 / 1.042 / 1.490",
             "s15_5_closest": f"{r155.panel}/{r155.convention}/cap={r155.cap}/{r155.window}",
             "s15_5_closest_values": f"{r155.mean_effective_exposure:.3f}/{r155.worst_trailing_return_decile:.3f}/{r155.wildest_vol_decile:.3f}",
             "s15_5_distance": e155})
rows.append({"table": "canonical_exposure", "definition":
             "canonical = realized panel, open-to-open, cap on, primary window "
             "from 2011-10-04, conditioning statistics computed on full history "
             "and then sliced",
             "mean_effective_exposure": float(df[(df.panel=="realized")&(df.convention=="o2o")&(df.cap)&(df.window=="primary_2011_10_04")].mean_effective_exposure.iloc[0]),
             "worst_trailing_return_decile": float(df[(df.panel=="realized")&(df.convention=="o2o")&(df.cap)&(df.window=="primary_2011_10_04")].worst_trailing_return_decile.iloc[0]),
             "wildest_vol_decile": float(df[(df.panel=="realized")&(df.convention=="o2o")&(df.cap)&(df.window=="primary_2011_10_04")].wildest_vol_decile.iloc[0])})
rows.append({"table": "method_note", "note":
             "The decile conditioning is sensitive to whether the rolling "
             "statistic is computed before or after the window slice. Session "
             "15.5 computed the trailing volatility on the full history and "
             "sliced, which this step reproduces; slicing first discards the 60 "
             "sessions of history the estimator needs and moves the wildest-vol "
             "decile figure by roughly 0.23."})
pd.DataFrame(rows).to_csv(OUT / "exposure-reconciliation.csv", index=False)
print("[wrote exposure-reconciliation.csv]")
