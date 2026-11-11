"""Unseal: score frozen lineups and our real entries against each week's full Sunday Million field."""
import csv, json, re, bisect
FILES = {'wk1': '/home/claude/bt/133104.csv', 'wk2': '/mnt/user-data/uploads/134251-280648284.csv',
         'wk3': '/mnt/user-data/uploads/134503-280745135.csv', 'wk4': '/mnt/user-data/uploads/134747-280845253.csv',
         'wk5': '/mnt/user-data/uploads/135023-280945043.csv'}
OUR_WK5_IDS = {'3744535025', '3744535027', '3744535028', '3744535029', '3744535030', '3744535032'}
import sys
FROZEN_FILE = sys.argv[1]
frozen = json.load(open(FROZEN_FILE))

def load(wk):
    pts, fp, own, entries = [], {}, {}, []
    with open(FILES[wk], encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            if row[0].strip() and row[3].strip() not in ('', 'null'):
                p = float(row[3]); pts.append(p)
                entries.append((row[1], row[2], p, row[4], int(row[0])))
            if len(row) >= 11 and row[6].strip():
                m = re.match(r'(.*) \((\d+)-(\d+)\)', row[6])
                fp[m.group(3)] = float(row[9]); own[m.group(3)] = float(row[8].rstrip('%'))
    return pts, fp, own, entries

def pctl(sorted_pts, s):        # share of field this score beats
    return 100 * bisect.bisect_left(sorted_pts, s) / len(sorted_pts)

user = None
summary = {}
for wk in ['wk1', 'wk2', 'wk3', 'wk4', 'wk5']:
    pts, fp, own, entries = load(wk)
    sp = sorted(pts); n = len(sp)
    cut20 = sp[int(n * 0.80)]; cut1 = sp[int(n * 0.99)]; med = sp[n // 2]; top = sp[-1]
    if user is None:
        user = next(e[1] for e in entries if e[0] in OUR_WK5_IDS) if wk == 'wk5' else None
    summary[wk] = dict(n=n, median=med, cash20=cut20, top1=cut1, winner=top, fp=fp, own=own, entries=entries, sp=sp)

# our username comes from the Week 5 entry ids
_, _, _, e5 = load('wk5')
user = next(e[1] for e in e5 if e[0] in OUR_WK5_IDS).split(' (')[0]
print('Our FanDuel entry name:', user)

report = {}
for wk, S in summary.items():
    sp = S['sp']
    print(f"\n===== {wk.upper()}  field {S['n']:,} | median {S['median']:.1f} | cash line (top 20%) {S['cash20']:.1f} | top 1% {S['top1']:.1f} | winner {S['winner']:.1f}")
    rows = []
    for i, L in enumerate(frozen[wk], 1):
        sc = 0; zero = []; detail = []
        for p in L:
            f = S['fp'].get(p['pid'])
            if f is None: f = 0.0; zero.append(p['name'] + ' (not in field)')
            elif f == 0: zero.append(p['name'])
            sc += f; detail.append((p['pos'], p['name'], p['salary'], f, S['own'].get(p['pid'], 0)))
        cum = sum(d[4] for d in detail)
        rows.append(dict(L=i, qb=L[0]['name'], score=sc, pct=pctl(sp, sc), cash=sc >= S['cash20'], zero=zero, cum_own=cum, detail=detail))
        print(f"  NEW L{i} {L[0]['name']:<16} {sc:6.2f}  beats {pctl(sp, sc):5.1f}%  {'CASH' if sc >= S['cash20'] else '----'}  cumOwn {cum:5.1f}%  zeros:{zero}")
    ours = [e for e in S['entries'] if e[1].split(' (')[0] == user]
    seen = {}
    for e in ours: seen.setdefault(e[3], e)
    old = []
    for lu, e in seen.items():
        old.append(dict(score=e[2], pct=pctl(sp, e[2]), cash=e[2] >= S['cash20'], lineup=lu, rank=e[4]))
    old.sort(key=lambda d: -d['score'])
    for o in old:
        print(f"  OLD {o['score']:6.2f}  beats {o['pct']:5.1f}%  {'CASH' if o['cash'] else '----'}  | {o['lineup'][:150]}")
    print(f"  entries by us in this contest: {len(ours)} ({len(seen)} distinct rosters)")
    report[wk] = dict(field=S['n'], median=S['median'], cash20=S['cash20'], top1=S['top1'], winner=S['winner'],
                      new=rows, old=old, our_entries=len(ours))
json.dump(report, open(FROZEN_FILE.replace('.json', '_grade.json'), 'w'), indent=1, default=str)
