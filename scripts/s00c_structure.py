"""Session 00C, Steps 7 and 8.

Step 7. Vote structure for the S3 vote set and three alternatives (informs 6.7,
        documents 6.8).
Step 8. Overbought panel structure for the S1 and T11 panels (informs 6.9).

Both tables are written in long form, one row per measured quantity, because the
measurements are matrices, distributions and scalars together.

A vote is one instrument's price against its own moving average. A panel
condition is one instrument's RSI against a threshold. Neither is a position and
nothing here is summed into a portfolio.
"""

import itertools

import numpy as np
import pandas as pd

from s00c_indicators import (OUT, RSI_PERIODS, effective_independent, load_panel,
                             sma, tr_series, wilder_rsi)

VOTE_SMA = [50, 100, 150, 200, 250]
VOTE_SETS = {
    "S3_current": ["SPY", "QQQ", "SMH", "SOXL"],
    "alt1_TLT_for_SOXL": ["SPY", "QQQ", "SMH", "TLT"],
    "alt2_KMLM_for_SOXL": ["SPY", "QQQ", "SMH", "KMLM"],
    "alt3_drop_SOXL": ["SPY", "QQQ", "SMH"],
}

PANELS = {
    "S1_eleven": ["QQQE", "VTV", "VOX", "TECL", "VOOG", "VOOV", "TQQQ",
                  "XLP", "XLY", "FAS", "SPY"],
    "T11_five": ["SPY", "IOO", "TQQQ", "VTV", "XLF"],
}
PANEL_THRESHOLDS = [70, 75, 80]


def safe_corr(M: np.ndarray) -> np.ndarray:
    """Correlation matrix tolerant of constant columns, which are given zero
    off-diagonal correlation and unit variance on the diagonal."""
    k = M.shape[1]
    sd = M.std(axis=0, ddof=0)
    C = np.eye(k)
    for i, j in itertools.combinations(range(k), 2):
        if sd[i] > 0 and sd[j] > 0:
            C[i, j] = C[j, i] = np.corrcoef(M[:, i], M[:, j])[0, 1]
    return C


def vote_frame(tr: dict, members, n: int) -> pd.DataFrame:
    cols = {}
    for t in members:
        s = tr[t]
        cols[t] = (s > sma(s, n))[sma(s, n).notna()]
    return pd.concat(cols, axis=1, join="inner").dropna().astype(bool)


def step7(tr: dict) -> pd.DataFrame:
    """Each vote set is measured on its own maximal window and, so that the
    sets are comparable, on two shared windows: the window the current S3 set
    supports, and the window every set including KMLM supports."""
    frames = {(s, n): vote_frame(tr, m, n)
              for s, m in VOTE_SETS.items() for n in VOTE_SMA}
    bases = {}
    for n in VOTE_SMA:
        bases[("common_with_S3", n)] = frames[("S3_current", n)].index
        idx = frames[("S3_current", n)].index
        for s in VOTE_SETS:
            idx = idx.intersection(frames[(s, n)].index)
        bases[("common_all_sets", n)] = idx

    rows = []
    for set_name, members in VOTE_SETS.items():
        for n in VOTE_SMA:
            for basis in ("native", "common_with_S3", "common_all_sets"):
                j = frames[(set_name, n)]
                if basis != "native":
                    j = j.reindex(j.index.intersection(bases[(basis, n)]))
                if len(j) < 2:
                    continue
                rows.extend(_vote_rows(set_name, members, n, j, basis))
    return pd.DataFrame(rows)


