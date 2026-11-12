#!/usr/bin/env python3
"""Collect the paid pull out of the result files the client saved to disk (plan mode of get_event_odds_historical_batch).
Each file is one JSON result: {"plan", "batches_done", "games": [[batch, line], ...], ...} with one line per game:
  key~event_id~home~away~asked>ts>market=book,point,a,b,age/book,...>market=...~asked>ts>...
  spreads: point = HOME spread, price_a = home, price_b = away.  totals: point = total, price_a = Over, price_b = Under.
  age = seconds between the snapshot (ts) and that book's last update of that market.
Writes pulled_<plan>.csv.gz (one row per game, look, market and book) and prints which batches of the plan are still missing.
Rows are keyed, so running it again over the same files changes nothing.
Usage: python3 22_collect_saved_results.py <tool-results folder>"""
import sys, os, json, csv, glob, gzip, collections
HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ['plan', 'batch', 'game_id', 'event_id', 'home', 'away', 'asked', 'ts', 'market', 'book', 'point', 'price_a', 'price_b', 'age']
files = sorted(glob.glob(os.path.join(sys.argv[1], 'mcp-MLB_Stats-get_event_odds_historical_batch-*.txt')))
rows, done, errs, credits, nolook = collections.defaultdict(dict), collections.defaultdict(set), [], collections.Counter(), collections.defaultdict(set)
plans = {}
for fn in files:
    try: d = json.load(open(fn))
    except Exception as ex: print('unreadable', os.path.basename(fn), type(ex).__name__); continue
    name = d.get('plan')
    if not name or 'games' not in d: continue
    if name not in plans: plans[name] = json.load(open(os.path.join(HERE, name + '.json')))
    credits[name] += d.get('approx_credits_used') or 0
    for k, v in (d.get('errors') or {}).items(): errs.append((name, int(k), 'batch', v))
    seen = collections.Counter()
    for b, line in d['games']:
        done[name].add(b); p = line.split('~'); key, ev, home, away = (p + ['', '', '', ''])[:4]
        ids = plans[name][b]['game_ids']; keys = [it.split('|')[0] for it in plans[name][b]['items'].split(';')]
        gid = ids[keys.index(key)] if key in keys else ''
        for look in p[4:]:
            if look.startswith('ERR'): errs.append((name, b, gid or key, look)); continue
            q = look.split('>')
            if len(q) < 2 or q[1].startswith('ERR'): errs.append((name, b, gid or key, look)); continue
            asked, ts = q[0], q[1]
            if len(q) == 2: nolook[name].add((gid, asked))
            for mk in q[2:]:
                mname, _, body = mk.partition('=')
                for x in [x for x in body.split('/') if x]:
                    v = x.split(',')
                    if len(v) < 4: continue
                    rows[name][(gid, asked, mname, v[0])] = dict(plan=name, batch=b, game_id=gid, event_id=ev, home=home, away=away, asked=asked, ts=ts, market=mname,
                                                               book=v[0], point=v[1], price_a=v[2], price_b=v[3], age=v[4] if len(v) > 4 else '')
for name, plan in plans.items():
    out = os.path.join(HERE, 'pulled_' + name + '.csv.gz'); old = {}
    if os.path.exists(out):
        for r in csv.DictReader(gzip.open(out, 'rt', newline='')): old[(r['game_id'], r['asked'], r['market'], r['book'])] = r
    old.update(rows[name]); allr = sorted(old.values(), key=lambda r: (int(r['batch']), r['game_id'], r['asked'], r['market'], r['book']))
    with gzip.open(out, 'wt', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(allr)
    have = {int(r['batch']) for r in allr} | done[name]; missing = [i for i in range(len(plan)) if i not in have]
    games = {r['game_id'] for r in allr}; want = {g for b in plan for g in b['game_ids']}
    print('%s: %d rows | games with quotes %d of %d | looks %d | batches seen %d of %d | credits reported in these files %d' % (name, len(allr), len(games & want), len(want), len({(r['game_id'], r['asked']) for r in allr}), len(have), len(plan), credits[name]))
    print('   batches missing:', missing[:40], '...' if len(missing) > 40 else '')
    print('   games in the plan with no quote at all: %d' % len(want - games), sorted(want - games)[:12])
    print('   looks that came back with no book posting: %d' % len(nolook[name]))
print('errors:', len(errs))
for e in errs[:25]: print('  ', e)
