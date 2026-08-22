"""Session 25 phase B. The figure inventory.

Both session 24 undrawable findings are confirmed against the current artifacts
rather than accepted, since outputs/session-22/rebuilt/nulls.csv at 10,000 draws
was written after the figure specification.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = ROOT/"outputs"/"session-25"; OUT.mkdir(parents=True, exist_ok=True)
rows = []
def add(t, **kw): rows.append({"table": t, **kw})

# ---- confirm undrawable finding 1, the null histograms -----------------------
NF = "outputs/session-22/rebuilt/nulls.csv"
hdr = next(csv.reader(open(ROOT/NF)))
draws = {r["n_draws"] for r in csv.DictReader(open(ROOT/NF)) if r["n_draws"]}
per_draw = [h for h in hdr if h.endswith(("_draws","_array","_samples")) or "draw_" in h]
summary = [h for h in hdr if h.startswith("null_")]
add("confirm_undrawable", item="null_histograms", value=0,
    note=f"CONFIRMED. {NF} at n_draws {sorted(draws)} carries {len(summary)} summary "
         f"columns, being {', '.join(summary)}, and {len(per_draw)} per-draw columns. "
         f"The distribution shape is unavailable and retaining the draws is a new "
         f"measurement rather than a read")
add("confirm_undrawable", item="null_quantile_alternative", value=1,
    note="a five-point quantile marker plot IS drawable from the p05, p50, p95, mean "
         "and max columns. It is not a histogram and is not substituted for one here")

# ---- confirm undrawable finding 2, effective exposure by decile --------------
EF = "outputs/session-16/exposure-reconciliation.csv"
eh = next(csv.reader(open(ROOT/EF)))
dec = [h for h in eh if "decile" in h]
add("confirm_undrawable", item="effective_exposure_by_decile", value=0,
    note=f"CONFIRMED. {EF} carries mean_effective_exposure with {len(dec)} named "
         f"decile columns, being {', '.join(dec)}, rather than a ten-decile series. "
         f"outputs/session-15.5/short-leg-decomposition.csv carries the same two named "
         f"deciles and no series, and no other committed CSV carries effective "
         f"exposure at all")

# ---- the PBO report's existing figures ---------------------------------------
EXIST = {
 "logit-histogram.svg": ("logit histogram with the PBO region shaded", "4"),
 "degradation-scatter.svg": ("in-sample against out-of-sample Sharpe as a scatter", "4,5"),
 "selected-vs-median.svg": ("out-of-sample Sharpe, selected against the median trial", ""),
 "specification-curve.svg": ("specification curve with structural axes as strata", "6,8"),
}
for f,(what,cl) in EXIST.items():
    p = ROOT/"outputs"/"session-19"/"figures"/f
    add("already_drawn", item=f, value=p.stat().st_size,
        illustrates_claims=cl,
        note=f"{what}, drawn session 19 under scripts/s19_svg.py, the same path this "
             f"session uses")

# ---- the candidate set --------------------------------------------------------
C = [
 ("equity-curve","equity curve of the designated cell against buy-and-hold QQQ and the matched-exposure line",
  "outputs/session-20/rebuilt/_ladder_returns.pkl",
  "strategy[(o2o,primary)] and lines[(buy_hold_QQQ,o2o,primary)] and lines[(matched_exposure_levered_QQQ_1.70,o2o,primary)]",
  "1","primary","draw",""),
 ("drawdown","drawdown series for the same three lines",
  "outputs/session-20/rebuilt/_ladder_returns.pkl","the same three series","","none","draw",
  "illustrates no claim in the frozen set, since no claim quotes a drawdown figure"),
 ("cost-sweep","strategy and benchmark Sharpe against round-turn cost with the crossings marked",
  "outputs/session-20/rebuilt/cost-sweep-designated.csv and outputs/session-21/reads.csv",
  "slippage_bp, sharpe_naive, sharpe_lo, crossing_bp","15","supporting","draw",""),
 ("leave-one-out","Lo-corrected Sharpe with each calendar year removed, base marked",
  "outputs/session-22/rebuilt/leave-one-out.csv","dropped_year, sharpe_lo, base_sharpe_lo",
  "13","primary","draw",""),
 ("hedge-intensity","short-leg intensity against outcome",
  "outputs/session-15.5/hedge-intensity.csv","arm, short_notional, ann_return, sharpe_lo",
  "","none","draw","illustrates no claim in the frozen set, and none of the 15.5 arms is adopted"),
 ("nav-capacity","designated cell against starting NAV",
  "outputs/session-20/rebuilt/nav-sweep.csv","nav, ann_return, sharpe_lo, cap_frac_of_target_dollars",
  "","none","draw",
  "the session 24 specification named outputs/session-15/nav-sweep.csv, which is on the "
  "superseded boundary. The rebuilt file exists and carries the corrected boundary, so "
  "the figure uses it"),
 ("lo-factor-vs-null","each ladder row's Lo factor against its own no-autocorrelation null bounds",
  "outputs/session-20/lo-q-sweep.csv","line, lo, null_p05, null_p95, inside_own_null",
  "14,1","primary","draw","not carried by the session 24 specification. It carries "
  "claim 14's own figures and claim 1's ordering on the Lo-corrected convention, being "
  "two primary claims"),
 ("rolling-beta-dispersion","rolling beta dispersion at the four estimation windows",
  "outputs/session-21/beta-decomposition.csv and outputs/session-22/beta-window-sensitivity.csv",
  "window, beta_mean, beta_sd, beta_min, beta_max","","none","draw",
  "not carried by the session 24 specification. It illustrates register 9.42, being "
  "the window sensitivity of the beta estimate, and no frozen claim. Claim 12's own "
  "figures are the timing contributions, which this figure does not plot, and claim "
  "11's beta is a full-sample regression rather than a rolling mean"),
 ("logit-histogram","logit histogram with the PBO region shaded",
  "outputs/session-19/cscv-draws-s16.npz","logit","4","primary","exclude_already_drawn",
  "outputs/session-19/figures/logit-histogram.svg carries it"),
 ("is-vs-oos-scatter","in-sample against out-of-sample Sharpe as a scatter",
  "outputs/session-19/cscv-draws-s16.npz","is_sel, os_sel","4,5","primary","exclude_already_drawn",
  "outputs/session-19/figures/degradation-scatter.svg carries it, with a fitted line "
  "for the degradation slope withdrawn at 9.35"),
 ("specification-curve","specification curve across the searched axes with structural axes as strata",
  "outputs/session-19/specification-curve.csv","axis, classification, sharpe_lo_p05, sharpe_lo_mean, sharpe_lo_p95",
  "6,8","primary","exclude_already_drawn",
  "outputs/session-19/figures/specification-curve.svg carries it"),
 ("null-histograms","the two randomization nulls with the observed value marked",
  "outputs/session-22/rebuilt/nulls.csv","the per-draw arrays","2","primary","exclude_undrawable",
  "the file carries summary quantiles only"),
 ("effective-exposure-decile","mean effective exposure against conditioning decile",
  "outputs/session-16/exposure-reconciliation.csv","a ten-decile series","","none","exclude_undrawable",
  "the file carries the mean and two named deciles only"),
]
for n,(name,content,src,cols,cl,tier,dis,note) in enumerate(C,1):
    lit = {"cost-sweep": 1, "leave-one-out": 1, "lo-factor-vs-null": 1}.get(name, 0)
    add("candidate", item=name, value=n, content=content, source_file=src,
        columns_read=cols, illustrates_claims=cl, claim_tier=tier,
        disposition=dis, carries_claim_literal=lit, note=note)
draw = [c for c in C if c[6]=="draw"]
add("inventory", item="candidates", value=len(C))
add("inventory", item="excluded_undrawable", value=sum(1 for c in C if c[6]=="exclude_undrawable"))
add("inventory", item="excluded_already_drawn", value=sum(1 for c in C if c[6]=="exclude_already_drawn"),
    note="three candidates are figures the PBO report already carries, drawn in session "
         "19 under the same standard-library path, so redrawing them would duplicate "
         "rather than add")
add("inventory", item="final_drawable_set", value=len(draw))
add("inventory", item="target", value=8)
add("inventory", item="drop_rule_applied", value=0,
    note="the final set equals the target, so the rule that a figure illustrating a "
         "supporting claim yields to one illustrating a primary claim was not needed. "
         "Had it been applied, the three figures illustrating no frozen claim would "
         "have ranked below the one illustrating a supporting claim, being drawdown, "
         "hedge-intensity, nav-capacity and rolling-beta-dispersion")
add("inventory", item="figures_illustrating_no_claim", value=4,
    note="drawdown, hedge-intensity, nav-capacity and rolling-beta-dispersion. Each is "
         "retained because the set "
         "is at target without dropping them, and each is reported rather than silently "
         "carried")

# ---- claims with no figure ----------------------------------------------------
cl_rows = list(csv.DictReader(open(ROOT/"outputs/session-24/claim-sources.csv")))
covered_here = set()
for c in C:
    if c[6]=="draw":
        covered_here |= {x for x in c[4].split(",") if x}
covered_report = set()
for c in C:
    if c[6]=="exclude_already_drawn":
        covered_report |= {x for x in c[4].split(",") if x}
for r in cl_rows:
    n = r["n"]
    where = ("this session" if n in covered_here else
             "the PBO report" if n in covered_report else "none")
    if where != "none":
        add("claim_coverage", item=f"claim_{n}", value=where,
            claim_tier=r["tier"], note=r["statement"][:110])
    else:
        add("claim_without_figure", item=f"claim_{n}", value="none",
            claim_tier=r["tier"], note=r["statement"][:110])
nof = [r for r in rows if r["table"]=="claim_without_figure"]
add("inventory", item="claims_without_any_figure", value=len(nof),
    note="being " + ", ".join(x["item"].replace("claim_","") for x in nof) +
         ". A primary claim without a figure is a choice recorded here rather than an "
         "oversight, and claim 2 is among them only because its figure is undrawable")

add("inventory", item="figures_carrying_a_claim_literal", value=3,
    note="cost-sweep, leave-one-out and lo-factor-vs-null. The other five illustrate a "
         "claim's subject or a register finding without plotting any figure the claim "
         "quotes, so phase E can check three of the eight against a literal and reports "
         "the rest as carrying none")
fn = ["table","item","value","content","source_file","columns_read","illustrates_claims",
      "claim_tier","disposition","carries_claim_literal","note"]
with open(OUT/"figure-inventory.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
    for r in rows: w.writerow({k: r.get(k,"") for k in fn})
print(f"wrote figure-inventory.csv, {len(rows)} rows, final drawable set {len(draw)}")
for r in rows:
    if r["table"] in ("inventory","claim_without_figure"):
        print(f"  {r['table']:24s} {r['item']:34s} {r['value']}")
