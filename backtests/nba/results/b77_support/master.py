"""Master player-slate table: LineStar final history + point-in-time game-log features + ownership."""
import pandas as pd, numpy as np, re, unicodedata
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/'
def k(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); s=re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s); return re.sub(r'[^a-z]','',s)
P=pd.read_csv('hist_players.csv'); P['k']=P.name.map(k)
G=pd.concat([pd.read_csv(R+f'nba_player_games_{s}.csv') for s in ['2024-25','2025-26','2026-27']])
G=G[~G.did_not_play.astype(str).eq('True')&(G.minutes>0)].copy(); G['k']=G.athlete_display_name.map(k)
G=G.sort_values(['k','game_date']).reset_index(drop=True)
g=G.groupby('k')
G['l5']=g.fd_pts.transform(lambda x:x.rolling(5,min_periods=1).mean())
G['l10']=g.fd_pts.transform(lambda x:x.rolling(10,min_periods=1).mean())
G['min3']=g.minutes.transform(lambda x:x.rolling(3,min_periods=1).mean())
G['min10']=g.minutes.transform(lambda x:x.rolling(10,min_periods=1).mean())
G['sd10']=g.fd_pts.transform(lambda x:x.rolling(10,min_periods=4).std())
G['gp']=g.cumcount()+1
G['gdate']=pd.to_datetime(G.game_date); P['pdate']=pd.to_datetime(P.date)
# alias fixes for common name mismatches: map unmatched LineStar keys to game-log keys by last-name+first-initial when unique
gk=set(G.k); miss=sorted(set(P[P.ls_proj>0].k)-gk)
import collections
bylast=collections.defaultdict(set)
for n in G.athlete_display_name.unique():
    p=n.split(); 
    if len(p)>=2: bylast[(k(p[-1]) if p[-1].lower().strip('.') not in ('jr','sr','ii','iii','iv') else k(p[-2]), n[0].lower())].add(k(n))
alias={}
for n in P[P.k.isin(miss)].name.unique():
    p=n.split()
    if len(p)<2: continue
    last=k(p[-1]) if p[-1].lower().strip('.') not in ('jr','sr','ii','iii','iv') else k(p[-2])
    c=bylast.get((last,n[0].lower()),set())
    if len(c)==1: alias[k(n)]=list(c)[0]
print('unmatched keys',len(miss),'aliased',len(alias),list(alias.items())[:12])
alias['carltoncarrington']='bubcarrington'; P['gk']=P.k.map(lambda x:alias.get(x,x))
M=pd.merge_asof(P.sort_values('pdate'),G[['k','gdate','l5','l10','min3','min10','sd10','gp']].rename(columns={'k':'gk'}).sort_values('gdate'),
                left_on='pdate',right_on='gdate',by='gk',allow_exact_matches=False)
M['days_since']=(M.pdate-M.gdate).dt.days
pr=M[M.ls_proj>0]; print('proj>0 rows',len(pr),'with l5',pr.l5.notna().mean().round(4),'main',pr[pr.in_main==1].l5.notna().mean().round(4))
print('unmatched proj>0 main rows by name (top):',pr[(pr.in_main==1)&pr.l5.isna()].name.value_counts().head(15).to_dict())
M.drop(columns=['pdate','gdate']).to_pickle('master.pkl'); print(M.shape, M.date.min(), M.date.max())
