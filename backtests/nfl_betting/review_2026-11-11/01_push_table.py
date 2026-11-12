#!/usr/bin/env python3
"""B-NFL-3: one-sided exact-margin table for NFL halves, 2015 to 2026-11-09. Writes ../push_table_onesided_2015_2026.csv"""
import os, numpy as np, pandas as pd
from nfl_halves import load, favourite_view, HERE
d = load(); f, c = favourite_view(d); N = len(f); rec = f[f.season >= 2024]
# 1. reproduce the protocol's own table B-NFL-2 (2025 regular season + 2026 through 10/5)
sub = d[((d.season == 2025) & (d.season_type == 'REG')) | ((d.season == 2026) & (d.gameday <= '2026-10-05'))]
print('B-NFL-2 check, n=%d: 1H either team by 3 %.1f%%, 7 %.1f%%, 10 %.1f%%, tie %.1f%% | 2H regulation 3 %.1f%%, 7 %.1f%%, 10 %.1f%%, tie %.1f%%' % (
    (len(sub),) + tuple(100 * (sub.m1.abs() == k).mean() for k in (3, 7, 10, 0)) + tuple(100 * (sub.m2reg.abs() == k).mean() for k in (3, 7, 10, 0))))
print('   protocol text says:      1H 3 = 15.7%, 7 = 14.2%, 10 = 7.1%, tie = 8.3% (n=337) | 2H 3 = 9.5%, 7 = 12.5%, 10 = 6.8%, tie = 10.7%')
rows = []
for half, col, who in (('1H', 'fm1', 'pregame favourite'), ('2H incl OT (DSB)', 'lay2ot', '2H favourite: pregame spread and halftime margin'),
                       ('2H regulation (Robinhood)', 'lay2reg', '2H favourite: pregame spread and halftime margin')):
    for k in range(0, 18):
        e, a, b = (f[col].abs() == k).mean(), (f[col] == k).mean(), (f[col] == -k).mean()
        e2, a2, b2 = (rec[col].abs() == k).mean(), (rec[col] == k).mean(), (rec[col] == -k).mean()
        if k == 0: a = b = e; a2 = b2 = e2
        rows.append(dict(half=half, margin=k, either_team_pct=round(100 * e, 2), team_laying_points_pct=round(100 * a, 2),
                         team_getting_points_pct=round(100 * b, 2), se_pct=round(100 * np.sqrt(a * (1 - a) / N), 2),
                         either_team_2024_26_pct=round(100 * e2, 2), team_laying_points_2024_26_pct=round(100 * a2, 2),
                         team_getting_points_2024_26_pct=round(100 * b2, 2), n_all=N, n_2024_26=len(rec), laying_side=who))
T = pd.DataFrame(rows); T.to_csv(os.path.join(HERE, '..', 'push_table_onesided_2015_2026.csv'), index=False)
pd.set_option('display.width', 220)
print('\nn = %d games with a favourite (2015 to 2026-11-09), %d in 2024-26. 2H favourite model: %.3f x pregame spread %+.3f x halftime margin %+.2f' % ((N, len(rec)) + tuple(c)))
print(T[T.margin.isin([0, 1, 2, 3, 4, 6, 7, 10, 14])][['half', 'margin', 'either_team_pct', 'team_laying_points_pct', 'team_getting_points_pct', 'se_pct', 'team_laying_points_2024_26_pct']].to_string(index=False))
def lay(h, k): return float(T[(T.half.str.startswith(h)) & (T.margin == k)].team_laying_points_pct.iloc[0]) / 100
print('\nValue of a flat key number against books on the hook, at a 50% fair on the hook number (points of conditional win probability):')
for lab, old, new in (('1H 3', .157, lay('1H', 3)), ('1H 7', .142, lay('1H', 7)), ('2H incl OT 3', .095, lay('2H incl', 3)), ('2H incl OT 7', .125, lay('2H incl', 7))):
    print('  %-13s as run with %.1f%%: %+.1f | one-sided %.1f%%: %+.1f' % (lab, 100 * old, 100 * (.5 / (1 - old) - .5), 100 * new, 100 * (.5 / (1 - new) - .5)))
p = 0.556 * (1 - 0.095)   # 11/1 LAR -3 2H @ -105: the board printed "effective 55.6% vs 51.2 implied" using a 9.5% push mass
for m, lab in ((0.095, 'as run'), (lay('2H incl', 3), 'one-sided, 2015-26')):
    print('11/1 LAR -3 2H @ DSB -105, push mass %.1f%% (%s): conditional win %.1f%% vs break-even 51.2%% = %+.1f points' % (100 * m, lab, 100 * p / (1 - m), 100 * (p / (1 - m) - 0.5122)))
