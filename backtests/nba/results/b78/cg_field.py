"""ChatGPT Q1 + Q9 + exact payouts.
(1) Date-held-out calibration of the field model on the 18 real contests, entry by entry; original SD proxy vs a shift-invariant one.
(2) Same-slate contest comparison (field strength, lines, users, fill).  (3) Exact payouts of rebuilt lineups inside the real contests."""
import pandas as pd, numpy as np, glob, os, re, warnings, pickle
warnings.filterwarnings('ignore'); pd.set_option('display.width',260); pd.set_option('display.max_columns',40)
A='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'; R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/standings/'
att={'08ad4fb1-136227-281386492.csv':'2026-11-04','d30626fb-136227-281386493.csv':'2026-11-04','bfa77127-136288-281415449.csv':'2026-11-05','d62a48dc-136288-281415467.csv':'2026-11-05','23632d04-136333-281428632.csv':'2026-11-06','4f14fd8b-136333-281428650.csv':'2026-11-06','3f990762-136378-281443024.csv':'2026-11-07','79523267-136378-281443029.csv':'2026-11-07','363f0206-136475-281475573.csv':'2026-11-09','86ee8b01-136475-281475577.csv':'2026-11-09','eb8ea2d9-136535-281491886.csv':'2026-11-10'}
files=[(A+f,d) for f,d in att.items()]+[(f,re.search(r'(2026-\d\d-\d\d)',os.path.basename(f)).group(1)) for f in sorted(glob.glob(R+'*.csv'))]
C=[]
for f,dt in files:
    d=pd.read_csv(f,encoding='utf-8-sig',low_memory=False)
    ci=dict(d[['Contest Info','Contest Value']].dropna().values.tolist()) if 'Contest Info' in d else {}
    e=d[d.EntryId.notna()].copy(); e['Points']=pd.to_numeric(e.Points,errors='coerce'); e=e[e.Points.notna()].sort_values('Points',ascending=False).reset_index(drop=True)
    e['w']=pd.to_numeric(e.Won.astype(str).str.replace('[$,]','',regex=True),errors='coerce').fillna(0) if 'Won' in e else 0.0
    p=d[d.Player.notna()].copy(); p['own']=p['%Drafted'].astype(str).str.rstrip('%').astype(float)/100; p['F']=pd.to_numeric(p.FPTS,errors='coerce').fillna(0)
    pts=e.Points.values; mu=pts.mean(); mo=(p.own*p.F).sum(); so=p.own.sum()
    u=e.EntryName.astype(str).str.replace(r'\s*\(.*','',regex=True); uc=u.value_counts()
    fee=float(str(ci.get('Entry Fee','$0')).replace('$','') or 0); pool=float(str(ci.get('Prize Pool','$0')).replace('$','').replace(',','') or 0)
    C.append(dict(file=os.path.basename(f)[:28],date=dt,name=str(ci.get('Contest Name',''))[:30],fee=fee,pool=pool,maxent=ci.get('Max Entries Per User',''),filled=float(ci.get('Seats Filled',0) or 0),seats=float(ci.get('Total Seats',0) or 0),
        n=len(e),mean=mu,sd=pts.std(),mu_own=mo,sum_own=so,proxy=np.sqrt((p.own*(1-p.own)*p.F**2).sum()),proxyC=np.sqrt((p.own*(1-p.own)*(p.F-mo/9)**2).sum()),
        cash=(e[e.w>0].Points.min() if (e.w>0).any() else np.nan),q90=np.quantile(pts,.9),q99=np.quantile(pts,.99),q999=np.quantile(pts,.999),users=len(uc),top10share=uc.head(10).sum()/len(e),share_150=(uc[uc>=100].sum()/len(e)),
        pts=pts,w=e.w.values))
