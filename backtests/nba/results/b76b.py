"""B76 - construction / source / exposure / anchor ablation on the LineStar history.
Point-in-time inputs only: LineStar projection+ceiling+projected ownership for the date,
game logs strictly before the date. 4 lineups per slate per config.
"""
import pandas as pd, numpy as np, pulp, re, unicodedata, sys, json
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/'
OUT='/tmp/claude-0/-home-claude/6b87524e-2daf-575b-8b1e-b163002da830/scratchpad/'
def k(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); s=re.sub(r'\b(jr|sr|ii|iii)\b','',s); return re.sub(r'[^a-z]','',s)
P=pd.read_csv(R+'linestar/players.csv'); P['k']=P.name.map(k)
O=pd.read_csv(R+'linestar/ownership.csv',usecols=['date','kind','slate','slate_games','player_id','owned_pct'])
main=O[(O.slate=='Main')&(O.kind=='actual')]
pown=O[O.kind=='projected'].groupby(['date','player_id']).owned_pct.max()
G=pd.concat([pd.read_csv(R+f'nba_player_games_{s}.csv') for s in ['2024-25','2025-26','2026-27']])
G=G[~G.did_not_play.astype(bool)&(G.minutes>0)]; G['k']=G.athlete_display_name.map(k); G=G.sort_values('game_date')
def slots(pos):
    s=set(str(pos).split('/')); out={'UTIL'}|(s&{'PG','SG','SF','PF','C'})
    if s&{'PG','SG','SF','PF'}: out.add('G/F')
    if s&{'SF','PF','C'}: out.add('F/C')
    return out
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED=dict(PG=1,SG=1,SF=1,PF=1,C=1,UTIL=2,**{'G/F':1,'F/C':1})
def prep(dt):
    d=P[(P.date==dt)&(P.ls_proj>0)&(P.status!='out')].copy()
    ids=set(main[main.date==dt].player_id); d=d[d.player_id.isin(ids)]
    g=G[G.game_date<dt]
    a=g.groupby('k').agg(min3=('minutes',lambda x:x.tail(3).mean()),l5=('fd_pts',lambda x:x.tail(5).mean()))
    d=d.merge(a,left_on='k',right_index=True,how='left')
    d['blend']=0.7*d.ls_proj+0.3*d.l5.fillna(d.ls_proj)
    d['pown']=[pown.get((dt,pid),0.0) for pid in d.player_id]
    d['own_x']=(d.pown*1.35).clip(upper=90)
    tot=d.pown.sum(); d['own_900']=d.pown*900/tot if tot>0 else d.pown
    d['sl']=d.pos.map(slots); d['up']=(d.ls_ceil-d.ls_proj).clip(lower=0)
    return d.reset_index(drop=True)
