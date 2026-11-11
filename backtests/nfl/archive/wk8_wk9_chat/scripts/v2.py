"""v2 backtest engine, Weeks 2-5, real FanDuel pools, real payouts.
- Pair rule fixed: non-stack pair in <= 2 of 6 lineups (protocol v1.2) — now enforced.
- Projections: 'salary' (current stand-in) or 'q75' (75th-pct quantile regression, trained on the OTHER weeks only).
- Arms: qb_lo, valve, bring, overlap/expo, dst_cap, role gate (nflverse prior-week WOPR/touch share).
Nothing from the evaluated week's results is used in construction."""
import csv, json, sys, bisect, re, itertools, os
import numpy as np
sys.path.insert(0, '/home/claude/bt/scripts')
from build import AB, MULT
import pulp
U = '/root/.claude/uploads/3eb2421d-9eec-59a8-8c78-d010d6054058/'
POOLS = {'wk2': U + 'a48a5c25-FanDuel-NFL-2026_PDT-09_PDT-20_PDT-134251-players-list.csv',
         'wk3': U + 'be8c6d38-FanDuel-NFL-2026_PDT-09_PDT-27_PDT-134503-players-list.csv',
         'wk4': U + 'd3a3b81f-FanDuel-NFL-2026_PDT-10_PDT-04_PDT-134747-players-list.csv',
         'wk5': U + 'cd6153f7-FanDuel-NFL-2026_PDT-10_PDT-11_PDT-135023-players-list.csv'}
FILES = {'wk2': '/mnt/user-data/uploads/134251-280648284.csv', 'wk3': '/mnt/user-data/uploads/134503-280745135.csv',
         'wk4': '/mnt/user-data/uploads/134747-280845253.csv', 'wk5': '/mnt/user-data/uploads/135023-280945043.csv'}
WEEKS = list(POOLS)
FIX = {'JAC': 'JAX', 'LA': 'LAR', 'WSH': 'WAS'}
TABLE = [(1,1,250000),(2,2,80000),(3,3,40000),(4,4,20000),(5,5,10000),(6,6,5000),(7,7,3000),(8,8,2000),(9,9,1500),(10,10,1000),
 (11,12,800),(13,15,600),(16,20,500),(21,30,400),(31,50,300),(51,75,200),(76,100,150),(101,200,125),(201,300,100),(301,500,80),
 (501,1000,70),(1001,1500,60),(1501,2000,55),(2001,3000,50),(3001,5000,45),(5001,7000,40),(7001,10000,35),(10001,15000,30),(15001,25274,25)]
N5 = 99740
BASE = dict(proj='salary', qb_lo=6800, valve=False, bring=False, overlap=5, expo=3, dst_cap=None, role=False, pair=True)

