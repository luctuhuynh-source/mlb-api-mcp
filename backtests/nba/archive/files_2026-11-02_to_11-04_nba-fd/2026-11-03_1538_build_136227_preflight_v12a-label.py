import pandas as pd, numpy as np, pulp, re, sys, json
from collections import Counter, defaultdict
D='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/'
PL='/mnt/user-data/attachments/0af725b5-583a-505c-8506-bd4d1923ac69/fbd9793b-FanDuel-NBA-2026_PST-11_PST-04_PST-136227-players-list.csv'
TPL='/mnt/user-data/attachments/0af725b5-583a-505c-8506-bd4d1923ac69/df0bd579-FanDuel-NBA-2026-11-04-136227-entries-upload-template.csv'
OUT='/tmp/claude-0/-home-claude/0af725b5-583a-505c-8506-bd4d1923ac69/scratchpad/'
N_LINEUPS=int(sys.argv[1]) if len(sys.argv)>1 else 4

fd=pd.read_csv(PL)
fd=fd[['Id','Position','Nickname','FPPG','Played','Salary','Game','Team','Opponent','Injury Indicator','Injury Details','Roster Position']]
fd.columns=['id','pos','name','fppg','played','salary','game','team','opp','inj','injd','rpos']
fd['inj']=fd['inj'].fillna('')
# game tip order (ET): 4:00 PT = PHI@DET, ATL@WAS ; 4:30 = MIL@BOS, CHA@BKN, CHI@NY ; 5:00 = IND@MEM, UTA@NO, CLE@OKC
tip={'PHI@DET':0,'ATL@WAS':0,'MIL@BOS':1,'CHA@BKN':1,'CHI@NY':1,'IND@MEM':2,'UTA@NO':2,'CLE@OKC':2}
fd['tip']=fd['game'].map(tip)

# ---- ESPN injury report overrides (pulled 11/3 3:34 PM PT) beyond the FD flags
espn_out={'Jock Landale','Mouhamed Gueye','Henri Veesaar','Devin Carter','Egor Demin','Tyler Bilodeau','Grant Williams','Jaylon Tyson','Peyton Watson','Isaiah Joe','Jalen Duren','T.J. McConnell','Ivica Zubac','Johnny Furphy','Ben Sheppard','Tyrese Haliburton','Scotty Pippen','Yves Missi','Nikola Topic','Thomas Sorber','Cason Wallace','Chet Holmgren','Jalen Williams','Dominick Barlow','Ariel Hukporti','Jusuf Nurkic','Jaren Jackson','Trey Alexander','Reece Beekman','Tristan Vukcevic','Justin Champagnie','Jamir Watkins'}
espn_q={'Jalen Johnson','Payton Pritchard','Jayson Tatum','Nic Claxton','Josh Hart','Jaylin Williams','Mo Bamba','Alex Sarr','Anthony Gill','Kelly Oubre','Larry Nance','Obi Toppin'}
espn_p={'Kon Knueppel','Coby White','Jalen Smith','Jordan Poole','Trey Murphy','Pascal Siakam','Aaron Nesmith','Andrew Nembhard','Quinten Post'}
def status(r):
    if r['name'] in espn_out or r.inj=='O': return 'O'
    if r['name'] in espn_q or r.inj=='Q': return 'Q'
    if r['name'] in espn_p or r.inj=='P': return 'P'
    return ''
fd['st']=fd.apply(status,axis=1)

# ---- game logs
g=pd.concat([pd.read_csv(D+'nba_player_games_2025-26.csv'),pd.read_csv(D+'nba_player_games_2026-27.csv')])
g['game_date']=pd.to_datetime(g['game_date'])
def norm(s): return re.sub(r'[^a-z]','',str(s).lower().replace('jr','').replace('iii','').replace('ii',''))
g['key']=g['athlete_display_name'].map(norm)
fd['key']=fd['name'].map(norm)
cur=g[g.season==g.season.max()] if g.season.dtype!=object else g[g.season==sorted(g.season.unique())[-1]]
prev=g[g.season!=cur.season.iloc[0]]
cur=cur.sort_values('game_date')
print('logs through',cur.game_date.max().date(), 'season',cur.season.iloc[0])
played=cur[(cur.did_not_play!=True)&(cur.minutes>0)]
agg={}
for k,df in played.groupby('key'):
    df=df.sort_values('game_date')
    mins=df.minutes.values; fp=df.fd_pts.values
    agg[k]=dict(gp=len(df),smin=mins.sum(),rate=fp.sum()/mins.sum(),
               rate5=fp[-5:].sum()/mins[-5:].sum(),min3=mins[-3:].mean(),min5=mins[-5:].mean(),
               minhi=mins.max(),start_last=bool(df.starter.values[-1]),starts=int(df.starter.sum()),
               minlast=mins[-1])
pv={}
for k,df in prev[(prev.did_not_play!=True)&(prev.minutes>0)].groupby('key'):
    pv[k]=dict(smin=df.minutes.sum(),rate=df.fd_pts.sum()/df.minutes.sum())
