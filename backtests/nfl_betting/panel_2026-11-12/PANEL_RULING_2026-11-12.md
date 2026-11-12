# Panel ruling on the NFL Totals protocol v0.2 draft - 2026-11-12

Panel, as Phong set it (10/31, 11/1, 11/12 "You as the manager always"): Gemini = scout, ChatGPT = doubter, Claude = manager and final decision.
Reviewed: `TOTALS_PROTOCOL_v0.2_DRAFT.md`. Prompts: `PROMPT_gemini_scout.txt`, `PROMPT_chatgpt_doubter.txt`. Replies as received: `REPLY_gemini_scout.txt`, `REPLY_chatgpt_doubter.txt`.
Result: `../TOTALS_PROTOCOL_v0.2.md` (final text, **not in force until Phong ratifies it**) and `../backtest_2026-11-12/halftime_pull/TEST_PLAN_LOCKED.md`.

## 1. Bottom line

- **The doubter's report is accepted almost whole.** Every number in it was re-run and every one is right (`out_40_panel_checks.txt`).
- **Its biggest point decides the test plan:** 2023-2026 has only 51 games with wind 15+ (30 and 21 by period). The paid data cannot prove or kill that cell on its own. The wind test is now one pooled claim, wind 10+.
- **The paid data is a replication at real prices, not a proof.** The 2022-2026 full-game results were already looked at, and a second-half Under wins 78% of the time when the full-game Under won. Proof can only come from games played after 11/12/2026.
- **The draft's gate was too weak** (a coin-flip cell passes it about 1 time in 3). It is now a screen for paper printing only. Real money needs a second, much harder bar.
- **The price-fire lane is taken out of the track.** It duplicated the engine and contradicted the no-Over rule. Totals price fires stay in the engine, unchanged.
- **The scout's facts mostly check; its five new cells do not earn a place.** Two could be tested on data in hand and both fail a period. The others become logged tags.
- **Best evidence in the file, found while checking:** the full-game Under in wind 10+ at the real closing price is +9.7% on 965 games, 3.3 standard errors, all three periods positive, and it still stands after allowing for 45 comparisons (`out_42_fullgame_wind_strength.txt`). The second-half 143-107 is much weaker on its own (about 7 chances in 100 against break-even).

## 2. Checks the manager ran

| Check | Result | File |
|---|---|---|
| Doubter: 143 of 250 tails, 45-cell odds, bets needed, gate pass rates, 40-bet stop | All match: 1.33% / 7.16%; 45.3% / 96.5%; 5,875 and 719 bets; 31.1% and 18.7%; 23.0% | out_40 A |
| Games each cell catches in 2023-2026 (no result read) | Wind 15+: 30 + 21. Wind 10-14: 85 + 44. No wind reading: 46 + 56 (41 in 2023, 52 in 2026). Indoors: 316 | out_40 B |
| Full-game Under against second-half Under, same game | Correlation 0.52 to 0.56. In wind 15+: 81% against 26% | out_40 C1 |
| Leader covers against Under wins, inside the cells | 0.09 in all games, 0.14 in wind 10+, 0.17 in wind 15+ | out_40 C2 |
| The 15 games without a second-half total | 11 games of 9/23/2018 (the archive repeats the full-game total), 4 games of 2020 (line of 0) | out_40 D |
| Scout cell: primetime Under, full game | 402-372-9, 51.9%, -0.8%. By period 48.1 / 53.5 / 55.0. Fails 2011-16. 2025 alone 29-27, not the 27-19-1 quoted | out_40 E |
| Scout cell: calm outdoor Over (wind under 8) | 741-660-16, 52.9%, +1.0%. By period 53.3 / 50.9 / 54.9. Fails 2017-21 | out_40 E |
| Scout: is 20+ stronger than 15-19 | No. Full game 52.6% (78 games) against 57.6%. Second half 57.8% against 57.0% | out_40 E |
| Scout: regulation-only settlement and the Under | Worth 0.7 points to an Under on average, 0.0 to 0.2 in wind. Never negative | out_41 |
| Full-game wind 10+ at real closing prices | +9.7%, se 3.0 with weeks counted together, one-sided p 0.0006, 0.025 after x45 | out_42 |
| How many books post second-half lines in the odds archive | 3 in 2023 and 2024, 3 to 6 in 2025, 4 in 2026. No Pinnacle in any region | 4 test pulls, 204 credits |
| First-half totals before kickoff, 2023 week 1 | 6 books | same |
| Scout's sources | Odds archive start (May 2023), Open-Meteo forecast archive (most models from January 2024), 2025 overtime and touchback rules: confirmed. The Fox 54%, the field-goal rates, the 2025 yardage figure, the K-ball effect: not verified | web |

