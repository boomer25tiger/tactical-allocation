# Session 19.5 report

Run 2026-08-19. Ladder construction audit then window strip. No holdout was
executed and the 2021-08-01 boundary is untouched. No grid was re-executed and no
grid point was adopted or promoted. The primary window remains 2011-10-04. No
strategy parameter, threshold, instrument, weight, sleeve budget, cost model, cap
level, premium, NAV, or window boundary changed, and no construction defect was
repaired here.

Every figure below is read from an emitted CSV in `outputs/session-19_5/` under 9.12.

## Opening three

**The canonical positive control passes.** Rebuilt from the frozen inputs rather
than read from the deleted grid, the canonical specification returns
0.521845 annualised and
1.381701 Lo-corrected Sharpe over
2472 sessions, against targets 0.521845 and
1.381701 at gaps of 2.55e-07 and
3.06e-07 inside a 5e-07 tolerance stated
before comparing. All 339 manifested frozen inputs verify with zero mismatches.

**The QQQ row does not deviate.** Rebuilt with the ladder's own entry index and
start date, buy-and-hold QQQ reproduces the emitted ladder row to a worst gap of
5.55e-17 against a 5e-05 tolerance stated before
comparing. The motivating arithmetic argument is not borne out as an arithmetic
error in the row.

**No ladder row is a costless scaling.** The construction audit verdict is that
the levered rows hold the live fund ticker rather than a scaling of QQQ, and the
decisive check confirms it on the sharpest available discriminator.

## Step 0, the ladder artifact

The twelve-row ladder is `outputs/session-15/metrics-full.csv`, written by session
15, carrying 568 rows across
64 columns of which
12 sit in the designated cell.
Twelve rows exist. Session 14's `ladder.csv` carries fourteen lines including the
intraday-only and overnight-only hold universes, which the twelve-row ladder drops.

All six prose figures match the CSV at the three decimals the prose carries, with
0 disagreements.

**Every ladder row is on the superseded window.** The ladder's STRATEGY row reads
1.3846 over
2473 sessions, which is the
pre-correction 2011-10-03 start. Register 7.14a superseded that with 1.3817 over
2472 sessions on the 2011-10-04 start. Session 15 ran before that correction and
`s14_common.PRIMARY_START` still defaults to 2011-10-03, so every ladder row carries
the superseded boundary. This is documentation of a known correction not yet
propagated, rather than a new defect.

**Romano-Wolf, with the sign now established.** One of eleven one-sided comparisons
sits below 0.05, being the equal-weight universe at 0.033 with a mean daily
difference of +0.001378
and a t of
+2.288, so the
**strategy is above** the equal-weight universe. Buy-and-hold QQQ follows at 0.052,
also with the strategy above. The strategy sits below buy-and-hold TQQQ, both S2 and
S3 standalone, and long-legs-only, none of which reaches 0.05.

## Step 1, the QQQ row

Over the corrected primary window from the frozen input.

| quantity | value |
|---|---|
| annualised return | 0.230963 |
| annualised volatility | 0.190301 |
| mean risk-free rate over the window | 0.006050 |
| naive Sharpe | 1.156109 |
| Lo-corrected Sharpe | 1.803321 |
| implied Lo factor | 1.559819 |
| first-order daily autocorrelation | -0.100270 |
| lag count in the correction | 251 |
| weighted autocorrelation sum | -74.213 |
| sessions | 2472 |

The motivating arithmetic put QQQ's naive Sharpe near 1.25 and the measurement puts
it at 1.1561, so the naive figure is
lower than the argument assumed rather than higher.

**External verification is pending.** The only QQQ total-return path in this
repository is the frozen input the ladder itself used, so no independent series
exists offline and no network fetch was attempted inside this session.

## The Lo correction, measured against its own null

`bt.lo_sharpe` sums 251 weighted sample autocorrelations estimated from 2472
observations. The question the motivation raises is whether a factor of that size is
supported. It is answered by a control rather than by argument.

The null is 300 independent permutations of the same
excess returns at seed 20260819 fixed before drawing, which
preserves the marginal distribution and destroys serial dependence entirely.

| quantity | observed | null mean | null sd | null 5th | null 95th |
|---|---|---|---|---|---|
| weighted autocorrelation sum | -74.213 | -12.382 | 43.647 | | |
| implied Lo factor | 1.5598 | 1.1129 | 0.2235 | 0.7938 | 1.4783 |

The observed sum sits 1.417 standard
deviations from a null in which there is no autocorrelation at all, and a series with
no autocorrelation still produces a mean Lo factor of
1.1129 reaching
1.4783 at the 95th percentile. The null mean is
not one because each sample autocorrelation carries a small-sample bias of order
minus one over n and 251 of them are summed with weights up to 251.

