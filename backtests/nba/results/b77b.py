"""B77b (stage 2, AggProj era 2025-10-21 on) - field-relative backtest of NBA FD v1.3 and variants on the LineStar history.
Inputs per slate (main slate only): LineStar final projection/ceiling/AggProj, starter flag (STAT==1), Main-slate projected
ownership, game logs strictly before the date. Field model: mean = sum(realized own x actual pts) of the main-slate GPP
LineStar tracks (+1.0 FP for untracked ownership); SD = 0.35 x sqrt(sum own(1-own)pts^2), calibrated on 18 real contests.
Usage: python3 b77.py <out.csv> [nproc] [limit]
"""
import pandas as pd, numpy as np, sys, time, warnings
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy import sparse
from multiprocessing import Pool
warnings.filterwarnings('ignore')
KAPPA=0.35; MU_OFF=1.0
M=pd.read_pickle('master.pkl'); M=M[(M.in_main==1)&(M.date<'2026-11-10')&(M.date>='2025-10-21')].copy()
C=pd.read_csv('hist_contests_mu.csv')
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED=[1,1,1,1,1,1,1,2]
def slots(pos):
    s=set(str(pos).split('/')); out={'UTIL'}|(s&{'PG','SG','SF','PF','C'})
    if s&{'PG','SG','SF','PF'}: out.add('G/F')
    if s&{'SF','PF','C'}: out.add('F/C')
    return out
def ref_contests(dt):
    c=C[C.date==dt]; g=c[(c.ctype==4)&(c.fee<=20)]
    if not len(g): return None,None
    shot=g[g.contest.str.contains('Shot')&~g.contest.str.contains('Pigg')]
    r=(shot if len(shot) else g).sort_values('entries').iloc[-1]
    du=c[c.ctype==1]; du=du.sort_values('entries').iloc[-1] if len(du) else None
    return r,du
CFG={
 'V0_blend':dict(proj='blend'),
 'LS':dict(proj='ls'),
 'CAL':dict(proj='cal'),
 'CAL_cap2':dict(proj='cal',expo='cap2'),
 'CAL_t2':dict(proj='cal',expo='t2'),
 'CAL_cap3':dict(proj='cal',expo='none'),
 'CAL_free':dict(proj='cal',expo='none',ov=6),
 'CAL_ov6':dict(proj='cal',ov=6),
 'CAL_noContra':dict(proj='cal',contra=None),
 'CAL_contra2':dict(proj='cal',contra=2),
 'CAL_lam0':dict(proj='cal',lam=0.0),
 'CAL_lam3':dict(proj='cal',lam=0.3),
 'CAL_chalk3':dict(proj='cal',lev=-0.03),
 'CAL_lev3':dict(proj='cal',lev=0.03),
 'CAL_ns':dict(proj='calns'),
 'CAL_t2_ov6':dict(proj='cal',expo='t2',ov=6),
}
class Slate:
    def __init__(s,d,games):
        s.d=d; s.n=n=len(d); s.games=games
        sl=[slots(p) for p in d.pos]
        pairs=[(i,k) for i in range(n) for k,x in enumerate(SL) if x in sl[i]]
        s.pi=np.array([p[0] for p in pairs]); s.pk=np.array([p[1] for p in pairs]); s.nv=nv=len(pairs)
        rows=[];lo=[];hi=[]
        for k in range(8):
            r=np.zeros(n+nv); r[n:][s.pk==k]=1; rows.append(r); lo.append(NEED[k]); hi.append(NEED[k])
        L=np.zeros((n,n+nv)); L[s.pi,n+np.arange(nv)]=1; L[np.arange(n),np.arange(n)]=-1; rows+=list(L); lo+=[0]*n; hi+=[0]*n
        r=np.zeros(n+nv); r[:n]=d.salary.values; rows.append(r); lo.append(0); hi.append(60000)
        s.base=(rows,lo,hi)
        s.team=[]
        for t in d.team.unique():
            a=np.zeros(n+nv); a[:n]=(d.team.values==t); b=np.zeros(n+nv); b[:n]=(d.team.values==t)&(d.salary.values<5000)
            s.team.append((a,3)); 
            if b.sum()>2: s.team.append((b,2))
        s.integ=np.zeros(n+nv); s.integ[:n]=1
    def solve(s,obj,extra=(),ban=(),team=True):
        rows,lo,hi=[list(x) for x in s.base]
        if team:
            for a,c in s.team: rows.append(a); lo.append(0); hi.append(c)
        for a,c in extra: rows.append(a); lo.append(0); hi.append(c)
        ub=np.ones(s.n+s.nv); 
        if len(ban): ub[list(ban)]=0
        c=np.zeros(s.n+s.nv); c[:s.n]=-obj
        r=milp(c,constraints=LinearConstraint(sparse.csr_matrix(np.array(rows)),lo,hi),integrality=s.integ,bounds=Bounds(0,ub),options={'mip_rel_gap':1e-7,'time_limit':20})
        if r.x is None: return None
        return list(np.where(r.x[:s.n]>0.5)[0])
    def vec(s,idx):
        a=np.zeros(s.n+s.nv); a[list(idx)]=1; return a
