"""NFL FanDuel live build - CANONICAL SCRIPT. Run this file as-is; never retype the rules from notes.
Live set = NFL FD protocol v1.8 (in force from Week 10, 2026-11-15): props-only projection + rules C1-C7, 3 QBs x 5 lineups.
Assembled 2026-11-11 from the Week 8 builder (prep.py + build.py + fill.py) and the Week 9 fixes (C1-C7, compliance print, relaxations),
with the projection switched to props only as v1.8 says. v1.8 had never been built before this file; there is no past live build to test against.

Usage:
  python3 build_live.py <fd_players_list.csv> <lines.csv> <props_dir> <nflverse_stats_player_week.csv> <week> \
                        <fd_entries_template.csv> <out_upload.csv> [<linestar_raw.json.gz>]
  - lines.csv: header away,home,home_spread,total  (FanDuel team abbreviations; home_spread negative = home favoured), one row per Main game.
  - props_dir: one raw JSON per game from get_event_odds, markets player_pass_yds, player_pass_tds, player_rush_yds,
    player_reception_yds, player_receptions, player_anytime_td (american odds), saved verbatim.
  - nflverse file: stats_player_week_<season>.csv from the nflverse-data stats_player release; weeks before <week> feed the role gate.
  - LineStar raw file: the newest backtests/nfl/linestar/live/*_raw.json.gz. LineStar is NOT in the v1.8 projection; it is used for the
    ownership log and to drop skill players it projects at 0.5 or less (not expected to play). Without it the run is NOT FULL.
Writes <out_upload.csv> and <out_upload>_lineups.json = the manifest (live 15, the v1.6 shadow, the C2-amended shadow, compliance, run check).

Rules as run (C1-C7 of the 11/1 list):
  Projection (v1.8): per player, median main line across books -> 0.04 pass yd + 4 pass TD + 0.1 rush yd + 0.1 rec yd + 0.5 rec + 6 x E[TD],
    E[TD] = -ln(1 - p), p = median anytime-TD implied probability x 0.92 (capped 0.97); QB -0.6. D-ST = (30 - opponent implied total, floor 2) x 0.55.
  Eligibility: not O / IR / NA / D; priced (a yardage or receptions line; TD-only = unpriced) (C5); WR/TE salary 4,500+ (C4);
    RB needs 35%+ of team carries over his last 2 games unless he has no nflverse rows (C5).
  C7 QB pick: salary 6,800-8,300, score = team implied total + 0.4 x game total - 1.5 x max(0, salary - 7,600)/1,000, top 3, one per game.
  C1 QB + 2 or 3 of his own WR/TE, each passing the role gate (WOPR 0.30+ or target share 0.18+ over last 2 games, or no nflverse rows).
  C2 no RB from the QB's team; max 1 RB per game.   C3 FLEX = RB (3 RBs), RB x3 salary 20,000+, salary 59,500-60,000.
  C4 no D-ST against any of our offensive players; players at 4,500 or less only from the QB's game.   Max 4 per team.
  C5 bring-back WR/TE from the QB's opponent must pass the role gate.
  C6 overlap <= 5 with every earlier lineup; exposure <= 7 of 15 (QB and D-ST exempt); non-stack pair <= 6; lineups 2-5 of a QB keep at
     least one stack partner of lineup 1, use a different D-ST and at most 2 of lineup 1's RBs.
  If a lineup cannot be built, the Week 9 relaxations are tried in order (overlap 6; then overlap 6 with exposure 8) and reported as NOT FULL.
Shadows (logged, never entered): v1.6 = props + salary formula 50/50; C2-amended = a pass-catching RB (receptions line 3.0+ or target share
  12%+) may play with his own QB.

RUN CHECK. The last block printed is "PROTOCOL RUN: FULL" or "PROTOCOL RUN: NOT FULL - n item(s)". It goes at the very top of the reply to
Phong, word for word, and is saved in the manifest under "protocol_run". The check only reads.
  env NFL_RATIFIED_SHA = the script hash written in the protocol record (v1.8 section)
  env NFL_REFRESH      = Pacific time the inactives / injury tags were last checked, e.g. "9:35 AM"
  env NFL_LOCK         = lock time, Pacific; default "10:00 AM"
  env NFL_KEEP_OUT     = optional: comma-separated FanDuel names ruled out by news but not yet tagged by FanDuel; treated as Out
"""
VERSION='NFL FD v1.8 live + shadows (build_live.py 2026-11-11b)'
import pandas as pd, numpy as np, json, glob, re, sys, os, csv, itertools, hashlib, datetime, gzip, collections
import pulp
if len(sys.argv)<8: sys.exit('PROTOCOL RUN: STOPPED - build_live.py needs 7 arguments (usage at the top of the file). Nothing built. Tell Phong.')
POOL,LINESF,PROPS,NVF,WEEK,TPL,OUTF=sys.argv[1:8]; LSRAW=sys.argv[8] if len(sys.argv)>8 and sys.argv[8] else None; WEEK=int(WEEK)
for _n,_p in [('FanDuel players list',POOL),('lines file',LINESF),('props folder',PROPS),('nflverse stats file',NVF),('FanDuel upload template',TPL)]:
    if not os.path.exists(_p): sys.exit(f'PROTOCOL RUN: STOPPED - {_n} not found: {_p}. Nothing built. Tell Phong.')
