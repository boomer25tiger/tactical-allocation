"""Session 06: tier reassignment v2 and structural branch-condition counts.

Counts how often branch conditions hold and co-occur. Conditions are
evaluated directly on indicator series with the study's 1.9 semantics
(threshold test with unavailable input reads false); NO sleeve function is
called, no weight is formed, and nothing here reports what any branch would
have returned as a weight. Ticker identities of branch routes are counts of
routing, not positions.

Windows: the union trading calendar of the panel (SPY's sessions). Where a
step needs a specific gate series, the evaluable window is stated in the
output.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src import config
from src.data import build_ticker_frame
from src.indicators import sma, wilder_rsi

OUT = ROOT / "outputs" / "session-06"
OUT.mkdir(parents=True, exist_ok=True)

CASCADE = list(("QQQE", "VTV", "VOX", "TECL", "VOOG", "VOOV", "XLP",
                "TQQQ", "XLY", "FAS", "SPY"))
T10_DIPS = ["TQQQ", "SOXL", "SPXL", "LABU"]
T11_PANEL = ["SPY", "IOO", "TQQQ", "VTV", "XLF"]
NEEDED = sorted(set(CASCADE + T10_DIPS + T11_PANEL +
                    ["QQQ", "SMH", "TLT", "PSQ", "AGG", "SH", "IEF", "BND"]))
PERIODS = [7, 14, 28]

# ---------------------------------------------------------------------------
# Load and precompute
# ---------------------------------------------------------------------------

frames = {t: build_ticker_frame(t, pd.read_parquet(
    ROOT / "data" / "raw" / "etf" / f"{t}.parquet")) for t in NEEDED}
CAL = frames["SPY"].index
print(f"calendar: {len(CAL):,} sessions {CAL.min().date()} -> {CAL.max().date()}")

TR = {t: frames[t].tr_index.reindex(CAL) for t in NEEDED}
RSI = {(t, n): wilder_rsi(TR[t].dropna(), n).reindex(CAL)
       for t in NEEDED for n in PERIODS}
SMA200 = {t: sma(TR[t].dropna(), config.SMA_LONG).reindex(CAL)
          for t in ["SPY", "QQQ", "SMH", "SOXL", "TQQQ"]}
SMA20_TQQQ = sma(TR["TQQQ"].dropna(), config.SMA_SHORT).reindex(CAL)
QQQ_R60 = ((TR["QQQ"] / TR["QQQ"].shift(config.CRASH_HORIZON_SESSIONS) - 1.0)
           * 100.0)

def gt(series, bound):
    """Threshold test, 1.9: unavailable reads false."""
    return series.notna() & (series > bound)

def lt(series, bound):
    return series.notna() & (series < bound)

def above(px, ma):
    return px.notna() & ma.notna() & (px > ma)

def episodes(mask: np.ndarray) -> list[tuple[int, int]]:
    out, i, n = [], 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out.append((i, j)); i = j + 1
        else:
            i += 1
    return out

# ---- POSITIVE CONTROLS ----------------------------------------------------
assert episodes(np.array([0, 1, 1, 0, 1], bool)) == [(1, 2), (4, 4)]
_spy70 = gt(RSI[("SPY", 14)], 70)
assert _spy70.sum() > 0, "CONTROL FAILED: SPY RSI14>70 never true on history"
print(f"CONTROLS PASSED: episode counter; SPY RSI14>70 holds on "
      f"{int(_spy70.sum())} sessions (known-present condition)\n")

# ===========================================================================
# Step 1: tier reassignment v2 from session 05 measurements
# ===========================================================================

dv = pd.read_csv(ROOT / "outputs" / "session-05" / "dollar-volume.csv")
sp = pd.read_csv(ROOT / "outputs" / "session-05" / "spread-estimates.csv")
dv_full = dv[dv.window == "full"].set_index("ticker")["median_dollar_volume"]
sp_full = sp[sp.window == "full"].set_index("ticker")[
    ["median_bp_zero", "median_bp_exclude"]]

EXCLUDED = {
    "RYMFX": "excluded from tiering: never held (signal input only, 2.5), "
             "takes no slippage; no volume and no intraday range",
    "SOXS": "volume record unusable (zero volume stored on 57.7% of "
            "sessions from reverse-split integer rounding); assigned "
            "directly to the thinnest tier",
    "TECS": "volume record unusable (zero volume on 28.6% of sessions); "
            "assigned directly to the thinnest tier",
}
ranked = dv_full.drop(index=["RYMFX", "SOXS", "TECS"]).sort_values(
    ascending=False)
assert len(ranked) == 33
tiers = pd.Series(index=ranked.index, dtype=int)
tiers.iloc[:11], tiers.iloc[11:22], tiers.iloc[22:] = 1, 2, 3

rows = []
for t in dv_full.index:
    if t == "RYMFX":
        tier = None
    elif t in ("SOXS", "TECS"):
        tier = 3
    else:
        tier = int(tiers.loc[t])
    rows.append(dict(
        ticker=t, median_dollar_volume=dv_full.loc[t], tier=tier,
        spread_bp_zero=sp_full.loc[t, "median_bp_zero"],
        spread_bp_exclude=sp_full.loc[t, "median_bp_exclude"],
        exclusion_flag=EXCLUDED.get(t, ""),
    ))
tier_v2 = pd.DataFrame(rows).sort_values(
    ["tier", "median_dollar_volume"], ascending=[True, False], na_position="last")
tier_v2.to_csv(OUT / "tier-assignment-v2.csv", index=False)

b1 = ranked.iloc[10], ranked.iloc[11]   # tier1/tier2 boundary straddle
b2 = ranked.iloc[21], ranked.iloc[22]
print("=== STEP 1: tiers by median dollar volume alone (33 names) ===")
for k in (1, 2, 3):
    names = tiers[tiers == k].index.tolist()
    if k == 3:
        names += ["SOXS*", "TECS*"]
    print(f"  tier {k}: {names}")
print(f"  boundaries: tier1/2 between ${b1[0]:,.0f} and ${b1[1]:,.0f}; "
      f"tier2/3 between ${b2[0]:,.0f} and ${b2[1]:,.0f}")

mult = {}
for treat in ("zero", "exclude"):
    col = f"spread_bp_{treat}"
    med = tier_v2[tier_v2.tier.notna()].groupby("tier")[col].median()
    mult[treat] = med / med.loc[1]
    print(f"\n  {treat}-treatment tier median spreads bp: "
          f"{med.round(2).to_dict()}")
    print(f"  multipliers unrounded: "
          f"{(med / med.loc[1]).round(4).to_dict()}   rounded: "
          f"{(med / med.loc[1]).round(1).to_dict()}")

t12_close = all(abs(mult[tr].loc[2] - 1.0) <= 0.20 for tr in mult)
print(f"\n  tier1 vs tier2 within 20% under both treatments: {t12_close}")
if t12_close:
    two = tier_v2[tier_v2.tier.notna()].copy()
    two["tier2way"] = np.where(two.tier <= 2, 1, 2)
    for treat in ("zero", "exclude"):
        med2 = two.groupby("tier2way")[f"spread_bp_{treat}"].median()
        print(f"  TWO-TIER {treat}: medians {med2.round(2).to_dict()} "
              f"multiplier {(med2 / med2.loc[1]).round(4).to_dict()} "
              f"rounded {(med2 / med2.loc[1]).round(1).to_dict()}")

# ===========================================================================
# Step 2: T10 cascade co-occurrence
# ===========================================================================

GRID = [(14, 30), (7, 20), (7, 40), (28, 20), (28, 40)]
s2_rows = []
print("\n=== STEP 2: T10 oversold co-occurrence ===")
for n, os_thr in GRID:
    overbought = pd.Series(False, index=CAL)
    for t in CASCADE:
        overbought |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_1)
    dips = pd.DataFrame({t: lt(RSI[(t, n)], os_thr) for t in T10_DIPS})
    k = dips.sum(axis=1)

    for scope, mask in (("all", pd.Series(True, index=CAL)),
                        ("not_overbought", ~overbought)):
        denom = int(mask.sum())
        dist = {c: int(((k == c) & mask).sum()) for c in range(5)}
        for c, s in dist.items():
            s2_rows.append(dict(rsi_period=n, oversold=os_thr, scope=scope,
                                measure=f"count_{c}", sessions=s,
                                fraction=s / denom))
        multi = int(((k >= 2) & mask).sum())
        s2_rows.append(dict(rsi_period=n, oversold=os_thr, scope=scope,
                            measure="count_2plus", sessions=multi,
                            fraction=multi / denom))

    # pair matrix (unconditional joint-hold sessions; diagonal = solo total)
    for i, a in enumerate(T10_DIPS):
        for j, b in enumerate(T10_DIPS):
            joint = int((dips[a] & dips[b]).sum())
            s2_rows.append(dict(rsi_period=n, oversold=os_thr, scope="all",
                                measure=f"pair_{a}&{b}", sessions=joint,
                                fraction=joint / len(CAL)))

    # reach rates: step k evaluated iff every prior step false
    reach = pd.Series(True, index=CAL)
    names = ["overbought"] + T10_DIPS + ["trend_switcher"]
    conds = [overbought] + [dips[t] for t in T10_DIPS] + [None]
    for name, cond in zip(names, conds):
        r = int(reach.sum())
        s2_rows.append(dict(rsi_period=n, oversold=os_thr, scope="all",
                            measure=f"reach_{name}", sessions=r,
                            fraction=r / len(CAL)))
        if cond is not None:
            reach = reach & ~cond
    if (n, os_thr) == (14, 30):
        canon = {r["measure"]: r for r in s2_rows
                 if r["rsi_period"] == 14 and r["oversold"] == 30}
        print("  canonical (14, 30):")
        for c in range(5):
            a = canon[f"count_{c}"]
            print(f"    {c} dips hold: {a['sessions']:5d} sessions "
                  f"({a['fraction']:.4%})")
pd.DataFrame(s2_rows).to_csv(OUT / "t10-cascade-cooccurrence.csv", index=False)

canon2 = [r for r in s2_rows if r["rsi_period"] == 14 and r["oversold"] == 30]
print("  conditional on not-overbought, 2+ dips: " + str(
    [f"{r['sessions']} ({r['fraction']:.4%})" for r in canon2
     if r["scope"] == "not_overbought" and r["measure"] == "count_2plus"][0]))
print("  reach rates:", {r["measure"].replace("reach_", ""):
      f"{r['fraction']:.2%}" for r in canon2 if r["measure"].startswith("reach")})

# ===========================================================================
# Step 3: dip ladders in the other three sleeves
# ===========================================================================

print("\n=== STEP 3: dip-ladder pairs (source-verified) ===")
s3_rows = []
for n, os_thr in GRID:
    # T11: pair (TQQQ, SPY->SPXL); reached iff tier-1 overbought not fired
    t11_ob = pd.Series(False, index=CAL)
    for t in T11_PANEL:
        t11_ob |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_1)
    t11_reach = ~t11_ob
    a, b = lt(RSI[("TQQQ", n)], os_thr), lt(RSI[("SPY", n)], os_thr)
    both = a & b
    s3_rows.append(dict(rsi_period=n, oversold=os_thr, sleeve="T11",
                        pair="TQQQ&SPY", sessions_both=int(both.sum()),
                        frac_all=float(both.mean()),
                        sessions_reached=int(t11_reach.sum()),
                        both_and_reached=int((both & t11_reach).sum()),
                        frac_of_reached=float((both & t11_reach).sum()
                                              / max(t11_reach.sum(), 1))))
    # S2: pair (TQQQ->TECL, SOXL); reached iff NOT TQQQ above SMA200
    s2_reach = ~above(TR["TQQQ"], SMA200["TQQQ"])
    a, b = lt(RSI[("TQQQ", n)], os_thr), lt(RSI[("SOXL", n)], os_thr)
    both = a & b
    s3_rows.append(dict(rsi_period=n, oversold=os_thr, sleeve="S2",
                        pair="TQQQ&SOXL", sessions_both=int(both.sum()),
                        frac_all=float(both.mean()),
                        sessions_reached=int(s2_reach.sum()),
                        both_and_reached=int((both & s2_reach).sum()),
                        frac_of_reached=float((both & s2_reach).sum()
                                              / max(s2_reach.sum(), 1))))
    # S3: disjunction (QQQ, SMH) -> same target; reached iff bear (votes<3)
    votes = sum(above(TR[t], SMA200[t]).astype(int)
                for t in ["SPY", "QQQ", "SMH", "SOXL"])
    s3_reach = votes < 3
    a, b = lt(RSI[("QQQ", n)], os_thr), lt(RSI[("SMH", n)], os_thr)
    both = a & b
    s3_rows.append(dict(rsi_period=n, oversold=os_thr, sleeve="S3",
                        pair="QQQ&SMH", sessions_both=int(both.sum()),
                        frac_all=float(both.mean()),
                        sessions_reached=int(s3_reach.sum()),
                        both_and_reached=int((both & s3_reach).sum()),
                        frac_of_reached=float((both & s3_reach).sum()
                                              / max(s3_reach.sum(), 1))))
s3_df = pd.DataFrame(s3_rows)
s3_df.to_csv(OUT / "dip-ladder-cooccurrence.csv", index=False)
print(s3_df[s3_df.rsi_period == 14][["sleeve", "pair", "sessions_both",
      "frac_all", "both_and_reached", "frac_of_reached"]]
      .round(5).to_string(index=False))

# ===========================================================================
# Step 4: T11 bear sub-model agreement
# ===========================================================================

print("\n=== STEP 4: T11 bear sub-model agreement ===")
n = 14
t11_ob = pd.Series(False, index=CAL)
for t in T11_PANEL:
    t11_ob |= gt(RSI[(t, n)], config.OVERBOUGHT_TIER_1)
dip_t = lt(RSI[("TQQQ", n)], config.OVERSOLD)
dip_s = lt(RSI[("SPY", n)], config.OVERSOLD)
spy_above = above(TR["SPY"], SMA200["SPY"])
sma_ok = SMA200["SPY"].notna()
bear = sma_ok & ~spy_above & ~t11_ob & ~dip_t & ~dip_s

crash = QQQ_R60.notna() & (QQQ_R60 < config.CRASH_THRESHOLD_PCT)
tqqq_above20 = above(TR["TQQQ"], SMA20_TQQQ)
psq_dip = lt(RSI[("PSQ", n)], config.OVERSOLD)

def pairwise(a_key, b_key):
    a, b = RSI[(a_key, n)], RSI[(b_key, n)]
    det = a.notna() & b.notna()
    return det, det & (a > b)

det_tlt, tlt_gt = pairwise("TLT", "PSQ")
det_agg, agg_gt = pairwise("AGG", "SH")
det_ief, ief_gt = pairwise("IEF", "PSQ")
det_bnd, bnd_gt = pairwise("BND", "QQQ")

def tail_route():
    """Shared lower body: PSQ/TQQQ/SQQQ, with determinacy mask."""
    route = pd.Series("", index=CAL, dtype=object)
    det = pd.Series(True, index=CAL)
    up = tqqq_above20
    route[up & psq_dip] = "PSQ"
    need_agg = up & ~psq_dip
    route[need_agg & agg_gt] = "TQQQ"
    route[need_agg & ~agg_gt] = "PSQ"
    det &= ~need_agg | det_agg
    dn = ~up
    route[dn & ief_gt] = "PSQ"
    route[dn & ~ief_gt] = "SQQQ"
    det &= ~dn | det_ief
    return route, det

tail, tail_det = tail_route()
bond = tail.copy(); bond_det = tail_det & det_tlt
bond[tlt_gt] = "QQQ"
bond_det = (det_tlt & tlt_gt) | (det_tlt & ~tlt_gt & tail_det)
feaver = tail.copy(); feaver_det = tail_det.copy()
feaver[crash & bnd_gt] = "QLD"
feaver[crash & ~bnd_gt] = "BTAL"
feaver_det = (~crash & tail_det) | (crash & det_bnd)

scope = bear & bond_det & feaver_det
indet = bear & ~(bond_det & feaver_det)
agree = scope & (bond == feaver)
n_bear, n_scope = int(bear.sum()), int(scope.sum())
print(f"  bear branch reached: {n_bear:,} sessions "
      f"({n_bear / len(CAL):.2%} of calendar); routing determinate on "
      f"{n_scope:,}, indeterminate on {int(indet.sum())}")
print(f"  sub-models agree: {int(agree.sum()):,} ({int(agree.sum())/n_scope:.2%} "
      f"of determinate-bear); differ: {n_scope - int(agree.sum()):,}")

pairs = pd.DataFrame({"bond": bond[scope & ~agree],
                      "feaver": feaver[scope & ~agree]})
pair_freq = pairs.value_counts()
print("  disagreement pairs (bond, feaver):")
for (bb, ff), cnt in pair_freq.items():
    print(f"    ({bb:5s}, {ff:5s}): {cnt:5d}  "
          f"({cnt / max(n_scope - int(agree.sum()), 1):.1%} of disagreements)")
crash_in_bear = int((crash & bear).sum())
tlt_in_bear = int((tlt_gt & bear & det_tlt).sum())
print(f"  crash fires | bear reached: {crash_in_bear:,} "
      f"({crash_in_bear / n_bear:.2%})")
print(f"  TLT>PSQ head | bear reached: {tlt_in_bear:,} "
      f"({tlt_in_bear / n_bear:.2%})")

s4 = dict(bear_sessions=n_bear, determinate=n_scope,
          indeterminate=int(indet.sum()), agree=int(agree.sum()),
          agree_frac=float(agree.sum() / n_scope),
          crash_given_bear=crash_in_bear,
          crash_given_bear_frac=crash_in_bear / n_bear,
          tlt_head_given_bear=tlt_in_bear,
          tlt_head_given_bear_frac=tlt_in_bear / n_bear)
s4_rows = [dict(measure=k, value=v) for k, v in s4.items()]
s4_rows += [dict(measure=f"pair_{bb}_{ff}", value=int(cnt))
            for (bb, ff), cnt in pair_freq.items()]
pd.DataFrame(s4_rows).to_csv(OUT / "t11-submodel-agreement.csv", index=False)

# ===========================================================================
# Step 5: T11 tier-two firing
# ===========================================================================

print("\n=== STEP 5: T11 panel max-RSI firing ===")
s5_rows = []
for n in PERIODS:
    panel = pd.DataFrame({t: RSI[(t, n)] for t in T11_PANEL})
    mx = panel.max(axis=1)
    evaluable = mx.notna()
    n_eval = int(evaluable.sum())
    who = pd.Series(index=CAL, dtype=object)
    who[evaluable] = panel[evaluable].idxmax(axis=1)
    for thr in (70, 75, 80, 85):
        fire = evaluable & (mx > thr)
        eps = episodes(fire.to_numpy())
        attr = who[fire].value_counts().to_dict()
        s5_rows.append(dict(rsi_period=n, threshold=thr,
                            sessions=int(fire.sum()),
                            frac_of_evaluable=float(fire.sum() / n_eval),
                            episodes=len(eps),
                            evaluable_sessions=n_eval,
                            argmax_attribution="; ".join(
                                f"{k}:{v}" for k, v in sorted(
                                    attr.items(), key=lambda x: -x[1]))))
    if n == 14:
        for thr in (70, 75, 80, 85):
            r = s5_rows[-4 + (thr - 70) // 5]
        print("  period 14:")
        for r in s5_rows[-4:]:
            print(f"    >{r['threshold']}: {r['sessions']:5d} sessions "
                  f"({r['frac_of_evaluable']:.3%}), {r['episodes']:3d} episodes"
                  f"   [{r['argmax_attribution']}]")
s5 = pd.DataFrame(s5_rows)
s5.to_csv(OUT / "t11-tier2-firing.csv", index=False)
for n in (7, 28):
    sub = s5[s5.rsi_period == n]
    print(f"  period {n}: " + "; ".join(
        f">{r.threshold}: {r.sessions} ({r.episodes} ep)"
        for r in sub.itertuples()))

print("\nDONE - five CSVs written to outputs/session-06/")
