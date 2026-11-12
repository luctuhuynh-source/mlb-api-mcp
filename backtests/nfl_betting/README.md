# NFL betting protocols - rule record, run checklist, audit

Built 2026-11-11 at Phong's direction ("Start with the NFL betting protocol... A full audit and such protocol rules are in repo").
The football doc ("Football Execution Engines - CFB + NFL system prompts") stays the source; these files are a flat, numbered copy so
a new chat cannot run half the rules without saying so.

**Start here: `REVIEW_2026-11-11.md`** (the protocol review Phong asked for on 11/11: verdict by version, the push-table fix, decisions
waiting on him), **`RULES_CURRENT.md`** (the one flat rule list a board is run from) and **`BACKTEST_2026-11-12.md`** (backtests of the six
proposed engine changes and the case for a separate totals track; nothing in it is in force).

| File | What it is |
|---|---|
| `REVIEW_2026-11-11.md` | The 11/11 review: results by version, closing-line value, 12-season FLOW check, what was fixed, decisions for Phong |
| `BACKTEST_2026-11-12.md` + `backtest_2026-11-12/` | 11/12 backtests: lean and total rules against real second-half lines 2011-2021, totals key numbers and half-point values, wind, a stand-in engine test on the 45 closing snapshots, what a paid test would cost. Scripts, outputs and the decoded second-half line file |
| `TOTALS_PROTOCOL_v0.2.md` | NFL Totals protocol v0.2, final text after the panel review of 11/12: a paper ledger for Under cells (wind, first-half score), rules T-01 to T-15, a two-level gate. NOT IN FORCE. Its cells failed the paid replication of 11/12 (BACKTEST section 15), so nothing in it prints |
| `TOTALS_PROTOCOL_v0.2_DRAFT.md` | The draft the panel reviewed: what the earlier MLB Over and Under protocols and the early NFL totals fires showed, the NFL cells put through the same gate, draft rules, draft test plan. Superseded by the final text |
| `panel_2026-11-12/` | The review panel on the totals rewrite (Gemini as scout, ChatGPT as doubter; Claude is the manager): both prompts, both replies as received, `PANEL_RULING_2026-11-12.md` (every finding ruled on), and the manager's check scripts 40 to 42 with their outputs |
| `backtest_2026-11-12/halftime_pull/` | The paid pull, run 11/12 (50,072 credits): `TEST_PLAN_LOCKED.md` (six claims, fixed before any price was graded), the two plan files, the halftime clock for 990 games, the pulled quotes (`pulled_*.csv.gz`), collector 22, grading scripts 24 and 25 and their outputs. Results: BACKTEST section 15. Also the flow-against-totals screen of 11/12: `FLOW_TOTALS_TEST_PLAN.md`, scripts 26 to 28, `h1_flow_2023_2026.csv`; results in BACKTEST section 16 |
| `backtest_2026-11-12/robinhood_pilot/` | Robinhood (Kalshi) price history against the books' fair at the 45 saved closes: plan, quotes, scripts 30 to 32, outputs |
| `TOTALS_TRACK_v0.1.md` | NFL Totals track v0.1, written 11/12 and put ON HOLD the same hour pending the rewrite. Not run. Table B-NFL-5 |
| `RULES_CURRENT.md` | Numbered rules in force today (1H v0.6c / 2H v0.6b, rules text 2026-11-12): v0.5 + the eight changes + one reading per contradiction + the push-table fix |
| `PUSH_TABLE_B-NFL-3.md` + `push_table_onesided_2015_2026.csv` | One-sided exact-margin table (push probability of a line), 2015-2026. Replaces the either-team table for HOOK pricing and number conversions |
| `clv_1h_2026-10-18_to_11-05.csv` | Closing-line value for every first-half lean and fire in the rebuilt ledger |
| `clv_2h_2026-10-18_to_11-05.csv` | The same for every second-half lean and fire (24 entries). Halftime and 3Q kickoff clock times for those games: `review_2026-11-11/halftime_clock_2026-10-18_to_11-05.csv` |
| `review_2026-11-11/` | Data and scripts behind the review (closing-line snapshots, nflverse half scores 2015-2026, the four analysis scripts and their output) |
| `RULES_v05_baseline.md` | Numbered rules of the FROZEN versions (10/11/2026 freeze): NFL FG+1H v0.5, NFL 2H v0.5, Game-flow read v1.1, Robinhood venue rules v1.0 |
| `POST_FREEZE_CHANGES.md` | The eight changes made after the freeze (date, version, Phong's words). All kept: Phong ruled the current profile in force on 11/12 |
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
`profile` in the checklist is `v05` (strict frozen baseline, run from `RULES_v05_baseline.md`) or `current` (v0.6c 1H / v0.6b 2H,
run from `RULES_CURRENT.md`). The checker prints the rule list it used and that file's hash.
**The profile in force is `current`** (Phong, 11/12/2026: "Current but make this can fire by any books instead of dsb only."). A board runs `v05` only when he asks for it, and the checker
then prints a note saying so. The push-table fix (check C36) applies to both profiles: it is a formula fix.
