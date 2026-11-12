# Robinhood second-half prices against the books - test plan, LOCKED 2026-11-12, about 4:00 AM

Phong, 3:47 AM: "Ready for Gemini response? Then we can test robinhood". The Gemini file he posted at 3:48 AM is byte-for-byte the round-2 reply already on file (`../../panel_2026-11-12/round2/REPLY_gemini_scout_round2.txt`), so the round-2 ruling stands unchanged.

This plan takes the place of R2 in `../halftime_pull/ROUND2_TEST_PLAN_LOCKED.md`, which could not run because its gate (the number table's check) failed. It is the re-scoped test of the round-2 ruling, section 6 item 2: **the same number only, no table, second-half spreads and totals, both halftime looks, this season's games.** It is the second and last frozen claim allowed on these games.

The commit that adds this file is the lock. It is made before any Robinhood halftime price is pulled. After the first result is seen, no threshold is moved, no claim is reworded and no view is added.

## 1. What is used

| | |
|---|---|
| Games | The 136 games of 2026 (week 1 to 11/9) in the halftime pull, in kickoff order |
| Book quotes | Already on file (`../halftime_pull/pulled_pull_plan.csv.gz`): second-half spreads and totals at two looks, up to ten books. No credits are spent |
| Robinhood quotes | The exchange's public one-minute history of bid and ask (Kalshi contracts KXNFL2HSPREAD and KXNFL2HTOTAL), every contract of each game, from 3 minutes before the last first-half play to 2 minutes after the third-quarter kickoff. Pulled with `kalshi_get_candlesticks` in plan mode from `kalshi_plan.json`. Free |
| Results | The contract's own settlement as the exchange reports it, checked against nflverse second-half points with overtime. Every disagreement is listed |

**Settlement.** These contracts count overtime (change P9, 11/12). So do the books' second-half lines. The comparison is like for like and nothing is adjusted.

**Seen before.** The pilot looked at Robinhood second-half spread prices of 23 games (10/18 to 11/5) at the close, which is near look 2. Those games are inside this test and are marked in the look-2 view. No Robinhood halftime price at look 1 and no Robinhood total has been looked at.

## 2. Rules, fixed now

- **Book cleaning:** as in `../halftime_pull/TEST_PLAN_LOCKED.md` section 2. Main line only (both prices between -200 and +200). Fresh (last update at or after the last first-half play). A look counts for a market when two or more books pass. The decision look is look 1; if look 1 does not count, look 2.
- **The same number.** A spread contract "TEAM wins the second half by more than 2.5" is matched to book quotes where TEAM lays exactly 2.5. A total contract "more than 20.5 points" is matched to book totals of exactly 20.5. Yes is TEAM -2.5 or the Over; No is the other team +2.5 or the Under. A book number that is a whole number has no contract and is counted.
- **Fair:** the median of the no-vig probabilities of the fresh main-line books that post exactly that number at that look. Two or more such books are needed.
- **Robinhood quote at a look:** the standing bid and ask at the first whole minute at or after the book snapshot's own time stamp. Robinhood is therefore given up to 60 seconds longer than the books.
- **All-in price:** Yes = ask + 2 cents. No = 100 - bid + 2 cents. Two cents is the ceiling of Robinhood's published fee. No fee is counted at settlement, since a contract held to settlement is not traded again.
- **Venue rule R-03:** the ask of the side bought is 60 cents or less, and the bid-ask spread is 4 cents or less with both a bid and an ask standing. A price that fails it is shown apart and is never an entry.
- **Edge** = fair, in points, minus the all-in price, in cents.
- **Grading:** at the all-in price, on the contract's own settlement. Stake to win $300. Return = net won divided by amount risked. One price step worse = one cent more.
- **Two parts of the season:** the games that have Robinhood contracts, in kickoff order, cut into a first half and a second half.

## 3. The one frozen claim

**K1. The engine's floor at Robinhood.** At the decision look, for each game and market (spread, total): the same-number contract side with the largest edge that passes R-03. It is an entry when that edge is 3.0 or more. Spreads and totals are counted together.

- **PASSED THE SCREEN:** return above zero in both parts of the season with 40 or more entries in each, and the pooled return still above zero one cent worse.
- **FAILED:** at or below zero in either part, with 40 or more in each.
- **UNDERPOWERED:** fewer than 40 entries in a part. This is the expected word: the pilot found Robinhood about 2 points worse than fair on average.

| Result | What it does |
|---|---|
| PASSED THE SCREEN | Robinhood same-number prices of 3.0 or better are logged silently on boards. Nothing prints and no rule changes without Phong |
| FAILED | Reported to Phong, with the question whether halftime runs should keep pulling the Robinhood ladders. His call |
| UNDERPOWERED | The answer is view B (how often such a price exists) and view E (resting orders). Reported to Phong. Any rule change is his |

**None of this is proof.** These games' book prices and results were studied all night. Proof is games played after 11/12/2026.

## 4. Reported for information only (cannot pass or fail anything)

- **A. Price level.** The edge of every same-number contract side that passes R-03: mean, median, and the share at 0 or better, 1.0+, 2.0+, 3.0+. By market, by side (Yes, No; favourite, underdog; Over, Under) and by look.
- **B. How often.** Games per 100 with a best edge of 3.0+, 2.0+, 1.0+ and 0 or better, at look 1 and at look 2.
- **C. Bands.** The record and return of the best side per game and market at 2.0 to 2.9, 1.0 to 1.9, 0 to 0.9 and below 0.
- **D. Does it last.** For look-1 prices at 3.0+ and at 0 or better: whether the same all-in price or better still stood 1, 2, 3 and 5 minutes later, and the edge of the same contract against the look-2 fair when the books still post that number.
- **E. Resting orders** (the scout's point that price-takers lose on this exchange; Robinhood's help pages confirm its contract orders are limit orders that can wait unfilled). At look 1, for each same-number contract and each side: T = the highest whole-cent price at which the all-in cost (T + 2) is 3.0 or more below the look-1 fair, with T at most 60. If the standing price is already T or better it belongs to K1, not here. Otherwise an order to buy at T is taken to be placed at the look-1 minute and cancelled at the third-quarter kickoff. It counts as filled in the first later minute in which the market reached T (Yes side: ask low at or below T, or a trade at or below T; No side: bid high at or above 100 - T, or a trade at or above 100 - T). Reported: orders placed, share filled, record and return of the filled orders at T + 2, the record the unfilled ones would have had, and how the fair moved between the looks for each group. The same again with T set at the fair (all-in at the fair or better). **This view flatters the order:** it assumes first place in the queue and enough contracts traded. Real fills will be fewer.
- **F. Other strikes, by the conversion in force (rule R-07).** Robinhood strikes within 1.5 points of the books' median number that fewer than two books post: spreads moved with table B-NFL-3, totals with the flat 1.5 points per half-point. Best side per game and market, bands as in C, half a point away and further away shown apart. Never pooled with the same-number results. The totals conversion is untested and failed a related check tonight; it is shown because it is how the engine would price that contract today.
- **G. Liquidity.** The bid-ask spread of same-number contracts, the share that fail R-03, and contracts traded during halftime.
- **H. Settlement audit.** The exchange's result against nflverse second-half points with overtime, every contract.
- **I. Sensitivity.** The Robinhood quote one minute earlier; the fee at 1 cent.
- **J. Coverage.** Games with no Robinhood contracts, with no same-number contract, and with fewer than two books on a number.

## 5. Not testable here, and said so

- How many contracts stood at the ask. The history carries prices and volume, not depth.
- A phone's delay beyond the one-minute allowance.
- A resting order's place in the queue.

## 6. How it is run

1. `kalshi_get_candlesticks(tickers="plan:kalshi_plan:<from>-135")`. Each call stops after about 22 seconds and says where to resume. The result is long on purpose, so the client saves it to a file instead of reading it into the conversation. `event_ticker="peek"` shows the first game only, as a format check.
2. `51_collect_kalshi.py <tool-results folder>` turns the saved files into `kalshi_halftime_2026.csv.gz` and lists anything missing.
3. `52_grade_robinhood.py` is written after this lock and implements sections 2 to 4 as written.
