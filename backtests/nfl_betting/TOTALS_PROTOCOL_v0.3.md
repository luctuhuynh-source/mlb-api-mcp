# NFL Totals protocol v0.3 - second-half totals, Over and Under - IN FORCE from 11/12/2026

**Status: IN FORCE, live at reduced size, on Phong's word.** Worked out by voice on 11/12/2026 between about 4:25 and 5:00 AM and written at 5:05 AM. Phong: "package to be under protocol and uh, under only and also push it to uh, repo, make it live". On running it: one totals run checks both sides on every game.

v0.2 (`TOTALS_PROTOCOL_v0.2.md`) and v0.1 are superseded. Their wind and high-scoring-first-half rules are out: both failed at real prices (`BACKTEST_2026-11-12.md`, section 15).

## What the evidence is, said plainly
- Both rules come from **screens** on 990 games that were opened many times on 11/12. Neither is proven.
- The Under rule is not the claim that was fixed in advance (that one caught 33 games and could not be judged). It is one of seven side-looks (section 19).
- The manager's recommendation was a shadow rule first. Phong chose live now, because the season is short and the Under side had nothing else. The reduced size and the stop below are the answer to that risk.

## Rules

- **TT-01 Window.** Second half only. Run at halftime, in the same pass as the NFL 2H board. One totals line per game: Over, Under or "no view".
- **TT-02 Flow number.** Combined first-half yards per play: both teams' first-half yards divided by both teams' first-half plays (built for the backtest by `backtest_2026-11-12/halftime_pull/26_build_h1_flow.py`; at halftime, from the play-by-play or box score of the half). Print the number.
- **TT-03 OVER rule.** Yards per play above **5.89**. Screen: 330 games, 56.2%, +5.1% (+1.4% in 2023-24, +10.6% in 2025-26); section 16.
- **TT-04 UNDER rule.** Yards per play under **4.93** AND at least one team under **55%** first-half completions (completions divided by completions + incompletions + interceptions; sacks, spikes and kneels left out). Print both teams' rates. Screen: 168 games, 59.1%, +10.6% (+16.9% then +3.4%); section 19.
- **TT-05 Personnel flag (judgment, cannot be backtested).** A top receiver or the starting tight end confirmed out during the first half. It strengthens an Under that already fires under TT-04. It never fires alone and never moves the size. It is printed and logged as its own tag so its record can be read apart.
- **TT-06 Price gate.** The bet needs a price at the fair or better at one of Phong's venues (DSB, Red105, Robinhood), **at the same number as the consensus**. Fair = median no-vig price of the books posting that number, two or more books. Robinhood: ask + 2 cents, and rule R-03. No conversion across numbers.
- **TT-07 Size.** Over: half a unit, $150 to win. Under: a quarter unit, $75 to win.
- **TT-08 Stop.** Each rule is counted on its own. If a rule is below break-even after 20 graded bets, it goes back to shadow by itself and Phong is told at the top of that reply.
- **TT-09 No price, no bet.** Trigger met but no venue at the fair or better on the same number: the line reads "trigger met, no price" and is logged at $0.
- **TT-10 Ledger.** Every game run is logged: yards per play, both completion rates, the personnel tag, the consensus number and fair, the venue price taken, the result. A price-only line (same price gate, no flow) is logged silently beside each bet, so it can be seen whether flow adds anything (the doubter's condition).
- **TT-11 Not a side signal.** A totals line never changes a side lean, and a side lean never changes a totals line.
- **TT-12 Review.** At 20 graded bets per rule (TT-08), and again at season's end.

## Not in this protocol
- First-half and full-game totals. Wind. Points scored in the first half as a trigger. Any conversion between totals numbers.
