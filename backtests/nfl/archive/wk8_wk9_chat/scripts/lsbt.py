"""Long-run LineStar backtest engine (2022–2026 main slates).
Pool = LineStar FanDuel salary file per week (salaries, LS projection, actual FD pts, Vegas lines, Sunday Million ownership).
Projection = blend of LineStar proj and the saved salary×ITT formula (props unavailable historically).
Field = ownership-weighted simulated lineups, calibrated against the 2026 weeks with real standings.
Rules = v1.6 (C1–C7) via v3.solve3; arms via cfg (stack_min, pc_rb, qb_cap, blend, per_qb ...)."""
import gzip, json, glob, csv, re, bisect, math, random, statistics as st, sys, datetime as dt, os
sys.path.insert(0, '/home/claude/bt/scripts')
import v3, v2, pulp
from v3 import solve3, norm
from build import MULT
from props import props_table, fd_points, nm
_props = {}
def props_for(key):
    if key not in _props: _props[key] = props_table(key)
    return _props[key]
RAW = '/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nfl/linestar/raw/'
FIX = {'JAC': 'JAX', 'LA': 'LAR', 'WSH': 'WAS'}
TABLE, N5 = v2.TABLE, v2.N5

# ---------------- nflverse, multi-season ----------------
_stats = {}
def stats(season):
    if season not in _stats:
        rows = []
        for r in csv.DictReader(open(f'/home/claude/bt/ls/stats_{season}.csv')):
            if r.get('season_type', 'REG') != 'REG': continue
            r['team'] = FIX.get(r['team'], r['team']); rows.append(r)
        _stats[season] = rows
    return _stats[season]

_role = {}
def role_table(season):
    if season in _role: return _role[season]
    rows = stats(season); team_car = {}
    for r in rows:
        k = (r['team'], int(r['week'])); team_car[k] = team_car.get(k, 0) + float(r['carries'] or 0)
    R = {}
    for r in rows:
        if r['position'] not in ('RB', 'WR', 'TE'): continue
        w = int(r['week'])
        R[(norm(r['player_display_name']), r['team'], w)] = dict(ts=float(r['target_share'] or 0), wopr=float(r['wopr'] or 0),
            car_share=float(r['carries'] or 0) / max(team_car[(r['team'], w)], 1))
    _role[season] = R; return R

def parse_key(wk):  # 's2025w06'
    m = re.match(r's(\d{4})w(\d+)', wk); return int(m.group(1)), int(m.group(2))

def role_prior(name, team, wk):
    season, n = parse_key(wk); R = role_table(season)
    vals = [R.get((norm(name), team, w)) for w in (n - 1, n - 2)]; vals = [v for v in vals if v]
    if not vals: return None
    return dict(ts=max(v['ts'] for v in vals), wopr=max(v['wopr'] for v in vals), car_share=max(v['car_share'] for v in vals))
v3.role_prior = role_prior   # solve3 resolves role_prior from v3's namespace

def rb_window(season, n, w=1.5):
    rows = stats(season); weeks = [x for x in (n - 1, n - 2) if x >= 1]
    TW = {}
    for r in rows:
        k = (r['team'], int(r['week'])); d = TW.setdefault(k, dict(car=0.0, tgt=0.0))
        d['car'] += float(r['carries'] or 0); d['tgt'] += float(r['targets'] or 0)
    out = {}
    for r in rows:
        if r['position'] != 'RB' or int(r['week']) not in weeks: continue
        k = (norm(r['player_display_name']), r['team']); d = out.setdefault(k, dict(car=0, tgt=0))
        d['car'] += float(r['carries'] or 0); d['tgt'] += float(r['targets'] or 0)
    res = {}
    for (name, team), d in out.items():
        tg = [x for x in weeks if (team, x) in TW]
        tcar = sum(TW[(team, x)]['car'] for x in tg); tt = sum(TW[(team, x)]['tgt'] for x in tg); G = max(len(tg), 1)
        res[(name, team)] = dict(C=d['car'] / max(tcar, 1), T=d['tgt'] / max(tt, 1), WTG=(d['car'] + w * d['tgt']) / G, G=G)
    return res

