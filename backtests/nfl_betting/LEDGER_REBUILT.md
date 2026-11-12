# NFL betting ledger - rebuilt from the chat archives (10/18 to 11/5/2026)

Rebuilt 2026-11-11 at Phong's direction ("Rebuilt from archive"). Row-level data: `ledger_rebuilt_2026-10-18_to_11-05.csv` (48 rows, IDs R01-R48).

## How it was built
- **Rows:** every lean, engine fire and parlay listed in the eight transcript-only reports in `archive/`. Nothing was taken from the running log for 10/18-11/5.
- **Grades:** as graded in the chat that ran the board, where it graded. Nine entries were never graded in their chats; they were graded 11/11 from ESPN linescores (the `get_football_scoreboard` pull for 10/19, 10/25, 11/1 and 11/2). Those nine are marked in the CSV and listed in section 5. All nine games ended in regulation.
- **Old shadow numbers are dropped.** Two chats numbered 2H shadows independently and collided: "#33-#44" in the 10/18-10/25 chat are different bets from "#33-#42" in the running log. Rows here carry new IDs only.
- **Closing lines:** none when this was built. Added later on 11/11: first-half closes for all 22 first-half entries and the one full-game lean (`clv_1h_2026-10-18_to_11-05.csv`). The first-half leans beat the books' closing price 18 of 21 but closed 1.0 point worse than the no-vig fair on average. Second-half closes were pulled after that (`clv_2h_2026-10-18_to_11-05.csv`): the 21 second-half leans were priced 0.2 points worse than fair on average, the 3 second-half fires 2.6 points better. See `REVIEW_2026-11-11.md` sections 2 and 12.
- DSB and Red105 are paper accounts. Robinhood is live money (one row: 11/5 JAX 1H).

## 1. Record, 10/18 to 11/5 (archive-backed)

| Class | Record | Was carried as |
|---|---|---|
| 1H leans | **12-8-1** | 9-3 for the same dates (15-5 since 10/11, less 6-2 on 10/11) |
| 2H leans | **8-12-1** | about 5-3 graded, with five ungraded |
| Engine fires | **4-0** as issued (2H 3-0, 1H 1-0); **3-0 valid** | 1-0 with one ungraded |
| Full-game lean | 1-0 | not carried |
| Parlay | 0-1 | not carried |

What moved the numbers:
- **Added - never in the running log:** 10/19 SF -4 1H (W); 10/22 NE@CHI 1H, FG and 2H leans (3 W); the whole 10/25 Sunday slate (1H 2-4-1, 2H 1-3, parlay L); 10/25 KC +2.5 1H (L); six more 10/18 2H leans (1-4-1) and the two 10/18 engine fires (2 W).
- **Graded for the first time:** five 11/1 2H leans (2-3), the 11/1 LAR -3 fire (W), SF -4, KC +2.5, CHI +1 2H.
- **Detail filled in:** the 10/29 GB lean was GB -2.5 1H @ DSB -110 (CAR@GB, half 20-10).

**LAR -3 2H (R44), added 11/11:** the play-by-play clock puts the 3Q kickoff of LAC@LAR at 2:40:23 PM PT. The fire was issued about 2:52 PM. It was issued after the second half had started and is not a valid fire. It stays in the file as issued, tagged.

## 2. By day

| Date | 1H leans | 2H leans | Engine fires | Other | Version in force (see `VERSION_BY_DATE.md`) |
|---|---|---|---|---|---|
| Sun 10/18 | 4-2 | 1-6-1 | 2-0 (Over 24.5 CHI@ATL, ARI +6.5) | | v0.6; doc not opened |
| Mon 10/19 | 1-0 | | | | v0.6; doc not opened, no FLOW |
| Thu 10/22 | 1-0 | 1-0 | | FG lean 1-0 | v0.6; doc not opened |
| Sun 10/25 | 2-5-1 | 1-3 | | parlay 0-1 | v0.6; 1H boards ran no written version |
| Mon 10/26 | 1-0 | 1-0 | | | v0.6; both tabs read |
| Thu 10/29 | 1-0 | pass | | | v0.6; 1H tab read, 2H from notes |
| Sun 11/1 | 1-1 | 2-3 | 1-0 (LAR -3 2H) | | 1H v0.6a, 2H v0.6 then v0.6a; from memory |
| Mon 11/2 | pass | 1-0 | 1-0 (CHI +2.5 1H) | | v0.6a; from memory |
| Thu 11/5 | 1-0 | 1-0 | | | v0.6a; both tabs read |

