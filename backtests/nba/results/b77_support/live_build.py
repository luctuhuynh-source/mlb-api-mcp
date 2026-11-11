"""Live-window test (no look-ahead): rebuild 4 lineups from the last pre-lock LineStar pull under v1.3 structure with
each projection source, score with actuals, and price late swap (frozen vs rule-17 swap vs full re-optimisation of unlocked slots)."""
import pandas as pd, numpy as np, re, unicodedata, warnings, sys
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy import sparse
warnings.filterwarnings('ignore'); pd.set_option('display.width',250); pd.set_option('display.max_columns',60)
A=pd.read_pickle('live_vs_final.pkl')   # last pull merged with final, dates < 11/10
T=pd.read_pickle('live_pulls.pkl'); M=pd.read_pickle('master.pkl'); C=pd.read_csv('hist_contests_mu.csv'); FC=pd.read_csv('field_cal.csv')
ATT='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'
def k(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); s=re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s); return re.sub(r'[^a-z]','',s)
FDOUT={}
for d,f in {'2026-11-04':'c9ce2675-FanDuel-NBA-2026_PST-11_PST-04_PST-136227-players-list-2.csv','2026-11-05':'02b93fb6-FanDuel-NBA-2026_PST-11_PST-05_PST-136288-players-list.csv',
            '2026-11-06':'b4302679-FanDuel-NBA-2026_PST-11_PST-06_PST-136333-players-list-1.csv','2026-11-07':'2ed186ab-FanDuel-NBA-2026_PST-11_PST-07_PST-136378-players-list-2.csv'}.items():
    p=pd.read_csv(ATT+f); FDOUT[d]=set(p[p['Injury Indicator'].isin(['O','Q','D'])].Nickname.map(k))
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED=[1,1,1,1,1,1,1,2]
def slots(pos):
    s=set(str(pos).split('/')); out={'UTIL'}|(s&{'PG','SG','SF','PF','C'})
    if s&{'PG','SG','SF','PF'}: out.add('G/F')
    if s&{'SF','PF','C'}: out.add('F/C')
    return out
def solve(d,obj,extra=(),ban=(),force=(),teamcap=True):
    n=len(d); sl=[slots(p) for p in d.pos]
    pairs=[(i,kk) for i in range(n) for kk,x in enumerate(SL) if x in sl[i]]
    pi=np.array([p[0] for p in pairs]); pk=np.array([p[1] for p in pairs]); nv=len(pairs)
    rows=[];lo=[];hi=[]
    for kk in range(8):
        r=np.zeros(n+nv); r[n:][pk==kk]=1; rows.append(r); lo.append(NEED[kk]); hi.append(NEED[kk])
    L=np.zeros((n,n+nv)); L[pi,n+np.arange(nv)]=1; L[np.arange(n),np.arange(n)]=-1; rows+=list(L); lo+=[0]*n; hi+=[0]*n
    r=np.zeros(n+nv); r[:n]=d.salary.values; rows.append(r); lo.append(0); hi.append(60000)
    if teamcap:
        for t in d.team.unique():
            a=np.zeros(n+nv); a[:n]=(d.team.values==t); rows.append(a); lo.append(0); hi.append(3)
            b=np.zeros(n+nv); b[:n]=(d.team.values==t)&(d.salary.values<5000)
            if b.sum()>2: rows.append(b); lo.append(0); hi.append(2)
    for a,c in extra:
        v=np.zeros(n+nv); v[:n]=a; rows.append(v); lo.append(0); hi.append(c)
    lb=np.zeros(n+nv); ub=np.ones(n+nv)
    if len(ban): ub[list(ban)]=0
    if len(force): lb[list(force)]=1
    c=np.zeros(n+nv); c[:n]=-obj; integ=np.zeros(n+nv); integ[:n]=1
    r=milp(c,constraints=LinearConstraint(sparse.csr_matrix(np.array(rows)),lo,hi),integrality=integ,bounds=Bounds(lb,ub),options={'mip_rel_gap':1e-7,'time_limit':30})
    return None if r.x is None else list(np.where(r.x[:n]>0.5)[0])
def build4(d,obj,games):
    n=len(d); own=d.own.values; cap=np.where(own>=35,3,np.where(own>=15,2,1)); ov=4 if games>=6 else (5 if games>=4 else 8)
    contra=((own<10).astype(float),1 if games>=4 else 2); built=[]; cnt=np.zeros(n,int)
    for j in range(4):
        ids=solve(d,obj,[contra]+[(np.isin(np.arange(n),L).astype(float),ov) for L in built],ban=np.where(cnt>=cap)[0])
        if ids is None: break
        built.append(ids); cnt[ids]+=1
    return built
def field(dt):
    c=C[(C.date==dt)&(C.ctype==4)&(C.fee<=20)]; s=c[c.contest.str.contains('Shot')&~c.contest.str.contains('Pigg')] if len(c) else c
    if len(c):
        r=(s if len(s) else c).sort_values('entries').iloc[-1]; return r.mu_ls+1.0,0.35*r.proxy_ls
    f={'2026-11-06':'23632d04','2026-11-10':'eb8ea2d9'}.get(dt)
    r=FC[FC.file.str.startswith(f)].iloc[0]; return r['mean'],r['sd']
