#!/usr/bin/env python3
"""Checks on the flow-totals screen, written AFTER its results were seen (so: description, not a claim).
(1) Re-derives the Over rate straight from points against the median line, without the money code, as a cross-check of script 27.
(2) Over rate by third of first-half yards per play, by period. (3) How much chance alone would pass the screen:
random thirds of the same games, 4,000 draws, graded on the same per-game returns.
Usage: python3 28_flow_totals_check.py <nflverse games.csv>"""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '24_grade_totals_claims.py')).read().split("Q2 = load('pull_plan', 'totals_h2')")[0])
Q2 = load('pull_plan', 'totals_h2'); D2, st2, ok2 = decision_quotes(Q2, True)
F = pd.read_csv(os.path.join(HERE, 'h1_flow_2023_2026.csv'))
m = D2.groupby('game_id').point.median().rename('h2_line').reset_index().merge(T[['game_id', 'pts2_ot', 'per']], on='game_id').merge(F[['game_id', 'ypp', 'plays', 'rz_stalled', 'pts1', 'cheap_pts']], on='game_id')
m['o'] = np.sign(m.pts2_ot - m.h2_line)
lo, hi = F.ypp.quantile(1 / 3), F.ypp.quantile(2 / 3); m['third'] = np.where(m.ypp > hi, '3 top', np.where(m.ypp < lo, '1 bottom', '2 middle'))
print('cuts: bottom third under %.2f yards per play, top third over %.2f' % (lo, hi))
print('Over rate against the median line (ties left out), by third of first-half yards per play:')
for p in ('all', '2023-24', '2025-26'):
    y = m if p == 'all' else m[m.per == p]
    print('  %-8s' % p, ' | '.join('%s: %d-%d %.1f%%' % (k, (g.o > 0).sum(), (g.o < 0).sum(), 100 * (g.o > 0).sum() / max(1, (g.o != 0).sum())) for k, g in y.groupby('third')))
a, b = m[m.third == '3 top'], m[m.third == '1 bottom']; pa, pb = (a.o > 0).sum() / (a.o != 0).sum(), (b.o > 0).sum() / (b.o != 0).sum()
se = np.sqrt(pa * (1 - pa) / (a.o != 0).sum() + pb * (1 - pb) / (b.o != 0).sum()); print('  top third minus bottom third: %.1f points, standard error %.1f, z %.1f' % (100 * (pa - pb), 100 * se, (pa - pb) / se))
print('Over rate with 2+ stalled red-zone drives: %.1f%%; with fewer: %.1f%%' % (100 * (m[m.rz_stalled >= 2].o > 0).sum() / (m[m.rz_stalled >= 2].o != 0).sum(), 100 * (m[m.rz_stalled < 2].o > 0).sum() / (m[m.rz_stalled < 2].o != 0).sum()))
# chance check: random thirds graded with the same money rules
go, g1o = per_game(bets(D2, 'pts2_ot', side='over')), per_game(bets(D2, 'pts2_ot', side='over', step=0.01))
gu, g1u = per_game(bets(D2, 'pts2_ot', side='under')), per_game(bets(D2, 'pts2_ot', side='under', step=0.01))
rng = np.random.default_rng(20261112); ids = go.game_id.values; n = 330; passed = {'over': 0, 'under': 0}; draws = 4000
def ok(g, g1, pick):
    x, x1 = g[g.game_id.isin(pick)], g1[g1.game_id.isin(pick)]
    a_, b_ = x[x.per == '2023-24'], x[x.per == '2025-26']
    return len(a_) >= 40 and len(b_) >= 40 and roi(a_) > 0 and roi(b_) > 0 and roi(x1) > 0
for _ in range(draws):
    pick = set(rng.choice(ids, n, replace=False))
    passed['over'] += ok(go, g1o, pick); passed['under'] += ok(gu, g1u, pick)
po, pu = passed['over'] / draws, passed['under'] / draws
print('a random third of the games passes the screen as an Over claim %.1f%% of the time, as an Under claim %.1f%%' % (100 * po, 100 * pu))
lam = 5 * po + 5 * pu
print('with five Over and five Under claims, chance alone expects about %.2f passes; two or more passes by chance: about %.0f%% (claims treated as unrelated)' % (lam, 100 * (1 - np.exp(-lam) * (1 + lam))))
