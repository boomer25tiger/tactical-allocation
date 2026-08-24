# Session 31, publication readiness

2026-08-23. Seven phases. One commit, at phase G. **The repository stays private and nothing in this session changed visibility.** No measurement ran, no frozen input was repaired, no commit history was rewritten.

## Opening

**Gate A clears.** 0 credential or key patterns matched across 919 tracked text files, swept in full rather than sampled.

**Gate D clears at the third pass.** The canonical reproduces from a clean clone at 0.5218447451814521 annualised and 1.3817013060244996 Lo-corrected over 2472 sessions, inside the stated tolerance, in 37.6 seconds from a 514784 KiB clone.

**Both gates cleared**, so the publication instruction at phase F stands as written.

## Phase A, the audit

1088 tracked files.

| class | files |
|---|---|
| session output | 527 |
| derived artifact | 12 |
| document | 13 |
| code | 218 |
| frozen input | 316 |
| other | 2 |

| directory | bytes | files | tracked |
|---|---|---|---|
| `.pytest_cache/` | 14762 | 5 | 0 |
| `.venv/` | 300663903 | 8828 | 0 |
| `data/` | 36939890 | 348 | 328 |
| `docs/` | 335448 | 13 | 12 |
| `outputs/` | 276110669 | 529 | 527 |
| `scripts/` | 2454555 | 218 | 188 |
| `src/` | 163599 | 18 | 16 |
| `tests/` | 391724 | 14 | 14 |

**Four reader-facing documents were checked and three were absent.**

| document | state before this session |
|---|---|
| README | ABSENT |
| license | ABSENT |
| requirements.txt | ABSENT |
| .gitignore | present |

13 tracked files exceed 10 megabytes, the largest being `outputs/session-18/spec-index-augmented.csv` at 30516699 bytes. None approaches the 100 megabyte limit.

### What should not be public

| kind | hits | files |
|---|---|---|
| email_address | 1 | 1 |
| absolute_home_path | 95 | 94 |

The single email hit is in `scripts/s09_financing.py`, inside the User-Agent header the SEC EDGAR fetch sends, which is a legitimate use of a personal address and is still a personal address.

**`CLAUDE.md` is tracked at the repository root** and describes the working discipline the sessions ran under. It goes public with everything else unless it is removed first, which is a disclosure decision rather than a defect.

### The vendor question

no vendor licence has been read against these artifacts inside this project, so whether every tracked series may be redistributed is not established. The question is reported and not answered, and it bears on the publication decision rather than on any measurement.

| source | artifacts | terms as far as this project establishes them |
|---|---|---|
| etf_and_index_series | 45 | price and total-return history sourced through yfinance from Yahoo Finance, whose terms permit personal use and do not grant redistribution rights. REDISTRIBUTION IS NOT ESTABLISHED as permitted and the question is reported rather than answered here |
| cboe_vx_settles | 274 | Cboe VX futures daily settlement, published by Cboe on its own site. The terms attach to the publisher rather than to a purchase and the question is reported rather than answered here |
| issuer_nav | 3 | ProShares issuer net asset value for UVXY and SVXY, taken from the issuer's own published record |
| rates | 1 | DTB3 from the Federal Reserve H.15 release, which is United States government work and carries no redistribution restriction |

## Phase B, the environment

Python 3.13.13, 30 packages installed, 6 pinned as direct dependencies and 24 imported by nothing in this codebase.

| package | version |
|---|---|
| numpy | 2.5.2 |
| pandas | 3.0.5 |
| pytest | 9.1.1 |
| requests | 2.34.2 |
| yfinance | 1.6.0 |
| pyarrow | 25.0.1 |

**the current environment rather than an authoritative record.** no authoritative requirements file exists. requirements-session-00a.txt is a session 00a artifact and predates the session 18s rebuild.

`pyarrow` is pinned although nothing imports it by name, being the engine `pandas.read_parquet` resolves to. **matplotlib is deliberately absent**, per the plotting decision at 9.53.

