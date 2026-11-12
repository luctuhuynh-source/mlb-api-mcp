#!/usr/bin/env python3
"""Grades claims C1 to C4 of TEST_PLAN_LOCKED.md on the paid pull. Written before any pulled price was looked at.
  C1 WIND 10+ Under, second half      C2 WIND 10+ Under, first half (pregame look)
  C3 SCORE Under (first half 28+), calm or indoors      C4 SCORE inside wind: return with 28+ minus return with fewer
Cleaning (plan section 2): main line only (both prices between -200 and +200); fresh (halftime: last update at or after the last
first-half play; pregame: 30 minutes old or less); a look counts with 2+ books; decision look = look 1, else look 2; a bet is the
Under at one book's own number and price; sportsbook settlement (second half includes overtime, tie refunded); stake to win $300;
each game counts once (its books averaged); one price step worse = break-even + 1.0 point; periods 2023-24 and 2025-26.
Usage: python3 24_grade_totals_claims.py <nflverse games.csv>"""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.join(HERE, '..', '..', 'review_2026-11-11')
clock = pd.read_csv(os.path.join(HERE, 'halftime_clock_2023_2026.csv'))
H = pd.read_csv(os.path.join(REV, 'halves_2015_2026.csv'))
G = pd.read_csv(sys.argv[1])[['game_id', 'season', 'week', 'game_type', 'roof', 'wind']]
T = clock[clock.ok == 1][['game_id', 'last_1h_play_utc', 'kickoff_utc', 'look1', 'look2']].merge(H[['game_id', 'h1_home', 'h1_away', 'reg_home', 'reg_away', 'fin_home', 'fin_away']], on='game_id', how='left').merge(G, on='game_id', how='left')
T['pts1'] = T.h1_home + T.h1_away; T['pts2_ot'] = T.fin_home + T.fin_away - T.pts1; T['pts2_reg'] = T.reg_home + T.reg_away - T.pts1
T['ot'] = (T.fin_home + T.fin_away) != (T.reg_home + T.reg_away)
T['out'] = T.roof.isin(['outdoors', 'open']); T['per'] = np.where(T.season <= 2024, '2023-24', '2025-26')
T['wk'] = T.season.astype(str) + '_' + T.week.astype(str)
print('games in the plan: %d | with scores: %d | outdoor %d (no wind reading %d) | indoor %d' % (len(T), T.pts1.notna().sum(), T.out.sum(), (T.out & T.wind.isna()).sum(), (~T.out).sum()))

def be(o):
    o = float(o); return -o / (-o + 100) if o < 0 else 100 / (o + 100)
def load(name, market):
    q = pd.read_csv(os.path.join(HERE, 'pulled_%s.csv' % name)); q = q[q.market == market].copy()
    for c in ('point', 'price_a', 'price_b', 'age'): q[c] = pd.to_numeric(q[c], errors='coerce')
    q['main'] = q.price_a.between(-200, 200) & q.price_b.between(-200, 200) & q.point.notna()
    return q
def decision_quotes(q, halftime):
    """Rows of the decision look of each game, after the main-line and freshness tests."""
    q = q.merge(T[['game_id', 'last_1h_play_utc', 'look1', 'look2']], on='game_id', how='inner')
    ts = pd.to_datetime(q.ts, utc=True)
    if halftime:
        upd = ts - pd.to_timedelta(q.age, unit='s'); q['fresh'] = q.age.notna() & (upd >= pd.to_datetime(q.last_1h_play_utc, utc=True))
        q['look'] = np.where(q.asked == q.look1, 1, np.where(q.asked == q.look2, 2, 0))
    else:
        q['fresh'] = q.age.notna() & (q.age <= 1800); q['look'] = 1
    stats = dict(rows=len(q), not_main=int((~q.main).sum()), stale=int((q.main & ~q.fresh).sum()), no_age=int(q.age.isna().sum()))
    ok = q[q.main & q.fresh & (q.look > 0)]
    n = ok.groupby(['game_id', 'look']).book.nunique().unstack(fill_value=0)
    for k in (1, 2):
        if k not in n.columns: n[k] = 0
    pick = pd.Series(np.where(n[1] >= 2, 1, np.where(n[2] >= 2, 2, 0)), index=n.index, name='pick')
    d = ok.merge(pick.reset_index(), on='game_id'); d = d[d.look == d.pick]
    stats.update(games_with_quotes=int(q.game_id.nunique()), decided_look1=int((pick == 1).sum()), decided_look2=int((pick == 2).sum()), no_look=int((pick == 0).sum()) + int(len(T) - len(pick)))
    return d, stats, ok

