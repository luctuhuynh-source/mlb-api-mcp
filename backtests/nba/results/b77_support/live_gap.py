"""Lock-time information gap: last pre-lock LineStar pull vs LineStar's final (post-lock) record for the same slate."""
import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
T=pd.read_pickle('live_pulls.pkl'); M=pd.read_pickle('master.pkl')
last=T.groupby('date').pull.max().to_dict(); first={d:T[(T.date==d)&(T.pull>='1400')].pull.min() for d in last}
rows=[]; allm=[]
for d,pl in last.items():
    if d>='2026-11-10': continue
    L=T[(T.date==d)&(T.pull==pl)&(T.in_main==1)]
    F=M[(M.date==d)&(M.in_main==1)]
    m=L.merge(F[['salary_id','name','ls_proj','agg','stat','actual','l5','min3','pown','gt','main_start']],on='salary_id',suffixes=('_live','_fin'))
    if len(m)<20: print('skip',d,'(no final record)'); continue
    assert (m.name_live==m.name_fin).mean()>0.98,(d,(m.name_live==m.name_fin).mean())
    m['tip_off']=(m.gt_fin/1000-pd.to_datetime(m.main_start_fin).astype('int64')//10**9)/60
    m['date']=d; allm.append(m)
    el=m[(m.stat_fin!=4)&(m.ls_proj_fin>0)&((m.stat_fin==1)|(m.min3>=18))]
    r=dict(date=d,pull=pl,n=len(el),mae_live=(el.actual-el.ls_proj_live).abs().mean(),mae_fin=(el.actual-el.ls_proj_fin).abs().mean(),
           mae_agg_live=(el.actual-el.agg_live.where(el.agg_live>0,el.ls_proj_live)).abs().mean(),mae_agg_fin=(el.actual-el.agg_fin.where(el.agg_fin>0,el.ls_proj_fin)).abs().mean(),
           up5=((el.ls_proj_fin-el.ls_proj_live)>=5).sum(),dn5=((el.ls_proj_live-el.ls_proj_fin)>=5).sum(),
           scratched=((m.ls_proj_live>0)&(m.stat_live!=4)&(m.stat_fin==4)).sum(),new_start=((m.stat_live!=1)&(m.stat_fin==1)).sum(),lost_start=((m.stat_live==1)&(m.stat_fin!=1)).sum())
    rows.append(r)
R=pd.DataFrame(rows); print(R.round(2).to_string()); print(R[['mae_live','mae_fin','mae_agg_live','mae_agg_fin','up5','dn5','scratched','new_start','lost_start']].mean().round(2).to_dict())
A=pd.concat(allm); A['chg']=A.ls_proj_fin-A.ls_proj_live
A['val']=A.actual/(A.salary/1000)
print('\nPlayers whose LineStar projection rose >=5 FP after the last pre-lock pull:')
u=A[(A.chg>=5)&(A.stat_fin!=4)].sort_values(['date','chg'],ascending=[True,False])
print(u[['date','name_live','team','salary','ls_proj_live','ls_proj_fin','chg','stat_live','stat_fin','tip_off','actual','val','pown_live','pown_fin']].round(1).to_string())
print('\nScratched after the last pre-lock pull (live proj>0, final OUT):')
s=A[(A.ls_proj_live>0)&(A.stat_live!=4)&(A.stat_fin==4)]
print(s[['date','name_live','team','salary','ls_proj_live','stat_live','tip_off','pown_live']].round(1).to_string())
print('\nrisers summary: n=%d per slate=%.1f mean live proj %.1f final %.1f actual %.1f value %.2fx p6x %.2f mean tip offset %.0f min; share in games tipping >=60 min after lock %.2f'%(len(u),len(u)/R.date.nunique(),u.ls_proj_live.mean(),u.ls_proj_fin.mean(),u.actual.mean(),u.val.mean(),(u.val>=6).mean(),u.tip_off.mean(),(u.tip_off>=60).mean()))
A.to_pickle('live_vs_final.pkl')
