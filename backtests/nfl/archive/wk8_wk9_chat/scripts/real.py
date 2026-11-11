"""Weeks 2-5 backtest on REAL FanDuel player lists (teams + pre-lock injury tags).
Pre-lock: O / D / IR / NA removed. 8:30 check: only Q-tagged players who did not play (0 pts, <1% owned) are removed.
Builder = variants.solve (today's rules or bring-back + cheap DST), 3 QBs x k lineups. Payouts: Week 5 exact table; Weeks 2-4 percentile-mapped."""
import csv, json, sys, bisect, re
sys.path.insert(0, '/home/claude/bt/scripts')
from build import AB, MULT
from variants import solve
U = '/root/.claude/uploads/3eb2421d-9eec-59a8-8c78-d010d6054058/'
POOLS = {'wk2': U + 'a48a5c25-FanDuel-NFL-2026_PDT-09_PDT-20_PDT-134251-players-list.csv',
         'wk3': U + 'be8c6d38-FanDuel-NFL-2026_PDT-09_PDT-27_PDT-134503-players-list.csv',
         'wk4': U + 'd3a3b81f-FanDuel-NFL-2026_PDT-10_PDT-04_PDT-134747-players-list.csv',
         'wk5': U + 'cd6153f7-FanDuel-NFL-2026_PDT-10_PDT-11_PDT-135023-players-list.csv'}
FILES = {'wk2': '/mnt/user-data/uploads/134251-280648284.csv', 'wk3': '/mnt/user-data/uploads/134503-280745135.csv',
         'wk4': '/mnt/user-data/uploads/134747-280845253.csv', 'wk5': '/mnt/user-data/uploads/135023-280945043.csv'}
FIX = {'JAC': 'JAX', 'LA': 'LAR', 'WSH': 'WAS'}
TABLE = [(1,1,250000),(2,2,80000),(3,3,40000),(4,4,20000),(5,5,10000),(6,6,5000),(7,7,3000),(8,8,2000),(9,9,1500),(10,10,1000),
 (11,12,800),(13,15,600),(16,20,500),(21,30,400),(31,50,300),(51,75,200),(76,100,150),(101,200,125),(201,300,100),(301,500,80),
 (501,1000,70),(1001,1500,60),(1501,2000,55),(2001,3000,50),(3001,5000,45),(5001,7000,40),(7001,10000,35),(10001,15000,30),(15001,25274,25)]
N5 = 99740

