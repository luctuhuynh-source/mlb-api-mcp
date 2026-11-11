"""NBA FanDuel live build - CANONICAL SCRIPT. Run this file as-is; never retype the rules from notes.
Live set = protocol v1.4 exactly as written in the protocol doc (in force from 2026-11-11). Shadow sets are logged for grading only.

Usage:
  python3 build_live.py <fd_players_list.csv> <linestar_players.csv> <linestar_projown.csv> <linestar_slate_id> \
                        <fd_entries_template.csv> <out_upload.csv> "<starter1,starter2,...>" "<exclude1,exclude2,...>"
  - starters: RotoWire expected/confirmed starters pulled in the SAME refresh as the LineStar file (rule 2).
  - excludes: anyone tagged O/Q/D on the injury report who is not already tagged on the FanDuel list (rule 10).
  - AggProj is read from the matching *_raw.json.gz next to the LineStar players file; a player without one uses LineStar's number.
Writes <out_upload.csv> (FanDuel upload) and <out_upload>_lineups.json = the run's manifest (script version + hash, mode, input files +
hashes, snapshot name, game-log date, eligible list, objective, live + shadow lineups).
v1.4 live set: P = -0.26 + 0.136*LS + 0.856*AggProj, objective P + 0.1*(LS ceiling - LS projection); four lineups in sequence, any two
share <= 6 players (8 on slates of 3 games or fewer), max 3 per team, nothing else; late games placed in the flexible slots.
env NBA_LIVE = v14 (default, the protocol in force) | v13 | v14cand | v14nocap : which set is uploaded. Only switch it when Phong says so.
If the live set cannot produce four lineups the script stops with a PROTOCOL RUN: STOPPED line and writes nothing.

RUN CHECK (rule 1). The last block the script prints is "PROTOCOL RUN: FULL" or "PROTOCOL RUN: NOT FULL - n item(s)" with every item
listed. That block goes at the very top of the reply to Phong, word for word. It is also saved in the manifest under "protocol_run".
The check only reads; it never changes a lineup. FULL needs all of these, and three of them are passed by the session:
  env NBA_RATIFIED_SHA = the script hash written in rule 1 of the protocol doc (proves the doc was opened and this is the ratified script)
  env NBA_REFRESH      = Pacific time the starting lineups and the injury report were pulled, e.g. "3:47 PM" (rule 2: one refresh)
  env NBA_PRIMARY      = part of the primary contest's name; only needed when the upload template holds two contests (rules 19, 22)
  env NBA_LOCK         = optional override of the lock time (Pacific), e.g. "4:00 PM"; default = first tip in the LineStar file
Checked by the script itself: it is the unmodified repo copy; live set = v14; LineStar files are one pull, dated today, the newest of the
day, taken no more than 25 minutes before lock; projections present for every game; AggProj on 90%+ of the eligible players; ownership
slate matches the FanDuel slate; game logs current; five starters matched per team; every starter and exclusion name matched; no listed
starter without a projection; the three shadow sets built; the upload file re-read and validated (slots, salary, team cap, overlap,
entry ids); contests in the template within rules 19-20.
"""
VERSION='NBA FD v1.4 live + shadows (build_live.py 2026-11-11e)'
import pandas as pd, numpy as np, pulp, re, unicodedata, sys, csv, json, gzip, os, hashlib, datetime
HERE=os.path.dirname(os.path.abspath(__file__))
R=os.environ.get('NBA_REPO') or (os.path.join(HERE,'..','') if os.path.exists(os.path.join(HERE,'..','nba_player_games_2026-27.csv')) else '/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/')   # repo folder backtests/nba/
if len(sys.argv)<9: sys.exit('PROTOCOL RUN: STOPPED - build_live.py needs 8 arguments (usage at the top of the file). Nothing built. Tell Phong.')
pl,lsf,owf,slate,tpl,out,starters_s,excl_s=sys.argv[1:9]
for _n,_p in [('FanDuel players list',pl),('LineStar players file',lsf),('LineStar ownership file',owf),('FanDuel upload template',tpl),
              ('game logs 2025-26',R+'nba_player_games_2025-26.csv'),('game logs 2026-27',R+'nba_player_games_2026-27.csv')]:
    if not os.path.exists(_p): sys.exit(f'PROTOCOL RUN: STOPPED - {_n} not found: {_p}. Nothing built. Tell Phong.')
