"""v1.7 build: props projection + LineStar + salary formula (1/3 each), v1.6 shadow (props+salary 50/50).
Usage: python3 -I build.py [v17|v16] [PER_QB]"""
import pandas as pd, numpy as np, json, glob, re, sys, math, itertools
import pulp
WK='/home/claude/wk8'
MODE = sys.argv[1] if len(sys.argv)>1 else 'v17'
PER_QB = int(sys.argv[2]) if len(sys.argv)>2 else 5

def norm(n):
    n = str(n).lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return ' '.join(n.split())
def imp(price):
    price=float(price)
    return 100/(price+100) if price>0 else -price/(-price+100)

# ---------- props -> FD points
MK = ['player_pass_yds','player_pass_tds','player_rush_yds','player_reception_yds','player_receptions','player_anytime_td']
rows=[]
for f in glob.glob(f'{WK}/props/*.json'):
    d=json.load(open(f))
    for g in d['games']:
        for b in g['books']:
            for m in b['markets']:
                for o in m['outcomes']:
                    rows.append(dict(game=g['away']+'@'+g['home'], book=b['key'], mkt=m['key'], side=o['name'],
                                     price=o['price'], point=o['point'], player=o.get('description')))
P = pd.DataFrame(rows)
P['key']=P['player'].map(norm)
# main line per player/market/book: the Over whose price is nearest -110 (books post one line each; keep Over rows)
ov = P[P['side'].isin(['Over','Yes'])].copy()
ov['dist'] = (ov['price'].astype(float)+110).abs()
main = ov[ov['mkt']!='player_anytime_td'].sort_values('dist').groupby(['key','mkt','book']).head(1)
lines = main.groupby(['key','mkt'])['point'].median().unstack()
# anytime TD prob: median implied prob across books, single-sided haircut 0.92
td = ov[ov['mkt']=='player_anytime_td'].groupby('key')['price'].apply(lambda s: np.median([imp(x) for x in s]))*0.92
td = td.clip(upper=0.97)
proj = pd.DataFrame(index=lines.index.union(td.index))
for c in MK[:-1]:
    proj[c] = lines[c] if c in lines else np.nan
proj['p_td'] = td
proj = proj.fillna({c:0 for c in MK[:-1]}).fillna({'p_td':0})
proj['e_td'] = -np.log(1-proj['p_td'].clip(upper=0.97))
proj['fp_props'] = (0.04*proj['player_pass_yds'] + 4*proj['player_pass_tds'] + 0.1*proj['player_rush_yds']
                    + 0.1*proj['player_reception_yds'] + 0.5*proj['player_receptions'] + 6*proj['e_td'])
proj.loc[proj['player_pass_yds']>0,'fp_props'] -= 0.6   # INT drag for QBs
# a player counts as "priced" only with a yardage/reception line (TD-only = unpriced, per 10/31 sed edit)
proj['priced'] = (proj[MK[:-1]].sum(axis=1)>0)
nbooks = ov.groupby('key')['book'].nunique()
proj['nbooks']=nbooks

# ---------- pool
p = pd.read_csv(f'{WK}/pool.csv')
p = p.merge(proj[['fp_props','priced','nbooks','p_td']], left_on='key', right_index=True, how='left')
p['priced']=p['priced'].fillna(False).astype(bool)
# D-ST projection: shared across arms (opp implied total based), labelled VEGAS-DERIVED
p.loc[p['pos']=='D','fp_props'] = p.loc[p['pos']=='D','proj_sal']
p.loc[p['pos']=='D','priced']=True
# blend
if MODE=='v17':
    def blend(r):
        parts=[r['fp_props'], r['ls_proj'], r['proj_sal']]
        if r['pos']=='D': return r['proj_sal'] if pd.isna(r['ls_proj']) else 0.5*r['proj_sal']+0.5*r['ls_proj']
        parts=[x for x in parts if pd.notna(x)]
        return float(np.mean(parts)) if parts else np.nan
else:
    def blend(r):
        if r['pos']=='D': return r['proj_sal']
        parts=[x for x in [r['fp_props'], r['proj_sal']] if pd.notna(x)]
        return float(np.mean(parts)) if parts else np.nan
p['proj']=p.apply(blend,axis=1)

