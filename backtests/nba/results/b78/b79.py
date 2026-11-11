"""B79 - tests requested in the ChatGPT review, AggProj era, FINAL LineStar data (same basis as B77/B78).
All arms: CAL projection, no exposure cap, overlap 6 (unless stated), objective U = CAL + lam x (LS ceiling - LS projection).
 team cap 3 vs 4 (FanDuel's legal max) x cheap-teammate cap 2 vs none, contrarian cap on/off, ceiling weight 0.2,
 ownership tie-break on lineups 3-4 (lowest projected ownership among lineups within 1.0 of the best objective), overlap 8.
Usage: python3 b79.py <out.csv> <part> <nparts>"""
import pandas as pd, numpy as np, sys, time, warnings
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy import sparse
warnings.filterwarnings('ignore')
import b78a as B
M=B.M
CFG={
 'c4':dict(contra=True,sub=True,team=3),
 'c4_nc':dict(contra=False,sub=True,team=3),
 'c4_nc_ns':dict(contra=False,sub=False,team=3),
 'c4_nc_t4':dict(contra=False,sub=True,team=4),
 'c4_nc_ns_t4':dict(contra=False,sub=False,team=4),
 'c4_nc_ns_lam20':dict(contra=False,sub=False,team=3,lam=0.2),
 'c4_nc_ns_tb':dict(contra=False,sub=False,team=3,tb=1.0),
 'c4_nc_ns_o8':dict(contra=False,sub=False,team=3,ov=8),
}
def solve(S,c,extra=(),ban=(),team=3,sub=True):
    rows,lo,hi=[list(x) for x in S.base]
    for a,_,_ in S.team: rows.append(a); lo.append(0); hi.append(team)
    if sub:
        for a,l,h in S.sub: rows.append(a); lo.append(l); hi.append(h)
    for a,l,h in extra: rows.append(a); lo.append(l); hi.append(h)
    ub=np.ones(S.N); ub[S.n+S.nv:]=0
    if len(ban): ub[list(ban)]=0
    cc=np.zeros(S.N); cc[:S.n]=c
    r=milp(cc,constraints=LinearConstraint(sparse.csr_matrix(np.array(rows)),lo,hi),integrality=S.integ,bounds=Bounds(0,ub),options={'mip_rel_gap':1e-7,'time_limit':20})
    return None if r.x is None else list(np.where(r.x[:S.n]>0.5)[0])
def run_date(dt):
    t0=time.time()
    a=M[M.date==dt]; games=int(a.main_games.iloc[0]) if len(a) and a.main_games.notna().any() else 0
    if games<4: return None
    ref=B.ref_contests(dt)
    if ref is None or not np.isfinite(ref.mu_ls) or ref.proxy_ls<=0: return None
    d=a[(a.ls_proj>0)&(a.stat!=4)].copy(); d=d[(d.stat==1)|(d.min3>=18)].reset_index(drop=True)
    if len(d)<25 or d.actual.sum()==0 or not ((d['agg']>0).mean()>0.5): return None
    d['aggp']=np.where(d['agg']>0,d['agg'],d.ls_proj); d['cal']=-0.26+0.136*d.ls_proj+0.856*d.aggp
    d['up']=(d['ceil']-d.ls_proj).clip(lower=0).fillna(0)
    po=d.pown.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95) if po.sum()>0 else po
    S=B.Slate(d,games); n=S.n; act=d.actual.values; own=d.own.values
    out=dict(date=dt,games=games,n=n,mu=ref.mu_ls+B.MU_OFF,sd=B.KAPPA*ref.proxy_ls)
    def vec(v):
        x=np.zeros(S.N); x[:n]=v; return x
    for name,cfg in CFG.items():
        U=d.cal.values+cfg.get('lam',0.1)*d.up.values; ov=cfg.get('ov',6)
        ex0=[(vec(own<10),0,1)] if cfg['contra'] else []
        built=[]; give=[]
        for j in range(4):
            ex=list(ex0)+[(S.vec(L),0,ov) for L in built]
            if ov>=9: pass
            ids=solve(S,-U,ex,team=cfg['team'],sub=cfg['sub'])
            if ids is None: break
            if cfg.get('tb') and j>=2:
                ub=U[ids].sum(); ids2=solve(S,own,ex+[(vec(U),ub-cfg['tb'],1e9)],team=cfg['team'],sub=cfg['sub'])
                if ids2 is not None: give.append(ub-U[ids2].sum()); ids=ids2
            built.append(ids)
            out[f'{name}_s{j+1}']=float(act[ids].sum()); out[f'{name}_own{j+1}']=float(own[ids].sum()); out[f'{name}_mt{j+1}']=int(pd.Series(d.team.values[ids]).value_counts().iloc[0])
        if give: out[name+'_give']=float(np.mean(give))
    out['secs']=round(time.time()-t0,1)
    return out
if __name__=='__main__':
    outf=sys.argv[1]; part=int(sys.argv[2]); nparts=int(sys.argv[3])
    dates=sorted(M.date.unique())[part::nparts]
    rows=[]; t=time.time()
    for i,dt in enumerate(dates):
        r=run_date(dt)
        if r: rows.append(r)
        if i%10==9: pd.DataFrame(rows).to_csv(outf,index=False); print(i+1,len(rows),round(time.time()-t),'s',flush=True)
    pd.DataFrame(rows).to_csv(outf,index=False); print('DONE',len(rows),round(time.time()-t),'s')
