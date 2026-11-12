#!/usr/bin/env python3
"""Collect kalshi_get_candlesticks results out of a Claude session log (jsonl) into kalshi_quotes.csv.
Each result carries self-describing lines "ticker|floor_strike|result|source|kept_of_total|end_ts,bid,ask,lo,hi,vol;...".
Usage: python3 30_extract_kalshi_from_log.py <session.jsonl>"""
import sys, json, os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
    elif isinstance(o, str): yield o
rows = {}
with open(sys.argv[1]) as f:
    for line in f:
        if 'markets_found' not in line: continue
        try: rec = json.loads(line)
        except Exception: continue
        for s in walk(rec):
            i = s.find('{"count"')
            if i < 0 or 'markets_found' not in s: continue
            try: d = json.loads(s[i:s.rfind('}') + 1])
            except Exception: continue
            for m in d.get('markets', []):
                if isinstance(m, dict):          # first version of the tool returned one dict per market
                    if not str(m.get('ticker', '')).startswith('KXNFL'): continue
                    for c in m.get('candles') or []:
                        rows[(m['ticker'], str(c[0]))] = dict(ticker=m['ticker'], floor_strike=m.get('floor_strike'), result=m.get('result') or '', source=m.get('source') or '',
                                                             end_ts=str(c[0]), yes_bid=c[1], yes_ask=c[2], ask_low=c[3], ask_high=c[4], volume=c[5] if len(c) > 5 else '')
                    continue
                p = m.split('|')
                if len(p) < 6 or not p[0].startswith('KXNFL'): continue
                for c in [x for x in p[5].split(';') if x]:
                    v = c.split(',')
                    rows[(p[0], v[0])] = dict(ticker=p[0], floor_strike=p[1], result=p[2], source=p[3], end_ts=v[0], yes_bid=v[1], yes_ask=v[2], ask_low=v[3], ask_high=v[4], volume=v[5] if len(v) > 5 else '')
out = sorted(rows.values(), key=lambda r: (r['ticker'], int(r['end_ts'])))
with open(os.path.join(HERE, 'kalshi_quotes.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out), 'quote rows,', len({r['ticker'] for r in out}), 'contracts,', len({r['ticker'].rsplit('-', 1)[0] for r in out}), 'events')
