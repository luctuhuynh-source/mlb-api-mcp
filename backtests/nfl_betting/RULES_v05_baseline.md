# NFL betting - frozen baseline rules (10/11/2026 freeze)

Source: football doc tabs "NFL full-game + 1H prompt" (rev 9), "NFL 2H prompt" (rev 10), "Game-flow read (all engines)" (rev 13),
"Robinhood venue rules (all engines)" (rev 4), "Analysis & change log". Read 2026-11-11.

Freeze entry (change log, 10/11/2026 ~6:17 AM, Phong: "Lets freeze our current models on all protocols"):
frozen NFL FG+1H v0.5, NFL 2H v0.5, Game-flow read v1.1, Robinhood venue rules v1.0, until each engine has 20 boards graded under
that version; one data-driven review then. Permitted during the freeze: bug fixes to a wrong formula or tool quirk, grading and
ledger work, background audits. Not permitted: threshold, gate, anchor, sizing or venue changes, new review rounds.

v0.5 is layered: v0.2 text, amended by v0.3, v0.4, v0.5. This list is the net rule set as of the freeze. Where a layer left a
question open it is marked [AMBIGUOUS] and listed in CONTRADICTIONS.md. Rule IDs are new (this file); the doc has none.

---
## Engine A - NFL full-game + 1H, v0.5  (IDs F-xx)

### Scope and venues
- F-01 Pregame window only (line posted to kickoff). Never bet in-play.
- F-02 Execution venue: DiamondSB (DSB) only. Robinhood is reference-only (v0.4, Liem D7). RH ladders are pulled every run for reference/CLV; RH never enters the consensus; an RH full-game contract is never a 1H signal.
- F-03 Sizing: Liem unit, $300 to win. The v0.2 "$50K / 0.5u = $250" text is superseded. Liem exposure rules sit above the ticket cap.
- F-04 Trigger phrases: "run our NFL board" / "run our NFL 1H protocol" -> read the tab, run on the DSB screens supplied.

### Inputs and pulls
- F-05 Canary first: any tool/data failure or silent workaround flagged at the top before anything else; RH status printed per game.
- F-06 FLOW read before the odds pulls: both teams' most recent completed game (schedule-verified, not "last Sunday"), get_football_drives half=0 summary plus the 1H split; FLOW table per team. Note-only. Fallback under v0.5: skip and say so (FLOW SKIPPED - TIME PRIORITY).
- F-07 Consensus pull: 5 or more books, spreads, totals, h2h, spreads_h1, totals_h1. Wed/Thu/Fri practice reports, official inactives (90 min pre-kick), weather at kick.
- F-08 Pull schedule per kickoff window: T-100 baseline, T-85 (post-inactives), T-60, T-30, T-20 decision pull, T-12 terminal audit. Primetime/standalone add 5-minute polling T-30 to T-12, except Thursday (six pulls only).

### Consensus and fair
- F-09 Leave-DSB-out; de-vig each book with one documented method; compare probabilities only at identical numbers.
- F-10 Across different numbers: convert with a documented distribution carrying push mass (1H spreads at 3/7: the B-NFL-2 table). No conversion -> CONSENSUS PRICE UNRESOLVED, shadow.
- F-11 A split across a key number is a candidate fair region, not a fair probability.
- F-12 Every executable edge is a win/push/loss estimate at DSB's exact selection, number and price, stated in implied-probability points.
- F-13 Derived 1H lines (0.50 x FG spread, 0.50 x FG total) are diagnostic only and never authorize a ticket.
- F-14 Key numbers: FG spreads 3/7/10; FG totals 41/44/47/51; 1H spreads 3/7 (exact 3 = 15.7%, 7 = 14.2%, 10 = 7.1%, tie = 8.3%, n=337); 1H totals 13/17/20/23.

