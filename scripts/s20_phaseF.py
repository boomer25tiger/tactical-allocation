"""Session 20 phase F. The January 2013 event, attributed rather than asserted."""
from __future__ import annotations
import ast, csv, re, resource, sys, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
OUT = ROOT / "outputs" / "session-20"
SPAN0, SPAN1 = pd.Timestamp("2013-01-02"), pd.Timestamp("2013-01-22")
WINDOW, THRESH = 14, -0.15
t0 = time.time()
rows = []


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


env = C.build_env(verbose=False)
cal, sigs, o2o, cap_fn = env["cal"], env["sigs"], env["o2o"], env["cap_fn"]
sig = sigs["realized"]
acc = bt.run_account(sig["sig"], o2o, sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=cap_fn)
daily = acc["daily"]
pos = {d: i for i, d in enumerate(cal)}
by_i = {r["i"]: r for r in sig["rows"]}
SLEEVES = list(sig["rows"][0]["sleeves"].keys())

# terminal labels from the session 18 census, matched on the returned ticker set
cen = pd.read_csv(ROOT / "outputs/session-18/reachability.csv")
cen = cen[cen.table == "census"]
tmap = {}
for sl, term in cen[["sleeve", "terminal"]].drop_duplicates().itertuples(index=False):
    m = re.search(r"return (\{.*\}|\"[A-Z]+\")", str(term))
    if not m:
        continue
    body = m.group(1)
    try:
        ks = frozenset(ast.literal_eval(body).keys()) if body.startswith("{") \
            else frozenset({ast.literal_eval(body)})
    except (ValueError, SyntaxError):
        ks = frozenset(re.findall(r'"([A-Z]{2,5})"', body)) | \
             ({"SVXY","SVIX"} if "vol_short" in body else set()) | \
             ({"UVXY","UVIX"} if re.search(r"\bvol\b", body) else set())
    tmap.setdefault((str(sl), ks), str(term))


def label(sl, wd):
    ks = frozenset(t for t, v in wd.items() if v)
    lab = tmap.get((sl, ks))
    if lab is None:
        cand = sorted({v for (s2, k2), v in tmap.items() if s2 == sl and ks < k2})
        lab = cand[0] if len(cand) == 1 else f"UNMATCHED {sorted(ks)}"
    return lab


span = daily.index[(daily.index >= SPAN0) & (daily.index <= SPAN1)]
print(f"span {span[0].date()} to {span[-1].date()}, {len(span)} sessions")
cum = 1.0
sleeve_tot = {s: 0.0 for s in SLEEVES}
inst_tot = {}
for d in span:
    ret = float(daily["ret"].loc[d])
    cum *= (1.0 + ret)
    w = daily["weights"].loc[d]
    w = {k: float(v) for k, v in w.items() if abs(float(v)) > 0} if isinstance(w, dict) else {}
    srow = by_i.get(pos[d] - 1)           # fill_lag=1, the prior signal produced today
    owner, labs = {}, {}
    if srow:
        for s in SLEEVES:
            sw = srow["sleeves"].get(s)
            if sw is None:
                labs[s] = "no emission"; continue
            labs[s] = label(s, sw)
            for t in sw:
                owner.setdefault(t, []).append(s)
    for t, wt in w.items():
        r_t = o2o[t].ret_total.reindex([d]).iloc[0] if t in o2o.frames else np.nan
        contrib = wt * (0.0 if pd.isna(r_t) else float(r_t))
        inst_tot[t] = inst_tot.get(t, 0.0) + contrib
        for s in owner.get(t, []):
            sleeve_tot[s] += contrib / len(owner[t])
        rows.append({"table": "session_instrument", "date": str(d.date()), "item": t,
                     "weight": wt, "instrument_return": None if pd.isna(r_t) else float(r_t),
                     "contribution": contrib,
                     "sleeves": " ".join(owner.get(t, ["unattributed"]))})
    rows.append({"table": "session", "date": str(d.date()), "item": "daily_return",
                 "contribution": ret,
                 "note": " | ".join(f"{s}: {labs.get(s,'')}" for s in SLEEVES),
                 "sleeves": " ".join(f"{t}={v:.4f}" for t, v in sorted(w.items()))})
cum_ret = cum - 1.0
rows.append({"table": "span", "item": "cumulative_return", "contribution": cum_ret})
rows.append({"table": "span", "item": "n_sessions", "weight": len(span)})
print(f"cumulative {cum_ret:.6f}")

print("\nattribution by sleeve, arithmetic contribution summed over the span")
for s in SLEEVES:
    rows.append({"table": "sleeve_attribution", "item": s, "contribution": sleeve_tot[s]})
    print(f"  {s:<6} {sleeve_tot[s]:+.6f}")
neg = [s for s in SLEEVES if sleeve_tot[s] < 0]
uvxy_sleeves = set()
for r in rows:
    if r["table"] == "session_instrument" and r["item"] == "UVXY":
        uvxy_sleeves |= set(r["sleeves"].split())
rows.append({"table": "attribution_test", "item": "sleeves_with_negative_contribution",
             "weight": len(neg), "note": " ".join(neg)})
rows.append({"table": "attribution_test", "item": "uvxy_sleeves",
             "weight": len(uvxy_sleeves), "note": " ".join(sorted(uvxy_sleeves)),
             "note2": "UVXY appears across this many sleeves during the span"})
