import pandas as pd, numpy as np
p=pd.read_csv('/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/linestar/players.csv')
p=p[p.date<'2026-11-04'].copy()
p['played']=p.actual_fd_pts>0
# previous team game status per player
p=p.sort_values('date')
tg=p.groupby(['team','date']).size().reset_index()[['team','date']]
tg['prev']=tg.groupby('team').date.shift()
p=p.merge(tg,on=['team','date'])
prev=p[['player_id','date','played']].rename(columns={'date':'prev','played':'played_prev'})
p=p.merge(prev,on=['player_id','prev'],how='left')
out=p[(p.status=='out')]
out=out.assign(fresh=out.played_prev.fillna(False).astype(bool))
key=out[out.ppg>=25]
agg=lambda d: d.groupby(['team','date']).agg(vac=('ppg','sum'),n=('ppg','size'),pos=('pos',lambda s:'/'.join(s)))
fk=agg(key[key.fresh]).add_prefix('f_'); lk=agg(key[~key.fresh]).add_prefix('l_')
a=p[(p.ls_proj>0)&(p.status!='out')].join(fk,on=['team','date']).join(lk,on=['team','date'])
a['f_vac']=a.f_vac.fillna(0); a['l_vac']=a.l_vac.fillna(0)
a['res']=a.actual_fd_pts-a.ls_proj
a['rk']=a.groupby(['team','date']).ls_proj.rank(ascending=False,method='first')
def pm(r):
    if pd.isna(r.f_pos): return False
    mine=set(r.pos.split('/')); g={'PG','SG'}; f={'SF','PF'}; c={'C'}
    o=set(r.f_pos.replace('/','|').split('|'))
    for grp in (g,f,c):
        if mine&grp and o&grp: return True
    return False
a['posmatch']=a.apply(pm,axis=1)
a['grp']=np.select([a.f_vac>0,a.l_vac>0],['FRESH key out','long-term key out'],'no key out')
a['rkb']=pd.cut(a.rk,[0,2,5,8,20],labels=['top2','3-5','6-8','9+'])
a['x6']=a.actual_fd_pts>=6*a.salary/1000
print('Mean residual (actual - LineStar proj), n:')
print(a.pivot_table(index='rkb',columns='grp',values='res',aggfunc=['mean','size'],observed=True).round(2))
f=a[a.f_vac>0]
print('\nFRESH out, by position match & rank:')
print(f.groupby(['posmatch','rkb'],observed=True).agg(n=('res','size'),res=('res','mean'),proj=('ls_proj','mean'),x6=('x6','mean')).round(2))
print('\nBaseline 6x rate by rank (no key out):'); print(a[a.grp=='no key out'].groupby('rkb',observed=True).x6.mean().round(3))
a['yr']=np.where(a.date<'2025-10-01','2024-25','2025-26+')
print('\nStability by season (FRESH, rank<=5):'); print(f[f.rk<=5].assign(yr=lambda d:np.where(d.date<'2025-10-01','2024-25','2025-26+')).groupby(['yr','posmatch']).res.agg(['size','mean']).round(2))
a.to_pickle('bt_out.pkl')