# ---------- eligibility
OUT = p['inj'].isin(['O','IR','NA','D'])
elig = p[(~OUT) & p['priced'] & p['proj'].notna()].copy()
# WR/TE $4,500 floor, RB $4,000 (all)
elig = elig[~((elig['pos'].isin(['WR','TE'])) & (elig['salary']<4500))]
# zero-ish LineStar projection (not expected to play) -> drop skill players
elig = elig[~((elig['pos']!='D') & (elig['ls_proj'].fillna(1)<=0.5))]
unpriced_excluded = p[(~OUT)&(~p['priced'])&(p['pos']!='D')&(p['salary']>=5000)][['name','pos','team','salary']]
# role gate (v1.4): WR/TE in the QB stack need wopr2>=0.30 or tshare2>=0.18; RB carry_share2>=0.35 unless starter out.
# ungated if no nflverse rows. Applied as: stack-eligible flags; RB gate applied to all RBs (starter-out exceptions listed manually).
RB_EXCEPT = set()   # names allowed despite carry share (replacement RBs confirmed out ahead) — fill after inactives
elig['stack_ok'] = (elig['ngames'].isna()) | (elig['wopr2']>=0.30) | (elig['tshare2']>=0.18)
rb_gate = (elig['pos']!='RB') | elig['ngames'].isna() | (elig['carry_share2']>=0.35) | elig['name'].isin(RB_EXCEPT)
rb_dropped = elig[(elig['pos']=='RB') & ~rb_gate][['name','team','salary','carry_share2','proj']]
elig = elig[rb_gate].copy()

# ---------- QB selection (v1.6 rule)
q = elig[(elig['pos']=='QB')&(elig['salary'].between(6800,8300))].copy()
q['qscore'] = q['itt'] + 0.4*q['total'] - 1.5*np.maximum(0, q['salary']-7600)/1000
q = q.sort_values('qscore', ascending=False)
qbs=[]; used_games=set()
for _,r in q.iterrows():
    if r['game'] in used_games: continue
    qbs.append(r['name']); used_games.add(r['game'])
    if len(qbs)==3: break
qbtab = q[['name','team','salary','itt','total','qscore','proj','ls_proj','fp_props','proj_sal']].head(8)

# ---------- ILP builder
N = 3*PER_QB
EXP_CAP = 7; PAIR_CAP = 6; OVERLAP = 5
elig = elig.reset_index(drop=True)
idx = {r['id']:i for i,r in elig.iterrows()}
def build_one(qb_name, prev, exposure, pairs):
    m = pulp.LpProblem('fd', pulp.LpMaximize)
    x = {i: pulp.LpVariable(f'x{i}', cat='Binary') for i in elig.index}
    # slots: we model FLEX=RB => RB count 3, WR 3, TE 1, QB 1, D 1
    pos = elig['pos']
    m += pulp.lpSum(x[i]*elig.loc[i,'proj'] for i in x)
    m += pulp.lpSum(x[i] for i in x if pos[i]=='QB')==1
    m += pulp.lpSum(x[i] for i in x if pos[i]=='RB')==3
    m += pulp.lpSum(x[i] for i in x if pos[i]=='WR')==3
    m += pulp.lpSum(x[i] for i in x if pos[i]=='TE')==1
    m += pulp.lpSum(x[i] for i in x if pos[i]=='D')==1
    m += pulp.lpSum(x[i]*elig.loc[i,'salary'] for i in x) <= 60000
    m += pulp.lpSum(x[i]*elig.loc[i,'salary'] for i in x) >= 59500
    m += pulp.lpSum(x[i]*elig.loc[i,'salary'] for i in x if pos[i]=='RB') >= 20000
    qi = elig.index[elig['name']==qb_name][0]; m += x[qi]==1
    qteam = elig.loc[qi,'team']
    # stack: >=1 same-team WR/TE that passes the role gate
    m += pulp.lpSum(x[i] for i in x if pos[i] in ('WR','TE') and elig.loc[i,'team']==qteam and elig.loc[i,'stack_ok'])>=1
    # bring-back catchers must pass role gate too (any opp WR/TE used must be stack_ok)
    for i in x:
        if pos[i] in ('WR','TE') and elig.loc[i,'team']==elig.loc[qi,'opp'] and not elig.loc[i,'stack_ok']:
            m += x[i]==0
    # D-ST negative correlation: no offensive player from the D's opponent
    for i in x:
        if pos[i]=='D':
            for j in x:
                if pos[j]!='D' and elig.loc[j,'team']==elig.loc[i,'opp']:
                    m += x[i]+x[j]<=1
    # FD: max 4 per team, >=3 teams (approx via max 4)
    for t in elig['team'].unique():
        m += pulp.lpSum(x[i] for i in x if elig.loc[i,'team']==t)<=4
    # anti-stack (A96): no two RBs same game
    for g in elig['game'].unique():
        m += pulp.lpSum(x[i] for i in x if pos[i]=='RB' and elig.loc[i,'game']==g)<=1
    # portfolio caps
    for i in x:
        if pos[i]!='QB' and pos[i]!='D' and exposure.get(i,0)>=EXP_CAP: m += x[i]==0
    for pl in prev:
        m += pulp.lpSum(x[i] for i in pl) <= OVERLAP
    for (a,b),c in pairs.items():
        if c>=PAIR_CAP: m += x[a]+x[b]<=1
    m.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[m.status]!='Optimal': return None
    return [i for i in x if x[i].value()>0.5]

