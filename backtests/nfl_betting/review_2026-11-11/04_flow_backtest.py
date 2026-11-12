#!/usr/bin/env python3
"""B-NFL-4: does FLOW (yards per play and giveaways in a half) predict the next half, beyond the closing spread and the score?
A = the 2H lean shape (halftime FLOW -> second half). B = the 1H lean shape (previous game's 1H FLOW -> this game's first half).
Limits: no historical 1H or 2H lines here, so the side is graded against the margin expected from the closing full-game spread
(and the halftime score for A), rounded to the half point. FLOW is reduced to yards per play, score margin and giveaways."""
import os, pandas as pd, numpy as np, numpy.linalg as la
from scipy import stats
from nfl_halves import load, HERE
G=load(); h1=pd.read_csv(os.path.join(HERE,'flow_1h_2015_2026.csv'))
h1['ypp']=h1.yards/h1.plays
key=h1.set_index(['game_id','posteam'])
def get(gid,team,col):
    try: return key.at[(gid,team),col]
    except KeyError: return np.nan
G['ypp_h']=[get(g,t,'ypp') for g,t in zip(G.game_id,G.home)]; G['ypp_a']=[get(g,t,'ypp') for g,t in zip(G.game_id,G.away)]
G['to_h']=[get(g,t,'giveaways') for g,t in zip(G.game_id,G.home)]; G['to_a']=[get(g,t,'giveaways') for g,t in zip(G.game_id,G.away)]
G=G.dropna(subset=['ypp_h','ypp_a']).copy(); G['edge']=G.ypp_h-G.ypp_a
def ols(y,Xcols,df):
    X=np.column_stack([df[c].values for c in Xcols]+[np.ones(len(df))]); b,res,rk,sv=la.lstsq(X,df[y].values,rcond=None)
    r=df[y].values-X@b; s2=r@r/(len(df)-X.shape[1]); cov=s2*la.inv(X.T@X); return b,np.sqrt(np.diag(cov)),X@b
def cover(df,side_sign,margin_col,exp_col,lab):
    exp=(df[exp_col]*side_sign); line=np.round(exp*2)/2      # proxy line the side must beat (its expected margin, to the half point)
    res=df[margin_col]*side_sign-line
    w=(res>0).sum(); l=(res<0).sum(); p=(res==0).sum()
    pv=stats.binomtest(int(w),int(w+l),0.5).pvalue if w+l else float('nan')
    print('  %-58s n %4d  %d-%d-%d  %.1f%%  (p vs 50%% = %.2f)  mean vs expectation %+.2f pts'%(lab,len(df),w,l,p,100*w/(w+l) if w+l else 0,pv,(df[margin_col]*side_sign-exp).mean()))
