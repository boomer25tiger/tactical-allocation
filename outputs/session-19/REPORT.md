# Session 19 report

Run 2026-08-19. Remote creation, then PBO, the deflated Sharpe, and the
specification curve through commit. No grid was re-executed, no holdout was
executed, the 2021-08-01 boundary under 2.10 is untouched, and no grid point was
adopted or promoted over the canonical. No strategy parameter, threshold,
instrument, weight, sleeve budget, cost model, cap level, premium, NAV, or window
boundary changed, and no canonical value changed on any axis.

Every figure below is read from an emitted CSV in `outputs/session-19/` under 9.12.

## Headline

**The repository has an off-machine copy.** A private GitHub repository was
created at https://github.com/boomer25tiger/tactical-allocation and the full history pushed, remote main matching local
HEAD. 192.18 MB in 862
objects. The single-copy exposure that STATE.md and session 18s both named is
closed, and it was closed before any step wrote a derived artifact on top of it.

**The canonical positive control holds.** Specification 106312
reads annualised return 0.521845 and Lo-corrected Sharpe
1.381701 inside the completed grid, reproducing the designated
cell to six decimals with axis values read from config rather than from a literal.

**PBO is 0.1578** at S equal to 16 over the full 12,870 combination
enumeration across 121,500 specifications, reproducing session 18's interrupted
measurement exactly. The degradation slope is -1.0663 and
the probability of loss is 0.000078.

**The deflated Sharpe at N equal to 364,500 is 0.000660
for the canonical and 0.023736 for the
grid's in-sample-best.** The expected maximum Sharpe under a no-skill null is
2.1082 annualised, exceeding both
the canonical's 1.0911 and the in-sample-best's
1.4723, which is what produces deflated
figures below one half. Reported as measured.

## Stratified PBO, the figure that separates parameter search from structural search

The smooth-axis restriction the session 18 prompt specified spans 27
specifications and is not comparable to a 121,500-point figure, so it was replaced
rather than run. Holding one structural axis at one value fixes the strategy shape
that axis controls and leaves the other eight free, so the PBO inside a stratum is
the parameter-search component alone.

| structural axis | values | PBO min | PBO max | full-grid inside |
|---|---|---|---|---|
| sma_long | 4 | 0.1033 | 0.1882 | yes |
| crash_threshold | 5 | 0.1688 | 0.1807 | no |
| rsi_dip | 3 | 0.0667 | 0.1874 | yes |
| rsi_rs | 3 | 0.1232 | 0.2303 | yes |
| overbought_t1 | 5 | 0.0100 | 0.4673 | yes |
| oversold | 5 | 0.0731 | 0.2026 | yes |

Against a full-grid reference of 0.1578, the full-grid PBO exceeds none of the 6 within-stratum ranges, lying inside 5 of them and below 1, which indicates search across strategy shapes does not contribute overfitting beyond parameter search, with the one range it falls below indicating the full grid overfits less than any single stratum of that axis.

Each stratum is reported in `pbo-strata.csv` with the terminals that never fire at
that value. The widest range is overbought tier one at 0.0100 to 0.4673 across its
five values, and the narrowest is the crash threshold at 0.1688 to 0.1807.

## Step by step

**Step 1, the remote.** gh 2.89.0 was installed and authenticated. A private
repository was created with no README, no .gitignore and no license, so no initial
commit could conflict with local history. The first push failed with RPC error
HTTP 400 and nothing reached the remote, which is the large-pack symptom over
HTTPS. It succeeded after http.postBuffer was raised to 524288000, which is local
configuration and altered no history, no object and no tracked file. Both panel
directories and the virtual environment remain excluded by .gitignore, and the
largest tracked file is outputs/session-18/spec-index-augmented.csv at
29.10 MB, under the 100
megabyte rule.

**Step 2, inventory and integrity.** 23.6 GB free at
95.2 percent used. Zero of 906
files outside `.venv` carry the dataless flag, checked by st_flags and by find
independently. `git fsck --no-dangling` exits 0. All 24 shards read and parse, the
identifier space covers 0 to 121,499 with 0 duplicates and 0 gaps, and both session
17 engine changes are confirmed enabled during the run and off by module default.
The axis classification carries 6 structural and 3 smooth axes.

**Step 3, moment additivity.** Re-verified rather than trusted, since the session
18 file was evicted and recovered. Maximum absolute deviation 3.331e-16
against a 1e-10 tolerance fixed before the comparison ran, reproducing session 18's
3.3e-16. The comparison against the retained float32 series is 1.962e-08 against a
1e-5 tolerance, the looser bound being the panel's own precision. The geometric
annualised return is a product rather than a sum, is not additive across disjoint
blocks, and is checked against the metric set instead.

