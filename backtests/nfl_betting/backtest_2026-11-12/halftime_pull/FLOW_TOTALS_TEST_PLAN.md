# Flow against second-half totals - test plan, fixed 2026-11-12 about 2:45 AM, before any of it is graded

Phong, 11/12, 2:38 AM: "What about flow of the games. Are you still reading play per plays to get a feel for the flow of the game? ... Is that still part of the determining process?" Then, 2:40 AM: "Test flow total".

**What this is.** A screen of the flow read on totals (rule H-38 bars it from totals while it is shadow-tested; the live shadow log stood at 3-2 on five graded entries on 10/26). First-half flow numbers from play-by-play, against the real second-half totals and prices bought on 11/12 (990 games, 2023 to 11/9/2026).

**What it is not.** Proof. That data has been opened: the base rates are known (second-half Unders 48.5%, Overs 54.3% in 2025-2026). Ten claims are tried. A claim that passes buys a silent forward log, nothing more. No rule changes without Phong.

## Flow numbers (first half only, both teams added together, from nflverse play-by-play)
- **Plays:** pass and run plays, sacks and scrambles included. Kneel-downs, spikes and penalty-only plays are left out.
- **YPP:** yards gained divided by plays.
- **TEMPO:** the number of plays.
- **Drives:** possessions that began in the first half and had at least one play as defined above.
- **SUSTAIN:** share of drives with two or more first downs, or a touchdown.
- **3-AND-OUT:** share of drives with no first down that ended in a punt.
- **STALLED RED ZONE:** drives that got inside the 20 and did not end in a touchdown.
- **CHEAP POINTS** (rule G-02): points from return touchdowns, from scoring drives that started strictly inside the opponent's 40, and from scoring drives that gained under 30 net yards. Conversion points go with their touchdown. Each score is counted once.
- **First-half points:** the half score.
- **Top third / bottom third:** above the 66.7th / below the 33.3rd percentile of that number over the 990 games. **Median** for first-half points: at or below it is "low", above it is "high". These cuts use no result.

## The ten claims
| # | Claim | Bet |
|---|---|---|
| T1 | YPP in the top third | Over |
| T2 | YPP in the bottom third | Under |
| T3 | TEMPO in the top third | Over |
| T4 | TEMPO in the bottom third | Under |
| T5 | CHEAP POINTS of 10 or more | Under |
| T6 | Moved the ball, did not score: YPP top third and first-half points low | Over |
| T7 | Scored without moving it: first-half points high and YPP bottom third | Under |
| T8 | Two or more STALLED RED ZONE drives | Over |
| T9 | 3-AND-OUT rate in the top third | Under |
| T10 | SUSTAIN rate in the top third | Over |

## Grading
Exactly as `TEST_PLAN_LOCKED.md`, section 2: decision look (look 1, else look 2), main line only, fresh quotes, the average book at its own number and price, sportsbook settlement (second half includes overtime, tie refunded), to win $300, each game once, periods 2023-24 and 2025-26, one price step worse = break-even + 1.0 point.

- **PASSED THE SCREEN:** return above zero in both periods with 40 or more games in each, and the pooled return above zero one price step worse.
- **FAILED:** at or below zero in either period, with 40 or more in each.
- **UNDERPOWERED:** fewer than 40 in a period. No threshold is moved to fix that.

## Also reported, for information only
- Each claim beside the base rate of its own side (every Over, every Under) in the same period.
- The cautious end of each estimate, plain and corrected for ten claims.
- Each flow number against "second-half points minus the market's line", one at a time (slope and t), as a check that does not depend on the cuts.
