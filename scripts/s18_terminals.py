"""Session 18 step 1 support: terminal-state firing counts.

A terminal is identified by the line of the return statement that
executed, recovered with sys.settrace rather than by reimplementing the
branch logic, so the counter cannot drift from src/sleeves.py. An exit
by NotImplementedError is counted as its own pseudo-terminal.

Signals only. No weight is used beyond what determines which terminal
fired, no account is run, and no cost is evaluated.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s13_backtest as bt      # noqa: E402
import src.sleeves as sleeves          # noqa: E402
from src import config                 # noqa: E402

SLEEVE_FILE = sleeves.__file__
TRACED = {"t10_weights", "t11_weights", "s2_weights", "s3_weights",
          "_t11_bond_baller", "_t11_feaver_bear"}
OWNER = {"t10_weights": "T10", "t11_weights": "T11",
         "s2_weights": "S2", "s3_weights": "S3",
         "_t11_bond_baller": "T11", "_t11_feaver_bear": "T11"}

# Terminal names keyed by (function, return line). Filled on first use from
# the source text so the label always matches the line it names.
_LABELS: dict[tuple[str, int], str] = {}


def _label(fn: str, lineno: int) -> str:
    key = (fn, lineno)
    if key not in _LABELS:
        src = Path(SLEEVE_FILE).read_text().splitlines()
        text = src[lineno - 1].strip() if 0 < lineno <= len(src) else "?"
        _LABELS[key] = f"{fn}:L{lineno} {text}"
    return _LABELS[key]


def count_terminals(sig, i_from: int, i_to: int) -> Counter:
    """Firing count of every terminal over calendar positions [i_from, i_to)."""
    counts: Counter = Counter()
    cal = sig.calendar
    fns = bt.SLEEVE_FNS

    def local(frame, event, arg):
        if event == "return":
            fn = frame.f_code.co_name
            if arg is None:
                counts[(OWNER[fn], f"{fn}:RAISE")] += 1
            else:
                counts[(OWNER[fn], _label(fn, frame.f_lineno))] += 1
        return local

    def glob(frame, event, arg):
        if (event == "call" and frame.f_code.co_name in TRACED
                and frame.f_code.co_filename == SLEEVE_FILE):
            frame.f_trace_lines = False
            return local
        return None

    sys.settrace(glob)
    try:
        for i in range(i_from, i_to):
            st = sig.state_at(i)
            d = cal[i]
            for name in ("T10", "T11", "S2", "S3"):
                try:
                    fns[name](d, st)
                except NotImplementedError:
                    pass
    finally:
        sys.settrace(None)
    return counts
