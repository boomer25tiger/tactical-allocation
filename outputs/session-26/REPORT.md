# Session 26, the prediction commit

2026-08-22. Five phases. One commit, at phase E. No measurement ran, so no positive control was required.

## Opening

**4 decisions applied and one withdrawal added.**

| decision | register | kind |
|---|---|---|
| claim 4's scope phrase narrowed to the re-emitted block counts | 9.59 | correctness repair, being a wording repair |
| the paper's figure cap raised from two to six | 9.60 | specification change |
| 9.56's grounds recorded in the narrowed form | 9.61 | register decision |
| the size convention | 9.62 | documentation |
| the section 4 holdout prediction withdrawn | 9.63 | register decision, recorded as documentation of a withdrawal |

**The prediction is written and carries five components.** P1 is the primary rank prediction, P2 the Sharpe band, P3 the two-part mechanism, P4 the named unknown with its guard, and P5 the interesting failure mode.

**Pre-commit readings.** Working tree 826564 KiB, git directory 206024 KiB, free space 18.57 GiB. The expected delta is +0 KiB on the working tree, since every file the commit touches is already written to disk, so the working tree reading above already includes them and committing adds no working tree bytes, and +81 or less KiB on the git directory. Free space is expected to read 0.00 to -0.01 GiB different. **The readings were taken immediately before this report was written**, so they exclude this file's own bytes and the git objects the staging of it writes.

## Phase A, the four decisions

### A1, claim 4's scope phrase narrowed to the re-emitted block counts

Register 9.59. **Correctness repair, being a wording repair.**

Before. *Probability of backtest overfitting is 0.1578088578088578 at S equal to 16 over the full 12,870 combination enumeration, spanning 0.11428571428571428 to 0.170995670995671 across block counts 8 through 48.*

After. *Probability of backtest overfitting is 0.1578088578088578 at S equal to 16 over the full 12,870 combination enumeration, spanning 0.11428571428571428 to 0.170995670995671 across the block counts 8, 12, 16 and 24 re-emitted on repaired code.*

Grounds. The two quoted figures are 0.11428571428571428 at S equal to 8 and 0.170995670995671 at S equal to 12, both re-emitted on repaired code at 9.48, and neither depends on the unre-emitted S equal to 48. No quoted figure moved and the claim asserts the same thing about the same numbers.

### A2, the paper's figure cap raised from two to six

Register 9.60. **Specification change.**

Before. *the paper carries two figures with the rest carried by the PBO report*

After. *the paper carries at most six figures with the rest carried by the PBO report, and six is fixed rather than left open*

Grounds. The cap of two was set before the paper's shape was known. Eight figures are drawn at 9.55 and four of them illustrate no frozen claim, so a cap of two forced a choice the evidence did not support. Six is fixed now rather than after the holdout is read, so no figure is added on the basis of what the read shows.

### A3, 9.56's grounds recorded in the narrowed form

Register 9.61. **Register decision.**

Before. *the strategy's own Lo factor sits inside its own no-autocorrelation null while buy-and-hold QQQ's sits outside*

After. *the narrowed form, being that buy-and-hold QQQ's Lo factor at 1.8033205778849906 sits outside its own null upper bound of 1.47866235794891 while the strategy's at 1.3817011382923612 sits inside its own bound of 1.5045050578577397. The general form fails, since long_legs_only at 1.4695627600234846 and vol_targeted_QQQ_matched at 1.4304523894100714 both outrank the strategy from inside their own nulls, their upper bounds being 1.5153672392519424 and 1.5159596470316377*

Grounds. The 8.2 decision to lead on the naive Sharpe rests on the narrowed form together with the q sweep moving nine of twelve ladder rows in rank, the second being independent of the null finding, so 8.2 does not rest on the form that fails.

### A4, the size convention

Register 9.62. **Documentation.**

Before. *repository size and free space are read before and after the commit*

After. *repository size, working tree size and free space are read before the commit and reported with the expected delta stated, and no figure is read after the commit*

Grounds. Session 25 ended with two dirty files carrying post-commit readings, which a one-commit session cannot contain. Reading pre-commit and stating the expected delta leaves no file dirty. Applies from session 26 forward.

## Phase B, the withdrawal

Register 9.63. **Withdrawn by argument rather than by measurement**, the two underlying measurements being session 22's leave-one-out rebuild and session 22's beta window sensitivity, each of which confirmed its own figures without supporting the inference chain. The base estimate reproduces at 1.3817013060244996 and the timing component reads 0.011293050910284682 at 60 sessions against -0.0077512681113622505 at 504. Recorded as withdrawal 11 in `docs/WITHDRAWN.md`, which now carries 11 against 10 before.

## Phase C, the prediction

`docs/HOLDOUT-PREDICTION.md`, 10496 bytes, SHA-256 3a3d150e986bcedfb9946deeb299373efac7026e7ccc7ca45625b9553fbecb2f.

The sealed span runs from 2021-08-01 to 2026-08-14, the latter read from `outputs/session-00e/manifest-truncated.csv` across all 39 frozen inputs. The primary window carries 2472 sessions.

**The holdout session count is not stated.** Register 2.10 records that no post-boundary quantity has been computed anywhere, and counting sessions inside the sealed span is a post-boundary quantity. The scaffold asked for it, and it is left for the read with the reason recorded rather than computed.

