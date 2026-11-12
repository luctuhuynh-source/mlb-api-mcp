#!/usr/bin/env python3
"""Robinhood (Kalshi) half-spread contracts against the books' fair at the 45 closing snapshots already on disk
(22 first-half closes, 8 books; 23 second-half closes, 4 books; 10/18 to 11/5/2026).
For each contract ("TEAM wins the half by over N.5"): the standing bid and ask at the snapshot minute (kalshi_quotes.csv),
the all-in price of each side (YES = ask + 2 cents, NO = 100 - bid + 2 cents), and the books' no-vig fair at that strike
(de-vig each book, convert to the strike with the one-sided table B-NFL-3, median). Edge = fair - all-in price, in points.
Venue rules applied (R-03): price of the side bought at most 60 cents, bid-ask spread at most 4 cents.
Second half: Robinhood settles on regulation, the books include overtime. 'ot_safe' marks contracts no overtime result can
change (the regulation-tie margin is more than 8 points from the strike). The others are shown apart and are approximate."""
import os, sys, json, statistics as st
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.join(HERE, '..', '..', 'review_2026-11-11')
sys.path.insert(0, REV)
from nfl_halves import load, favourite_view
D = load(); F, _ = favourite_view(D); N = len(F)
pm1 = (F.fm1.value_counts() / N).to_dict(); lay2 = (F.lay2ot.value_counts() / N).to_dict()
K = {'Arizona Cardinals':'ARI','Atlanta Falcons':'ATL','Baltimore Ravens':'BAL','Buffalo Bills':'BUF','Carolina Panthers':'CAR','Chicago Bears':'CHI','Cincinnati Bengals':'CIN','Cleveland Browns':'CLE','Dallas Cowboys':'DAL','Denver Broncos':'DEN','Detroit Lions':'DET','Green Bay Packers':'GB','Houston Texans':'HOU','Indianapolis Colts':'IND','Jacksonville Jaguars':'JAC','Kansas City Chiefs':'KC','Las Vegas Raiders':'LV','Los Angeles Chargers':'LAC','Los Angeles Rams':'LAR','Miami Dolphins':'MIA','Minnesota Vikings':'MIN','New England Patriots':'NE','New Orleans Saints':'NO','New York Giants':'NYG','New York Jets':'NYJ','Philadelphia Eagles':'PHI','Pittsburgh Steelers':'PIT','San Francisco 49ers':'SF','Seattle Seahawks':'SEA','Tampa Bay Buccaneers':'TB','Tennessee Titans':'TEN','Washington Commanders':'WAS'}
NV = {'JAC': 'JAX', 'LAR': 'LA'}
def imp(a): a = float(a); return (-a) / ((-a) + 100) if a < 0 else 100 / (a + 100)
def convert(q_i, s_i, s_b, pm):
    push_i = pm(-s_i) if float(s_i).is_integer() else 0.0
    W = q_i * (1 - push_i); lo, hi = sorted((-s_b, -s_i))
    mass = sum(pm(k) for k in range(int(np.floor(lo)) - 1, int(np.ceil(hi)) + 2) if lo < k <= hi)
    W_b = W + mass if s_b > s_i else W - mass
    push_b = pm(-s_b) if float(s_b).is_integer() else 0.0
    return W_b / (1 - push_b)
plan = pd.read_csv(os.path.join(HERE, 'pilot_plan.csv')); Q = pd.read_csv(os.path.join(HERE, 'kalshi_quotes.csv'))
Q['event'] = Q.ticker.str.rsplit('-', n=1).str[0]; Q['suffix'] = Q.ticker.str.rsplit('-', n=1).str[1]
G26 = D[D.season == 2026]
snaps = {}
for half, fn, mkey in [('1H', 'closes_1h_2026-10-18_to_11-05.json', 'spreads_h1'), ('2H', 'closes_2h_2026-10-18_to_11-05.json', 'spreads_h2')]:
    for v in json.load(open(os.path.join(REV, fn))).values():
        snaps[(half, K[v['away']], K[v['home']])] = (v, mkey)
