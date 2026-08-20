"""Session 22 phases D and E.

WINDOWS, STATED BEFORE RUNNING AND CHOSEN FOR COVERAGE.
  120, 252 and 504 sessions, being twice session 21's 60, about one trading
  year, and about two. None is chosen for its result.
"""
from __future__ import annotations
import ast, csv, math, re, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT=Path("/Users/GualyCr/Downloads/tactical-allocation"); sys.path.insert(0,str(ROOT))
import scripts.s13_backtest as bt   # noqa: E402
import scripts.s14_common as C      # noqa: E402
import scripts.s15_lines as L       # noqa: E402
import src.sleeves as SL            # noqa: E402
from src import config              # noqa: E402
OUT=ROOT/"outputs/session-22"; ANN=math.sqrt(252.0); WINDOWS=(120,252,504)
t0=time.time()

def sharpes(x):
    mu,sd=x.mean(),x.std(ddof=1)
    if sd==0: return float("nan"),float("nan")
    naive=mu/sd*ANN; xc=x-mu; den=float(np.dot(xc,xc)); q=252
    acf=sum((q-k)*float(np.dot(xc[:-k],xc[k:]))/den for k in range(1,q))
    sc=q+2.0*acf
    return naive,(mu/sd)*q/math.sqrt(sc) if sc>0 else float("nan")

env=C.build_env(verbose=False)
cal,sigs,o2o,cap_fn=env["cal"],env["sigs"],env["o2o"],env["cap_fn"]
sig=sigs["realized"]; LINES=L.make_lines(cal)
i0=int(np.searchsorted(cal.to_numpy(),np.datetime64(C.PRIMARY_START)))
def run(rws): return bt.run_account(sig["sig"],o2o,rws,C.ANCHOR,
    commission_fn=C.ARMS[C.CANONICAL_ARM],slip_fn=C.slip_class_premium(),cap_fn=cap_fn)
acc_s=run(sig["rows"]); acc_q=run(LINES["buy_hold_QQQ"][0](o2o,sig["rows"],i0))
rf_all=bt.rf_per_session(acc_s["daily"].index)
idx=acc_s["daily"].index[acc_s["daily"].index>=C.PRIMARY_START]
rs=acc_s["daily"]["ret"].reindex(idx).fillna(0.0).to_numpy()
rq=acc_q["daily"]["ret"].reindex(idx).fillna(0.0).to_numpy()
rf=rf_all.reindex(idx).fillna(0.0).to_numpy()
ys,yq=rs-rf,rq-rf
X=np.column_stack([np.ones(len(yq)),yq]); b_full,*_=np.linalg.lstsq(X,ys,rcond=None)
beta_bar=float(b_full[1])
lad=pd.read_csv(ROOT/"outputs/session-20/rebuilt/metrics-full.csv")
lad=lad[(lad.table=="metrics")&(lad.panel=="realized")&(lad.convention=="o2o")
        &(lad.window=="primary")]
rows=[]
rows.append({"table":"windows","item":"stated_before_running",
             "note":"120, 252 and 504 sessions, being twice session 21's 60, about one "
                    "trading year, and about two, chosen for coverage not for result"})
rows.append({"table":"windows","item":"session21_window","value":60,
             "note":"config.CRASH_HORIZON_SESSIONS, registered for crash detection "
                    "rather than for beta estimation"})
rows.append({"table":"implementability","item":"exposure_matched_line",
             "note":"beta is estimated from the strategy's own realised returns, so the "
                    "line is not implementable and enters the paper as a decomposition "
                    "rather than as an ex-ante benchmark"})
