"""CFB FanDuel live build - CANONICAL SCRIPT. Run this file as-is; never retype the rules from notes.
Live set = CFB FD protocol v1.4 as written in section 17 of the protocol doc (in force from 2026-11-07). It is the 11/7 build
(merge step + cfbcode/build_v14.py with its two edits) joined into one file, plus the run check.

Usage:
  python3 build_live.py <fd_players_list.csv> <linestar_players.csv> <linestar_projown.csv> <linestar_slate_id> \
                        <fd_entries_template.csv> <out_upload.csv> "<QBs that passed the QB gate, comma separated>" "<core players, max 2>"
  - QB gate list (F2): full names as FanDuel prints them. A QB not on this list cannot be rostered.
  - core (C5): at most two named players who may be in all four lineups; everyone else is in at most three.
Writes <out_upload.csv> (FanDuel upload) and <out_upload>_lineups.json = the run's manifest.

v1.4 as run: projection = 100% LineStar. Eligible = not tagged O/Q/D on the FanDuel list, not LineStar status 4 (out), more than 2 games
played, LineStar projection 10+ for a QB (and on the QB gate list) or 6+ for anyone else. Four lineups in sequence, each the best legal
lineup left: QB, RB, RB, WR/TE x3, SuperFLEX = second QB (mandatory); salary $58,500-$60,000; max 3 per team, 4 when that team's QB is
rostered; max 1 RB per team; every rostered QB needs one of his own WR/TE projected 8+; any two lineups share at most 5 of 7; a player
is in at most 3 of 4 lineups unless named core. Shadows (logged, never entered): best 1-QB lineup, best free-choice lineup.

RUN CHECK. The last block printed is "PROTOCOL RUN: FULL" or "PROTOCOL RUN: NOT FULL - n item(s)" with every item listed. That block goes
at the very top of the reply to Phong, word for word. It is saved in the manifest under "protocol_run". The check only reads.
  env CFB_RATIFIED_SHA = the script hash written in section 17 of the protocol doc
  env CFB_REFRESH      = Pacific time the QB gate and injury tags were last checked, e.g. "8:33 AM"
  env CFB_LOCK         = optional override of the first lock (Pacific), e.g. "9:00 AM"; default = earliest kick in the LineStar file
"""
VERSION='CFB FD v1.4 live + shadows (build_live.py 2026-11-11a)'
import csv, sys, re, os, json, hashlib, datetime, unicodedata, collections
import pulp
if len(sys.argv)<9: sys.exit('PROTOCOL RUN: STOPPED - build_live.py needs 8 arguments (usage at the top of the file). Nothing built. Tell Phong.')
pl,lsf,owf,slate,tpl,OUT,qbok_s,core_s=sys.argv[1:9]
for _n,_p in [('FanDuel players list',pl),('LineStar players file',lsf),('LineStar ownership file',owf),('FanDuel upload template',tpl)]:
    if not os.path.exists(_p): sys.exit(f'PROTOCOL RUN: STOPPED - {_n} not found: {_p}. Nothing built. Tell Phong.')
def norm(s): s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode(); s=re.sub(r'[^a-z ]','',s.lower()); return re.sub(r'\b(jr|sr|ii|iii|iv)\b','',s).strip()
LS=list(csv.DictReader(open(lsf)))
nproj=sum(1 for l in LS if float(l['ls_proj'] or 0)>0)
if nproj<=15: sys.exit(f'PROTOCOL RUN: STOPPED - only {nproj} players carry a LineStar projection in {os.path.basename(lsf)}: the LineStar login cookie has expired. Nothing built. Tell Phong: the cookie in ~/.linestar_auth on the Mac needs recopying.')
L={(norm(l['name']),l['team']):l for l in LS}
OW=list(csv.DictReader(open(owf)))
O={(norm(o['name']),o['team']):float(o['proj_owned']) for o in OW if o['slate']==str(slate)}
FD=list(csv.DictReader(open(pl,encoding='utf-8-sig')))
print(VERSION); print('LineStar file',os.path.basename(lsf),'| LineStar slate',slate,'| FanDuel players',len(FD))
# ---- merge (the 11/7 merge step) ----
P=[]
for p in FD:
    kk=(norm(p['Nickname']),p['Team']); l=L.get(kk)
    inj=(p['Injury Indicator'] or '').strip()
    if l and l['status']=='4' and not inj: inj='O'          # LineStar says out
    P.append(dict(Id=p['Id'],Nickname=p['Nickname'],pos=p['Position'],tm=p['Team'],sal=int(p['Salary']),n=int(p['Played'] or 0),inj=inj,
                  proj=float(l['ls_proj']) if l else 0.0,own=O.get(kk,0.0),kick=(l['game'].split(' ',1)[1] if l else ''),game=p.get('Game',''),matched=bool(l)))