rows, missing = [], []
for p in plan.itertuples():
    q = Q[(Q.event == p.event_ticker) & (Q.end_ts <= p.end_ts)]
    if q.empty: missing.append(p.event_ticker); continue
    v, mkey = snaps[(p.half, p.away, p.home)]
    books = []
    for b in v['books']:
        for m in b['markets']:
            if m['key'] != mkey: continue
            ho = [o for o in m['outcomes'] if o['name'] == v['home']][0]; ao = [o for o in m['outcomes'] if o['name'] == v['away']][0]
            books.append((float(ho['point']), float(ho['price']), float(ao['price'])))
    med = st.median([b[0] for b in books]); books = [b for b in books if abs(b[0] - med) < 3]
    g = G26[(G26.home == NV.get(p.home, p.home)) & (G26.away == NV.get(p.away, p.away))]
    g = g.iloc[(pd.to_datetime(g.gameday) - pd.Timestamp(p.snapshot[:10])).abs().argsort()[:1]]
    m1_home = float(g.m1.iloc[0])
    for tk, c in q.groupby('ticker'):
        c = c.sort_values('end_ts').iloc[-1]; suf = c.suffix
        team = ''.join(ch for ch in suf if ch.isalpha()); strike = float(c.floor_strike)
        if team not in (p.home, p.away) or pd.isna(c.yes_ask) or pd.isna(c.yes_bid): continue
        is_home = team == p.home; s = -strike                                  # team lays the strike
        tlines = [(b[0] if is_home else -b[0]) for b in books]; tmed = st.median(tlines)
        dist = pm1 if p.half == '1H' else lay2
        if tmed < 0: pm = lambda k: dist.get(k, 0.0)
        elif tmed > 0: pm = lambda k: dist.get(-k, 0.0)
        else: pm = lambda k: (dist.get(k, 0.0) + dist.get(-k, 0.0)) / 2
        conv = []
        for hp, hpr, apr in books:
            io, ip = (imp(hpr), imp(apr)) if is_home else (imp(apr), imp(hpr))
            conv.append(convert(io / (io + ip), hp if is_home else -hp, s, pm))
        fair_yes = 100 * st.median(conv); spread = c.yes_ask - c.yes_bid
        m1_team = m1_home if is_home else -m1_home
        ot_safe = (p.half == '1H') or abs((-m1_team) - strike) > 8
        for side, price, fair in [('YES', c.yes_ask, fair_yes), ('NO', 100 - c.yes_bid, 100 - fair_yes)]:
            won = (c.result == 'yes') if side == 'YES' else (c.result == 'no')
            rows.append(dict(half=p.half, game=p.away + '@' + p.home, contract=suf, side=side, strike=strike, dist_from_books=round(abs(-strike - tmed), 1),
                             price=price, all_in=price + 2, fair=round(fair, 1), edge=round(fair - price - 2, 1), ba_spread=spread,
                             passes_venue=bool(price <= 60 and spread <= 4 and c.yes_ask > 0), ot_safe=bool(ot_safe), fair_range=round(100 * (max(conv) - min(conv)), 1), won=bool(won)))
R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, 'robinhood_vs_fair.csv'), index=False)
print('events asked %d, with quotes %d, missing %s' % (len(plan), plan.event_ticker.isin(Q.event).sum(), missing))
print('contract-sides priced: %d (%d contracts)' % (len(R), len(R) // 2))
def block(lab, X):
    X = X[X.passes_venue]
    if X.empty: print('--- %s: nothing passes the venue rules' % lab); return
    print('--- %s: %d contract-sides pass the venue rules, in %d games ---' % (lab, len(X), X.game.nunique()))
    print('   all-in price against fair: mean %+.1f, median %+.1f, best %+.1f (edge; minus = worse than fair)' % (X.edge.mean(), X.edge.median(), X.edge.max()))
    for name, lo, hi in [('3.0 or more', 3, 99), ('2.0 to 2.9', 2, 3), ('1.0 to 1.9', 1, 2), ('0 to 0.9', 0, 1), ('0 to 2 worse', -2, 0), ('2 to 4 worse', -4, -2), ('more than 4 worse', -99, -4)]:
        x = X[(X.edge >= lo) & (X.edge < hi)]
        print('   %-18s %3d sides in %2d games%s' % (name, len(x), x.game.nunique(), ('   went %d-%d' % (x.won.sum(), (~x.won).sum())) if lo >= 1 and len(x) else ''))
near = R[R.dist_from_books <= 3.5]
block('FIRST HALF, strikes within 3.5 points of the books', near[near.half == '1H'])
block('SECOND HALF, overtime cannot matter, strikes within 3.5', near[(near.half == '2H') & near.ot_safe])
block('SECOND HALF, overtime could matter (approximate), strikes within 3.5', near[(near.half == '2H') & ~near.ot_safe])
block('ALL strikes, both halves', R)
pd.set_option('display.width', 220)
top = R[R.passes_venue].sort_values('edge', ascending=False).head(15)
print('--- best 15 contract-sides ---'); print(top[['half', 'game', 'contract', 'side', 'price', 'all_in', 'fair', 'edge', 'dist_from_books', 'fair_range', 'ot_safe', 'won']].to_string(index=False))
print('bid-ask spread: median %.0f cents; share of contracts with spread 4 or less: %.0f%%' % (R[R.side == 'YES'].ba_spread.median(), 100 * (R[R.side == 'YES'].ba_spread <= 4).mean()))
