- **9.92 the publication audit (session 31, 2026-08-23).** 1088 tracked files, of which
  527 are session outputs, 316 are frozen inputs, 218 are code, 13 are documents, 12 are
  derived artifacts and 2 are neither. 919 tracked text files were swept in full rather
  than sampled.

  **GATE A CLEARS. No credential or key pattern matched anywhere.** The sweep covered
  AWS access keys, private key blocks, GitHub and Slack token forms, bearer headers and
  any assignment of a password, secret, api key, access token, auth token or client
  secret to a literal.

  **Two personal identifiers are present and are not repaired here.** An absolute home
  path appears 95 times across 94 tracked files, and one email address appears once, at
  scripts/s09_financing.py:25 inside the User-Agent header the SEC EDGAR fetch sends.
  Both are recorded at 9.95 with what removal would require.

  **13 tracked files exceed 10 megabytes**, the largest being
  outputs/session-18/spec-index-augmented.csv at 30516699 bytes. **None approaches the
  100 megabyte limit.**

  **CLAUDE.md is tracked at the repository root** and describes the working discipline
  the sessions ran under. It goes public with everything else unless it is removed
  first, which is a disclosure decision rather than a defect.

  **The vendor question is OPEN.** The frozen inputs carry price and total-return
  history taken through yfinance from Yahoo Finance, Cboe VX futures settlements, issuer
  net asset value from ProShares and DTB3 from the Federal Reserve H.15 release. The
  last carries no restriction, being United States government work. No vendor licence
  has been read against these artifacts inside this project, so whether every tracked
  series may be redistributed is **not established**, and the question is reported
  rather than answered.

- **9.93 the environment pinned (session 31, 2026-08-23).** requirements.txt is written
  at the repository root, pinning 6 direct dependencies at their installed versions
  under Python 3.13.13. **It is GENERATED FROM THE CURRENT ENVIRONMENT rather than from
  an authoritative record**, since none exists. Session 18s rebuilt the environment from
  a pre-removal freeze and 10.1 records that the zero version divergence it reported is
  partly a construction of that method.

  30 packages are installed and 24 of them are imported by nothing in this codebase,
  being transitive dependencies or unused. **pyarrow is pinned although nothing imports
  it by name**, since it is the engine pandas.read_parquet resolves to and every frozen
  input load needs it. Three imports resolve to no distribution, being AlgorithmImports
  which only docs/source-quantconnect.py reads and which is never executed, and two
  local session 00c modules imported by path.

  **matplotlib is deliberately absent**, per the plotting decision at 9.53.

- **9.94 the clean-clone reproduction, GATE D CLEARS at the third pass (session 31,
  2026-08-23).** The clone goes to a scratch path outside the working directory and the
  sequence runs from docs/REPRODUCE.md exactly as written.

  **Pass 1 found two defects, both the same cause.** requirements.txt and
  scripts/reproduce.py exist only in the working tree, so a clone of committed history
  lacks them and both the environment build and the reproduction failed.

  **Pass 2 found the defect that mattered.** With the four pending files copied in, the
  environment built and the input verifier passed, and the reproduction failed on a
  missing data/interim/synthetics/SYN_TQQQ.parquet. The synthetic reconstructions are
  gitignored as rebuildable and their rebuild reads a network series at run time, so
  **the reproduction as first written was not offline-reproducible from a clean clone.**

  **The repair.** scripts/reproduce.py now builds the REALIZED arm alone rather than
  calling scripts/s14_common.py build_env, which builds both arms. The designated cell
  is the realized arm and needs neither the synthetic panel nor the network. The
  calendar is taken from the realized SPY frame, which is the same frozen frame the
  synthetic panel carries for an unlevered ticker, and the repaired path reproduces the
  canonical exactly in the working copy before any clone was retried.

  **Pass 3 reproduces from a clean clone.** Annualised return 0.5218447451814521 against
  a target of 0.521845 at a deviation of 2.5481854792896996e-07, Lo-corrected Sharpe
  1.3817013060244996 against 1.381701 at 3.0602449951899757e-07, and 2472 sessions
  exactly. The tolerance is 5e-07 on each figure and bit-identical output is not
  asserted, since float reduction order varies with thread count and BLAS version. The
  clone is 514784 KiB and the whole sequence takes 37.6 seconds.

  **Both repaired vacuous checks exit zero against the fresh clone.**
  scripts/s195_verify_inputs.py, whose cardinality floor was added at 9.22 after it
  reported PASS on zero matched files, and scripts/verify_prediction_precedes_read.py,
  which must exit zero on a fresh clone since the prediction is in committed history.
  Neither had been exercised against an empty state before.

  **One limitation is stated rather than hidden.** Passes 2 and 3 copy in the four files
  this session's commit adds, since a clone reads committed objects and the commit had
  not happened. A clone of the pushed commit carries them and any later session can
  re-run scripts/s31_phaseD.py against it.

