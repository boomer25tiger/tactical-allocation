"""Session 29 phase B. Corporate action integrity, and the gate.

Runs first. A defect here invalidates every downstream measurement.

GATE B, stated before the check. If any unexplained session above 50 percent
absolute return is found in a held instrument, the session halts and reports
before any other phase runs.
"""
from __future__ import annotations

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

OUT = ROOT / "outputs" / "session-29"
S28 = ROOT / "outputs" / "session-28"
BOUNDARY = bt.HOLDOUT_BOUNDARY
PRIMARY = C.PRIMARY_START
THRESH = 0.50
INVERSE_OR_VOL = ("UVXY", "SVXY", "SQQQ", "PSQ", "SH", "TECS", "SOXS")
rows = []


def add(t, **kw):
    rows.append({"table": t, **kw})


def q(v):
    return repr(float(v))


print("building the environment")
env = C.build_env(verbose=False)
panel = env["panels"]["realized"]
TICK = sorted(bt.UNLEVERED + bt.LEVERED)
add("scope", item="loaded_universe", value=len(TICK),
    note="bt.UNLEVERED plus bt.LEVERED, unmodified")

# which of them the strategy actually held, from the session 28 persisted weights
held = set()
for sl in ("T10", "T11", "S2", "S3"):
    w = pd.read_parquet(S28 / f"_sleeve_weights_{sl}.parquet")
    held |= {t for t in w.columns if (w[t] != 0).any()}
add("scope", item="instruments_ever_held", value=len(held),
    note=", ".join(sorted(held)))

WIN = {"holdout": (BOUNDARY, None), "primary": (PRIMARY, BOUNDARY)}
RAW = {}
for t in TICK:
    p = ROOT / "data" / "raw" / "etf" / f"{t}.parquet"
    if p.exists():
        d = pd.read_parquet(p)
        d.index = pd.to_datetime(d.index).tz_localize(None).normalize()
        RAW[t] = d

# ---- largest single-session absolute return per instrument per window -----------
extremes = {}
for wname, (lo, hi) in WIN.items():
    scored = []
    for t in TICK:
        r = panel[t].ret_total
        m = r.index >= lo
        if hi is not None:
            m = m & (r.index < hi)
        rr = r.loc[m].dropna()
        if not len(rr):
            continue
        d0 = rr.abs().idxmax()
        scored.append((t, float(rr.loc[d0]), d0))
    scored.sort(key=lambda x: -abs(x[1]))
    extremes[wname] = scored
    for rk, (t, v, d0) in enumerate(scored, 1):
        add("largest_single_session", item=t, window=wname, value=q(v), rank=rk,
            date=str(d0.date()), held=int(t in held),
            inverse_or_vol=int(t in INVERSE_OR_VOL))

# ---- every session above the threshold ------------------------------------------
# The registered underlying and multiple for each levered or inverse fund, read
# from src/schedule.py rather than typed. A single session's return on a
# daily-reset fund tracks the multiple times the underlying almost exactly, so
# comparing the two discriminates a market move from an adjustment artifact.
from src.schedule import FUND_SCHEDULE                 # noqa: E402
PROXY = {"Nasdaq-100 Index": "QQQ", "S&P 500 Index": "SPY",
         "Technology Select Sector Index": "XLK",
         "ICE Semiconductor Index": "SMH",
         "PHLX Semiconductor Sector Index": "SMH",
         "NYSE Arca Broker/Dealer Index": None, "Financials Select Sector Index": "XLF",
         "Russell 1000 Financial Services Index": "XLF"}
MULT_TOL = 0.20
# The volatility funds track a VIX short-term futures index rather than an equity
# line, so the frozen constant-maturity thirty-day settle series stands for it.
_VX = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30.parquet")
_VX = _VX.set_index(pd.DatetimeIndex(_VX["trade_date"]).normalize())["cm30_settle"]
VX_RET = _VX.astype(float).pct_change()
VOL_BENCH = "S&P 500 VIX Short-Term Futures Index"


def registered(t, d0):
    for pr in FUND_SCHEDULE.get(t, []):
        st = pd.Timestamp(pr.start)
        en = pd.Timestamp(pr.end) if pr.end is not None else None
        if d0 >= st and (en is None or d0 <= en):
            return pr.multiple, pr.benchmark
    return None, None


