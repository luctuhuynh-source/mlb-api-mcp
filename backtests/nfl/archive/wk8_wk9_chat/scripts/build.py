"""Blind rebuild of 6 NFL FD lineups per week under NFL FD v1.2/v1.2a/v1.2b/v1.3/v1.3a + book 11.
Reads ONLY build/ files (name, position, salary, team) and pre-lock lines. Never opens sealed/ results."""
import csv, sys, json, os
REPAIR = os.environ.get('REPAIR') == '1'
INACT = json.load(open('/home/claude/bt/build/inactives.json')) if REPAIR else {}
import pulp

AB = {'Arizona Cardinals':'ARI','Atlanta Falcons':'ATL','Baltimore Ravens':'BAL','Buffalo Bills':'BUF','Carolina Panthers':'CAR',
'Chicago Bears':'CHI','Cincinnati Bengals':'CIN','Cleveland Browns':'CLE','Dallas Cowboys':'DAL','Denver Broncos':'DEN',
'Detroit Lions':'DET','Green Bay Packers':'GB','Houston Texans':'HOU','Indianapolis Colts':'IND','Jacksonville Jaguars':'JAX',
'Kansas City Chiefs':'KC','Las Vegas Raiders':'LV','Los Angeles Chargers':'LAC','Los Angeles Rams':'LAR','Miami Dolphins':'MIA',
'Minnesota Vikings':'MIN','New England Patriots':'NE','New Orleans Saints':'NO','New York Giants':'NYG','New York Jets':'NYJ',
'Philadelphia Eagles':'PHI','Pittsburgh Steelers':'PIT','San Francisco 49ers':'SF','Seattle Seahawks':'SEA','Tennessee Titans':'TEN',
'Washington Commanders':'WAS','Tampa Bay Buccaneers':'TB'}
MULT = {'QB':2.65,'RB':2.15,'WR':2.0,'TE':1.75}
CAP, MAXUNUSED = 60000, 500
QB_BAND = (6800, 7600)

WK5_POOL = '/root/.claude/uploads/3eb2421d-9eec-59a8-8c78-d010d6054058/cd6153f7-FanDuel-NFL-2026_PDT-10_PDT-11_PDT-135023-players-list.csv'

def load(wk):
    n = int(wk[2:])
    games = {}
    for r in csv.DictReader(open('/home/claude/bt/build/lines.csv')):
        if int(r['week']) != n: continue
        a, h = AB[r['away']], AB[r['home']]
        S, T = float(r['home_spread']), float(r['total'])
        itt_h, itt_a = (T - S) / 2, (T + S) / 2      # home spread negative = home favored
        games[h] = dict(opp=a, itt=itt_h, total=T, spread=S, game=f'{a}@{h}')
        games[a] = dict(opp=h, itt=itt_a, total=T, spread=-S, game=f'{a}@{h}')
    out_status = {}
    if n == 5:   # the real Week 5 pool file carries pre-lock designations
        for r in csv.DictReader(open(WK5_POOL, encoding='utf-8-sig')):
            out_status[r['Id'].split('-')[1]] = r['Injury Indicator']
    players = []
    for r in csv.DictReader(open(f'/home/claude/bt/build/{wk}_t.csv')):
        t = r['team']
        if t not in games: continue
        if out_status.get(r['pid'], '') in ('O', 'IR', 'D', 'NA'): continue
        if r['pid'] in INACT.get(wk, []): continue   # 8:30 AM official inactives (pre-lock repair)
        r['salary'] = int(r['salary'])
        r['pos'] = 'DST' if r['pos'] == 'D' else r['pos']
        g = games[t]
        mean_itt = sum(v['itt'] for v in games.values()) / len(games)
        if r['pos'] == 'DST':
            r['proj'] = 7 + 0.6 * (mean_itt - games[g['opp']]['itt']) + 0.5 * (r['salary'] / 1000 - 4)
        else:
            if r['salary'] <= 4000: continue        # A93 opportunity screen: min-price = no role signal
            r['proj'] = (r['salary'] - 3000) / 1000 * MULT[r['pos']] * (g['itt'] / mean_itt)   # A92 Vegas-derived baseline
        r['opp'] = g['opp']; r['game'] = g['game']; r['itt'] = g['itt']
        players.append(r)
    return players, games

