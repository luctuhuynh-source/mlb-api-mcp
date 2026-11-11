"""Profile every Sunday Million lineup (Weeks 1-5): what top-1% and cashing lineups do differently."""
import csv, re, json, sys
sys.path.insert(0, '/home/claude/bt/scripts')
from build import AB
FILES = {'wk1': '/home/claude/bt/133104.csv', 'wk2': '/mnt/user-data/uploads/134251-280648284.csv',
         'wk3': '/mnt/user-data/uploads/134503-280745135.csv', 'wk4': '/mnt/user-data/uploads/134747-280845253.csv',
         'wk5': '/mnt/user-data/uploads/135023-280945043.csv'}
PAT = re.compile(r'(QB|RB|WR|TE|D) (.+?) \(\d+-(\d+)\)')

def games_for(wk):
    n = int(wk[2:]); g = {}
    for r in csv.DictReader(open('/home/claude/bt/build/lines.csv')):
        if int(r['week']) != n: continue
        a, h = AB[r['away']], AB[r['home']]; S, T = float(r['home_spread']), float(r['total'])
        g[h] = dict(opp=a, itt=(T - S) / 2, total=T, game=f'{a}@{h}')
        g[a] = dict(opp=h, itt=(T + S) / 2, total=T, game=f'{a}@{h}')
    return g

def feats(wk):
    games = games_for(wk)
    team = {r['pid']: r['team'] for r in csv.DictReader(open(f'/home/claude/bt/build/{wk}_t.csv'))}
    sal = {r['pid']: int(r['salary']) for r in csv.DictReader(open(f'/home/claude/bt/build/{wk}_t.csv'))}
    own = {}; rows = []
    with open(FILES[wk], encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            if len(row) >= 11 and row[6].strip():
                m = re.match(r'(.*) \((\d+)-(\d+)\)', row[6]); own[m.group(3)] = float(row[8].rstrip('%'))
            if row[0].strip() and row[3] not in ('', 'null') and row[4].strip():
                rows.append((float(row[3]), row[4]))
    rows.sort(key=lambda x: -x[0]); n = len(rows)
    top_total = max(v['total'] for v in games.values())
    out = []
    for i, (pts, lu) in enumerate(rows):
        P = PAT.findall(lu)
        if len(P) != 9: continue
        tier = 'top1' if i < n * 0.01 else ('cash' if i < n * 0.20 else 'rest')
        pl = []
        for pos, name, pid in P:
            t = AB.get(name) if pos == 'D' else team.get(pid)
            pl.append((pos, pid, t, sal.get(pid, 0)))
        qb = pl[0]; qt = qb[2]
        if qt not in games: continue
        opp = games[qt]['opp']
        catchers = sum(1 for p in pl[1:8] if p[2] == qt and p[0] in ('WR', 'TE'))
        own_rb = sum(1 for p in pl[1:8] if p[2] == qt and p[0] == 'RB')
        bring = sum(1 for p in pl[1:8] if p[2] == opp)
        gcount = {}
        for p in pl[:8]:
            if p[2] in games: gcount[games[p[2]]['game']] = gcount.get(games[p[2]]['game'], 0) + 1
        rbs = [p for p in pl[1:8] if p[0] == 'RB']
        rb_games = [games[p[2]]['game'] for p in rbs if p[2] in games]
        dst = pl[8]
        dst_conf = sum(1 for p in pl[:8] if dst[2] in games and p[2] == games[dst[2]]['opp'])
        lown = [own.get(p[1], 0) for p in pl]
        out.append(dict(tier=tier, qb_sal=qb[3], qb_itt=games[qt]['itt'], qb_game_total=games[qt]['total'],
            qb_top_game=games[qt]['total'] == top_total, catchers=catchers, own_rb=own_rb, bring=bring,
            qb_game_n=gcount.get(games[qt]['game'], 0), max_game_n=max(gcount.values()) if gcount else 0,
            rb_sal=sum(p[3] for p in rbs), flex=pl[7][0], dst_sal=dst[3],
            dst_opp_itt=games[games[dst[2]]['opp']]['itt'] if dst[2] in games else None, dst_conflict=dst_conf,
            rb_same_game=len(rb_games) - len(set(rb_games)), unused=60000 - sum(p[3] for p in pl),
            cum_own=sum(lown), sub5=sum(1 for o in lown if o < 5)))
    return out

def summarize(F):
    def avg(k, t): xs = [f[k] for f in F if f['tier'] == t and f[k] is not None]; return sum(xs) / len(xs) if xs else 0
    def share(fn, t): xs = [f for f in F if f['tier'] == t]; return 100 * sum(1 for f in xs if fn(f)) / len(xs)
    S = {}
    for t in ('top1', 'cash', 'rest'):
        S[t] = dict(n=sum(1 for f in F if f['tier'] == t),
            qb_sal=avg('qb_sal', t), qb_itt=avg('qb_itt', t), qb_game_total=avg('qb_game_total', t),
            qb_in_top_total_game=share(lambda f: f['qb_top_game'], t),
            catchers=avg('catchers', t), stack0=share(lambda f: f['catchers'] == 0, t), stack1=share(lambda f: f['catchers'] == 1, t),
            stack2=share(lambda f: f['catchers'] == 2, t), stack3p=share(lambda f: f['catchers'] >= 3, t),
            bringback_any=share(lambda f: f['bring'] >= 1, t), bring_avg=avg('bring', t),
            qb_own_rb=share(lambda f: f['own_rb'] >= 1, t), qb_game_n=avg('qb_game_n', t), max_game_n=avg('max_game_n', t),
            rb_sal=avg('rb_sal', t), flex_rb=share(lambda f: f['flex'] == 'RB', t), dst_sal=avg('dst_sal', t),
            dst_opp_itt=avg('dst_opp_itt', t), dst_conflict=share(lambda f: f['dst_conflict'] > 0, t),
            rb_same_game=share(lambda f: f['rb_same_game'] > 0, t), unused=avg('unused', t),
            cum_own=avg('cum_own', t), sub5=avg('sub5', t))
    return S

if __name__ == '__main__':
    allS = {}
    for wk in FILES:
        F = feats(wk); allS[wk] = summarize(F)
        print(wk, 'parsed', len(F))
    json.dump(allS, open('/home/claude/bt/profile.json', 'w'), indent=1)
    keys = list(allS['wk1']['top1'].keys())
    print(f"{'metric':<22}" + ''.join(f"{wk+' '+t:>11}" for wk in FILES for t in ('top1', 'rest')))
    for k in keys:
        print(f"{k:<22}" + ''.join(f"{allS[wk][t][k]:>11.1f}" for wk in FILES for t in ('top1', 'rest')))
