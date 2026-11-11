#!/bin/sh
# Regression test for build_live.py. Run after ANY change to the script, before it is used for a live build:
#     sh backtests/nba/live/regression/regress.sh
# Both lines must say PASS. The runs print PROTOCOL RUN: NOT FULL (test mode, old pull) - that is expected here.
D=$(cd "$(dirname "$0")" && pwd); S="$D/../build_live.py"; L="$D/../../linestar/live"; O=$(mktemp -d)
P="$D/FanDuel-NBA-2026-11-07-136378-players-list.csv"; T="$D/FanDuel-NBA-2026-11-07-136378-entries-upload-template.csv"
ST=$(cat "$D/starters.txt"); EX=$(cat "$D/excludes.txt"); rc=0
NBA_LIVE=v13 NBA_ASOF=2026-11-07 python3 "$S" "$P" "$L/2026-11-07_1445_players.csv" "$L/2026-11-07_1445_projown.csv" 30544 "$T" "$O/v13.csv" "$ST" "$EX" > "$O/v13.log" 2>&1
if cmp -s "$O/v13.csv" "$D/expected_v13_upload.csv"; then echo "PASS 1: v1.3 mode reproduces the 11/7 upload byte for byte"; else echo "FAIL 1: v1.3 mode no longer reproduces the 11/7 upload (log: $O/v13.log)"; rc=1; fi
NBA_ASOF=2026-11-07 python3 "$S" "$P" "$L/2026-11-07_1445_players.csv" "$L/2026-11-07_1445_projown.csv" 30544 "$T" "$O/v14.csv" "$ST" "$EX" > "$O/v14.log" 2>&1
if cmp -s "$O/v14.csv" "$D/expected_v14_upload.csv"; then echo "PASS 2: default (v1.4) mode reproduces the recorded v1.4 upload byte for byte"; else echo "FAIL 2: default mode no longer reproduces the recorded v1.4 upload (log: $O/v14.log)"; rc=1; fi
echo "script hash: $(sha256sum "$S" | cut -c1-16)   (must equal the hash in rule 1 of the protocol doc)"
exit $rc
