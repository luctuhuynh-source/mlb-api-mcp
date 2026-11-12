#!/usr/bin/env python3
"""Turns the saved results of kalshi_get_candlesticks (plan mode) into two files.
The server pads each result so the client saves it to a file instead of reading it into the conversation; this script reads
those files. One line per event:  i~game~event~source~t0~markets~contract^contract^...
  contract = suffix,strike,result,status,label|m,bid,ask,ask_low,bid_high,trade_low,trade_high,volume;...
  m = minutes after t0 (0 = the standing quote going into the window); prices in cents; a minute in which nothing changed and
  nothing traded is left out, so the last row at or before a minute is the standing quote at that minute.
Writes kalshi_contracts_2026.csv (one row per contract) and kalshi_halftime_2026.csv.gz (one row per contract and minute kept).
Usage: python3 51_collect_kalshi.py <folder with the saved tool results>"""
import os, sys, json, glob, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else '.'
plan = json.load(open(os.path.join(HERE, 'kalshi_plan.json')))
files = sorted(glob.glob(os.path.join(D, 'mcp-MLB_Stats-kalshi_get_candlesticks-*.txt')), key=os.path.getmtime)
events, errs = {}, {}
for fn in files:
    try: d = json.load(open(fn))
    except Exception as ex: print('unreadable', os.path.basename(fn), type(ex).__name__); continue
    if d.get('plan') != 'kalshi_plan': continue
    print('%s | asked %s-%s | done %d | next %s | http %s | sec %s | errors %s | size %d' % (os.path.basename(fn)[-18:], d.get('from'), d.get('to'), len(d.get('games_done', [])),
          d.get('next'), d.get('http_calls'), d.get('seconds'), d.get('errors'), os.path.getsize(fn)))
    for i, ln in d.get('events', []):
        h = ln.split('~')
        if len(h) >= 4 and h[3].startswith('ERR'):
            errs[(int(h[0]), h[2])] = h[3]
            continue
        events[(int(h[0]), h[2].split('-')[0])] = ln           # the latest good line for this game and series wins
cons, rows = [], []
for (i, series), ln in sorted(events.items()):
    idx, g, ev, src, t0, nmk, body = ln.split('~', 6)
    t0 = int(t0)
    for part in body.split('^'):
        head, _, rr = part.partition('|')
        suf, strike, result, status, label = head.split(',', 4)
        tk = ev + '-' + suf
        n = 0
        for r in [x for x in rr.split(';') if x]:
            m, b, a, al, bh, pl, ph, v = (r.split(',') + [''] * 8)[:8]
            rows.append((g, series, tk, int(m), t0 + 60 * int(m), b, a, al, bh, pl, ph, v)); n += 1
        cons.append((int(idx), g, series, ev, tk, suf, strike, result, status, label.strip(), src, t0, n))
C = pd.DataFrame(cons, columns=['idx', 'game_id', 'series', 'event', 'ticker', 'suffix', 'strike', 'result', 'status', 'label', 'source', 't0', 'rows'])
R = pd.DataFrame(rows, columns=['game_id', 'series', 'ticker', 'm', 'end_ts', 'bid', 'ask', 'ask_low', 'bid_high', 'trade_low', 'trade_high', 'volume'])
for c in ('bid', 'ask', 'ask_low', 'bid_high', 'trade_low', 'trade_high', 'volume'): R[c] = pd.to_numeric(R[c], errors='coerce')
C.to_csv(os.path.join(HERE, 'kalshi_contracts_2026.csv'), index=False); R.to_csv(os.path.join(HERE, 'kalshi_halftime_2026.csv.gz'), index=False)
have = {(i, s) for (i, s) in events}
print('\nsaved files read: %d | events collected: %d | contracts: %d | minute rows: %d' % (len(files), len(events), len(C), len(R)))
for s in ('KXNFL2HSPREAD', 'KXNFL2HTOTAL'):
    got = sorted(i for (i, ss) in have if ss == s); miss = [i for i in range(len(plan)) if i not in got]
    noev = sorted({i for (i, ev), e in errs.items() if ev.startswith(s) and 'no markets' in e and i in miss}); other = [i for i in miss if i not in noev]
    print('%s: games with contracts %d of %d | no such event on the exchange: %d | not pulled or failed: %d %s' % (s, len(got), len(plan), len(noev), len(other), other[:20]))
    if noev: print('   no event:', ', '.join(plan[i]['g'] for i in noev[:60]))
if len(C):
    print('source of the candles:', C.groupby('source').size().to_dict(), '| contracts per event: median %d, min %d, max %d' % (C.groupby('event').size().median(), C.groupby('event').size().min(), C.groupby('event').size().max()))
    print('contracts with no row at all: %d of %d | status: %s | result: %s' % ((C.rows == 0).sum(), len(C), C.status.value_counts().to_dict(), C.result.fillna('').replace('', '(none)').value_counts().to_dict()))
    print('labels (sample):', C.groupby('series').label.apply(lambda x: list(x.unique()[:4])).to_dict())
