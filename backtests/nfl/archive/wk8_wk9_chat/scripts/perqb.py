import os, sys, json, bisect, csv, re
os.environ['REPAIR'] = '1'
sys.path.insert(0, '/home/claude/bt/scripts')
import build, variants
from variants import solve
def run(wk, cfg, per_qb):
    P, games = build.load(wk)
    mean_itt = sum(v['itt'] for v in games.values()) / len(games)
    for p in P:
        if p['pos'] == 'DST':
            base = 7 + 0.6 * (mean_itt - games[p['opp']]['itt'])
            p['p2'] = base + (0.5 * (p['salary']/1000 - 4) if cfg['dst'] == 'oppitt' else -0.8 * (p['salary']/1000 - 4))
        else:
            p['p2'] = (p['salary'] - 3000)/1000 * build.MULT[p['pos']] * (games[p['team']]['itt']/mean_itt) ** cfg['alpha']
        p['opp'] = games[p['team']]['opp']
    qbs = sorted([p for p in P if p['pos'] == 'QB' and 6800 <= p['salary'] <= 7600], key=lambda p: (-p['itt'], -p['salary']))
    picked, used = [], set()
    for q in qbs:
        if q['game'] in used: continue
        picked.append(q); used.add(q['game'])
        if len(picked) == 3: break
    N = 3 * per_qb; cap = N // 2
    prior, expo, out = [], {}, []
    for q in picked:
        first = None
        for k in range(per_qb):
            e = {pid: (c if c >= cap else 0) for pid, c in expo.items()}
            e = {pid: 3 for pid, c in expo.items() if c >= cap}          # solve() blocks players at >=3; map cap hits to 3
            if first is None:
                L = solve(P, q, cfg, prior, e)
            else:
                share = [p['pid'] for p in first if p['team'] == q['team'] and p['pos'] in ('WR', 'TE')]
                last = out[-1] if out[-1] else first
                dst = [p['pid'] for p in last if p['pos'] == 'DST'][0]
                rbs = [p['pid'] for p in last if p['pos'] == 'RB']
                L = solve(P, q, cfg, prior, e, share, dst, rbs)
            out.append(L or [])
            if L:
                if first is None: first = L
                ids = [p['pid'] for p in L]; prior.append(ids)
                for pid in ids: expo[pid] = expo.get(pid, 0) + 1
    return out, picked
FILES = variants.FILES
fpd = {}
for wk, f in FILES.items():
    fp, pts = {}, []
    with open(f, encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); next(r)
        for row in r:
            if len(row) >= 11 and row[6].strip():
                m = re.match(r'(.*) \((\d+)-(\d+)\)', row[6]); fp[m.group(3)] = float(row[9])
            if row[0].strip() and row[3] not in ('', 'null'): pts.append(float(row[3]))
    sp = sorted(pts); fpd[wk] = (fp, sp, sp[int(len(sp)*.8)], sp[int(len(sp)*.99)])
for label, cfg in [('TODAY RULES', dict(stack=2, bring=0, alpha=1, qb='itt', dst='oppitt', rbfloor=20000)),
                   ('+bring+cheapDST', dict(stack=2, bring=1, alpha=1, qb='itt', dst='cheap', rbfloor=20000))]:
    for per_qb in (2, 5):
        tot = dict(n=0, cash=0, top1=0, pct=0, empty=0, wk_any=0); per = []
        for wk in FILES:
            out, picked = run(wk, cfg, per_qb)
            fp, sp, c20, t1 = fpd[wk]; wc = 0; byqb = []
            for i, L in enumerate(out):
                if not L: tot['empty'] += 1; continue
                s = sum(fp.get(p['pid'], 0) for p in L); pc = 100*bisect.bisect_left(sp, s)/len(sp)
                tot['n'] += 1; tot['pct'] += pc; tot['cash'] += s >= c20; tot['top1'] += s >= t1; wc += s >= c20
                byqb.append(round(s))
            tot['wk_any'] += wc > 0; per.append((wk, wc, len([L for L in out if L]), max(byqb) if byqb else 0))
        print(f"{label:<16} {per_qb}/QB: lineups {tot['n']} (no legal: {tot['empty']}) | cashed {tot['cash']} = {100*tot['cash']/max(tot['n'],1):.0f}% | top1 {tot['top1']} | avg beats {tot['pct']/max(tot['n'],1):.1f}% | weeks w/ a cash {tot['wk_any']}/5 | per wk (cash/lineups/best) {[(w[1], w[2], w[3]) for w in per]}")
