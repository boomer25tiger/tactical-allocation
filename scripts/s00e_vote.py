"""Session 00e, step 3. Vote leave-one-out under both threshold treatments.

Informs 6.7. Session 00C reported flip counts under removal but did not state how
the threshold was treated. Both treatments are computed here:

  held   the threshold stays at 3, so a three-vote set requires unanimity
  moved  the threshold becomes 2, a simple majority of the three that remain

Windows follow Session 00C's "native" basis: for each SMA length, the sessions on
which every member of the full four-vote set has a defined SMA.

Vote classifications are properties of price series. Nothing is summed into a
portfolio and no return is computed.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s00c_indicators import load_panel, sma, tr_series   # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs" / "session-00e"

MEMBERS = ["SPY", "QQQ", "SMH", "SOXL"]
SMA_LENGTHS = [50, 100, 150, 200, 250]
FULL_THRESHOLD = 3          # three of four


def vote_frame(tr, members, n):
    """Identical to Session 00C's vote_frame."""
    cols = {}
    for t in members:
        s = tr[t]
        cols[t] = (s > sma(s, n))[sma(s, n).notna()]
    return pd.concat(cols, axis=1, join="inner").dropna().astype(bool)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tr = tr_series(load_panel())

    rows = []
    for n in SMA_LENGTHS:
        j = vote_frame(tr, MEMBERS, n)
        V = j[MEMBERS].to_numpy(bool)
        counts = V.sum(axis=1)
        base = counts >= FULL_THRESHOLD
        meta = dict(vote_set="S3_current", members="|".join(MEMBERS),
                    sma_length=n, n_sessions=len(j),
                    first_date=j.index[0].date().isoformat(),
                    last_date=j.index[-1].date().isoformat(),
                    full_threshold=FULL_THRESHOLD)

        for a, m in enumerate(MEMBERS):
            red = counts - V[:, a].astype(int)          # 3-vote count
            for label, thr in (("held_at_3_unanimity", 3),
                               ("moved_to_2_of_3", 2)):
                flip = base != (red >= thr)
                rows.append(dict(**meta, removed_vote=m,
                                 threshold_treatment=label,
                                 reduced_threshold=thr,
                                 flip_count=int(flip.sum()),
                                 flip_fraction=float(flip.mean()),
                                 frac_bull_full=float(base.mean()),
                                 frac_bull_reduced=float((red >= thr).mean())))

    res = pd.DataFrame(rows)
    res.to_csv(OUT / "vote-leave-one-out.csv", index=False)

    with pd.option_context("display.width", 240):
        for label in ("held_at_3_unanimity", "moved_to_2_of_3"):
            p = res[res.threshold_treatment == label].pivot(
                index="sma_length", columns="removed_vote", values="flip_count")
            print(f"\n=== flip_count, {label} ===")
            print(p[MEMBERS].to_string())
        print("\n=== window per SMA length ===")
        w = res.groupby("sma_length").agg(
            n_sessions=("n_sessions", "first"),
            first=("first_date", "first"), last=("last_date", "first"),
            frac_bull_full=("frac_bull_full", "first"))
        print(w.to_string())

    c = res[(res.sma_length == 200) &
            (res.threshold_treatment == "held_at_3_unanimity")]
    print("\n=== reproduction check against Session 00C, SMA 200 ===")
    ref = {"SPY": 408, "QQQ": 404, "SMH": 412, "SOXL": 12}
    for _, r in c.iterrows():
        print(f"  {r.removed_vote:5s} 00e={int(r.flip_count):4d} "
              f"00C={ref[r.removed_vote]:4d} "
              f"delta={int(r.flip_count)-ref[r.removed_vote]:+d}")
    print(f"  n_sessions 00e={int(c.n_sessions.iloc[0])} 00C=3935 "
          f"(00C window ended 2026-08-17, now truncated to "
          f"{c.last_date.iloc[0]})")
    print(f"wrote {OUT/'vote-leave-one-out.csv'} ({len(res)} rows)")


if __name__ == "__main__":
    main()
