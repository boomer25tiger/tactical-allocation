"""Session 00C, Step 6. SMA crossover divergence (informs 6.16).

For each long leveraged pair and each SMA length, measures how often the
leveraged fund and its underlying disagree on whether price sits above the
average, how long those disagreements last, and how far apart their crossover
events fall. Reported over the full common window and, separately, over the 60
sessions following each entry into a 20 percent drawdown in the underlying.

No strategy return, allocation, or performance statistic is computed. Above or
below an average is a property of one price series, not a position.
"""

import numpy as np
import pandas as pd

from s00c_indicators import OUT, SMA_LENGTHS, load_panel, run_lengths, sma, tr_series
from s00c_rsi import LONG_PAIRS

MAX_LAG = 60      # sessions; matching window for corresponding crossovers
DD_LEVEL = 0.20   # drawdown depth defining the stress regime
DD_WINDOW = 60    # sessions following each drawdown entry


def crossovers(above: pd.Series):
    """Integer positions of crossover events. Up is below to above."""
    a = above.to_numpy(bool)
    d = np.diff(a.astype(np.int8))
    return np.flatnonzero(d == 1) + 1, np.flatnonzero(d == -1) + 1


def match_offsets(u_idx: np.ndarray, l_idx: np.ndarray, max_lag: int):
    """One-to-one nearest matching of underlying crossovers to leveraged
    crossovers, greedy by absolute offset, ties broken by earlier underlying
    event. Offset is leveraged position minus underlying position, so a
    positive offset means the leveraged series crossed later."""
    if u_idx.size == 0 or l_idx.size == 0:
        return np.array([]), u_idx.size, l_idx.size
    cand = []
    for i, u in enumerate(u_idx):
        for j, l in enumerate(l_idx):
            off = int(l) - int(u)
            if abs(off) <= max_lag:
                cand.append((abs(off), int(u), i, j, off))
    cand.sort()
    used_u, used_l, offs = set(), set(), []
    for _, _, i, j, off in cand:
        if i in used_u or j in used_l:
            continue
        used_u.add(i)
        used_l.add(j)
        offs.append(off)
    return (np.array(offs, dtype=int),
            int(u_idx.size - len(used_u)), int(l_idx.size - len(used_l)))


def drawdown_windows(tr: pd.Series, level: float, window: int) -> np.ndarray:
    """Boolean mask over positions: the `window` sessions following each entry
    into a drawdown of `level` or deeper, measured from the running maximum."""
    v = tr.to_numpy(float)
    dd = v / np.maximum.accumulate(v) - 1.0
    deep = dd <= -level
    entry = np.flatnonzero(deep & ~np.concatenate(([False], deep[:-1])))
    mask = np.zeros(len(v), dtype=bool)
    for e in entry:
        mask[e:min(len(v), e + window)] = True
    return mask, entry


def offset_stats(offs: np.ndarray, unmatched_u: int, unmatched_l: int,
                 prefix: str = "") -> dict:
    p = prefix
    if offs.size == 0:
        base = {f"{p}n_matched": 0, f"{p}mean_offset": np.nan,
                f"{p}median_offset": np.nan, f"{p}sd_offset": np.nan,
                f"{p}min_offset": np.nan, f"{p}p05_offset": np.nan,
                f"{p}p25_offset": np.nan, f"{p}p75_offset": np.nan,
                f"{p}p95_offset": np.nan, f"{p}max_offset": np.nan,
                f"{p}frac_offset_zero": np.nan, f"{p}frac_abs_offset_le_1": np.nan,
                f"{p}frac_abs_offset_le_5": np.nan, f"{p}frac_offset_positive": np.nan}
    else:
        base = {
            f"{p}n_matched": int(offs.size),
            f"{p}mean_offset": float(offs.mean()),
            f"{p}median_offset": float(np.median(offs)),
            f"{p}sd_offset": float(offs.std(ddof=1)) if offs.size > 1 else np.nan,
            f"{p}min_offset": int(offs.min()),
            f"{p}p05_offset": float(np.percentile(offs, 5)),
            f"{p}p25_offset": float(np.percentile(offs, 25)),
            f"{p}p75_offset": float(np.percentile(offs, 75)),
            f"{p}p95_offset": float(np.percentile(offs, 95)),
            f"{p}max_offset": int(offs.max()),
            f"{p}frac_offset_zero": float((offs == 0).mean()),
            f"{p}frac_abs_offset_le_1": float((np.abs(offs) <= 1).mean()),
            f"{p}frac_abs_offset_le_5": float((np.abs(offs) <= 5).mean()),
            f"{p}frac_offset_positive": float((offs > 0).mean()),
        }
    base[f"{p}n_unmatched_underlying"] = unmatched_u
    base[f"{p}n_unmatched_leveraged"] = unmatched_l
    return base


