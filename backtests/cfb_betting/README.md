# CFB betting - run package (started 2026-11-12)

Phong, 11/12/2026: "package the betting protocols". Same shape as `../nfl_betting/`: a rule list, a checklist the chat fills on every board, and a checker that prints the status line.

| File | What it is |
|---|---|
| `RULES_CFB_2H_CURRENT.md` | CFB 2H v2.3b as a flat list (IDs X-01 to X-25), with the dead text named. Written from the tab; not yet audited line by line |
| `run_checklist_cfb_2h.json` | 27 checks, in run order |
| `check_run.py` | `python3 check_run.py runs/<file>.json` prints PROTOCOL RUN: FULL or NOT FULL |
| `CFB_2H_tab.txt`, `CFB_1H_tab.txt`, `GAME_FLOW_tab.txt`, `ROBINHOOD_tab.txt` | The football doc's tabs as exported 11/12/2026, 5:20 AM. Snapshots: the doc is the live text |
| `runs/` | Filled checklists |

**Not packaged yet:** CFB 1H v2.0e (tab text is here, no rule list or checklist), golf, Liem F5. The checker says so if asked for 1H.
