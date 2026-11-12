#!/usr/bin/env python3
"""Grades claims C5 and C6 of TEST_PLAN_LOCKED.md: the engine's premise, tested on the big books at halftime, 2023 to 11/9/2026.
Each book takes a turn as "the venue". Its second-half line and price are tested against the fair made from the OTHER fresh
books at the same look: vig removed, moved to the venue's number with the one-sided table B-NFL-3 for spreads (same number only
for totals), median, two or more other books needed. Edge = fair win probability at the venue's number minus the break-even of
its price (the engine's own sum, F-28 / H-19). One entry per game, market and side: the book with the largest edge.
  C5: edge 3.0 or more.   C6: edge 2.0 to 2.9.
Cleaning as in the plan: main line only (both prices between -200 and +200); fresh (last update at or after the last first-half
play); decision look = look 1 when 2+ books pass, else look 2; graded at that book's number and price, sportsbook settlement
(second half includes overtime, tie refunded); stake to win $300; one price step worse = break-even + 1.0 point.
Usage: python3 25_grade_engine_claims.py"""
import os, sys, statistics as st, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.join(HERE, '..', '..', 'review_2026-11-11')
sys.path.insert(0, REV)
from nfl_halves import load, favourite_view
D = load(); F, _ = favourite_view(D); N = len(F); lay2 = (F.lay2ot.value_counts() / N).to_dict()
clock = pd.read_csv(os.path.join(HERE, 'halftime_clock_2023_2026.csv')); clock = clock[clock.ok == 1]
T = clock[['game_id', 'season', 'last_1h_play_utc', 'look1', 'look2']].merge(D[['game_id', 'week', 'h1_home', 'h1_away', 'fin_home', 'fin_away', 'm2ot']], on='game_id', how='left')
T['pts2'] = T.fin_home + T.fin_away - T.h1_home - T.h1_away; T['per'] = np.where(T.season <= 2024, '2023-24', '2025-26'); T['wk'] = T.season.astype(str) + '_' + T.week.astype(str)
def imp(a): a = float(a); return (-a) / ((-a) + 100) if a < 0 else 100 / (a + 100)
def convert(q_i, s_i, s_b, pm):
    push_i = pm(-s_i) if float(s_i).is_integer() else 0.0
    W = q_i * (1 - push_i); lo, hi = sorted((-s_b, -s_i))
    mass = sum(pm(k) for k in range(int(np.floor(lo)) - 1, int(np.ceil(hi)) + 2) if lo < k <= hi)
    W_b = W + mass if s_b > s_i else W - mass
    push_b = pm(-s_b) if float(s_b).is_integer() else 0.0
    return W_b / (1 - push_b)