### Triage
- F-15 T-100 watchlist if any: FG consensus moved 1.0+ from open; DSB off the leave-out consensus by 0.5+ pts or 5+ cents; a monitored starter (QB1, OT1/OT2, C, CB1) Q/D/GTD on Friday; outdoor sustained wind 15+ or gusts 25+.
- F-16 Cap: four games get full treatment per window, ranked personnel uncertainty -> DSB divergence -> key-number movement -> trigger readiness.
- F-17 Every pull runs a lightweight screen on EVERY game, STATIC included; STATIC = DEEP REVIEW DEFERRED; print NONE only after a current check. Pending signals are stored and never erased by demotion (TRIAGE OVERFLOW - SHADOW).

### Personnel
- F-18 T-85: inactives and starter announcements for EVERY game, watchlist or not.
- F-19 RESOLVED = expected QB1 active with no material limitation, or an officially confirmed replacement with markets re-evaluated on current quotes. Unannounced backup, GTD, credibly limited, unresolved replacement -> LINEUP UNRESOLVED - SHADOW ONLY.
- F-20 Two or more starting OL out -> OL SHOCK: re-evaluate FG and 1H; numeric adjustment only with a documented method, else UNPRICED, shadow.
- F-21 Revalidate at T-20; cancel affected conditionals if a new change can't be resolved before execution.

### Triggers
- F-22 Signal precedence: (1) hard gates (market available, current DSB quote, starter confirmed, weather, no adverse key-number crossing); (2) trigger classes; (3) STEAM review; (4) one EV per selection at DSB's number and price; (5) rank; (6) same-game and ticket-cap rules.
- F-23 HOOK (fire-eligible): DSB flat on a 1H 3 or 7 at -115 or better while outside books sit on the hook. Estimate P_win/P_push/P_loss at DSB's number with the exact-margin table; EV = b*P_win - P_loss; conditional win = P_win/(P_win+P_loss). Fire only when conditional win beats break-even by 3.0+ points AND EV > 0. Cannot convert -> HOOK UNPRICED, shadow.
- F-24 CONSENSUS DIVERGENCE: outside books disagree by more than 0.5 -> shadow only.
- F-25 DERIV-LAG: logged only; fire-eligible after 20 logged boards (one board = one separately dated T-20 slate-wide snapshot). FG move 1.0+ from T-100 opens a LAG REVIEW. Fire additionally needs a direct outside 1H comparison, a valid conversion, edge 3.0+ and EV > 0. Exclusions: QB scratch inside 10 min; DSB suspended; juice worse than -135.
- F-26 Simultaneous triggers: HOOK is the classification, DERIV-LAG supporting; never summed, never two wagers.
- F-27 STEAM: an adverse open-to-current move of 1.0+ triggers revalidation; a remaining DSB lag keeps eligibility only if no hard gate is violated.
- F-28 [AMBIGUOUS] Direct gap: v0.2 fired on 1.5 pt spread / 2 pt total / 3 cent price gaps; v0.4 "keeps the gap as a benchmark". Whether a plain same-number price gap of 3.0+ points is a fire class in v0.5 is not stated. It has been run as one (11/2 CHI +2.5).

### Same game, ranking, cap
- F-29 FG vs 1H evaluated independently; higher verified EV wins; FG only on an exact tie; an unpriced market is never chosen by default.
- F-30 One selection per game.
- F-31 Ticket cap 3 per window (2 if delivery slips past T-16, 1 past T-14); extras logged CAP-BLOCKED.

### Weather
- F-32 Dome / confirmed closed roof -> N/A. Unconfirmed retractable roof -> WEATHER UNRESOLVED, totals shadow.
- F-33 Outdoor sustained 15+ or gusts 25+ -> WIND FLAG: Over fires vetoed (FG and 1H). An Under gains nothing from the flag.
- F-34 Total drop of 2.5+ (FG) / 1.5+ (1H) from open -> WEATHER REPRICING REVIEW. Recheck at T-20.

