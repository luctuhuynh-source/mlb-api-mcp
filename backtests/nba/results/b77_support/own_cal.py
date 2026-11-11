import pandas as pd, numpy as np, warnings
warnings.filterwarnings('ignore'); pd.set_option('display.width',250)
E=pd.read_pickle('elig.pkl'); C=pd.read_csv('hist_contests_mu.csv'); O=pd.read_csv('hist_own.csv')
g=C[(C.ctype==4)&(C.fee<=20)].copy(); g['shot']=g.contest.str.contains('Shot')&~g.contest.str.contains('Pigg')
ref=g.sort_values(['date','shot','entries']).groupby('date').tail(1)[['date','cid']]
O=O.merge(ref,on=['date','cid'])
E=E.merge(O[['date','salary_id','own']],on=['date','salary_id'],how='inner') if False else E.merge(O[['date','salary_id','own']],on=['date','salary_id'],how='left')
E=E[E.date.isin(ref.date)]; E['own']=E.own.fillna(0)
po=E.pown.fillna(0); E['own900']=po*900/E.groupby('date').pown.transform(lambda x:x.fillna(0).sum())
E=E[E.main_games>=4]
print('slates',E.date.nunique(),'rows',len(E),' corr proj900~realized %.3f ; sum realized among eligible per slate %.0f'%(E.own900.corr(E.own),E.groupby('date').own.sum().mean()))
E['b']=pd.cut(E.own900,[-1,2,5,10,15,25,35,50,200])
t=E.groupby('b').agg(n=('own','size'),proj=('own900','mean'),real=('own','mean'),mae=('own',lambda x:0),val=('val','mean'),p6=('val',lambda x:(x>=6).mean()),act_minus_ls=('actual',lambda x:0))
t['mae']=E.assign(e=(E.own-E.own900).abs()).groupby('b').e.mean(); t['act_minus_ls']=E.assign(e=E.actual-E.ls_proj).groupby('b').e.mean()
print(t.round(2).to_string())
def tier(x): return np.where(x>=35,3,np.where(x>=15,2,1))
E['tp']=tier(E.own900); E['tr']=tier(E.own)
print('tier confusion (rows=projected tier 1:<15,2:15-35,3:>=35; cols=realized):\n',pd.crosstab(E.tp,E.tr,normalize='index').round(2).to_string())
print('contrarian flag (<10%% projected) but realized >=10%%: %.2f ; realized <10%% among proj>=10%%: %.2f'%((E[E.own900<10].own>=10).mean(),(E[E.own900>=10].own<10).mean()))
# value by REALIZED ownership bucket (does chalk deliver?)
E['rb']=pd.cut(E.own,[-1,2,5,10,20,35,100])
print(E.groupby('rb').agg(n=('own','size'),sal=('salary','mean'),val=('val','mean'),p6=('val',lambda x:(x>=6).mean()),act_minus_ls=('actual',lambda x:0)).assign(act_minus_ls=E.assign(e=E.actual-E.ls_proj).groupby('rb').e.mean()).round(2).to_string())
# role-up cheap players: projected vs realized ownership
ru=E[(E.gap>=6)&(E.salary<5500)]; print('cheap role-up: n %d proj900 %.1f realized %.1f val %.2f p6 %.2f'%(len(ru),ru.own900.mean(),ru.own.mean(),ru.val.mean(),(ru.val>=6).mean()))
for lo,hi in [(0,5),(5,15),(15,35),(35,101)]:
    x=ru[(ru.own>=lo)&(ru.own<hi)]; print('   realized own %d-%d: n %d val %.2f p6 %.2f act-LS %+.2f'%(lo,hi,len(x),x.val.mean(),(x.val>=6).mean(),(x.actual-x.ls_proj).mean()))
