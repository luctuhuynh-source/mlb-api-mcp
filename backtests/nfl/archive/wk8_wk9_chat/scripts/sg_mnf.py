"""FanDuel Single Game (MVP 1.5x pts & salary + 4 FLEX, $60k) — props projection, brute force."""
import csv, sys, itertools
sys.path.insert(0,'scripts')
from props import props_table, fd_points, nm
POOL=sys.argv[1]; T=props_table('mnf7')
SF_ITT=(51.5+7.5)/2; WAS_ITT=(51.5-7.5)/2
P=[]
for r in csv.DictReader(open(POOL,encoding='utf-8-sig')):
    if r['Injury Indicator'] in ('O','IR','D','NA'): continue
    pos=r['Position']; t=r['Team']; itt=SF_ITT if t=='SF' else WAS_ITT; opp=WAS_ITT if t=='SF' else SF_ITT
    if pos=='K': pr=0.30*itt
    elif pos=='D': pr=max(1.0, 7-0.25*(opp-20))
    else:
        o=T.get((nm(r['Nickname']),('WAS','SF')))
        if not o: continue          # unpriced = no market interest -> excluded in single game
        pr=fd_points(o,pos)
    P.append(dict(name=r['Nickname'],pos=pos,team=t,sal=int(r['Salary']),mvp_sal=int(r['MVP 1.5x Salary']),pr=pr,tag=r['Injury Indicator'],id=r['Id']))
P.sort(key=lambda p:-p['pr'])
for p in P: print(f"{p['pos']:3}{p['team']:4}{p['name']:24}{p['sal']:6} {p['pr']:5.1f} {p['tag']}")
best=[]
for m in P:
    rest=[p for p in P if p is not m]
    for f in itertools.combinations(rest,5):
        L=(m,)+f
        sal=m['mvp_sal']+sum(p['sal'] for p in f)
        if sal>60000 or sal<59000: continue
        if len({p['team'] for p in L})<2: continue
        qbs=[p for p in L if p['pos']=='QB']
        if not qbs: continue                       # protocol: always roster a QB
        q=qbs[0]
        if not any(p['team']==q['team'] and p['pos'] in('WR','TE') for p in L): continue  # QB + own catcher
        if sum(p['pos'] in('K','D') for p in L)>1: continue
        if any(p['pos']=='D' and p['team']!=q['team'] for p in L): continue  # no DST vs own QB
        best.append((1.5*m['pr']+sum(p['pr'] for p in f),sal,L))
best.sort(key=lambda x:-x[0])
out=[best[0]]
for b in best[1:]:
    A={p['name'] for p in out[0][2]}; B={p['name'] for p in b[2]}
    if b[2][0]['name']!=out[0][2][0]['name'] and len(A&B)<=5: out.append(b); break
for s,sal,L in out:
    print(f"\nproj {s:.1f} ${sal}: MVP {L[0]['name']} ({L[0]['pos']} {L[0]['team']} {L[0]['mvp_sal']}) | "+' | '.join(f"{p['name']} ({p['pos']} {p['team']} {p['sal']}, {p['pr']:.1f})" for p in L[1:]))
print('\nTOP BY MVP:')
seen=set()
for s,sal,L in best:
    if L[0]['name'] in seen: continue
    seen.add(L[0]['name'])
    print(f"{s:.1f} ${sal} MVP {L[0]['name']} | "+' | '.join(p['name'] for p in L[1:]))
    if len(seen)==6: break