D=pd.DataFrame(C); D['kappa']=D.sd/D.proxy; D['kappaC']=D.sd/D.proxyC; D['rake']=np.where((D.fee>0)&(D.pool>0),1-D.pool/(D.fee*D.n),np.nan); D['fill']=D.filled/D.seats
pickle.dump(D,open('contests18.pkl','wb'))
print('FIELD-MEAN RECONCILIATION: actual mean minus sum(own x pts); tracked ownership total')
print(D[['date','name','n','mean','mu_own','sum_own']].assign(gap=D['mean']-D.mu_own,gap_after_offset=D['mean']-D.mu_own-0.12*(900-100*D.sum_own)).round(2).to_string())
print('kappa original: mean %.3f sd %.3f cv %.3f | shift-invariant: mean %.3f sd %.3f cv %.3f'%(D.kappa.mean(),D.kappa.std(),D.kappa.std()/D.kappa.mean(),D.kappaC.mean(),D.kappaC.std(),D.kappaC.std()/D.kappaC.mean()))
# ---- (1) date-held-out, entry-level calibration
def zq(c,k): return np.quantile((c.pts-c['mean'])/c.sd,np.linspace(0.0005,0.9995,2000))
res=[]
for dt in D.date.unique():
    tr=D[D.date!=dt]; te=D[D.date==dt]
    for lab,kcol,pcol in [('original','kappa','proxy'),('shift-invariant','kappaC','proxyC')]:
        kap=tr.groupby('date')[kcol].mean().mean()                      # dates weighted equally
        pool=np.sort(np.concatenate([np.concatenate([zq(c,kcol) for _,c in g.iterrows()])[::len(g)] for _,g in tr.groupby('date')]))
        for _,c in te.iterrows():
            muh=c.mu_own+0.12*(900-100*c.sum_own); sdh=kap*c[pcol]
            pred=100*np.searchsorted(pool,(c.pts-muh)/sdh,side='left')/len(pool); act=100*(1-(np.arange(len(c.pts))+0.5)/len(c.pts))
            err=pred-act; m=lambda lo,hi:(np.abs(err[(act>=lo)&(act<hi)]).mean(),err[(act>=lo)&(act<hi)].mean())
            res.append(dict(model=lab,date=dt,file=c.file,bias=err.mean(),mae=np.abs(err).mean(),mae_cash=m(70,80)[0],bias_cash=m(70,80)[1],mae_t10=m(85,95)[0],bias_t10=m(85,95)[1],mae_t1=m(98.5,99.5)[0],bias_t1=m(98.5,99.5)[1],
                            cashline_err=(muh+np.quantile(pool,1-np.mean(c.w>0))*sdh-c.cash) if np.isfinite(c.cash) else np.nan))
Rr=pd.DataFrame(res)
print('\nDATE-HELD-OUT entry-level calibration (percentile points; mean across 12 dates, SE across dates):')
for lab,g in Rr.groupby('model'):
    x=g.groupby('date').mean(numeric_only=True); se=lambda c:x[c].std()/np.sqrt(len(x))
    print(f'  {lab:16} bias {x.bias.mean():+.2f} (se {se("bias"):.2f}) | abs error all {x.mae.mean():.2f} (se {se("mae"):.2f}) | near cash line {x.mae_cash.mean():.2f} (bias {x.bias_cash.mean():+.2f}, se {se("bias_cash"):.2f}) | near top 10% {x.mae_t10.mean():.2f} (bias {x.bias_t10.mean():+.2f}, se {se("bias_t10"):.2f}) | near top 1% {x.mae_t1.mean():.2f} (bias {x.bias_t1.mean():+.2f}) | worst date abs error {x.mae.max():.2f} | cash-line FP error mean abs {g.cashline_err.abs().mean():.2f}')
a=Rr[Rr.model=='original'].groupby('date').mae.mean(); b=Rr[Rr.model=='shift-invariant'].groupby('date').mae.mean(); dd=b-a
print('  shift-invariant minus original, abs error: %+.2f (se %.2f), better on %d of %d dates'%(dd.mean(),dd.std()/np.sqrt(len(dd)),(dd<0).sum(),len(dd)))
# ---- (2) same-slate contests
print('\nSAME-SLATE CONTESTS:')
print(D[D.fee>0][['date','name','fee','n','fill','rake','maxent','users','top10share','share_150','mean','cash','q90','q99','q999']].round(3).to_string())
