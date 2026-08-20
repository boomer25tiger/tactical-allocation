# Session 19.6 report

Three measurements, all read-only against the repository outside
`outputs/session-19_6/`. Nothing was repaired, nothing committed, no register entry
written, and the 2021-08-01 holdout boundary is untouched. The stored 48-block
moment array was reused, which is not a grid re-execution. Every figure below is
read from an emitted CSV in this directory.

## M1 positive control, and what it uncovered

The positive control **passes**, reproducing all four session 19 figures at a gap of
exactly zero against a 1e-12 tolerance stated before comparing, with the chunk
pinned to 514.

| figure | reproduced | target | gap |
|---|---|---|---|
| pbo | 0.1578088578088578 | 0.1578088578088578 | 0.0e+00 |
| degradation_slope | -1.0663023854544191 | -1.0663023854544191 | 0.0e+00 |
| degradation_intercept | 2.7549013078347317 | 2.7549013078347317 | 0.0e+00 |
| degradation_r_squared | 0.5469127629590327 | 0.5469127629590327 | 0.0e+00 |

Pinning the chunk is not cosmetic. A first attempt derived the chunk from a memory
ceiling, produced 128, and **failed** the same control on three of the four figures,
with the slope off by 1.8e-04. The chunk sweep that followed is the reason the
failure is reported rather than tuned away.

| chunk | PBO gap | slope gap | seconds | peak GB |
|---|---|---|---|---|
| 128 | 0.0e+00 | 1.84e-04 | 38.8 | 1.089 |
| 257 | 0.0e+00 | 7.28e-05 | 63.1 | 1.824 |
| 514 | 0.0e+00 | 0.00e+00 | 96.9 | 3.561 |

PBO is identical at every chunk size while the three regression figures are not, and
0 of 12,870 selections differ between chunk 128 and chunk 514, so the cause is not the
argmax flipping.

### The cause, in `scripts/s19_step4.py` lines 143 and 144

```
        n_is = float(mc[0] @ nvec)
        n_os = float(oc[0] @ nvec)
```

The in-sample session count is taken from the **first combination of each chunk** and
applied to every combination in that chunk. The merged super-block counts are
unequal, spanning 153 to 156 sessions, so the true in-sample count varies across
combinations from 1224 to 1248 across 9 distinct values. The chunk boundaries therefore
enter the emitted figures. The same line is at `scripts/s18_step3.py` line 142, so
the defect originates in session 18 and was inherited unchanged.

PBO is unaffected because within a chunk the substituted count scales every
specification identically and rank ordering is preserved. The regression compares
Sharpe levels across combinations, which is where the count enters.

Recomputing at chunk 514 with the exact per-combination count gives the following.

| figure | as emitted | exact count | shift |
|---|---|---|---|
| pbo | 0.1578088578088578 | 0.1578088578088578 | 0.000e+00 |
| slope | -1.0663023854544191 | -1.0666200132036998 | 3.176e-04 |
| intercept | 2.7549013078347317 | 2.7556630502858295 | 7.617e-04 |
| R-squared | 0.5469127629590327 | 0.547339642724338 | 4.269e-04 |

## M1 result, the mechanical null

The null permutes the 48 stored blocks independently per specification at seed
20260822 fixed before drawing, then merges to 16 by the same
adjacent-triple reduction. Each specification keeps its own full-window moments, and
the full-window naive Sharpe is preserved to 8.882e-16
against a 1e-10 tolerance stated before comparing. What survives is the
complementary-half arithmetic and nothing else.

The pilot replication ran in 105.7 s. A wall-clock budget of
1800 s stated before the count was chosen gives
**17 replications**, and the count is set by that
budget rather than by a power calculation.

| quantity | null mean | null sd | null 5th | null 95th | observed | z | percentile |
|---|---|---|---|---|---|---|---|
| slope | -0.808988 | 0.065423 | -0.883650 | -0.702697 | -1.066620 | -3.9379 | 0.00 |
| intercept | 2.051508 | 0.146526 | 1.819204 | 2.226303 | 2.755663 | 4.8057 | 100.00 |
| R-squared | 0.062795 | 0.009674 | 0.047841 | 0.077872 | 0.547340 | 50.0889 | 100.00 |
| PBO | 0.991928 | 0.001813 | 0.989402 | 0.994390 | 0.157809 | -460.0064 | 0.00 |

**The null slope is centred at -0.808988**, which is neither near
zero nor near minus one. Partition arithmetic alone therefore carries most of the
observed slope's magnitude, and the observed -1.066620
carries a z of -3.9379
against the null mean, at the null's 0th percentile.