PER_QB=5; EXP_CAP=7; PAIR_CAP=6; OVERLAP=5
def norm(n):
    n=str(n).lower().replace('.','').replace("'",'').replace('-',' ')
    n=re.sub(r'\b(jr|sr|ii|iii|iv|v)\b','',n)
    return ' '.join(n.split())
def imp(price):
    price=float(price)
    return 100/(price+100) if price>0 else -price/(-price+100)
print(VERSION)
# ---------- lines
ITT={};TOT={};SPR={}
for r in csv.DictReader(open(LINESF)):
    a,h,hs,t=r['away'].strip(),r['home'].strip(),float(r['home_spread']),float(r['total'])
    ITT[h]=(t-hs)/2; ITT[a]=(t+hs)/2; TOT[h]=TOT[a]=t; SPR[h]=hs; SPR[a]=-hs
# ---------- FanDuel pool (prep.py)
p=pd.read_csv(POOL)
p=p.rename(columns={'Id':'id','Position':'pos','Nickname':'name','Salary':'salary','Team':'team','Opponent':'opp','Injury Indicator':'inj','FPPG':'fppg','Played':'played','Game':'game'})
p=p[p['id'].notna()][['id','pos','name','salary','team','opp','inj','fppg','played','game']].copy()
p['inj']=p['inj'].fillna('')
KEEP_OUT=set(x.strip() for x in (os.environ.get('NFL_KEEP_OUT') or '').split(',') if x.strip())    # players ruled out by news that FanDuel has not tagged yet
KO_MISS=sorted(KEEP_OUT-set(p['name'])); p.loc[p['name'].isin(KEEP_OUT),'inj']='O'
p['itt']=p['team'].map(ITT); p['total']=p['team'].map(TOT); p['spread']=p['team'].map(SPR); p['opp_itt']=p['opp'].map(ITT)
nol=sorted(set(p.loc[p['itt'].isna(),'team']))
if nol: sys.exit(f'PROTOCOL RUN: STOPPED - no line in {os.path.basename(LINESF)} for team(s) {nol} on the FanDuel list. Nothing built. Tell Phong.')
p['key']=p['name'].map(norm); p.loc[p['pos']=='D','key']='D_'+p.loc[p['pos']=='D','team']
MULT={'QB':2.65,'RB':2.15,'WR':2.0,'TE':1.75}
def salproj(r):
    if r['pos']=='D': return np.nan
    return MULT.get(r['pos'],0)*max(r['salary']-3000,0)/1000*(r['itt']/22.5)**0.7
p['proj_sal']=p.apply(salproj,axis=1)
p.loc[p['pos']=='D','proj_sal']=(30-p.loc[p['pos']=='D','opp_itt']).clip(lower=2)*0.55
# ---------- LineStar: ownership log only (v1.8)
p['ls_own']=np.nan; p['ls_proj']=np.nan
if LSRAW and os.path.exists(LSRAW):
    d=json.load(gzip.open(LSRAW,'rt')); sc=json.loads(d.get('SalaryContainerJson') or '{}')
    L=pd.DataFrame([dict(k=('D_'+str(s.get('PTEAM')) if s.get('POS')=='D' else norm(s.get('Name'))),lsp=s.get('PP'),sid=s['Id']) for s in sc.get('Salaries',[])])
    if len(L):
        own={}; O=d.get('Ownership') or {}
        best=max(((k,v) for k,v in (O.get('Projected') or {}).items() if v),key=lambda kv:len(kv[1]),default=(None,[]))
        for od in best[1] or []: own[od['SalaryId']]=od.get('Owned')
        L['lso']=L['sid'].map(own); L=L.drop_duplicates('k').set_index('k')
        p['ls_own']=p['key'].map(L['lso']); p['ls_proj']=p['key'].map(L['lsp'])
