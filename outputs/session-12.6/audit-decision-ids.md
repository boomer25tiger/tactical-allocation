# Session 12.6, step 1 — decision-ID audit

Method. Contextual regex extraction ("decision X.Y", "per X.Y", "under
X.Y", "(X.Y)", bold headers, config comment style) over outputs/, src/,
and docs/, compared against every ID present in docs/DECISIONS-v3.md.
Positive controls passed before any negative finding: 2.10 and 6.1 found
by the tree search; 6.10 found in src/ by the src-only search. Numeric
false positives (e.g. "1.28%", "2.429e-16", "6.24 on 2000-11-06", "1.5x",
percentages in parentheses) were individually inspected in context and
removed. Raw pass and contexts reproduced by
scratchpad/audit_ids.py (session-local; method recorded here).

## List 1 — IDs referenced in the tree, absent from DECISIONS-v3.md

The v3 register was reconstructed from session reports, so IDs whose
disposition happened only in conversation or under the v2 namespace are
absent. Two groups.

**Group 1a — referenced by session reports under outputs/ (not only by
superseded docs):**

| ID | Where referenced | What it was |
|---|---|---|
| 1.12 | outputs/session-00c/REPORT.md | Distribution coverage; closed by measurement (worst ticker 4.05 bp/yr) |
| 2.18 | outputs/session-00a/REPORT.md, source-notes.md | VX early-liquidity inspection; addressed by 00A |
| 2.20 | outputs/session-00c/REPORT.md, smh-continuity.md | SMH stitch continuity; closed by measurement |
| 6.7 | outputs/session-00c, session-00e REPORT.md | S3 vote threshold; 00E leave-one-out informed it |
| 6.16 | outputs/session-00d/REPORT.md | S2 trend filter series ("TQQQ as supplied") |
| 6.20 | outputs/session-00c/REPORT.md | RSI(inverse) vs 100−RSI(underlying); closed by measurement |

**Group 1b — referenced only by docs/HANDOFF.md (2026-08-17, pre-00D,
v2-era namespace) and/or the v2 archive:**

0.1, 0.2, 0.3, 1.7, 1.10, 1.13, 2.4, 2.16, 2.17, 2.21, 2.23,
3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.10, 4.5, 4.8, 4.9,
5.8, 6.15, 6.21, 7.1, 7.2–7.9 (grid-range block), 7.11,
8.3, 8.4, 8.5, 8.6, 8.7, 8.14, 9.1, 9.2, 9.3, 9.4, 9.7, 9.9.

Of these, the ones with standing relevance to the next sessions:

- **4.5 commission plan** (IBKR Fixed 0.005/share, 1.00 minimum, 1% cap)
  appears in no register entry and no config constant, yet the session 13
  prompt executes it. Register gap with immediate effect.
- **4.6 in the v2 namespace was starting NAV**; v3's 4.6 is the sizing
  size-dependence. Starting NAV has no register entry and no config
  constant anywhere.
- 8.3–8.7, 8.14 (alpha model, timing regressions, PSR/DSR, metric order)
  and 9.1–9.7 (nulls, families, freeze governance) are evaluation-stage
  decisions not yet re-registered in v3.

Step 2 of this session adds only the six closures the prompt names; the
rest of List 1 is reported, not amended.

## List 2 — register IDs never referenced elsewhere in the tree

None. Every ID in DECISIONS-v3.md is referenced by at least one file in
outputs/, src/, or docs/ beyond the register itself.

## Config-versus-register check

Every constant in src/config.py carries a decision ID comment; every such
ID is present in DECISIONS-v3.md (2.5a, 6.11, 6.12 appear as inline or
indented headers rather than list-entry headers, which a naive header
scan misses). Every value agrees with the register: warm-up 210 (2.11),
RSI 14/14/14 (6.1), tiers 70/80/30 (6.2–6.4), SMA 200/20 (6.5/6.6), crash
−15 on 60 sessions of QQQ (6.10), budgets 0.25×4 (5.4), gross cap 1.00
(5.3), whole-percent label (5.1), DTB3 at /360 calendar (8.1, 5.5a),
financing 75/70 (2.14), slippage grid (0,5,10,20,35,50) uniform (4.4,
4.3), SMH accrual 1.5 with (0,1,2) arm (3.12), grids and the 7.10 pin.
**No value disagreement found.**

Two stale-comment defects, reported not repaired (out of this session's
amendment scope, which covers the register only):

1. **src/sleeves.py module docstring, substitution note 2** says "the
   canonical level is -10 percent" for the crash threshold. Stale: 6.10
   was re-closed at −15 in session 09, and config.CRASH_THRESHOLD_PCT is
   −15.0. The code reads config, so behaviour is correct; the comment is
   wrong.
2. **src/config.py header note** cites docs/DECISIONS-OPEN-v2.md, a path
   renamed to docs/ARCHIVE-DECISIONS-OPEN-v2-STALE.md by session 12.5.

## Working-tree premise discrepancy

The session prompt states the repository is "committed at ad6be24 with
five documentation files uncommitted." The tree is at 3f6c232 (session
12.5's commit), which already committed DECISIONS-v3.md, STATE.md, the v2
archive rename, and outputs/session-12.5/REPORT.md; the working tree was
clean at session start. Reported per the standing rule; the step 4 commit
covers this session's amendments and the prompt archive.
