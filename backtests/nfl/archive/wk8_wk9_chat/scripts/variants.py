"""Grid of builder variants, all with the 8:30 inactives repair. Scores each config x week; LOO selection done in loo.py."""
import os, sys, json, itertools, bisect, csv, re
os.environ['REPAIR'] = '1'
sys.path.insert(0, '/home/claude/bt/scripts')
import build
from multiprocessing import Pool
import pulp

GRID = dict(stack=[1, 2], bring=[0, 1], alpha=[0, 1, 2], qb=['itt', 'total'], dst=['oppitt', 'cheap'], rbfloor=[0, 20000])
FILES = {'wk1': '/home/claude/bt/133104.csv', 'wk2': '/mnt/user-data/uploads/134251-280648284.csv',
         'wk3': '/mnt/user-data/uploads/134503-280745135.csv', 'wk4': '/mnt/user-data/uploads/134747-280845253.csv',
         'wk5': '/mnt/user-data/uploads/135023-280945043.csv'}

def solve(P, qb, cfg, prior, expo, must_share=None, avoid_dst=None, avoid_rbset=None):
    m = pulp.LpProblem('lu', pulp.LpMaximize)
    x = {p['pid']: pulp.LpVariable('x' + p['pid'], cat='Binary') for p in P}
    by = lambda f: [p for p in P if f(p)]
    m += pulp.lpSum(p['p2'] * x[p['pid']] for p in P)
    m += x[qb['pid']] == 1
    for pos, k in (('QB', 1), ('RB', 3), ('WR', 3), ('TE', 1), ('DST', 1)):
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, pos=pos: p['pos'] == pos)) == k
    sal = pulp.lpSum(p['salary'] * x[p['pid']] for p in P)
    m += sal <= 60000; m += sal >= 59500
    if cfg['rbfloor']: m += pulp.lpSum(p['salary'] * x[p['pid']] for p in by(lambda p: p['pos'] == 'RB')) >= cfg['rbfloor']
    catchers = by(lambda p: p['team'] == qb['team'] and p['pos'] in ('WR', 'TE'))
    m += pulp.lpSum(x[p['pid']] for p in catchers) >= cfg['stack']
    m += pulp.lpSum(x[p['pid']] for p in catchers) <= 3
    if cfg['bring']:
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['team'] == qb['opp'] and p['pos'] in ('RB', 'WR', 'TE'))) >= 1
    for p in by(lambda p: p['pos'] == 'RB' and p['team'] == qb['team']): m += x[p['pid']] == 0
    for g in set(p['game'] for p in P):
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, g=g: p['pos'] == 'RB' and p['game'] == g)) <= 1
    for d in by(lambda p: p['pos'] == 'DST'):
        for p in by(lambda p, d=d: p['team'] == d['opp'] and p['pos'] in ('QB', 'WR', 'TE')):
            m += x[d['pid']] + x[p['pid']] <= 1
    for p in by(lambda p: p['pos'] in ('RB', 'WR', 'TE') and p['salary'] <= 4500 and p['game'] != qb['game']):
        m += x[p['pid']] == 0
    for pid, c in expo.items():
        if c >= 3 and pid in x and pid != qb['pid']: m += x[pid] == 0
    for L in prior: m += pulp.lpSum(x[pid] for pid in L if pid in x) <= 5
    if must_share: m += pulp.lpSum(x[pid] for pid in must_share) >= 1
    if avoid_dst: m += x[avoid_dst] == 0
    if avoid_rbset: m += pulp.lpSum(x[pid] for pid in avoid_rbset) <= 2
    m.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))
    if pulp.LpStatus[m.status] != 'Optimal': return None
    return [p for p in P if x[p['pid']].value() > 0.5]

def run(wk, cfg):
    P, games = build.load(wk)
    mean_itt = sum(v['itt'] for v in games.values()) / len(games)
    for p in P:
        if p['pos'] == 'DST':
            base = 7 + 0.6 * (mean_itt - games[p['opp']]['itt'])
            p['p2'] = base + (0.5 * (p['salary'] / 1000 - 4) if cfg['dst'] == 'oppitt' else -0.8 * (p['salary'] / 1000 - 4))
        else:
            p['p2'] = (p['salary'] - 3000) / 1000 * build.MULT[p['pos']] * (games[p['team']]['itt'] / mean_itt) ** cfg['alpha']
        p['opp'] = games[p['team']]['opp']
    key = (lambda p: (-p['itt'], -p['salary'])) if cfg['qb'] == 'itt' else (lambda p: (-games[p['team']]['total'], -p['itt']))
    qbs = sorted([p for p in P if p['pos'] == 'QB' and 6800 <= p['salary'] <= 7600], key=key)
    picked, used = [], set()
    for q in qbs:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    prior, expo, out = [], {}, []
    for q in picked:
        for k in range(2):
            if k == 0: L = solve(P, q, cfg, prior, expo)
            else:
                A = out[-1] if out and out[-1] else None
                if A is None: L = solve(P, q, cfg, prior, expo)
                else:
                    share = [p['pid'] for p in A if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')]
                    dst = [p['pid'] for p in A if p['pos'] == 'DST'][0]
                    rbs = [p['pid'] for p in A if p['pos'] == 'RB']
                    L = solve(P, q, cfg, prior, expo, share, dst, rbs)
            out.append(L or [])
            if L:
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
    return [[p['pid'] for p in L] for L in out]

def job(args):
    wk, cfg = args
    try: return (wk, json.dumps(cfg, sort_keys=True), run(wk, cfg))
    except Exception as e: return (wk, json.dumps(cfg, sort_keys=True), str(e))

if __name__ == '__main__':
    cfgs = [dict(zip(GRID, v)) for v in itertools.product(*GRID.values())]
    jobs = [(wk, c) for wk in FILES for c in cfgs]
    with Pool(os.cpu_count()) as pool:
        res = pool.map(job, jobs, chunksize=4)
    json.dump(res, open('/home/claude/bt/variants_lineups.json', 'w'))
    print('configs', len(cfgs), 'jobs', len(jobs), 'errors', sum(1 for r in res if isinstance(r[2], str)))
