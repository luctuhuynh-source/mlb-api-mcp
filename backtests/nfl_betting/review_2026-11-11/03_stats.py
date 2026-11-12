#!/usr/bin/env python3
"""Significance blocks (Liem L3.1) on the rebuilt ledger, version and run-basis comparisons, and the 2H leans split by halftime state.
Needs scipy. Counts for days outside 10/18-11/5 are from the running log (see ../LEDGER_REBUILT.md section 3)."""
import os, csv, re, math, numpy as np, pandas as pd
from scipy import stats
from nfl_halves import load, HERE
L = list(csv.DictReader(open(os.path.join(HERE, '..', 'ledger_rebuilt_2026-10-18_to_11-05.csv'))))
def imp(a): a=float(a); return (-a)/((-a)+100) if a<0 else 100/(a+100)
def fill(vp):
    m=re.search(r'([+-]\d+)\s*$',vp)
    if m: return imp(m.group(1))
    m=re.search(r'(\d+)c',vp)
    if m: return (int(m.group(1))+2)/100
    return None
for r in L: r['fp']=fill(r['venue_price'])
def block(rows,lab,exp_margin=0.0238):
    rows=[r for r in rows if r['fp'] and r['result'] in 'WLP']
    n=len(rows); W=sum(r['result']=='W' for r in rows); Lo=sum(r['result']=='L' for r in rows); Pu=n-W-Lo
    risk=[r['fp']/(1-r['fp']) for r in rows]        # risk per 1 unit to win
    prof=[1 if r['result']=='W' else (-k if r['result']=='L' else 0) for r,k in zip(rows,risk)]
    tot_risk=sum(risk); y=sum(prof)/tot_risk
    o=np.mean([1/r['fp'] for r in rows])             # mean decimal odds
    rr=1-exp_margin; se=math.sqrt(rr*(o-rr)/n); z=(y-(-exp_margin))/se; p=1-stats.norm.cdf(z)
    need=(3.09*math.sqrt(rr*(o-rr))/(y+exp_margin))**2 if y+exp_margin>0 else float('inf')
    # monkey null: same tickets, each wins with fill prob less half the 10-cent overround
    rng=np.random.default_rng(7); sims=[]
    pw=np.array([r['fp']-0.012 for r in rows]); rk=np.array(risk)
    for _ in range(20000):
        w=rng.random(n)<pw; sims.append((w.sum()-(rk[~w]).sum()))
    pct=100*(np.array(sims)<sum(prof)).mean()
    print('%-28s n %2d  %d-%d-%d  units %+.2f  yield %+.1f%%  expected %.1f%%  mean odds %.3f  SE %.1f%%  z %+.2f  p %.3f  n to reach p=0.001 at this yield: %s  monkey percentile %.0f'%(lab,n,W,Lo,Pu,sum(prof),100*y,-100*exp_margin,o,100*se,z,p,('%d'%round(need) if need<1e6 else 'never'),pct))
print('== L3.1 blocks, rebuilt ledger 10/18-11/5 (flat $300-to-win units) ==')
block([r for r in L if r['class']=='1H lean'],'1H leans')
block([r for r in L if r['class']=='2H lean'],'2H leans')
block([r for r in L if r['class'] in('1H lean','2H lean','FG lean')],'all leans')
block([r for r in L if 'fire' in r['class']],'engine fires')
# since 10/11 totals (log-only days added as counts)
print('\n== binomial, since 10/11 (pushes dropped) ==')
for lab,w,l in (('1H leans',18,11),('2H leans',19,17),('all leans',37,28),('v0.5 leans 10/11-10/12',15,6),('filter-era leans 10/15-11/9',22,22),('doc read before the board (10/11 slate + 5 later boards)',19,6),('every other board since 10/11',18,22)):
    p=stats.binomtest(w,w+l,0.5,alternative='greater').pvalue
    lo,hi=stats.binomtest(w,w+l).proportion_ci(0.95)
    print('  %-58s %d-%d  %.1f%%  95%% CI %.0f-%.0f%%  p(one-sided vs 50%%) %.3f'%(lab,w,l,100*w/(w+l),100*lo,100*hi,p))
