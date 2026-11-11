# NBA FD v1.4 - IN FORCE from 2026-11-11 (first slate: Wed 11/11)
Copy of the v1.4 section of the protocol doc. The doc is the record; `build_live.py` in this folder is what runs it.

v1.4 is the first version graded against the contest field instead of on fantasy points. A field-relative backtest (B77-B79, 164 slates) put v1.3 at the 52nd percentile with 24.4% cash, against 24.5% by chance; pre-lock replays of 8 live slates put it at the 42nd. Three causes are fixed here: the last-5 blend, the ownership tiers with overlap 4, and builds that were stale or retyped. v1.4 replaces v1.3 in full: a rule from an earlier version is in force only if it is restated below.

Ratified by Phong 11/11 ("Write v1.4"). Sources: the 11/10 review packet, the Gemini and ChatGPT reviews of 11/11 and the manager's grades, in `../reviews/`. Ledger: v1.3 ran 3 slates (11/7, 11/9, 11/10): 20 entries, 3 cashes, -$77.

## A. Process and data
1. One canonical script builds every live set: `backtests/nba/live/build_live.py`, run as-is, never retyped. If the script can't be found, the build stops and Phong is told; no rebuild from notes. Each run writes a manifest: script version and hash, mode, input files and hashes, snapshot, game-log date, eligible list, objective, lineups and the run-check result. Full run or notify (Phong, 11/11): the script ends every run with a run check, and every reply that carries lineups opens with its result, word for word: PROTOCOL RUN: FULL, or NOT FULL with each missing item, or STOPPED with the reason. The ratified script is build_live.py 2026-11-11f, hash 946a997b4aa3d633; a run on any other hash, or on a copy that is not the repo's, is NOT FULL. The check covers the build through the upload file; it does not cover the recheck before lock, late swap, contest choice by rake or grading.
2. One synchronized refresh before any build, never partial: starting lineups (RotoWire), injury report, LineStar projections with AggProj and projected ownership, and the game logs. A pull with 15 or fewer projected players means an expired cookie; flag it at the top of the build.
3. Timing runs off the slate's actual lock T: refresh and build at T-15, upload confirmed by T-5, status of every rostered player rechecked before lock. The standing pulls (3:15 and 3:45 PM PT; Saturday 2:15 and 2:45) serve a lock 15 minutes after the second pull; any other lock needs its own pull.
4. A listed starter with a zero projection triggers a status review. A starter flag changes only on recorded confirmation (the starters list passed to the script). Newly confirmed starters are eligible regardless of recent minutes.
5. If the live set cannot produce four lineups, the script stops and writes nothing, and that is reported at the top of the reply. A team with 8 or fewer healthy players is flagged at the top of the build for a manual look.

## B. Projection
6. P = -0.26 + 0.14 x LineStar + 0.86 x AggProj (exact weights 0.136 and 0.856, frozen). For a player with no AggProj, LineStar's number takes its place.
7. Objective U = P + 0.1 x (LineStar ceiling - LineStar projection).
8. Standing gate: if P loses to pure LineStar on both pre-lock player error and pre-lock lineup FP over the accumulated snapshots, paid builds revert to pure LineStar on the same structure. Checked every 10 slates. Status 11/11: passed (error 8.16 vs 8.45 on 742 pre-lock player rows; +11 to +13 FP per lineup on 8 slates, SE 8-9).
9. The last-5 blend, the engine projection and every ownership adjustment are out of the live projection. Projected ownership is still reconciled to 900% for reporting.

## C. Eligibility
10. Not tagged Out, Doubtful or Questionable on the FanDuel list or the injury report at the build; LineStar projection above 0; and listed starter, or 18+ minutes averaged over the last 3 games. v1.3's text said "not Out/Doubtful", but every v1.3 build also excluded Questionable; v1.4 writes down what is run and was tested.

## D. Construction
11. Four lineups built in sequence on U. Any two share at most 6 of 9 players (8 of 9 on slates of 3 games or fewer; untested).
12. Max 3 players per team. Salary cap $60,000, no spend floor.
13. Dropped: the ownership tiers, the no-4-of-4 exposure rule, the contrarian cap, the 2-under-$5k team limit and every ownership term. A player may be in all four lineups.
14. Slot placement: players in the earliest games take the base position slots; the latest games take UTIL, then G/F and F/C, so locked players leave the flexible slots open for late swap.

## E. Late swap
15. Compare whole lineups under one data snapshot, never a fresh candidate against a stale incumbent.
16. Mandatory: replace a rostered player who is ruled out before his game tips.
17. One healthy-player swap per lineup is allowed when a newly confirmed starter follows a newly ruled-out teammate, both players are unlocked, and the full-lineup projection rises 3.5 or more. Never two healthy players.
18. Checks 15 minutes before each later tip, when a snapshot exists for it. Each check's snapshot is archived; the frozen, rule-17 and full re-optimisation lineups are all scored afterwards as shadows.

