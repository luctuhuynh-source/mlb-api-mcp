# NFL betting - current rules (rules text of 2026-11-12)

**Versions: NFL FG+1H v0.6d. NFL 2H v0.6c. Game-flow read v1.3 with CLEAR LEAN v1.1 (lean price gate, P11), ALWAYS PULL FLOW and QB-CHANGE rows (P15). Robinhood venue rules v1.2 (v1.0, the 10/17 addenda, the 11/12 overtime correction, and totals at the same number only, P12).**

**Ratified 11/12/2026, 6:53 PM PT (change P15, item B closed): a team whose starting QB tonight is not the QB who started its last game gets its FLOW row from that QB's most recent start, tagged `QB-CHANGE`, instead of a void row.** Phong, offered "Ratify the QB-change fix" after the WAS@NYG boards: "Ratify". Origin: 11/9 BUF@MIN, where MIN's void row left the 1H read with one input; the test line BUF -1.5 1H would have won.

**Three decisions by voice, 11/12/2026 about 5:10 AM, written on Phong's typed "Push into repo" (5:11 AM): P11 a lean is bet only at the fair or better; P12 totals are never converted across numbers, spreads keep table B-NFL-3; P13 no settlement-wording check, the rules stay "including overtime" (X-36 closed).**

**NFL Totals v0.3 (second-half Over and Under), in force from 11/12/2026, 5:05 AM, change P10: rules TT-01 to TT-12 in `TOTALS_PROTOCOL_v0.3.md`.** Run in the same pass as the 2H board. Over: first-half yards per play above 5.89, $150 to win. Under: yards per play under 4.93 and at least one team under 55% completions, $75 to win. Both need a price at the fair or better on the consensus number. Each rule drops to shadow by itself if below break-even after 20 bets.

**Corrected 11/12/2026, 3:36 AM (change P9; X-35 and X-31 closed): Robinhood second-half contracts count overtime, like DSB and Red105.** Phong: "RH include over time.  Fix it". Changed below: R-02, H-02, H-12, H-17, H-18, and check C28. Three confirmations: the contract text ("in the 2nd half (including overtime)", on 10/18 and 11/16 contracts for the spread, the total and the winner), Phong's own check in the app, and the 10/15 SEA@DEN overtime game (Seattle won the second half by 11 in regulation and by 8 with overtime; "Seattle wins 2H by over 9.5" settled No).

**Totals track: none in force.** v0.1 was written 11/12 and put on hold the same hour (Phong: "Lets rewrite the track before you start the pull."). The rewrite went through the review panel on 11/12 (ruling in `panel_2026-11-12/`). Its final text, `TOTALS_PROTOCOL_v0.2.md`, is NOT in force. The paid replication of 11/12 failed all three testable totals claims (`BACKTEST_2026-11-12.md`, section 15), so the protocol has no printable cell; Phong decides between a silent ledger and shelving it. Round 2 (number table, 11/12) also failed: `BACKTEST_2026-11-12.md` section 17. Boards print ENGINE and MATCHUP LEAN only.

**Profile in force: current.** Phong, 11/12/2026: "Current but make this can fire by any books instead of dsb only." Strict v0.5 (`RULES_v05_baseline.md`) is run only when he asks for it.

This is the frozen v0.5 (`RULES_v05_baseline.md`) with the nine ratified changes applied (`POST_FREEZE_CHANGES.md`, P1 to P9), every contradiction in `CONTRADICTIONS.md` given one reading, and one formula fix. Built 2026-11-11 from the four doc tabs and the change log; P8 and P9 added 2026-11-12. The football doc stays the source; this file is the flat copy a board is run from.

