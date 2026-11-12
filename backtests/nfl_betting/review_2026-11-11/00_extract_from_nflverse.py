#!/usr/bin/env python3
"""Rebuilds halves_2015_2026.csv and flow_1h_2015_2026.csv from nflverse play-by-play (public data on GitHub).
Needs: pip install pandas pyarrow ; network access to github.com. About 20 MB per season, deleted after use.
Halftime score = highest running score on any play in quarters 1-2 (total_home_score / total_away_score are end-of-play).
Checked 2026-11-11: 22 of 22 halftime scores in the rebuilt ledger match."""
import os, subprocess, pandas as pd, pyarrow.parquet as pq
SEASONS = range(2015, 2027)
BASE = 'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_%d.parquet'
GAMES = 'https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv'
def fetch(url, fn):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '180', '-o', fn, '-w', '%{http_code}', url], capture_output=True, text=True)
    if r.stdout.strip() != '200': raise SystemExit('download failed: %s (%s)' % (url, r.stdout))
fetch(GAMES, 'games.csv'); days = pd.read_csv('games.csv', usecols=['game_id', 'gameday'])
halves, flow = [], []
for s in SEASONS:
    fn = 'pbp_%d.parquet' % s; fetch(BASE % s, fn)
    cols = ['game_id', 'play_id', 'qtr', 'game_half', 'posteam', 'play_type', 'yards_gained', 'interception', 'fumble_lost',
            'total_home_score', 'total_away_score', 'home_team', 'away_team', 'spread_line', 'total_line', 'season_type', 'week']
    df = pq.read_table(fn, columns=cols).to_pandas().sort_values(['game_id', 'play_id'])
    for gid, g in df.groupby('game_id', sort=False):
        h, reg = g[g.qtr <= 2], g[g.qtr <= 4]
        if len(h) == 0 or (g.qtr == 3).sum() == 0: continue
        halves.append(dict(game_id=gid, season=s, season_type=g.season_type.iloc[0], week=int(g.week.iloc[0]),
                           home=g.home_team.iloc[0], away=g.away_team.iloc[0],
                           h1_home=int(h.total_home_score.max()), h1_away=int(h.total_away_score.max()),
                           reg_home=int(reg.total_home_score.max()), reg_away=int(reg.total_away_score.max()),
                           fin_home=int(g.total_home_score.max()), fin_away=int(g.total_away_score.max()),
                           spread_line=g.spread_line.iloc[0], total_line=g.total_line.iloc[0]))
    p = df[df.play_type.isin(['pass', 'run']) & df.posteam.notna() & (df.game_half == 'Half1')].copy()
    p['to'] = p.interception.fillna(0) + p.fumble_lost.fillna(0)
    flow.append(p.groupby(['game_id', 'posteam']).agg(plays=('yards_gained', 'size'), yards=('yards_gained', 'sum'), giveaways=('to', 'sum')).reset_index())
    os.remove(fn); print(s, 'done', flush=True)
H = pd.DataFrame(halves).merge(days, on='game_id', how='left')
H[['game_id', 'season', 'season_type', 'week', 'gameday', 'home', 'away', 'h1_home', 'h1_away', 'reg_home', 'reg_away', 'fin_home', 'fin_away', 'spread_line', 'total_line']].to_csv('halves_2015_2026.csv', index=False)
F = pd.concat(flow); F['giveaways'] = F.giveaways.astype(int); F.to_csv('flow_1h_2015_2026.csv', index=False)
print(len(H), 'games;', len(F), 'team first halves')