## F. Contests and sizing
19. Four lineups per slate: a primary GPP named before the build, plus at most one secondary GPP, at Phong's chosen fees (D21, D23). The slate fee budget is fixed before contests are chosen and is not raised for overlay.
20. DROPPED by Phong 11/11 ("Drop rule 20"). Was: no double-ups, no Crossover contests. One set of four lineups now fills every contest entered on the slate. The finding stays on record: on 2 slates Crossover fields averaged 13-23 FP higher and the cash line sat 10-15 FP higher.
21. Among the $3-$9 GPPs, lowest current effective rake first: 1 - guaranteed prizes / (current entries x fee).

## G. Grading and stop rule
22. Slate value Y = mean exact percentile of the four lineups in the primary contest. Also logged per slate: fee-weighted net return, cashes and top-10% finishes. Field-model numbers are labelled estimated and never used for top-1%, top-0.1% or return.
23. Trial: 30 new slates on the frozen protocol, starting 11/11. Stop at 15 slates if mean Y is under 44. At 30, continue only at 55 or better. No stake increase unless the lower 95% limit is above 50 and realized return is positive.
24. Final-data history, pre-lock replays and prospective results are reported as three separate samples.

## H. Shadows (logged every slate, never entered)
- v1.3 as written.
- Pure LineStar on the v1.4 structure.
- The v1.4 projection with max 3 of 4 exposure.
- Late-swap variants under rule 18.

## No longer in force
Earlier rules the build script does not run and no test supports are retired with v1.4: the engine's minutes, rate, pace and matchup rules; the core-candidate screen; star pairing; the starter-plus-backup ban; the team cap of 4 on small slates; the Questionable slot rule; and the depleted-team rule, which is now only the flag in rule 5.

## Rejected in the v1.4 round (all tested)
- Field-SD regression and a shift-invariant SD formula: no better on held-out dates.
- Overlap 7 or 8 (four distinct lineups): no gain, and all four miss on 30-32% of slates against 24-25%.
- Game stacks on lineups 2-4: -0.3 to -0.9 FP.
- Late-game exposure exception (cap 3 for later tips): keeps 0.85 of the 2.90 FP.
- Ceiling weight 0.2 on all lineups, or 0.25 on lineups 3-4: -1.2 FP, no tail gain.
- 285% cumulative-ownership cap, ownership penalty and lowest-ownership tie-break: no effect or negative.
- Team cap 4: -0.3 FP.
- Single-entry and 3-max routing: no data.
- Re-optimising every unlocked slot at each tip as the live rule: the replay gain is an upper bound, so it runs as a shadow.

## Watch items
- This season's backtest level is the 56th-58th percentile on 14 slates, against the 65th-68th last season.
- The projection's margin over LineStar is 10.8 FP before lock and 17.2 on final data on the same 7 slates, so the 164-slate margin is probably overstated.
- The Questionable exclusion: eligibility changes after the snapshot were worth 0.9 FP.
- Rules for 2-3 game slates are untested.
- v1.3's rules could not build four lineups on 6 of 15 slates with 11-12 games.

## Backtest record (v1.4)
The 164-slate rows use LineStar's final values and are optimistic by 1-10 FP per lineup; the replay rows use only the last pre-lock snapshot.

| ID | Date | What | Result |
|---|---|---|---|
| B77 | 11/10 | Field-relative backtest: 237 slates, 164 in the AggProj era | v1.3 52.5 percentile, 24.4% cash (chance 50, 24.5%); new projection with max 3 of 4 and overlap 6: 65.0, 42.5% |
| B78 | 11/11 | Gemini round, 164 slates: exposure, dead caps, ceiling, game stack, ownership cap, late-starter haircut | no exposure cap +2.9 FP (SE 0.7); nothing else gained; haircut 1.0-1.4 FP |
| B79 | 11/11 | ChatGPT round, 164 slates: team cap, cheap-teammate cap, contrarian cap, ceiling 0.2, tie-break, overlap 8 | contrarian cap off +0.9 FP (SE 0.8); the rest within 0.5 FP or negative; v1.4 structure 316.8 FP, 68.3 percentile, 47.3% cash, 23.3% top-10% |
| Pre-lock gate | 11/11 | AggProj vs LineStar on 742 pre-lock player rows, 7 slates | error 8.21 vs 8.45; AggProj moves less than LineStar after the pull |
| Pre-lock replays | 11/11 | 8 live slates rebuilt from the last pre-lock snapshot; exact standings on 6 | v1.4: 317.0 FP, 61st percentile, 13 of 32 cashes, $190 back on $180. v1.3: 295.8, 42nd, 5 of 32, $48 |
| Field model | 11/11 | 18 real contests, each date held out | absolute error 2.1 percentile points; cash line off 2.3 FP |
| Late-swap replay | 11/11 | 28 pre-lock lineups walked forward one tip window at a time | out-only +0.9 FP; rule 17 +3.4 (SE 1.7); full re-optimisation at +3.5: +14.8 (SE 7.8) against a no-information control of +4.7. Upper bounds |
