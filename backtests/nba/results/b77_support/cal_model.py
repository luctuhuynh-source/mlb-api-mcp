"""Small calibrated projection: actual ~ LS + AggProj + ownership + new-starter flags. Fit on the first half of the AggProj era, test on the rest."""
import pandas as pd, numpy as np, warnings
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
E=pd.read_pickle('elig.pkl'); E=E[(E['agg']>0)&(E.main_games>=2)].copy()
E['own900']=E.pown.fillna(0)*900/E.groupby('date').pown.transform(lambda x:x.fillna(0).sum())
E['ns']=((E.stat==1)&~(E.min3>=24)).astype(float); E['ns_cheap']=E.ns*(E.salary<5500); E['bench']=(E.stat!=1).astype(float)
E['gapu']=(E.ls_proj-E.l5f).clip(lower=0); E['gapd']=(E.l5f-E.ls_proj).clip(lower=0); E['sal']=E.salary/1000
tr=E[E.date<'2026-03-01']; te=E[E.date>='2026-03-01']
print('train',len(tr),tr.date.nunique(),'slates | test',len(te),te.date.nunique(),'slates',te.date.min(),te.date.max())
def fit(cols,d=tr):
    X=np.c_[np.ones(len(d)),d[cols].values]; return np.linalg.lstsq(X,d.actual.values,rcond=None)[0]
def pred(b,cols,d): return np.c_[np.ones(len(d)),d[cols].values]@b
def rep(name,p,d=te):
    e=d.actual.values-p; return f'{name:34} MAE {np.abs(e).mean():.3f}  RMSE {np.sqrt((e**2).mean()):.3f}  bias {e.mean():+.2f}'
print(rep('LS',te.ls_proj.values)); print(rep('AggProj',te['agg'].values)); print(rep('0.5 LS + 0.5 Agg',0.5*te.ls_proj.values+0.5*te['agg'].values)); print(rep('v1.3 blend 0.7LS+0.3 l5',te.blend.values))
models={'M1 LS+Agg':['ls_proj','agg'],'M2 +own900':['ls_proj','agg','own900'],'M3 +own900+newstarter':['ls_proj','agg','own900','ns','ns_cheap'],
        'M4 +l5':['ls_proj','agg','own900','ns','ns_cheap','l5f'],'M5 +bench+sal':['ls_proj','agg','own900','ns','ns_cheap','bench','sal']}
B={}
for nm,cols in models.items():
    b=fit(cols); B[nm]=(b,cols); print(rep(nm,pred(b,cols,te)),' coef',dict(zip(['const']+cols,np.round(b,3))))
# stability: fit on test, coefficients
b=fit(models['M3 +own900+newstarter'],te); print('M3 refit on TEST half:',dict(zip(['const']+models['M3 +own900+newstarter'],np.round(b,3))))
b=fit(models['M3 +own900+newstarter'],E); print('M3 fit on ALL:',dict(zip(['const']+models['M3 +own900+newstarter'],np.round(b,3))))
# decile calibration of M3 on test
b,cols=B['M3 +own900+newstarter']; te=te.assign(m3=pred(b,cols,te))
print(te.groupby(pd.qcut(te.m3,8)).agg(n=('actual','size'),m3=('m3','mean'),ls=('ls_proj','mean'),agg=('agg','mean'),act=('actual','mean')).round(2).to_string())
import json; json.dump({k:(list(map(float,v[0])),v[1]) for k,v in B.items()},open('cal_coefs.json','w'))
