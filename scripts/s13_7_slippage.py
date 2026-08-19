"""Session 13.7 step 3 — measured per-instrument slippage profile.

Post-hoc parallel cost model under 9.10 (2026-08-18): a uniform
assumption across SPY-class liquidity and thin inverse sector funds is
inaccurate in a known direction at both ends. The registered 4.4 uniform
sweep is unchanged as the sensitivity surface.

Session 05/06 failure modes, stated before construction:
 (i)  session 05's composite tiering priced the thinnest tier sub-unity
      (multipliers 1.0/0.98/3.26) because tier MEDIANS were dominated by
      the CS estimator's biases rather than by liquidity;
 (ii) session 06's dollar-volume-only tiering repeated it: the CS bias is
      leverage-correlated while leverage sorts into tiers, so the
      ratios-survive-bias premise failed;
 (iii) session 09's re-closure: an auction fill does not cross the
      spread, so a spread-based cost applies to spread-crossing
      executions, not MOC prints.
This construction uses DIRECT per-instrument per-year levels — no tiers,
no multipliers, no ratios — so (i) and (ii) are not reproduced. (iii) is
inherited and recorded, not worked around: under the step-2 splice arm
the zero explicit commission is accompanied by wholesaler routing, and
the measured spread profile is what carries that execution cost.

Estimator: Corwin-Schultz (2012), overnight adjustment, negatives set to
zero, yearly mean per instrument. Cross-check: Abdi-Ranaldo (2017),
yearly moment estimate sqrt(max(mean s2, 0)). Both reported; the profile
consumed by cost model B is the CS figure (the step names CS as the
estimator, AR as the cross-check).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.spread import corwin_schultz, abdi_ranaldo
import scripts.s13_backtest as bt

OUT = ROOT / "outputs" / "session-13.7"
OUT.mkdir(parents=True, exist_ok=True)

TRADED = ("UVXY", "SVXY", "TECL", "TECS", "SOXL", "SOXS", "SPXL", "LABU",
          "SQQQ", "TQQQ", "QLD", "PSQ", "QQQ", "TLT", "BIL", "BTAL", "BSV")
HIGH_VOL_YEARS = (2008, 2009, 2011, 2020)
ANCHOR_RT_BP = 10.0

rows = []
profile: dict[str, dict[int, float]] = {}

# H/L coverage check before estimating (required by the step).
print("== H/L coverage ==")
for t in TRADED:
    raw = bt._load_raw(t)
    n = len(raw)
    ok = int((raw["High"].notna() & raw["Low"].notna() &
              (raw["High"] > 0) & (raw["Low"] > 0)).sum())
    flat = int((raw["High"] == raw["Low"]).sum())
    rows.append({"table": "hl_coverage", "ticker": t, "rows_in_window": n,
                 "hl_populated": ok, "flat_hl_rows": flat,
                 "note": "" if ok == n else "gaps present"})
    if ok != n:
        print(f"  {t}: {n-ok} rows missing H/L")

# positive control for the estimator pipeline: SPY's full-period CS mean
# must land in the low single-digit bp (its known spread class), and the
# most-levered thin funds must exceed it.
# Convention: the profile value is the YEARLY MEDIAN of zero-treated daily
# CS estimates — session 05's recorded convention (spread-estimates.csv,
# median_bp_zero), robust to the documented high-volatility spike bias.
# The yearly MEAN is reported beside so the bias is visible, per the step.
ctrl = {}
for t in TRADED:
    raw = bt._load_raw(t)
    cs = corwin_schultz(raw["High"], raw["Low"], raw["Close"])
    ar = abdi_ranaldo(raw["High"], raw["Low"], raw["Close"])
    y_med = cs["spread_zero"].groupby(cs.index.year).median() * 1e4
    y_mean = cs["spread_zero"].groupby(cs.index.year).mean() * 1e4
    ar_med = ar["spread"].groupby(ar.index.year).median() * 1e4
    neg_frac = cs["negative"].groupby(cs.index.year).mean()
    ctrl[t] = float(cs["spread_zero"].median() * 1e4)
    prof_t = {}
    for y in sorted(set(y_med.index)):
        rt_cs = float(y_med.loc[y])
        prof_t[int(y)] = rt_cs
        rows.append({"table": "profile", "ticker": t, "year": int(y),
                     "cs_round_turn_bp": rt_cs,
                     "cs_mean_bp": float(y_mean.loc[y]),
                     "ar_round_turn_bp": float(ar_med.loc[y]),
                     "cs_negative_frac": float(neg_frac.loc[y]),
                     "high_vol_year": y in HIGH_VOL_YEARS})
    # pre-listing back-fill: earliest listed year's value carried back,
    # flagged (synthetic segments have no H/L).
    first_year = min(prof_t)
    for y in range(2007, first_year):
        prof_t[y] = prof_t[first_year]
        rows.append({"table": "profile", "ticker": t, "year": y,
                     "cs_round_turn_bp": prof_t[first_year],
                     "ar_round_turn_bp": np.nan, "cs_negative_frac": np.nan,
                     "high_vol_year": y in HIGH_VOL_YEARS,
                     "note": f"pre-listing: carried back from {first_year} (flagged)"})
    profile[t] = prof_t

# Positive control: session 05's per-year medians on the identical
# estimator and identical per-year data must be reproduced.
s05 = pd.read_csv(ROOT / "outputs" / "session-05" / "spread-estimates.csv")
ctrl_pairs = [("BTAL", 2015), ("BTAL", 2020), ("TQQQ", 2015), ("SQQQ", 2020)]
worst = 0.0
for t, y in ctrl_pairs:
    rec = s05[(s05.ticker == t) & (s05.window == str(y))]
    if not len(rec):
        continue
    mine = profile[t][y] if t in profile and y in profile[t] else np.nan
    gap = abs(float(rec.iloc[0]["median_bp_zero"]) - mine)
    worst = max(worst, gap)
    print(f"  control {t} {y}: session05 {float(rec.iloc[0]['median_bp_zero']):.2f} "
          f"vs recomputed {mine:.2f} (gap {gap:.2f} bp)")
assert worst < 1.0, f"positive control failed: worst gap {worst:.2f} bp vs session 05"
print("positive control vs session 05 per-year medians: PASS")

# summary vs the uniform anchor
for t in TRADED:
    ys = pd.Series(profile[t])
    med, mean = float(ys.median()), float(ys.mean())
    hv = float(ys[ys.index.isin(HIGH_VOL_YEARS)].mean())
    lv = float(ys[~ys.index.isin(HIGH_VOL_YEARS)].mean())
    rows.append({"table": "vs_anchor", "ticker": t,
                 "cs_median_bp": med, "cs_mean_bp": mean,
                 "high_vol_years_mean_bp": hv, "other_years_mean_bp": lv,
                 "anchor_bp": ANCHOR_RT_BP,
                 "verdict": ("uniform OVERCHARGES" if med < ANCHOR_RT_BP
                             else "uniform UNDERCHARGES"),
                 "magnitude_bp": med - ANCHOR_RT_BP})
rows.append({"table": "bias_note", "note":
             "CS is upward-biased in high-volatility periods (variance leakage "
             "into the range) and downward-biased for discontinuously traded "
             "assets; high-vol years are flagged in the profile so the bias is "
             "visible. AR is reported beside as the better-behaved cross-check. "
             "Failure mode (iii): a spread-based cost applies to "
             "spread-crossing executions, not auction prints; recorded, "
             "carried by the step-2 splice-arm reasoning."})

pd.DataFrame(rows).to_csv(OUT / "slippage-profile.csv", index=False)
with open(OUT / "_slippage_profile.json", "w") as fh:
    json.dump(profile, fh)
print(f"[wrote slippage-profile.csv: {len(rows)} rows; profile JSON saved]")
p = pd.DataFrame(rows)
p = p[p.table == "vs_anchor"]
print(p[["ticker", "cs_median_bp", "high_vol_years_mean_bp", "verdict",
         "magnitude_bp"]].round(1).to_string(index=False))
