import csv,re,glob
pools=['/root/.claude/uploads/3eb2421d-9eec-59a8-8c78-d010d6054058/cd6153f7-FanDuel-NFL-2026_PDT-10_PDT-11_PDT-135023-players-list.csv',
'/root/.claude/uploads/3eb2421d-9eec-59a8-8c78-d010d6054058/e0f9e439-FanDuel-NFL-2026_PDT-10_PDT-12_PDT-135282-players-list.csv']
team={}
for p in pools:
    for r in csv.DictReader(open(p,encoding='utf-8-sig')):
        team[r['Id'].split('-')[1]]=r['Team']
for wk in ['wk1','wk2','wk3','wk4','wk5']:
    rows=list(csv.DictReader(open(f'build/{wk}.csv')))
    out=[];miss=[]
    for r in rows:
        m=re.match(r'(.*) \((\d+)-(\d+)\)',r['name'])
        nm,pid=m.group(1),m.group(3)
        t=team.get(pid,'')
        if r['pos']=='D' and not t: t=''
        out.append([pid,nm,r['pos'],int(r['salary']),t])
        if not t: miss.append((nm,r['pos'],int(r['salary'])))
    out.sort(key=lambda x:(-x[3],x[1]))
    w=csv.writer(open(f'build/{wk}_t.csv','w',newline=''));w.writerow(['pid','name','pos','salary','team']);w.writerows(out)
    big=[m for m in miss if m[2]>=5000]
    print(wk,'missing team',len(miss),'of',len(rows),'| salary>=5000 missing:',len(big))
    print('  ',sorted(big,key=lambda x:-x[2])[:40])
