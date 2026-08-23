"""Session 30 phase B. The corporate action class sweep.

Runs first, since every downstream phase reads price series this phase screens.

THE SCREENING RULE, stated before running.

  For each levered or inverse fund the registered multiple m and the registered
  underlying come from src/schedule.py. The underlying is stood for by a frozen
  proxy instrument. A daily-reset fund's one-session return tracks m times the
  underlying almost exactly, so the TRACKING RESIDUAL

      e = r_observed - m * u_proxy

  is the discriminator. Under no corporate action e is one-session tracking error.
  Under a MISSING split of ratio R the observed return carries an extra factor of
  1/R, so e is approximately 1/R - 1, which is -0.0476 at R = 1.05, -0.1667 at
  R = 1.2 and -0.5 at R = 2, and which does NOT shrink as the underlying's move
  grows.

  RESIDUAL_TOL = 0.05. A fund's one-session tracking error against its own index
  sits far below five points, and the threshold catches any split ratio at or
  above about 1.053. It is set low enough to catch ratios well below 2, which the
  50 percent absolute-return threshold session 29 used could not.

  THE IMPLIED MULTIPLE is reported as the scaffold asks, being r_observed divided
  by u_proxy, together with its deviation from m. It is NOT the primary
  discriminator, since its denominator is unstable.

  MIN_ABS_UNDERLYING = 0.005. Below that the implied multiple is not computed.
  Those sessions are screened on absolute return instead at ABS_RET_TOL = 0.25,
  so they are not silently dropped. A missing split of ratio 1.33 or larger shows
  as an absolute return above 0.25 on its own.

Nothing here repairs any series. No frozen input is edited.
"""
from __future__ import annotations

import ast
import csv
import os
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
from src import config                                 # noqa: E402
from src.schedule import FUND_SCHEDULE                 # noqa: E402

OUT = ROOT / "outputs" / "session-30"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
RESIDUAL_TOL, MIN_ABS_UNDERLYING, ABS_RET_TOL = 0.05, 0.005, 0.25
PROXY = {"Nasdaq-100 Index": "QQQ", "S&P 500 Index": "SPY",
         "Technology Select Sector Index": "XLK",
         "ICE Semiconductor Index": "SMH",
         "PHLX Semiconductor Sector Index": "SOXX",
         "S&P Biotechnology Select Industry Index": "XBI",
         "Financials Select Sector Index": "XLF",
         "Russell 1000 Financial Services Index": "XLF",
         "Russell 1000 Financials 40 Act 15/22.5 Daily Capped Index": "XLF"}
VOL_BENCH = "S&P 500 VIX Short-Term Futures Index"
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


import subprocess                                       # noqa: E402
_l = [float(x) for x in subprocess.run(["sysctl", "-n", "vm.loadavg"],
      capture_output=True, text=True).stdout.strip().strip("{} ").split()]
_s = VM.sample()
for k, v in (("load_1min", _l[0]), ("compressor_gib", _s["compressor_gib"]),
             ("swap_used_mb", _s["swap_used_mb"]), ("swap_free_mb", _s["swap_free_mb"])):
    add("machine_at_phase_B", item=k, value=v)

add("rule", item="residual_tolerance", value=RESIDUAL_TOL,
    note="the tracking residual e equals the observed return minus the registered "
         "multiple times the proxy's return. A missing split of ratio R contributes "
         "about 1/R minus 1 to e, being -0.0476 at R equal to 1.05 and -0.1667 at R "
         "equal to 1.2, and it does not shrink as the underlying's move grows. The "
         "threshold catches ratios at and above about 1.053")
add("rule", item="min_abs_underlying_return", value=MIN_ABS_UNDERLYING,
    note="below this the implied multiple is not computed, since its denominator is "
         "unstable. Those sessions are screened on absolute return instead")
add("rule", item="absolute_return_tolerance", value=ABS_RET_TOL,
    note="applied to the sessions the implied multiple cannot be computed on, so they "
         "are not silently dropped. A missing split of ratio 1.33 or larger shows as an "
         "absolute return above this on its own")
add("rule", item="stated_before_running", value=1)

