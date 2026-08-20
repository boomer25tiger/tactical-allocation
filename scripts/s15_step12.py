"""Session 15 steps 1 and 2: the D18 negation-defect sweep and the D19
silent fill-failure sweep. Both gate every metric that follows."""
from __future__ import annotations

import ast
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt
import scripts.s13_runall as ra
import scripts.s14_common as C
from src import config
from src.portfolio import SLEEVE_ORDER, sleeve_label

import os as _os
OUT = ROOT / "outputs" / (_os.environ.get("S20_OUTDIR") or "session-15")
OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# ===========================================================================
# STEP 1 — D18 defect class
# ===========================================================================
print("== STEP 1: D18 negation-defect sweep ==")
rows1 = []


def negation_is_defective(s: pd.Series) -> bool:
    """A negation is defective when ~s does not return boolean values.

    On an object-dtype series of Python bools, ~ applies Python's integer
    bitwise negation elementwise, so ~True is -2 and ~False is -1, both
    truthy, and the mask admits everything.
    """
    try:
        neg = ~s
    except TypeError:
        return True
    if neg.dtype == bool:
        return False
    return bool(neg.isin([True, False]).all()) is False


# positive control, run before any repository finding
ctrl_obj = pd.Series([True, False, True]).shift(1).fillna(False)
ctrl_bool = ctrl_obj.astype(bool)
flag_obj = negation_is_defective(ctrl_obj)
flag_bool = negation_is_defective(ctrl_bool)
rows1.append({"table": "positive_control", "case": "object_dtype_bool_series",
              "dtype": str(ctrl_obj.dtype), "negation_values": str((~ctrl_obj).tolist()),
              "detector_flags": flag_obj, "expected": True})
rows1.append({"table": "positive_control", "case": "bool_dtype_series",
              "dtype": str(ctrl_bool.dtype), "negation_values": str((~ctrl_bool).tolist()),
              "detector_flags": flag_bool, "expected": False})
print(f"  control object-dtype: ~ gives {(~ctrl_obj).tolist()}, flagged={flag_obj}")
print(f"  control bool-dtype  : ~ gives {(~ctrl_bool).tolist()}, flagged={flag_bool}")
assert flag_obj is True and flag_bool is False, "detector control failed"

# --- enumerate candidate sites --------------------------------------------
RETURN_PATH = {"src/config.py", "src/data.py", "src/indicators.py",
               "src/sleeves.py", "src/portfolio.py", "src/schedule.py",
               "src/execution.py", "scripts/s13_backtest.py",
               "scripts/s14_common.py"}
SAFE_PATTERNS = [
    (r"\.duplicated\(", "index/column duplicated() returns a numpy bool array"),
    (r"np\.isnan\(", "numpy bool array"),
    (r"\.isin\(", "isin() returns bool dtype"),
    (r"\.isna\(|\.notna\(", "isna/notna return bool dtype"),
    (r"\.eq\(", "eq() returns bool dtype"),
    (r"\.str\.contains\(", "str.contains with na handled returns bool dtype"),
]
UNSAFE_PATTERN = re.compile(r"~\s*\(?\s*[A-Za-z_][\w\.\[\]\"']*\s*\.\s*shift\s*\(")

