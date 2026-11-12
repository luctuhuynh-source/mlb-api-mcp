import pandas as pd, numpy as np, sys, re
for f,label in [("/mnt/user-data/uploads/136166-281367338.csv","A"),("/mnt/user-data/uploads/136166-281367344.csv","B")]:
    df=pd.read_csv(f,encoding='utf-8-sig')
    ent=df.dropna(subset=['Points']).copy()
    ent['Points']=ent['Points'].astype(float)
    n=len(ent); pts=ent['Points'].values
    pl=df.dropna(subset=['Player']).copy()
    pl['own']=pl['%Drafted'].str.rstrip('%').astype(float)
    pl['FPTS']=pl['FPTS'].astype(float); pl['Salary']=pl['Salary'].astype(float)
    pl['x']=pl['FPTS']/(pl['Salary']/1000)
    print(f"\n=== {label} {f.split('/')[-1]}  entries={n}")
    for q in [50,75,80,85,90,95,99]:
        print(f"  top{100-q}% line {np.percentile(pts,q):.1f}", end='')
    print(f"  max {pts.max()}")
    me=ent[ent.EntryName.str.startswith('dalatcrew')].sort_values('Points',ascending=False)
    for _,r in me.iterrows():
        beat=(pts<r.Points).mean()*100
        print(f"  {r.EntryName} rank {int(r.Rank)}/{n} {r.Points} beat {beat:.1f}%")
    # player table lookup
    own=dict(zip(pl.Player.str.replace(r' \(.*\)','',regex=True),zip(pl.own,pl.FPTS,pl.Salary)))
    # our exposure
    from collections import Counter
    c=Counter()
    for _,r in me.iterrows():
        for p in r.Lineup.split(', '):
            name=re.sub(r'^[A-Z/]+ ','',p); name=re.sub(r' \(.*\)','',name); c[name]+=1
    print("  our players: exposure / own / FPTS / sal / x")
    for name,k in c.most_common():
        o=own.get(name,(np.nan,)*3)
        print(f"    {name:28s} {k}/6  own {o[0]:5.1f}%  FP {o[1]:5.1f}  ${o[2]:.0f}  {o[1]/(o[2]/1000):.1f}x  lev {k/6*100-o[0]:+.0f}")
    # top 100 analysis
    top=ent.head(100)
    cnt=Counter(); 
    for _,r in top.iterrows():
        for p in r.Lineup.split(', '):
            name=re.sub(r'^[A-Z/]+ ','',p); name=re.sub(r' \(.*\)','',name); cnt[name]+=1
    print("  top-100 most used:", [(k,v,own.get(k,(0,0,0))[1]) for k,v in cnt.most_common(12)])
    print("  best FP:", pl.sort_values('FPTS',ascending=False)[['Player','FPTS','Salary','own']].head(12).to_string(index=False))
    print("  best value x (sal<=5500):", pl[pl.Salary<=5500].sort_values('x',ascending=False)[['Player','FPTS','Salary','own','x']].head(8).to_string(index=False))
    print("  busts (own>=25%):", pl[pl.own>=25].sort_values('x')[['Player','FPTS','Salary','own','x']].head(8).to_string(index=False))
