# NFL Totals track v0.1 (paper only) - rules text of 2026-11-12

**ON HOLD since 11/12/2026, about 1:15 AM. Not run on any board.** Phong: "Lets rewrite the track before you start the pull." The rewrite is `TOTALS_PROTOCOL_v0.2_DRAFT.md`, out for ChatGPT and Gemini review with Claude as manager. Until Phong ratifies a version, boards run as before: ENGINE and MATCHUP LEAN only.

Ratified by Phong, 11/12/2026: "Lets do all 3" (the third item offered was "build totals: I write the totals track, paper only").
Evidence and reasons: `BACKTEST_2026-11-12.md`, sections 6 and 7.

**What this is:** a lean layer for totals, run in the same pass as the game, with its own rules, record and line in RECOMMENDED.
**What it is not:** it changes no engine rule. Engine fires on totals, the Over vetoes (F-33, H-25, H-26), the one-selection-per-game rules for tickets (F-30, H-36) and the 1.5-per-half-point conversion the engine uses for totals (R-07) all stand as written.

## Rules
- T-01 Scope. NFL only. First-half and full-game totals before kickoff; second-half totals at halftime. Same clock rules as the engine it runs beside (kickoff, or the 3rd-quarter kickoff, is the hard stop).
- T-02 Paper only. Every line is $0, with the venue, number and price logged. No size is ever printed. Liem L5.7 and L3.2 govern any step up: review at 30 graded lines; nothing goes to micro-live before 60 lines with a closing price, and only on Phong's word.
- T-03 Under only. No Over line is ever printed by this track. (Backtest: Overs lost in every group tested.)
- T-04 Inputs, three:
  - WIND. Outdoor game (or a confirmed open roof), sustained wind 10 mph or more at kickoff from the weather pull -> WIND on. Dome, closed roof, or an unconfirmed retractable roof -> off.
  - SCORE (second half only). First-half points 28 or more -> SCORE on.
  - PRICE. The Under at each of Phong's venues (DSB, Red105, Robinhood all-in = ask + 2 cents) against the consensus fair for the Under at the same number. Other numbers are converted with the table below. Robinhood half totals are regulation-only: compare only at a sportsbook number and note the settlement; no conversion is written.
- T-05 The line. When WIND or SCORE is on, a paper line is LOGGED for the Under at the best venue price, every time. It is PRINTED in RECOMMENDED only when that price is at the consensus fair or better (edge 0 or more). Otherwise the totals line reads `TOTALS: none` and the entry stays in the ledger, tagged `price worse than fair`.
- T-06 No line at all when: the consensus for the total cannot be priced (`CONSENSUS PRICE UNRESOLVED`); fewer than 3 books post the total; a quarterback change at the half is unresolved (H-27); the weather pull failed (then WIND is unknown, say so at the top, and only SCORE can turn a line on).
- T-07 Output. RECOMMENDED gets a third line after ENGINE and MATCHUP LEAN: `TOTALS (paper, $0): Under <number> <half> @ <venue> <price>, <WIND and/or SCORE>, price <edge> vs fair` or `TOTALS: none`. Nothing else from this track is shown: no shadows, no near-misses (Phong, 10/11).
- T-08 Ledger. Own IDs (T-001 up), own record. Each entry: game, half, number, venue, price, inputs on, edge at the time, result on the venue's settlement, closing fair and CLV. Printed and logged-only entries are graded alike and reported apart.
- T-09 Tickets. If Phong bets a printed totals line it is a DISC ticket under M-02 and Liem L5.6 (leader-side plus Under in the same half is one thesis; 2u cap on the pair). This track never tells him to.
- T-10 Review. At 30 graded entries: beat-close rate, mean CLV minus margin, record by input (WIND, SCORE, both) and by printed vs logged-only. The Under angles are also to be re-tested on 2023-2026 prices when the paid halftime pull is run.

## Table B-NFL-5 (draft v1): share of halves that land exactly on a total
Crossing a whole number moves the Under's (or Over's) win probability by this share; on a whole-number line the push is then taken out of both sides. Source: `backtest_2026-11-12/out_12_totals_structure.txt`.

| Number | Second half (real lines 2011-2021, line within half a point) | First half (2015-2026, derived half total within 2) |
|---|---|---|
| 17 | 11.9% | 8.0% |
| 18 | 0.0% | 1.9% |
| 19 | 3.3% | 4.6% |
| 20 | 5.7% | 9.7% |
| 21 | 5.0% | 3.4% |
| 22 | 2.0% | 1.5% |
| 23 | 4.9% | 7.6% |
| 24 | 7.6% | 7.5% |
| 25 | 1.7% | 0.2% |
| 26 | 2.3% | 3.8% |
| 27 | 7.2% | 8.7% |
| 28 | 0.9% | 3.6% |

Outside 17 to 28, and for full-game totals, no table exists yet: compare at the same number only, else no PRICE read (the line is then logged, not printed).

## What the backtest showed (why these inputs)
- Second-half Unders after a first half of 28+ points: 428-361-17, 54.2% (2011-2021, real lines, -110 assumed).
- Second-half Unders with wind 15+: 143-107-7, 57.2%. Wind 10-14: 53.5%.
- Full-game Unders with wind 10+, 2011 to 2026-11-09: 539-416-10, 56.4%; 57.5% in 2022-2026.
- Break-even at -110 is 52.4%. These are modest and unproven at Phong's venues. That is why the track is paper.

## Open
- Whether the engine should also use table B-NFL-5 in place of the flat 1.5 per half-point (R-07). Not changed; Phong's call.
- A first-half and full-game number table from real lines (none on hand before 2023; the paid pull can supply second-half prices only).
- A regulation-versus-overtime conversion for Robinhood half totals.
