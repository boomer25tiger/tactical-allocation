"""Session 22 phase G. The register-claim sweep.

Third instance of the class, being an inference recorded as a measurement. A
vacuous check passing on empty input, a gate turning on a single draw, and a
resource claim asserting a mechanism never observed. 9.13 covers defects found
in code; this class sits in the register text.
"""
from __future__ import annotations
import csv, re, sys
from pathlib import Path
ROOT=Path("/Users/GualyCr/Downloads/tactical-allocation"); OUT=ROOT/"outputs/session-22"
TARGETS=[ROOT/"docs/DECISIONS-v3.md", ROOT/"docs/STATE.md"] + sorted(ROOT.glob("outputs/*/REPORT*.md"))
# phrases that assert an impossibility, a cause, or a mechanism
PAT=[(r"blocked on memory","resource claim asserting a cause"),
     (r"halted on the memory gate","resource claim asserting a cause"),
     (r"killed on the memory gate","resource claim asserting an agent"),
     (r"died thrashing","resource claim asserting a cause"),
     (r"which killed two passes","resource claim asserting an agent"),
     (r"cannot be (measured|sourced|run|done)","impossibility claim"),
     (r"is not available","impossibility claim"),
     (r"unavailable at this machine state","impossibility claim"),
     (r"is unreachable","impossibility claim")]
rows=[]
for f in TARGETS:
    try: t=f.read_text()
    except Exception: continue
    for i,line in enumerate(t.split("\n"),1):
        for pat,cls in PAT:
            if re.search(pat,line,re.I):
                rows.append({"table":"hit","file":str(f.relative_to(ROOT)),"line":i,
                             "claim":line.strip()[:150],"class":cls})
                break
print(f"swept {len(TARGETS)} documents, {len(rows)} hits")
ESTAB=[
 ("blocked on memory / halted on the memory gate",
  "correctness repair",
  "What was established is that each pass was terminated by hand after slowing, with "
  "no completion attempt allowed. No process was terminated by the operating system. "
  "Session 22 phase A allowed a completion attempt under a pre-registered 1800 second "
  "limit and the pass still did not finish, so the passes do not complete at this "
  "machine state. The MECHANISM in the original claim was wrong, since peak resident "
  "reached 1.133 GB against the 3.561 GB that completed in m1-diagnostic.csv, page-outs "
  "averaged 344 per fifteen second sample, and the compressor stayed near 2.7 GiB. The "
  "measured constraint is CPU contention, with load average 39.57 on eight cores and "
  "the process receiving a mean of 6.25 percent CPU"),
 ("free memory quoted as available headroom",
  "wording correction",
  "macOS holds free near zero by design and uses the remainder as cache, so a low free "
  "figure is not low headroom. Sessions 19.6 through 21 quoted free as headroom "
  "repeatedly. The meaningful signals are compressor size, swap used, and the page-out "
  "rate, and this session reports those instead"),
 ("gate C tripped, stated as a property of the result",
  "correctness repair",
  "What was established is that one exceedance of 1,000 draws did not clear a threshold "
  "reachable only at zero exceedances. Session 22 phase B measured seven exceedances of "
  "10,000, being p 0.00070, which does clear it. The gate outcome was a property of the "
  "gate's resolution and not of the strategy"),
 ("the leave-one-out artifacts carry the superseded boundary",
  "correctness repair",
  "Session 21 F2 recorded this as established. Session 22 phase C rebuilt them and the "
  "base estimate is identical to ten decimals at 1.3817013060, which is the corrected "
  "value. Session 16 made the 7.14a correction and s16_step4.py ran after it, so the "
  "artifacts were already correct and the claim was inferred from the rebuild list "
  "rather than measured"),
 ("the 1.5636 agreement is coincidental",
  "correctness repair",
  "Session 21 F2 asserted this from the two operations being differently defined. They "
  "are not independent. The primary window begins 2011-10-04, so dropping calendar 2011 "
  "removes very nearly the sessions that starting at the first session of 2012 removes, "
  "and the two agree to 8.326e-07 rather than to four decimals. The agreement is "
  "structural"),
 ("the exposure-matched line reaches a higher naive Sharpe than the strategy",
  "wording correction",
  "Session 21 measured this at a single 60 session window. Session 22 phase D shows it "
  "holds only there, with the matched line reading 1.033797 at 120 sessions, 0.965584 "
  "at 252 and 0.917770 at 504 against the strategy's 1.0911, so the finding is "
  "window-dependent and the window that produced it is the noisiest"),
 ("SVIX and UVIX are unreachable",
  "claim holds as written",
  "Phase E traces the path. State.available returns False for a ticker absent from the "
  "panel, the switch selects the fallback before the weight dictionary is built, and no "
  "renormalisation occurs. The claim was traced rather than inferred when first made"),
 ("config.SIZING_MODE is unwired",
  "claim holds as written",
  "Session 20 traced the engine hardcoding math.trunc at s13_backtest.py:528 and "
  "session 21 confirmed no call to size_position. Established by tracing"),
]
for claim,cls,note in ESTAB:
    rows.append({"table":"assessment","claim":claim,"class":cls,"note":note})
n_rep=sum(1 for _,c,_ in ESTAB if c=="correctness repair")
n_word=sum(1 for _,c,_ in ESTAB if c=="wording correction")
n_hold=sum(1 for _,c,_ in ESTAB if c=="claim holds as written")
rows.append({"table":"summary","claim":"assessed","class":str(len(ESTAB))})
rows.append({"table":"summary","claim":"correctness repairs","class":str(n_rep)})
rows.append({"table":"summary","claim":"wording corrections","class":str(n_word)})
rows.append({"table":"summary","claim":"hold as written","class":str(n_hold)})
rows.append({"table":"scope","claim":"class_definition",
             "note":"an inference recorded as a measurement. The three instances are a "
                    "vacuous check passing on empty input at 9.22, a gate turning on a "
                    "single draw at 9.38, and a resource claim asserting a mechanism "
                    "never observed, which this entry covers"})
with open(OUT/"register-claim-sweep.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","file","line","claim","class","note"],
                     extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"assessed {len(ESTAB)}: {n_rep} correctness repairs, {n_word} wording "
      f"corrections, {n_hold} hold as written")
print(f"wrote {OUT/'register-claim-sweep.csv'} with {len(rows)} rows")