print("building the environment")
env = C.build_env(verbose=False)
panel = env["panels"]["realized"]
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
RET = pd.DataFrame({t: panel[t].ret_total for t in TICK})
# the volatility proxy, the frozen constant-maturity thirty-day VIX futures settle
_VX = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30.parquet")
_VX = _VX.set_index(pd.DatetimeIndex(_VX["trade_date"]).normalize())["cm30_settle"]
VX_RET = _VX.astype(float).pct_change()
add("proxy", item="volatility_benchmark", value="data/interim/vx-cm30.parquet",
    note="the frozen constant-maturity thirty-day VIX futures settle. It is an "
         "IMPERFECT PROXY for a front-month-tracking product, which is why session 29 "
         "flagged SVXY on 2018-02-06 and UVXY on 2018-02-05 and 2020-03-16 as "
         "unexplained where the underlying event is the February 2018 volatility spike "
         "and the March 2020 volatility peak respectively")
for b, p in sorted(PROXY.items()):
    add("proxy", item=b, value=p,
        note="frozen instrument standing for the registered index" +
             ("" if p in TICK or (ROOT / "data" / "raw" / "etf" / f"{p}.parquet").exists()
              else ". NOT PRESENT in the frozen inputs"))
    if p not in RET.columns:
        pp = ROOT / "data" / "raw" / "etf" / f"{p}.parquet"
        if pp.exists():
            fr = pd.read_parquet(pp)
            fr.index = pd.DatetimeIndex(fr.index).tz_localize(None).normalize()
            col = "Adj Close" if "Adj Close" in fr.columns else "Close"
            RET[p] = fr[col].astype(float).pct_change().reindex(RET.index)

# the derived held universe, from the session 28 weights
sw = {sl: pd.read_parquet(ROOT / "outputs" / "session-28" /
                          f"_sleeve_weights_{sl}.parquet")
      for sl in ("T10", "T11", "S2", "S3")}
W = sum(sw.values())
HELD = sorted([t for t in TICK if t in W.columns and (W[t] != 0).any()])
add("scope", item="loaded_universe", value=len(TICK),
    note="bt.UNLEVERED plus bt.LEVERED, unmodified")
add("scope", item="derived_held_universe", value=len(HELD), note=", ".join(HELD))

IDX = RET.index[(RET.index >= PRIMARY) & (RET.index <= pd.Timestamp("2026-08-14"))]
add("scope", item="sessions_screened_per_instrument", value=len(IDX),
    note=f"{IDX.min().date()} to {IDX.max().date()}, the full combined window")


def registered(t, d0):
    for pr in FUND_SCHEDULE.get(t, []):
        st, en = pd.Timestamp(pr.start), (pd.Timestamp(pr.end) if pr.end else None)
        if d0 >= st and (en is None or d0 <= en):
            return pr.multiple, pr.benchmark
    return None, None


