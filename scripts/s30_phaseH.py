"""Session 30 phase H. Instrument attribution.

The exposure sensitivity at the end states a non-zero k for the volatility
instruments BEFORE computing and records it as illustrative rather than adopted.
Register 2.15 carries k equal to zero for them and that is unchanged.
"""
from __future__ import annotations

import csv
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
os.environ["READ_HOLDOUT_THROUGH"] = "2026-08-14"

import numpy as np                                     # noqa: E402
import pandas as pd                                    # noqa: E402
import scripts.s13_backtest as bt                      # noqa: E402
import scripts.s14_common as C                         # noqa: E402
import scripts.s22_vm as VM                            # noqa: E402

OUT = ROOT / "outputs" / "session-30"
S27 = ROOT / "outputs" / "session-27"
S28 = ROOT / "outputs" / "session-28"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
ANN = math.sqrt(252.0)
K_ILLUSTRATIVE = 1.0
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


l = [float(x) for x in subprocess.run(["sysctl", "-n", "vm.loadavg"],
     capture_output=True, text=True).stdout.strip().strip("{} ").split()]
s0 = VM.sample()
for k, v in (("load_1min", l[0]), ("compressor_gib", s0["compressor_gib"]),
             ("swap_used_mb", s0["swap_used_mb"]), ("swap_free_mb", s0["swap_free_mb"])):
    add("machine_at_phase_H", item=k, value=v)
add("preregistration", item="illustrative_k", value=K_ILLUSTRATIVE,
    note="stated before computing. Register 2.15 carries k equal to zero for the "
         "volatility instruments and that is unchanged. A value of one is the smallest "
         "non-zero choice and is used only to show how far the exposure figure moves, "
         "so it is illustrative rather than adopted")

print("building the environment")
env = C.build_env(verbose=False)
o2o, panel, syn = env["o2o"], env["panels"]["realized"], env["panels"]["synthetic"]
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
# The REALISED portfolio weights, not the lagged sleeve targets. Session 28's
# attribution and its exposure figure both read acc["raw_rows"], which carries the
# weights after the participation cap truncates and after the fill lands. Summing
# the persisted sleeve target dictionaries instead gives a different quantity, and
# the primary-window exposure it produces does not reproduce the committed
# 1.7769723457408557.
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
W = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in sorted(bt.UNLEVERED + bt.LEVERED)}
                  for r in acc["raw_rows"]], index=acc["daily"].index)
RET = pd.DataFrame({t: o2o[t].ret_total for t in TICK})
hl = pd.read_parquet(S27 / "_holdout_line_returns.parquet")
HOLD = hl.index
PRIM = W.index[(W.index >= PRIMARY) & (W.index < BOUNDARY)]
WIN = {"holdout": HOLD, "primary": PRIM}
add("setup", item="convention", value="open-to-open",
    note="the designated cell's convention, so the contributions are the ones the "
         "account realises")
add("setup", item="weights", value="realised portfolio weights",
    note="read from the account's own raw_rows, being the weights after the "
         "participation cap truncates and after the fill lands, which is what session "
         "28's attribution and its exposure figure both use")

# k equal to zero under register 2.15
mult = {}
for t in TICK:
    fr = syn[t].frame
    mult[t] = (fr["multiple"] if "multiple" in fr.columns and fr["multiple"].notna().any()
               else pd.Series(0.0 if t == "BTAL" else 1.0, index=fr.index))
K0 = sorted([t for t in TICK if float(pd.Series(mult[t]).dropna().iloc[0]) == 0.0
             or (t in ("UVXY", "SVXY", "UVIX", "SVIX", "BTAL")
                 and t not in ("UVXY", "SVXY"))])
# the register's k=0 set, being the instruments whose market-beta contribution the
# exposure figure treats as zero
K0 = sorted([t for t in TICK if t in ("UVXY", "SVXY", "UVIX", "SVIX", "BTAL")])
add("k_zero", item="instruments", value=len(K0), note=", ".join(K0) +
    ". Register 2.15 carries k equal to zero for the volatility instruments and BTAL "
    "carries no multiple at all, being an anti-beta long and short strategy")

