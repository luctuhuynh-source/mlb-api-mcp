import pandas as pd, numpy as np, pulp, re, unicodedata
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/'
def k(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); s=re.sub(r'\b(jr|sr|ii|iii)\b','',s); return re.sub(r'[^a-z]','',s)
P=pd.read_csv(R+'linestar/players.csv'); P['k']=P.name.map(k)
O=pd.read_csv(R+'linestar/ownership.csv',usecols=['date','kind','slate','slate_games','player_id'])
G=pd.read_csv(R+'nba_player_games_2026-27.csv'); G=G[~G.did_not_play.astype(bool)&(G.minutes>0)]; G['k']=G.athlete_display_name.map(k)
# add 11/6 from live file + standings actuals
l6=pd.read_csv(R+'linestar/live/2026-11-06_1545_players.csv'); l6['k']=l6.name.map(k); a6=pd.read_csv('pts1106.csv'); a6['k']=a6.name.map(k)
l6=l6.merge(a6[['k','FPTS']],on='k',how='inner').rename(columns={'FPTS':'actual_fd_pts'}); l6['date']='2026-11-06'; l6['status']=np.where(l6.ls_proj>0,'active','out')
def engine(d,date):
    g=G[G.game_date<date].sort_values('game_date')
    a=g.groupby('k').apply(lambda x: pd.Series({'min3':x.minutes.tail(3).mean(),'minS':x.minutes.mean(),'rate':(x.fd_pts.sum()+0.9*250)/(x.minutes.sum()+250),'l5':x.fd_pts.tail(5).mean(),'gp':len(x)}))
    d=d.merge(a,left_on='k',right_index=True,how='left')
    d['eng']=(0.6*d.min3+0.4*d.minS)*d.rate
    d['blend']=0.7*d.ls_proj+0.3*d.l5.fillna(d.ls_proj)
    return d
def slots(pos):
    s=set(str(pos).split('/')); out={'UTIL'}|(s&{'PG','SG','SF','PF','C'})
    if s&{'PG','SG','SF','PF'}: out.add('G/F')
    if s&{'SF','PF','C'}: out.add('F/C')
    return out
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED=dict(PG=1,SG=1,SF=1,PF=1,C=1,UTIL=2,**{'G/F':1,'F/C':1})
def build(d,col,N=4):
    d=d.reset_index(drop=True); built=[]; out=[]
    for _ in range(N):
        m=pulp.LpProblem('x',pulp.LpMaximize); x={(i,s):pulp.LpVariable(f'x{i}_{s.replace("/","")}',cat='Binary') for i in d.index for s in d.sl[i]}
        y={i:pulp.lpSum(x[i,s] for s in d.sl[i]) for i in d.index}
        m+=pulp.lpSum(d[col][i]*y[i] for i in d.index)
        for s in SL: m+=pulp.lpSum(x[i,s] for i in d.index if s in d.sl[i])==NEED[s]
        for i in d.index: m+=y[i]<=1
        m+=pulp.lpSum(d.salary[i]*y[i] for i in d.index)<=60000
        for t,g in d.groupby('team'): m+=pulp.lpSum(y[i] for i in g.index)<=3
        for L in built: m+=pulp.lpSum(y[i] for i in L)<=6
        if m.solve(pulp.PULP_CBC_CMD(msg=0))!=1: break
        ids=[i for i in d.index if pulp.value(y[i])>0.5]; built.append(ids); out.append(d.actual_fd_pts[ids].sum())
    return out
rows=[]
dates=['2026-10-26','2026-10-27','2026-10-28','2026-10-30','2026-10-31','2026-11-01','2026-11-02','2026-11-04','2026-11-05','2026-11-06']
for dt in dates:
    if dt=='2026-11-06': d=l6.copy()
    else:
        d=P[P.date==dt].copy()
        mo=O[(O.date==dt)&(O.kind=='actual')&(O.slate=='Main')]
        if len(mo): d=d[d.player_id.isin(mo.player_id)]
    d=d[(d.ls_proj>0)&(d.status!='out')]
    if len(d)<20: continue
    d=engine(d,dt); d=d[d.eng.notna()].copy(); d['sl']=d.pos.map(slots)
    played=d[d.actual_fd_pts>0]
    mae=lambda c:(played[c]-played.actual_fd_pts).abs().mean()
    r=dict(date=dt,games=d.team.nunique()//2,n=len(d),mae_ls=mae('ls_proj'),mae_eng=mae('eng'),mae_blend=mae('blend'))
    for c in ['eng','ls_proj','blend']:
        s=build(d,c); r[c+'_avg']=np.mean(s); r[c+'_best']=max(s)
    rows.append(r); print(r)
pd.DataFrame(rows).to_csv('eng_vs_ls.csv',index=False)