Stated as measured, the Lo-corrected Sharpe as implemented carries a scale factor
whose sampling dispersion is of the same order as the difference between ladder rows.

## Step 2, ladder decomposition

Every one of the twelve rows reproduces from the frozen inputs, worst gap
9.99e-07 against the 5e-05 tolerance.

| line | naive | rank | Lo | rank | Lo factor | rho1 | turnover |
|---|---|---|---|---|---|---|---|
| buy_hold_TQQQ | 1.1412 | 4 | 1.7937 | 1 | 1.5718 | -0.0804 | 0.00 |
| buy_hold_QQQ | 1.1699 | 3 | 1.7924 | 2 | 1.5322 | -0.0980 | 0.02 |
| matched_exposure_levered_QQQ_1.70 | 1.1384 | 5 | 1.7899 | 3 | 1.5723 | -0.0804 | 0.85 |
| long_legs_only | 1.2133 | 1 | 1.4614 | 4 | 1.2045 | -0.0473 | 28.07 |
| vol_targeted_QQQ_matched | 1.0866 | 7 | 1.4353 | 5 | 1.3209 | -0.0718 | 1.29 |
| STRATEGY | 1.0922 | 6 | 1.3846 | 6 | 1.2677 | -0.0378 | 37.87 |
| sleeve_S2_standalone | 1.2071 | 2 | 1.3558 | 7 | 1.1232 | -0.0157 | 12.97 |
| sleeve_S3_standalone | 1.0721 | 8 | 1.1951 | 8 | 1.1147 | -0.0283 | 21.56 |
| naive_fast_1d_momentum | 0.7903 | 10 | 1.0754 | 9 | 1.3608 | -0.0255 | 64.66 |
| sleeve_T11_standalone | 0.8075 | 9 | 0.9736 | 10 | 1.2058 | -0.0030 | 53.49 |
| equal_weight_universe | 0.5806 | 11 | 0.5903 | 11 | 1.0167 | -0.0841 | 0.04 |
| sleeve_T10_standalone | 0.4061 | 12 | 0.5070 | 12 | 1.2485 | -0.0850 | 52.68 |

**8 of twelve rows change rank between
the two metrics.** The strategy holds rank
6 under the naive Sharpe and rank
6 under the Lo-corrected Sharpe, so its own
position is unchanged while the ordering around it is not.

The three rows the motivation identified as suspiciously close, being buy-and-hold
TQQQ, buy-and-hold QQQ, and matched-exposure levered QQQ, span
0.0038 on the Lo-corrected Sharpe and
0.0315 on the naive Sharpe, a factor of
8.23 wider.
Their Lo factors are 1.5718, 1.5322 and 1.5723. The convergence is produced by the
correction rather than by the construction.

## Step 3, construction audit

On the realized arm `bt.load_arm_panel` takes every levered ticker from
`_frozen_frame`, being the frozen fund parquet, so the series is the live fund's own
history with its real daily reset, financing and expense already embedded by the
issuer. On the synthetic arm the same tickers come from `_synthetic_frame`, being the
reconstruction. The designated cell is the realized arm.

Financing applies to the reconstructions only. The rate source is the frozen DTB3
accrued at rate over 360 per calendar day between sessions under the 5.5a convention,
the spread is `config.FINANCING_SPREAD_BP` over that reference for multiples above
one with a haircut for inverse funds and k equal to zero for the volatility funds
under 2.15, and the reset compounds daily with a daily close rebalance.

**Decisive check.** Tolerance 5e-03 on annualised Sharpe, stated before comparing.

| series | annualised return | annualised volatility | naive Sharpe |
|---|---|---|---|
| costless 3x QQQ, daily compounded, no financing | 0.655357 | 0.572361 | 1.163321 |
| live TQQQ | 0.601644 | 0.563735 | 1.112362 |
| ladder buy-and-hold TQQQ row | 0.626941 | 0.562710 | 1.141225 |

The ladder row sits 0.022096 from the costless
construction and 0.028863 from the live fund on
naive Sharpe, so neither is inside the tolerance and the Sharpe does not
discriminate. Annualised volatility does, being untouched by the risk-free
subtraction and by the account's cash accrual. The row sits
0.001025 from the live fund and
0.009650 from the costless construction, a
factor of nine closer to the live fund.

**Verdict: the row is not a costless scaling**, recorded as
`row_is_costless_scaling` = 0.

## Gate

The gate clears on both of its conditions, since no levered or inverse row is a
costless scaling and the QQQ row does not deviate beyond tolerance. Step 4 ran.

Two findings the gate does not cover are recorded rather than treated as passing,
being the superseded boundary on every ladder row and the sampling behaviour of the
Lo correction.

