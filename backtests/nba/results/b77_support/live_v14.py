"""No-look-ahead check of the v1.4 candidate: rebuild from the LAST PRE-LOCK pull on every live slate, score on the real field."""
import pandas as pd, numpy as np, warnings, io, contextlib, sys, os, re
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
with contextlib.redirect_stdout(io.StringIO()): import live_build as LB
A=pd.read_pickle('live_vs_final.pkl'); T=pd.read_pickle('live_pulls.pkl'); k=LB.k
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/'; ATT='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'
CSV={'2026-11-04':'08ad4fb1-136227-281386492.csv','2026-11-05':'d62a48dc-136288-281415467.csv','2026-11-06':'23632d04-136333-281428632.csv','2026-11-07':'79523267-136378-281443029.csv','2026-11-09':'86ee8b01-136475-281475577.csv','2026-11-10':'eb8ea2d9-136535-281491886.csv'}
def buildx(d,obj,games,mode):
    n=len(d); own=d.own.values
    if mode=='tiers': cap=np.where(own>=35,3,np.where(own>=15,2,1)); ov=4 if games>=6 else (5 if games>=4 else 8)
    elif mode=='free': cap=np.full(n,3); ov=6 if games>=4 else 8
    else: cap=np.full(n,4); ov=6 if games>=4 else 8
    contra=((own<10).astype(float),1 if games>=4 else 2); built=[]; cnt=np.zeros(n,int)
    for j in range(4):
        ids=LB.solve(d,obj,[contra]+[(np.isin(np.arange(n),L).astype(float),ov) for L in built],ban=np.where(cnt>=cap)[0])
        if ids is None: break
        built.append(ids); cnt[ids]+=1
    return built
G=pd.concat([pd.read_csv(R+f'nba_player_games_{s}.csv') for s in ['2025-26','2026-27']]); G=G[~G.did_not_play.astype(str).eq('True')&(G.minutes>0)].copy(); G['k']=G.athlete_display_name.map(k); G=G.sort_values('game_date')
rows=[]
dates=sorted(A.date.unique())+['2026-11-10']
for dt in dates:
    if dt=='2026-11-10':
        L=T[(T.date==dt)&(T.pull=='1545')&(T.in_main==1)].copy(); L['kk']=L.name.map(k)
        f=G[G.game_date<dt].groupby('k').agg(l5=('fd_pts',lambda x:x.tail(5).mean()),min3=('minutes',lambda x:x.tail(3).mean())); L=L.merge(f,left_on='kk',right_index=True,how='left')
        a=L.rename(columns={'name':'name_live','ls_proj':'ls_proj_live','agg':'agg_live','stat':'stat_live','pown':'pown_live'}); a['stat_fin']=1; a['actual']=np.nan
        fdout=set(map(k,['Tyler Herro',"Kel'el Ware",'Tristan da Silva','Max Christie']))
    else:
        a=A[A.date==dt].copy(); a['kk']=a.name_live.map(k); fdout=LB.FDOUT.get(dt,set())
    games=int(T[T.date==dt].main_games.iloc[0])
    if dt in CSV:
        c=pd.read_csv(ATT+CSV[dt],encoding='utf-8-sig',low_memory=False); pts=pd.to_numeric(c[c.EntryId.notna()].Points,errors='coerce').dropna().values; pts=np.sort(pts); mu,sd=pts.mean(),pts.std(); cashline=pd.to_numeric(c[c.EntryId.notna()&(pd.to_numeric(c.Won.astype(str).str.replace('[$,]','',regex=True),errors='coerce')>0)].Points).min()
        p=c[c.Player.notna()].copy(); p['kk']=p.Player.str.replace(r' \(.*','',regex=True).map(k); fp=pd.to_numeric(p.set_index('kk').FPTS)
        if dt=='2026-11-10': a['actual']=a.kk.map(fp).fillna(0)
        pct=lambda x:100*np.searchsorted(pts,x,side='left')/len(pts)
    else:
        mu,sd=LB.field(dt); zp=np.load('z_pool.npy'); pct=lambda x:100*np.searchsorted(zp,(x-mu)/sd,side='left')/len(zp)
    a['l5f']=a.l5.fillna(a.ls_proj_live)
    d=a[(a.ls_proj_live>0)&(a.stat_live!=4)&~a.kk.isin(fdout)&((a.stat_live==1)|(a.min3>=18))].reset_index(drop=True)
    po=d.pown_live.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95); up=(d.ceil-d.ls_proj_live).clip(lower=0).fillna(0).values
    aggl=np.where(d.agg_live>0,d.agg_live,d.ls_proj_live); cal=-0.26+0.136*d.ls_proj_live.values+0.856*aggl; blend=0.7*d.ls_proj_live.values+0.3*d.l5f.values
    act=d.actual.where(d.stat_fin!=4,0).values
    row=dict(date=dt,games=games)
    for nm,(pr,mode) in {'v1.3':(blend,'tiers'),'CAL_tiers':(cal,'tiers'),'v1.4cand':(cal,'free'),'CAL_c4o6':(cal,'c4')}.items():
        Ls=buildx(d,pr+0.1*up,games,mode); sc=[float(act[L].sum()) for L in Ls]; pc=[pct(x) for x in sc]
        row[nm]=' '.join(f'{x:.0f}' for x in sc); row[nm+'_pct']=' '.join(f'{x:.0f}' for x in pc); row[nm+'_mean']=np.mean(sc); row[nm+'_mpct']=np.mean(pc); row[nm+'_cash']=sum((x-mu)/sd>=0.72 for x in sc) if dt not in CSV else sum(x>=cashline for x in sc); row[nm+'_t10']=sum(p>=90 for p in pc)
    rows.append(row)
Rr=pd.DataFrame(rows)
for nm in ['v1.3','CAL_tiers','v1.4cand','CAL_c4o6']:
    print(f'\n{nm}:'); print(Rr[['date','games',nm,nm+'_pct',nm+'_mean',nm+'_mpct',nm+'_cash',nm+'_t10']].round(1).to_string(index=False))
    print(f'  TOTAL {nm}: mean FP {Rr[nm+"_mean"].mean():.1f} | mean percentile {Rr[nm+"_mpct"].mean():.1f} | cashes {int(Rr[nm+"_cash"].sum())} of {4*len(Rr)} | top-10% {int(Rr[nm+"_t10"].sum())}')
d1=Rr['v1.4cand_mean']-Rr['v1.3_mean']; d2=Rr['v1.4cand_mpct']-Rr['v1.3_mpct']
print(f'\npaired v1.4cand - v1.3: {d1.mean():+.1f} FP per lineup (se {d1.std()/np.sqrt(len(d1)):.1f}); mean percentile {d2.mean():+.1f} (se {d2.std()/np.sqrt(len(d2)):.1f}); slates better {int((d1>0).sum())} of {len(d1)}')
Rr.to_csv('live_v14_results.csv',index=False)
