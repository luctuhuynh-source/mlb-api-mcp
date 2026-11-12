# NFL betting archive — chat "NFL betting protocols" (Sun 10/18/2026 – Sun 10/25/2026)

Built 11/11/2026 from this chat's own transcript only. No memory notes, no current protocol doc, no gap-filling. Where the transcript has nothing, the field says NOT IN THIS CHAT.

This chat also contains the 10/11–10/12 (Week 5) boards and the Week 5 CLV pull; they are outside the requested range and are not reported here except where a version label or a rule first appears (Step 3).

Screenshots Phong attached in the range are saved beside this file in `screens_2026-10-18_to_10-25_nfl-betting-protocols/` (55 files, named `<date>_<venue>_<engine>_<game>`). DSB screens appear in a browser tab (the 10/25 ones were opened next to a Red105 tab); the Red105 screens are the 10/25 1H slate; the ESPN screens are pregame or halftime pages.

**Time note.** The transcript read used for this rebuild shows message text but not message clocks. Times below are quoted from the reply text where the reply stated one ("(12:45 AM, T-345)", "Lock ≈ 11:33"). Where only the message timestamp is given it is marked "(msg)" and comes from the earlier pass over this same chat before its context was compacted. Kickoffs are as stated in the replies.

---

## Step 1 — Date by date

