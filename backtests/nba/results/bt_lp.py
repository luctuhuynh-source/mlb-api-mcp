import pandas as pd, numpy as np, pulp
a=pd.read_pickle('bt_out.pkl')
a['yr']=np.where(a.date<'2025-10-01','fit','test')
a['fr']=(a.f_vac>0)&a.posmatch&(a.rk<=8)
a['big']=a.f_vac>=45
fit=a[(a.yr=='fit')&a.fr]
pct={}
for big in [False,True]:
    for top in [True,False]:
        s=fit[(fit.big==big)&((fit.rk<=5)==top)]
        pct[(big,top)]=float((s.res.sum()/s.ls_proj.sum()))
print('fitted bump % (big_vac, starter-tier):',{k:round(v*100,1) for k,v in pct.items()})
a['bump']=[pct[(b,r<=5)] if f else 0 for f,b,r in zip(a.fr,a.big,a.rk)]
a['proj_b']=a.ls_proj*(1+a.bump)
o=pd.read_csv('/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/linestar/ownership.csv',usecols=['date','kind','slate','slate_games','player_id','owned_pct','actual_fd_pts','contest'])
main=o[(o.kind=='actual')&(o.slate=='Main')&(o.slate_games>=5)]
pool_ids=main.groupby('date').player_id.apply(set)
# field reference: top-1% proxy unavailable -> use ownership-weighted field mean lineup score approx
def slots(pos):
    s=set(pos.split('/')); out={'UTIL'}
    for t in s:
        if t in('PG','SG','SF','PF','C'): out.add(t)
    if s&{'PG','SG','SF','PF'}: out.add('G/F')
    if s&{'SF','PF','C'}: out.add('F/C')
    return out
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED=dict(PG=1,SG=1,SF=1,PF=1,C=1,**{'G/F':1,'F/C':1,'UTIL':2})
def best(d,col):
    d=d.reset_index(drop=True); obj=d[col]+0.1*(d.ls_ceil-d.ls_proj).clip(lower=0)
    m=pulp.LpProblem('x',pulp.LpMaximize); x={}
    for i in d.index:
        for s in d.sl[i]: x[i,s]=pulp.LpVariable(f'x{i}_{s.replace("/","")}',cat='Binary')
    y={i:pulp.lpSum(x[i,s] for s in d.sl[i]) for i in d.index}
    m+=pulp.lpSum(obj[i]*y[i] for i in d.index)
    for s in SL: m+=pulp.lpSum(x[k] for k in x if k[1]==s)==NEED[s]
    for i in d.index: m+=y[i]<=1
    m+=pulp.lpSum(d.salary[i]*y[i] for i in d.index)<=60000
    for t,g in d.groupby('team'): m+=pulp.lpSum(y[i] for i in g.index)<=3
    m.solve(pulp.PULP_CBC_CMD(msg=0))
    ids=[i for i in d.index if pulp.value(y[i])>0.5]
    return d.actual_fd_pts[ids].sum(), set(d.player_id[ids]), d.fr[ids].sum()
rows=[]
dates=sorted(set(a[a.yr=='test'].date)&set(pool_ids.index))
for dt in dates:
    d=a[(a.date==dt)&a.player_id.isin(pool_ids[dt])&(a.ls_proj>0)].copy()
    if d.fr.sum()==0 or len(d)<30: continue
    d['sl']=d.pos.map(slots)
    s0,p0,n0=best(d,'ls_proj'); s1,p1,n1=best(d,'proj_b')
    rows.append(dict(date=dt,base=s0,bump=s1,diff=s1-s0,changed=len(p1-p0),fr0=n0,fr1=n1))
r=pd.DataFrame(rows); r.to_csv('bt_lp_results.csv',index=False)
print(f'test slates (2025-26+ main, with a fresh key out): {len(r)}; lineup changed on {(r.changed>0).sum()}')
print(f'mean actual FP  base {r.base.mean():.2f}  bump {r.bump.mean():.2f}  diff {r["diff"].mean():+.2f}  (se {r["diff"].std()/np.sqrt(len(r)):.2f})')
c=r[r.changed>0]; print(f'on changed slates: n={len(c)} diff {c["diff"].mean():+.2f} se {c["diff"].std()/np.sqrt(len(c)):.2f}; bump better {(c["diff"]>0).mean():.0%}, avg players swapped {c.changed.mean():.1f}')
print(f'fresh-beneficiaries per lineup: base {r.fr0.mean():.2f} -> bump {r.fr1.mean():.2f}')