print('games with first-half play data:',len(G))
# ---------- A. halftime FLOW -> second half (DSB basis: 2H incl. OT) ----------
G['half_spread']=0.5*G.spread_line
b,se,G['exp2']=ols('m2ot',['spread_line','m1'],G)
print('\nA. SECOND HALF. Baseline: 2H+OT home margin = %.3f*spread %+.3f*halftime margin %+.2f'%tuple(b))
b2,se2,_=ols('m2ot',['spread_line','m1','edge'],G)
print('   adding the 1H yards-per-play edge: coefficient %+.3f per 1.0 YPP (se %.3f, t %+.2f)'%(b2[2],se2[2],b2[2]/se2[2]))
G['to_diff']=G.to_a-G.to_h
b3,se3,_=ols('m2ot',['spread_line','m1','edge','to_diff'],G)
print('   adding 1H giveaway margin too: YPP %+.3f (t %+.2f), giveaway margin %+.3f per turnover (t %+.2f)'%(b3[2],b3[2]/se3[2],b3[3],b3[3]/se3[3]))
s=np.sign(G.edge); lead=np.sign(G.m1)
flow=G[(G.edge.abs()>=1.5)&(lead==s)&(G.m1!=0)]; cover(flow,np.sign(flow.edge),'m2ot','exp2','FLOW side: YPP edge 1.5+ and leading (the 2H lean shape)')
f2=flow[flow.m1.abs()<17]; cover(f2,np.sign(f2.edge),'m2ot','exp2','  same, lead under 17 (blowout gate)')
f3=flow[flow.season>=2024]; cover(f3,np.sign(f3.edge),'m2ot','exp2','  same, 2024-26 only')
conf=G[(G.edge.abs()>=1.5)&(lead==-s)&(G.m1!=0)]; cover(conf,np.sign(conf.edge),'m2ot','exp2','YPP edge 1.5+ but TRAILING (FLOW CONFLICT)')
nof=G[(G.edge.abs()<1.5)&(G.m1!=0)]; cover(nof,np.sign(nof.m1),'m2ot','exp2','halftime leader, YPP edge under 1.5')
allL=G[G.m1!=0]; cover(allL,np.sign(allL.m1),'m2ot','exp2','every halftime leader')
# raw: leader vs half the pregame spread (old anchor: 0.50 x pregame spread)
cover(allL,np.sign(allL.m1),'m2ot','half_spread','every halftime leader vs 0.50 x pregame spread (Anchor)')
cover(flow,np.sign(flow.edge),'m2ot','half_spread','FLOW side vs 0.50 x pregame spread (Anchor)')
# ---------- B. previous game's 1H FLOW -> this game's first half ----------
T=[]
for _,r in G.iterrows():
    T.append((r.game_id,r.season,r.gameday,r.home,r.ypp_h-r.ypp_a,r.m1,r.to_a-r.to_h)); T.append((r.game_id,r.season,r.gameday,r.away,r.ypp_a-r.ypp_h,-r.m1,r.to_h-r.to_a))
T=pd.DataFrame(T,columns=['game_id','season','gameday','team','edge','m1','to_margin']).sort_values(['team','gameday'])
for c in ('edge','m1','to_margin'): T['prev_'+c]=T.groupby(['team','season'])[c].shift(1)
P=T.set_index(['game_id','team'])
G['pe_h']=[P.at[(g,t),'prev_edge'] for g,t in zip(G.game_id,G.home)]; G['pe_a']=[P.at[(g,t),'prev_edge'] for g,t in zip(G.game_id,G.away)]
G['pm_h']=[P.at[(g,t),'prev_m1'] for g,t in zip(G.game_id,G.home)]; G['pm_a']=[P.at[(g,t),'prev_m1'] for g,t in zip(G.game_id,G.away)]
B=G.dropna(subset=['pe_h','pe_a']).copy(); B['gap']=B.pe_h-B.pe_a; B['mgap']=B.pm_h-B.pm_a
bb,sb,B['exp1']=ols('m1',['spread_line'],B)
print('\nB. FIRST HALF. Baseline: 1H home margin = %.3f*spread %+.2f  (n %d, both teams have a previous game that season)'%(bb[0],bb[1],len(B)))
bb2,sb2,_=ols('m1',['spread_line','gap'],B)
print('   adding the previous-game 1H YPP gap: coefficient %+.3f per 1.0 YPP (se %.3f, t %+.2f)'%(bb2[1],sb2[1],bb2[1]/sb2[1]))
fl=B[(B.gap.abs()>=1.5)&(np.sign(B.mgap)==np.sign(B.gap))]; cover(fl,np.sign(fl.gap),'m1','exp1','FLOW side: prev-game 1H YPP gap 1.5+, margin same sign')
fl2=fl[fl.season>=2024]; cover(fl2,np.sign(fl2.gap),'m1','exp1','  same, 2024-26 only')
fl3=B[(B.gap.abs()>=3)&(np.sign(B.mgap)==np.sign(B.gap))]; cover(fl3,np.sign(fl3.gap),'m1','exp1','  gap 3.0+')
any_=B[B.gap!=0]; cover(any_,np.sign(any_.gap),'m1','exp1','side with any previous-game 1H YPP gap')
