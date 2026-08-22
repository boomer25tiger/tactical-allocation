"""Session 24 phases A through E. Claims, withdrawals, limitations, figure spec.

Every figure is read from an emitted CSV with the path and literal value carried
beside it. Nothing is recalled from a session report's prose.
"""
from __future__ import annotations
import csv, pickle
from pathlib import Path
import pandas as pd
R = Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = R/"outputs"/"session-24"; OUT.mkdir(parents=True, exist_ok=True)


def rd(p): return list(csv.DictReader(open(R/p)))
def val(rows, pred, f="value"):
    for r in rows:
        if pred(r): return r.get(f)
    return None


# ---------------- sources ----------------
LAD = "outputs/session-20/rebuilt/metrics-full.csv"
lad = pd.read_csv(R/LAD)
lad = lad[(lad.table=="metrics")&(lad.panel=="realized")&(lad.convention=="o2o")
          &(lad.window=="primary")]
S = lad[lad.line=="STRATEGY"].iloc[0]; Q = lad[lad.line=="buy_hold_QQQ"].iloc[0]
rn = lad.sharpe_naive.rank(ascending=False,method="min")
rl = lad.sharpe_lo.rank(ascending=False,method="min")
N10 = "outputs/session-22/rebuilt/nulls.csv"
n10 = pd.read_csv(R/N10); nd = n10[n10.table=="null_distribution"]
RW = "outputs/session-20/rebuilt/nulls.csv"
rw = pd.read_csv(R/RW); rw = rw[rw.table=="romano_wolf"]
PBO = "outputs/session-19/pbo.csv"; pbo = rd(PBO)
STR = "outputs/session-19/pbo-strata.csv"; strat = rd(STR)
DN = "outputs/session-19_6/degradation-null.csv"; dn = rd(DN)
SPEC = "outputs/session-19/specification-curve.csv"; spec = rd(SPEC)
PROV = "outputs/session-21/canonical-provenance.csv"; prov = rd(PROV)
REC = "outputs/session-21/recentred-comparison.csv"; rec = rd(REC)
EFN = "outputs/session-20/effective-n.csv"; efn = rd(EFN)
BETA = "outputs/session-21/beta-decomposition.csv"; beta = rd(BETA)
BWIN = "outputs/session-22/beta-window-sensitivity.csv"; bwin = rd(BWIN)
LOO = "outputs/session-22/rebuilt/leave-one-out.csv"
loo = pd.read_csv(R/LOO); loo = loo[(loo.table=="loo")&(loo.series=="STRATEGY")]
loo = loo[loo.dropped_year.astype(str)!="none (base)"]
LOOR = "outputs/session-22/loo-rebuilt.csv"; loor = rd(LOOR)
LOQ = "outputs/session-20/lo-q-sweep.csv"; loq = rd(LOQ)
READS = "outputs/session-21/reads.csv"; reads = rd(READS)
VOL = "outputs/session-22/volatility-terminal-resolution.csv"; vol = rd(VOL)
UNW = "outputs/session-21/unwired-config.csv"; unw = rd(UNW)

def pv(Sv, m):
    return val(pbo, lambda r: r["table"]=="pbo" and r["S"]==str(Sv)
               and r["metric"]==m and r["restriction"]=="full_grid")

C = []   # claim rows
def claim(n, statement, source, value, reg, tier, cat, overturn):
    C.append({"n":n,"statement":statement,"source_file":source,"literal_value":value,
              "register_item":reg,"tier":tier,"category":cat,"overturned_by":overturn})