rows.append({"table": "attribution_test", "item": "verdict",
             "note": ("UVXY appears in more than one sleeve AND other sleeves lose "
                      "alongside" if len(uvxy_sleeves) > 1 and len(neg) > 1 else
                      "UVXY appears in one sleeve, so the loss requires other sleeves "
                      "losing alongside" if len(uvxy_sleeves) <= 1 else
                      "UVXY appears across more than one sleeve")})
print(f"  UVXY carried by sleeves {sorted(uvxy_sleeves)}, sleeves losing {neg}")
top = sorted(inst_tot.items(), key=lambda kv: kv[1])[:6]
for t, v in top:
    rows.append({"table": "instrument_attribution", "item": t, "contribution": v})
print("  worst instruments " + " ".join(f"{t}={v:+.4f}" for t, v in top))

# ---- every other 14-session window below the threshold -------------------
r_all = daily["ret"].loc[daily.index >= C.PRIMARY_START].dropna()
g = (1.0 + r_all).values
n = len(g)
cw = np.array([np.prod(g[i:i + WINDOW]) - 1.0 for i in range(n - WINDOW + 1)])
idx = r_all.index
hits = [(idx[i], idx[i + WINDOW - 1], cw[i]) for i in np.argsort(cw) if cw[i] < THRESH]
rows.append({"table": "drawdown_scan", "item": "window_sessions", "weight": WINDOW})
rows.append({"table": "drawdown_scan", "item": "threshold", "contribution": THRESH})
rows.append({"table": "drawdown_scan", "item": "n_windows_below_threshold",
             "weight": len(hits),
             "note": "overlapping windows across the primary window"})
for a, b, v in hits[:25]:
    rows.append({"table": "drawdown_window", "date": str(a.date()), "item": str(b.date()),
                 "contribution": float(v)})
jan_rank = None
for k, (a, b, v) in enumerate(hits, 1):
    if a <= SPAN0 <= b or a <= SPAN1 <= b:
        jan_rank = k; break
rows.append({"table": "drawdown_scan", "item": "january_2013_rank", "weight": jan_rank,
             "note": "rank of the first window overlapping the span among all windows "
                     "below the threshold, ordered most negative first"})
print(f"\n{len(hits)} overlapping 14-session windows below {THRESH}, "
      f"January 2013 ranks {jan_rank}")
if hits:
    print(f"  worst {hits[0][0].date()} to {hits[0][1].date()} at {hits[0][2]:.6f}")

# ---- strata tie and strip consequence ------------------------------------
st = list(csv.DictReader(open(ROOT / "outputs/session-19/pbo-strata.csv")))
ob = [r for r in st if r["table"] == "stratum" and r["axis"] == "overbought_t1"]
rng = [r for r in st if r["table"] == "axis_range" and r["axis"] == "overbought_t1"][0]
rows.append({"table": "strata_tie", "item": "overbought_t1_pbo_range",
             "note": f"{float(rng['pbo_min']):.4f} to {float(rng['pbo_max']):.4f}, the "
                     f"widest within-axis range of the six structural axes"})
can = [r for r in ob if r["is_canonical_value"] == "1"][0]
rows.append({"table": "strata_tie", "item": "canonical_stratum_pbo",
             "contribution": float(can["pbo"]),
             "note": "the canonical value on the same axis whose tier-one terminal "
                     "returns UVXY at full sleeve weight"})
ws = list(csv.DictReader(open(ROOT / "outputs/session-19_5/window-strip.csv")))
for r in ws:
    if r["table"] == "strip":
        inc = pd.Timestamp(r["start"]) <= SPAN0
        rows.append({"table": "strip_consequence", "item": r["item"], "date": r["start"],
                     "contribution": float(r["ann_return"]),
                     "note": "includes the event" if inc else "excludes the event"})
rows.append({"table": "strip_asymmetry", "item": "strategy",
             "note": "nested through run(sig[\"rows\"]) which takes no start argument, so "
                     "every arm slices one account"})
STATEFUL = ["vol_targeted_QQQ_matched", "naive_fast_1d_momentum", "long_legs_only",
            "sleeve_T10_standalone", "sleeve_T11_standalone", "sleeve_S2_standalone",
            "sleeve_S3_standalone"]
ENTRY_ONLY = ["buy_hold_QQQ", "buy_hold_TQQQ", "matched_exposure_levered_QQQ_1.70",
              "equal_weight_universe"]
rows.append({"table": "strip_asymmetry", "item": "benchmarks_reinitialised",
             "note": "each built through LINES[ln][0](o2o, sig[\"rows\"], i0) with the "
                     "per-arm entry index"})
rows.append({"table": "strip_asymmetry", "item": "lines_carrying_state",
             "weight": len(STATEFUL), "note": " ".join(STATEFUL),
             "note2": "these depend on a rolling estimate or on the strategy's own "
                      "signal stream, so re-entry changes their path rather than only "
                      "their start"})
rows.append({"table": "strip_asymmetry", "item": "lines_entry_only",
             "weight": len(ENTRY_ONLY), "note": " ".join(ENTRY_ONLY),
             "note2": "buy-and-hold or daily-constant, so re-entry moves only the "
                      "entry price"})
with open(OUT / "jan2013-attribution.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["table","date","item","weight",
                                        "instrument_return","contribution","sleeves",
                                        "note","note2"], extrasaction="ignore")
    wr.writeheader(); wr.writerows(rows)
print(f"\nwrote {OUT/'jan2013-attribution.csv'} with {len(rows)} rows")
print(f"phase F peak {rss():.3f} GB, {time.time()-t0:.1f}s")