## Step 4, the window strip

A post-hoc sensitivity under 9.10. The primary window remains 2011-10-04. The
positive control at the canonical start reproduces the canonical to
2.55e-07 and
3.06e-07.

| start | date | sessions | annualised | naive | Lo | rank naive | rank Lo | realized-available share |
|---|---|---|---|---|---|---|---|---|
| earliest_full_composition | 2013-01-23 | 2146 | 0.6749 | 1.3242 | 1.6979 | 3 | 6 | 0.725 |
| pre_D21_boundary | 2011-10-03 | 2473 | 0.5226 | 1.0922 | 1.3846 | 6 | 6 | 0.629 |
| canonical | 2011-10-04 | 2472 | 0.5218 | 1.0911 | 1.3817 | 6 | 6 | 0.629 |
| first_session_2012 | 2012-01-03 | 2410 | 0.5809 | 1.1644 | 1.5636 | 3 | 5 | 0.646 |
| first_session_2013 | 2013-01-02 | 2160 | 0.6286 | 1.2641 | 1.5741 | 4 | 7 | 0.720 |
| first_session_2014 | 2014-01-02 | 1908 | 0.6336 | 1.2513 | 1.6016 | 3 | 5 | 0.816 |

**The strategy's rank is not stable across start dates.** It spans
3 to 6 under the naive Sharpe and
5 to 7 under the Lo-corrected Sharpe. The
canonical start returns the lowest rank of any start date tested under both metrics.
Reported as measured, with no interpretation and no change to the primary window.

## Step 5, coverage at the earliest start

**The earliest date at which all sleeves reach full composition on the synthetic
panel is 2013-01-23**, not 2007. It is bound
by QQQE first appearing
2012-03-21 plus
210 warmup sessions. That date is **later**
than the canonical 2011-10-04, so the synthetic panel supports no genuinely early
full-composition arm and the strip has no arm that reaches back before the canonical
window.

Over the 2146 sessions from that start,
0.7251 of sessions have every
sleeve-held ticker available on the realized panel and
0.2749 do not, so a start there is
confounded with panel source since the panel differs alongside the window. The
confound is disclosed rather than resolved.

**Register tension, recorded and left open.** Register 7.14b fixed the early-window
reporting form as coverage tables and availability timelines with no return figure at
any prominence. Step 4 emits return figures at the early start as a diagnostic, which
is in tension with that form. Whether any early-start figure enters the paper is a
register decision this session does not make and does not pre-empt.

## Step 6, defect class sweep under 9.13

Run regardless of the gate. Step 3 found no construction defect, so there is no
defect class to sweep. The sweep instead records the construction of all fourteen
levered and inverse instruments the strategy trades, being the leveraged longs, the
inverse funds, and the two volatility ETPs. Each takes the frozen fund parquet on the
realized arm and the reconstruction on the synthetic arm, and the two arms are the
registered pair rather than a defect.

**The canonical result does not depend on any instrument carrying the defect**,
recorded as `canonical_depends_on_defect` = 0, since the canonical runs on the
realized arm where every levered and inverse instrument is the live fund's own frozen
history. Nothing was repaired.

## Findings and the class of change each would need

| finding | class |
|---|---|
| every ladder row carries the superseded 2011-10-03 boundary | correctness repair, owned by session 20 step 5 |
| the Lo factor's sampling dispersion is of the same order as the gaps between ladder rows | register decision on whether 8.2 keeps the Lo-corrected Sharpe as headline |
| eight of twelve rows change rank between the naive and Lo-corrected metrics | documentation |
| the strategy's rank varies across start dates and is lowest at the canonical start | documentation, the primary window is unchanged |
| no full-composition start earlier than canonical exists on the synthetic panel | documentation |
| the 7.14b reporting form is in tension with emitting early-start return figures | register decision |
| no construction defect in any levered or inverse line | nothing to act on |
| external QQQ verification pending, no independent offline series | specification change if an independent source is added |

No recommendation is made on any of these.

## Resources

A memory ceiling of 4.0 GB was stated before
running. Peak observed was 0.157 GB across steps 1 to
3 and 0.188 GB across steps 4 to 6, both far below the
ceiling as single-specification runs were expected to be.

| step | seconds |
|---|---|
| environment build | 3.2 |
| step 1 positive control | 0.5 |
| step 1 QQQ | 1.1 |
| step 2 decomposition | 3.7 |
| step 3 construction audit | 0.0 |
| Lo sampling control | 0.1 |
| steps 4 to 6 | 20.2 |

## Stop condition

Halted after step 8. No holdout executed and the 2021-08-01 boundary untouched. No
grid re-executed and no grid point adopted or promoted. The primary window remains
2011-10-04. No construction defect repaired. One commit.

