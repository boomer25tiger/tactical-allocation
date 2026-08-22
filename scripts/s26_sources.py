"""Session 26 figure gather. Every figure the prediction quotes, read from its
emitted CSV under 9.12, with the prompt's value recorded beside it where the
prompt named one. No figure is taken from the prompt."""
from __future__ import annotations
import ast, csv, pathlib
R = pathlib.Path("/Users/GualyCr/Downloads/tactical-allocation")
OUT = R/"outputs"/"session-26"; OUT.mkdir(parents=True, exist_ok=True)
S, D = [], []
def src(item, path, value, note="", prompt=""):
    S.append({"item": item, "source_file": path, "literal_value": value,
              "prompt_value": prompt, "note": note})
def dis(item, prompt, source, path, kind, note):
    D.append({"item": item, "prompt_value": prompt, "source_value": source,
              "source_file": path, "kind": kind, "note": note})

def rows(p): return list(csv.DictReader(open(R/p)))

# ---- ladder metrics ----------------------------------------------------------
MFP = "outputs/session-20/rebuilt/metrics-full.csv"
MF = {r["line"]: r for r in rows(MFP)
      if r["table"] == "metrics" and r["convention"] == "o2o" and r["window"] == "primary"}
src("strategy_sharpe_naive_primary", MFP, MF["STRATEGY"]["sharpe_naive"], prompt="1.091086")
src("strategy_sharpe_lo_primary", MFP, MF["STRATEGY"]["sharpe_lo"], prompt="1.381701")
src("strategy_ann_turnover", MFP, MF["STRATEGY"]["ann_turnover"], prompt="37.87")
src("buy_hold_QQQ_ann_turnover", MFP, MF["buy_hold_QQQ"]["ann_turnover"], prompt="0.02")
src("strategy_max_dd_duration_sessions", MFP, MF["STRATEGY"]["max_dd_duration_sessions"],
    "the deepest drawdown's own duration")
src("strategy_max_dd_duration_calendar_days", MFP,
    MF["STRATEGY"]["max_dd_duration_calendar_days"])
src("strategy_n_drawdowns_gt_20pct", MFP, MF["STRATEGY"]["n_drawdowns_gt_20pct"])
src("strategy_max_drawdown", MFP, MF["STRATEGY"]["max_drawdown"])
dis("buy_hold_QQQ_ann_turnover", "0.02", MF["buy_hold_QQQ"]["ann_turnover"], MFP,
    "rounding", "the prompt rounds to two decimals and the emitted value is quoted here")

# ---- beta decomposition and window sensitivity -------------------------------
BD = "outputs/session-21/beta-decomposition.csv"
g21 = {}
for r in csv.reader(open(R/BD)):
    if r and r[0] == "timing_decomposition": g21[r[1]] = r[2]
    if r and r[0] == "rolling": g21["rolling_" + r[1]] = r[2]
src("timing_ann_contribution_60", BD, g21["timing_ann_contribution"], prompt="+0.011293")
src("total_ann_check_60", BD, g21["total_ann_check"], prompt="+0.572563")
src("rolling_beta_sd_60", BD, g21["rolling_beta_sd"])
BW = "outputs/session-22/beta-window-sensitivity.csv"
bw = {(r["window"], r["item"]): r["value"] for r in rows(BW) if r["table"] in ("timing","rolling")}
for w in ("120", "252", "504"):
    src(f"timing_ann_contribution_{w}", BW, bw[(w, "timing_ann_contribution")])
    src(f"rolling_beta_sd_{w}", BW, bw[(w, "beta_sd")])

# ---- leave one out -----------------------------------------------------------
LO = "outputs/session-22/rebuilt/leave-one-out.csv"
lo = {r["dropped_year"]: r["sharpe_lo"] for r in rows(LO)
      if r["table"] == "loo" and r["series"] == "STRATEGY"}
src("loo_base_sharpe_lo", LO, lo["none (base)"], prompt="1.381701")
src("loo_drop_2011_sharpe_lo", LO, lo["2011"], prompt="1.5636")
src("loo_drop_2020_sharpe_lo", LO, lo["2020"], prompt="1.6183")
src("loo_drop_2018_sharpe_lo", LO, lo["2018"],
    "the minimum across the eleven, so removing 2018 LOWERS the estimate")
dis("crisis_years", "fast crashes in 2011, 2018 and 2020",
    f"2011 {lo['2011']}, 2020 {lo['2020']}, 2018 {lo['2018']} against a base of "
    f"{lo['none (base)']}", LO, "figure",
    "removal of 2011 and of 2020 each raises the estimate, so both are years the "
    "strategy did worse than its average. Removal of 2018 gives the minimum across the "
    "eleven, so 2018 is a year the strategy did BETTER than its average and does not "
    "belong in a list of years its weakness showed")

# ---- effective exposure -------------------------------------------------------
EX = "outputs/session-16/exposure-reconciliation.csv"
can = next(r for r in rows(EX) if r["table"] == "canonical_exposure")
src("canonical_mean_effective_exposure", EX, can["mean_effective_exposure"], prompt="1.70")
src("canonical_wildest_vol_decile_exposure", EX, can["wildest_vol_decile"])
dis("mean_effective_exposure", "near 1.70", can["mean_effective_exposure"], EX, "figure",
    "1.70 is the leverage factor naming the matched_exposure_levered_QQQ_1.70 ladder "
    "line, a different quantity. The canonical's own mean effective exposure is the "
    "emitted value")