QB_OK=set(x.strip() for x in qbok_s.split(',') if x.strip())
CORE=set(x.strip() for x in core_s.split(',') if x.strip())
# ---- eligibility (build_v14.py): O/Q/D out, 2 or fewer games out, QB 10+ and on the gate list, others 6+ ----
elig=[]
for p in P:
    if p['inj'] in ('O','Q','D'): continue
    if p['n']<=2: continue
    if p['pos']=='QB':
        if p['proj']<10 or p['Nickname'] not in QB_OK: continue
    else:
        if p['proj']<6: continue
    elig.append(p)
print('eligible',len(elig),'QBs',sum(p['pos']=='QB' for p in elig),'| injury tags removed',dict(collections.Counter(p['inj'] for p in P if p['inj'] in ('O','Q','D'))))
teams=sorted({p['tm'] for p in elig})
def build(prev,used_count,force_two_qb,max_use):
    m=pulp.LpProblem('lu',pulp.LpMaximize)
    x={i:pulp.LpVariable(f'x{i}',cat='Binary') for i in range(len(elig))}
    s={i:pulp.LpVariable(f's{i}',cat='Binary') for i in range(len(elig))}   # in SuperFLEX
    m+=pulp.lpSum(x[i]*elig[i]['proj'] for i in x)
    m+=pulp.lpSum(x.values())==7
    m+=pulp.lpSum(x[i]*elig[i]['sal'] for i in x)<=60000
    m+=pulp.lpSum(x[i]*elig[i]['sal'] for i in x)>=58500
    for i in x: m+=s[i]<=x[i]
    m+=pulp.lpSum(s.values())==1
    qb=[i for i in x if elig[i]['pos']=='QB']; rb=[i for i in x if elig[i]['pos']=='RB']
    wr=[i for i in x if elig[i]['pos'] in ('WR','TE')]
    m+=pulp.lpSum(x[i] for i in qb)-pulp.lpSum(s[i] for i in qb)==1
    m+=pulp.lpSum(x[i] for i in rb)-pulp.lpSum(s[i] for i in rb)==2
    m+=pulp.lpSum(x[i] for i in wr)-pulp.lpSum(s[i] for i in wr)==3
    if force_two_qb==2: m+=pulp.lpSum(x[i] for i in qb)==2
    if force_two_qb==1: m+=pulp.lpSum(x[i] for i in qb)==1
    for t in teams:
        ti=[i for i in x if elig[i]['tm']==t]
        tq=[i for i in ti if elig[i]['pos']=='QB']
        m+=pulp.lpSum(x[i] for i in ti)<=3+pulp.lpSum(x[i] for i in tq)          # C3: 3, 4 with the stack team
        m+=pulp.lpSum(x[i] for i in ti if elig[i]['pos']=='RB')<=1               # C8
        partners=[i for i in ti if elig[i]['pos'] in ('WR','TE') and elig[i]['proj']>=8]
        for q in tq: m+=pulp.lpSum(x[i] for i in partners)>=x[q]                 # C2 stack
    for Lp in prev: m+=pulp.lpSum(x[i] for i in Lp)<=5                           # C5 overlap
    for i in x:
        if used_count.get(i,0)>=(4 if elig[i]['Nickname'] in CORE else max_use): m+=x[i]==0   # C5 exposure, named core exempt
    m.solve(pulp.PULP_CBC_CMD(msg=0))
    if pulp.LpStatus[m.status]!='Optimal': return None,None
    sel=[i for i in x if x[i].value()>0.5]; sf=[i for i in sel if s[i].value()>0.5][0]
    q2=sorted([i for i in sel if elig[i]['pos']=='QB'],key=lambda i:(elig[i]['proj'],-i))
    if len(q2)==2: sf=q2[0]          # two QBs: the lower-projected one is written in the SuperFLEX column (same points either way; keeps the file repeatable)
    return sel,sf
