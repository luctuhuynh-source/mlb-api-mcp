#!/usr/bin/env python3
"""Closing-line value for every 1H lean and fire (and the one full-game lean) in the rebuilt ledger, 10/18 to 11/5/2026.
Close = the Odds API historical snapshot just before kickoff (closes_1h_2026-10-18_to_11-05.json, 8 US books, DSB not among them).
Per book: de-vig (proportional), convert to the bet's number with the one-sided table (B-NFL-3), take the median across books.
CLV (Liem L1.1) = closing implied probability minus fill implied probability on the same side and number.
'CLV minus margin' = closing no-vig fair minus fill implied probability: the part that is real edge."""
import os, json, csv, statistics as st, collections
import pandas as pd, numpy as np
from nfl_halves import load, favourite_view, HERE
H, _ = favourite_view(load())
N = len(H)
pm1 = (H.fm1.value_counts()/N).to_dict()          # P(favourite 1H margin = k)
closes = json.load(open(os.path.join(HERE, 'closes_1h_2026-10-18_to_11-05.json')))
def imp(a): a=float(a); return (-a)/((-a)+100) if a<0 else 100/(a+100)
def find(away_kw, home_kw, market):
    for k,d in closes.items():
        if away_kw in d['away'] and home_kw in d['home'] and market in d['consensus']:
            return d
    raise KeyError((away_kw,home_kw,market))
# id, date, class, away kw, home kw, our team kw, our line, fill prob (from price), market, version, run basis
def P(american): return imp(american)
ROWS = [
 ('R01','10/18','1H lean','Texans','Jaguars','Texans',+0.5,P(+103),'spreads_h1'),
 ('R02','10/18','1H lean','Jets','Patriots','Patriots',-4,P(-100),'spreads_h1'),
 ('R03','10/18','1H lean','Titans','Colts','Colts',-4,P(-103),'spreads_h1'),
 ('R04','10/18','1H lean','Cardinals','Rams','Rams',-7,P(+102),'spreads_h1'),
 ('R05','10/18','1H lean','Bills','Raiders','Bills',-3.5,P(-105),'spreads_h1'),
 ('R06','10/18','1H lean','Chargers','Chiefs','Chiefs',-4,P(-110),'spreads_h1'),
 ('R17','10/19','1H lean','Commanders','49ers','49ers',-4,P(-115),'spreads_h1'),
 ('R18','10/22','1H lean','Patriots','Bears','Bears',-2.5,P(-110),'spreads_h1'),
 ('R19','10/22','FG lean','Patriots','Bears','Bears',-3,P(-105),'spreads'),
 ('R21','10/25','1H lean','49ers','Falcons','49ers',-0.5,P(-100),'spreads_h1'),
 ('R22','10/25','1H lean','Colts','Vikings','Vikings',-4,P(-105),'spreads_h1'),
 ('R23','10/25','1H lean','Dolphins','Jets','Jets',-2.5,P(-115),'spreads_h1'),
 ('R24','10/25','1H lean','Bengals','Ravens','Bengals',-1,P(-105),'spreads_h1'),
 ('R25','10/25','1H lean','Giants','Texans','Texans',-6.5,P(-105),'spreads_h1'),
 ('R26','10/25','1H lean','Broncos','Cardinals','Broncos',-3,P(-100),'spreads_h1'),
 ('R27','10/25','1H lean','Packers','Lions','Lions',-3,P(-100),'spreads_h1'),
 ('R28','10/25','1H lean','Chiefs','Seahawks','Chiefs',+2.5,P(-105),'spreads_h1'),
 ('R34','10/26','1H lean','Cowboys','Eagles','Cowboys',-2.5,P(-110),'spreads_h1'),
 ('R36','10/29','1H lean','Panthers','Packers','Packers',-2.5,P(-110),'spreads_h1'),
 ('R37','11/1','1H lean','Browns','Steelers','Browns',+2.5,P(-100),'spreads_h1'),
 ('R38','11/1','1H lean','Patriots','Dolphins','Dolphins',+3.5,P(-100),'spreads_h1'),
 ('R45','11/2','1H engine fire','Bears','Seahawks','Bears',+2.5,P(+110),'spreads_h1'),
 ('R47','11/5','1H lean','Jaguars','Ravens','Jaguars',-4.5,0.54,'spreads_h1'),
]
led = {r['id']:r for r in csv.DictReader(open(os.path.join(HERE, '..', 'ledger_rebuilt_2026-10-18_to_11-05.csv')))}
def pmfM(our_is_fav):
    return (lambda k: pm1.get(k,0.0)) if our_is_fav else (lambda k: pm1.get(-k,0.0))
