"""LIVE Week 6 build — NFL FD v1.5 (props 50/50 blend + v1.4 role gate + v1.4c name fix), 3 QBs x PER_QB.
No results data exists for this week; nothing post-lock is read."""
import csv, json, sys, itertools, os
sys.path.insert(0, '/home/claude/bt/scripts')
from build import AB, MULT
import v3
from v3 import solve3, rb_window, rb_eligible, norm
from props import props_table, fd_points, nm

WK = 'wk7'; PER_QB = int(os.environ.get('PER_QB', 5)); BLEND = float(os.environ.get('BLEND', 0.5))
POOL = '/home/claude/bt/wk7/pool.csv'
FIX = {'JAC': 'JAX', 'LA': 'LAR', 'WSH': 'WAS'}

def games():
    g = {}
    for r in csv.DictReader(open('/home/claude/bt/build/lines_wk7.csv')):
        a, h = AB[r['away']], AB[r['home']]; S, T = float(r['home_spread']), float(r['total'])
        g[h] = dict(opp=a, itt=(T - S) / 2, total=T, spread=S, game=f'{a}@{h}')
        g[a] = dict(opp=h, itt=(T + S) / 2, total=T, spread=-S, game=f'{a}@{h}')
    return g

def load():
    G = games(); mean_itt = sum(v['itt'] for v in G.values()) / len(G)
    T = props_table(WK); P = []; flags = []
    for r in csv.DictReader(open(POOL, encoding='utf-8-sig')):
        t = FIX.get(r['Team'], r['Team'])
        if t not in G: continue
        tag = r['Injury Indicator']
        if tag in ('O', 'D', 'IR', 'NA'): continue
        pos = 'DST' if r['Position'] == 'D' else r['Position']; sal = int(r['Salary']); g = G[t]
        if pos in ('RB', 'WR', 'TE') and sal <= 4000: continue
        p = dict(pid=r['Id'].split('-')[1], fdid=r['Id'], name=r['Nickname'], pos=pos, salary=sal, team=t, opp=g['opp'], game=g['game'],
                 itt=g['itt'], opp_itt=G[g['opp']]['itt'], mean_itt=mean_itt, tag=tag, fppg=float(r['FPPG'] or 0))
        if pos == 'DST':
            p['p2'] = 7 + 0.6 * (mean_itt - p['opp_itt']) + 0.5 * (sal / 1000 - 4); p['props'] = None
        else:
            o = T.get((nm(p['name']), tuple(g['game'].split('@'))))
            sal_p = (sal - 3000) / 1000 * MULT[pos] * (g['itt'] / mean_itt)
            if o: p['props'] = fd_points(o, pos); p['p2'] = BLEND * sal_p + (1 - BLEND) * p['props']
            else: flags.append(f"{p['name']} ({pos} {t}) UNPRICED by books -> excluded (v1.5a)"); continue
            if tag == 'Q':
                if o is None: flags.append(f"{p['name']} ({pos} {t}) Q-tagged and UNPRICED by books -> excluded"); continue
                flags.append(f"{p['name']} ({pos} {t}) Q-tagged but priced by books -> eligible, verify at 8:30")
        P.append(p)
    return P, G, flags

def build():
    P, G, flags = load()
    cfg = dict(mode='flat', per_qb=PER_QB, _wk=WK)
    W = rb_window(WK)
    for p in P:
        if p['pos'] == 'RB': p['elig'] = rb_eligible(p, W, 'flat')
    qbs = sorted([p for p in P if p['pos'] == 'QB' and 6800 <= p['salary'] <= 7600], key=lambda p: (-p['itt'], -p['salary']))
    picked, used = [], set()
    for q in qbs:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    prior, expo, pairs, out = [], {}, {}, []
    for q in picked:
        first = None
        for k in range(PER_QB):
            args = (None, None, None) if first is None else ([p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')],
                     [p['pid'] for p in (out[-1] or first) if p['pos'] == 'DST'][0], [p['pid'] for p in (out[-1] or first) if p['pos'] == 'RB'])
            L = solve3(P, q, cfg, prior, expo, pairs, *args)
            out.append(L or [])
            if L:
                if first is None: first = L
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
                stack = {p['pid'] for p in L if p['pos'] == 'QB' or (p['team'] == q['team'] and p['pos'] in ('WR', 'TE'))}
                for a, b in itertools.combinations(sorted(ids), 2):
                    if not (a in stack and b in stack): pairs[(a, b)] = pairs.get((a, b), 0) + 1
    return P, G, flags, picked, out

if __name__ == '__main__':
    P, G, flags, picked, out = build()
    board = sorted({(v['game'], v['total']) for v in G.values()}, key=lambda x: -x[1])
    print('ENV BOARD:', [(g, t, round(G[g.split('@')[0]]['itt'], 1), round(G[g.split('@')[1]]['itt'], 1)) for g, t in board])
    print('QBs:', [(q['name'], q['team'], q['salary'], round(q['itt'], 1)) for q in picked])
    print('FLAGS:', *flags, sep='\n  ')
    order = {'QB': 0, 'RB': 1, 'WR': 2, 'TE': 3, 'DST': 4}
    res = []
    for i, L in enumerate(out, 1):
        if not L: print(f'L{i}: NO LEGAL LINEUP'); res.append(None); continue
        L = sorted(L, key=lambda p: (order[p['pos']], -p['salary']))
        sal = sum(p['salary'] for p in L); proj = sum(p['p2'] for p in L)
        print(f"L{i} ${sal} proj {proj:.1f}: " + ' | '.join(f"{p['pos']} {p['name']} {p['team']} {p['salary']} ({p['p2']:.1f}{'' if p['props'] is not None or p['pos']=='DST' else ' unpriced'}{' Q' if p['tag']=='Q' else ''})" for p in L))
        res.append([dict(pos=p['pos'], name=p['name'], team=p['team'], salary=p['salary'], fdid=p['fdid'], proj=round(p['p2'], 2), tag=p['tag']) for p in L])
    exp = {}
    for L in res:
        for p in (L or []): exp[p['name']] = exp.get(p['name'], 0) + 1
    print('EXPOSURE:', sorted(exp.items(), key=lambda x: -x[1])[:15])
    json.dump(dict(qbs=[q['name'] for q in picked], lineups=res, flags=flags), open(f'/home/claude/bt/wk7/build_x{PER_QB}.json', 'w'), indent=1)
