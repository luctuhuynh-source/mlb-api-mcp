#!/usr/bin/env python3
"""First-half flow numbers for the 990 games of the paid pull, from nflverse play-by-play, as defined in FLOW_TOTALS_TEST_PLAN.md.
Both teams added together. No second-half result is read here. Writes h1_flow_2023_2026.csv and prints the cuts and the number
of games each claim catches in each period.
Usage: python3 26_build_h1_flow.py <folder with pbp_YYYY.parquet>"""
import sys, os, numpy as np, pandas as pd, pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.join(HERE, '..', '..', 'review_2026-11-11')
clock = pd.read_csv(os.path.join(HERE, 'halftime_clock_2023_2026.csv')); ids = set(clock[clock.ok == 1].game_id)
H = pd.read_csv(os.path.join(REV, 'halves_2015_2026.csv'))[['game_id', 'season', 'h1_home', 'h1_away']]
COLS = ['game_id', 'play_id', 'order_sequence', 'qtr', 'posteam', 'play_type', 'yards_gained', 'fixed_drive', 'fixed_drive_result', 'drive_first_downs', 'drive_inside20', 'ydsnet',
        'drive_start_yard_line', 'touchdown', 'td_team', 'return_touchdown', 'field_goal_result', 'total_home_score', 'total_away_score']
def start_100(txt, posteam):
    """Distance to the opponent's goal line at the start of the drive, from text like 'KC 25' or '50'."""
    if not isinstance(txt, str): return np.nan
    p = txt.split()
    try:
        if len(p) == 1: return float(p[0])
        n = float(p[1]); return 100 - n if p[0] == posteam else n
    except ValueError: return np.nan
rows = []
for season in (2023, 2024, 2025, 2026):
    t = pq.read_table(os.path.join(sys.argv[1], f'pbp_{season}.parquet'), columns=COLS).to_pandas()
    t = t[t.game_id.isin(ids) & (t.qtr <= 2)].copy()
    t['ord'] = t.order_sequence.fillna(t.play_id); t = t.sort_values(['game_id', 'ord'])
    for gid, x in t.groupby('game_id', sort=False):
        pl = x[x.play_type.isin(['pass', 'run'])]
        d = pl.groupby('fixed_drive').agg(team=('posteam', 'first'), res=('fixed_drive_result', 'first'), fd=('drive_first_downs', 'first'), in20=('drive_inside20', 'first'))
        td = d.res == 'Touchdown'
        # points, score by score
        tot = (x.total_home_score + x.total_away_score).ffill().fillna(0); delta = tot.diff().fillna(tot.iloc[0] if len(tot) else 0)
        cheap = 0.0; await_conv = False; conv_cheap = False
        for (i, r), dl in zip(x.iterrows(), delta):
            if r.play_type == 'kickoff': await_conv = False            # the try after a touchdown is over once the ball is kicked off
            if dl <= 0: continue
            if r.touchdown == 1:
                ret = (r.return_touchdown == 1) or (isinstance(r.td_team, str) and isinstance(r.posteam, str) and r.td_team != r.posteam)
                s100 = start_100(r.drive_start_yard_line, r.posteam)
                conv_cheap = bool(ret or (s100 < 40) or (pd.notna(r.ydsnet) and r.ydsnet < 30)); await_conv = True
                if conv_cheap: cheap += dl
            elif await_conv and dl in (1, 2):                          # conversion points go with their touchdown
                if conv_cheap: cheap += dl
                await_conv = False
            elif r.field_goal_result == 'made':
                s100 = start_100(r.drive_start_yard_line, r.posteam)
                if (s100 < 40) or (pd.notna(r.ydsnet) and r.ydsnet < 30): cheap += dl
            # a safety, or anything else, is not cheap
        rows.append(dict(game_id=gid, plays=len(pl), yards=float(pl.yards_gained.sum()), drives=len(d), sustain_n=int(((d.fd >= 2) | td).sum()),
                         three_out_n=int(((d.fd == 0) & (d.res == 'Punt')).sum()), rz_stalled=int(((d.in20 == 1) & ~td).sum()), rz_trips=int((d.in20 == 1).sum()),
                         cheap_pts=cheap, pts1_pbp=float(tot.iloc[-1]) if len(tot) else 0.0))
F = pd.DataFrame(rows).merge(H, on='game_id', how='left')
F['pts1'] = F.h1_home + F.h1_away; F['ypp'] = F.yards / F.plays; F['sustain'] = F.sustain_n / F.drives; F['three_out'] = F.three_out_n / F.drives
F['per'] = np.where(F.season <= 2024, '2023-24', '2025-26')
F.drop(columns=['h1_home', 'h1_away']).to_csv(os.path.join(HERE, 'h1_flow_2023_2026.csv'), index=False)
print('games %d of %d | first-half points from play-by-play equal the half score in %d games' % (len(F), len(ids), int((F.pts1_pbp == F.pts1).sum())))
print(F[['plays', 'ypp', 'drives', 'sustain', 'three_out', 'rz_trips', 'rz_stalled', 'cheap_pts', 'pts1']].describe().round(2).loc[['mean', 'std', 'min', '50%', 'max']].to_string())
q = lambda c, p: float(F[c].quantile(p))
cuts = dict(ypp_lo=q('ypp', 1 / 3), ypp_hi=q('ypp', 2 / 3), plays_lo=q('plays', 1 / 3), plays_hi=q('plays', 2 / 3), three_hi=q('three_out', 2 / 3), sustain_hi=q('sustain', 2 / 3), pts_med=float(F.pts1.median()))
print('cuts:', {k: round(v, 3) for k, v in cuts.items()})
M = {'T1 YPP top third (Over)': F.ypp > cuts['ypp_hi'], 'T2 YPP bottom third (Under)': F.ypp < cuts['ypp_lo'], 'T3 TEMPO top third (Over)': F.plays > cuts['plays_hi'],
     'T4 TEMPO bottom third (Under)': F.plays < cuts['plays_lo'], 'T5 CHEAP POINTS 10+ (Under)': F.cheap_pts >= 10,
     'T6 YPP top third, points low (Over)': (F.ypp > cuts['ypp_hi']) & (F.pts1 <= cuts['pts_med']), 'T7 points high, YPP bottom third (Under)': (F.pts1 > cuts['pts_med']) & (F.ypp < cuts['ypp_lo']),
     'T8 two or more stalled red-zone drives (Over)': F.rz_stalled >= 2, 'T9 3-AND-OUT top third (Under)': F.three_out > cuts['three_hi'], 'T10 SUSTAIN top third (Over)': F.sustain > cuts['sustain_hi']}
print('games each claim catches (no result read):')
for k, m in M.items(): print('  %-48s %4d   2023-24 %3d   2025-26 %3d' % (k, m.sum(), (m & (F.per == '2023-24')).sum(), (m & (F.per == '2025-26')).sum()))
