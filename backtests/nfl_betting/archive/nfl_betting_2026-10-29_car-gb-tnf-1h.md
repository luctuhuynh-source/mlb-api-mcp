# NFL betting archive — chat "CAR@GB TNF 1H" (Thu 10/29/2026)

Built 11/11/2026 from this chat's own transcript only. No memory notes, no current protocol doc, no gap-filling.
Companion file from a different chat (2H board, same game): `nfl_betting_2026-10-29_car-gb-tnf-2h.md` — NOT part of this chat.

Attached file saved with this report: `2026-10-29_car-gb_dsb_1h_screen.jpeg` (DSB "NFL 1st Half" screen, phone clock 4:48, sent with the 4:48 PM PT request).

---

## Step 1 — Date by date

| Date | What this chat ran |
|---|---|
| Sun 10/18 | no NFL board in this chat |
| Mon 10/19 | no NFL board in this chat |
| Thu 10/22 | no NFL board in this chat |
| Sun 10/25 | no NFL board in this chat (Sun 10/25 TB@CAR and GB@DET finals were *pulled* on 10/29 as FLOW inputs for the board below; no board was run for 10/25) |
| Mon 10/26 | no NFL board in this chat |
| Thu 10/29 | CAR@GB 1H board — Run A (request 4:48 PM PT), Run B rerun (request 4:52 PM PT), follow-up "What's the lean" (4:54 PM PT) |
| Sun 11/1 | no NFL board in this chat |
| Mon 11/2 | no NFL board in this chat |

---

## Step 2 — Boards

### Board 1 — Thu 10/29, CAR@GB, 1H, Run A

1. **Date / time / T-minus:** Thu 10/29/2026. Request sent 4:48 PM PT; odds pulled 23:49:05 UTC = 4:49 PM PT. Kickoff 5:15 PM PT → T-26 at the odds pull (reply text said "Kickoff is in about 25 minutes" and the flag line said "This run is at T-25").
2. **Game / engine:** CAR @ GB, 1H (full-game lines pulled as reference only).
3. **Version:** NO VERSION STATED in the reply. (The doc tab read in-run carried sections headed v0.2 through v0.6 plus the 10/17 time-lock and Robinhood addenda, but the reply never named a version.)
4. **Protocol doc opened?** Yes. Memory files were read first (`/areas/nfl-betting.md`, `/areas/liem-f5-agent.md`), then the football doc was opened with the Docs tool and the "NFL full-game + 1H prompt" tab was read in full in this run. Line from the tab as read: "TRIGGER PHRASE: \"run our NFL board\" or \"run our NFL 1H protocol\" → read this tab and execute against the DSB screens supplied." The "Game-flow read (all engines)" tab (where the CLEAR LEAN rule lives) and the "Robinhood venue rules" tab were NOT opened; the CLEAR LEAN test was applied from the v0.6 pointer in the 1H tab plus the stored preference.
5. **Inputs:**
   - DSB screen: yes (the attached 4:48 screenshot).
   - Red105 screen: no.
   - Book consensus: yes — 1H spread 8 books, 1H total 8 books (BetMGM 33.5 excluded as stale → 7 at 23.5), full-game 11 books.
   - Robinhood ladder: yes — KXNFL1HSPREAD-26OCT29CARGB and KXNFL1HTOTAL-26OCT29CARGB pulled at ~4:49.
   - Game-flow tables: partial — each team's previous game pulled whole-game (half=0, include_plays=false): CAR = TB@CAR 10/25 (final TB 43–13), GB = GB@DET 10/25 (final DET 20–17). The 1H split (half=1) the tab calls for was NOT pulled separately; 1H scores were read off the drive list. No full FLOW table (sustain rate, 3-and-out rate, RZ conversion, clean margin) was printed — only YPP, giveaways and halftime score.
   - Inactives: yes — web search (FOX11, Panthers.com, Yahoo Sports, AtoZ Sports and others).
   - Weather: no — flagged at top.
