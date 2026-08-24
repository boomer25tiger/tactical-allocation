"""Session 31 phase G. Write outputs/session-31/REPORT.md from the emitted CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

R = Path("/Users/GualyCr/Downloads/tactical-allocation")
O = R / "outputs" / "session-31"


def rd(p):
    return list(csv.DictReader(open(O / p)))


AU, EN, DC = rd("publication-audit.csv"), rd("environment.csv"), rd("documents.csv")
CC, HS, PB, SZ = (rd("clean-clone.csv"), rd("history-sweep.csv"),
                  rd("publication.csv"), rd("size.csv"))


def g(rows, t, i, f="value"):
    for r in rows:
        if r.get("table") == t and r.get("item") == i:
            return r.get(f)
    return None


def last(rows, t, i, f="value"):
    v = None
    for r in rows:
        if r.get("table") == t and r.get("item") == i:
            v = r.get(f)
    return v


L = []; a = L.append
a("# Session 31, publication readiness")
a("")
a("2026-08-23. Seven phases. One commit, at phase G. **The repository stays private and "
  "nothing in this session changed visibility.** No measurement ran, no frozen input "
  "was repaired, no commit history was rewritten.")
a("")
a("## Opening")
a("")
a(f"**Gate A clears.** {g(AU,'gate_A','credentials_or_keys_found')} credential or key "
  f"patterns matched across {g(AU,'sweep','text_files_swept')} tracked text files, swept "
  f"in full rather than sampled.")
a("")
a(f"**Gate D clears at the third pass.** The canonical reproduces from a clean clone at "
  f"{last(CC,'reproduction','ann_return')} annualised and "
  f"{last(CC,'reproduction','sharpe_lo')} Lo-corrected over "
  f"{last(CC,'reproduction','n_sessions')} sessions, inside the stated tolerance, in "
  f"{last(CC,'reproduction','wall_clock_seconds')} seconds from a "
  f"{last(CC,'clone','total_kib')} KiB clone.")
a("")
a(f"**Both gates cleared**, so the publication instruction at phase F stands as written.")
a("")
a("## Phase A, the audit")
a("")
a(f"{g(AU,'scope','tracked_files')} tracked files.")
a("")
a("| class | files |")
a("|---|---|")
for r in AU:
    if r["table"] == "classification" and r["item"] != "note":
        a(f"| {r['item']} | {r['value']} |")
a("")
a("| directory | bytes | files | tracked |")
a("|---|---|---|---|")
for r in AU:
    if r["table"] == "top_level_directory":
        a(f"| `{r['item']}` | {r['value']} | {r['n_files']} | {r['tracked']} |")
a("")
a("**Four reader-facing documents were checked and three were absent.**")
a("")
a("| document | state before this session |")
a("|---|---|")
for r in AU:
    if r["table"] == "reader_document":
        a(f"| {r['item']} | {'present' if r['value'] != 'ABSENT' else 'ABSENT'} |")
a("")
a(f"{g(AU,'size','tracked_files_above_10mb')} tracked files exceed 10 megabytes, the "
  f"largest being `outputs/session-18/spec-index-augmented.csv` at "
  f"{[r['value'] for r in AU if r['table']=='large_tracked_file'][0]} bytes. None "
  f"approaches the 100 megabyte limit.")
a("")
a("### What should not be public")
a("")
a("| kind | hits | files |")
a("|---|---|---|")
for r in AU:
    if r["table"] == "identifier_summary":
        a(f"| {r['item']} | {r['value']} | {r['n_files']} |")
a("")
a(f"The email address is `{g(AU,'email_hit','')}`" if g(AU, "email_hit", "") else
  "The single email hit is in `scripts/s09_financing.py`, inside the User-Agent header "
  "the SEC EDGAR fetch sends, which is a legitimate use of a personal address and is "
  "still a personal address.")
a("")
a("**`CLAUDE.md` is tracked at the repository root** and describes the working "
  "discipline the sessions ran under. It goes public with everything else unless it is "
  "removed first, which is a disclosure decision rather than a defect.")
a("")
a("### The vendor question")
a("")
a(f"{g(AU,'vendor','verdict','note')}.")
a("")
a("| source | artifacts | terms as far as this project establishes them |")
a("|---|---|---|")
for i in ("etf_and_index_series", "cboe_vx_settles", "issuer_nav", "rates"):
    a(f"| {i} | {g(AU,'vendor',i)} | {g(AU,'vendor',i,'note')} |")
a("")
a("## Phase B, the environment")
a("")
a(f"{g(EN,'environment','python')}, {g(EN,'environment','installed_packages')} packages "
  f"installed, {g(EN,'counts','direct_dependencies')} pinned as direct dependencies and "
  f"{g(EN,'counts','installed_but_not_imported')} imported by nothing in this codebase.")
a("")
a("| package | version |")
a("|---|---|")
for r in EN:
    if r["table"] in ("direct_dependency", "runtime_requirement"):
        a(f"| {r['item']} | {r['value']} |")
a("")
a(f"**{g(EN,'requirements','generated_from')}.** "
  f"{g(EN,'requirements','generated_from','note')}.")
a("")
a("`pyarrow` is pinned although nothing imports it by name, being the engine "
  "`pandas.read_parquet` resolves to. **matplotlib is deliberately absent**, per the "
  "plotting decision at 9.53.")
a("")
a("| import resolving to no distribution | why |")
a("|---|---|")
for r in EN:
    if r["table"] == "missing_dependency":
        a(f"| {r['item']} | {r['note']} |")
a("")
a("## Phase C, the reader-facing documents")
a("")
a(f"**`README.md` written.** {g(DC,'readme','written','note')}. "
  f"{g(DC,'readme_check','figures_checked')} figures were read from their emitted CSVs "
  f"and checked against the written file, with "
  f"{g(DC,'readme_check','figures_not_found_in_the_readme')} not found.")
a("")
a(f"**`docs/REPRODUCE.md` written.** {g(DC,'reproduce_guide','written','note')}.")
a("")
a("**The licence decision is OPEN and no licence file is written.**")
a("")
a("| option | what it permits |")
a("|---|---|")
for r in DC:
    if r["table"] == "licence_option":
        a(f"| {r['item']} | {r['value']} |")
a("")
a("| file class | coverage | note |")
a("|---|---|---|")
for r in DC:
    if r["table"] == "licence_coverage":
        a(f"| {r['item']} | {r['value']} | {r['note']} |")
a("")
a(f"{g(DC,'licence_decision','verdict','note')}.")
a("")
a("## Phase D, the clean-clone reproduction")
a("")
a(f"The contention check passed at a one-minute load of "
  f"{g(CC,'machine_at_phase_D','load_1min')} against a threshold of "
  f"{g(CC,'contention_check','threshold')}, and the wall limit of "
  f"{g(CC,'preregistration','wall_limit_seconds')} seconds was stated before launching.")
a("")
a("| pass | outcome |")
a("|---|---|")
a("| 1 | two defects, being `requirements.txt` and `scripts/reproduce.py` absent from "
  "committed history |")
a("| 2 | one defect, being `data/interim/synthetics/SYN_TQQQ.parquet` absent from a "
  "clean clone |")
a("| 3 | **REPRODUCED** |")
a("")
a("**The defect that mattered.** The synthetic reconstructions are gitignored as "
  "rebuildable and their rebuild reads a network series at run time, so the reproduction "
  "as first written was not offline-reproducible from a clean clone. "
  "`scripts/reproduce.py` now builds the realized arm alone rather than calling "
  "`build_env`, which builds both. The designated cell is the realized arm and needs "
  "neither the synthetic panel nor the network.")
a("")
a("| quantity | observed | target | deviation |")
a("|---|---|---|---|")
for i in ("ann_return", "sharpe_lo", "n_sessions"):
    a(f"| {i} | {last(CC,'reproduction',i)} | {last(CC,'reproduction',i,'target')} | "
      f"{last(CC,'reproduction',i,'deviation')} |")
a("")
a(f"The clone is {last(CC,'clone','total_kib')} KiB of which "
  f"{last(CC,'clone','git_directory_kib')} KiB is the git directory, and the whole "
  f"sequence takes {last(CC,'reproduction','wall_clock_seconds')} seconds.")
a("")
a("**Both repaired vacuous checks exit zero against the fresh clone.** Neither had been "
  "exercised against an empty state before, which is what their cardinality floors were "
  "written for.")
a("")
a("| check | exit |")
a("|---|---|")
for r in CC:
    if r["table"] == "vacuous_check" and r["pass_number"] == "3":
        a(f"| `{r['item']}` | {r['value']} |")
a("")
a(f"**One limitation is stated rather than hidden.** "
  f"{last(CC,'pending_files_copied_in','count','note')}.")
a("")
a("## Phase E, the history sweep")
a("")
a(f"{g(HS,'history','commits')} commits. {g(HS,'deleted','files_ever_committed')} files "
  f"were ever committed and {g(HS,'deleted','files_in_the_current_tree')} are in the "
  f"current tree, so {g(HS,'deleted','files_deleted')} were committed and later deleted.")
a("")
a("| deleted file | removing commit |")
a("|---|---|")
for r in HS:
    if r["table"] == "deleted_file":
        a(f"| `{r['item']}` | {r['value']} |")
a("")
a("| identifier | commit-and-path pairs | distinct paths | commits |")
a("|---|---|---|---|")
for r in HS:
    if r["table"] == "history_identifier" and "contents" in r["item"]:
        a(f"| {r['item']} | {r['value']} | {r['n_files']} | {r['n_commits']} |")
a("")
a(f"**No commit message names anything that should not be public.** "
  f"{g(HS,'commit_message_summary','messages_flagged')} matched, and "
  f"{g(HS,'commit_message_summary','messages_flagged','note')}.")
a("")
a(f"The largest blob ever committed is {g(HS,'blob_summary','largest_blob_bytes')} "
  f"bytes and {g(HS,'blob_summary','blobs_over_100mb_at_any_point_in_history')} blobs "
  f"have ever exceeded 100 megabytes.")
a("")
a(f"**History is not rewritten.** "
  f"{g(HS,'history_identifier','absolute_home_path_removal_requires','note')}. The trade "
  f"is recorded and not taken.")
a("")
a("## Phase F, the publication instruction")
a("")
a("| gate | outcome |")
a("|---|---|")
for r in PB:
    if r["table"] == "gate" and r["item"] != "all_gates_cleared":
        a(f"| {r['item']} | **{r['value']}** |")
a(f"| all gates cleared | {g(PB,'gate','all_gates_cleared')} |")
a("")
a("**The steps, reported rather than executed.**")
a("")
for r in PB:
    if r["table"] == "publication_step" and r["item"].isdigit():
        a(f"{r['item']}. **{r['value']}** {r['note']}")
a("")
a(f"**{g(PB,'publication_step','executed_in_this_session','note')}.**")
a("")
a("### What a first-time visitor sees")
a("")
a(f"The README title reads *{g(PB,'first_visit','readme_title')}* and opens with the "
  f"paragraph carrying the primary-window and holdout ranks and the falsification "
  f"result.")
a("")
a(f"The root listing is {g(PB,'first_visit','root_listing')}.")
a("")
a(f"**{g(PB,'first_visit','languages_github_will_detect')}** is the only language "
  f"GitHub will detect. {g(PB,'first_visit','languages_github_will_detect','note')}.")
a("")
a("### The resume-facing summary")
a("")
a("One line.")
a("")
a(f"> {g(PB,'summary_one_line','text')}")
a("")
a("Three lines.")
a("")
for r in PB:
    if r["table"] == "summary_three_line":
        a(f"> {r['value']}")
        a("")
a("Neither form calls any figure good or bad and neither describes the strategy as one "
  "anybody should trade.")
a("")
a("## Two corrections this session made")
a("")
a("**Register 9.88 carried fifteen superseded bootstrap figures and `docs/STATE.md` "
  "carried three.** Session 30's phase F was run, the prose was written from it, and "
  "the phase was then re-run to strip a numpy repr wrapper, which shifted the "
  "percentiles in their seventh significant figure. The report was regenerated from the "
  "new CSV and the register entry and the state document were not. All eighteen are "
  "corrected in place against their emitted CSVs at 9.97.")
a("")
a("**The checker that should have caught them could not.** The prose-against-CSV "
  "checkers at sessions 28 through 30 added `docs/DECISIONS-v3.md` to the corpus a "
  "figure is validated against, while also checking the register's own tail as a "
  "document. A figure written into the register therefore validated against the "
  "register, which is a self-validating loop. `scripts/s31_check.py` treats the register "
  "as a checked document and removes it from the corpus, and on its first run it found "
  "the three figures in `docs/STATE.md` the old checker had passed over.")
a("")
a("## What each finding is")
a("")
a("| finding | what acting on it would be |")
a("|---|---|")
a("| no credential or key anywhere | documentation |")
a("| the absolute home path and the email address | a correctness repair in the working "
  "tree and a history rewrite in history, the second recorded as not taken |")
a("| `CLAUDE.md` going public | a register decision, open |")
a("| the vendor question on the frozen inputs | a register decision, open |")
a("| `requirements.txt` generated rather than authoritative | documentation |")
a("| the reproduction needing the synthetic arm | a correctness repair, applied |")
a("| the two files absent from history at pass 1 | a correctness repair, applied by "
  "this session's commit |")
a("| the licence | a register decision, open |")
a("| register 9.88 and `docs/STATE.md` carrying superseded figures | a correctness "
  "repair, applied at 9.97 |")
a("| the self-validating checker | a correctness repair, applied in "
  "`scripts/s31_check.py` |")
a("")
a("**No recommendation is made on any of them.**")
a("")
a("## Is the repository ready to publish")
a("")
a("**Yes on both gates, and three decisions remain that are the author's rather than "
  "the session's.**")
a("")
a("1. The licence, open at 9.96.")
a("2. Whether the absolute home path and the email address stay, given that removing "
  "either changes the prediction commit SHA.")
a("3. Whether `CLAUDE.md` stays.")
a("")
a("The corporate action disposition at 9.85 also remains open. It bears on the study "
  "rather than on publication and it is not decided here.")
a("")
a("## Repository size and free space")
a("")
a(f"**No committed file exceeds 100 megabytes.** The largest is "
  f"{g(SZ,'size','largest_tracked_file_mb')} MB, being "
  f"`{g(SZ,'size','largest_tracked_file_bytes','note')}`, and the count above the limit "
  f"is {g(SZ,'size','tracked_files_over_100mb')}.")
a("")
a("| reading | before the commit | expected delta |")
a("|---|---|---|")
a(f"| working tree, KiB | {g(SZ,'size','working_tree_kib_before_commit')} | "
  f"{g(SZ,'expected_delta','working_tree_kib')} |")
a(f"| git directory, KiB | {g(SZ,'size','git_directory_kib_before_commit')} | "
  f"{g(SZ,'expected_delta','git_directory_kib')} |")
a(f"| free space, GiB | {g(SZ,'space','free_gib_before_commit')} | "
  f"{g(SZ,'expected_delta','free_space_gib')} |")
a("")
a(f"The commit touches {g(SZ,'commit_contents','files_in_the_commit')} files totalling "
  f"{g(SZ,'commit_contents','bytes_of_those_files')} bytes on disk, of which "
  f"{g(SZ,'commit_contents','files_new_to_the_repository')} files and "
  f"{g(SZ,'commit_contents','bytes_new_to_the_repository')} bytes are new. **Nothing is "
  f"read after the commit**, under 9.62.")
a("")
a("## Register")
a("")
a("9.92 the publication audit. 9.93 the environment pinned. 9.94 the clean-clone "
  "reproduction. 9.95 the history sweep. 9.96 the licence, open. 9.97 the correction to "
  "9.88 and the self-validating checker.")
a("")
a("## Artifacts")
a("")
for x in ("publication-audit.csv", "environment.csv", "documents.csv",
          "clean-clone.csv", "history-sweep.csv", "publication.csv", "size.csv"):
    a(f"- `outputs/session-31/{x}`")
a("- `README.md`, `requirements.txt`, `docs/REPRODUCE.md`, `scripts/reproduce.py`")
a("")
a("**No figure is drawn, since the cap at 9.60 is reached.**")
a("")
(O / "REPORT.md").write_text("\n".join(L) + "\n")
print(f"wrote REPORT.md, {len(L)} lines")
