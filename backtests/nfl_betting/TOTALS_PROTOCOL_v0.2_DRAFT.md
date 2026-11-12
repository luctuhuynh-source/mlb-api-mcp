# NFL Totals protocol v0.2 - DRAFT for panel review (not in force)

Phong, 11/12/2026, about 1:14 to 1:17 AM: "Lets rewrite the track before you start the pull." Then: "I want you to dig up earlier version of the under and over. We had extensive back tests and live score with it. Use whatever data is useful. I also want Chatgpt and Gemini inputs on this revised protocol of the totals. So write a prompt for them with their role. You as the manager always."

**Status.** Totals track v0.1 (written an hour earlier) is ON HOLD and is not run on any board. This v0.2 is a draft. It goes to the panel (Gemini = scout, ChatGPT = doubter, Claude = manager). Nothing here is in force until Phong ratifies it. The paid data pull also waits, because the test plan in section 4 has to be locked first.

## 1. What the earlier Over and Under work says

Dug up 11/12 from the Cornerstone records (MLB first five innings, July to October 2026) and the early NFL second-half boards.

**A. The MLB Over engine (Cornerstone v1.4-T, later v3.0 to v3.2)**
- Built from a closing-line census: about 3,600 games, 7 books, 2025 and 2026.
- Its rules were about the shape of the board, not a scoring model. Enter: consensus total 5.0 or higher, 5 or more books, bet the best Over price at the consensus number. Vetoes: MGM alone posts the best Over (that cell lost 16% and 30% by season); best price 10 or more cents better than the second best; books 1.0 or more apart on the number; average Under price -120 or worse at the consensus number.
- Backtest: 583 bets, +6.8% (2025) and +8.7% (2026). A deeper run: 647 bets, +50.3 units, still +6.3% at 3 cents worse. The number had come out of a sweep of about 90 cells.
- Re-validated before v3.0: 669 bets, +0.8% and +2.1% after one point of price slip; negative in 2025 at two points. Stated expectation: +1 to +3%.
- Live: 18 placed bets went 7-11 (about -$998) through 8/8, before v3.0. Under v3.1 the fires went 3-0, then 2-8 (5-8 through 9/17). The last-20 check on Over recommendations read 7-12-1.
- The 9/18 diagnosis, after Phong asked for the culprit:
  - The backtest bet whole-number consensus lines, where a tie is refunded. Live bets were Robinhood half-point strikes, where the tie loses. The bridge was a "derived fair" with a 9% push constant. The measured push rate was 12.4% at 5.0 and 14.0% at 4.0.
  - Rules added after single bad nights (sign agreement, knife-edge, method divergence) were never backtested and selected against winners: the qualifiers the engine fired went 0-4, the ones it skipped went 11-6.

**B. The MLB Under protocol**
- Failed three separate backtests: the 7/23 census (3,638 games, no passing cell), the 8/4 window (the profit was two hot days), and the 8/6 pre-registered test (7 cells, 0 passed the gate "return above zero in both seasons, 40 or more bets in each"). Wind-in was +1.6% and -6.7% on 36 and 27 bets.
- Unders stayed display-only. One live observation was never tested: Robinhood Under prices sat at or below fair while Overs sat above it.

**C. NFL second-half totals in the early NFL versions (September and October 2026)**
- Price-gap fires on second-half totals: Under 21.5 MIN@TB won, Under 23 PHI@CHI won, Over 21.5 NYJ@CHI lost, Over 20.5 LAC@SEA won, Over 24.5 CHI@ATL won. 4-1 on five bets. Two had a measured close: +7 cents and +1.8 points.
- Totals leans from first-half yards per play lost to the price three straight times and were barred on 10/11. The shadow log since is 3-2.
- Rules dropped along the way: "lead of 17 or more means Under only"; the anchor total of 0.515 x the pregame total (audit B-NFL-1 on 129 games moved it to 0.50); "Unders within 3 at the half are shadow-only because of overtime".

**Lessons carried into v0.2**
- L1. Board and price rules held up better than matchup reads.
- L2. Bet and grade the same instrument: same number, same settlement. No derived fair.
- L3. Declare cells before looking. A cell passes only if it is above zero in each period on its own, 40 or more bets in each. Expect the live number to be a fraction of the backtest.
- L4. No rule from a single night. A veto is tested first. Until then it is a tag.
- L5. Log every qualifier, printed or not, so "printed against skipped" can be checked later.
- L6. A fair price is a requirement, not a tiebreak. Phong's own 46 NFL half bets: 12-5 at the closing fair or better, 12-15-2 worse.

