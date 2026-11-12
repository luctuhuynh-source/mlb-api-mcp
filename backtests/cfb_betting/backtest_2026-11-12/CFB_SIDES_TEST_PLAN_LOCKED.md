# College football sides at halftime - test plan, LOCKED 2026-11-12, about 7:00 AM (audit B-CFB-7)

Locked by the manager after the panel review (`../panel_2026-11-12/PANEL_RULING_CFB_SIDES_2026-11-12.md`). The commit that adds this file is the lock. It is made before any second-half result is summarised and before the price pull. After the first result is seen, no threshold is moved, no claim is reworded and no view is added.

Seen before the lock, and nothing else: three test lookups (Texas Tech 10/31, Coastal Carolina 9/24, Louisville 9/11) to learn which books post the market; counts of how many games each trigger catches.

## 1. What is used

| | |
|---|---|
| Games | 2026 games with an FBS team, weeks 1 to 10 (8/29 to 11/7), from the public cfbfastR play-by-play: 685. Usable halftime clock: 665 |
| First-half numbers | `60_build_h1_features.py` -> `cfb_h1_features_2026.csv`. No price is read there |
| Prices | Odds archive, second-half spreads, one look per game: the snapshot at or before "last first-half play + 10 minutes". Books: draftkings, fanduel, williamhill_us, bovada, betrivers, unibet_us, hardrockbet, ballybet, betparx, fliff. About 6,700 credits. Plan file `cfb_pull_plan.json` |
| Results | Second-half points with overtime, from the same play-by-play |

## 2. Rules, fixed now

- **Clean quotes.** Main line only (both prices between -200 and +200). Fresh (the book's last update is at or after the last-first-half time stamp of the feature file). A look counts with two or more such books; otherwise the game is out and is counted.
- **A bet** is one side at each such book's own number and price. Each game counts once: its books are averaged. Sportsbook settlement: second half with overtime, a tie is a refund. Stake to win $300. Return = net won / amount risked. One price step worse = break-even + 1.0 point.
- **Discovery Saturdays.** 10/24 and 10/31 produced 58-33 and 17-6. They are left out of the verdict for claims H and F and shown apart.
- **Two halves** of a claim's verdict games, in kickoff order.

## 3. The three claims

| # | Claim | Bet |
|---|---|---|
| H | HOME, second half | The home team's second-half spread. Neutral sites out |
| F | FLOW side, lead under 21 | The team with a first-half yards-per-play edge of 1.5 or more AND a clean margin that is not zero and favours the same team; halftime lead (either team) under 21. Its second-half spread |
| S | SUCCESS-RATE side, lead under 21 (the scout's finding 7) | The team whose first-half success rate is 7 percentage points or more above its opponent's; halftime lead under 21. Its second-half spread. All dates |

Definitions (scrimmage play, yards per play, success, clean points) are in the docstring of `60_build_h1_features.py` and are part of this lock.

## 4. Result words

- **CLEARS THE DOUBTER'S BAR:** return above zero, and the one-sided 98.33% lower bound above zero. Bound: calendar weeks resampled as whole blocks, 100,000 resamples, seed 20261112, statistic = total net / total risked. Fewer than eight weeks contributing: not judged.
- **PASSED THE SCREEN:** return above zero in both halves with 40 or more games in each, and the pooled return above zero one price step worse.
- **FAILED:** at or below zero in either half, with 40 or more in each.
- **UNDERPOWERED:** fewer than 40 in a half.

| Claim | FAILED | PASSED THE SCREEN | CLEARS THE BAR |
|---|---|---|---|
| H | Proposed to Phong: close the home-team shadow column | The column stays, with this plan as its written forward test | Proposed to Phong as a lean input |
| F | Proposed: close the FLOW column and its control | The same | The same |
| S | The idea is dropped | Proposed: a success-rate column on the board, logged silently | Proposed: success rate replaces yards per play in the FLOW vote |

**None of this is proof.** Proof is games played after 11/12/2026.

## 5. Reported for information only (cannot pass or fail anything)

1. **Reproduction.** H and F on the two discovery Saturdays, at DraftKings' own number (the replay's basis) and at the average book.
2. **Price basis.** Each claim at the no-vig fair price and at the best book.
3. **Controls on the same games:** the away team; the halftime leader with a lead under 21, and the leader where FLOW does not agree (the tab's control column); the trailing team; the team receiving the third-quarter kickoff; the favourite of the second-half line.
4. **Variants:** yards-per-play edge alone; F and S when the side leads and when it trails (trailing by 1 to 14 is the scout's "outplayed but behind"); S where the side also lost more fumbles than its opponent; F and S naming the same team, and only one of them naming a team.
5. **Tiers:** both teams in a power-four conference; other FBS against FBS; FBS against FCS.
6. **Home, split** by pregame favourite or underdog and by leading, trailing or tied at the half (the split queued on 11/6).
7. **Engine premise:** a book whose price at its own number is 3.0 or more better than the no-vig median of the other fresh books on that same number (two or more others): how often, and its record.
8. **How the market sets the second-half spread:** the median second-half line, and the actual second-half margin, each regressed on the pregame spread, the halftime margin and the yards-per-play edge.
9. **Coverage:** games with a counting look, books per look, quotes dropped as stale, halftime length.

**Separate and free, not a betting claim: audit B-CFB-4.** The one-sided push table the HOOK rule needs: how often the team laying points leads by exactly 3, 7 and 10 at the half, and wins the second half by exactly those margins, by size of the pregame spread, 2023 to 2026.

## 6. Not in this test
- Robinhood college prices (needs the exchange's event list; free; a separate pull). DSB and Red105 prices (no history exists).
- Personnel. Whether a displayed price could be filled. First-half (pregame) prices.