### Execution clock (the time locks)
- F-35 Board delivered at T-20, queue by T-17. Two blocks: EXECUTE NOW, then SHADOW / LOG. One line per fire: selection, signed line, worst acceptable price, quote timestamp, expiry.
- F-36 Placement window T-17 to T-12. Nothing is placed after T-12; the T-12 pull closes unfilled conditionals as TIME-BLOCKED.
- F-37 Confirm the live DSB price immediately before submitting; log accepted price separately from the recommendation.
- F-38 Suspended line during placement -> abandon, log SUSPENDED - UNFILLED, next item. A reopened line needs full revalidation.
- F-39 Late-posted 1H: quotes first appearing after T-20 -> shadow for that window.
- F-40 A conditional = selection + floor price + expiry; never permission to take a worse number or cross a hook.

### Lean layer and output
- F-41 MATCHUP LEAN: one line per game examined, $0 paper, snapshot price logged, graded on hit and beat-market. (No CLEAR LEAN filter in v0.5: every game examined gets a lean line.) Must cite its FLOW rows.
- F-42 Standing two-part RECOMMENDED section on every run.
- F-43 Output order: ENGINE (fires or "none" plus conditionals), MATCHUP LEAN, OWED, LEDGER line.
- F-44 Never override a gate silently; surface conflicts and let Phong decide.

### Ledger, CLV, handoff
- F-45 Log every FIRE / conditional / SHADOW / CAP-BLOCKED / TIME-BLOCKED / SUSPENDED: game, market, selection, signed line, price, source, timestamp, disposition.
- F-46 CLV after close on every entry: last valid pre-kick DSB quote and leave-out consensus via the historical odds pull. Executed CLV against the accepted ticket. Shadows get SHADOW QUOTE-TO-CLOSE.
- F-47 Halftime handoff exported for the 2H engine: 1H score, FLOW, pregame 1H market history, personnel, weather, open FG tickets.
- F-48 [AMBIGUOUS] Kill switch (v0.2: 0-3 on live fires -> shadow; checkpoints at 5 and 10 fires) is never restated or retired after v0.2.

---
## Engine B - NFL 2H, v0.5  (IDs H-xx)

### Scope and venues
- H-01 Halftime window only. Nothing is ever placed after the 3rd-quarter kickoff.
- H-02 DSB is the only execution venue (v0.4). RH ladders pulled for CLV and price reference only. RH 2H is regulation-only -> OT SETTLEMENT MISMATCH; it never sets DSB's fair.
- H-03 DSB 2H spreads and totals include overtime (confirmed 10/4). The OT-unknown veto is retired. Grade DSB on 2H + OT.
- H-04 Sizing: Liem unit, $300 to win. The "$250 / $125" text is superseded.
- H-05 DSB-only engine ledger starts at 0-0 (10/11); the old 4-1 is history, tagged by venue.

### Inputs
- H-06 Phong sends the DSB "NFL 2nd Half" screenshot and "run 2H on [games]". Claude pulls the rest.
- H-07 Load the pregame handoff first; verify score against the ESPN halftime board: HANDOFF VERIFIED / INCOMPLETE / UNAVAILABLE. Nothing fabricated.
- H-08 get_football_scoreboard -> confirm halftime, note the 2H kickoff receiver (2H-KICK).
- H-09 get_football_drives(half=1, include_plays=true) -> FLOW table (Game-flow tab). Never run on a half-empty box; data problems flagged at the top.
- H-10 Odds: live 2H spreads/totals and live full-game line; RH 2H ladders; pregame close; weather for outdoor totals.

### Consensus
- H-11 Outside 2H quotes must match DSB's market and settlement (OT-inclusive). Leave-DSB-out. Compare only at identical numbers; across numbers a documented conversion with push mass, else CONSENSUS PRICE UNRESOLVED, shadow.
- H-12 Push table (regulation, n=337): exact 3 = 9.5%, 7 = 12.5%, 10 = 6.8%, tie = 10.7% - distribution context only.
- H-13 Count independent sources, not unique quote combinations.

