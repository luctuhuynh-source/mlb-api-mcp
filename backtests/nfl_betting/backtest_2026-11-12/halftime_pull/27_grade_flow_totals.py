#!/usr/bin/env python3
"""Grades the ten flow claims of FLOW_TOTALS_TEST_PLAN.md against the real second-half totals of the paid pull.
The cleaning and money rules are the ones of 24_grade_totals_claims.py: the top of that script (everything above its first
claim) is run here as is, so the two cannot drift apart. Flow numbers come from h1_flow_2023_2026.csv (26_build_h1_flow.py).
Usage: python3 27_grade_flow_totals.py <nflverse games.csv>"""
import sys, os, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '24_grade_totals_claims.py')).read().split("Q2 = load('pull_plan', 'totals_h2')")[0])
Q2 = load('pull_plan', 'totals_h2'); D2, st2, ok2 = decision_quotes(Q2, True)
F = pd.read_csv(os.path.join(HERE, 'h1_flow_2023_2026.csv'))
q = lambda c, p: float(F[c].quantile(p))
ypp_lo, ypp_hi, pl_lo, pl_hi, three_hi, sus_hi, pts_med = q('ypp', 1 / 3), q('ypp', 2 / 3), q('plays', 1 / 3), q('plays', 2 / 3), q('three_out', 2 / 3), q('sustain', 2 / 3), float(F.pts1.median())
CLAIMS = [('T1', 'YPP top third', F.ypp > ypp_hi, 'over'), ('T2', 'YPP bottom third', F.ypp < ypp_lo, 'under'), ('T3', 'TEMPO top third', F.plays > pl_hi, 'over'),
          ('T4', 'TEMPO bottom third', F.plays < pl_lo, 'under'), ('T5', 'CHEAP POINTS 10+', F.cheap_pts >= 10, 'under'),
          ('T6', 'moved it, did not score', (F.ypp > ypp_hi) & (F.pts1 <= pts_med), 'over'), ('T7', 'scored without moving it', (F.pts1 > pts_med) & (F.ypp < ypp_lo), 'under'),
          ('T8', '2+ stalled red-zone drives', F.rz_stalled >= 2, 'over'), ('T9', '3-AND-OUT top third', F.three_out > three_hi, 'under'), ('T10', 'SUSTAIN top third', F.sustain > sus_hi, 'over')]
Z10 = stats.norm.ppf(1 - 0.05 / 10)
base = {s: per_game(bets(D2, 'pts2_ot', side=s)) for s in ('over', 'under')}
print('\n=== base rates, every game ===')
for s in ('over', 'under'): line('every game, ' + s.capitalize(), base[s])
print('\n=== THE TEN CLAIMS (average book at its own number and price, decision look) ===')
summary = []
for tag, lab, mask, side in CLAIMS:
    ids = set(F[mask].game_id); d = D2[D2.game_id.isin(ids)]
    g, g1 = per_game(bets(d, 'pts2_ot', side=side)), per_game(bets(d, 'pts2_ot', side=side, step=0.01))
    v = verdict(g, g1).replace('REPLICATED', 'PASSED THE SCREEN')
    line('%s %s -> %s' % (tag, lab, side.capitalize()), g, g1)
    lifts = ' ; '.join('%s %+.1f' % (p, roi(g[g.per == p]) - roi(base[side][base[side].per == p])) for p in ('2023-24', '2025-26'))
    print('      against every %s in the same period: %s points | cautious end of the return: %+.1f%% plain, %+.1f%% corrected for ten claims | %s' % (side.capitalize(), lifts, lcb(g, 1.645), lcb(g, Z10), v))
    summary.append((tag, lab, side, len(g), roi(g), roi(g[g.per == '2023-24']), roi(g[g.per == '2025-26']), v))
print('\n=== FOR INFORMATION: each flow number against (second-half points minus the market line), one at a time ===')
m = D2.groupby('game_id').point.median().rename('h2_line').reset_index().merge(T[['game_id', 'pts2_ot', 'per']], on='game_id').merge(F, on='game_id', suffixes=('', '_f'))
m['miss'] = m.pts2_ot - m.h2_line
print('games %d | mean miss %+.2f points (2023-24 %+.2f, 2025-26 %+.2f) | sd %.1f' % (len(m), m.miss.mean(), m[m.per == '2023-24'].miss.mean(), m[m.per == '2025-26'].miss.mean(), m.miss.std()))
for c, lab in [('ypp', 'yards per play'), ('plays', 'tempo (plays)'), ('sustain', 'sustain rate'), ('three_out', '3-and-out rate'), ('rz_stalled', 'stalled red-zone drives'), ('rz_trips', 'red-zone trips'), ('cheap_pts', 'cheap points'), ('pts1', 'first-half points'), ('h2_line', 'the line itself')]:
    out = []
    for p in ('all', '2023-24', '2025-26'):
        y = m if p == 'all' else m[m.per == p]; x = (y[c] - y[c].mean()) / y[c].std(); r = stats.linregress(x, y.miss)
        out.append('%s %+.2f pts per 1 sd (t %+.1f)' % (p, r.slope, r.slope / r.stderr))
    print('  %-26s %s' % (lab, ' | '.join(out)))
X = m[['ypp', 'plays', 'sustain', 'three_out', 'rz_stalled', 'cheap_pts', 'pts1']]; Xs = (X - X.mean()) / X.std(); A = np.column_stack([np.ones(len(Xs)), Xs.values])
beta, res, rk, sv = np.linalg.lstsq(A, m.miss.values, rcond=None); fit = A @ beta; r2 = 1 - ((m.miss - fit) ** 2).sum() / ((m.miss - m.miss.mean()) ** 2).sum()
print('  all seven together explain %.1f%% of the miss (R-squared), n %d' % (100 * r2, len(m)))
print('\n=== summary ===')
for s in summary: print('  %-4s %-28s %-5s n %3d  return %+6.1f%%  (%+6.1f / %+6.1f)  %s' % s)
