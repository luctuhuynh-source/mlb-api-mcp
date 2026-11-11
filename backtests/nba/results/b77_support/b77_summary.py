import pandas as pd, numpy as np, sys, warnings
warnings.filterwarnings('ignore'); pd.set_option('display.width',280); pd.set_option('display.max_columns',60); pd.set_option('display.max_rows',200)
f=sys.argv[1] if len(sys.argv)>1 else 'b77_results.csv'; base=sys.argv[2] if len(sys.argv)>2 else 'V0_blend'
R=pd.read_csv(f); R=R[R.games>=4].reset_index(drop=True) if '--all' not in sys.argv else R
# field model from the best-tracked low-stakes GPP on the main slate (tracked ownership >= 880 of 900)
C=pd.read_csv('hist_contests_mu.csv'); KAP=float([a.split('=')[1] for a in sys.argv if a.startswith('--kappa=')][0]) if any(a.startswith('--kappa=') for a in sys.argv) else 0.35
g=C[(C.ctype==4)&(C.fee<=20)&(C.tracked>=880)].copy(); g['shot']=(g.contest.str.contains('Shot')&~g.contest.str.contains('Pigg')).astype(int)
ref=g.sort_values(['date','shot','entries']).groupby('date').tail(1).set_index('date')
du=C[(C.ctype==1)&(C.tracked>=880)].sort_values(['date','entries']).groupby('date').tail(1).set_index('date')
n0=len(R); R=R[R.date.isin(ref.index)].reset_index(drop=True)
R['mu']=R.date.map(ref.mu_ls)+0.12*(900-R.date.map(ref.tracked)); R['sd']=KAP*R.date.map(ref.proxy_ls); R['ref']=R.date.map(ref.contest)
R['du_mu']=R.date.map(du.mu_ls)+0.12*(900-R.date.map(du.tracked)); R['du_sd']=KAP*R.date.map(du.proxy_ls)
print('slates with a well-tracked reference GPP:',len(R),'of',n0,'| ref kinds',R.ref.str.contains('Pigg').map({True:'piggy',False:'shot'}).value_counts().to_dict())
R['season']=np.where(R.date<'2025-07-01','2024-25',np.where(R.date<'2026-07-01','2025-26','2026-27'))
zp=np.load('z_pool.npy'); ZC,Z10,Z1,Z01=0.72,1.27,2.17,2.74
def topfrac(z): return 1-np.searchsorted(zp,z,side='left')/len(zp)
def pay(p,cap=True):
    b=[(0.0001,2398.23),(0.001,129.94),(0.005,8.64),(0.01,4.02),(0.02,3.10),(0.05,2.39),(0.10,2.04),(0.15,1.82),(0.20,1.77),(0.245,1.43)]
    for lim,x in b:
        if p<=lim: return min(x,8.64) if cap else x
    return 0.0
cfgs=[c[:-3] for c in R.columns if c.endswith('_s1')]
print(f'{f}: slates {len(R)} (>=4 games unless --all) | seasons {R.season.value_counts().to_dict()} | field mu mean {R.mu.mean():.1f} sd mean {R.sd.mean():.1f} | opt mean {R.opt.mean():.1f} = z {((R.opt-R.mu)/R.sd).mean():.2f}')
rows=[]; ZS={}
for c in cfgs:
    S=R[[f'{c}_s{j}' for j in range(1,5)]].values; ok=~np.isnan(S).any(axis=1)
    Z=(S-R.mu.values[:,None])/R.sd.values[:,None]; ZS[c]=(Z,ok)
    z=Z[ok]; tf=topfrac(z)
    pc=np.vectorize(pay)(tf); pf=np.vectorize(lambda p:pay(p,False))(tf)
    best=z.max(axis=1)
    rows.append(dict(cfg=c,n=int(ok.sum()),mean=S[ok].mean(),z=z.mean(),pct=100*(1-tf).mean(),cash=100*(z>=ZC).mean(),top10=100*(z>=Z10).mean(),top1=100*(z>=Z1).mean(),top01=100*(z>=Z01).mean(),
        best_z=best.mean(),best_pct_med=100*np.median(1-topfrac(best)),any_cash=100*(best>=ZC).mean(),any_top10=100*(best>=Z10).mean(),any_top1=100*(best>=Z1).mean(),
        roi_cap=100*(pc.mean()-1),roi_full=100*(pf.mean()-1),wipe=100*(S[ok].max(axis=1)<0.70*R.opt.values[ok]).mean(),
        L1z=z[:,0].mean(),L2z=z[:,1].mean(),L3z=z[:,2].mean(),L4z=z[:,3].mean(),L1cash=100*(z[:,0]>=ZC).mean(),L4cash=100*(z[:,3]>=ZC).mean()))
