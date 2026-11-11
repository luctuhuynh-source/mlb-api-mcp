"""Score every variant, then leave-one-week-out selection."""
import json, csv, re, bisect, sys
from collections import defaultdict
FILES = {'wk1': '/home/claude/bt/133104.csv', 'wk2': '/mnt/user-data/uploads/134251-280648284.csv',
         'wk3': '/mnt/user-data/uploads/134503-280745135.csv', 'wk4': '/mnt/user-data/uploads/134747-280845253.csv',
         'wk5': '/mnt/user-data/uploads/135023-280945043.csv'}
WEEKS = list(FILES)
F = {}
for wk, f in FILES.items():
    fp, pts = {}, []
    with open(f, encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            if len(row) >= 11 and row[6].strip():
                m = re.match(r'(.*) \((\d+)-(\d+)\)', row[6]); fp[m.group(3)] = float(row[9])
            if row[0].strip() and row[3] not in ('', 'null'): pts.append(float(row[3]))
    sp = sorted(pts); n = len(sp)
    F[wk] = dict(fp=fp, sp=sp, cash=sp[int(n * .8)], top1=sp[int(n * .99)])

res = json.load(open('/home/claude/bt/variants_lineups.json'))
score = {}      # (cfg, wk) -> dict
for wk, cfg, Ls in res:
    S = F[wk]; pc, cash, t1, sc = [], 0, 0, []
    for L in Ls:
        if not L: pc.append(0); sc.append(0); continue
        s = sum(S['fp'].get(pid, 0) for pid in L); sc.append(s)
        pc.append(100 * bisect.bisect_left(S['sp'], s) / len(S['sp']))
        cash += s >= S['cash']; t1 += s >= S['top1']
    score[(cfg, wk)] = dict(mean_pct=sum(pc) / 6, cash=cash, top1=t1, best=max(sc), empty=sum(1 for L in Ls if not L))
cfgs = sorted(set(c for c, _ in score))
def agg(cfg, weeks, k): return sum(score[(cfg, w)][k] for w in weeks)

BASE = json.dumps(dict(stack=2, bring=0, alpha=1, qb='itt', dst='oppitt', rbfloor=20000), sort_keys=True)
print('BASELINE (today rules):', [(w, round(score[(BASE, w)]['mean_pct'], 1), score[(BASE, w)]['cash']) for w in WEEKS],
      'total cash', agg(BASE, WEEKS, 'cash'), 'mean pct', round(agg(BASE, WEEKS, 'mean_pct') / 5, 1))

print('\nLEAVE-ONE-WEEK-OUT (pick best avg-percentile config on 4 weeks, score the 5th):')
lo_cash = lo_pct = lo_t1 = 0
for w in WEEKS:
    train = [x for x in WEEKS if x != w]
    best = max(cfgs, key=lambda c: (agg(c, train, 'mean_pct'), agg(c, train, 'cash')))
    s = score[(best, w)]; lo_cash += s['cash']; lo_pct += s['mean_pct']; lo_t1 += s['top1']
    print(f"  hold {w}: chose {best} -> held-out mean pct {s['mean_pct']:.1f}, cash {s['cash']}/6, top1 {s['top1']}  (baseline {score[(BASE, w)]['mean_pct']:.1f}, cash {score[(BASE, w)]['cash']})")
print(f"  LOO total: cash {lo_cash}/30, top1 {lo_t1}, mean pct {lo_pct / 5:.1f}  vs baseline cash {agg(BASE, WEEKS, 'cash')}/30, top1 {agg(BASE, WEEKS, 'top1')}, mean pct {agg(BASE, WEEKS, 'mean_pct') / 5:.1f}")

print('\nONE-FACTOR EFFECTS (avg over all other settings; per-week mean pct, and weeks where it wins):')
GRID = dict(stack=[1, 2], bring=[0, 1], alpha=[0, 1, 2], qb=['itt', 'total'], dst=['oppitt', 'cheap'], rbfloor=[0, 20000])
for k, vals in GRID.items():
    rows = []
    for v in vals:
        cs = [c for c in cfgs if json.loads(c)[k] == v]
        per = [sum(score[(c, w)]['mean_pct'] for c in cs) / len(cs) for w in WEEKS]
        cash = sum(agg(c, WEEKS, 'cash') for c in cs) / len(cs)
        t1 = sum(agg(c, WEEKS, 'top1') for c in cs) / len(cs)
        rows.append((v, per, cash, t1))
    best_by_week = [max(rows, key=lambda r: r[1][i])[0] for i in range(5)]
    for v, per, cash, t1 in rows:
        print(f"  {k}={v!s:<7} pct/wk {[round(x, 1) for x in per]} avg {sum(per) / 5:5.1f} | avg cashes/30 {cash:4.1f} | avg top1 {t1:3.1f} | wins {best_by_week.count(v)}/5 weeks")

top = sorted(cfgs, key=lambda c: -agg(c, WEEKS, 'mean_pct'))[:8]
print('\nTOP 8 IN-SAMPLE (for reference only — not out-of-sample):')
for c in top:
    print(f"  {c}  pct {agg(c, WEEKS, 'mean_pct') / 5:.1f} cash {agg(c, WEEKS, 'cash')} top1 {agg(c, WEEKS, 'top1')} per-week cash {[score[(c, w)]['cash'] for w in WEEKS]}")
json.dump({f'{c}|{w}': v for (c, w), v in score.items()}, open('/home/claude/bt/variant_scores.json', 'w'))