Marks on each rule:
- `[=]` unchanged from the frozen v0.5.
- `[P1]`..`[P9]` changed by that ratified change (Phong's words are in `POST_FREEZE_CHANGES.md`).
- `[R]` a reading chosen on 11/11 where the doc text disagreed with itself. The reason is given. Phong can overrule any of them.
- `[FIX]` the 11/11 push-table fix (`PUSH_TABLE_B-NFL-3.md`).

How readings were chosen: a later ratified ruling beats an earlier one; a sentence is dropped only when a later ruling expressly replaces it; an NFL-specific table beats a shared-tab figure; Liem v1.1 beats a sport tab ("where this doc and a sport protocol conflict, this doc wins").

---
## Betting policy (was only in memory notes; now also at the top of both NFL tabs)
- M-01 [=] "$300" from Phong means $300 to win. The unit is $300 to win.
- M-02 [=] Phong bets only engine fires and printed MATCHUP LEANs. DISC tickets only on a printed lean or an engine fire; a NO CLEAR LEAN game is a pass for DISC too. Upsizing (DISC-UP) is declared before the price is seen, with the unit, capped at 2u ($600 to win). No parlay on the same thesis as a single. One parlay per slate, $150 to win.
- M-03 [=] Three venues: DSB, Red105, Robinhood. DSB and Red105 are paper accounts; Robinhood is live money. One rule for all three: best price for the side (Phong, 10/25: "Dsb red105 or robinhood").
- M-04 [R] Drawdown line: Liem v1.1 L3.3 replaced every 0-3 kill switch. NFL (full game, 1H and 2H together): 17u = $5,100 down from the NFL equity high sends NFL to shadow and micro-live. Nothing short of that line changes sizing or status. The v0.2 kill-switch paragraphs in both tabs are dead text.
- M-05 [=] Liem L3.1 and L3.2: no promotion or retirement of a class on W-L under n = 200; a class with fewer than 60 closing-line entries reports but never promotes.

---
## Engine A - NFL full-game + 1H, v0.6d (IDs F-xx)

### Scope and venues
- F-01 [=] Pregame window only (line posted to kickoff). Never bet in-play. [P2] "Runs after kickoff are overrides, graded vs the pregame close." [R] Since never-bet-in-play is unchanged, a read made after kickoff is not a recommendation and is labelled as such (11/8 NE -1.5 was printed after kickoff and bet).
- F-02 [P3] Execution venues: DSB, Red105 and Robinhood. (Red105: Phong, 10/25, "I have another platform to use along with dsb. Red105." The doc text was not updated for it until 11/12. It dealt the same numbers as DSB on 10/25, prices within 5 cents.) Every run pulls the Robinhood ladders. Robinhood never enters the consensus; a Robinhood full-game contract is never a 1H signal. Venue tests: R-06 to R-10.
- F-03 [=] Sizing: the unit, $300 to win. The v0.2 "$50K / 0.5u = $250" text is dead. Liem exposure rules sit above the ticket cap.
- F-04 [=] Trigger phrases: "run our NFL board" / "run our NFL 1H protocol" -> read the tab, run on the DSB screens supplied.

### Inputs and pulls
- F-05 [=] Canary first: any tool or data failure or silent workaround flagged at the top before anything else; Robinhood status printed per game.
- F-06 [P7][P6] FLOW for EVERY game on EVERY run (sweep, STATIC games, individual runs, final pulls): each team's most recent completed game (schedule-verified), `half=0` summary plus the 1H split, one FLOW row per team labelled with its source game. A team off a bye uses its last played game, tagged `STALE-1WK`. [P15] A team starting a different QB than in its last game uses that QB's most recent start instead, tagged `QB-CHANGE` (G-07a). FLOW is never skipped for time: inside about T-10 use summary-only pulls (`include_plays=false`) and run the full protocol anyway. `FLOW SKIPPED - TIME PRIORITY` is retired. The only fallback is a tool error, flagged at the top. FLOW never fires a bet, never moves a fair or a size, and is barred from total leans.
- F-07 [=][P6] Consensus pull: 5 or more books, spreads, totals, h2h, spreads_h1, totals_h1. Practice reports. Official inactives from the team sites or the official tracker at the 90-minute mark, not a general search. Weather at kick.
- F-08 [P2] Pull schedule T-100 / T-85 / T-60 / T-30 / T-20 is recommended timing, not a lock. "T-12 terminal audit" means the final pre-kick run. The final run re-pulls the consensus and re-confirms QB1 and inactives before any fire.

### Consensus and fair
- F-09 [=] Leave DSB out; de-vig each book with one documented method; compare probabilities only at identical numbers.
- F-10 [FIX] Across different numbers: convert with the one-sided table B-NFL-3. Cannot convert -> `CONSENSUS PRICE UNRESOLVED`, shadow.
- F-11 [=] A split across a key number is a candidate fair region, not a fair probability.
- F-12 [=] Every executable edge is a win / push / loss estimate at the venue's exact selection, number and price, in implied-probability points.
- F-13 [=] Derived 1H lines (0.50 x FG spread, 0.50 x FG total) are diagnostic only and never authorize a ticket.
- F-14 [=][FIX] Key numbers: FG spreads 3/7/10; FG totals 41/44/47/51; 1H spreads 3/7; 1H totals 13/17/20/23. The frequencies printed in the tab (3 = 15.7%, 7 = 14.2%, 10 = 7.1%, tie = 8.3%, n=337) count either team. They are not push probabilities. Push probability of a 1H line on 3 = 6.5%, on 7 = 7.4%, on 10 = 4.9%, pick'em tie = 7.3% (B-NFL-3).

### Slate workflow (replaces the T-100 watchlist)
- F-15 [P4][P7] Step 1, sweep: Phong sends every DSB 1H screen for the window in one message. Claude pulls 1H and FG consensus and the FLOW rows for every game in one pass and prints one triage row per game: `game | DSB vs modal gap | HOOK? | personnel flag | 1H YPP, giveaways, clean margin per team | provisional lean read | FLAGGED / STATIC`.
- F-15a [P4][P7] FLAGGED when any of: a price gap within 1.5 points of the 3.0 floor; a HOOK candidate; a DERIV-LAG candidate; a confirmed personnel edge (starter QB / OL / WR1 out); a provisional 2-of-3 lean; FLOW alone (1H YPP gap of 1.5 or more with clean margin the same sign, or FLOW plus one other input aligned). Everything else is STATIC.
- F-16 [P4] Step 2, individual runs: each FLAGGED game gets the full run on its own: FLOW tables, injuries and inactives, Robinhood 1H ladder, weather, gap math, conditionals, the CLEAR LEAN test. [R] At most four full runs per window, ranked personnel uncertainty -> DSB divergence -> key-number movement -> trigger readiness; a FLAGGED game past four is logged `TRIAGE OVERFLOW - SHADOW` with its signal kept. (v0.5: "Cap stays four". The 11/1 workflow never retired it. On 11/1 six games were flagged across the day, four of them in the 10 AM window.)
- F-17 [P4][P7] STATIC games print in RECOMMENDED as a one-line `pass` with no lean line and count toward the filtered-game tally like a NO CLEAR LEAN. They still get FLOW rows (P7) and [R] the inactives check (F-18, never retired). A STATIC game is re-swept only if its DSB number moves 1 point or more or an inactive changes a starter: Phong sends the new screen, Claude re-triages that game alone.
- F-17a [P4] Step 3, final pull: FLAGGED games only, after inactives post (about 90 minutes before kickoff), on fresh DSB screens. Tickets are written here.

### Personnel
- F-18 [=][P6] Inactives and starter announcements for EVERY game, flagged or not, at about T-90.
- F-19 [=] RESOLVED = expected QB1 active with no material limitation, or an officially confirmed replacement with markets re-evaluated on current quotes. Unannounced backup, game-time decision, credibly limited, unresolved replacement -> `LINEUP UNRESOLVED - SHADOW ONLY`.
- F-20 [=] Two or more starting OL out -> `OL SHOCK`: re-evaluate FG and 1H; a numeric adjustment only with a documented method, else `UNPRICED`, shadow.
- F-21 [=] Revalidate on the final run; cancel affected conditionals if a new change cannot be resolved before execution.
- F-21a [R] Monitored starters: QB1, OT1, OT2, C, CB1, S1, WR1 (the CLEAR LEAN list, the widest of the three lists in the text).

### Triggers
- F-22 [=] Signal precedence: (1) hard gates (market available, current venue quote, starter confirmed, weather, no adverse key-number crossing); (2) trigger classes; (3) STEAM review; (4) one EV per selection at the venue's number and price; (5) rank; (6) same-game and ticket-cap rules.
- F-23 [=][FIX] HOOK (fire-eligible): DSB (or Red105, read with F-02) flat on a 1H 3 or 7 at -115 or better while the outside books sit on the hook. Work out whether the half-point turns a loss into a push or a push into a win for our side. P_push = the B-NFL-3 one-sided figure (team laying the points wins the half by exactly that number: 3 = 6.5%, 7 = 7.4%). EV = b x P_win - P_loss. Conditional win = P_win / (P_win + P_loss). Fire only when conditional win beats the price's break-even by 3.0 points or more AND EV > 0. Cannot convert -> `HOOK UNPRICED`, shadow.
- F-24 [=] CONSENSUS DIVERGENCE: outside books disagree by more than 0.5 -> shadow only.
- F-25 [=] DERIV-LAG: logged only. Fire-eligible after 20 logged boards (one board = one separately dated slate-wide decision snapshot). Count on 11/11: 0 of 20. After 20, a fire also needs a direct outside 1H comparison, a valid conversion, edge of 3.0 or more and EV > 0. Exclusions: QB scratch inside 10 minutes; DSB suspended; juice worse than -135.
- F-26 [=] Simultaneous triggers: HOOK is the classification, DERIV-LAG supporting; never summed, never two wagers.
- F-27 [=] STEAM: an adverse open-to-current move of 1.0 or more triggers revalidation; a remaining DSB lag keeps eligibility only if no hard gate is violated.
- F-28 [R] Direct gap (fire-eligible): at the venue's exact number and price, the consensus fair win probability at that same number is 3.0 points or more above the price's break-even, and EV > 0. Every hard gate and F-24 apply. Basis: v0.2 fired on "3 cents or more"; v0.4 "keeps the gap as a benchmark"; the 11/1 ratified workflow flags a game "within 1.5 pts of the 3.0 floor"; every board has run it this way. The one fire in this class (11/2 CHI +2.5) closed 0.7 below fair, so this class is graded on the close every time.

### Same game, ranking, cap
- F-29 [=] FG vs 1H evaluated independently; higher verified EV wins; FG only on an exact tie; an unpriced market is never chosen by default.
- F-30 [=] One selection per game.
- F-31 [P2] Ticket cap 3 per window; extras logged `CAP-BLOCKED`. The step-down (2 past T-16, 1 past T-14) is retired.

### Weather
- F-32 [=] Dome or confirmed closed roof -> N/A. Unconfirmed retractable roof -> `WEATHER UNRESOLVED`, totals shadow.
- F-33 [=] Outdoor sustained wind 15+ or gusts 25+ -> `WIND FLAG`: Over fires vetoed (FG and 1H). An Under gains nothing from the flag.
- F-34 [=] Total drop of 2.5+ (FG) or 1.5+ (1H) from open -> `WEATHER REPRICING REVIEW`. Recheck on the final run.

### Execution
- F-35 [P2] The engine may fire on any run completed before kickoff. Kickoff is the only hard stop. Output in two blocks, `EXECUTE NOW` then `SHADOW / LOG`; one line per fire: selection, signed line, worst acceptable price, quote timestamp, expiry.
- F-36 [P2] The T-17 to T-12 placement window, "nothing after T-12" and `TIME-BLOCKED` are retired. A fire off a DSB screen older than the final re-pull is conditional on the price still being live.
- F-37 [=] Confirm the live price immediately before submitting; log the accepted price separately from the recommendation.
- F-38 [=] Suspended line during placement -> abandon, log `SUSPENDED - UNFILLED`, next item. A reopened line needs full revalidation.
- F-39 [R] A 1H line that posts late is live until kickoff (10/17: "may fire on any run completed before kickoff"; the 2H text says the same of a late-posted 2H market). The v0.5 "first appearing after T-20 -> shadow" depended on the T-20 lock that was retired.
- F-40 [=] A conditional = selection + floor price + expiry; never permission to take a worse number or cross a hook.

### Lean layer and output
- F-41 [P1] MATCHUP LEAN under CLEAR LEAN v1.0 (G-09). $0 paper line with the snapshot price logged; graded on hit and beat-market; must cite its FLOW rows. Whether Phong bets it is M-02.
- F-42 [=] Two-part RECOMMENDED section on every run: ENGINE, then MATCHUP LEAN, "none" stated when none.
- F-43 [=] Output order: ENGINE (fires or "none" plus conditionals), MATCHUP LEAN, OWED, LEDGER line.
- F-44 [=] Never override a gate silently; surface conflicts and let Phong decide.

### Ledger, CLV, handoff
- F-45 [=] Log every FIRE / conditional / SHADOW / CAP-BLOCKED / SUSPENDED: game, market, selection, signed line, price, venue, timestamp, disposition.
- F-46 [=] CLV after the close on every entry, per Liem L1.1: the last consensus snapshot before kickoff (historical odds pull); CLV = closing implied probability minus fill implied probability, same side and number; across numbers use B-NFL-3. Report n, beat-close %, mean CLV, mean CLV minus margin. Executed CLV against the accepted ticket.
- F-47 [=] Halftime handoff exported for the 2H engine: 1H score, FLOW, pregame 1H market history, personnel, weather, open FG tickets.
- F-48 [R] Kill switch: retired, see M-04.

---
## Engine B - NFL 2H, v0.6c (IDs H-xx)

### Scope and venues
- H-01 [=] Halftime window only. Nothing is ever placed after the 3rd-quarter kickoff.
- H-02 [P3][P9] Execution venues: DSB, Red105 and Robinhood. Every halftime run pulls the Robinhood 2H ladders. All three settle a second half with overtime included (DSB confirmed 10/4; Red105: Phong, 11/6; Robinhood: contract text "2nd half (including overtime)" and Phong, 11/12). Grade each ticket on its venue's own result. A Robinhood 2H price is compared with the consensus fair like any other venue price: all-in = ask + 2 cents (R-06), the venue limits of R-03, and R-07 when the strike is not the consensus number. Robinhood never enters the consensus. Retired with P9: "Robinhood 2H contracts are regulation-only", the `CONSENSUS PRICE UNRESOLVED` shadow for a Robinhood price that overtime could change, and the "more than 8 points from the tie margin" test.
- H-03 [=] DSB 2H spreads and totals include overtime (confirmed 10/4). Grade DSB on 2H + OT. The OT-unknown veto is retired; every remaining mention of it in the tabs is dead text.
- H-04 [=] Sizing: the unit, $300 to win.
- H-05 [=] DSB-only engine ledger started at 0-0 on 10/11; the old 4-1 is history, tagged by venue.

### Inputs
- H-06 [=] Phong sends the DSB "NFL 2nd Half" screenshot and "run 2H on [games]". Claude pulls the rest.
- H-07 [=] Load the pregame handoff first; verify the score against the ESPN halftime board: `HANDOFF VERIFIED / INCOMPLETE / UNAVAILABLE`. Nothing fabricated.
- H-08 [=] Scoreboard -> confirm halftime, note the 2H kickoff receiver (`2H-KICK`).
- H-09 [=] Drives (`half=1`, plays included) -> FLOW table. Never run on a half-empty box; data problems flagged at the top.
- H-10 [=] Odds: live 2H spreads and totals and the live full-game line; Robinhood 2H ladders; pregame close; weather for outdoor totals.

### Consensus
- H-11 [=][FIX] Outside 2H quotes must match DSB's market and settlement (overtime in). Leave DSB out. Compare only at identical numbers; across numbers convert with B-NFL-3, else `CONSENSUS PRICE UNRESOLVED`, shadow.
- H-12 [FIX][P9] The tab's push table (3 = 9.5%, 7 = 12.5%, 10 = 6.8%, tie = 10.7%, n=337) counts either team, regulation only. Push probability of a 2H line, at every venue (overtime in): 3 = 5.6%, 7 = 7.3%, 10 = 4.7%, level = 7.3%. The separate Robinhood (regulation) figures (6.1%, 7.5%, 4.8%, 7.7%) are retired with P9.
- H-13 [=] Count independent sources, not unique quote combinations.

### Fire path
- H-14 [=] Sweep: scoreboard, one odds call per market for every game, DSB posted or `OFFLINE`.
- H-15 [=] Convergence screen: before marking `CONVERGED` check availability, freshness, settlement and whether the DSB-vs-median difference touches 3 or 7. Any favourable half-point crossing, landing on or moving off 3 or 7 is a `HOOK CANDIDATE` and is evaluated, never cleared by the 0.5 tolerance.
- H-16 [=] Direct 2H consensus and the FG-derived benchmark are evaluated independently; same selection from both -> one EV; material disagreement -> `BENCHMARK CONFLICT`, shadow.
- H-17 [=][FIX][P8] HOOK: a venue (DSB, Red105; Robinhood by its strike and all-in price, R-03 and R-06) on a favourable 2H number around 3 or 7; at a sportsbook the price must be -115 or better. [R] The frozen text says "DSB"; P8 made the divergence exception venue-neutral and the base rule has to match it. P_push from H-12 (one-sided, overtime in, the same at every venue since P9). Fire only when conditional win is at break-even + 3.0 points or more AND EV > 0. No distribution -> `HOOK UNPRICED`, shadow.
- H-18 [P5][P8] CONSENSUS DIVERGENCE: outside books disagree by more than 0.5 -> shadow. Exception (v0.6b, 11/12): a HOOK candidate stays fire-eligible at any of Phong's venues (DSB, Red105 or Robinhood) if, and only if, that venue's number is strictly better for the bet side than the number at every book in the consensus pull, not equal to any. The edge is computed against the nearest book number (the one least favourable to the bet) with the push table (H-12) and must still clear the 3.0 floor at that venue's price (Robinhood: ask + 2 cents, R-03 applies; no overtime restriction since P9). More than one venue qualifies -> better-EV venue first, one ticket (H-36). Ties the best book, or beats the modal but not the outlier -> shadow. Until 11/12 this exception was DSB only (v0.6a). Valid fires under either wording so far: none (11/1 LAR -3 was issued after the 3Q kickoff).
- H-19 [R] Direct gap (fire-eligible): a DSB number 1.5 points or more better than the leave-out 2H median opens the evaluation (v0.4); it fires only when the edge priced at DSB's exact number and price is 3.0 points or more with EV > 0 (the uniform practice, and the wording of P5). A smaller number gap that still prices to 3.0 or more is evaluated the same way.
- H-20 [=] DERIV-LAG: implied 2H spread = live FG home spread + 1H home margin; implied total = live FG total - 1H points. 1.0 point or 5 probability points = `LAG REVIEW` only. A live quote is usable only with both sides up, age under 60 seconds, overround under 7.5%. Persistence: two observations 45-60 seconds apart, else `PERSISTENCE UNVERIFIED`, shadow. Shadow phase of 20 boards: log both the immediate and the persisted signal. No fire before 20 boards. Count on 11/11: 0 of 20 (no board has logged the persistence pair).
- H-21 [=] Anchor Mode (0.50 x pregame spread, 0.50 x pregame total) is diagnostic, shadow-only. Every "Anchor Mode fires" line in the v0.2 block and the Robinhood tab is dead text.
- H-22 [=] `NO BENCHMARK` -> shadow only.

### Gates
- H-23 [=] Hard gates before any trigger executes.
- H-24 [=] `BLOWOUT REVIEW` at a halftime lead of 17+: a 2H spread on the team leading by 17+ is ineligible; the opposing spread and both totals run under ordinary gates. (The v0.2 "lead 17+ -> total under only" is dead text.)
- H-25 [=][R] 1H combined 41+ -> `REGRESSION WATCH`, note only. 45+ -> affected Over candidates shadow-only (v0.5; the v0.2 "needs a 2 pt gap" and v0.4 "+2.0" lines are superseded).
- H-26 [=] Wind 15+ sustained or gusts 25+ -> 2H Overs dead, Unders eligible (dome N/A).
- H-27 [=] QB change at half -> `QB UNRESOLVED`, shadow, until a confirmed replacement and current quotes under that starter are checked.
- H-28 [=] Opener: `VERIFIED OPENER` = earliest valid DSB 2H quote; first seen = `FIRST OBSERVED`; unestablished -> `OPENER UNVERIFIED`, and UNVERIFIED on a line sitting on 3 or 7 -> shadow only.
- H-29 [=] Halftime margin 3 or less: OT flag logged (research).
- H-30 [=] `OPEN FG SAME GAME` flagged when the handoff shows an open full-game ticket; never auto-offset.

### Clock
- H-31 [P2] Per-game halftime clock: halftime start and estimated 3Q kickoff, both logged in Pacific time on every board (the 2H close cannot be pulled without them).
- H-32 [=] Default ONE deep review; a second only when measured time fits before the 3Q kickoff.
- H-33 [=] Deliver each verified ticket immediately.
- H-34 [P2][R] The 3Q kickoff is the only hard stop. Retired: "under 3 minutes of halftime left -> shadow only" (10/17, named) and the Q3 -4 lock (10/17: "the engine may fire on any run completed before the 3rd-quarter kickoff"). v0.6a's "the Q3 lock [is] unchanged" refers to the 3Q-kickoff stop.
- H-35 [P2] `OFFLINE`: DSB 2H spread and total tracked separately; re-poll at T+5 and T+8. A DSB 2H market that posts any time before the 3Q kickoff is live.
- H-36 [=][P2] Suspended during placement: one re-poll while the 3Q has not kicked, then shadow. One 2H market per game. A fire off a DSB screen older than the latest re-pull is conditional on the price still being live.

### FLOW use
- H-37 [=] Clean margin per G-02 (points, not drives). FLOW shift only if |YPP edge| is 1.5+ AND clean margin has the same nonzero sign; else `FLOW CONFLICT` / `FLOW NEUTRAL` / `FLOW DATA GAP`. Print ORIGINAL ANCHOR, FLOW-ADJUSTED ANCHOR, KICKOFF-CAPPED SHADOW.
- H-38 [=] FLOW may not generate a 2H total fire or a directional lean on a total during the 20-board test; every board prints a `FLOW-TOTAL (SHADOW)` line (or "no view").

### Lean layer, output, ledger
- H-39 [P1] MATCHUP LEAN under CLEAR LEAN v1.0 (G-09). $0 paper line, graded on the 2H result on the venue's settlement basis (hit and beat-market). Must cite FLOW rows. IDs follow `LEDGER_REBUILT.md` (the old #-numbers collided and are dropped).
- H-40 [=] Output: ENGINE, hard gates, executable numbers and prices, expiry and ticket instructions first; concise FLOW table. Two-part RECOMMENDED on every run.
- H-41 [=] Per-game log fields: event id, halftime score and margin, halftime start, est. 3Q kickoff, 2H-KICK, live FG consensus, implied 2H line, DSB 2H line and price, delta, persistence T1/T2, gates, status, fill time and price.
- H-42 [=] CLV: after the 3Q starts, the last valid pre-3Q consensus quote via the historical pull; no reliable close -> `CLOSE UNAVAILABLE`. How-to, not a rule: if the board did not log the 3Q kickoff, the wall-clock time of the first 3rd-quarter play in nflverse play-by-play (`time_of_day`) gives it the next day; pull the last snapshot at least 30 seconds before it (`review_2026-11-11/05_clv_2h.py`).
- H-43 [R] Separate 2H kill switch: retired, see M-04.

---
## Shared - Game-flow read v1.1 with CLEAR LEAN and ALWAYS PULL FLOW (IDs G-xx)
- G-01 [=] Eight FLOW metrics per team: YPP edge, clean margin, short-field share, sustain rate, 3-and-out rate, RZ conversion, tempo, last-3. Rates print numerator and denominator.
- G-02 [=] Clean margin (6.1): actual points; exclude return TDs, scoring drives starting strictly inside the opponent's 40, scoring drives gaining under 30 net yards; each event excluded once; reconcile to the linescore.
- G-03 [=] The read never fires a bet, never moves a consensus fair, a gap, sizing or a veto.
- G-04 [=] QB and injury text reads (6.4): `QB ROTATION SUSPECTED / CONFIRMED`; `INJURY REPORTED`; missing verification never becomes PASS.
- G-05 [=] Halftime sequencing (6.8): status -> DSB 2H market present -> hard vetoes -> compact FLOW table -> fair, gates, class -> rank -> ticket. A candidate whose mandatory read did not run -> `SHADOW - UNVERIFIED`.
- G-06 [=] Data integrity (6.9): verify event ID, teams, period, drive chronology, scoring reconciliation, orientation, play text. Discrepancy -> `FLOW DATA CONFLICT`.
- G-07 [P7][P6] Previous-game selection (6.7): most recent completed game from the schedule; each row labelled with its source game; bye -> last played game, `STALE-1WK`. The time-priority skip is retired for every football engine.
- G-07a [P15] QB-CHANGE row (pregame 1H and full-game runs). When the QB starting tonight is not the QB who started the team's most recent completed game (a backup in, or QB1 back from injury), the team's FLOW row comes from the most recent game THIS QB started for this team this season, labelled with its source game and tagged `QB-CHANGE` (plus `STALE-nWK` when it is older than last week). If he has no start for this team this season (first career start, new signing, trade), the row is `FLOW DATA GAP - QB-CHANGE` and the FLOW input does not count, as before. The starter is the one confirmed under F-19; until then the row is provisional. Half-time runs are unchanged: their FLOW is the half just played (H-27 still governs a QB change at half). Phong, 11/12: "Ratify".
- G-08 [=] Audit fields (6.10) on every fire, shadow and lean.
- G-09 [P1] CLEAR LEAN v1.0. Three inputs: PERSONNEL (monitored starters QB1, OTs, C, CB1, S1, WR1 out or credibly limited; which side gains). FLOW (the per-team rows: YPP, giveaways, clean margin, sustain rate; the 1H split for 1H runs, the 1H just played for 2H runs). PRICE (which side DSB prices at or above the leave-out fair: the side with the smaller negative edge, or a positive one). A lean prints only when at least 2 of the 3 point the same way AND there is no hard counter from the third. Hard counter = a QB1 scratch or unannounced backup, a FLOW gap of 1.5 YPP or more against the side, or two or more monitored starters out on the side being leaned. Otherwise the line reads exactly `NO CLEAR LEAN - pass` plus one line naming the split.
- G-10 [R] Two aligned inputs with no hard counter print the lean. "Soft" is not a term in the rule; the 11/8 "two soft inputs is not clear" ruling was stricter than the text.
- G-11 [P1] Every NO CLEAR LEAN is logged with its split and graded as a paper no-bet on the same close, for an audit of the filter at 30 filtered games. OPEN: the text never says which side the paper no-bet is on (review decision 3).
- G-12 [R] Dead text in sections 1 and 3 of the tab: "the <3-min rule" (retired 10/17) and the "DSB-OT veto" (retired 10/4).
- G-13 [P11] LEAN PRICE GATE (CLEAR LEAN v1.1). A clear lean still prints. It prints with the best venue price for its side and the consensus fair at that number, and one tag: `BETTABLE` when the venue price is at the fair or better (Robinhood: ask + 2 cents), or `PRICE WORSE THAN FAIR - pass`. A lean is bet only when it is BETTABLE. Phong, 11/12: "Fair or better." Basis: his 46 half bets, 12-5 at the fair or better and 12-15-2 worse (a pattern on few bets, not proof). G-03 is unchanged: the read never fires an engine bet.

## Shared - Robinhood venue rules v1.0 with the 10/17 addenda (IDs R-xx)
- R-01 [=] Contracts: KXNFL1HSPREAD / TOTAL / WINNER, KXNFL2HSPREAD / TOTAL / WINNER, KXNFLSPREAD / TOTAL / GAME; pulled with `kalshi_get_markets`. No pull and no screen -> "RH: none".
- R-02 [P9] Price = the ask on the side bought. A first-half contract settles on the first half alone. Second-half and full-game contracts include overtime (contract text; Phong, 11/12). The frozen wording "Halves are regulation-only" was right through Sunday 9/13/2026 and wrong from Monday 9/14/2026: the exchange changed "(excluding overtime)" to "(including overtime)" between those two days (found 11/12, `BACKTEST_2026-11-12.md` section 18.1; week 1's New Orleans at Detroit settled on regulation). No rule makes a run read the wording, by Phong's decision of 11/12 (P13).
- R-03 [=] Ask cap 60 cents; bid-ask spread 4 cents or less with a resting ask.
- R-04 [=] Never buy across a key number to reach a cheaper ask. A full-game contract is never a half signal.
- R-05 [P3] Robinhood is an execution venue for both NFL engines (10/17). The tab's intro "co-primary", v0.4 "reference-only" and v0.6a "DSB-only execution venue" are all superseded by this.
- R-06 [P3][R] Price test: Robinhood all-in price = ask + 2 cents per contract, compared with the consensus fair at the same strike. An engine fire at Robinhood needs fair minus all-in price of 3.0 points or more (the engine's floor), plus R-03. The tab's older "ask <= fair" is the minimum for any Robinhood ticket, not the fire test.
- R-07 [FIX][R] Off-strike (the Robinhood strike is not the consensus number): convert the consensus fair to the strike with B-NFL-3. For NFL this replaces "CFB/NFL 1H: 3 = 11.5%, 7 = 15.3%, tie 5.7%" (CFB figures), "2.5 cents per half-point (5 crossing 3 or 7)" and the flat "2.0 points per half-point". Totals: 1.5 points per half-point, unchanged and untested.
- R-07a [P12] Totals are compared at the same number only, at every venue and in both engines. The flat "1.5 points per half-point" is retired: a total whose venue number is not the consensus number is not priced and cannot fire. Spreads keep the B-NFL-3 conversion. Phong, 11/12: "Yes, I agree." Basis: `BACKTEST_2026-11-12.md` sections 17 and 18 (converted totals 12-16 at the books, 4-5 at Robinhood; the better-built table failed its check).
- R-08 [R] NFL key numbers are the engine tabs': full game 3/7/10, halves 3/7. The Robinhood tab's "3, 7, 10, 14" is the shared CFB/NFL list.
- R-09 [R] When more than one venue passes, name the better-EV venue first (10/17; three venues since 10/25). An exact tie goes to DSB (the tab's older tie rule, which the 10/17 line does not contradict).
- R-10 [R] Size at Robinhood: the unit is $300 to win, so contracts = 300 / (0.98 - ask) and risk = contracts x (ask + 0.02). The tab's "contracts = size / ask" gives that count only if "size" is read as dollars risked.

---
## Open, not rules
- Closed 11/12 (P15, G-07a): item B ratified. QB-change FLOW rows use the starting QB's most recent start for the team this season, tagged `QB-CHANGE`.
- Paper side for NO CLEAR LEAN games (G-11).
- Closed 11/12 (P11, G-13): a lean is bet only at the fair or better.
- Closed 11/12 (P13): no run check on the Robinhood settlement wording. Phong: "No, no need to do that. But just keep the wording, including overtime". If the exchange changes the wording again, nothing in a run will catch it.
- Totals: no push table; FLOW-TOTAL shadow test still short of 20 boards, and the shadow line has no written test. A screen on 990 real second-half totals (11/12, `BACKTEST_2026-11-12.md` section 16) points to first-half yards per play (Over above 5.89 combined, Under below 4.93); a written shadow test is proposed there and waits for Phong. H-38 unchanged. A Totals track is written and reviewed (`TOTALS_PROTOCOL_v0.2.md`, final text after the 11/12 panel; v0.1 on hold). Its Under cells failed the paid replication on 11/12. Not in force; Phong decides between a silent ledger and shelving it. The engine's own totals conversion (R-07, 1.5 per half-point) is unchanged; whether it should use table B-NFL-5 is Phong's call.
- Closed 11/12 (P9): no method is needed to restate an overtime-in fair on a regulation basis. Robinhood second-half contracts count overtime.
- Robinhood at halftime, tested 11/12 on all 136 games of 2026 (`BACKTEST_2026-11-12.md` section 18): its price sits on the books' fair and costs about 2.7 points to take; at the same number the 3.0 floor showed in 3 of 125 games; 28 of 31 would-be fires rest on a converted number (R-07) and went 13-15, +7.0%; resting orders filled 9% of the time and went 15-23. No rule changed. The proposed settlement-wording check was declined (P13).
