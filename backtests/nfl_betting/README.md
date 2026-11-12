# NFL betting protocols - rule record, run checklist, audit

Built 2026-11-11 at Phong's direction ("Start with the NFL betting protocol... A full audit and such protocol rules are in repo").
The football doc ("Football Execution Engines - CFB + NFL system prompts") stays the source; these files are a flat, numbered copy so
a new chat cannot run half the rules without saying so.

**Start here: `REVIEW_2026-11-11.md`** (the protocol review Phong asked for on 11/11: verdict by version, the push-table fix, decisions
waiting on him) and **`RULES_CURRENT.md`** (the one flat rule list a board is run from).

| File | What it is |
|---|---|
| `REVIEW_2026-11-11.md` | The 11/11 review: results by version, closing-line value, 12-season FLOW check, what was fixed, decisions for Phong |
| `RULES_CURRENT.md` | Numbered rules in force today (1H v0.6c / 2H v0.6a, rules text 2026-11-11): v0.5 + the seven changes + one reading per contradiction + the push-table fix |
| `PUSH_TABLE_B-NFL-3.md` + `push_table_onesided_2015_2026.csv` | One-sided exact-margin table (push probability of a line), 2015-2026. Replaces the either-team table for HOOK pricing and number conversions |
| `clv_1h_2026-10-18_to_11-05.csv` | Closing-line value for every first-half lean and fire in the rebuilt ledger |
| `review_2026-11-11/` | Data and scripts behind the review (closing-line snapshots, nflverse half scores 2015-2026, the four analysis scripts and their output) |
| `RULES_v05_baseline.md` | Numbered rules of the FROZEN versions (10/11/2026 freeze): NFL FG+1H v0.5, NFL 2H v0.5, Game-flow read v1.1, Robinhood venue rules v1.0 |
| `POST_FREEZE_CHANGES.md` | The seven changes made after the freeze (date, version, Phong's words), each waiting for keep / drop |
| `CONTRADICTIONS.md` | Every place the doc tabs disagree with themselves or with each other, each with its status after the review |
| `AUDIT_2026.md` | Board-by-board audit of this season, results split by version in force |
| `run_checklist_template.json` | The checklist a chat fills in on every NFL board |
| `check_run.py` | Reads a filled checklist, prints `PROTOCOL RUN: FULL` or `PROTOCOL RUN: NOT FULL - n item(s)` |
| `VERSION_BY_DATE.md` | Version in force and what was actually run, board by board, 10/25 to 11/5/2026 (built from the `archive/` transcript reports) |
| `LEDGER_REBUILT.md` + `ledger_rebuilt_2026-10-18_to_11-05.csv` | The lean / fire ledger for 10/18 to 11/5 rebuilt row by row from the `archive/` reports; supersedes the running-log records for those dates |
| `archive/` | Transcript-only reports of each NFL betting chat, with the screenshots Phong sent |

## Full run or notify
Every NFL board reply opens with the line `check_run.py` prints, word for word.
```
python3 backtests/nfl_betting/check_run.py <filled_checklist.json>
```
Limit, stated plainly: the DFS scripts verify their own inputs. This checker cannot. It verifies that every rule of the chosen
profile was answered (done, or not applicable with a reason, or skipped) - it relies on the chat filling the checklist honestly.
A skipped item or an item left blank is NOT FULL. Saved checklists go in `runs/`.

## Profile
`profile` in the checklist is `v05` (strict frozen baseline, run from `RULES_v05_baseline.md`) or `current` (v0.6c 1H / v0.6a 2H,
run from `RULES_CURRENT.md`). The checker prints the rule list it used and that file's hash.
Which profile is in force is Phong's call. The 11/11 review recommends `current` (decision 1 in `REVIEW_2026-11-11.md`); until he
rules, a chat states the profile it ran at the top. The push-table fix (check C36) applies to both profiles: it is a formula fix.
