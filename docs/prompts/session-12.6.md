Session 12.6 — register completion and prompt archival
Scaffold

Repository is tactical-allocation, committed at ad6be24 with five documentation files uncommitted. Read docs/DECISIONS-v3.md and docs/STATE.md first.

Run alone. No timeout binary. Positive controls before negative findings. No backtest, no performance statistic.

Purpose

DECISIONS-v3.md was built from session reports, so decisions closed in conversation without a corresponding session are absent. Add them, and archive the session prompts so the repository is the complete record.

Steps
1. Audit for missing decisions

Enumerate every decision ID referenced anywhere in outputs/, src/, or docs/, and compare against the IDs present in DECISIONS-v3.md. Report any ID appearing in one and not the other.

Then check the register against src/config.py, since config carries decision IDs on every constant. Any constant whose ID is absent from the register, or whose value disagrees with it, is a defect.

Report both lists before amending anything.

2. Add the conversation-only closures

Add these to DECISIONS-v3.md with status closed and the reasoning recorded.

2.7, closed as report-without-threshold. No pass-fail band. Report correlation, annualised tracking difference, and maximum rolling divergence per fund with the validation target and window stated. Two external anchors were sought and neither exists. Session 11 established issuers publish no tracking error against the levered daily objective, only against the unlevered index, which under daily-reset compounding is a different quantity. A separate search established that Direxion and ProShares prospectuses describe index correlation risk qualitatively with no numeric target. The two-tier band session 12 proposed was rejected because its thresholds fell in the empty gap between the eleven passing funds at 0.993 to 0.999 correlation and the three exceptions at 6.2 to 8.9 percent tracking difference, so any value in that gap produces the same partition and the threshold does no work. Flag as [A], since the decision rests on the absence of an anchor rather than on a measurement.

SOXS, keep the synthetic. The recorded exception of 6.21 percent annualised tracking difference and 1394 percent maximum rolling divergence stands and is reported beside every dependent result. Listed SOXS from 2010-03 was rejected because it would remove T11's bull-branch inverse basket across 2008.

SVXY, exclude 2018-02-06 from validation. Stated exclusion with the reason that the fund's NAV rebounded 187 percent against an index-implied 26 percent during the termination-scale event, which is a portfolio departure from the index rather than a construction failure. Every other session in the pre-2018 window matches to decimals.

8.8, benchmark ladder and nulls. Benchmarks are buy-and-hold QQQ, buy-and-hold TQQQ, vol-targeted QQQ at matched exposure, one fast-rebalancing naive rival at comparable trading frequency, and each of the four sleeves run standalone at full budget. Nulls are a timing shuffle preserving state distribution and holding-period structure via block bootstrap under 8.9, and a turnover-matched switching null at the measured transition rate. All at canonical parameters per 9.8, 1,000 draws, every line bearing the identical cost model. Ensemble against the best single sleeve is disclosed as post-hoc and joins 8.10's Romano-Wolf family. Pairwise correlation of the four standalone tracks reported alongside. Record the rationale, being that buy-and-hold comparisons confound the signal with a trading frequency of 105 transitions per year.

4.4, range retained at 0 to 50 basis points. Session 05's stress-window spread estimates showing SOXS at 401 basis points and SOXL at 288 in COVID were not used to extend the range, because the Corwin-Schultz variance-scaling assumption is violated on daily-reset funds so those figures substantially read volatility as spread. Recorded as a limitation that the cost model proxies auction cost with a continuous-market spread estimator and does not cover crisis conditions.

4.6, reopened and unresolvable before a result. The sweep as specified measures starting NAV, but the account compounds, so the liquidity and impact question applies to terminal size. Blocked until a first backtest exists.

3. Archive the session prompts

Create docs/prompts/ and save every session prompt that can be recovered from the session reports or from the working tree, named by session. Where a prompt cannot be recovered, record the session number and note the absence.

Save the session 13 prompt as docs/prompts/session-13.md. The user will supply its text.

4. Commit

One commit covering the five uncommitted documentation files, the register amendments, and the prompt archive. Report the hash and file count.

5. Report

outputs/session-12.6/REPORT.md covering the audit results, every decision added, the prompt archive contents and any gaps, and the commit hash.

Stop condition

Halt after step 5.