def _vote_rows(set_name, members, n, j, basis):
            rows = []
            k = len(members)
            V = j[members].to_numpy(bool)
            counts = V.sum(axis=1)
            meta = dict(step="7_vote_structure", vote_set=set_name,
                        window_basis=basis,
                        members="|".join(members), n_votes=k, sma_length=n,
                        n_sessions=len(j),
                        first_date=j.index[0].date().isoformat(),
                        last_date=j.index[-1].date().isoformat())

            for a, b in itertools.combinations(range(k), 2):
                rows.append(dict(**meta, metric="pairwise_agreement",
                                 key1=members[a], key2=members[b],
                                 value=float((V[:, a] == V[:, b]).mean())))
            C = safe_corr(V.astype(float))
            for a, b in itertools.combinations(range(k), 2):
                rows.append(dict(**meta, metric="pairwise_correlation",
                                 key1=members[a], key2=members[b],
                                 value=float(C[a, b])))
            for c in range(k + 1):
                rows.append(dict(**meta, metric="vote_count_fraction",
                                 key1=str(c), key2="", value=float((counts == c).mean())))
                rows.append(dict(**meta, metric="vote_count_n",
                                 key1=str(c), key2="", value=float((counts == c).sum())))
            rows.append(dict(**meta, metric="effective_independent_votes",
                             key1="", key2="", value=effective_independent(C)))
            rows.append(dict(**meta, metric="mean_vote_count",
                             key1="", key2="", value=float(counts.mean())))

            for thr in range(1, k + 1):
                bull = counts >= thr
                rows.append(dict(**meta, metric="frac_bull", key1=str(thr),
                                 key2="", value=float(bull.mean())))
                for a in range(k):
                    drop = (counts - V[:, a].astype(int)) >= thr
                    rows.append(dict(**meta, metric="flip_fraction_leave_one_out",
                                     key1=str(thr), key2=members[a],
                                     value=float((bull != drop).mean())))
                    rows.append(dict(**meta, metric="flip_count_leave_one_out",
                                     key1=str(thr), key2=members[a],
                                     value=float((bull != drop).sum())))
            return rows


def step8(tr: dict) -> pd.DataFrame:
    rows = []
    for panel_name, members in PANELS.items():
        for n in RSI_PERIODS:
            cols = {t: wilder_rsi(tr[t], n).dropna() for t in members}
            j = pd.concat(cols, axis=1, join="inner").dropna()
            if len(j) < 2:
                continue
            k = len(members)
            R = j[members].to_numpy(float)
            meta = dict(step="8_overbought_panel", panel=panel_name,
                        members="|".join(members), n_names=k, rsi_period=n,
                        n_sessions=len(j),
                        first_date=j.index[0].date().isoformat(),
                        last_date=j.index[-1].date().isoformat())

            C = safe_corr(R)
            for a, b in itertools.combinations(range(k), 2):
                rows.append(dict(**meta, metric="pairwise_rsi_correlation",
                                 key1=members[a], key2=members[b],
                                 value=float(C[a, b])))
            rows.append(dict(**meta, metric="effective_independent_signals",
                             key1="", key2="", value=effective_independent(C)))
            rows.append(dict(**meta, metric="mean_pairwise_rsi_correlation",
                             key1="", key2="",
                             value=float(C[np.triu_indices(k, 1)].mean())))

            for thr in PANEL_THRESHOLDS:
                F = R > thr                       # per-name condition
                disj = F.any(axis=1)
                nd = int(disj.sum())
                rows.append(dict(**meta, metric="disjunction_firing_rate",
                                 key1=str(thr), key2="", value=float(disj.mean())))
                rows.append(dict(**meta, metric="disjunction_firing_days",
                                 key1=str(thr), key2="", value=float(nd)))
                rows.append(dict(**meta, metric="mean_names_firing_given_fire",
                                 key1=str(thr), key2="",
                                 value=float(F.sum(axis=1)[disj].mean()) if nd else np.nan))
                for a in range(k):
                    rows.append(dict(**meta, metric="individual_firing_rate",
                                     key1=str(thr), key2=members[a],
                                     value=float(F[:, a].mean())))
                    only = F[:, a] & (F.sum(axis=1) == 1)
                    rows.append(dict(**meta, metric="marginal_contribution",
                                     key1=str(thr), key2=members[a],
                                     value=float(only.sum() / nd) if nd else np.nan))
                    rows.append(dict(**meta, metric="marginal_contribution_days",
                                     key1=str(thr), key2=members[a],
                                     value=float(only.sum())))
                    drop = np.delete(F, a, axis=1).any(axis=1)
                    rows.append(dict(**meta, metric="disjunction_rate_without_name",
                                     key1=str(thr), key2=members[a],
                                     value=float(drop.mean())))
    return pd.DataFrame(rows)