# ---------- nflverse role gate: last 2 games played before this week
nv=pd.read_csv(NVF,low_memory=False)
if 'season_type' in nv: nv=nv[nv['season_type']=='REG']
NVMAX=int(nv['week'].max()) if len(nv) else 0
nv=nv[nv['week']<=WEEK-1].copy(); nv['key']=nv['player_display_name'].map(norm); nv=nv.sort_values('week')
last2=nv.groupby('key').tail(2)
agg=last2.groupby('key').agg(wopr2=('wopr','mean'),tshare2=('target_share','mean'),ngames=('week','count'))
tc=last2.groupby(['team','week'])['carries'].sum().rename('team_carries').reset_index(); l2=last2.merge(tc,on=['team','week'])
agg=agg.join(l2.groupby('key').apply(lambda x:x['carries'].sum()/max(x['team_carries'].sum(),1)).rename('carry_share2'))
p=p.merge(agg,on='key',how='left')
# ---------- props -> FD points (build.py)
MK=['player_pass_yds','player_pass_tds','player_rush_yds','player_reception_yds','player_receptions','player_anytime_td']
rows=[]; PFILES=sorted(glob.glob(os.path.join(PROPS,'*.json'))); PULLED=[]; PGAMES=set()
for f in PFILES:
    d=json.load(open(f))
    if d.get('pulled_at_utc'): PULLED.append(str(d['pulled_at_utc']))
    for g in d.get('games',[]):
        PGAMES.add(g.get('away','')+'@'+g.get('home',''))
        for b in g.get('books',[]):
            for m in b.get('markets',[]):
                for o in m.get('outcomes',[]):
                    rows.append(dict(book=b['key'],mkt=m['key'],side=o['name'],price=o['price'],point=o.get('point'),player=o.get('description')))
