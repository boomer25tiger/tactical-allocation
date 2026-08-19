"""Session 17 step 1: one shard of the 121,500-specification grid.

Usage:  python scripts/s17_grid_worker.py <shard> <n_shards>

Nothing is printed to stdout. All progress goes to
outputs/session-17/grid-run.log, which every shard appends to, with a
timestamped heartbeat every HEARTBEAT specifications.

Each shard owns a contiguous block of specification indices and writes
four fixed-width binary files, so a killed shard resumes at the last
completed specification rather than restarting. The completed-
specification index is the resume point and is written as specifications
complete, never accumulated in memory.

No hardcoded parameter enters any measurement: every axis value comes
from src.config through s17_common.AXES, and the cost model, cap, and
commission arm come from s14_common. 7.4, the tier-two offset, is not a
searched axis and is held at its canonical value on every specification.

Emitted per specification:
  index-<shard>.i64    1 int64: the specification index, written last
  metrics-<shard>.f64  72 float64: index, 9 axis values, 40 standalone
                       metrics (8.11), 22 per-calendar-year figures
  moments-<shard>.f64  96 float64: excess-return sum and sum of squares
                       over each of the 48 base blocks
  panel-<shard>.f32    2472 float32: daily total return, primary window
"""
from __future__ import annotations

import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.s13_backtest as bt          # noqa: E402
import scripts.s14_common as C             # noqa: E402
import scripts.s15_lines as L              # noqa: E402
import scripts.s17_common as S             # noqa: E402
from src import config                     # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-17"
GRID = OUT / "grid"
PANEL = OUT / "panel"
LOG = OUT / "grid-run.log"

# 7.14 as corrected in session 16 step 1. s14_common still carries the
# superseded 2011-10-03; the override is local, as in session 16.
PRIMARY_START = pd.Timestamp("2011-10-04")

N_BASE_BLOCKS = 48
BATCH = 100
HEARTBEAT = 500

METRIC_ORDER = [
    "n_sessions", "total_return", "ann_return", "ann_vol", "sharpe_naive",
    "sharpe_lo", "max_drawdown", "calmar", "arith_mean_excess_ann",
    "ann_turnover", "sortino_mar_dtb3", "downside_deviation_ann", "skewness",
    "excess_kurtosis", "var_95_daily", "var_99_daily", "var_95_annualised",
    "var_99_annualised", "cvar_95_daily", "cvar_99_daily",
    "cvar_95_annualised", "cvar_99_annualised", "max_dd_duration_sessions",
    "max_dd_duration_calendar_days", "time_to_recovery_sessions",
    "recovered_within_window", "n_drawdowns_gt_20pct",
    "mean_duration_drawdowns_gt_20pct_sessions", "ulcer_index", "pain_ratio",
    "rolling_12m_sharpe_min", "rolling_12m_sharpe_max",
    "rolling_12m_sharpe_frac_below_zero", "pct_positive_months",
    "split_half_first_sharpe_lo", "split_half_second_sharpe_lo",
    "split_half_first_ann_return", "split_half_second_ann_return",
    "return_per_unit_turnover", "turnover_adjusted_sharpe",
]
YEARS = list(range(2011, 2022))
N_MET = 1 + len(S.AXES) + len(METRIC_ORDER) + 2 * len(YEARS)


def log(msg: str) -> None:
    """Append one timestamped line. O_APPEND keeps shards from interleaving."""
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}\n"
    fd = os.open(LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode())
    finally:
        os.close(fd)


def as_float(v) -> float:
    if v is None:
        return math.nan
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return math.nan


