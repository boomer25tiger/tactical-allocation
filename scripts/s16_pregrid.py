"""Session 16 steps 1, 3, 4: boundary correction, exposure reconciliation,
leave-one-year-out robustness."""
from __future__ import annotations
import math, sys, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
import scripts.s14_common as C
import scripts.s15_lines as L
from src import config
from src.portfolio import SLEEVE_ORDER

OUT = ROOT / "outputs" / "session-16"; OUT.mkdir(parents=True, exist_ok=True)
OLD_START = pd.Timestamp("2011-10-03")
NEW_START = pd.Timestamp("2011-10-04")

env = L.build_env()
cal, sigs, panels, o2o = env["cal"], env["sigs"], env["panels"], env["o2o"]
cap_fn = env["cap_fn"]; TICK = list(ra.TARGET_TICKERS)

def run(conv, cap=True, panel_override=None, rows=None, sigkey="realized"):
    panel = panel_override if panel_override is not None else (
        o2o if conv == "o2o" else panels["realized" if sigkey == "realized" else sigkey])
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    return bt.run_account(sigs[sigkey]["sig"], panel,
                          rows if rows is not None else sigs[sigkey]["rows"],
                          C.ANCHOR, commission_fn=C.ARMS[C.CANONICAL_ARM],
                          slip_fn=sf, cap_fn=cap_fn if cap else None)

def win(s, start): return s[s.index >= start]

# ===========================================================================
print("== STEP 1: 7.14 boundary moved to 2011-10-04 ==")
rows1 = []
for conv in ("c2c", "o2o"):
    acc = run(conv)
    uf = acc["unavailable_fills"]
    if len(uf):
        uf = uf.copy(); uf["date"] = pd.to_datetime(uf["date"])
        old_n = int((uf["date"] >= OLD_START).sum())
        new_n = int((uf["date"] >= NEW_START).sum())
        det = uf[uf["date"] >= OLD_START]
    else:
        old_n = new_n = 0; det = uf
    rows1.append({"table": "boundary_fills", "convention": conv,
                  "unavailable_fills_from_2011_10_03": old_n,
                  "unavailable_fills_from_2011_10_04": new_n,
                  "instruments": ";".join(sorted(det["ticker"].unique())) if len(det) else "",
                  "dates": ";".join(str(pd.Timestamp(d).date()) for d in det["date"]) if len(det) else ""})
    print(f"  [{conv}] fills from 2011-10-03: {old_n}; from 2011-10-04: {new_n}")
    m_old = L.standalone_metrics(win(acc["daily"]["ret"], OLD_START), acc["daily"]["nav"], acc["orders"])
    m_new = L.standalone_metrics(win(acc["daily"]["ret"], NEW_START), acc["daily"]["nav"], acc["orders"])
    rows1.append({"table": "canonical", "convention": conv,
                  "old_start_ann": m_old["ann_return"], "old_start_sharpe_lo": m_old["sharpe_lo"],
                  "new_start_ann": m_new["ann_return"], "new_start_sharpe_lo": m_new["sharpe_lo"],
                  "d_ann": m_new["ann_return"] - m_old["ann_return"],
                  "d_sharpe_lo": m_new["sharpe_lo"] - m_old["sharpe_lo"]})
    print(f"  [{conv}] {m_old['ann_return']:.4f}/{m_old['sharpe_lo']:.4f} -> "
          f"{m_new['ann_return']:.4f}/{m_new['sharpe_lo']:.4f}")
tot_new = sum(r.get("unavailable_fills_from_2011_10_04", 0) for r in rows1 if r["table"] == "boundary_fills")
rows1.append({"table": "halt_check", "remaining_unavailable_fills_on_corrected_boundary": tot_new,
              "result": "PASS" if tot_new == 0 else "FAIL"})
assert tot_new == 0, "corrected boundary still carries an unavailable fill"
# session 15 predicted values
pred = {"o2o": (0.5218, 1.3817), "c2c": (0.2962, 0.9251)}
for conv, (pa, ps) in pred.items():
    r = [x for x in rows1 if x["table"] == "canonical" and x["convention"] == conv][0]
    rows1.append({"table": "reproduction_vs_session15", "convention": conv,
                  "s15_predicted_ann": pa, "measured_ann": r["new_start_ann"],
                  "d_ann": r["new_start_ann"] - pa,
                  "s15_predicted_sharpe_lo": ps, "measured_sharpe_lo": r["new_start_sharpe_lo"],
                  "d_sharpe_lo": r["new_start_sharpe_lo"] - ps,
                  "match_4dp": bool(abs(r["new_start_ann"] - pa) < 5e-5 and
                                    abs(r["new_start_sharpe_lo"] - ps) < 5e-5)})