res=[]; detail=[]
for dt in sorted(A.date.unique()):
    a=A[A.date==dt].copy(); games=int(T[(T.date==dt)].main_games.iloc[0]); mu,sd=field(dt)
    a['kk']=a.name_live.map(k); fdout=FDOUT.get(dt,set())
    a['l5f']=a.l5.fillna(a.ls_proj_live)
    # ---- frozen build at the last pull ----
    d=a[(a.ls_proj_live>0)&(a.stat_live!=4)&~a.kk.isin(fdout)&((a.stat_live==1)|(a.min3>=18))].reset_index(drop=True)
    po=d.pown_live.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95)
    up=(d.ceil-d.ls_proj_live).clip(lower=0).fillna(0).values
    aggl=np.where(d.agg_live>0,d.agg_live,d.ls_proj_live)
    P={'blend':0.7*d.ls_proj_live.values+0.3*d.l5f.values,'LS':d.ls_proj_live.values,'AGG':aggl,'MIX':0.5*d.ls_proj_live.values+0.5*aggl}
    act=d.actual.where(d.stat_fin!=4,0).values
    row=dict(date=dt,games=games,mu=mu,sd=sd,n=len(d))
    for nm,p in P.items():
        Ls=build4(d,p+0.1*up,games); sc=[float(act[L].sum()) for L in Ls]
        row[nm+'_mean']=np.mean(sc); row[nm+'_best']=max(sc); row[nm+'_scores']=' '.join(f'{x:.1f}' for x in sc); row[nm+'_cash']=sum((x-mu)/sd>=0.72 for x in sc); row[nm+'_top10']=sum((x-mu)/sd>=1.27 for x in sc)
        row[nm+'_dead']=sum(int((d.stat_fin.values[L]==4).sum()) for L in Ls)
        if nm in('blend','LS'):
            # ---- late swap pricing on this set ----
            f=a[(a.stat_fin!=4)&(a.ls_proj_fin>0)&((a.stat_fin==1)|(a.min3>=18))].copy()
            for j,L in enumerate(Ls):
                base=d.iloc[L]; frozen=float(act[L].sum())
                locked=base[base.tip<60]; lockids=set(locked.salary_id)
                pool=pd.concat([locked.assign(_lock=1),f[(f.tip>=60)&~f.salary_id.isin(lockids)].assign(_lock=0)],ignore_index=True)
                pool['p']=np.where(pool._lock==1,0,pool.ls_proj_fin); pool['a']=np.where(pool.stat_fin!=4,pool.actual,0)
                force=list(np.where(pool._lock==1)[0])
                # (b) full re-optimisation of unlocked slots on final LineStar projections
                full=solve(pool,pool.p.values,force=force)
                fullsc=float(pool.a.values[full].sum()) if full else np.nan
                # (a) rule-17: replace only players ruled out; keep every healthy player
                keep=base[(base.tip>=60)&(base.stat_fin!=4)]; dead=base[(base.tip>=60)&(base.stat_fin==4)]
                if len(dead):
                    force2=force+list(np.where(pool.salary_id.isin(set(keep.salary_id)))[0])
                    r17=solve(pool,pool.p.values,force=force2); r17sc=float(pool.a.values[r17].sum()) if r17 else frozen
                else: r17sc=frozen
                detail.append(dict(date=dt,src=nm,lu=j+1,frozen=frozen,rule17=r17sc,full=fullsc,n_locked=len(locked),n_dead=len(dead),dead=','.join(dead.name_live),
                                   swapped_in=','.join(sorted(set(pool.name_live.values[full])-set(base.name_live))) if full else ''))
    res.append(row)
R=pd.DataFrame(res); D=pd.DataFrame(detail)
print(R[['date','games','n','mu','sd']+[c for c in R if c.endswith('_scores')]].round(1).to_string())
print(R[['date']+[c for c in R if c.endswith('_mean') or c.endswith('_best')]].round(1).to_string())
print('MEANS',R[[c for c in R if c.endswith('_mean') or c.endswith('_best')]].mean().round(1).to_dict())
print('cash count /28',{c:int(R[c].sum()) for c in R if c.endswith('_cash')},'top10',{c:int(R[c].sum()) for c in R if c.endswith('_top10')},'dead roster spots',{c:int(R[c].sum()) for c in R if c.endswith('_dead')})
print('paired LS-blend mean diff %.1f (se %.1f); AGG-blend %.1f (se %.1f); MIX-blend %.1f (se %.1f)'%tuple(x for nm in ['LS','AGG','MIX'] for x in ((R[nm+'_mean']-R.blend_mean).mean(),(R[nm+'_mean']-R.blend_mean).std()/np.sqrt(len(R)))))
print('\nLATE SWAP pricing (per lineup):')
for nm,g in D.groupby('src'):
    print(nm,'lineups',len(g),'frozen %.1f | rule-17 swap %.1f (+%.1f) | full re-opt of unlocked slots %.1f (+%.1f, se %.1f) ; lineups with a dead player %d ; avg locked players %.1f'%(g.frozen.mean(),g.rule17.mean(),(g.rule17-g.frozen).mean(),g.full.mean(),(g.full-g.frozen).mean(),(g.full-g.frozen).std()/np.sqrt(len(g)),(g.n_dead>0).sum(),g.n_locked.mean()))
    print(g.groupby('date').apply(lambda x:pd.Series(dict(frozen=x.frozen.mean(),rule17=x.rule17.mean(),full=x.full.mean()))).round(1).to_string())
print(D[D.src=='LS'][['date','lu','frozen','rule17','full','n_locked','dead','swapped_in']].round(1).to_string())
R.to_csv('live_build_results.csv',index=False); D.to_csv('late_swap_detail.csv',index=False)