**Step 4, PBO via CSCV.** The moment array loads as 121,500 by 48 by 2 float64 at
93.3 MB. The scaffold specified 48 by 5 with cubes, fourth powers and a per-block
count; that layout was never written, the stored layout is 48 by 2 with the count
held once in `block-sizes.npy`, and the naive Sharpe is reconstructible from it
while skewness and excess kurtosis are read from the metric set. The combination
loop is two tensor contractions with no Python-level loop over specifications or
combinations.

| S | PBO | combinations | enumeration | slope | probability of loss | seconds | peak GB |
|---|---|---|---|---|---|---|---|
| 16 (primary) | 0.1578 | 12,870 | full | -1.0663 | 0.000078 | 775.0 | 2.879 |
| 8 | 0.1143 | 70 | full | -1.1612 | 0.000000 | 0.4 | 2.879 |
| 12 | 0.1710 | 924 | full | -1.2723 | 0.000000 | 88.2 | 2.879 |
| 24 | 0.1646 | 20,000 | sampled of 2,704,156 | -1.1477 | 0.002150 | 598.2 | 3.348 |
| 48 | 0.1540 | 20,000 | sampled of 32,247,603,683,100 | -0.9553 | 0.001400 | 962.5 | 3.355 |

**Wall-clock for the primary pass is 775.0
seconds and observed peak resident memory is 2.879 GB**, against
a 2.0 GB ceiling stated before the run. The ceiling was exceeded, reaching
3.355 GB at S equal to 48, because the chunk formula counts four
large arrays while the working set also carries the moment array and the merged
block copies. The machine carries 8 GB, so the ceiling is not decorative. No
arithmetic depends on the chunk size and no figure changes, and the overshoot is
recorded rather than absorbed.

**Step 5, stratified PBO.** Reported above.

**Step 6, the deflated Sharpe.** N is 364,500 enumerated with 121,500 evaluated,
and 8.7 is amended to carry both. The probabilistic and deflated Sharpe are
computed on the naive Sharpe, since the formula carries its own skewness and excess
kurtosis adjustment while the Lo correction addresses autocorrelation, and the
Lo-corrected figures are carried as a disclosed sensitivity at
0.010884 and
0.085737. The probabilistic
Sharpe against a benchmark of zero is 0.999715
for the canonical and 0.999998 for
the in-sample-best. At N equal to 121,500 the deflated figures read
0.001979 and
0.048847.

The cross-sectional naive Sharpe across the grid has mean 0.6199,
standard deviation 0.4520, and 5th, 50th and 95th
percentiles of -0.2660, 0.7442 and
1.1597. The estimation caveat is that this dispersion
comes from the evaluated subset rather than the enumerated space, and that the
evaluated grid spans structurally different strategies, so the dispersion carries
structural variation alongside parameter variation.

**Step 7, the specification curve.** The canonical ranks
6,834 of 121,500 on Lo-corrected Sharpe and
8,237 on annualised return. Marginals are
reported for all nine searched axes, the six structural ones as separated strata.
Five choice axes are sourced from emitted CSVs at a recorded base cell, being
panel, convention, window, commission arm and the participation cap, plus starting
NAV and the slippage model. **Three axes are not sourced**, being the SMH accrual
arm, the sizing mode and the unavailable-fill completion rule, since no emitted CSV
in this repository carries a two-arm designated-cell comparison for any of them.
The financing spread carries its sweep levels but no per-level return. The
tier-two offset is not on the curve and was not searched, because the register
marks 7.4 informed rather than closed.

**Step 8, the PBO report.** `PBO-REPORT.md` and four SVG figures. Regenerability
was verified by generating the document twice and comparing bytes, and again after
the step 10 deletion. matplotlib is not in the registered environment, so the
figures are drawn by `scripts/s19_svg.py` using the standard library alone rather
than by adding packages to an environment the manifest records.

**Step 9, the manifest.** 39 input hashes, the config
hash, the seeds, the 48 block boundary dates, the per-shard specification counts,
the environment record, and the exact command that regenerates the panel.
`scripts/verify_panel.py` was rewritten for the sharded panel layout and reports
maximum absolute deviation against a 1e-6 tolerance rather than asserting
bit-identical equality, since reduction order varies with thread count and BLAS
version and the run was sharded across eight processes.

The 9.12 figure check was extended to cover every file matching `*REPORT*.md`
rather than `REPORT.md` alone, which is a change to the checking mechanism and not
to any measurement, following the precedent session 15.5 set.

