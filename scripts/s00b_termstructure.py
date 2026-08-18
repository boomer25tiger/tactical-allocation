"""Session 00b, step 6. Term-structure characterization of the front two contracts.

No inference is drawn. This characterizes the series only.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00b"


def main():
    p = pd.read_parquet(INTERIM / "vx-panel.parquet")
    d = p[(p["settle_idx"] > 0)].copy()
    d = d[d["expiry_effective"] >= d["trade_date"]]
    d["dte"] = (d["expiry_effective"] - d["trade_date"]).dt.days
    d = d.sort_values(["trade_date", "dte", "contract"])
    d["rank"] = d.groupby("trade_date").cumcount()

    f = d[d["rank"] == 0].set_index("trade_date")
    s = d[d["rank"] == 1].set_index("trade_date")
    m = pd.DataFrame({
        "front_contract": f["contract"], "front_settle": f["settle_idx"],
        "front_dte": f["dte"],
        "second_contract": s["contract"], "second_settle": s["settle_idx"],
        "second_dte": s["dte"],
    }).dropna().reset_index()

    m["slope"] = (m["second_settle"] - m["front_settle"]) / m["front_settle"]
    m["abs_slope"] = m["slope"].abs()
    m["contango"] = m["second_settle"] > m["front_settle"]
    m["backwardation"] = m["second_settle"] < m["front_settle"]
    m["flat"] = m["second_settle"] == m["front_settle"]
    m["expiry_session"] = m["front_dte"] == 0
    m["year"] = m["trade_date"].dt.year

    g = m.groupby("year")
    res = pd.DataFrame({
        "sessions": g.size(),
        "frac_contango": g["contango"].mean(),
        "frac_backwardation": g["backwardation"].mean(),
        "frac_flat": g["flat"].mean(),
        "median_abs_slope": g["abs_slope"].median(),
        "median_signed_slope": g["slope"].median(),
        "mean_signed_slope": g["slope"].mean(),
        "frac_expiry_sessions": g["expiry_session"].mean(),
        "median_front_dte": g["front_dte"].median(),
        "median_second_dte": g["second_dte"].median(),
    }).reset_index()
    res.to_csv(OUT / "term-structure.csv", index=False)
    m.to_parquet(INTERIM / "vx-term-structure-s00b.parquet", index=False)

    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(res.round(4).to_string(index=False))
    print(f"\nfull sample: contango {m['contango'].mean():.4f} "
          f"backwardation {m['backwardation'].mean():.4f} "
          f"flat {m['flat'].mean():.4f} "
          f"median|slope| {m['abs_slope'].median():.4f}")
    ex = m[~m["expiry_session"]]
    print(f"excluding expiry sessions (n={len(ex)}): contango "
          f"{ex['contango'].mean():.4f} backwardation "
          f"{ex['backwardation'].mean():.4f} "
          f"median|slope| {ex['abs_slope'].median():.4f}")


if __name__ == "__main__":
    main()
