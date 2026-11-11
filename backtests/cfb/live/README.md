# CFB FanDuel live build - canonical script

`build_live.py` is the ONLY script that builds live CFB lineups. Run it as-is. Never retype the rules from notes or memory.
If a session cannot find this script, the build stops and Phong is told. No rebuild from notes.
It runs protocol **v1.4** (section 17 of the protocol doc, Claude Doc id `cc22c30c-4f25-4ccd-b33c-ed3e16fba012`), in force from 2026-11-07. `CFB_FD_v14_protocol.md` here is a copy of the rules as run.
Recovered 2026-11-11 from the 11/7 build chat (merge step + build_v14.py with its two edits); it reproduces the four lineups entered on 11/7.

```
CFB_RATIFIED_SHA=<hash from the doc> CFB_REFRESH="8:33 AM" python3 backtests/cfb/live/build_live.py <fd_players_list.csv> \
    backtests/cfb/linestar/live/<stamp>_players.csv backtests/cfb/linestar/live/<stamp>_projown.csv <linestar_slate_id> \
    <fd_entries_template.csv> <out_upload.csv> "<QBs that passed the QB gate>" "<core players, max 2>"
```

- LineStar pull: the Mac pulls Saturdays at 8:30 AM Pacific; first lock is usually 9:00. Use the newest `*_players.csv` + `*_projown.csv` pair of the day. The LineStar slate id is the slate in the projown file that fits the FanDuel list (the script flags a wrong one).
- QB gate list (F2): the session checks each team's starter (`get_cfb_qb_status`, news) and passes the full names, spelled as FanDuel prints them. A QB not on the list cannot be rostered.
- Core (C5): at most two players named before lock who may be in all four lineups.
- Output: the FanDuel upload CSV and `<out>_lineups.json`, the run's manifest (script version + hash, input files + hashes, QB gate list, core, eligible list, the four lineups, the 1-QB and free-choice shadows, the run-check result). Save the json to `backtests/cfb/lineups/`.
- With two QBs the lower-projected one is written in the SuperFLEX column (same points either way).
- Not in the script: the props-hybrid shadow (no documented method yet), later-window QB audits and swaps (C7), grading.

## Full run or notify
Phong's rule of 11/11: either the full protocol is run, or he is told that it was not and what is missing.
- The script ends every run with `PROTOCOL RUN: FULL` or `PROTOCOL RUN: NOT FULL - n item(s)`, or stops with `PROTOCOL RUN: STOPPED - <reason>` and writes nothing. That block goes at the very top of the reply, word for word, on the first build and on every rebuild.
- The session passes `CFB_RATIFIED_SHA` (the hash in section 17 of the doc, currently `2a38d1446c3c6476`, version 2026-11-11a; read it from the doc) and `CFB_REFRESH` (Pacific time the QB gate and injury tags were checked). Optional `CFB_LOCK="9:00 AM"`.
- The script checks the rest: unmodified repo copy; LineStar files one pull, dated today, newest of the day, within 45 minutes of first lock; 16+ projected players (else cookie expired = STOPPED); projections for every game; LineStar slate fits the FanDuel list; injury tags present; every QB-gate and core name matched; both shadows built; the upload file re-read and validated (slots, salary, team caps, stacks, overlap, exposure).
- Regression: `sh backtests/cfb/live/regression/regress.sh` must say PASS after any change. The FanDuel list in `regression/` is a stand-in rebuilt from the 11/7 LineStar pull, because the real 11/7 FanDuel files were not kept.
- Changing the script: only on Phong's say. Bump `VERSION`, run the regression, write the new hash into section 17 of the doc and into the protocol copy here, then push.
