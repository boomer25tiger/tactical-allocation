"""Session 00a, step 7. Apply the pre-registered start-date rule mechanically.

The four conditions and their thresholds are fixed. Nothing here is tuned to what
the data shows. Where a condition cannot be evaluated because no VXX overlap
exists, that is recorded as NA and, per the rule's own wording ("where VXX
overlap exists"), does not block the year.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "session-00a"

C1_MIN_LISTING = 0.99
C2_MIN_BOTH_VOL = 0.80
C3_MIN_ROLL_VOL = 1.00
C4_MIN_CORR = 0.95


def main():
    diag = pd.read_csv(OUT / "vx-diagnostics.csv")
    val = pd.read_csv(OUT / "vxx-validation.csv")

    d = diag.merge(val[["year", "overlap_sessions", "daily_return_correlation"]],
                   on="year", how="left")

    rows = []
    for _, r in d.iterrows():
        c1_v = r["frac_sessions_two_contracts"]
        c2_v = r["frac_sessions_both_nonzero_volume"]
        c3_v = r["frac_rolls_entered_nonzero_volume"]
        c4_v = r["daily_return_correlation"]
        has_overlap = pd.notna(c4_v)

        c1 = bool(c1_v >= C1_MIN_LISTING)
        c2 = bool(c2_v >= C2_MIN_BOTH_VOL)
        c3 = bool(c3_v >= C3_MIN_ROLL_VOL)
        c4 = bool(c4_v >= C4_MIN_CORR) if has_overlap else None

        failing = []
        if not c1:
            failing.append("C1 listing")
        if not c2:
            failing.append("C2 both-leg volume")
        if not c3:
            failing.append("C3 roll volume")
        if has_overlap and not c4:
            failing.append("C4 VXX correlation")

        rows.append({
            "year": int(r["year"]),
            "c1_frac_two_contracts": c1_v,
            "c1_pass": c1,
            "c2_frac_both_nonzero_volume": c2_v,
            "c2_pass": c2,
            "c3_frac_rolls_nonzero_volume": c3_v,
            "c3_pass": c3,
            "c4_vxx_correlation": c4_v,
            "c4_pass": ("NA (no overlap)" if not has_overlap else c4),
            "all_pass": bool(c1 and c2 and c3 and (c4 is not False)),
            "binding_failures": "; ".join(failing) if failing else "",
        })

    res = pd.DataFrame(rows)
    res.to_csv(OUT / "vx-decision-rule.csv", index=False)

    passing = res[res["all_pass"]]
    start_year = int(passing["year"].iloc[0]) if len(passing) else None

    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(res.to_string(index=False))
    print()
    if start_year is None:
        print("NO YEAR SATISFIES ALL FOUR CONDITIONS")
    else:
        print(f"FIRST YEAR SATISFYING ALL FOUR CONDITIONS: {start_year}")
        panel_min = pd.read_parquet(ROOT / "data" / "interim" / "vx-cm30.parquet")
        first_date = panel_min.loc[
            panel_min["trade_date"].dt.year == start_year, "trade_date"].min()
        print(f"SAMPLE START DATE (first CM30 session in that year): "
              f"{first_date.date()}")
        (OUT / "_start_date.txt").write_text(f"{start_year},{first_date.date()}")

    pre2009 = res[(res["year"] < 2009) & (res["all_pass"])]
    print(f"\nyears before 2009 passing: "
          f"{sorted(pre2009['year'].tolist()) if len(pre2009) else 'NONE'}")


if __name__ == "__main__":
    main()