posavg=played.groupby('athlete_position_abbreviation').apply(lambda d:d.fd_pts.sum()/d.minutes.sum()).to_dict()

# ---- LineStar
ls=pd.read_csv(D+'linestar/live/2026-11-03_1515_players.csv'); ls['key']=ls['name'].map(norm)
po=pd.read_csv(D+'linestar/live/2026-11-03_1515_projown.csv'); po=po[po.slate==30497]; po['key']=po['name'].map(norm)
fd=fd.merge(ls[['key','ls_proj','ls_floor','ls_ceil','line','total']],on='key',how='left').merge(po[['key','proj_owned']],on='key',how='left')
print('LineStar matched',fd.ls_proj.notna().sum(),'of',len(fd),'| projown rows',fd.proj_owned.notna().sum())

# ---- engine projection: minutes (starters-first vacated) x shrunk rate
rows=[]
for _,r in fd.iterrows():
    a=agg.get(r.key); p=pv.get(r.key)
    prior=p['rate'] if p else posavg.get(r.pos.split('/')[0],0.9)
    if a:
        rate=(a['smin']*a['rate']+250*prior)/(a['smin']+250)
        rate5=(min(a['smin'],5*a['min5'])*a['rate5']+250*prior)/(min(a['smin'],5*a['min5'])+250)
        base_min=a['min3']; rec_min=0.6*a['min3']+0.4*a['minlast']
    else:
        rate=prior; rate5=prior; base_min=0; rec_min=0
    rows.append(dict(rate=rate,rate5=rate5,base_min=base_min,rec_min=rec_min,
                     minhi=a['minhi'] if a else 0,start=a['start_last'] if a else False,gp=a['gp'] if a else 0,starts=a['starts'] if a else 0))
fd=pd.concat([fd.reset_index(drop=True),pd.DataFrame(rows)],axis=1)
avail=fd.st.isin(['','P'])
fd.loc[fd.st=='O',['base_min','rec_min']]=0  # Q players keep their minutes (not vacated pre-flight), just not rostered
# vacated minutes: per team, if avail minutes <240 give to starters (cap 36) then bench (cap minhi)
for col in ['base_min','rec_min']:
    for t,df in fd[fd.st!='O'].groupby('team'):
        tot=df[col].sum(); need=240-tot
        if need<=2:
            if tot>245: fd.loc[df.index,col]*=240/tot
            continue
        st=df[df.start].sort_values(col,ascending=False)
        for i in st.index:
            room=36-fd.at[i,col]
            if room>0 and need>0: add=min(room,need); fd.at[i,col]+=add; need-=add
        be=df[~df.start].sort_values(col,ascending=False)
        for i in be.index:
            room=max(fd.at[i,'minhi'],fd.at[i,col]+6)-fd.at[i,col]
            if room>0 and need>0: add=min(room,need); fd.at[i,col]+=add; need-=add
fd['eng']=fd.base_min*fd.rate; fd['eng_rec']=fd.rec_min*fd.rate5
fd['proj']=np.where(fd.ls_proj.notna(),0.7*fd.ls_proj+0.3*fd.eng,fd.eng)
fd['proj_rec']=np.where(fd.ls_proj.notna(),0.7*fd.ls_proj+0.3*fd.eng_rec,fd.eng_rec)
fd['sd']=np.where(fd.ls_ceil.notna(),(fd.ls_ceil-fd.ls_floor)/3.3,fd.proj*0.3)
fd['own']=(fd.proj_owned.fillna(2)*1.35).clip(upper=95)
fd['x']=fd.proj/(fd.salary/1000)
# role gate: <=6500 needs confirmed role = started last game or >=20 min in last-3 avg
fd['role_ok']=(fd.salary>6500)|(fd.start)|(fd.base_min>=20)
pool=fd[avail&fd.role_ok&(fd.proj>8)].copy()
pool.loc[pool.gp==0,'proj']*=0.7  # rookies/no-log shrink
print('pool',len(pool))

# slots
SLOTS=['PG','SG','SF','PF','C','G/F','F/C','UTIL','UTIL2']
def elig(rp):
    toks=rp.split('/'); s=set(); i=0
    while i<len(toks):
        t=toks[i]
        if t in('G','F') and i+1<len(toks) and toks[i+1] in('F','C') and t+'/'+toks[i+1] in('G/F','F/C'):
            s.add(t+'/'+toks[i+1]); i+=2
        else: s.add(t); i+=1
    if 'UTIL' in s: s.add('UTIL2')
    return s
pool['elig']=pool.rpos.map(elig)
pool=pool.reset_index(drop=True)
top2=set()
for t,df in pool.groupby('team'): top2|=set(df.sort_values('salary',ascending=False).head(2).index)