Stated as measured. A null slope near minus one would mean the observed slope
carries little information beyond partition arithmetic. A null slope near zero would
mean it measures degradation. The measured null sits between the two, so part of the
observed slope is mechanical and part is not, and the emitted figure separates the
two nowhere.

The other three comparisons are larger. Null R-squared averages
0.062795 against an observed 0.547340, and
null PBO averages 0.991928 against an observed
0.157809. Under the null the in-sample-best
specification lands in the bottom half of the out-of-sample ranking almost always,
which is what destroying cross-specification block alignment produces.

No recommendation follows and nothing was changed.

## M2, composition on held tickers only

The held universe is derived from the abstract syntax tree of `src/sleeves.py`. A
ticker is held if it carries a non-zero weight in a returned dictionary or is
returned as a bare ticker string by a terminal helper. No list is written by hand,
which is the convention `scripts/s195_strip.py` breached.

**19 held tickers** and
**13 signal-only tickers**. QQQE is signal-only,
confirming that the 19.5 binding constraint was a ticker the strategy never holds.

Four tickers are classified differently by the hardcoded list.

| ticker | difference |
|---|---|
| FAS | derived signal-only, hardcoded held |
| KMLM | derived neither, hardcoded held |
| QQQ | derived held, hardcoded signal input |
| SH | derived neither, hardcoded held |

### Warmup, derived rather than assumed

The moving average at 200 sessions binds, since
it exceeds Wilder RSI seed convergence at 190
sessions for the grid maximum period of 28. The derived
requirement is 200 against
`config.WARMUP_SESSIONS` of 210, a stated
margin of 10.

### Full composition on held tickers

| arm | date | binding |
|---|---|---|
| synthetic | 2012-07-13 | bound by BTAL first available 2011-09-13 plus 210 warmup sessions |
| realized | 2016-03-29 | bound by LABU first available 2015-05-28 plus 210 warmup sessions |

Neither date falls before 2011-10-04, so the conclusion that the panel supports no
earlier full-composition start survives the correction, while the 19.5 date of
2013-01-23 is superseded on the synthetic arm by
2012-07-13.

Two held tickers, SVIX and UVIX, are never available on either panel, so a strict
reading of full composition is unreachable on any date. They are reached only through
an availability switch that resolves to SVXY and UVXY, and the dates above are
computed over the tickers that do load.

### The two measures side by side

Over the canonical window of 2472 sessions,
**916 sessions** carry at
least one held ticker unlisted on the realized panel, a share of
0.3706. Over the same window
`outputs/session-16/boundary-correction.csv` records
**0.0 unavailable fills**.
The two are different quantities. Listing coverage counts sessions where a ticker was
unlisted whether or not it was targeted, and the 7.14 measure counts fills the
strategy attempted and could not make. The 19.5 report presented the first without
distinguishing it from the second.

## M3, the fourteen sessions at the front of the 2013-01-02 arm

The front span runs 2013-01-02 to
2013-01-22, being 14 sessions.
Its cumulative return is **-0.190783**, and UVXY is held
on 10 of those sessions.