## 3. Doubter's findings

| # | Finding | Ruling | What changes |
|---|---|---|---|
| D1 FATAL | P1 and P2 are not a clean holdout | **Accepted.** Measured: correlation 0.52 to 0.56 | Renamed "replication at real prices". Confirmation only on games after 11/12/2026 |
| D2 FATAL | Wind labels use a kickoff reading, and readings are missing | **Accepted.** A game picked because its kickoff reading was high probably also had more wind than the forecast said, which would flatter the backtest. Not measured yet | Live reading defined (T-04). Missing is never calm. Step W0 rebuilds every label from an hourly archive, with the day-before forecast for 2024-2026. A full-game line needs a reading taken within 90 minutes of kickoff |
| D3 FATAL | One book at an assumed -110, or the best of four, is not what Phong can get | **Accepted in part.** DSB and Red105 have no price history, so their filter (T-05) cannot be replayed. That is a limit, stated in the plan | Primary grade is the average book at its own number and price. Best price is a side note. Robinhood is tested from its own price history (free) |
| D4 MAJOR | 45 comparisons | **Accepted for the second-half cells and SCORE.** Not for full-game wind: it was a named rule before the sweep (F-33, H-26) and it survives the correction | Six claims frozen in the plan, one statistic each |
| D5 MAJOR | SCORE is not shown apart from wind | **Accepted.** | The stand-alone SCORE claim is calm or indoor games only. A windy subset cannot rescue it |
| D6 MAJOR | The gate and the 40-bet stop read noise | **Accepted.** | Two-level gate (T-13). Reviews on fixed dates (T-14). The 40-bet stop is gone |
| D7 MAJOR | Fills, weather timing, stacked exposure | **Accepted.** | Every position in one game is one thesis (T-15). Each venue graded on its own settlement; no overtime game is ever left out |
| D8 MINOR | 2,931 against 2,946 | **Accepted, accounted for** (section 2) | Written into the backtest notes |
| Case against a separate track | Lane A duplicates the engine; a shadow ledger would do | **Half accepted.** Lane A is removed. The track is a ledger plus at most one paper line | The printed paper line stays for one cell only. Phong can choose "shadow only" instead |

## 4. Doubter's rule verdicts

| Rule | Verdict | Ruling |
|---|---|---|
| T-01 | Keep | Kept |
| T-02 | Define CLV; 30 or 60 lines prove nothing | Accepted. CLV defined. 60 forward lines buy a micro-stake test at most, never a full unit |
| T-03 | Fee, cell, Over permission | Settled by removing Lane A. The 2-cent fee was already inside the Robinhood price (R-06); now written into T-05 |
| T-04 | Decision-time weather, rounding | Accepted |
| T-05 | Paired quotes, freshness, consensus, independent books, pushes | Accepted. Book count set from what the feed really carries: 3 on the number for a full game, 2 for a second half |
| T-06 | Keep | Kept, with one addition from the scout (a Robinhood second-half Under may print: regulation-only can only help it) |
| T-07 | Deterministic pick, shared exposure | Accepted |
| T-08 | Define unresolved, weather success, roof | Accepted |
| T-09 | Reconcile with T-03 | Done |
| T-10 | Same pull; cents on one scale | Accepted. Tags are in probability points |
| T-11 | A veto needs shown harm | Accepted |
| T-12 | Log every candidate and why it was held back | Accepted |
| T-13 | 40 bets and a plus sign are not enough | Accepted |
| T-14 | No 40-bet cutoff; scheduled reviews | Accepted |
| T-15 | Discretionary tickets bypass the paper rule | Accepted in part. The track cannot stop Phong betting. It says so on every line, keeps those tickets out of its record, and counts them against his discretionary cap |