| Date | What this chat ran (time order) |
|---|---|
| Sun 10/18 | **Night-before 1H boards** (12:45–12:56 AM): HOU@JAX (London) · PIT@TB / BAL@CLE / CHI@ATL / NYJ@NE batch · TEN@IND · CAR@PHI / NO@NYG / ARI@LAR batch · BUF@LV / LAC@KC batch; alarm set for 1 PM. **Halftime 2H boards** (locks 11:33–11:52 AM): TEN@IND · BAL@CLE · NYJ@NE · PIT@TB · NO@NYG · CHI@ATL (ENGINE FIRE #1) · CAR@PHI. **1H rerun** BUF@LV + LAC@KC (11:49 AM) and **second rerun** after inactives. **2H boards**: ARI@LAR (ENGINE FIRE #2, lock ~2:39) · BUF@LV (lock ~2:58) · LAC@KC (lock ~3:04). **SNF 1H** DAL@GB (pass). **Grading** of the day (after 6 PM). **SNF 2H** DAL@GB (blowout gate, pass). |
| Mon 10/19 | **MNF 1H** WAS@SF (lean SF −4). No 2H board, no grade in this chat. |
| Thu 10/22 | **TNF 1H** NE@CHI · **TNF FG** NE@CHI ("What about whole game") · **TNF 2H** NE@CHI · Over 25½ question (declined) · **Grading** that night. Fri 10/23: record Q&A only (no board). |
| Sun 10/25 | 7:08 AM: Week 7 spreads recorded for DSB + Red105, Red105 declared paper. **Pregame 1H boards** one game at a time: SF@ATL · CLE@TEN · IND@MIN · MIA@NYJ · TB@CAR · CIN@BAL · NYG@HOU · DEN@ARI · GB@DET · LAR@LV. Parlay / sizing / 3-of-3 record Q&A. **10 AM inactives update** (all seven early games). MIN −4 move ruling. **Halftime 2H batch** CIN@BAL / MIA@NYJ / IND@MIN / SF@ATL (all pass) · MIA@NYJ re-ask · **2H** CLE@TEN + NYG@HOU · **2H** DEN@ARI · **2H** GB@DET (LAR@LV gated). **Grading** that night. KC@SEA SNF: NOT IN THIS CHAT (never run). |
| Mon 10/26 | no NFL board in this chat (10/25 grade ended with "DAL@PHI 1H tomorrow at ~3:45 for the inactive check" — the board was never run here) |
| Thu 10/29 | no NFL board in this chat |
| Sun 11/1 | no NFL board in this chat |
| Mon 11/2 | no NFL board in this chat |

The chat's last board turn is the 10/25 grading; the next message is the 11/11 archive request.

---

## Step 2 — Boards

Fields common to every board in the range, stated once:
- **Version (field 3):** NO VERSION STATED on every board from 10/18 through 10/25. The only version label in this chat is "NFL FG+1H v0.5" on 10/11 (turn 1) and "v0.5" references the same day.
- **Protocol doc opened (field 4):** No board in the range opened the protocol doc. The doc was read on 10/11 only ("Running the NFL 1H protocol on the 10 AM slate — reading the v0.5 tab, then pulling consensus and flow." followed by Docs reads of the 1H tab and, for the 2H board, the 2H tab). Every 10/18–10/25 board ran straight from tool pulls with no doc read and no memory read; the replies contain no line saying a tab was opened. On 10/25 the chat told Phong: "Just the screenshot. "NFL 1H" plus the game screen is enough — the protocol is understood for the rest of the session."
- **Red105 screen (field 5):** no, on every board before 10/25 (Red105 did not exist in this chat until 7:08 AM 10/25).
- **Time lock (field 6):** every pregame board in the range stated kickoff as the only stop ("No time lock, kickoff is the stop", "kickoff is the only stop", "Kick 5:20, that's the only lock"); every 2H board stated a lock at the Q3 kick ("Lock ≈ 11:33"). No T-17 / T-12 clock was applied in the range (it was applied on 10/11 only).
- **One selection per game:** applied implicitly on every board (one lean printed per game); the rule was named once in the range, in the 10/22 FG board correlation flag.
- **2H total shadow line:** not shown on any 2H board in the range. Phong asked on 10/11 to hide it ("Can you not show the flow total shadow ? Keep it invisible, still track it though."); the chat replied "Done. From the next board on: RECOMMENDED shows only ENGINE and MATCHUP LEAN." The only total read surfaced in range was the 10/22 "How about the over?" answer, which named it as a FLOW-total shadow.

### Board 1 — Sun 10/18, HOU@JAX (London), 1H, night-before run

1. **Time:** "(12:45 AM, T-345)"; "Kick 6:30 AM PT at Wembley".
2. **Game / engine:** HOU @ JAX, 1H.
3. **Version:** NO VERSION STATED.
4. **Doc:** not opened; ran from pulls (see common note).
5. **Inputs:** DSB screen yes (Phong's 1H screen, 12:40 AM). Red105 no. Book consensus yes — "(1H, 8 books; BetMGM's 10.5 total excluded)"; FG "JAX −2.5 ×10". Robinhood ladder: **no — tool returned empty** ("⚠️ Robinhood: no 1H ladder found for HOU/JAX (the event ticker returned empty while every other Week 6 game is listed)"). Game-flow tables yes — last game FG+1H split: HOU "vs TEN", JAX "vs PHI". Inactives: partial — "Friday reports; Sunday inactives are the checkpoint" (web search). Weather yes — Xweather Wembley: "WIND FLAG: Wembley at kick 14 mph, gusts 26 → Over vetoed for the engine."
6. **Rules:** clear-lean test applied — "2 of 3 aligned, both weak: FLOW HOU (4.14 vs 3.91, clean +6 vs −7) · price HOU (best number on the board, 0.75 past anchor) · personnel JAX". Book-disagreement check applied (spread "JAX −0.5 ×6, FD/BetRivers −1.5"). Hook pricing applied — "No 3/7 touch, no HOOK; DERIV-LAG baseline set here." 3.0 floor applied (conditionals printed at floor prices). Blowout gate n/a. Time lock: "No time lock, kickoff is the stop."
7. **ENGINE (word for word):** "ENGINE: none, $0. Conditionals for the 6:10 pull: HOU +½ 1H @ DSB **+116 or better**; Under 20.5 1H @ DSB **+110 or better**; RH if it posts: HOU +0.5 YES ≤ 46¢ after the 2¢ fee."
8. **MATCHUP LEAN (word for word):** "MATCHUP LEAN: **HOU +½ 1H @ DSB +103** (implied 49.3%) — 2 of 3 aligned, both weak: FLOW HOU (4.14 vs 3.91, clean +6 vs −7) · price HOU (best number on the board, 0.75 past anchor) · personnel **JAX** (HOU down RB1/Dell/Pitre vs JAX down CB2 with Thomas Q). Clear by the rule, not by much. Gate: drop to NO CLEAR LEAN if Braden Smith is inactive or Thomas Jr. is active at 5:00. DISC if you take it: $300 to win, $291 risk."
9. **Withdrawn / changed / re-run:** The owed 5:00 inactives read and 6:10 final pull never happened ("I never got the inactives read, so it stays a paper lean" — 2H board, ~11:30 AM).
10. **Tickets:** not placed — Phong at grading: "I BET ALL LEAN WIN 300 except Houston 1h."
11. **Grade:** WIN — "HOU +½ 1H WIN (HOU led 17–14...)"; grading table "HOU +½ | +103 | WIN (17–14) | not bet". No closing line pulled.
12. **Rule change:** none.
13. **Flags:** RH ladder missing (quoted above); inactives read skipped.

### Board 2 — Sun 10/18, PIT@TB / BAL@CLE / CHI@ATL / NYJ@NE, 1H, night-before batch

1. **Time:** "(12:50 AM, T-550)"; 10 AM kicks.
2. **Engine:** 1H, four games.
3. NO VERSION STATED. 4. Doc not opened.
5. **Inputs:** DSB screen yes (12:49 AM screen). Red105 no. Consensus yes "(1H, 8 books each; BetMGM's junk totals excluded)". RH partial — "only PIT/TB was in the listing (PIT −2.5 YES 47¢ vs fair ≈ 40 → no); BAL/CLE, CHI/ATL, NYJ/NE re-pulled at the final run" (that final run never happened). Game-flow yes, "(last game, 1H split; FG not pulled)": PIT, BAL (Huntley), CLE, CHI (Bagent), ATL, NYJ, NE each from their 10/11 game; **TB "DATA GAP (TNF 10/8, Daniels at QB)"**. Inactives partial — "Friday/Saturday reports" (web). Weather: not pulled.
6. **Rules:** clear-lean test applied on all four (splits below). Book-disagreement applied (counts per game). Hook: "No HOOK (NE sits on 4, not 3)." Floor: "No conditional within 2 pts of the floor anywhere." Time lock: "kickoff is the only stop."
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN (word for word):**
   - "NYJ@NE: **NE −4 1H @ DSB −100** (implied 50.0%) — 3 of 3: personnel NE (Hall/Mitchell/Parham/Ossai out) · FLOW NE (8.53 vs 3.93 YPP) · price NE (best NE number/price on the board). Gate: drop to NO CLEAR LEAN if A.J. Brown is inactive. DISC if taken: $300 to win, $300 risk."
   - "PIT@TB: **NO CLEAR LEAN — pass** (personnel PIT · FLOW DATA GAP · price TB)."
   - "BAL@CLE: **NO CLEAR LEAN — pass** (personnel CLE/QB UNVERIFIED · FLOW BAL · price CLE). Re-read when Cleveland names its QB."
   - "CHI@ATL: **NO CLEAR LEAN — pass**, LINEUP UNRESOLVED (Williams Q). Provisional 2-of-3 ATL (personnel · FLOW) with price CHI — if Williams is active at 8:30 the personnel column flips and it stays a pass; if Bagent starts, ATL PK becomes a clear lean at DSB −107."
9. **Changed / re-run:** The owed "8:30 inactives read on all four" and "9:40 final pull" were never run. BAL/CLE and CHI/ATL were never re-read pregame.
10. **Tickets:** NE −4 — Phong: "I BET ALL LEAN WIN 300 except Houston 1h."
11. **Grade:** "NE −4 1H WIN (17–3)" (stated at the NYJ@NE 2H board); grading table "+300". No closing line pulled.
12. none. 13. TB FLOW data gap; CLE QB unverified; RH ladders missing for three games; inactives read skipped.

### Board 3 — Sun 10/18, TEN@IND, 1H, night-before

1. "(12:52 AM)"; "10 AM, dome". 2. 1H. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes. Red105 no. Consensus yes "(1H, 8 books)", FG "IND −6.5 ×7 / −7 ×4". RH yes — "RH ladder: IND −3.5 YES 53¢ ... TEN +3.5 via IND4 NO 48¢ → nothing within 3¢." Game-flow yes: "IND (at PIT)", "TEN (vs HOU)". Inactives partial (report, no source line beyond "Personnel: IND OUT WR Dulin, LB Carlies..."). Weather: "dome".
6. Clear-lean applied (split below). Disagreement applied ("Spread split three ways: IND −3.5 ×2, −4 ×3, −4.5 ×3"). Hook: "No HOOK (DSB on 4)." Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals (both DSB sides sit 1.2 under fair; nothing within 2 pts of the floor)."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **IND −4 1H @ DSB −103** (implied 50.7%) — 2 of 3: FLOW IND (4.71 vs 3.69, TEN 2 turnovers + 2 three-and-outs) · personnel IND (soft, TEN thin at RB/WR) · price neutral. Clear by the rule, with no price help; DISC if taken: $300 to win, $309 risk. Gate: none pending — re-confirmed at 8:30 inactives with the rest of the slate."
9. 8:30 re-confirmation never run. 10. Bet $300 ("I BET ALL LEAN WIN 300"). 11. "IND −4 1H WIN (13–0)"; "+300". No close pulled. 12. none. 13. none flagged.

### Board 4 — Sun 10/18, CAR@PHI / NO@NYG / ARI@LAR, 1H, night-before batch

1. "(12:55 AM)". 2. 1H, three games (ARI@LAR kicks 1:05 PM). 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes. Red105 no. Consensus yes (8 books; FG "CAR −3 at all 11 books"). RH yes for CAR/PHI and NO/NYG and ARI/LAR ladders. Game-flow: CAR@PHI — "PHI's 5.65-YPP half vs JAX was Hurts — **QB CHANGE, row unusable**; CAR off a bye — DATA GAP"; NO@NYG — "NO ... vs MIN; NYG ... vs WSH"; ARI@LAR — "LAR ... vs BUF; ARI ... vs DET (Brissett)". Inactives partial (reports). Weather: not pulled.
6. Clear-lean applied ×3 (below). Disagreement applied (NO@NYG "books all over the place"). Hook applied — ARI@LAR "7 is a key number and DSB is flat on it at plus money with three books on the hook: push-mass math puts LAR −7 at roughly +1.5, short of the floor." Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. Conditionals: LAR −7 1H @ DSB **+108 or better**; PHI +2½ 1H @ DSB **+110 or better**."
8. **MATCHUP LEAN (word for word):**
   - "**NO CLEAR LEAN — pass** (personnel CAR · FLOW n/a · price PHI)." (CAR@PHI)
   - "**NO CLEAR LEAN — pass** (personnel UNVERIFIED · FLOW NO weak · price NO weak). Two weak columns on an 8-book market that can't agree within 3 points is not a lean I'll print. Re-read at 8:30 if Nabers is out." (NO@NYG)
   - "**MATCHUP LEAN: LAR −7 1H @ DSB +102** (implied 49.5%) — 3 of 3 (personnel · FLOW · price), on the 7 at plus money. DISC if taken: $300 to win, $294 risk." (ARI@LAR)
   - Summary line: "MATCHUP LEAN: LAR −7 1H @ DSB +102. CAR/PHI and NO/NYG: NO CLEAR LEAN — pass."
9. No re-read of NO@NYG at 8:30. 10. LAR −7 bet $300. 11. "LAR −7 is a **LOSS** (9–9)" (at the ARI@LAR 2H board); grading "−294". No close pulled. 12. none. 13. PHI row unusable (QB change), CAR data gap.

### Board 5 — Sun 10/18, BUF@LV / LAC@KC, 1H, night-before batch

1. "(12:56 AM). 1:25 PM kicks". 2. 1H. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes. Red105 no. Consensus yes (8 books; FG BUF −4.5 ×7, KC −7.5 ×9). RH yes (ladders quoted). Game-flow: BUF "vs LAR (without Moore)", LV "vs NE", LAC "vs DEN", "KC off a bye — DATA GAP on one side". Inactives partial ("Moore's shoulder status this week unconfirmed"). Weather not pulled.
6. Clear-lean applied ×2. Disagreement applied. Hook applied — "DSB **BUF −3 −110 → −0.4** flat on the key number, with push-mass vs the five books at 3.5 it reads about +1.5 — short of the floor". Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. Conditionals: KC −4½ 1H @ DSB **+119 or better**; BUF −3 1H @ DSB **−100 or better** (flat 3 at even money would clear with the push mass)."
8. **MATCHUP LEAN (word for word):**
   - "**MATCHUP LEAN: BUF −3 1H @ DSB −110** (implied 52.4%) — 2 of 3: FLOW BUF · price BUF (flat 3 vs a 3.5 market) · personnel unresolved. Gate: re-read if Moore is out again. DISC if taken: $300 to win, $330 risk."
   - "**MATCHUP LEAN: KC −4½ 1H @ DSB +110** (implied 47.6%) — 2 of 3: price KC · personnel KC (soft) · FLOW one-sided (LAC). DISC if taken: $300 to win, $273 risk."
   - Summary: "MATCHUP LEAN: BUF −3 1H @ DSB −110 · KC −4½ 1H @ DSB +110."
   - Exposure note printed: "That's six leans — note L5.6's same-thesis cap doesn't bite (different games), but at flat 1u each it's 6u of 1H exposure in one day".
9. **Re-run twice** (Boards 13 and 14) — numbers moved to BUF −3½ and KC −4; see those boards.
10–11. See Board 14. 12. none. 13. KC data gap (bye).

Alarm: Phong "Set alarm at 1pm to run NFL 1h for 1:25 games." — alarm created "Run NFL 1H protocol — 1:25 games".

### Board 6 — Sun 10/18, TEN@IND, 2H

1. "Lock ≈ **11:33** (Q3 kick ~11:37)". 2. 2H. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes. Red105 no. Consensus yes — "2H books: IND −3.5 ×3 ... Bovada −2.5 −115"; live FG for derivative. RH yes. Game-flow yes — 1H of this game (drives tool). Inactives n/a. Weather n/a.
6. Clear-lean applied. Disagreement applied — "**DIVERGENCE** (1.0)". Hook applied — "a full point better on a number that crosses 3: with the push mass at 3 that reads ≈ **+4.8**, which clears the floor. Two things block it: (1) the >0.5 divergence rule ... (2) DERIV-LAG says no lag". Floor applied. Blowout gate: D=+13, not reached. Lock stated. 2H total shadow: not shown.
7. **ENGINE:** "ENGINE: none, $0 (candidate blocked by divergence; no conditional since the number is the issue, not the price)."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **IND −2½ 2H @ DSB −110** (implied 52.4%) — 3 of 3: FLOW IND · price IND (best number on the board, under 3) · personnel n/a. DISC if taken: $300 to win, $330 risk." Ledger: "2H-SHADOW #31 IND −2.5 @ DSB −110".
9. none. 10. Bet $300. 11. "#31 IND −2½ −110 | 13–0 → 20–26 | IND 7–26 | LOSS | −330". No close pulled. 12. none. 13. "BAL/CLE 2H is OFFLINE on your screen".

### Board 7 — Sun 10/18, BAL@CLE, 2H

1. "Lock ≈ **11:33**". 2. 2H. 3–4. as common.
5. DSB yes. Consensus yes (4 books, "can't agree within 3 points"). RH yes. FLOW yes (1H of this game). 
6. Clear-lean applied. Divergence applied — "DIVERGENCE, mean CLE −0.5". Hook: no 3/7 touch stated via DERIV-LAG match. Floor applied. Blowout not reached (D=−10). Lock stated.
7. **ENGINE:** "ENGINE: none, $0 (CLE −½ +105 clears nothing once the divergence is counted; no conditional)."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **BAL +½ 2H @ DSB −115** (implied 53.5%) — 2 of 3: FLOW BAL · personnel BAL (Cleveland's offense is non-functional at 1.86 YPP) · price CLE (the 2H market is paying the trailing team to push, and DSB's CLE −½ is the better price). DISC if taken: $300 to win, $345 risk." "2H-SHADOW #32".
9. none. 10. $300. 11. "#32 BAL +½ −115 | 10–0 → 10–13 | BAL 0–13 | LOSS | −345". No close. 12–13. none.

### Board 8 — Sun 10/18, NYJ@NE, 2H

1. "Lock ≈ **11:40** (Q3 kick ~11:43)". 2. 2H. 3–4. common.
5. DSB yes; consensus yes (FD/BR −3.5, DK −2.5); RH yes; FLOW yes (this game's 1H).
6. Clear-lean applied. Divergence applied "(1.0)". Hook applied — "same hook shape as IND ... Blocked twice: divergence rule, and DERIV-LAG says no lag". Floor applied. Blowout: D=+14, not reached. Lock stated.
7. **ENGINE:** "ENGINE: none, $0 (hook candidate divergence-blocked; no price conditional)."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NE −2½ 2H @ DSB −110** (implied 52.4%) — 3 of 3: FLOW NE · personnel NE (Hall/Mitchell/Parham out) · price NE (best number on the board, under 3). DISC if taken: $300 to win, $330 risk." "2H-SHADOW #33".
9. none. 10. $300. 11. "#33 NE −2½ −110 | 17–3 → 26–19 | NE 9–16 | LOSS | −330". No close. 12. none. 13. "Two hook candidates in ten minutes, both blocked by the same rule — logged for the review."

### Board 9 — Sun 10/18, PIT@TB, 2H

1. "Lock ≈ **11:42**". 2. 2H. 3–4. common. 5. DSB yes; consensus yes ("PIT −3.5 at all four → **CONVERGED**"); RH yes; FLOW yes.
6. Clear-lean applied. Divergence: converged. Hook: "DSB matches both exactly." Floor applied. Blowout n/a (D=+10). Lock stated.
7. **ENGINE:** "ENGINE: none, $0."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NO CLEAR LEAN — pass** (personnel PIT · FLOW neutral · price neutral). Two identically bad offenses and a market priced to the derivative; nothing to lean on." "No shadow entry."
9–13. none / not bet / not graded (pass).

### Board 10 — Sun 10/18, NO@NYG, 2H

1. "Lock ≈ **11:46** (Q3 kick ~11:50)". 2. 2H. 3–4. common. 5. DSB yes; consensus yes ("split 1.5 / 1.5 / 2 / 2.5"); RH yes; FLOW yes.
6. Clear-lean applied. Divergence applied. Hook/DERIV-LAG: "DSB's NO −1.5 is a full point off the derivative in NO's favor, which is a lag candidate, but the fair at −1.5 only gets to ≈ 52.3 against a 52.4 break-even, so no fire." Floor applied. Lock stated.
7. **ENGINE:** "ENGINE: none, $0. No conditional."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NYG +1½ 2H @ DSB −100** (implied 50.0%) — 2 of 3: FLOW NYG · price NYG (best number/price on the board) · personnel unresolved. DISC if taken: $300 to win, $300 risk." "2H-SHADOW #34".
9. none. 10. $300. 11. "#34 NYG +1½ −100 | 10–10 → 27–34 | NYG 17–24 | LOSS | −300". No close. 12–13. none.

### Board 11 — Sun 10/18, CHI@ATL, 2H — ENGINE FIRE #1

1. "Lock is **Q3 kickoff (~11:43)**". 2. 2H. 3–4. common. 5. DSB yes; consensus yes ("Live FG consensus is converged at 54.5 (6 of 8 books)"; 2H totals at four books); RH yes; FLOW yes (this game's 1H); "Dome, no weather gate".
6. Clear-lean applied. Divergence applied (spread converged). Hook: "No lag, no hook" on the spread. Floor applied — "+3.8 / +2.8 — clears the 3.0 floor on the primary benchmark". Blowout: D=−14, not reached. Lock stated.
7. **ENGINE (word for word):** "ENGINE: **Over 24½ 2H @ DSB −105, $300 to win** (fire #1, DSB-only ledger; conditional on the price still being live at Q3 kick)." Fire line: "**FIRE: Over 24½ 2H @ DSB −105 — $300 to win, $315 risk.** Source of edge: MORE INFO — DSB's 2H total lagging the full-game derivative by 2 pts. Floor price −110; don't chase below that."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **CHI +4 2H @ DSB −115** (implied 53.5%) — 2 of 3: personnel CHI (Williams back, ATL offense stalling) · FLOW CHI (clean margin) · price ATL. Weak; DISC if taken, 1u." "2H-SHADOW #35".
9. none. 10. Fire: "The engine fires is bet disc up 500"; lean: $300.
11. Fire: "1 | CHI/ATL O24½ 2H −105 | WIN (2H 10–16 = 26) | +500". Lean: "#35 CHI +4 −115 | 21–7 → 31–23 | CHI 10–16 | LOSS | −345". No close pulled.
12. none. 13. none.

### Board 12 — Sun 10/18, CAR@PHI, 2H

1. "Lock ≈ **11:52** (Q3 kick ~11:55)". 2. 2H. 3–4. common. 5. DSB yes; consensus yes (FD/BR −2.5, DK −1.5); RH yes; FLOW yes.
6. Clear-lean applied. Divergence applied "(1.0)". DERIV-LAG applied ("the derivative kills it"). Floor applied. Lock stated.
7. **ENGINE:** "ENGINE: none, $0. No conditional."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **CAR −1 2H @ DSB −105** (implied 51.2%) — 2 of 3: personnel CAR (PHI on a backup QB) · price CAR (best CAR number on the board) · FLOW conflict. DISC if taken: $300 to win, $315 risk." "2H-SHADOW #36".
9. none. 10. $300. 11. "#36 CAR −1 −105 | 10–7 → 25–14 | CAR 15–7 | WIN | +300". No close. 12–13. none.

### Board 13 — Sun 10/18, BUF@LV / LAC@KC, 1H rerun (before inactives)

1. 11:49 AM (the next reply says "the markets haven't moved an inch since 11:49"); "kick 1:25". Phong: "Rerun these two games using our 1h NFL protocol and recommend bets. Last night's run recommend buff and KC".
2. 1H. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes (fresh screen). Red105 no. Consensus yes ("1H BUF −3½ at all 8 books"; "KC −4½ ×5 / KC −4 ×3"). RH yes (both ladders). Game-flow: not re-pulled ("structural BUF (last night's read)"). Inactives: partial — "**Inactives aren't posted yet** (they drop ~11:55)"; web search + legionreport fetch attempted. Weather: no.
6. Clear-lean applied ×2. Divergence applied ("0.5 apart, not blocked"). Hook: DSB moved off 3 ("DSB has moved through the key number to **−3½**"). Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals — nothing within 2 points of the floor at either venue."
8. **MATCHUP LEAN (word for word):**
   - "**BUF −3½ 1H @ DSB −105** (implied 51.2) — 2 of 3: personnel BUF · structural BUF (last night's read) · price neutral. Holds, but weaker than last night's −3; if you take it, 1u ($300 to win, $315 risk), and only if Spencer Brown is active."
   - "**KC −4 1H @ DSB −110** (implied 52.4) — 2 of 3: personnel KC (LAC OL gutted) · structural KC · price neutral. Holds; 1u ($300 to win, $330 risk), only after Herbert is confirmed."
9. Re-run again (Board 14). 13. Tool: legionreport fetches returned nothing usable ("The official 90-minute lists still aren't indexed anywhere I can reach" — next reply).

### Board 14 — Sun 10/18, BUF@LV / LAC@KC, 1H second rerun ("The inactive list should be ready")

1. Shortly before 12:00 PM (msg); kick 1:25. 2. 1H. 3–4. common.
5. DSB: same screen (no new one). Consensus yes (re-pulled, "haven't moved an inch"). RH yes. FLOW not re-pulled. Inactives: partial — "The official 90-minute lists still aren't indexed anywhere I can reach, but the two gates I set are resolved by the Friday reports and this morning's beat coverage" (web search; ESPN game page fetch attempted). Weather no.
6. As Board 13; gates cleared ("Gate cleared; personnel leg stays BUF" / "stays KC").
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN (word for word):**
   - "**BUF −3½ 1H @ DSB −105** — 2 of 3: personnel BUF · structural BUF · price neutral. Gate cleared. 1u: $300 to win, $315 risk."
   - "**KC −4 1H @ DSB −110** — 2 of 3: personnel KC · structural KC · price neutral. Gate cleared. 1u: $300 to win, $330 risk."
   - Ledger note: "Both are the same ledger entries as last night at the moved numbers; CLV on each is already negative versus the −3 / −4½ +110 opens".
9. none further. 10. Both bet $300 ("I BET ALL LEAN WIN 300").
11. "BUF −3½ | −105 | LOSS (13–13) | −315"; "KC −4 | −110 | WIN (19–3) | +300". No close pulled.
12. none. 13. Inactive lists unreachable; ESPN page fetch returned no text.

### Board 15 — Sun 10/18, ARI@LAR, 2H — ENGINE FIRE #2

1. "Lock is **Q3 kickoff (~2:39)**". 2. 2H. 3–4. common.
5. DSB yes (2H screen); consensus yes ("Live FG consensus LAR −4.5 (6 of 8 books) / 42.5"; 2H books DK/BR −4.5, FD/Bovada −5.5); RH yes ("LAR −6.5 YES trades 45¢"); FLOW yes (this game's 1H); weather n/a.
6. Clear-lean applied. Divergence applied ("divergent, fair LAR −4.5 ≈ 50.5"). DERIV-LAG applied — "DSB is posting **LAR −6½ / ARI +6½** — two full points past the derivative". Floor applied — "Marginal clear at 3.1 — this is a floor fire, not a fat one." Blowout n/a (9–9). Lock stated.
7. **ENGINE (word for word):** "ENGINE: **ARI +6½ 2H @ DSB −110, $300 to win** (fire #2, DSB-only ledger; conditional on the number being ≥ +6 at Q3 kick)." Fire line: "**FIRE: ARI +6½ 2H @ DSB −110 — $300 to win, $330 risk.** Source of edge: DERIV-LAG (DSB 2 pts past the FG-derived −4.5). Floor: +6 at −110 is the minimum; below that pass."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **ARI +6½ 2H @ DSB −110** — 2 of 3: FLOW ARI · price ARI · personnel LAR (structural, −12.5 pregame). Same ticket as the fire; no separate DISC." "2H-SHADOW #37".
9. none. 10. "The engine fires is bet disc up 500".
11. "2 | ARI +6½ 2H −110 | WIN (ARI 9–7 2H, won outright 18–16) | +500". 1H grade given here: "1H lean LAR −7 is a **LOSS** (9–9)." No close pulled. 12–13. none.

### Board 16 — Sun 10/18, BUF@LV, 2H

1. "Lock ≈ **2:58** (Q3 kick)". 2. 2H. 3–4. common. 5. DSB yes; consensus yes ("BUF −2.5 at all three posting ... CONVERGED"); RH yes; FLOW yes.
6. Clear-lean applied. Divergence: converged. DERIV-LAG: "DSB total matches exactly, spread is half a point off." Floor applied ("BUF −3.5 YES 43¢ ... → +2, short of the floor"). Blowout n/a. Lock stated.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **LV +3 2H @ DSB −110** (implied 52.4%) — 2 of 3: FLOW LV · price LV (the only +3 on the board, half a point past the derivative) · personnel BUF (structural, −5.5 pregame). DISC if taken: $300 to win, $330 risk." "2H-SHADOW #38".
9. none. 10. $300. 11. "#38 LV +3 −110 | 13–13 → 30–33 | LV 17–20 | PUSH | 0". 1H grades stated here: "**BUF −3½ LOSS** (13–13); **LAR −7 LOSS** (9–9)." No close. 12–13. none.

### Board 17 — Sun 10/18, LAC@KC, 2H

1. "Lock ≈ **3:04** (Q3 kick)". 2. 2H. 3–4. common. 5. DSB yes; consensus yes ("KC −2.5 ×3 ... vs DK −1.5 → DIVERGENCE 1.0"); RH yes; FLOW yes.
6. Clear-lean applied. Divergence applied. DERIV-LAG: "trigger is met at exactly 1.0 but the edge doesn't clear." Floor applied ("+2.8, short of the floor by 0.2"). **Blowout gate applied:** "KC 19–3, D = +16, under the 17-pt blowout gate but barely". Lock stated.
7. **ENGINE:** "ENGINE: none, $0. Conditional: **LAC +3 2H @ DSB −110 or +2½ at +105 or better** → fire, $300 to win — the derivative says KC −1.5, so a full 3 is +4-ish."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **KC −2½ 2H @ DSB −110** — 2 of 3: FLOW KC (8.1 vs 4.3 YPP, zero three-and-outs) · personnel KC · price LAC (mild counter, −2.9). DISC if taken: $300 to win, $330 risk. Note the 16-point cushion is one score from the gate — KC coasting is the way this loses." "2H-SHADOW #39".
9. none. 10. $300. 11. "#39 KC −2½ −110 | 19–3 → 22–6 | 3–3 | LOSS | −330". 1H grade here: "**KC −4 WIN** (19–3)". No close. 12–13. none.

### Board 18 — Sun 10/18, DAL@GB (SNF), 1H

1. Request ~4:35 PM (msg); "Kick **5:20**, that's the only lock." 2. 1H. 3–4. common.
5. DSB yes. Red105 no. Consensus yes (1H spread "scattered from DAL −1.5 ... to GB −0.5 → DIVERGENT 2 pts"; total 7 books). RH yes. Game-flow: **not pulled** (no FLOW table; "structural GB" used). Inactives yes — "Personnel (official inactives)" via web search. Weather yes — "Lambeau, 59° and clear, no weather gate".
6. Clear-lean applied. Divergence applied. Hook: not shown. Floor: "Nothing within 2 points of the floor." Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NO CLEAR LEAN — pass.** Split: personnel DAL (GB OL down four) · structural GB (home, the better unit on form) · price GB (+½ at −115 is the fairer side). The OL situation is a hard counter to the GB side, so the 2-of-3 doesn't print."
9–11. pass, nothing placed, not graded. 12. none. 13. "Books posted a 36.5 1H total at BetMGM — a stray listing, excluded from consensus."

### Grading — Sun 10/18 (after the afternoon games)

Phong (exact words): "Grade todays games.  I BET ALL LEAN WIN  300 except Houston 1h.  The engine fires is bet disc up 500"

Reply headline: "**Week 6 Sunday grades — day net on the paper account: −$689.**" Lines: "1H: 4-2 (3-2 bet), **+$291**. Class record 10-4 across Weeks 5–6." "DSB-only engine: **2-0, +$1,000.** Both DERIV-LAG fires; both landed with room." "2H leans: **1-6-1, −$1,980.**" "**Day total: +291 + 1,000 − 1,980 = −$689.**"

Ruling made in the grade: "#30 DEN +3½ 2H (TNF): **LOSS**, not win — DEN 14–3 at half, SEA outscored them 11–3 in 2H+OT. The open-items note had it wrong; corrected." (That #30 board is not in this chat.) "2H-SHADOW cumulative: **21-18-1, n=39**". "DISC-UP class: 3-0 (BUF +4½ MNF, both fires today)." Closing lines: not pulled — "CLV pulls for Week 6 (1H and 2H closes) still owed".

### Board 19 — Sun 10/18, DAL@GB (SNF), 2H

1. "Lock ≈ **7:07** if you DISC anything." 2. 2H. 3–4. common. 5. DSB yes; consensus yes (2H DAL −3.5/−3/−2.5, totals 27.5 ×4); RH yes; FLOW yes (1H of this game).
6. **Blowout gate applied:** "ENGINE: **none — blowout gate.** GB 17–0 is exactly the 17-point line, so the 2H engine is off regardless of price." Clear-lean applied. Divergence applied. Floor: "Nothing near the floor even without the gate." Lock stated.
7. **ENGINE:** "ENGINE: none, $0 (blowout gate). No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NO CLEAR LEAN — pass.** Split: FLOW GB (hard) · personnel DAL · price DAL. The market has DAL as a 3.5-point 2H favorite purely on the scoreboard regression; FLOW says the better team is the one up 17. Two legs on DAL with a hard counter from the half just played doesn't print — and after today's 2H lean day, laying with the half-time favorite is the exact pattern that went 0-5."
9–13. pass; "Day stays at −$689."

### Board 20 — Mon 10/19, WAS@SF (MNF), 1H

1. Request ~1:35 PM (msg); "Kick **5:15**; inactives post ~3:45." 2. 1H. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes (Phong's 1H screen). Red105 no. Consensus yes ("1H SF −4.5 ×5 / SF −4 ×3"; total "26.5 ×7"; FG "SF −7.5 (10 of 11)"). RH yes. Game-flow: **not pulled**. Inactives partial — "final report; inactives pending" (web search). Weather yes — "Levi's, 65° clear, no weather gate".
6. Clear-lean applied. Divergence applied ("0.5 apart, not blocked"). Hook not shown. Floor: "Nothing within 2 of the floor." Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **SF −4 1H @ DSB −115** (implied 53.5%) — 2 of 3: personnel SF · structural SF (5-0, home, healthier) · price WAS (mild, −0.8 vs −1.5). 1u: $300 to win, $345 risk. If Daniels shows up on the inactive list it becomes a 3-of-3 and the number will be gone."
9. "Resend the screen after inactives if either Evans or Daniels moves." — no resend, no rerun in this chat.
10. Tickets: NOT IN THIS CHAT.
11. **Grade: NOT IN THIS CHAT** — later references only: "WAS@SF MNF 1H lean SF −4 still ungraded — I'll pull it with the Week 6 CLV batch" (10/22) and "MNF SF −4 from 10/19 still owed — SF won 23–17, half score not pulled" (10/25). No closing line pulled.
12. none. 13. "BetMGM again lists a stray 36.5 1H total — excluded."

### Board 21 — Thu 10/22, NE@CHI (TNF), 1H

1. Request ~2:29 PM (msg); "Kick **5:15**; inactives post ~3:45." 2. 1H. 3–4. common.
5. DSB yes. Red105 no. Consensus yes ("1H CHI −2.5 ×6 vs CHI −1.5 at FD and BetRivers"; "FG CHI −3 (all 11 books)"). RH yes. Game-flow: **not pulled**. Inactives partial — "final reports; inactives pending" (web search). Weather yes — "Soldier Field, 66° clear, no weather gate".
6. Clear-lean applied. Divergence applied ("divergent 1.0"). Floor: "Nothing near the floor." Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **CHI −2½ 1H @ DSB −110** (implied 52.4%) — 2 of 3: personnel CHI · structural CHI (home, −3 full game) · price NE (mild, −0.5 vs −1.9). 1u: **$300 to win, $330 risk.**"
9. none. 10. Phong at grade: "I disc up $500 for 1h whole game and 2nd half bear." (DSB, −110, $500 to win.)
11. "CHI 1H | −2½ −110 | WIN (20–14) | +$500"; also "1H grade: **CHI −2½ WIN** (20–14)" at the 2H board. No close pulled.
12. none. 13. "BetMGM lists a stray 35.5 1H total again — excluded."

### Board 22 — Thu 10/22, NE@CHI (TNF), FG ("What about whole game")

1. Request ~2:42 PM (msg); "Kick **5:15**". 2. FG. 3–4. common.
5. DSB yes (FG screen). Consensus yes ("CHI −3 at all 11 books (CONVERGED)"; ML; totals 51 ×6 / 50.5 ×5). RH: not pulled for FG. FLOW not pulled. Inactives: "unchanged from the 1H run". Weather as 1H.
6. Clear-lean applied. Divergence: converged. Hook: not shown. Floor: "Nothing within 2 points of the floor." **One selection per game applied:** "**Correlation flag:** this is the same thesis as the 1H lean (CHI −2½ 1H). Taking both is one CHI position at 2u, which the DISC policy logs as a stacking deviation ... Pick one."
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **CHI −3 FG @ DSB −105** (implied 51.2%) — 2 of 3: personnel CHI · structural CHI (home) · price NE (mild, −0.5 vs −1.9). 1u: $300 to win, $315 risk."
9. none. 10. "I disc up $500 for 1h whole game and 2nd half bear." 11. "CHI FG | −3 −105 | WIN (by 6) | +$500". No close. 12. none. 13. none.

### Board 23 — Thu 10/22, NE@CHI (TNF), 2H

1. Request ~6:48 PM (msg); "Lock ≈ **7:00** (Q3 kick)". 2. 2H. 3–4. common.
5. DSB yes (2H screen); consensus yes ("NE −1.5 at DK, FD, BetRivers vs Bovada NE −0.5 → divergent 1.0"; live FG "CHI −5.5 (all 7 books)"); RH yes; FLOW yes (this game's 1H).
6. Clear-lean applied. Divergence applied. DERIV-LAG applied. Floor: "Nothing near the floor." Blowout n/a (D=+6). Lock stated. One-selection: "If you're holding CHI −3 full game, this adds to the same position."
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **CHI +½ 2H @ DSB −105** (implied 51.2%) — 3 of 3: FLOW CHI (mild) · personnel CHI (NE down both guards and three corners) · price CHI (+0.3 vs −2.7). 1u: **$300 to win, $315 risk.**" "2H-SHADOW #40 CHI +½ @ DSB −105 | n=40."
9. Follow-up "How about the over?" → "Short answer: **not a bet under the protocol** — it's a FLOW-total read, not a lean or a fire." with a correction to the Over pricing ("+0.3 to +1.3 — real but well short of the 3.0 floor. No fire.") and "**RECOMMENDED (unchanged)** ENGINE: none, $0. MATCHUP LEAN: **CHI +½ 2H @ DSB −105** — $300 to win, $315 risk. Over 25½: no lean printed."
10. "I disc up $500 for 1h whole game and 2nd half bear." 11. "CHI 2H | +½ −105 | WIN (10–10 tie, the half-point cashed) | +$500"; "FLOW-total shadow: Over 25½ 2H **LOSS**". No close. 12. none. 13. none.

### Grading — Thu 10/22

Phong: "Grade tonight's pick. I disc up $500 for 1h whole game and 2nd half bear." Reply: "**Tonight: 3-0, +$1,500 on the paper account.** CHI 30, NE 24 (half 20–14, 2H 10–10)." Ledger: "1H lean class: **11-4**", "2H-SHADOW: **22-18-1, n=40**", "Full-game lean class: 1-0, first entry.", "DISC-UP class: **6-0**". Deviation log: "1H −2½ and FG −3 were the same CHI thesis — that's 2u+ stacked on one read ... Each ticket stayed under the $600 DISC-UP cap; the issue is the total, not the size." No closing lines pulled.

Fri 10/23 record Q&A corrections (not a board): "2H record is **22-17-1**, not 22-18-1. I miscounted Week 6 as 2-8-1 on Sunday; #30–#39 was actually 2-7-1." and "The 2H count includes #27 (DET/ARI U25½), which was a FLOW-total shadow, not a side lean."

### Sun 10/25 — pre-board rulings (7:08 AM)

Phong: "Here are the spreads for this week.  I have another platform to use along with dsb.   Red105.  Records the spreads i will run the protocol on each of these games individually on the next prompt" → table of 13 games, DSB and Red105, "as of 7:08 AM". Reply notes: "The two books are the same feed — every spread matches, and the prices differ by at most 5 cents"; "Red105 1H max is $500 per market"; "Red105 balance shows **−$711.04** — flagging it so you tell me whether that's a paper account".
Phong: "Red105 is paper account" → "Noted — Red105 is paper, same as DSB. DISC-UP sizing treats both venues identically: $500 cap per ticket".
Phong: "Dsb red105 or robinhood" → "Three venues, one rule: **best price for the side we land on**."
Phong: "Should I wait until 8 30 to run these? Or run now and ask for update at 8 30" → "Run now, then I'll do one batch re-check at 8:30."
Phong: "Do i need to run the whole command or just send the Pic of next game?" → "Just the screenshot. "NFL 1H" plus the game screen is enough — the protocol is understood for the rest of the session."

### Board 24 — Sun 10/25, SF@ATL, 1H

1. ~7:15 AM (msg); "Kick **10:00**; inactives post ~8:30." 2. 1H. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes (7:08 slate screen); **Red105 yes** (7:08 slate screen). Consensus yes ("1H SF −0.5 ×6 / SF −1.5 ×2"; "FG SF −2.5 (10 of 11)"). RH yes. Game-flow: **not pulled**. Inactives partial — "final reports; inactives pending" (web). Weather: "dome, no weather gate".
6. Clear-lean applied. Divergence applied ("divergent 1.0"). Floor: "Nothing near the floor." Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **SF −½ 1H @ DSB −100** (Red105 EV equal; implied 50.0) — 2 of 3: structural SF (6-0, −2.5 full game) · price SF (−0.4 vs −2.0 for ATL) · personnel neutral. 1u: **$300 to win, $300 risk.** Thin — the price leg is a nickel's worth. Gate: if Kirk is also out, SF is down three WRs and this goes to NO CLEAR LEAN."
9. 10 AM inactives update: "SF −½ | **HOLDS, gate cleared** | **Christian Kirk active** (off IR) ..." 10. Grade assumed $300 at −100 (Phong did not state the ticket; the grade table carried it as "SF −½ | −100 | 14–12 | WIN | +300" with "assuming the sizing we discussed"). 11. WIN (14–12). No close. 12. none. 13. "BetMGM again lists a stray 34.5 1H total — excluded."

### Board 25 — Sun 10/25, CLE@TEN, 1H

1. ~7:20 AM (msg); kick 10:00. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("1H CLE −0.5 ×7 / CLE −1.5 FD"; total "18.5 ×5 / 17.5 ×2"); RH yes; FLOW not pulled; inactives partial (web; "**the CLE starter is not confirmed in anything I can find; LINEUP UNRESOLVED.**"); weather "outdoor — Nashville forecast clear, no weather gate".
6. Clear-lean applied. Divergence applied ("blocked by the 17.5/18.5 divergence"). Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. Conditional: **O17½ at −105 or better if the 18.5 books come down to 17.5 before kick** → that clears divergence and fair moves to ≈ 53 → +1.8 still short; no fire either way. Listed only so you don't take it on your own."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NO CLEAR LEAN — pass.** Split: personnel TEN · structural CLE (4-2 vs 1-5, −2 FG) · price neutral (0.4 apart). The CLE QB is the unresolved gate — if a backup starts, this flips to a printed TEN +½ @ Red105 −110; if it's the Week 6 starter who beat BAL, structural and personnel stay split and it stays a pass."
9. Inactives update: "CLE@TEN | pass | **STAYS PASS** | ... TEN scratched **Ridley and Spears** — WR1 and RB2. Personnel moves toward even, not toward TEN; still no 2-of-3." 10–11. pass; grade note "Passes were right: TB 33–6, CLE 17–14, LAR 28–3." 12. none. 13. CLE QB unresolved; "BetMGM lists a 7.5 1H total — stray, excluded."

### Board 26 — Sun 10/25, IND@MIN, 1H

1. ~7:24 AM (msg); kick 10:00. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("1H MIN −3.5 ×4 / −4 ×3 / −4.5 FD"); RH yes; FLOW not pulled; inactives partial (web); weather "dome".
6. Clear-lean applied. Divergence applied ("divergent 1.0"). Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **MIN −3½ 1H @ DSB −115** (Red105 −115 equal; implied 53.5) — 2 of 3: personnel MIN · structural MIN (5-0, best scoring D, off bye, home) · price neutral (IND +3½ +105 is 0.3 better, not enough to call). 1u: **$300 to win, $345 risk.**" Plus: "If DSB/Red105 move to −4 before kick, the lean holds but the number is worse — take it at −3½ or not at all."
9. **Changed:** Phong "Min is up to -4 now on DSB. Worth betting?" → "My call: **MIN −3½ at Red105 if available; otherwise pass**". Phong "Min -4 105 on red too. What should I do" → "Lean holds as printed — 2-of-3, price neutral. **MIN −4 1H @ Red105 −105 — $300 to win, $315 risk.** Take it." (reverses "take it at −3½ or not at all").
10. Ticket: Red105, MIN −4, −105, $300 to win (Phong's words: "Min -4 105 on red too. What should I do" — the placement itself was not confirmed in words; graded as bet).
11. "MIN −4 | −105 Red105 | 6–10 | LOSS | −315". No close. 12. none. 13. "BetMGM lists a stray 23.5 1H total — excluded."

### Board 27 — Sun 10/25, MIA@NYJ, 1H

1. ~7:28 AM (msg); kick 10:00. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("NYJ −2.5 at all 7 real books (CONVERGED)"); RH yes; FLOW not pulled; inactives partial (web); weather yes "MetLife, 54° sunny, no wind flag".
6. Clear-lean applied. Divergence: converged. Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NYJ −2½ 1H @ DSB −115** (Red105 −115 equal; implied 53.5) — 2 of 3: personnel NYJ · structural NYJ (home, −4 FG vs an 0-5 team on a backup QB) · price MIA (mild, −0.7 vs −1.6). 1u: **$300 to win, $345 risk.** Thin on price; the number is fair and you're paying 15 cents for it." Plus: "If DSB/Red105 go to −3 before kick, the lean is off".
9. Inactives update: "NYJ −2½ | **HOLDS, slightly softer** | Breece Hall **inactive** ... Lean still 2-of-3". 10. Graded as bet $300 (no placement words from Phong). 11. "NYJ −2½ | −115 | 7–21 | LOSS | −345". No close. 12. none. 13. "BetMGM lists a 21.5 stray, BetRivers a 9.5 stray — both excluded."

### Board 28 — Sun 10/25, TB@CAR, 1H

1. ~7:32 AM (msg); kick 10:00. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("CAR −1.5 ×7 / Bovada −0.5"; total "scattered 21.5–23.5"); RH yes; FLOW not pulled; inactives partial (web); weather yes "56° sunny".
6. Clear-lean applied. Divergence applied (total). Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NO CLEAR LEAN — pass.** Split: structural CAR (home, 3-2 vs 1-5, −3 FG) · price TB (+1½ is the fairer side, −0.5 vs −1.9) · personnel neutral."
9. Inactives: "TB@CAR | pass | **STAYS PASS** | **Mayfield active** (glove)". 10–11. pass. 13. "BetMGM lists a 32.5 stray — excluded."

### Board 29 — Sun 10/25, CIN@BAL, 1H

1. ~7:36 AM (msg); kick 10:00. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("1H CIN −1.5 ×6 / CIN −1 ×2"; "FG CIN −3 (10 of 11)"); RH yes; FLOW not pulled; inactives partial (web; "Lamar Jackson OUT (announced Saturday)"); weather yes "58° sunny".
6. Clear-lean applied. Divergence applied. Floor applied ("RH ... BAL +2.5 via CIN3 NO 51¢ (53 vs ≈ 55) → +1.8, the closest thing to a fire today"). Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. Conditional: **RH "CIN wins 1H by over 2.5" NO at 50¢ or lower** → BAL +2.5 at ≈ +2.8–3.0, fire $300 if it gets there (it's 51 now). Low odds it moves that way with Lamar out."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **CIN −1 1H @ DSB −105** (Red105 −105 equal; implied 51.2) — **3 of 3**: personnel CIN (full roster vs backup QB, two defensive starters out, LT iffy) · structural CIN (−3 FG, road favorite) · price CIN (best number on the board, half a point under the market). 1u: **$300 to win, $315 risk.**"
9. Inactives: "CIN −1 | **HOLDS, firmer** ... Still 3-of-3." Sizing advice in the slate Q&A: "3-of-3 → $500 DISC-UP (CIN −1 now ...)"; "Place CIN now".
10. Graded as "$500 DISC-UP" and as the first leg of the $150 parlay; Phong's own words on placement: NOT IN THIS CHAT (he asked "These 3.. do i have to wait for 8 45 update run? Or can I place the bets now" and did not confirm afterwards).
11. "CIN −1 (3/3, $500 DISC-UP) | −105 | 0–13 | LOSS | −525"; "Parlay CIN/DEN/DET | $150 | | LOSS (CIN) | −150". No close. 12. none. 13. "BetMGM lists a 13.5 stray — excluded."

### Board 30 — Sun 10/25, NYG@HOU, 1H

1. ~7:40 AM (msg); kick 10:00. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("HOU −6.5 at all 8 books (CONVERGED)"; "FG HOU −10.5 at all 11"); RH yes; FLOW not pulled; inactives partial (web; "**J.J. McCarthy's first Giants start**"); weather "roof".
6. Clear-lean applied. Divergence: converged. Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **HOU −6½ 1H @ Red105 −105** (DSB −110 is the fallback; implied 51.2) — 2 of 3: personnel HOU · structural HOU (−10.5 FG, home) · price NYG (mild — DSB +6½ at even is the fairest line on the board). 1u: **$300 to win, $315 risk.** Red105 over DSB here; the nickel is the whole price leg."
9. Inactives: "HOU −6½ | **HOLDS** | ... **Tank Dell active**". At the 2H board the pregame QB read was found wrong: "Winston, not McCarthy, is the QB of record on the TD; worth noting the pregame QB read was wrong."
10. Graded as bet $300 at Red105 (no placement words). 11. "HOU −6½ | −105 Red105 | 14–14 | LOSS | −315". No close. 12. none. 13. "BetMGM lists a 31.5 stray — excluded"; QB read wrong.

### Board 31 — Sun 10/25, DEN@ARI, 1H

1. ~7:44 AM (msg); "Kick **1:05**; inactives ~11:35." 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("1H DEN −2.5 ×3 / −3 ×3 / −3.5 ×2 → divergent 1.0"); RH yes; FLOW not pulled; inactives partial (web; "QB Carson Beck questionable"); weather "roof".
6. Clear-lean applied. Divergence applied ("+1.7 and blocked by divergence"). Hook: flat 3 noted. Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. Conditional: none at this price — DEN −3 at EV is +1.7 and blocked by divergence; it would need −2½ at EV to clear."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **DEN −3 1H @ DSB −100** (Red105 EV equal; implied 50.0) — **3 of 3**: personnel DEN · structural DEN (4-2, −4.5 road favorite) · price DEN (best number and best price on the board). 1u: **$300 to win, $300 risk.**"
9. The ~11:35 inactives check for DEN@ARI was never run in this chat. 10. Graded as "$500" ("tell me if DEN wasn't $500"); Phong's words: NOT IN THIS CHAT. 11. "DEN −3 (3/3, $500) | −100 | 13–6 | WIN | +500"; also "1H grade: **DEN −3 WIN** (13–6)" at the 2H board. No close. 12. none. 13. "BetMGM lists an 11.5 stray — excluded."

### Board 32 — Sun 10/25, GB@DET, 1H

1. ~7:48 AM (msg); "Kick **1:25**; inactives ~11:55." 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("1H DET −2.5 ×5 ... / DET −3 ×3 (−105)"); RH yes; FLOW not pulled; inactives partial (web); weather "dome".
6. Clear-lean applied. Divergence applied. Hook: "Push risk on exactly 3 is the cost of the price." Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals — +1.3 at a flat 3 is as close as this gets."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **DET −3 1H @ DSB −100** (Red105 EV equal; implied 50.0) — **3 of 3**: personnel DET (GB's two starting LBs out vs Gibbs; Branch back) · structural DET (home, off bye, −3.5 FG) · price DET (even money on the 3 when the market's at −2.5 juiced). 1u: **$300 to win, $300 risk.** Push risk on exactly 3 is the cost of the price."
9. 11:55 inactives check never run in this chat. Parlay advice: "the cleanest three-leg from today's board is **CIN −1 (10:00) / DEN −3 (1:05) / DET −3 (1:25)** — all three 3-of-3 leans, $150 per the one-parlay-per-slate rule."
10. Phong's placement words: NOT IN THIS CHAT. 11. "DET −3 (3/3) | −100 | 10–7 | PUSH | 0"; "**DET −3 PUSH** (10–7) — refund on the single". No close. 12. none. 13. "BetMGM lists a 37.5 stray — excluded."

### Board 33 — Sun 10/25, LAR@LV, 1H

1. ~7:52 AM (msg); kick 1:25. 2. 1H. 3–4. common.
5. DSB yes; Red105 yes; consensus yes ("LAR −2.5 ×7 / FD −1.5"); RH yes; FLOW not pulled; inactives partial (web); weather "dome".
6. Clear-lean applied. Divergence applied. Floor applied. Time lock: kickoff.
7. **ENGINE:** "ENGINE: none, $0. No conditionals."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **NO CLEAR LEAN — pass.** Split: personnel LV · structural LAR (road favorite, −3.5 FG) · price neutral (0.4 apart). The market is still laying 3.5 with a 2-4 team that just lost its WR2, DT1 and a starting DT, and that's a hard-counter-shaped number."
9. Nacua/McDuffie gate never re-checked (11:55 update not run). 10–11. pass. 13. "BetMGM lists a 33.5 stray — excluded."

### Sun 10/25 — slate Q&A rulings between boards (exact words)

- Phong: "What would be my command prompt for 8 45 am updates on inactives" → "Just send: NFL 1H inactives update — 10 AM slate".
- Phong: "For Detroit game. Should I bet detroit early as part of a parlay 3?" → "Yes, it qualifies ... Logged as the Week 7 slate parlay either way — $150."
- Phong: "So MIN -3.5 is the safer none 3/3 bet?" → "Safer from pushing, not safer to win ... My pick is still CIN / DET / DEN."
- Phong: "These 3.. do i have to wait for 8 45 update run? Or can I place the bets now" → "Place CIN now; the other two can wait. ... Place the $150 parlay now, then hold the single-ticket DET and DEN leans for the inactive checks."
- Phong: "NFL 1H inactives update — 10 AM slate" → table (quoted per board above); "Nothing flipped. Five leans live for 10:00, two passes." Source: web search.
- Phong: "Are the other 2/3 lean worth betting?" → "Yes, at 1u — that's what the class is for. ... **3-of-3 → $500 DISC-UP** ... **2-of-3 → $300**".
- Phong: "Whats our record for 3/3 lean?" → "**2-3** since the CLEAR LEAN rule started tagging legs on 10/15." (table of five). Sizing ruling: "If you want the DISC-UP to be evidence-based, the honest move is $300 on everything until the 3-of-3 tag has 20+ results."
- Phong: "Min is up to -4 now on DSB. Worth betting?" / "Min -4 105 on red too. What should I do" → see Board 26.

### Board 34 — Sun 10/25, CIN@BAL / MIA@NYJ / IND@MIN / SF@ATL, 2H batch ("Do a deep analysis of each games")

1. ~11:26 AM (msg); "Lock ≈ **11:38** (Q3 kicks)." 2. 2H, four games. 3. NO VERSION STATED. 4. Doc not opened.
5. DSB yes (two 2H screens); Red105 no 2H screen; consensus yes (all live 2H + FG markets pulled, 4 books per game); RH yes (four ladders); FLOW yes for CIN@BAL, MIA@NYJ, IND@MIN (this game's 1H); **SF@ATL FLOW missing** — "**drive data did not come back for this game** — I have the score only."; inactives n/a; weather n/a.
6. Clear-lean applied ×4. Divergence applied per game. DERIV-LAG applied. Floor applied. Blowout: none at 17 (D = +13, −14, −4, −2). Lock stated. 2H total shadow: not shown.
7. **ENGINE:** "ENGINE: none, $0. Conditional: RH NYJ −7.5 YES ≤ 35¢ → $300."
8. **MATCHUP LEAN (word for word):** "MATCHUP LEAN: **NO CLEAR LEAN — pass** on all four. Splits: CIN@BAL personnel CIN · FLOW BAL · price CIN | MIA@NYJ personnel NYJ · FLOW MIA · price NYJ | IND@MIN personnel MIN · FLOW conflict · price neutral | SF@ATL price SF · personnel neutral · FLOW n/a." Per-game lines: "**NO CLEAR LEAN — pass.** Split: personnel CIN · FLOW BAL (hard) · price CIN." / "**NO CLEAR LEAN — pass.** Split: personnel NYJ · FLOW MIA (hard) · price NYJ (mild)." / "**NO CLEAR LEAN — pass.** Split: personnel MIN · FLOW conflict · price neutral." / "**NO CLEAR LEAN — pass.** Split: price SF · personnel neutral · FLOW not pulled. If you want the SF PK at −105 on your own read, it's the only one of the four where the price is on the side that's also winning — log it DISC, 1u max."
   1H grades stated here: "1H leans went **1-4** — SF −½ WIN (14–12); **CIN −1 LOSS (0–13)**, MIN −4 LOSS (6–10), NYJ −2½ LOSS (7–21), HOU −6½ LOSS (6–14 at the two-minute warning). The parlay is dead on the CIN leg."
9. Phong re-asked MIA@NYJ ("Run our 2H NFL protocol on this game") → "Already run in the batch above — nothing changed in the three minutes since." Same lean line repeated; "Lock is Q3 kick, about now."
10. none placed. 11. Passes reviewed at grading: "CIN@BAL | CIN −6½ | CIN 35–0 | WIN", "MIA@NYJ | NYJ −6½ | NYJ 18–7 | WIN", "IND@MIN | MIN −6½ | MIN 10–0 | WIN", "SF@ATL | SF PK | ATL 17–6 | LOSS". 12. none. 13. SF@ATL drives tool returned nothing.

### Board 35 — Sun 10/25, CLE@TEN + NYG@HOU, 2H

1. ~11:43 AM (msg); "Lock ≈ **11:50** (Q3 kicks)." 2. 2H, two games. 3–4. common.
5. DSB yes (2H screen); consensus yes; RH yes (both); FLOW yes (both games' 1H); personnel carried from pregame.
6. Clear-lean applied ×2. Divergence applied ("divergent 1.0" / "CONVERGED"). DERIV-LAG applied — NYG@HOU "DERIV-LAG trigger met on the Under (1.5 pts), edge short of 3.0". Floor applied. Blowout n/a (D=−3, 0). Lock stated.
7. **ENGINE (word for word):** CLE@TEN: "ENGINE: none, $0." NYG@HOU: "ENGINE: none, $0. Conditional: **U23½ 2H @ DSB −107 or better** → clears on the derivative (+3.4), fire $300. Also the OT-unmodeled caveat applies to any 2H under in a tied game." Top line: "**ENGINE: none on either.**"
8. **MATCHUP LEAN (word for word):**
   - "MATCHUP LEAN: **CLE −½ 2H @ DSB −105** (implied 51.2) — **3 of 3**: FLOW CLE · personnel CLE · price CLE. 1u: **$300 to win, $315 risk.** This is a half-time leader laying a number, which is today's losing shape — but it's a half-point, DSB is a point better than the market, and the FLOW gap is real. If one of these is going to work, it's this one."
   - "MATCHUP LEAN: **HOU −3½ 2H @ DSB +105** (implied 48.8) — 2 of 3: personnel HOU · price HOU · FLOW NYG (moderate counter). 1u: **$300 to win, $286 risk.** Printed because the rule is 2-of-3 with no hard counter; stated plainly, it's the weaker of the two leans by a lot — you're laying 3.5 in a half with the team that's been outgained, and that shape went 0-5 last week. If you only take one, take CLE."
   - "2H-SHADOW #41 CLE −½ @ DSB −105, #42 HOU −3½ @ DSB +105 | n=42."
   1H grade here: "HOU −6½ **LOSS** (14–14). 1H day finishes **1-4**".
9. none. 10. Phong's placement words: NOT IN THIS CHAT (graded as bet $300 each). 11. "41 | CLE −½ (3/3) −105 | 17–14 → 27–24 | 10–10 | LOSS | −315"; "42 | HOU −3½ +105 | 14–14 → 21–27 | 7–13 | LOSS | −286". No close. 12. none. 13. none.

### Board 36 — Sun 10/25, DEN@ARI, 2H

1. ~2:46 PM (msg); "Lock ≈ **2:58** (Q3 kick)." 2. 2H. 3–4. common.
5. DSB yes; consensus yes ("2H books are all over the place ... Two-point spread between books"); RH yes; FLOW yes (this game's 1H).
6. Clear-lean applied. Divergence applied ("Divergence blocks the consensus read; derivative lag is only 0.5. No fire."). Floor applied. Blowout n/a (D=−7). Lock stated.
7. **ENGINE:** "ENGINE: none, $0. Conditional: **RH DEN −2.5 YES ≤ 37¢** → +3 on every fair I can build, fire $300."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **DEN PK 2H @ DSB −100** (implied 50.0) — **3 of 3**: FLOW DEN (moderate) · personnel DEN · price DEN (+2.5). 1u: **$300 to win, $300 risk.**" "2H-SHADOW #43 | n=43."
9. none. 10. NOT IN THIS CHAT (graded as bet $300). 11. "43 | DEN PK (3/3) −100 | 13–6 → 30–16 | 17–10 | WIN | +300". No close. 12–13. none.

### Board 37 — Sun 10/25, GB@DET, 2H (LAR@LV gated)

1. ~2:50 PM (msg); "Lock ≈ **3:01**." 2. 2H. 3–4. common.
5. DSB yes; consensus yes ("DET −2.5 ×3 ... / Bovada −2"); RH yes; FLOW yes (this game's 1H; LAR@LV 1H drives also pulled).
6. Clear-lean applied. Divergence applied. DERIV-LAG applied ("DSB is posting **DET −1½** — a full point under both the books and the derivative. DERIV-LAG trigger met (1.0)"). Floor applied ("Nothing clears 3.0"). **Blowout gate applied to LAR@LV:** "LAR is up 28–3 on LV at the two-minute warning — that one's over the 17-point blowout gate; no 2H run." Lock stated.
7. **ENGINE:** "ENGINE: none, $0. Conditional: **DET −½ or PK at −105** on either venue → clears on the derivative, fire $300. Unlikely, but DSB's number is already soft."
8. **MATCHUP LEAN:** "MATCHUP LEAN: **DET −1½ 2H @ DSB −105** (implied 51.2) — **3 of 3**: FLOW DET · personnel DET · price DET (+1.2, with the derivative lag behind it). 1u: **$300 to win, $315 risk.**" "2H-SHADOW #44 | n=44."
   1H grade here: "**DET −3 PUSH** (10–7)".
9. none. 10. NOT IN THIS CHAT (graded as bet $300). 11. "44 | DET −1½ (3/3) −105 | 10–7 → 20–17 | 10–10 | LOSS | −315". No close. 12–13. none.

### Grading — Sun 10/25

Phong: "Grade todays games." Reply: "**Week 7 Sunday: 1H 2-4-1, 2H 1-3. Rough day.**" "1H net: **−$850** (assuming the sizing we discussed; tell me if DEN wasn't $500)." "2H net: **−$616.**" "**Day: ≈ −$1,466.**" Ledger: "1H lean class: **13-8-1**", "2H-SHADOW: **23-20-1, n=44.**", "3-of-3 tag: today 2-3-1 → cumulative **4-6-1.** The tag is not earning its DISC-UP; sizing back to $300 across the board until it does is the honest move.", "Engine: 2-0, no fires today. DISC-UP class: 7-1.", "CLV pulls for Weeks 6–7 still owed". Review note: "I passed those on the Week 6 pattern (0-5 last Sunday). Today the market's regression read was right three times out of three. ... It goes in the review packet as an open question, not a finding." Closing lines: none pulled. Last line: "DAL@PHI 1H tomorrow at ~3:45 for the inactive check." — never run in this chat.

---

## Step 3 — Lists

### Version labels appearing in this chat
| Label | First appearance | Where |
|---|---|---|
| "NFL FG+1H v0.5" | Sun 10/11 | turn 1 header "**NFL FG+1H v0.5 — 10:00 AM window, PRE-BASELINE snapshot (6:35 AM PT = T-206)**"; same turn "reading the v0.5 tab" |
| "v0.5" (unqualified) | Sun 10/11 | "That's the v0.5 protocol doing exactly what it was rewritten to do"; "v0.5 vs the old version" |
| Any label on 10/18–10/25 boards | — | NO VERSION STATED (none) |
| "v0.6", "NFL 2H v0.6", "CLEAR LEAN RULE v1.0" | — | NOT IN THIS CHAT (the chat says only "since the CLEAR LEAN rule started tagging legs on 10/15", no version number) |

Rule references that appear without a version: "L5.3", "L5.6", "D6", "D7", "D9", "the 10/4 rule" (DSB 2H includes OT), ">0.5 divergence rule", "DERIV-LAG", "HOOK", "17-pt blowout gate", "T-17 / T-12" (10/11 only), "DISC / DISC-UP" (defined 10/11–10/12).

### Every lean and fire in the range, with grade
Sun 10/18
- Sun — 1H HOU +½ @ DSB +103 — WIN (17–14) — not bet
- Sun — 1H NE −4 @ DSB −100 (3/3) — WIN (17–3) — $300
- Sun — 1H IND −4 @ DSB −103 — WIN (13–0) — $300
- Sun — 1H LAR −7 @ DSB +102 (3/3) — LOSS (9–9) — $300
- Sun — 1H BUF −3 → rerun BUF −3½ @ DSB −105 — LOSS (13–13) — $300
- Sun — 1H KC −4½ +110 → rerun KC −4 @ DSB −110 — WIN (19–3) — $300
- Sun — 1H passes: PIT@TB, BAL@CLE, CHI@ATL, CAR@PHI, NO@NYG, DAL@GB (SNF) — not graded
- Sun — 2H #31 IND −2½ @ DSB −110 (3/3) — LOSS (2H 7–26) — $300
- Sun — 2H #32 BAL +½ @ DSB −115 — LOSS (0–13) — $300
- Sun — 2H #33 NE −2½ @ DSB −110 (3/3) — LOSS (9–16) — $300
- Sun — 2H PIT@TB — pass
- Sun — 2H #34 NYG +1½ @ DSB −100 — LOSS (17–24) — $300
- Sun — **ENGINE FIRE #1 Over 24½ 2H CHI@ATL @ DSB −105** — WIN (2H 26) — $500 DISC-UP
- Sun — 2H #35 CHI +4 @ DSB −115 — LOSS (10–16) — $300
- Sun — 2H #36 CAR −1 @ DSB −105 — WIN (15–7) — $300
- Sun — **ENGINE FIRE #2 ARI +6½ 2H @ DSB −110** (#37) — WIN (ARI 9–7) — $500 DISC-UP
- Sun — 2H #38 LV +3 @ DSB −110 — PUSH (17–20) — $300
- Sun — 2H #39 KC −2½ @ DSB −110 — LOSS (3–3) — $300
- Sun — 2H DAL@GB (SNF) — pass (blowout gate)
Mon 10/19
- Mon — 1H SF −4 @ DSB −115 — UNGRADED in this chat (final SF 23–17 noted; half score not pulled)
Thu 10/22
- Thu — 1H CHI −2½ @ DSB −110 — WIN (20–14) — $500 DISC-UP
- Thu — FG CHI −3 @ DSB −105 — WIN (30–24) — $500 DISC-UP
- Thu — 2H #40 CHI +½ @ DSB −105 (3/3) — WIN (10–10) — $500 DISC-UP
- Thu — Over 25½ 2H — not a lean (FLOW-total shadow) — LOSS (2H 20)
Sun 10/25
- Sun — 1H SF −½ @ DSB −100 — WIN (14–12) — $300
- Sun — 1H CLE@TEN — pass
- Sun — 1H MIN −3½ −115 → taken MIN −4 @ Red105 −105 — LOSS (6–10) — $300
- Sun — 1H NYJ −2½ @ DSB −115 — LOSS (7–21) — $300
- Sun — 1H TB@CAR — pass
- Sun — 1H CIN −1 @ DSB −105 (3/3) — LOSS (0–13) — $500 DISC-UP
- Sun — 1H HOU −6½ @ Red105 −105 — LOSS (14–14) — $300
- Sun — 1H DEN −3 @ DSB −100 (3/3) — WIN (13–6) — $500
- Sun — 1H DET −3 @ DSB −100 (3/3) — PUSH (10–7)
- Sun — 1H LAR@LV — pass
- Sun — Parlay CIN −1 / DEN −3 / DET −3 — LOSS — $150
- Sun — 2H CIN@BAL, MIA@NYJ, IND@MIN, SF@ATL — all pass (would have gone W, W, W, L)
- Sun — 2H #41 CLE −½ @ DSB −105 (3/3) — LOSS (10–10) — $300
- Sun — 2H #42 HOU −3½ @ DSB +105 — LOSS (7–13) — $300
- Sun — 2H #43 DEN PK @ DSB −100 (3/3) — WIN (17–10) — $300
- Sun — 2H #44 DET −1½ @ DSB −105 (3/3) — LOSS (10–10) — $300
- Sun — 2H LAR@LV — not run (blowout gate); SNF KC@SEA — not run

No engine fires other than #1 and #2 (both Sun 10/18). Engine record in range: 2-0.

### Still ungraded or unconfirmed in the range
- Mon 10/19 MNF WAS@SF 1H lean SF −4 @ DSB −115: half score never pulled; no ticket confirmed.
- Closing lines / CLV: not pulled for any board 10/18–10/25 ("CLV pulls for Weeks 6–7 still owed").
- Phong's actual tickets on 10/25: the grade assumed "$500 DISC-UP" on CIN −1 and DEN −3, $300 on the 2-of-3 leans, $300 on each 2H lean and the $150 parlay ("assuming the sizing we discussed; tell me if DEN wasn't $500"). Phong never confirmed in words which 10/25 tickets he placed or at what size.
- 10/18 HOU +½ 1H: gates (Braden Smith / Thomas Jr.) never checked; graded WIN but "stays a paper lean".
- 10/18 night-before passes BAL@CLE, CHI@ATL, NO@NYG and the 8:30 / 9:40 pregame re-reads: never run.
- 10/25 inactive checks for DEN@ARI (~11:35) and the 1:25 games (~11:55): never run; Beck, Branch/Mays, Nacua/McDuffie gates unresolved.
- 10/25 SNF KC@SEA and 10/26 MNF DAL@PHI: recorded on the 7:08 AM spreads table, never run.
- Ledger discrepancy left open: 2H record stated as 22-18-1 on 10/22, corrected to 22-17-1 on 10/23 ("#30–#39 was actually 2-7-1"); the #30 board itself is not in this chat.
- Sizing ruling left open: 10/25 grade said "sizing back to $300 across the board until it does is the honest move" — no "from now on" instruction from Phong followed.