**Step 10, the deletion.** 8 session 17 panel shards and
8 superseded ten-axis panel shards were removed,
reclaiming 1256.8 MB. The working tree went from 1764.7
MB to 508.0
MB, and free space from 25.1
GB to 25.5 GB.
The superseded directory was not removed wholesale and its grid moments, block
sizes, metrics and shard logs are preserved. Every required artifact remains and
the regenerability check after deletion is byte-identical to the check before it.

## Findings carried from sessions 13.5 through 18s

Each carries what would have to change to act on it and the class of that change.
No recommendation is made.

| finding | status | to act on it | class |
|---|---|---|---|
| D16 financing spread | OPEN, assumed and swept 25 to 200 bp | a measured borrow cost series, or a register decision fixing the level | register decision |
| D23 per-instrument attribution confound | corrected in place session 15.5 | nothing; the correction stands | correctness repair, done |
| D25 effective exposure superseded | recorded as documentation | nothing; 1.777 mean and 1.499 in the wildest volatility decile supersede 13.5 | documentation |
| D26 the 218,700 total was never derivable | raised in session 16b's report, NOT in the register | a register entry recording it | documentation |
| D27 enumeration rule underdetermined | raised in session 16b's report, NOT in the register | a register decision on cardinality when neither values nor a cardinality are recorded | register decision |
| 9.11 three curve axes unsourced | OPEN, found this session | running a two-arm comparison for the SMH accrual arm, the sizing mode and the completion rule | specification change |
| 8.11 metric count | the register says 41 standalone metrics, the emitter carries 40 plus 22 per-year | a register correction to the count | documentation |
| CSCV memory ceiling | OPEN, found this session | a chunk formula counting the resident moment array and merged copies | correctness repair |
| terminal counter basis | corrected this session at 9.15 | nothing; both bases are recorded | documentation |
| single-copy repository | CLOSED this session at 10.2 | nothing | done |

## Provisional operating values, current status

| value | current | status |
|---|---|---|
| financing spread | 75 bp anchor, swept 25 to 200 | assumed, D16 open |
| SMH pre-2013 return basis | constant | closed provisionally at 3.12 |
| mean effective market exposure | 1.777 | superseded 1.70 at D25; the 8.8 matched-exposure benchmark still names 1.70 and has not been refreshed |
| starting NAV | 1,000,000 | closed at 4.6, on the specification curve by D20 |
| tier-two offset | 10 | informed at 7.4, held at canonical, not searched |
| primary window start | 2011-10-04 | closed at 7.14a, correctness repair |
| N for the deflated Sharpe | 364,500 enumerated, 121,500 evaluated | amended at 8.7 this session |

## Defect register

D1 through D12, D14, D15, D17 through D22 and D24 closed, repaired, or swept. D13
never assigned. D25 recorded as documentation. **Open: D16, D23, and D26 and D27,**
the latter two still absent from the register despite being raised in session 16b's
report. **New this session: none classified as a defect.** The CSCV memory
overshoot and the three unsourced curve axes are recorded above and in the register
rather than given defect numbers, since neither changes a computed figure.

## Register updates made this session

Six, each dated 2026-08-19. Their full text is in `docs/DECISIONS-v3.md`.

- **8.7, amended again**, superseding N at 131,220 with N at 364,500 enumerated and
  121,500 evaluated, carrying the deflated Sharpe result and the estimation caveat
  on the cross-sectional standard deviation.
- **8.12, new**, the PBO result, the S equal to 16 pre-registration, the
  naive-Sharpe approximation and its reason, the block-count sensitivity, and the
  memory-ceiling overshoot.
- **8.13, new**, the stratified PBO design, the reason the smooth-axis restriction
  was replaced, and the result.
- **9.14, new**, the four-tier artifact scheme as executed, with the regenerability
  check named as the test that the deletion was safe.
- **9.15, new**, the corrected positive-control basis for the terminal counter,
  carrying both session 13.5's basis and the primary-window figures.
- **10.2, new**, the remote creation, closing the single-copy exposure.

## What remains open before the holdout can run

- **D16**, the financing spread, is assumed rather than measured.
- **Three specification-curve axes are unsourced**, being the SMH accrual arm, the
  sizing mode, and the unavailable-fill completion rule. 9.11 names all three as
  curve axes and no emitted CSV carries a comparison for any of them.
- **D26 and D27 are not in the register.**
- **The 8.8 matched-exposure benchmark still names 1.70** as the strategy's mean
  effective exposure, which D25 superseded with 1.777.

Nothing above was acted on this session and no recommendation is made on any of it.

## Stop condition

Halted after step 12. No grid re-executed, no holdout executed, the 2021-08-01
boundary untouched, no grid point adopted or promoted over the canonical, and no
canonical value changed on any axis. Two commits, being the step 1 push of existing
history and the step 11 session commit. The session 17 panel is deleted and the
manifest records its canonicalised hash.

