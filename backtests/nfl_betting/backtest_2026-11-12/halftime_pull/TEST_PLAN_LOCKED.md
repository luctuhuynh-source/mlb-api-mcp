# Test plan for the paid pull - LOCKED 2026-11-12

Locked by the manager after the panel review (`../../panel_2026-11-12/PANEL_RULING_2026-11-12.md`) and before any pulled price is graded. The commit that adds this file is the lock. After the first result is seen, no threshold is moved, no claim is reworded and no cell is added. A new idea goes to games played after 11/12/2026.

## 1. What is bought

| | Halftime pull | Pregame pull |
|---|---|---|
| Plan file | `pull_plan.json`, 286 batches | `pull_plan_h1.json`, 286 batches |
| Games | 990, 2023 week 1 to 11/9/2026 (one game with a broken halftime clock is left out) | the same 990 |
| Looks per game | Two. Look 1: the feed snapshot at or before "last first-half play + 7 minutes" (2 to 7 minutes into halftime). Look 2: the last snapshot before the 3rd-quarter kickoff | One: the last snapshot before the scheduled kickoff |
| Markets | Second-half spreads and totals | First-half totals |
| Books (ten named books cost the same as one region) | draftkings, fanduel, williamhill_us, bovada, betrivers, unibet_us, hardrockbet, ballybet, betparx, fliff | draftkings, fanduel, betmgm, williamhill_us, betrivers, bovada, betonlineag, betus, pointsbetus, unibet_us |
| Credits | about 39,900 | about 10,200 |

- Book lists come from four test pulls (2023, 2024, 2025, 2026): these are the books that post the market. The archive carries 3 books on second-half lines in 2023, 4 to 5 in 2024, 5 to 6 in 2025, 8 in 2026. No Pinnacle or Circa.
- Every quote carries its age (seconds since that book last updated that market).
- Results: nflverse scores by half, at the end of regulation and final.
- Wind: the nflverse kickoff reading, the label the cells were found on. Outdoor games with no reading (102 of 991) are left out of the wind claims and counted. They are never treated as calm.

## 2. Cleaning rules, fixed now

- **Main line only.** A quote counts when both of its prices are between -200 and +200.
- **Fresh.** At halftime a quote counts when its last update is at or after the last first-half play. Before kickoff, when it is 30 minutes old or less.
- **A look counts** when two or more books pass both tests. The decision look is look 1. If look 1 does not count, look 2 is used. If neither counts, the game is out and is counted.
- **A totals bet** is the Under at one book's own number and price. Sportsbook settlement: the second half includes overtime, a tie is a refund.
- **Stake** is to win $300. Return = net won divided by amount risked.
- **Each game counts once.** Its books are averaged (each bet weighs 1 divided by the number of books).
- **One price step worse** means every price's break-even raised by 1.0 point of probability (about -110 to -115, or 1 cent on a contract).
- **Outdoor** means nflverse roof "outdoors" or "open".
- **Periods:** 2023-2024 and 2025-2026.

## 3. The six claims

| # | Claim | Graded on |
|---|---|---|
| C1 | WIND 10+ Under, second half | Outdoor games with a reading of 10 mph or more. Bands 15+ and 10-14 are shown apart; 15+ alone has about 51 games and cannot be judged alone |
| C2 | WIND 10+ Under, first half | The same games, pregame look, first-half points |
| C3 | SCORE Under, calm or indoors | Second half, first-half points 28 or more, in indoor games and outdoor games with a reading under 10 |
| C4 | SCORE inside wind | Second half, wind 10+: the return with 28+ first-half points minus the return with fewer |
| C5 | Engine premise at 3.0+ | At the decision look, a book whose price on a side or a total is 3.0 or more points better than the fair from the other fresh books (edge = fair win probability at that book's number minus the break-even of its price, as in F-28 and H-19). Fair: the other books with the vig removed, moved to that book's number with table B-NFL-3 for spreads, same number only for totals, median, two or more other books needed. One entry per game, market and side: the book with the largest edge. Graded at that book's number and price |
| C6 | Engine premise at 2.0 to 2.9 | The same |

## 4. Result words, and what each one does

- **REPLICATED:** return above zero in both periods with 40 or more games in each, and the pooled return still above zero one price step worse. For C4: the gap above zero in both periods with 40 or more games in each group.
- **FAILED:** at or below zero in either period, with 40 or more in each.
- **UNDERPOWERED:** fewer than 40 in a period. Nothing changes.

| Claim | REPLICATED | FAILED |
|---|---|---|
| C1 | U2 (wind 10-14) may print on paper at halftime. U1 stays | No wind line prints in either window until forward games say otherwise |
| C2 | A first-half window is proposed to Phong. Nothing changes without his word | First-half wind entries stay logged only |
| C3 | U3 may print on paper | The stand-alone SCORE claim is dropped. A windy subset cannot rescue it |
| C4 | BOTH stays a tag worth watching | SCORE adds nothing inside wind; the tag is kept for the record only |
| C5, C6 | Reported to Phong with the engine levers (floor, second tier). Any rule change is his | The same |

**None of this is proof.** The 2022-2026 full-game results were looked at before this pull, and in the same game a second-half Under wins 78% of the time when the full-game Under won. Proof is the forward ledger (protocol T-13b).

## 5. Reported for information only (cannot pass or fail anything)

- The pooled one-sided 95% lower bound of each claim, corrected over the six claims and with the games of one week counted together. No claim is expected to clear it at these counts.
- Best-price grading; look 2 grading; the wind bands apart; 15-19 against 20+.
- The same Unders graded on regulation only at half-point lines, less 2 cents (the Robinhood view).
- Tags of protocol T-10 as splits, where each group has 40 or more.
- Controls expected to fail: Overs in domes; Overs after a first half of 13 or fewer.
- How the market set the second-half total in 2023-2026 (the weight on first-half points).
- How often a book is 2.0 or more off at look 1 and gone by look 2; stale-quote rates by book.
- Robinhood: all-in prices against the fair at both looks for every 2026 game that has price history (free).
- **W0, label audit.** Wind for every outdoor game 2011-2026 rebuilt from an hourly weather archive at the stadium, plus the day-before forecast for 2024-2026. Shows how often the archive and the kickoff reading agree at 10 and 15 mph, fills the 102 games with no reading, and re-grades C1 and C2 on the rebuilt label. Needs one more server tool.

## 6. How it is run

1. `get_event_odds_historical_batch` in plan mode: `items="plan:pull_plan:<from>-285"`, markets `spreads_h2,totals_h2`, `regions="bk:<the ten books>"`, `compact=true`. The same for `pull_plan_h1` with `totals_h1`. Each call stops after about 22 seconds and says where to resume.
2. Each result is long on purpose, so the client saves it to a file instead of reading it into the conversation. `22_collect_saved_results.py <tool-results folder>` turns the files into `pulled_pull_plan.csv` and `pulled_pull_plan_h1.csv` and lists anything missing.
3. Grading scripts are written after this lock and implement sections 2 to 5 as written.
