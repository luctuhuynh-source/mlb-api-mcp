#!/bin/sh
# Regression test for the NFL build_live.py. Run after ANY change:  sh backtests/nfl/live/regression/regress.sh
# These inputs are STAND-INS (Week 9 pool rebuilt from the LineStar pull, made-up props). They prove the script still behaves the same,
# not that it matches a past live build: v1.8 had none before 11/15. PROTOCOL RUN: NOT FULL is expected here.
D=$(cd "$(dirname "$0")" && pwd); S="$D/../build_live.py"; O=$(mktemp -d)
python3 "$S" "$D/FanDuel-NFL-2026-11-08-136184-players-list-SYNTH.csv" "$D/lines.csv" "$D/props" "$D/nflverse_2026_wk1-8_trimmed.csv" 9 "$D/FanDuel-NFL-2026-11-08-136184-entries-upload-template-SYNTH.csv" "$O/out.csv" > "$O/run.log" 2>&1
if cmp -s "$O/out.csv" "$D/expected_upload.csv"; then echo "PASS: same 15 lineups as recorded"; rc=0; else echo "FAIL: output changed (log: $O/run.log)"; rc=1; fi
echo "script hash: $(sha256sum "$S" | cut -c1-16)   (must equal the hash in NFL_FD_v18_protocol.md)"; exit $rc
