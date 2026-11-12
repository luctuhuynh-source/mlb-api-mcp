# Round-2 test plan - LOCKED 2026-11-12, about 3:30 AM, before any of it is graded

After the round-2 panel (`../../panel_2026-11-12/round2/`): Gemini (scout) and ChatGPT (doubter) on the manager's eight totals strategies. Both put the number table first and Robinhood second. The doubter's limit is adopted: **at most two frozen claims on these 990 games**, R1 now and R2 only after two checks. Everything else is dropped or goes to a silent forward log. A pass earns a silent forward log and nothing more. Proof is games played after 11/12/2026.

## R1. The number table (strategy S1): second-half totals, each book against the others ACROSS numbers

**The table.** The chance that a second half lands exactly on k points when the market line is L:
p(k | L) = g(k) x bell((k - L) / s), rescaled to add to 1.
- g(k): share of second halves (overtime included) with exactly k points, 2011 to 2022.
- s: standard deviation of "second-half points minus the closing second-half line", 2011 to 2021.
- bell: the normal curve. L: the median number of the other books at that look.
- No 2023-2026 result enters the table.

**Moving a price across numbers, with ties handled as three outcomes (win, tie, loss).**
- From each other book: its no-vig Under probability U at its number n. If n is a whole number, U is conditional on no tie, so P(points below n) = U x (1 - p(n)). If n is a half-point, P(points below n) = U.
- To the venue's number v: add p(k) for every whole number k with n <= k < v (or subtract for v <= k < n).
- At the venue: Under wins with that probability; the tie is p(v) when v is a whole number; Over wins with the rest. Fair = win probability divided by (1 - tie). The median over the other books is the fair.
- Edge = fair minus the break-even of the venue's price, in points.

**The claim.** At the decision look (look 1 if two or more fresh main-line books, else look 2), a book with two or more other books posted, whose Over or Under shows an edge of 3.0 or more. **One wager per game:** the largest edge among all books and both sides. Graded at that book's number and price, sportsbook settlement (overtime counts, tie refunded), to win $300.

**Result words.**
- PASSED THE SCREEN: return above zero in 2023-24 and in 2025-26 with 40 or more games in each; pooled return above zero one price step worse (break-even + 1.0 point: one contract cent, about -115 to -120); pooled return above zero when the same book and side are graded at their number and price five minutes later (look 2; a book that has pulled the market is a missed bet and is counted); and all of that again with every p(k) cut by a quarter and raised by a quarter.
- FAILED: at or below zero in either period, 40 or more in each.
- UNDERPOWERED: fewer than 40 in a period.

**Conversion check (decides whether the table may replace the flat 1.5, and whether R2 may run).**
- V1: on 2023-2026 whole-number lines, the tie rate the table predicts against the tie rate that happened. Passes when they differ by less than two standard errors.
- V2 (reported): what the books themselves charge for crossing each number, from pairs of books one point apart at the same look, beside the table.

**What each result does.**
- V1 passes: the table is proposed to Phong in place of the flat 1.5 (rule R-07). His word decides.
- R1 PASSED: totals number gaps are logged silently on boards. Nothing prints.
- R1 FAILED or UNDERPOWERED: the betting idea on big books ends. The arithmetic repair stands on V1 alone.

## R2. Robinhood totals (strategy S5). Defined now, run only after V1 passes and the settlement audit is done
- **Settlement audit first.** The doubter reports that Kalshi's second-half total contracts count overtime. The protocol has treated Robinhood halves as regulation-only. The contract text of the second-half total, second-half spread, first-half total and full-game total is read and recorded before anything is priced. The fair is then built on the contract's own settlement.
- **Games:** every 2026 game of the 990 that has a Robinhood second-half total.
- **Quotes:** the standing ask of each strike at the two look times, the same moments as the book quotes. All-in = ask + 2 cents (for a No, 100 - bid + 2).
- **Fair:** the books at that look, at the same number where a book posts the strike, otherwise moved with the R1 table.
- **The claim:** an all-in price 3.0 or more better than fair. One wager per game, the largest edge. Same result words. With about 136 games it is expected to be UNDERPOWERED; its real answer is how often such a price exists.
- **Not testable here, and said so:** how many contracts were available at that price, and a phone's delay.

## Not in this batch
- Silent forward logs, if Phong says "log it": yards per play Over (S2, Over side only, beside the same price rule without flow) and the Over drift (S8, with a fixed review date).
- Dropped: S2 Under, S3 team half form, S4 line-move leadership (two looks cannot show who moved first), S7 rain, snow and cold.
- Held: S6 live total check. No credits spent. One 10-credit lookup showed the feed does carry live full-game totals at halftime (ten books, all on one number), so it is possible later as an anchor.
- Parked, from the scout: quarterback change at the half, favourite receiving the second-half kickoff, two-minute-drill fade, late-season division Unders.
