"""Gemini Q2 gate part 2 + look-ahead haircut. On every live slate: build 4 lineups from the LAST PRE-LOCK pull and (where we hold
the final record) from LineStar's FINAL post-lock data, same structure, for pure LS / CAL / blend. Score on actuals vs the real field."""
import pandas as pd, numpy as np, warnings, io, contextlib
warnings.filterwarnings('ignore'); pd.set_option('display.width',250); pd.set_option('display.max_columns',60)
with contextlib.redirect_stdout(io.StringIO()): import live_build as LB
A=pd.read_pickle('live_vs_final.pkl'); T=pd.read_pickle('live_pulls.pkl'); M=pd.read_pickle('master.pkl'); k=LB.k
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
CF={'v1.3':('blend','tiers'),'LS_free':('ls','free'),'CAL_free':('cal','free'),'AGG_free':('agg','free'),'LS_c4':('ls','c4'),'CAL_c4':('cal','c4')}
rows=[]
for dt in sorted(A.date.unique())+['2026-11-10']:
    if dt=='2026-11-10':
        L=T[(T.date==dt)&(T.pull=='1545')&(T.in_main==1)].copy(); L['kk']=L.name.map(k)
        f=G[G.game_date<dt].groupby('k').agg(l5=('fd_pts',lambda x:x.tail(5).mean()),min3=('minutes',lambda x:x.tail(3).mean())); L=L.merge(f,left_on='kk',right_index=True,how='left')
        a=L.rename(columns={'name':'name_live','ls_proj':'ls_proj_live','agg':'agg_live','stat':'stat_live','pown':'pown_live'}); a['stat_fin']=1; a['actual']=np.nan; a['ceil_fin']=np.nan
        fdout=set(map(k,['Tyler Herro',"Kel'el Ware",'Tristan da Silva','Max Christie'])); hasfin=False
    else:
        a=A[A.date==dt].copy(); a['kk']=a.name_live.map(k); fdout=LB.FDOUT.get(dt,set()); hasfin=True
        a=a.merge(M[M.date==dt][['salary_id','ceil']].rename(columns={'ceil':'ceil_fin'}),on='salary_id',how='left')
    games=int(T[T.date==dt].main_games.iloc[0])
    if dt in CSV:
        c=pd.read_csv(ATT+CSV[dt],encoding='utf-8-sig',low_memory=False); pts=np.sort(pd.to_numeric(c[c.EntryId.notna()].Points,errors='coerce').dropna().values); mu,sd=pts.mean(),pts.std()
        cashline=pd.to_numeric(c[c.EntryId.notna()&(pd.to_numeric(c.Won.astype(str).str.replace('[$,]','',regex=True),errors='coerce')>0)].Points).min()
        p=c[c.Player.notna()].copy(); p['kk']=p.Player.str.replace(r' \(.*','',regex=True).map(k); fp=pd.to_numeric(p.set_index('kk').FPTS)
        if dt=='2026-11-10': a['actual']=a.kk.map(fp).fillna(0)
        pct=lambda x:100*np.searchsorted(pts,x,side='left')/len(pts)
    else:
        mu,sd=LB.field(dt); zp=np.load('z_pool.npy'); pct=lambda x:100*np.searchsorted(zp,(x-mu)/sd,side='left')/len(zp); cashline=mu+0.72*sd
    a['l5f']=a.l5.fillna(a.ls_proj_live)
    row=dict(date=dt,games=games)
    for era in (['pre','fin'] if hasfin else ['pre']):
        if era=='pre':
            d=a[(a.ls_proj_live>0)&(a.stat_live!=4)&~a.kk.isin(fdout)&((a.stat_live==1)|(a.min3>=18))].reset_index(drop=True)
            ls=d.ls_proj_live.values; ag=np.where(d.agg_live>0,d.agg_live,ls); po=d.pown_live.fillna(0); ce=d.ceil.values
        else:
            d=a[(a.ls_proj_fin>0)&(a.stat_fin!=4)&((a.stat_fin==1)|(a.min3>=18))].reset_index(drop=True)
            ls=d.ls_proj_fin.values; ag=np.where(d.agg_fin>0,d.agg_fin,ls); po=d.pown_fin.fillna(0); ce=d.ceil_fin.fillna(d.ceil).values
        d['own']=(po*900/po.sum()).clip(upper=95); up=np.nan_to_num(np.clip(ce-ls,0,None))
        P={'ls':ls,'agg':ag,'cal':-0.26+0.136*ls+0.856*ag,'blend':0.7*ls+0.3*d.l5.fillna(pd.Series(ls)).values}
        act=d.actual.where(d.stat_fin!=4,0).values
        for nm,(pr,mode) in CF.items():
            Ls=buildx(d,P[pr]+0.1*up,games,mode); sc=[float(act[L].sum()) for L in Ls]; pc=[pct(x) for x in sc]
            key=f'{era}_{nm}'; row[key+'_fp']=np.mean(sc); row[key+'_pct']=np.mean(pc); row[key+'_cash']=sum(x>=cashline for x in sc); row[key+'_t10']=sum(q>=90 for q in pc)
            row[key+'_dead']=sum(int((d.stat_fin.values[L]==4).sum()) for L in Ls); row[key+'_sc']=' '.join(f'{x:.0f}' for x in sc)
    rows.append(row); print(dt,'done',flush=True)