def k(s): s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower(); s=re.sub(r'\b(jr|sr|ii|iii)\b','',s); return re.sub(r'[^a-z]','',s)
fd=pd.read_csv(pl); fd=fd[fd.Id.notna()].copy(); fd['k']=fd.Nickname.map(k)
ls=pd.read_csv(lsf); ls['k']=ls.name.map(k)
if int((ls.ls_proj>0).sum())<=15: sys.exit(f'PROTOCOL RUN: STOPPED - only {int((ls.ls_proj>0).sum())} players carry a LineStar projection in {os.path.basename(lsf)}: the LineStar login cookie has expired (rule 2). Nothing built. Tell Phong: the cookie in ~/.linestar_auth on the Mac needs recopying.')
ow_all=pd.read_csv(owf); ow=ow_all[ow_all.slate==int(slate)].copy(); ow['k']=ow.name.map(k)
g=pd.concat([pd.read_csv(R+f'nba_player_games_{s}.csv') for s in ['2025-26','2026-27']])
asof=os.environ.get('NBA_ASOF')        # testing only: rebuild a past slate with logs strictly before that date
if asof: g=g[g.game_date<asof]
print(VERSION); print('game logs through',g.game_date.max(),'| LineStar file',os.path.basename(lsf),'| slate',slate)
g=g[~g.did_not_play.astype(bool)&(g.minutes>0)]; g['k']=g.athlete_display_name.map(k); g=g.sort_values('game_date')
rec=g.groupby('k').agg(l5=('fd_pts',lambda x:x.tail(5).mean()),min3=('minutes',lambda x:x.tail(3).mean()),
                       rate=('fd_pts',lambda x:(x.sum()+0.9*250)/(g.loc[x.index,'minutes'].sum()+250)),minS=('minutes','mean'))
def tipmin(g):
    m=re.search(r'(\d+):(\d+)\s*(AM|PM)',str(g))
    return np.nan if not m else (int(m.group(1))%12+(12 if m.group(3)=='PM' else 0))*60+int(m.group(2))
ls['tip']=ls['game'].map(tipmin) if 'game' in ls else np.nan
fd=fd.merge(ls[['k','ls_proj','ls_ceil','tip']].drop_duplicates('k'),on='k',how='left').merge(ow[['k','proj_owned']].drop_duplicates('k'),on='k',how='left').merge(rec,left_on='k',right_index=True,how='left')
# AggProj from the raw pull (shadow only)
raw=lsf.replace('_players.csv','_raw.json.gz'); agg={}
if os.path.exists(raw):
    sc=json.loads(json.load(gzip.open(raw)).get('SalaryContainerJson') or '{}')
    agg={k(s['Name']):s.get('AggProj') for s in sc.get('Salaries',[]) if (s.get('AggProj') or 0)>0}
fd['agg']=fd.k.map(agg)
starters=set(map(k,starters_s.split(','))) if starters_s else set()
excl=set(map(k,excl_s.split(','))) if excl_s else set()
st_raw=[x.strip() for x in starters_s.split(',') if x.strip()]; ex_raw=[x.strip() for x in excl_s.split(',') if x.strip()]   # as typed, for the run check
fd['starter']=fd.k.isin(starters)
miss=starters-set(fd.k)
if miss: print('WARNING starters not matched to the FanDuel list:',sorted(miss))
zero=fd[fd.starter&~(fd.ls_proj>0)&~fd['Injury Indicator'].isin(['O'])]
if len(zero): print('WARNING (rule 2) listed starters with no LineStar projection - check status / promote next man:',zero.Nickname.tolist())
dep={}
if 'Played' in fd:
    hl=fd[(fd['Injury Indicator']!='O')&(fd.Played>=3)].groupby('Team').size(); dep=hl[hl<=8]
    if len(dep): print('NOTE depleted team(s), 8 or fewer healthy players - look at them by hand:',dep.to_dict())