# ---------- data ----------
_res = {}
def results(wk):
    if wk in _res: return _res[wk]
    fp, own, pts = {}, {}, []
    with open(FILES[wk], encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            if len(row) >= 11 and row[6].strip():
                m = re.match(r'(.*) \((\d+)-(\d+)\)', row[6]); fp[m.group(3)] = float(row[9]); own[m.group(3)] = float(row[8].rstrip('%'))
            if row[0].strip() and row[3] not in ('', 'null'): pts.append(float(row[3]))
    _res[wk] = (fp, own, sorted(pts)); return _res[wk]

def games_for(wk):
    n = int(wk[2:]); g = {}
    for r in csv.DictReader(open('/home/claude/bt/build/lines.csv')):
        if int(r['week']) != n: continue
        a, h = AB[r['away']], AB[r['home']]; S, T = float(r['home_spread']), float(r['total'])
        g[h] = dict(opp=a, itt=(T - S) / 2, total=T, spread=S, game=f'{a}@{h}')
        g[a] = dict(opp=h, itt=(T + S) / 2, total=T, spread=-S, game=f'{a}@{h}')
    return g

_role = None
def role_table():
    """nflverse weekly stats -> per (name, team, week): target_share, wopr, carries, team carries share."""
    global _role
    if _role is not None: return _role
    rows = list(csv.DictReader(open('/home/claude/bt/ext/stats_player_week_2026.csv')))
    team_car = {}
    for r in rows:
        k = (r['team'], int(r['week'])); team_car[k] = team_car.get(k, 0) + float(r['carries'] or 0)
    _role = {}
    for r in rows:
        if r['position'] not in ('RB', 'WR', 'TE'): continue
        t = FIX.get(r['team'], r['team']); w = int(r['week'])
        _role[(r['player_display_name'], t, w)] = dict(ts=float(r['target_share'] or 0), wopr=float(r['wopr'] or 0),
            car_share=float(r['carries'] or 0) / max(team_car[(r['team'], w)], 1))
    return _role

def role_prior(name, team, wk):
    """Trailing-2-week role (weeks strictly before wk). Returns None if no rows."""
    n = int(wk[2:]); R = role_table(); vals = [R.get((name, team, w)) for w in (n - 1, n - 2)]
    vals = [v for v in vals if v]
    if not vals: return None
    return dict(ts=max(v['ts'] for v in vals), wopr=max(v['wopr'] for v in vals), car_share=max(v['car_share'] for v in vals))

def load(wk, repair_q=True):
    fp, own, _ = results(wk); games = games_for(wk)
    mean_itt = sum(v['itt'] for v in games.values()) / len(games)
    P = []
    for r in csv.DictReader(open(POOLS[wk], encoding='utf-8-sig')):
        t = FIX.get(r['Team'], r['Team'])
        if t not in games: continue
        tag = r['Injury Indicator']; pid = r['Id'].split('-')[1]
        if tag in ('O', 'D', 'IR', 'NA'): continue
        if repair_q and tag == 'Q' and fp.get(pid, 0) == 0 and own.get(pid, 0) < 1: continue
        pos = 'DST' if r['Position'] == 'D' else r['Position']; sal = int(r['Salary']); g = games[t]
        if pos in ('RB', 'WR', 'TE') and sal <= 4000: continue
        fppg = float(r['FPPG']) if r['FPPG'] not in ('', None) else 0.0
        P.append(dict(pid=pid, name=r['Nickname'], pos=pos, salary=sal, team=t, opp=g['opp'], game=g['game'], itt=g['itt'],
                      opp_itt=games[g['opp']]['itt'], spread=g['spread'], total=g['total'], fppg=fppg, played=int(r['Played'] or 0),
                      mean_itt=mean_itt, actual=fp.get(pid, 0.0)))
    return P, games, mean_itt

# ---------- projections ----------
POS = ['QB', 'RB', 'WR', 'TE', 'DST']
def feats(p):
    d = [1.0 if p['pos'] == k else 0.0 for k in POS]
    s = p['salary'] / 1000; f = p['fppg']; it = p['itt']; oi = p['opp_itt']
    x = d + [s, f, it, oi, p['spread'], s * f, s * it, f * it]
    for k in POS: x += [s if p['pos'] == k else 0.0, f if p['pos'] == k else 0.0]
    return x

_q = {}
def q75_model(test_wk):
    if test_wk in _q: return _q[test_wk]
    from sklearn.linear_model import QuantileRegressor
    from sklearn.preprocessing import StandardScaler
    X, y = [], []
    for wk in WEEKS:
        if wk == test_wk: continue
        for p in load(wk)[0]: X.append(feats(p)); y.append(p['actual'])
    sc = StandardScaler().fit(X)
    m = QuantileRegressor(quantile=0.75, alpha=0.1, solver='highs').fit(sc.transform(X), y)
    _q[test_wk] = (sc, m); return _q[test_wk]

def project(P, wk, cfg):
    if cfg['proj'] == 'salary':
        for p in P:
            if p['pos'] == 'DST': p['p2'] = 7 + 0.6 * (p['mean_itt'] - p['opp_itt']) + 0.5 * (p['salary'] / 1000 - 4)
            else: p['p2'] = (p['salary'] - 3000) / 1000 * MULT[p['pos']] * (p['itt'] / p['mean_itt'])
    else:
        sc, m = q75_model(wk); pred = m.predict(sc.transform([feats(p) for p in P]))
        for p, v in zip(P, pred): p['p2'] = float(v)

# ---------- builder ----------
def solve(P, qb, cfg, prior, expo, pairs, must_share=None, avoid_dst=None, avoid_rbset=None):
    m = pulp.LpProblem('lu', pulp.LpMaximize)
    x = {p['pid']: pulp.LpVariable('x' + p['pid'], cat='Binary') for p in P}
    by = lambda f: [p for p in P if f(p)]
    m += pulp.lpSum(p['p2'] * x[p['pid']] for p in P)
    m += x[qb['pid']] == 1
    for pos, k in (('QB', 1), ('RB', 3), ('WR', 3), ('TE', 1), ('DST', 1)):
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, pos=pos: p['pos'] == pos)) == k
    sal = pulp.lpSum(p['salary'] * x[p['pid']] for p in P); m += sal <= 60000; m += sal >= 59500
    m += pulp.lpSum(p['salary'] * x[p['pid']] for p in by(lambda p: p['pos'] == 'RB')) >= 20000
    catchers = by(lambda p: p['team'] == qb['team'] and p['pos'] in ('WR', 'TE'))
    m += pulp.lpSum(x[p['pid']] for p in catchers) >= 2; m += pulp.lpSum(x[p['pid']] for p in catchers) <= 3
    if cfg['bring']: m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['team'] == qb['opp'] and p['pos'] in ('RB', 'WR', 'TE'))) >= 1
    for p in by(lambda p: p['pos'] == 'RB' and p['team'] == qb['team']): m += x[p['pid']] == 0
    for g in set(p['game'] for p in P):
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, g=g: p['pos'] == 'RB' and p['game'] == g)) <= 1
    for d in by(lambda p: p['pos'] == 'DST'):
        for p in by(lambda p, d=d: p['team'] == d['opp'] and p['pos'] in ('QB', 'WR', 'TE')): m += x[d['pid']] + x[p['pid']] <= 1
        if cfg['dst_cap'] and d['salary'] > cfg['dst_cap']: m += x[d['pid']] == 0
    cheap_off = by(lambda p: p['pos'] in ('RB', 'WR', 'TE') and p['salary'] <= 4500 and p['game'] != qb['game'])
    if cfg['valve']:
        ok = [p for p in cheap_off if p['fppg'] >= 8.0]
        for p in cheap_off:
            if p not in ok: m += x[p['pid']] == 0
        m += pulp.lpSum(x[p['pid']] for p in ok) <= 1
    else:
        for p in cheap_off: m += x[p['pid']] == 0
    if cfg['role']:   # WR/TE in stack or bring-back need prior WOPR>=.30 or TS>=.18; RB needs car_share>=.35
        for p in by(lambda p: p['pos'] in ('WR', 'TE') and p['team'] in (qb['team'], qb['opp'])):
            rp = role_prior(p['name'], p['team'], cfg['_wk'])
            if rp is not None and rp['wopr'] < 0.30 and rp['ts'] < 0.18: m += x[p['pid']] == 0
        for p in by(lambda p: p['pos'] == 'RB'):
            rp = role_prior(p['name'], p['team'], cfg['_wk'])
            if rp is not None and rp['car_share'] < 0.35: m += x[p['pid']] == 0
    for pid, c in expo.items():
        if c >= cfg['expo'] and pid in x and pid != qb['pid']: m += x[pid] == 0
    for L in prior: m += pulp.lpSum(x[pid] for pid in L if pid in x) <= cfg['overlap']
    if cfg['pair']:
        for (a, b), c in pairs.items():
            if c >= 2 and a in x and b in x: m += x[a] + x[b] <= 1
    if must_share: m += pulp.lpSum(x[pid] for pid in must_share) >= 1
    if avoid_dst: m += x[avoid_dst] == 0
    if avoid_rbset: m += pulp.lpSum(x[pid] for pid in avoid_rbset) <= 2
    m.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=60))
    if pulp.LpStatus[m.status] != 'Optimal': return None
    return [p for p in P if x[p['pid']].value() > 0.5]

