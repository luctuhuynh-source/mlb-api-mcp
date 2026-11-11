"""Calibrate a field-score model on the real FanDuel standings CSVs we hold."""
import pandas as pd, numpy as np, re, glob, os, warnings, json
warnings.filterwarnings('ignore')
A='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/standings/'
files=[(A+f) for f in ['08ad4fb1-136227-281386492.csv','d30626fb-136227-281386493.csv','bfa77127-136288-281415449.csv','d62a48dc-136288-281415467.csv',
 '23632d04-136333-281428632.csv','4f14fd8b-136333-281428650.csv','3f990762-136378-281443024.csv','79523267-136378-281443029.csv',
 '363f0206-136475-281475573.csv','86ee8b01-136475-281475577.csv','eb8ea2d9-136535-281491886.csv']]+sorted(glob.glob(R+'*.csv'))
H=pd.read_csv('hist_players.csv',usecols=['date','main_games']).drop_duplicates('date').set_index('date').main_games
out=[]; Z=[]; PAY=[]
for f in files:
    d=pd.read_csv(f,encoding='utf-8-sig',low_memory=False)
    ci=dict(d[['Contest Info','Contest Value']].dropna().values.tolist()) if 'Contest Info' in d else {}
    e=d[d.EntryId.notna()].copy(); e['Points']=pd.to_numeric(e.Points,errors='coerce'); e=e[e.Points.notna()]
    n=len(e); pts=e.Points.values
    p=d[d.Player.notna()].copy(); p['own']=p['%Drafted'].astype(str).str.rstrip('%').astype(float)/100; p['FPTS']=pd.to_numeric(p.FPTS,errors='coerce').fillna(0)
    mu=pts.mean(); sd=pts.std(); mu_own=(p.own*p.FPTS).sum(); proxy=np.sqrt((p.own*(1-p.own)*p.FPTS**2).sum())
    row=dict(file=os.path.basename(f)[:34],name=ci.get('Contest Name','')[:28],fee=ci.get('Entry Fee',''),start=ci.get('Start Time','')[:10],n=n,mean=mu,mu_own=mu_own,sum_own=p.own.sum(),median=np.median(pts),sd=sd,proxy=proxy,kappa=sd/proxy,
        q75=np.quantile(pts,.75),q90=np.quantile(pts,.90),q99=np.quantile(pts,.99),q999=np.quantile(pts,.999),win=pts.max())
    if 'Won' in e:
        e['w']=pd.to_numeric(e.Won.astype(str).str.replace('[$,]','',regex=True),errors='coerce').fillna(0)
        if (e.w>0).any():
            cash=e[e.w>0].Points.min(); row.update(cash=cash,paid=(e.w>0).mean(),zcash=(cash-mu)/sd)
            fee=float(str(ci.get('Entry Fee','$0')).replace('$','') or 0)
            if fee>0:
                e=e.sort_values('Points',ascending=False).reset_index(drop=True); e['pct']=(e.index+0.5)/n
                row.update(rake=1-e.w.sum()/(fee*n),mincash_x=e[e.w>0].w.min()/fee,x_top10=e.w.iloc[int(n*.10)-1]/fee,x_top1=e.w.iloc[int(n*.01)-1]/fee,x_top01=e.w.iloc[max(int(n*.001)-1,0)]/fee,x_win=e.w.iloc[0]/fee)
                PAY.append(pd.DataFrame(dict(pct=e.pct,x=e.w/fee,c=row['file'])))
    row.update(z50=(row['median']-mu)/sd,z75=(row['q75']-mu)/sd,z90=(row['q90']-mu)/sd,z99=(row['q99']-mu)/sd,z999=(row['q999']-mu)/sd,zwin=(row['win']-mu)/sd)
    row['games']=H.get(row['start'],np.nan)
    out.append(row); Z.append((pts-mu)/sd)
T=pd.DataFrame(out); pd.set_option('display.width',260); pd.set_option('display.max_columns',40)
print(T[['file','name','fee','start','games','n','mean','mu_own','sum_own','median','sd','proxy','kappa']].round(2).to_string())
print(T[['file','cash','paid','q75','q90','q99','q999','win','z50','zcash','z75','z90','z99','z999','zwin']].round(2).to_string())
print(T[['file','rake','mincash_x','x_top10','x_top1','x_top01','x_win']].round(2).to_string())
print('\nkappa mean %.3f sd %.3f ; by games corr %.2f'%(T.kappa.mean(),T.kappa.std(),T[['kappa','games']].corr().iloc[0,1]))
print(T[['z50','zcash','z75','z90','z99','z999']].describe().round(3).loc[['mean','std','min','max']])
Zall=np.concatenate(Z); qs=[.5,.6,.7,.75,.8,.85,.9,.95,.98,.99,.995,.999]
print('pooled z quantiles',{q:round(float(np.quantile(Zall,q)),3) for q in qs})
np.save('z_pool.npy',np.sort(Zall)[::max(1,len(Zall)//20000)])
T.to_csv('field_cal.csv',index=False)
PP=pd.concat(PAY); PP['bin']=pd.cut(PP.pct,[0,.0001,.001,.005,.01,.02,.05,.10,.15,.20,.25,.30,1.0])
print(PP.groupby('bin').x.mean().round(2)); PP.groupby('bin').x.mean().to_csv('payout_curve.csv')