# ================================ B1 ==============================================
flags, screened, no_proxy, low_u = 0, 0, [], 0
per_inst = {}
for t in HELD:
    m_series, u_series, prox_names = [], [], set()
    for d0 in IDX:
        m, b = registered(t, d0)
        if m is None:
            m_series.append(np.nan); u_series.append(np.nan); continue
        if b == VOL_BENCH:
            u = VX_RET.get(d0, np.nan); prox_names.add("vx-cm30")
        else:
            p = PROXY.get(b)
            if p is None or p not in RET.columns:
                u = np.nan
                if b:
                    no_proxy.append((t, b))
            else:
                u = RET[p].get(d0, np.nan); prox_names.add(p)
        m_series.append(m); u_series.append(u)
    mm = pd.Series(m_series, index=IDX)
    uu = pd.Series(u_series, index=IDX)
    rr = RET[t].reindex(IDX)
    ok = mm.notna() & uu.notna() & rr.notna()
    screened += int(ok.sum())
    resid = rr - mm * uu
    lowmask = ok & (uu.abs() < MIN_ABS_UNDERLYING)
    low_u += int(lowmask.sum())
    implied = pd.Series(np.nan, index=IDX)
    hi = ok & ~lowmask
    implied[hi] = rr[hi] / uu[hi]
    fl_res = ok & (resid.abs() > RESIDUAL_TOL)
    fl_abs = lowmask & (rr.abs() > ABS_RET_TOL)
    fl = fl_res | fl_abs
    per_inst[t] = {"screened": int(ok.sum()), "flagged": int(fl.sum()),
                   "low_u": int(lowmask.sum()), "dates": list(IDX[fl]),
                   "proxy": ",".join(sorted(prox_names)) or "none"}
    flags += int(fl.sum())
    add("instrument_screen", item=t, value=int(fl.sum()),
        n_screened=int(ok.sum()), n_low_underlying=int(lowmask.sum()),
        proxy=per_inst[t]["proxy"],
        registered_multiple=(q(mm.dropna().iloc[0]) if ok.any() else ""),
        note="unlevered or no registered schedule, so the implied-multiple screen does "
             "not apply" if not ok.any() else "")
    for d0 in IDX[fl]:
        w_lag = float(W[t].shift(1).get(d0, 0.0)) if t in W.columns else 0.0
        add("flagged_session", item=t, date=str(d0.date()),
            value=q(rr[d0]), implied_multiple=(q(implied[d0]) if hi[d0] else ""),
            registered_multiple=q(mm[d0]), underlying_return=q(uu[d0]),
            residual=q(resid[d0]), proxy=per_inst[t]["proxy"],
            weight_lagged=q(w_lag), contribution=q(w_lag * rr[d0]),
            window="holdout" if d0 >= BOUNDARY else "primary",
            screen="residual" if fl_res[d0] else "absolute return",
            note="the implied multiple is not computed, the underlying's move being "
                 "below the floor" if lowmask[d0] else "")
add("B1_summary", item="instruments_screened", value=len(HELD))
add("B1_summary", item="sessions_screened", value=screened,
    note="instrument-sessions on which a registered multiple and a proxy return both "
         "exist")
add("B1_summary", item="sessions_flagged", value=flags,
    note=f"a selectivity of {flags/screened:.8f}" if screened else "")
add("B1_summary", item="sessions_below_the_underlying_floor", value=low_u,
    note="screened on absolute return instead of on the implied multiple")
add("B1_summary", item="benchmarks_with_no_frozen_proxy",
    value=len(set(no_proxy)), note="; ".join(sorted({f"{a} {b}" for a, b in no_proxy})
                                             ) or "none")

# the three session 29 volatility flags under this sweep's rule
for t, dt in (("SVXY", "2018-02-06"), ("UVXY", "2018-02-05"), ("UVXY", "2020-03-16")):
    d0 = pd.Timestamp(dt)
    still = d0 in per_inst.get(t, {}).get("dates", [])
    add("proxy_limitation", item=f"{t} {dt}", value=int(still),
        note="remains flagged under the sweep's rule" if still else
             "no longer flagged under the sweep's rule. Recorded as a proxy limitation "
             "rather than a defect, the constant-maturity series being an imperfect "
             "stand-in for a front-month-tracking product")

# ================================ B2 ==============================================
DEC = list(csv.DictReader(open(ROOT / "outputs" / "session-28" /
                               "holdout-decomposition.csv")))


def dec(t, i, w):
    for r in DEC:
        if r["table"] == t and r["item"] == i and r["window"] == w:
            return r["value"]
    return None


contrib = {}
for r in DEC:
    if r["table"] == "instrument":
        contrib.setdefault(r["window"], {})[r["item"]] = float(r["value"])
WSUM = {w: float(dec("window", f"{w}_arithmetic_return_sum", "")) for w in
        ("holdout", "primary")}
flag_contrib = {}
for r in rows:
    if r["table"] == "flagged_session":
        k = (r["item"], r["window"])
        flag_contrib[k] = flag_contrib.get(k, 0.0) + float(r["contribution"])
