#!/usr/bin/env python3
"""Checks run by the manager on the two panel reports of 2026-11-12 (ChatGPT = doubter, Gemini = scout).
Part A re-does the doubter's arithmetic. Part B counts how many 2023-2026 games each declared cell will catch
(no bet result is read). Part C measures how far the 2022-2026 full-game look contaminates a second-half test (finding D1)
and the side/total correlation inside the cells (finding D7). Part D accounts for the 15 games without a second-half total (D8).
Part E checks two scout cells on full-game data already on hand (U6 primetime Under, O1 calm outdoor Over) and the 15-19 / 20+ split.
Usage: python3 40_panel_checks.py <nflverse games.csv>"""
import sys, os, math, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); BT = os.path.join(HERE, '..', 'backtest_2026-11-12')
BE = 110 / 210
print('=== A. the doubter\'s arithmetic ===')
t50 = stats.binom.sf(142, 250, 0.5); tbe = stats.binom.sf(142, 250, BE)
print('143 wins of 250: one-sided tail vs 50%% = %.2f%% (report: 1.33%%); vs -110 break-even = %.2f%% (report: 7.16%%)' % (100 * t50, 100 * tbe))
print('at least one such result in 45 independent cells: %.1f%% and %.1f%% (report: 45.3%% and 96.5%%)' % (100 * (1 - (1 - t50) ** 45), 100 * (1 - (1 - tbe) ** 45)))
def need(p1, p0=BE, a=0.05, pw=0.80):
    za, zb = stats.norm.ppf(1 - a), stats.norm.ppf(pw)
    return ((za * math.sqrt(p0 * (1 - p0)) + zb * math.sqrt(p1 * (1 - p1))) / (p1 - p0)) ** 2
print('bets needed, one-sided 5%%, 80%% power: 54%% true -> %.0f (report: about 5,900); 57%% true -> %.0f (report: about 725)' % (need(0.54), need(0.57)))
def p_pos(n, p, price):                       # chance the return is above zero on n bets, no pushes
    k = math.floor(n * price / (100 + price)) + 1
    return stats.binom.sf(k - 1, n, p), k
a, k = p_pos(40, BE, 110); b, k2 = p_pos(40, BE, 115)
print('40 bets at -110: %d wins needed for a return above zero (report: 21-19 passes). Break-even cell passes one period %.1f%%, two periods %.1f%% (report: 31%%)' % (k, 100 * a, 100 * a * a))
print('   the same graded at -115: %d wins needed; passes two periods %.1f%% (report: about 19%%)' % (k2, 100 * b * b))
kk = max(w for w in range(41) if (w * 100 / 110 - (40 - w)) / 40 <= -0.03)
print('a true 57%% cell at -3%% or worse after 40 bets: %.1f%% (report: about 23%%)  [%d wins or fewer]' % (100 * stats.binom.cdf(kk, 40, 0.57), kk))
print('1476+1379+76 = %d of 2946 games (report: 15 missing)' % (1476 + 1379 + 76))
print('second-half WIND-A share 2011-2021: 257 of 2931 = %.2f%%; x 990 games = %.0f (report: roughly 87)' % (100 * 257 / 2931, 990 * 257 / 2931))

g = pd.read_csv(sys.argv[1]); g = g[(g.season >= 2011) & g.home_score.notna()].copy()
g['out'] = g.roof.isin(['outdoors', 'open'])
print('\n=== B. coverage 2023 to 2026-11-09, counted without reading any bet result ===')
h = pd.read_csv(os.path.join(BT, 'halftime_pull', 'halftime_clock_2023_2026.csv'))
x = g[g.game_id.isin(h.game_id)].copy(); x['per'] = np.where(x.season <= 2024, '2023-24', '2025-26')
print('games in the pull: %d (clock file %d)' % (len(x), len(h)))
def band(r):
    if not r.out: return 'indoors (dome or closed roof)'
    if pd.isna(r.wind): return 'outdoors, NO wind reading'
    return 'outdoors wind 15+' if r.wind >= 15 else ('outdoors wind 10-14' if r.wind >= 10 else 'outdoors wind under 10')
x['band'] = x.apply(band, axis=1)
print(pd.crosstab(x.band, x.per, margins=True).to_string())
print('outdoor games with no reading, by season:', x[x.out].groupby('season').wind.apply(lambda s: '%d of %d' % (s.isna().sum(), len(s))).to_dict())
hv = os.path.join(os.path.dirname(sys.argv[1]), 'halves_2015_2026.csv')
if os.path.exists(hv):
    hh = pd.read_csv(hv); cols = hh.columns.tolist()
    print('halves file columns:', cols[:14])

d = pd.read_csv(os.path.join(BT, 'h2_lines_2011_2021.csv'))
print('\n=== D. the 15 games without a usable second-half total (finding D8) ===')
bad = d[d.h2_total_ok != 1]
print('games %d, usable total %d, not usable %d' % (len(d), (d.h2_total_ok == 1).sum(), len(bad)))
print(bad[['season', 'gameday', 'game_id', 'close_total', 'h2_total', 'h2_spread_abs', 'h1_home', 'h1_away']].to_string(index=False))