| import resolving to no distribution | why |
|---|---|
| AlgorithmImports | the QuantConnect runtime namespace, imported only by docs/source-quantconnect.py, which is the source strategy carried as a reference document and is never executed here |
| s00c_indicators | a local session 00c module imported by path rather than as a package, so it resolves at run time and is not a third-party dependency |
| s00c_rsi | a local session 00c module imported by path rather than as a package, so it resolves at run time and is not a third-party dependency |

## Phase C, the reader-facing documents

**`README.md` written.** 70 lines. 21 figures were read from their emitted CSVs and checked against the written file, with 0 not found.

**`docs/REPRODUCE.md` written.** 53 lines.

**The licence decision is OPEN and no licence file is written.**

| option | what it permits |
|---|---|
| MIT | permits use, copying, modification and redistribution including commercially, requiring only that the notice travels with the code. It says nothing about data |
| Apache-2.0 | as MIT plus an express patent grant and a requirement to state changes. It says nothing about data |
| BSD-3-Clause | as MIT plus a clause forbidding use of the author's name to endorse derived work |
| CC-BY-4.0 | written for content rather than code, permitting redistribution with attribution. It is the usual choice for the document and data halves and an unusual one for code |
| none | no licence means no permission is granted. Readers may look at a public repository and may not reuse it |

| file class | coverage | note |
|---|---|---|
| code | src/, scripts/, tests/, being 218 tracked files | the author's own work, so a licence choice is unconstrained |
| documents | docs/ and every REPORT.md under outputs/ | the author's own work, so a licence choice is unconstrained |
| session outputs | the emitted CSVs under outputs/ | derived from the frozen inputs, so their redistributability follows the inputs' rather than the author's choice |
| frozen inputs | data/raw/ and data/interim/ | third-party price and settlement series. Whether they may be redistributed is NOT established inside this project, and a licence the author grants cannot convey rights the author does not hold |

the register records no licence decision and the vendor question at phase A is unresolved, so the choice is not unambiguous from what the register already records. NO LICENCE FILE IS WRITTEN and the decision is reported as open. Nothing is recommended.

## Phase D, the clean-clone reproduction

The contention check passed at a one-minute load of 3.59 against a threshold of 16, and the wall limit of 2400.0 seconds was stated before launching.

| pass | outcome |
|---|---|
| 1 | two defects, being `requirements.txt` and `scripts/reproduce.py` absent from committed history |
| 2 | one defect, being `data/interim/synthetics/SYN_TQQQ.parquet` absent from a clean clone |
| 3 | **REPRODUCED** |

**The defect that mattered.** The synthetic reconstructions are gitignored as rebuildable and their rebuild reads a network series at run time, so the reproduction as first written was not offline-reproducible from a clean clone. `scripts/reproduce.py` now builds the realized arm alone rather than calling `build_env`, which builds both. The designated cell is the realized arm and needs neither the synthetic panel nor the network.

| quantity | observed | target | deviation |
|---|---|---|---|
| ann_return | 0.5218447451814521 | 0.521845 | 2.5481854792896996e-07 |
| sharpe_lo | 1.3817013060244996 | 1.381701 | 3.0602449951899757e-07 |
| n_sessions | 2472 | 2472 | 0 |

The clone is 514784 KiB of which 208784 KiB is the git directory, and the whole sequence takes 37.6 seconds.

**Both repaired vacuous checks exit zero against the fresh clone.** Neither had been exercised against an empty state before, which is what their cardinality floors were written for.

| check | exit |
|---|---|
| `scripts/s195_verify_inputs.py` | 0 |
| `scripts/verify_prediction_precedes_read.py` | 0 |

**One limitation is stated rather than hidden.** requirements.txt; scripts/reproduce.py; docs/REPRODUCE.md; README.md. A clone reads committed objects and this session's commit has not happened yet, so these files are absent from history. They are copied in for this pass and the limitation is stated rather than hidden.

## Phase E, the history sweep

20 commits. 1090 files were ever committed and 1088 are in the current tree, so 4 were committed and later deleted.