def rb_eligible(p, W, mode):
    if mode == 'nogate': return 'open'
    r = W.get((norm(p['name']), p['team']))
    if r is None: return 'nodata'
    if r['C'] >= 0.35: return 'lead'
    if mode == 'flat': return None
    if r['C'] >= 0.20 and r['T'] >= 0.08 and r['WTG'] >= 10: return 'committee'
    if r['T'] >= 0.12 and r['WTG'] >= 10: return 'receiving'
    return None

# ---------------- LineStar slate loader ----------------
def slate_files():
    out = []
    for f in sorted(glob.glob(RAW + '*.json.gz')):
        out.append(f)
    return out

def load_slate(f):
    d = json.load(gzip.open(f)); j = json.loads(d['SalaryContainerJson'])
    m = re.match(r'Week (\d+), (\d{4})', j['Period']['Name'])
    if not m: return None
    week, season = int(m.group(1)), int(m.group(2)); key = f's{season}w{week:02d}'
    G = {}
    for g in j['Games']:
        t = dt.datetime.fromisoformat(g['DateUtc'][:19])
        if t.weekday() != 6 or not (17 <= t.hour <= 21): continue        # Sunday main slate only
        ou, lh = g.get('VegasOverUnder') or 0, g.get('VegasLineHome')
        if not ou or lh is None: continue
        a, h = FIX.get(g['AwayTeam'], g['AwayTeam']), FIX.get(g['HomeTeam'], g['HomeTeam'])
        G[h] = dict(opp=a, itt=(ou - lh) / 2, total=ou, game=f'{a}@{h}')
        G[a] = dict(opp=h, itt=(ou + lh) / 2, total=ou, game=f'{a}@{h}')
    if len(G) < 16: return None                                           # need ≥8 main games with lines
    own = {}; own_src = 'none'
    mil = [c for c in d['Ownership']['ContestResults'] if 'Sunday Million' in c['Contest']['ContestName']]
    if mil:
        for o in mil[0]['OwnershipData']: own[o['SalaryId']] = o['Owned']
        own_src = 'million'
    else:
        pr = d['Ownership'].get('Projected') or {}
        best = max(pr.values(), key=len) if pr else []
        for o in best: own[o['SalaryId']] = o['Owned']
        own_src = 'projected' if best else 'none'
    mean_itt = st.mean(v['itt'] for v in G.values())
    P = []
    for p in j['Salaries']:
        team = FIX.get(p['PTEAM'], p['PTEAM'])
        if team not in G or p['POS'] == 'K': continue
        pos = 'DST' if p['POS'] == 'D' else p['POS']
        if pos not in ('QB', 'RB', 'WR', 'TE', 'DST'): continue
        g = G[team]
        P.append(dict(pid=str(p['Id']), name=p['Name'], pos=pos, team=team, opp=g['opp'], game=g['game'], salary=int(p['SAL']),
                      ls=float(p['PP'] or 0), floor=float(p['Floor'] or 0), ceil=float(p['Ceil'] or 0), actual=float(p['PS'] or 0),
                      own=float(own.get(p['Id'], 0)), itt=g['itt'], total=g['total'], opp_itt=G[g['opp']]['itt'], mean_itt=mean_itt))
    n_act = sum(1 for p in P if p['actual'] > 0)
    if n_act < 60: return None                                            # actuals not populated
    return dict(key=key, season=season, week=week, P=P, games=G, own_src=own_src, file=os.path.basename(f))