def bets(d, pts_col, side='under', step=0.0, settle=None):
    """One row per book quote: net and risk for a bet to win $300 on that side at that book's number and price."""
    x = d.merge(T[['game_id', pts_col, 'per', 'wk', 'season']], on='game_id'); x = x[x[pts_col].notna()].copy()
    price = x.price_b if side == 'under' else x.price_a
    p = price.map(be) + step; x['risk'] = 300 * p / (1 - p)
    diff = (x.point - x[pts_col]) if side == 'under' else (x[pts_col] - x.point)
    x['res'] = np.sign(diff); x['net'] = np.where(x.res > 0, 300.0, np.where(x.res < 0, -x.risk, 0.0))
    # a refunded bet (tie) keeps its stake in the amount risked, as in the earlier scripts
    return x
def per_game(x):
    g = x.groupby('game_id').agg(net=('net', 'mean'), risk=('risk', 'mean'), books=('book', 'nunique'), w=('res', lambda r: (r > 0).mean()), l=('res', lambda r: (r < 0).mean()),
                                 per=('per', 'first'), wk=('wk', 'first'), season=('season', 'first'), line=('point', 'median'), juice=('price_b', 'median')).reset_index()
    return g
def roi(g): return float('nan') if len(g) == 0 or g.risk.sum() == 0 else 100 * g.net.sum() / g.risk.sum()
def lcb(g, z):
    if len(g) < 5: return float('nan')
    r = g.net.sum() / g.risk.sum(); c = g.groupby('wk').agg(n=('net', 'sum'), k=('risk', 'sum')); k = len(c)
    if k < 3: return float('nan')
    se = np.sqrt(k / (k - 1) * ((c.n - r * c.k) ** 2).sum()) / g.risk.sum()
    return 100 * (r - z * se)
def line(lab, g, g1=None):
    parts = []
    for p in ('2023-24', '2025-26'):
        y = g[g.per == p]; parts.append('%s n %3d  %5.1f%% won  return %+6.1f%%' % (p, len(y), 100 * y.w.sum() / max(1e-9, (y.w.sum() + y.l.sum())), roi(y)))
    s = '%-44s n %4d  %5.1f%% won  return %+6.1f%%' % (lab, len(g), 100 * g.w.sum() / max(1e-9, (g.w.sum() + g.l.sum())), roi(g))
    if g1 is not None: s += '  | one step worse %+6.1f%%' % roi(g1)
    print(s + '  | ' + ' ; '.join(parts))
def verdict(g, g1):
    a, b = g[g.per == '2023-24'], g[g.per == '2025-26']
    if len(a) < 40 or len(b) < 40: return 'UNDERPOWERED (%d and %d games)' % (len(a), len(b))
    return 'REPLICATED' if roi(a) > 0 and roi(b) > 0 and roi(g1) > 0 else 'FAILED'
def claim(tag, lab, d, mask_ids, pts_col):
    x = bets(d[d.game_id.isin(mask_ids)], pts_col); x1 = bets(d[d.game_id.isin(mask_ids)], pts_col, step=0.01)
    g, g1 = per_game(x), per_game(x1)
    line(tag + ' ' + lab, g, g1)
    print('      books per game %.1f | median line %.1f | median Under price %+.0f | lower bound of the return: %+.1f%% plain, %+.1f%% corrected for six claims | %s' % (
        g.books.mean() if len(g) else float('nan'), g.line.median() if len(g) else float('nan'), g.juice.median() if len(g) else float('nan'), lcb(g, 1.645), lcb(g, 2.394), verdict(g, g1)))
    return g

Q2 = load('pull_plan', 'totals_h2'); D2, st2, ok2 = decision_quotes(Q2, True)
print('second-half totals:', st2)
Q1 = load('pull_plan_h1', 'totals_h1'); D1, st1, ok1 = decision_quotes(Q1, False)
print('first-half totals: ', st1)
wind10 = set(T[T.out & (T.wind >= 10)].game_id); windA = set(T[T.out & (T.wind >= 15)].game_id); windB = wind10 - windA
calm = set(T[(~T.out) | (T.out & (T.wind < 10))].game_id); score = set(T[T.pts1 >= 28].game_id); noread = set(T[T.out & T.wind.isna()].game_id)
print('cells (games in the plan): wind 10+ %d (15+ %d, 10-14 %d) | calm or indoors %d | first half 28+ %d | outdoor with no reading, left out of every claim %d' % (len(wind10), len(windA), len(windB), len(calm), len(score), len(noread)))
print('\n=== PRIMARY CLAIMS (Under, average book at its own number and price, decision look) ===')
g_c1 = claim('C1', 'WIND 10+ Under, second half', D2, wind10, 'pts2_ot')
g_c2 = claim('C2', 'WIND 10+ Under, first half', D1, wind10, 'pts1')
g_c3 = claim('C3', 'SCORE Under, calm or indoors', D2, calm & score, 'pts2_ot')
print('C4 SCORE inside wind (second half, wind 10+): return with first half 28+ minus return with fewer')
ga = per_game(bets(D2[D2.game_id.isin(wind10 & score)], 'pts2_ot')); gb = per_game(bets(D2[D2.game_id.isin(wind10 - score)], 'pts2_ot'))
line('   wind 10+ and first half 28+', ga); line('   wind 10+ and first half under 28', gb)
gaps, enough = [], True
for p in ('2023-24', '2025-26'):
    a, b = ga[ga.per == p], gb[gb.per == p]; gaps.append(roi(a) - roi(b)); enough = enough and len(a) >= 40 and len(b) >= 40
    print('      %s gap %+.1f points (%d against %d games)' % (p, gaps[-1], len(a), len(b)))