## 2. The NFL cells through that gate

Free data only, no prices, every bet graded at -110 (break-even 52.4%). Script `backtest_2026-11-12/16_totals_cells_gate.py`.

| Cell | Record | Win % | Return at -110 | at -120 | By period | Gate |
|---|---|---|---|---|---|---|
| 2H Under, every game (base rate) | 1,476-1,379-76 | 51.7 | -1.3% | -5.1% | -1.7 / -0.7 | fail |
| 2H Under, wind 15+ | 143-107-7 | 57.2 | +8.9% | +4.7% | +7.7 / +10.5 | PASS |
| 2H Under, wind 10-14 | 243-211-12 | 53.5 | +2.1% | -1.8% | -0.6 / +5.3 | fail |
| 2H Under, first half 28+ | 428-361-17 | 54.2 | +3.5% | -0.5% | +3.0 / +4.0 | PASS |
| ... of which wind 10+ as well | 102-67-4 | 60.4 | +14.9% | +10.4% | +3.2 / +27.0 | PASS |
| ... of which no wind 10+ | 326-294-13 | 52.6 | +0.4% | -3.5% | +3.0 / -2.5 | fail |
| 2H Over, every game | 1,379-1,476-76 | 48.3 | -7.6% | -11.2% | -7.1 / -8.1 | fail |
| Full-game Under, wind 15+ | 181-140-5 | 56.4 | +7.5% | +3.3% | +4.8 / +10.3 / +8.8 | PASS |
| Full-game Under, wind 10-14 | 358-276-5 | 56.5 | +7.7% | +3.5% | -1.6 / +17.0 / +10.1 | fail |
| Full-game Over, wind under 10 | 945-884-21 | 51.7 | -1.3% | -5.2% | -2.4 / -2.6 / +2.2 | fail |

Periods: second half 2011-2016 and 2017-2021; full game adds 2022-2026.

- **Wind 15+ is the only cell that passes cleanly:** both markets, every period, and it survives -120.
- **First half 28+ passes as declared, but it is thin.** It dies at -120, and without wind it fails. It may be a by-product of wind.
- **Wind 10-14 fails the gate** on 2011-2016, though it is strong after that in both markets.
- **No Over cell is close.**
- **Full-game Under, wind 10+, at the actual closing Under price** (median -106): +9.7% on 965 games; +3.2% / +17.2% / +10.1% by period.
- **Windy games close only 0.5 to 1.0 point lower** than calm ones (43.9 and 44.4 against 44.9).
- **The old overtime worry has no support.** Games within 3 at the half go to overtime 7.2% of the time against 5.3%, and Unders did not do worse there (first half 28+ and within 3: 57.2%).

## 3. Draft rules

**Scope and status**
- T-01 NFL only. Full-game totals before kickoff; second-half totals at halftime. Same hard stops as the engine it runs beside. First-half totals are logged only: no real first-half line history exists to test them.
- T-02 Paper only. Every line is $0 with venue, number and price logged. Steps up, each on Phong's word: (a) the cell passes on 2023-2026 prices (section 4); (b) review at 30 graded printed lines; (c) micro-live only after 60 lines with a closing price and CLV above the margin (Liem L3.2, L5.7).

**Lane A: price fires (the engine, unchanged)**
- T-03 A total, Over or Under, fires only through the engine as written: a venue price 3.0 or more points better than the consensus fair at the same number, EV above zero, all gates (F-28, H-19). This draft changes nothing there.

**Lane B: Under cells (paper)**
- T-04 Cells, declared 11/12:
  - U1 WIND-A. Outdoor game or confirmed open roof, sustained wind 15 mph or more at kickoff. Printable.
  - U2 WIND-B. The same at 10 to 14 mph. Logged only until it passes on 2023-2026.
  - U3 SCORE. Second half only, first-half points 28 or more. Logged only until it passes on 2023-2026, with and without wind reported apart.
