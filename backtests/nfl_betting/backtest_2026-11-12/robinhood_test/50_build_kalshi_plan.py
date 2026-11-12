#!/usr/bin/env python3
"""Builds kalshi_plan.json: one item per 2026 game of the halftime pull, for the server tool kalshi_get_candlesticks in plan
mode (tickers="plan:kalshi_plan:<from>-<to>"). For each game: the Robinhood (Kalshi) second-half spread and total events, and the
window of one-minute price history wanted: 3 minutes before the last first-half play to 2 minutes after the third-quarter kickoff.
Event ticker = SERIES-<YYMONDD><AWAY><HOME>, the date being the kickoff date in US Eastern time; Kalshi writes JAC and LAR where
nflverse writes JAX and LA. A second candidate with the UTC date is listed when the two dates differ.
Usage: python3 50_build_kalshi_plan.py"""
import os, json, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
C = pd.read_csv(os.path.join(HERE, '..', 'halftime_pull', 'halftime_clock_2023_2026.csv'))
C = C[(C.season == 2026) & (C.ok == 1)].copy()
C['ko'] = pd.to_datetime(C.kickoff_utc, utc=True); C = C.sort_values(['ko', 'game_id']).reset_index(drop=True)
KX = {'JAX': 'JAC', 'LA': 'LAR'}
def code(ts): return ts.strftime('%y%b%d').upper()
plan = []
for r in C.itertuples():
    et, utc = r.ko.tz_convert('America/New_York'), r.ko
    a, h = KX.get(r.away, r.away), KX.get(r.home, r.home)
    dates = [code(et)] + ([code(utc)] if code(utc) != code(et) else [])
    t0 = int(pd.Timestamp(r.last_1h_play_utc).floor('min').timestamp()) - 180
    t1 = int(pd.Timestamp(r.q3_kickoff_utc).ceil('min').timestamp()) + 120
    plan.append({'g': r.game_id, 'ev': [[f'{s}-{d}{a}{h}' for d in dates] for s in ('KXNFL2HSPREAD', 'KXNFL2HTOTAL')], 't0': t0, 't1': t1})
json.dump(plan, open(os.path.join(HERE, 'kalshi_plan.json'), 'w'), separators=(',', ':'))
print('games', len(plan), '| first', plan[0], '| last', plan[-1])
print('window minutes: min %.0f median %.0f max %.0f' % tuple(pd.Series([(p['t1'] - p['t0']) / 60 for p in plan]).quantile([0, .5, 1])))
print('games with a second date candidate:', sum(len(p['ev'][0]) > 1 for p in plan))