pd.DataFrame(rows1).to_csv(OUT / "boundary-correction.csv", index=False)
print(f"  halt check: {tot_new} remaining unavailable fills -> PASS")

# ===========================================================================
print("\n== STEP 3: effective exposure reconciliation ==")
rows3 = []
mult = {}
for t in TICK:
    fr = panels["synthetic"][t].frame
    mult[t] = (fr["multiple"] if "multiple" in fr.columns and fr["multiple"].notna().any()
               else pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index))
sig = sigs["realized"]["sig"]
crash = pd.Series(sig.crash, index=cal)
qqq_r = panels["realized"]["QQQ"].ret_total
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
            for wlabel, wstart in (("primary_2011_10_04", NEW_START),):
                rwp = rw[rw.index >= wstart]
                eff = pd.Series(sum(rwp[t].to_numpy() * mult[t].reindex(rwp.index).to_numpy()
                                    for t in TICK), index=rwp.index)
                cr = crash.reindex(rwp.index); vol = qqq_r.reindex(rwp.index).rolling(60).std()*math.sqrt(252)
                dr = pd.qcut(cr, 10, labels=False, duplicates="drop")
                dv = pd.qcut(vol, 10, labels=False, duplicates="drop")
                rows3.append({"table": "exposure", "panel": pname, "convention": conv,
                              "cap": capflag, "window": wlabel,
                              "mean_effective_exposure": float(eff.mean()),
                              "worst_trailing_return_decile": float(eff[dr == 0].mean()),
                              "wildest_vol_decile": float(eff[dv == 9].mean())})
                print(f"  [{pname} {conv} cap={capflag}] mean {eff.mean():.3f} "
                      f"worst-ret {eff[dr==0].mean():.3f} wildest-vol {eff[dv==9].mean():.3f}")
df3 = pd.DataFrame([r for r in rows3 if r["table"] == "exposure"])
def closest(target):
    d = ((df3.mean_effective_exposure - target[0])**2 +
         (df3.worst_trailing_return_decile - target[1])**2 +
         (df3.wildest_vol_decile - target[2])**2)
    return df3.loc[d.idxmin()], float(d.min())**0.5
r135, e135 = closest((1.70, 0.78, 1.06))
r155, e155 = closest((1.776, 1.042, 1.490))
rows3.append({"table": "reconciliation",
              "s13_5_claim": "1.70 / 0.78 / 1.06",
              "s13_5_closest_combination": f"{r135.panel} {r135.convention} cap={r135.cap}",
              "s13_5_closest_values": f"{r135.mean_effective_exposure:.3f} / "
                                      f"{r135.worst_trailing_return_decile:.3f} / "
                                      f"{r135.wildest_vol_decile:.3f}",
              "s13_5_distance": e135,
              "s15_5_claim": "1.776 / 1.042 / 1.490",
              "s15_5_closest_combination": f"{r155.panel} {r155.convention} cap={r155.cap}",
              "s15_5_closest_values": f"{r155.mean_effective_exposure:.3f} / "
                                      f"{r155.worst_trailing_return_decile:.3f} / "
                                      f"{r155.wildest_vol_decile:.3f}",
              "s15_5_distance": e155,
              "note": "session 13.5 measured on the pre-repair synthetic panel over "
                      "the FULL sample with no cap and before the SOXS split patch, "
                      "the expense corrections and the boundary move; session 15.5 "
                      "measured on the realized open-to-open panel over the primary "
                      "window with the cap. The two are not the same quantity."})
pd.DataFrame(rows3).to_csv(OUT / "exposure-reconciliation.csv", index=False)
print(f"  13.5 claim closest to {r135.panel}/{r135.convention}/cap={r135.cap} (dist {e135:.3f})")
print(f"  15.5 claim closest to {r155.panel}/{r155.convention}/cap={r155.cap} (dist {e155:.3f})")
