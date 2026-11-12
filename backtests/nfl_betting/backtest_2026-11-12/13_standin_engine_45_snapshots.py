#!/usr/bin/env python3
"""Stand-in engine test on the 45 closing snapshots already on disk (22 first-half closes with 8 books, 23 second-half closes
with 4 books, 10/18 to 11/5/2026). DSB and Red105 are not in any feed, so each feed book takes a turn as "the venue":
its line and price are tested against the fair made from the OTHER books (de-vig each, convert to the venue's number with
the one-sided table B-NFL-3, take the median). Edge = fair win probability at the venue's number minus the price's break-even,
the same sum the engine does for a direct gap (F-28 / H-19). The bet is then graded on the half's result.
This shows (1) how often a real book hangs a price 3.0+ or 2.0-2.9 points better than the rest at the close,
(2) whether those prices won, (3) what the 'books disagree' block does to them. The sample is 45 games: a first look, not proof."""
import os, sys, json, statistics as st, collections
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.join(HERE, '..', 'review_2026-11-11')
sys.path.insert(0, REV)
from nfl_halves import load, favourite_view
D = load(); F, _ = favourite_view(D); N = len(F)
pm1 = (F.fm1.value_counts() / N).to_dict(); lay2 = (F.lay2ot.value_counts() / N).to_dict()
ABBR = {'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL', 'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
        'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL', 'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
        'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX', 'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV',
        'Los Angeles Chargers': 'LAC', 'Los Angeles Rams': 'LA', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN', 'New England Patriots': 'NE',
        'New Orleans Saints': 'NO', 'New York Giants': 'NYG', 'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
        'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB', 'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS'}
G26 = D[D.season == 2026]
def imp(a): a = float(a); return (-a) / ((-a) + 100) if a < 0 else 100 / (a + 100)
def convert(q_i, s_i, s_b, pm):
    push_i = pm(-s_i) if float(s_i).is_integer() else 0.0
    W = q_i * (1 - push_i); lo, hi = sorted((-s_b, -s_i))
    mass = sum(pm(k) for k in range(int(np.floor(lo)) - 1, int(np.ceil(hi)) + 2) if lo < k <= hi)
    W_b = W + mass if s_b > s_i else W - mass
    push_b = pm(-s_b) if float(s_b).is_integer() else 0.0
    return W_b / (1 - push_b), push_b
rows = []
for half, fn, mkey in [('1H', 'closes_1h_2026-10-18_to_11-05.json', 'spreads_h1'), ('2H', 'closes_2h_2026-10-18_to_11-05.json', 'spreads_h2')]:
    for snap in json.load(open(os.path.join(REV, fn))).values():
        h, a = ABBR[snap['home']], ABBR[snap['away']]
        g = G26[(G26.home == h) & (G26.away == a)]
        g = g.iloc[(pd.to_datetime(g.gameday) - pd.Timestamp(snap['commence_time'][:10])).abs().argsort()[:1]]
        hm = float(g.m1.iloc[0]) if half == '1H' else float(g.m2ot.iloc[0])      # home margin in that half (2H incl. OT)
        quotes = []
        for b in snap['books']:
            for m in b['markets']:
                if m['key'] != mkey: continue
                ho = [o for o in m['outcomes'] if o['name'] == snap['home']][0]; ao = [o for o in m['outcomes'] if o['name'] == snap['away']][0]
                age = (pd.Timestamp(snap['snapshot_timestamp']) - pd.Timestamp(b['last_update'])).total_seconds()
                quotes.append(dict(book=b['key'], hp=float(ho['point']), hprice=float(ho['price']), aprice=float(ao['price']), age=age))
        med = st.median([q['hp'] for q in quotes]); quotes = [q for q in quotes if abs(q['hp'] - med) < 3]
        for v in quotes:
            others = [q for q in quotes if q['book'] != v['book']]
            if len(others) < 3: continue
            for side in ('home', 'away'):
                s = v['hp'] if side == 'home' else -v['hp']; price = v['hprice'] if side == 'home' else v['aprice']
                omed = st.median([(q['hp'] if side == 'home' else -q['hp']) for q in others])
                dist = pm1 if half == '1H' else lay2
                if omed < 0: pm = lambda k: dist.get(k, 0.0)
                elif omed > 0: pm = lambda k: dist.get(-k, 0.0)
                else: pm = lambda k: (dist.get(k, 0.0) + dist.get(-k, 0.0)) / 2
                conv = []
                for q in others:
                    io, ip = (imp(q['hprice']), imp(q['aprice'])) if side == 'home' else (imp(q['aprice']), imp(q['hprice']))
                    c, push = convert(io / (io + ip), q['hp'] if side == 'home' else -q['hp'], s, pm); conv.append(c)
                fair = st.median(conv); be = imp(price); edge = fair - be
                b_ = (100 / -price) if price < 0 else price / 100
                ev = b_ * fair * (1 - push) - (1 - fair) * (1 - push)
                opts = [(q['hp'] if side == 'home' else -q['hp']) for q in others]
                mar = (hm if side == 'home' else -hm) + s
                rows.append(dict(half=half, game=a + '@' + h, book=v['book'], side=h if side == 'home' else a, line=s, price=price, fair=fair, edge=100 * edge, ev=ev,
                                 others=len(others), num_range=max(opts) - min(opts), fair_range=100 * (max(conv) - min(conv)),
                                 strictly_best=all(s > x for x in opts), age=v['age'], res='W' if mar > 0 else ('L' if mar < 0 else 'P')))
