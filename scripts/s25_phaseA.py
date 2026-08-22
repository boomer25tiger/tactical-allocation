"""Session 25 phase A. Two claim-wording checks and the standing positive control.

TOL_CANON = 5e-7, the same tolerance session 23 stated, written before comparing.
Both checks are reads. Nothing is amended here.
"""
from __future__ import annotations
import csv, subprocess, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
import scripts.s22_vm as VM         # noqa: E402
OUT = ROOT/"outputs"/"session-25"; OUT.mkdir(parents=True, exist_ok=True)
TOL = 5e-7
rows = []
def add(t, **kw): rows.append({"table": t, **kw})

def loadavg():
    o = subprocess.run(["sysctl","-n","vm.loadavg"],capture_output=True,text=True).stdout
    return [float(x) for x in o.strip().strip("{}").split()]

l = loadavg(); s = VM.sample()
for k, v in (("load_1min",l[0]),("load_5min",l[1]),("load_15min",l[2]),
             ("compressor_gib",s["compressor_gib"]),("swap_used_mb",s["swap_used_mb"]),
             ("swap_free_mb",s["swap_free_mb"])):
    add("machine_at_start", item=k, value=v)

# ---- A1, the Lo null finding -------------------------------------------------
src = "outputs/session-20/lo-q-sweep.csv"
ln = [r for r in csv.DictReader(open(ROOT/src)) if r["table"] == "lo_null"]
ln.sort(key=lambda r: -float(r["lo"]))
strat_rank = next(i for i, r in enumerate(ln, 1) if r["line"] == "STRATEGY")
add("A1", item="strategy_rank_by_lo", value=strat_rank,
    note=f"of {len(ln)} ladder rows, source {src} table lo_null")
add("A1", item="rows_outranking_strategy", value=strat_rank-1)
for i, r in enumerate(ln[:strat_rank-1], 1):
    lo = float(r["lo"]); p05 = float(r["null_p05"]); p95 = float(r["null_p95"])
    consistent = int((p05 <= lo <= p95) == (r["inside_own_null"] == "1"))
    add("A1_outranking", item=r["line"], value=r["lo"], rank=i,
        null_p05=r["null_p05"], null_p95=r["null_p95"],
        inside_own_null=r["inside_own_null"], null_mean=r["null_mean"],
        flag_consistent_with_bounds=consistent)
r = ln[strat_rank-1]
add("A1_strategy", item="STRATEGY", value=r["lo"], rank=strat_rank,
    null_p05=r["null_p05"], null_p95=r["null_p95"],
    inside_own_null=r["inside_own_null"], null_mean=r["null_mean"])
out_top = [r["line"] for r in ln[:strat_rank-1] if r["inside_own_null"] == "0"]
in_top  = [r["line"] for r in ln[:strat_rank-1] if r["inside_own_null"] == "1"]
add("A1_verdict", item="argument_as_stated", value="holds",
    note="8.2 names buy-and-hold QQQ specifically. buy_hold_QQQ sits outside its own "
         "null and the strategy sits inside its own, so the sentence as written is true")
add("A1_verdict", item="argument_narrowed_to_top_three", value="holds",
    note=f"the three outside are {', '.join(out_top)}, being lo ranks 1 to 3")
add("A1_verdict", item="argument_generalised_to_all_outranking", value="fails",
    note=f"{len(in_top)} of the {strat_rank-1} rows outranking the strategy sit INSIDE "
         f"their own null, being {', '.join(in_top)}, so outranking the strategy does "
         f"not imply sitting outside the null")
add("A1_verdict", item="grounds_as_they_should_read",
    note="the strategy's own Lo factor sits inside its own no-autocorrelation null "
         "while the three rows ranked highest on the Lo-corrected Sharpe sit outside "
         "theirs, and two further rows outranking the strategy sit inside theirs, so "
         "the property separates the top three rather than separating every row above "
         "the strategy from every row below it")
add("A1_verdict", item="current_register_text_8_2",
    note="The grounds are that session 20's D1 measured the strategy's own Lo factor "
         "sitting inside its own no-autocorrelation null while buy-and-hold QQQ's sits "
         "outside, and that nine of twelve ladder rows change rank across the q sweep, "
         "so the Lo-corrected ordering is not stable under a parameter that was never "
         "registered")
