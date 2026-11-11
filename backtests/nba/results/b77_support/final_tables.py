import pandas as pd, numpy as np, sys, warnings
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
C=pd.read_csv('hist_contests_mu.csv'); zp=np.load('z_pool.npy')
def load(f,kap=0.35):
    R=pd.read_csv(f); R=R[R.games>=4]
    g=C[(C.ctype==4)&(C.fee<=20)&(C.tracked>=880)].copy(); g['shot']=(g.contest.str.contains('Shot')&~g.contest.str.contains('Pigg')).astype(int)
    ref=g.sort_values(['date','shot','entries']).groupby('date').tail(1).set_index('date')
    R=R[R.date.isin(ref.index)].reset_index(drop=True)
    R['mu']=R.date.map(ref.mu_ls)+0.12*(900-R.date.map(ref.tracked)); R['sd']=kap*R.date.map(ref.proxy_ls); return R
def Z(R,c):
    S=R[[f'{c}_s{j}' for j in range(1,5)]].values; return (S-R.mu.values[:,None])/R.sd.values[:,None]
def stats(R,c):
    z=Z(R,c); ok=~np.isnan(z).any(axis=1); z=z[ok]; pct=100*np.searchsorted(zp,z,side='left')/len(zp)
    return dict(n=ok.sum(),fp=R[[f'{c}_s{j}' for j in range(1,5)]].values[ok].mean(),pct=pct.mean(),cash=100*(z>=.72).mean(),t10=100*(z>=1.27).mean(),t1=100*(z>=2.17).mean(),L1cash=100*(z[:,0]>=.72).mean(),L4cash=100*(z[:,3]>=.72).mean(),L1pct=pct[:,0].mean(),L4pct=pct[:,3].mean(),bestmed=np.median(pct.max(axis=1)),anycash=100*(z.max(axis=1)>=.72).mean())
def paired(R,a,b):
    za,zb=Z(R,a),Z(R,b); ok=~np.isnan(za).any(axis=1)&~np.isnan(zb).any(axis=1)
    dc=((za[ok]>=.72).mean(axis=1)-(zb[ok]>=.72).mean(axis=1))*100; dt=((za[ok]>=1.27).mean(axis=1)-(zb[ok]>=1.27).mean(axis=1))*100
    dp=(100*np.searchsorted(zp,za[ok],side='left')/len(zp)).mean(axis=1)-(100*np.searchsorted(zp,zb[ok],side='left')/len(zp)).mean(axis=1)
    n=ok.sum(); return f'{a} - {b}: n={n} cash {dc.mean():+.1f} pts (se {dc.std()/np.sqrt(n):.1f}); top10 {dt.mean():+.1f} (se {dt.std()/np.sqrt(n):.1f}); mean percentile {dp.mean():+.1f} (se {dp.std()/np.sqrt(n):.1f})'
R1=load('b77_results.csv'); R2=load('b77b_results.csv')
print('FULL HISTORY (Jan 2025-Nov 2026):',len(R1),'slates'); 
for c in ['V0_blend','LS','LS_free']: print(' ',c,{k:round(float(v),1) for k,v in stats(R1,c).items()})
print(' ',paired(R1,'LS','V0_blend')); print(' ',paired(R1,'LS_free','LS'))
print('AGGPROJ ERA (Oct 2025-Nov 2026):',len(R2),'slates')
for c in ['V0_blend','LS','CAL','CAL_cap2','CAL_t2','CAL_cap3','CAL_free']: print(' ',c,{k:round(float(v),1) for k,v in stats(R2,c).items()})
for a,b in [('CAL','V0_blend'),('CAL_free','CAL'),('CAL_free','V0_blend'),('CAL_cap3','CAL'),('CAL_t2','CAL')]: print(' ',paired(R2,a,b))
print('kappa sensitivity (field SD multiplier 0.31 / 0.35 / 0.39):')
for kap in (0.31,0.35,0.39):
    R=load('b77b_results.csv',kap); print('  kappa',kap,{c:(round(stats(R,c)['pct'],1),round(stats(R,c)['cash'],1),round(stats(R,c)['t10'],1),round(stats(R,c)['t1'],2)) for c in ['V0_blend','CAL','CAL_free']})
# null check: 4 random field percentiles
print('null best-of-4 median percentile =',round(100*0.5**0.25,1))
