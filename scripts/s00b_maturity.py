"""Session 00b, step 3. Realized-maturity diagnostics for constructions A, B, C.

Answers whether 2004 and 2005 remain problematic under B and C, or whether the
problem was specific to the interpolation construction.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00b"

LO, HI = 25.0, 35.0


def main():
    frames = {
        "A_interpolation": pd.read_parquet(INTERIM / "vx-cm30-a.parquet"),
        "B_sp_roll": pd.read_parquet(INTERIM / "vx-cm30-b.parquet"),
        "C_fixed_roll": pd.read_parquet(INTERIM / "vx-cm30-c.parquet"),
    }

    rows = []
    for tag, df in frames.items():
        df = df.copy()
        df["year"] = pd.to_datetime(df["trade_date"]).dt.year
        df["outside_band"] = (df["realized_dte"] < LO) | (df["realized_dte"] > HI)
        for y, g in df.groupby("year"):
            if tag == "A_interpolation":
                pin = float(g["clipped"].mean())
                pin_note = "clipping rate (weights clipped to [0,1])"
            else:
                pin = np.nan
                pin_note = ("not applicable: weights are in [0,1] by "
                            "construction, no clipping possible")
            rows.append({
                "construction": tag,
                "year": int(y),
                "sessions": len(g),
                "realized_dte_mean": g["realized_dte"].mean(),
                "realized_dte_sd": g["realized_dte"].std(),
                "realized_dte_min": g["realized_dte"].min(),
                "realized_dte_max": g["realized_dte"].max(),
                "frac_outside_25_35": float(g["outside_band"].mean()),
                "clipping_or_pinning_rate": pin,
                "clipping_concept": pin_note,
                "mean_abs_dev_from_30": (g["realized_dte"] - 30.0).abs().mean(),
            })

    res = pd.DataFrame(rows).sort_values(["construction", "year"])
    res.to_csv(OUT / "maturity-diagnostics.csv", index=False)

    piv = res.pivot(index="year", columns="construction",
                    values=["realized_dte_mean", "realized_dte_sd",
                            "frac_outside_25_35"])
    with pd.option_context("display.width", 250, "display.max_columns", 40):
        print(piv.round(3).to_string())

    print("\nfull-sample summary")
    for tag, df in frames.items():
        d = df["realized_dte"]
        out = ((d < LO) | (d > HI)).mean()
        print(f"  {tag:18s} mean={d.mean():6.2f} sd={d.std():5.2f} "
              f"min={d.min():6.2f} max={d.max():6.2f} "
              f"outside[25,35]={out:.4f} mean|dev30|={(d-30).abs().mean():.2f}")

    print("\n2004-2005 only")
    for tag, df in frames.items():
        d = df[pd.to_datetime(df["trade_date"]).dt.year <= 2005]["realized_dte"]
        out = ((d < LO) | (d > HI)).mean()
        print(f"  {tag:18s} n={len(d)} mean={d.mean():6.2f} sd={d.std():5.2f} "
              f"outside[25,35]={out:.4f} mean|dev30|={(d-30).abs().mean():.2f}")


if __name__ == "__main__":
    main()
