"""B78a - structural tests requested in the Gemini review, AggProj era, FINAL LineStar data (same basis as B77).
New knobs vs B77c: hybrid exposure by tip time, drop sub-$5k / contrarian caps, ceiling 0.25 for lineups 3-4,
game-stack rule for lineups 2-4, cumulative-ownership cap. Usage: python3 b78a.py <out.csv> [limit]"""
import pandas as pd, numpy as np, sys, time, warnings
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy import sparse
warnings.filterwarnings('ignore')
KAPPA=0.35; MU_OFF=1.0
M=pd.read_pickle('master.pkl'); M=M[(M.in_main==1)&(M.date<'2026-11-10')&(M.date>='2025-10-21')].copy()
M['tip']=(M['gt']/1000-pd.to_datetime(M.main_start).astype('int64')//10**9)/60+180
C=pd.read_csv('hist_contests_mu.csv')
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED=[1,1,1,1,1,1,1,2]
def slots(pos):
    s=set(str(pos).split('/')); out={'UTIL'}|(s&{'PG','SG','SF','PF','C'})
    if s&{'PG','SG','SF','PF'}: out.add('G/F')
    if s&{'SF','PF','C'}: out.add('F/C')
    return out
def ref_contests(dt):
    c=C[C.date==dt]; g=c[(c.ctype==4)&(c.fee<=20)]
    if not len(g): return None
    shot=g[g.contest.str.contains('Shot')&~g.contest.str.contains('Pigg')]
    return (shot if len(shot) else g).sort_values('entries').iloc[-1]
CFG={
 'CAL_free':dict(expo='none'),
 'CAL_c4o6':dict(expo='c4'),
 'CAL_hyb':dict(expo='hyb'),
 'CAL_free_noSub':dict(expo='none',sub5k=False),
 'CAL_free_noBoth':dict(expo='none',sub5k=False,contra=None),
 'CAL_c4_noBoth':dict(expo='c4',sub5k=False,contra=None),
 'CAL_free_lam25':dict(expo='none',lam34=0.25),
 'CAL_c4_lam25':dict(expo='c4',lam34=0.25),
 'CAL_c4_stack6':dict(expo='c4',stack=True),
 'CAL_c4_stack7':dict(expo='c4',stack=True,ov=7),
 'CAL_c4_cum285':dict(expo='c4',cum=285),
}
class Slate:
    def __init__(s,d,games):
        s.d=d; s.n=n=len(d); s.games=games
        sl=[slots(p) for p in d.pos]
        pairs=[(i,k) for i in range(n) for k,x in enumerate(SL) if x in sl[i]]
        s.pi=np.array([p[0] for p in pairs]); s.pk=np.array([p[1] for p in pairs]); s.nv=nv=len(pairs)
        # stackable games: top half by combined projected points of listed starters
        g=d[d.stat==1].groupby('gid').cal.sum().sort_values(ascending=False); s.sg=list(g.index[:int(np.ceil(len(g)/2))]); s.G=G=len(s.sg); s.N=N=n+nv+G
        rows=[];lo=[];hi=[]
        for k in range(8):
            r=np.zeros(N); r[n:n+nv][s.pk==k]=1; rows.append(r); lo.append(NEED[k]); hi.append(NEED[k])
        L=np.zeros((n,N)); L[s.pi,n+np.arange(nv)]=1; L[np.arange(n),np.arange(n)]=-1; rows+=list(L); lo+=[0]*n; hi+=[0]*n
        r=np.zeros(N); r[:n]=d.salary.values; rows.append(r); lo.append(0); hi.append(60000)
        s.base=(rows,lo,hi); s.team=[]; s.sub=[]
        for t in d.team.unique():
            a=np.zeros(N); a[:n]=(d.team.values==t); b=np.zeros(N); b[:n]=(d.team.values==t)&(d.salary.values<5000)
            s.team.append((a,0,3))
            if b.sum()>2: s.sub.append((b,0,2))
        s.stk=[]
        for j,gid in enumerate(s.sg):
            m=(d.gid.values==gid); ts=pd.unique(d.team.values[m])
            a=np.zeros(N); a[:n]=m; a[n+nv+j]=-3; s.stk.append((a,0,9))
            for t in ts:
                b=np.zeros(N); b[:n]=m&(d.team.values==t); b[n+nv+j]=-1; s.stk.append((b,0,9))
        z=np.zeros(N); z[n+nv:]=1; s.stk.append((z,1,G))
        s.integ=np.zeros(N); s.integ[:n]=1; s.integ[n+nv:]=1
    def solve(s,obj,extra=(),ban=(),team=True,sub5k=True,stack=False):
        rows,lo,hi=[list(x) for x in s.base]
        cons=(s.team if team else [])+(s.sub if (team and sub5k) else [])+(s.stk if stack else [])
        for a,l,h in cons: rows.append(a); lo.append(l); hi.append(h)
        for a,c in extra: rows.append(a); lo.append(0); hi.append(c)
        ub=np.ones(s.N)
        if not stack: ub[s.n+s.nv:]=0
        if len(ban): ub[list(ban)]=0
        c=np.zeros(s.N); c[:s.n]=-obj
        r=milp(c,constraints=LinearConstraint(sparse.csr_matrix(np.array(rows)),lo,hi),integrality=s.integ,bounds=Bounds(0,ub),options={'mip_rel_gap':1e-7,'time_limit':20})
        if r.x is None: return None
        return list(np.where(r.x[:s.n]>0.5)[0])
    def vec(s,idx):
        a=np.zeros(s.N); a[list(idx)]=1; return a
def run_date(dt):
    t0=time.time()
    a=M[M.date==dt]; games=int(a.main_games.iloc[0]) if len(a) and a.main_games.notna().any() else 0
    if games<4: return None
    ref=ref_contests(dt)
    if ref is None or not np.isfinite(ref.mu_ls) or ref.proxy_ls<=0: return None
    d=a[(a.ls_proj>0)&(a.stat!=4)].copy()
    d=d[(d.stat==1)|(d.min3>=18)].reset_index(drop=True)
    if len(d)<25 or d.actual.sum()==0: return None
    if not ((d['agg']>0).mean()>0.5): return None
    d['aggp']=np.where(d['agg']>0,d['agg'],d.ls_proj); d['cal']=-0.26+0.136*d.ls_proj+0.856*d.aggp
    d['up']=(d['ceil']-d.ls_proj).clip(lower=0).fillna(0)
    po=d.pown.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95) if po.sum()>0 else po
    S=Slate(d,games); n=S.n; act=d.actual.values; own=d.own.values; tip=d.tip.values
    out=dict(date=dt,games=games,n=n,mu=ref.mu_ls+MU_OFF,sd=KAPPA*ref.proxy_ls,first_tip_share=float((tip<30).mean()),stack_games=S.G)
    o=S.solve(act,team=False)
    if o is None: return None
    out['opt']=float(act[o].sum())
    for name,cfg in CFG.items():
        ov=cfg.get('ov',6); expo=cfg['expo']
        cap={'none':np.full(n,3),'c4':np.full(n,4),'hyb':np.where(tip<30,4,3)}[expo]
        extra0=[]
        if cfg.get('contra',1) is not None:
            v=np.zeros(S.N); v[:n]=(own<10); extra0.append((v,1))
        built=[];cnt=np.zeros(n,int)
        for j in range(4):
            lam=cfg.get('lam34',0.1) if j>=2 else 0.1
            extra=list(extra0)+[(S.vec(L),ov) for L in built]
            if cfg.get('cum') and j>=2 and games<=4:
                v=np.zeros(S.N); v[:n]=own; extra.append((v,cfg['cum']))
            ids=S.solve(d.cal.values+lam*d.up.values,extra,ban=np.where(cnt>=cap)[0],sub5k=cfg.get('sub5k',True),stack=bool(cfg.get('stack')) and j>=1)
            if ids is None: break
            built.append(ids); cnt[ids]+=1
            out[f'{name}_s{j+1}']=float(act[ids].sum()); out[f'{name}_p{j+1}']=float(d.cal.values[ids].sum())
            out[f'{name}_own{j+1}']=float(own[ids].sum()); out[f'{name}_mg{j+1}']=int(pd.Series(d.gid.values[ids]).value_counts().iloc[0])
        out[name+'_uniq']=int((cnt>0).sum()); out[name+'_max4']=int((cnt==4).sum())
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
