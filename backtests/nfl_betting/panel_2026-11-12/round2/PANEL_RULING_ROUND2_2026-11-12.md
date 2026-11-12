# Panel ruling, round 2: new strategies for totals - 2026-11-12, about 3:45 AM

Panel: Gemini = scout, ChatGPT = doubter, Claude = manager. Slate: `TOTALS_STRATEGY_SLATE_2026-11-12.md`. Replies as received: `REPLY_gemini_scout_round2.txt`, `REPLY_chatgpt_doubter_round2.txt`. Locked plan: `../../backtest_2026-11-12/halftime_pull/ROUND2_TEST_PLAN_LOCKED.md`. Results: `../../BACKTEST_2026-11-12.md`, section 17.

## 1. Bottom line
- **The doubter was right on both of its FATAL findings**, and one of them reaches past totals into rules that are in force.
- **Robinhood second-half contracts count overtime.** The contract text says so (section 2). Rules R-02, H-02 and H-12 and change P8 say "regulation only". The engine has been shadowing Robinhood second-half prices over a mismatch that does not exist. Logged as X-35. Phong's word is needed to correct the rules.
- **The number table (S1) failed.** Its own check failed (ties predicted 7.0%, happened 4.4%), and betting the book with the better number went 91-99-2, -11.4%.
- **Nothing on the slate earned a place.** Totals stay price-only at the same number.

## 2. What was verified
| Claim | Result |
|---|---|
| Doubter: Kalshi second-half totals count overtime | **True, and wider.** Contract text of KXNFL2HTOTAL, KXNFL2HSPREAD and KXNFL2H (winner): "in the 2nd half (including overtime)" and "Only points scored during the 2nd half (including overtime) of play count towards this market". Read on a 10/18/2026 contract and on 11/16/2026 contracts. First-half contracts: "in the 1st half" |
| Scout: a Kalshi study shows price-takers lose | The paper exists (Burgi, Deng and Whelan, "Makers and Takers", CESifo working paper 12122): over 300,000 contracts, a favourite-longshot bias, makers the better-informed side. The scout's return figures are not in its abstract |
| Robinhood's fee | Its help page: commission capped at 1 cent a contract plus an exchange fee of up to 1 cent, on opening and closing trades. "Ask + 2 cents" is the ceiling. Resting orders are not mentioned |
| Scout: books run live game totals beside halftime lines | One 10-credit lookup: the odds archive does carry live full-game totals at halftime (ten books, all on one number, quotes seconds old) |
| Scout: Borghesi on weather and totals | Exists: "Weather biases in the NFL totals market", Applied Financial Economics, 2008 |
| Doubter's arithmetic | Reconciles. The 3.0+ spread entries were about -110 on average; the cautious end it computes for the yards-per-play Over (-3.3%) differs from ours (-4.1%) because ours counts the games of one week together |

## 3. The doubter's findings
| # | Finding | Ruling |
|---|---|---|
| 1 FATAL | Robinhood totals: settlement is not regulation-only; minute data cannot be matched to two book looks | **Accepted.** Settlement audited (section 2). Robinhood is compared with the books only at the two look times |
| 2 FATAL | The number table can manufacture the whole edge | **Accepted and confirmed by the test.** The table failed its check and the bets lost |
| 3 MAJOR | 41-33-1 is 75 bets, not 68 games; returns need real prices | Accepted. They are real prices; the count is 75 entries in 68 games |
| 4 MAJOR | The 990 games are used up; two frozen claims at most | Accepted. R1 and R2 only |
| 5 MAJOR | Flow plus price brings a failed Under back | Accepted. Under side dropped. Over side is a silent log only |
| 6 MAJOR | Team half form has no support | Accepted. Dropped |
| 7 MAJOR | Two looks cannot show which book moved first | Accepted. Dropped as a claim |
| 8 MAJOR | Do not buy live totals before access is shown | Accepted. No credits spent beyond the 10-credit check |
| 9 MAJOR | Rain, snow and cold have no evidence here | Accepted. Dropped |
| 10 MAJOR | The Over drift is an era split, not a cause | Accepted. Silent log with a fixed review date, if Phong wants it |
| 11 MAJOR | "Price carries the edge" is not proven | Accepted. It is a working reading on 44 decisions |
| 12 MINOR | Rounding | Noted |

## 4. The scout's findings
- **Taken:** number table first (tested, failed); the Robinhood test should include resting orders; a staged pilot before any live-totals purchase; halftime numbers are formula-made and stale ones last seconds to minutes.
- **Its drops agreed:** team half form, non-wind weather, flow on raw yards per play as a rule.
- **Parked, untested:** quarterback change at the half, favourite receiving the second-half kickoff, two-minute-drill fade, late-season division Unders, better flow numbers (success rate, expected points). The two-claim limit leaves no room for them on this data.
- **Its "close-game regulation Under on Robinhood" is void:** the contracts count overtime.
- **Not verified:** the return figures (1.5 to 2.5%), the 2026 kicking numbers, anything sourced to "NFL Analytic".

## 5. Results of the locked plan
- **R1 number table: FAILED.** Details in the backtest write-up, section 17.
- **R2 Robinhood totals: not run.** Its gate (the table's check) failed. The settlement audit it also required is done.

## 6. What Phong decides
1. Confirm in the Robinhood app that a second-half contract's rules line says "including overtime", then "fix it": correct R-02, H-02, H-12 and P8.
2. "robinhood": a re-scoped test at the same number only (no table), second-half spreads and totals against the books at both halftime looks, this season's games. Free.
3. "log it" for the two silent logs (yards-per-play Over; Over drift), or leave them.

## 7. Outcome (11/12, 3:36 to 3:45 AM)
- Phong, 3:36 AM: "RH include over time.  Fix it". Change P9 written: NFL 2H v0.6c, Robinhood venue rules v1.1 (`RULES_CURRENT.md`, `POST_FREEZE_CHANGES.md`, checklist C28, the football doc's NFL 2H tab, Robinhood tab and change log). X-35 and X-31 closed.
- A third confirmation was found: the 10/15 SEA@DEN overtime game. Seattle won the second half by 11 in regulation and by 8 with overtime; "Seattle wins 2H by over 9.5" settled No.
- Phong, 3:40 AM: "CFB too". The college contracts carry the same words (11/14 contract). CFB 2H v2.3a written into the football doc: eight lines corrected in place in the CFB 2H tab, an addendum, and a change-log entry. CFB rules live in the doc only; there is no CFB rule file in this repo.
- Not re-graded: past Robinhood-priced entries from overtime games, NFL or college.