def convert(q_i, s_i, s_b, pm):
    """q_i = no-vig win prob (given no push) at our line s_i -> same at our line s_b. M = our margin; win iff M + s > 0."""
    push_i = pm(-s_i) if float(s_i).is_integer() else 0.0
    W = q_i*(1-push_i)                       # P(M > -s_i)
    lo, hi = sorted((-s_b, -s_i))
    ks = [k for k in range(int(np.floor(lo))-1, int(np.ceil(hi))+2) if lo < k <= hi]
    mass = sum(pm(k) for k in ks)
    W_b = W + mass if s_b > s_i else W - mass  # more points for us -> more ways to win
    push_b = pm(-s_b) if float(s_b).is_integer() else 0.0
    return W_b/(1-push_b)
out=[]
for rid,date,cls,akw,hkw,team,line,fill,market in ROWS:
    d = find(akw,hkw,market)
    books=[]
    for b in d['books']:
        for m in b['markets']:
            if m['key']!=market: continue
            ours=[o for o in m['outcomes'] if team in o['name']][0]; opp=[o for o in m['outcomes'] if team not in o['name']][0]
            books.append((b['key'], float(ours['point']), float(ours['price']), float(opp['price'])))
    med = st.median([b[1] for b in books])
    books=[b for b in books if abs(b[1]-med)<3]
    modal = collections.Counter([b[1] for b in books]).most_common(1)[0][0]
    our_is_fav = med < 0
    if market=='spreads':   # full game: same number at every book here, no conversion needed
        pm = lambda k: 0.0
    else:
        pm = pmfM(our_is_fav)
    conv=[]; margins=[]; same=[]
    for key,pt,po,pp in books:
        io,ip = imp(po),imp(pp); q = io/(io+ip); margins.append(io-q)
        conv.append(convert(q,pt,line,pm))
        if pt==line: same.append(q)
    fair = st.median(conv); margin = st.mean(margins)
    clv_net = fair - fill; clv = clv_net + margin
    line_move = line - modal     # + = our number is better than the closing modal number
    r = led[rid]
    out.append(dict(id=rid,date=date,cls=cls,game=r['game'],pick=r['pick'],fill_prob=round(fill,4),
        close_snapshot=d['snapshot_timestamp'],books=len(books),close_modal_our_line=modal,line_move_pts=line_move,
        books_at_our_number=len(same), fair_same_number=(round(st.median(same),4) if same else ''),
        close_fair_at_our_number=round(fair,4), per_side_margin=round(margin,4),
        clv_prob=round(clv,4), clv_minus_margin=round(clv_net,4), beat_close=int(clv>0), result=r['result']))
df = pd.DataFrame(out)
df.to_csv(os.path.join(HERE, '..', 'clv_1h_2026-10-18_to_11-05.csv'),index=False)
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(df[['id','date','pick','fill_prob','close_modal_our_line','line_move_pts','books_at_our_number','fair_same_number','close_fair_at_our_number','clv_prob','clv_minus_margin','beat_close','result']].to_string(index=False))
h1 = df[df.cls!='FG lean']
def line(s,lab):
    n=len(s); bc=s.beat_close.mean(); m=s.clv_prob.mean(); mn=s.clv_minus_margin.mean(); sd=s.clv_minus_margin.std(ddof=1) if n>1 else float('nan')
    z = mn/(sd/np.sqrt(n)) if n>1 and sd>0 else float('nan')
    print('%-34s n %2d | beat close %2d/%2d (%.0f%%) | mean CLV %+.2f | mean CLV - margin %+.2f (sd %.2f, z %+.2f) | W-L-P %d-%d-%d | line moved for us %d, against %d, flat %d'%(lab,n,s.beat_close.sum(),n,100*bc,100*m,100*mn,100*sd,z,(s.result=='W').sum(),(s.result=='L').sum(),(s.result=='P').sum(),(s.line_move_pts>0).sum(),(s.line_move_pts<0).sum(),(s.line_move_pts==0).sum()))
print()
line(h1,'ALL 1H leans + 1H fire')
line(h1[h1.cls=='1H lean'],'1H leans only')
struct = ['R17','R21','R22','R23','R24','R25','R26','R27']
text = ['R34','R36','R47']
line(h1[h1.id.isin(struct)],'structural-input boards (10/19,10/25)')
line(h1[(h1.cls=='1H lean')&~h1.id.isin(struct)],'other 1H leans')
line(h1[h1.id.isin(text)],'from-written-text 1H boards')
line(h1[(h1.cls=='1H lean')&~h1.id.isin(text)],'from memory / notes 1H leans')
line(h1[h1.date.isin(['10/18','10/19','10/22','10/25','10/26','10/29'])],'v0.6 + 10/17 addenda (10/18-10/29)')
line(h1[h1.date.isin(['11/1','11/2','11/5'])],'v0.6a (11/1-11/5) incl. fire')
line(h1[h1.result=='W'],'winners'); line(h1[h1.result=='L'],'losers')
print('corr(clv_minus_margin, win) =', round(np.corrcoef(h1[h1.result!='P'].clv_minus_margin, (h1[h1.result!='P'].result=='W').astype(int))[0,1],3))
