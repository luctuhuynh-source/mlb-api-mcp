"""B80 - lineup count: v1.4 structure (CAL projection, U = CAL + 0.1 x upside, overlap 6, team cap 3, nothing else), 10 lineups built in
sequence per slate on FINAL LineStar data (same basis as B77-B79). Score lineups 1-4 vs 1-6 vs 1-10.  Usage: python3 b80.py <out.csv> <part> <nparts>"""
import pandas as pd, numpy as np, sys, time, warnings
warnings.filterwarnings('ignore')
import b78a as B, b79
M=B.M; NL=10
def run_date(dt):
    a=M[M.date==dt]; games=int(a.main_games.iloc[0]) if len(a) and a.main_games.notna().any() else 0
    if games<4: return None
    ref=B.ref_contests(dt)
    if ref is None or not np.isfinite(ref.mu_ls) or ref.proxy_ls<=0: return None
    d=a[(a.ls_proj>0)&(a.stat!=4)].copy(); d=d[(d.stat==1)|(d.min3>=18)].reset_index(drop=True)
    if len(d)<25 or d.actual.sum()==0 or not ((d['agg']>0).mean()>0.5): return None
    d['aggp']=np.where(d['agg']>0,d['agg'],d.ls_proj); d['cal']=-0.26+0.136*d.ls_proj+0.856*d.aggp
    d['up']=(d['ceil']-d.ls_proj).clip(lower=0).fillna(0)
    S=B.Slate(d,games); act=d.actual.values; U=d.cal.values+0.1*d.up.values
    out=dict(date=dt,games=games,n=S.n); built=[]
    for j in range(NL):
        ids=b79.solve(S,-U,[(S.vec(L),0,6) for L in built],team=3,sub=False)
        if ids is None: break
        built.append(ids); out[f's{j+1}']=float(act[ids].sum()); out[f'p{j+1}']=float(U[ids].sum())
    out['uniq']=len(set(i for L in built for i in L)); return out
if __name__=='__main__':
    outf=sys.argv[1]; part=int(sys.argv[2]); nparts=int(sys.argv[3]); rows=[]; t=time.time()
    for i,dt in enumerate(sorted(M.date.unique())[part::nparts]):
        r=run_date(dt)
        if r: rows.append(r)
        if i%20==19: pd.DataFrame(rows).to_csv(outf,index=False); print(i+1,len(rows),round(time.time()-t),'s',flush=True)
    pd.DataFrame(rows).to_csv(outf,index=False); print('DONE',len(rows),round(time.time()-t),'s')
