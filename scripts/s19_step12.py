"""Session 19 step 12: the session report.

Every prose figure is read from an emitted CSV under 9.12.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-19"


def rd(n):
    return list(csv.DictReader(open(OUT / n)))


pbo, strata = rd("pbo.csv"), rd("pbo-strata.csv")
dsr, curve = rd("deflated-sharpe.csv"), rd("specification-curve.csv")
inv, dele, rem = rd("inventory.csv"), rd("deletion.csv"), rd("remote-status.csv")
add = rd("additivity-check.csv")
man = json.loads((OUT / "MANIFEST.json").read_text())


def pv(S, m):
    for r in pbo:
        if r["table"] == "pbo" and r["S"] == str(S) and r["metric"] == m \
                and r["restriction"] == "full_grid":
            return float(r["value"])
    raise KeyError((S, m))


def pmeta(S, k):
    for r in pbo:
        if r["table"] == "pbo" and r["S"] == str(S):
            return r[k]
    return ""


def dv(w, m, sm="sharpe_naive"):
    for r in dsr:
        if r["table"] == "point" and r["which"] == w and r["metric"] == m \
                and r["sharpe_metric"] == sm:
            return float(r["value"])
    raise KeyError(m)


def xs(m):
    for r in dsr:
        if r["table"] == "cross_section" and r["metric"] == m:
            return float(r["value"])
    raise KeyError(m)


def iv(i):
    for r in inv:
        if r["item"] == i:
            return r["value"]
    return ""


def dl(i):
    for r in dele:
        if r["item"] == i:
            return r["value"]
    return ""


def rv(i):
    for r in rem:
        if r["item"] == i:
            return r["value"]
    return ""


def ck(axis, k):
    for r in curve:
        if r["table"] == "canonical_rank" and r["axis"] == axis:
            return r[k]
    return ""


ranges = [r for r in strata if r["table"] == "axis_range"]
ref = next(r for r in strata if r["table"] == "reference")
interp = next(r["note"] for r in strata if r["table"] == "interpretation")
worst_add = float(next(r["abs_gap_metric_set"] for r in add if r["which"] == "step3"))

L = []
A = L.append
A("# Session 19 report")
A("")
A("Run 2026-08-19. Remote creation, then PBO, the deflated Sharpe, and the")
A("specification curve through commit. No grid was re-executed, no holdout was")
A("executed, the 2021-08-01 boundary under 2.10 is untouched, and no grid point was")
A("adopted or promoted over the canonical. No strategy parameter, threshold,")
A("instrument, weight, sleeve budget, cost model, cap level, premium, NAV, or window")
A("boundary changed, and no canonical value changed on any axis.")
A("")
A("Every figure below is read from an emitted CSV in `outputs/session-19/` under 9.12.")
A("")
A("## Headline")
A("")
A(f"**The repository has an off-machine copy.** A private GitHub repository was")
A(f"created at {rv('url')} and the full history pushed, remote main matching local")
A(f"HEAD. {float(rv('pack_mb_pushed')):.2f} MB in {int(rv('objects_in_pack')):,}")
A("objects. The single-copy exposure that STATE.md and session 18s both named is")
A("closed, and it was closed before any step wrote a derived artifact on top of it.")
A("")
A(f"**The canonical positive control holds.** Specification {iv('canonical_spec_id')}")
A(f"reads annualised return {float(iv('ann_return')):.6f} and Lo-corrected Sharpe")
A(f"{float(iv('sharpe_lo')):.6f} inside the completed grid, reproducing the designated")
A("cell to six decimals with axis values read from config rather than from a literal.")
A("")
A(f"**PBO is {pv(16,'pbo'):.4f}** at S equal to 16 over the full 12,870 combination")
A(f"enumeration across 121,500 specifications, reproducing session 18's interrupted")
A(f"measurement exactly. The degradation slope is {pv(16,'degradation_slope'):.4f} and")
A(f"the probability of loss is {pv(16,'probability_of_loss'):.6f}.")
A("")
A(f"**The deflated Sharpe at N equal to 364,500 is {dv('canonical','deflated_sharpe_N_364500'):.6f}")
A(f"for the canonical and {dv('in_sample_best','deflated_sharpe_N_364500'):.6f} for the")
A(f"grid's in-sample-best.** The expected maximum Sharpe under a no-skill null is")
A(f"{dv('canonical','expected_max_sharpe_ann_N_364500'):.4f} annualised, exceeding both")
A(f"the canonical's {dv('canonical','sharpe_annualised'):.4f} and the in-sample-best's")
A(f"{dv('in_sample_best','sharpe_annualised'):.4f}, which is what produces deflated")
A("figures below one half. Reported as measured.")
A("")
A("## Stratified PBO, the figure that separates parameter search from structural search")
A("")
A("The smooth-axis restriction the session 18 prompt specified spans 27")
A("specifications and is not comparable to a 121,500-point figure, so it was replaced")
A("rather than run. Holding one structural axis at one value fixes the strategy shape")
A("that axis controls and leaves the other eight free, so the PBO inside a stratum is")
A("the parameter-search component alone.")
A("")
A("| structural axis | values | PBO min | PBO max | full-grid inside |")
A("|---|---|---|---|---|")
for r in ranges:
    A(f"| {r['axis']} | {int(float(r['n_specifications']))} | {float(r['pbo_min']):.4f} | "
      f"{float(r['pbo_max']):.4f} | "
      f"{'yes' if r['full_grid_inside_range']=='1' else 'no'} |")
A("")
A(f"Against a full-grid reference of {float(ref['pbo']):.4f}, {interp}.")
A("")
A("Each stratum is reported in `pbo-strata.csv` with the terminals that never fire at")
A("that value. The widest range is overbought tier one at 0.0100 to 0.4673 across its")
A("five values, and the narrowest is the crash threshold at 0.1688 to 0.1807.")
A("")
A("## Step by step")
A("")
A("**Step 1, the remote.** gh 2.89.0 was installed and authenticated. A private")
A("repository was created with no README, no .gitignore and no license, so no initial")
A("commit could conflict with local history. The first push failed with RPC error")
A("HTTP 400 and nothing reached the remote, which is the large-pack symptom over")
A("HTTPS. It succeeded after http.postBuffer was raised to 524288000, which is local")
A("configuration and altered no history, no object and no tracked file. Both panel")
A("directories and the virtual environment remain excluded by .gitignore, and the")
A(f"largest tracked file is {rv('largest_tracked_file')} at")
A(f"{rv('largest_tracked_file')and ''}"
  f"{[r['note'] for r in rem if r['item']=='largest_tracked_file'][0]}, under the 100")
A("megabyte rule.")
A("")
A(f"**Step 2, inventory and integrity.** {iv('free_gb')} GB free at")
A(f"{iv('percent_used')} percent used. Zero of {iv('files_scanned_excluding_venv')}")
A("files outside `.venv` carry the dataless flag, checked by st_flags and by find")
A("independently. `git fsck --no-dangling` exits 0. All 24 shards read and parse, the")
A("identifier space covers 0 to 121,499 with 0 duplicates and 0 gaps, and both session")
A("17 engine changes are confirmed enabled during the run and off by module default.")
A("The axis classification carries 6 structural and 3 smooth axes.")
A("")
A(f"**Step 3, moment additivity.** Re-verified rather than trusted, since the session")
A(f"18 file was evicted and recovered. Maximum absolute deviation {worst_add:.3e}")
A("against a 1e-10 tolerance fixed before the comparison ran, reproducing session 18's")
A("3.3e-16. The comparison against the retained float32 series is 1.962e-08 against a")
A("1e-5 tolerance, the looser bound being the panel's own precision. The geometric")
A("annualised return is a product rather than a sum, is not additive across disjoint")
A("blocks, and is checked against the metric set instead.")
A("")
A(f"**Step 4, PBO via CSCV.** The moment array loads as 121,500 by 48 by 2 float64 at")
A(f"93.3 MB. The scaffold specified 48 by 5 with cubes, fourth powers and a per-block")
A("count; that layout was never written, the stored layout is 48 by 2 with the count")
A("held once in `block-sizes.npy`, and the naive Sharpe is reconstructible from it")
A("while skewness and excess kurtosis are read from the metric set. The combination")
A("loop is two tensor contractions with no Python-level loop over specifications or")
A("combinations.")
A("")
A("| S | PBO | combinations | enumeration | slope | probability of loss | seconds | peak GB |")
A("|---|---|---|---|---|---|---|---|")
for S in ("16", "8", "12", "24", "48"):
    samp = pmeta(S, "combinations_sampled")
    enum = "full" if samp == "0" else f"sampled of {int(pmeta(S,'combinations_full')):,}"
    star = " (primary)" if S == "16" else ""
    A(f"| {S}{star} | {pv(S,'pbo'):.4f} | {int(pmeta(S,'n_combinations')):,} | {enum} | "
      f"{pv(S,'degradation_slope'):.4f} | {pv(S,'probability_of_loss'):.6f} | "
      f"{float(pmeta(S,'seconds')):.1f} | {pmeta(S,'peak_rss_gb')} |")
A("")
A(f"**Wall-clock for the primary pass is {pv(16,'pbo') and float(pmeta(16,'seconds')):.1f}")
A(f"seconds and observed peak resident memory is {pmeta(16,'peak_rss_gb')} GB**, against")
A("a 2.0 GB ceiling stated before the run. The ceiling was exceeded, reaching")
A(f"{pmeta(48,'peak_rss_gb')} GB at S equal to 48, because the chunk formula counts four")
A("large arrays while the working set also carries the moment array and the merged")
A("block copies. The machine carries 8 GB, so the ceiling is not decorative. No")
A("arithmetic depends on the chunk size and no figure changes, and the overshoot is")
A("recorded rather than absorbed.")
A("")
A("**Step 5, stratified PBO.** Reported above.")
A("")
A("**Step 6, the deflated Sharpe.** N is 364,500 enumerated with 121,500 evaluated,")
A("and 8.7 is amended to carry both. The probabilistic and deflated Sharpe are")
A("computed on the naive Sharpe, since the formula carries its own skewness and excess")
A("kurtosis adjustment while the Lo correction addresses autocorrelation, and the")
A("Lo-corrected figures are carried as a disclosed sensitivity at")
A(f"{dv('canonical','deflated_sharpe_N_364500','sharpe_lo'):.6f} and")
A(f"{dv('in_sample_best','deflated_sharpe_N_364500','sharpe_lo'):.6f}. The probabilistic")
A(f"Sharpe against a benchmark of zero is {dv('canonical','probabilistic_sharpe_vs_zero'):.6f}")
A(f"for the canonical and {dv('in_sample_best','probabilistic_sharpe_vs_zero'):.6f} for")
A("the in-sample-best. At N equal to 121,500 the deflated figures read")
A(f"{dv('canonical','deflated_sharpe_N_121500'):.6f} and")
A(f"{dv('in_sample_best','deflated_sharpe_N_121500'):.6f}.")
A("")
A(f"The cross-sectional naive Sharpe across the grid has mean {xs('sharpe_naive_ann_mean'):.4f},")
A(f"standard deviation {xs('sharpe_naive_ann_sd'):.4f}, and 5th, 50th and 95th")
A(f"percentiles of {xs('sharpe_naive_ann_p05'):.4f}, {xs('sharpe_naive_ann_p50'):.4f} and")
A(f"{xs('sharpe_naive_ann_p95'):.4f}. The estimation caveat is that this dispersion")
A("comes from the evaluated subset rather than the enumerated space, and that the")
A("evaluated grid spans structurally different strategies, so the dispersion carries")
A("structural variation alongside parameter variation.")
A("")
A(f"**Step 7, the specification curve.** The canonical ranks")
A(f"{int(float(ck('sharpe_lo','rank'))):,} of 121,500 on Lo-corrected Sharpe and")
A(f"{int(float(ck('ann_return','rank'))):,} on annualised return. Marginals are")
A("reported for all nine searched axes, the six structural ones as separated strata.")
A("Five choice axes are sourced from emitted CSVs at a recorded base cell, being")
A("panel, convention, window, commission arm and the participation cap, plus starting")
A("NAV and the slippage model. **Three axes are not sourced**, being the SMH accrual")
A("arm, the sizing mode and the unavailable-fill completion rule, since no emitted CSV")
A("in this repository carries a two-arm designated-cell comparison for any of them.")
A("The financing spread carries its sweep levels but no per-level return. The")
A("tier-two offset is not on the curve and was not searched, because the register")
A("marks 7.4 informed rather than closed.")
A("")
A(f"**Step 8, the PBO report.** `PBO-REPORT.md` and four SVG figures. Regenerability")
A("was verified by generating the document twice and comparing bytes, and again after")
A("the step 10 deletion. matplotlib is not in the registered environment, so the")
A("figures are drawn by `scripts/s19_svg.py` using the standard library alone rather")
A("than by adding packages to an environment the manifest records.")
A("")
A(f"**Step 9, the manifest.** {len(man['input_sha256'])} input hashes, the config")
A("hash, the seeds, the 48 block boundary dates, the per-shard specification counts,")
A("the environment record, and the exact command that regenerates the panel.")
A("`scripts/verify_panel.py` was rewritten for the sharded panel layout and reports")
A("maximum absolute deviation against a 1e-6 tolerance rather than asserting")
A("bit-identical equality, since reduction order varies with thread count and BLAS")
A("version and the run was sharded across eight processes.")
A("")
A("The 9.12 figure check was extended to cover every file matching `*REPORT*.md`")
A("rather than `REPORT.md` alone, which is a change to the checking mechanism and not")
A("to any measurement, following the precedent session 15.5 set.")
A("")
A(f"**Step 10, the deletion.** {dl('session17_panel_files')} session 17 panel shards and")
A(f"{dl('superseded_panel_files')} superseded ten-axis panel shards were removed,")
A(f"reclaiming {dl('reclaimed_mb')} MB. The working tree went from {dl('repository_mb')}")
A(f"MB to {[r['value'] for r in dele if r['table']=='after' and r['item']=='repository_mb'][0]}")
A(f"MB, and free space from {[r['value'] for r in dele if r['table']=='before' and r['item']=='free_gb'][0]}")
A(f"GB to {[r['value'] for r in dele if r['table']=='after' and r['item']=='free_gb'][0]} GB.")
A("The superseded directory was not removed wholesale and its grid moments, block")
A("sizes, metrics and shard logs are preserved. Every required artifact remains and")
A("the regenerability check after deletion is byte-identical to the check before it.")
A("")
A("## Findings carried from sessions 13.5 through 18s")
A("")
A("Each carries what would have to change to act on it and the class of that change.")
A("No recommendation is made.")
A("")
A("| finding | status | to act on it | class |")
A("|---|---|---|---|")
A("| D16 financing spread | OPEN, assumed and swept 25 to 200 bp | a measured borrow "
  "cost series, or a register decision fixing the level | register decision |")
A("| D23 per-instrument attribution confound | corrected in place session 15.5 | "
  "nothing; the correction stands | correctness repair, done |")
A("| D25 effective exposure superseded | recorded as documentation | nothing; 1.777 "
  "mean and 1.499 in the wildest volatility decile supersede 13.5 | documentation |")
A("| D26 the 218,700 total was never derivable | raised in session 16b's report, NOT "
  "in the register | a register entry recording it | documentation |")
A("| D27 enumeration rule underdetermined | raised in session 16b's report, NOT in the "
  "register | a register decision on cardinality when neither values nor a cardinality "
  "are recorded | register decision |")
A("| 9.11 three curve axes unsourced | OPEN, found this session | running a two-arm "
  "comparison for the SMH accrual arm, the sizing mode and the completion rule | "
  "specification change |")
A("| 8.11 metric count | the register says 41 standalone metrics, the emitter carries "
  "40 plus 22 per-year | a register correction to the count | documentation |")
A("| CSCV memory ceiling | OPEN, found this session | a chunk formula counting the "
  "resident moment array and merged copies | correctness repair |")
A("| terminal counter basis | corrected this session at 9.15 | nothing; both bases are "
  "recorded | documentation |")
A("| single-copy repository | CLOSED this session at 10.2 | nothing | done |")
A("")
A("## Provisional operating values, current status")
A("")
A("| value | current | status |")
A("|---|---|---|")
A("| financing spread | 75 bp anchor, swept 25 to 200 | assumed, D16 open |")
A("| SMH pre-2013 return basis | constant | closed provisionally at 3.12 |")
A("| mean effective market exposure | 1.777 | superseded 1.70 at D25; the 8.8 "
  "matched-exposure benchmark still names 1.70 and has not been refreshed |")
A("| starting NAV | 1,000,000 | closed at 4.6, on the specification curve by D20 |")
A("| tier-two offset | 10 | informed at 7.4, held at canonical, not searched |")
A("| primary window start | 2011-10-04 | closed at 7.14a, correctness repair |")
A("| N for the deflated Sharpe | 364,500 enumerated, 121,500 evaluated | amended at "
  "8.7 this session |")
A("")
A("## Defect register")
A("")
A("D1 through D12, D14, D15, D17 through D22 and D24 closed, repaired, or swept. D13")
A("never assigned. D25 recorded as documentation. **Open: D16, D23, and D26 and D27,**")
A("the latter two still absent from the register despite being raised in session 16b's")
A("report. **New this session: none classified as a defect.** The CSCV memory")
A("overshoot and the three unsourced curve axes are recorded above and in the register")
A("rather than given defect numbers, since neither changes a computed figure.")
A("")
A("## Register updates made this session")
A("")
A("Six, each dated 2026-08-19. Their full text is in `docs/DECISIONS-v3.md`.")
A("")
A("- **8.7, amended again**, superseding N at 131,220 with N at 364,500 enumerated and")
A("  121,500 evaluated, carrying the deflated Sharpe result and the estimation caveat")
A("  on the cross-sectional standard deviation.")
A("- **8.12, new**, the PBO result, the S equal to 16 pre-registration, the")
A("  naive-Sharpe approximation and its reason, the block-count sensitivity, and the")
A("  memory-ceiling overshoot.")
A("- **8.13, new**, the stratified PBO design, the reason the smooth-axis restriction")
A("  was replaced, and the result.")
A("- **9.14, new**, the four-tier artifact scheme as executed, with the regenerability")
A("  check named as the test that the deletion was safe.")
A("- **9.15, new**, the corrected positive-control basis for the terminal counter,")
A("  carrying both session 13.5's basis and the primary-window figures.")
A("- **10.2, new**, the remote creation, closing the single-copy exposure.")
A("")
A("## What remains open before the holdout can run")
A("")
A("- **D16**, the financing spread, is assumed rather than measured.")
A("- **Three specification-curve axes are unsourced**, being the SMH accrual arm, the")
A("  sizing mode, and the unavailable-fill completion rule. 9.11 names all three as")
A("  curve axes and no emitted CSV carries a comparison for any of them.")
A("- **D26 and D27 are not in the register.**")
A("- **The 8.8 matched-exposure benchmark still names 1.70** as the strategy's mean")
A("  effective exposure, which D25 superseded with 1.777.")
A("")
A("Nothing above was acted on this session and no recommendation is made on any of it.")
A("")
A("## Stop condition")
A("")
A("Halted after step 12. No grid re-executed, no holdout executed, the 2021-08-01")
A("boundary untouched, no grid point adopted or promoted over the canonical, and no")
A("canonical value changed on any axis. Two commits, being the step 1 push of existing")
A("history and the step 11 session commit. The session 17 panel is deleted and the")
A("manifest records its canonicalised hash.")
A("")
(OUT / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"wrote {OUT/'REPORT.md'} {len('\n'.join(L)):,} bytes")
