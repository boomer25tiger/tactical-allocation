"""Session 20 phase A. Universe derivation and the holdout-critical unknowns.

TOLERANCE, STATED BEFORE THE COMPARISON IT GOVERNS.
  TOL_CANON = 5e-7 absolute on the standing positive control, being the
  canonical rebuilt from the frozen inputs against 0.521845 annualised and
  1.381701 Lo-corrected Sharpe over 2,472 sessions.

No ticker list is written by hand anywhere in this file. The held and signal
sets are derived from the abstract syntax tree of src/sleeves.py.
"""
from __future__ import annotations
import ast, csv, re, resource, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt      # noqa: E402
import scripts.s14_common as C         # noqa: E402
import scripts.s15_lines as L          # noqa: E402
import src.sleeves as SL               # noqa: E402
from src import config                 # noqa: E402

OUT = ROOT / "outputs" / "session-20"; OUT.mkdir(parents=True, exist_ok=True)
TOL_CANON = 5e-7
TARGET_ANN, TARGET_SLO, TARGET_N = 0.521845, 1.381701, 2472
CORRECTED_START = pd.Timestamp("2011-10-04")
t_phase = time.time()


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


def w(name, rows, cols):
    with open(OUT / name, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        wr.writeheader(); wr.writerows(rows)
    print(f"wrote {OUT/name} with {len(rows)} rows")


# ===================== A1, the authoritative held universe ==================
src = (ROOT / "src" / "sleeves.py").read_text()
tree = ast.parse(src)
ACC = {"rsi_exhaustion", "rsi_dip", "rsi_rs", "price", "sma",
       "trailing_return_pct", "available"}
lines = src.split("\n")
assign_str = {}
for n in ast.walk(tree):
    if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
        v = [c.value for c in ast.walk(n.value)
             if isinstance(c, ast.Constant) and isinstance(c.value, str)
             and re.fullmatch(r"[A-Z]{2,5}", c.value)]
        if v:
            assign_str.setdefault(n.targets[0].id, set()).update(v)

held_rows, held, signal = [], {}, {}
for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
    for n in ast.walk(fn):
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict):
            for k, v in zip(n.value.keys, n.value.values):
                if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)) and v.value == 0:
                    continue
                wt = ast.unparse(v)
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    tk = [k.value]; via = ""
                elif isinstance(k, ast.Name):
                    tk = sorted(assign_str.get(k.id, set())); via = k.id
                else:
                    continue
                for t in tk:
                    held.setdefault(t, []).append((fn.name, n.lineno, wt, via))
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant) \
                and isinstance(n.value.value, str) and re.fullmatch(r"[A-Z]{2,5}", n.value.value):
            held.setdefault(n.value.value, []).append((fn.name, n.lineno, "1.0 (bare return)", ""))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ACC:
            for a in n.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    signal.setdefault(a.value, set()).add(f"{fn.name}.{n.func.attr}")
for nm, tup in (("T10_CASCADE", SL.T10_CASCADE), ("T11_PANEL", SL.T11_PANEL),
                ("S3_VOTES", tuple(SL.S3_VOTES))):
    for t in tup:
        signal.setdefault(t, set()).add(nm)
signal.setdefault(config.TREND_SIGNAL_SERIES, set()).add("config.TREND_SIGNAL_SERIES")

SLEEVE_OF = {"t10_weights": "T10", "t11_weights": "T11", "_t11_bond_baller": "T11",
             "_t11_feaver_bear": "T11", "s2_weights": "S2", "s3_weights": "S3"}
HELD = sorted(held); SIGNAL_ONLY = sorted(t for t in signal if t not in held)
for t in HELD:
    for fnname, ln, wt, via in held[t]:
        held_rows.append({"table": "held", "ticker": t,
                          "sleeve": SLEEVE_OF.get(fnname, fnname),
                          "function": fnname, "line": ln, "weight": wt,
                          "via_variable": via})
for t in SIGNAL_ONLY:
    held_rows.append({"table": "signal_only", "ticker": t,
                      "note": " ; ".join(sorted(signal[t]))})
held_rows.append({"table": "counts", "ticker": "n_held", "line": len(HELD)})
held_rows.append({"table": "counts", "ticker": "n_signal_only", "line": len(SIGNAL_ONLY)})
held_rows.append({"table": "counts", "ticker": "session_19_6_n_held", "line": 19,
                  "note": "reconciliation target"})
held_rows.append({"table": "counts", "ticker": "session_19_6_n_signal_only", "line": 13})
held_rows.append({"table": "reconciliation", "ticker": "difference_vs_19_6",
                  "note": "none" if (len(HELD), len(SIGNAL_ONLY)) == (19, 13)
                          else f"derived {len(HELD)}/{len(SIGNAL_ONLY)}"})
