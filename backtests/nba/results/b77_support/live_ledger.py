import pandas as pd, numpy as np, re, glob, os, warnings
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
A='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'; R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/standings/'
files=[('11/04','v1.2b',A+'08ad4fb1-136227-281386492.csv'),('11/04','v1.2b',A+'d30626fb-136227-281386493.csv'),('11/05','v1.2b',A+'bfa77127-136288-281415449.csv'),('11/05','v1.2b',A+'d62a48dc-136288-281415467.csv'),
 ('11/06','v1.2b',A+'23632d04-136333-281428632.csv'),('11/06','v1.2b',A+'4f14fd8b-136333-281428650.csv'),('11/07','v1.3',A+'3f990762-136378-281443024.csv'),('11/07','v1.3',A+'79523267-136378-281443029.csv'),
 ('11/09','v1.3',A+'363f0206-136475-281475573.csv'),('11/09','v1.3',A+'86ee8b01-136475-281475577.csv'),('11/10','v1.3',A+'eb8ea2d9-136535-281491886.csv')]
rows=[]
for dt,ver,f in files:
    d=pd.read_csv(f,encoding='utf-8-sig',low_memory=False); ci=dict(d[['Contest Info','Contest Value']].dropna().values.tolist())
    e=d[d.EntryId.notna()].copy(); e['Points']=pd.to_numeric(e.Points); n=len(e); pts=np.sort(e.Points.values)
    e['w']=pd.to_numeric(e.Won.astype(str).str.replace('[$,]','',regex=True),errors='coerce').fillna(0)
    me=e[e.EntryName.astype(str).str.startswith('dalatcrew')].sort_values('Points',ascending=False)
    pct=[100*np.searchsorted(pts,x,side='left')/n for x in me.Points]
    mu,sd=pts.mean(),pts.std(); fee=float(ci['Entry Fee'].replace('$',''))
    p=d[d.Player.notna()].copy(); p['own']=p['%Drafted'].astype(str).str.rstrip('%').astype(float); p['id']=p.Player.str.extract(r'\((.*?)\)'); own=p.set_index('id').own; sal=pd.to_numeric(p.set_index('id').Salary)
    def anat(L):
        ids=re.findall(r'\((\d+-\d+)\)',L); return own.reindex(ids).sum(), int((own.reindex(ids)<10).sum()), int((sal.reindex(ids)>=10000).sum())
    top=e.sort_values('Points',ascending=False).head(max(int(n*.01),1)); fld=e.sample(min(4000,n),random_state=1)
    ta=np.array([anat(L) for L in top.Lineup]); fa=np.array([anat(L) for L in fld.Lineup.dropna()]); ma=np.array([anat(L) for L in me.Lineup])
    rows.append(dict(date=dt,ver=ver,contest=ci['Contest Name'][:24],fee=fee,n=n,entries=len(me),scores=' '.join(f'{x:.1f}' for x in me.Points),pct=' '.join(f'{x:.0f}' for x in pct),best_pct=max(pct),mean_pct=np.mean(pct),
        z=' '.join(f'{(x-mu)/sd:+.2f}' for x in me.Points),cash=int((me.w>0).sum()),fees=fee*len(me),won=me.w.sum(),
        own_us=ma[:,0].mean(),own_top1=ta[:,0].mean(),own_field=fa[:,0].mean(),lt10_us=ma[:,1].mean(),lt10_top1=ta[:,1].mean(),lt10_field=fa[:,1].mean(),n10k_us=ma[:,2].mean(),n10k_top1=ta[:,2].mean(),n10k_field=fa[:,2].mean()))
T=pd.DataFrame(rows)
print(T[['date','ver','contest','fee','n','entries','scores','pct','best_pct','mean_pct','cash','fees','won']].round(1).to_string())
print(T[['date','contest','own_us','own_top1','own_field','lt10_us','lt10_top1','lt10_field','n10k_us','n10k_top1','n10k_field']].round(2).to_string())
for v,g in T.groupby('ver'):
    sl=g.groupby('date').best_pct.max()
    print(v,'slates',g.date.nunique(),'entries',int(g.entries.sum()),'cashes',int(g.cash.sum()),'fees',g.fees.sum(),'won',g.won.sum(),'net',g.won.sum()-g.fees.sum(),'best-of-4 pct by slate',sl.round(0).to_dict(),'median',sl.median().round(1),'mean lineup pct',round(np.average(g.mean_pct,weights=g.entries),1))
print('anatomy means (all 11 contests): us cum-own %.0f top1%% %.0f field %.0f | sub-10%% players us %.2f top1%% %.2f field %.2f | >=$10k players us %.2f top1%% %.2f field %.2f'%tuple(T[c].mean() for c in ['own_us','own_top1','own_field','lt10_us','lt10_top1','lt10_field','n10k_us','n10k_top1','n10k_field']))
T.to_csv('live_ledger.csv',index=False)