add("A1_verdict", item="amended_this_phase", value=0, note="8.2 is not amended here")

# ---- A2, the block-count range ----------------------------------------------
claims = ROOT/"docs"/"CLAIMS.md"
txt = claims.read_text().split("## Claim 4,")[1].split("## Claim 5,")[0]
stmt = [x for x in txt.split("\n") if x.strip() and not x.startswith("-")][1].strip()
add("A2", item="claim_4_statement_verbatim", note=stmt)
pf = {r["item"]: r for r in csv.DictReader(open(ROOT/"outputs/session-24/phaseF-relaunch.csv"))}
reemitted = [S for S in ("8","12","16","24","48") if f"S={S}_pbo_reemitted" in pf]
add("A2", item="block_counts_re_emitted", value=",".join(reemitted),
    note="source outputs/session-24/phaseF-relaunch.csv")
add("A2", item="block_counts_not_re_emitted", value="48")
pbo = {}
for r in csv.DictReader(open(ROOT/"outputs/session-19/pbo.csv")):
    if r.get("table")=="pbo" and r.get("restriction")=="full_grid" and r.get("metric")=="pbo":
        pbo.setdefault(r["S"], r["value"])
lo_S = min(pbo, key=lambda S: float(pbo[S])); hi_S = max(pbo, key=lambda S: float(pbo[S]))
add("A2", item="range_minimum", value=pbo[lo_S], note=f"at S equal to {lo_S}")
add("A2", item="range_maximum", value=pbo[hi_S], note=f"at S equal to {hi_S}")
add("A2", item="numeric_endpoints_are_re_emitted", value=int(lo_S in reemitted and hi_S in reemitted),
    note=f"the range's two numeric endpoints are S equal to {lo_S} and S equal to {hi_S}")
spans_all = "8 through 48" in stmt
add("A2", item="wording_spans_all_five_block_counts", value=int(spans_all),
    note="the phrase 'across block counts 8 through 48' names the scope of the sweep "
         "rather than the two S values the endpoints come from, so the wording covers "
         "S equal to 48, which is not re-emitted, while the two numeric figures quoted "
         "do not depend on it")
add("A2_repair_candidate", item="narrow_the_wording", value=1,
    note="restate the scope as the block counts re-emitted on repaired code, so the "
         "sentence carries no figure and no scope that S equal to 48 could move")
add("A2_repair_candidate", item="leave_open_pending_S48", value=1,
    note="leave the wording and carry the item open at 9.48 until S equal to 48 "
         "re-emits, since the two quoted figures already stand on repaired code")
add("A2_repair_candidate", item="recommendation", value="none",
    note="the scaffold requires no change and no recommendation in this phase")

# ---- standing positive control ----------------------------------------------
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]; ret = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
m = L.standalone_metrics(ret, d["nav"], acc["orders"])
pc = (abs(m["ann_return"]-0.521845) <= TOL and abs(m["sharpe_lo"]-1.381701) <= TOL
      and len(ret) == 2472)
add("positive_control", item="tolerance", value=TOL, note="stated before comparing")
add("positive_control", item="ann_return", value=m["ann_return"], target=0.521845)
add("positive_control", item="sharpe_lo", value=m["sharpe_lo"], target=1.381701)
add("positive_control", item="n_sessions", value=len(ret), target=2472)
add("positive_control", item="verdict", note="PASS" if pc else "FAIL")
print(f"positive control {'PASS' if pc else 'FAIL'} "
      f"ann {m['ann_return']:.6f} lo {m['sharpe_lo']:.6f} n {len(ret)}")

fn = ["table","item","value","rank","null_mean","null_p05","null_p95",
      "inside_own_null","flag_consistent_with_bounds","target","note"]
with open(OUT/"claim-checks.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
    for r in rows: w.writerow({k: r.get(k,"") for k in fn})
print(f"wrote outputs/session-25/claim-checks.csv, {len(rows)} rows")
