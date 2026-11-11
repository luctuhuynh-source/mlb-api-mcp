# NBA FanDuel live build - canonical script

`build_live.py` is the ONLY script that builds live lineups. Run it as-is. Never retype the rules from notes or memory.
If a session cannot find this script, the build stops and Phong is told. No rebuild from notes (v1.4 rule 1).
The rules it runs are protocol **v1.4**, in force from 2026-11-11 (`NBA_FD_v14_protocol.md` in this folder is a copy of the doc section).

```
python3 backtests/nba/live/build_live.py <fd_players_list.csv> <linestar_players.csv> <linestar_projown.csv> <linestar_main_slate_id> \
        <fd_entries_template.csv> <out_upload.csv> "<starters, comma separated>" "<extra exclusions, comma separated>"
```

- Use the newest `linestar/live/*_players.csv` + `*_projown.csv` pair (the matching `*_raw.json.gz` next to it supplies AggProj); the Main slate id is the slate in the projown file that matches the FanDuel slate's games.
- Starters come from the RotoWire lineups tool, pulled in the same refresh as the LineStar file.
- Output: the FanDuel upload CSV and `<out>_lineups.json`, the run's manifest (script version + hash, mode, input files + hashes, snapshot, game-log date, eligible list, objective, the live set and the shadow sets: v1.3 as written, pure LineStar on the v1.4 structure, the v1.4 projection with max 3 of 4). Save the json to `backtests/nba/lineups/`.
- Which set is uploaded: env `NBA_LIVE` = `v14` (default, the protocol in force), `v13`, `v14cand` or `v14nocap`. Only switch it when Phong says so.
- If the live set cannot produce four lineups the script stops with a `PROTOCOL RUN: STOPPED` line and writes nothing. (v1.3 did this on about 40% of 11-12 game slates in the backtest; the v1.4 set never did.)
- Lineups are written with early games in the base position slots and the latest games in UTIL, G/F and F/C (rule 14).
- Regression test: `sh backtests/nba/live/regression/regress.sh` (inputs and expected uploads are in `regression/`). v1.3 mode must reproduce the 11/7 upload byte for byte and the default mode the recorded v1.4 upload. Run it after any change to the script.

## Full run or notify (rule 1)
Phong's rule of 11/11: either the full protocol is run, or he is told that it was not and what is missing.
- The script ends every run with a block that starts `PROTOCOL RUN: FULL` or `PROTOCOL RUN: NOT FULL - n item(s)`, or it stops with `PROTOCOL RUN: STOPPED - <reason>` and writes nothing. That block goes at the very top of the reply to Phong, word for word, on the first build and on every rebuild. The result is also saved in the manifest under `protocol_run`.
- A reply with lineups and no such line means the script did not run. Treat those lineups as not built by the protocol.
- The session passes three things; without them the run is NOT FULL:
  - `NBA_RATIFIED_SHA` = the script hash written in rule 1 of the protocol doc (currently `946a997b4aa3d633`, version 2026-11-11f). Read it from the doc, not from this file.
  - `NBA_REFRESH` = the Pacific time the starting lineups and the injury report were pulled, e.g. `"3:47 PM"`. More than 20 minutes from the LineStar pull is flagged.
  - `NBA_PRIMARY` = part of the primary contest's name, only when the upload template holds two contests.
  - Optional: `NBA_LOCK="4:00 PM"` overrides the lock time (default: first tip in the LineStar file, Pacific).
- The script checks the rest itself: it is the unmodified repo copy; live set = v14; the LineStar files are one pull, dated today, the newest of the day, no more than 25 minutes before lock; projections for every game (15 or fewer projected players = expired cookie = STOPPED); AggProj on 90%+ of the eligible players; the LineStar slate fits the FanDuel list; game logs through yesterday; five starters matched for every team; every starter and exclusion name matched to the FanDuel list; no listed starter without a projection; shadow sets built; the upload file re-read and validated; contests in the template within rule 19.
- Example of a full run:
```
NBA_RATIFIED_SHA=<hash from the doc> NBA_REFRESH="3:47 PM" python3 backtests/nba/live/build_live.py <fd_players_list.csv> \
    backtests/nba/linestar/live/<stamp>_players.csv backtests/nba/linestar/live/<stamp>_projown.csv <linestar_slate_id> \
    <fd_entries_template.csv> <out_upload.csv> "<starters>" "<extra exclusions>"
```
- The check covers the build through the upload file. It does not cover the recheck before lock, late swap (rules 15-18), contest choice by rake (rule 21) or grading.
- Changing the script: only on Phong's say. Bump the version date in `VERSION`, run `regression/regress.sh`, write the new hash into rule 1 of the protocol doc and into `NBA_FD_v14_protocol.md`, then push.

# results/
- `b76*`: 11/6-11/7 rule ablation (fantasy points only; superseded by B77).
- `b77.py`, `b77b.py`, `b77c.py` + results: 11/10 field-relative backtest (stage 1 full history, stage 2-3 AggProj era).
- `b77_support/`: field model calibration, projection audit, ownership calibration, lock-time gap, live-window rebuilds. Run order: parse_raw.py, master.py, field_cal.py, then the others.
- `b78/`: 11/11 tests for the Gemini and ChatGPT review rounds (run from a folder that also holds the b77_support files).
  - `gate_q2.py`, `gate_q2b.py`: is AggProj's edge there BEFORE lock? Player level and lineup level on the pre-lock pulls, plus the look-ahead gap.
  - `kappa_cv.py`: leave-one-slate-out check of a regression for the field-SD multiplier (rejected). `stop_boot.py`: stop-rule error rates.
  - `swap_q7c.py`: late-swap rules walked forward one tip window at a time on the real pre-lock lineups (upper bounds; final values are not timestamped).
  - `b78a.py`: structure tests on 164 slates (hybrid exposure, dead caps, ceiling 0.25, game stack, cumulative-ownership cap). `b78h.py`: archive haircut for starters named after the pull. `b78_summary.py`: tables.
  - `cg_field.py`: date-held-out field-model calibration and same-slate contest comparison. `gate_cg.py`: pre-lock replays (projection x exposure, overlap 8, look-ahead split, two snapshot times, exact payouts). `b79.py`: team cap 3 vs 4, cheap-teammate cap, contrarian cap, ceiling 0.2, ownership tie-break, overlap 8 on 164 slates.

# reviews/
The 11/10 review packet, Gemini's and ChatGPT's answers, and the manager's grade of each.