| deleted file | removing commit |
|---|---|
| `docs/DECISIONS-OPEN-v2.md` | 3f6c232 2026-08-18 Session 12.5: reissue register as v3, add STATE.md handoff, archive stale v2 |
| `outputs/session-18/pbo.csv` | 40ff46b 2026-08-19 Session 18s: relocation off iCloud registered, environment rebuilt, object store packed |
| `src/__pycache__/config.cpython-313.pyc` | a90f352 2026-08-19 Session 16: pre-grid closures; grid blocked on unenumerated axes (D24) |
| `src/__pycache__/sleeves.cpython-313.pyc` | a90f352 2026-08-19 Session 16: pre-grid closures; grid blocked on unenumerated axes (D24) |

| identifier | commit-and-path pairs | distinct paths | commits |
|---|---|---|---|
| absolute_home_path_in_file_contents | 1028 | 118 | 20 |
| email_address_in_file_contents | 20 | 1 | 20 |

**No commit message names anything that should not be public.** 0 matched, and every commit message scanned for credential words, an absolute home path and an email address.

The largest blob ever committed is 30516699 bytes and 0 blobs have ever exceeded 100 megabytes.

**History is not rewritten.** git filter-repo or an equivalent across every commit, which changes every commit SHA including 35466c2131f24e35a5ce7fed13c4ed8c821ca45b, the commit that establishes the holdout prediction predates the read. That SHA is cited in docs/DECISIONS-v3.md at 9.64 and 9.66, in outputs/session-27/gates.csv and in docs/REPRODUCE.md, and it is load-bearing evidence rather than a convenience. The trade is recorded and not taken.

## Phase F, the publication instruction

| gate | outcome |
|---|---|
| A, credentials and keys | **PROCEED** |
| D, the clean-clone reproduction | **PASS** |
| all gates cleared | 1 |

**The steps, reported rather than executed.**

1. **Decide the licence.** The decision is recorded as OPEN at phase C. A public repository with no licence grants no reuse rights, which may be the intent. The vendor question on the frozen inputs is also open and a licence the author grants cannot convey rights the author does not hold
2. **Decide whether the personal identifiers stay.** 1028 commit-and-path pairs carry an absolute home path and 20 carry an email address, both across committed history. Removing either requires a full history rewrite that changes every commit SHA including the one establishing the prediction predates the read
3. **Decide whether CLAUDE.md stays.** It is tracked at the repository root and describes the working discipline the sessions ran under. It goes public with everything else unless it is removed first
4. **Change the visibility.** gh repo edit boomer25tiger/tactical-allocation --visibility public --accept-visibility-change-consequences
5. **Or through the web interface.** github.com/boomer25tiger/tactical-allocation, Settings, then General, then Danger Zone, then Change repository visibility
6. **Verify afterwards.** clone the public URL into a scratch directory and run the sequence in docs/REPRODUCE.md, which is the same sequence phase D verified

**the repository stays private. Nothing in this session changes visibility.**

### What a first-time visitor sees

The README title reads *Tactical allocation, a pre-registered negative-result study* and opens with the paragraph carrying the primary-window and holdout ranks and the falsification result.

The root listing is CLAUDE.md, README.md, data, docs, outputs, requirements-session-00a.txt, requirements.txt, scripts, src, tests.

**Python** is the only language GitHub will detect. GitHub's linguist counts source files and excludes data and documentation by default, and the only source language present is Python. By bytes on disk the largest extensions are .f64 at 163.0 MB, .csv at 51.8 MB, .parquet at 33.1 MB, .pkl at 28.4 MB, .npy at 18.9 MB, .py at 2.1 MB.

### The resume-facing summary

One line.

> Pre-registered study of a four-sleeve tactical allocation strategy against eleven leverage-matched benchmarks, with a five-year holdout sealed at 2021-08-01, a prediction committed to git before the read, and all five prediction components falsified when it was opened once.

Three lines.

