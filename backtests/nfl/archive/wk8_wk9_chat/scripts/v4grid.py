import sys, json, itertools
sys.path.insert(0, '/home/claude/bt/scripts')
import v4
from v4 import *
# generalize gem rule with parameters
def pick_qbs_g(P, cfg):
    w, pen, cap = cfg['w'], cfg['pen'], cfg['cap']
    Q = sorted([q for q in P if q['pos'] == 'QB' and 6800 <= q['salary'] <= cap], key=lambda p: -(p['itt'] + w * p['total'] - pen * max(0, p['salary'] - 7600) / 1000))
    picked, used = [], set()
    for q in Q:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    return picked
v4.pick_qbs = pick_qbs_g
out = {}
for w, pen, cap in itertools.product([0.2, 0.4, 0.6], [0.5, 1.5, 2.5], [8300, 8500, 8700]):
    k = f'w{w}_p{pen}_c{cap}'
    R = evaluate4(k, dict(w=w, pen=pen, cap=cap, wrte_salfloor=4500))
    out[k] = dict(roi=R['roi'], cash=R['cash'], n=R['n'], top5=R['top5'], top1=R['top1'], dead=R['dead'], med=R['med'],
                  per={wk: dict(cash=v['cash'], won=v['won'], fees=v['fees'], med=v['med_pct'], qbs=v['qbs']) for wk, v in R['per'].items()})
    print(f"{k}: ROI {R['roi']:+.0f}% cash {R['cash']}/{R['n']} top5 {R['top5']} top1 {R['top1']} dead {R['dead']} med {R['med']:.0f}", flush=True)
    json.dump(out, open('/home/claude/bt/v4_grid.json', 'w'), indent=1)
print('done')
