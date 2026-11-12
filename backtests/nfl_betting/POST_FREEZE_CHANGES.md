# Changes made to the NFL protocols after the 10/11/2026 freeze

All were made at Phong's direction. None has been reverted. On 11/11 Phong said "there was a version that got frozen since it was
working well. I'd like to use that version", which left the choice of profile open.

**Ruled 11/12/2026: the profile in force is `current`.** Phong: "Current but make this can fire by any books instead of dsb only." That keeps P1 to P7 and adds P8. P9 (11/12, 3:36 AM) corrects a fact the rules had wrong: Robinhood second-half contracts count overtime.

| # | Date | Engine | Version label | Change | Phong's words (change log / tab) | Baseline rules it replaces |
|---|---|---|---|---|---|---|
| P1 | 10/15 | 1H and 2H | v0.6 | CLEAR LEAN rule v1.0: a lean prints only when 2 of 3 of personnel / FLOW / price agree and there is no hard counter; otherwise "NO CLEAR LEAN - pass" | Ratified on the SEA@DEN TNF board: display a lean only when it is clear | F-41, H-39 |
| P2 | 10/17 | 1H and 2H | none (addendum) | Time locks removed: 1H loses "nothing after T-12", the T-17 to T-12 window, TIME-BLOCKED, the 3/2/1 cap step-down; 2H loses "under 3 minutes -> shadow" and "unposted inside 4 minutes -> DEAD". Kickoff / 3Q kickoff are the only hard stops | "Yes unfreeze and change that for NFL protocol too" | F-31 (step-down), F-35, F-36, F-39; H-34, H-35 |
| P3 | 10/17 | 1H and 2H | none (addendum) | Robinhood restored as an execution venue: RH ask + 2 cents fee vs fair at the same strike, ask cap 60, spread 4 or less, better-EV venue first. Also 10/17: off-strike RH fires allowed ("Engine fire ok") | "Change that for NFL too. Robinhood is used to bet if the odds favor." | F-02, H-02, R-05 |
| P4 | 11/1 | 1H | v0.6a | Slate workflow: sweep all games in one pass, full runs on FLAGGED games only, STATIC games one-line pass, final pull on flagged games after inactives | "Let's do that from here on out. Same process as part of our NFL 1H betting protocol." | F-15 to F-18 |
| P5 | 11/1 | 2H | v0.6a | HOOK fires through CONSENSUS DIVERGENCE when the DSB number strictly beats every book in the pull; edge vs the nearest book; 3.0 floor unchanged | "let a HOOK fire through divergence when the DSB number beats every book in the spread, not just the modal" | H-18 |
| P6 | 11/8 | 1H | v0.6b | Bye-week teams use their last played game's FLOW row (STALE-1WK); inactives from team sites / official tracker at T-90 | "Do both." | F-06, F-18 (data source only) |
| P7 | 11/9 | 1H (and Game-flow tab, all engines) | v0.6c | ALWAYS PULL FLOW: every game, every run, never skipped for time; a game can be FLAGGED on FLOW alone | "Always pull flow." | F-06 fallback, G-07 |
| P8 | 11/12 | 2H | v0.6b | HOOK through divergence can fire at any of Phong's venues (DSB, Red105, Robinhood) whose number strictly beats every book in the pull, not at DSB only. Edge vs the nearest book, 3.0 floor at that venue's price. Robinhood 2H is regulation-only, so it qualifies only where overtime cannot change the result until a conversion is written | "Current but make this can fire by any books instead of dsb only." | H-18 (P5 wording), H-17 |
| P9 | 11/12 | 2H; Robinhood venue rules | 2H v0.6c; venue rules v1.1 | Robinhood second-half contracts count overtime, like DSB and Red105. A Robinhood 2H price is compared with the consensus fair like any other venue price. Retired: the overtime shadow in H-02, the "8 points from the tie margin" test, the separate regulation push table, and the overtime restriction on P8. Evidence: the contract text ("in the 2nd half (including overtime)") on 10/18 and 11/16 contracts for spread, total and winner; the 10/15 SEA@DEN overtime game settled with overtime counted. Found by ChatGPT in the 11/12 totals review | "RH include over time.  Fix it" | H-02, H-12, H-17, H-18, R-02 |

## Keep / drop (11/11/2026 review, `REVIEW_2026-11-11.md` section 10)
Recommended: keep all seven. No change is tied to worse results: v0.6 and v0.6a pick leans with the same rule and went 15-18-2 and
7-3. Two conditions: P5 runs on the corrected push table (its one fire, LAR -3, reads +2.1 instead of +4.4 and would not have
fired), and P4 keeps the two v0.5 parts it never retired (four full runs per window, inactives for every game). Phong's ruling is
still needed to make `current` the profile in force.

## What strict v0.5 would bring back
- A lean line on every game examined (no NO CLEAR LEAN filter). Under the 10/11 betting policy that means more tickets.
- The 1H T-12 placement cutoff and the 2H Q3 -4 lock. Boards run late (11/8 GB@NE at T-2, most halftime boards) would be TIME-BLOCKED.
- DSB as the only execution venue. Robinhood is the live-money venue; DSB is a paper account (memory note M-03). Strict v0.5 means no live NFL tickets at all.
- Watchlist of four games per window with a lightweight screen on the rest, instead of sweep -> flagged.
- No HOOK-through-divergence: the 2H engine went 0 fires from 10/11 to 11/1 under H-18.
- FLOW may be skipped for time, and bye-week teams have no FLOW row.

## Open items raised 11/9, never ratified (not rules)
- A: two soft aligned inputs with no hard counter -> print the lean?
- B: QB-change rows use the replacement QB's most recent start instead of void? (Phong 11/9: information only, "Dont change anything in our protocol".)