print('\n== Fisher exact (two-sided) ==')
for lab,a,b,c,d in (('v0.5 (15-6) vs filter era (22-22)',15,6,22,22),('doc read (19-6) vs every other board (18-22)',19,6,18,22),('1H v0.5 (6-2) vs later (12-9)',6,2,12,9),('2H v0.5 (9-4) vs later (10-13)',9,4,10,13),('v0.6 (15-18) vs v0.6a (7-3)',15,18,7,3)):
    print('  %-44s p = %.3f'%(lab,stats.fisher_exact([[a,b],[c,d]])[1]))
# 2H leans by halftime state (nflverse halftime scores)
H=load(); H=H[H.season==2026]
abbr={'TEN@IND':'TEN_IND','BAL@CLE':'BAL_CLE','NYJ@NE':'NYJ_NE','NO@NYG':'NO_NYG','CHI@ATL':'CHI_ATL','CAR@PHI':'CAR_PHI','BUF@LV':'BUF_LV','LAC@KC':'LAC_KC','ARI@LAR':'ARI_LA','NE@CHI':'NE_CHI','CLE@TEN':'CLE_TEN','NYG@HOU':'NYG_HOU','DEN@ARI':'DEN_ARI','GB@DET':'GB_DET','DAL@PHI':'DAL_PHI','LV@NYJ':'LV_NYJ','CLE@PIT':'CLE_PIT','NE@MIA':'NE_MIA','KC@DEN':'KC_DEN','PHI@WAS':'PHI_WAS','LAC@LAR':'LAC_LA','CHI@SEA':'CHI_SEA','JAX@BAL':'JAX_BAL'}
out=[]
for r in L:
    if not r['class'].startswith('2H'): continue
    g=H[H.game_id.str.endswith('_'+abbr[r['game']])]
    mm,dd=r['date'].split('/'); g=g[g.gameday>= '2026-%02d-%02d'%(int(mm),int(dd)-1)].iloc[0]
    away,home=r['game'].split('@'); team=r['pick'].split()[0]
    hm=g.h1_home-g.h1_away
    tm = hm if team==home else (-hm if team==away else None)
    m=re.search(r'([+-]\d+(\.\d+)?|PK)',r['pick']); line=0.0 if (m and m.group(1)=='PK') else (float(m.group(1)) if m else None)
    state = None if tm is None else ('leader' if tm>0 else ('trailer' if tm<0 else 'tied'))
    out.append((r['id'],r['date'],r['class'],r['game'],r['pick'],'%d-%d'%(g.h1_away,g.h1_home),tm,state,line,r['result']))
D=pd.DataFrame(out,columns=['id','date','class','game','pick','half_away_home','our_halftime_margin','state','line','result'])
print('\n== 2H entries by halftime state ==')
print(D.to_string(index=False))
le=D[D['class']=='2H lean']
for s in ('leader','trailer','tied'):
    x=le[le.state==s]; print('  2H leans on the halftime %-7s: %d-%d-%d'%(s,(x.result=='W').sum(),(x.result=='L').sum(),(x.result=='P').sum()))
lay=le[le.line<0]; take=le[le.line>0]; pk=le[le.line==0]
print('  2H leans laying points: %d-%d-%d ; taking points: %d-%d-%d ; pick: %d-%d-%d'%((lay.result=='W').sum(),(lay.result=='L').sum(),(lay.result=='P').sum(),(take.result=='W').sum(),(take.result=='L').sum(),(take.result=='P').sum(),(pk.result=='W').sum(),(pk.result=='L').sum(),(pk.result=='P').sum()))
ll=le[(le.state=='leader')&(le.line<0)]; print('  leader laying points: %d-%d-%d'%((ll.result=='W').sum(),(ll.result=='L').sum(),(ll.result=='P').sum()))
D.to_csv(os.path.join(HERE,'2h_entries_by_halftime_state.csv'),index=False)