Rr=pd.DataFrame(rows); Rr.to_csv('gate_q2b_results.csv',index=False)
n=len(Rr)
print('\nPRE-LOCK builds, per slate mean FP per lineup:'); print(Rr[['date','games']+[f'pre_{c}_fp' for c in CF]].round(1).to_string(index=False))
print('PRE-LOCK builds, per slate mean field percentile:'); print(Rr[['date']+[f'pre_{c}_pct' for c in CF]].round(1).to_string(index=False))
print('\nTOTALS pre-lock (8 slates, 32 lineups each):')
for c in CF: print(f'  {c:9} FP {Rr[f"pre_{c}_fp"].mean():.1f}  pct {Rr[f"pre_{c}_pct"].mean():.1f}  cashes {int(Rr[f"pre_{c}_cash"].sum())}/32  top10 {int(Rr[f"pre_{c}_t10"].sum())}  dead spots {int(Rr[f"pre_{c}_dead"].sum())}')
def pr(a,b,lab):
    d=Rr[a+'_fp']-Rr[b+'_fp']; q=Rr[a+'_pct']-Rr[b+'_pct']; ok=d.notna()
    print(f'  {lab}: {d[ok].mean():+.1f} FP/lineup (se {d[ok].std()/np.sqrt(ok.sum()):.1f}), pct {q[ok].mean():+.1f} (se {q[ok].std()/np.sqrt(ok.sum()):.1f}), better on {int((d[ok]>0).sum())} of {int(ok.sum())} slates')
print('\nPAIRED, pre-lock:'); pr('pre_CAL_free','pre_LS_free','CAL - pure LS, max 3 of 4'); pr('pre_CAL_c4','pre_LS_c4','CAL - pure LS, no exposure cap'); pr('pre_AGG_free','pre_LS_free','AggProj alone - LS, max 3 of 4'); pr('pre_CAL_free','pre_v1.3','candidate - v1.3'); pr('pre_CAL_c4','pre_CAL_free','no cap - max 3 of 4 (CAL)')
F=Rr[Rr['fin_CAL_free_fp'].notna()] if 'fin_CAL_free_fp' in Rr else None
if F is not None:
    print('\nLOOK-AHEAD HAIRCUT (same 7 slates): final-data build vs pre-lock build')
    for c in CF:
        d=F[f'fin_{c}_fp']-F[f'pre_{c}_fp']; q=F[f'fin_{c}_pct']-F[f'pre_{c}_pct']
        print(f'  {c:9} final {F[f"fin_{c}_fp"].mean():.1f} FP / pct {F[f"fin_{c}_pct"].mean():.1f} / cashes {int(F[f"fin_{c}_cash"].sum())}/28 | pre-lock {F[f"pre_{c}_fp"].mean():.1f} / {F[f"pre_{c}_pct"].mean():.1f} / {int(F[f"pre_{c}_cash"].sum())}/28 | haircut {d.mean():+.1f} FP (se {d.std()/np.sqrt(len(d)):.1f}), {q.mean():+.1f} pct (se {q.std()/np.sqrt(len(q)):.1f})')
    print('  paired on FINAL data: ',end=''); Rr2=Rr; pr('fin_CAL_free','fin_LS_free','CAL - LS (final data)')