R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, 'standin_engine_45_snapshots.csv'), index=False)
def rec(g):
    return '%d-%d-%d' % ((g.res == 'W').sum(), (g.res == 'L').sum(), (g.res == 'P').sum())
def uniq(g):   # one entry per game and side: the best-edge book
    return g.sort_values('edge', ascending=False).drop_duplicates(['half', 'game', 'side'])
print('book-side prices tested: %d (1H %d over %d games, 2H %d over %d games)' % (len(R), (R.half == '1H').sum(), R[R.half == '1H'].game.nunique(), (R.half == '2H').sum(), R[R.half == '2H'].game.nunique()))
print('edge of a book-side price against the other books: mean %+.2f, sd %.2f (1H: %+.2f, sd %.2f | 2H: %+.2f, sd %.2f)' % (
    R.edge.mean(), R.edge.std(), R[R.half == '1H'].edge.mean(), R[R.half == '1H'].edge.std(), R[R.half == '2H'].edge.mean(), R[R.half == '2H'].edge.std()))
print()
for half in ('1H', '2H', 'both'):
    X = R if half == 'both' else R[R.half == half]
    print('--- %s ---' % half)
    for lab, lo, hi in [('3.0 or more', 3.0, 99), ('2.0 to 2.9', 2.0, 3.0), ('1.0 to 1.9', 1.0, 2.0), ('0 to 0.9', 0.0, 1.0), ('below 0', -99, 0.0)]:
        g = X[(X.edge >= lo) & (X.edge < hi) & ((X.ev > 0) | (lo < 0))]; u = uniq(g)
        print('  edge %-12s book-sides %3d (%4.1f%% of all) | distinct game-sides %2d in %2d games | result per game-side %s | mean edge %+.1f' % (
            lab, len(g), 100 * len(g) / len(X), len(u), u.game.nunique(), rec(u), g.edge.mean() if len(g) else float('nan')))
print()
print('--- the 3.0+ prices, one line each ---')
pd.set_option('display.width', 250)
top = R[(R.edge >= 3.0) & (R.ev > 0)].sort_values(['half', 'game', 'edge'], ascending=[True, True, False])
print(top[['half', 'game', 'book', 'side', 'line', 'price', 'edge', 'num_range', 'fair_range', 'strictly_best', 'age', 'res']].round(1).to_string(index=False))
print()
print('--- what the "books disagree" block does (prices 2.0 or more better than the rest, one per game-side) ---')
u = uniq(R[(R.edge >= 2.0) & (R.ev > 0)])
for half in ('1H', '2H'):
    x = u[u.half == half]
    print('  %s: %d game-sides. Other books more than half a point apart (blocked today): %d, went %s | within half a point (allowed today): %d, went %s' % (
        half, len(x), (x.num_range > 0.5).sum(), rec(x[x.num_range > 0.5]), (x.num_range <= 0.5).sum(), rec(x[x.num_range <= 0.5])))
    print('      measured on price instead, other books more than 3 points apart (blocked): %d, went %s | within 3 points (allowed): %d, went %s' % (
        (x.fair_range > 3).sum(), rec(x[x.fair_range > 3]), (x.fair_range <= 3).sum(), rec(x[x.fair_range <= 3])))
print()
print('--- who hangs the outlier prices (2.0+ better than the rest) ---')
print(R[(R.edge >= 2.0) & (R.ev > 0)].groupby(['half', 'book']).size().to_string())
print()
print('--- age of the quote behind a 2.0+ price vs all quotes (seconds since the book last updated) ---')
print('  2.0+ prices: median %.0f s | all quotes: median %.0f s' % (R[(R.edge >= 2.0)].age.median(), R.age.median()))
