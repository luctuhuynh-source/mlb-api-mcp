#!/usr/bin/env python3
"""Audit B-CFB-4: the one-sided push table the college HOOK rule needs. For every game with an FBS team, 2023 to 2026 (public cfbfastR
play-by-play): which team was laying points before the game, its margin at the half, and its margin over the second half with overtime.
Prints how often a half lands exactly on 3, 7 and 10 FOR THE TEAM LAYING POINTS and for the team getting them, by size of the pregame
spread, beside the either-team frequencies the tabs print (first half: 3 = 11.5%, 7 = 15.3%, 10 = 6.1%, tie 5.7%; second half:
3 = 7.0%, 7 = 11.5%, 10 = 5.4%, tie 4.1%). No betting claim is tested here.
Usage: python3 63_push_table_audit.py <folder holding pbp_slim_YYYY.parquet>   (made by --slim from the .rds files)"""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ['game_id', 'period', 'pos_team', 'def_pos_team', 'home', 'away', 'pos_team_score', 'def_pos_team_score', 'spread', 'home_team_division', 'away_team_division', 'neutral_site', 'week']
if sys.argv[1] == '--slim':
    import pyreadr
    for y in sys.argv[3:]:
        df = pyreadr.read_r('/home/claude/sportsdataverse/cfbfastr-data/data/rds/pbp_players_pos_%s.rds' % y)[None]
        df[[c for c in COLS if c in df.columns]].to_parquet(os.path.join(sys.argv[2], 'pbp_slim_%s.parquet' % y)); print('slim', y, df.shape, [c for c in COLS if c not in df.columns]); del df
    sys.exit()
rows = []
for y in (2023, 2024, 2025, 2026):
    fn = os.path.join(sys.argv[1], 'pbp_slim_%d.parquet' % y)
    if not os.path.exists(fn): print('missing', y); continue
    p = pd.read_parquet(fn); p = p[(p.home_team_division == 'fbs') | (p.away_team_division == 'fbs')]
    p['hs'] = np.where(p.pos_team == p.home, p.pos_team_score, np.where(p.def_pos_team == p.home, p.def_pos_team_score, np.nan))
    p['as_'] = np.where(p.pos_team == p.away, p.pos_team_score, np.where(p.def_pos_team == p.away, p.def_pos_team_score, np.nan))
    h = p[p.period <= 2].groupby('game_id').agg(h1h=('hs', 'max'), h1a=('as_', 'max')); f = p.groupby('game_id').agg(fh=('hs', 'max'), fa=('as_', 'max'), spread=('spread', 'first'), per=('period', 'max'))
    g = h.join(f).dropna(subset=['h1h', 'h1a', 'fh', 'fa', 'spread']); g = g[g.per >= 4]; g['season'] = y; rows.append(g.reset_index())
G = pd.concat(rows, ignore_index=True); G = G[G.spread != 0]
sgn = np.where(G.spread < 0, 1, -1)                                   # +1 when the home team is laying points
G['m1'] = sgn * (G.h1h - G.h1a); G['m2'] = sgn * ((G.fh - G.h1h) - (G.fa - G.h1a)); G['lay'] = G.spread.abs()
G.to_csv(os.path.join(HERE, 'cfb_half_margins_2023_2026.csv'), index=False)
print('games %d (%s) | the team laying points led at the half in %.1f%%, tied %.1f%%, trailed %.1f%%' % (len(G), G.groupby('season').size().to_dict(), 100 * (G.m1 > 0).mean(), 100 * (G.m1 == 0).mean(), 100 * (G.m1 < 0).mean()))
def tab(lab, col, tabs):
    print('\n%s' % lab)
    print('  %-26s %6s | %s | tie' % ('pregame spread', 'games', ' | '.join('by %2d: either  LAYING  getting' % k for k in (3, 7, 10))))
    for bl, lo, hi in [('all games', 0, 99), ('0.5 to 3', 0, 3), ('3.5 to 7', 3.5, 7), ('7.5 to 10', 7.5, 10), ('10.5 to 14', 10.5, 14), ('14.5 to 21', 14.5, 21), ('21.5 and up', 21.5, 99)]:
        x = G[(G.lay >= lo) & (G.lay <= hi)]; m = x[col]
        print('  %-26s %6d | %s | %4.1f%%' % (bl, len(x), ' | '.join('       %5.1f%%  %5.1f%%  %5.1f%%' % (100 * (m.abs() == k).mean(), 100 * (m == k).mean(), 100 * (m == -k).mean()) for k in (3, 7, 10)), 100 * (m == 0).mean()))
    print('  the tab prints (either team): %s' % tabs)
tab('FIRST HALF: how often the half ends with a margin of exactly 3, 7 or 10', 'm1', '3 = 11.5%, 7 = 15.3%, 10 = 6.1%, tie 5.7% (314 games)')
tab('SECOND HALF with overtime: margin of exactly 3, 7 or 10', 'm2', '3 = 7.0%, 7 = 11.5%, 10 = 5.4%, tie 4.1% (314 games, regulation)')
se = lambda p, n: 100 * np.sqrt(p * (1 - p) / n)
for lab, lo, hi, k in [('first-half line of 3 (pregame spread 4.5 to 8)', 4.5, 8, 3), ('first-half line of 7 (pregame spread 11.5 to 16.5)', 11.5, 16.5, 7)]:
    x = G[(G.lay >= lo) & (G.lay <= hi)]; p1 = (x.m1 == k).mean()
    print('\n%s: %d games | the team laying leads by exactly %d: %.1f%% (standard error %.1f) | the team getting leads by exactly %d: %.1f%% | either: %.1f%%' % (lab, len(x), k, 100 * p1, se(p1, len(x)), k, 100 * (x.m1 == -k).mean(), 100 * (x.m1.abs() == k).mean()))