if not rows: sys.exit(f'PROTOCOL RUN: STOPPED - no props found in {PROPS}. Nothing built. Tell Phong.')
P=pd.DataFrame(rows); P['key']=P['player'].map(norm)
ov=P[P['side'].isin(['Over','Yes'])].copy()
lines=ov.groupby(['key','mkt'])['point'].median().unstack()
td=ov[ov['mkt']=='player_anytime_td'].groupby('key')['price'].apply(lambda s:np.median([imp(x) for x in s]))*0.92
td=td.clip(upper=0.97)
proj=pd.DataFrame(index=lines.index.union(td.index))
for c in MK[:-1]: proj[c]=lines[c] if c in lines else np.nan
proj['p_td']=td
proj=proj.fillna({c:0 for c in MK[:-1]}).fillna({'p_td':0})
proj['e_td']=-np.log(1-proj['p_td'].clip(upper=0.97))
proj['fp_props']=(0.04*proj['player_pass_yds']+4*proj['player_pass_tds']+0.1*proj['player_rush_yds']+0.1*proj['player_reception_yds']+0.5*proj['player_receptions']+6*proj['e_td'])
proj.loc[proj['player_pass_yds']>0,'fp_props']-=0.6
proj['priced']=(proj[MK[:-1]].sum(axis=1)>0)
p=p.merge(proj[['fp_props','priced','player_receptions']],left_on='key',right_index=True,how='left')
p['priced']=p['priced'].fillna(False).astype(bool)
p.loc[p['pos']=='D','fp_props']=p.loc[p['pos']=='D','proj_sal']; p.loc[p['pos']=='D','priced']=True
def run(mode,c2amend=False,quiet=False):
    """mode v18 = props only; v16 = props + salary formula 50/50. Returns dict with lineups (lists of FD ids in slot order) and notes."""
    global OVERLAP,EXP_CAP,PAIR_CAP
    q0=p.copy()
    if mode=='v18': q0['proj']=q0['fp_props']
    else: q0['proj']=q0.apply(lambda r:r['proj_sal'] if r['pos']=='D' else float(np.mean([x for x in [r['fp_props'],r['proj_sal']] if pd.notna(x)])) if (pd.notna(r['fp_props']) or pd.notna(r['proj_sal'])) else np.nan,axis=1)
    OUT=q0['inj'].isin(['O','IR','NA','D'])
    elig=q0[(~OUT)&q0['priced']&q0['proj'].notna()].copy()
    elig=elig[~((elig['pos'].isin(['WR','TE']))&(elig['salary']<4500))]
    elig=elig[~((elig['pos']!='D')&(elig['ls_proj'].fillna(1)<=0.5))]      # LineStar says not expected to play (kept by Phong 11/11); needs the LineStar file
    unpriced=q0[(~OUT)&(~q0['priced'])&(q0['pos']!='D')&(q0['salary']>=5000)][['name','pos','team','salary']]
    elig['stack_ok']=(elig['ngames'].isna())|(elig['wopr2']>=0.30)|(elig['tshare2']>=0.18)
    rb_gate=(elig['pos']!='RB')|elig['ngames'].isna()|(elig['carry_share2']>=0.35)
    rb_dropped=elig[(elig['pos']=='RB')&~rb_gate][['name','team','salary','carry_share2']]
    elig=elig[rb_gate].copy()
    elig['pcrb']=(elig['pos']=='RB')&((elig['player_receptions'].fillna(0)>=3.0)|(elig['tshare2'].fillna(0)>=0.12))
    q=elig[(elig['pos']=='QB')&(elig['salary'].between(6800,8300))].copy()
    q['qscore']=q['itt']+0.4*q['total']-1.5*np.maximum(0,q['salary']-7600)/1000
    q=q.sort_values('qscore',ascending=False); qbs=[]; ug=set()
    for _,r in q.iterrows():
        if r['game'] in ug: continue
        qbs.append(r['name']); ug.add(r['game'])
        if len(qbs)==3: break
    elig=elig.reset_index(drop=True); pos=elig['pos']
    def build_one(qb_name,prev,exposure,pairs,first=None):
        m=pulp.LpProblem('fd',pulp.LpMaximize)
        x={i:pulp.LpVariable(f'x{i}',cat='Binary') for i in elig.index}
        m+=pulp.lpSum(x[i]*elig.loc[i,'proj'] for i in x)
        for ps,n in [('QB',1),('RB',3),('WR',3),('TE',1),('D',1)]: m+=pulp.lpSum(x[i] for i in x if pos[i]==ps)==n
        m+=pulp.lpSum(x[i]*elig.loc[i,'salary'] for i in x)<=60000
        m+=pulp.lpSum(x[i]*elig.loc[i,'salary'] for i in x)>=59500
        m+=pulp.lpSum(x[i]*elig.loc[i,'salary'] for i in x if pos[i]=='RB')>=20000
        qi=elig.index[elig['name']==qb_name][0]; m+=x[qi]==1
        qteam=elig.loc[qi,'team']; qgame=elig.loc[qi,'game']
        same=[i for i in x if pos[i] in ('WR','TE') and elig.loc[i,'team']==qteam]
        for i in same:
            if not elig.loc[i,'stack_ok']: m+=x[i]==0                 # C5 role gate on stack partners
        m+=pulp.lpSum(x[i] for i in same)>=2                           # C1
        m+=pulp.lpSum(x[i] for i in same)<=3                           # C1
        for i in x:
            if pos[i]=='RB' and elig.loc[i,'team']==qteam and not (c2amend and elig.loc[i,'pcrb']): m+=x[i]==0     # C2
            if pos[i]!='D' and elig.loc[i,'salary']<=4500 and elig.loc[i,'game']!=qgame: m+=x[i]==0               # C4 cheap only from QB's game
            if pos[i] in ('WR','TE') and elig.loc[i,'team']==elig.loc[qi,'opp'] and not elig.loc[i,'stack_ok']: m+=x[i]==0   # C5 bring-back
            if pos[i]=='D':
                for j in x:
                    if pos[j]!='D' and elig.loc[j,'team']==elig.loc[i,'opp']: m+=x[i]+x[j]<=1                    # C4 D-ST conflict
        for t in elig['team'].unique(): m+=pulp.lpSum(x[i] for i in x if elig.loc[i,'team']==t)<=4
        for g in elig['game'].unique(): m+=pulp.lpSum(x[i] for i in x if pos[i]=='RB' and elig.loc[i,'game']==g)<=1   # C2
        for i in x:
            if pos[i]!='QB' and pos[i]!='D' and exposure.get(i,0)>=EXP_CAP: m+=x[i]==0                                  # C6 exposure
        for pl in prev: m+=pulp.lpSum(x[i] for i in pl)<=OVERLAP                                                      # C6 overlap
        for (a,b),c in pairs.items():
            if c>=PAIR_CAP: m+=x[a]+x[b]<=1                                                                            # C6 pair
        if first is not None:                                                                                         # C6 branch rules
            m+=pulp.lpSum(x[i] for i in first if pos[i] in ('WR','TE') and elig.loc[i,'team']==qteam)>=1
            m+=pulp.lpSum(x[i] for i in first if pos[i]=='RB')<=2
            for i in first:
                if pos[i]=='D': m+=x[i]==0
        m.solve(pulp.PULP_CBC_CMD(msg=0))
        if pulp.LpStatus[m.status]!='Optimal': return None
        return [i for i in x if x[i].value()>0.5]
    lineups=[];exposure={};pairs={};relaxed=[];missing=[]
    for qb in qbs:
        first=None
        for k in range(PER_QB):
            sel=build_one(qb,list(lineups),exposure,pairs,first)
            if sel is None:
                OVERLAP=6; sel=build_one(qb,list(lineups),exposure,pairs,first)
                if sel is not None: relaxed.append(f'{qb} lineup {k+1}: overlap raised to 6')
                else:
                    EXP_CAP=8; sel=build_one(qb,list(lineups),exposure,pairs,first)
                    if sel is not None: relaxed.append(f'{qb} lineup {k+1}: overlap 6, exposure 8')
                OVERLAP=5; EXP_CAP=7; PAIR_CAP=6
            if sel is None: missing.append(f'{qb} lineup {k+1}'); continue
            if first is None: first=sel
            lineups.append(sel)
            for i in sel: exposure[i]=exposure.get(i,0)+1
            for a,b in itertools.combinations(sorted(sel),2):
                stack=(pos[a]=='QB' and elig.loc[b,'team']==elig.loc[a,'team'] and pos[b] in('WR','TE')) or (pos[b]=='QB' and elig.loc[a,'team']==elig.loc[b,'team'] and pos[a] in('WR','TE'))
                if not stack: pairs[(a,b)]=pairs.get((a,b),0)+1
    out=[];comp=[];viol=0
    for n,sel in enumerate(lineups,1):
        Lr=elig.loc[sel].sort_values('salary',ascending=False); rbs=Lr[Lr.pos=='RB']
        o=pd.concat([Lr[Lr.pos=='QB'],rbs.iloc[:2],Lr[Lr.pos=='WR'],Lr[Lr.pos=='TE'],rbs.iloc[2:3],Lr[Lr.pos=='D']])
        out.append([f"{r['id']}:{r['name']}" for _,r in o.iterrows()])
        qq=Lr[Lr.pos=='QB'].iloc[0]; st=int(((Lr.team==qq.team)&Lr.pos.isin(['WR','TE'])).sum()); rbq=int(((Lr.team==qq.team)&(Lr.pos=='RB')&((~Lr.pcrb) if c2amend else True)).sum())
        rbsal=int(rbs.salary.sum()); sal=int(Lr.salary.sum()); cheap=int(((Lr.salary<=4500)&(Lr.pos!='D')&(Lr.game!=qq.game)).sum())
        dconf=int(sum(((Lr.pos!='D')&(Lr.team==dd.opp)).sum() for _,dd in Lr[Lr.pos=='D'].iterrows()))
        ovm=max([len(set(sel)&set(o2)) for j,o2 in enumerate(lineups) if j!=n-1] or [0])
        ok=2<=st<=3 and rbq==0 and len(rbs)==3 and rbsal>=20000 and 59500<=sal<=60000 and cheap==0 and dconf==0 and ovm<=5
        viol+=(not ok)
        comp.append(f"L{n}: stack {st} | RB same team {rbq} | RBx3 ${rbsal:,} | ${sal:,} | cheap off-game {cheap} | D conflict {dconf} | max overlap {ovm} -> {'OK' if ok else 'VIOLATION'}")
        if not quiet: print(f"L{n} ${sal:,} proj {Lr.proj.sum():.1f} | "+' | '.join(f"{r['pos']} {r['name']} ({r['team']}) ${r['salary']}" for _,r in o.iterrows()))
    expo={elig.loc[i,'name']:c for i,c in sorted(exposure.items(),key=lambda t:-t[1]) if c>=3}
    return dict(mode=mode,c2amend=c2amend,qbs=qbs,qb_table=q[['name','team','salary','itt','total','qscore']].head(8).round(2).values.tolist(),lineups=out,relaxed=relaxed,missing=missing,
                compliance=comp,violations=int(viol),exposure=expo,unpriced_excluded=[f"{r['name']} {r['team']} ${r['salary']}" for _,r in unpriced.iterrows()],
                rb_gate_dropped=[f"{r['name']} {r['team']} ${r['salary']} share {r['carry_share2']:.2f}" for _,r in rb_dropped.iterrows()],elig=elig)