fd_all=fd      # the whole FanDuel list with the LineStar columns, before eligibility; read by the run check only
# Eligibility (v1.4 rule 10): not O/Q/D, LineStar proj > 0, (starter OR >=18 min last 3)
fd=fd[~fd['Injury Indicator'].isin(['O','Q','D'])&~fd.k.isin(excl)&(fd.ls_proj>0)&(fd.starter|(fd.min3>=18))].copy()
# Projections (v1.4 rules 6-7; the v1.3 blend is kept for its shadow) + ownership reconciled to 900 (reporting and the v1.3 shadow)
fd['l5']=fd.l5.fillna(fd.ls_proj); fd['blend']=0.7*fd.ls_proj+0.3*fd.l5
fd['eng']=((0.6*fd.min3.fillna(fd.minS)+0.4*fd.minS).fillna(28)*fd.rate).fillna(fd.ls_proj)
fd['cal']=-0.26+0.136*fd.ls_proj+0.856*fd['agg'].fillna(fd.ls_proj)     # v1.4 candidate projection (B77), shadow only
po=fd.proj_owned.fillna(0); fd['own']=(po*900/po.sum()).clip(upper=95) if po.sum()>0 else po
fd['up']=(fd.ls_ceil-fd.ls_proj).clip(lower=0).fillna(0)
def slots(rp):
    o={'UTIL'}
    if '/G/F' in rp: o.add('G/F'); rp=rp.replace('/G/F','',1)
    if rp.endswith('/F/C/UTIL'): o.add('F/C'); rp=rp[:-len('/F/C/UTIL')]+'/UTIL'
    for t in rp.split('/'):
        if t in ('PG','SG','SF','PF','C'): o.add(t)
    return o
fd['sl']=fd['Roster Position'].map(slots); fd=fd.reset_index(drop=True)
SL=['PG','SG','SF','PF','C','G/F','F/C','UTIL']; NEED={'PG':1,'SG':1,'SF':1,'PF':1,'C':1,'G/F':1,'F/C':1,'UTIL':2}
games=fd.Game.nunique()
OV=4 if games>=6 else (5 if games>=4 else 8)          # v1.3 overlap (shadow)
def build(col,N=4,tiers=True,ov=None,cap=3,contra=True,sub5k=True,teamcap=3):
    ov=OV if ov is None else ov
    built=[];expo={};res=[]
    for n in range(N):
        m=pulp.LpProblem('x',pulp.LpMaximize)
        x={(i,s):pulp.LpVariable(f'x{i}_{s.replace("/","")}',cat='Binary') for i in fd.index for s in fd.sl[i]}
        y={i:pulp.lpSum(x[i,s] for s in fd.sl[i]) for i in fd.index}
        m+=pulp.lpSum((fd[col][i]+0.1*fd.up[i])*y[i] for i in fd.index)                      # objective: projection + 0.1 x (LS ceiling - LS projection)
        for s in SL: m+=pulp.lpSum(x[i,s] for i in fd.index if s in fd.sl[i])==NEED[s]
        for i in fd.index: m+=y[i]<=1
        m+=pulp.lpSum(fd.Salary[i]*y[i] for i in fd.index)<=60000
        for t,d in fd.groupby('Team'):
            m+=pulp.lpSum(y[i] for i in d.index)<=teamcap                                    # team cap (v1.4 rule 12)
            if sub5k: m+=pulp.lpSum(y[i] for i in d.index if fd.Salary[i]<5000)<=2           # v1.3 sub-$5k limit (shadow only)
        if contra: m+=pulp.lpSum(y[i] for i in fd.index if fd.own[i]<10)<=(1 if games>=4 else 2)   # v1.3 contrarian cap (shadow only)
        for L in built: m+=pulp.lpSum(y[i] for i in L)<=ov
        for i,c in expo.items():
            lim=(3 if fd.own[i]>=35 else 2 if fd.own[i]>=15 else 1) if tiers else cap        # v1.3 tiers (shadow) / exposure cap (3, or 4 = none)
            if c>=lim: m+=y[i]==0
        m.solve(pulp.PULP_CBC_CMD(msg=0))
        if pulp.LpStatus[m.status]!='Optimal':
            print(f'WARNING: lineup {n+1} of the [{col}] set cannot be built under these rules (solver: {pulp.LpStatus[m.status]}); {len(res)} built'); break
        ids=[(s,i) for s in SL for i in fd.index if s in fd.sl[i] and x[i,s].value()>0.5]
        built.append([i for _,i in ids])
        for _,i in ids: expo[i]=expo.get(i,0)+1
        res.append(ids)
    return res