**Pass bar and kill rules.** Adopted as the proof level (T-13b) and the retire rule (T-13c). One change: the doubter's bar cannot be met by any wind cell on 990 games (a true 57% cell needs about 720 bets), so applying it to the purchased data would only produce "unconfirmed". The purchased data is therefore judged on the screen, labelled as such, and the proof bar is kept for forward games and for money.

## 5. Scout's findings

| # | Finding | Ruling |
|---|---|---|
| G1 | Wind bites at 15, collapses at 20, crosswind matters most | Sources are betting sites; the numbers are not verified. Our data shows no extra Under value at 20+. Speed and direction are logged so the split can be read later. No new cell |
| G2 | Books set the second-half total at 52-54% of pregame and over-react to a big first half | Our fit on real lines is about half the pregame total plus 0.063 per first-half point. The 28+ effect is not reported by anyone else. Re-fit on 2023-2026 added as a side note |
| G3 | Half-market odds exist only from May 2023; check week 1 first | Confirmed, and checked: 3 books at halftime in 2023 week 1 |
| G4 | nflverse wind is a kickoff figure; Open-Meteo has hourly history and archived forecasts | Forecast archive confirmed (most models from January 2024). Adopted as step W0. The nflverse source is not named in its own dictionary |
| G5 | Rule changes since 2021 | 2025 overtime (both teams get the ball) and the 35-yard touchback confirmed. The rest not verified. Overtime games are tagged; nothing else changes |
| G6 | Five new cells | See section 6 |
| G7 | Use a sharp book as the anchor; a lone best price without one may be noise | Sound, but Pinnacle and Circa are not in the feed for second-half lines. LONE-BEST stays a tag |
| G8 | The 2-cent fee costs about 2 points; regulation-only settlement spares the Under | Fee: already charged. Settlement: true but small, 0.7 points on average. Adopted in T-06 |

## 6. Scout's proposed cells

| Cell | Ruling |
|---|---|
| U4 crosswind 12+ with wind 15+ | Not declared. No direction data yet, about 20 games a season. Wind direction is logged from now on |
| U5 first-half Under in wind 15+ | Already in the plan (claim C2, at wind 10+) |
| U6 primetime Under | Not declared. Fails 2011-16 on our data. Logged as tag PRIME |
| O1 calm outdoor Over | Not declared. Fails 2017-21, and +1.0% does not cover a price step. No Over is printed |
| U7 big first half with a defensive or special-teams touchdown | Not declared (15 to 20 games a season). Logged as tag DST-TD on SCORE entries |

## 7. Where the manager did not follow the panel

- **Doubter: no printed line at all, shadow ledger only.** Kept one paper line for wind 15+. Reasons: the price rule keeps every printed line at fair or better, printed-against-skipped can only be checked if something is printed, and the full-game wind result is stronger than the doubter could see from the summary. Phong can overrule with "shadow only".
- **Doubter: the full statistical bar on the purchased data.** Not applied as pass or fail, for the reason in section 4. It is reported for information.
- **Scout: buy with Pinnacle or Circa in the book list.** Not possible; they are not in the feed for these markets.
- **Scout: confidence "high" on findings 1, 5, 7 and 8.** Marked down: the sources are betting-content sites and several numbers could not be found anywhere else.

## 8. What Phong decides

1. **Ratify v0.2** as written, or "shadow only" (no printed line).
2. **Start the paid pull** on the locked plan (about 49,800 credits of the 99,755 on hand).
