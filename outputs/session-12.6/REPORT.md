# Session 12.6 — register completion and prompt archival

Run 2026-08-18. No backtest, no return, no performance statistic computed.
Positive controls passed before every negative finding (detailed in
audit-decision-ids.md).

## Premise discrepancy, reported first

The prompt states the repository is "committed at ad6be24 with five
documentation files uncommitted." The tree was at 3f6c232 (session 12.5's
commit) with a clean working tree; that commit already carried
DECISIONS-v3.md, STATE.md, the v2 archive rename, and
outputs/session-12.5/REPORT.md. Reported per the standing rule, not
adjusted. This session's commit therefore covers the register amendments
and the prompt archive only.

## Step 1 — audit results

Full detail with method and positive controls: audit-decision-ids.md.

**IDs referenced in the tree, absent from DECISIONS-v3.md.** Six are
referenced by session reports under outputs/: 1.12, 2.18, 2.20, 6.7,
6.16, 6.20 (all dispositioned by sessions 00A–00E; the v3 reconstruction
from later reports dropped them). Roughly forty more appear only in
docs/HANDOFF.md (the 2026-08-17 pre-00D handoff, v2-era namespace) and
the v2 archive: 0.1–0.3, 1.7, 1.10, 1.13, 2.4, 2.16, 2.17, 2.21, 2.23,
3.1–3.8, 3.10, 4.5, 4.8, 4.9, 5.8, 6.15, 6.21, 7.1, 7.2–7.9, 7.11,
8.3–8.7, 8.14, 9.1–9.4, 9.7, 9.9. Of these, two have immediate standing
relevance and no register entry or config constant: **4.5, the commission
plan** (IBKR Fixed 0.005/share, 1.00 minimum, 1 percent cap — the session
13 prompt executes it), and **starting NAV** (v2's 4.6; v3's 4.6 is the
sizing size-dependence). Only the six closures the prompt names were
added; the rest are reported here.

**Register IDs never referenced elsewhere in the tree.** None.

**Config versus register.** Every constant in src/config.py carries an ID
present in the register and every value agrees. No defect. Two stale
comments reported, not repaired (outside this session's amendment scope):
src/sleeves.py's module docstring still says the canonical crash level is
−10 percent (6.10 re-closed at −15; the code reads config and is
correct), and src/config.py's header cites the pre-rename path
docs/DECISIONS-OPEN-v2.md.

## Step 2 — decisions added to DECISIONS-v3.md

1. **2.7 closed as report-without-threshold.** No pass-fail band; report
   correlation, annualised TD, and max rolling divergence per fund with
   target and window stated. Both external anchors absent (no issuer TE
   against the levered daily objective; prospectuses qualitative only).
   Session 12's proposed two-tier band rejected: its thresholds fall in
   the empty gap between the eleven passing funds (0.993–0.999 corr) and
   the three exceptions (6.2–8.9%/yr TD), so any value in the gap
   produces the same partition. Flagged [A]. Entry header updated;
   removed from the open-items list.
2. **2.12a SOXS sourcing closed: keep the synthetic.** The 6.21%/yr TD /
   1394% max rolling divergence exception stands and travels with every
   dependent result; listed SOXS from 2010-03 rejected because it removes
   T11's bull-branch inverse basket across 2008.
3. **2.12b SVXY 2018-02-06 excluded from validation.** Stated exclusion:
   the fund's NAV rebounded +187% against an index-implied +26% during
   the termination-scale event — a portfolio departure from the index,
   not a construction failure. Every other pre-2018 session matches to
   decimals.
4. **8.8 full specification recorded.** Benchmarks: buy-and-hold QQQ,
   buy-and-hold TQQQ, vol-targeted QQQ at matched exposure, one
   fast-rebalancing naive rival at comparable trading frequency, each
   sleeve standalone at full budget. Nulls: block-bootstrap timing
   shuffle preserving state distribution and holding-period structure
   (8.9), and a turnover-matched switching null at the measured
   transition rate. Canonical parameters per 9.8, 1,000 draws, identical
   cost model on every line; ensemble-vs-best-sleeve post-hoc into 8.10's
   Romano-Wolf family; pairwise correlation of the four standalone tracks
   reported. Rationale: buy-and-hold confounds the signal with a
   105-transitions/yr trading frequency.
5. **4.4 range retained at 0–50 bp.** Session 05's COVID stress-window
   estimates (SOXS 401 bp, SOXL 288 bp) not used to extend the range —
   Corwin-Schultz variance scaling is violated on daily-reset funds, so
   those figures substantially read volatility as spread. Limitation
   recorded: the cost model proxies auction cost with a continuous-market
   spread estimator and does not cover crisis conditions.
6. **4.6 restated as reopened and unresolvable before a result.** The
   sweep measures starting NAV; the account compounds, so liquidity and
   impact apply to terminal size. Blocked until a first backtest exists.

Register header updated to "as of session 12.6" with the amendment list.

## Step 3 — prompt archive

Created docs/prompts/ with three files:

- **session-12.6.md** — this session's prompt, verbatim.
- **session-13.md** — the canonical-backtest prompt, supplied by the user
  in this conversation, archived ahead of its run.
- **README.md** — records that no verbatim prompt for sessions 00A
  through 12.5 exists anywhere in the working tree (reports quote
  fragments and paraphrase steps; a paraphrase is not the prompt, so none
  was fabricated). All eighteen earlier sessions listed as absent. The
  00D report notes the Claude session transcripts under ~/.claude/
  contain prompt texts; they are outside the repository and were not
  read.

## Step 4 — commit

**502ca42**, 4 files changed (285 insertions, 19 deletions):
docs/DECISIONS-v3.md, docs/prompts/README.md,
docs/prompts/session-12.6.md, docs/prompts/session-13.md. The five
documentation files the prompt expected to include were already committed
at 3f6c232, as reported above. This report and audit-decision-ids.md
under outputs/session-12.6/ are left uncommitted.

## Items surfaced for the user, no action taken

- The 4.5 commission plan and starting NAV have no register entry and no
  config constant, and session 13 needs both (its prompt states the
  commission terms inline; starting NAV appears nowhere — source's
  set_cash(10_000) is the only value on record).
- docs/STATE.md's "immediate next step" paragraph still lists "the 2.7
  band confirmation" among post-backtest steps; 2.7 is now closed.
- The two stale src comments from step 1.

Halted at the stop condition.