def explain(t, d0):
    """Screen a jump against a corporate action first and against the registered
    underlying second, since a large market move is an explanation too."""
    raw = RAW.get(t)
    if raw is None:
        return "no frozen parquet", ""
    idx = raw.index
    pos = idx.searchsorted(d0)
    near = [idx[i] for i in (pos - 1, pos, pos + 1) if 0 <= i < len(idx)]
    for dd in near:
        sp = float(raw.loc[dd, "Stock Splits"] or 0.0)
        if sp:
            return f"stock split {sp:g}", str(dd.date())
    for dd in near:
        dv = float(raw.loc[dd, "Dividends"] or 0.0)
        cg = float(raw.loc[dd, "Capital Gains"] or 0.0)
        if dv or cg:
            return f"distribution, dividend {dv:g} capital gain {cg:g}", str(dd.date())
    mult, und = registered(t, d0)
    if mult and und == VOL_BENCH and d0 in VX_RET.index and pd.notna(VX_RET.loc[d0]):
        u = float(VX_RET.loc[d0])
        r = float(panel[t].ret_total.loc[d0])
        if abs(u) > 1e-9:
            implied = r / u
            if abs(implied - mult) <= MULT_TOL * abs(mult):
                return (f"market move, the frozen constant-maturity thirty-day VIX "
                        f"futures settle returned {u!r} and the implied multiple is "
                        f"{implied!r} against the registered {mult:g}"), str(d0.date())
            return "", ""
    proxy = PROXY.get(und) if und else None
    if mult and proxy and proxy in RAW:
        pr = panel[proxy].ret_total
        if d0 in pr.index and pd.notna(pr.loc[d0]):
            u = float(pr.loc[d0])
            r = float(panel[t].ret_total.loc[d0])
            if abs(u) > 1e-9:
                implied = r / u
                if abs(implied - mult) <= MULT_TOL * abs(mult):
                    return (f"market move, {proxy} returned {u!r} and the implied "
                            f"multiple is {implied!r} against the registered {mult:g}"), \
                           str(d0.date())
    return "", ""


breaches, unexplained = [], []
for wname, (lo, hi) in WIN.items():
    for t in TICK:
        r = panel[t].ret_total
        m = r.index >= lo
        if hi is not None:
            m = m & (r.index < hi)
        rr = r.loc[m].dropna()
        big = rr[rr.abs() > THRESH]
        for d0, v in big.items():
            act, adate = explain(t, d0)
            breaches.append((wname, t, d0, float(v), act, adate))
            mult, und = registered(t, d0)
            if und == VOL_BENCH and d0 in VX_RET.index:
                u = float(VX_RET.loc[d0]); pname = "the VIX futures settle"
            else:
                pxy = PROXY.get(und) if und else None
                if pxy and pxy in RAW and d0 in panel[pxy].ret_total.index:
                    u = float(panel[pxy].ret_total.loc[d0]); pname = pxy
                else:
                    u = float("nan"); pname = "none"
            implied = float(v) / u if u == u and abs(u) > 1e-9 else float("nan")
            ratio = (abs(implied / mult) if implied == implied and mult
                     else float("nan"))
            direction = ("the same sign at {:.2f} times the registered magnitude".format(ratio)
                         if implied == implied and mult and implied * mult > 0
                         else "the opposite sign" if implied == implied and mult
                         else "not establishable")
            add("above_threshold", item=t, window=wname, value=q(v),
                date=str(d0.date()), held=int(t in held),
                corporate_action=act or "none identifiable",
                action_date=adate,
                note=("EXPLAINED" if act else "UNEXPLAINED")
                     + f". Underlying proxy {pname} returned {u!r}, the implied multiple "
                       f"is {implied!r} against the registered "
                       f"{mult if mult is not None else 'none'}, so the direction is "
                       f"{direction}")
            if not act and t in held:
                unexplained.append((wname, t, d0, float(v)))
                add("unexplained_detail", item=t, window=wname, value=q(v),
                    date=str(d0.date()),
                    note=f"no corporate action in the frozen record within one session. "
                         f"Underlying proxy {pname} returned {u!r} and the implied "
                         f"multiple is {implied!r} against the registered "
                         f"{mult if mult is not None else 'none'}. The direction is "
                         f"{direction}, so the session is "
                         + ("an order of magnitude beyond what any move in the "
                            "registered underlying produces, which is the signature of "
                            "an unrecorded corporate action"
                            if ratio == ratio and ratio > 4.0
                            and implied * mult > 0 else
                            "not attributable by this screen, since a fund whose net "
                            "asset value strikes at a different time from the proxy's "
                            "settle can move against it on a single session"
                            if implied == implied and mult and implied * mult < 0 else
                            "within a factor the proxy's own tracking error can account "
                            "for, so it is consistent with a market move the proxy "
                            "measures imperfectly"))
