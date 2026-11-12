# B-NFL-3 - one-sided exact-margin table for NFL halves (2026-11-11)

**Note, 11/12/2026 (change P9):** Robinhood second-half contracts count overtime. The rows marked "2H regulation (Robinhood)" are kept for the record only. Every venue, Robinhood included, now uses the overtime-in rows for a second-half line.


Built during the 11/11/2026 protocol review. Data: nflverse play-by-play, every NFL game 2015 through 2026-11-09 (3,164 games, 3,160 with a favourite). Full table: `push_table_onesided_2015_2026.csv`. Script: `review_2026-11-11/01_push_table.py`.

## What was wrong
The protocol's push table (B-NFL-2, n=337) says how often **either team** wins a half by exactly 3, 7 or 10. A spread line pushes only when **the team laying the points** wins by exactly that number. The boards used the either-team figure as the push probability, which roughly doubles the value of a hook.

The script reproduces B-NFL-2 from the same data (2025 regular season plus 2026 through 10/5, n=336): 1H 3 = 15.5%, 7 = 14.3%, 10 = 7.1%, tie = 8.3%; 2H regulation 3 = 9.5%, 7 = 12.5%, 10 = 6.8%, tie = 10.7%. So the old table is the either-team count, as suspected.

## The table to use

Push probability of a line sitting on the number = the "team laying the points" column.

| Half | Number | Either team (old table's meaning) | Team laying the points wins by exactly this | Team getting the points wins by exactly this |
|---|---|---|---|---|
| 1H | 3 | 12.1% | **6.5%** | 5.5% |
| 1H | 7 | 11.4% | **7.4%** | 4.1% |
| 1H | 10 | 8.6% | **4.9%** | 3.8% |
| 1H | 4 | 9.9% | **5.6%** | 4.3% |
| 1H | tie | 7.3% | 7.3% | 7.3% |
| 2H incl. overtime (DSB) | 3 | 10.4% | **5.6%** | 4.8% |
| 2H incl. overtime (DSB) | 7 | 11.6% | **7.3%** | 4.3% |
| 2H incl. overtime (DSB) | 10 | 7.3% | **4.7%** | 2.6% |
| 2H incl. overtime (DSB) | level | 7.3% | 7.3% | 7.3% |
| 2H regulation (Robinhood) | 3 | 10.9% | **6.1%** | 4.8% |
| 2H regulation (Robinhood) | 7 | 12.1% | **7.5%** | 4.5% |
| 2H regulation (Robinhood) | 10 | 7.3% | **4.8%** | 2.6% |
| 2H regulation (Robinhood) | level | 7.7% | 7.7% | 7.7% |

Standard error on each bold figure is about 0.4 to 0.5 points. Margins 0 to 17 are in the CSV.

- 1H "team laying the points" = the pregame favourite.
- 2H "team laying the points" = the side expected to win the second half given the pregame spread and the halftime score (fitted: 0.61 x pregame spread, minus 0.14 x halftime margin, minus 0.5). Using the pregame favourite instead gives the same figures within 0.2.
- 4 is nearly as heavy as 3 in a first half (7-3, 10-6, 14-10). Treat a half-point on or off 4 as a real half-point.

## How to use it
- **HOOK.** P_push = the bold figure for that half and number. P_win and P_loss as before. Conditional win = P_win / (P_win + P_loss). Fire only at break-even + 3.0 points and EV > 0 (unchanged).
- **Converting a fair between two numbers.** Every whole number crossed moves the win probability by that number's one-sided figure (the laying side's column when the crossed number is on the favourite's side of zero, the getting side's column when it is on the underdog's side, the tie row at zero); on a whole-number line the push is then taken out of both sides. Exact arithmetic: `convert()` in `review_2026-11-11/02_clv_1h.py`. This replaces, for NFL only, the flat "2.0 points per half-point" and the "3 = 11.5%, 7 = 15.3%, tie 5.7%" line in the Robinhood tab (those are CFB figures).
- **Totals** are not covered here. The 1.5 points per half-point rule for totals is unchanged and untested.

## What it does to a hook
With the books on the hook at a 50% fair, a flat key number at DSB is worth, in points of conditional win probability:

| | As the boards ran it | One-sided |
|---|---|---|
| 1H flat 3 | +9.3 | +3.5 |
| 1H flat 7 | +8.3 | +4.0 |
| 2H flat 3 (DSB) | +5.2 | +3.0 |
| 2H flat 7 (DSB) | +7.1 | +3.9 |

Break-even is 51.2% at -105 and 52.4% at -110, so a flat 3 at -105 nets about +2.3 in a first half and +1.8 in a second half. It clears the 3.0 floor only near even money, or when the books' hook side is itself better than 50%.

**11/1 LAR -3 2H @ DSB -105 (the HOOK-through-divergence fire).** As run: 9.5% push mass, conditional win 55.6% vs 51.2% = +4.4, fired. One-sided: 5.6% push mass, conditional win 53.3% = +2.1. Under the 3.0 floor. It would not have fired. It won.

## Limits
- Not conditioned on the exact line. Splitting by the size of the pregame spread moves the bold figures by one to two points either way, which is inside the noise for groups that small (200 to 1,000 games).
- 2024-26 alone (706 games) runs a little heavier on a first-half 3: 7.4% for the laying side, 14.6% either team. Shown in the CSV. The default is the 12-season column; rerun the script after each season.
- No first-half or second-half closing lines are in this data, so "team laying the points" is derived from the full-game spread.
