import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
M=pd.read_pickle('master.pkl')
M=M[(M.in_main==1)&(M.ls_proj>0)&(M.stat!=4)&(M.main_games>=2)].copy()
M=M[M.date<'2026-11-10']
M['l5f']=M.l5.fillna(M.ls_proj); M['blend']=0.7*M.ls_proj+0.3*M.l5f
M['elig']=(M.stat==1)|(M.min3>=18)
M['season']=np.where(M.date<'2025-07-01','2024-25',np.where(M.date<'2026-07-01','2025-26','2026-27'))
E=M[M.elig].copy(); E['val']=E.actual/(E.salary/1000)
print('player-slates eligible',len(E),'slates',E.date.nunique(), E.groupby('season').date.nunique().to_dict())
def acc(d,cols):
    return {c:(round((d.actual-d[c]).abs().mean(),2),round((d.actual-d[c]).mean(),2)) for c in cols}
print('\n1) MAE / bias (actual-proj):')
for s,d in list(E.groupby('season'))+[('ALL',E)]:
    print(s,len(d),acc(d,['ls_proj','blend','l5f']))
A=E[E['agg']>0]
print('agg subset',len(A),acc(A,['ls_proj','agg','blend']), 'corr ls~agg',round(A.ls_proj.corr(A['agg']),3))
A=A.assign(ha=0.5*A.ls_proj+0.5*A['agg']); print('  0.5/0.5 LS+agg',acc(A,['ha']))
print('\n2) by salary tier:')
E['tier']=pd.cut(E.salary,[0,4500,5500,7000,8500,10000,20000],labels=['<=4.5k','4.5-5.5k','5.5-7k','7-8.5k','8.5-10k','>10k'])
t=E.groupby('tier').apply(lambda d:pd.Series(dict(n=len(d),ls=d.ls_proj.mean(),blend=d.blend.mean(),act=d.actual.mean(),bias_ls=(d.actual-d.ls_proj).mean(),bias_blend=(d.actual-d.blend).mean(),
    mae_ls=(d.actual-d.ls_proj).abs().mean(),mae_bl=(d.actual-d.blend).abs().mean(),sd_act=(d.actual-d.ls_proj).std(),p5x=(d.val>=5).mean(),p6x=(d.val>=6).mean(),p7x=(d.val>=7).mean(),dnp=(d.actual==0).mean())))
print(t.round(2).to_string())
print('\n3) by role-change gap (LS - last5):')
E['gap']=E.ls_proj-E.l5f
E['gb']=pd.cut(E.gap,[-99,-8,-4,-2,2,4,8,99])
def ols(d):
    X=np.c_[np.ones(len(d)),d.ls_proj,d.l5f]; b=np.linalg.lstsq(X,d.actual,rcond=None)[0]; return b
rows=[]
for g,d in E[E.l5.notna()].groupby('gb'):
    b=ols(d); rows.append(dict(gap=str(g),n=len(d),share=len(d)/len(E),ls=d.ls_proj.mean(),l5=d.l5f.mean(),act=d.actual.mean(),bias_ls=(d.actual-d.ls_proj).mean(),bias_blend=(d.actual-d.blend).mean(),
        mae_ls=(d.actual-d.ls_proj).abs().mean(),mae_blend=(d.actual-d.blend).abs().mean(),w_ls=b[1],w_l5=b[2],sal=d.salary.mean(),p6x=(d.val>=6).mean()))
print(pd.DataFrame(rows).round(2).to_string())
b=ols(E[E.l5.notna()]); print('pooled OLS actual ~ %.2f + %.3f LS + %.3f l5'%tuple(b))
for s,d in E[E.l5.notna()].groupby('season'):
    b=ols(d); print(' ',s,'OLS: %.2f + %.3f LS + %.3f l5'%tuple(b))
print('\n4) new-role starters (starter, min3<24) vs established:')
E['newrole']=(E.stat==1)&((E.min3<24)|E.min3.isna())
E['cheap']=E.salary<5500
for (nr,ch),d in E.groupby(['newrole','cheap']):
    print(f'newrole={nr} cheap={ch} n={len(d)} per-slate={len(d)/E.date.nunique():.1f} ls={d.ls_proj.mean():.1f} blend={d.blend.mean():.1f} act={d.actual.mean():.1f} bias_ls={(d.actual-d.ls_proj).mean():+.2f} bias_blend={(d.actual-d.blend).mean():+.2f} val={d.val.mean():.2f} p6x={(d.val>=6).mean():.3f} p7x={(d.val>=7).mean():.3f}')
# role-up: LS >= l5+6 and cheap
E['roleup']=(E.gap>=6)
for (ru,ch),d in E.groupby(['roleup','cheap']):
    print(f'roleup(LS-l5>=6)={ru} cheap={ch} n={len(d)} per-slate={len(d)/E.date.nunique():.1f} ls={d.ls_proj.mean():.1f} blend={d.blend.mean():.1f} act={d.actual.mean():.1f} bias_ls={(d.actual-d.ls_proj).mean():+.2f} bias_blend={(d.actual-d.blend).mean():+.2f} val={d.val.mean():.2f} p6x={(d.val>=6).mean():.3f} pown={d.pown.mean():.1f}')
E.to_pickle('elig.pkl')