held_rows.append({"table": "authority", "ticker": "supersedes",
                  "note": "outputs/session-20/held-universe.csv supersedes every "
                          "hardcoded ticker list in the repository"})
print(f"A1 held {len(HELD)}: {HELD}")
print(f"A1 signal-only {len(SIGNAL_ONLY)}: {SIGNAL_ONLY}")

lit_scripts = []
for p in sorted(list((ROOT / "scripts").glob("*.py")) + list((ROOT / "src").glob("*.py"))):
    txt = p.read_text()
    tk = set(re.findall(r'"([A-Z]{2,5})"', txt)) & (set(HELD) | set(SIGNAL_ONLY))
    if len(tk) >= 3 and p.name not in ("sleeves.py",):
        lit_scripts.append(p)
        held_rows.append({"table": "hardcoded_list_site",
                          "ticker": str(p.relative_to(ROOT)), "line": len(tk),
                          "note": "carries a ticker list phase B3 sweeps"})
print(f"A1 scripts carrying ticker lists for the B3 sweep: {len(lit_scripts)}")
w("held-universe.csv", held_rows,
  ["table", "ticker", "sleeve", "function", "line", "weight", "via_variable", "note"])

# ===================== standing positive control ============================
C.PRIMARY_START = CORRECTED_START
env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn, panels = (env["cal"], env["sigs"], env["o2o"],
                                  env["cap_fn"], env["panels"])
sig = sigs["realized"]
acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
daily = acc["daily"]
r_can = daily["ret"].loc[daily.index >= CORRECTED_START].dropna()
m = L.standalone_metrics(r_can, daily["nav"], acc["orders"])
pc = {"ann_return": (m["ann_return"], TARGET_ANN), "sharpe_lo": (m["sharpe_lo"], TARGET_SLO),
      "n_sessions": (float(len(r_can)), float(TARGET_N))}
pc_ok = all(abs(a - b) <= (TOL_CANON if k != "n_sessions" else 0) for k, (a, b) in pc.items())
print(f"\nstanding positive control {'PASS' if pc_ok else 'FAIL'}: "
      f"ann {m['ann_return']:.6f} lo {m['sharpe_lo']:.6f} n {len(r_can)}")

# ===================== A2, SVIX and UVIX ====================================
a2 = []
for k, (a, b) in pc.items():
    a2.append({"table": "positive_control", "item": k, "value": a, "target": b,
               "abs_gap": abs(a - b), "within": int(abs(a - b) <= (TOL_CANON if k != "n_sessions" else 0))})
a2.append({"table": "positive_control", "item": "tolerance", "value": TOL_CANON,
           "note": "stated before comparing"})
a2.append({"table": "positive_control", "item": "verdict", "note": "PASS" if pc_ok else "FAIL"})

for t in ("SVIX", "UVIX"):
    for fnname, ln, wt, via in held.get(t, []):
        a2.append({"table": "site", "item": t, "sleeve": SLEEVE_OF.get(fnname, fnname),
                   "note": f"{fnname} line {ln}, weight {wt}, selected through variable "
                           f"{via}", "value": ln})
    a2.append({"table": "loaded", "item": t,
               "value": int(t in bt.LEVERED or t in bt.UNLEVERED),
               "note": "membership of bt.LEVERED or bt.UNLEVERED, the loader tuples"})
    for arm in ("realized", "synthetic"):
        a2.append({"table": "panel_presence", "item": f"{t}_{arm}",
                   "value": int(t in panels[arm].frames),
                   "note": "presence in the loaded panel frames"})
    for p in (ROOT / f"data/raw/etf/{t}.parquet", ROOT / f"data/interim/synthetics/SYN_{t}.parquet"):
        if p.exists():
            d = pd.read_parquet(p); idx = pd.to_datetime(d.index)
            a2.append({"table": "file_on_disk", "item": str(p.relative_to(ROOT)),
                       "value": len(d),
                       "note": f"first {idx.min().date()} last {idx.max().date()}"})

# terminal firing counts over the primary window
i0 = int(np.searchsorted(cal.to_numpy(), np.datetime64(CORRECTED_START)))
cnt = {"t10_vol_short_terminal": 0, "s3_vol_terminal": 0,
       "t10_resolved_SVIX": 0, "s3_resolved_UVIX": 0}
