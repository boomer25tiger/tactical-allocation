# Session 23 report

The quiet-machine pass, on a machine that was not quiet. Phase A halted on the
contention condition before launching, phase B was skipped as dependent on it, and
phases C and D ran. The 2021-08-01 holdout boundary is untouched, no grid was
re-executed, and no grid point was adopted.

Free memory is not reported as headroom anywhere. The metrics used are load average,
process CPU percent, compressor size, swap used, swap free, and page-outs.

## Machine state at launch

| quantity | value |
|---|---|
| cores | 8 |
| halt threshold, twice the core count | 16 |
| load average, one minute | 71.43 |
| load average, five minute | 53.18 |
| load average, fifteen minute | 33.06 |
| compressor | 2.813 GiB |
| swap used | 14433.19 MB |
| swap free | 926.81 MB |

The five processes consuming the most CPU at launch.

| rank | percent | process |
|---|---|---|
| 1 | 73.5 | /Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.fram |
| 2 | 49.1 | /Applications/Google Chrome.app/Contents/Frameworks/Google Chrome Framework.fram |
| 3 | 26.2 | /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents |
| 4 | 22.6 | /Library/Frameworks/Python.framework/Versions/3.13/Resources/Python.app/Contents |
| 5 | 21.5 | /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer |

The load average of 71.43 is
8.9288 times the
core count and higher than the 39.57 session 22 recorded when its pass failed to
complete. Five samples taken before this reading showed the one-minute figure between
60 and 63 with the five and fifteen minute figures rising, and by the phase C write
the one-minute figure read 121.2, so the load was not a
transient spike.

## Phase A, the B1 re-emission

**Halted on the contention condition without launching.** load average 71.43 at launch exceeds twice the core count at 16. Session 22 established that a pass does not finish under these conditions, and the halt condition requires reporting rather than starting one. The pass is not attempted, so no wall limit is consumed and no figure is produced.

The abandonment rule was written to the artifact before the halt check, so the
pre-registration stands unconsumed. The limit would have been
969 seconds, being
ten times the 96.9 second chunk-514 pass in m1-diagnostic.csv, which completed at a larger working set of 3.561 GB, at chunk
257, which completed at a 1.824 GB peak in 63.1 seconds.

The standing positive control passes, with the canonical rebuilt from the frozen
inputs returning 0.521845 annualised and
1.381701 Lo-corrected Sharpe over
2472 sessions inside a
5e-07 tolerance stated before comparing.

the session anticipated a quiet machine and the machine is not quiet. The one-minute load is higher than the 39.57 session 22 recorded, and the five and fifteen minute figures were rising across five samples.

## Phase B, the corrected degradation null

**Skipped.** phase A halted on contention without launching, so phase B does not run.

The construction stays as recorded, being read from
outputs/session-20/degradation-null-corrected.csv and unmodified. the construction was recorded there and would run unchanged. It decomposes each specification's per-block moments into the cross-sectional block mean plus a residual, permutes each residual across blocks independently at a seed fixed before drawing, then recomposes, which preserves the shared period effect while removing any persistent idiosyncratic edge.

**the slope's removal at 9.35 was decided on the absence of a valid null rather than on any result, so the removal is unaffected by this phase not running. A favourable outcome would have reopened the question rather than settling it, and no outcome exists.**

## Phase C, the resource record

The constraint is CPU contention, not memory. Established by session 22 phase A under a pre-registered rule.

| observation from session 22 | value |
|---|---|
| peak resident | 1.133 |
| maximum page-out rate | 80.9 |
| compressor | 2.7 |
| load average | 39.57 |
| process CPU mean percent | 6.25 |

**Neither pass ran this session**, so neither pass ran. The machine was not quiet, so the session provides no new completion observation and therefore neither confirms nor refutes the contention diagnosis by completion. It is consistent with it, since the load that halted the session is higher than the load under which session 22's pass failed.

### The diagnosis history

| stage | claim | what was actually established |
|---|---|---|
| session 21 | memory | CLAIMED blocked on memory. OBSERVED processes at low CPU and low resident size, each terminated by hand. NEVER OBSERVED an operating-system kill, memory exhaustion, or any completion attempt. The claim asserted a mechanism from an absence |
| correction | impatience | CLAIMED the passes might have finished had they not been killed. OBSERVED that a chunk-514 pass peaked at 3.561 GB, higher than any killed pass, and completed in 96.9 seconds. NEVER OBSERVED a completion attempt at the killed configuration, so this claim also ran ahead of the evidence, in the opposite direction |
| session 22 | contention | CLAIMED CPU contention. OBSERVED a pre-registered 1800 second attempt that did not complete, with peak resident 1.133 GB, page-outs at 80.9 per second, the compressor flat, load average 39.57 on eight cores and the process receiving 6.25 percent CPU. This is the first of the three supported by a measurement rather than an inference |
| session 23 | consistent, not confirmed | the halt condition fired before any launch, so no completion observation was added. The diagnosis stands on session 22's measurement alone |

the class of an inference recorded as a measurement has now produced three register corrections, at 9.22 for a vacuous check, at 9.38 for a gate turning on a single draw, and at 9.35 with 8.12 for the resource claim.

The record is kept because each of the first two diagnoses named a mechanism the evidence did not reach. The third named one the evidence did reach, and it was reached only because a rule was pre-registered and a completion attempt was allowed to run to that rule.

## Findings and the class of change each would need

| finding | class |
|---|---|
| the machine is under heavier contention than when session 22's pass failed | documentation |
| the B1 re-emission remains outstanding, with a measured reason | correctness repair, deferred |
| the corrected degradation null remains unrun | documentation, since the slope's removal did not rest on it |
| the diagnosis class has produced three register corrections | documentation |

No recommendation is made on any of these.

## What remains open before the holdout can run

**Two measurements remain outstanding**, being the B1 re-emission and the corrected
degradation null. Neither is load-bearing. The chunk-first-element defect is repaired
in code at four sites and the degradation slope is removed from the paper at 9.35, so
both close defects rather than restore figures.

- **Ten config parameters have no consumer** and two more are read but never invoked.
- **`crash_threshold` was fixed after measurement on its own axis.**
- **SVIX and UVIX leave a code path that will not execute at the holdout read**, with
  the loader left unchanged deliberately.
- **D16 and D23 stand.**

## Resources per phase

| phase | load one minute | compressor GiB | swap used MB | swap free MB |
|---|---|---|---|---|
| A, at the halt check | 71.43 | 2.813 | 14433.19 | 926.81 |
| B | not launched | | | |
| C, at the write | 121.2 | 2.757 | 14689.12 | 670.88 |

No process CPU percent is reported for a measured pass, since no pass ran.

## Stop

Halted after phase D. No holdout executed, no grid re-executed, no grid point
adopted, no canonical value changed, and the primary window remains 2011-10-04.

