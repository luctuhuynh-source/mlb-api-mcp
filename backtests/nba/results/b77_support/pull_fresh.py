"""Value of pull freshness: same slate, same rules, earlier vs later pre-lock LineStar pull."""
import pandas as pd, numpy as np, warnings, io, contextlib, sys, re
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
with contextlib.redirect_stdout(io.StringIO()):
    import live_build as LB, live_v14 as V
T=pd.read_pickle('live_pulls.pkl'); M=pd.read_pickle('master.pkl'); k=LB.k
rows=[]
for dt in ['2026-10-31','2026-11-04','2026-11-05','2026-11-06','2026-11-07','2026-11-09']:
    F=M[(M.date==dt)&(M.in_main==1)][['salary_id','stat','actual','l5','min3']].rename(columns={'stat':'stat_fin'})
    games=int(T[T.date==dt].main_games.iloc[0]); fdout=LB.FDOUT.get(dt,set())
    pulls=sorted(T[(T.date==dt)].pull.unique()); pulls=[pulls[0],pulls[-1]]
    for pl in pulls:
        a=T[(T.date==dt)&(T.pull==pl)&(T.in_main==1)].merge(F,on='salary_id'); a['kk']=a.name.map(k); a['l5f']=a.l5.fillna(a.ls_proj)
        d=a[(a.ls_proj>0)&(a.stat!=4)&~a.kk.isin(fdout)&((a.stat==1)|(a.min3>=18))].reset_index(drop=True)
        po=d.pown.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95); up=(d.ceil-d.ls_proj).clip(lower=0).fillna(0).values
        aggl=np.where(d['agg']>0,d['agg'],d.ls_proj); cal=-0.26+0.136*d.ls_proj.values+0.856*aggl; blend=0.7*d.ls_proj.values+0.3*d.l5f.values
        act=d.actual.where(d.stat_fin!=4,0).values
        for nm,(pr,mode) in {'v1.3':(blend,'tiers'),'v1.4cand':(cal,'free')}.items():
            Ls=V.buildx(d,pr+0.1*up,games,mode); sc=[float(act[L].sum()) for L in Ls]
            rows.append(dict(date=dt,pull=pl,cfg=nm,mean=np.mean(sc),dead=sum(int((d.stat_fin.values[L]==4).sum()) for L in Ls)))
R=pd.DataFrame(rows); R['which']=R.groupby(['date','cfg']).cumcount().map({0:'first',1:'last'})
print(R.pivot_table(index=['date'],columns=['cfg','which'],values='mean').round(1).to_string())
p=R.pivot_table(index=['date','cfg'],columns='which',values='mean'); p['d']=p['last']-p['first']
print(p.groupby('cfg').d.agg(['mean','std','count']).round(2)); print('dead roster spots by pull:',R.groupby('which').dead.sum().to_dict())
print(R[R.date=='2026-10-31'])