def show(sel,sf,tag):
    order=sorted(sel,key=lambda i:({'QB':0,'RB':1,'WR':2,'TE':2}[elig[i]['pos']],-elig[i]['proj']))
    order=[i for i in order if i!=sf]+[sf]
    tot=sum(elig[i]['proj'] for i in sel); sal=sum(elig[i]['sal'] for i in sel)
    print(f"{tag}  ${sal}  proj {tot:.1f}  cum-own {sum(elig[i]['own'] for i in sel):.0f}%")
    for i in order:
        p=elig[i]; slot='SF' if i==sf else p['pos']
        print(f"   {slot:2} {p['Nickname']:22} {p['tm']:5} ${p['sal']:5} proj {p['proj']:5.1f} own {p['own']:4.1f}% kick {p['kick']}")
    return order
rows=[]; prev=[]; used={}; live=[]
for k in range(4):
    sel,sf=build(prev,used,2,3)
    if sel is None: sys.exit(f'PROTOCOL RUN: STOPPED - URGENT: only {k} of 4 lineups can be built under the v1.4 rules (QB gate list, core, caps). Nothing written. Tell Phong.')
    order=show(sel,sf,f'L{k+1}'); prev.append(sel); live.append(order)
    for i in sel: used[i]=used.get(i,0)+1
    rows.append([f"{elig[i]['Id']}:{elig[i]['Nickname']}" for i in order])
sh={}
for tag,f2 in [('shadow_1QB',1),('shadow_free_choice',0)]:
    sel,sf=build([],{},f2,9)
    sh[tag]=None if sel is None else dict(proj=round(sum(elig[i]['proj'] for i in sel),1),players=[f"{elig[i]['Id']}:{elig[i]['Nickname']}" for i in show(sel,sf,tag)])
def sha(p):
    try: return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]
    except Exception: return None
raw=lsf.replace('_players.csv','_raw.json.gz')
man=dict(version=VERSION,script_sha=sha(os.path.realpath(__file__)),built_utc=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),linestar_slate=slate,linestar=os.path.basename(lsf),
         inputs={n:dict(file=os.path.basename(p),sha=sha(p)) for n,p in [('fd_players',pl),('linestar_players',lsf),('linestar_projown',owf),('linestar_raw',raw),('fd_template',tpl)]},
         qb_gate=sorted(QB_OK),core=sorted(CORE),eligible=[p['Id'] for p in elig],live=rows,live_proj=[round(sum(elig[i]['proj'] for i in o),1) for o in live],shadows=sh)
