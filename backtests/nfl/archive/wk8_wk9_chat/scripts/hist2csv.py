"""usage: python3 -I hist2csv.py <tool-result json path> <week key>  -> /home/claude/bt/props/<key>/<event_id>.csv (props.py format)"""
import json, csv, sys, os
d = json.load(open(sys.argv[1])); key = sys.argv[2]
out = f'/home/claude/bt/props/{key}/{d["event_id"]}.csv'; os.makedirs(os.path.dirname(out), exist_ok=True)
n = 0
with open(out, 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['away', 'home', 'snapshot', 'book', 'market', 'player', 'side', 'point', 'price'])
    for b in d['books']:
        for m in b['markets']:
            for o in m['outcomes']:
                w.writerow([d['away'], d['home'], d['snapshot_timestamp'], b['key'], m['key'], o.get('description', ''), o['name'], o.get('point') if o.get('point') is not None else '', o['price']]); n += 1
print(out, n, 'rows', 'remaining', d.get('requests_remaining'))