Q = pd.read_csv(os.path.join(HERE, 'pulled_pull_plan.csv.gz'))
for c in ('point', 'price_a', 'price_b', 'age'): Q[c] = pd.to_numeric(Q[c], errors='coerce')
Q = Q.merge(T, on='game_id', how='inner')
Q['main'] = Q.price_a.between(-200, 200) & Q.price_b.between(-200, 200) & Q.point.notna()
Q['fresh'] = Q.age.notna() & ((pd.to_datetime(Q.ts, utc=True) - pd.to_timedelta(Q.age, unit='s')) >= pd.to_datetime(Q.last_1h_play_utc, utc=True))
Q['look'] = np.where(Q.asked == Q.look1, 1, np.where(Q.asked == Q.look2, 2, 0))
OK = Q[Q.main & Q.fresh & (Q.look > 0)]
rows = []
for (gid, mk), g in OK.groupby(['game_id', 'market']):
    n1, n2 = g[g.look == 1].book.nunique(), g[g.look == 2].book.nunique()
    pick = 1 if n1 >= 2 else (2 if n2 >= 2 else 0)
    if pick == 0: continue
    t = g.iloc[0]
    for lk in (1, 2):
        x = g[g.look == lk]
        if x.book.nunique() < 3: continue                         # a venue needs two or more other books
        for v in x.itertuples():
            others = x[x.book != v.book]
            for side in ('a', 'b'):                               # a = home (spread) or Over (total); b = away or Under
                price = v.price_a if side == 'a' else v.price_b
                if mk == 'spreads_h2':
                    s = v.point if side == 'a' else -v.point
                    olines = [(o.point if side == 'a' else -o.point) for o in others.itertuples()]; omed = st.median(olines)
                    if omed < 0: pm = lambda k: lay2.get(k, 0.0)
                    elif omed > 0: pm = lambda k: lay2.get(-k, 0.0)
                    else: pm = lambda k: (lay2.get(k, 0.0) + lay2.get(-k, 0.0)) / 2
                    conv = []
                    for o in others.itertuples():
                        io, ip = (imp(o.price_a), imp(o.price_b)) if side == 'a' else (imp(o.price_b), imp(o.price_a))
                        conv.append(convert(io / (io + ip), o.point if side == 'a' else -o.point, s, pm))
                    if len(conv) < 2: continue
                    mar = (t.m2ot if side == 'a' else -t.m2ot) + s; num_range = max(olines) - min(olines)
                else:
                    same = others[others.point == v.point]
                    if len(same) < 2: continue
                    conv = [(imp(o.price_a) if side == 'a' else imp(o.price_b)) / (imp(o.price_a) + imp(o.price_b)) for o in same.itertuples()]
                    mar = (t.pts2 - v.point) if side == 'a' else (v.point - t.pts2); num_range = others.point.max() - others.point.min()
                fair = st.median(conv); edge = 100 * (fair - imp(price))
                rows.append(dict(game_id=gid, market=mk, look=lk, decision=int(lk == pick), book=v.book, side=side, line=v.point, price=price, fair=100 * fair, edge=edge, others=len(conv),
                                 num_range=num_range, fair_range=100 * (max(conv) - min(conv)), age=v.age, res=float(np.sign(mar)), per=t.per, wk=t.wk, season=t.season))
R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, 'engine_standin_2023_2026.csv.gz'), index=False)
Dn = R[R.decision == 1]
print('games with a decision look and 3+ books: spreads %d, totals %d (of %d)' % (Dn[Dn.market == 'spreads_h2'].game_id.nunique(), Dn[Dn.market == 'totals_h2'].game_id.nunique(), len(T)))
print('book-side prices tested at the decision look: %d | mean edge %+.2f (spreads %+.2f, totals %+.2f)' % (len(Dn), Dn.edge.mean(), Dn[Dn.market == 'spreads_h2'].edge.mean(), Dn[Dn.market == 'totals_h2'].edge.mean()))
def uniq(g): return g.sort_values('edge', ascending=False).drop_duplicates(['game_id', 'market', 'side'])
def money(g, step=0.0):
    p = g.price.map(imp) + step; risk = 300 * p / (1 - p); net = np.where(g.res > 0, 300.0, np.where(g.res < 0, -risk, 0.0)); return net, risk
def roi(g, step=0.0):
    if len(g) == 0: return float('nan')
    net, risk = money(g, step); return 100 * net.sum() / risk.sum()
def lcb(g, z):
    if len(g) < 5: return float('nan')
    net, risk = money(g); r = net.sum() / risk.sum(); c = pd.DataFrame(dict(wk=g.wk.values, n=net, k=risk)).groupby('wk').sum(); k = len(c)
    return float('nan') if k < 3 else 100 * (r - z * np.sqrt(k / (k - 1) * ((c.n - r * c.k) ** 2).sum()) / risk.sum())
def rec(g): return '%d-%d-%d' % ((g.res > 0).sum(), (g.res < 0).sum(), (g.res == 0).sum())
def show(lab, g):
    parts = ' ; '.join('%s n %3d %s %+6.1f%%' % (p, (g.per == p).sum(), rec(g[g.per == p]), roi(g[g.per == p])) for p in ('2023-24', '2025-26'))
    print('  %-34s n %4d in %3d games  %-11s return %+6.1f%%  one step worse %+6.1f%% | %s' % (lab, len(g), g.game_id.nunique(), rec(g), roi(g), roi(g, 0.01), parts))
