from __future__ import annotations
import csv
from pathlib import Path
OUT = Path("/Users/GualyCr/Downloads/tactical-allocation/outputs/session-19_6")


def rd(n):
    return list(csv.DictReader(open(OUT / n)))


dn, hc, j13 = rd("degradation-null.csv"), rd("held-composition.csv"), rd("jan2013-read.csv")
dg, nc = rd("m1-diagnostic.csv"), rd("m1-nis-correction.csv")
ms = rd("machine-state.csv")


def g(rows, t, i, f="value"):
    for r in rows:
        if r["table"] == t and r.get("item") == i:
            return r.get(f)
    return None


def fl(rows, t, i, f="value"):
    v = g(rows, t, i, f)
    return float(v) if v not in (None, "") else float("nan")


def gm(rows, t, m, f="value", chunk=None):
    for r in rows:
        if r["table"] == t and r.get("metric") == m and (chunk is None or r.get("chunk") == str(chunk)):
            return r.get(f)
    return None


L = []
A = L.append
A("# Session 19.6 report")
A("")
A("Three measurements, all read-only against the repository outside")
A("`outputs/session-19_6/`. Nothing was repaired, nothing committed, no register entry")
A("written, and the 2021-08-01 holdout boundary is untouched. The stored 48-block")
A("moment array was reused, which is not a grid re-execution. Every figure below is")
A("read from an emitted CSV in this directory.")
A("")
A("## M1 positive control, and what it uncovered")
A("")
A("The positive control **passes**, reproducing all four session 19 figures at a gap of")
A("exactly zero against a 1e-12 tolerance stated before comparing, with the chunk")
A("pinned to 514.")
A("")
A("| figure | reproduced | target | gap |")
A("|---|---|---|---|")
for k in ("pbo", "degradation_slope", "degradation_intercept", "degradation_r_squared"):
    A(f"| {k} | {g(dn,'positive_control',k)} | {g(dn,'positive_control',k,'target')} | "
      f"{float(g(dn,'positive_control',k,'abs_gap')):.1e} |")
A("")
A("Pinning the chunk is not cosmetic. A first attempt derived the chunk from a memory")
A("ceiling, produced 128, and **failed** the same control on three of the four figures,")
A("with the slope off by 1.8e-04. The chunk sweep that followed is the reason the")
A("failure is reported rather than tuned away.")
A("")
A("| chunk | PBO gap | slope gap | seconds | peak GB |")
A("|---|---|---|---|---|")
for c in (128, 257, 514):
    A(f"| {c} | {float(gm(dg,'chunk_sweep','pbo','abs_gap',c)):.1e} | "
      f"{float(gm(dg,'chunk_sweep','degradation_slope','abs_gap',c)):.2e} | "
      f"{gm(dg,'chunk_sweep','seconds',chunk=c)} | {gm(dg,'chunk_sweep','peak_rss_gb',chunk=c)} |")
A("")
A("PBO is identical at every chunk size while the three regression figures are not, and")
A(f"{gm(dg,'selection_stability','selections_differing_from_chunk_514',chunk=128)} of "
  f"12,870 selections differ between chunk 128 and chunk 514, so the cause is not the")
A("argmax flipping.")
A("")
A("### The cause, in `scripts/s19_step4.py` lines 143 and 144")
A("")
A("```")
A("        n_is = float(mc[0] @ nvec)")
A("        n_os = float(oc[0] @ nvec)")
A("```")
A("")
A("The in-sample session count is taken from the **first combination of each chunk** and")
A("applied to every combination in that chunk. The merged super-block counts are")
A(f"unequal, spanning {int(fl(nc,'counts','superblock_min') if False else float(gm(nc,'counts','superblock_min')))} to "
  f"{int(float(gm(nc,'counts','superblock_max')))} sessions, so the true in-sample count varies across")
A(f"combinations from {int(float(gm(nc,'counts','n_is_true_min')))} to "
  f"{int(float(gm(nc,'counts','n_is_true_max')))} across "
  f"{int(float(gm(nc,'counts','n_is_distinct_values')))} distinct values. The chunk boundaries therefore")