for Wn in WINDOWS:
    bt_=np.full(len(ys),np.nan)
    for i in range(Wn,len(ys)):
        xs,ysl=yq[i-Wn:i],ys[i-Wn:i]
        v=float(((xs-xs.mean())**2).sum())
        if v>0: bt_[i]=float(((xs-xs.mean())*(ysl-ysl.mean())).sum())/v
    ok=~np.isnan(bt_)
    for k,v in (("beta_mean",bt_[ok].mean()),("beta_sd",bt_[ok].std(ddof=1)),
                ("beta_min",bt_[ok].min()),("beta_max",bt_[ok].max()),
                ("share_above_1.0",(bt_[ok]>1.0).mean()),
                ("share_above_1.7",(bt_[ok]>1.7).mean()),
                ("beta_range",bt_[ok].max()-bt_[ok].min())):
        rows.append({"table":"rolling","window":Wn,"item":k,"value":float(v)})
    bl=np.roll(bt_,1); bl[0]=np.nan; m=~np.isnan(bl)
    stat=beta_bar*yq[m]; tim=(bl[m]-beta_bar)*yq[m]; res=ys[m]-stat-tim
    for nm,arr in (("static_exposure",stat),("timing",tim),("residual",res)):
        nv,lo=sharpes(arr)
        rows.append({"table":"timing","window":Wn,"item":nm+"_ann_contribution",
                     "value":float(arr.mean()*252.0)})
        rows.append({"table":"timing","window":Wn,"item":nm+"_sharpe_naive","value":nv})
        rows.append({"table":"timing","window":Wn,"item":nm+"_sharpe_lo","value":lo})
    bser=pd.Series(bl,index=idx).clip(lower=0.0)
    seq={int(np.searchsorted(cal.to_numpy(),np.datetime64(d))):{"QQQ":float(bser.iloc[i])}
         for i,d in enumerate(idx) if not np.isnan(bl[i])}
    a=run(L.rows_from_weights(seq,always_emit=True))
    rm=a["daily"]["ret"].reindex(idx).dropna()
    mm=L.standalone_metrics(rm,a["daily"]["nav"],a["orders"])
    nvm,lom=sharpes((rm-rf_all.reindex(rm.index).fillna(0.0)).to_numpy())
    for k,v in (("ann_return",mm["ann_return"]),("ann_vol",mm["ann_vol"]),
                ("sharpe_naive",nvm),("sharpe_lo",lom),
                ("ann_turnover",mm["ann_turnover"])):
        rows.append({"table":"exposure_matched","window":Wn,"item":k,"value":float(v)})
    for metric,val in (("sharpe_naive",nvm),("sharpe_lo",lom)):
        rows.append({"table":"exposure_matched","window":Wn,
                     "item":f"ladder_rank_{metric}",
                     "value":int((lad[metric]>val).sum())+1,
                     "note":"of thirteen, being the twelve rebuilt ladder rows plus this line"})
    print(f"  W={Wn:<4} beta mean {bt_[ok].mean():+.4f} sd {bt_[ok].std(ddof=1):.4f} "
          f"range {bt_[ok].min():+.4f} to {bt_[ok].max():+.4f} | timing "
          f"{tim.mean()*252:+.6f} | matched naive {nvm:.6f} turn {mm['ann_turnover']:.2f}",
          flush=True)
sd60=1.164612
sds=[r["value"] for r in rows if r["table"]=="rolling" and r["item"]=="beta_sd"]
rows.append({"table":"verdict","item":"beta_range_narrows_with_window",
             "value":int(all(sds[i]>=sds[i+1] for i in range(len(sds)-1))),
             "note":f"session 21 measured a standard deviation of {sd60} at window 60. "
                    f"A monotone decline across 120, 252 and 504 marks the extremes as "
                    f"small-sample estimation noise rather than real exposure"})
tims=[r["value"] for r in rows if r["table"]=="timing" and r["item"]=="timing_ann_contribution"]
rows.append({"table":"verdict","item":"timing_stability",
             "note":f"session 21 measured +0.011293 at window 60. Across the three "
                    f"windows the timing contribution reads "
                    f"{' '.join(f'{v:+.6f}' for v in tims)}"})
with open(OUT/"beta-window-sensitivity.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","window","item","value","note"],
                     extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(f"wrote {OUT/'beta-window-sensitivity.csv'} with {len(rows)} rows")

# ---------------- phase E ----------------
er=[]
src=(ROOT/"src"/"sleeves.py").read_text(); lines=src.split("\n")
tree=ast.parse(src)
assign={}
for n in ast.walk(tree):
    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
        v=[c.value for c in ast.walk(n.value) if isinstance(c,ast.Constant)
           and isinstance(c.value,str) and re.fullmatch(r"[A-Z]{2,5}",c.value)]
        if v: assign[n.targets[0].id]=v