T=pd.DataFrame(rows).set_index('cfg'); print(T.round(2).to_string())
print(f'\nPaired vs {base} (same slates): mean FP diff per lineup (SE by slate), z diff, cash-rate diff, top-10% diff, top-1% diff')
Zb,okb=ZS[base]
for c in cfgs:
    if c==base: continue
    Z,ok=ZS[c]; m=ok&okb
    dS=(R[[f'{c}_s{j}' for j in range(1,5)]].values[m].mean(axis=1)-R[[f'{base}_s{j}' for j in range(1,5)]].values[m].mean(axis=1))
    dB=Z[m].max(axis=1)-Zb[m].max(axis=1)
    seas={s:round(float(dS[(R.season.values[m]==s)].mean()),1) for s in ['2024-25','2025-26','2026-27'] if (R.season.values[m]==s).any()}
    print(f'  {c:12} n={m.sum():3d}  dFP {dS.mean():+5.2f} (se {dS.std()/np.sqrt(m.sum()):.2f})  dz {(Z[m].mean()-Zb[m].mean()):+.3f}  dcash {100*((Z[m]>=ZC).mean()-(Zb[m]>=ZC).mean()):+5.1f}  dtop10 {100*((Z[m]>=Z10).mean()-(Zb[m]>=Z10).mean()):+5.1f}  dtop1 {100*((Z[m]>=Z1).mean()-(Zb[m]>=Z1).mean()):+5.2f}  dbest_z {dB.mean():+.3f} (se {dB.std()/np.sqrt(m.sum()):.3f})  by season {seas}')
print('\nBy season, cash% / top10% / top1% per lineup:')
for c in cfgs:
    Z,ok=ZS[c]; print(f'  {c:12}',{s:(round(100*(Z[ok&(R.season==s).values]>=ZC).mean(),1),round(100*(Z[ok&(R.season==s).values]>=Z10).mean(),1),round(100*(Z[ok&(R.season==s).values]>=Z1).mean(),2)) for s in ['2024-25','2025-26','2026-27']})
print('\nBy slate size (games), base and LS: mean z per lineup, cash%')
R['gb']=pd.cut(R.games,[3,5,7,9,20],labels=['4-5','6-7','8-9','10+'])
for c in [base]:
    Z,ok=ZS[c]; print(f'  {c:12}',{str(g):(int(((R.gb==g).values&ok).sum()),round(float(Z[ok&(R.gb==g).values].mean()),2),round(100*(Z[ok&(R.gb==g).values]>=ZC).mean(),1)) for g in R.gb.cat.categories})
# double-up estimate for lineup 1
du=R[R.du_mu.notna()]
print('\nDouble-up (L1 only): slates with a tracked $2 double-up',len(du))
for c in cfgs:
    s=du[f'{c}_s1']; line=du.du_mu+0.19*du.du_sd; m=s.notna()
    print(f'  {c:12} L1 mean {s[m].mean():.1f} vs DU field mean {du.du_mu[m].mean():.1f} | est. DU cash rate {100*(s[m]>=line[m]).mean():.1f}% (break-even 53.6% at 13% rake... 862 entries, top 375 paid 2x)')
# anatomy
an=['n10k','n45','ru','ruc','cumown','lt10','ge35','sal','maxteam']
pre=[p for p in ['V0_blend','LS','CAL'] if f'{p}1_n10k' in R.columns]
print('\nLineup anatomy (means): optimal lineup vs built lineups')
print(pd.DataFrame({'optimal':[R['opt_'+a].mean() for a in an],**{f'{c}{j}':[R[f'{c}{j}_{a}'].mean() for a in an] for c in pre for j in (1,4)}},index=an).round(2).to_string())
print('\nBy slate size: mean z per lineup / cash% / top10%')
for c in cfgs:
    Z,ok=ZS[c]; print(f'  {c:13}',{str(g):(int(((R.gb==g).values&ok).sum()),round(float(Z[ok&(R.gb==g).values].mean()),2),round(100*(Z[ok&(R.gb==g).values]>=ZC).mean(),1),round(100*(Z[ok&(R.gb==g).values]>=Z10).mean(),1)) for g in R.gb.cat.categories})
T.to_csv(f.replace('.csv','_summary.csv'))