# ---------------- projection + rules ----------------
def project(P, cfg):
    keep = []; b = cfg.get('blend', 0.5)
    for p in P:
        if p['pos'] == 'DST':
            p['p2'] = 7 + 0.6 * (p['mean_itt'] - p['opp_itt']) + 0.5 * (p['salary'] / 1000 - 4); p['props'] = None; p['o'] = {}; keep.append(p); continue
        if p['ls'] <= 0: continue                                         # LineStar zero = out / no projection (≈ unpriced)
        sal = (p['salary'] - 3000) / 1000 * MULT[p['pos']] * (p['itt'] / p['mean_itt'])
        mode = cfg.get('proj', 'ls')
        if mode in ('v16', 'v17', 'props'):
            Tb = props_for(cfg['_wk']); o = Tb.get((nm(p['name']), tuple(p['game'].split('@'))))
            if not o: continue                                        # v1.5a: unpriced excluded
            pr = fd_points(o, p['pos']); p['props'] = pr; p['o'] = o
            p['p2'] = {'v16': 0.5 * sal + 0.5 * pr, 'v17': (sal + pr + p['ls']) / 3, 'props': pr}[mode]
        else:
            p['props'] = p['ls']; p['o'] = {}
            p['p2'] = b * sal + (1 - b) * p['ls']
        if cfg.get('wrte_salfloor') and p['pos'] in ('WR', 'TE') and p['salary'] < cfg['wrte_salfloor']: continue
        keep.append(p)
    return keep

def pick_qbs(P, cfg):
    mode = cfg.get('qb', 'gem'); lo = 6800
    Q = [p for p in P if p['pos'] == 'QB']
    if mode == 'band': Q = sorted([q for q in Q if lo <= q['salary'] <= cfg.get('qb_hi', 7600)], key=lambda p: (-p['itt'], -p['salary']))
    elif mode == 'proj': Q = sorted([q for q in Q if q['salary'] >= lo], key=lambda p: -p['props'])
    else: Q = sorted([q for q in Q if lo <= q['salary'] <= cfg.get('qb_cap', 8300)], key=lambda p: -(p['itt'] + 0.4 * p['total'] - 1.5 * max(0, p['salary'] - 7600) / 1000))
    picked, used = [], set()
    for q in Q:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    return picked

