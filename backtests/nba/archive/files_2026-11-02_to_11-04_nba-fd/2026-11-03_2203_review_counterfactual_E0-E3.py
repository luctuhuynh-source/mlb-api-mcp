import pandas as pd, numpy as np, pulp
R='/tmp/claude-0/-home-claude/0af725b5-583a-505c-8506-bd4d1923ac69/scratchpad/r/'
df=pd.read_csv(R+'p1102.csv')
st=pd.read_csv('/mnt/user-data/uploads/136166-281367344.csv',encoding='utf-8-sig'); pts=st.dropna(subset=['Points']).Points.astype(float).values
ls=pd.read_csv('/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/linestar/live/2026-11-02_1515_players.csv')
spread=ls.groupby('team').line.first().to_dict()
df=df[(df.ls_proj>5)].copy().reset_index(drop=True)
df['spread']=df.team.map(spread)
def elig(p):
    s=set(p.split('/')); e={'UTIL','UTIL2'}
    for x in s: e.add(x)
    if s&{'PG','SG','SF','PF'}: e.add('G/F')
    if s&{'SF','PF','C'}: e.add('F/C')
    return e
df['el']=df.pos.map(elig)
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL','UTIL2']
top2=set()
for t,d in df.groupby('team'): top2|=set(d.sort_values('sal',ascending=False).head(2).index)
def build(col,n=6):
    out=[]
    for k in range(n):
        pr=pulp.LpProblem('x',pulp.LpMaximize)
        x={(i,s):pulp.LpVariable(f'x{i}_{s.replace("/","")}',cat='Binary') for i in df.index for s in SL if s in df.at[i,'el']}
        u={i:pulp.lpSum(v for (j,s),v in x.items() if j==i) for i in df.index}
        pr+=pulp.lpSum(u[i]*df.at[i,col] for i in df.index)
        for s in SL: pr+=pulp.lpSum(v for (j,t),v in x.items() if t==s)==1
        for i in df.index: pr+=u[i]<=1
        pr+=pulp.lpSum(u[i]*df.at[i,'sal'] for i in df.index)<=60000
        for t,d in df.groupby('team'):
            pr+=pulp.lpSum(u[i] for i in d.index)<=3
            pr+=pulp.lpSum(u[i] for i in d.index if df.at[i,'sal']<5000)<=2
            pr+=pulp.lpSum(u[i] for i in d.index if i in top2)<=1
        for L in out: pr+=pulp.lpSum(u[i] for i in L)<=6
        pr.solve(pulp.PULP_CBC_CMD(msg=0)); out.append([i for i in df.index if u[i].value()>0.5])
    return out
def rep(name,col):
    Ls=build(col); a=[df.loc[L,'fp'].sum() for L in Ls]
    beat=[(pts<s).mean()*100 for s in a]; cash=sum(s>=355.2 for s in a)
    print(f"{name:42s} actual {np.mean(a):6.1f} (best {max(a):.1f})  median beat {np.median(beat):4.0f}%  cashes {cash}/6")
    return Ls
# E0 LineStar alone with our construction rules
rep('E0 LineStar proj + our rules','ls_proj')
# E1 blowout haircut: |spread|>=12 -> stars (proj>=30) x0.88, also nothing for bench
df['p1']=np.where((df.spread.abs()>=12)&(df.ls_proj>=30),df.ls_proj*0.88,df.ls_proj)
rep('E1 + blowout haircut (|spr|>=12)','p1')
# E2 depleted team fix: team with available min3 sum <200 -> fill to 240 equal-share among active rotation, cap 40
df['p2']=df.ls_proj.copy()
for t,d in df.groupby('team'):
    av=d[d.ls_proj>5]; tot=av.min3.fillna(0).sum()
    if tot<200:
        need=240-tot; m=av.min3.fillna(0).copy()
        while need>0.5:
            room=(40-m).clip(lower=0); open_=room[room>0]
            if open_.empty: break
            add=min(need/len(open_),open_.min()); m[open_.index]+=add; need-=add*len(open_)
        newp=m*av.rate.fillna(0.9)
        df.loc[av.index,'p2']=np.maximum(av.ls_proj,0.5*av.ls_proj+0.5*newp)
        print(f'  depleted team {t}: available recent minutes {tot:.0f} → filled to 240'); print(pd.DataFrame({'name':av.name,'min3':av.min3.round(0),'new_min':m.round(0),'ls':av.ls_proj,'p2':df.loc[av.index,'p2'].round(1),'actual':av.fp}).to_string(index=False))
rep('E2 + depleted-team 240 fill','p2')
df['p3']=np.where((df.spread.abs()>=12)&(df.p2>=30),df.p2*0.88,df.p2)
L=rep('E3 both fixes','p3')
for l in L[:2]: print('   ',[(df.at[i,'name'],int(df.at[i,'sal']),df.at[i,'fp']) for i in l])
# oracle: perfect projections, our rules
rep('ORACLE actual points + our rules','fp')
