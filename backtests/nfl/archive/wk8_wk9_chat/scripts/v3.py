"""v1.4b test: three-path RB eligibility + opportunity-value tie-break, vs v1.4 (variant A). Pooled last-2-team-games window, prior weeks only."""
import csv, json, sys, bisect, re, itertools
import numpy as np
sys.path.insert(0, '/home/claude/bt/scripts')
import v2
from v2 import *
import pulp

SUFFIX = re.compile(r'\s+(Jr\.|Sr\.|II|III|IV)$')
def norm(n): return SUFFIX.sub('', n).strip()

# ---------- nflverse pooled role window ----------
_rows = None
def rows():
    global _rows
    if _rows is None:
        _rows = list(csv.DictReader(open('/home/claude/bt/ext/stats_player_week_2026.csv')))
        for r in _rows: r['team'] = FIX.get(r['team'], r['team']); r['opponent_team'] = FIX.get(r['opponent_team'], r['opponent_team'])
    return _rows

def team_week_totals():
    T = {}
    for r in rows():
        k = (r['team'], int(r['week'])); d = T.setdefault(k, dict(car=0.0, tgt=0.0, att=0.0))
        d['car'] += float(r['carries'] or 0); d['tgt'] += float(r['targets'] or 0); d['att'] += float(r['attempts'] or 0)
    return T

def rb_window(wk, w=1.5):
    """pooled over the team's last two completed games before wk -> {(norm name, team): dict(C, T, WTG, G)}"""
    n = int(wk[2:]); TW = team_week_totals(); out = {}
    weeks = [x for x in (n - 1, n - 2) if x >= 1]
    for r in rows():
        if r['position'] != 'RB' or int(r['week']) not in weeks: continue
        k = (norm(r['player_display_name']), r['team']); d = out.setdefault(k, dict(car=0, tgt=0, tcar=0, tt=0, G=set()))
        d['car'] += float(r['carries'] or 0); d['tgt'] += float(r['targets'] or 0); d['G'].add(int(r['week']))
    # team denominators: all games the TEAM played in the window (even if the player missed one)
    res = {}
    for (name, team), d in out.items():
        tg = [x for x in weeks if (team, x) in TW]
        tcar = sum(TW[(team, x)]['car'] for x in tg); tt = sum(TW[(team, x)]['tgt'] for x in tg); G = max(len(tg), 1)
        res[(name, team)] = dict(C=d['car'] / max(tcar, 1), T=d['tgt'] / max(tt, 1), WTG=(d['car'] + w * d['tgt']) / G, G=G)
    return res

def defense_prior(wk):
    """per defense: FPA to RBs per game and rush YPC allowed, prior weeks only"""
    n = int(wk[2:]); D = {}
    for r in rows():
        if int(r['week']) >= n: continue
        d = D.setdefault(r['opponent_team'], dict(fp=0.0, g=set(), ry=0.0, car=0.0))
        if r['position'] == 'RB': d['fp'] += float(r['fantasy_points'] or 0) - 0.5 * float(r['receptions'] or 0)  # nflverse fantasy_points is standard; FD half-PPR ≈ +0.5/rec
        d['ry'] += float(r['rushing_yards'] or 0); d['car'] += float(r['carries'] or 0); d['g'].add(int(r['week']))
    return {t: dict(fpa=d['fp'] / max(len(d['g']), 1), ypc=d['ry'] / max(d['car'], 1)) for t, d in D.items()}

# ---------- eligibility ----------
def rb_eligible(p, W, mode, floor=True, ts_committee=0.08):
    if mode == 'nogate': return 'open'
    r = W.get((norm(p['name']), p['team']))
    if r is None: return 'nodata'
    if r['C'] >= 0.35: return 'lead'
    if mode == 'flat': return None
    if r['C'] >= 0.20 and r['T'] >= ts_committee and (not floor or r['WTG'] >= 10): return 'committee'
    if r['T'] >= 0.12 and (not floor or r['WTG'] >= 10): return 'receiving'
    return None

