"""Session 13.7a step 3 — the tracking difference test (decisive).

If the synthetic applies 0.95%/yr while the real fund's economic drag is
1.32-1.90%/yr, the synthetic must drift ABOVE the real fund by the
difference, compounding to ~4-10% over the in-window listed period. TD
definition: the geometric annualised difference fixed by session 13.7
step 8 (2.7a). Validation basis: issuer NAV for UVXY/SVXY (the funds'
close-timing class makes exchange closes noisy; NAV is the economic
path), frozen closes for TQQQ/SQQQ (baseline control).

SVXY is reported both with and without 2018-02-06, the register's stated
validation exclusion (2.12b).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt

OUT = ROOT / "outputs" / "session-13.7a"
OUT.mkdir(parents=True, exist_ok=True)
B = pd.Timestamp("2021-07-30")
rows = []


def syn_ret(t):
    f = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / f"SYN_{t}.parquet")
    f.index = pd.to_datetime(f.index).normalize()
    return f["syn_ret"].astype(float)


def nav_ret(t):
    f = pd.read_parquet(ROOT / "data" / "raw" / "nav" / f"{t}_nav.parquet")
    s = f.set_index(pd.to_datetime(f["date"]).dt.normalize())["nav"].astype(float)
    s = s[~s.index.duplicated(keep="last")]
    return s.pct_change()


def close_ret(t):
    return bt.build_ticker_frame(t, bt._load_raw(t)).ret_total


def td_stats(s, r, label, exclude=None):
    j = pd.DataFrame({"s": s, "r": r}).dropna().loc[:B]
    if exclude is not None:
        j = j.drop(index=[d for d in exclude if d in j.index])
    n = len(j)
    ann_s = (1 + j["s"]).prod() ** (252 / n) - 1
    ann_r = (1 + j["r"]).prod() ** (252 / n) - 1
    cum_s = float((1 + j["s"]).prod() - 1)
    cum_r = float((1 + j["r"]).prod() - 1)
    cs = (1 + j["s"]).rolling(252).apply(np.prod, raw=True)
    cr = (1 + j["r"]).rolling(252).apply(np.prod, raw=True)
    mx = float((cs / cr - 1).abs().max())
    ratio_drift = ((1 + cum_s) / (1 + cum_r)) ** (252 / n) - 1
    out = {"pair": label, "n": n,
           "window": f"{j.index.min().date()}..{j.index.max().date()}",
           "ann_td_pct_27a_definition": (ann_s - ann_r) * 100,
           "ann_ratio_drift_pct": ratio_drift * 100,
           "cumulative_divergence_pct": ((1 + cum_s) / (1 + cum_r) - 1) * 100,
           "max_roll252_div": mx,
           "drift_sign": "synthetic ABOVE real" if cum_s > cum_r else "synthetic BELOW real"}
    yearly = []
    for y, g in j.groupby(j.index.year):
        ys = float((1 + g["s"]).prod() - 1)
        yr = float((1 + g["r"]).prod() - 1)
        yearly.append({"pair": label, "year": int(y),
                       "yearly_td_pct": ((1 + ys) / (1 + yr) - 1) * 100})
    return out, yearly


PAIRS = [
    ("UVXY", syn_ret("UVXY"), nav_ret("UVXY"), "UVXY syn vs issuer NAV", None),
    ("SVXY_incl", syn_ret("SVXY"), nav_ret("SVXY"),
     "SVXY syn vs issuer NAV (incl 2018-02-06)", None),
    ("SVXY_excl", syn_ret("SVXY"), nav_ret("SVXY"),
     "SVXY syn vs issuer NAV (excl 2018-02-06 per 2.12b)",
     [pd.Timestamp("2018-02-06")]),
    ("TQQQ", syn_ret("TQQQ"), close_ret("TQQQ"), "TQQQ syn vs real close (0.95 confirmed baseline)", None),
    ("SQQQ", syn_ret("SQQQ"), close_ret("SQQQ"), "SQQQ syn vs real close (0.95 confirmed baseline)", None),
]
print("== tracking differences, in-window listed periods ==")
for key, s, r, label, excl in PAIRS:
    out, yearly = td_stats(s, r, label, excl)
    rows.append({"table": "headline", **out})
    rows += [{"table": "by_year", **y} for y in yearly]
    print(f"  {label}: ratio drift {out['ann_ratio_drift_pct']:+.2f}%/yr "
          f"(2.7a diff {out['ann_td_pct_27a_definition']:+.2f}), cumulative "
          f"{out['cumulative_divergence_pct']:+.2f}%, {out['drift_sign']} ({out['n']} d)")

# Second positive control: deliberately mis-specified UVXY at 1.90% ER.
# First run exposed that the 2.7a difference metric CANNOT detect the
# effect on a steeply declining fund (shift −0.148 pp: sensitivity scales
# by (1+ann_return) ≈ 0.15 at −85%/yr) — the control did its job. The
# verdict metric is therefore the annualised RATIO drift, whose
# sensitivity is the full expense delta; both metrics are reported.
mis = syn_ret("UVXY") - (1.90 - 0.95) / 100.0 / 252.0
out_base, _ = td_stats(syn_ret("UVXY"), nav_ret("UVXY"), "base")
out_mis, _ = td_stats(mis, nav_ret("UVXY"), "UVXY mis-specified at 1.90% ER vs issuer NAV")
shift_diff = out_mis["ann_td_pct_27a_definition"] - out_base["ann_td_pct_27a_definition"]
shift_ratio = out_mis["ann_ratio_drift_pct"] - out_base["ann_ratio_drift_pct"]
rows.append({"table": "misspec_control", **out_mis,
             "shift_27a_diff_pp": shift_diff, "shift_ratio_pp": shift_ratio,
             "expected_shift_pp": -0.95,
             "note": "2.7a difference metric insensitive on declining funds "
                     "(control finding); ratio drift is the verdict metric"})
print(f"  mis-specified control: ratio-drift shifts {shift_ratio:+.3f} pp "
      f"(expected ~-0.95); 2.7a-diff shifts {shift_diff:+.3f} pp (insensitive)")
assert abs(shift_ratio + 0.95) < 0.05, "control failed: test cannot detect the effect"

# verdict on the ratio-drift metric
hl = [r for r in rows if r["table"] == "headline"]
def get(pat):
    return [r for r in hl if pat in r.get("pair", "")][0]["ann_ratio_drift_pct"]
uvxy_d = get("UVXY syn vs issuer NAV")
svxy_d = get("excl 2018-02-06")
base_d = [r["ann_ratio_drift_pct"] for r in hl if "baseline" in r.get("pair", "")]
verdict = (
    "DEFINITIONAL ARTIFACT for the fund that carried the finding. UVXY — "
    "18.5% of dollar exposure, the dominant term of 13.7's 0.22-0.28 pp/yr "
    f"claim — drifts {uvxy_d:+.2f}%/yr BELOW issuer NAV: the opposite "
    "direction of a 0.87-0.95 pp/yr understated expense, and inside the "
    f"TQQQ/SQQQ baseline noise band ({base_d[0]:+.2f}/{base_d[1]:+.2f}%/yr). "
    "The 0.95 constant reproduces the fund's economic path; the 1.82-1.90 "
    "filing ratios (brokerage-commission-inclusive) measure costs already "
    "embedded in the NAV the construction was validated against, and "
    "applying them would double-count. SVXY (4.0% of exposure) drifts "
    f"{svxy_d:+.2f}%/yr ABOVE NAV excluding the 2.12b termination day — a "
    "drift LARGER than its 0.37-0.58 pp filing gap and sitting inside the "
    "already-recorded SVXY residual class; not cleanly attributable to "
    "expenses. The 13.7 direction confirmation does not survive.")
rows.append({"table": "VERDICT", "note": verdict})
print("\nVERDICT:", verdict[:200], "...")

pd.DataFrame(rows).to_csv(OUT / "tracking-verdict.csv", index=False)
print(f"[wrote tracking-verdict.csv: {len(rows)} rows]")
