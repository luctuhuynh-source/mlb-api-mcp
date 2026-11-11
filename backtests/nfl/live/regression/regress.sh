#!/bin/sh
# Regression test for the NFL build_live.py. Run after ANY change:  sh backtests/nfl/live/regression/regress.sh
# Real Week 9 inputs from backtests/nfl/archive/wk8_wk9_chat (post-inactives FanDuel list, props, lines, 9:25 LineStar pull) and the seven
# players ruled out by hand that morning. Test 1: the v1.6 shadow must equal the Week 9 v1.6 lineups built on 11/8, 15 of 15 in order.
# Test 2: the v1.8 upload must equal the recorded one. PROTOCOL RUN: NOT FULL is expected here (old slate).
D=$(cd "$(dirname "$0")" && pwd); S="$D/../build_live.py"; A="$D/../../archive/wk8_wk9_chat"; O=$(mktemp -d)
NFL_KEEP_OUT="DeVonta Smith,Garrett Wilson,Dontayvion Wicks,Treylon Burks,CJ Donaldson,KaVontae Turpin,Britain Covey" python3 "$S" "$A/fanduel_inputs/6e4ac99d-FanDuel-NFL-2026_PST-11_PST-08_PST-136184-players-list-1.csv" "$D/wk9_lines.csv" "$A/wk9/props" "$D/nflverse_2026_wk1-8_trimmed.csv" 9 "$A/fanduel_inputs/9e8c48a8-FanDuel-NFL-2026-11-08-136184-entries-upload-template-1.csv" "$O/out.csv" "$D/../../linestar/live/2026-11-08_0925_raw.json.gz" > "$O/run.log" 2>&1
rc=0
python3 - "$O/out_lineups.json" "$A/wk9/lineups_v16.csv" <<'PY' || rc=1
import json,csv,sys
m=json.load(open(sys.argv[1])); ref={}
for r in csv.DictReader(open(sys.argv[2])): ref.setdefault(int(r['lineup']),set()).add(r['id'])
mine=[set(x.split(':')[0] for x in l) for l in m['shadows']['shadow_v16']['lineups']]
n=sum(ref[k]==mine[k-1] for k in sorted(ref) if k<=len(mine))
print(('PASS 1' if n==15 else 'FAIL 1')+f': v1.6 shadow matches the real Week 9 v1.6 build on {n} of 15 lineups'); sys.exit(0 if n==15 else 1)
PY
if cmp -s "$O/out.csv" "$D/expected_v18_wk9_upload.csv"; then echo "PASS 2: v1.8 upload equals the recorded one"; else echo "FAIL 2: v1.8 output changed (log: $O/run.log)"; rc=1; fi
echo "script hash: $(sha256sum "$S" | cut -c1-16)   (must equal the hash in NFL_FD_v18_protocol.md)"; exit $rc