OV14=6 if games>=4 else 8
V14=dict(tiers=False,ov=OV14,cap=4,contra=False,sub5k=False)      # v1.4 rules 11-13: no tiers, no exposure cap, overlap 6 (8 on <=3 games), team cap 3, nothing else
SETS={'v13':('blend',{}),'v14':('cal',V14),'v14cand':('cal',dict(tiers=False,ov=OV14)),'v14nocap':('cal',dict(tiers=False,ov=OV14,cap=4))}
MODE=os.environ.get('NBA_LIVE','v14')
assert MODE in SETS,f'NBA_LIVE must be one of {list(SETS)}'
lcol,lkw=SETS[MODE]
nagg=int(fd['agg'].notna().sum())
print(f'games {games}  overlap cap {lkw.get("ov",OV)}  eligible {len(fd)}  AggProj matched {nagg}')
print(f'LIVE SET = {MODE}'+('' if MODE=='v14' else '   *** NOT the protocol in force (v1.4) - uploaded on request ***'))
if nagg<0.9*len(fd): print(f'WARNING AggProj matched only {nagg} of {len(fd)} players - the v1.4 sets fall back to the LineStar projection for the rest')
live=build(lcol,**lkw)
if len(live)<4: sys.exit(f'PROTOCOL RUN: STOPPED - URGENT: the live set ({MODE}) produced only {len(live)} of 4 lineups under its rules - nothing written. Tell Phong.')
def place(ids):
    # v1.4 rule 14: early games take the base position slots, the latest games take UTIL, then G/F and F/C
    I=[i for _,i in ids]
    if any(pd.isna(fd.tip[i]) for i in I): return ids
    w={'PG':0,'SG':0,'SF':0,'PF':0,'C':0,'G/F':1,'F/C':1,'UTIL':2}
    m=pulp.LpProblem('p',pulp.LpMaximize); z={(i,s):pulp.LpVariable(f'z{i}_{s.replace("/","")}',cat='Binary') for i in I for s in fd.sl[i]}
    m+=pulp.lpSum(w[s]*float(fd.tip[i])*z[i,s] for (i,s) in z)
    for s in SL: m+=pulp.lpSum(z[i,s] for i in I if s in fd.sl[i])==NEED[s]
    for i in I: m+=pulp.lpSum(z[i,s] for s in fd.sl[i])==1
    m.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[m.status]!='Optimal': return ids
    new=[(s,i) for s in SL for i in I if s in fd.sl[i] and z[i,s].value()>0.5]
    ok=sorted(i for _,i in new)==sorted(I) and all(sum(1 for s,_ in new if s==t)==NEED[t] for t in SL) and all(s in fd.sl[i] for s,i in new)
    return new if ok else ids
if MODE=='v14':
    live=[place(ids) for ids in live]
    if fd.tip.isna().all(): print('NOTE no game times in the LineStar file - slot placement by tip time skipped')
rows=[]
for n,ids in enumerate(live):
    I=[i for _,i in ids]
    print(f'\nL{n+1} proj {fd[lcol][I].sum():.1f}  sal ${fd.Salary[I].sum()}  cum-own {fd.own[I].sum():.0f}%')
    for s,i in ids: print(f'  {s:5} {fd.Nickname[i]:24} {fd.Team[i]:4} ${fd.Salary[i]:5}  {fd[lcol][i]:5.1f}  own {fd.own[i]:4.0f}%'+('' if MODE!='v14' or pd.isna(fd.tip[i]) else f'  tip {int(fd.tip[i])//60%12 or 12}:{int(fd.tip[i])%60:02d}'))
    rows.append([fd.Id[i] for _,i in ids])
sh={}
if MODE=='v14':   # v1.4 rule H: v1.3 as written, pure LineStar on the v1.4 structure, v1.4 projection with max 3 of 4
    shadows=[('shadow_v13',)+SETS['v13'],('shadow_LS_v14struct','ls_proj',V14),('shadow_v14cap3',)+SETS['v14cand']]
else:
    shadows=[('shadow_pureLS','ls_proj',{}),('shadow_engine','eng',{}),('shadow_v14cand',)+SETS['v14cand'],('shadow_v14nocap',)+SETS['v14nocap'],('shadow_v14',)+SETS['v14'],('shadow_LS_v14struct','ls_proj',V14)]
    if MODE!='v13': shadows.insert(0,('shadow_v13',)+SETS['v13'])
for name,col,kw in shadows:
    b=build(col,**kw); sh[name]=[[fd.Id[i] for _,i in ids] for ids in b]
    print(f'\n{name}:'); [print('  ',' · '.join(fd.Nickname[i] for _,i in ids)) for ids in b]
def sha(p):
    try: return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
    except Exception: return None
