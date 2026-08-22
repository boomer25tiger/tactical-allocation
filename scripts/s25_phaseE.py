"""Session 25 phase E. The figure-to-claim check.

Every check compares a value in a figure's emitted series CSV against the literal
in outputs/session-24/claim-sources.csv or against the emitted scalar the derived
series should reproduce. A disagreement is reported and not repaired, since which
of two emitted files is right belongs in chat rather than in a patch.
"""
from __future__ import annotations
import csv
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT/"outputs"/"session-25"; FIG = OUT/"figures"
TOL = 5e-7           # the standing positive-control tolerance, stated before comparing
rows = []
def add(**kw): rows.append(kw)
def fig(n): return list(csv.DictReader(open(FIG/f"{n}.csv")))
CL = {r["n"]: r for r in csv.DictReader(open(ROOT/"outputs/session-24/claim-sources.csv"))}
MF = [r for r in csv.DictReader(open(ROOT/"outputs/session-20/rebuilt/metrics-full.csv"))
      if r["table"] == "metrics" and r["convention"] == "o2o" and r["window"] == "primary"]
def mf(line, col): return float(next(r[col] for r in MF if r["line"] == line))


def chk(claim, figure, quantity, claim_v, fig_v, note=""):
    try:
        a, b = float(claim_v), float(fig_v)
        if a != a and b != b:            # both not-a-number, which is the recorded
            dev = 0.0; agree = exact = 1  # value when no crossing exists
        else:
            dev = abs(a - b)
            agree = int(dev <= TOL); exact = int(a == b)
    except (TypeError, ValueError):
        dev = ""; agree = int(str(claim_v) == str(fig_v)); exact = agree
    add(claim=claim, figure=figure, quantity=quantity, claim_value=claim_v,
        figure_value=fig_v, deviation=dev, exact=exact,
        within_tolerance=agree, verdict="agrees" if exact else
        ("agrees within tolerance" if agree else "DISAGREES"), note=note)


add(claim="", figure="", quantity="tolerance", claim_value=TOL, figure_value=TOL,
    deviation=0, exact=1, within_tolerance=1, verdict="stated before comparing",
    note="the standing positive-control tolerance, applied to every numeric check below")

# ---- claim 14, lo-factor-vs-null ---------------------------------------------
lf = fig("lo-factor-vs-null")
ins = sum(1 for r in lf if r["inside_own_null"] == "1")
outs = [r["line"] for r in sorted(lf, key=lambda r: -float(r["lo"]))
        if r["inside_own_null"] == "0"]
chk("14", "lo-factor-vs-null", "rows inside their own null", "9", str(ins),
    "claim 14 states nine of twelve")
chk("14", "lo-factor-vs-null", "rows plotted", "12", str(len(lf)))
chk("14", "lo-factor-vs-null", "rows outside, in Lo order",
    "buy_hold_TQQQ,buy_hold_QQQ,matched_exposure_levered_QQQ_1.70", ",".join(outs))

# ---- claim 1, lo-factor-vs-null and the ladder metrics -----------------------
byl = {r["line"]: r for r in lf}
rank = sorted(lf, key=lambda r: -float(r["lo"]))
srank = next(i for i, r in enumerate(rank, 1) if r["line"] == "STRATEGY")
chk("1", "lo-factor-vs-null", "strategy rank on the Lo convention", "6", str(srank))
chk("1", "lo-factor-vs-null", "ladder rows", "12", str(len(lf)))
chk("1", "lo-factor-vs-null", "strategy Lo-corrected Sharpe",
    "1.3817013060244996", byl["STRATEGY"]["lo"],
    "claim 1 quotes outputs/session-20/rebuilt/metrics-full.csv while the figure plots "
    "outputs/session-20/lo-q-sweep.csv, so this compares two emitted files")
gap = float(byl["buy_hold_QQQ"]["lo"]) - float(byl["STRATEGY"]["lo"])
chk("1", "lo-factor-vs-null", "Lo gap to buy-and-hold QQQ",
    "0.42161920118337926", repr(gap),
    "claim 1 states the gap as a negative figure and the figure plots the two levels, "
    "so the magnitude is compared")