def run(wk, cfg):
    cfg = dict(cfg); cfg['_wk'] = wk
    P, games, mean_itt = load(wk); project(P, wk, cfg)
    qbs = sorted([p for p in P if p['pos'] == 'QB' and cfg['qb_lo'] <= p['salary'] <= 7600], key=lambda p: (-p['itt'], -p['salary']))
    picked, used = [], set()
    for q in qbs:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    prior, expo, pairs, out = [], {}, {}, []
    for q in picked:
        first = None
        for k in range(2):
            if first is None: L = solve(P, q, cfg, prior, expo, pairs)
            else:
                share = [p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')]
                L = solve(P, q, cfg, prior, expo, pairs, share, [p['pid'] for p in first if p['pos'] == 'DST'][0],
                          [p['pid'] for p in first if p['pos'] == 'RB'])
            out.append(L or [])
            if L:
                if first is None: first = L
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
                stack = {p['pid'] for p in L if p['pos'] == 'QB' or (p['team'] == q['team'] and p['pos'] in ('WR', 'TE'))}
                for a, b in itertools.combinations(sorted(ids), 2):
                    if a in stack and b in stack: continue
                    pairs[(a, b)] = pairs.get((a, b), 0) + 1
    return out, picked

def prize(wk, s, sp):
    better = len(sp) - bisect.bisect_right(sp, s)
    rank = better + 1 if wk == 'wk5' else max(1, int(round((better + 1) / len(sp) * N5)))
    for a, b, pz in TABLE:
        if a <= rank <= b: return pz
    return 0

def score(wk, Ls):
    fp, own, sp = results(wk); rows = []
    for L in Ls:
        if not L: rows.append(dict(score=0, pct=0, prize=0, top5=False)); continue
        s = sum(p['actual'] for p in L)
        rows.append(dict(score=s, pct=100 * bisect.bisect_left(sp, s) / len(sp), prize=prize(wk, s, sp), top5=s >= sp[int(len(sp) * .95)],
                         zeros=sum(1 for p in L if p['pos'] != 'DST' and p['actual'] == 0)))
    return rows

def evaluate(name, cfg):
    per = {}
    for wk in WEEKS:
        Ls, picked = run(wk, cfg); rows = score(wk, Ls)
        per[wk] = dict(qbs=[q['name'] + ' $' + str(q['salary']) for q in picked], n=len([L for L in Ls if L]),
                       cash=sum(1 for r in rows if r['prize'] > 0), won=sum(r['prize'] for r in rows), fees=15 * len(Ls),
                       best_pct=max(r['pct'] for r in rows), avg_pct=sum(r['pct'] for r in rows) / len(rows),
                       top5=sum(1 for r in rows if r['top5']), zeros=sum(r.get('zeros', 0) for r in rows),
                       lineups=[[dict(pos=p['pos'], name=p['name'], team=p['team'], salary=p['salary'], pts=p['actual']) for p in L] for L in Ls])
    fees = sum(v['fees'] for v in per.values()); won = sum(v['won'] for v in per.values())
    return dict(name=name, cfg=cfg, per=per, fees=fees, won=won, roi=100 * (won - fees) / fees,
                cash=sum(v['cash'] for v in per.values()), top5=sum(v['top5'] for v in per.values()), zeros=sum(v['zeros'] for v in per.values()))

def show(R, base=None):
    print(f"\n== {R['name']}: fees ${R['fees']} won ${R['won']} ROI {R['roi']:+.0f}% | cash {R['cash']}/24 | top5% {R['top5']} | zero-pt skill slots {R['zeros']}")
    for wk, v in R['per'].items():
        bp = f" (base {base['per'][wk]['best_pct']:.0f})" if base else ''
        print(f"   {wk}: QBs {v['qbs']} | cash {v['cash']}/6 won ${v['won']} | best {v['best_pct']:.0f}%{bp} avg {v['avg_pct']:.0f}% | zeros {v['zeros']}")
    if base:
        wins = sum(1 for wk in WEEKS if R['per'][wk]['best_pct'] > base['per'][wk]['best_pct'])
        print(f"   vs baseline: best-of-6 better in {wins}/4 weeks | ROI {R['roi'] - base['roi']:+.0f} pts | top5% {R['top5'] - base['top5']:+d} | cash {R['cash'] - base['cash']:+d}")

if __name__ == '__main__':
    arms = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None
    out = {}
    base = evaluate('BASELINE v1.3 (pair rule fixed)', BASE); show(base); out['base'] = base
    if arms is None:
        arms = {'q75 projection': dict(proj='q75'), 'QB band $6,000': dict(qb_lo=6000), 'off-game valve': dict(valve=True),
                'bring-back required': dict(bring=True), 'overlap<=3 expo<=2': dict(overlap=3, expo=2), 'DST<=$3,800': dict(dst_cap=3800),
                'role gate (nflverse)': dict(role=True)}
    for name, d in arms.items():
        cfg = dict(BASE); cfg.update(d); R = evaluate(name, cfg); show(R, base); out[name] = R
    json.dump(out, open('/home/claude/bt/v2_results.json', 'w'), indent=1)