A("enter the emitted figures. The same line is at `scripts/s18_step3.py` line 142, so")
A("the defect originates in session 18 and was inherited unchanged.")
A("")
A("PBO is unaffected because within a chunk the substituted count scales every")
A("specification identically and rank ordering is preserved. The regression compares")
A("Sharpe levels across combinations, which is where the count enters.")
A("")
A("Recomputing at chunk 514 with the exact per-combination count gives the following.")
A("")
A("| figure | as emitted | exact count | shift |")
A("|---|---|---|---|")
for k, lbl in (("pbo", "pbo"), ("degradation_slope", "slope"),
               ("degradation_intercept", "intercept"), ("degradation_r_squared", "R-squared")):
    A(f"| {lbl} | {gm(nc,'correction',k,'as_emitted')} | {gm(nc,'correction',k)} | "
      f"{float(gm(nc,'correction',k,'abs_gap')):.3e} |")
A("")
A("## M1 result, the mechanical null")
A("")
A("The null permutes the 48 stored blocks independently per specification at seed")
A(f"{int(fl(dn,'setup','null_seed'))} fixed before drawing, then merges to 16 by the same")
A("adjacent-triple reduction. Each specification keeps its own full-window moments, and")
A(f"the full-window naive Sharpe is preserved to {float(g(dn,'marginal_control','max_abs_sharpe_deviation')):.3e}")
A("against a 1e-10 tolerance stated before comparing. What survives is the")
A("complementary-half arithmetic and nothing else.")
A("")
A(f"The pilot replication ran in {fl(dn,'pilot','seconds'):.1f} s. A wall-clock budget of")
A(f"{int(fl(dn,'setup','wall_budget_seconds'))} s stated before the count was chosen gives")
A(f"**{int(fl(dn,'replication_count','chosen'))} replications**, and the count is set by that")
A("budget rather than by a power calculation.")
A("")
A("| quantity | null mean | null sd | null 5th | null 95th | observed | z | percentile |")
A("|---|---|---|---|---|---|---|---|")
for k, lbl in (("slope", "slope"), ("intercept", "intercept"),
               ("r2", "R-squared"), ("pbo", "PBO")):
    note = g(dn, "observed_vs_null", k, "note")
    z = note.split("z ")[1].split(",")[0]
    pct = note.split("percentile ")[1].split(",")[0]
    A(f"| {lbl} | {fl(dn,'null',k):.6f} | {fl(dn,'null',k+'_sd'):.6f} | "
      f"{fl(dn,'null',k+'_p05'):.6f} | {fl(dn,'null',k+'_p95'):.6f} | "
      f"{fl(dn,'observed_vs_null',k):.6f} | {z} | {pct} |")
A("")
A(f"**The null slope is centred at {fl(dn,'null','slope'):.6f}**, which is neither near")
A("zero nor near minus one. Partition arithmetic alone therefore carries most of the")
A(f"observed slope's magnitude, and the observed {fl(dn,'observed_vs_null','slope'):.6f}")
A(f"carries a z of {g(dn,'observed_vs_null','slope','note').split('z ')[1].split(',')[0]}")
A("against the null mean, at the null's 0th percentile.")
A("")
A("Stated as measured. A null slope near minus one would mean the observed slope")
A("carries little information beyond partition arithmetic. A null slope near zero would")
A("mean it measures degradation. The measured null sits between the two, so part of the")
A("observed slope is mechanical and part is not, and the emitted figure separates the")
A("two nowhere.")
A("")
A(f"The other three comparisons are larger. Null R-squared averages")
A(f"{fl(dn,'null','r2'):.6f} against an observed {fl(dn,'observed_vs_null','r2'):.6f}, and")
A(f"null PBO averages {fl(dn,'null','pbo'):.6f} against an observed")
A(f"{fl(dn,'observed_vs_null','pbo'):.6f}. Under the null the in-sample-best")
A("specification lands in the bottom half of the out-of-sample ranking almost always,")
A("which is what destroying cross-specification block alignment produces.")
A("")
A("No recommendation follows and nothing was changed.")
A("")
A("## M2, composition on held tickers only")
A("")
A("The held universe is derived from the abstract syntax tree of `src/sleeves.py`. A")
A("ticker is held if it carries a non-zero weight in a returned dictionary or is")
A("returned as a bare ticker string by a terminal helper. No list is written by hand,")
A("which is the convention `scripts/s195_strip.py` breached.")
A("")
A(f"**{int(fl(hc,'counts','n_held'))} held tickers** and")
A(f"**{int(fl(hc,'counts','n_signal_only'))} signal-only tickers**. QQQE is signal-only,")
A("confirming that the 19.5 binding constraint was a ticker the strategy never holds.")
A("")
A("Four tickers are classified differently by the hardcoded list.")
A("")
A("| ticker | difference |")
A("|---|---|")
for r in hc:
    if r["table"] == "classification_differs" and r["item"] != "count":
        A(f"| {r['item']} | {r['note']} |")
