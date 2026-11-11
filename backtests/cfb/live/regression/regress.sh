#!/bin/sh
# Regression test for the CFB build_live.py. Run after ANY change to the script:  sh backtests/cfb/live/regression/regress.sh
# The FanDuel list here is a stand-in rebuilt from the 11/7 LineStar pull (the real 11/7 FanDuel files were not kept). With it the script
# must give the four lineups entered on 11/7 (Weigman core; projections 133.7, 131.7, 131.4, 126.8). PROTOCOL RUN: NOT FULL is expected here.
D=$(cd "$(dirname "$0")" && pwd); S="$D/../build_live.py"; L="$D/../../linestar/live"; O=$(mktemp -d)
python3 "$S" "$D/FanDuel-CFB-2026-11-07-136266-players-list-SYNTH.csv" "$L/2026-11-07_0830_players.csv" "$L/2026-11-07_0830_projown.csv" 4596 "$D/FanDuel-CFB-2026-11-07-136266-entries-upload-template-SYNTH.csv" "$O/out.csv" "$(cat "$D/qb_gate.txt")" "$(cat "$D/core.txt")" > "$O/run.log" 2>&1
if cmp -s "$O/out.csv" "$D/expected_upload.csv"; then echo "PASS: reproduces the four 11/7 lineups byte for byte"; rc=0; else echo "FAIL: the 11/7 lineups are no longer reproduced (log: $O/run.log)"; rc=1; fi
echo "script hash: $(sha256sum "$S" | cut -c1-16)   (must equal the hash in section 17 of the protocol doc)"; exit $rc
