"""Props-based projection: pre-lock player props (16:40Z Sunday) -> FanDuel expected points; run as a backtest arm vs v1.4."""
import csv, glob, json, sys, math, re, statistics as st
sys.path.insert(0, '/home/claude/bt/scripts')
import v3
from v3 import *
from build import AB

SUF = re.compile(r"\s+(Jr\.?|Sr\.?|II|III|IV)$")
def nm(s): return SUF.sub('', s.replace('.', '').replace("'", '')).strip().lower()

def implied(price):
    price = float(price); return 100 / (price + 100) if price > 0 else -price / (-price + 100)

def props_table(wk):
    """{(norm name, team): dict(pass_yds, pass_tds, rush_yds, rec_yds, rec, td_prob)} using main lines (over price nearest -110), median across books."""
    per = {}
    for f in glob.glob(f'/home/claude/bt/props/{wk}/*.csv'):
        rows = list(csv.DictReader(open(f)))
        if not rows: continue
        away, home = AB[rows[0]['away']], AB[rows[0]['home']]
        byk = {}
        for r in rows: byk.setdefault((r['player'], r['market'], r['book']), []).append(r)
        for (player, market, book), rs in byk.items():
            key = (nm(player), (away, home))
            d = per.setdefault(key, {})
            if market == 'player_anytime_td':
                yes = [r for r in rs if r['side'] == 'Yes']
                if yes: d.setdefault('td', []).append(implied(yes[0]['price']))
            else:
                overs = [r for r in rs if r['side'] == 'Over' and r['point']]
                if not overs: continue
                main = min(overs, key=lambda r: abs(float(r['price']) + 110))   # main line = over price nearest -110
                d.setdefault(market, []).append(float(main['point']))
    out = {}
    for key, d in per.items():
        o = {k: st.median(v) for k, v in d.items()}
        out[key] = o
    return out

def fd_points(o, pos):
    pts = 0.0
    pts += 0.04 * o.get('player_pass_yds', 0) + 4 * o.get('player_pass_tds', 0)
    pts += 0.1 * o.get('player_rush_yds', 0) + 0.1 * o.get('player_reception_yds', 0) + 0.5 * o.get('player_receptions', 0)
    if 'td' in o:
        p = min(o['td'] * 0.92, 0.95)                  # ~8% single-sided overround haircut
        pts += 6 * (-math.log(1 - p))                  # Poisson: E[TD] from P(>=1)
    if pos == 'QB': pts -= 0.6                         # avg interception drag (no INT market pulled)
    return pts

def project_props(P, wk, blend=0.0):
    T = props_table(wk); hit = 0
    # salary fallback scaled to props level
    for p in P:
        if p['pos'] == 'DST': p['p2'] = 7 + 0.6 * (p['mean_itt'] - p['opp_itt']) + 0.5 * (p['salary'] / 1000 - 4); continue
        g = tuple(p['game'].split('@')); o = T.get((nm(p['name']), g))
        sal = (p['salary'] - 3000) / 1000 * MULT[p['pos']] * (p['itt'] / p['mean_itt'])
        if o:
            hit += 1; pr = fd_points(o, p['pos']); p['p2'] = pr * (1 - blend) + sal * blend; p['props'] = pr
        else:
            p['p2'] = sal * 0.6; p['props'] = None          # unpriced = no market interest; discount hard
    return hit, len([p for p in P if p['pos'] != 'DST'])

# monkeypatch v3's project() so run3 uses props when cfg['proj']=='props'
_orig = v3.project
def project_patched(P, wk, cfg):
    if cfg.get('use_props'): project_props(P, wk, cfg.get('blend', 0.0))
    else: _orig(P, wk, cfg)
v3.project = project_patched

if __name__ == '__main__':
    import numpy as np
    print('COVERAGE and ACCURACY (props vs salary formula, all pool skill players):')
    for wk in WEEKS:
        P, _, _ = load(wk); hit, n = project_props(P, wk)
        pr = [(p['props'], p['actual']) for p in P if p.get('props') is not None]
        _orig(P, wk, dict(BASE, proj='salary'))
        sa = [(p['p2'] * 1.4, p['actual']) for p in P if p.get('props') is not None]      # k≈1.4 calibration from earlier pinball test
        mae = lambda z: np.mean([abs(a - b) for a, b in z]); corr = lambda z: np.corrcoef([a for a, _ in z], [b for _, b in z])[0, 1]
        sal_top = sorted(P, key=lambda p: -p['salary'])[:60]
        print(f"  {wk}: priced {hit}/{n} skill players | top-60 by salary priced {sum(1 for p in sal_top if p.get('props') is not None)}/60 | MAE props {mae(pr):.2f} vs salary {mae(sa):.2f} | corr props {corr(pr):.3f} vs salary {corr(sa):.3f}")
    A = json.load(open('/home/claude/bt/v3_results.json'))['A']
    print(f"\n== A (v1.4 flat gate, salary proj) from v3: ROI {A['roi']:+.0f}% cash {A['cash']}/24 top5 {A['top5']} zeros {A['zeros_all']}")
    R1 = evaluate3('props projection + v1.4 gate', dict(mode='flat', use_props=True)); show3(R1, A)
    R2 = evaluate3('props projection, NO role gate', dict(mode='nogate', use_props=True)); show3(R2, A)
    R3 = evaluate3('props 50/50 blend w/ salary + gate', dict(mode='flat', use_props=True, blend=0.5)); show3(R3, A)
    json.dump(dict(props_gate=R1, props_nogate=R2, props_blend=R3), open('/home/claude/bt/props_results.json', 'w'), indent=1)