A("")
A("### Warmup, derived rather than assumed")
A("")
A(f"The moving average at {int(fl(hc,'warmup','max_sma_lookback'))} sessions binds, since")
A(f"it exceeds Wilder RSI seed convergence at {int(fl(hc,'warmup','rsi_seed_convergence_sessions'))}")
A(f"sessions for the grid maximum period of {int(fl(hc,'warmup','max_rsi_period'))}. The derived")
A(f"requirement is {int(fl(hc,'warmup','derived_requirement'))} against")
A(f"`config.WARMUP_SESSIONS` of {int(fl(hc,'warmup','config_WARMUP_SESSIONS'))}, a stated")
A(f"margin of {int(fl(hc,'warmup','stated_margin'))}.")
A("")
A("### Full composition on held tickers")
A("")
A(f"| arm | date | binding |")
A("|---|---|---|")
for arm in ("synthetic", "realized"):
    A(f"| {arm} | {g(hc,'full_composition',arm,'note')} | {g(hc,'full_composition',arm,'note2')} |")
A("")
A("Neither date falls before 2011-10-04, so the conclusion that the panel supports no")
A("earlier full-composition start survives the correction, while the 19.5 date of")
A("2013-01-23 is superseded on the synthetic arm by")
A(f"{g(hc,'full_composition','synthetic','note')}.")
A("")
A(f"Two held tickers, SVIX and UVIX, are never available on either panel, so a strict")
A("reading of full composition is unreachable on any date. They are reached only through")
A("an availability switch that resolves to SVXY and UVXY, and the dates above are")
A("computed over the tickers that do load.")
A("")
A("### The two measures side by side")
A("")
A(f"Over the canonical window of {int(fl(hc,'two_measures','window_sessions'))} sessions,")
A(f"**{int(fl(hc,'two_measures','sessions_any_held_ticker_unavailable'))} sessions** carry at")
A(f"least one held ticker unlisted on the realized panel, a share of")
A(f"{fl(hc,'two_measures','share'):.4f}. Over the same window")
A(f"`outputs/session-16/boundary-correction.csv` records")
A(f"**{fl(hc,'two_measures','unavailable_fills_from_2011_10_04'):.1f} unavailable fills**.")
A("The two are different quantities. Listing coverage counts sessions where a ticker was")
A("unlisted whether or not it was targeted, and the 7.14 measure counts fills the")
A("strategy attempted and could not make. The 19.5 report presented the first without")
A("distinguishing it from the second.")
A("")
A("## M3, the fourteen sessions at the front of the 2013-01-02 arm")
A("")
A(f"The front span runs {g(j13,'front','first_session','note')} to")
A(f"{g(j13,'front','last_session','note')}, being {int(fl(j13,'front','n_sessions'))} sessions.")
A(f"Its cumulative return is **{fl(j13,'front','cumulative_return'):.6f}**, and UVXY is held")
A(f"on {int(fl(j13,'front','n_sessions_uvxy_held'))} of those sessions.")
A("")
A("| date | return | UVXY held | holdings |")
A("|---|---|---|---|")
for r in j13:
    if r["table"] == "front_session":
        A(f"| {r['item']} | {float(r['value']):+.6f} | {'yes' if r['within']=='1' else 'no'} | "
          f"{r['note']} |")
