"""Gemini Q11: slate-level SD of our mean percentile, and false-stop / false-continue rates of candidate stop rules (bootstrap of B77 slate means)."""
import pandas as pd, numpy as np, io, contextlib, warnings
warnings.filterwarnings('ignore')
with contextlib.redirect_stdout(io.StringIO()): import final_tables as FT
zp=FT.zp; R=FT.load('b77c_results.csv'); R2=FT.load('b77b_results.csv')
def slate_pct(R,c):
    z=FT.Z(R,c); ok=~np.isnan(z).any(axis=1); return (100*np.searchsorted(zp,z[ok],side='left')/len(zp)).mean(axis=1), R.date.values[ok]
def slate_fp(R,c): return R[[f'{c}_s{j}' for j in range(1,5)]].mean(axis=1).values
cand,_=slate_pct(R,'CAL_free'); c4,_=slate_pct(R,'CAL_c4o6'); v13,_=slate_pct(R2,'V0_blend'); lsf,_=slate_pct(R,'LS_free')
print('slates',len(cand),'| slate-mean percentile: candidate mean %.1f SD %.1f | no-cap %.1f SD %.1f | v1.3 %.1f SD %.1f'%(cand.mean(),cand.std(),c4.mean(),c4.std(),v13.mean(),v13.std()))
print('autocorr lag1 of candidate slate means: %.2f'%np.corrcoef(cand[:-1],cand[1:])[0,1])
dfp=slate_fp(R,'CAL_free')-slate_fp(R,'LS_free'); ok=~np.isnan(dfp); dfp=dfp[ok]
print('paired candidate - pure-LS shadow (same structure), FP per lineup per slate: mean %+.2f SD %.1f'%(dfp.mean(),dfp.std()))
rng=np.random.default_rng(7); B=20000
def sim(x,true,n):  # shift the empirical slate distribution so its mean equals `true`
    y=x-x.mean()+true; return rng.choice(y,(B,n)).mean(axis=1)
print('\nP(15-slate mean percentile below threshold) by TRUE long-run mean (candidate-shaped slate distribution, SD %.1f):'%cand.std())
print('  true mean :   45     50     55     60     65')
for thr in (50,47,44):
    print(f'  stop if <{thr}: '+'  '.join(f'{100*(sim(cand,t,15)<thr).mean():5.1f}%' for t in (45,50,55,60,65)))
print('P(25-slate mean percentile at or above threshold) by TRUE mean:')
for thr in (50,55,58):
    print(f'  cont if >={thr}: '+'  '.join(f'{100*(sim(cand,t,25)>=thr).mean():5.1f}%' for t in (45,50,55,60,65)))
print('SE of the mean: 15 slates %.1f, 25 slates %.1f, 40 slates %.1f'%(cand.std()/np.sqrt(15),cand.std()/np.sqrt(25),cand.std()/np.sqrt(40)))
print('\nPaired rule (live minus pure-LS shadow, FP per lineup): P(15-slate mean diff < threshold) by TRUE mean diff')
print('  true diff :   -3      0     +3     +6    +9.6')
for thr in (-2.0,0.0):
    print(f'  stop if <{thr:+.0f}: '+'  '.join(f'{100*((rng.choice(dfp-dfp.mean()+t,(B,15)).mean(axis=1))<thr).mean():5.1f}%' for t in (-3,0,3,6,9.6)))
print('  SE of 15-slate paired diff %.2f FP; 25 slates %.2f'%(dfp.std()/np.sqrt(15),dfp.std()/np.sqrt(25)))
# combined two-stage rule (Gemini): stop at 15 if <44; at 25 continue only if >=55
def two(true,s1,s2):
    y=cand-cand.mean()+true; X=rng.choice(y,(B,25)); a=X[:,:15].mean(axis=1)<s1; b=X.mean(axis=1)<s2; return 100*(a|b).mean()
print('\nTwo-stage rules: P(stopped by slate 25) by TRUE mean  45 / 50 / 55 / 60 / 65')
for s1,s2,lab in [(44,55,'Gemini: <44 at 15, or <55 at 25'),(50,50,'R6 draft: <50 at 15 (and <50 at 25)'),(45,50,'<45 at 15, or <50 at 25'),(45,52,'<45 at 15, or <52 at 25')]:
    print(f'  {lab:36}: '+' / '.join(f'{two(t,s1,s2):.0f}%' for t in (45,50,55,60,65)))
