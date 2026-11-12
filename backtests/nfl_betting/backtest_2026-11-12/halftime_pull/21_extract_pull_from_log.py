#!/usr/bin/env python3
"""Collect get_event_odds_historical_batch results (compact mode) out of Claude session logs into pulled_quotes.csv.
Each game arrives as one line: key~event_id~home~away~asked>ts>market=book,point,a,b,age/book,...>market=...~asked>ts>...
  spreads: point = HOME spread, price_a = home price, price_b = away price
  totals:  point = total, price_a = Over price, price_b = Under price
  age:     seconds between the snapshot (ts) and that book's last update of that market (blank in pulls made before 11/12 2 AM)
Rows are keyed on (event_id, asked, market, book), so re-running over several logs is safe.
Usage: python3 21_extract_pull_from_log.py <session.jsonl> [more.jsonl ...]"""
import sys, json, os, csv
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'pulled_quotes.csv')
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)
    elif isinstance(o, str): yield o
rows, errors = {}, []
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT)): r.setdefault('age', ''); rows[(r['event_id'], r['asked'], r['market'], r['book'])] = r
for src in sys.argv[1:]:
    with open(src) as f:
        for line in f:
            if 'lookups_asked' not in line: continue
            try: rec = json.loads(line)
            except Exception: continue
            for s in walk(rec):
                i = s.find('{"pulled"')
                if i < 0 or 'lookups_asked' not in s: continue
                try: d = json.loads(s[i:s.rfind('}') + 1])
                except Exception: continue
                for g in d.get('games', []):
                    if not isinstance(g, str): continue
                    p = g.split('~')
                    if len(p) < 4: continue
                    key, ev, home, away = p[:4]
                    for look in p[4:]:
                        if look.startswith('ERR'): errors.append((key, look)); continue
                        q = look.split('>')
                        if len(q) < 2 or q[1].startswith('ERR'): errors.append((key, look)); continue
                        asked, ts = q[0], q[1]
                        for mk in q[2:]:
                            name, _, body = mk.partition('=')
                            for b in [x for x in body.split('/') if x]:
                                v = b.split(',')
                                if len(v) < 4: continue
                                k = (ev, asked, name, v[0]); age = v[4] if len(v) > 4 else ''
                                if k in rows and age == '' and rows[k].get('age', '') != '': continue      # keep the row that has an age
                                rows[k] = dict(event_id=ev, home=home, away=away, asked=asked, ts=ts, market=name, book=v[0], point=v[1], price_a=v[2], price_b=v[3], age=age)
out = sorted(rows.values(), key=lambda r: (r['ts'], r['event_id'], r['asked'], r['market'], r['book']))
with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['event_id', 'home', 'away', 'asked', 'ts', 'market', 'book', 'point', 'price_a', 'price_b', 'age']); w.writeheader(); w.writerows(out)
print(len(out), 'quote rows |', len({r['event_id'] for r in out}), 'games |', len({(r['event_id'], r['asked']) for r in out}), 'looks | errors:', len(errors))
for e in errors[:20]: print('  ', e)
