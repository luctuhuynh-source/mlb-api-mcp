"""Gemini Q2 gate: is AggProj's edge still there on PRE-LOCK snapshots? Player level + lineup level."""
import pandas as pd, numpy as np, warnings, io, contextlib
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
A=pd.read_pickle('live_vs_final.pkl')   # last pre-lock pull merged with final, 7 slates (10/31-11/9)
A['aggl']=np.where(A.agg_live>0,A.agg_live,np.nan); A['aggf']=np.where(A.agg_fin>0,A.agg_fin,np.nan)
# eligible by PRE-LOCK info; drop players later ruled out (no projection can score those)
E=A[(A.ls_proj_live>0)&(A.stat_live!=4)&((A.stat_live==1)|(A.min3>=18))&(A.stat_fin!=4)&A.aggl.notna()].copy()
E['cal_l']=-0.26+0.136*E.ls_proj_live+0.856*E.aggl; E['l5f']=E.l5.fillna(E.ls_proj_live); E['blend_l']=0.7*E.ls_proj_live+0.3*E.l5f
E['late']=E.tip>=30
def mae(d,c): return (d.actual-d[c]).abs().mean()
print('PRE-LOCK player rows',len(E),'slates',E.date.nunique())
for nm,d in [('all',E),('first-tip games',E[~E.late]),('later games',E[E.late])]:
    print(f'  {nm:16} n={len(d):4d}  MAE pre-lock: LS {mae(d,"ls_proj_live"):.2f}  Agg {mae(d,"aggl"):.2f}  CAL {mae(d,"cal_l"):.2f}  blend {mae(d,"blend_l"):.2f} | MAE final: LS {mae(d,"ls_proj_fin"):.2f}  Agg {mae(d,"aggf"):.2f} | post-lock MAE drop: LS {mae(d,"ls_proj_live")-mae(d,"ls_proj_fin"):+.2f}  Agg {mae(d,"aggl")-mae(d,"aggf"):+.2f}')
# paired per-slate difference LS abs err - CAL abs err (pre-lock), SE across slates
s=E.groupby('date').apply(lambda d:(d.actual-d.ls_proj_live).abs().mean()-(d.actual-d.cal_l).abs().mean())
print('  per-slate (LS MAE - CAL MAE), pre-lock:',s.round(2).to_dict(),'mean %.3f se %.3f, slates CAL better %d of %d'%(s.mean(),s.std()/np.sqrt(len(s)),(s>0).sum(),len(s)))
X=np.c_[np.ones(len(E)),E.ls_proj_live,E.aggl]; b=np.linalg.lstsq(X,E.actual,rcond=None)[0]; print('  OLS on PRE-LOCK values: actual = %.2f + %.3f LS + %.3f Agg'%tuple(b))
# how much do the two fields move after the snapshot?
for nm,d in [('first-tip games',E[~E.late]),('later games',E[E.late])]:
    print(f'  {nm:16} mean |final - prelock|: LS {(d.ls_proj_fin-d.ls_proj_live).abs().mean():.2f}  Agg {(d.aggf-d.aggl).abs().mean():.2f} ; share moved 3+ FP: LS {((d.ls_proj_fin-d.ls_proj_live).abs()>=3).mean():.3f}  Agg {((d.aggf-d.aggl).abs()>=3).mean():.3f}')
# when Agg and LS disagree PRE-LOCK by 4+, who is right?
E['dgap']=E.aggl-E.ls_proj_live
for lo,hi in [(-99,-4),(-4,4),(4,99)]:
    d=E[(E.dgap>lo)&(E.dgap<=hi)]; print(f'  pre-lock Agg-LS in ({lo},{hi}]: n {len(d)} LS {d.ls_proj_live.mean():.1f} Agg {d.aggl.mean():.1f} actual {d.actual.mean():.1f} | MAE LS {mae(d,"ls_proj_live"):.2f} Agg {mae(d,"aggl"):.2f}')
