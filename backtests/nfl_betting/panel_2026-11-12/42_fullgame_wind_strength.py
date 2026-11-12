#!/usr/bin/env python3
"""How strong is the full-game wind result once the number of comparisons is allowed for (doubter finding D4)?
Full-game Under, outdoor wind 10+, at the actual nflverse closing Under price, 2011 to 2026-11-09 (the +9.7% line in
out_14 / out_16). Standard error from the per-bet returns, and again with every game of one week counted together.
Usage: python3 42_fullgame_wind_strength.py <nflverse games.csv>"""
import sys, numpy as np, pandas as pd
from scipy import stats
g = pd.read_csv(sys.argv[1]); g = g[(g.season >= 2011) & g.total_line.notna() & g.home_score.notna()].copy()
g['out'] = g.roof.isin(['outdoors', 'open']) & g.wind.notna()
def ret(r):
    t = r.home_score + r.away_score; o = r.under_odds
    if t == r.total_line: return 0.0
    if t > r.total_line: return -1.0
    return 100.0 / -o if o < 0 else o / 100.0
for lab, m in [('wind 10+', g.out & (g.wind >= 10)), ('wind 15+', g.out & (g.wind >= 15)), ('wind 10-14', g.out & (g.wind >= 10) & (g.wind < 15)), ('wind under 10', g.out & (g.wind < 10))]:
    x = g[m & g.under_odds.notna()].copy(); x['r'] = x.apply(ret, axis=1)
    n = len(x); mu = x.r.mean(); se = x.r.std(ddof=1) / np.sqrt(n)
    wk = x.groupby(['season', 'week']).r.agg(['sum', 'size']); k = len(wk)
    se_cl = np.sqrt(k / (k - 1) * ((wk['sum'] - mu * wk['size']) ** 2).sum()) / n
    z = mu / se_cl; p = stats.norm.sf(z)
    print('%-14s n %4d  return %+5.1f%%  se %.1f (by week %.1f)  z %.2f  one-sided p %.4f  x45 comparisons %.3f  | lower 95%% bound %+.1f%%' % (lab, n, 100 * mu, 100 * se, 100 * se_cl, z, p, min(1, 45 * p), 100 * (mu - 1.645 * se_cl)))
    print('      by period:', ' ; '.join('%s %+.1f%% (n %d)' % (l, 100 * x[(x.season >= a) & (x.season <= b)].r.mean(), ((x.season >= a) & (x.season <= b)).sum()) for l, a, b in [('2011-16', 2011, 2016), ('2017-21', 2017, 2021), ('2022-26', 2022, 2026)]))
