# NFL Totals protocol v0.2 (paper only) - final text after panel review

**Status: NOT IN FORCE, and after the replication it has no printable cell.** The paid pull was graded on the locked plan on 11/12 (`BACKTEST_2026-11-12.md`, section 15): the second-half wind Under returned -0.9% at real halftime prices and FAILED, so by the plan's own rule no wind line prints in either window; the first-half wind claim and the stand-alone SCORE claim FAILED too. What is left of this protocol is a silent ledger. Phong decides: keep it as a silent ledger, or shelve it. Boards run as before (ENGINE and MATCHUP LEAN only) and v0.1 stays on hold.
Written 11/12/2026 after the review Phong ordered ("I also want Chatgpt and Gemini inputs on this revised protocol of the totals... You as the manager always"). The draft the panel saw is `TOTALS_PROTOCOL_v0.2_DRAFT.md`. Every ruling and its reason is in `panel_2026-11-12/PANEL_RULING_2026-11-12.md`.

## What this track is

- A **paper ledger for Under cells on NFL totals**, run in the same pass as the game. It prints at most one line per game per window, at $0.
- It changes no engine rule. **Price fires on totals stay in the engine** (F-28, H-19) with the engine's Over vetoes (F-33, H-25, H-26) and its one-selection rules (F-30, H-36).
- It never prints an Over.
- **What to expect:** about 15 to 17 games a season have wind of 15 mph or more. Each can give one full-game entry and one second-half entry, and the price rule will hold some of those back. This track tests an angle cheaply. It will not add many bets.

## Rules

**Scope and status**
- T-01 NFL only. Two windows: full-game totals before kickoff, second-half totals at halftime. Same hard stops as the engine (kickoff; the 3rd-quarter kickoff). First-half totals are logged only.
- T-02 Paper only. Every line is $0 with venue, number and price logged. Steps up, each on Phong's word only:
  - (a) A paper line: the cell has passed the screen, T-13(a).
  - (b) A micro-stake test (Liem L5.7 size): 60 printed lines on games played after 11/12/2026, each with a closing price, return above zero, average CLV zero or better. A coin-flip cell gets this far about half the time. That is why it buys a micro stake at a fair-or-better price and nothing more.
  - (c) A full unit: the proof bar, T-13(b).
  - CLV here means: the closing fair of the Under at the same number and the same settlement (T-05, last pull before kickoff or before the 3rd-quarter kickoff) minus the break-even of the price taken, in probability points. A Robinhood price includes the 2-cent fee. No closing quote at that number: CLV is blank, not zero, and the line does not count toward the 60.

**What is outside this track**
- T-03 A total that qualifies on price alone, Over or Under, is an engine matter and is handled there as written. If the engine fires a total in a game and window, that is the game's totals line. This track's entry for it is logged with the tag ENGINE-SAME or ENGINE-OPPOSITE and is not printed.

**Cells (Under only), declared 11/12/2026**
- T-04
  - U1 WIND-A. Outdoor game or confirmed open roof, sustained wind 15.0 mph or more. Printable on paper. **Switched to logged-only on 11/12 by the replication result (claim C1 failed).**
  - U2 WIND-B. The same at 10.0 to 14.9 mph. Logged only.
  - U3 SCORE. Second half only, first-half points 28 or more. Logged only. Its stand-alone claim is the calm or indoor games; SCORE in wind is judged as the gain over windy games without it.
  - The wind reading is the sustained wind speed in mph at the stadium from the weather pull. Gusts and direction are logged, not used. No rounding: 14.9 is not 15.
  - Full game: the forecast for the kickoff hour, from a pull made within 90 minutes of kickoff. An earlier reading is logged, not printed.
  - Second half: the current-hour reading at the halftime pull.
  - A failed or missing weather pull means the wind is unknown. Unknown is never treated as calm: no line, and the failure is flagged at the top of the reply.
  - Retractable roof: open or closed must come from the team, the league or the broadcast before the pull, with source and time logged. Unconfirmed: no line (F-32).

**Price**
- T-05 A line prints only when the Under at the venue is priced at the fair or better, at the same number and the same settlement.
  - Fair = the median no-vig Under probability of the books that quote both sides at that exact number in the same pull.
  - Books needed on that number: 3 for a full game, 2 for a second half (the feed carries only 3 to 6 books on second-half totals). Two brands of one operator or one feed count once.
  - A quote that was last updated before the first half ended is stale and is dropped at halftime. Before kickoff, a quote older than 30 minutes is dropped.
  - Venue price: sportsbook odds as shown. Robinhood all-in = ask + 2 cents.
  - Edge = fair minus the break-even of the venue price, in probability points. Prints at 0.0 or more.
  - Whole-number totals: the tie is a refund at the venue and at the books alike, so the two are compared at that same whole number with no adjustment. Robinhood strikes are half-points and are compared only with books on that same half-point.
  - No conversion across numbers. Table B-NFL-5 is a diagnostic.

**Settlement**
- T-06
  - DSB and Red105: the second half includes overtime, as at the books.
  - Robinhood full game: includes overtime. Printable at a strike equal to a book number.
  - Robinhood second half: regulation only. Overtime points can only hurt an Under, so the books' fair is a floor for a Robinhood second-half Under (worth 0.7 points on average, 2011-2021). It may print at a strike equal to a book number when its all-in price is at that fair or better, tagged REG-ONLY.
  - Every entry is graded on its own venue's settlement. No overtime game is ever left out.