for r in sig["rows"]:
    if r["i"] < i0:
        continue
    s10 = r["sleeves"].get("T10"); s3 = r["sleeves"].get("S3")
    if s10 and set(s10) == {"TECL", "SOXL", "SVXY"}:
        cnt["t10_vol_short_terminal"] += 1
    if s10 and "SVIX" in s10:
        cnt["t10_resolved_SVIX"] += 1
    if s3 and set(s3) == {"UVXY"}:
        cnt["s3_vol_terminal"] += 1
    if s3 and "UVIX" in s3:
        cnt["s3_resolved_UVIX"] += 1
for k, v in cnt.items():
    a2.append({"table": "terminal_firing", "item": k, "value": v,
               "note": "sessions across the primary window under the canonical"})
print(f"A2 terminal firing over the primary window: {cnt}")

a2.append({"table": "engine_behaviour", "item": "available_on_absent_ticker",
           "note": "ArmSignals State.available at scripts/s13_backtest.py:344 reads "
                   "self.sig.avail.get(t) and returns False when the ticker is absent "
                   "from the panel, so the switch resolves to SVXY and UVXY on every "
                   "session and the SVIX and UVIX branches are unreachable"})
a2.append({"table": "engine_behaviour", "item": "weight_dict_naming_absent_ticker",
           "note": "the fill path at scripts/s13_backtest.py:500 reads px = raw[t][i] "
                   "where raw is built only over panel.frames, so an absent ticker "
                   "raises KeyError rather than being silently dropped, renormalised, "
                   "or routed to cash. Register 1.9 covers threshold reads and is "
                   "silent on weight dictionaries, and the traced behaviour is an "
                   "exception"})
a2.append({"table": "gate_A2", "item": "engine_raises_on_absent_held_ticker", "value": 1,
           "note": "KeyError, established by tracing rather than by execution"})
a2.append({"table": "gate_A2", "item": "terminal_can_fire_inside_holdout", "value": 0,
           "note": "the availability switch cannot select SVIX or UVIX while the loader "
                   "tuples exclude them, so the branch cannot fire inside the holdout "
                   "under the current loader and the gate does not trip"})
a2.append({"table": "gate_A2", "item": "verdict", "note": "PASS, session continues"})
a2.append({"table": "holdout_consequence", "item": "listing_inside_holdout", "value": 1,
           "note": "SVIX and UVIX list 2022-03-30 on the frozen files, which falls "
                   "inside the holdout span beginning 2021-08-01, so the source "
                   "strategy's SVIX_LIVE and UVIX_LIVE guards would activate there "
                   "while this implementation will not, since the loader excludes them"})
a2.append({"table": "holdout_consequence", "item": "untested_code_path", "value": 1,
           "note": "the SVIX and UVIX branches executed zero times in sample and remain "
                   "unexecuted at the holdout read under the current loader. A session "
                   "that adds them to the loader tuples activates them for the first "
                   "time inside the holdout"})
w("unlisted-holdings.csv", a2,
  ["table", "item", "sleeve", "value", "target", "abs_gap", "within", "note"])

# ===================== A3, QQQ as a held instrument =========================
a3 = []
for fnname, ln, wt, via in held.get("QQQ", []):
    a3.append({"table": "site", "item": "QQQ", "sleeve": SLEEVE_OF.get(fnname, fnname),
               "value": ln, "note": f"{fnname} line {ln}, weight {wt}"})
wts = daily["weights"].loc[daily.index >= CORRECTED_START]
qw = np.array([float(x.get("QQQ", 0.0)) if isinstance(x, dict) else 0.0 for x in wts])
hold = qw > 0
a3 += [{"table": "holding", "item": "sessions_in_window", "value": int(len(qw))},
       {"table": "holding", "item": "sessions_holding_qqq", "value": int(hold.sum())},
       {"table": "holding", "item": "share_of_sessions", "value": float(hold.mean())},
       {"table": "holding", "item": "mean_weight_conditional",
        "value": float(qw[hold].mean()) if hold.any() else 0.0},
       {"table": "holding", "item": "mean_weight_unconditional", "value": float(qw.mean())},
       {"table": "holding", "item": "max_weight", "value": float(qw.max())}]
rq = o2o["QQQ"].ret_total.reindex(daily.index).loc[daily.index >= CORRECTED_START]
contrib = qw * rq.fillna(0.0).to_numpy()
tot = r_can.reindex(rq.index).fillna(0.0).to_numpy()
a3 += [{"table": "overlap", "item": "sum_qqq_contribution_arithmetic",
        "value": float(np.nansum(contrib))},
       {"table": "overlap", "item": "sum_total_return_arithmetic", "value": float(np.nansum(tot))},
       {"table": "overlap", "item": "share_of_arithmetic_return",
        "value": float(np.nansum(contrib) / np.nansum(tot)) if np.nansum(tot) else float("nan"),
        "note": "sum of weight times QQQ return over sum of daily strategy return, an "
                "arithmetic share rather than a compounded attribution"}]