for w in ("holdout", "primary"):
    ranked = sorted(contrib.get(w, {}), key=lambda k: -abs(contrib[w][k]))
    for rk, t in enumerate(ranked, 1):
        fc = flag_contrib.get((t, w), 0.0)
        add("contribution_rank", item=t, window=w, rank=rk,
            value=q(contrib[w][t]), n_flagged=per_inst.get(t, {}).get("flagged", 0),
            flagged_contribution=q(fc),
            share_of_window=q(abs(fc) / WSUM[w]) if WSUM[w] else "",
            note="read from outputs/session-28/holdout-decomposition.csv rather than "
                 "recomputed")
    tot_fc = sum(v for (t, ww), v in flag_contrib.items() if ww == w)
    add("B2_summary", item="cumulative_flagged_contribution", window=w, value=q(tot_fc),
        note=f"against the window's arithmetic return sum of {WSUM[w]!r}, a share of "
             f"{abs(tot_fc)/WSUM[w]!r}" if WSUM[w] else "")
    mat = [t for (t, ww), v in flag_contrib.items()
           if ww == w and WSUM[w] and abs(v) / WSUM[w] > 0.05]
    add("B2_summary", item="instruments_material_under_the_gate", window=w,
        value=len(mat), note="; ".join(sorted(mat)) or
        "none. Materiality was fixed at 5 percent of the window's arithmetic return sum "
        "before the flags were seen")
for t in ("TQQQ",):
    for w in ("holdout", "primary"):
        add("B2_named", item=t, window=w, value=q(contrib[w].get(t, 0.0)),
            n_flagged=per_inst.get(t, {}).get("flagged", 0),
            flagged_contribution=q(flag_contrib.get((t, w), 0.0)),
            note="named explicitly because an unrecorded adjustment here moves the "
                 "result where one in a zero-weight instrument does not")

# ================================ B3 ==============================================
src = (ROOT / "src" / "sleeves.py").read_text()
tree = ast.parse(src)
fns = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
       if isinstance(n, ast.FunctionDef)]
LOOKBACK = {"rs": config.RSI_PERIOD_RELATIVE_STRENGTH,
            "rsi_dip": config.RSI_PERIOD_DIP,
            "rsi_exhaustion": config.RSI_PERIOD_EXHAUSTION,
            "trailing_return_pct": config.CRASH_HORIZON_SESSIONS}
reads = []
for n in ast.walk(tree):
    fn = None
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
        fn = n.func.id
    elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
        fn = n.func.attr
    if fn not in ("rs", "sma", "rsi_dip", "rsi_exhaustion", "trailing_return_pct",
                  "price"):
        continue
    lits = [a.value for a in n.args if isinstance(a, ast.Constant)
            and isinstance(a.value, str)]
    nums = [a.value for a in n.args if isinstance(a, ast.Constant)
            and isinstance(a.value, int)]
    attrs = [a.attr for a in n.args if isinstance(a, ast.Attribute)]
    if not lits:
        for a in n.args:
            if isinstance(a, ast.Attribute) and a.attr == "TREND_SIGNAL_SERIES":
                lits = [config.TREND_SIGNAL_SERIES]
    if not lits:
        continue
    lb = (nums[0] if nums else
          getattr(config, attrs[0], None) if attrs else LOOKBACK.get(fn))
    own = min((f for f in fns if f[0] <= n.lineno <= f[1]), key=lambda f: f[1] - f[0])
    for t in lits:
        reads.append((t, fn, lb, n.lineno, own[2]))
reads = sorted(set(reads), key=lambda x: x[3])
for t, fn, lb, ln, own in reads:
    add("indicator_read", item=t, indicator=fn, lookback=lb,
        value=f"src/sleeves.py:{ln}", note=f"inside {own}")
POSITIONS = set()
for n in ast.walk(tree):
    if isinstance(n, ast.Dict):
        for k in n.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                POSITIONS.add(k.value)
    if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant) \
            and isinstance(n.value.value, str):
        POSITIONS.add(n.value.value)
SIGNALS = {t for t, *_ in reads}
TERM = pd.read_parquet(ROOT / "outputs" / "session-28" / "_terminals.parquet")
SIG = pd.read_parquet(ROOT / "outputs" / "session-28" / "_signal_rows.parquet")
breaks = sorted({(r["item"], r["date"]) for r in rows
                 if r["table"] == "flagged_session"})
