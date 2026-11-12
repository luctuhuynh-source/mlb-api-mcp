#!/usr/bin/env python3
"""Builds the halftime pull plan for the college sides test: one lookup per usable game, second-half spreads, at
"last first-half play + 10 minutes" (cfb_h1_features_2026.csv, column look). The odds archive returns the snapshot at or before
that time. The server finds each game by a fragment of its home team's name, so each game gets a key: the team's nickname when no
other FBS or FCS team shares it, otherwise school + nickname in the odds feed's spelling.
Writes ../../nfl_betting/backtest_2026-11-12/halftime_pull/<name>.json (the only folder the server's plan mode reads).
Usage: python3 61_build_pull_plan.py [name] [csv with game_id,key overrides]"""
import sys, os, json, re, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); NAME = sys.argv[1] if len(sys.argv) > 1 else 'cfb_pull_plan'
F = pd.read_csv(os.path.join(HERE, 'cfb_h1_features_2026.csv')); F = F[F.ok == 1].copy()
T = pd.read_parquet('/home/claude/sportsdataverse/cfbfastr-data/team_info/parquet/cfb_team_info_2026.parquet')
T = T[T.classification.isin(['fbs', 'fcs'])]
SCHOOL = {'App State': 'Appalachian State', 'San José State': 'San Jose State', 'Southern Miss': 'Southern Miss', "Hawai'i": 'Hawaii', 'Massachusetts': 'UMass', 'Sam Houston': 'Sam Houston'}
def nick(m):
    m = str(m).strip()
    if "'" in m: m = m.split("'")[-1].strip() if not m.split("'")[-1].strip() == '' else m.replace("'", '')
    m = m.split(' ', 1)[1] if "'" in str(m) else m
    return m.lower()
T['nick'] = T.mascot.map(lambda m: re.sub(r"^\S*'\S*\s+", '', str(m).strip()).lower())
cnt = {}
for n in T.nick:
    for other in T.nick:
        pass
def shared(n): return sum(1 for o in T.nick if n in o) > 1          # another nickname contains this one
T['key'] = [n if not shared(n) else (SCHOOL.get(s, s) + ' ' + n).lower() for s, n in zip(T.school, T.nick)]
T.loc[T.school == 'Southern Miss', 'key'] = 'southern miss'
KEY = dict(zip(T.school, T.key))
over = {}
if len(sys.argv) > 2:
    o = pd.read_csv(sys.argv[2]); over = dict(zip(o.game_id, o.key))
F['key'] = [over.get(g, KEY.get(h, h.lower())) for g, h in zip(F.game_id, F.home)]
F['t'] = pd.to_datetime(F.look, utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ'); F['ko'] = pd.to_datetime(F.start, utc=True)
F = F.sort_values(['ko', 'game_id'])
if over: F = F[F.game_id.isin(over)]
batches, cur = [], []
def flush():
    if cur:
        t0 = min(c.ko for c in cur) - pd.Timedelta(hours=2)
        batches.append({'events_date': t0.strftime('%Y-%m-%dT%H:%M:%SZ'), 'game_ids': [int(c.game_id) for c in cur], 'items': ';'.join('%s|%s' % (c.key, c.t) for c in cur)})
        cur.clear()
for r in F.itertuples():
    if cur and (len(cur) >= 12 or (r.ko - cur[0].ko) > pd.Timedelta(hours=20) or any(c.key == r.key for c in cur)): flush()
    cur.append(r)
flush()
out = os.path.join(HERE, '..', '..', 'nfl_betting', 'backtest_2026-11-12', 'halftime_pull', NAME + '.json')
json.dump(batches, open(out, 'w'), separators=(',', ':')); F[['game_id', 'home', 'away', 'key', 't']].to_csv(os.path.join(HERE, NAME + '_keys.csv'), index=False)
print('plan %s: %d games in %d batches | credits about %d | keys by school+nickname: %d' % (NAME, len(F), len(batches), 10 * len(F) + len(batches), F.key.str.contains(' ').sum()))
print('; '.join(sorted({'%s -> %s' % (h, k) for h, k in zip(F.home, F.key) if ' ' in k or k in ('southern miss',)})))
print('single-word keys:', ', '.join(sorted({k for k in F.key if ' ' not in k})))