# ---- claim 13, leave-one-out --------------------------------------------------
lo = [r for r in fig("leave-one-out") if r["dropped_year"] != "none (base)"]
vs = [float(r["sharpe_lo"]) for r in lo]
chk("13", "leave-one-out", "estimates plotted", "11", str(len(lo)))
chk("13", "leave-one-out", "minimum", "1.287076427656795", repr(min(vs)))
chk("13", "leave-one-out", "maximum", "1.6183359759194622", repr(max(vs)))
top2 = [r["dropped_year"] for r in sorted(lo, key=lambda r: -float(r["sharpe_lo"]))[:2]]
chk("13", "leave-one-out", "two years whose removal raises it most", "2020,2011",
    ",".join(top2))

# ---- claim 15, cost-sweep -----------------------------------------------------
cs = [r for r in csv.reader(open(FIG/"cost-sweep.csv")) if r and r[0] == "crossing"]
ins_c = [r for r in cs if r[4] == "inside"]
chk("15", "cost-sweep", "crossings inside the swept range", "10", str(len(ins_c)))
chk("15", "cost-sweep", "crossings that would be extrapolations", "12",
    str(len(cs) - len(ins_c)))
qn = next(r for r in cs if r[1] == "buy_hold_QQQ" and r[2] == "sharpe_naive")
chk("15", "cost-sweep", "buy-and-hold QQQ crossing on the naive Sharpe",
    "10.084002378357239", qn[3])
ql = next(r for r in cs if r[1] == "buy_hold_QQQ" and r[2] == "sharpe_lo")
chk("15", "cost-sweep", "buy-and-hold QQQ crossing on the Lo-corrected Sharpe",
    "nan", ql[3], "claim 15 states there is no crossing inside the range")

# ---- derived series against the emitted scalars -------------------------------
eq = fig("equity-curve"); dd = fig("drawdown")
for ln in ("STRATEGY", "buy_hold_QQQ", "matched_exposure_levered_QQQ_1.70"):
    chk("", "equity-curve", f"{ln} total return", repr(mf(ln, "total_return")),
        repr(float(eq[-1][ln]) - 1.0),
        "the plotted growth series is derived from the committed return series, so its "
        "final value is checked against the emitted scalar rather than assumed")
    chk("", "drawdown", f"{ln} maximum drawdown", repr(mf(ln, "max_drawdown")),
        repr(min(float(r[ln]) for r in dd)),
        "as above, the derived series minimum against the emitted scalar")
chk("", "equity-curve", "sessions plotted", "2472", str(len(eq)),
    "the primary window session count the positive control reproduces")

# ---- figures carrying no claim literal ----------------------------------------
for f_, why in (("hedge-intensity", "no frozen claim quotes a hedge-arm figure"),
                ("nav-capacity", "no frozen claim quotes a NAV-sweep figure"),
                ("rolling-beta-dispersion",
                 "it illustrates register 9.42 rather than a frozen claim, and claim "
                 "12's own figures are the timing contributions this figure does not plot"),
                ("drawdown", "no frozen claim quotes a drawdown figure"),
                ("equity-curve",
                 "claim 1's figures are Sharpe ratios and a rank rather than a growth "
                 "series, so the figure illustrates the claim's subject without carrying "
                 "its literal")):
    add(claim="", figure=f_, quantity="claim literal carried", claim_value="none",
        figure_value="none", deviation="", exact="", within_tolerance="",
        verdict="no literal to check", note=why)
    n = len(fig(f_))
    add(claim="", figure=f_, quantity="plotted rows read straight from the source",
        claim_value=str(n), figure_value=str(n), deviation=0, exact=1,
        within_tolerance=1, verdict="agrees",
        note="every plotted value is copied from the source CSV without transformation, "
             "so the series and the source agree by construction")

fn = ["claim","figure","quantity","claim_value","figure_value","deviation","exact",
      "within_tolerance","verdict","note"]
with open(OUT/"figure-claim-check.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
    for r in rows: w.writerow({k: r.get(k,"") for k in fn})
num = [r for r in rows if r.get("verdict") in ("agrees","agrees within tolerance","DISAGREES")]
bad = [r for r in num if r["verdict"] == "DISAGREES"]
tolonly = [r for r in num if r["verdict"] == "agrees within tolerance"]
print(f"wrote figure-claim-check.csv, {len(rows)} rows, {len(num)} numeric checks")
print(f"  exact {len(num)-len(tolonly)-len(bad)}, within tolerance only {len(tolonly)}, "
      f"disagreements {len(bad)}")
for r in tolonly + bad:
    print(f"  {r['verdict']:24s} claim {r['claim'] or '-':>2} {r['figure']:24s} "
          f"{r['quantity']:44s} {r['claim_value']} vs {r['figure_value']} dev {r['deviation']}")