lineups=[]; exposure={}; pairs={}
for qb in qbs:
    for k in range(PER_QB):
        sel = build_one(qb, [l for l in lineups], exposure, pairs)
        if sel is None: print('NO LEGAL LINEUP for', qb, k); continue
        lineups.append(sel)
        qi = [i for i in sel if elig.loc[i,'pos']=='QB'][0]
        for i in sel: exposure[i]=exposure.get(i,0)+1
        for a,b in itertools.combinations(sorted(sel),2):
            stack = (elig.loc[a,'pos']=='QB' and elig.loc[b,'team']==elig.loc[a,'team'] and elig.loc[b,'pos'] in('WR','TE')) or \
                    (elig.loc[b,'pos']=='QB' and elig.loc[a,'team']==elig.loc[b,'team'] and elig.loc[a,'pos'] in('WR','TE'))
            if not stack: pairs[(a,b)]=pairs.get((a,b),0)+1

# ---------- output
ORDER={'QB':0,'RB':1,'WR':2,'TE':3,'D':4}
out=[]
for n,sel in enumerate(lineups,1):
    L = elig.loc[sel].copy(); L['ord']=L['pos'].map(ORDER); L=L.sort_values(['ord','salary'],ascending=[True,False])
    rbs=L[L.pos=='RB'];
    slots=['QB']+['RB','RB']+['WR']*3+['TE']+['FLEX']+['DEF']
    ordered = pd.concat([L[L.pos=='QB'], rbs.iloc[:2], L[L.pos=='WR'], L[L.pos=='TE'], rbs.iloc[2:3], L[L.pos=='D']])
    ordered['slot']=slots; ordered['lineup']=n
    out.append(ordered)
O=pd.concat(out)
O.to_csv(f'{WK}/lineups_{MODE}.csv', index=False)
elig.to_csv(f'{WK}/elig_{MODE}.csv', index=False)
with open(f'{WK}/report_{MODE}.txt','w') as f:
    f.write(f'MODE {MODE}  N={len(lineups)}\nQBs: {qbs}\n')
    f.write(qbtab.to_string(index=False)+'\n\n')
    f.write('UNPRICED EXCLUDED (>=5k): '+', '.join(f"{r['name']} {r['team']} ${r['salary']}" for _,r in unpriced_excluded.iterrows())+'\n')
    f.write('RB ROLE-GATE DROPPED: '+', '.join(f"{r['name']} {r['team']} ${r['salary']} cs={r['carry_share2']:.2f}" for _,r in rb_dropped.iterrows())+'\n\n')
    for n,sel in enumerate(lineups,1):
        L=O[O.lineup==n]
        f.write(f"L{n} ${L.salary.sum():,} proj {L.proj.sum():.1f} | "+' | '.join(f"{r['slot']} {r['name']} ({r['team']}) ${r['salary']}" for _,r in L.iterrows())+'\n')
    f.write('\nEXPOSURE: '+', '.join(f"{elig.loc[i,'name']} x{c}" for i,c in sorted(exposure.items(), key=lambda t:-t[1]) if c>=3)+'\n')
    mo=0
    for a,b in itertools.combinations(range(len(lineups)),2): mo=max(mo,len(set(lineups[a])&set(lineups[b])))
    f.write(f'MAX PAIRWISE OVERLAP {mo}; MAX PAIR {max(pairs.values()) if pairs else 0}\n')
    f.write('LS own on rostered: '+', '.join(f"{elig.loc[i,'name']} {elig.loc[i,'ls_own']}" for i in sorted(exposure, key=lambda i:-exposure[i])[:25])+'\n')
print(open(f'{WK}/report_{MODE}.txt').read())