Split of the 1H leans by how the board was run:
- The eight leans from boards that used a "structural" input in place of FLOW (10/19 and the 10/25 Sunday chat): **3-4-1**.
- The other thirteen: **9-4**.
- The five boards shown to have run from the written tab (10/26 x2, 10/29 1H, 11/5 x2): **5-0**. Five results is not a sample.

## 3. Since the 10/11 freeze (rebuilt range plus the un-archived days)

The days outside 10/18-11/5 have no archive report yet. They are carried from the running log and marked as such.

| Class | 10/11-10/15 (log only) | 10/18-11/5 (archives) | 11/8-11/9 (log only) | Total since 10/11 |
|---|---|---|---|---|
| 1H leans | 6-2 | 12-8-1 | 0-1 (NE -1.5, printed after kickoff) | **18-11-1** |
| 2H leans | 9-5 | 8-12-1 | 2-0 (SF -1.5, HOU PK) | **19-17-1** |
| Engine fires | 0 | 4-0 | 0 | **4-0** |

Old headlines these replace: 1H leans "15-5"; 2H-SHADOW "21-13" (24-13 with late grades); engine "1-0 + LAR -3 ungraded". The season 2H figure before 10/11 (10-6 on entries #1-#16) is untouched and not included above.

## 4. Tickets, as recorded

Sizes are only as good as the words behind them. "Phong stated" means he said it in the chat; "assumed" means the chat graded at the size it had advised and he never confirmed.

| Date | Tickets | Net as recorded | Status |
|---|---|---|---|
| 10/18 | all leans $300 to win except HOU 1H; both fires $500 | 1H +$291, fires +$1,000, 2H leans -$1,980 = **-$689** | Phong stated |
| 10/22 | CHI 1H, FG, 2H at $500 each | **+$1,500** | Phong stated |
| 10/25 | CIN and DEN $500, other leans $300, $150 parlay | 1H -$850, 2H -$616 = **-$1,466** | assumed, never confirmed |
| 10/26 | DAL 1H and 2H, $300 each | **+$600** | Phong stated |
| 10/29 | GB 1H, $300 | **+$300** | Phong stated 11/1 |
| 11/1 | none stated | - | LAR -3 fire placement unconfirmed |
| 11/2 | CHI +2.5 1H $300 | **+$300** | Phong stated |
| 11/2 | CHI +1 2H | +$300 or $0 | CONFLICT: the 11/2 chat has "I'll pass then."; the 11/9 log says he bet it |
| 11/5 | JAX 1H (Robinhood, live), JAX 2H $300 | **+$600** at stated sizes | 1H fill unresolved: "placed 300" vs 1,028 contracts (about $535 risk / $493 to win) |

Stated tickets, excluding the two unresolved items: **+$2,611**. Including 10/25 as assumed: **+$1,145**. All paper except the 11/5 Robinhood ticket.

## 5. The nine entries graded 11/11 from ESPN linescores

| ID | Date | Entry | Score | Grade |
|---|---|---|---|---|
| R17 | 10/19 | SF -4 1H | half SF 20-3 | W |
| R28 | 10/25 | KC +2.5 1H | half SEA 10-0 | L |
| R39 | 11/1 | NYJ +3 2H | 2H LV 24-10 | L |
| R40 | 11/1 | PIT -0.5 2H | 2H PIT 7-0 | W |
| R41 | 11/1 | MIA +7 2H | 2H NE 21-6 | L |
| R42 | 11/1 | KC +1 2H | 2H DEN 15-7 | L |
| R43 | 11/1 | WAS -1 2H | 2H WAS 14-0 | W |
| R44 | 11/1 | LAR -3 2H (engine fire) | 2H LAR 14-0 | W |
| R46 | 11/2 | CHI +1 2H | 2H CHI 21-8 | W |

The 10/25 and 11/1 chat grades already in the archives were re-checked against the same linescores; none changed.

## 6. Still open
- (Closed 11/11: closing lines are now on every row of 10/18 to 11/5, both halves.)
- 10/25 ticket sizes; the 11/2 CHI 2H ticket conflict; the 11/5 JAX 1H fill size; whether the LAR -3 fire was placed.
- No archive report yet for 10/11-10/15 (in the "NFL betting protocols" chat, outside the range it was asked for), the 11/8 afternoon chat (LV@SF, HOU@LAC 2H) or 11/9 BUF@MIN.
- Paper no-bets on NO CLEAR LEAN games were never graded on the close and are not counted here.
- 11/6 CFB games run on the NFL 2H shape are not NFL entries and are left out.
- `AUDIT_2026.md` sections 1, 2 and 4 were written from the running log before these archives existed; this file supersedes their records for 10/18-11/5.