| component | prediction | falsified by |
|---|---|---|
| P1 | the strategy ranks no better than sixth of twelve on the naive Sharpe | any rank of fifth or better |
| P2 | the holdout naive Sharpe lands between 0.25 and 0.85, against 1.0910863648060856 over the primary window | above 0.85 or below 0.25 |
| P3 part one | SQQQ and TLT realise positive daily return correlation over the holdout | a negative realised correlation |
| P3 part two | T10's risk-off branch contributes negatively to holdout return | a positive contribution |
| P4 | state-classification latency in a slow bear is not predicted | nothing, since it makes no prediction |
| P5 | if P1 fails, 2022 gave the short sleeve its only sustained tailwind | recorded as less likely than even |

**P3 part two is the weaker half and the document says so.** The branch's short leg already contributes -1.074235187878671 arithmetically over the primary window at `outputs/session-15.5/short-leg-decomposition.csv`, so part two predicts that an observed sign persists while part one predicts that a sign flips against a committed baseline of -0.5618926986740371.

**Six items the scaffold named are not carried as it stated them.** Each is recorded rather than adopted, in `outputs/session-26/prompt-disagreements.csv` and in the document's closing section.

| item | the scaffold | the source | kind |
|---|---|---|---|
| buy_hold_QQQ_ann_turnover | 0.02 | 0.017286585046131533 | rounding |
| crisis_years | fast crashes in 2011, 2018 and 2020 | 2011 1.5635962707744817, 2020 1.6183359759194622, 2018 1.287076427656795 against a base of 1.3817013060244996 | figure |
| mean_effective_exposure | near 1.70 | 1.7769723457408557 | figure |
| sqqq_sites | four sites across three sleeves | 5 sites across 3 sleeves | figure |
| lag_mechanism | session 15 located the mechanism of the dip-buying signal firing roughly one session early in fast crashes so  | the register's corrections list item 12 records an execution-lag sensitivity in which annualised return improves under one extra s | unsupported claim |
| holdout_session_count | the session count against the primary window's 2,472 | not established | not computed |
| tlt_2022 | TLT had its worst year in decades in 2022 | not in any emitted file | external fact |

**Three external premises are labelled as external** rather than sourced, being that the policy rate exceeded five percent inside the holdout, that the holdout contains the only sustained bear in either window, and that TLT had its worst year in decades in 2022. No committed CSV carries any of them and establishing any from the panel would be a post-boundary quantity. P5 rests on the third, which is why it is recorded as less likely than even.

## Phase D, the verification hook

`scripts/verify_prediction_precedes_read.py`, run as the first step of any holdout session. It confirms the prediction exists in committed history, reports the commit SHA with its author and commit timestamps, confirms the working copy is unmodified against that commit, and reports the file's hash.

**Run in this session before the commit, it exits 1**, reporting that the file appears in no commit. That is the correct answer at that moment, since the commit happens at phase E. **The first context in which it exits zero is a session running after this commit.**

## What each item is

| item | what acting on it is |
|---|---|
| claim 4's scope phrase narrowed | correctness repair, being a wording repair |
| the figure cap raised from two to six | specification change |
| 9.56's grounds recorded in the narrowed form | register decision |
| the size convention | documentation |
| the section 4 prediction withdrawn | register decision |
| the prediction document frozen | specification change, since it constrains every later session |
| the verification hook | specification change, since it gates the holdout session |
| the six scaffold figures not carried as stated | correctness repair on four of them and documentation on two |
| the holdout session count left uncomputed | documentation |

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count above the limit is 0.

| reading | before the commit | expected delta |
|---|---|---|
| working tree, KiB | 826564 | +0 |
| git directory, KiB | 206024 | +81 or less |
| free space, GiB | 18.57 | 0.00 to -0.01 |

The commit touches 22 files totalling 310430 bytes on disk, of which 13 files and 82816 bytes are new to the repository. **Nothing is read after the commit**, under the convention adopted at 9.62, so this session leaves no dirty file.

## What remains before the holdout can run

**Nothing.** The claim set is frozen with claim 4's wording repaired, the prediction is committed and frozen, the verification hook is in place, the figure cap is fixed at six, and the withdrawn set records what the project stopped believing. S equal to 48 of the B1 re-emission remains outstanding at 9.48 and sets neither endpoint of any quoted range, and the corrected degradation null remains unrun at 9.46 with its slope withdrawn at 9.35, so neither is load-bearing and neither blocks the read.

The holdout session's first step is `scripts/verify_prediction_precedes_read.py`, and it proceeds only if that exits zero.

## Register

9.59 claim 4's narrowed wording. 9.60 the figure cap at six. 9.61 the 8.2 grounds in the narrowed form. 9.62 the size convention. 9.63 the section 4 prediction withdrawn. 9.64 the prediction frozen. 9.65 the verification hook.

## Artifacts

- `outputs/session-26/decisions-applied.csv`
- `outputs/session-26/prediction-sources.csv`
- `outputs/session-26/prompt-disagreements.csv`
- `outputs/session-26/size-and-verification.csv`
- `docs/HOLDOUT-PREDICTION.md`
- `scripts/verify_prediction_precedes_read.py`