def results(wk):
    fp, own, pts = {}, {}, []
    with open(FILES[wk], encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            if len(row) >= 11 and row[6].strip():
                m = re.match(r'(.*) \((\d+)-(\d+)\)', row[6]); fp[m.group(3)] = float(row[9]); own[m.group(3)] = float(row[8].rstrip('%'))
            if row[0].strip() and row[3] not in ('', 'null'): pts.append(float(row[3]))
    return fp, own, sorted(pts)

def load(wk, fp, own, repair_q=True):
    n = int(wk[2:]); games = {}
    for r in csv.DictReader(open('/home/claude/bt/build/lines.csv')):
        if int(r['week']) != n: continue
        a, h = AB[r['away']], AB[r['home']]; S, T = float(r['home_spread']), float(r['total'])
        games[h] = dict(opp=a, itt=(T - S) / 2, total=T, game=f'{a}@{h}')
        games[a] = dict(opp=h, itt=(T + S) / 2, total=T, game=f'{a}@{h}')
    mean_itt = sum(v['itt'] for v in games.values()) / len(games)
    P, dropped_q, unmatched = [], [], set()
    for r in csv.DictReader(open(POOLS[wk], encoding='utf-8-sig')):
        t = FIX.get(r['Team'], r['Team'])
        if t not in games: unmatched.add(t); continue
        tag = r['Injury Indicator']; pid = r['Id'].split('-')[1]
        if tag in ('O', 'D', 'IR', 'NA'): continue                      # pre-lock designations
        if repair_q and tag == 'Q' and fp.get(pid, 0) == 0 and own.get(pid, 0) < 1:
            dropped_q.append(r['Nickname']); continue                    # 8:30 check resolves the Q tag: did not play
        pos = 'DST' if r['Position'] == 'D' else r['Position']
        sal = int(r['Salary']); g = games[t]
        if pos in ('RB', 'WR', 'TE') and sal <= 4000: continue           # A93 opportunity screen
        p = dict(pid=pid, name=r['Nickname'], pos=pos, salary=sal, team=t, opp=g['opp'], game=g['game'], itt=g['itt'])
        P.append(p)
    return P, games, mean_itt, dropped_q, unmatched

def run(wk, cfg, per_qb, fp, own, repair_q=True):
    P, games, mean_itt, dq, um = load(wk, fp, own, repair_q)
    for p in P:
        if p['pos'] == 'DST':
            base = 7 + 0.6 * (mean_itt - games[p['opp']]['itt'])
            p['p2'] = base + (0.5 * (p['salary'] / 1000 - 4) if cfg['dst'] == 'oppitt' else -0.8 * (p['salary'] / 1000 - 4))
        else:
            p['p2'] = (p['salary'] - 3000) / 1000 * MULT[p['pos']] * (p['itt'] / mean_itt) ** cfg['alpha']
    qbs = sorted([p for p in P if p['pos'] == 'QB' and 6800 <= p['salary'] <= 7600], key=lambda p: (-p['itt'], -p['salary']))
    picked, used = [], set()
    for q in qbs:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    cap = (3 * per_qb) // 2; prior, expo, out = [], {}, []
    for q in picked:
        first = None
        for k in range(per_qb):
            e = {pid: 3 for pid, c in expo.items() if c >= cap}
            if first is None: L = solve(P, q, cfg, prior, e)
            else:
                share = [p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')]
                last = out[-1] or first
                L = solve(P, q, cfg, prior, e, share, [p['pid'] for p in last if p['pos'] == 'DST'][0],
                          [p['pid'] for p in last if p['pos'] == 'RB'])
            out.append(L or [])
            if L:
                if first is None: first = L
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
    return out, picked, dq, um

def prize(wk, s, sp):
    better = len(sp) - bisect.bisect_right(sp, s)
    rank = better + 1 if wk == 'wk5' else max(1, int(round((better + 1) / len(sp) * N5)))
    for a, b, pz in TABLE:
        if a <= rank <= b: return pz
    return 0

if __name__ == '__main__':
    R = {wk: results(wk) for wk in FILES}
    CFGS = [('TODAY RULES', dict(stack=2, bring=0, alpha=1, qb='itt', dst='oppitt', rbfloor=20000)),
            ('+bring+cheapDST', dict(stack=2, bring=1, alpha=1, qb='itt', dst='cheap', rbfloor=20000))]
    report = {}
    for wk in FILES:
        _, _, _, dq, um = load(wk, R[wk][0], R[wk][1])
        print(f'{wk}: Q-tagged resolved OUT at 8:30 -> {dq}; pool teams not on Main lines: {sorted(um)}')
    for label, cfg in CFGS:
        for per_qb in (2, 3, 5):
            rows = []; detail = {}
            for wk in FILES:
                fp, own, sp = R[wk]
                Ls, picked, _, _ = run(wk, cfg, per_qb, fp, own)
                won = cash = top1 = 0; pcts = []; missing = 0
                for L in Ls:
                    if not L: continue
                    missing += sum(1 for p in L if p['pid'] not in fp)
                    s = sum(fp.get(p['pid'], 0) for p in L); pz = prize(wk, s, sp)
                    won += pz; cash += pz > 0; top1 += s >= sp[int(len(sp) * .99)]
                    pcts.append(100 * bisect.bisect_left(sp, s) / len(sp))
                rows.append(dict(wk=wk, n=len([L for L in Ls if L]), cash=cash, top1=top1, fees=15 * len(Ls), won=won,
                                 pct=sum(pcts) / len(pcts), qbs=[q['name'] for q in picked], undrafted_picks=missing))
                detail[wk] = [[dict(pos=p['pos'], name=p['name'], team=p['team'], salary=p['salary'], pts=fp.get(p['pid'], 0)) for p in L] for L in Ls]
            tf = sum(r['fees'] for r in rows); tw = sum(r['won'] for r in rows)
            print(f"\n{label} | 3 QBs x {per_qb}: fees ${tf} won ${tw} net ${tw - tf} ROI {100 * (tw - tf) / tf:+.0f}% | cashed {sum(r['cash'] for r in rows)}/{sum(r['n'] for r in rows)} | top1 {sum(r['top1'] for r in rows)}")
            for r in rows:
                print(f"   {r['wk']}: QBs {r['qbs']} cash {r['cash']}/{r['n']} won ${r['won']} vs fees ${r['fees']} avg beats {r['pct']:.0f}% undrafted picks {r['undrafted_picks']}")
            report[f'{label}|{per_qb}'] = dict(rows=rows, lineups=detail)
    json.dump(report, open('/home/claude/bt/real_report.json', 'w'), indent=1)
