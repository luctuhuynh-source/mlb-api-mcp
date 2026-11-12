# NFL betting - which protocol ran on which date (10/25 to 11/5/2026)

Written 2026-11-11 at Phong's request ("narrow in the exact protocol that was ran Oct 25th to Nov 5th").

Two different questions are answered here and kept apart:
1. **Version in force** - what the written protocol said on that date and time. Source: the football doc change log, as copied in `POST_FREEZE_CHANGES.md`. This part is exact.
2. **What was actually run** - whether the board read the written tab, and how far the run departed from it. Source: the transcript-only archive reports in `archive/`, plus one direct read of the original chat turns for 11/5 (see the note under the table).

No board reply in the range stated a version label except the two 11/5 boards. Every other label below is assigned from the change log by timestamp.

## 1. Version in force

| Period | NFL FG+1H | NFL 2H |
|---|---|---|
| 10/17 to 11/1 8:30 AM PT | v0.6 = frozen v0.5 + CLEAR LEAN (10/15) + time locks removed (10/17) + Robinhood as an execution venue (10/17) | v0.6, same three additions |
| 11/1 8:30 AM to 2:51 PM PT | v0.6a = v0.6 + slate workflow (sweep, then full runs on FLAGGED games only) | v0.6 |
| 11/1 2:51 PM PT to 11/5 | v0.6a | v0.6a = v0.6 + HOOK fires through CONSENSUS DIVERGENCE when DSB strictly beats every book |

Caution carried from `CONTRADICTIONS.md` X-02: the label "v0.6" covers two rule sets (before and after the 10/17 addenda). All boards in this range are after 10/17.

## 2. What actually ran

| Date | Board(s) | Version in force | Protocol tab opened in the run? | Distance from the written version | Archive file |
|---|---|---|---|---|---|
| Sun 10/25 | 10 pregame 1H boards (SF@ATL, CLE@TEN, IND@MIN, MIA@NYJ, TB@CAR, CIN@BAL, NYG@HOU, DEN@ARI, GB@DET, LAR@LV) | 1H v0.6 | No. Last doc read in that chat was 10/11 (the v0.5 tab). | **Not a run of any written version.** FLOW was not pulled on any of the ten. The CLEAR LEAN test used a "structural" input (record, full-game line, home field) in FLOW's place. "3-of-3 -> $500 DISC-UP" sizing was introduced in-chat. Red105 added as a venue that morning on Phong's word. 11:35 / 11:55 inactives checks never run. | `nfl_betting_2026-10-18_nfl-betting-protocols.md` |
| Sun 10/25 | 2H boards: CIN@BAL / MIA@NYJ / IND@MIN / SF@ATL batch, CLE@TEN + NYG@HOU, DEN@ARI, GB@DET | 2H v0.6 | No | Close in shape: this game's 1H FLOW pulled (missing on SF@ATL, tool returned nothing), divergence, DERIV-LAG, 3.0 floor, blowout gate, Q3-kick stop all applied. No FLOW-total shadow line. Shadow numbers #41-#44 used there collide with the main ledger. | same |
| Sun 10/25 | KC@SEA SNF 1H | 1H v0.6 | No. Ran from memory notes. | Partial: FLOW printed as prose, inactives UNVERIFIED, no weather, no final pull. Lean KC +2.5 never graded. | `nfl_betting_2026-10-25_kc-sea-snf-1h.md` |
| Mon 10/26 | DAL@PHI 1H | 1H v0.6 | **Yes** - "NFL full-game + 1H prompt" tab read before the odds pulls | Closest to a full run in the range. No closing line pulled. | `nfl_betting_2026-10-26_dal-phi-mnf-1h-2h.md` |
| Mon 10/26 | DAL@PHI 2H | 2H v0.6 | **Yes** - "NFL 2H prompt" tab read at the start of the run | Close. FLOW-total shadow recorded later as "no view". No closing line pulled. | same |
| Thu 10/29 | CAR@GB 1H (Run A, rerun B) | 1H v0.6 | **Yes** - 1H tab read in full in Run A; not re-opened for Run B | Close. Game-flow tab and Robinhood tab not opened. FLOW was whole-game, not the 1H split, and no full FLOW table. Weather missing in Run A, pulled in Run B. Lean GB -2.5 @ DSB -110; grade not in that chat (Phong reported a win on 11/1). | `nfl_betting_2026-10-29_car-gb-tnf-1h.md` |
| Thu 10/29 | CAR@GB 2H | 2H v0.6 | No. Ran from memory notes. | Partial: no inactives, no weather, no FLOW-total line, "logged" with no write. NO CLEAR LEAN - pass. | `nfl_betting_2026-10-29_car-gb-tnf-2h.md` |
| Sun 11/1 | 1H sweep (8:32 AM), six individual 1H runs, re-sweep, 12:00 re-run, SNF PHI@WAS 1H | 1H v0.6a | No. From memory. (The same chat had written the slate-workflow section at 8:30 AM.) | Unverified against the text. STATIC games got no FLOW (as the 11/1 rule said). No Red105 pricing. No closing lines. | `nfl_betting_2026-11-01_week8-slate-workflow.md` |
| Sun 11/1 | 10 AM-window 2H boards (11:27-11:50 AM) | 2H v0.6 | No. From memory. | Unverified against the text. | same |
| Sun 11/1 | LAC@LAR 2H (revised 2:52 PM), NE@MIA, KC@DEN, PHI@WAS 2H | 2H v0.6a | No. From memory. (Rule written at 2:51 PM in the same chat.) | LAR -3 fire issued about 22 minutes into halftime with no re-poll or 3Q-kick check. | same |
| Mon 11/2 | CHI@SEA 1H and 2H | 1H v0.6a, 2H v0.6a | No. From memory. | 1H weather stated without a pull. 2H Robinhood unpriced (rate limit). The 1H engine fire rests on a fire class the 1H tab does not define (`CONTRADICTIONS.md` X-21). | same |
| Thu 11/5 | JAX@BAL 1H | 1H v0.6a - **stated in the reply** ("NFL FG+1H v0.6a") | **Yes** - 1H tab read before the odds pulls (see note) | Close. Game-flow tab and Robinhood tab not opened. First Robinhood pull failed on the JAX/JAC ticker, fixed in the next turn. Lean then moved from DSB -6 to a Robinhood strike priced under the floor; ticket about 1.6u, not declared before the price. | `nfl_betting_2026-11-05_jax-bal-tnf-week9-sunday.md` |
| Thu 11/5 | JAX@BAL 2H | 2H v0.6a - **stated in the reply** ("NFL 2H v0.6a") | **Yes** - 2H tab read at the start of the run (see note) | Close. No closing line pulled. | same |