def solve3(P, qb, cfg, prior, expo, pairs, must_share=None, avoid_dst=None, avoid_rbset=None, min_proj=None, force=None):
    m = pulp.LpProblem('lu', pulp.LpMaximize)
    x = {p['pid']: pulp.LpVariable('x' + p['pid'], cat='Binary') for p in P}
    by = lambda f: [p for p in P if f(p)]
    if min_proj is None: m += pulp.lpSum(p['p2'] * x[p['pid']] for p in P)
    else:
        m += pulp.lpSum(p.get('V', 0) * x[p['pid']] for p in P) + 1e-4 * pulp.lpSum(p['p2'] * x[p['pid']] for p in P)
        m += pulp.lpSum(p['p2'] * x[p['pid']] for p in P) >= min_proj
    m += x[qb['pid']] == 1
    for pos, k in (('QB', 1), ('RB', 3), ('WR', 3), ('TE', 1), ('DST', 1)):
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, pos=pos: p['pos'] == pos)) == k
    sal = pulp.lpSum(p['salary'] * x[p['pid']] for p in P); m += sal <= 60000; m += sal >= 59500
    m += pulp.lpSum(p['salary'] * x[p['pid']] for p in by(lambda p: p['pos'] == 'RB')) >= 20000
    catchers = by(lambda p: p['team'] == qb['team'] and p['pos'] in ('WR', 'TE'))
    m += pulp.lpSum(x[p['pid']] for p in catchers) >= cfg.get('stack_min', 2); m += pulp.lpSum(x[p['pid']] for p in catchers) <= 3
    for p in by(lambda p: p['pos'] == 'RB' and p['team'] == qb['team']):
        pc = cfg.get('pc_rb') and ((p.get('o') or {}).get('player_receptions', 0) >= cfg['pc_rb'] or p.get('T', 0) >= 0.12)
        if not pc: m += x[p['pid']] == 0
    for g in set(p['game'] for p in P):
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p, g=g: p['pos'] == 'RB' and p['game'] == g)) <= 1
    for d in by(lambda p: p['pos'] == 'DST'):
        for p in by(lambda p, d=d: p['team'] == d['opp'] and p['pos'] in ('QB', 'WR', 'TE')): m += x[d['pid']] + x[p['pid']] <= 1
    for p in by(lambda p: p['pos'] in ('RB', 'WR', 'TE') and p['salary'] <= 4500 and p['game'] != qb['game']): m += x[p['pid']] == 0
    # WR/TE role gate (v1.4) on stack + bring-back
    for p in by(lambda p: cfg['mode'] != 'nogate' and p['pos'] in ('WR', 'TE') and p['team'] in (qb['team'], qb['opp'])):
        rp = role_prior(p['name'], p['team'], cfg['_wk'])
        if rp is not None and rp['wopr'] < 0.30 and rp['ts'] < 0.18: m += x[p['pid']] == 0
    # RB eligibility
    for p in by(lambda p: p['pos'] == 'RB'):
        if p['elig'] is None: m += x[p['pid']] == 0
    if cfg.get('lead_only_rb12'):   # committee/receiving backs allowed in at most one of the three RB slots (the FLEX)
        m += pulp.lpSum(x[p['pid']] for p in by(lambda p: p['pos'] == 'RB' and p['elig'] in ('committee', 'receiving'))) <= 1
    N = 3 * cfg.get('per_qb', 2)
    for pid, c in expo.items():
        if c >= N // 2 and pid in x and pid != qb['pid']: m += x[pid] == 0
    for L in prior: m += pulp.lpSum(x[pid] for pid in L if pid in x) <= 5
    for (a, b), c in pairs.items():
        if c >= int(0.4 * N) and a in x and b in x: m += x[a] + x[b] <= 1
    if must_share: m += pulp.lpSum(x[pid] for pid in must_share) >= 1
    if force:
        for pid in force: m += x[pid] == 1
    if avoid_dst: m += x[avoid_dst] == 0
    if avoid_rbset: m += pulp.lpSum(x[pid] for pid in avoid_rbset) <= 2
    m.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=60))
    if pulp.LpStatus[m.status] != 'Optimal': return None
    return [p for p in P if x[p['pid']].value() > 0.5]

