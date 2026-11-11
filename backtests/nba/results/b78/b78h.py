"""B78h - look-ahead haircut on the AggProj-era archive (Gemini Q12 #2, simplified to the part we can calibrate).
The archive holds FINAL values. Live pulls show 26% of late-game 'new starters' (listed starter, <24 min over last 3) and ~10-18% of
first-tip ones were not yet flagged at our last pre-lock pull; their projection then was 0.72x (LS) / 0.85x (AggProj) of the final.
 hair  : randomly revert that share to the pre-news view (bench status -> needs 18+ min to be eligible; projection scaled down)
 noNS  : bound - no late-game new starter is usable at all
Lineups are built on the degraded view and scored on actuals. Usage: python3 b78h.py <out.csv> [limit]"""
import pandas as pd, numpy as np, sys, time, warnings
warnings.filterwarnings('ignore')
import b78a as B
M=B.M
CFG={'V0':('blend','tiers'),'LS_free':('ls','none'),'CAL_free':('cal','none'),'CAL_c4o6':('cal','c4')}
def run_date(dt):
    t0=time.time()
    a=M[M.date==dt]; games=int(a.main_games.iloc[0]) if len(a) and a.main_games.notna().any() else 0
    if games<4: return None
    ref=B.ref_contests(dt)
    if ref is None or not np.isfinite(ref.mu_ls) or ref.proxy_ls<=0: return None
    d=a[(a.ls_proj>0)&(a.stat!=4)].copy(); d=d[(d.stat==1)|(d.min3>=18)].reset_index(drop=True)
    if len(d)<25 or d.actual.sum()==0 or not ((d['agg']>0).mean()>0.5): return None
    d['aggp']=np.where(d['agg']>0,d['agg'],d.ls_proj); d['cal']=-0.26+0.136*d.ls_proj+0.856*d.aggp
    d['up']=(d['ceil']-d.ls_proj).clip(lower=0).fillna(0); d['l5f']=d.l5.fillna(d.ls_proj)
    po=d.pown.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95) if po.sum()>0 else po
    S=B.Slate(d,games); n=S.n; act=d.actual.values; own=d.own.values; tip=d.tip.values
    late=tip>=30; ns=(d.stat.values==1)&~(d.min3.values>=24)
    rng=np.random.default_rng(int(dt.replace('-','')))
    out=dict(date=dt,games=games,n=n,mu=ref.mu_ls+B.MU_OFF,sd=B.KAPPA*ref.proxy_ls,ns_late=int((ns&late).sum()),ns_early=int((ns&~late).sum()))
    for sc in ('fin','hair','noNS'):
        ls=d.ls_proj.values.copy(); ag=d.aggp.values.copy(); up=d.up.values.copy(); ban=np.zeros(n,bool); o=own.copy()
        if sc=='hair':
            f=ns&(rng.random(n)<np.where(late,0.26,0.10)); ls[f]*=0.72; ag[f]*=0.85; up[f]*=0.72; o[f]*=0.5; ban=f&~(d.min3.values>=18); out['flips']=int(f.sum()); out['flips_banned']=int(ban.sum())
        if sc=='noNS': ban=ns&late
        P={'ls':ls,'cal':-0.26+0.136*ls+0.856*ag,'blend':0.7*ls+0.3*d.l5f.values}
        for name,(pr,expo) in CFG.items():
            if expo=='tiers': cap=np.where(o>=35,3,np.where(o>=15,2,1)); ov=4 if games>=6 else 5
            else: cap=np.full(n,3 if expo=='none' else 4); ov=6
            v=np.zeros(S.N); v[:n]=(o<10); extra0=[(v,1)]
            built=[];cnt=np.zeros(n,int)
            for j in range(4):
                ids=S.solve(P[pr]+0.1*up,list(extra0)+[(S.vec(L),ov) for L in built],ban=np.where((cnt>=cap)|ban)[0])
                if ids is None: break
                built.append(ids); cnt[ids]+=1; out[f'{sc}_{name}_s{j+1}']=float(act[ids].sum())
            out[f'{sc}_{name}_ns']=float(np.mean([(ns&late)[L].sum() for L in built])) if built else np.nan
    out['secs']=round(time.time()-t0,1)
    return out
if __name__=='__main__':
    outf=sys.argv[1]; lim=int(sys.argv[2]) if len(sys.argv)>2 else 0
    dates=sorted(M.date.unique())
    if lim: dates=dates[-lim:]
    rows=[]; t=time.time()
    for i,dt in enumerate(dates):
        r=run_date(dt)
        if r: rows.append(r)
        if i%20==19: pd.DataFrame(rows).to_csv(outf,index=False); print(i+1,len(rows),round(time.time()-t),'s',flush=True)
    pd.DataFrame(rows).to_csv(outf,index=False); print('DONE',len(rows),round(time.time()-t),'s')