print(f'week {WEEK} | games {len(TOT)//2} | props files {len(PFILES)} | nflverse through week {min(NVMAX,WEEK-1)}')
LIVE=run('v18'); EL=LIVE.pop('elig')
print('QBs (C7):',LIVE['qbs']); print('UNPRICED EXCLUDED (5k+):',', '.join(LIVE['unpriced_excluded']) or 'none'); print('RB ROLE GATE DROPPED:',', '.join(LIVE['rb_gate_dropped']) or 'none')
print('EXPOSURE (3+):',LIVE['exposure']); print('COMPLIANCE:'); [print('  '+c) for c in LIVE['compliance']]; print('VIOLATIONS:',LIVE['violations'])
if len(LIVE['qbs'])<3 or not LIVE['lineups']: sys.exit(f"PROTOCOL RUN: STOPPED - URGENT: the QB rule found {len(LIVE['qbs'])} of 3 quarterbacks and {len(LIVE['lineups'])} lineups were built. Nothing written. Tell Phong.")
SH={}
for nm,(md,c2) in {'shadow_v16':('v16',False),'shadow_c2_amended':('v18',True)}.items():
    try: r=run(md,c2,quiet=True); r.pop('elig'); SH[nm]=r; print(f"{nm}: {len(r['lineups'])} lineups, QBs {r['qbs']}")
    except Exception as e: SH[nm]=dict(error=f'{type(e).__name__}: {e}',lineups=[]); print(f'{nm}: FAILED {e}')
