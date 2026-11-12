import pandas as pd, numpy as np, pulp
R='/tmp/claude-0/-home-claude/0af725b5-583a-505c-8506-bd4d1923ac69/scratchpad/r/'
df=pd.read_csv(R+'p1102.csv')
st=pd.read_csv('/mnt/user-data/uploads/136166-281367344.csv',encoding='utf-8-sig'); pts=st.dropna(subset=['Points']).Points.astype(float).values
ls=pd.read_csv('/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/linestar/live/2026-11-02_1515_players.csv')
spread=ls.groupby('team').line.first().to_dict()
df=df[(df.ls_proj>5)&~df.name.isin(['Joel Embiid','LaMelo Ball','Zach LaVine','Ben Sheppard'])].copy().reset_index(drop=True)
EXEMPT=set()
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
            pr+=pulp.lpSum(u[i] for i in d.index)<=(5 if t in EXEMPT else 3)
            pr+=pulp.lpSum(u[i] for i in d.index if df.at[i,'sal']<5000)<=(5 if t in EXEMPT else 2)
            pr+=pulp.lpSum(u[i] for i in d.index if i in top2)<=1
        for L in out: pr+=pulp.lpSum(u[i] for i in L)<=6
        pr.solve(pulp.PULP_CBC_CMD(msg=0)); out.append([i for i in df.index if u[i].value()>0.5])
    return out
def rep(name,col):
    Ls=build(col); a=[df.loc[L,'fp'].sum() for L in Ls]
    beat=[(pts<s).mean()*100 for s in a]; cash=sum(s>=355.2 for s in a)
    print(f"{name:42s} actual {np.mean(a):6.1f} (best {max(a):.1f})  median beat {np.median(beat):4.0f}%  cashes {cash}/6")
    return Ls

rep('E0 LineStar + our rules (Q excluded)','ls_proj')
EXEMPT.add('IND')
rep('E5 + IND exempt from team caps','ls_proj')
# IND 240 fill only for IND
df['p6']=df.ls_proj.copy()
av=df[df.team=='IND']; m=av.min3.fillna(0).copy(); need=240-m.sum()
while need>0.5:
    room=(40-m).clip(lower=0); o=room[room>0]
    if o.empty: break
    a=min(need/len(o),o.min()); m[o.index]+=a; need-=a*len(o)
df.loc[av.index,'p6']=np.maximum(av.ls_proj,av.rate.fillna(0.9)*m)
print(df.loc[av.index,['name','ls_proj','p6','fp']].round(1).to_string(index=False))
rep('E6 + IND exempt + IND minutes filled to 240','p6')