claim(1,"In the designated cell the strategy places sixth of twelve on both Sharpe "
        "conventions, trailing buy-and-hold QQQ on the naive Sharpe by 0.0650226373237004 "
        "and on the Lo-corrected Sharpe by 0.42161920118337926.",
      LAD, f"STRATEGY naive {S.sharpe_naive!r} lo {S.sharpe_lo!r}; buy_hold_QQQ naive "
           f"{Q.sharpe_naive!r} lo {Q.sharpe_lo!r}; ranks {int(rn[S.name])} and {int(rl[S.name])} of {len(lad)}",
      "8.8, rebuilt at 9.23","primary","strategy",
      "a ladder line rebuilt on a different cost model or a corrected benchmark "
      "construction that moves the strategy's rank")
exc = {}
for _, r in nd.iterrows():
    for c, l in (("p_value_ann_one_sided","annualised return"),
                 ("p_value_sharpe_one_sided","Lo-corrected Sharpe")):
        exc[f"{r['null']}|{l}"] = (int(round(float(r[c])*float(r.n_draws))), int(r.n_draws))
claim(2,"Against two randomization nulls at 10,000 draws on the designated cell, the "
        "strategy is exceeded on 7 of 10,000 draws by the timing shuffle on annualised "
        "return and on 0 of 10,000 in the other three combinations.",
      N10, "; ".join(f"{k} {v[0]} of {v[1]}" for k,v in exc.items()),
      "8.9, re-run at 9.40","primary","strategy",
      "a null construction that preserves a feature of the strategy the current two do not")
claim(3,"Romano-Wolf across eleven comparisons leaves one below 0.05, being the "
        "equal-weight universe with the strategy above it.",
      RW, f"comparisons {len(rw)}, below 0.05 {int((rw.rw_adjusted_p<0.05).sum())}, "
          f"equal_weight_universe p {float(rw[rw.hypothesis=='strategy_minus_equal_weight_universe'].rw_adjusted_p.iloc[0])!r} "
          f"sign above; buy_hold_QQQ p {float(rw[rw.hypothesis=='strategy_minus_buy_hold_QQQ'].rw_adjusted_p.iloc[0])!r}",
      "8.10","primary","strategy",
      "re-running the family at a higher replication count, since this ran at 1,000 draws "
      "where the two randomization nulls were raised to 10,000")
claim(4,"Probability of backtest overfitting is 0.1578088578088578 at S equal to 16 over "
        "the full 12,870 combination enumeration, spanning 0.11428571428571428 to "
        "0.170995670995671 across block counts 8 through 48.",
      PBO, f"S16 {pv(16,'pbo')}, S8 {pv(8,'pbo')}, S12 {pv(12,'pbo')}, S24 {pv(24,'pbo')}, "
           f"S48 {pv(48,'pbo')}",
      "8.12","primary","grid",
      "a CSCV variant that changes the selection rule rather than the block count")
claim(5,"An estimator control puts the same harness at a PBO of 0.9919283331048036 when "
        "selection is driven purely by idiosyncratic noise.",
      DN, val(dn, lambda r: r["table"]=="null" and r["item"]=="pbo"),
      "9.30","supporting","apparatus",
      "a control construction that preserves cross-specification structure the current "
      "permutation destroys")
rng = {r["axis"]:(r["pbo_min"],r["pbo_max"],r["full_grid_inside_range"])
       for r in strat if r["table"]=="axis_range"}
can = {r["axis"]:r["pbo"] for r in strat if r["table"]=="stratum" and r["is_canonical_value"]=="1"}
claim(6,"The full-grid PBO exceeds none of the six within-stratum ranges, lying inside "
        "five and below one, which indicates search across strategy shapes adds nothing "
        "beyond parameter search.",
      STR, "; ".join(f"{a} {v[0]} to {v[1]} inside {v[2]}" for a,v in rng.items()),
      "8.13","primary","grid",
      "a stratification on an axis not currently classified structural that places the "
      "full-grid figure above its range")
claim(7,"The canonical's own stratum PBO on each structural axis ranges from "
        "0.13916083916083916 on oversold to 0.2355089355089355 on overbought tier one.",
      STR, "; ".join(f"{a}={v}" for a,v in can.items()),
      "8.13","supporting","grid","as claim 6")