def main(shard: int, n_shards: int) -> None:
    GRID.mkdir(parents=True, exist_ok=True)
    PANEL.mkdir(parents=True, exist_ok=True)

    total = S.grid_size()
    lo = shard * total // n_shards
    hi = (shard + 1) * total // n_shards
    n_own = hi - lo

    fi = GRID / f"index-{shard:02d}.i64"
    fm = GRID / f"metrics-{shard:02d}.f64"
    fo = GRID / f"moments-{shard:02d}.f64"
    fp = PANEL / f"panel-{shard:02d}.f32"

    # Resume point: the completed-specification index. The recorded indices
    # must be exactly lo..lo+done-1, since a shard writes them in order.
    done = 0
    if fi.exists():
        rec = np.fromfile(fi, dtype=np.int64)
        if len(rec):
            expect = np.arange(lo, lo + len(rec), dtype=np.int64)
            if len(rec) > n_own or not np.array_equal(rec, expect):
                log(f"shard {shard} HALT: completed index is not the contiguous "
                    f"block {lo}..{lo + len(rec) - 1}")
                raise AssertionError("completed-specification index is not contiguous")
            done = len(rec)
    if done >= n_own:
        log(f"shard {shard} already complete at {n_own:,} specifications, nothing to do")
        return

    log(f"shard {shard} start range {lo:,}..{hi - 1:,} ({n_own:,} specs), "
        f"skipping {done:,} already recorded")

    C.PRIMARY_START = PRIMARY_START
    S.install_rf_cache()
    bt.s17_enable_engine_cache(True)
    env = C.build_env(verbose=False)
    cal = env["cal"]
    sig = S.fat_signals(env["panels"]["realized"], cal)
    o2o, cap_fn = env["o2o"], env["cap_fn"]
    rfa = S.rf_factor_array(cal)
    commission_fn = C.ARMS[C.CANONICAL_ARM]
    slip_fn = C.slip_class_premium()

    n_sess = None
    blocks = None
    year_pos = None

    mode = "r+b" if done else "wb"
    t0 = time.time()
    ibuf, mbuf, obuf, pbuf = [], [], [], []
    with open(fi, mode) as hidx, open(fm, mode) as hm, \
            open(fo, mode) as ho, open(fp, mode) as hp:
        if done:
            hidx.truncate(done * 8); hidx.seek(0, os.SEEK_END)
            hm.truncate(done * 8 * N_MET); hm.seek(0, os.SEEK_END)
            ho.truncate(done * 8 * 2 * N_BASE_BLOCKS); ho.seek(0, os.SEEK_END)

        for k in range(done, n_own):
            idx = lo + k
            values = S.spec_at(idx)
            S.apply_spec(values)

            rows = bt.run_signals(sig)["rows"]
            acc = bt.run_account(sig, o2o, rows, C.ANCHOR,
                                 commission_fn=commission_fn, slip_fn=slip_fn,
                                 cap_fn=cap_fn, rf_factors=rfa)
            daily = acc["daily"]
            r = C.window_slice(daily["ret"], "primary")

            if n_sess is None:
                n_sess = len(r)
                blocks = np.array_split(np.arange(n_sess), N_BASE_BLOCKS)
                year_pos = {y: np.flatnonzero(r.index.year == y) for y in YEARS}
                if shard == 0:
                    np.save(GRID / "block-sizes.npy",
                            np.array([len(b) for b in blocks], dtype=np.int64))
                if done:
                    hp.truncate(done * 4 * n_sess); hp.seek(0, os.SEEK_END)
            assert len(r) == n_sess, f"window length changed at spec {idx}"

            m = L.standalone_metrics(r, daily["nav"], acc["orders"])
            rf = bt.rf_per_session(r.index).fillna(0.0)
            ex = (r - rf).to_numpy()
            rv = r.to_numpy()

            rec = [float(idx)] + [float(v) for v in values]
            rec += [as_float(m.get(key)) for key in METRIC_ORDER]
            for y in YEARS:
                p = year_pos[y]
                if len(p) < 2:
                    rec += [math.nan, math.nan]
                    continue
                rec.append(float(np.prod(1.0 + rv[p]) - 1.0))
                rec.append(as_float(bt.lo_sharpe(pd.Series(ex[p]))))

            mom = np.empty(2 * N_BASE_BLOCKS, dtype=np.float64)
            for b, sel in enumerate(blocks):
                seg = ex[sel]
                mom[2 * b] = seg.sum()
                mom[2 * b + 1] = float(np.dot(seg, seg))

            mbuf.append(np.asarray(rec, dtype=np.float64))
            obuf.append(mom)
            pbuf.append(rv.astype(np.float32))
            ibuf.append(idx)

            if len(mbuf) >= BATCH or k == n_own - 1:
                # Payload first, the completed index last, so a kill between
                # the two leaves the index short rather than overstated.
                hm.write(np.concatenate(mbuf).tobytes())
                ho.write(np.concatenate(obuf).tobytes())
                hp.write(np.concatenate(pbuf).tobytes())
                hm.flush(); ho.flush(); hp.flush()
                os.fsync(hm.fileno()); os.fsync(ho.fileno()); os.fsync(hp.fileno())
                hidx.write(np.asarray(ibuf, dtype=np.int64).tobytes())
                hidx.flush(); os.fsync(hidx.fileno())
                ibuf, mbuf, obuf, pbuf = [], [], [], []

            if (k + 1) % HEARTBEAT == 0 or k == n_own - 1:
                el = time.time() - t0
                per = el / (k - done + 1)
                log(f"shard {shard} heartbeat completed {k + 1:,}/{n_own:,} "
                    f"elapsed {el:.0f}s rate {1.0 / per:.2f} spec/s "
                    f"eta {per * (n_own - k - 1) / 3600:.2f}h")

    log(f"shard {shard} COMPLETE {n_own:,} specifications in "
        f"{(time.time() - t0) / 3600:.2f}h")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