def build(prev_lineups,objcol,contr_used,forced=set()):
    prob=pulp.LpProblem('fd',pulp.LpMaximize)
    x={(i,s):pulp.LpVariable(f'x_{i}_{s}',cat='Binary') for i in pool.index for s in SLOTS if s in pool.at[i,'elig']}
    use={i:pulp.lpSum(x[i,s] for s in SLOTS if (i,s) in x) for i in pool.index}
    prob+=pulp.lpSum(use[i]*(pool.at[i,objcol]-0.1*pool.at[i,'sd']) for i in pool.index)
    for s in SLOTS: prob+=pulp.lpSum(x[i,s] for i in pool.index if (i,s) in x)==1
    for i in pool.index: prob+=use[i]<=1
    prob+=pulp.lpSum(use[i]*pool.at[i,'salary'] for i in pool.index)<=60000
    prob+=pulp.lpSum(use[i]*pool.at[i,'salary'] for i in pool.index)>=59500
    for t,df in pool.groupby('team'):
        prob+=pulp.lpSum(use[i] for i in df.index)<=3
        prob+=pulp.lpSum(use[i] for i in df.index if pool.at[i,'salary']<5000)<=2
        prob+=pulp.lpSum(use[i] for i in df.index if i in top2)<=1
    # contrarian: adj own < 8% -> <=1 per lineup; player cap 2 of N across set
    contr=[i for i in pool.index if pool.at[i,'own']<8]
    prob+=pulp.lpSum(use[i] for i in contr)<=1
    for i in contr:
        if contr_used[i]>=2: prob+=use[i]==0
    for L in prev_lineups: prob+=pulp.lpSum(use[i] for i in L)<=6
    for i in forced: prob+=use[i]==1
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return [i for i in pool.index if use[i].value()>0.5]

lineups=[]; contr_used=Counter()
# shadow: one lineup carries the highest-projected anchor
anchor=pool.sort_values('proj',ascending=False).index[0]
for k in range(N_LINEUPS):
    objcol='proj' if k<N_LINEUPS//2 else 'proj_rec'
    L=build(lineups,objcol,contr_used,forced={anchor} if k==0 else set())
    lineups.append(L)
    for i in L:
        if pool.at[i,'own']<8: contr_used[i]+=1

# slot assignment with late-swap placement: earliest tips in fixed slots, latest in G/F,F/C,UTIL
def assign(L):
    best=None
    import itertools
    Ls=sorted(L,key=lambda i:-pool.at[i,'tip'])
    # try to put high-tip players into flex slots: brute force assignment via matching
    for perm in itertools.permutations(L):
        ok=all(SLOTS[j] in pool.at[perm[j],'elig'] for j in range(9))
        if not ok: continue
        score=sum(pool.at[perm[j],'tip'] for j in range(5,9))
        if best is None or score>best[0]: best=(score,perm)
    return best[1]

import csv
with open(TPL,newline='') as f: rows_=list(csv.reader(f))
hdr=rows_[0]; entries=pd.DataFrame([r for r in rows_[1:] if r and re.match(r'^\d+$',r[0])])
out=[hdr[:13]]
report=[]
for k,L in enumerate(lineups):
    perm=assign(L); row=entries.iloc[k].tolist()[:4]+[f"{pool.at[i,'id']}:{pool.at[i,'name']}" for i in perm]
    out.append(row)
    sal=sum(pool.at[i,'salary'] for i in L); pr=sum(pool.at[i,'proj'] for i in L); ow=sum(pool.at[i,'own'] for i in L)
    report.append((k+1,sal,pr,ow,[(SLOTS[j].replace('UTIL2','UTIL'),pool.at[perm[j],'name'],pool.at[perm[j],'team'],int(pool.at[perm[j],'salary']),round(pool.at[perm[j],'proj'],1),round(pool.at[perm[j],'own'],0),pool.at[perm[j],'st']) for j in range(9)]))
pd.DataFrame(out).to_csv(OUT+'FanDuel-NBA-136227-upload.csv',index=False,header=False)
for k,sal,pr,ow,ps in report:
    print(f'\nL{k}  ${sal:,}  proj {pr:.1f}  cum-own {ow:.0f}%')
    for p in ps: print('  ',p)
exp=Counter(i for L in lineups for i in L)
print('\nEXPOSURE:');
for i,c in exp.most_common(): print(f"  {pool.at[i,'name']:26s} {c}/{N_LINEUPS}  own {pool.at[i,'own']:.0f}%  proj {pool.at[i,'proj']:.1f} LS {pool.at[i,'ls_proj']} eng {pool.at[i,'eng']:.1f} min {pool.at[i,'base_min']:.0f} ${int(pool.at[i,'salary'])} {pool.at[i,'st']}")
ov=max(len(set(a)&set(b)) for a in lineups for b in lineups if a is not b); print('max overlap',ov)
pool.sort_values('proj',ascending=False)[['name','team','salary','proj','ls_proj','eng','base_min','own','x','st']].head(40).to_csv(OUT+'pool_top.csv',index=False)
print(pool.sort_values('x',ascending=False)[['name','team','salary','proj','ls_proj','eng','base_min','own','x','st']].head(25).to_string())
print(fd[fd.st=='Q'][['name','team','salary','ls_proj']].to_string())
