#!/usr/bin/env python3
"""Confirm the holdout prediction was committed before the holdout is read.

A holdout session runs this as its FIRST step. It exits zero only when
docs/HOLDOUT-PREDICTION.md exists in committed history and the working copy
matches the committed blob exactly. It exits non-zero when the file is absent,
uncommitted, or modified, since in any of those cases the prediction's precedence
over the read is not established by the repository.

Written session 26. The commit that adds this script also adds the prediction, so
the first context in which this exits zero is a session running after that commit.
"""
from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = "docs/HOLDOUT-PREDICTION.md"


def git(*args: str) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout or r.stderr).strip()


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")
    print("The prediction's precedence over the holdout read is NOT established. "
          "Do not read the holdout.")
    sys.exit(1)


def main() -> None:
    print(f"verifying {TARGET}")
    path = ROOT / TARGET
    if not path.exists():
        fail(f"{TARGET} is absent from the working tree")

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"  working copy sha256   {digest}")
    print(f"  working copy bytes    {path.stat().st_size}")

    rc, out = git("log", "-1", "--format=%H%n%ad%n%cd", "--date=iso-strict", "--", TARGET)
    if rc != 0 or not out:
        fail(f"{TARGET} appears in no commit, so it is uncommitted")
    sha, authored, committed = (out.split("\n") + ["", ""])[:3]
    print(f"  commit                {sha}")
    print(f"  author timestamp      {authored}")
    print(f"  commit timestamp      {committed}")

    rc, out = git("cat-file", "-e", f"{sha}:{TARGET}")
    if rc != 0:
        fail(f"{TARGET} is not present in commit {sha}")

    rc, out = git("diff", "--quiet", "HEAD", "--", TARGET)
    if rc != 0:
        rc2, stat = git("diff", "--stat", "HEAD", "--", TARGET)
        fail(f"{TARGET} differs from HEAD, so the committed prediction is not the one "
             f"on disk. {stat}")

    rc, out = git("ls-files", "--error-unmatch", TARGET)
    if rc != 0:
        fail(f"{TARGET} is untracked")

    rc, blob = git("rev-parse", f"HEAD:{TARGET}")
    print(f"  blob at HEAD          {blob}")
    print("PASS  the prediction is committed and unmodified, so it predates this read.")
    sys.exit(0)


if __name__ == "__main__":
    main()
