# NFL FanDuel live build - canonical script

`build_live.py` is the ONLY script that builds live NFL lineups. Run it as-is. Never retype the rules from notes or memory.
If a session cannot find this script, the build stops and Phong is told. No rebuild from notes.
Rules: `NFL_FD_v18_protocol.md` in this folder (v1.8, in force from Week 10, 2026-11-15). It also holds the ratified script hash.
**Status: assembled 2026-11-11 from the Week 8 and Week 9 builders; v1.8 had never been built before. Tested only on stand-in inputs. Week 10 is its first real run - do a night-before build on Saturday.**

```
NFL_RATIFIED_SHA=<hash from NFL_FD_v18_protocol.md> NFL_REFRESH="9:35 AM" python3 backtests/nfl/live/build_live.py <fd_players_list.csv> \
    <lines.csv> <props_dir> <nflverse_stats_player_week_2026.csv> <week> <fd_entries_template.csv> <out_upload.csv> [<linestar_raw.json.gz>]
```

What the session prepares (one refresh, Sunday about 9:30 AM Pacific; lock 10:00):
1. **lines.csv** with header `away,home,home_spread,total`: one row per Main game, FanDuel team abbreviations, home spread negative when the home team is favoured. Source: `get_event_odds` (sport americanfootball_nfl, markets spreads,totals), consensus point.
2. **props_dir**: one JSON per game from `get_event_odds` with `event_id` and markets `player_pass_yds,player_pass_tds,player_rush_yds,player_reception_yds,player_receptions,player_anytime_td`, odds_format american, saved verbatim (large results are auto-saved by the harness; copy that file).
3. **nflverse**: `stats_player_week_2026.csv` from the nflverse-data `stats_player` release on GitHub.
4. FanDuel players list (re-downloaded after inactives) and entries template, from Phong.
5. Optional: the newest `backtests/nfl/linestar/live/*_raw.json.gz` for the ownership log.

Output: the upload CSV (QB, RB, RB, WR, WR, WR, TE, FLEX, DEF) and `<out>_lineups.json` (live 15, both shadows, compliance lines, run check). Save the json to `backtests/nfl/lineups/` before lock.

## Full run or notify
- The script ends with `PROTOCOL RUN: FULL` or `PROTOCOL RUN: NOT FULL - n item(s)`, or stops with `PROTOCOL RUN: STOPPED - <reason>`. That block goes at the very top of the reply, word for word.
- Checked: unmodified repo copy and ratified hash; lines and props for every game; props no older than 90 minutes at lock; 150+ priced skill players; nflverse through last week; injury tags present; inactives time recorded (`NFL_REFRESH`); 15 lineups; no relaxation; C1-C7 compliance; shadows; the upload file re-read and validated.
- Not covered: weather, the 9:50 swap check, replacement-RB calls, the kill-switch tally, grading.
- Regression: `sh backtests/nfl/live/regression/regress.sh` (stand-in inputs).
- Changing the script: only on Phong's say; bump `VERSION`, run the regression, write the new hash into `NFL_FD_v18_protocol.md`, push.
