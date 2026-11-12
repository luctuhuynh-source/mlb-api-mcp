import pandas as pd, numpy as np, re, pulp
from collections import Counter
R='/tmp/claude-0/-home-claude/0af725b5-583a-505c-8506-bd4d1923ac69/scratchpad/r/'
df=pd.read_csv(R+'p1102.csv')
st=pd.read_csv('/mnt/user-data/uploads/136166-281367344.csv',encoding='utf-8-sig')
ent=st.dropna(subset=['Points']).copy(); pts=ent.Points.astype(float).values
def parse(l): return [re.sub(r' \(.*\)','',re.sub(r'^[A-Z/]+ ','',p)) for p in l.split(', ')]
ent['pl']=ent.Lineup.map(parse)
idx=df.set_index('name')
me=ent[ent.EntryName.str.startswith('dalatcrew')].copy()
def lsum(L,c): return sum(idx.at[n,c] for n in L if n in idx.index and pd.notna(idx.at[n,c]))
print('=== OUR LINEUPS: LineStar projection at lock vs actual')
for _,r in me.iterrows():
    print(f"{r.EntryName:16s} LSproj {lsum(r.pl,'ls_proj'):6.1f}  actual {r.Points:6.1f}  diff {r.Points-lsum(r.pl,'ls_proj'):+6.1f}  projown {lsum(r.pl,'proj_owned'):5.0f}%")
our=Counter(n for L in me.pl for n in L)
print('\n=== OUR PLAYERS: proj vs actual, minutes')
t=idx.loc[list(our)].copy(); t['exp']=[our[n] for n in t.index]
t['miss']=t.fp-t.ls_proj; t['exp_miss']=t.miss*t.exp
print(t[['exp','sal','ls_proj','fp','miss','exp_miss','min3','act_min','own','proj_owned']].sort_values('exp_miss').round(1).to_string())
print('total exposure-weighted miss vs LineStar:',round(t.exp_miss.sum(),1),'over 6 lineups =',round(t.exp_miss.sum()/6,1),'per lineup')
# field top-100 & top-1%
top=ent.head(int(len(ent)*0.01))
print(f'\n=== FIELD: top1% n={len(top)} line {top.Points.astype(float).min()}; cash~ {np.percentile(pts,78):.1f}')
for name,grp in [('top1%',top),('ours',me),('field',ent)]:
    print(f"{name:6s} LSproj {np.mean([lsum(L,'ls_proj') for L in grp.pl]):.1f}  actual {grp.Points.astype(float).mean():.1f}  own {np.mean([lsum(L,'own') for L in grp.pl]):.0f}%  stud$≥9k {np.mean([sum(idx.at[n,'sal']>=9000 for n in L if n in idx.index) for L in grp.pl]):.2f}  sub$4.5k {np.mean([sum(idx.at[n,'sal']<=4500 for n in L if n in idx.index) for L in grp.pl]):.2f}  mid$5-7k {np.mean([sum((idx.at[n,'sal']>=5000)&(idx.at[n,'sal']<7000) for n in L if n in idx.index) for L in grp.pl]):.2f}")
# biggest beats/misses vs LineStar on slate
df['miss']=df.fp-df.ls_proj
print('\n=== SLATE BIGGEST BEATS (actual - LS proj)'); print(df.sort_values('miss',ascending=False)[['name','team','sal','ls_proj','fp','miss','min3','act_min','own','proj_owned']].head(15).round(1).to_string(index=False))
print('\n=== SLATE BIGGEST MISSES'); print(df[df.own>3].sort_values('miss')[['name','team','sal','ls_proj','fp','miss','min3','act_min','own','proj_owned']].head(12).round(1).to_string(index=False))
# LineStar ownership accuracy on the slate's chalk
print('\nprojown vs real own corr', round(df[['proj_owned','own']].corr().iloc[0,1],2))
print(df[df.own>=25][['name','sal','proj_owned','own']].sort_values('own',ascending=False).to_string(index=False))
