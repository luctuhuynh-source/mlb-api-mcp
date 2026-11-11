import pandas as pd, numpy as np, io, contextlib, warnings, sys
warnings.filterwarnings('ignore'); pd.set_option('display.width',260)
with contextlib.redirect_stdout(io.StringIO()): import final_tables as FT
zp=FT.zp
EDG=np.array([0.0001,0.001,0.005,0.01,0.02,0.05,0.10,0.15,0.20,0.25,0.30,1.0]); MUL=np.array([2398.2,129.9,8.64,4.02,3.10,2.39,2.04,1.82,1.77,1.43,0.016,0.0])
def ret(pct,cap=True):
    t=np.clip(1-np.asarray(pct)/100,1e-9,1); m=MUL[np.searchsorted(EDG,t,side='left')]; return np.minimum(m,8.64) if cap else m
def pcts(R,c):
    z=FT.Z(R,c); return 100*np.searchsorted(zp,z,side='left')/len(zp), z
def line(R,c,lus=slice(0,4)):
    S=R[[f'{c}_s{j}' for j in range(1,5)]].values; ok=~np.isnan(S).any(axis=1); p,z=pcts(R,c); S,p,z=S[ok][:,lus],p[ok][:,lus],z[ok][:,lus]; opt=R.opt.values[ok][:,None] if 'opt' in R else np.nan
    allp,_=pcts(R,c); allz=FT.Z(R,c)[ok]
    return dict(n=int(ok.sum()),fp=S.mean(),pct=p.mean(),cash=100*(z>=.72).mean(),t10=100*(z>=1.27).mean(),t1=100*(z>=2.17).mean(),ge360=100*(S>=360).mean(),of_opt=100*(S/opt).mean() if 'opt' in R else np.nan,
                L1=allp[ok][:,0].mean(),L4=allp[ok][:,3].mean(),miss4=100*(allz.max(axis=1)<.72).mean(),ret=ret(p).mean())
def show(R,cs,lus=slice(0,4),lab=''):
    print(f'{"config"+lab:22} {"n":>4} {"FP":>6} {"pct":>5} {"cash%":>6} {"top10%":>6} {"top1%":>6} {">=360":>6} {"%ofOpt":>6} {"L1pct":>6} {"L4pct":>6} {"0of4":>5} {"ret/$":>6}')
    for c in cs:
        if f'{c}_s1' not in R: continue
        x=line(R,c,lus); print(f'{c:22} {x["n"]:4d} {x["fp"]:6.1f} {x["pct"]:5.1f} {x["cash"]:6.1f} {x["t10"]:6.1f} {x["t1"]:6.2f} {x["ge360"]:6.1f} {x["of_opt"]:6.1f} {x["L1"]:6.1f} {x["L4"]:6.1f} {x["miss4"]:5.1f} {x["ret"]:6.2f}')
def pair(R,a,b,lus=slice(0,4),lab=''):
    Sa=R[[f'{a}_s{j}' for j in range(1,5)]].values; Sb=R[[f'{b}_s{j}' for j in range(1,5)]].values; ok=~np.isnan(Sa).any(axis=1)&~np.isnan(Sb).any(axis=1)
    pa,za=pcts(R,a); pb,zb=pcts(R,b); n=ok.sum(); se=lambda x:x.std()/np.sqrt(len(x))
    df=(Sa[ok][:,lus]-Sb[ok][:,lus]).mean(axis=1); dp=(pa[ok][:,lus]-pb[ok][:,lus]).mean(axis=1); dc=100*((za[ok][:,lus]>=.72).mean(axis=1)-(zb[ok][:,lus]>=.72).mean(axis=1)); dt=100*((za[ok][:,lus]>=1.27).mean(axis=1)-(zb[ok][:,lus]>=1.27).mean(axis=1)); d1=100*((za[ok][:,lus]>=2.17).mean(axis=1)-(zb[ok][:,lus]>=2.17).mean(axis=1))
    print(f'  {a} - {b}{lab}: n={n} | FP {df.mean():+.2f} (se {se(df):.2f}) | pct {dp.mean():+.2f} (se {se(dp):.2f}) | cash {dc.mean():+.1f} (se {se(dc):.1f}) | top10 {dt.mean():+.1f} (se {se(dt):.1f}) | top1 {d1.mean():+.2f} (se {se(d1):.2f}) | slates differing {int((np.abs(Sa[ok]-Sb[ok]).sum(axis=1)>0.01).sum())}')