def run_slate(S, cfg):
    import itertools
    cfg = dict(cfg); cfg['_wk'] = S['key']; cfg.setdefault('mode', 'flat'); cfg.setdefault('per_qb', 5)
    P = [dict(p) for p in S['P']]; P = project(P, cfg)
    W = rb_window(S['season'], S['week'])
    for p in P:
        if p['pos'] == 'RB':
            p['elig'] = rb_eligible(p, W, cfg['mode']); r = W.get((norm(p['name']), p['team']))
            p['cshare'] = r['C'] if r else 0; p['T'] = r['T'] if r else 0
            if cfg.get('pc_rb') and not p.get('o'): p['o'] = {'player_receptions': 3.0 if p['T'] >= 0.10 else 0}   # no props: pass-catching = target share ≥10%
    picked = pick_qbs(P, cfg)
    prior, expo, pairs, out = [], {}, {}, []
    for q in picked:
        first = None
        for k in range(cfg['per_qb']):
            args = (None, None, None) if first is None else ([p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')],
                     [p['pid'] for p in (out[-1] or first) if p['pos'] == 'DST'][0], [p['pid'] for p in (out[-1] or first) if p['pos'] == 'RB'])
            L = solve3(P, q, cfg, prior, expo, pairs, *args)
            out.append(L or [])
            if L:
                if first is None: first = L
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
                stack = {p['pid'] for p in L if p['pos'] == 'QB' or (p['team'] == q['team'] and p['pos'] in ('WR', 'TE'))}
                for a, b2 in itertools.combinations(sorted(ids), 2):
                    if not (a in stack and b2 in stack): pairs[(a, b2)] = pairs.get((a, b2), 0) + 1
    return out, picked

# ---------------- simulated field ----------------
def sim_field(P, n=6000, seed=1):
    rnd = random.Random(seed)
    pools = {}
    for pos in ('QB', 'RB', 'WR', 'TE', 'DST'):
        c = [p for p in P if p['pos'] == pos and p['salary'] > 0]
        w = [max(p['own'], 0.15) for p in c]          # unlisted players get a small floor weight
        pools[pos] = (c, w)
    def pick(pos, k, taken):
        c, w = pools[pos]; out = []
        for _ in range(k):
            for _try in range(50):
                p = rnd.choices(c, w)[0]
                if p['pid'] not in taken: taken.add(p['pid']); out.append(p); break
        return out
    scores = []
    for i in range(n):
        for _try in range(30):
            taken = set(); L = pick('QB', 1, taken) + pick('RB', 2, taken) + pick('WR', 3, taken) + pick('TE', 1, taken) + pick('DST', 1, taken)
            r = rnd.random(); L += pick('RB' if r < 0.72 else 'WR' if r < 0.95 else 'TE', 1, taken)
            sal = sum(p['salary'] for p in L)
            if 56500 <= sal <= 60000 and len(L) == 9: break
        scores.append(sum(p['actual'] for p in L))
    return sorted(scores)

# calibration map sim-percentile -> real-percentile is fitted in calibrate(); default identity
SCALE = 1.0663   # real field quantiles ≈ SCALE × simulated (fit on 2026 wk2–7, 24 quantile points)
def field_pct(sp, s):
    return 100 * bisect.bisect_left(sp, s / SCALE) / len(sp)

def prize_from_pct(pct):
    rank = max(1, int(round((100 - pct) / 100 * N5)))
    for a, b, pz in TABLE:
        if a <= rank <= b: return pz
    return 0

def score_slate(S, Ls, sp):
    rows = []
    for L in Ls:
        if not L: rows.append(dict(score=0, pct=0, prize=0, top5=False, top1=False, dead=0)); continue
        s = sum(p['actual'] for p in L); pct = field_pct(sp, s)
        rows.append(dict(score=s, pct=pct, prize=prize_from_pct(pct), top5=pct >= 95, top1=pct >= 99,
                         dead=sum(1 for p in L if p['pos'] != 'DST' and p['actual'] <= 1.0)))
    return rows

_fields = {}
def field_for(S):
    if S['key'] not in _fields:
        cache = f"/home/claude/bt/ls/field_{S['key']}.json"
        if os.path.exists(cache): _fields[S['key']] = json.load(open(cache))
        else:
            sp = sim_field(S['P']); json.dump(sp, open(cache, 'w')); _fields[S['key']] = sp
    return _fields[S['key']]

def evaluate(name, cfg, slates, fee=15):
    per = {}
    for S in slates:
        Ls, picked = run_slate(S, cfg); sp = field_for(S); rows = score_slate(S, Ls, sp)
        per[S['key']] = dict(qbs=[f"{q['name']} ${q['salary']}" for q in picked], n=len([L for L in Ls if L]),
                             cash=sum(1 for r in rows if r['prize'] > 0), won=sum(r['prize'] for r in rows), fees=fee * len(Ls),
                             best_pct=max(r['pct'] for r in rows), med_pct=st.median(r['pct'] for r in rows),
                             med_score=st.median(r['score'] for r in rows),
                             top5=sum(1 for r in rows if r['top5']), top1=sum(1 for r in rows if r['top1']), dead=sum(r['dead'] for r in rows),
                             lineups=[[dict(pos=p['pos'], name=p['name'], team=p['team'], salary=p['salary'], pts=p['actual']) for p in L] for L in Ls])
        print(f"  {name} {S['key']}: cash {per[S['key']]['cash']}/{per[S['key']]['n']} ${per[S['key']]['won']} med {per[S['key']]['med_pct']:.0f}% | {', '.join(per[S['key']]['qbs'])}", flush=True)
    fees = sum(v['fees'] for v in per.values()); won = sum(v['won'] for v in per.values())
    return dict(name=name, cfg=cfg, per=per, fees=fees, won=won, roi=100 * (won - fees) / max(fees, 1), cash=sum(v['cash'] for v in per.values()),
                n=sum(v['n'] for v in per.values()), top5=sum(v['top5'] for v in per.values()), top1=sum(v['top1'] for v in per.values()),
                dead=sum(v['dead'] for v in per.values()), med=st.median(v['med_pct'] for v in per.values()),
                weeks_pos=sum(1 for v in per.values() if v['won'] > v['fees']))

def show(R):
    print(f"\n== {R['name']}: ROI {R['roi']:+.0f}% (${R['won']}/${R['fees']}) | cash {R['cash']}/{R['n']} ({100*R['cash']/max(R['n'],1):.0f}%) | top5 {R['top5']} top1 {R['top1']} | dead {R['dead']} | median-lineup pct {R['med']:.0f} | profitable weeks {R['weeks_pos']}/{len(R['per'])}", flush=True)