def main():
    panel = load_panel()
    tr = tr_series(panel)
    rows = []

    for lev, und in LONG_PAIRS:
        for n in SMA_LENGTHS:
            tl, tu = tr[lev], tr[und]
            al = (tl > sma(tl, n))
            au = (tu > sma(tu, n))
            ok_l = sma(tl, n).notna()
            ok_u = sma(tu, n).notna()
            j = pd.concat({"l": al[ok_l], "u": au[ok_u]}, axis=1, join="inner").dropna()
            if len(j) < 2:
                continue
            j = j.astype(bool)
            tu_c = tu.reindex(j.index)

            dd_mask, dd_entries = drawdown_windows(tu_c, DD_LEVEL, DD_WINDOW)

            for scope in ("all", "post_dd20"):
                m = np.ones(len(j), dtype=bool) if scope == "all" else dd_mask
                if m.sum() < 2:
                    continue
                sub = j[m]
                agree = (sub["l"] == sub["u"]).to_numpy(bool)
                runs = run_lengths(~agree)

                # crossovers are always identified on the full common window;
                # under the stress scope only those events whose underlying
                # crossover falls inside the window are retained
                lu, ld = crossovers(j["l"])
                uu, ud = crossovers(j["u"])
                if scope == "post_dd20":
                    keep_u = np.flatnonzero(m)
                    uu = uu[np.isin(uu, keep_u)]
                    ud = ud[np.isin(ud, keep_u)]

                o_up, uu_un, lu_un = match_offsets(uu, lu, MAX_LAG)
                o_dn, ud_un, ld_un = match_offsets(ud, ld, MAX_LAG)
                o_all = np.concatenate([o_up, o_dn])

                base = dict(
                    pair=f"{lev}/{und}", leveraged=lev, underlying=und,
                    sma_length=n, scope=scope,
                    n_sessions=int(m.sum()),
                    first_date=sub.index[0].date().isoformat(),
                    last_date=sub.index[-1].date().isoformat(),
                    n_drawdown_entries=int(len(dd_entries)),
                    frac_agree_above_below=float(agree.mean()),
                    n_disagree_sessions=int((~agree).sum()),
                    n_disagreement_runs=int(runs.size),
                    run_mean=float(runs.mean()) if runs.size else np.nan,
                    run_median=float(np.median(runs)) if runs.size else np.nan,
                    run_p75=float(np.percentile(runs, 75)) if runs.size else np.nan,
                    run_p95=float(np.percentile(runs, 95)) if runs.size else np.nan,
                    run_max=int(runs.max()) if runs.size else 0,
                    run_n_len_1=int((runs == 1).sum()),
                    run_n_len_2_5=int(((runs >= 2) & (runs <= 5)).sum()),
                    run_n_len_6_20=int(((runs >= 6) & (runs <= 20)).sum()),
                    run_n_len_gt_20=int((runs > 20).sum()),
                    n_crossovers_underlying=int(uu.size + ud.size),
                    n_crossovers_leveraged=int(lu.size + ld.size),
                    frac_lev_above=float(sub["l"].mean()),
                    frac_und_above=float(sub["u"].mean()),
                )
                rows.append(dict(**base, direction="all",
                                 **offset_stats(o_all, uu_un + ud_un, lu_un + ld_un)))
                rows.append(dict(**base, direction="up",
                                 **offset_stats(o_up, uu_un, lu_un)))
                rows.append(dict(**base, direction="down",
                                 **offset_stats(o_dn, ud_un, ld_un)))

    df = pd.DataFrame(rows).sort_values(
        ["pair", "sma_length", "scope", "direction"]).reset_index(drop=True)
    df.to_csv(OUT / "sma-crossover-divergence.csv", index=False)

    pd.set_option("display.width", 250)
    print("=== Step 6, agreement on above or below, full window ===")
    m = (df.scope == "all") & (df.direction == "all")
    print(df[m].pivot(index="sma_length", columns="pair",
                      values="frac_agree_above_below")
          .to_string(float_format=lambda x: f"{x:.4f}"))
    print()
    print("=== disagreement sessions, full window ===")
    print(df[m].pivot(index="sma_length", columns="pair",
                      values="n_disagree_sessions").to_string())
    print()
    print("=== disagreement run length, median and max, full window, SMA 200 ===")
    print(df[m & (df.sma_length == 200)][
        ["pair", "n_sessions", "n_disagree_sessions", "n_disagreement_runs",
         "run_median", "run_p95", "run_max", "run_n_len_1", "run_n_len_gt_20"]
    ].to_string(index=False))
    print()
    print("=== crossover offsets, SMA 200, full window ===")
    m2 = (df.scope == "all") & (df.sma_length == 200)
    print(df[m2][["pair", "direction", "n_crossovers_underlying",
                  "n_crossovers_leveraged", "n_matched", "mean_offset",
                  "median_offset", "p05_offset", "p95_offset", "min_offset",
                  "max_offset", "frac_offset_zero", "frac_abs_offset_le_1",
                  "n_unmatched_underlying", "n_unmatched_leveraged"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print()
    print("=== stress regime, 60 sessions after a 20 percent underlying drawdown ===")
    m3 = (df.direction == "all") & (df.sma_length == 200)
    print(df[m3][["pair", "scope", "n_sessions", "n_drawdown_entries",
                  "frac_agree_above_below", "n_disagree_sessions", "run_max",
                  "n_matched", "mean_offset", "median_offset"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.4f}"))


if __name__ == "__main__":
    main()
