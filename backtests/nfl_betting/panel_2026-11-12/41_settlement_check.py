#!/usr/bin/env python3
"""Scout finding G8 (dual settlement): the same second-half Under graded two ways on the real lines of 2011-2021.
Sportsbook rule = second half includes overtime. Robinhood rule = regulation only (overtime points never count).
An Under can only gain from the regulation rule, never lose. This measures how much. No bet is selected by result."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, '..', 'backtest_2026-11-12', 'h2_lines_2011_2021.csv')); d = d[d.h2_total_ok == 1].copy()
d['pts1'] = d.h1_home + d.h1_away
d['p2_ot'] = (d.fin_home + d.fin_away) - d.pts1; d['p2_reg'] = (d.reg_home + d.reg_away) - d.pts1
d['out'] = d.nv_roof.isin(['outdoors', 'open']) & d.nv_wind.notna()
def rec(x, col):
    r = np.sign(x.h2_total - x[col]); w, l, p = int((r == 1).sum()), int((r == -1).sum()), int((r == 0).sum())
    return w, l, p, 100 * w / (w + l)
def win_prob(x, col):                       # Under win share of all bets, pushes counted as half (for a half-point strike use the next line)
    r = np.sign(x.h2_total - x[col]); return 100 * ((r == 1).sum() + 0.5 * (r == 0).sum()) / len(x)
print('overtime games: %d of %d (%.1f%%)' % (d.ot.sum(), len(d), 100 * d.ot.mean()))
for lab, m in [('every game', d.pts1 >= 0), ('half-point lines only', (d.h2_total % 1) != 0), ('wind 15+', d.out & (d.nv_wind >= 15)), ('wind 10+', d.out & (d.nv_wind >= 10)), ('first half 28+', d.pts1 >= 28), ('halftime margin 0-3', (d.h1_home - d.h1_away).abs() <= 3), ('halftime margin 0-7', (d.h1_home - d.h1_away).abs() <= 7)]:
    x = d[m]; a = rec(x, 'p2_ot'); b = rec(x, 'p2_reg')
    print('  %-22s n %4d | with overtime %d-%d-%d %.1f%% | regulation only %d-%d-%d %.1f%% | gain %.1f points' % (lab, len(x), a[0], a[1], a[2], a[3], b[0], b[1], b[2], b[3], b[3] - a[3]))
x = d[d.ot == 1]; a = rec(x, 'p2_ot'); b = rec(x, 'p2_reg')
print('  overtime games alone: with overtime %d-%d-%d (%.1f%%), regulation only %d-%d-%d (%.1f%%)' % (a[0], a[1], a[2], a[3], b[0], b[1], b[2], b[3]))
assert (d.p2_reg <= d.p2_ot).all()
print('check: regulation points are never above the with-overtime points in any game ->', bool((d.p2_reg <= d.p2_ot).all()))
