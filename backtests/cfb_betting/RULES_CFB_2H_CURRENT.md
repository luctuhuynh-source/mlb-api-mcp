# CFB 2H - current rules, v2.3b (flat list written 2026-11-12 from the football doc's "Paste-ready prompt" tab)

Source text: `CFB_2H_tab.txt` (the tab as exported 11/12/2026, 5:20 AM), with the shared tabs `GAME_FLOW_tab.txt` and `ROBINHOOD_tab.txt`. Where this list and the tab differ, the tab controls and the difference is reported to Phong. This list is a reading aid for the run checklist; it has not had the line-by-line audit the NFL list had.

**Dead text in the tab (do not run it):** Anchor Mode as a trigger (v2.0 Rule 1); the 4-book Consensus Mode gap rules of sections 2 to 5 as the engine (v2.0 Rule 2 replaced them); the G5/FCS shadow block (v2.0 Rule 6); the 3-minute cutoff (v1.5); "Market B reference-only" (v1.5a); the FLOW-led lean of v2.1 (v2.2); "Robinhood regulation-only" (v2.3a); the -115 juice cap as the lean's only price test (v2.3b is stricter).

## Run order
- X-01 Canary once per time window, first line of the reply (section 4, v1.4 item 10).
- X-02 Step 0, game-flow read: `get_football_scoreboard` to confirm halftime, then `get_football_drives(event_id, half=1, include_plays=true)` for every game; FLOW table printed before the board (v1.2). Clean margin by the v1.3 definition; missing inputs -> FLOW DATA GAP.
- X-03 Per game, in order: halftime confirmed and time left -> an explicit 2H market at a venue -> hard vetoes -> FLOW -> fair, gates, class -> rank -> ticket (v1.4 item 10). Each game keeps its own clock. The 3rd-quarter kickoff is the only hard stop (v1.5, v2.0 Rule 9).
- X-04 Handoff from a first-half run when one exists; 2H-KICK from a named source or UNKNOWN (v1.4 item 7).

## Engine
- X-05 Engine = price test (v2.0 Rule 2). Fire when a venue price (DSB, Red105, or Robinhood ask + 2 cents) beats the de-vigged halftime fair of outside books **at the same number** by 3.0 points of win probability or more, EV above 0. Two or more outside books; DSB, Red105 and Robinhood never in the consensus. One book only, or books 1.0+ point apart -> SHADOW.
- X-06 Executability (v2.3): edge measured after venue cost; both outside quotes no older than 30 seconds at fire time; fillable size for the full 0.5u; Robinhood bid-ask 4 cents or less. Missing -> SHADOW, `EXEC UNVERIFIED`.
- X-07 Robinhood (v2.0 Rule 3, venue rules tab): state settlement (2H including overtime, v2.3a), strike convention and tie handling before any fire; ask cap 60 cents; spread strikes converted with the v1.3a push table and tagged OFF-STRIKE; more than one point outside the books -> lean or shadow only. On every Robinhood fire also post a limit order at fair minus 2 cents and log fill or no fill.
- X-08 Totals at the same number only; no total is converted across numbers at any venue (v2.3b).
- X-09 Size 0.5u = $150 to win; cap 0.5u per game, 1.5u per time window; window exposure printed (section 1, v2.0 Rule 2). Spread and total both qualifying -> one wager.
- X-10 Pre-ticket checks (v2.0 Rule 4): re-pull outside books and the venue price; one news check for a late-Q2 injury or QB change plus the play-text QB read. A 3+ point gap with unexplained news -> SHADOW.
- X-11 Anchor printed for calibration only (0.50 x close spread, 0.49 x close total, FLOW shift up to 1.5 under v1.4 item 1). It never triggers a fire or a lean (v2.0 Rule 1).

## Gates and vetoes
- X-12 Blowout: lead 28+ -> no fire, all markets; 21 to 27 -> spread dead and the blowout-Under ban stands (logged as shadow) (v1.4 item 6, v2.0 Rule 6).
- X-13 QB status CONTINUING / CHANGED / UNVERIFIED with source and time; a confirmed change needs replacement data, a recompute and a post-news quote; unresolved -> shadow the directional candidate (v1.4 item 5).
- X-14 Wind 15 mph or more sustained: totals dead (section 5).
- X-15 Market status: labelled 2H and tradable; a 3Q live line at "halftime" -> MARKET/STATUS MISMATCH, no fire. Halftime beyond 25 minutes, or any player news or delay -> re-pull before a ticket (v1.4 item 5).
- X-16 Opener gates (key-number movement, ranked-vs-public): PASS, FAIL or UNVERIFIED; `OPENER UNVERIFIED` printed on every affected fire and shadow (v1.4 item 4).
- X-17 Kill switch and ledger line on every output: live record, live ROI, shadow n, mode (section 2).
- X-18 All tiers eligible; tier recorded (v2.0 Rule 6).

## Lean
- X-19 MATCHUP LEAN = CLEAR LEAN v1.0 from the Game-flow tab: 2 of 3 of personnel, FLOW, price, no hard counter; otherwise `NO CLEAR LEAN - pass` with the split (v2.2).
- X-20 Hard counters: lead 21+ (spread lean), net turnovers 2+, wind 15+ on a totals lean, juice worse than -115, and no vote from a missing input (v2.2, v2.3).
- X-21 Lean price gate (v2.3b): every printed lean carries its best venue price, the fair at that number and the tag BETTABLE or PRICE WORSE THAN FAIR - pass. A lean is bet only when BETTABLE.

## Logging
- X-22 Shadow columns every board: home team 2H (NEUTRAL excluded), trailing team favoured, 3Q-kickoff receiving team, leader under 21 without FLOW (v2.0 Rule 7, v2.3).
- X-23 CLV: the 2H line at 3Q kickoff logged for every fire and printed lean; first-observed, decision and executed quotes with times (v1.4 item 7, v2.0 Rule 8).
- X-24 Output format of section 6 on every run, one block per game; RECOMMENDED never omitted: ENGINE, then MATCHUP LEAN; then the shadow log.
- X-25 Grading: every venue on 2H + overtime (v2.3, v2.3a). Live fires and shadows graded apart.