6. **Rules:**
   - Clear-lean test: applied — "clear 2 of 3: personnel GB · FLOW GB · price CAR, no hard counter".
   - Book-disagreement check: applied — "There's no HOOK setup (DSB isn't sitting on 3) and no divergence between books."
   - Hook pricing: applied (found not applicable — DSB not on 3).
   - 3.0-point floor: applied — "Nothing is within 3 points of the floor."
   - Blowout gate: not applied (pregame 1H board; gate is a 2H rule).
   - Time lock: not shown as a lock; run treated kickoff as the only stop (no T-12 lock cited).
   - One selection per game: applied implicitly (one lean only); not stated.
   - 2H total shadow line: not applied (1H board).
7. **ENGINE (word for word):** "**ENGINE:** none, $0. Nothing is within 3 points of the floor."
8. **MATCHUP LEAN (word for word):**
   "**MATCHUP LEAN** (clear 2 of 3: personnel GB · FLOW GB · price CAR, no hard counter)
   - **Bet:** GB −2½ 1H
   - **Venue price:** DSB −110 (implied 52.4%)
   - **Size:** 1u, $300 to win ($330 risk) if taken
   - **Gate:** pass if DSB moves to GB −3"
9. **Withdrawn / changed / re-run:** Re-run at 4:52 PM PT at Phong's request (Board 2) to fix the missing weather and T-100 baseline. Lean not withdrawn.
10. **Tickets Phong said he placed:** NOT IN THIS CHAT.
11. **Grade:** NOT IN THIS CHAT (no 1H score pulled, no closing line pulled).
12. **Rule changes / rulings:** none in this board.
13. **Flags (as printed at the top of the reply):**
   - "**No T-100 baseline.** This run is at T-25, so DERIV-LAG can't be assessed for this game."
   - "**Weather not pulled.** Lambeau is outdoors, so totals are WEATHER UNRESOLVED."
   - "**One stale 1H total excluded.** BetMGM is posting 33.5; I left it out of the consensus."
   - "**Drive tool labels look off.** The scoring-play team labels are mismatched, so I read FLOW off the drive results instead."
   - "**OL SHOCK on both sides.** GB is without C Rhyan and RG Glover. CAR is without LG Lewis and RT Moton."
   - Not flagged at the time (found now): the Game-flow tab and Robinhood rules tab were not opened; 1H-split FLOW (half=1) not pulled; first Artifact read of the doc returned only page HTML before the Docs tool read succeeded.

### Board 2 — Thu 10/29, CAR@GB, 1H, Run B (rerun)

1. **Date / time / T-minus:** Thu 10/29. Request 4:52 PM PT ("Rerun it to make sure everything works..like weather n t100"). Odds pulled 23:52:53 UTC = 4:52–4:53 PM PT. Reply stated "**Rerun at 4:53 PT (T-22).**"
2. **Game / engine:** CAR @ GB, 1H.
3. **Version:** NO VERSION STATED.
4. **Protocol doc opened?** No — not re-opened in this run; ran on the tab read in Run A. No quoting line; the reply relied on Run A's read.
5. **Inputs:**
   - DSB screen: yes (same 4:48 screen, not refreshed — flagged).
   - Red105: no.
   - Book consensus: yes — live 1H 8 books, FG 11 books; plus historical T-100 snapshot at 22:30:36 UTC (3:30 PM PT), 8 / 11 books.
   - Robinhood ladder: partial — not re-pulled; 4:49 ladder reused (flagged as stale).
   - Game-flow tables: not re-pulled; Run A data carried ("Personnel and FLOW are unchanged from the first run").
   - Inactives: not re-checked; Run A data carried.
   - Weather: yes — Xweather hourly at Lambeau coordinates.
