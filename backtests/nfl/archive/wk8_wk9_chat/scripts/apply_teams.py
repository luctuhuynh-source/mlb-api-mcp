import csv,sys
sys.path.insert(0,'/home/claude/bt/scripts'); from manual_teams import M
inv={n:t for t,ns in M.items() for n in ns}
for wk in ['wk1','wk2','wk3','wk4','wk5']:
    rows=list(csv.DictReader(open(f'build/{wk}_t.csv')))
    for r in rows:
        if not r['team'] and r['name'] in inv: r['team']=inv[r['name']]
    w=csv.DictWriter(open(f'build/{wk}_t.csv','w',newline=''),fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    teams={}
    for r in rows:
        if r['team']: teams[r['team']]=teams.get(r['team'],0)+1
    unk=[(r['name'],r['salary']) for r in rows if not r['team'] and int(r['salary'])>=4500]
    print(wk,'teams',len(teams),sorted(teams),'| still unknown >=4500:',unk)