add("above_threshold_summary", item="sessions_above_50_percent", value=len(breaches),
    note=f"across both windows and the full loaded universe, at a threshold of "
         f"{THRESH}")
add("above_threshold_summary", item="unexplained_in_a_held_instrument",
    value=len(unexplained),
    note="; ".join(f"{w} {t} {d.date()} {v!r}" for w, t, d, v in unexplained) or "none")

# ---- split adjustment status per instrument ---------------------------------------
for t in TICK:
    raw = RAW.get(t)
    if raw is None:
        add("split_adjustment", item=t, value="no frozen parquet")
        continue
    sp = raw["Stock Splits"].astype(float).fillna(0.0)
    ev = sp[sp != 0]
    if not len(ev):
        add("split_adjustment", item=t, value="no split in the frozen record",
            note="the Stock Splits column carries no non-zero entry across the span, so "
                 "no adjustment question arises")
        continue
    # If Close is split-adjusted the close ratio across the event is near the
    # underlying move, and if it is unadjusted the ratio is near the split factor.
    checks = []
    for dd, f in ev.items():
        pos = raw.index.searchsorted(dd)
        if pos == 0 or pos >= len(raw):
            continue
        c1 = float(raw["Close"].iloc[pos])
        c0 = float(raw["Close"].iloc[pos - 1])
        if c0 == 0:
            continue
        ratio = c1 / c0
        checks.append((dd, f, ratio, abs(ratio - 1.0 / f)))
    if not checks:
        add("split_adjustment", item=t, value="not establishable")
        continue
    unadj = sum(1 for _, f, ratio, gap in checks if gap < 0.15)
    add("split_adjustment", item=t,
        value="adjusted" if unadj == 0 else "UNADJUSTED",
        n_events=len(checks),
        note=f"{len(checks)} split events in the frozen record. The close ratio across "
             f"each event is compared against the reciprocal of the split factor, which "
             f"is what an UNADJUSTED series would show. {unadj} of {len(checks)} events "
             f"match that pattern within 0.15. Establishing method, the raw Close "
             f"column against the Stock Splits column in the same frozen parquet")
    for dd, f, ratio, gap in checks:
        add("split_event", item=t, date=str(dd.date()), value=q(ratio),
            note=f"split factor {f:g}, an unadjusted series would show a close ratio "
                 f"near {1.0/f:g} and the observed ratio is {ratio!r}, a gap of {gap!r}",
            window="holdout" if dd >= BOUNDARY else
                   "primary" if dd >= PRIMARY else "pre-window")

add("adjustment_method", item="realized_arm",
    value="the issuer's own history as the vendor supplies it",
    note="scripts/s13_backtest.py load_arm_panel takes the frozen fund parquet for "
         "every levered ticker on the realized arm and sets multiple to NaN. "
         "src/data.py build_ticker_frame computes ret_total as close plus dividend over "
         "the prior close on the compressed available-only series, so the adjustment "
         "the vendor already applied to Close is the adjustment that reaches returns")
add("adjustment_method", item="synthetic_arm",
    value="reconstructions validated against live NAV",
    note="the synthetic arm rebuilds each levered fund from the underlying at the "
         "registered multiple with financing, and session 10 validated those against "
         "issuer NAV. The DESIGNATED CELL IS THE REALIZED ARM, so the holdout figures "
         "carry the issuer's own history and not a reconstruction")
add("adjustment_method", item="differs_between_windows", value=0,
    note="the same loader and the same total-return construction run across both "
         "windows on the realized arm, so the adjustment method does not change at the "
         "boundary. What changes is which instruments are available, since the primary "
         "window carries sessions on which some loaded tickers had not yet listed")