longest = 0
for t, dt in breaks:
    d0 = pd.Timestamp(dt)
    role = ("both" if t in POSITIONS and t in SIGNALS else
            "position" if t in POSITIONS else
            "signal input" if t in SIGNALS else "neither")
    add("break_role", item=t, date=dt, value=role,
        note="from src/sleeves.py, a position being a ticker appearing in a returned "
             "weight dictionary and a signal input being a ticker an indicator reads")
    my = [(fn, lb, ln) for tt, fn, lb, ln, _ in reads if tt == t]
    if not my:
        add("contamination", item=t, date=dt, value=0,
            note="no indicator reads this instrument, so no indicator window spans the "
                 "break")
        continue
    for fn, lb, ln in my:
        if lb is None:
            add("contamination", item=t, date=dt, indicator=fn, value="",
                note=f"lookback not resolvable at src/sleeves.py:{ln}")
            continue
        after = IDX[(IDX > d0)]
        n_cont = int(min(len(after), lb - 1))
        longest = max(longest, n_cont)
        span = after[:n_cont]
        fired = 0
        if len(span):
            ch = SIG["changed"].reindex(span).fillna(0)
            fired = int(ch.sum())
        add("contamination", item=t, date=dt, indicator=fn, lookback=lb,
            value=n_cont, n_terminal_firings=fired,
            note=f"sessions after the break on which a {fn} window of {lb} spans it, "
                 f"with {fired} of them carrying a terminal transition")
add("B3_summary", item="breaks_examined", value=len(breaks))
add("B3_summary", item="longest_contaminated_span", value=longest,
    note=f"sma_long at {config.SMA_LONG} sessions sets the outer bound for any "
         f"instrument an SMA reads")
cont_fire = sum(int(r.get("n_terminal_firings") or 0) for r in rows
                if r["table"] == "contamination" and r.get("n_terminal_firings"))
add("B3_summary", item="contaminated_sessions_coinciding_with_a_terminal_firing",
    value=cont_fire,
    note="a terminal transition inside a contaminated indicator window, being the "
         "condition gate B tests")

# ================================ B4 ==============================================
fn_neg, fp_neg = 0, 0
for t in HELD:
    p = ROOT / "data" / "raw" / "etf" / f"{t}.parquet"
    if not p.exists():
        continue
    fr = pd.read_parquet(p)
    fr.index = pd.DatetimeIndex(fr.index).tz_localize(None).normalize()
    if "Stock Splits" not in fr.columns:
        add("split_column", item=t, value="absent",
            note="the frozen record carries no Stock Splits column")
        continue
    sp = fr["Stock Splits"].astype(float)
    ev = sp[(sp != 0) & sp.notna()]
    cl = fr["Close"].astype(float)
    step = (cl / cl.shift(1)).reindex(IDX)
    for d0, ratio in ev.items():
        if d0 < IDX.min() or d0 > IDX.max():
            continue
        near = step.loc[max(IDX.min(), d0 - pd.Timedelta(days=5)):
                        min(IDX.max(), d0 + pd.Timedelta(days=5))]
        disc = bool((near.dropna() < 0.75).any() or (near.dropna() > 1.33).any())
        add("recorded_split", item=t, date=str(d0.date()), value=q(ratio),
            matching_discontinuity=int(disc),
            note="" if disc else "recorded split with NO matching price discontinuity, "
                                 "so the price series is already adjusted for it")
        if not disc:
            fn_neg += 1
    # discontinuities with no recorded split
    d_mask = step.notna() & ((step < 0.60) | (step > 1.67))
    for d0 in IDX[d_mask.reindex(IDX).fillna(False)]:
        has = bool(((ev.index >= d0 - pd.Timedelta(days=5))
                    & (ev.index <= d0 + pd.Timedelta(days=5))).any())
        if not has:
            fp_neg += 1
            add("discontinuity_without_split", item=t, date=str(d0.date()),
                value=q(step[d0]),
                note="a close-to-close price step beyond the 0.60 to 1.67 band with no "
                     "recorded corporate action within five days")
add("B4_summary", item="recorded_splits_with_no_price_discontinuity", value=fn_neg,
    note="the price series is already adjusted for these, which is the expected state "
         "for an adjusted series rather than a defect")
add("B4_summary", item="price_discontinuities_with_no_recorded_split", value=fp_neg,
    note="the split column's false-negative count across the study's own held "
         "instruments, being the class the SOXS defect belongs to")