man=dict(version=VERSION,script_sha=sha(os.path.abspath(__file__)),live_mode=MODE,built_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),slate=slate,linestar=os.path.basename(lsf),
         inputs={n:dict(file=os.path.basename(p),sha=sha(p)) for n,p in [('fd_players',pl),('linestar_players',lsf),('linestar_projown',owf),('linestar_raw',raw),('fd_template',tpl)]},
         game_logs_through=str(g.game_date.max()),games=int(games),objective={'v13':'0.7*LS+0.3*last5 + 0.1*(LS ceiling-LS)','v14':'-0.26+0.136*LS+0.856*AggProj (LS if AggProj missing) + 0.1*(LS ceiling-LS)'},
         aggproj_matched=nagg,starters=sorted(starters),excludes=sorted(excl),eligible=[str(x) for x in fd.Id],live=rows,**sh)
json.dump(man,open(out.replace('.csv','_lineups.json'),'w'))
t=list(csv.reader(open(tpl))); o=[t[0][:13]]+[r[:4]+rows[j%4] for j,r in enumerate([r for r in t[1:] if r[0]])]
csv.writer(open(out,'w',newline='')).writerows(o); print(f'\nwrote {out}: {len(o)-1} entries')

# ------------------------------------------------------------------------------------------------------------------------------------
# RUN CHECK (v1.4 rule 1): either the full protocol ran, or Phong is told what did not. It only reads; it never changes a lineup.
# ------------------------------------------------------------------------------------------------------------------------------------
def hm(m): m=int(m); return f'{(m//60)%12 or 12}:{m%60:02d} {"AM" if (m//60)%24<12 else "PM"}'
def clock(x):
    m=re.search(r'(\d{1,2}):(\d{2})\s*([AaPp][Mm])?',str(x or ''))
    if not m: return None
    h=int(m.group(1))
    if m.group(3): h=h%12+(12 if m.group(3).upper()=='PM' else 0)
    return h*60+int(m.group(2))