A("")
A("Terminal identity per sleeve is in `jan2013-read.csv`, matched by the ticker set each")
A("sleeve returns against the terminal strings in")
A("`outputs/session-18/reachability.csv`, and reported against the prior calendar")
A("position since `run_account` fills with a one-session lag.")
A("")
A("### The arithmetic verifies")
A("")
A(f"Compounding the late arm's growth of {fl(j13,'verification','growth_late_arm'):.6f} with")
A(f"the front span's {fl(j13,'verification','growth_front_span'):.6f} and annualising over")
A(f"{int(fl(j13,'arms','early_start'))} sessions gives")
A(f"{fl(j13,'verification','ann_reconstructed'):.16f} against the emitted")
A(f"{fl(j13,'verification','ann_emitted'):.16f}, a gap of")
A(f"{fl(j13,'verification','abs_gap'):.3e} inside a 1e-9 tolerance stated before")
A("comparing. The premise holds and the difference between the two arms is carried")
A("entirely by those sessions.")
A("")
A("### The three overlap figures, now emitted")
A("")
A("| figure | value |")
A("|---|---|")
A(f"| overlapping sessions | {int(fl(j13,'overlap','n_sessions'))} |")
A(f"| daily return correlation | {g(j13,'overlap','daily_return_correlation')} |")
A(f"| max absolute daily return difference | {fl(j13,'overlap','max_abs_daily_return_difference'):.3e} |")
A(f"| cumulative return, early arm | {g(j13,'overlap','cumulative_return_early_arm')} |")
A(f"| cumulative return, late arm | {g(j13,'overlap','cumulative_return_late_arm')} |")
A(f"| position vectors agree every session | "
  f"{'yes' if g(j13,'overlap','position_vectors_agree_every_session')=='1' else 'no'} |")
A("")
A("### The nesting asymmetry")
A("")
A(f"{g(j13,'nesting','consequence','note')}.")
A("")
A("## Findings and the class of change each would need")
A("")
A("| finding | class |")
A("|---|---|")
A("| the in-sample session count is taken from the first combination of each chunk in `s19_step4.py:143` and `s18_step3.py:142` | correctness repair |")
A("| the emitted degradation slope, intercept and R-squared depend on the chunk size, being the same root cause | correctness repair |")
A("| the null slope is centred well away from zero, so most of the observed slope's magnitude is partition arithmetic | register decision on whether the slope is reported at all, documentation if it is |")
A("| the 19.5 full-composition date was bound by a signal input the strategy never holds | documentation, the 19.5 figure is superseded |")
A("| `s195_strip.py` classified four tickers by a hardcoded list that disagrees with the code | correctness repair |")
A("| SVIX and UVIX are held in code and never load on either panel | documentation |")
A("| listing coverage and unavailable fills were conflated in the 19.5 report | documentation |")
A("| the strip compares a nested strategy against re-initialised benchmarks | correctness repair |")
A("| the front span carries the whole difference between the two 2013 arms | documentation |")
A("")
A("No recommendation is made on any of these and nothing was repaired.")
A("")
A("## Resources")
A("")
A("| measurement | wall clock | peak resident |")
A("|---|---|---|")
A(f"| M1 positive control | {fl(dn,'positive_control','seconds'):.1f} s | "
  f"{fl(dn,'positive_control','peak_rss_gb'):.3f} GB |")
A(f"| M1 null, {int(fl(dn,'replication_count','chosen'))} replications | "
  f"{fl(dn,'pilot','seconds'):.1f} s for the pilot | {fl(dn,'resources','peak_rss_gb'):.3f} GB |")
A(f"| M2 | under a second after the environment build | not separately recorded |")
A(f"| M3 | {fl(j13,'resources','seconds'):.1f} s | {fl(j13,'resources','peak_rss_gb'):.3f} GB |")
A("")
A("Two earlier M1 attempts are recorded rather than omitted. The first stated a 5.0 GB")
A(f"ceiling, which sized the chunk at 1286 and drove the machine to "
  f"{g(ms,'m1_attempt_1','observed_cpu_percent')} percent CPU with "
  f"{g(ms,'m1_attempt_1','swap_used_gb')} GB of swap in use. The second stated "
  f"{g(ms,'m1_attempt_2','stated_ceiling_gb')} GB, session 19's own value, and also thrashed, "
  f"because the machine carried {g(ms,'m1_attempt_2','swap_used_gb')} GB of "
  f"{g(ms,'m1_attempt_2','swap_total_gb')} GB swap in use at the time. The "
  f"wall-clock figures here are therefore not comparable with session 19's "
  f"{g(ms,'session19_reference','pass_seconds')} s for the same pass, which is recorded in "
  f"outputs/session-19/pbo.csv.")
A("")
A("## Stop")
A("")
A("Halted after the report. Nothing repaired, nothing committed, no register entry")
A("written, holdout untouched, grid not re-executed, no grid point adopted or promoted.")
A("")
(OUT / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"wrote {OUT/'REPORT.md'} {len('\n'.join(L))} bytes")