### Fire path
- H-14 Sweep: scoreboard, one odds call per market for every game, DSB posted or OFFLINE.
- H-15 Convergence screen: before marking CONVERGED check availability, freshness, settlement and whether the DSB-vs-median difference touches 3 or 7. Any favourable half-point crossing, landing on or moving off 3 or 7 is a HOOK CANDIDATE and is evaluated, never cleared by the 0.5 tolerance.
- H-16 Direct 2H consensus and the FG-derived benchmark are evaluated independently; same selection from both -> one EV; material disagreement -> BENCHMARK CONFLICT, shadow.
- H-17 HOOK: DSB on a favourable 2H number around 3 or 7 at -115 or better; OT-inclusive P_win/P_push/P_loss; fire only when conditional win >= break-even + 3.0 points AND EV > 0. No distribution -> HOOK UNPRICED, shadow.
- H-18 CONSENSUS DIVERGENCE: outside books disagree by more than 0.5 -> shadow. (No exception in v0.5.)
- H-19 Direct gap (v0.4, not restated in v0.5): DSB 1.5+ pts better than the leave-out 2H median. [AMBIGUOUS: in practice run as "3.0 points of edge".]
- H-20 DERIV-LAG: implied 2H spread = live FG home spread + 1H home margin; implied total = live FG total - 1H points. 1.0+ pt or 5+ probability points = LAG REVIEW only. Live quote usable only with both sides up, age under 60 s, overround under 7.5%. Persistence: two observations 45-60 s apart, else PERSISTENCE UNVERIFIED, shadow. Shadow phase of 20 boards: log both the immediate and the persisted signal. No fire before 20 boards.
- H-21 Anchor Mode (0.50 x pregame spread, 0.50 x pregame total) is diagnostic, shadow-only.
- H-22 NO BENCHMARK -> shadow only.

### Gates
- H-23 Hard gates before any trigger executes.
- H-24 BLOWOUT REVIEW at a halftime lead of 17+: a 2H spread on the team leading by 17+ is ineligible; the opposing spread and both totals run under ordinary gates.
- H-25 1H combined 41+ -> REGRESSION WATCH, note only. 45+ -> affected Over candidates shadow-only.
- H-26 Wind 15+ sustained or gusts 25+ -> 2H Overs dead, Unders eligible (dome N/A).
- H-27 QB change at half -> QB UNRESOLVED, shadow, until a confirmed replacement and current quotes under that starter are checked.
- H-28 Opener: VERIFIED OPENER = earliest valid DSB 2H quote; first seen = FIRST OBSERVED; unestablished -> OPENER UNVERIFIED, and UNVERIFIED on a line sitting on 3 or 7 -> shadow only.
- H-29 Halftime margin 3 or less: OT flag logged (research).
- H-30 OPEN FG SAME GAME flagged when the handoff shows an open full-game ticket; never auto-offset.

### Clock (the time locks)
- H-31 Per-game halftime clock: halftime start, estimated Q3 kick, Q3 -4 lock, ticket expiry.
- H-32 Default ONE deep review; a second only when measured time fits before its own lock.
- H-33 Deliver each verified ticket immediately.
- H-34 Q3 -4 is the hard lock; anything that can't complete -> TIME-BLOCKED. (v0.2: under 3 minutes of halftime left -> shadow only.)
- H-35 OFFLINE: DSB 2H spread and total tracked separately; re-poll at T+5 and T+8; still unposted inside 4 minutes of the 3Q kick -> UNPOSTED / DEAD; late post executable only if everything fits before Q3 -4.
- H-36 Suspended during placement -> abandon, SUSPENDED - UNFILLED. One 2H market per game.