if __name__=='__main__':
    print('check: average entry capped return',round(float(ret(np.random.default_rng(1).uniform(0,100,400000)).mean()),3),'uncapped',round(float(ret(np.random.default_rng(1).uniform(0,100,4000000),False).mean()),3))
    R=FT.load('b78a_results.csv'); print('B78a slates',len(R))
    cs=['CAL_free','CAL_hyb','CAL_c4o6','CAL_free_noSub','CAL_free_noBoth','CAL_c4_noBoth','CAL_free_lam25','CAL_c4_lam25','CAL_c4_stack6','CAL_c4_stack7','CAL_c4_cum285']
    show(R,cs)
    print('PAIRED:')
    for a,b in [('CAL_c4o6','CAL_free'),('CAL_hyb','CAL_free'),('CAL_c4o6','CAL_hyb'),('CAL_free_noSub','CAL_free'),('CAL_free_noBoth','CAL_free'),('CAL_c4_noBoth','CAL_c4o6'),('CAL_free_lam25','CAL_free'),('CAL_c4_lam25','CAL_c4o6'),('CAL_c4_stack6','CAL_c4o6'),('CAL_c4_stack7','CAL_c4o6')]: pair(R,a,b)
    print('lineups 3-4 only:'); show(R,['CAL_free','CAL_free_lam25','CAL_c4o6','CAL_c4_lam25'],slice(2,4)); pair(R,'CAL_free_lam25','CAL_free',slice(2,4),' [L3-4]'); pair(R,'CAL_c4_lam25','CAL_c4o6',slice(2,4),' [L3-4]')
    print('lineups 2-4 only:'); show(R,['CAL_c4o6','CAL_c4_stack6','CAL_c4_stack7'],slice(1,4)); pair(R,'CAL_c4_stack6','CAL_c4o6',slice(1,4),' [L2-4]'); pair(R,'CAL_c4_stack7','CAL_c4o6',slice(1,4),' [L2-4]')
    R4=R[R.games==4].reset_index(drop=True); print('4-game slates only:',len(R4)); show(R4,['CAL_c4o6','CAL_c4_cum285'],slice(2,4)); pair(R4,'CAL_c4_cum285','CAL_c4o6',slice(2,4),' [L3-4]')
    for c in ['CAL_free','CAL_hyb','CAL_c4o6']: print(c,'players used %.1f, players in all 4: %.2f'%(R[c+'_uniq'].mean(),R[c+'_max4'].mean()),'| mean cum own L1 %.0f L4 %.0f | max from one game L1 %.2f'%(R[c+'_own1'].mean(),R[c+'_own4'].mean(),R[c+'_mg1'].mean()))
    print('first-tip share of pool %.2f ; stackable games %.1f'%(R.first_tip_share.mean(),R.stack_games.mean()))
    # ---- haircut
    H=FT.load('b78h_results.csv'); print('\nB78h slates',len(H),'| late new-starter-like per slate %.1f, early %.1f, flips applied %.2f, of which ineligible pre-lock %.2f'%(H.ns_late.mean(),H.ns_early.mean(),H.flips.mean(),H.flips_banned.mean()))
    for sc in ('fin','hair','noNS'): show(H.assign(opt=np.nan),[f'{sc}_{c}' for c in ['V0','LS_free','CAL_free','CAL_c4o6']],lab=' '+sc)
    for c in ['V0','LS_free','CAL_free','CAL_c4o6']: pair(H,f'fin_{c}',f'hair_{c}'); pair(H,f'fin_{c}',f'noNS_{c}')
    for sc in ('fin','hair','noNS'): pair(H,f'{sc}_CAL_free',f'{sc}_LS_free'); pair(H,f'{sc}_CAL_free',f'{sc}_V0'); pair(H,f'{sc}_CAL_c4o6',f'{sc}_CAL_free')
    print('late new starters per lineup: '+', '.join(f'{c} {H[c].mean():.2f}' for c in H.columns if c.endswith('_ns') and c.startswith('fin')))