def main():
    panel = load_panel()
    tr = tr_series(panel)

    d7 = step7(tr)
    d7.to_csv(OUT / "vote-structure.csv", index=False)
    d8 = step8(tr)
    d8.to_csv(OUT / "overbought-panel-structure.csv", index=False)

    pd.set_option("display.width", 250)
    for basis in ("native", "common_with_S3", "common_all_sets"):
        e = d7[(d7.metric == "effective_independent_votes") &
               (d7.window_basis == basis)]
        if not len(e):
            continue
        nsess = d7[d7.window_basis == basis].groupby("vote_set").n_sessions.first()
        print(f"=== Step 7, effective independent votes, window basis = {basis} ===")
        print(e.pivot(index="sma_length", columns="vote_set", values="value")
              .to_string(float_format=lambda x: f"{x:.3f}"))
        print("  sessions:", dict(nsess))
        print()
    print("=== Step 7, S3 pairwise agreement, SMA 200 ===")
    m = ((d7.vote_set == "S3_current") & (d7.sma_length == 200)
         & (d7.window_basis == "native"))
    print(d7[m & (d7.metric == "pairwise_agreement")][["key1", "key2", "value"]]
          .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print()
    print("=== Step 7, S3 pairwise vote correlation, SMA 200 ===")
    print(d7[m & (d7.metric == "pairwise_correlation")][["key1", "key2", "value"]]
          .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print()
    print("=== Step 7, S3 vote count distribution ===")
    v = d7[(d7.vote_set == "S3_current") & (d7.metric == "vote_count_fraction")
           & (d7.window_basis == "native")]
    print(v.pivot(index="sma_length", columns="key1", values="value")
          .to_string(float_format=lambda x: f"{x:.4f}"))
    print()
    print("=== Step 7, frac bull and leave-one-out flip, S3, SMA 200 ===")
    print(d7[m & (d7.metric == "frac_bull")][["key1", "value"]]
          .rename(columns={"key1": "threshold", "value": "frac_bull"})
          .to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print()
    print(d7[m & (d7.metric == "flip_fraction_leave_one_out")]
          .pivot(index="key2", columns="key1", values="value")
          .to_string(float_format=lambda x: f"{x:.4f}"))
    print()
    print("=== Step 8, effective independent signals ===")
    e8 = d8[d8.metric == "effective_independent_signals"]
    print(e8.pivot(index="rsi_period", columns="panel", values="value")
          .to_string(float_format=lambda x: f"{x:.3f}"))
    print()
    print("=== Step 8, mean pairwise RSI correlation ===")
    print(d8[d8.metric == "mean_pairwise_rsi_correlation"]
          .pivot(index="rsi_period", columns="panel", values="value")
          .to_string(float_format=lambda x: f"{x:.4f}"))
    print()
    print("=== Step 8, disjunction firing rate against individual rates, period 14 ===")
    for p in PANELS:
        sub = d8[(d8.panel == p) & (d8.rsi_period == 14)]
        dj = sub[sub.metric == "disjunction_firing_rate"].set_index("key1")["value"]
        ind = sub[sub.metric == "individual_firing_rate"].pivot(
            index="key2", columns="key1", values="value")
        mc = sub[sub.metric == "marginal_contribution"].pivot(
            index="key2", columns="key1", values="value")
        print(f"-- {p}: disjunction " +
              "  ".join(f"{t}={dj[t]:.4f}" for t in dj.index))
        print("   individual firing rate")
        print(ind.to_string(float_format=lambda x: f"{x:.4f}"))
        print("   marginal contribution, sole trigger share of firings")
        print(mc.to_string(float_format=lambda x: f"{x:.4f}"))
        print()


if __name__ == "__main__":
    main()
