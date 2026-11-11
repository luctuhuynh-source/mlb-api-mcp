"""v4: Weeks 2–5 + 7 (Week 6 pending its standings CSV). 3 QBs x 5, $15 Million. Arms from the 10/26 debate.
Baseline = v1.5a: 50/50 props blend, role gate, unpriced EXCLUDED, QB band 6.8–7.6k ranked by ITT."""
import sys, json, itertools, math, statistics as st
sys.path.insert(0, '/home/claude/bt/scripts')
import v2, v3, props
from v3 import *
from props import props_table, fd_points, nm
U = '/root/.claude/uploads/3eb2421d-9eec-59a8-8c78-d010d6054058/'
v2.POOLS['wk7'] = '/home/claude/bt/wk7/pool.csv'; v2.FILES['wk7'] = '/home/claude/bt/wk7/standings/million.csv'
WEEKS = ['wk2', 'wk3', 'wk4', 'wk5', 'wk7']; v2.WEEKS = WEEKS; v3.WEEKS = WEEKS
_T = {}
def T(wk):
    if wk not in _T: _T[wk] = props_table(wk)
    return _T[wk]

def project4(P, wk, cfg):
    """blend projection + per-player props fields; drop unpriced skill players (v1.5a)."""
    Tb = T(wk); keep = []
    for p in P:
        if p['pos'] == 'DST':
            p['p2'] = 7 + 0.6 * (p['mean_itt'] - p['opp_itt']) + 0.5 * (p['salary'] / 1000 - 4); p['props'] = None; keep.append(p); continue
        o = Tb.get((nm(p['name']), tuple(p['game'].split('@'))))
        sal = (p['salary'] - 3000) / 1000 * MULT[p['pos']] * (p['itt'] / p['mean_itt'])
        if not o: continue                                   # v1.5a: unpriced excluded
        p['o'] = o; p['props'] = fd_points(o, p['pos']); b = cfg.get('blend', 0.5)
        p['p2'] = b * sal + (1 - b) * p['props']
        # WR/TE floor arm
        if cfg.get('wrte_salfloor') and p['pos'] in ('WR', 'TE') and p['salary'] < cfg['wrte_salfloor']: continue
        if cfg.get('wrte_floor') and p['pos'] in ('WR', 'TE'):
            if 'player_reception_yds' not in o or 'player_receptions' not in o or p['props'] < cfg['wrte_floor']: continue
        keep.append(p)
    return keep

def pick_qbs(P, cfg):
    mode = cfg.get('qb', 'band'); lo, hi = 6800, cfg.get('qb_hi', 7600)
    Q = [p for p in P if p['pos'] == 'QB']
    if mode == 'band': Q = sorted([q for q in Q if lo <= q['salary'] <= hi], key=lambda p: (-p['itt'], -p['salary']))
    elif mode == 'proj': Q = sorted([q for q in Q if q['salary'] >= lo], key=lambda p: -p['props'])
    elif mode == 'gem2':  # Gemini R2: props proj - 1.5*max(0, sal-7600)/1000, no cap
        Q = sorted([q for q in Q if q['salary'] >= lo], key=lambda p: -(p['props'] - 1.5 * max(0, p['salary'] - 7600) / 1000))
    elif mode == 'gem':  # Gemini: ITT + 0.4*total - 1.5*max(0, sal-7600)/1000, cap 8500
        Q = sorted([q for q in Q if lo <= q['salary'] <= cfg.get('qb_cap', 8500)], key=lambda p: -(p['itt'] + 0.4 * p['total'] - 1.5 * max(0, p['salary'] - 7600) / 1000))
    picked, used = [], set()
    for q in Q:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    return picked

_orig_solve = pulp.LpProblem.solve
def solve3c(P, q, cfg, prior, expo, pairs, *args, **kw):
    if not cfg.get('chalk_cap'): return solve3(P, q, cfg, prior, expo, pairs, *args, **kw)
    cap = cfg['chalk_cap']
    def patched(self, *a, **k):
        x = {v.name[1:]: v for v in self.variables()}
        self += pulp.lpSum(p['pct'] * x[p['pid']] for p in P if p['pid'] in x) <= cap
        return _orig_solve(self, *a, **k)
    pulp.LpProblem.solve = patched
    try: return solve3(P, q, cfg, prior, expo, pairs, *args, **kw)
    finally: pulp.LpProblem.solve = _orig_solve