for fn in [n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)]:
    for n in ast.walk(fn):
        if isinstance(n,ast.Return) and isinstance(n.value,ast.Dict):
            keys=[]
            for k in n.value.keys:
                if isinstance(k,ast.Constant): keys.append(k.value)
                elif isinstance(k,ast.Name): keys.append(f"<{k.id}>")
            names=[x for k in n.value.keys if isinstance(k,ast.Name)
                   for x in assign.get(k.id,[])]
            if any(x in ("SVIX","UVIX") for x in names):
                var=[k.id for k in n.value.keys if isinstance(k,ast.Name)][0]
                er.append({"table":"terminal","item":f"{fn.name}:L{n.lineno}",
                           "note":lines[n.lineno-1].strip(),
                           "note2":f"variable {var} resolves to {assign.get(var)}"})
er.append({"table":"engine_path","item":"available",
           "note":"scripts/s13_backtest.py:344 State.available reads self.sig.avail.get(t) "
                  "and returns False when the ticker is absent from the panel, so the "
                  "switch selects the fallback and the dictionary written into the "
                  "weight map never names SVIX or UVIX"})
er.append({"table":"engine_path","item":"renormalisation",
           "note":"there is none, and none is needed. The switch chooses the ticker "
                  "BEFORE the dictionary is built, so the returned weights are the "
                  "written weights with the fallback ticker substituted. No weight is "
                  "dropped, no balance goes to cash, and no renormalisation occurs"})
env2=env; panels=env2["panels"]
i0b=int(np.searchsorted(cal.to_numpy(),np.datetime64(C.PRIMARY_START)))
cnt={"t10_vol_short":0,"s3_vol":0}; held={"SVXY":0,"UVXY":0}
for r in sig["rows"]:
    if r["i"]<i0b: continue
    s10=r["sleeves"].get("T10"); s3=r["sleeves"].get("S3")
    if s10 and set(s10)=={"TECL","SOXL","SVXY"}:
        cnt["t10_vol_short"]+=1; held["SVXY"]+=1
    if s3 and set(s3)=={"UVXY"}:
        cnt["s3_vol"]+=1; held["UVXY"]+=1
for k,v in cnt.items():
    er.append({"table":"firing","item":k,"value":v,
               "note":"sessions across the primary window under the canonical"})
for k,v in held.items():
    er.append({"table":"realised_holding","item":k,"value":v,
               "note":"the ticker actually held on those sessions"})
for t in ("SVIX","UVIX"):
    er.append({"table":"loader","item":f"{t}_in_bt_LEVERED",
               "value":int(t in bt.LEVERED),
               "note":"bt.LEVERED is not modified by this session"})
    for arm in ("realized","synthetic"):
        er.append({"table":"panel","item":f"{t}_{arm}",
                   "value":int(t in panels[arm].frames)})
    p=ROOT/f"data/raw/etf/{t}.parquet"
    if p.exists():
        d=pd.read_parquet(p); ix=pd.to_datetime(d.index)
        er.append({"table":"listing","item":t,"note":str(ix.min().date()),
                   "note2":"against the holdout span beginning 2021-08-01, so the "
                           "listing falls inside the holdout"})
er.append({"table":"disposition","item":"if_added_to_loader",
           "note":"adding either ticker to bt.LEVERED would make State.available return "
                  "True from its listing date, the switch would select it, and the "
                  "branch would execute for the first time inside the single holdout "
                  "read. The loader is left unchanged and the limitation is disclosed"})
with open(OUT/"volatility-terminal-resolution.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=["table","item","value","note","note2"],
                     extrasaction="ignore")
    w.writeheader(); w.writerows(er)
print(f"E terminals {cnt}, realised holdings {held}")
print(f"wrote {OUT/'volatility-terminal-resolution.csv'} with {len(er)} rows")
print(f"phases D and E {time.time()-t0:.1f}s")
