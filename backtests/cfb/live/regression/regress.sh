#!/bin/sh
# Regression test for the CFB build_live.py. Run after ANY change to the script:  sh backtests/cfb/live/regression/regress.sh
# Uses the real 11/7 FanDuel files (backtests/cfb/archive/2026-11-07_chat) and the 8:30 LineStar pull. The script must reproduce the
# file uploaded on 11/7 byte for byte. PROTOCOL RUN: NOT FULL is expected here (old pull, no refresh time).
D=$(cd "$(dirname "$0")" && pwd); S="$D/../build_live.py"; L="$D/../../linestar/live"; A="$D/../../archive/2026-11-07_chat"; O=$(mktemp -d)
python3 "$S" "$A/attachments/FanDuel-CFB-2026_PST-11_PST-07_PST-136266-players-list-1.csv" "$L/2026-11-07_0830_players.csv" "$L/2026-11-07_0830_projown.csv" 4596 "$A/attachments/FanDuel-CFB-2026-11-07-136266-entries-upload-template-3.csv" "$O/out.csv" "$(cat "$D/qb_gate.txt")" "$(cat "$D/core.txt")" > "$O/run.log" 2>&1
if cmp -s "$O/out.csv" "$A/uploads_sent/FanDuel-CFB-2026-11-07-upload-v14-FINAL.csv"; then echo "PASS: reproduces the 11/7 upload byte for byte"; rc=0; else echo "FAIL: the 11/7 upload is no longer reproduced (log: $O/run.log)"; rc=1; fi
echo "script hash: $(sha256sum "$S" | cut -c1-16)   (must equal the hash in section 17 of the protocol doc)"; exit $rc
