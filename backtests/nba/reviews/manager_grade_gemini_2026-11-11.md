# Manager's grade of Gemini's review of NBA FD v1.3 (2026-11-11)

Tests are in `results/b78/`. "Candidate" = CAL projection, no ownership tiers, overlap 6. Percentiles are versus the contest field.
All 164-slate numbers use LineStar's final (post-lock) data, like B77.

> Superseded in part by the ChatGPT round (see `manager_grade_chatgpt_2026-11-11.md` and `NBA_FD_v14_proposal_2026-11-11.md`): Q7 - the wide
> re-optimisation rule is a shadow, not the live rule; Q10 - the cheap-teammate cap is dropped and team cap 3 kept after a four-arm test;
> Q11 - the trial is 30 slates, one value per slate in a primary contest named before the build.

## Corrections to the packet
- R5 was worded as "replace only players ruled out", which drops v1.3 rule 17(b). That was a wording error, and the conclusion behind it (late swap is worth ~1 FP) was wrong: see Q7.
- B77 levels are optimistic by an amount we cannot pin down yet: see Q12.

## Verdicts
| Q | Gemini | Test | Verdict |
|---|---|---|---|
| 1 | Regress the field-SD multiplier on slate size and ownership concentration; use the empirical distribution | Multiplier vs games r = -0.07, vs sum(own^2) r = -0.09. Leave-one-slate-out error is worse with the regression: field SD off by 3.2 FP vs 2.7 for the fixed 0.35; top-10% line 4.0 vs 3.7; top-1% line 6.4 vs 5.6 (18 contests, 12 slates). Empirical distribution is already in use. | REJECT |
| 2 | AggProj may leak post-lock news; gate R2 on the pre-lock pulls | Player level (742 pre-lock rows, 7 slates): error LS 8.45, AggProj 8.21, CAL 8.16; CAL better on 6 of 7 slates (0.24, SE 0.08). AggProj moves LESS than LS after the pull (3+ FP movers 2-6% vs 7-9%; accuracy gain after lock 0.03 vs 0.09). When they disagreed by 4+ FP before lock, AggProj was right (n=85: LS 23.1, Agg 28.9, actual 28.6). Lineup level (8 slates, same structure): CAL - pure LS = +11.4 FP per lineup (SE 7.6), 6 of 8 slates; cashes 11 of 32 vs 2. Same slates on final data: +12.4. | GATE PASSED, R2 stays |
| 3 | Overlap 7 plus a game stack on lineups 2-4 | Overlap 7 or 8 vs 6 (no exposure cap): -0.2 / 0.0 FP (SE 0.7) and slates with no cash rise from 25% to 32%. Game stack: -0.3 FP (SE 0.7) at overlap 6, -0.9 (SE 0.8) at overlap 7; top-1% estimate +0.3 pts (SE 0.6). Lineups already hold 3.4 players from one game. | REJECT both |
| 4 | Drop the 3-of-4 exposure cap, except for late games | No cap vs max 3 of 4: +2.9 FP, +2.6 percentile (SE 0.7), cash 45.9% vs 42.5% on 164 slates; +5.8 FP (SE 1.1), 7 of 8 slates, on pre-lock rebuilds; 25 vs 17 cashes of 60 when the backtest lineups are placed in the 15 real contests we hold. Late-game exception (4 for first-tip games, 3 for later): keeps only +0.85 of the +2.90 FP. Scratch risk it insures: 1 dead roster spot in 576 on the pre-lock rebuilds. | ADOPT no cap; REJECT the exception |
| 5 | Ceiling weight 0.25 on lineups 3-4; model-free tail tests | 0.25 on L3-4: -1.2 FP, -1.1 percentile (SE 0.6) for the set; on L3-4 themselves -2.4 FP, share of 360+ scores 11.6% vs 13.1%, modelled top-1% rate +0.9 pts (SE 1.2). Placing lineups in the real contests has no tail power: 0 top-1% finishes in 60 lineup-contests per rule set (0.6 expected at the field's rate). | REJECT 0.25; keep 0.10. ADOPT the 360+ share and %-of-optimal as tail metrics |
| 6 | No ownership penalty on 5+ games; 285% cumulative-ownership cap on small slates; -0.02 x own tie-breaker | 285% cap on 27 four-game slates: +0.2 FP (SE 1.8). On our 2-game slate the top-1% lineups carried 438-446% cumulative ownership. A -0.03 x own penalty was already tested: -0.3 FP (SE 0.7). | REJECT cap and tie-breaker; no ownership terms anywhere |
| 7 | Keep a narrow new-starter swap: trigger on a newly named starter, max 2 swaps, +5.0 gain | 28 real pre-lock lineups walked forward one tip window at a time, overlap rule kept (SE across 7 slates): ruled-out only +0.9 FP; v1.3 rule 17(b) +3.4 (SE 1.7); Gemini's rule +4.0 (SE 2.1); any re-optimisation of unlocked slots that adds 3.5+ projected: +14.8 (SE 7.8), never worse on a slate; unrestricted: +13.4 (SE 7.9), worse on 2 slates; no-information control +4.7 (SE 4.5). Most of the gain is on slates where the pull was 45+ minutes old (+21 vs +6.6 on 15-minute-old pulls). For the unrestricted rule the first two windows hold all of the gain (+13.9 vs +13.4). | ADOPT, wider than proposed: re-optimise unlocked slots before each of the first two later tip windows; upload when a lineup gains 3.5+. Provisional (7 slates); log frozen vs swapped. |
| 8 | Lock-relative pulls and build (T-45/-30/-15/-10, build T-12, upload T-8), placeholders, CSV upload | Consistent with our data (30-minute-fresher pull +6 to +12 FP). Placeholders and CSV upload are already how we enter. | ADOPT: pulls every 15 minutes, final build on a pull no older than 15 minutes at lock. Auto-build on the Mac: later. |
| 9 | Under-filled GPP first; otherwise single-entry / 3-max; no double-ups | $9 $111K Shot was 87-88% full on 11/7 and 11/9: rake 3-5% vs 16%. No data on single-entry or 3-max fields. | ADOPT the under-filled rule and no double-ups; single-entry/3-max NOT YET |
| 10 | Delete the contrarian cap and the sub-$5k team cap | Both removed: +0.6 FP (SE 0.9) with max 3 of 4, +0.8 FP (SE 0.8) with no cap. Sub-$5k cap alone binds on 11 of 164 slates. | ADOPT (no cost, fewer rules to mistype) |
| 11 | 25-slate window; stop if mean percentile < 44 after 15, continue at 25 only if >= 55; paired check vs the pure-LS shadow | Slate-level SD of our mean percentile is 17.2 (SE 4.4 at 15 slates, 3.4 at 25). Draft R6 (one check: stop under 50 after 15) leaves a no-edge system running 51% of the time and stops a true-55 system 13%. Gemini's two-stage rule stops a true-50 system 93%, a true-55 system 49%, a true-60 system 8%. Paired live - pure-LS shadow has SE 5.3 FP at 15 slates: too weak for a hard stop. | ADOPT the two-stage rule. Pure-LS comparison kept as a tripwire for the projection only. |
| 12 | Biggest risk is look-ahead in B77; three diagnostics | (1) done, see Q2. (2) Archive version of the part we can calibrate (starters named after our pull, reverted at observed rates): candidate -1.4 FP (SE 0.5); bound if no late-game new starter were usable: -3.8 FP, about 3 percentile points. Direct measure on 7 slates (final-data build minus pre-lock build): +8 to +9.5 FP (SE 6-7). Rule-set rankings unchanged under both (CAL - LS +10.1 / +8.9; no cap - cap +3.3 / +3.2). (3) No tail power, see Q5. | RIGHT on direction, smaller than feared on AggProj. Stakes stay at $3-$9 until the 25-slate check. |

## Also found
- This season's 14 slates run low in the backtest: candidate 56.0, no cap 58.5, vs 65.5 / 67.8 for the rest of last season (129 slates). 1.8 SE; watch item.
- Best structure tested: CAL, no exposure cap, overlap 6, team cap 3, no contrarian or sub-$5k caps: 316.8 FP, 68.3 percentile, 47.3% cash, 23.3% top-10% (v1.3: 298.9, 52.5, 24.4%, 10.3%).
- Return per $1 excluding the top-0.1% jackpots: average entry 0.52, v1.3 0.49, candidate 0.91, no cap 1.00 (final data); 0.86 / 0.95 after the archive haircut.

## v1.4 draft after this round (ChatGPT round still to come)
R1 one canonical script. R2 CAL projection, ceiling term 0.10. R3 no tiers, no exposure cap, overlap 6 (8 on 3 games or fewer), team cap 3, nothing else.
R4 final build on a pull no older than 15 minutes at lock. R5 re-optimise unlocked slots before the first two later tip windows, upload at +3.5.
R6 grade vs the field; stop under 44 after 15 slates, continue at 25 only at 55+. R7 no double-ups; under-filled $3-$9 GPP first.
R8 shadows: v1.3, pure LS, max-3-of-4 candidate; log frozen vs swapped.