def verdict(g):
    a, b = g[g.per == '2023-24'], g[g.per == '2025-26']
    if len(a) < 40 or len(b) < 40: return 'UNDERPOWERED (%d and %d entries)' % (len(a), len(b))
    return 'REPLICATED' if roi(a) > 0 and roi(b) > 0 and roi(g, 0.01) > 0 else 'FAILED'
print('\n=== PRIMARY CLAIMS (decision look, sides and totals together, one entry per game, market and side) ===')
c5 = uniq(Dn[Dn.edge >= 3.0]); c6 = uniq(Dn[(Dn.edge >= 2.0)]); c6 = c6[c6.edge < 3.0]
show('C5 edge 3.0 or more', c5); print('      lower bound of the return: %+.1f%% plain, %+.1f%% corrected for six claims | %s' % (lcb(c5, 1.645), lcb(c5, 2.394), verdict(c5)))
show('C6 edge 2.0 to 2.9', c6); print('      lower bound of the return: %+.1f%% plain, %+.1f%% corrected for six claims | %s' % (lcb(c6, 1.645), lcb(c6, 2.394), verdict(c6)))
print('\n=== FOR INFORMATION ONLY ===')
for mk in ('spreads_h2', 'totals_h2'):
    X = Dn[Dn.market == mk]; print('-- %s: every edge band, best-edge book per game and side --' % mk)
    for lab, lo, hi in [('3.0 or more', 3, 99), ('2.0 to 2.9', 2, 3), ('1.0 to 1.9', 1, 2), ('0 to 0.9', 0, 1), ('below 0', -99, 0)]:
        u = uniq(X[X.edge >= lo]); u = u[u.edge < hi] if hi < 99 else u
        if lo < 0: u = uniq(X); u = u[u.edge < 0]
        show(lab, u)
print('-- how often (decision look) --')
games = Dn.game_id.nunique()
for lab, lo in [('3.0+', 3.0), ('2.0+', 2.0), ('1.0+', 1.0)]:
    u = uniq(Dn[Dn.edge >= lo]); print('  a price %s better than the rest: %d entries in %d of %d games (%.1f per 100 games); by season %s' % (lab, len(u), u.game_id.nunique(), games, 100 * len(u) / games, u.groupby('season').size().to_dict()))
print('-- does it last? 3.0+ at look 1, the same book and side at look 2 --')
a = R[(R.look == 1) & (R.edge >= 3.0)][['game_id', 'market', 'book', 'side', 'edge']]; b = R[R.look == 2][['game_id', 'market', 'book', 'side', 'edge']].rename(columns={'edge': 'edge2'})
m = a.merge(b, on=['game_id', 'market', 'book', 'side'], how='left')
print('  3.0+ at look 1: %d book-sides. At look 2: still 3.0+ %d, 0 to 2.9 %d, below 0 %d, book gone or under 3 books %d' % (len(m), (m.edge2 >= 3).sum(), ((m.edge2 >= 0) & (m.edge2 < 3)).sum(), (m.edge2 < 0).sum(), m.edge2.isna().sum()))
print('-- who hangs the 3.0+ prices (decision look, book-sides) --'); print(Dn[Dn.edge >= 3.0].groupby(['market', 'book']).size().unstack(0).fillna(0).astype(int).to_string())
print('-- 3.0+ entries split on whether the other books agree (spreads: numbers within half a point; price: fairs within 3 points) --')
u = c5
for lab, m_ in [('other books within half a point', u.num_range <= 0.5), ('other books more than half a point apart', u.num_range > 0.5), ('fairs within 3 points', u.fair_range <= 3), ('fairs more than 3 points apart', u.fair_range > 3)]:
    show(lab, u[m_])
print('-- 3.0+ by side --')
show('spread sides', c5[c5.market == 'spreads_h2']); show('Overs', c5[(c5.market == 'totals_h2') & (c5.side == 'a')]); show('Unders', c5[(c5.market == 'totals_h2') & (c5.side == 'b')])
print('-- age of the quote behind a 3.0+ price: median %.0f s (all quotes %.0f s) --' % (Dn[Dn.edge >= 3].age.median(), Dn.age.median()))