### FLOW use
- H-37 Clean margin per Game-flow 6.1 (points, not drives). FLOW shift only if |YPP edge| 1.5+ AND clean margin same nonzero sign; else FLOW CONFLICT / FLOW NEUTRAL / FLOW DATA GAP. Print ORIGINAL ANCHOR, FLOW-ADJUSTED ANCHOR, KICKOFF-CAPPED SHADOW.
- H-38 FLOW may not generate a 2H total fire or a directional MATCHUP LEAN on a total during the 20-board test; every board prints a FLOW-TOTAL (SHADOW) line (or "no view").

### Lean layer, output, ledger
- H-39 MATCHUP LEAN: one line per game, $0 paper, graded on the 2H result (hit and beat-market); 2H-SHADOW entries numbered. (No CLEAR LEAN filter in v0.5.) Must cite FLOW rows.
- H-40 Output: ENGINE, hard gates, executable numbers/prices, expiry and ticket instructions first; concise FLOW table. Two-part RECOMMENDED on every run.
- H-41 Per-game log fields: event id, halftime score and D, est. Q3 kick, 2H-KICK, live FG consensus, implied 2H line, DSB 2H line and price, delta, persistence T1/T2, gates, status, fill time and price.
- H-42 CLV: after Q3 starts, last valid pre-Q3 DSB quote and independent references via the historical pull; no reliable close -> CLOSE UNAVAILABLE.
- H-43 [AMBIGUOUS] Separate 2H kill switch (9/24: 0-3 on live 2H fires -> shadow) never restated or retired.

---
## Shared - Game-flow read v1.1  (IDs G-xx)
- G-01 Eight FLOW metrics per team: YPP edge, clean margin, short-field share, sustain rate, 3-and-out rate, RZ conversion, tempo, last-3. Rates print numerator and denominator.
- G-02 Clean margin canonical definition (6.1): actual points; exclude return TDs, scoring drives starting strictly inside the opponent's 40, scoring drives gaining under 30 net yards; each event excluded once; reconcile to the linescore.
- G-03 The read never fires a bet, never moves a Consensus fair, a gap, sizing or a veto.
- G-04 QB/injury text reads (6.4): QB ROTATION SUSPECTED / CONFIRMED; INJURY REPORTED; missing verification never becomes PASS.
- G-05 Halftime sequencing (6.8): status -> DSB 2H market present -> hard vetoes -> compact FLOW table -> fair/gates/class -> rank -> ticket. A candidate whose mandatory read did not run -> SHADOW - UNVERIFIED.
- G-06 Data integrity (6.9): verify event ID, teams, period, drive chronology, scoring reconciliation, orientation, play text. Discrepancy -> FLOW DATA CONFLICT.
- G-07 Previous-game selection (6.7): most recent completed game from the schedule; label each row with its source game. Near a lock: FLOW SKIPPED - TIME PRIORITY allowed (v1.1).
- G-08 Audit fields (6.10) on every fire, shadow and lean.

## Shared - Robinhood venue rules v1.0  (IDs R-xx)
- R-01 Contracts: KXNFL1HSPREAD/TOTAL/WINNER, KXNFL2HSPREAD/TOTAL/WINNER, KXNFLSPREAD/TOTAL/GAME; pulled with kalshi_get_markets. No pull and no screen -> "RH: none".
- R-02 Price = the ask on the side bought. Halves are regulation-only; full-game includes OT.
- R-03 Ask cap 60 cents; bid-ask spread 4 cents or less with a resting ask.
- R-04 Never buy across a key number to reach a cheaper ask. A full-game contract is never a half signal.
- R-05 Under the frozen NFL engines (F-02, H-02) RH is reference-only, so R-03 and the fire test are not used for execution.

## Rules that exist only in memory notes, not in the doc
- M-01 "$300" from Phong means $300 to win (10/5).
- M-02 Phong bets only engine fires and MATCHUP LEANs (10/11). Upsizing: declared before the price with the unit, class DISC-UP, cap 2u ($600 to win); no parlay on the same thesis; one parlay per slate at $150 to win.
- M-03 DSB is a paper account (10/11); Robinhood is live.