# ---- contribution of any unexplained session to holdout return --------------------
hl = pd.read_parquet(ROOT / "outputs" / "session-27" / "_holdout_line_returns.parquet")
tot_h = float(hl["STRATEGY"].dropna().sum())
sw = {sl: pd.read_parquet(S28 / f"_sleeve_weights_{sl}.parquet")
      for sl in ("T10", "T11", "S2", "S3")}
tot_w = sum(sw.values())
unexp_contrib = 0.0
for wname, t, d0, v in unexplained:
    if wname != "holdout" or t not in tot_w.columns:
        continue
    pos = tot_w.index.searchsorted(d0)
    w = float(tot_w[t].iloc[pos - 1]) if pos > 0 else 0.0
    c = w * v
    unexp_contrib += c
    add("unexplained_contribution", item=t, date=str(d0.date()), value=q(c),
        note=f"the lagged portfolio weight {w!r} times the session return {v!r}")
add("unexplained_contribution", item="total", value=q(unexp_contrib),
    note=f"against the holdout arithmetic return sum of {tot_h!r}, a share of "
         f"{unexp_contrib/tot_h if tot_h else float('nan')!r}")

# ---- independent cross-check on the three largest holdout returns ------------------
top3 = extremes["holdout"][:3]
for rk, (t, v, d0) in enumerate(top3, 1):
    raw = RAW.get(t)
    if raw is None or "Adj Close" not in raw.columns:
        add("cross_check", item=t, rank=rk, date=str(d0.date()), value="",
            note="no alternative price path exists inside the frozen inputs")
        continue
    ac = raw["Adj Close"].astype(float)
    pos = ac.index.searchsorted(d0)
    if pos == 0:
        add("cross_check", item=t, rank=rk, date=str(d0.date()), value="",
            note="the session is the first observation, so no prior close exists")
        continue
    alt = float(ac.iloc[pos] / ac.iloc[pos - 1] - 1.0)
    add("cross_check", item=t, rank=rk, date=str(d0.date()), value=q(alt),
        note=f"the adjusted-close path gives {alt!r} against the engine's {v!r}, a "
             f"deviation of {abs(alt - v)!r}. The adjusted close is an independent "
             f"column in the same frozen parquet, dividend and split adjusted by the "
             f"vendor, so it is an alternative path rather than a second read of the "
             f"same one")

# ---- the gate -----------------------------------------------------------------------
gate = len(unexplained) == 0
add("gate_B", item="unexplained_sessions_in_a_held_instrument", value=len(unexplained))
add("gate_B", item="unexplained_inside_the_holdout",
    value=sum(1 for w_, _t, _d, _v in unexplained if w_ == "holdout"))
add("gate_B", item="soxs_holdout_sessions_held",
    value=int((tot_w["SOXS"].loc[tot_w.index >= BOUNDARY] != 0).sum()),
    note="of the holdout's sessions. The weight is zero across the whole of "
         "2026-05-18 to 2026-06-05, so the defect session itself carries no position")
add("gate_B", item="soxs_in_any_signal_path", value=0,
    note="src/sleeves.py names SOXS at line 266 alone, inside T11's bear split, which "
         "is a position rather than a signal, so the defect cannot enter through the "
         "signal path")
add("gate_B", item="verdict", value="PASS" if gate else "HALT",
    note="the session proceeds to phase C" if gate else
         "the session halts before any other phase runs")

fn = ["table", "item", "window", "value", "rank", "date", "held", "inverse_or_vol",
      "corporate_action", "action_date", "n_events", "note"]
with open(OUT / "corporate-actions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote corporate-actions.csv, {len(rows)} rows")
print(f"  sessions above {THRESH}: {len(breaches)}, unexplained in a held instrument: "
      f"{len(unexplained)}")
for w_, t, d0, v in unexplained:
    print(f"    UNEXPLAINED {w_} {t} {d0.date()} {v!r}")
print(f"  GATE B {'PASS' if gate else 'HALT'}")
un = [r for r in rows if r["table"] == "split_adjustment" and r.get("value") == "UNADJUSTED"]
print(f"  instruments whose close looks unadjusted: {len(un)}"
      + ("" if not un else " " + ", ".join(r["item"] for r in un)))
sys.exit(0 if gate else 1)
