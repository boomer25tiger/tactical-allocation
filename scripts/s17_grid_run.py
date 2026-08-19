"""Session 17 step 1 launcher: run the whole grid detached.

Usage:  nohup python scripts/s17_grid_run.py <n_shards> >> log 2>&1 &

Spawns one worker process per shard, waits for all of them, and writes a
single summary line on completion. Progress lives in
outputs/session-17/grid-run.log; this process prints nothing per
specification. Killing this process and relaunching it resumes every
shard from its completed-specification index.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s17_common as S            # noqa: E402
from src import config                    # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-17"
LOG = OUT / "grid-run.log"
WORKER = ROOT / "scripts" / "s17_grid_worker.py"


def log(msg: str) -> None:
    with open(LOG, "a") as fh:
        fh.write(f"{datetime.now().isoformat(timespec='seconds')} {msg}\n")


def main(n_shards: int) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    config.validate()
    total = S.grid_size()
    log(f"launcher start pid {os.getpid()} shards {n_shards} "
        f"searched {total:,} of enumerated {S.enumerated_size():,} "
        f"(7.4 tier-two offset held at {S.CANONICAL_TIER_TWO_OFFSET}, not searched)")

    t0 = time.time()
    procs = []
    for k in range(n_shards):
        p = subprocess.Popen([sys.executable, str(WORKER), str(k), str(n_shards)],
                             cwd=str(ROOT), stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT)
        procs.append((k, p))
        log(f"launcher spawned shard {k} pid {p.pid}")

    failed = []
    for k, p in procs:
        rc = p.wait()
        if rc != 0:
            failed.append((k, rc))
            log(f"launcher shard {k} exited non-zero rc {rc}")

    el = (time.time() - t0) / 3600
    done = 0
    for f in sorted((OUT / "grid").glob("index-*.i64")):
        done += f.stat().st_size // 8
    status = "COMPLETE" if not failed and done == total else "INCOMPLETE"
    line = (f"GRID {status}: {done:,}/{total:,} specifications in {el:.2f}h"
            + (f", failed shards {failed}" if failed else ""))
    log("launcher " + line)
    print(line, flush=True)
    return 0 if status == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 8))