> A four-sleeve daily tactical allocation strategy was reconstructed with every parameter registered and tested against eleven leverage-matched benchmarks, placing sixth of twelve on both Sharpe conventions over the primary window.

> A five-year holdout was sealed at 2021-08-01 and a falsifiable prediction of what it would show was committed to git before it was opened, with a verification hook that checks that precedence against git rather than against recollection.

> The holdout was read once. The strategy placed 2 of twelve on the naive Sharpe at 1.637799226672021, all five prediction components were falsified, and the result is capacity-bounded, the same figure falling to 0.9817333726959366 at a starting NAV of 1028029775.2491124.

Neither form calls any figure good or bad and neither describes the strategy as one anybody should trade.

## Two corrections this session made

**Register 9.88 carried fifteen superseded bootstrap figures and `docs/STATE.md` carried three.** Session 30's phase F was run, the prose was written from it, and the phase was then re-run to strip a numpy repr wrapper, which shifted the percentiles in their seventh significant figure. The report was regenerated from the new CSV and the register entry and the state document were not. All eighteen are corrected in place against their emitted CSVs at 9.97.

**The checker that should have caught them could not.** The prose-against-CSV checkers at sessions 28 through 30 added `docs/DECISIONS-v3.md` to the corpus a figure is validated against, while also checking the register's own tail as a document. A figure written into the register therefore validated against the register, which is a self-validating loop. `scripts/s31_check.py` treats the register as a checked document and removes it from the corpus, and on its first run it found the three figures in `docs/STATE.md` the old checker had passed over.

## What each finding is

| finding | what acting on it would be |
|---|---|
| no credential or key anywhere | documentation |
| the absolute home path and the email address | a correctness repair in the working tree and a history rewrite in history, the second recorded as not taken |
| `CLAUDE.md` going public | a register decision, open |
| the vendor question on the frozen inputs | a register decision, open |
| `requirements.txt` generated rather than authoritative | documentation |
| the reproduction needing the synthetic arm | a correctness repair, applied |
| the two files absent from history at pass 1 | a correctness repair, applied by this session's commit |
| the licence | a register decision, open |
| register 9.88 and `docs/STATE.md` carrying superseded figures | a correctness repair, applied at 9.97 |
| the self-validating checker | a correctness repair, applied in `scripts/s31_check.py` |

**No recommendation is made on any of them.**

## Is the repository ready to publish

**Yes on both gates, and three decisions remain that are the author's rather than the session's.**

1. The licence, open at 9.96.
2. Whether the absolute home path and the email address stay, given that removing either changes the prediction commit SHA.
3. Whether `CLAUDE.md` stays.

The corporate action disposition at 9.85 also remains open. It bears on the study rather than on publication and it is not decided here.

## Repository size and free space

**No committed file exceeds 100 megabytes.** The largest is 29.10 MB, being `outputs/session-18/spec-index-augmented.csv`, and the count above the limit is 0.

| reading | before the commit | expected delta |
|---|---|---|
| working tree, KiB | 833608 | +0 |
| git directory, KiB | 209024 | +168 or less |
| free space, GiB | 18.07 | 0.00 to -0.01 |

The commit touches 27 files totalling 398778 bytes on disk, of which 25 files and 172283 bytes are new. **Nothing is read after the commit**, under 9.62.

## Register

9.92 the publication audit. 9.93 the environment pinned. 9.94 the clean-clone reproduction. 9.95 the history sweep. 9.96 the licence, open. 9.97 the correction to 9.88 and the self-validating checker.

## Artifacts

- `outputs/session-31/publication-audit.csv`
- `outputs/session-31/environment.csv`
- `outputs/session-31/documents.csv`
- `outputs/session-31/clean-clone.csv`
- `outputs/session-31/history-sweep.csv`
- `outputs/session-31/publication.csv`
- `outputs/session-31/size.csv`
- `README.md`, `requirements.txt`, `docs/REPRODUCE.md`, `scripts/reproduce.py`

**No figure is drawn, since the cap at 9.60 is reached.**