# ================================ break classification ==============================
# A BREAK is a price discontinuity outside the 0.60 to 1.67 band with no recorded
# corporate action within five days AND flagged by the residual screen. Both
# components were written before the run. The conjunction is what their
# construction implies, since a session the residual screen clears is by
# definition consistent with the registered multiple times the underlying's move
# and is therefore a market move rather than an adjustment artifact. The band on
# its own gives false positives for a 3x fund whenever the underlying moves beyond
# about 13 percent, which is why the two are conjoined rather than either alone.
flagged_set = {(r["item"], r["date"]) for r in rows if r["table"] == "flagged_session"}
disc = [(r["item"], r["date"], r["value"]) for r in rows
        if r["table"] == "discontinuity_without_split"]
break_inst = set()
for t, dt, step in disc:
    is_break = (t, dt) in flagged_set
    if is_break:
        break_inst.add(t)
    add("break_classification", item=t, date=dt, value=int(is_break),
        note=("BREAK. The price step is outside the band and the residual screen also "
              "flags it, so the registered multiple times the underlying's move does "
              "not account for it")
        if is_break else
        ("market move. The price step is outside the band because the underlying moved "
         "far enough that the registered multiple carries the fund past it, and the "
         "residual screen clears the session, so no adjustment artifact is present"))
add("B4_summary", item="breaks_after_conjoining_the_two_screens", value=len(disc) and
    sum(1 for t, dt, _ in disc if (t, dt) in flagged_set),
    note="; ".join(f"{t} {dt}" for t, dt, _ in disc if (t, dt) in flagged_set) or "none")

# ================================ gate B ===========================================
# The gate as the scaffold states it is CONJUNCTIVE, being a break IN an instrument
# contributing materially. Both evaluations are recorded, since the first
# implementation tested materiality alone and would have halted on UVXY, which
# carries no break.
mat = {(r["window"], t) for r in rows if r["table"] == "B2_summary"
       and r["item"] == "instruments_material_under_the_gate" and int(r["value"]) > 0
       for t in r["note"].split("; ") if t and not t.startswith("none")}
mat_inst = {t for _, t in mat}
both = sorted(break_inst & mat_inst)
halt = bool(both) or cont_fire > 0
add("gate_B", item="instruments_with_a_break", value=len(break_inst),
    note=", ".join(sorted(break_inst)) or "none")
add("gate_B", item="instruments_material_by_flagged_contribution", value=len(mat_inst),
    note=", ".join(sorted(mat_inst)) or "none")
add("gate_B", item="instruments_with_both", value=len(both),
    note=", ".join(both) or "none, so no break sits in a material instrument")
add("gate_B", item="contaminated_session_coinciding_with_a_firing", value=cont_fire)
add("gate_B", item="verdict_materiality_alone", value="HALT" if mat_inst else "PROCEED",
    note="the first implementation tested materiality without conjoining the break "
         "condition and would have halted on " + (", ".join(sorted(mat_inst)) or "none"))
add("gate_B", item="verdict", value="HALT" if halt else "PROCEED",
    note="the gate as the scaffold states it, being a break in an instrument "
         "contributing materially. " +
         ("the session halts before phase C" if halt else
          "no break sits in a material instrument and no contaminated indicator session "
          "coincides with a terminal firing, so phases C through H proceed"))
add("gate_B", item="materiality_definition_unchanged", value=0.05,
    note="the 5 percent threshold fixed at 9.82 before the flags were seen is not "
         "moved. Only the conjunction the scaffold states was added to the "
         "implementation")

fnames = ["table", "item", "window", "date", "value", "rank", "n_screened",
          "n_low_underlying", "n_flagged", "flagged_contribution", "share_of_window",
          "implied_multiple", "registered_multiple", "underlying_return", "residual",
          "proxy", "weight_lagged", "contribution", "screen", "indicator", "lookback",
          "n_terminal_firings", "matching_discontinuity", "note"]
with open(OUT / "corporate-action-sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote corporate-action-sweep.csv, {len(rows)} rows")
print(f"  screened {screened} instrument-sessions, flagged {flags}")
print(f"  breaks examined {len(breaks)}, contaminated sessions with a firing {cont_fire}")
print(f"  split column false negatives {fp_neg}, already-adjusted recorded splits {fn_neg}")
print(f"  GATE B {'HALT' if halt else 'PROCEED'}")
sys.exit(0)
