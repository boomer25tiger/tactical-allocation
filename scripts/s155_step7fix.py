"""Session 15.5 step 7, corrected: decompose the SHORT-LEG position in
isolation at T10 standalone, where the branch is the only holder.

At portfolio level rw[short] captures the instrument across every sleeve,
so SQQQ picks up T11's bull-short basket, both T11 bear terminals, and
S2's defensive state, and the arms are then not notional-matched. The
control below requires the beta components of arms B and C to agree, as
matched notional demands, and would fail on the portfolio-level series.
"""
import sys, math, pickle
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s155_arms as S   # reuses the built environment and arms
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
import scripts.s14_common as C
import scripts.s15_lines as L

OUT = S.OUT
rows = []
qqq = S.panels["realized"]["QQQ"].ret_total
for a in S.ARM_ORDER:
    short = S.ARMS[a]["short"]
    if not short:
        continue
    acc = S.ACC[(a, "realized", "o2o", "primary", "T10_standalone")]
    d = acc["daily"]
    rw = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in S.TICK}
                       for r in acc["raw_rows"]], index=d.index)
    rwp = rw[rw.index >= C.PRIMARY_START]
    w = rwp[short].shift(1)
    ri = S.panels["realized"][short].ret_total.reindex(rwp.index)
    ru = qqq.reindex(rwp.index)
    M = S.mult_of(short)
    tot = float((w * ri).sum()); beta = float((w * M * ru).sum())
    sl = (w * ri).fillna(0.0)
    port = C.window_slice(d["ret"], "primary")
    rest = port - sl
    msk = sl != 0
    rows.append({"table": "decomposition_t10_isolated", "arm": a, "short_leg": short,
                 "leverage_multiple": M, "mean_weight_when_held": float(w[w > 0].mean()),
                 "notional_frac_of_sleeve": float(w[w > 0].mean() * abs(M)),
                 "total_arith_contribution": tot, "beta_component": beta,
                 "residual_component": tot - beta,
                 "corr_short_vs_rest_of_sleeve": float(sl[msk].corr(rest[msk])),
                 "held_sessions": int((rwp[short] > 0).sum())})
df = pd.DataFrame(rows)
bB = df[df.arm == "B"].beta_component.iloc[0]
bC = df[df.arm == "C"].beta_component.iloc[0]
ctrl = abs(bB - bC) / abs(bB) < 0.02
print(f"matched-notional beta control: B {bB:.4f} vs C {bC:.4f} -> "
      f"{'PASS' if ctrl else 'FAIL'} (relative gap {abs(bB-bC)/abs(bB):.3%})")
rows.append({"table": "matched_notional_control", "arm_B_beta": bB, "arm_C_beta": bC,
             "relative_gap": abs(bB - bC) / abs(bB), "pass": bool(ctrl),
             "note": "matched notional requires equal beta components; the "
                     "portfolio-level series fails this because SQQQ is also held "
                     "by T11's bull-short basket, both T11 bear terminals, and "
                     "S2's defensive state, so the isolated T10 series is the one "
                     "that answers the instrument question"})
print(df[["arm", "short_leg", "leverage_multiple", "mean_weight_when_held",
          "notional_frac_of_sleeve", "total_arith_contribution", "beta_component",
          "residual_component", "corr_short_vs_rest_of_sleeve"]].round(4).to_string(index=False))
old = pd.read_csv(OUT / "short-leg-decomposition.csv")
old = old[old.table.isin(["diversification"])]
old["table"] = "diversification_portfolio_level"
pd.concat([pd.DataFrame(rows), old], ignore_index=True).to_csv(
    OUT / "short-leg-decomposition.csv", index=False)
print("[rewrote short-leg-decomposition.csv with the isolated decomposition]")