qcol = hl["buy_hold_QQQ"]
for wname, idx in WIN.items():
    wl = W.shift(1).reindex(idx).fillna(0.0)
    R = RET.reindex(idx).fillna(0.0)
    contrib = (wl * R).sum()
    port = (wl * R).sum(axis=1)
    var_tot = float(port.var(ddof=1))
    ranked = sorted(TICK, key=lambda t: -contrib[t])
    k0_ret = float(sum(contrib[t] for t in K0))
    k0_var = 0.0
    for rk, t in enumerate(ranked, 1):
        c = float(contrib[t])
        if abs(c) < 1e-12 and float((wl[t] != 0).sum()) == 0:
            continue
        series = (wl[t] * R[t])
        # the instrument's share of portfolio variance, being its covariance with the
        # portfolio over the portfolio's variance, which sums to one across instruments
        cov = float(np.cov(series.to_numpy(), port.to_numpy(), ddof=1)[0, 1])
        share = cov / var_tot if var_tot else float("nan")
        if t in K0:
            k0_var += share
        own_vol = float(R[t].std(ddof=1) * ANN)
        corr = (float(np.corrcoef(R[t].to_numpy(),
                                  qcol.reindex(idx).fillna(0.0).to_numpy())[0, 1])
                if wname == "holdout" else "")
        add("instrument", item=t, window=wname, rank=rk, value=q(c),
            variance_share=q(share), own_ann_vol=q(own_vol),
            corr_with_buy_hold_QQQ=(q(corr) if corr != "" else ""),
            sessions_held=int((wl[t] != 0).sum()),
            k_zero=int(t in K0))
    add("summary", item="portfolio_variance", window=wname, value=q(var_tot))
    add("summary", item="k_zero_share_of_return", window=wname, value=q(k0_ret),
        note="the arithmetic contribution of the k equal to zero instruments")
    add("summary", item="k_zero_share_of_variance", window=wname, value=q(k0_var),
        note="their combined share of portfolio variance, computed as the covariance "
             "with the portfolio over the portfolio's variance")

# ---- the exposure sensitivity -----------------------------------------------------
for wname, idx in WIN.items():
    # Exposure is a LEVEL, so it reads the contemporaneous weight rather than the
    # lagged one the contributions use. Session 28 reads it the same way and this
    # reproduces its figure.
    wl = W.reindex(idx).fillna(0.0)
    base = pd.Series(sum(wl[t].to_numpy()
                         * mult[t].reindex(idx).fillna(0.0).to_numpy() for t in TICK),
                     index=idx)
    m2 = dict(mult)
    for t in ("UVXY", "SVXY"):
        reg = syn[t].frame["multiple"] if "multiple" in syn[t].frame.columns else None
        m2[t] = pd.Series(K_ILLUSTRATIVE, index=mult[t].index)
    alt = pd.Series(sum(wl[t].to_numpy() * m2[t].reindex(idx).fillna(0.0).to_numpy()
                        for t in TICK), index=idx)
    add("exposure", item="mean_at_register_k", window=wname, value=q(base.mean()),
        note="reproduces 1.7769723457408557 over the primary window at "
             "outputs/session-16/exposure-reconciliation.csv"
             if wname == "primary" else
             "against 0.9681564510351294 at outputs/session-28/holdout-decomposition.csv")
    add("exposure", item=f"mean_at_illustrative_k_{K_ILLUSTRATIVE:g}", window=wname,
        value=q(alt.mean()),
        note="the volatility instruments carried at a non-zero k. Illustrative and NOT "
             "adopted, since register 2.15 is unchanged")
    add("exposure", item="difference", window=wname, value=q(alt.mean() - base.mean()))
    if wname == "holdout":
        st = hl["STRATEGY"]
        vr = float(st.std(ddof=1) / qcol.std(ddof=1))
        add("exposure", item="realised_volatility_ratio_against_buy_hold_QQQ",
            window=wname, value=q(vr),
            note="the strategy's own realised volatility over buy-and-hold QQQ's across "
                 "the holdout, against a mean effective exposure of "
                 "0.9681564510351294. The gap between the two is what the k convention "
                 "bears on")

fn = ["table", "item", "window", "rank", "value", "variance_share", "own_ann_vol",
      "corr_with_buy_hold_QQQ", "sessions_held", "k_zero", "note"]
with open(OUT / "instrument-attribution.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote instrument-attribution.csv, {len(rows)} rows")
for r in rows:
    if r["table"] in ("summary", "exposure", "k_zero"):
        print(f"  {r['table']:10s} {r['item'][:44]:46s} {r.get('window',''):9s} "
              f"{str(r['value'])[:22]}")
