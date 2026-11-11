import os, sys, json, bisect
sys.path.insert(0, '/home/claude/bt/scripts')
import perqb
TABLE = [(1,1,250000),(2,2,80000),(3,3,40000),(4,4,20000),(5,5,10000),(6,6,5000),(7,7,3000),(8,8,2000),(9,9,1500),(10,10,1000),
 (11,12,800),(13,15,600),(16,20,500),(21,30,400),(31,50,300),(51,75,200),(76,100,150),(101,200,125),(201,300,100),(301,500,80),
 (501,1000,70),(1001,1500,60),(1501,2000,55),(2001,3000,50),(3001,5000,45),(5001,7000,40),(7001,10000,35),(10001,15000,30),(15001,25274,25)]
FEE = 15; N5 = 99740; PAID_SHARE = 25274 / N5
def prize_by_rank(rank):
    for a, b, p in TABLE:
        if a <= rank <= b: return p
    return 0
def prize(wk, s):
    fp, sp, _, _ = perqb.fpd[wk]
    better = len(sp) - bisect.bisect_right(sp, s)          # entries strictly above us
    if wk == 'wk5': return prize_by_rank(better + 1), better + 1
    # other weeks: map our finishing percentile onto the Week 5 table
    r = int(round((better + 1) / len(sp) * N5)); return prize_by_rank(max(r, 1)), better + 1
out = {}
for label, cfg in [('TODAY RULES', dict(stack=2, bring=0, alpha=1, qb='itt', dst='oppitt', rbfloor=20000)),
                   ('+bring+cheapDST', dict(stack=2, bring=1, alpha=1, qb='itt', dst='cheap', rbfloor=20000))]:
    for per_qb in (2, 3, 5):
        rows = []
        for wk in perqb.FILES:
            Ls, _ = perqb.run(wk, cfg, per_qb)
            fp = perqb.fpd[wk][0]
            won = cashes = 0
            for L in Ls:
                s = sum(fp.get(p['pid'], 0) for p in L); pz, rk = prize(wk, s); won += pz; cashes += pz > 0
            fees = FEE * len(Ls)
            rows.append((wk, len(Ls), cashes, fees, won))
        tf = sum(r[3] for r in rows); tw = sum(r[4] for r in rows); tc = sum(r[2] for r in rows); tn = sum(r[1] for r in rows)
        print(f"{label:<16} {per_qb}/QB @ $15: per wk (cash, fees, won) {[(r[2], r[3], r[4]) for r in rows]}")
        print(f"{'':<16} TOTAL lineups {tn}, cashed {tc} ({100*tc/tn:.0f}%), fees ${tf}, won ${tw}, net ${tw-tf}, ROI {100*(tw-tf)/tf:+.0f}%  | Week 5 only (exact table): net ${rows[4][4]-rows[4][3]}")
