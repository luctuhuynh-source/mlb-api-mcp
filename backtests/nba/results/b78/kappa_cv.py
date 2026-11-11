"""Gemini Q1: does a regression for the field-SD multiplier (kappa) on slate size + ownership concentration beat the fixed 0.35? Leave-one-SLATE-out CV on the 18 real contests."""
import pandas as pd, numpy as np, glob, os, re, warnings
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
A='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'; R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/standings/'
att={'08ad4fb1-136227-281386492.csv':'2026-11-04','d30626fb-136227-281386493.csv':'2026-11-04','bfa77127-136288-281415449.csv':'2026-11-05','d62a48dc-136288-281415467.csv':'2026-11-05','23632d04-136333-281428632.csv':'2026-11-06','4f14fd8b-136333-281428650.csv':'2026-11-06','3f990762-136378-281443024.csv':'2026-11-07','79523267-136378-281443029.csv':'2026-11-07','363f0206-136475-281475573.csv':'2026-11-09','86ee8b01-136475-281475577.csv':'2026-11-09','eb8ea2d9-136535-281491886.csv':'2026-11-10'}
files=[(A+f,d) for f,d in att.items()]
for f in sorted(glob.glob(R+'*.csv')):
    m=re.search(r'(2026-\d\d-\d\d)',os.path.basename(f)); files.append((f,m.group(1)))
H=pd.read_csv('hist_players.csv',usecols=['date','main_games']).drop_duplicates('date').set_index('date').main_games
T=pd.read_pickle('live_pulls.pkl').drop_duplicates('date').set_index('date').main_games
rows=[]
for f,dt in files:
    d=pd.read_csv(f,encoding='utf-8-sig',low_memory=False); e=pd.to_numeric(d[d.EntryId.notna()].Points,errors='coerce').dropna().values
    p=d[d.Player.notna()].copy(); p['own']=p['%Drafted'].astype(str).str.rstrip('%').astype(float)/100; p['F']=pd.to_numeric(p.FPTS,errors='coerce').fillna(0)
    teams=p.Team.nunique() if 'Team' in p else np.nan
    g=H.get(dt,np.nan); g=T.get(dt,np.nan) if not np.isfinite(g) else g
    if not np.isfinite(g) and np.isfinite(teams): g=teams/2
    rows.append(dict(file=os.path.basename(f)[:30],date=dt,games=g,n=len(e),mean=e.mean(),sd=e.std(),proxy=np.sqrt((p.own*(1-p.own)*p.F**2).sum()),own2=(p.own**2).sum(),
                     q75=np.quantile(e,.75),q90=np.quantile(e,.90),q99=np.quantile(e,.99),q999=np.quantile(e,.999)))
D=pd.DataFrame(rows); D['kappa']=D.sd/D.proxy
print(D.round(3).to_string()); print('corr kappa~games %.2f ; kappa~own2 %.2f ; games~own2 %.2f'%(D.kappa.corr(D.games),D.kappa.corr(D.own2),D.games.corr(D.own2)))
def fit(X,y): return np.linalg.lstsq(np.c_[np.ones(len(X)),X],y,rcond=None)[0]
models={'fixed 0.35':None,'LOO mean':[],'games':['games'],'own2':['own2'],'games+own2':['games','own2']}
res={m:[] for m in models}
for dt in D.date.unique():
    tr,te=D[D.date!=dt],D[D.date==dt]
    for m,cols in models.items():
        if cols is None: kh=np.full(len(te),0.35)
        elif cols==[]: kh=np.full(len(te),tr.kappa.mean())
        else: b=fit(tr[cols].values,tr.kappa.values); kh=np.c_[np.ones(len(te)),te[cols].values]@b
        for (_,r),kk in zip(te.iterrows(),kh):
            sdh=kk*r.proxy; res[m].append(dict(date=dt,kerr=kk-r.kappa,sderr=sdh-r.sd,e75=(r['mean']+0.70*sdh)-r.q75,e90=(r['mean']+1.27*sdh)-r.q90,e99=(r['mean']+2.17*sdh)-r.q99))
print('\nLeave-one-slate-out error (18 contests, 12 slates): mean absolute error')
for m in models:
    x=pd.DataFrame(res[m]); print(f'  {m:11} kappa {x.kerr.abs().mean():.3f} | field SD {x.sderr.abs().mean():.2f} FP | top-25% line {x.e75.abs().mean():.2f} FP | top-10% line {x.e90.abs().mean():.2f} FP | top-1% line {x.e99.abs().mean():.2f} FP | worst top-1% miss {x.e99.abs().max():.1f}')
b=fit(D[['games','own2']].values,D.kappa.values); print('full-sample fit kappa = %.3f %+.4f*games %+.4f*own2'%tuple(b))
b=fit(D[['games']].values,D.kappa.values); print('full-sample fit kappa = %.3f %+.4f*games'%tuple(b))