- T-05 Price. A line prints only when the Under at the venue's number is at the consensus fair or better at that same number, with 3 or more books on that number. No conversion across numbers. Table B-NFL-5 is a diagnostic until it is validated.
- T-06 Settlement. Printable venues: DSB and Red105 (second half includes overtime), and Robinhood full-game totals at a strike equal to the consensus number (all-in = ask + 2 cents). Robinhood half totals are regulation-only: logged, never printed.
- T-07 One totals line per game per window: full game before kickoff, second half at halftime.
- T-08 No line when a quarterback change at the half is unresolved, the weather pull failed (flagged at the top), a retractable roof is unconfirmed, or fewer than 3 books post the number.

**Lane C: Overs**
- T-09 This track prints no Over. Overs are display-only here, as MLB Unders were, until a declared Over cell passes the gate. The engine can still fire an Over on price with its existing vetoes.

**Tags (logged on every entry; none is a veto until tested)**
- T-10 LONE-BEST: one book alone has the best Under price by 10 or more cents. SPREAD-OUT: books' totals 1.0 or more apart. JUICE-OVER: average Over price -120 or worse at the consensus number. JUICE-UNDER: the same for the Under. CLOSE: halftime margin 0 to 3. BOTH: wind 10+ and first half 28+. Plus the venue gap (venue price against fair) on every entry.
- T-11 No new rule from a single slate. A tag becomes a veto, and a logged cell becomes printable, only by passing T-13.

**Output and ledger**
- T-12 RECOMMENDED gets a third line: `TOTALS (paper, $0): Under <number> <FG or 2H> @ <venue> <price>, WIND-A <mph>, price <edge> vs fair`, or `TOTALS: none`. Logged-only entries are never shown (Phong, 10/11). Every qualifier of every cell goes in the ledger, printed or not: inputs, tags, venue price, fair, result on the venue's settlement, closing fair, CLV.

**Gate and checkpoints**
- T-13 The gate for any cell or tag: defined before the data is looked at; return above zero in each period with 40 or more bets per period; still above zero one price step worse; then confirmed on data that was not used to find it.
- T-14 Review at 30 graded printed lines. At 40, a cell at -3% or worse goes back to logged-only. No promotion on win-loss alone under 200 bets (Liem L3.1).
- T-15 A printed line Phong bets is a DISC ticket (M-02; Liem L5.6, leader plus Under in the same half is one thesis). The track never tells him to bet.

## 4. Test plan for the paid pull (to be locked before any data is bought)

Data, 990 games, 2023 to 11/9/2026:
- Halftime, two looks per game (2 to 7 minutes in, and the last look before the 3rd-quarter kickoff): second-half spreads and totals, about 39,600 credits.
- Before kickoff, one look: first-half totals, about 9,900 credits. Full-game closing totals and prices are free (nflverse).
- Wind: nflverse kickoff reading where it exists. Games with no reading are left out and counted. A weather-archive tool can fill them if the panel says it matters.

Tests, each graded twice (at the best feed price on the consensus number, and at the average price there):
- P1 WIND-A and WIND-B Unders on second-half totals 2023-2026. Unseen data.
- P2 WIND-A and WIND-B Unders on first-half totals 2023-2026. Unseen data.
- P3 SCORE Unders on second-half totals 2023-2026, with and without wind. Unseen data.
- P4 The tags as modifiers: does a cell do worse when LONE-BEST, SPREAD-OUT or JUICE is on. Reported; acted on only with 40 or more in each arm.
- P5 The engine questions from 11/12: how often one book is 2 or 3 points off the rest when halftime opens, and whether it is corrected by the close. Sides and totals apart.
- P6 Control cells expected to fail: Overs in domes; Overs after a first half of 13 or fewer.
- Already seen, so not counted as confirmation: full-game wind 2022-2026.

Pass rule: T-13 with periods 2023-2024 and 2025-2026. A cell with fewer than 40 in a period is "underpowered" and stays logged-only. No cell is added after the data is seen without a fresh holdout.

## 5. Open questions for the panel
1. Is the wind figure a kickoff reading, and how far off is a forecast 60 to 90 minutes before kickoff?
2. Has the market closed the wind gap since 2021?
3. Is SCORE real, or a by-product of wind?
4. Which other inputs deserve a declared cell?
5. Do the MLB board tags mean anything for NFL totals?
6. Is the gate strong enough after about 45 comparisons?
7. What will go wrong at Phong's venues even if the backtest is true?
