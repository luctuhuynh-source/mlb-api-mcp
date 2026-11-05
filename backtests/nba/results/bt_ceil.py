import pandas as pd, numpy as np, pulp
exec(open('bt_lp.py').read().split('rows=[]')[0].replace("print('fitted","_=('"))
def best(d,lam_fr,col=None):
    d=d.reset_index(drop=True)
    if col: obj=d[col]
    else: obj=d.ls_proj+np.where(d.fr,lam_fr,0.1)*(d.ls_ceil-d.ls_proj).clip(lower=0)
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
    return d.actual_fd_pts[ids].sum(), d.fr[ids].sum()
LAMS=[0.1,0.3,0.6,1.0]; rows=[]
for dt in sorted(set(a.date)&set(pool_ids.index)):
    d=a[(a.date==dt)&a.player_id.isin(pool_ids[dt])&(a.ls_proj>0)].copy()
    if d.fr.sum()==0 or len(d)<30: continue
    d['sl']=d.pos.map(slots)
    opt,_=best(d,0,col='actual_fd_pts')
    r=dict(date=dt,yr=d.yr.iloc[0],opt=opt)
    for l in LAMS: r[f's{l}'],r[f'n{l}']=best(d,l)
    rows.append(r)
r=pd.DataFrame(rows); r.to_csv('bt_ceil_results.csv',index=False)
for yr in ['fit','test']:
    q=r[r.yr==yr]; print(f'\n== {yr} ({"2024-25" if yr=="fit" else "2025-26+"}) slates={len(q)}')
    for l in LAMS:
        s=q[f's{l}']; dlt=s-q['s0.1']
        print(f'  lam_fr {l:<4} meanFP {s.mean():6.2f}  vs base {dlt.mean():+5.2f} (se {dlt.std()/np.sqrt(len(q)):.2f})  >=85%opt {(s>=.85*q.opt).mean():.1%}  >=90%opt {(s>=.90*q.opt).mean():.1%}  beats base by 15+ {(dlt>=15).mean():.1%} / loses 15+ {(dlt<=-15).mean():.1%}  fr/lineup {q[f"n{l}"].mean():.2f}')
