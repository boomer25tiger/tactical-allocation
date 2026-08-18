"""Session 00a, steps 4, 5 and 7.

Diagnostics by calendar year, the 30-day constant-maturity construction, and the
mechanical application of the pre-registered start-date rule.

No strategy return, Sharpe ratio, allocation, signal or performance statistic is
computed here. Counts, distributions and data properties only.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "session-00a"

TARGET_DAYS = 30
RUN_LEN = 60


def build_front_second(df):
    """At each session, rank the monthly contracts that carry a settlement price
    by time to expiry. Front is the nearest contract not yet past expiry."""
    d = df[(df["settle_idx"] > 0)].copy()
    d = d[d["expiry_effective"] >= d["trade_date"]]
    d["dte"] = (d["expiry_effective"] - d["trade_date"]).dt.days
    d = d.sort_values(["trade_date", "dte", "contract"])
    d["rank"] = d.groupby("trade_date").cumcount()
    return d


def main():
    panel = pd.read_parquet(INTERIM / "vx-panel.parquet")

    # per-contract settle-to-settle change, used by the spread proxy
    panel = panel.sort_values(["contract", "trade_date"])
    panel["settle_prev"] = panel.groupby("contract")["settle_idx"].shift(1)
    panel["abs_settle_chg"] = (panel["settle_idx"] - panel["settle_prev"]).abs()

    d = build_front_second(panel)
    sessions = np.sort(panel["trade_date"].unique())
    sess = pd.DataFrame({"trade_date": sessions})
    sess["year"] = pd.to_datetime(sess["trade_date"]).dt.year

    # ---- listing coverage ---------------------------------------------------
    n_listed = d.groupby("trade_date").size().rename("n_contracts")
    sess = sess.merge(n_listed, on="trade_date", how="left")
    sess["n_contracts"] = sess["n_contracts"].fillna(0).astype(int)
    sess["has_two"] = sess["n_contracts"] >= 2
    sess["has_three"] = sess["n_contracts"] >= 3

    # first date beginning an unbroken run of RUN_LEN sessions with >= 2
    ht = sess["has_two"].to_numpy()
    fwd = np.convolve(ht.astype(int), np.ones(RUN_LEN, dtype=int), mode="valid")
    starts = np.where(fwd == RUN_LEN)[0]
    global_first_run = (pd.Timestamp(sessions[starts[0]]) if len(starts) else pd.NaT)

    run_start_flag = np.zeros(len(sess), dtype=bool)
    run_start_flag[starts] = True
    sess["begins_60_run"] = run_start_flag

    # ---- front / second panels ---------------------------------------------
    front = d[d["rank"] == 0].set_index("trade_date")
    second = d[d["rank"] == 1].set_index("trade_date")

    def leg_frame(leg, tag):
        f = leg[["contract", "dte", "settle_idx", "volume", "open_interest",
                 "high_idx", "low_idx", "abs_settle_chg"]].copy()
        f.columns = [f"{tag}_{c}" for c in f.columns]
        return f

    fs = leg_frame(front, "f1").join(leg_frame(second, "f2"), how="inner")
    fs = fs.reset_index().rename(columns={"index": "trade_date"})
    fs["year"] = fs["trade_date"].dt.year
    fs["both_nonzero_vol"] = (fs["f1_volume"] > 0) & (fs["f2_volume"] > 0)

    # ---- roll dates ---------------------------------------------------------
    # the session on which the front contract expires and the second becomes front
    roll = fs[fs["f1_dte"] == 0].copy()
    roll["entered_contract"] = roll["f2_contract"]
    roll["entered_volume"] = roll["f2_volume"]
    roll["entered_nonzero"] = roll["entered_volume"] > 0
    roll[["trade_date", "year", "f1_contract", "entered_contract",
          "entered_volume", "entered_nonzero"]].to_csv(
        OUT / "vx-roll-dates.csv", index=False)

    # ---- spread proxy -------------------------------------------------------
    for tag in ("f1", "f2"):
        rng = (fs[f"{tag}_high_idx"] - fs[f"{tag}_low_idx"]) / fs[f"{tag}_settle_idx"]
        fs[f"{tag}_range_ratio"] = rng.where(fs[f"{tag}_volume"] > 0)
        fs[f"{tag}_settlechg_ratio"] = (
            fs[f"{tag}_abs_settle_chg"] / fs[f"{tag}_settle_idx"]
        ).where(fs[f"{tag}_volume"] == 0)

    # ---- constant maturity --------------------------------------------------
    cm = fs[["trade_date", "f1_contract", "f2_contract", "f1_dte", "f2_dte",
             "f1_settle_idx", "f2_settle_idx"]].copy()
    cm = cm.rename(columns={"f1_contract": "front_contract",
                            "f2_contract": "second_contract",
                            "f1_dte": "d1", "f2_dte": "d2"})
    denom = (cm["d2"] - cm["d1"]).replace(0, np.nan)
    w1_raw = (cm["d2"] - TARGET_DAYS) / denom
    cm["w1_raw"] = w1_raw
    cm["w1"] = w1_raw.clip(0.0, 1.0)
    cm["clipped"] = (w1_raw < 0) | (w1_raw > 1) | w1_raw.isna()
    cm["w1"] = cm["w1"].fillna(0.0)
    cm["cm30_settle"] = (cm["w1"] * cm["f1_settle_idx"]
                         + (1 - cm["w1"]) * cm["f2_settle_idx"])
    cm["year"] = cm["trade_date"].dt.year
    cm_out = cm[["trade_date", "cm30_settle", "front_contract", "second_contract",
                 "d1", "d2", "w1", "clipped"]].sort_values("trade_date")
    cm_out.to_parquet(INTERIM / "vx-cm30.parquet", index=False)

    # ---- assemble the by-year diagnostic table ------------------------------
    g_sess = sess.groupby("year")
    g_fs = fs.groupby("year")
    g_roll = roll.groupby("year")
    g_cm = cm.groupby("year")

    diag = pd.DataFrame({
        "sessions": g_sess.size(),
        "frac_sessions_two_contracts": g_sess["has_two"].mean(),
        "frac_sessions_three_contracts": g_sess["has_three"].mean(),
        "n_contracts_median": g_sess["n_contracts"].median(),
        "n_contracts_min": g_sess["n_contracts"].min(),
        "first_date_begins_60_session_2contract_run":
            g_sess.apply(lambda x: (x.loc[x["begins_60_run"], "trade_date"].min()
                                    if x["begins_60_run"].any() else pd.NaT),
                         include_groups=False),
        "front_median_volume": g_fs["f1_volume"].median(),
        "second_median_volume": g_fs["f2_volume"].median(),
        "front_median_open_interest": g_fs["f1_open_interest"].median(),
        "second_median_open_interest": g_fs["f2_open_interest"].median(),
        "frac_sessions_both_nonzero_volume": g_fs["both_nonzero_vol"].mean(),
        "n_roll_dates": g_roll.size(),
        "roll_entered_median_volume": g_roll["entered_volume"].median(),
        "frac_rolls_entered_nonzero_volume": g_roll["entered_nonzero"].mean(),
        "front_spread_proxy_range_over_settle": g_fs["f1_range_ratio"].median(),
        "second_spread_proxy_range_over_settle": g_fs["f2_range_ratio"].median(),
        "front_spread_proxy_settlechg_over_settle": g_fs["f1_settlechg_ratio"].median(),
        "second_spread_proxy_settlechg_over_settle": g_fs["f2_settlechg_ratio"].median(),
        "n_front_zero_volume_sessions": g_fs.apply(
            lambda x: int((x["f1_volume"] == 0).sum()), include_groups=False),
        "n_second_zero_volume_sessions": g_fs.apply(
            lambda x: int((x["f2_volume"] == 0).sum()), include_groups=False),
        "cm30_sessions": g_cm.size(),
        "clipping_rate": g_cm["clipped"].mean(),
    })
    diag.index.name = "year"
    diag = diag.reset_index()
    diag.to_csv(OUT / "vx-diagnostics.csv", index=False)

    print(f"global first date beginning a {RUN_LEN}-session run with >=2 "
          f"contracts: {global_first_run.date() if pd.notna(global_first_run) else 'none'}")
    print(f"cm30 sessions: {len(cm_out)}  "
          f"{cm_out['trade_date'].min().date()} .. {cm_out['trade_date'].max().date()}")
    print(f"overall clipping rate: {cm['clipped'].mean():.4f}")
    print()
    show = ["year", "sessions", "frac_sessions_two_contracts",
            "n_contracts_median", "n_contracts_min",
            "front_median_volume", "second_median_volume",
            "frac_sessions_both_nonzero_volume", "n_roll_dates",
            "frac_rolls_entered_nonzero_volume", "clipping_rate"]
    with pd.option_context("display.width", 250, "display.max_columns", 50):
        print(diag[show].to_string(index=False))

    (OUT / "_global_first_run.txt").write_text(
        str(global_first_run.date()) if pd.notna(global_first_run) else "none")


if __name__ == "__main__":
    main()