# ---- the short leg -------------------------------------------------------------
SL = "outputs/session-15.5/short-leg-decomposition.csv"
a = next(r for r in rows(SL)
         if r["table"] == "decomposition_t10_isolated" and r["arm"] == "A")
src("t10_short_leg_ticker", SL, a["short_leg"])
src("t10_short_leg_leverage_multiple", SL, a["leverage_multiple"])
src("t10_short_leg_mean_weight_when_held", SL, a["mean_weight_when_held"], prompt="0.5")
src("t10_short_leg_held_sessions", SL, a["held_sessions"])
src("t10_corr_short_vs_rest_of_sleeve", SL, a["corr_short_vs_rest_of_sleeve"],
    "the primary-window baseline P3 part one predicts a sign change against")
src("t10_short_leg_total_arith_contribution", SL, a["total_arith_contribution"])
src("t10_short_leg_beta_component", SL, a["beta_component"])
src("t10_short_leg_residual_component", SL, a["residual_component"])

# ---- SQQQ sites, read from the source rather than from the prompt --------------
SP = "src/sleeves.py"
text = (R/SP).read_text(); tree = ast.parse(text)
fns = [(n.lineno, n.end_lineno, n.name) for n in ast.walk(tree)
       if isinstance(n, ast.FunctionDef)]
sites = []
for i, line in enumerate(text.split("\n"), 1):
    if '"SQQQ"' in line and line.strip().startswith("return"):
        own = min((f for f in fns if f[0] <= i <= f[1]), key=lambda f: f[1] - f[0])
        sites.append((i, own[2], line.strip()))
sleeves = sorted({("T10" if s[1].startswith("t10") else "T11" if "t11" in s[1] else "S2")
                  for s in sites})
for i, fn, ln in sites:
    src(f"sqqq_site_{SP}:{i}", SP, fn, ln)
src("sqqq_position_sites", SP, str(len(sites)), prompt="4")
src("sqqq_sleeves", SP, ",".join(sleeves), prompt="3")
dis("sqqq_sites", "four sites across three sleeves",
    f"{len(sites)} sites across {len(sleeves)} sleeves", SP, "figure",
    "the sites returning an SQQQ position are " +
    ", ".join(f"{fn} at line {i}" for i, fn, _ in sites))

# ---- the state machine and the lag record -------------------------------------
REG = "docs/DECISIONS-v3.md"
src("s3_vote_threshold", REG, "3 of 4",
    "register 6.7, informed rather than closed, literal at config.S3_VOTE_THRESHOLD")
LA = "outputs/session-15/lag-anomaly.csv"
lag = {r["lag"]: r for r in rows(LA) if r["table"] == "lag_levels" and r["convention"] == "c2c"}
for k in ("1.0", "2.0", "3.0"):
    src(f"lag_{k}_ann_return", LA, lag[k]["ann_return"])
    src(f"lag_{k}_sharpe_lo", LA, lag[k]["sharpe_lo"])
dis("lag_mechanism",
    "session 15 located the mechanism of the dip-buying signal firing roughly one "
    "session early in fast crashes so the long side enters early and the short side late",
    "the register's corrections list item 12 records an execution-lag sensitivity in "
    "which annualised return improves under one extra session of lag while the "
    "Lo-corrected Sharpe degrades, and records that no dedicated lookahead test has run",
    f"{REG} and {LA}", "unsupported claim",
    "session 15's lag-anomaly measurement carries lag levels and per-instrument, "
    "per-sleeve and per-year differences. It does not locate a dip-buying mechanism, "
    "does not separate fast crashes from other episodes, and does not establish that "
    "the long side enters early while the short side enters late. The prediction states "
    "what the record carries")

# ---- the sealed span ------------------------------------------------------------
MT = "outputs/session-00e/manifest-truncated.csv"
ends = sorted({r["new_last_date"] for r in rows(MT)})
src("data_end", MT, ends[0] if len(ends) == 1 else ",".join(ends),
    f"across {len(rows(MT))} frozen inputs")
src("holdout_boundary", REG, "2021-08-01", "register 2.10, closed and untouched")
src("primary_window_sessions", "outputs/session-25/figures/equity-curve.csv", "2472",
    "rows in the emitted series, matching the standing positive control")
dis("holdout_session_count", "the session count against the primary window's 2,472",
    "not established", REG, "not computed",
    "register 2.10 records that no post-boundary quantity has been computed anywhere, "
    "and counting sessions inside the sealed span is a post-boundary quantity. The span "
    "endpoints and the primary window's count are stated and the holdout count is left "
    "for the read")
dis("tlt_2022", "TLT had its worst year in decades in 2022", "not in any emitted file",
    "", "external fact",
    "no committed CSV carries a TLT annual return. The statement is carried in the "
    "prediction as an external premise and labelled as one, since P5 rests on it")

fn = ["item", "source_file", "literal_value", "prompt_value", "note"]
with open(OUT/"prediction-sources.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn); w.writeheader(); w.writerows(S)
fn2 = ["item", "prompt_value", "source_value", "source_file", "kind", "note"]
with open(OUT/"prompt-disagreements.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fn2); w.writeheader(); w.writerows(D)
print(f"wrote prediction-sources.csv, {len(S)} figures")
print(f"wrote prompt-disagreements.csv, {len(D)} items")
for d in D: print(f"  {d['kind']:18s} {d['item']}")
