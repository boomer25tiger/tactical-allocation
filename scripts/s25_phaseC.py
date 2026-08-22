"""Session 25 phase C. Draw the eight figures set by phase B.

Every figure reads a committed artifact and emits the exact series it plots as a
CSV beside it at full round-trip precision, so the check in phase E compares
numbers rather than pixels. Nothing is recomputed that an emitted file already
carries. Where a figure derives a series from a committed return series, being
the equity and drawdown curves, phase E checks the derived value against the
emitted scalar.
"""
from __future__ import annotations
import csv, math, pickle, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s25_svg as V                              # noqa: E402
import scripts.s14_common as C14                         # noqa: E402
from scripts.s19_svg import Fig, L, T, PW, PH, FG        # noqa: E402
FIG = ROOT/"outputs"/"session-25"/"figures"; FIG.mkdir(parents=True, exist_ok=True)
made = []
def q(v): return repr(float(v))          # full round-trip precision in every emitted CSV


def done(name, fig, header, rows, source, period):
    V.caption(fig, source, period)
    (FIG/f"{name}.svg").write_text(fig.svg())
    with open(FIG/f"{name}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    n = (FIG/f"{name}.svg").stat().st_size
    made.append((name, n, len(rows)))
    print(f"  {name:26s} {n:>7} bytes  {len(rows):>5} plotted rows")


PKL = "outputs/session-20/rebuilt/_ladder_returns.pkl"
d = pickle.load(open(ROOT/PKL, "rb"))
KEYS = [("STRATEGY", d["strategy"][("o2o", "primary")]),
        ("buy_hold_QQQ", d["lines"][("buy_hold_QQQ", "o2o", "primary")]),
        ("matched_exposure_levered_QQQ_1.70",
         d["lines"][("matched_exposure_levered_QQQ_1.70", "o2o", "primary")])]
SER = []
for nm, s in KEYS:
    s = s.dropna()
    s = s.loc[s.index >= C14.PRIMARY_START]      # boundary read from the module, not typed
    SER.append((nm, [t.strftime("%Y-%m-%d") for t in s.index], [float(x) for x in s.values]))
assert len({len(x[1]) for x in SER}) == 1, "the three series differ in length"
DATES = SER[0][1]
PERIOD = f"{DATES[0]} to {DATES[-1]}, {len(DATES)} sessions"
YT = []
for i, dt in enumerate(DATES):
    if i == 0 or dt[:4] != DATES[i-1][:4]:
        YT.append((i, dt[:4]))
YT = [t for k, t in enumerate(YT) if k % 2 == 0]
print(f"loaded {PKL}, {PERIOD}")


def growth(rs):
    g, out = 1.0, []
    for r in rs:
        g *= (1.0 + r); out.append(g)
    return out


def ddown(gs):
    pk, out = -1e18, []
    for g in gs:
        pk = max(pk, g); out.append(g/pk - 1.0)
    return out


print("drawing")
# ---- 1 equity curve ----------------------------------------------------------
G = [(nm, growth(rs)) for nm, _, rs in SER]
xs = list(range(len(DATES)))
ys = [math.log10(v) for _, g in G for v in g]
f = Fig("Growth of one dollar, designated cell against two benchmark lines",
        "session date", "growth of one dollar, log base 10",
        (0, len(xs)-1), (min(ys), max(ys)))
V.axes2(f, xticks=YT, yfmt="{:.1f}")
for i, (nm, g) in enumerate(G):
    V.polyline(f, xs, [math.log10(v) for v in g], V.PAL[i], 1.5)
V.legend_box(f, [(f"{nm}, final {g[-1]:.3f} times", V.PAL[i])
                 for i, (nm, g) in enumerate(G)], L+14, T+18)
done("equity-curve", f, ["date"]+[nm for nm, _ in G],
     [[DATES[k]] + [q(g[k]) for _, g in G] for k in xs], PKL, PERIOD)

# ---- 2 drawdown --------------------------------------------------------------
D = [(nm, ddown(g)) for nm, g in G]
lo = min(v for _, dd in D for v in dd)
f = Fig("Drawdown from the running peak, designated cell against two benchmark lines",
        "session date", "drawdown, fraction of the running peak", (0, len(xs)-1), (lo, 0.0))
V.axes2(f, xticks=YT, yfmt="{:.2f}")
for i, (nm, dd) in enumerate(D):
    V.polyline(f, xs, dd, V.PAL[i], 1.3)
V.legend_box(f, [(f"{nm}, worst {min(dd):.6f}", V.PAL[i]) for i, (nm, dd) in enumerate(D)],
             L+14, T+PH-58)
done("drawdown", f, ["date"]+[nm for nm, _ in D],
     [[DATES[k]] + [q(dd[k]) for _, dd in D] for k in xs], PKL, PERIOD)

# ---- 3 cost sweep ------------------------------------------------------------
CS = "outputs/session-20/rebuilt/cost-sweep-designated.csv"
sw = [r for r in csv.DictReader(open(ROOT/CS)) if r["table"] == "sweep"]
F1 = [r for r in csv.DictReader(open(ROOT/"outputs/session-21/reads.csv"))
      if r["table"] == "F1" and "|" in r["item"]]
SHOW = ["STRATEGY", "buy_hold_QQQ", "buy_hold_TQQQ",
        "matched_exposure_levered_QQQ_1.70", "vol_targeted_QQQ_matched"]
SHORT = {"STRATEGY": "designated cell", "buy_hold_QQQ": "QQQ", "buy_hold_TQQQ": "TQQQ",
         "matched_exposure_levered_QQQ_1.70": "matched exposure",
         "vol_targeted_QQQ_matched": "vol targeted"}
bps = sorted({float(r["slippage_bp"]) for r in sw})
cur = {ln: [float(next(r["sharpe_naive"] for r in sw
                       if r["line"] == ln and float(r["slippage_bp"]) == b)) for b in bps]
       for ln in SHOW}
allv = [v for c in cur.values() for v in c]
f = Fig("Naive Sharpe against uniform round-turn cost, with the benchmark crossings",
        "uniform round-turn cost, basis points", "naive Sharpe, annualised",
        (0, 50), (min(allv)-0.005, max(allv)+0.005))
V.axes2(f, yfmt="{:.2f}")
for i, ln in enumerate(SHOW):
    V.polyline(f, bps, cur[ln], V.PAL[i], 1.5)
    for b, v in zip(bps, cur[ln]):
        V.marker(f, b, v, V.PAL[i], 2.2)
inside = [r for r in F1 if r["value"] != "nan"]
for i, ln in enumerate(SHOW):
    r = next((r for r in F1 if r["item"] == f"{ln}|sharpe_naive"), None)
    if r is None or r["value"] == "nan":
        continue
    x = float(r["value"])
    f.line(f.sx(x), T, f.sx(x), T+PH, V.PAL[i], 1.0, "3,3")
    V.halo(f, f.sx(x), T+PH-8-13*i, f"{SHORT[ln]} {x:.2f} bp", "middle", 9, V.PAL[i])
V.legend_box(f, [(SHORT[ln], V.PAL[i]) for i, ln in enumerate(SHOW)], L+14, T+PH-118)
f.text(L+PW-4, T+16,
       f"{len(inside)} of {len(F1)} crossings across the eleven lines and both Sharpe "
       f"conventions fall inside the swept range", "end", 9, "#555")
f.text(L+PW-4, T+28,
       f"{len(F1)-len(inside)} would be extrapolations and are not marked", "end", 9, "#555")
rows = [[f"{b:g}"] + [q(cur[ln][k]) for ln in SHOW] for k, b in enumerate(bps)]
rows += [["crossing", r["item"].split("|")[0], r["item"].split("|")[1], r["value"],
          "inside" if r["value"] != "nan" else "extrapolation"] for r in F1]
done("cost-sweep", f, ["slippage_bp"]+SHOW, rows,
     f"{CS} and outputs/session-21/reads.csv", PERIOD)

# ---- 4 leave one out ---------------------------------------------------------
LO = "outputs/session-22/rebuilt/leave-one-out.csv"
lr = [r for r in csv.DictReader(open(ROOT/LO))
      if r["table"] == "loo" and r["series"] == "STRATEGY"]
est = sorted(((r["dropped_year"], float(r["sharpe_lo"])) for r in lr
              if r["dropped_year"] != "none (base)"), key=lambda t: int(t[0]))
base = next(float(r["sharpe_lo"]) for r in lr if r["dropped_year"] == "none (base)")
vs = [v for _, v in est]
pad = (max(vs)-min(vs))*0.22
f = Fig("Lo-corrected Sharpe with each calendar year removed",
        "calendar year removed", "Lo-corrected Sharpe, annualised",
        (int(est[0][0])-0.7, int(est[-1][0])+0.7), (min(vs)-pad, max(vs)+pad))
V.axes2(f, xticks=[(int(y), y) for y, _ in est], yfmt="{:.2f}")
for y, v in est:
    V.vbar(f, int(y), min(vs)-pad, v, V.PAL[0], 0.62, 0.85)
f.line(L, f.sy(base), L+PW, f.sy(base), V.PAL[1], 1.4, "5,3")
V.halo(f, f.sx(int(est[0][0])-0.3), f.sy(base)-6,
       f"base estimate {base:.6f}", "start", 9, V.PAL[1])
V.legend_box(f, [(f"{len(est)} estimates, {min(vs):.6f} to {max(vs):.6f}", V.PAL[0])],
             L+14, T+18)
done("leave-one-out", f, ["dropped_year", "sharpe_lo"],
     [[y, q(v)] for y, v in est] + [["none (base)", q(base)]], LO, PERIOD)

# ---- 5 hedge intensity -------------------------------------------------------
HI = "outputs/session-15.5/hedge-intensity.csv"
hr = sorted((r for r in csv.DictReader(open(ROOT/HI))
             if r["table"] == "curve" and r["convention"] == "o2o"
             and r["window"] == "primary"), key=lambda r: float(r["short_notional"]))
sn = [float(r["short_notional"]) for r in hr]
sl = [float(r["sharpe_lo"]) for r in hr]
an = [float(r["ann_return"]) for r in hr]
f = Fig("Outcome against short-leg notional across the session 15.5 hedge arms",
        "short-leg notional, fraction of NAV", "Lo-corrected Sharpe, annualised",
        (min(sn)-0.05, max(sn)+0.05), (min(sl)-0.008, max(sl)+0.016))
V.axes2(f, xticks=[(x, f"{x:g}") for x in sn], yfmt="{:.2f}")
V.polyline(f, sn, sl, V.PAL[0], 1.6)
for r, x, y in zip(hr, sn, sl):
    V.marker(f, x, y, V.PAL[0], 3.4)
    V.halo(f, f.sx(x), f.sy(y)-9, f"arm {r['arm']}, {y:.6f}", "middle", 9, FG)
V.legend_box(f, [("Lo-corrected Sharpe, o2o convention, primary window", V.PAL[0])],
             L+14, T+18)
f.text(L+PW-4, T+PH-10, "no arm is adopted, the canonical is arm A", "end", 9, "#555")
done("hedge-intensity", f, ["arm", "short_notional", "sharpe_lo", "ann_return"],
     [[r["arm"], q(x), q(y), q(a)] for r, x, y, a in zip(hr, sn, sl, an)],
     HI, "o2o primary window")

# ---- 6 nav capacity ----------------------------------------------------------
NV = "outputs/session-20/rebuilt/nav-sweep.csv"
nr = sorted((r for r in csv.DictReader(open(ROOT/NV))
             if r["table"] == "cell" and r["convention"] == "o2o"
             and r["window"] == "primary"), key=lambda r: float(r["nav"]))
nv = [float(r["nav"]) for r in nr]
nl = [float(r["sharpe_lo"]) for r in nr]
na = [float(r["ann_return"]) for r in nr]
lx = [math.log10(v) for v in nv]
f = Fig("Designated cell outcome against starting NAV",
        "starting NAV, dollars", "Lo-corrected Sharpe, annualised",
        (min(lx)-0.16, max(lx)+0.16), (min(nl)-0.012, max(nl)+0.038))
V.axes2(f, xticks=[(x, f"{v:,.0f}".replace(",", " ")) for x, v in zip(lx, nv)],
        yfmt="{:.3f}")
V.polyline(f, lx, nl, V.PAL[0], 1.6)
for x, y in zip(lx, nl):
    V.marker(f, x, y, V.PAL[0], 3.4)
    V.halo(f, f.sx(x), f.sy(y)-9, f"{y:.6f}", "middle", 9, FG)
V.legend_box(f, [(f"Lo-corrected Sharpe across {len(nr)} NAV levels", V.PAL[0])],
             L+14, T+PH-24)
done("nav-capacity", f, ["nav", "sharpe_lo", "ann_return"],
     [[q(v), q(y), q(a)] for v, y, a in zip(nv, nl, na)], NV, "o2o primary window")

# ---- 7 Lo factor against each row's own null ---------------------------------
LQ = "outputs/session-20/lo-q-sweep.csv"
ln_ = sorted((r for r in csv.DictReader(open(ROOT/LQ)) if r["table"] == "lo_null"),
             key=lambda r: float(r["lo"]))
vals = [float(r[k]) for r in ln_ for k in ("lo", "null_p05", "null_p95")]
f = Fig("Lo-corrected Sharpe against each ladder row's own no-autocorrelation null",
        "Lo-corrected Sharpe, annualised", "ladder row, ordered by the observed value",
        (min(vals)-0.34, max(vals)+0.06), (-3.2, len(ln_)-0.3))
V.axes2(f, yticks=[], xfmt="{:.1f}")
for i, r in enumerate(ln_):
    ins = r["inside_own_null"] == "1"
    col = V.PAL[0] if ins else V.PAL[1]
    V.hrange(f, i, float(r["null_p05"]), float(r["null_p95"]), "#9aa5b1", 1.6)
    V.marker(f, float(r["null_mean"]), i, "#9aa5b1", 2.0)
    V.marker(f, float(r["lo"]), i, col, 4.0, "o" if ins else "s")
    st = r["line"] == "STRATEGY"
    V.halo(f, L+5, f.sy(i)+4, r["line"] + (", the designated cell" if st else ""),
           "start", 9, FG, "bold" if st else "normal")
V.legend_box(f, [("observed value inside its own null", V.PAL[0]),
                 ("observed value outside its own null", V.PAL[1]),
                 ("bar spans the null 5th to 95th percentile, dot is the null mean",
                  "#9aa5b1")], L+14, T+PH-50)
done("lo-factor-vs-null", f,
     ["line", "lo", "null_p05", "null_mean", "null_p95", "inside_own_null"],
     [[r["line"], q(r["lo"]), q(r["null_p05"]), q(r["null_mean"]), q(r["null_p95"]),
       r["inside_own_null"]] for r in ln_], LQ, PERIOD)

# ---- 8 rolling beta dispersion ------------------------------------------------
BD = "outputs/session-21/beta-decomposition.csv"
BW = "outputs/session-22/beta-window-sensitivity.csv"
byw = {}
for r in csv.reader(open(ROOT/BD)):
    if r and r[0] == "rolling" and r[1] in ("beta_mean","beta_sd","beta_min","beta_max"):
        byw.setdefault("60", {})[r[1]] = r[2]
for r in csv.DictReader(open(ROOT/BW)):
    if r["table"] == "rolling":
        byw.setdefault(r["window"], {})[r["item"]] = r["value"]
ws = sorted(byw, key=int)
lx = [math.log10(int(w)) for w in ws]
mn = [float(byw[w]["beta_min"]) for w in ws]
mx = [float(byw[w]["beta_max"]) for w in ws]
me = [float(byw[w]["beta_mean"]) for w in ws]
sd = [float(byw[w]["beta_sd"]) for w in ws]
f = Fig("Rolling beta against buy-and-hold QQQ at four estimation windows",
        "estimation window, sessions", "rolling beta",
        (min(lx)-0.10, max(lx)+0.10), (min(mn)-0.35, max(mx)+0.75))
V.axes2(f, xticks=[(x, w) for x, w in zip(lx, ws)], yfmt="{:.1f}")
V.band(f, lx, mn, mx, V.PAL[0], 0.16)
V.polyline(f, lx, mn, V.PAL[0], 1.0, "4,3")
V.polyline(f, lx, mx, V.PAL[0], 1.0, "4,3")
V.polyline(f, lx, me, V.PAL[0], 1.8)
for k, (w, x, m, s_) in enumerate(zip(ws, lx, me, sd)):
    V.marker(f, x, m, V.PAL[0], 3.4)
    V.halo(f, f.sx(x), f.sy(m)-10, f"sd {s_:.6f}",
           "end" if k == len(ws)-1 else "middle", 9, V.PAL[1])
V.legend_box(f, [("mean rolling beta", V.PAL[0]),
                 ("dashed lines and shading span the minimum to the maximum", V.PAL[0])],
             L+14, T+18)
done("rolling-beta-dispersion", f,
     ["window_sessions", "beta_mean", "beta_sd", "beta_min", "beta_max"],
     [[w, q(byw[w]["beta_mean"]), q(byw[w]["beta_sd"]), q(byw[w]["beta_min"]),
       q(byw[w]["beta_max"])] for w in ws], f"{BD} and {BW}", PERIOD)

print(f"\n{len(made)} figures written to outputs/session-25/figures/")