d = d[d.h2_total_ok == 1].copy()
d['pts1'] = d.h1_home + d.h1_away; d['pts2'] = (d.fin_home + d.fin_away) - d.pts1
d['u2'] = np.sign(d.h2_total - d.pts2); d['out'] = d.nv_roof.isin(['outdoors', 'open']) & d.nv_wind.notna()
d['ufg'] = np.sign(d.close_total - (d.fin_home + d.fin_away))
print('\n=== C1. how much a full-game Under result says about the second-half Under in the same game (finding D1) ===')
for lab, m in [('every game', d.u2.notna()), ('outdoor wind 10+', d.out & (d.nv_wind >= 10)), ('outdoor wind 15+', d.out & (d.nv_wind >= 15))]:
    y = d[m & (d.u2 != 0) & (d.ufg != 0)]
    a = y[y.ufg == 1]; b = y[y.ufg == -1]
    print('  %-18s n %4d  corr %.2f  2H Under wins %.1f%% when the full-game Under won (%d), %.1f%% when it lost (%d)' % (lab, len(y), np.corrcoef(y.u2, y.ufg)[0, 1], 100 * (a.u2 == 1).mean(), len(a), 100 * (b.u2 == 1).mean(), len(b)))
print('\n=== C2. side and total inside the cells (finding D7) ===')
s = d[d.h2_side_ok == 1].copy()
s['m1'] = s.h1_home - s.h1_away; s['m2'] = (s.fin_home - s.fin_away) - s.m1
s['lead_home'] = np.sign(s.m1)
s['cover_home'] = np.sign(s.m2 + s.h2_home_line)
s['lead_cov'] = s.lead_home * s.cover_home                     # +1 leader covered its second-half line
for lab, m in [('every game with a leader', s.m1 != 0), ('WIND 10+', s.out & (s.nv_wind >= 10) & (s.m1 != 0)), ('WIND 15+', s.out & (s.nv_wind >= 15) & (s.m1 != 0)), ('first half 28+', (s.pts1 >= 28) & (s.m1 != 0))]:
    y = s[m & (s.lead_cov != 0) & (s.u2 != 0)]
    both = ((y.lead_cov == 1) & (y.u2 == 1)).mean(); neither = ((y.lead_cov == -1) & (y.u2 == -1)).mean()
    print('  %-26s n %4d  corr(leader covers, Under wins) %+.2f  both win %.1f%%  both lose %.1f%%  (independent coin flips: 25%% and 25%%)' % (lab, len(y), np.corrcoef(y.lead_cov, y.u2)[0, 1], 100 * both, 100 * neither))

print('\n=== E. scout cells checked on data already on hand (full game, nflverse closing total, -110) ===')
g = g[g.total_line.notna()].copy(); g['res'] = np.sign(g.total_line - (g.home_score + g.away_score)); g['o'] = g.out & g.wind.notna()
def rec(x, side=1):
    w = int((x.res == side).sum()); l = int((x.res == -side).sum()); p = int((x.res == 0).sum())
    return w, l, p, (100 * w / (w + l) if w + l else float('nan')), (100 * (w * 100 / 110 - l) / (w + l + p) if w + l + p else float('nan'))
P3 = [('2011-16', 2011, 2016), ('2017-21', 2017, 2021), ('2022-26', 2022, 2026)]
def cell(name, m, side=1):
    x = g[m]; a = rec(x, side); parts = []
    for lab, lo, hi in P3:
        b = rec(x[(x.season >= lo) & (x.season <= hi)], side); parts.append('%s %d-%d %.1f%% %+.1f' % (lab, b[0], b[1], b[3], b[4]))
    print('  %-44s %4d-%-4d-%-3d %5.1f%%  roi %+5.1f | %s' % (name, a[0], a[1], a[2], a[3], a[4], ' ; '.join(parts)))
hr = pd.to_numeric(g.gametime.astype(str).str[:2], errors='coerce')
prime = (g.game_type == 'REG') & (((g.weekday == 'Sunday') & (hr >= 20)) | ((g.weekday == 'Monday') & (hr >= 19)) | ((g.weekday == 'Thursday') & (hr >= 19)))
cell('U6 PRIMETIME Under (Sun/Mon/Thu night, regular season)', prime)
cell('   primetime, outdoors or open roof', prime & g.out)
cell('   primetime, indoors', prime & ~g.out)
cell('   NOT primetime, Under', (g.game_type == 'REG') & ~prime)
cell('O1 CALM outdoor (wind under 8) OVER', g.o & (g.wind < 8), side=-1)
cell('Under, outdoor wind 15-19', g.o & (g.wind >= 15) & (g.wind < 20))
cell('Under, outdoor wind 20+', g.o & (g.wind >= 20))
x = g[prime & (g.season == 2025)]; a = rec(x); print('  primetime Under in 2025 alone: %d-%d-%d (scout: 27-19-1)' % a[:3])
print('  second half, real lines 2011-2021:')
for lab, m in [('Under, wind 15-19', d.out & (d.nv_wind >= 15) & (d.nv_wind < 20)), ('Under, wind 20+', d.out & (d.nv_wind >= 20))]:
    y = d[m]; w = int((y.u2 == 1).sum()); l = int((y.u2 == -1).sum()); p = int((y.u2 == 0).sum())
    print('    %-22s %d-%d-%d  %.1f%%' % (lab, w, l, p, 100 * w / (w + l)))
