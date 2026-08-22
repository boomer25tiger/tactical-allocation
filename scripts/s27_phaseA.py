"""Session 27 phase A. The three gates.

TOL_CANON = 5e-7, the standing positive-control tolerance, stated before comparing.
A failure on any gate halts the session before any holdout quantity is computed.
"""
from __future__ import annotations
import csv, hashlib, subprocess, sys
from pathlib import Path
ROOT = Path("/Users/GualyCr/Downloads/tactical-allocation")
sys.path.insert(0, str(ROOT))
OUT = ROOT/"outputs"/"session-27"; OUT.mkdir(parents=True, exist_ok=True)
TOL = 5e-7
EXPECTED_HASH = "3a3d150e986bcedfb9946deeb299373efac7026e7ccc7ca45625b9553fbecb2f"
rows = []
def add(t, **kw): rows.append({"table": t, **kw})
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True,
                                 cwd=ROOT)

add("preregistration", item="tolerance", value=TOL, note="stated before comparing")
add("preregistration", item="halt_rule",
    note="a failure on any of the three gates halts the session before any holdout "
         "quantity is computed")

# ---- A1, the prediction precedes the read ------------------------------------
r = sh(f"{sys.executable} scripts/verify_prediction_precedes_read.py")
add("A1", item="hook_exit_code", value=r.returncode)
for line in r.stdout.strip().split("\n"):
    s = line.strip()
    for k in ("working copy sha256", "working copy bytes", "author timestamp",
              "commit timestamp", "blob at HEAD", "commit "):
        if s.startswith(k):
            add("A1", item=k.strip().replace(" ", "_"), value=s[len(k):].strip())
            break
    if s.startswith(("PASS", "FAIL")):
        add("A1", item="hook_verdict", value=s.split()[0], note=s)
committed = sh("git show HEAD:docs/HOLDOUT-PREDICTION.md").stdout.encode()
digest = hashlib.sha256(committed).hexdigest()
add("A1", item="committed_blob_sha256", value=digest, target=EXPECTED_HASH)
a1 = (r.returncode == 0 and digest == EXPECTED_HASH)
add("A1", item="verdict", value="PASS" if a1 else "FAIL",
    note="the hook exits zero and the committed blob's hash matches the scaffold's "
         "expected value" if a1 else "halt")
print(f"A1 {'PASS' if a1 else 'FAIL'}")
if not a1:
    sys.exit(1)

# ---- A3, input integrity, run before the rebuild -----------------------------
r3 = sh(f"{sys.executable} scripts/s195_verify_inputs.py")
ver = {}
for line in r3.stdout.strip().split("\n"):
    if ":" in line and not line.startswith(" "):
        k, _, val = line.partition(":")
        ver[k.strip()] = val.strip()
n_checked = int(ver.get("carrying a manifest row and checked", "0") or 0)
n_bad = int(ver.get("mismatches", "1") or 1)
add("A3", item="files_under_data", value=ver.get("files under data/"))
add("A3", item="manifested_and_checked", value=n_checked)
add("A3", item="mismatches", value=n_bad)
add("A3", item="unmanifested", value=ver.get("unmanifested"))
add("A3", item="verifier_exit_code", value=r3.returncode)
a3 = (r3.returncode == 0 and n_bad == 0 and n_checked >= 339)
add("A3", item="verdict", value="PASS" if a3 else "FAIL",
    note=f"{n_checked} hashed frozen inputs verify with {n_bad} mismatches")
print(f"A3 {'PASS' if a3 else 'FAIL'}  checked {n_checked} mismatches {n_bad}")
if not a3:
    with open(OUT/"gates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table","item","value","target","note"],
                           extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    sys.exit(1)

# ---- A2, the standing positive control ---------------------------------------
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
env = C.build_env(verbose=False)
sig = env["sigs"]["realized"]
acc = bt.run_account(sig["sig"], env["o2o"], sig["rows"], C.ANCHOR,
                     commission_fn=C.ARMS[C.CANONICAL_ARM],
                     slip_fn=C.slip_class_premium(), cap_fn=env["cap_fn"])
d = acc["daily"]; ret = d["ret"].loc[d.index >= C.PRIMARY_START].dropna()
m = L.standalone_metrics(ret, d["nav"], acc["orders"])
a2 = (abs(m["ann_return"]-0.521845) <= TOL and abs(m["sharpe_lo"]-1.381701) <= TOL
      and len(ret) == 2472)
add("A2", item="ann_return", value=m["ann_return"], target=0.521845)
add("A2", item="sharpe_lo", value=m["sharpe_lo"], target=1.381701)
add("A2", item="n_sessions", value=len(ret), target=2472)
add("A2", item="primary_start", value=str(C.PRIMARY_START.date()),
    note="read from scripts/s14_common.py rather than typed")
add("A2", item="verdict", value="PASS" if a2 else "FAIL")
print(f"A2 {'PASS' if a2 else 'FAIL'}  ann {m['ann_return']:.6f} lo {m['sharpe_lo']:.6f} "
      f"n {len(ret)}")

add("gates", item="all_three", value="PASS" if (a1 and a2 and a3) else "FAIL",
    note="the read proceeds only on PASS")
with open(OUT/"gates.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["table","item","value","target","note"],
                       extrasaction="ignore"); w.writeheader(); w.writerows(rows)
print(f"wrote gates.csv, {len(rows)} rows")
sys.exit(0 if (a1 and a2 and a3) else 1)