| date | return | UVXY held | holdings |
|---|---|---|---|
| 2013-01-02 | -0.087777 | no | SOXL=0.1250 SOXS=0.0834 SQQQ=0.2084 TECS=0.0834 TLT=0.1250 TQQQ=0.3752 |
| 2013-01-03 | +0.002073 | yes | SOXL=0.1669 SVXY=0.0834 TECL=0.1669 TQQQ=0.3338 UVXY=0.2503 |
| 2013-01-04 | -0.013836 | no | SOXL=0.1251 SOXS=0.0834 SQQQ=0.2086 TECS=0.0835 TLT=0.1251 TQQQ=0.3755 |
| 2013-01-07 | -0.003035 | yes | BIL=0.0834 BTAL=0.0024 SOXL=0.1251 TQQQ=0.3754 UVXY=0.3337 |
| 2013-01-08 | -0.010760 | yes | BIL=0.0843 BTAL=0.0024 SOXL=0.1250 TQQQ=0.3827 UVXY=0.3247 |
| 2013-01-09 | -0.017739 | no | SOXL=0.1251 SOXS=0.0834 SQQQ=0.2085 TECS=0.0834 TLT=0.1250 TQQQ=0.3754 |
| 2013-01-10 | +0.005185 | no | SOXL=0.1315 SOXS=0.0790 SQQQ=0.2019 TECS=0.0812 TLT=0.1237 TQQQ=0.3835 |
| 2013-01-11 | -0.000920 | yes | BIL=0.0834 BTAL=0.0061 SOXL=0.1251 TQQQ=0.3754 UVXY=0.3337 |
| 2013-01-14 | -0.009184 | yes | BIL=0.0841 BTAL=0.0061 SOXL=0.1261 TQQQ=0.3747 UVXY=0.3318 |
| 2013-01-15 | -0.004649 | yes | SOXL=0.1251 SOXS=0.0834 SQQQ=0.0833 TECS=0.0834 TQQQ=0.3751 UVXY=0.2501 |
| 2013-01-16 | -0.007963 | yes | SOXL=0.1263 SOXS=0.0847 SQQQ=0.0836 TECS=0.0840 TQQQ=0.3799 UVXY=0.2419 |
| 2013-01-17 | -0.008169 | yes | SOXL=0.2085 TECL=0.0834 TQQQ=0.4586 UVXY=0.2502 |
| 2013-01-18 | +0.002431 | yes | SOXL=0.0834 TECL=0.0834 TQQQ=0.3335 UVXY=0.5004 |
| 2013-01-22 | -0.051427 | yes | BIL=0.0833 BTAL=0.0066 SOXL=0.1250 TQQQ=0.3751 UVXY=0.3335 |

Terminal identity per sleeve is in `jan2013-read.csv`, matched by the ticker set each
sleeve returns against the terminal strings in
`outputs/session-18/reachability.csv`, and reported against the prior calendar
position since `run_account` fills with a one-session lag.

### The arithmetic verifies

Compounding the late arm's growth of 80.825627 with
the front span's 0.809217 and annualising over
2160 sessions gives
0.6286270583369205 against the emitted
0.6286270583369207, a gap of
2.220e-16 inside a 1e-9 tolerance stated before
comparing. The premise holds and the difference between the two arms is carried
entirely by those sessions.

### The three overlap figures, now emitted

| figure | value |
|---|---|
| overlapping sessions | 2146 |
| daily return correlation | 1.0 |
| max absolute daily return difference | 0.000e+00 |
| cumulative return, early arm | 79.82562654420259 |
| cumulative return, late arm | 79.82562654420259 |
| position vectors agree every session | yes |

### The nesting asymmetry

the strip compares a nested strategy against non-nested benchmarks, so a rank change across arms mixes the strategy's window change with the benchmarks' re-entry. The 19.5 report does not state this.

## Findings and the class of change each would need

| finding | class |
|---|---|
| the in-sample session count is taken from the first combination of each chunk in `s19_step4.py:143` and `s18_step3.py:142` | correctness repair |
| the emitted degradation slope, intercept and R-squared depend on the chunk size, being the same root cause | correctness repair |
| the null slope is centred well away from zero, so most of the observed slope's magnitude is partition arithmetic | register decision on whether the slope is reported at all, documentation if it is |
| the 19.5 full-composition date was bound by a signal input the strategy never holds | documentation, the 19.5 figure is superseded |
| `s195_strip.py` classified four tickers by a hardcoded list that disagrees with the code | correctness repair |
| SVIX and UVIX are held in code and never load on either panel | documentation |
| listing coverage and unavailable fills were conflated in the 19.5 report | documentation |
| the strip compares a nested strategy against re-initialised benchmarks | correctness repair |
| the front span carries the whole difference between the two 2013 arms | documentation |

No recommendation is made on any of these and nothing was repaired.

## Resources

| measurement | wall clock | peak resident |
|---|---|---|
| M1 positive control | 97.7 s | 3.489 GB |
| M1 null, 17 replications | 105.7 s for the pilot | 3.489 GB |
| M2 | under a second after the environment build | not separately recorded |
| M3 | 3.4 s | 0.177 GB |

Two earlier M1 attempts are recorded rather than omitted. The first stated a 5.0 GB
ceiling, which sized the chunk at 1286 and drove the machine to 10.2 percent CPU with 13.8 GB of swap in use. The second stated 2.0 GB, session 19's own value, and also thrashed, because the machine carried 12.6 GB of 14.0 GB swap in use at the time. The wall-clock figures here are therefore not comparable with session 19's 775.0 s for the same pass, which is recorded in outputs/session-19/pbo.csv.

## Stop

Halted after the report. Nothing repaired, nothing committed, no register entry
written, holdout untouched, grid not re-executed, no grid point adopted or promoted.