claim(8,"The canonical ranks 6,834 of 121,500 on the Lo-corrected Sharpe and 8,237 on "
        "annualised return, with eight of its nine axis values fixed before any "
        "comparison on that axis.",
      f"{SPEC} and {PROV}",
      f"rank lo {val(spec, lambda r: r['table']=='canonical_rank' and r['axis']=='sharpe_lo','rank')} "
      f"pct {val(spec, lambda r: r['table']=='canonical_rank' and r['axis']=='sharpe_lo','percentile')}; "
      f"rank ann {val(spec, lambda r: r['table']=='canonical_rank' and r['axis']=='ann_return','rank')}; "
      f"axes before {val(prov, lambda r: r['table']=='state_count' and r['axis']=='before','canonical_value')}, "
      f"after {val(prov, lambda r: r['table']=='state_count' and r['axis']=='after','canonical_value')}",
      "9.32","primary","grid",
      "establishing that a further axis was fixed after a comparison on that axis")
claim(9,"Against the grid's own cross-sectional distribution the canonical sits "
        "1.0424959653759258 standard deviations above the mean at the 89.27654320987655 "
        "percentile, and it exceeds the expected maximum of an equivalent independent "
        "search only at the participation-ratio effective count and at none of the other "
        "three, so the two correlation-accounting methods disagree.",
      REC, f"z {val(rec, lambda r: r['item']=='canonical_sharpe_naive_z_from_grid_mean')}; "
           f"pct {val(rec, lambda r: r['item']=='canonical_sharpe_naive_percentile')}; "
           f"exceeds at PR {val(rec, lambda r: r['item']=='participation_ratio_canonical_exceeds')}, "
           f"SE {val(rec, lambda r: r['item']=='spectral_entropy_canonical_exceeds')}, "
           f"VT95 {val(rec, lambda r: r['item']=='variance_threshold_95_canonical_exceeds')}, "
           f"nominal {val(rec, lambda r: r['item']=='nominal_121500_canonical_exceeds')}",
      "8.7 as amended","primary","apparatus",
      "an accounting method that resolves the disagreement between the two reported here")
claim(10,"Across the pre-registered 2,001-series subsample the effective number of "
         "independent trials is 3.4279931063515994 under the participation ratio, "
         "6.719710164987509 under spectral entropy and 17 under a 95 percent variance "
         "threshold, with 0.4677702078080885 of variance in the first principal component.",
      EFN, f"PR {val(efn, lambda r: r['table']=='effective_n' and r['axis']=='participation_ratio','in_N')}; "
           f"SE {val(efn, lambda r: r['table']=='effective_n' and r['axis']=='spectral_entropy','in_N')}; "
           f"VT95 {val(efn, lambda r: r['table']=='effective_n' and r['axis']=='variance_threshold_95','in_N')}; "
           f"PC1 {val(efn, lambda r: r['table']=='effective_n' and r['axis']=='top_eigenvalue_share','in_N')}",
      "9.28 under 9.10","supporting","grid",
      "a subsample shown non-representative, which session 21 phase C tested and did not find")
claim(11,"Regressing the canonical on the investable buy-and-hold QQQ line gives a beta "
         "of 1.108672858112171 at an R-squared of 0.18679426851145753, with annualised "
         "alpha 0.28874420661558875 at a Newey-West t of 2.364283243646891, and the "
         "beta-hedged residual carries a naive Sharpe of 0.6558362612960221 and a "
         "Lo-corrected Sharpe of 0.8649152595612315.",
      BETA, "; ".join(f"{k}={val(beta, lambda r,k=k: r['table']=='static' and r['item']==k)}"
                      for k in ("beta","r_squared","alpha_annualised","alpha_t_newey_west",
                                "residual_sharpe_naive","residual_sharpe_lo")),
      "9.34","primary","strategy",
      "a benchmark other than buy-and-hold QQQ that absorbs more of the return")
