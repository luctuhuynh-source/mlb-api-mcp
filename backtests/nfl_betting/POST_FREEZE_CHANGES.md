# Changes made to the NFL protocols after the 10/11/2026 freeze

All seven were made at Phong's direction. None has been reverted. Each needs a keep / drop ruling if the frozen v0.5 is to be the
version in force (Phong, 11/11: "there was a version that got frozen since it was working well. I'd like to use that version").

| # | Date | Engine | Version label | Change | Phong's words (change log / tab) | Baseline rules it replaces |
|---|---|---|---|---|---|---|
| P1 | 10/15 | 1H and 2H | v0.6 | CLEAR LEAN rule v1.0: a lean prints only when 2 of 3 of personnel / FLOW / price agree and there is no hard counter; otherwise "NO CLEAR LEAN - pass" | Ratified on the SEA@DEN TNF board: display a lean only when it is clear | F-41, H-39 |
| P2 | 10/17 | 1H and 2H | none (addendum) | Time locks removed: 1H loses "nothing after T-12", the T-17 to T-12 window, TIME-BLOCKED, the 3/2/1 cap step-down; 2H loses "under 3 minutes -> shadow" and "unposted inside 4 minutes -> DEAD". Kickoff / 3Q kickoff are the only hard stops | "Yes unfreeze and change that for NFL protocol too" | F-31 (step-down), F-35, F-36, F-39; H-34, H-35 |
| P3 | 10/17 | 1H and 2H | none (addendum) | Robinhood restored as an execution venue: RH ask + 2 cents fee vs fair at the same strike, ask cap 60, spread 4 or less, better-EV venue first. Also 10/17: off-strike RH fires allowed ("Engine fire ok") | "Change that for NFL too. Robinhood is used to bet if the odds favor." | F-02, H-02, R-05 |
| P4 | 11/1 | 1H | v0.6a | Slate workflow: sweep all games in one pass, full runs on FLAGGED games only, STATIC games one-line pass, final pull on flagged games after inactives | "Let's do that from here on out. Same process as part of our NFL 1H betting protocol." | F-15 to F-18 |
| P5 | 11/1 | 2H | v0.6a | HOOK fires through CONSENSUS DIVERGENCE when the DSB number strictly beats every book in the pull; edge vs the nearest book; 3.0 floor unchanged | "let a HOOK fire through divergence when the DSB number beats every book in the spread, not just the modal" | H-18 |
| P6 | 11/8 | 1H | v0.6b | Bye-week teams use their last played game's FLOW row (STALE-1WK); inactives from team sites / official tracker at T-90 | "Do both." | F-06, F-18 (data source only) |
| P7 | 11/9 | 1H (and Game-flow tab, all engines) | v0.6c | ALWAYS PULL FLOW: every game, every run, never skipped for time; a game can be FLAGGED on FLOW alone | "Always pull flow." | F-06 fallback, G-07 |

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