lad = pd.read_csv(ROOT / "outputs/session-15/metrics-full.csv")
lad = lad[(lad.table == "metrics") & (lad.panel == "realized")
          & (lad.convention == "o2o") & (lad.window == "primary")]
gap = float(lad[lad.line == "STRATEGY"].sharpe_naive.iloc[0]) - \
      float(lad[lad.line == "buy_hold_QQQ"].sharpe_naive.iloc[0])
a3.append({"table": "consequence", "item": "naive_sharpe_gap_vs_buy_hold_qqq", "value": gap,
           "note": "read from outputs/session-15/metrics-full.csv, which carries the "
                   "superseded boundary; phase C rebuilds it"})
a3.append({"table": "consequence", "item": "statement",
           "note": "the canonical holds QQQ directly, so the gap against buy-and-hold "
                   "QQQ is partly a comparison of the strategy against a component of "
                   "itself. Reported as measured with no recommendation"})
print(f"A3 QQQ held on {int(hold.sum())} of {len(qw)} sessions, "
      f"mean conditional weight {qw[hold].mean() if hold.any() else 0:.4f}")
w("qqq-overlap.csv", a3, ["table", "item", "sleeve", "value", "note"])

# ===================== A4, coverage on the derived set ======================
a4 = []
win = cal[(cal >= CORRECTED_START) & (cal <= pd.Timestamp("2021-08-01"))]
for arm in ("realized", "synthetic"):
    p = panels[arm]
    present = [t for t in HELD if t in p.frames]
    absent = [t for t in HELD if t not in p.frames]
    av = pd.DataFrame({t: p[t].tr_index.reindex(cal).notna() for t in present}, index=cal)
    allok = av.all(axis=1).reindex(win)
    a4.append({"table": "coverage", "item": f"{arm}_sessions_any_held_unlisted",
               "value": int((~allok).sum()),
               "note": f"of {len(win)} window sessions, over the {len(present)} held "
                       f"tickers that load on this panel"})
    a4.append({"table": "coverage", "item": f"{arm}_share", "value": float((~allok).mean())})
    a4.append({"table": "coverage", "item": f"{arm}_held_never_loading",
               "value": len(absent), "note": " ".join(absent)})
    firsts = {}
    for t in present:
        i = np.flatnonzero(p[t].tr_index.reindex(cal).notna().to_numpy())
        if len(i):
            firsts[t] = cal[i[0]]
    latest = max(firsts.values()); binder = [t for t, v in firsts.items() if v == latest]
    j = int(np.searchsorted(cal.to_numpy(), np.datetime64(latest)))
    full = cal[j + config.WARMUP_SESSIONS]
    a4.append({"table": "full_composition", "item": arm, "note": str(full.date()),
               "value": int(full < CORRECTED_START),
               "note2": f"bound by {' '.join(binder)} first available {latest.date()} "
                        f"plus {config.WARMUP_SESSIONS} warmup sessions, over loading "
                        f"held tickers only"})
    print(f"A4 {arm}: {int((~allok).sum())} sessions with a held ticker unlisted, "
          f"full composition {full.date()}")
bc = pd.read_csv(ROOT / "outputs/session-16/boundary-correction.csv")
a4.append({"table": "distinction", "item": "unavailable_fills_from_2011_10_04",
           "value": float(bc[bc.table == "boundary_fills"]["unavailable_fills_from_2011_10_04"].iloc[0]),
           "note": "outputs/session-16/boundary-correction.csv, counting fills the "
                   "strategy attempted and could not make, which is what 7.14 defines "
                   "the window by"})
a4.append({"table": "distinction", "item": "listing_coverage_vs_unavailable_fills",
           "note": "the two are different quantities. Listing coverage counts sessions "
                   "where a held ticker was unlisted whether or not it was targeted. "
                   "The 19.5 report presented the first without distinguishing it"})
a4.append({"table": "strict_full_composition", "item": "reachable", "value": 0,
           "note": "SVIX and UVIX are held in code and load on neither panel, so strict "
                   "full composition over the derived held set is unreachable on any "
                   "date. The dates above are computed over loading held tickers only"})
w("coverage-derived.csv", a4, ["table", "item", "value", "note", "note2"])
print(f"\nphase A peak {rss():.3f} GB, {time.time()-t_phase:.1f}s")