def run4(wk, cfg):
    cfg = dict(cfg); cfg['_wk'] = wk; cfg.setdefault('mode', 'flat'); cfg.setdefault('per_qb', 5)
    P, games, mean_itt = load(wk); P = project4(P, wk, cfg)
    W = rb_window(wk)
    for p in P:
        if p['pos'] == 'RB':
            p['elig'] = rb_eligible(p, W, cfg['mode'])
            r = W.get((norm(p['name']), p['team'])); p['cshare'] = r['C'] if r else 0; p['T'] = r['T'] if r else 0
    picked = pick_qbs(P, cfg)
    if cfg.get('chalk_cap'):
        sk = sorted([p for p in P if p['pos'] != 'DST'], key=lambda p: p['p2'])
        for i, p in enumerate(sk): p['pct'] = (i + 1) / len(sk)
        for p in P:
            if p['pos'] == 'DST': p['pct'] = 0.5
    prior, expo, pairs, out = [], {}, {}, []
    N = 3 * cfg['per_qb']
    for q in picked:
        first = None
        for k in range(cfg['per_qb']):
            args = (None, None, None) if first is None else ([p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')],
                     [p['pid'] for p in (out[-1] or first) if p['pos'] == 'DST'][0], [p['pid'] for p in (out[-1] or first) if p['pos'] == 'RB'])
            # committee-RB cap arm (ChatGPT #4): carry share <55% and receptions line <3 -> max 3 of 15 unless carries+rec high
            exp2 = dict(expo)
            if cfg.get('rb_cap'):
                for p in P:
                    if p['pos'] == 'RB' and p['cshare'] < 0.55 and p['o'].get('player_receptions', 0) < 3 and expo.get(p['pid'], 0) >= 3: exp2[p['pid']] = 99
            if cfg.get('ds') and k < cfg['ds']:
                cat = [p for p in P if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')]
                ok = []
                for p in cat:
                    rp = role_prior(p['name'], p['team'], wk)
                    if rp is not None and rp['wopr'] < 0.30 and rp['ts'] < 0.18: continue
                    ok.append(p)
                key = (lambda p: -p['props']) if cfg.get('ds_by') == 'props' else (lambda p: -p['p2'])
                top2 = [p['pid'] for p in sorted(ok, key=key)[:2]]
                args = (None, None, None) if first is None else args
                L = solve3c(P, q, cfg, prior, exp2, pairs, *args, force=top2)
            else:
                L = solve3c(P, q, cfg, prior, exp2, pairs, *args)
            out.append(L or [])
            if L:
                if first is None: first = L
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
                stack = {p['pid'] for p in L if p['pos'] == 'QB' or (p['team'] == q['team'] and p['pos'] in ('WR', 'TE'))}
                for a, b in itertools.combinations(sorted(ids), 2):
                    if not (a in stack and b in stack): pairs[(a, b)] = pairs.get((a, b), 0) + 1
    return out, picked

def evaluate4(name, cfg, weeks=WEEKS):
    per = {}
    for wk in weeks:
        Ls, picked = run4(wk, cfg); rows_ = score(wk, Ls); fp, own, sp = results(wk)
        per[wk] = dict(qbs=[f"{q['name']} ${q['salary']}" for q in picked], n=len([L for L in Ls if L]),
                       cash=sum(1 for r in rows_ if r['prize'] > 0), won=sum(r['prize'] for r in rows_), fees=15 * len(Ls),
                       best_pct=max(r['pct'] for r in rows_), med_pct=st.median(r['pct'] for r in rows_),
                       top5=sum(1 for r in rows_ if r['top5']), top1=sum(1 for L in Ls if L and sum(p['actual'] for p in L) >= sp[int(len(sp) * .99)]),
                       dead=sum(1 for L in Ls for p in L if p['pos'] != 'DST' and p['actual'] <= 1.0),
                       lineups=[[dict(pos=p['pos'], name=p['name'], team=p['team'], salary=p['salary'], pts=p['actual']) for p in L] for L in Ls])
    fees = sum(v['fees'] for v in per.values()); won = sum(v['won'] for v in per.values())
    return dict(name=name, cfg=cfg, per=per, fees=fees, won=won, roi=100 * (won - fees) / fees, cash=sum(v['cash'] for v in per.values()),
                n=sum(v['n'] for v in per.values()), top5=sum(v['top5'] for v in per.values()), top1=sum(v['top1'] for v in per.values()),
                dead=sum(v['dead'] for v in per.values()), med=st.median(v['med_pct'] for v in per.values()))

def show4(R):
    print(f"\n== {R['name']}: ROI {R['roi']:+.0f}% (${R['won']}/${R['fees']}) | cash {R['cash']}/{R['n']} ({100*R['cash']/max(R['n'],1):.0f}%) | top5 {R['top5']} top1 {R['top1']} | dead {R['dead']} | median-lineup pct {R['med']:.0f}")
    for wk, v in R['per'].items():
        print(f"   {wk}: cash {v['cash']}/{v['n']} ${v['won']} best {v['best_pct']:.0f}% med {v['med_pct']:.0f}% dead {v['dead']} | {', '.join(v['qbs'])}")

if __name__ == '__main__':
    ARMS = {
      'A_v15a_base': dict(),
      'B_band_8300': dict(qb_hi=8300),
      'C_qb_noband_proj': dict(qb='proj'),
      'D_qb_gemini': dict(qb='gem'),
      'E_blend70': dict(blend=0.3),
      'F_props_only': dict(blend=0.0),
      'G_wrte_floor5': dict(wrte_floor=5),
      'G4_wrte_floor4': dict(wrte_floor=4),
      'G6_wrte_floor6': dict(wrte_floor=6),
      'H_rb_cap': dict(rb_cap=True),
      'CG_noband_floor5': dict(qb='proj', wrte_floor=5),
      'CEG_noband_b70_floor5': dict(qb='proj', blend=0.3, wrte_floor=5),
      'D2_qb_gem2': dict(qb='gem2'),
      'S_wrte_sal4500': dict(wrte_salfloor=4500),
      'K_chalk_cap75': dict(chalk_cap=7.5),
      'K8_chalk_cap8': dict(chalk_cap=8.0),
      'DB_gem_b70': dict(qb='gem', blend=0.3),
      'DS_gem_sal4500': dict(qb='gem', wrte_salfloor=4500),
      'BS_band8300_sal4500': dict(qb_hi=8300, wrte_salfloor=4500),
    }
    only = sys.argv[1:] or list(ARMS)
    R = {}
    for k in only:
        R[k] = evaluate4(k, ARMS[k]); show4(R[k])
        json.dump(R, open('/home/claude/bt/v4_results_%s.json' % only[0], 'w'), indent=1)