print('      C4:', ('REPLICATED' if all(x > 0 for x in gaps) else 'FAILED') if enough else 'UNDERPOWERED')

print('\n=== FOR INFORMATION ONLY ===')
print('-- bands and base rates, second half --')
line('wind 15+ Under', per_game(bets(D2[D2.game_id.isin(windA)], 'pts2_ot'))); line('wind 10-14 Under', per_game(bets(D2[D2.game_id.isin(windB)], 'pts2_ot')))
line('every game, Under', per_game(bets(D2, 'pts2_ot'))); line('every game, Over', per_game(bets(D2, 'pts2_ot', side='over')))
line('first half 28+, every game, Under', per_game(bets(D2[D2.game_id.isin(score)], 'pts2_ot')))
line('outdoor wind under 10, Under', per_game(bets(D2[D2.game_id.isin(set(T[T.out & (T.wind < 10)].game_id))], 'pts2_ot')))
print('-- bands, first half (pregame look) --')
line('wind 15+ Under', per_game(bets(D1[D1.game_id.isin(windA)], 'pts1'))); line('wind 10-14 Under', per_game(bets(D1[D1.game_id.isin(windB)], 'pts1')))
line('every game, Under', per_game(bets(D1, 'pts1'))); line('every game, Over', per_game(bets(D1, 'pts1', side='over')))
print('-- controls expected to fail --')
line('Over, indoors, second half', per_game(bets(D2[D2.game_id.isin(set(T[~T.out].game_id))], 'pts2_ot', side='over')))
line('Over after a first half of 13 or fewer', per_game(bets(D2[D2.game_id.isin(set(T[T.pts1 <= 13].game_id))], 'pts2_ot', side='over')))
print('-- best book instead of the average book (highest number, then best Under price) --')
def best(d):
    d = d.copy(); d['beu'] = d.price_b.map(be); return d.sort_values(['game_id', 'point', 'beu'], ascending=[True, False, True]).groupby('game_id').head(1)
line('C1 at the best book', per_game(bets(best(D2[D2.game_id.isin(wind10)]), 'pts2_ot'))); line('C3 at the best book', per_game(bets(best(D2[D2.game_id.isin(calm & score)]), 'pts2_ot')))
print('-- look 2 (last snapshot before the 3rd-quarter kickoff) instead of the decision look --')
L2 = ok2[ok2.look == 2]; L2 = L2[L2.groupby('game_id').book.transform('nunique') >= 2]
line('C1 at look 2', per_game(bets(L2[L2.game_id.isin(wind10)], 'pts2_ot'))); line('C3 at look 2', per_game(bets(L2[L2.game_id.isin(calm & score)], 'pts2_ot')))
print('-- the Robinhood view: half-point lines only, regulation points, break-even + 2 points for the fee --')
hp = D2[(D2.point % 1) != 0]
line('C1 regulation only, less 2 cents', per_game(bets(hp[hp.game_id.isin(wind10)], 'pts2_reg', step=0.02))); line('C1 same quotes, sportsbook rule', per_game(bets(hp[hp.game_id.isin(wind10)], 'pts2_ot')))
line('every game regulation only, less 2 cents', per_game(bets(hp, 'pts2_reg', step=0.02)))
print('-- how the market set the second-half total (median fresh main line per game at the decision look) --')
m = D2.groupby('game_id').point.median().rename('h2_total').reset_index().merge(T, on='game_id').merge(pd.read_csv(sys.argv[1])[['game_id', 'total_line']], on='game_id')
m = m[m.total_line.notna() & m.pts1.notna()]; m['lead'] = (m.h1_home - m.h1_away).abs()
X = np.column_stack([m.total_line, m.pts1, m.lead]); c = np.linalg.lstsq(X, m.h2_total.values, rcond=None)[0]; c2 = np.linalg.lstsq(X, m.pts2_ot.values, rcond=None)[0]
print('   market line = %.3f x pregame total %+.3f x first-half points %+.3f x halftime lead   (2011-2021: 0.481, +0.063, -0.083)' % tuple(c))
print('   actual points = %.3f x pregame total %+.3f x first-half points %+.3f x halftime lead' % tuple(c2))
