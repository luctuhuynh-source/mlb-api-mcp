# College football sides: what the protocols say today (11/12/2026)

Written for the panel review Phong asked for by voice ("write a detailed summaries of what we currently have ... a command prompt so that way ChatGPT and Gemini can help us examine our protocol ... let's just do this with the side only"), typed 5:27 AM: "Cfb review". Read from the doc tabs as exported at 5:20 AM (`CFB_1H_tab.txt`, `CFB_2H_tab.txt`, `GAME_FLOW_tab.txt`). Sides only: spreads and the lean. Totals are left out.

## Shared by both windows
- **Venues.** DSB and Red105 (paper sportsbooks) and Robinhood (real money, Kalshi contracts; ask + 2 cents; ask cap 60 cents; bid-ask 4 cents or less). None of the three enters the consensus.
- **Two outputs on every board.** ENGINE (a priced fire, $150 to win) and MATCHUP LEAN ($0 unless Phong bets it).
- **Engine = a price test.** Fire when a venue's price beats the de-vigged fair of outside books at the same number by 3.0 points of win probability, EV above 0.
- **Executability (11/6).** Outside quotes no older than 30 seconds, fillable size for the full stake; otherwise shadow.
- **CLEAR LEAN (10/15).** Three inputs: PERSONNEL (QB1, tackles, centre, CB1, S1, WR1 out or limited), FLOW (yards per play, giveaways, clean margin, sustain rate), PRICE (which side DSB prices at or above the fair). A lean prints when 2 of 3 agree and the third is not a hard counter (QB1 scratch, a 1.5 yards-per-play gap against the side, two monitored starters out). A missing input casts no vote. No lean at worse than -115.
- **Lean price gate (11/12, from NFL work).** A printed lean is bet only at the fair or better.
- **Spreads may be converted across a number** with the measured college push tables. All tiers (P4, G5, FCS) are eligible. Kill switch: 0-3 on live fires sends that engine to paper.

## CFB 1H v2.0e (pregame; kickoff is the only stop)
1. Read the venue's 1H spread and price.
2. Consensus: 6 to 8 outside books, de-vig at identical numbers. Fewer than 4 usable books, or books more than half a point apart: shadow.
3. Quarterback check per team: STABLE, MATERIAL UNCERTAINTY (shadow for spreads) or CONFIRMED CHANGE (the market must have repriced).
4. Engine fires on (a) the 3.0-point price test, or (b) a HOOK: the venue hangs 3 or 7 while the books sit on the hook, passing the same test with the push table (1H margin exactly 3 = 11.5%, 7 = 15.3%, 10 = 6.1%, tie 5.7%; 314 games).
5. FLOW for the lean is an optional quick read of each team's previous game. It never moves the fair.
6. Every fire, lean and shadow is logged with the closing consensus.
- **Retired:** the anchor (0.50 x full-game spread) as a trigger, the 2-point gap gate (never reached in about 25 boards), DERIV-LAG as a trigger, the four-pull schedule, the 12-minute lock, the four-tier quarterback gate, the G5/FCS block, steam, tempo, body-clock and script gates.

## CFB 2H v2.3b (halftime; the third-quarter kickoff is the only stop)
1. Step 0: confirm halftime, pull first-half drives for every game, print the FLOW table (yards per play, clean margin = margin without return scores, short-field scores and drives under 30 yards).
2. Engine: the 3.0-point price test against two or more outside books at the same number. One book only, or books a point apart: shadow.
3. Vetoes: lead of 28 or more, nothing; 21 to 27, no spread. Quarterback changed or unverified: shadow the side. Market must be a tradable 2H line.
4. Pre-ticket: re-pull the books and the venue, one news check.
5. Lean: CLEAR LEAN, with the extra hard counters lead 21+ and 2 or more net turnovers.
6. Shadow columns logged every board: home team 2H, trailing team favoured in the 2H line, team receiving the third-quarter kickoff, leader under 21 without FLOW.
- **Retired:** the anchor (0.50 x pregame spread, shifted up to 1.5 for FLOW) as a trigger, the 2-point and 3-point gap modes, the G5/FCS block, the FLOW-led lean (v2.1, lasted one day, 0-4).

## What our own tests have said (college, sides)
| Test | Result |
|---|---|
| 1H leans audited 10/17 | 13 leans, 8-5, beat the close 2 of 13, mean closing-line value -0.9 points |
| 1H pregame replay, 91 games (10/24, 10/31) | Best single-book price beat the consensus fair 3 times in 364 prices, by at most 0.52 points. Home 47-44, favourites 40-51 |
| 2H, 102 games (9/5 to 10/10) | The anchor has no value over the halftime market: betting toward it 15-17; our 36 boards on the anchor side 15-21 |
| 2H, about 40 boards reviewed 10/17 | The FLOW side went 3-8 against the 2H number; halftime leaders laying 2H points 5-10; FLOW-led leans 0-4 |
| 2H replay, 91 games (10/24, 10/31) | Engine stand-in 0 fires (two books never 3.0 apart). CLEAR LEAN 2-0. FLOW side with a lead under 21: 17-6. Leaders without FLOW 22-26. Home team 2H 58-33. Trailing team favoured 12-15 |
| Pooled FLOW side, three Saturdays | 23-19 |

## What the NFL work of 11/12 found (not tested on college)
- A big book 3.0 better than the rest at halftime: 68 of 901 games, 41-33-1, +5.4%; three in four gone in five minutes.
- Robinhood at halftime sits on the books' fair; it costs about 2.7 points to take; 3.0 better at the same number in 3 of 125 games.
- Phong's own half bets: 12-5 at the fair or better, 12-15-2 worse.
- The halftime team that moved the ball and led covered about 52%.

## Plain reading
- Both engines are the same idea: wait for a venue to misprice the consensus by 3 points. Against mainstream books that almost never happens, so nearly every board prints "ENGINE: none" and the lean carries the action.
- The lean has no proven edge: 8-5 with negative closing-line value in the first half; two reversals in one day in the second half.
- The two strongest things in the college data are untested shadow columns: home team in the second half (58-33) and the FLOW side with a lead under 21 (17-6). Both are two Saturdays.
