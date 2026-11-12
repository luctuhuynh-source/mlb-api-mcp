# College football sides at halftime: backtest B-CFB-7 (11/12/2026, about 6:45 AM)

Ordered by Phong (voice, then "Cfb review" 5:27 AM; panel replies posted 6:17 AM). Ruling: `panel_2026-11-12/PANEL_RULING_CFB_SIDES_2026-11-12.md`. Plan locked before the price pull: `backtest_2026-11-12/CFB_SIDES_TEST_PLAN_LOCKED.md`. Output: `backtest_2026-11-12/out_62_grade_cfb_sides.txt`, `out_63_push_table_audit.txt`.

## 1. Data
- **Games:** 685 games of 2026 with an FBS team, weeks 1 to 10 (8/29 to 11/7), from the public cfbfastR play-by-play. Usable halftime clock: 665.
- **Prices:** second-half spreads from the odds archive, one look per game, a median 7.8 minutes after the last first-half play. 663 of 665 found by plan; the other two (neutral sites, the feed lists the other team as home) pulled by hand and flipped. A counting look (two or more clean books): **614 games**. Books: DraftKings 614, Hard Rock 562, Bally 383, Bovada 366, Fliff 281.
- **Credits:** 6,793 used (63 test, 6,708 pull, 22 fixes). 42,717 left.
- **Check on the data:** on the two discovery Saturdays the home team went 57-32 at DraftKings' number here; the 11/6 replay had 58-33. Teams, signs and overtime grading line up.

## 2. The three claims: all FAILED

| Claim | Games | Won | Return | First half / second half of the games | Doubter's lower bound | Result |
|---|---|---|---|---|---|---|
| H. Home team, second half (outside the two discovery Saturdays) | 516 | 51.3% | **-5.3%** | -7.6% / -3.0% | -12.4% | **FAILED** |
| F. FLOW side, lead under 21 (outside the two discovery Saturdays) | 173 | 53.3% | **-1.4%** | -2.6% / -0.1% | -18.4% | **FAILED** |
| S. Success-rate side, lead under 21 | 310 | 48.3% | **-10.5%** | -10.3% / -10.7% | -22.1% | **FAILED** |

- **Home was two hot Saturdays.** 57-32 on 10/24 and 10/31; 51.3% on the other 516 games.
- **FLOW is a coin flip after the price.** On the discovery days the rebuilt classifier went 18-10 (the replay: 17-6 on 23 games). Outside them, 53.3%, which loses 1.4% at the books' prices.
- **Success rate did worse than yards per play, not better.** The scout's main claim is not supported here. Where success rate names a team and FLOW does not: 46.2% on 155 games.
- F and S name the same team in 124 of the verdict games.

## 3. What the information views show (cannot pass or fail anything)

| View | Result |
|---|---|
| Price basis | At the no-vig fair price the three claims return +2.1%, +6.4% and -3.5%. At the average book: -5.3%, -1.4%, -10.5%. **The books charge about 7.5 points of return on a college second-half spread** (prices such as -135/+100 and -130/-110), against about 4.5 for a -110 line |
| Engine premise | A book 3.0 better than the others on the same number: **2 of 512 games** (1-1). 2.0 to 2.9: 3 games |
| Books' numbers | Same number in 25% of games, half a point apart in 10%, **a point or more apart in 64%**. Rule X-05 sends "books 1.0+ point apart" to shadow, so by its own rule the engine cannot price about two games in three |
| Halftime leader, lead 1 to 20 | 448 games, 48.6%, -10.2%. **Where the leader has no FLOW edge: 259 games, 43.8%, -19.1%** (all dates; the replay's two Saturdays were 22-26) |
| Trailing team, deficit 1 to 20 | 448 games, 51.4%, -4.8% |
| Home team by state (all dates) | Home trails at the half: 210 games, 57.5%, +5.9%. Home leads: 352 games, 51.0%. Home leads by 21+: 100 games, 46.0% |
| Yards-per-play edge alone (1.5+), lead under 21 | 246 games, 57.1%, +5.7% (all dates, the two hot Saturdays included) |
| Success-rate side when it trails by 1 to 14 (the scout's idea) | 40 games, 56.7%, +6.5%. When it leads: 248 games, 47.1% |
| Team receiving the third-quarter kickoff | 613 games, 51.6%, -4.3% |
| Favourite of the second-half line | 606 games, 49.4%, -8.0% |
| Tiers | Home: 51.7% / 51.1% / 50.9% (power-four / other FBS / against FCS). Success rate in power-four games: 44.7% on 117 |
| How the market sets the line | Market: 0.464 x pregame edge - 0.058 x halftime margin + 0.09 x yards-per-play edge. Actual: 0.468 x pregame edge - 0.155 x halftime margin + 0.54 x yards-per-play edge. The pregame weight is right. **The market takes off too little for a halftime lead** (about 0.1 point per point of lead, roughly three standard errors) and gives little for the yards-per-play edge (about two standard errors) |

## 4. Audit B-CFB-4: the push table the HOOK rule needs (3,410 games, 2023 to 2026)

| First half | The tab (either team, 314 games) | Either team, measured | **The team laying points** | Standard error |
|---|---|---|---|---|
| Margin of exactly 3, first-half line near 3 (pregame spread 4.5 to 8; 701 games) | 11.5% | 11.3% | **5.6%** | 0.9 |
| Margin of exactly 7, first-half line near 7 (pregame spread 11.5 to 16.5; 498 games) | 15.3% | 11.8% | **8.8%** | 1.3 |

- The tab's figure counts both teams. A team laying 3 pushes only when it leads by exactly 3 itself.
- **What it does to a HOOK.** Books on -3.5 at a fair 50%, venue hangs -3 at -110. With the tab's 11.5% the edge reads +4.1 points and fires. With 5.6% it is +0.6 and does not. On 7: +6.6 with the tab's figure, +2.4 with 8.8%.
- Second-half table, same audit: either team 3 = 7.6%, 7 = 10.5%, 10 = 5.7%; the team laying (pregame) 3 = 4.7%, 7 = 7.3%, 10 = 3.9%. Full tables by spread size: `out_63_push_table_audit.txt`.
- Past HOOK fires were not re-checked.

## 5. Reading
- **Nothing tested here is a bet.** The three claims failed at real prices, two of them outside the days that suggested them.
- **The price is the first problem.** A college second-half spread at these books costs about 7.5% before any opinion. A lean has to be bet at the fair or better (this morning's rule) to have a chance.
- **The one pattern that shows on more than one view is the opposite of a FLOW lean:** halftime leaders do worse than the second-half line expects, most of all leaders who did not out-gain the other team. It appears in the control column (43.8% on 259), in the home split (home trailing 57.5%), in the regression, and in the replay's own two Saturdays (22-26). It was not a claim of this test and proves nothing yet.
- None of this is proof. Proof is games played after 11/12/2026.

## 6. Proposed to Phong (nothing changes without his word)
1. **"fix hook":** replace the first-half HOOK table with the one-sided figures (laying 3 = 5.6%, laying 7 = 8.8%). A formula fix.
2. **"close home":** close the home-team second-half shadow column. It failed.
3. **"log fade":** a silent forward log with this file as its written test: the TRAILING team's second-half spread when the halftime lead is 1 to 20 and the leader has no FLOW edge. Nothing prints until 40 entries.
4. **"wording":** the three text fixes of the ruling (what a bettable lean is; news check before the price re-pull; drop the optional previous-game read from first-half leans).
5. Not run: Robinhood college prices at halftime (free; needs the exchange's event list). "robinhood cfb" starts it.
