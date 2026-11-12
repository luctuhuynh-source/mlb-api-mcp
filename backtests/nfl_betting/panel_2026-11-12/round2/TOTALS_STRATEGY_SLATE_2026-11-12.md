# New strategies for the totals protocol - the manager's slate, 2026-11-12 about 3:00 AM

Phong, 2:54 AM: "Can you come up with any new strategy to improve our Total protocols? We can also asks chat gpt and gemini".

**Status.** Ideas only. Nothing here is a rule, nothing is in force, and none of it has been tested. The slate goes to the panel (Gemini = scout, ChatGPT = doubter, Claude = manager): `PROMPT_gemini_scout_round2.txt`, `PROMPT_chatgpt_doubter_round2.txt`. After the replies the manager rules, ONE test plan is locked, and the free tests are run in a single pass. The 990 games have been opened three times tonight, so they are not tested idea by idea.

## What tonight's data says a totals protocol has to be built on
- **Price carries the edge.** The average book charged -115 a side and sat 3.6 points worse than fair. The same wind bets were -0.9% at the average book and +4.3% at the best one. Phong's own half bets: 12-5 at fair or better, 12-15-2 worse.
- **Books disagree on the number, not the price.** At the first halftime look the books' second-half totals were a full point or more apart in 70% of games, and one book sat a point or more off the median in 60% (counted without reading a result). At the same number, no book was ever 3 points better than the rest in 685 games.
- **The engine cannot see that properly.** It moves a fair price across totals numbers at a flat 1.5 points per half-point. Measured, a half-point is worth from nothing (18, 22, 25, 28) to about 6 points (17), with 20, 24 and 27 in between.
- **One flow number sorts second halves:** first-half yards per play (Over rate 45.6% / 52.6% / 56.1% by third).
- **Unders are not a default any more.** Second halves ran 1.1 points over the line; Overs won 54.3% in 2025-2026.

## The slate

| # | Strategy | What it is | Why it might work | Test | Cost |
|---|---|---|---|---|---|
| S1 | Number table | A measured table of how often a total lands on each number, replacing the flat 1.5. A venue that hangs a better NUMBER then shows up as an edge; fire at 3.0+ | Number gaps are where totals differ, in most games. Every fire Phong has had came from a venue hanging a different number or price | Each book against the others across numbers, on the 990 games | Free |
| S2 | Flow plus price | A totals lean prints only when yards per play (top third Over, bottom third Under) and a fair-or-better venue price agree | The one flow number that sorted second halves, used only when the price does not give the edge back | The same games at the best posted book, then forward | Free |
| S3 | Team half form | Each team's season-to-date second-half scoring, for and against, measured against its earlier second-half lines | Halftime totals look formula-made; team habits by half may not be in them | Walk-forward on the 990 games | Free |
| S4 | Halftime line move | Which way the second-half total moves during halftime, and which book moves first | Three in four outlier prices are gone in five minutes: the early number may be the soft one | The two looks already bought | Free |
| S5 | Robinhood totals | Robinhood total contracts against the books' fair (S1 table, regulation-only adjustment), minute by minute at halftime | The only real-money venue. Its spreads were tight at the close; its totals at halftime open are untested | Kalshi price history for 2026 against the bought quotes | Free |
| S6 | Live total check | A book's second-half total against the live full-game total less first-half points | The same idea as DERIV-LAG on sides (2 fires, 2-0) | Live full-game totals at both looks | About 20,000 credits |
| S7 | More weather | Rain, snow and cold on full-game totals | Wind worked for years on full games before fading | 2011-2026 closing totals, weather text | Free |
| S8 | Over drift | Second halves running over the line since the 2025 rule changes | A market slow to re-price a rule change | Watch item only | Free |

## The manager's order, before the panel
1. **S1.** It is mechanical, it fixes something known to be wrong, and it feeds the engine, which is the only part of the protocol that has ever been shown to pay.
2. **S5.** It is the test that decides whether any of this can be bet with real money.
3. **S2,** as a silent log with a written rule.
4. **S3 and S4** if the panel thinks they are worth a claim each.
5. S6 only if S1 shows number gaps pay. S7 and S8 last.