def build(d,cfg,games):
    src=cfg['src']; proj=d[src]
    ownc='own_900' if cfg.get('own900') else 'own_x'; own=d[ownc]
    # role gate (current): sub-6500 needs min3>=24 (no starter info historically)
    drop=cfg.get('drop',set())
    if cfg['cons']=='current' and 'gate' not in drop: d=d[(d.salary>=6500)|(d.min3>=24)].reset_index(drop=True); proj=d[src]; own=d[ownc]
    big=games>=8
    top2={t:set(g.nlargest(2,'salary').index) for t,g in d.groupby('team')}
    top6=set(d.nlargest(6,'salary').index)
    built=[];expo={};scores=[];anchors=[]
    for n in range(4):
        m=pulp.LpProblem('x',pulp.LpMaximize)
        x={(i,s):pulp.LpVariable(f'x{i}_{s.replace("/","")}',cat='Binary') for i in d.index for s in d.sl[i]}
        y={i:pulp.lpSum(x[i,s] for s in d.sl[i]) for i in d.index}
        m+=pulp.lpSum((proj[i]+0.1*d.up[i])*y[i] for i in d.index)
        for s in SL: m+=pulp.lpSum(x[i,s] for i in d.index if s in d.sl[i])==NEED[s]
        for i in d.index: m+=y[i]<=1
        sal=pulp.lpSum(d.salary[i]*y[i] for i in d.index); m+=sal<=60000
        if cfg['cons']=='current':
            if 'floor' not in drop: m+=sal>=59500
            for t,g in d.groupby('team'):
                if 'team' not in drop: m+=pulp.lpSum(y[i] for i in g.index)<=3
                if 'sub5k' not in drop: m+=pulp.lpSum(y[i] for i in g.index if d.salary[i]<5000)<=2
                if big and 'top2' not in drop: m+=pulp.lpSum(y[i] for i in top2[t])<=1
            if 'contra' not in drop: m+=pulp.lpSum(y[i] for i in d.index if own[i]<10)<=(1 if big else 2)
        ov=cfg.get('overlap',6)
        for L in built: m+=pulp.lpSum(y[i] for i in L)<=ov
        ex=cfg.get('expo','current')
        for i,c in expo.items():
            if ex=='current':
                if c>=3 and own[i]<25: m+=y[i]==0
            elif ex=='gpt':
                cap=3 if (c>=2 and sum(1 for v in expo.values() if v>=3)<2) else 2
                if c>=cap: m+=y[i]==0
            elif ex=='gem':
                cap=3 if own[i]>=35 else (2 if own[i]>=15 else 1)
                if c>=cap: m+=y[i]==0
        if cfg.get('anchor'):
            for a in anchors: m+=y[a]==0  # distinct top-salary anchor per lineup
            for i in top6:
                if expo.get(i,0)>=2: m+=y[i]==0
        st=m.solve(pulp.PULP_CBC_CMD(msg=0,timeLimit=20))
        if st!=1: break
        ids=[i for i in d.index if pulp.value(y[i])>0.5]; built.append(ids)
        for i in ids: expo[i]=expo.get(i,0)+1
        anchors.append(max(ids,key=lambda i:d.salary[i]))
        scores.append(float(d.actual_fd_pts[ids].sum()))
    return scores
def optimal(d):
    m=pulp.LpProblem('o',pulp.LpMaximize)
    x={(i,s):pulp.LpVariable(f'x{i}_{s.replace("/","")}',cat='Binary') for i in d.index for s in d.sl[i]}
    y={i:pulp.lpSum(x[i,s] for s in d.sl[i]) for i in d.index}
    m+=pulp.lpSum(d.actual_fd_pts[i]*y[i] for i in d.index)
    for s in SL: m+=pulp.lpSum(x[i,s] for i in d.index if s in d.sl[i])==NEED[s]
    for i in d.index: m+=y[i]<=1
    m+=pulp.lpSum(d.salary[i]*y[i] for i in d.index)<=60000
    m.solve(pulp.PULP_CBC_CMD(msg=0,timeLimit=20)); return float(sum(d.actual_fd_pts[i] for i in d.index if pulp.value(y[i])>0.5))
CFG={
 'D0_cur_LS':dict(src='ls_proj',cons='current'),
 'D1_noGate':dict(src='ls_proj',cons='current',drop={'gate'}),
 'D2_noFloor':dict(src='ls_proj',cons='current',drop={'floor'}),
 'D3_noTeam':dict(src='ls_proj',cons='current',drop={'team','sub5k'}),
 'D4_noTop2':dict(src='ls_proj',cons='current',drop={'top2'}),
 'D5_noContra':dict(src='ls_proj',cons='current',drop={'contra'}),
 'D6_noGate_gemExpo':dict(src='ls_proj',cons='current',drop={'gate'},expo='gem',overlap=4),
}
slates=main.drop_duplicates('date')[['date','slate_games']]; slates=slates[slates.slate_games>=4].sort_values('date')
rows=[]
for _,r in slates.iterrows():
    dt=r.date; d=prep(dt)
    if len(d)<40 or d.actual_fd_pts.sum()==0: continue
    row=dict(date=dt,games=int(r.slate_games),n=len(d),opt=optimal(d))
    for name,cfg in CFG.items():
        s=build(d,cfg,int(r.slate_games))
        row[name+'_mean']=np.mean(s) if s else np.nan; row[name+'_best']=max(s) if s else np.nan; row[name+'_n']=len(s)
    rows.append(row); print(dt,row['games'],{c:round(row[c+'_mean'],1) for c in CFG},flush=True)
    pd.DataFrame(rows).to_csv(OUT+'b76b_results.csv',index=False)
print('DONE',len(rows))