def sha(f):
    try: return hashlib.sha256(open(f,'rb').read()).hexdigest()[:16]
    except Exception: return None
man=dict(keep_out=sorted(KEEP_OUT),version=VERSION,script_sha=sha(os.path.realpath(__file__)),built_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),week=WEEK,
         inputs=dict(fd_players=dict(file=os.path.basename(POOL),sha=sha(POOL)),lines=dict(file=os.path.basename(LINESF),sha=sha(LINESF)),props_files=len(PFILES),props_pulled_utc=sorted(PULLED)[:1]+sorted(PULLED)[-1:],
                     nflverse=dict(file=os.path.basename(NVF),through_week=min(NVMAX,WEEK-1)),fd_template=dict(file=os.path.basename(TPL),sha=sha(TPL)),linestar_raw=os.path.basename(LSRAW) if LSRAW else None),
         live=LIVE,shadows=SH)
json.dump(man,open(OUTF.replace('.csv','_lineups.json'),'w'))
T=list(csv.reader(open(TPL,newline=''))); ent=[r for r in T[1:] if r and r[0].strip()]; n=len(LIVE['lineups'])
out=[T[0][:13]]+[e[:4]+LIVE['lineups'][k%n] for k,e in enumerate(ent)]
csv.writer(open(OUTF,'w',newline='')).writerows(out); print(f'\nwrote {OUTF}: {len(out)-1} entries')

# ------------------------------------------------------------------------------------------------------------------------------------
# RUN CHECK: either the full protocol ran, or Phong is told what did not. It only reads; it never changes a lineup.
# ------------------------------------------------------------------------------------------------------------------------------------
def hm(m): m=int(m); return f'{(m//60)%12 or 12}:{m%60:02d} {"AM" if (m//60)%24<12 else "PM"}'
def clock(x):
    m=re.search(r'(\d{1,2}):(\d{2})\s*([AaPp][Mm])?',str(x or ''))
    if not m: return None
    h=int(m.group(1))
    if m.group(3): h=h%12+(12 if m.group(3).upper()=='PM' else 0)
    return h*60+int(m.group(2))
