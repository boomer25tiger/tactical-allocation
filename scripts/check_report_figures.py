"""Report-prose figure checker (register 9.12, session 15 step 9).

Report prose figures are read from the emitted CSVs rather than restated
from a separate computation. This script is the enforcement mechanism: it
re-derives the load-bearing figures of a session report from that
session's own CSVs and compares them to the numbers the prose carries.

Usage:  python scripts/check_report_figures.py <session-dir>

Prose-versus-data drift appeared in sessions 13.9 and 14, three figures
each time, so the check runs on every session report from 15 onward and
was run retrospectively against 14.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def numbers_in(text: str) -> set[str]:
    return set(re.findall(r"-?\d+\.\d+", text))


def check(session_dir: Path) -> int:
    rep = session_dir / "REPORT.md"
    if not rep.exists():
        print(f"no REPORT.md in {session_dir}")
        return 1
    text = rep.read_text()
    prose = numbers_in(text)
    csv_nums: set[str] = set()
    for c in sorted(session_dir.glob("*.csv")):
        try:
            df = pd.read_csv(c)
        except Exception:
            continue
        for col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            for v in s:
                for nd in (1, 2, 3, 4, 5, 6):
                    csv_nums.add(f"{v:.{nd}f}")
                    csv_nums.add(f"{v * 100:.{nd}f}")
                    csv_nums.add(f"{-v:.{nd}f}")
                    csv_nums.add(f"{-v * 100:.{nd}f}")
    # Register IDs and session numbers are prose tokens of the same shape as
    # figures; they are excluded by context rather than by value.
    ids = set(re.findall(r"(?:session|sessions|register at|item|under|per)\s+(\d+\.\d+)", text))
    ids |= set(re.findall(r"\b(\d\.\d{1,2})[a-c]\b", text))
    ids |= set(re.findall(r"\b([0-9]\.[0-9]{1,2})\b(?=[,.)\s]*(?:closed|amended|recorded|verdict|stand))", text))
    unmatched = sorted(x for x in prose if x not in csv_nums and x not in ids)
    print(f"{session_dir.name}: {len(prose)} decimal figures in prose, "
          f"{len(unmatched)} not found in the session's CSVs")
    for u in unmatched:
        ctx = ""
        m = re.search(r".{0,60}" + re.escape(u) + r".{0,40}", text)
        if m:
            ctx = m.group(0).replace("\n", " ")
        print(f"  UNMATCHED {u}  ...{ctx}...")
    return 0 if not unmatched else 2


if __name__ == "__main__":
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs" / "session-15"
    sys.exit(check(d if d.is_absolute() else ROOT / d))
