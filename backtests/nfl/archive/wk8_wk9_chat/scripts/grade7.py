import csv,re,json,bisect,statistics as st
F='wk7/standings/million.csv'
pts=[];fp={};own={};sal={};ours=[];top100=[]
with open(F,encoding='utf-8-sig',newline='') as fh:
    r=csv.reader(fh); next(r)
    for row in r:
        if row[0].strip() and row[3].strip() not in ('','null'):
            p=float(row[3]); pts.append(p)
            if row[2].startswith('dalatcrew'): ours.append((int(row[0]),p,row[4]))
            if int(row[0])<=100: top100.append(row[4])
        if len(row)>=11 and row[6].strip():
            m=re.match(r'(.*) \((\d+)-(\d+)\)',row[6]); pid=row[6].split('(')[-1].rstrip(')')
            fp[pid]=float(row[9]); own[pid]=float(row[8].rstrip('%')); sal[pid]=int(row[10])
sp=sorted(pts); n=len(sp)
cut20=sp[int(n*0.80)]; cut5=sp[int(n*0.95)]; cut1=sp[int(n*0.99)]
print(f'field {n:,} median {sp[n//2]:.1f} cash(top20%) {cut20:.1f} top5% {cut5:.1f} top1% {cut1:.1f} winner {sp[-1]:.1f}')
B=json.load(open('wk7/build_x5.json'))['lineups']
def key(L): return frozenset(p['fdid'] for p in L)
built={key(L):i+1 for i,L in enumerate(B)}
def parse(lu): return frozenset(re.findall(r'\((\d+-\d+)\)',lu))
print('\nOUR ENTRIES (Million):')
tot=0
for rank,p,lu in sorted(ours):
    k=parse(lu); i=built.get(k,'?'); pct=100*bisect.bisect_left(sp,p)/n
    cash='CASH' if p>=cut20 else '----'
    L=B[i-1] if i!='?' else None
    dead=[q['name'] for q in L if fp.get(q['fdid'],0)<=1.0] if L else []
    cum=sum(own.get(q['fdid'],0) for q in L) if L else 0
    print(f"  L{i:<3} rank {rank:>6} {p:6.2f} beats {pct:5.1f}% {cash} cumOwn {cum:5.0f}% dead:{dead}")
print(len(ours),'entries matched; built lineups found:',sorted(x for x in [built.get(parse(lu)) for _,_,lu in ours] if x))
# per-player realized
print('\nROSTERED PLAYERS realized (name, exposure, proj, actual, own):')
exp={}
for L in B:
    for q in L: exp.setdefault(q['fdid'],[q,0])[1]+=1
for pid,(q,e) in sorted(exp.items(), key=lambda x:-x[1][1]):
    print(f"  {q['name']:24}{q['pos']:4}x{e} proj {q['proj']:5.1f} act {fp.get(pid,0):5.1f} own {own.get(pid,0):5.1f}%")
# top100 pattern
from collections import Counter
c=Counter(); qbs=Counter(); flexrb=0
for lu in top100:
    ids=re.findall(r'(QB|RB|WR|TE|D) ([^,]+?) \((\d+-\d+)\)',lu)
    for pos,name,pid in ids: c[name]+=1
    qbs[ids[0][1]]+=1
    if ids[7][0]=='RB': flexrb+=1
print('\nTOP-100: FLEX=RB',flexrb,'| QBs',qbs.most_common(6))
print('most rostered',c.most_common(15))
