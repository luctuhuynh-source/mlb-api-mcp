#!/usr/bin/env python3
"""Halftime clock for every NFL game 2023 to 2026-11-09, from nflverse play-by-play `time_of_day` (UTC), and the pull plan
for the paid halftime price test. Per game: last first-half play, first third-quarter play (the 3Q kickoff), and two look times:
  look1 = last first-half play + 7 minutes  -> the feed snapshot at or before it sits 2 to 7 minutes into halftime
  look2 = 3Q kickoff - 30 seconds           -> the last snapshot before the second half starts
Writes halftime_clock_2023_2026.csv and pull_plan.json (batches of up to 16 games for get_event_odds_historical_batch).
Usage: python3 20_build_halftime_clock.py <folder with pbp_YYYY.parquet> <nflverse games.csv>"""
import sys, os, json, pandas as pd, pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); pbp_dir, games_csv = sys.argv[1], sys.argv[2]
NAME = {'ARI':'Arizona Cardinals','ATL':'Atlanta Falcons','BAL':'Baltimore Ravens','BUF':'Buffalo Bills','CAR':'Carolina Panthers','CHI':'Chicago Bears','CIN':'Cincinnati Bengals',
 'CLE':'Cleveland Browns','DAL':'Dallas Cowboys','DEN':'Denver Broncos','DET':'Detroit Lions','GB':'Green Bay Packers','HOU':'Houston Texans','IND':'Indianapolis Colts',
 'JAX':'Jacksonville Jaguars','KC':'Kansas City Chiefs','LV':'Las Vegas Raiders','LAC':'Los Angeles Chargers','LA':'Los Angeles Rams','MIA':'Miami Dolphins','MIN':'Minnesota Vikings',
 'NE':'New England Patriots','NO':'New Orleans Saints','NYG':'New York Giants','NYJ':'New York Jets','PHI':'Philadelphia Eagles','PIT':'Pittsburgh Steelers','SF':'San Francisco 49ers',
 'SEA':'Seattle Seahawks','TB':'Tampa Bay Buccaneers','TEN':'Tennessee Titans','WAS':'Washington Commanders'}
g = pd.read_csv(games_csv); g = g[(g.season >= 2023) & g.home_score.notna()]
kick = {r.game_id: pd.Timestamp(f'{r.gameday} {r.gametime}', tz='America/New_York').tz_convert('UTC') for r in g.itertuples() if isinstance(r.gametime, str)}
rows = []
for season in (2023, 2024, 2025, 2026):
    t = pq.read_table(os.path.join(pbp_dir, f'pbp_{season}.parquet'), columns=['game_id', 'play_id', 'qtr', 'time_of_day', 'home_team', 'away_team']).to_pandas()
    t = t[t.time_of_day.notna()].sort_values(['game_id', 'play_id']); t['tod'] = pd.to_datetime(t.time_of_day, utc=True, format='ISO8601')
    for gid, x in t.groupby('game_id', sort=False):
        h, q3 = x[x.qtr == 2], x[x.qtr == 3]
        if len(h) == 0 or len(q3) == 0 or gid not in kick: continue
        a, b = h.tod.max(), q3.tod.min(); mins = (b - a).total_seconds() / 60
        rows.append(dict(game_id=gid, season=season, home=x.home_team.iloc[0], away=x.away_team.iloc[0], home_name=NAME[x.home_team.iloc[0]], kickoff_utc=kick[gid],
                         last_1h_play_utc=a, q3_kickoff_utc=b, gap_minutes=round(mins, 1), ok=int(9 <= mins <= 40 and a > kick[gid])))
d = pd.DataFrame(rows)
f = lambda s: s.dt.strftime('%Y-%m-%dT%H:%M:%SZ')
d['look1'] = f(d.last_1h_play_utc + pd.Timedelta(minutes=7)); d['look2'] = f(d.q3_kickoff_utc - pd.Timedelta(seconds=30))
for c in ('kickoff_utc', 'last_1h_play_utc', 'q3_kickoff_utc'): d[c] = f(d[c])
d.to_csv(os.path.join(HERE, 'halftime_clock_2023_2026.csv'), index=False)
print(d.groupby('season').agg(games=('game_id', 'size'), ok=('ok', 'sum'), gap_median=('gap_minutes', 'median')).to_string())
print('not ok:', d[d.ok == 0][['game_id', 'gap_minutes']].to_string(index=False))
good = d[d.ok == 1].sort_values('kickoff_utc'); batches = []
for day, x in good.groupby(good.kickoff_utc.str[:10], sort=True):
    x = x.reset_index(drop=True)
    for i in range(0, len(x), 16):
        c = x.iloc[i:i + 16]
        batches.append(dict(events_date=(pd.Timestamp(c.kickoff_utc.min()) - pd.Timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%SZ'), game_ids=list(c.game_id),
                            items=';'.join(f'{r.home_name}|{r.look1}|{r.look2}' for r in c.itertuples())))
json.dump(batches, open(os.path.join(HERE, 'pull_plan.json'), 'w'), indent=0)
print('games in plan:', len(good), '| batches (tool calls):', len(batches), '| lookups:', 2 * len(good), '| credits at 20 per lookup:', 40 * len(good) + len(batches))