def run_date(dt):
    t0=time.time()
    a=M[M.date==dt]; games=int(a.main_games.iloc[0]) if len(a) and a.main_games.notna().any() else 0
    if games<2: return None
    ref,du=ref_contests(dt)
    if ref is None or not np.isfinite(ref.mu_ls) or ref.proxy_ls<=0: return None
    d=a[(a.ls_proj>0)&(a.stat!=4)].copy()
    d=d[(d.stat==1)|(d.min3>=18)].reset_index(drop=True)
    if len(d)<25 or d.actual.sum()==0: return None
    d['l5f']=d.l5.fillna(d.ls_proj); d['blend']=0.7*d.ls_proj+0.3*d.l5f; d['ls']=d.ls_proj
    hasagg=(d['agg']>0).mean()>0.5
    d['aggp']=np.where(d['agg']>0,d['agg'],d.ls_proj); d['mix']=0.5*d.ls_proj+0.5*d.aggp
    d['cal']=-0.26+0.136*d.ls_proj+0.856*d.aggp; d['calns']=d.cal+0.8*((d.stat==1)&~(d.min3>=24))
    d['up']=(d['ceil']-d.ls_proj).clip(lower=0).fillna(0)
    po=d.pown.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95) if po.sum()>0 else po
    d['ru']=((d.ls_proj-d.l5f>=6)|((d.stat==1)&~(d.min3>=24)))
    S=Slate(d,games); n=S.n
    mu=ref.mu_ls+MU_OFF; sd=KAPPA*ref.proxy_ls
    out=dict(date=dt,games=games,n=n,mu=mu,sd=sd,ref=ref.contest,ref_entries=ref.entries,hasagg=int(hasagg),
             du_mu=(du.mu_ls+MU_OFF if du is not None else np.nan),du_sd=(KAPPA*du.proxy_ls if du is not None else np.nan))
    act=d.actual.values
    def anat(ids,pre):
        ids=list(ids)
        out[pre+'_n10k']=int((d.salary.values[ids]>=10000).sum()); out[pre+'_n45']=int((d.salary.values[ids]<=4500).sum())
        out[pre+'_ru']=int(d.ru.values[ids].sum()); out[pre+'_ruc']=int((d.ru.values[ids]&(d.salary.values[ids]<5500)).sum())
        out[pre+'_cumown']=float(d.own.values[ids].sum()); out[pre+'_lt10']=int((d.own.values[ids]<10).sum()); out[pre+'_ge35']=int((d.own.values[ids]>=35).sum())
        out[pre+'_sal']=int(d.salary.values[ids].sum()); out[pre+'_maxteam']=int(pd.Series(d.team.values[ids]).value_counts().iloc[0])
    o=S.solve(act,team=False)
    if o is None: return None
    out['opt']=float(act[o].sum()); anat(o,'opt')
    for name,cfg in CFG.items():
        if not hasagg: return None
        base={'blend':d.blend,'ls':d.ls,'agg':d.aggp,'mix':d.mix,'cal':d.cal,'calns':d.calns}[cfg['proj']].values
        obj=base+cfg.get('lam',0.1)*d.up.values-cfg.get('lev',0.0)*d.own.values
        ov=cfg.get('ov',(4 if games>=6 else (5 if games>=4 else 8))); ov=min(8,ov+cfg.get('ovd',0))
        if games<4 and 'ov' in cfg: ov=8
        expo=cfg.get('expo','tiers'); own=d.own.values
        cap=np.where(own>=35,3,np.where(own>=15,2,1))
        if expo=='cap2': cap=np.full(n,2)
        if expo=='t2': cap=np.where(own>=35,3,2)
        if expo=='role': cap=np.where(d.ru.values&(d.salary.values<6000),3,cap)
        if expo=='none': cap=np.full(n,3)
        extra0=[]
        if cfg.get('contra',1) is not None:
            m=(own<10)
            if expo=='role': m=m&~(d.ru.values&(d.salary.values<6000))
            v=np.zeros(S.n+S.nv); v[:n]=m; extra0.append((v,max(cfg.get('contra',1),1 if games>=4 else 2)))
        built=[];cnt=np.zeros(n,int)
        for j in range(4):
            extra=list(extra0)+[(S.vec(L),ov) for L in built]
            ids=S.solve(obj,extra,ban=np.where(cnt>=cap)[0])
            if ids is None: break
            built.append(ids); cnt[ids]+=1
            out[f'{name}_s{j+1}']=float(act[ids].sum()); out[f'{name}_p{j+1}']=float(base[ids].sum())
        if name in('V0_blend','CAL') and built:
            for j,ids in enumerate(built): anat(ids,f'{name}{j+1}')
    out['secs']=round(time.time()-t0,1)
    return out
if __name__=='__main__':
    outf=sys.argv[1]; npr=int(sys.argv[2]) if len(sys.argv)>2 else 2; lim=int(sys.argv[3]) if len(sys.argv)>3 else 0
    dates=sorted(M.date.unique())
    if lim: dates=dates[-lim:]
    rows=[]; t=time.time()
    with Pool(npr) as p:
        for i,r in enumerate(p.imap_unordered(run_date,dates,chunksize=1)):
            if r: rows.append(r)
            if i%20==19:
                pd.DataFrame(rows).sort_values('date').to_csv(outf,index=False); print(i+1,len(rows),round(time.time()-t),'s',flush=True)
    pd.DataFrame(rows).sort_values('date').to_csv(outf,index=False); print('DONE',len(rows),round(time.time()-t),'s')
