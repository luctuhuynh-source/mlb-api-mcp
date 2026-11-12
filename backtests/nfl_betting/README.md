# NFL betting protocols - rule record, run checklist, audit

Built 2026-11-11 at Phong's direction ("Start with the NFL betting protocol... A full audit and such protocol rules are in repo").
Nothing here changes a rule. The football doc ("Football Execution Engines - CFB + NFL system prompts") stays the source; these files
are a flat, numbered copy so a new chat cannot run half the rules without saying so.

| File | What it is |
|---|---|
| `RULES_v05_baseline.md` | Numbered rules of the FROZEN versions (10/11/2026 freeze): NFL FG+1H v0.5, NFL 2H v0.5, Game-flow read v1.1, Robinhood venue rules v1.0 |
| `POST_FREEZE_CHANGES.md` | The seven changes made after the freeze (date, version, Phong's words), each waiting for keep / drop |
| `CONTRADICTIONS.md` | Every place the doc tabs disagree with themselves or with each other |
| `AUDIT_2026.md` | Board-by-board audit of this season, results split by version in force |
| `run_checklist_template.json` | The checklist a chat fills in on every NFL board |
| `check_run.py` | Reads a filled checklist, prints `PROTOCOL RUN: FULL` or `PROTOCOL RUN: NOT FULL - n item(s)` |

## Full run or notify
Every NFL board reply opens with the line `check_run.py` prints, word for word.
```
python3 backtests/nfl_betting/check_run.py <filled_checklist.json>
```
Limit, stated plainly: the DFS scripts verify their own inputs. This checker cannot. It verifies that every rule of the chosen
profile was answered (done, or not applicable with a reason, or skipped) - it relies on the chat filling the checklist honestly.
A skipped item or an item left blank is NOT FULL. Saved checklists go in `runs/`.

## Profile
`profile` in the checklist is `v05` (strict frozen baseline) or `current` (v0.6c 1H / v0.6a 2H, everything in the doc today).
Which profile is in force is Phong's call (asked 11/11, undecided). Until he rules, a chat states the profile it ran at the top.