- **9.95 the history sweep, NOTHING REWRITTEN (session 31, 2026-08-23).** 20 commits,
  1090 files ever committed and 1088 in the current tree, so **4 files were committed and
  later deleted**, being docs/DECISIONS-OPEN-v2.md, outputs/session-18/pbo.csv and two
  compiled Python caches under src/__pycache__/. Each remains reachable in history.

  **The largest blob ever committed is 30516699 bytes and no blob has ever exceeded 100
  megabytes**, so no push has carried an object above the limit. The git directory is
  208808 KiB.

  **No commit message names anything that should not be public.** Every message was
  scanned for credential words, an absolute home path and an email address, and none
  matched.

  **An absolute home path appears in 1028 commit-and-path pairs across 118 distinct
  paths and all 20 commits. An email address appears in 20 pairs across 1 path and all
  20 commits.**

  **Removing either requires a full history rewrite, and history is NOT rewritten.** A
  rewrite changes every commit SHA including
  35466c2131f24e35a5ce7fed13c4ed8c821ca45b, which is what establishes that the holdout
  prediction predates the read. That SHA is cited at 9.64 and 9.66, in
  outputs/session-27/gates.csv and in docs/REPRODUCE.md, and it is load-bearing evidence
  rather than a convenience. **The trade is recorded and not taken.**

- **9.96 the licence, OPEN (session 31, 2026-08-23).** MIT, Apache-2.0, BSD-3-Clause and
  CC-BY-4.0 are recorded with what each permits, together with a fourth option of no
  licence, under which readers may look at a public repository and may not reuse it.

  **The coverage differs by file class.** The code and the documents are the author's
  own work and a choice over them is unconstrained. The session outputs are derived from
  the frozen inputs, so their redistributability follows the inputs rather than the
  author's choice. **A licence the author grants cannot convey rights the author does
  not hold**, and the vendor question at 9.92 is unresolved.

  **NO LICENCE FILE IS WRITTEN and nothing is recommended**, since the choice is not
  unambiguous from what the register already records.

- **9.97 register 9.88 carried fifteen superseded figures, and the check that should
  have caught it could not (session 31, 2026-08-23), correcting 9.88.**

  **What happened.** Session 30's phase F was run, 9.88 was written from that run, and
  phase F was then re-run to strip a numpy repr wrapper. The re-run shifted the
  bootstrap percentiles in their seventh significant figure and the report was
  regenerated from the new CSV, while the register entry was not. 9.88's bootstrap
  interval table therefore disagreed with
  outputs/session-30/bootstrap-intervals.csv, which is authoritative. **The fifteen
  figures are corrected in place against the CSV.**

  **Why the check passed.** The prose-against-CSV checkers at sessions 28 through 30
  added docs/DECISIONS-v3.md to the corpus a figure is validated against, while also
  checking the register's own tail as a document. **A figure written into the register
  therefore validated against the register**, which is a self-validating loop and
  detects nothing. scripts/s31_check.py treats the register as a checked DOCUMENT and
  removes it from the corpus. This is the fourth instance of the class 9.47 records, of
  a procedure reporting a pass it did not earn.