6. **Rules:**
   - Clear-lean test: applied — "still clear 2 of 3: personnel GB · FLOW GB · price CAR".
   - Book-disagreement: applied — "There's no HOOK and no divergence between books."
   - Hook pricing: applied (not applicable).
   - 3.0-point floor: applied — "Every price is between 1.0¢ and 2.1¢ under fair, far from the 3.0 floor."
   - DERIV-LAG / steam: applied — "the full game didn't move 1.0 or more, so there's no LAG REVIEW and no trigger"; 1H drift "under the 1.0 threshold, so it isn't steam that vetoes anything."
   - Weather gate: applied — "No WIND FLAG".
   - Blowout gate: not applied (1H).
   - Time lock: not shown as a lock.
   - One selection per game: implicit.
   - 2H total shadow: not applied.
7. **ENGINE (word for word):** "**ENGINE:** none, $0. Every price is between 1.0¢ and 2.1¢ under fair, far from the 3.0 floor."
8. **MATCHUP LEAN (word for word):**
   "**MATCHUP LEAN** (still clear 2 of 3: personnel GB · FLOW GB · price CAR)
   - **Bet:** GB −2½ 1H
   - **Venue price:** DSB −110 (implied 52.4%)
   - **Size:** 1u, $300 to win ($330 risk)
   - **Gate:** pass if DSB moves to −3 or worse than −115"
   Note line: "The small market drift toward CAR since 3:30 is noted but doesn't change the lean."
9. **Withdrawn / changed:** Gate widened from Run A ("pass if DSB moves to GB −3") to "pass if DSB moves to −3 or worse than −115". At 4:54 PM PT Phong asked "What's the lean" and the reply restated: "**GB −2½ 1H** / **Venue price:** DSB −110 / **Size:** 1u, $300 to win ($330 risk) / **Gate:** pass if DSB moves to −3 or worse than −115".
10. **Tickets Phong said he placed:** NOT IN THIS CHAT.
11. **Grade:** NOT IN THIS CHAT.
12. **Rule changes / rulings:** none. Phong's only instruction: "Rerun it to make sure everything works..like weather n t100" (4:52 PM PT) — a rerun request, not a rule change.
13. **Flags:** reply said "Every pull worked this time, including weather and the T-100 baseline. The only stale items are the RH ladder (pulled at 4:49) and your DSB screen (4:48), so confirm the DSB price is still live before you place." Not flagged at the time: inactives and FLOW not re-checked; doc not re-opened.

**Run B numbers (as printed):** T-100 3:30 PT → now: 1H GB −2.5 ×8 both times, GB fair cover 51.6% → 51.1%; 1H total 23.5, fair Over 48.9% → 49.8%; FG GB −3.5 ×11 unchanged, FG total 46.5/47 → 47/47.5. Weather: 51°F, clear, 0% rain, wind 6 mph gusts 15. DSB vs fair: CAR +2½ −100 −1.1¢; GB −2½ −110 −1.3¢; O23½ −105 −1.4¢; U23½ −105 −1.0¢; RH GB3 NO 51¢ all-in −2.1¢.

---

## Step 3 — Lists

**Version labels appearing in this chat (first appearance):**
- Thu 10/29 — in the doc tab text read in Run A (not stated in any reply): v0.1, v0.2, v0.3, v0.4, v0.5, v0.6, plus "Time-lock removal (10/17/2026)" and "Robinhood restored as an execution venue (10/17/2026)" addenda. The memory note read the same run also names "NFL FG+1H v0.6" and "NFL 2H v0.6". No reply in this chat stated a version label.

**Leans and fires in the range, with grades:**
- Thu — CAR@GB 1H lean GB −2½ @ DSB −110, 1u — grade NOT IN THIS CHAT.
- Thu — ENGINE fires: none.

**Ungraded or unconfirmed in the range (from this chat):**
- GB −2½ 1H lean — 1H score not pulled, win/loss not graded here.
- Closing line / CLV at kick for that lean — not pulled.
- Whether Phong placed the ticket — not stated in this chat.
- 2H board at halftime — offered ("OWED"), not run in this chat.