**One line**
- T-07 One totals line per game per window. When more than one venue qualifies: the largest edge; then the better payout; then DSB, Red105, Robinhood in that order.
- T-08 No line when:
  - a starting quarterback has left the game and the team has not said who plays the 3rd quarter by the time of the pull (H-27);
  - the weather pull failed, or a full-game reading is older than 90 minutes;
  - a retractable roof is unconfirmed;
  - fewer books than T-05 requires are on the number.
- T-09 No Over is printed by this track.

**Tags (logged on every entry; none is a veto)**
- T-10 All from one pull, in probability points so sportsbook odds and contract cents share one scale.
  - LONE-BEST: the best Under price is 2.0 or more better than the second best.
  - SPREAD-OUT: the books' totals are 1.0 or more apart.
  - JUICE-UNDER, JUICE-OVER: the average price of that side at the most common number is 54.5% or worse (-120).
  - CLOSE: halftime margin 0 to 3. BOTH: wind 10+ and first half 28+.
  - PRIME: Sunday, Monday or Thursday night game. DST-TD: a defensive or special-teams touchdown in the first half. OT: the game went to overtime.
  - Also logged: wind speed, gusts and direction; the venue's edge against fair; how many books were dropped as stale.
- T-11 No new rule from a single slate. A tag becomes a veto only when the tagged entries are shown to do worse than the untagged ones (the gap itself, not "the rest is still profitable"), on games not used to find it, with 40 or more in each group.

**Output and ledger**
- T-12 RECOMMENDED gets a third line: `TOTALS (paper, $0): Under <number> <FG or 2H> @ <venue> <price>, WIND-A <mph> mph, price <edge> vs fair`, or `TOTALS: none`. Logged-only entries are never shown (Phong, 10/11). The ledger holds every candidate of every cell, printed or not, with the reason it was held back: price worse than fair, too few books, weather unknown, roof, quarterback, engine fired, or logged-only cell. Each entry: inputs, tags, venue price, fair, result on the venue's settlement, closing fair, CLV.

**Gate**
- T-13
  - (a) Screen, for a paper line only. The cell is defined before the data is looked at; its return is above zero in each period with 40 or more bets per period; the pooled return is still above zero one price step worse (-110 to -115, or 1 cent). **Passing the screen is not proof.** A coin-flip cell passes it about 1 time in 3.
  - (b) Proof, for any full-size stake. On games played after the cell was declared, at the prices logged when the line printed: the cautious end of the estimate (one-sided 95% lower bound of the return) is still a profit, after counting every cell on test and counting the games of one week together; and the same one price step worse. For a cell that truly wins 57% this takes roughly 700 graded lines.
  - (c) A cell is RETIRED when the hopeful end of the estimate (one-sided 95% upper bound) is a loss. A cell that is neither proven nor retired is UNPROVEN and stays on paper.
- T-14 Reviews happen on fixed dates, not after a run of results: once when the 2023-2026 replication is graded, then after Week 18 of each season. Nothing is promoted or cut between reviews.

**Exposure**
- T-15 The track never tells Phong to bet. A printed line he bets is his DISC ticket (M-02): it stays out of this track's record and counts against his discretionary cap. Every position in one game (full-game Under, second-half Under, a side) is one thesis under Liem L5.6. In wind the leader-plus-Under pair moves together more than usual (correlation 0.17 against 0.09).

## Evidence, in one table

| Cell | Record | Return | By period | Standing |
|---|---|---|---|---|
| Full-game Under, wind 10+, real closing price, 2011 to 11/9/2026 | 539-416-10 | +9.7% (se 3.0) | +3.2 / +17.2 / +10.1 | Strongest result on file. Stands after allowing for 45 comparisons |
| Full-game Under, wind 15+, real closing price | 181-140-5 | +9.4% (se 5.3) | +7.4 / +12.3 / +8.8 | Passes the screen |
| Full-game Under, wind 10-14, real closing price | 358-276-5 | +9.8% (se 3.7) | +0.8 / +19.8 / +10.6 | Passes by a hair in 2011-16; kept logged-only |
| Second-half Under, wind 15+, real lines 2011-2021, -110 assumed | 143-107-7 | +8.9% | +7.7 / +10.5 | Passes the screen; weak alone |
| Second-half Under, wind 10-14 | 243-211-12 | +2.1% | -0.6 / +5.3 | Fails the screen |
| Second-half Under, first half 28+, calm or indoors | 326-294-13 | +0.4% | +3.0 / -2.5 | Fails the screen |
| Any Over cell | - | below zero | - | None close |

Known limits, all from the review: the wind figure in these tests is a kickoff reading, not a forecast; no half-line prices exist before 2023; DSB and Red105 have no price history, so the price rule (T-05) can only be tested going forward; the 2023-2026 data overlaps results already seen.

## What changed from the draft

- Lane A (price fires) removed from the track; it stays in the engine. This also ends the clash with the no-Over rule.
- Wind reading defined for each window; unknown is never calm; a full-game line needs a reading within 90 minutes of kickoff.
- The price rule now says how the fair is built, how fresh a quote must be, and how many books are needed (3 full game, 2 second half).
- A Robinhood second-half Under may print (regulation-only can only help an Under). In the draft it was logged only.
- The gate is split into a screen (paper) and a proof bar (money). The 40-bet loss stop and the "200 bets" line are gone. Reviews are on fixed dates.
- Tags are in probability points. Three tags added from the scout: PRIME, DST-TD, wind direction.
- A veto needs shown harm against the untagged group.
- Every position in one game is one thesis.
