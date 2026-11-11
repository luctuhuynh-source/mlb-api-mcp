"""Week 8 prep: FD pool + lines + LineStar + nflverse role gate + salary formula.
Writes /home/claude/wk8/pool.csv (one row per FD player)."""
import pandas as pd, numpy as np, json, gzip, glob, re, os, sys

WK = '/home/claude/wk8'
POOL = '/mnt/user-data/attachments/d96743da-8be9-5bb5-9072-0f05208cdafb/34698ffd-FanDuel-NFL-2026_PST-11_PST-01_PST-135859-players-list-1.csv'
LS_DIR = '/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nfl/linestar/raw'
SLATE_ID = 135859

# ---- lines (Odds API consensus pulled 15:19Z) : home spread (negative = home fav), total
LINES = {  # away, home : (home_spread, total)
 ('ARI','DAL'): (-7.0, 54.5), ('ATL','TB'): (-2.0, 43.0), ('BAL','BUF'): (-3.0, 54.5),
 ('TEN','CIN'): (-13.0, 46.0), ('CLE','PIT'): (-3.5, 39.0), ('MIN','DET'): (-3.5, 46.0),
 ('IND','JAC'): (-10.0, 46.5), ('LV','NYJ'): (-2.0, 46.5), ('LAC','LAR'): (-6.5, 45.5),
 ('KC','DEN'): (1.0, 41.5), ('NE','MIA'): (7.0, 41.5)}
games = []
for (a,h),(hs,t) in LINES.items():
    itt_h = (t - hs)/2; itt_a = (t + hs)/2   # hs negative => home favoured => itt_h = (t+|hs|)/2
    games.append(dict(game=f'{a}@{h}', away=a, home=h, home_spread=hs, total=t, itt_home=itt_h, itt_away=itt_a))
G = pd.DataFrame(games)
ITT = {}; TOT={}; SPR={}
for g in games:
    ITT[g['home']] = g['itt_home']; ITT[g['away']] = g['itt_away']
    TOT[g['home']] = TOT[g['away']] = g['total']
    SPR[g['home']] = g['home_spread']; SPR[g['away']] = -g['home_spread']

# ---- FD pool
p = pd.read_csv(POOL)
p = p.rename(columns={'Id':'id','Position':'pos','Nickname':'name','Salary':'salary','Team':'team','Opponent':'opp',
                      'Injury Indicator':'inj','FPPG':'fppg','Played':'played','Game':'game'})
p = p[['id','pos','name','salary','team','opp','inj','Injury Details','fppg','played','game']]
p['inj'] = p['inj'].fillna('')
KEEP_OUT={'Emeka Egbuka','Carnell Tate','Brian Robinson Jr.','Tyjae Spears','KaVontae Turpin','Anthony Gould'}
p.loc[p['name'].isin(KEEP_OUT),'inj']='O'
p['itt'] = p['team'].map(ITT); p['total']=p['team'].map(TOT); p['spread']=p['team'].map(SPR); p['opp_itt']=p['opp'].map(ITT)
assert p['itt'].notna().all(), p[p['itt'].isna()].head()

def norm(n):
    n = str(n).lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return ' '.join(n.split())
p['key'] = p['name'].map(norm)

# ---- salary formula (saved backtest coefficients, per $1k over $3k) x ITT scaling
MULT = {'QB':2.65,'RB':2.15,'WR':2.0,'TE':1.75}
def salproj(r):
    if r['pos']=='D': return np.nan
    base = MULT[r['pos']] * max(r['salary']-3000, 0)/1000
    return base * (r['itt']/22.5)**0.7
p['proj_sal'] = p.apply(salproj, axis=1)
# D-ST: opp implied total map (qualitative scale used by the builder)
p.loc[p['pos']=='D','proj_sal'] = (30 - p.loc[p['pos']=='D','opp_itt']).clip(lower=2)*0.55

# ---- LineStar (latest raw file, Main slate rows)
files = sorted(glob.glob(f'{LS_DIR}/*.json.gz'))
lsf = '/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nfl/linestar/live/2026-11-01_0925_raw.json.gz'
d = json.load(gzip.open(lsf,'rt'))
sc = json.loads(d.get('SalaryContainerJson') or '{}')
rows=[]
for s in sc.get('Salaries', []):
    rows.append(dict(ls_name=s.get('Name'), ls_pos=s.get('POS'), ls_team=s.get('PTEAM'), ls_sal=s.get('SAL'),
                     ls_proj=s.get('PP'), ls_floor=s.get('Floor'), ls_ceil=s.get('Ceil'), ls_stat=s.get('STAT'), sid=s['Id'], ls_gi=s.get('GI')))
L = pd.DataFrame(rows)
own = {}
for od in (d.get('Ownership') or {}).get('Projected',{}).get('10751', []) or []:
    own[od['SalaryId']] = od.get('Owned')
L['ls_own'] = L['sid'].map(own)
L['key'] = L['ls_name'].map(norm)
L.loc[L['ls_pos']=='D','key'] = L.loc[L['ls_pos']=='D','ls_team'].map(lambda t: 'D_'+str(t))
p.loc[p['pos']=='D','key'] = 'D_'+p.loc[p['pos']=='D','team']
L = L.drop_duplicates('key')
p = p.merge(L[['key','ls_proj','ls_floor','ls_ceil','ls_own','ls_stat','ls_sal','ls_team']], on='key', how='left')
p['ls_file'] = os.path.basename(lsf)

# ---- nflverse role gate: trailing-2 games played (weeks <= 7, regular season)
nv = pd.read_csv(f'{WK}/nflverse/stats_player_week_2026.csv')
nv = nv[(nv['season_type']=='REG') & (nv['week']<=7)]
nv['key'] = nv['player_display_name'].map(norm)
nv = nv.sort_values('week')
last2 = nv.groupby('key').tail(2)
agg = last2.groupby('key').agg(wopr2=('wopr','mean'), tshare2=('target_share','mean'), carries2=('carries','sum'),
                               tgts2=('targets','sum'), nvteam=('team','last'), nvpos=('position','last'), ngames=('week','count'))
# team carry share: player carries / team carries over the same games
tc = last2.groupby(['team','week'])['carries'].sum().rename('team_carries').reset_index()
l2 = last2.merge(tc, on=['team','week'])
cs = l2.groupby('key').apply(lambda x: x['carries'].sum()/max(x['team_carries'].sum(),1)).rename('carry_share2')
agg = agg.join(cs)
p = p.merge(agg, on='key', how='left')

p.to_csv(f'{WK}/pool.csv', index=False)
G.to_csv(f'{WK}/games.csv', index=False)
print('LineStar file:', lsf)
print('pool', len(p), 'with LS proj', p['ls_proj'].notna().sum(), 'with LS own', p['ls_own'].notna().sum())
print('nflverse matched', p['ngames'].notna().sum())
print(G.sort_values('total', ascending=False).to_string(index=False))