def solve(P, qb, games, prior, expo, must_share=None, avoid_dst=None, avoid_rbset=None):
    m = pulp.LpProblem('lu', pulp.LpMaximize)
    x = {p['pid']: pulp.LpVariable('x' + p['pid'], cat='Binary') for p in P}
    by = lambda f: [p for p in P if f(p)]
    m += pulp.lpSum(p['proj'] * x[p['pid']] for p in P)
    m += x[qb['pid']] == 1
    m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['pos'] == 'QB')) == 1
    m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['pos'] == 'RB')) == 3        # RB/RB/FLEX (v1.2b FLEX=RB)
    m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['pos'] == 'WR')) == 3
    m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['pos'] == 'TE')) == 1        # no TE at FLEX
    m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['pos'] == 'DST')) == 1
    sal = pulp.lpSum(p['salary'] * x[p['pid']] for p in P)
    m += sal <= CAP; m += sal >= CAP - MAXUNUSED                                    # v1.2b <=$500 unused
    m += pulp.lpSum(p['salary'] * x[p['pid']] for p in by(lambda p: p['pos'] == 'RB')) >= 20000   # v1.3 rule 2
    catchers = by(lambda p: p['team'] == qb['team'] and p['pos'] in ('WR', 'TE'))
    m += pulp.lpSum(x[p['pid']] for p in catchers) >= 2                              # GPP stack QB + 2
    m += pulp.lpSum(x[p['pid']] for p in catchers) <= 3
    for p in by(lambda p: p['pos'] == 'RB' and p['team'] == qb['team']):            # A96 QB + own RB flagged -> excluded
        m += x[p['pid']] == 0
    for g in set(p['game'] for p in P):                                              # A96 no two RBs same game
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, g=g: p['pos'] == 'RB' and p['game'] == g)) <= 1
    for d in by(lambda p: p['pos'] == 'DST'):                                        # v1.2 negative-correlation gate
        for p in by(lambda p, d=d: p['team'] == d['opp'] and p['pos'] in ('QB', 'WR', 'TE')):
            m += x[d['pid']] + x[p['pid']] <= 1
    for p in by(lambda p: p['pos'] in ('RB', 'WR', 'TE') and p['salary'] <= 4500 and p['game'] != qb['game']):
        m += x[p['pid']] == 0                                                        # v1.3 r3: cheap plays must be stack-correlated
    for pid, c in expo.items():                                                      # exposure <= 3 of 6
        if c >= 3 and pid in x and pid != qb['pid']: m += x[pid] == 0
    for L in prior:                                                                  # overlap <= 5
        m += pulp.lpSum(x[pid] for pid in L if pid in x) <= 5
    if must_share:
        m += pulp.lpSum(x[pid] for pid in must_share) >= 1
    if avoid_dst: m += x[avoid_dst] == 0
    if avoid_rbset: m += pulp.lpSum(x[pid] for pid in avoid_rbset) <= 2
    m.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[m.status] != 'Optimal': return None
    return [p for p in P if x[p['pid']].value() > 0.5]

def run(wk):
    P, games = load(wk)
    qbs = sorted([p for p in P if p['pos'] == 'QB' and QB_BAND[0] <= p['salary'] <= QB_BAND[1]],
                 key=lambda p: (-p['itt'], -p['salary']))
    picked, used_games = [], set()
    for q in qbs:                                   # environment board: top implied totals, one QB per game
        if q['game'] in used_games: continue
        picked.append(q); used_games.add(q['game'])
        if len(picked) == 3: break
    prior, expo, lineups = [], {}, []
    for q in picked:
        for k in range(2):
            if k == 0:
                L = solve(P, q, games, prior, expo)
            else:
                A = lineups[-1]['players']
                share = [p['pid'] for p in A if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')]
                dst = [p['pid'] for p in A if p['pos'] == 'DST'][0]
                rbs = [p['pid'] for p in A if p['pos'] == 'RB']
                L = solve(P, q, games, prior, expo, must_share=share, avoid_dst=dst, avoid_rbset=rbs)
            if L is None:
                lineups.append(dict(qb=q['name'], players=[], note='NO LEGAL LINEUP')); continue
            ids = [p['pid'] for p in L]
            prior.append(ids)
            for pid in ids: expo[pid] = expo.get(pid, 0) + 1
            lineups.append(dict(qb=q['name'], players=L))
    return P, games, picked, lineups

if __name__ == '__main__':
    out = {}
    for wk in ['wk1', 'wk2', 'wk3', 'wk4', 'wk5']:
        P, games, picked, lineups = run(wk)
        out[wk] = []
        print(f'=== {wk}: QBs', [(q['name'], q['team'], q['salary'], round(q['itt'], 2)) for q in picked])
        for i, L in enumerate(lineups, 1):
            ps = L['players']
            if not ps: print(f'  L{i} {L["qb"]}: NO LEGAL LINEUP'); out[wk].append([]); continue
            order = {'QB': 0, 'RB': 1, 'WR': 2, 'TE': 3, 'DST': 4}
            ps = sorted(ps, key=lambda p: (order[p['pos']], -p['salary']))
            sal = sum(p['salary'] for p in ps)
            rbsal = sum(p['salary'] for p in ps if p['pos'] == 'RB')
            print(f'  L{i} ${sal} (unused {60000-sal}, RB ${rbsal}): ' + ' | '.join(f"{p['pos']} {p['name']} {p['team']} {p['salary']}" for p in ps))
            out[wk].append([dict(pid=p['pid'], name=p['name'], pos=p['pos'], team=p['team'], salary=p['salary']) for p in ps])
    fn = '/home/claude/bt/frozen_repaired.json' if REPAIR else '/home/claude/bt/frozen_lineups.json'
    json.dump(out, open(fn, 'w'), indent=1)
    print('FROZEN ->', fn)