tw = {w: val(bwin, lambda r,w=w: r["table"]=="timing" and r["window"]==str(w)
             and r["item"]=="timing_ann_contribution") for w in (120,252,504)}
claim(12,"The timing component of the return decomposition changes sign across the "
         "estimation window, reading positive at 60 and 120 sessions and negative at 252 "
         "and 504, so it is not stable.",
      f"{BETA} and {BWIN}",
      f"60 {val(beta, lambda r: r['table']=='timing_decomposition' and r['item']=='timing_ann_contribution')}; "
      + "; ".join(f"{w} {v}" for w,v in tw.items()),
      "9.42","primary","apparatus",
      "a window-selection rule fixed in advance that makes one window authoritative")
claim(13,"Across eleven leave-one-out estimates the Lo-corrected Sharpe ranges from "
         "1.287076427656795 to 1.6183359759194622, and the two years whose removal raises "
         "it most are 2020 and 2011.",
      LOO, f"min {loo.sharpe_lo.min()!r} max {loo.sharpe_lo.max()!r}; "
           f"2020 {float(loo[loo.dropped_year.astype(int)==2020].sharpe_lo.iloc[0])!r}; "
           f"2011 {float(loo[loo.dropped_year.astype(int)==2011].sharpe_lo.iloc[0])!r}",
      "9.41","primary","strategy",
      "a rebuild on a different boundary, which session 22 ran and found identical")
claim(14,"Nine of twelve ladder rows carry a Lo factor inside their own "
         "no-autocorrelation null, the three outside being exactly the three rows that "
         "outrank the strategy, and nine of twelve rows change rank across a sweep of the "
         "unregistered lag parameter q.",
      LOQ, f"inside own null {val(loq, lambda r: r['table']=='lo_null_meta' and r['line']=='rows_inside_own_null','value')} of 12; "
           f"rows changing rank across q {val(loq, lambda r: r['table']=='q_summary' and r['line']=='rows_changing_rank_across_q','value')}; "
           f"strategy rank range {val(loq, lambda r: r['table']=='q_summary' and r['line']=='STRATEGY_rank_range','note')}",
      "9.37, with 8.2 decided","primary","apparatus",
      "registering q as an axis and sweeping it before any figure is selected")
n_in = sum(1 for r in reads if r["table"]=="F1" and r["note"]=="inside the swept range")
n_ex = sum(1 for r in reads if r["table"]=="F1" and "extrapolation" in r["note"])
claim(15,"Over a round-turn cost sweep spanning 0 to 50 bp, 10 of the 22 benchmark "
         "crossings fall inside the swept range and 12 are extrapolations, with the "
         "strategy crossing buy-and-hold QQQ on the naive Sharpe at 10.084002378357239 bp "
         "and not crossing it on the Lo-corrected Sharpe inside the range.",
      READS, f"inside {n_in}, extrapolations {n_ex}; buy_hold_QQQ naive "
             f"{val(reads, lambda r: r['table']=='F1' and r['item']=='buy_hold_QQQ|sharpe_naive')}; "
             f"buy_hold_QQQ lo {val(reads, lambda r: r['table']=='F1' and r['item']=='buy_hold_QQQ|sharpe_lo')}",
      "4.4","supporting","strategy",
      "widening the sweep so the twelve extrapolated crossings become measured")
with open(OUT/"claim-sources.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["n","statement","source_file","literal_value",
                                    "register_item","tier","category","overturned_by"])
    w.writeheader(); w.writerows(C)
print(f"claim-sources.csv: {len(C)} claims")
for cat in ("strategy","grid","apparatus"):
    print(f"  {cat}: {sum(1 for c in C if c['category']==cat)}")
print(f"  primary {sum(1 for c in C if c['tier']=='primary')}, "
      f"supporting {sum(1 for c in C if c['tier']=='supporting')}")
