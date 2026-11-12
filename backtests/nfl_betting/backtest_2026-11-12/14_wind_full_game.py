#!/usr/bin/env python3
"""Second check on the wind result, in a different market and through this season: full-game Unders against the nflverse
closing total, outdoor games with a wind reading, 2011 to 2026-11-09. Graded at -110 (break-even 52.4%).
Rule under test: F-33 / H-26 (wind 15+ sustained -> Over fires vetoed; an Under 'gains nothing from the flag').
Usage: python3 14_wind_full_game.py <nflverse games.csv>"""
import sys, numpy as np, pandas as pd
g = pd.read_csv(sys.argv[1]); g = g[(g.season >= 2011) & g.total_line.notna() & g.home_score.notna()].copy(); g['tot'] = g.home_score + g.away_score
BE = 110 / 210
def rec(lab, x):
    u = int((x.tot < x.total_line).sum()); o = int((x.tot > x.total_line).sum()); p = int((x.tot == x.total_line).sum()); n = u + o
    if n == 0: print('  %-44s n 0' % lab); return
    se = np.sqrt(0.25 / n)
    print('  %-44s Under %4d-%-4d-%-3d %5.1f%%  (se %.1f)  vs 50%%: z %+.1f   vs 52.4%%: z %+.1f' % (lab, u, o, p, 100 * u / n, 100 * se, (u / n - 0.5) / se, (u / n - BE) / se))
out = g[g.roof.isin(['outdoors', 'open']) & g.wind.notna()]
print('full-game totals, 2011 to 2026-11-09: %d games, %d outdoors with a wind reading' % (len(g), len(out)))
rec('every game', g); rec('dome or closed roof', g[g.roof.isin(['dome', 'closed'])])
rec('wind under 10 mph', out[out.wind < 10]); rec('wind 10-14 mph', out[(out.wind >= 10) & (out.wind < 15)]); rec('wind 15+ mph', out[out.wind >= 15]); rec('wind 20+ mph', out[out.wind >= 20])
rec('wind 10+ mph', out[out.wind >= 10])
print(' wind 15+ by period')
rec('2011-2016', out[(out.wind >= 15) & (out.season <= 2016)]); rec('2017-2021', out[(out.wind >= 15) & (out.season >= 2017) & (out.season <= 2021)]); rec('2022-2026', out[(out.wind >= 15) & (out.season >= 2022)])
print(' wind 10+ by period')
rec('2011-2016', out[(out.wind >= 10) & (out.season <= 2016)]); rec('2017-2021', out[(out.wind >= 10) & (out.season >= 2017) & (out.season <= 2021)]); rec('2022-2026', out[(out.wind >= 10) & (out.season >= 2022)])
o2 = g[g.roof.isin(['outdoors', 'open'])]
print('outdoor games with no wind reading: %.0f%% overall, %.0f%% in 2022-2026 (those games are left out)' % (100 * o2.wind.isna().mean(), 100 * o2[o2.season >= 2022].wind.isna().mean()))