def run3(wk, cfg):
    cfg = dict(cfg); cfg['_wk'] = wk
    P, games, mean_itt = load(wk); project(P, wk, dict(cfg, proj='salary'))
    W = rb_window(wk, cfg.get('w', 1.5))
    for p in P:
        if p['pos'] == 'RB':
            p['elig'] = rb_eligible(p, W, cfg['mode'], cfg.get('floor', True), cfg.get('ts_committee', 0.08))
            r = W.get((norm(p['name']), p['team'])); p['V'] = (r['WTG'] / (p['salary'] / 1000)) if r else 0.0
    qbs = sorted([p for p in P if p['pos'] == 'QB' and 6800 <= p['salary'] <= 7600], key=lambda p: (-p['itt'], -p['salary']))
    picked, used = [], set()
    for q in qbs:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    prior, expo, pairs, out = [], {}, {}, []
    per_qb = cfg.get('per_qb', 2)
    for q in picked:
        first = None
        for k in range(per_qb):
            args = (None, None, None) if first is None else ([p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')],
                     [p['pid'] for p in first if p['pos'] == 'DST'][0], [p['pid'] for p in first if p['pos'] == 'RB'])
            L = solve3(P, q, cfg, prior, expo, pairs, *args)
            if L and cfg.get('tiebreak'):
                pmax = sum(p['p2'] for p in L)
                L2 = solve3(P, q, cfg, prior, expo, pairs, *args, min_proj=0.98 * pmax)
                if L2: L = L2
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

def evaluate3(name, cfg):
    per = {}
    for wk in WEEKS:
        Ls, picked = run3(wk, cfg); rows_ = score(wk, Ls); fp, own, sp = results(wk)
        per[wk] = dict(qbs=[q['name'] for q in picked], n=len([L for L in Ls if L]),
                       cash=sum(1 for r in rows_ if r['prize'] > 0), won=sum(r['prize'] for r in rows_), fees=15 * len(Ls),
                       best_pct=max(r['pct'] for r in rows_), avg_pct=sum(r['pct'] for r in rows_) / len(rows_),
                       top5=sum(1 for r in rows_ if r['top5']), top1=sum(1 for L in Ls if L and sum(p['actual'] for p in L) >= sp[int(len(sp) * .99)]),
                       zeros_all=sum(1 for L in Ls for p in L if p['pos'] != 'DST' and p['actual'] == 0),
                       zeros_rb=sum(1 for L in Ls for p in L if p['pos'] == 'RB' and p['actual'] == 0),
                       rb_pts=sum(p['actual'] for L in Ls for p in L if p['pos'] == 'RB'), wr_pts=sum(p['actual'] for L in Ls for p in L if p['pos'] == 'WR'),
                       rb_sal=sum(p['salary'] for L in Ls for p in L if p['pos'] == 'RB'),
                       lineups=[[dict(pos=p['pos'], name=p['name'], team=p['team'], salary=p['salary'], pts=p['actual'], elig=p.get('elig')) for p in L] for L in Ls])
    fees = sum(v['fees'] for v in per.values()); won = sum(v['won'] for v in per.values())
    return dict(name=name, cfg={k: v for k, v in cfg.items() if k != '_wk'}, per=per, fees=fees, won=won, roi=100 * (won - fees) / fees,
                cash=sum(v['cash'] for v in per.values()), top5=sum(v['top5'] for v in per.values()), top1=sum(v['top1'] for v in per.values()),
                zeros_all=sum(v['zeros_all'] for v in per.values()), zeros_rb=sum(v['zeros_rb'] for v in per.values()),
                rb_pts=sum(v['rb_pts'] for v in per.values()), wr_pts=sum(v['wr_pts'] for v in per.values()), rb_sal=sum(v['rb_sal'] for v in per.values()))

def changed(R, A):
    n = 0; wks = set()
    for wk in WEEKS:
        for L1, L2 in zip(R['per'][wk]['lineups'], A['per'][wk]['lineups']):
            if {p['name'] for p in L1} != {p['name'] for p in L2}: n += 1; wks.add(wk)
    return n, len(wks)

def show3(R, A=None):
    print(f"\n== {R['name']}: ROI {R['roi']:+.0f}% (won ${R['won']}/${R['fees']}) | cash {R['cash']}/{sum(v['n'] for v in R['per'].values())} | top5 {R['top5']} top1 {R['top1']} | zeros all {R['zeros_all']} rb {R['zeros_rb']} | RB pts {R['rb_pts']:.0f} WR pts {R['wr_pts']:.0f} | RB pts/$1k {1000 * R['rb_pts'] / R['rb_sal']:.2f}")
    for wk, v in R['per'].items():
        print(f"   {wk}: cash {v['cash']}/6 ${v['won']} best {v['best_pct']:.0f}% avg {v['avg_pct']:.0f}% zeros {v['zeros_all']}")
    if A:
        wins = sum(1 for wk in WEEKS if R['per'][wk]['best_pct'] > A['per'][wk]['best_pct'])
        ch, wks = changed(R, A)
        crit = [wins >= 3, R['roi'] - A['roi'] >= 10, R['zeros_all'] <= 7, R['top5'] >= A['top5'] and R['top1'] >= A['top1'],
                ch >= 6 and wks >= 3, R['rb_pts'] + R['wr_pts'] >= A['rb_pts'] + A['wr_pts']]
        print(f"   vs A: best-of-6 {wins}/4 | ROI {R['roi'] - A['roi']:+.0f} | zeros≤7 {R['zeros_all'] <= 7} | top5/1 no drop {crit[3]} | changed {ch}/24 over {wks} wks | RB+WR pts {R['rb_pts'] + R['wr_pts'] - A['rb_pts'] - A['wr_pts']:+.0f} | PASS {sum(crit)}/6")

if __name__ == '__main__':
    A = evaluate3('A: v1.4 flat 35% gate', dict(mode='flat')); show3(A)
    B = evaluate3('B: three-path eligibility', dict(mode='three')); show3(B, A)
    C = evaluate3('C: three-path + V tie-break (w=1.5)', dict(mode='three', tiebreak=True, w=1.5)); show3(C, A)
    print('   C vs B ROI:', f"{C['roi'] - B['roi']:+.0f}")
    S = {}
    S['w2'] = evaluate3('sweep: w=2.0', dict(mode='three', tiebreak=True, w=2.0)); show3(S['w2'], A)
    S['lead12'] = evaluate3('sweep: committee FLEX-only', dict(mode='three', tiebreak=True, w=1.5, lead_only_rb12=True)); show3(S['lead12'], A)
    S['nofloor'] = evaluate3('sweep: no WTG floor', dict(mode='three', tiebreak=True, w=1.5, floor=False)); show3(S['nofloor'], A)
    S['ts10'] = evaluate3('sweep: committee TS>=10% (Gemini)', dict(mode='three', tiebreak=True, w=1.5, ts_committee=0.10)); show3(S['ts10'], A)
    # eligibility pool sizes
    for wk in WEEKS:
        P, _, _ = load(wk); W = rb_window(wk)
        rbs = [p for p in P if p['pos'] == 'RB']
        cnt = {}
        for p in rbs: e = rb_eligible(p, W, 'three'); cnt[e] = cnt.get(e, 0) + 1
        flat = sum(1 for p in rbs if rb_eligible(p, W, 'flat') in ('lead', 'nodata'))
        print(f"   {wk} RB pool {len(rbs)}: flat-eligible {flat} | three-path {cnt}")
    # defense correlation test (Gemini disagreement 3): prior opp FPA-to-RB and YPC allowed vs realized RB points, pooled over weeks 3-5 (>=2 prior games)
    xs_f, xs_y, ys = [], [], []
    for wk in ['wk3', 'wk4', 'wk5']:
        P, _, _ = load(wk); D = defense_prior(wk); W = rb_window(wk)
        for p in P:
            if p['pos'] != 'RB' or p['opp'] not in D: continue
            r = W.get((norm(p['name']), p['team']))
            if not r or r['C'] < 0.20: continue      # starters/committee only, so game script noise from backups doesn't dominate
            xs_f.append(D[p['opp']]['fpa']); xs_y.append(D[p['opp']]['ypc']); ys.append(p['actual'])
    print(f"\nDEFENSE TEST (n={len(ys)} RB-games with >=20% carry share, weeks 3-5): corr(prior FPA-to-RB, actual) = {np.corrcoef(xs_f, ys)[0, 1]:.3f} | corr(prior YPC allowed, actual) = {np.corrcoef(xs_y, ys)[0, 1]:.3f}  (Gemini's bar: r >= 0.20)")
    json.dump(dict(A=A, B=B, C=C, **S), open('/home/claude/bt/v3_results.json', 'w'), indent=1)