def run_check():
    import subprocess, zoneinfo, difflib
    miss=[]; notes=[]; ok=[]
    now=datetime.datetime.now(zoneinfo.ZoneInfo('America/Los_Angeles')); today=now.strftime('%Y-%m-%d')
    # 1. the script: unmodified repo copy, and the hash ratified in the protocol doc
    me=os.path.realpath(__file__); mysha=sha(me)
    def git(where,*a):
        try: r=subprocess.run(['git','-C',where]+list(a),capture_output=True,text=True,timeout=20); return r.returncode,r.stdout.strip()
        except Exception: return 1,''
    rc,top=git(os.path.dirname(me),'rev-parse','--show-toplevel')
    rel=os.path.relpath(me,os.path.realpath(top)).replace(os.sep,'/') if rc==0 and top else ''
    inrepo=rel=='backtests/nba/live/build_live.py' and git(top,'ls-files','--error-unmatch',rel)[0]==0 and git(top,'status','--porcelain','--',rel)[1]==''
    if inrepo: ok.append(f'script is the unmodified repo copy (commit {git(top,"rev-parse","--short","HEAD")[1]})')
    else: miss.append(f'the script that ran is not the unmodified repo copy backtests/nba/live/build_live.py (it ran from {me}) - rule 1')
    exp=(os.environ.get('NBA_RATIFIED_SHA') or '').strip().lower()
    if not exp: miss.append('the script hash was not checked against the protocol doc - open the doc and pass NBA_RATIFIED_SHA=<hash in rule 1> - rule 1')
    elif exp[:16]!=mysha: miss.append(f'script hash {mysha} is not the hash ratified in the protocol doc ({exp[:16]}) - rule 1')
    else: ok.append(f'script hash {mysha} = the hash in the protocol doc')
    if MODE!='v14': miss.append(f'the live set was switched to {MODE} with NBA_LIVE - not the protocol in force (v1.4)')
    if asof: miss.append(f'test mode: game logs cut before {asof} (NBA_ASOF)')
    # 2. inputs: one pull, dated today, the newest of the day
    b=os.path.basename(lsf); mm=re.match(r'(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})_players\.csv$',b); pullmin=None; pulldate=None
    if not mm: miss.append(f'the LineStar file name ({b}) carries no pull time - snapshot and timing not checked - rule 3')
    else:
        pulldate=mm.group(1); stamp=b[:15]; pullmin=int(mm.group(2))*60+int(mm.group(3))
        if not os.path.basename(owf).startswith(stamp): miss.append(f'the ownership file ({os.path.basename(owf)}) is not from the same pull as {b} - rule 2')
        if pulldate!=today: miss.append(f'the LineStar pull is dated {pulldate}; today is {today} - rule 2')
        newer=sorted(f[11:15] for f in os.listdir(os.path.dirname(os.path.abspath(lsf))) if re.match(pulldate+r'_\d{4}_players\.csv$',f) and f[:15]>stamp)
        if newer: miss.append('a newer LineStar pull exists ('+', '.join(hm(int(x[:2])*60+int(x[2:])) for x in newer)+') and was not used - rule 3')
        else: ok.append(f'newest LineStar pull of the day ({hm(pullmin)})')
    if not os.path.exists(raw): miss.append('the raw LineStar file (AggProj) is missing next to the players file - every projection fell back to LineStar alone - rule 6')
    gl=str(g.game_date.max())[:10]
    if not asof:
        age=(datetime.date.fromisoformat(today)-datetime.date.fromisoformat(gl)).days
        if age>1: miss.append(f'game logs stop at {gl}, {age} days back - the 3:00 PM data refresh may not have run (fine only if no NBA games were played since) - rule 2')
        else: ok.append(f'game logs through {gl}')
    # 3. the FanDuel files and the LineStar slate belong to one slate
    ent=[r for r in t[1:] if r and r[0]]
    tsl=sorted({r[1].split('-')[0] for r in ent if len(r)>1 and r[1]}); fdslate=tsl[0] if len(tsl)==1 else None
    if len(tsl)>1: miss.append(f'the upload template holds entries for more than one FanDuel slate: {tsl}')
    pm=re.search(r'-(\d{5,7})-players-list',os.path.basename(pl))
    if pm and fdslate and pm.group(1)!=fdslate: miss.append(f'the FanDuel players list is slate {pm.group(1)} but the upload template is slate {fdslate}')
    elif pm and fdslate: ok.append(f'players list and template are both FanDuel slate {fdslate}')
    else: notes.append('FanDuel slate number not readable from the players-list file name or the template - the two files were not cross-checked')
    td=re.search(r'NBA-(\d{4}-\d{2}-\d{2})-',os.path.basename(tpl))
    if td and pulldate and td.group(1)!=pulldate: miss.append(f'the upload template is dated {td.group(1)} but the LineStar pull is dated {pulldate}')
    fk=set(fd_all.k); oa=ow_all.copy(); oa['k']=oa.name.map(k); oa['hit']=oa.k.isin(fk)
    sc=(oa.groupby('slate').hit.sum()-oa.groupby('slate').hit.apply(lambda x:(~x).sum())).sort_values(ascending=False)
    if int(slate) not in sc.index or not oa[oa.slate==int(slate)].hit.any(): miss.append(f'no projected ownership for LineStar slate {slate} in this pull - the v1.3 shadow and the ownership columns are not valid - rule H')
    elif sc.iloc[0]>sc[int(slate)]: miss.append(f'LineStar slate {slate} was passed, but slate {sc.index[0]} fits the FanDuel list better - rule 2')
    else: ok.append(f'LineStar slate {slate} fits the FanDuel list')
    # 4. timing against the actual lock
    tips=fd_all.tip.dropna(); lock=clock(os.environ.get('NBA_LOCK')) or (int(tips.min()) if len(tips) else None)
    if lock is None: miss.append('no game times in the LineStar file and no NBA_LOCK given - build timing not checked - rule 3')
    elif pullmin is not None:
        gap=lock-pullmin
        if gap<0: miss.append(f'the LineStar pull ({hm(pullmin)}) is after the first tip ({hm(lock)}) - this script builds pre-lock sets only - rule 3')
        elif gap>25: miss.append(f'the LineStar pull ({hm(pullmin)}) is {gap} minutes before lock ({hm(lock)}); the build belongs on a pull about 15 minutes before lock - rule 3')
        else: ok.append(f'pull {hm(pullmin)} is {gap} minutes before lock {hm(lock)}')
    # 5. projections
    nls=int((ls.ls_proj>0).sum())
    if nls<=15: miss.append(f'only {nls} players carry a LineStar projection - the LineStar login cookie has expired - rule 2')
    pg=fd_all.assign(p=(fd_all.ls_proj>0)).groupby('Game').p.sum(); thin=pg[pg<10]
    if len(thin): miss.append(f'LineStar projections thin or missing for game(s) { {a:int(c) for a,c in thin.items()} } - rule 2')
    else: ok.append(f'LineStar projections for all {len(pg)} games')
    if nagg<0.9*len(fd): miss.append(f'AggProj missing for {len(fd)-nagg} of {len(fd)} eligible players (LineStar number used for them) - rule 6')
    else: ok.append(f'AggProj on {nagg} of {len(fd)} eligible players')
    # 6. starters, exclusions, and when they were pulled
    teams=sorted(fd_all.Team.dropna().unique())
    if not st_raw: miss.append('no starters list was passed - rules 4 and 10')
    else:
        cnt=fd_all[fd_all.starter].groupby('Team').size().reindex(teams,fill_value=0); off=cnt[cnt!=5]
        if len(off): miss.append(f'the starters list does not match five players for every team: { {a:int(c) for a,c in off.items()} } - rule 4')
        else: ok.append(f'five starters matched for each of {len(teams)} teams')
    fl={}
    for nn,ln in zip(fd_all.Nickname,fd_all['Last Name']): fl.setdefault(k(ln),[]).append(str(nn))
    def lastk(x):
        w=re.sub(r'\b(jr|sr|ii|iii|iv)\b\.?','',str(x).lower()).split(); return k(w[-1]) if w else ''
    def unmatched(names):
        near=[]; far=[]
        for x in names:
            if k(x) in fk: continue
            c=fl.get(lastk(x)) or [str(fd_all.Nickname[fd_all.k==y].iloc[0]) for y in difflib.get_close_matches(k(x),sorted(fk),n=3,cutoff=0.8)]
            if c: near.append(f'{x} (FanDuel has {", ".join(c[:3])})')
            else: far.append(x)
        return near,far
    near,far=unmatched(st_raw)
    if near or far: miss.append('starter name(s) not matched to the FanDuel list: '+'; '.join(near+far)+' - rule 4')
    near,far=unmatched(ex_raw)
    if near: miss.append('exclusion name(s) not matched to the FanDuel list, so they were NOT excluded: '+'; '.join(near)+' - rule 10')
    if far: notes.append('exclusion name(s) not on the FanDuel list at all (no effect): '+', '.join(far))
    if len(zero): miss.append('listed starter(s) with no LineStar projection, status review owed: '+', '.join(map(str,zero.Nickname))+' - rule 4')
    rf=clock(os.environ.get('NBA_REFRESH'))
    if rf is None: miss.append('the time the starting lineups and the injury report were pulled is not recorded - pass NBA_REFRESH="3:47 PM" (Pacific) - rule 2')
    elif pullmin is not None and abs(rf-pullmin)>20: miss.append(f'lineups and injury report were pulled at {hm(rf)}, {abs(rf-pullmin)} minutes from the LineStar pull ({hm(pullmin)}); the refresh must be one refresh - rule 2')
    else: ok.append(f'lineups and injury report pulled at {hm(rf)}')
    if len(dep): notes.append(f'depleted team(s), 8 or fewer healthy players - look at them by hand: { {a:int(c) for a,c in dict(dep).items()} } - rule 5')
    # 7. the sets
    for nme,L in sh.items():
        if len(L)<4:
            if nme=='shadow_v13': notes.append(f'{nme}: only {len(L)} of 4 lineups can be built under the v1.3 rules on this slate (known on large slates); logged as is')
            else: miss.append(f'{nme}: only {len(L)} of 4 lineups were built - rule H')
    if MODE=='v14' and all(len(L)==4 for L in sh.values()): ok.append(f'four live lineups and {len(sh)} shadow sets built')
    # 8. the upload file, re-read from disk
    COLS=['PG','SG','SF','PF','C','G/F','F/C','UTIL','UTIL']; bad=[]; w=list(csv.reader(open(out)))
    if w[0][4:13]!=COLS: bad.append('the template columns are not PG, SG, SF, PF, C, G/F, F/C, UTIL, UTIL')
    if len(w)-1!=len(ent): bad.append(f'{len(w)-1} rows written for {len(ent)} entries')
    idx={str(fd.Id[i]):i for i in fd.index}; ovl=lkw.get('ov',OV); tc=lkw.get('teamcap',3); seen=[]
    for j,r in enumerate(w[1:]):
        ids=r[4:13]
        if j<len(ent) and r[:4]!=ent[j][:4]: bad.append(f'row {j+1}: the entry columns changed')
        if len(ids)!=9 or len(set(ids))!=9 or any(x not in idx for x in ids): bad.append(f'row {j+1}: not nine different eligible players'); continue
        I=[idx[x] for x in ids]
        if any(COLS[q] not in fd.sl[i] for q,i in enumerate(I)): bad.append(f'row {j+1}: a player sits in a slot he cannot fill')
        if fd.Salary[I].sum()>60000: bad.append(f'row {j+1}: salary over $60,000')
        if fd.Team[I].value_counts().max()>tc: bad.append(f'row {j+1}: more than {tc} players from one team')
        if set(ids) not in seen: seen.append(set(ids))
    if any(len(a&c)>ovl for q,a in enumerate(seen) for c in seen[q+1:]): bad.append(f'two lineups share more than {ovl} players')
    if len(seen)!=min(4,len(ent)): bad.append(f'{len(seen)} different lineups in the file for {len(ent)} entries')
    if bad: miss.append('the upload file failed validation: '+'; '.join(bad))
    else: ok.append(f'upload file valid ({len(w)-1} entries: slots, salary, team cap, overlap {ovl})')
    # 9. contests (rules 19-20)
    cs={}
    for r in ent:
        c=cs.setdefault(r[1],dict(name=r[2],fee=r[3],n=0)); c['n']+=1
    def fee(x):
        try: return float(str(x).replace('$','').replace(',',''))
        except Exception: return 0.0
    total=sum(fee(c['fee'])*c['n'] for c in cs.values()); prim=None
    if not ent: miss.append('the upload template has no entries - rule 19')
    if len(ent) and len(ent)<4: notes.append(f'only {len(ent)} entries in the template - lineups {len(ent)+1}-4 are built but not entered')
    if len(cs)>2: miss.append(f'{len(cs)} contests in the template; a primary and at most one secondary are allowed - rule 19')
    banned=[c['name'] for c in cs.values() if re.search(r'double.?up|crossover',c['name'],re.I)]
    if banned: miss.append('a double-up or Crossover contest is entered: '+'; '.join(banned)+' - rule 20')
    over=[c['name'] for c in cs.values() if c['n']>4]
    if over: miss.append('more than four entries in one contest, so a lineup repeats inside it: '+'; '.join(over)+' - rule 19')
    if len(cs)==1: prim=list(cs.values())[0]['name']
    elif len(cs)>1:
        want=(os.environ.get('NBA_PRIMARY') or '').strip().lower(); hits=[c['name'] for c in cs.values() if want and want in c['name'].lower()]
        if len(hits)==1: prim=hits[0]
        else: miss.append('more than one contest is entered and the primary is not named - pass NBA_PRIMARY="<part of its name>" - rules 19 and 22')
    bar='='*100
    print('\n'+bar)
    if miss:
        print(f'PROTOCOL RUN: NOT FULL - {len(miss)} item(s). This block goes at the very top of the reply to Phong, word for word.')
        for q,x in enumerate(miss,1): print(f'  {q}. {x}')
    else:
        print(f'PROTOCOL RUN: FULL - v1.4, script hash {mysha}, LineStar pull {hm(pullmin)}, lock {hm(lock)}. This line goes at the very top of the reply to Phong.')
    for x in notes: print('NOTE: '+x)
    print('Passed: '+'; '.join(ok)+'.')
    print('Contests in the template: '+('; '.join(f"{c['name']} x{c['n']} at ${c['fee']}" for c in cs.values()) or 'none')+f'. Fees ${total:g}.'+(f' Primary: {prim}.' if prim else ''))
    if lock is not None: print(f'Lock {hm(lock)} Pacific. Upload confirmed by {hm(lock-5)}. Not covered by this check: the recheck before lock, late swap (rules 15-18), contest choice by rake (rule 21), grading.')
    print(bar)
    return dict(status='NOT FULL' if miss else 'FULL',missing=miss,notes=notes,passed=ok,checked_pacific=now.strftime('%Y-%m-%d %H:%M'),
                lock=None if lock is None else hm(lock),linestar_pull=None if pullmin is None else hm(pullmin),refresh=os.environ.get('NBA_REFRESH'),
                ratified_sha=exp or None,fd_slate=fdslate,contests=list(cs.values()),fees=total,primary=prim)
try: man['protocol_run']=run_check()
except Exception as e:
    why=f'the run check itself failed ({type(e).__name__}: {e}) - treat this build as unchecked'
    man['protocol_run']=dict(status='NOT FULL',missing=[why])
    print('\n'+'='*100+f'\nPROTOCOL RUN: NOT FULL - 1 item(s). This block goes at the very top of the reply to Phong, word for word.\n  1. {why}\n'+'='*100)
json.dump(man,open(out.replace('.csv','_lineups.json'),'w'))