json.dump(man,open(OUT.replace('.csv','_lineups.json'),'w'))
T=list(csv.reader(open(tpl))); ent=[r for r in T[1:] if r and r[0]]
out=[T[0]]+[r[:4]+rows[k%4]+['',''] for k,r in enumerate(ent)]
csv.writer(open(OUT,'w',newline='')).writerows(out); print(f'\nwrote {OUT}: {len(out)-1} entries')

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
    import subprocess, zoneinfo, difflib
    miss=[]; notes=[]; ok=[]
    now=datetime.datetime.now(zoneinfo.ZoneInfo('America/Los_Angeles')); today=now.strftime('%Y-%m-%d')
    me=os.path.realpath(__file__); mysha=sha(me)
    def git(where,*a):
        try: r=subprocess.run(['git','-C',where]+list(a),capture_output=True,text=True,timeout=20); return r.returncode,r.stdout.strip()
        except Exception: return 1,''
    rc,top=git(os.path.dirname(me),'rev-parse','--show-toplevel')
    rel=os.path.relpath(me,os.path.realpath(top)).replace(os.sep,'/') if rc==0 and top else ''
    inrepo=rel=='backtests/cfb/live/build_live.py' and git(top,'ls-files','--error-unmatch',rel)[0]==0 and git(top,'status','--porcelain','--',rel)[1]==''
    if inrepo: ok.append(f'script is the unmodified repo copy (commit {git(top,"rev-parse","--short","HEAD")[1]})')
    else: miss.append(f'the script that ran is not the unmodified repo copy backtests/cfb/live/build_live.py (it ran from {me})')
    exp=(os.environ.get('CFB_RATIFIED_SHA') or '').strip().lower()
    if not exp: miss.append('the script hash was not checked against the protocol doc - open the doc and pass CFB_RATIFIED_SHA=<hash in section 17>')
    elif exp[:16]!=mysha: miss.append(f'script hash {mysha} is not the hash ratified in the protocol doc ({exp[:16]})')
    else: ok.append(f'script hash {mysha} = the hash in the protocol doc')
    # inputs: one pull, dated today, the newest of the day (N1)
    b=os.path.basename(lsf); mm=re.match(r'(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})_players\.csv$',b); pullmin=None; pulldate=None
    if not mm: miss.append(f'the LineStar file name ({b}) carries no pull time - snapshot and timing not checked')
    else:
        pulldate=mm.group(1); stamp=b[:15]; pullmin=int(mm.group(2))*60+int(mm.group(3))
        if not os.path.basename(owf).startswith(stamp): miss.append(f'the ownership file ({os.path.basename(owf)}) is not from the same pull as {b}')
        if pulldate!=today: miss.append(f'the LineStar pull is dated {pulldate}; today is {today}')
        newer=sorted(f[11:15] for f in os.listdir(os.path.dirname(os.path.abspath(lsf))) if re.match(pulldate+r'_\d{4}_players\.csv$',f) and f[:15]>stamp)
        if newer: miss.append('a newer LineStar pull exists ('+', '.join(hm(int(x[:2])*60+int(x[2:])) for x in newer)+') and was not used')
        else: ok.append(f'newest LineStar pull of the day ({hm(pullmin)})')
    if not os.path.exists(raw): notes.append('the raw LineStar file is not next to the players file - the 8:30 snapshot is not fully archived (Process)')
    # FanDuel files and LineStar slate belong together
    tsl=sorted({r[1].split('-')[0] for r in ent if len(r)>1 and r[1]}); fdslate=tsl[0] if len(tsl)==1 else None
    if len(tsl)>1: miss.append(f'the upload template holds entries for more than one FanDuel slate: {tsl}')
    pm=re.search(r'-(\d{5,7})-players-list',os.path.basename(pl))
    if pm and fdslate and pm.group(1)!=fdslate: miss.append(f'the FanDuel players list is slate {pm.group(1)} but the upload template is slate {fdslate}')
    elif pm and fdslate: ok.append(f'players list and template are both FanDuel slate {fdslate}')
    else: notes.append('FanDuel slate number not readable from the file names - players list and template were not cross-checked')
    td=re.search(r'CFB-(\d{4}-\d{2}-\d{2})-',os.path.basename(tpl))
    if td and pulldate and td.group(1)!=pulldate: miss.append(f'the upload template is dated {td.group(1)} but the LineStar pull is dated {pulldate}')
    fk={(norm(p['Nickname']),p['tm']) for p in P}; sc=collections.Counter()
    for o in OW: sc[o['slate']]+=1 if (norm(o['name']),o['team']) in fk else -1
    if not O: miss.append(f'no projected ownership for LineStar slate {slate} in this pull - the ownership columns are empty')
    elif sc and max(sc.values())>sc[str(slate)]: miss.append(f'LineStar slate {slate} was passed, but slate {max(sc,key=sc.get)} fits the FanDuel list better')
    else: ok.append(f'LineStar slate {slate} fits the FanDuel list')
    if not any(p['inj'] for p in P): miss.append('the FanDuel list carries no injury tags at all (N1 hard failure)')
    # projections per game
    pg=collections.Counter(); gms=set()
    for p in P:
        gms.add(p['game'])
        if p['proj']>0: pg[p['game']]+=1
    thin={g:pg[g] for g in gms if g and pg[g]<10}
    if thin: miss.append(f'LineStar projections thin or missing for game(s) {thin}')
    else: ok.append(f'LineStar projections for all {len(gms)} games ({nproj} projected players in the pull)')
    # timing against the first lock
    tips=[clock(p['kick']) for p in P if p['kick']]; tips=[t for t in tips if t is not None]
    lock=clock(os.environ.get('CFB_LOCK')) or (min(tips) if tips else None)
    if lock is None: miss.append('no kick times in the LineStar file and no CFB_LOCK given - build timing not checked')
    elif pullmin is not None:
        gap=lock-pullmin
        if gap<0: miss.append(f'the LineStar pull ({hm(pullmin)}) is after the first lock ({hm(lock)}) - this script builds pre-lock sets only')
        elif gap>45: miss.append(f'the LineStar pull ({hm(pullmin)}) is {gap} minutes before the first lock ({hm(lock)}); the build belongs on the pull about 30 minutes before lock')
        else: ok.append(f'pull {hm(pullmin)} is {gap} minutes before first lock {hm(lock)}')
    # QB gate (F2), core (C5), refresh time
    names={p['Nickname'] for p in P}
    def unmatched(lst):
        o=[]
        for x in lst:
            if x in names: continue
            c=difflib.get_close_matches(x,sorted(names),n=2,cutoff=0.75); o.append(f'{x} (FanDuel has {", ".join(c)})' if c else x)
        return o
    if not QB_OK: miss.append('no QB gate list was passed (F2)')
    u=unmatched(sorted(QB_OK))
    if u: miss.append('QB gate name(s) not matched to the FanDuel list, so those QBs were NOT eligible: '+'; '.join(u))
    notqb=[x for x in QB_OK if x in names and not any(p['Nickname']==x and p['pos']=='QB' for p in P)]
    if notqb: miss.append('QB gate name(s) that are not quarterbacks on the FanDuel list: '+', '.join(notqb))
    if len(CORE)>2: miss.append(f'{len(CORE)} core players named; C5 allows at most 2')
    u=unmatched(sorted(CORE))
    if u: miss.append('core name(s) not matched to the FanDuel list: '+'; '.join(u))
    rf=clock(os.environ.get('CFB_REFRESH'))
    if rf is None: miss.append('the time the QB gate and injury tags were checked is not recorded - pass CFB_REFRESH="8:33 AM" (Pacific)')
    elif pullmin is not None and abs(rf-pullmin)>30: miss.append(f'QB gate and injuries were checked at {hm(rf)}, {abs(rf-pullmin)} minutes from the LineStar pull ({hm(pullmin)}); they belong in the same refresh')
    else: ok.append(f'QB gate and injuries checked at {hm(rf)}')
    for tag,v in sh.items():
        if v is None: miss.append(f'{tag} could not be built')
    if all(v is not None for v in sh.values()): ok.append('four live lineups and both shadows built')
    # the upload file, re-read from disk
    bad=[]; w=list(csv.reader(open(OUT))); idx={p['Id']:p for p in elig}; seen=[]; cnt=collections.Counter()
    if len(w)-1!=len(ent): bad.append(f'{len(w)-1} rows written for {len(ent)} entries')
    for j,r in enumerate(w[1:]):
        ids=[c.split(':')[0] for c in r[4:11]]
        if j<len(ent) and r[:4]!=ent[j][:4]: bad.append(f'row {j+1}: the entry columns changed')
        if len(set(ids))!=7 or any(i not in idx for i in ids): bad.append(f'row {j+1}: not seven different eligible players'); continue
        pp=[idx[i] for i in ids]; pos=[p['pos'] for p in pp]
        if pos[0]!='QB' or pos[1]!='RB' or pos[2]!='RB' or any(q not in ('WR','TE') for q in pos[3:6]) or pos[6]!='QB': bad.append(f'row {j+1}: slots are not QB, RB, RB, WR/TE x3, SuperFLEX QB')
        sal=sum(p['sal'] for p in pp)
        if sal>60000 or sal<58500: bad.append(f'row {j+1}: salary ${sal} outside $58,500-$60,000')
        tc=collections.Counter(p['tm'] for p in pp); qt={p['tm'] for p in pp if p['pos']=='QB'}
        if any(n>(4 if t in qt else 3) for t,n in tc.items()): bad.append(f'row {j+1}: team cap broken')
        if any(n>1 for n in collections.Counter(p['tm'] for p in pp if p['pos']=='RB').values()): bad.append(f'row {j+1}: two RBs from one team')
        for q in [p for p in pp if p['pos']=='QB']:
            if not any(p['tm']==q['tm'] and p['pos'] in ('WR','TE') and p['proj']>=8 for p in pp): bad.append(f'row {j+1}: {q["Nickname"]} has no stack partner')
        if set(ids) not in seen:
            seen.append(set(ids))
            for i in ids: cnt[i]+=1
    if any(len(a&c)>5 for q,a in enumerate(seen) for c in seen[q+1:]): bad.append('two lineups share more than 5 players')
    over=[idx[i]['Nickname'] for i,n in cnt.items() if n>3 and idx[i]['Nickname'] not in CORE]
    if over: bad.append('in all four lineups without being named core: '+', '.join(over))
    if len(seen)!=min(4,len(ent)): bad.append(f'{len(seen)} different lineups in the file for {len(ent)} entries')
    if not ent: miss.append('the upload template has no entries')
    if bad: miss.append('the upload file failed validation: '+'; '.join(bad))
    else: ok.append(f'upload file valid ({len(w)-1} entries: slots, salary, team caps, stacks, overlap, exposure)')
    cs={}
    for r in ent:
        c=cs.setdefault(r[1],dict(name=r[2],fee=r[3],n=0)); c['n']+=1
    def fee(x):
        try: return float(str(x).replace('$','').replace(',',''))
        except Exception: return 0.0
    total=sum(fee(c['fee'])*c['n'] for c in cs.values())
    bar='='*100
    print('\n'+bar)
    if miss:
        print(f'PROTOCOL RUN: NOT FULL - {len(miss)} item(s). This block goes at the very top of the reply to Phong, word for word.')
        for q,x in enumerate(miss,1): print(f'  {q}. {x}')
    else:
        print(f'PROTOCOL RUN: FULL - CFB v1.4, script hash {mysha}, LineStar pull {hm(pullmin)}, first lock {hm(lock)}. This line goes at the very top of the reply to Phong.')
    for x in notes: print('NOTE: '+x)
    print('Passed: '+'; '.join(ok)+'.')
    print('Contests in the template: '+('; '.join(f"{c['name']} x{c['n']} at ${c['fee']}" for c in cs.values()) or 'none')+f'. Fees ${total:g} (B1: 1% of the DFS bankroll is the ceiling; information only).')
    print('Not covered by this check: whether each QB on the gate list truly cleared F2, the later-window QB audits and swaps (C7), the props-hybrid shadow, grading.')
    print(bar)
    return dict(status='NOT FULL' if miss else 'FULL',missing=miss,notes=notes,passed=ok,checked_pacific=now.strftime('%Y-%m-%d %H:%M'),
                lock=None if lock is None else hm(lock),linestar_pull=None if pullmin is None else hm(pullmin),refresh=os.environ.get('CFB_REFRESH'),
                ratified_sha=exp or None,fd_slate=fdslate,contests=list(cs.values()),fees=total)
try: man['protocol_run']=run_check()
except Exception as e:
    why=f'the run check itself failed ({type(e).__name__}: {e}) - treat this build as unchecked'
    man['protocol_run']=dict(status='NOT FULL',missing=[why])
    print('\n'+'='*100+f'\nPROTOCOL RUN: NOT FULL - 1 item(s). This block goes at the very top of the reply to Phong, word for word.\n  1. {why}\n'+'='*100)
json.dump(man,open(OUT.replace('.csv','_lineups.json'),'w'))
