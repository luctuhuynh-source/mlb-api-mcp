import csv, sys, pulp, itertools
SRC = sys.argv[1]; OUT = sys.argv[2]
P = list(csv.DictReader(open(SRC)))
for p in P:
    p['proj'] = float(p['proj']); p['sal'] = int(p['sal']); p['n'] = int(p['n'])
    p['pos'] = p['Position']; p['tm'] = p['Team']
    p['inj'] = (p['Injury Indicator'] or '').strip()
QB_OK = set(sys.argv[3].split(','))
CORE = set(sys.argv[4].split(',')) if len(sys.argv)>4 else set()          # teams whose starter passed the QB gate
# eligibility: F1 O out, F4 Q/D out, F3 n<=2 out (no role verification in pre-flight), F5 floors, F2 QB gate
elig = []
for p in P:
    if p['inj'] in ('O', 'Q', 'D'): continue
    if p['n'] <= 2: continue
    if p['pos'] == 'QB':
        if p['proj'] < 10 or p['Nickname'] not in QB_OK: continue
    else:
        if p['proj'] < 6: continue
    elig.append(p)
print('eligible', len(elig), 'QBs', sum(p['pos']=='QB' for p in elig))
teams = sorted({p['tm'] for p in elig})
games = sorted({p['Game'] for p in elig}) if 'Game' in elig[0] else None

def build(prev, used_count, force_two_qb, max_use):
    m = pulp.LpProblem('lu', pulp.LpMaximize)
    x = {i: pulp.LpVariable(f'x{i}', cat='Binary') for i in range(len(elig))}
    s = {i: pulp.LpVariable(f's{i}', cat='Binary') for i in range(len(elig))}  # in SuperFLEX
    m += pulp.lpSum(x[i]*elig[i]['proj'] for i in x)
    m += pulp.lpSum(x.values()) == 7
    m += pulp.lpSum(x[i]*elig[i]['sal'] for i in x) <= 60000
    m += pulp.lpSum(x[i]*elig[i]['sal'] for i in x) >= 58500
    for i in x: m += s[i] <= x[i]
    m += pulp.lpSum(s.values()) == 1
    qb = [i for i in x if elig[i]['pos']=='QB']; rb = [i for i in x if elig[i]['pos']=='RB']
    wr = [i for i in x if elig[i]['pos'] in ('WR','TE')]
    # base slots: 1 QB, 2 RB, 3 WR; SF adds one of any
    m += pulp.lpSum(x[i] for i in qb) - pulp.lpSum(s[i] for i in qb) == 1
    m += pulp.lpSum(x[i] for i in rb) - pulp.lpSum(s[i] for i in rb) == 2
    m += pulp.lpSum(x[i] for i in wr) - pulp.lpSum(s[i] for i in wr) == 3
    if force_two_qb == 2: m += pulp.lpSum(x[i] for i in qb) == 2
    if force_two_qb == 1: m += pulp.lpSum(x[i] for i in qb) == 1
    for t in teams:
        ti = [i for i in x if elig[i]['tm']==t]
        tq = [i for i in ti if elig[i]['pos']=='QB']
        m += pulp.lpSum(x[i] for i in ti) <= 3 + pulp.lpSum(x[i] for i in tq)   # 3, 4 with stack team
        m += pulp.lpSum(x[i] for i in ti if elig[i]['pos']=='RB') <= 1          # C8
        # C2 stack: each QB needs own WR/TE proj>=8
        partners = [i for i in ti if elig[i]['pos'] in ('WR','TE') and elig[i]['proj']>=8]
        for q in tq: m += pulp.lpSum(x[i] for i in partners) >= x[q]
    # 3 teams, 2 games (FanDuel) — teams>=3 implied by caps; games>=2:
    # overlap <=5 with previous lineups; exposure
    for L in prev: m += pulp.lpSum(x[i] for i in L) <= 5
    for i in x:
        if used_count.get(i,0) >= (4 if elig[i]['Nickname'] in CORE else max_use): m += x[i] == 0
    m.solve(pulp.PULP_CBC_CMD(msg=0))
    sel = [i for i in x if x[i].value() > 0.5]; sf = [i for i in sel if s[i].value() > 0.5][0]
    return sel, sf

def show(sel, sf, tag):
    order = sorted(sel, key=lambda i: ({'QB':0,'RB':1,'WR':2,'TE':2}[elig[i]['pos']], -elig[i]['proj']))
    order = [i for i in order if i != sf] + [sf]
    tot = sum(elig[i]['proj'] for i in sel); sal = sum(elig[i]['sal'] for i in sel)
    print(f'{tag}  ${sal}  proj {tot:.1f}')
    for i in order:
        p = elig[i]; slot = 'SF' if i == sf else p['pos']
        print(f"   {slot:2} {p['Nickname']:22} {p['tm']:5} ${p['sal']:5} proj {p['proj']:5.1f} kick {p['kick']}")
    return order

rows = []; prev = []; used = {}
for k in range(4):
    sel, sf = build(prev, used, 2, 3)
    order = show(sel, sf, f'L{k+1}')
    prev.append(sel)
    for i in sel: used[i] = used.get(i,0)+1
    rows.append([f"{elig[i]['Id']}:{elig[i]['Nickname']}" for i in order])
sel, sf = build([], {}, 1, 9); show(sel, sf, 'SHADOW best 1-QB')
sel, sf = build([], {}, 0, 9); show(sel, sf, 'SHADOW free choice')
with open(OUT,'w',newline='') as f:
    w = csv.writer(f); w.writerows(rows)