def run_check():
    import subprocess, zoneinfo
    miss=[];notes=[];ok=[]; PT=zoneinfo.ZoneInfo('America/Los_Angeles'); now=datetime.datetime.now(PT); today=now.strftime('%Y-%m-%d')
    me=os.path.realpath(__file__); mysha=sha(me)
    def git(where,*a):
        try: r=subprocess.run(['git','-C',where]+list(a),capture_output=True,text=True,timeout=20); return r.returncode,r.stdout.strip()
        except Exception: return 1,''
    rc,top=git(os.path.dirname(me),'rev-parse','--show-toplevel')
    rel=os.path.relpath(me,os.path.realpath(top)).replace(os.sep,'/') if rc==0 and top else ''
    inrepo=rel=='backtests/nfl/live/build_live.py' and git(top,'ls-files','--error-unmatch',rel)[0]==0 and git(top,'status','--porcelain','--',rel)[1]==''
    if inrepo: ok.append(f'script is the unmodified repo copy (commit {git(top,"rev-parse","--short","HEAD")[1]})')
    else: miss.append(f'the script that ran is not the unmodified repo copy backtests/nfl/live/build_live.py (it ran from {me})')
    exp=(os.environ.get('NFL_RATIFIED_SHA') or '').strip().lower()
    if not exp: miss.append('the script hash was not checked against the protocol record - pass NFL_RATIFIED_SHA=<hash in the v1.8 section>')
    elif exp[:16]!=mysha: miss.append(f'script hash {mysha} is not the ratified hash ({exp[:16]})')
    else: ok.append(f'script hash {mysha} = the ratified hash')
    # slate, lines, props
    games=sorted(set(p['game'].dropna())); ng=len(TOT)//2
    if ng<len(games): miss.append(f'lines cover {ng} games but the FanDuel list has {len(games)}')
    if len(PFILES)<len(games): miss.append(f'props were pulled for {len(PFILES)} of {len(games)} games - players in the other games are unpriced and excluded')
    else: ok.append(f'lines and props for all {len(games)} games')
    td=re.search(r'NFL-(\d{4}-\d{2}-\d{2})-',os.path.basename(TPL))
    if td and td.group(1)!=today: miss.append(f'the upload template is dated {td.group(1)}; today is {today} (an early build is not the final run)')
    lock=clock(os.environ.get('NFL_LOCK') or '10:00 AM')
    if not PULLED: miss.append('the props files carry no pull time - their age was not checked')
    else:
        try:
            old=min(datetime.datetime.fromisoformat(x.replace('Z','+00:00')) for x in PULLED).astimezone(PT)
            lk=now.replace(hour=lock//60,minute=lock%60,second=0,microsecond=0)
            if td:
                y,mo,dd=map(int,td.group(1).split('-')); lk=lk.replace(year=y,month=mo,day=dd)
            gap=int((lk-old).total_seconds()//60)
            if gap>90: miss.append(f'the oldest props file was pulled {old.strftime("%a %I:%M %p")} Pacific, {gap} minutes before the {hm(lock)} lock; the final build belongs on the Sunday ~9:30 pull')
            elif gap<0: miss.append('props were pulled after lock - this script builds pre-lock sets only')
            else: ok.append(f'props pulled within {gap} minutes of lock')
        except Exception as e: miss.append(f'props pull time unreadable ({e})')
    npri=int((p['priced']&(p['pos']!='D')).sum())
    if npri<150: miss.append(f'only {npri} skill players are priced by the books - the props pull looks incomplete')
    else: ok.append(f'{npri} skill players priced')
    if NVMAX<WEEK-1: miss.append(f'nflverse stats stop at week {NVMAX}; the role gate needs week {WEEK-1}')
    else: ok.append(f'nflverse role gate through week {WEEK-1}')
    if not (LSRAW and os.path.exists(LSRAW)) or p['ls_proj'].notna().sum()<100: miss.append('no usable LineStar file was passed - the not-expected-to-play filter (LineStar projection 0.5 or less) was NOT applied')
    else: ok.append('LineStar not-expected-to-play filter applied')
    if KO_MISS: miss.append('NFL_KEEP_OUT name(s) not matched to the FanDuel list, so they were NOT excluded: '+', '.join(KO_MISS))
    if KEEP_OUT: notes.append('ruled out by hand (NFL_KEEP_OUT): '+', '.join(sorted(KEEP_OUT)))
    if not (p['inj']!='').any(): miss.append('the FanDuel list carries no injury tags at all')
    rf=clock(os.environ.get('NFL_REFRESH'))
    if rf is None: miss.append('the time the inactives and injury tags were checked is not recorded - pass NFL_REFRESH="9:35 AM" (Pacific)')
    elif lock-rf>60 or rf>lock: miss.append(f'inactives were checked at {hm(rf)}; the final check belongs in the hour before the {hm(lock)} lock')
    else: ok.append(f'inactives checked at {hm(rf)}')
    # the sets
    if len(LIVE['lineups'])<15: miss.append(f"only {len(LIVE['lineups'])} of 15 lineups could be built (no legal lineup for: {', '.join(LIVE['missing'])})")
    for r in LIVE['relaxed']: miss.append('a cap was relaxed to fill a lineup: '+r+' (needs Phong\'s OK)')
    if LIVE['violations']: miss.append(f"{LIVE['violations']} lineup(s) fail the C1-C7 compliance check")
    if len(LIVE['lineups'])==15 and not LIVE['violations'] and not LIVE['relaxed']: ok.append('15 lineups, C1-C7 compliance 15 of 15, no relaxations')
    for nm,r in SH.items():
        if len(r.get('lineups',[]))<15: notes.append(f"{nm}: {len(r.get('lineups',[]))} of 15 lineups built"+(f" ({r['error']})" if r.get('error') else ''))
    dexp=collections.Counter(l[8].split(':',1)[1] for l in LIVE['lineups'])
    if dexp and max(dexp.values())>5: notes.append(f'D-ST exposure above 5 of 15 (watch item, not a rule): {dict(dexp)}')
    # the upload file, re-read from disk
    bad=[]; w=list(csv.reader(open(OUTF))); E=EL.set_index('id'); SLOT=['QB','RB','RB','WR','WR','WR','TE','RB','D']; seen=set()
    if len(w)-1!=len(ent): bad.append(f'{len(w)-1} rows written for {len(ent)} entries')
    for j,r in enumerate(w[1:]):
        ids=[c.split(':')[0] for c in r[4:13]]
        if j<len(ent) and r[:4]!=ent[j][:4]: bad.append(f'row {j+1}: the entry columns changed')
        if len(set(ids))!=9 or any(i not in E.index for i in ids): bad.append(f'row {j+1}: not nine different eligible players'); continue
        if [E.loc[i,'pos'] for i in ids]!=SLOT: bad.append(f'row {j+1}: slots are not QB, RB, RB, WR, WR, WR, TE, FLEX RB, DEF')
        if sum(E.loc[i,'salary'] for i in ids)>60000: bad.append(f'row {j+1}: salary over $60,000')
        if len(set(E.loc[i,'team'] for i in ids))<3: bad.append(f'row {j+1}: fewer than 3 teams')
        k=(r[1],frozenset(ids))
        if k in seen: bad.append(f'row {j+1}: same roster twice in one contest')
        seen.add(k)
    if not ent: miss.append('the upload template has no entries')
    if bad: miss.append('the upload file failed validation: '+'; '.join(bad[:8]))
    else: ok.append(f'upload file valid ({len(w)-1} entries)')
    cs={}
    for r in ent:
        c=cs.setdefault(r[1],dict(name=r[2],fee=r[3],n=0)); c['n']+=1
    def fee(x):
        try: return float(str(x).replace('$','').replace(',',''))
        except Exception: return 0.0
    total=sum(fee(c['fee'])*c['n'] for c in cs.values()); bar='='*100
    print('\n'+bar)
    if miss:
        print(f'PROTOCOL RUN: NOT FULL - {len(miss)} item(s). This block goes at the very top of the reply to Phong, word for word.')
        for q,x in enumerate(miss,1): print(f'  {q}. {x}')
    else: print(f'PROTOCOL RUN: FULL - NFL v1.8, script hash {mysha}, week {WEEK}, lock {hm(lock)}. This line goes at the very top of the reply to Phong.')
    for x in notes: print('NOTE: '+x)
    print('Passed: '+'; '.join(ok)+'.')
    print('Contests in the template: '+('; '.join(f"{c['name']} x{c['n']} at ${c['fee']}" for c in cs.values()) or 'none')+f'. Fees ${total:g}.')
    print('Not covered by this check: the weather look, the 9:50 swap check, replacement-RB calls, the kill-switch tally, grading.')
    print(bar)
    return dict(status='NOT FULL' if miss else 'FULL',missing=miss,notes=notes,passed=ok,checked_pacific=now.strftime('%Y-%m-%d %H:%M'),lock=hm(lock),refresh=os.environ.get('NFL_REFRESH'),ratified_sha=exp or None,contests=list(cs.values()),fees=total)
try: man['protocol_run']=run_check()
except Exception as e:
    why=f'the run check itself failed ({type(e).__name__}: {e}) - treat this build as unchecked'
    man['protocol_run']=dict(status='NOT FULL',missing=[why])
    print('\n'+'='*100+f'\nPROTOCOL RUN: NOT FULL - 1 item(s). This block goes at the very top of the reply to Phong, word for word.\n  1. {why}\n'+'='*100)
json.dump(man,open(OUTF.replace('.csv','_lineups.json'),'w'))
