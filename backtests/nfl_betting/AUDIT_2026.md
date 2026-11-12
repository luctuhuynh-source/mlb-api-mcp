# NFL betting - 2026 season audit (9/24 to 11/9)

> **Superseded in part (2026-11-11, later the same day).** The records in sections 1, 2 and 4 for 10/18 to 11/5 came from the running log. The chat archives show that log missed the 10/19, 10/22 and 10/25 boards, six 10/18 2H leans and two 10/18 engine fires. Use `LEDGER_REBUILT.md` for those dates: 1H leans 12-8-1, 2H leans 8-12-1, engine fires 4-0. Sections 3 and 5 are unchanged.

Written 2026-11-11. Evidence: the two running logs kept across chats (NFL betting 9/24-10/31, and the NFL log from 11/1) and the
football doc tabs and change log.

**Limits of this audit - read first**
- It is built from the logs, not from the original chat transcripts. A rule the log does not mention is marked "not evidenced", which means unknown, not skipped.
- All records are hit-only. Closing-line value was pulled once (10/11). No record below shows the protocol beats the price.
- DSB is a paper account per the log; DSB "tickets" are simulated.

## 1. Results by version in force

| Period | Version in force | 1H leans | 1H engine fires | 2H shadows / leans | 2H engine fires |
|---|---|---|---|---|---|
| 9/24 - 10/5 | v0.2 / v0.3 (pre-freeze) | 2-0 (10/5) | 0 | 10-6 (#1-#16) | 4-1 (#1-#5; three were Robinhood price artifacts) |
| 10/11 - 10/12 | **v0.5, the frozen version, as written** | **6-2** | 0 | **9-4** (#17-#29) | 0 |
| 10/15 | v0.6 (CLEAR LEAN, locks still on) | 0-0 (1 game filtered) | 0 | 0-1 (#30) | 0 |
| 10/17 - 10/31 | v0.6 + no time locks + Robinhood | 6-2 | 0 | 1-2 (#31-#33) | 0 |
| 11/1 - 11/8 10 AM | 1H v0.6a / 2H v0.6a | 2-1 | 1-0 (CHI +2.5, 11/2) | 2-0 graded (#39, #40); #34-#38 UNGRADED | LAR -3 (11/1) UNGRADED |
| 11/8 1:05 PM - 11/9 | 1H v0.6b then v0.6c / 2H v0.6a | 0-0 (no lean printed) | 0 | 2-0 (#41, #42) | 0 |
| **Total since 10/11** | | **14-5** | **1-0** | **14-7 graded, 5 ungraded** | **0-0, 1 ungraded** |

Reading it honestly:
- The frozen v0.5 ran as written for two days (10/11 Sunday and 10/12 Monday): 8 graded 1H leans and 13 2H shadows. That is the whole sample behind "it was working well". It is too small to separate from luck, and its 10/11 closing-line check was mixed (1H leans beat the close 4 of 8, mean -0.7; 2H shadows 8 of 11, mean +1.6).
- The 1H lean hit rate did not fall after the freeze was broken: 6-2 under v0.5, 6-2 under v0.6, 2-1 under v0.6a. What fell was volume: 8 leans in 2 days under v0.5; 8 in 2.5 weeks under v0.6; 3 in the 9 days of v0.6a; none on 11/8-11/9.
- The 2H shadows went 1-3 right after the freeze (#30-#33, all four leaning on the halftime leader or the anchor), then 4-0 on the graded November entries.

## 2. Ledger errors found
- L-1 The 1H lean record is carried as **15-5**. The logged entries add up to **14-5**. The extra win enters on 11/1, where the log says "13-4" after the 10/26 DAL and 10/29 GB wins; the items give 12-4. Either one win was never itemised or the count is one too high.
- L-2 The 2H-SHADOW headline says 21-13. With #39, #41 and #42 graded as wins it is 24-13, and #34-#38 (11/1) have not been graded for 10 days.
- L-3 The first engine fire under the HOOK-through-divergence rule (11/1 LAC@LAR, LAR -3 2H @ DSB -105) is ungraded and its placement unconfirmed.
- L-4 11/5 JAX -4.5 1H at Robinhood: two different fill sizes on record (1,028 contracts, about $535 risk, vs "placed 300"). Unresolved.
- L-5 The 10/29 TNF GB 1H lean is logged from Phong's report only: no opponent, number, price or board.

## 3. Rules skipped or applied differently (recurring)
| ID | Rule (baseline ID) | What happened | Evidence |
|---|---|---|---|
| S-1 | CLV on every fire, shadow and lean (F-46, H-42) | Pulled once, for 10/11. Every board from 10/12 on has no close. | "CLV unpulled on Weeks 6-8" repeated on every entry through 11/9 |
| S-2 | FLOW-TOTAL (SHADOW) line on every 2H board (H-38) | Not logged on any board 10/12 - 10/26; the 20-board test has 5 entries instead of about 15 | 10/26 entry "logging GAP found" |
| S-3 | NO CLEAR LEAN games graded as paper no-bets on the close (CLEAR LEAN ledger rule) | Not done systematically; a few "would have won" notes on the half score, none on the close; filtered-game tally not kept after n=4 | 10/15, 11/1, 11/8 entries |
| S-4 | Inactives for every game at T-85 / T-90 (F-18) | 10/11 afternoon PARTIAL; 10/18 inactives reads "owed", HOU +0.5 lean graded with its gate never checked; 11/8 partial on 5 of 7 games | 10/11, 10/18, 11/8 entries |
| S-5 | FLOW on every run (F-06, G-07) | 10/18 TB row not pulled; 11/1 STATIC games got none (by the 11/1 rule); 11/8 missing on 5 of 7; 11/8 GB@NE skipped at T-2 with no rule allowing it | 11/8 entry: "the skip was Claude's error" |
| S-6 | T-20 decision pull and the pull schedule (F-08) | 10/11 afternoon T-20 pulls skipped (no screens); most boards are a single run at whatever time the screen arrives (T-118, T-70, T-64, T-57, T-35, T-2) | 10/11 day-close entry and board timestamps |
| S-7 | Grade everything the next day (output OWED rule) | #1 took 10 days; #9/#10 a day late; Week 6 leans graded 8 days late (10/26); #34-#38 and LAR -3 still open | entries 10/4, 10/26, 11/9 |
| S-8 | DERIV-LAG 20-board log (F-25, H-20: both immediate and persisted signal) | Board count "0/20" on 10/11 and never updated; persistence observations not evidenced on any board | 10/11 entry; nothing later |
| S-9 | Handoff ingestion and per-game log fields (H-07, H-41) | Not evidenced: no board logs HANDOFF VERIFIED / INCOMPLETE; opener status logged on some boards only | logs |
| S-10 | CLEAR LEAN applied as written | 11/8: "two soft inputs aligned" ruled not clear - stricter than the text; with missing FLOW it produced zero leans on a 7-game slate | 11/9 entry: "Claude's stricter-than-text ruling" |
| S-11 | A scheduled run's result is delivered | The 11/8 11:35 scheduled run for the 1:25 games never surfaced; those 1H boards were not run before kickoff | 11/8 entry |
| S-12 | Never bet in-play (F-01) | 11/8 GB@NE: the FLOW read was pulled after kickoff and logged as a paper lean (NE -1.5 1H); Phong bet it; it lost | 11/9 entry |
| S-13 | Sizing and exposure (F-03, M-02) | 9/27-10/11: tickets at $300-$500 vs the unit, side bets on leans, up to three parlays a slate, same-thesis doubles. 11/5: about 1.6u not declared before the price | 9/27, 10/11, 11/5 entries |
| S-14 | Engine fires executed at the venue and price specified | Fires #4 and #5 (10/4) were specified at Robinhood and filled at DSB at zero graded edge | 10/4 entry |
| S-15 | Lean must be price-aligned or neutral, engine price floor is separate | 11/5 JAX: lean printed at DSB -6, then moved to a Robinhood strike priced under the floor (54 all-in vs fair 54-56) and bet at 1.6u | 11/5 entry |

## 4. Board-by-board

Status: OK = nothing in the log shows a rule missed; DEV = deviation, see the S- and L- items.

| Date | Game(s) | Engine / version | Engine result | Lean / shadow and grade | Status |
|---|---|---|---|---|---|
| 9/24 | ATL@GB | 2H v0.1 | none | #1 ATL +6 W (graded 10/4) | DEV S-7; fair derived, no consensus |
| 9/27 | ARI@SF, MIN@TB, BAL@DAL, LV@NO | 2H v0.2 | Fire #1 U21.5 W (filled +100, $300) | #2 W, #3 W, #4 L, #5 W | DEV S-13 (six side tickets, two parlays); four flags killed by the OT veto later retired |
| 9/27 | LAR@DEN | 2H v0.2 | none | #6 LAR +3.5 L | OK |
| 9/28 | PHI@CHI | 2H v0.2 | Fire #2 U23 W | #7 PHI -5.5 L | DEV: fire passed on the modal number, failed on the mean (flagged then) |
| 10/4 | NYJ@CHI, NE@BUF, LAR@PHI | 2H v0.2 | Fire #3 O21.5 L (RH) | #8 L, #9 W, #10 W | DEV S-7; LAR/PHI run with no DSB screen |
| 10/4 | MIA@MIN, KC@LV, DEN@SF, LAC@SEA, DET@CAR | 2H v0.3 | Fires #4 KC -4.5 W, #5 O20.5 W | #11 W, #12 W, #13 W, #14 L, #15 L | DEV S-14; LAC@SEA requested as "CFB 2H", run on NFL 2H |
| 10/5 | ATL@NO | FG+1H v0.3, 2H v0.3 | none | ATL +1 FG W, ATL +0.5 1H W; #16 ATL +4.5 W | OK |
| 10/11 | 8 early games | FG+1H v0.5 | none | CHI -0.5 L, U20.5 MIN/NO W, CIN -4 W, NYG +2.5 L | DEV: run at 6:35 AM before T-100 on 1H screens only; total leans printed though FLOW is note-only |
| 10/11 | 7 early halftimes | 2H v0.5 | none (all near-misses blocked by divergence) | #17 W, #18 W, #19 W, #20 W, #21 W, #22 L, #23 W, #24 L | DEV S-13 (10 tickets, two parlays) |
| 10/11 | DEN@LAC, SF@SEA, DET@ARI | FG+1H v0.5 | none | DET -3 W, SF +2.5 W, U20.5 W | DEV S-4, S-6; DEN@LAC run past the T-17 lock (lean only - lock applied correctly) |
| 10/11 | DEN@LAC, SF@SEA, DET@ARI | 2H v0.5 | none | #25 L, #26 W, #27 L | DEV S-13; blowout veto applied correctly on DET@ARI |
| 10/11 | BAL@ATL | FG+1H v0.5, 2H v0.5 | none | ATL -2.5 1H W; #28 BAL -0.5 W | DEV S-13 (1.9u ticket) |
| 10/12 | BUF@LAR | FG+1H v0.5, 2H v0.5 | none | BUF +2.5 withdrawn on the personnel gate (correct); #29 BUF +4.5 W | OK; DISC-UP declared |
| 10/15 | SEA@DEN | FG+1H v0.6, 2H v0.6 | none | NO CLEAR LEAN; #30 DEN +3.5 L | DEV S-3; rule changed mid-board under the freeze, at Phong's direction |
| 10/18 | 11 games (pre-game, run 12:45 AM) | FG+1H v0.6 | none | HOU +0.5 W, IND -4 W, NE -4 W, LAR -7 L, BUF -3 L, KC -4.5 W; 5 passes | DEV S-4, S-5, S-6, S-7: run about 9 hours before kickoff, inactives and final pulls never logged |
| 10/18 | TEN@IND, BAL@CLE | 2H v0.6 | none (IND -2.5 blocked by divergence) | #31 L, #32 L | DEV S-2 |
| 10/26 | DAL@PHI | FG+1H v0.6, 2H v0.6 | none | DAL -2.5 1H W; #33 DAL +0.5 W | DEV S-2 (found and fixed this day) |
| 10/29 | TNF (GB) | FG+1H v0.6 | not logged | GB 1H W per Phong | DEV L-5: no board on record |
| 11/1 | 12-game sweep, 6 flagged | FG+1H v0.6a | none | CLE +2.5 L, MIA +3.5 W; BAL +2.5 withdrawn; 3 NO CLEAR LEAN | DEV S-3; STATIC games got no FLOW (as the 11/1 rule said) |
| 11/1 | 10 AM halftimes | 2H v0.6 | none | #34 NYJ +3, #35 PIT -0.5 UNGRADED | DEV S-7, L-2 |
| 11/1 | LAC@LAR | 2H v0.6a | FIRE LAR -3 @ -105 UNGRADED | - | DEV L-3; rule written and first applied in the same halftime |
| 11/1 | NE@MIA, KC@DEN, PHI@WAS | 2H v0.6a; SNF 1H v0.6a | none | #36 MIA +7, #37 KC +1, #38 WAS -1 UNGRADED; SNF 1H NO CLEAR LEAN | DEV S-7 |
| 11/2 | CHI@SEA | FG+1H v0.6a, 2H v0.6a | FIRE CHI +2.5 1H @ +110 W | 1H NO CLEAR LEAN; #39 CHI +1 W | DEV: fire class not defined in the 1H tab (X-21); Robinhood unpriced (rate limit) |
| 11/5 | JAX@BAL | FG+1H v0.6a, 2H v0.6a | none | JAX -4.5 1H @ RH W; #40 JAX -3 W | DEV S-13, S-15, L-4 |
| 11/8 | 7 early games | FG+1H v0.6a, re-run v0.6b | none | NO CLEAR LEAN on all 7 | DEV S-4, S-5, S-10; version changed mid-window |
| 11/8 | HOU@LAC, LV@SF, GB@NE, ARI@SEA | FG+1H v0.6b | none | none before kickoff; NE -1.5 paper after kickoff, L | DEV S-5, S-11, S-12 |
| 11/8 | LV@SF, HOU@LAC (+ CLE@NO, DET@MIA, LAR@WAS, TB@CHI by voice) | 2H v0.6a | none | #41 SF -1.5 W, #42 HOU PK W; four NO CLEAR LEAN | DEV: GB@NE and ARI@SEA never run; two unfilled conditionals |
| 11/9 | BUF@MIN | FG+1H v0.6b, 2H v0.6a | none | NO CLEAR LEAN both halves; no ticket | OK - FLOW-TOTAL shadow logged, B test kept as information only |

## 5. What the audit supports, and what it does not
- Supported: no board in the log shows a fire placed against a hard gate. The gates that were applied (blowout, divergence, personnel withdrawal, wind) were applied as written.
- Supported: the bookkeeping rules are the ones that were skipped - closes, shadow grades, the FLOW-total line, inactives reads, the 20-board logs. Those are exactly the data the freeze said the next rule change must wait for.
- Not supported: that v0.5 "was working" in the sense of beating the price. Two days, hit-only.
- Not supported: that any later change made results worse. The drop in recommendations on 11/8 traces to missing FLOW rows, partial inactives and a stricter-than-text reading, not to a rule Phong ratified.