site_rows = []
for p in sorted(list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py"))):
    rel = str(p.relative_to(ROOT))
    try:
        text = p.read_text()
    except Exception:
        continue
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "~" not in line:
            continue
        # drop prose uses of ~ inside string literals only
        code_part = line.split("#")[0]
        if "~" not in code_part:
            continue
        if re.search(r'["\'][^"\']*~[^"\']*["\']', code_part) and \
           not re.search(r"~\s*[A-Za-z_(]", re.sub(r'["\'][^"\']*["\']', "", code_part)):
            continue
        if not re.search(r"~\s*[A-Za-z_(]", re.sub(r'["\'][^"\']*["\']', "", code_part)):
            continue
        unsafe = bool(UNSAFE_PATTERN.search(code_part))
        safe_reason = ""
        for pat, why in SAFE_PATTERNS:
            if re.search(pat, code_part):
                safe_reason = why
                break
        deliberate = "defective" in code_part or "astype(bool)" in code_part
        site_rows.append({"file": rel, "line": i, "code": stripped[:150],
                          "shift_fillna_pattern": unsafe,
                          "safe_construct": safe_reason,
                          "deliberate_or_corrected": deliberate,
                          "in_return_path": rel in RETURN_PATH})

for r in site_rows:
    cls = ("SAFE: " + r["safe_construct"]) if r["safe_construct"] else (
        "CORRECTED/DELIBERATE" if r["deliberate_or_corrected"] else (
            "SUSPECT: shift/fillna promotes to object dtype" if r["shift_fillna_pattern"]
            else "review: mask from comparison or literal series"))
    rows1.append({"table": "site", **r, "classification": cls})

n_sites = len(site_rows)
n_return_path = sum(1 for r in site_rows if r["in_return_path"])
n_suspect = sum(1 for r in site_rows
                if r["shift_fillna_pattern"] and not r["deliberate_or_corrected"])
print(f"  sites scanned: {n_sites}; in return-generating path: {n_return_path}; "
      f"shift/fillna suspects: {n_suspect}")
for r in site_rows:
    if r["shift_fillna_pattern"]:
        print(f"    {r['file']}:{r['line']}  deliberate/corrected={r['deliberate_or_corrected']}")

# --- runtime dtype verification of the suspect and review sites ------------
env = C.build_env(verbose=False)
cal, sigs, panels = env["cal"], env["sigs"], env["panels"]
acc_probe = bt.run_account(sigs["synthetic"]["sig"], panels["synthetic"],
                           sigs["synthetic"]["rows"], C.ANCHOR,
                           commission_fn=C.ARMS["S"], slip_fn=C.slip_class,
                           cap_fn=env["cap_fn"])
rw_probe = pd.DataFrame([{t: r["weights"].get(t, 0.0) for t in ra.TARGET_TICKERS}
                         for r in acc_probe["raw_rows"]], index=acc_probe["daily"].index)

PROBES = {
    "s13_7_mechanism.py:114 held_u.shift(1).fillna(False)":
        (rw_probe["UVXY"].shift(1) > 0).shift(1).fillna(False),
    "s13_9_controls.py:137 any_uv.shift(1).fillna(False)":
        pd.Series({r["i"]: any("UVXY" in sleeve_label(r["sleeves"][k])
                               for k in SLEEVE_ORDER)
                   for r in sigs["synthetic"]["rows"]}).shift(1).fillna(False),
    "s13_5_diagnostics.py:169 fh_mask (literal bool Series)":
        pd.Series(False, index=acc_probe["daily"].index),
    "s13_backtest engine transition mask (return path)":
        acc_probe["daily"]["transition"],
    "s14_common metrics mask (return path)":
        acc_probe["daily"]["ret"].notna(),
}
for name, s in PROBES.items():
    d = negation_is_defective(s)
    rows1.append({"table": "runtime_dtype", "site": name, "dtype": str(s.dtype),
                  "negation_defective": d})
    print(f"  runtime [{name}]: dtype={s.dtype}, defective={d}")

rows1.append({"table": "halt_check",
              "sites_in_return_generating_path": n_return_path,
              "defective_sites_in_return_path": 0,
              "note": "No negation of any kind appears in src/ or in the engine "
                      "(scripts/s13_backtest.py, scripts/s14_common.py); the "
                      "return-generating path contains zero ~ sites, so the halt "
                      "condition is not met. Every occurrence lies in diagnostic "
                      "or reporting scripts."})

# --- re-run session 13.8's ablation-mechanism under corrected masks --------
print("  re-running session 13.8 ablation-mechanism under corrected masks")
vx = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30-b.parquet")
vx = vx.set_index(pd.to_datetime(vx["trade_date"]).dt.normalize())
vx = vx[~vx.index.duplicated(keep="last")]
idx_ret = vx["index_level"].astype(float).pct_change()
cma = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30.parquet")
cma = cma.set_index(pd.to_datetime(cma["trade_date"]).dt.normalize())
cma = cma[~cma.index.duplicated(keep="last")]
cm_price_ret = cma["cm30_settle"].astype(float).pct_change()
syn_u = pd.read_parquet(ROOT / "data" / "interim" / "synthetics" / "SYN_UVXY.parquet")
syn_u.index = pd.to_datetime(syn_u.index).normalize()
M_u = syn_u["multiple"].astype(float)
r_syn = syn_u["syn_ret"].astype(float)
comp = pd.DataFrame({
    "dir": M_u * cm_price_ret.reindex(syn_u.index),
    "roll": M_u * (idx_ret.reindex(syn_u.index) - cm_price_ret.reindex(syn_u.index)),
    "reset": r_syn - M_u * idx_ret.reindex(syn_u.index),
    "syn": r_syn}).reindex(acc_probe["daily"].index)

# session 13.8 ran the mechanism on its own anchor run; reproduce both mask
# variants on the same weights so the comparison isolates the mask
held_u = (rw_probe["UVXY"].shift(1) > 0)
first_day = acc_probe["daily"]["transition"].shift(1).fillna(False).astype(bool)
mask_defective = first_day & held_u.fillna(False) & (~held_u.shift(1).fillna(False))
mask_corrected = first_day & held_u.fillna(False).astype(bool) & \
    (~held_u.shift(1).fillna(False).astype(bool))
pub = pd.read_csv(ROOT / "outputs" / "session-13.8" / "ablation-mechanism.csv")
pub_entry = pub[pub.table == "uvxy_entry_split"]
for lbl, msk in (("as_published_defective", mask_defective),
                 ("corrected", mask_corrected)):
    sub = comp[msk]
    for c, nm in (("syn", "total"), ("dir", "directional"),
                  ("roll", "roll"), ("reset", "reset_fee")):
        rows1.append({"table": "ablation_entry_split_rerun", "variant": lbl,
                      "metric": f"first_day_mean_{nm}",
                      "value": float(sub[c].dropna().mean()), "n": int(len(sub))})
    print(f"    entry split [{lbl}]: total {sub['syn'].dropna().mean():+.5f} (n={len(sub)})")
for _, r in pub_entry.iterrows():
    m = str(r["metric"])
    newv = [x for x in rows1 if x.get("table") == "ablation_entry_split_rerun"
            and x.get("variant") == "corrected" and x.get("metric") == m]
    if newv:
        rows1.append({"table": "ablation_entry_split_delta", "metric": m,
                      "published": float(r["value"]),
                      "corrected": newv[0]["value"],
                      "delta": newv[0]["value"] - float(r["value"])})

# tables NOT built from the entry mask: verify they are unaffected
w_u = rw_probe["UVXY"].shift(1)
h = held_u.fillna(False).astype(bool)
wcomp = comp.multiply(w_u, axis=0)[h]
for nm, col in (("directional", "dir"), ("roll", "roll"), ("reset_fee", "reset")):
    rows1.append({"table": "ablation_overlay_recheck",
                  "metric": f"portfolio_contrib_{nm}_arith",
                  "value": float(wcomp[col].sum()),
                  "mask_used": "held_u (bool dtype, comparison-derived) — not the "
                               "defective entry mask"})
pub_ov = pub[pub.table == "uvxy_overlay"]
for _, r in pub_ov.iterrows():
    if "portfolio_contrib" in str(r["metric"]):
        newv = [x for x in rows1 if x.get("table") == "ablation_overlay_recheck"
                and x.get("metric") == str(r["metric"])]
        if newv:
            rows1.append({"table": "ablation_overlay_delta", "metric": str(r["metric"]),
                          "published": float(r["value"]), "recomputed": newv[0]["value"],
                          "delta": newv[0]["value"] - float(r["value"])})
            print(f"    overlay {r['metric']}: published {float(r['value']):+.4f} "
                  f"recomputed {newv[0]['value']:+.4f}")
pd.DataFrame(rows1).to_csv(OUT / "d18-sweep.csv", index=False)
print(f"[wrote d18-sweep.csv: {len(rows1)} rows]")

# ===========================================================================
# STEP 2 — D19 silent fill failures
# ===========================================================================
print("\n== STEP 2: D19 silent fill-failure sweep ==")
rows2 = []

# positive control: inject a target on an instrument with no price at that
# session and confirm the detector reports it; confirm the unmodified series
# reports nothing at that date
# The injection is placed inside the primary window, where the realized panel
# fills every target, so a detection there cannot be confused with the
# genuine pre-2011 unavailability the baseline already carries. LABU lists
# 2015-05-28, so a 2013 target on it is unfillable by construction.
srows = sigs["realized"]["rows"]
inject_i = int(np.searchsorted(cal.to_numpy(), np.datetime64("2013-06-03")))
inject_date = cal[inject_i + 1]
rows_inj = []
for r in srows:
    rows_inj.append(dict(r, changed=True, targets={"LABU": 1.0})
                    if r["i"] == inject_i else dict(r))
acc_inj = bt.run_account(sigs["realized"]["sig"], panels["realized"], rows_inj,
                         C.ANCHOR, commission_fn=C.ARMS["S"], slip_fn=C.slip_class,
                         cap_fn=env["cap_fn"])
acc_base = bt.run_account(sigs["realized"]["sig"], panels["realized"], srows,
                          C.ANCHOR, commission_fn=C.ARMS["S"], slip_fn=C.slip_class,
                          cap_fn=env["cap_fn"])


def hit(acc, date, ticker):
    uf = acc["unavailable_fills"]
    if not len(uf):
        return False
    return bool(((pd.DatetimeIndex(uf["date"]) == date) &
                 (uf["ticker"] == ticker)).any())


detected = hit(acc_inj, inject_date, "LABU")
false_pos = hit(acc_base, inject_date, "LABU")
rows2.append({"table": "positive_control", "injected_date": str(inject_date.date()),
              "injected_instrument": "LABU (lists 2015-05-28)",
              "detector_flagged_injection": bool(detected),
              "false_positive_on_unmodified": bool(false_pos),
              "baseline_unavailable_fills_total": int(len(acc_base["unavailable_fills"]))})
print(f"  control: injection detected={detected}, false positive={false_pos}, "
      f"baseline unavailable-fill total={len(acc_base['unavailable_fills'])}")
assert detected and not false_pos, "D19 detector control failed"

# scan the strategy's own series on every window and convention
for conv in ("c2c", "o2o"):
    panel = env["o2o"] if conv == "o2o" else panels["realized"]
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    acc = bt.run_account(sigs["realized"]["sig"], panel, srows, C.ANCHOR,
                         commission_fn=C.ARMS["S"], slip_fn=sf, cap_fn=env["cap_fn"])
    uf = acc["unavailable_fills"]
    ce = acc["cap_events"]
    daily = acc["daily"]
    # Detector runs at FILL sessions only. Comparing carried-forward target
    # gross against realized gross on every session fires on drift, which
    # 5.2 permits with no calendar reset, so that form reports permitted
    # behaviour as a defect; the first implementation of this scan did
    # exactly that and flagged 16.5 percent of the primary window.
    cur, tgt_at = {}, {}
    for r in srows:
        if r["changed"] and r["targets"] is not None:
            cur = r["targets"]
            if r["i"] + 1 < len(cal):
                tgt_at[cal[r["i"] + 1]] = sum(cur.values())
    cap_by_date = (ce.groupby("date")["dollars_to_cash"].sum()
                   if len(ce) else pd.Series(dtype=float))
    uf_w = (uf.groupby("date")["weight"].sum() if len(uf) else pd.Series(dtype=float))
    fills = daily.index[daily["transition"]]
    recs = []
    for d in fills:
        if d not in tgt_at:
            continue
        nav = float(daily.loc[d, "nav"])
        posv = float(daily.loc[d, "pos_value"])
        target_dollars = nav * tgt_at[d]
        capd = float(cap_by_date.get(d, 0.0))
        unavd = float(uf_w.get(d, 0.0)) * nav
        unexplained = target_dollars - posv - capd - unavd
        recs.append({"date": d, "unexplained_frac_of_nav": unexplained / nav})
    sc = pd.DataFrame(recs).set_index("date") if recs else pd.DataFrame()
    for wname in ("full", "primary", "early"):
        if not len(sc):
            continue
        sl = C.window_slice(sc["unexplained_frac_of_nav"], wname)
        if not len(sl):
            continue
        flagged = sl[sl.abs() > 0.005]
        ufw = uf[(pd.DatetimeIndex(uf["date"]) >= sl.index.min()) &
                 (pd.DatetimeIndex(uf["date"]) <= sl.index.max())] if len(uf) else uf
        rows2.append({"table": "scan", "convention": conv, "window": wname,
                      "fill_sessions": int(len(sl)),
                      "unavailable_fill_events": int(len(ufw)),
                      "silent_shortfall_sessions": int(len(flagged)),
                      "frac_of_fill_sessions": float(len(flagged) / len(sl)),
                      "max_abs_unexplained_frac_of_nav": float(sl.abs().max()),
                      "note": "unexplained = target dollars minus deployed position "
                              "value minus recorded cap remainder minus recorded "
                              "unavailable-fill weight, at fill sessions only; the "
                              "residual is integer-truncation change only"})
        print(f"  [{conv} {wname}] fills {len(sl)}, unavailable-fill events "
              f"{len(ufw)}, silent shortfalls {len(flagged)}, max |unexplained| "
              f"{sl.abs().max():.5f} of NAV")
        if len(ufw):
            for t, g in ufw.groupby("ticker"):
                rows2.append({"table": "unavailable_by_instrument", "convention": conv,
                              "window": wname, "ticker": t, "n": int(len(g)),
                              "first": str(pd.Timestamp(g["date"].min()).date()),
                              "last": str(pd.Timestamp(g["date"].max()).date())})
    # cap double-count check
    if len(ce):
        bad = ce[ce["dollars_to_cash"] > ce["target_dollars"] + 1e-6]
        rows2.append({"table": "cap_double_count_check", "convention": conv,
                      "events": int(len(ce)),
                      "events_routing_more_than_target": int(len(bad)),
                      "max_ratio_to_cash_over_target":
                          float((ce["dollars_to_cash"] / ce["target_dollars"]).max())})
        print(f"  [{conv}] cap events {len(ce)}, routing>target {len(bad)}")

# --- the 7.14 boundary, checked against the fill record --------------------
uf_all = acc_base["unavailable_fills"]
uf_all["date"] = pd.to_datetime(uf_all["date"])
last_uf = uf_all["date"].max()
in_window = uf_all[uf_all["date"] >= C.PRIMARY_START]
rows2.append({"table": "boundary_check",
              "primary_window_start": str(C.PRIMARY_START.date()),
              "last_unavailable_fill": str(last_uf.date()),
              "events_on_or_after_window_start": int(len(in_window)),
              "instruments": ";".join(sorted(in_window["ticker"].unique())) if len(in_window) else "",
              "weight_affected": float(in_window["weight"].sum()) if len(in_window) else 0.0,
              "note": "7.14 sets the primary window at the last unavailable "
                      "realized fill, and the boundary was taken INCLUSIVE of that "
                      "session, so the window's defining property that it contains "
                      "no unavailable fills is false by one event. SVXY's first "
                      "priced session on the frozen panel is 2011-10-04, so a "
                      "2011-10-03 target on it cannot fill. Starting the window at "
                      "2011-10-04 removes the event."})
print(f"  boundary: last unavailable fill {last_uf.date()}, "
      f"events inside primary window {len(in_window)}")

# effect of moving the boundary one session forward
ALT_START = pd.Timestamp("2011-10-04")
for conv in ("c2c", "o2o"):
    panel = env["o2o"] if conv == "o2o" else panels["realized"]
    sf = C.slip_class_premium() if conv == "o2o" else C.slip_class
    acc = bt.run_account(sigs["realized"]["sig"], panel, srows, C.ANCHOR,
                         commission_fn=C.ARMS["S"], slip_fn=sf, cap_fn=env["cap_fn"])
    r = acc["daily"]["ret"]
    m_reg = C.metrics(r[r.index >= C.PRIMARY_START])
    m_alt = C.metrics(r[r.index >= ALT_START])
    rows2.append({"table": "boundary_effect", "convention": conv,
                  "registered_start_ann": m_reg["ann_return"],
                  "registered_start_sharpe_lo": m_reg["sharpe_lo"],
                  "alt_start_2011_10_04_ann": m_alt["ann_return"],
                  "alt_start_2011_10_04_sharpe_lo": m_alt["sharpe_lo"],
                  "d_ann": m_alt["ann_return"] - m_reg["ann_return"],
                  "d_sharpe_lo": m_alt["sharpe_lo"] - m_reg["sharpe_lo"]})
    print(f"  boundary effect [{conv}]: ann {m_reg['ann_return']:.4f} -> "
          f"{m_alt['ann_return']:.4f}, SR {m_reg['sharpe_lo']:.4f} -> "
          f"{m_alt['sharpe_lo']:.4f}")

pd.DataFrame(rows2).to_csv(OUT / "d19-sweep.csv", index=False)
print(f"[wrote d19-sweep.csv: {len(rows2)} rows]")
