#!/usr/bin/env python3
"""Second plan file for the paid pull: first-half totals at the last snapshot before kickoff (claim C2).
Same games and the same batches as pull_plan.json; one look per game, asked 60 seconds before the scheduled kickoff
(the feed returns the snapshot at or before the asked time, so it sits 1 to 6 minutes before kickoff).
Writes pull_plan_h1.json. Usage: python3 23_build_h1_plan.py"""
import os, json, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
clock = pd.read_csv(os.path.join(HERE, 'halftime_clock_2023_2026.csv')).set_index('game_id')
plan = json.load(open(os.path.join(HERE, 'pull_plan.json'))); out = []
for b in plan:
    items = []
    for gid in b['game_ids']:
        r = clock.loc[gid]; t = (pd.Timestamp(r.kickoff_utc) - pd.Timedelta(seconds=60)).strftime('%Y-%m-%dT%H:%M:%SZ')
        items.append(f'{r.home_name}|{t}')
    out.append(dict(events_date=b['events_date'], game_ids=b['game_ids'], items=';'.join(items)))
json.dump(out, open(os.path.join(HERE, 'pull_plan_h1.json'), 'w'), indent=0)
print('batches', len(out), '| games', sum(len(b['game_ids']) for b in out), '| credits at 10 per lookup:', 10 * sum(len(b['game_ids']) for b in out) + len(out))
print(out[0]); print(out[1]['items'][:160])