**Note on 11/5.** The 11/5 chat was compacted on 11/8, so its own archive report could not confirm the doc reads. They were recovered on 11/11 by reading that chat's original turns from a different chat: turn 1 shows Docs reads of the football doc project, file 215d5db9-17cd and node 34ac546d-9192 (the same 1H tab IDs the 10/26 archive records) before the first odds pull; the 2H turn shows a Docs read of node df2c40ac-799b (the 2H tab) first. This is the only row in the table that goes beyond the archive reports.

## 3. Summary

- **Ran from the written text (5 boards):** 10/26 DAL@PHI 1H and 2H, 10/29 CAR@GB 1H (v0.6 with the 10/17 addenda); 11/5 JAX@BAL 1H and 2H (v0.6a).
- **Ran from memory or notes (version in force, execution not verified):** 10/25 KC@SEA 1H, 10/25 2H boards, 10/29 CAR@GB 2H, all of 11/1 and 11/2.
- **Ran something not in any written version:** the ten 10/25 pregame 1H boards.
- 11/3 and 11/4: no NFL games.

## 4. What this means for comparing versions

- Results from 10/25 and from 11/1-11/2 cannot be credited cleanly to any version.
- The 10/25 Sunday slate (graded in its own chat as 1H 2-4-1, 2H 1-3) is not in the running ledger or in `AUDIT_2026.md`, whose "6-2 under v0.6" row predates these archives. The 10/19 WAS@SF and 10/22 NE@CHI boards and the two 10/18 engine fires recorded in that same chat are also absent from the ledger. The ledger has not been corrected here.
- Still ungraded in the range: KC +2.5 1H (10/25), the CAR@GB 2H paper no-bet (10/29), 2H leans #34-#38 and the LAR -3 fire (11/1). No closing line was pulled on anything in the range.
