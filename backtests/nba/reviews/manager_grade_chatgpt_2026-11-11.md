# Manager's grade of ChatGPT's review of NBA FD v1.3 (2026-11-11)

Tests are in `results/b78/` (`cg_field.py`, `gate_cg.py`, `b79.py` and their outputs). Samples are reported separately, as ChatGPT asked:
FINAL-DATA HISTORY = 164 AggProj-era slates on LineStar's final values; PRE-LOCK REPLAYS = 8 dates rebuilt from the last pre-lock snapshot
(exact rank and payout in the slate's primary contest on 6 dates, field-model estimate on 2); PROSPECTIVE = not started.

## Where ChatGPT corrected the manager
- Late swap (Q7). The replay behind "re-optimise at +3.5 gains 15 FP" used final values for each tip window; those are not timestamped, so the
  result is an upper bound, and its no-information control alone moved 4.7 FP (SE 4.5). The wide rule is demoted from live to shadow.
- "After lock" (4.6) should read "after our last snapshot". R5 dropped v1.3 rule 17(b) by wording error.
- Number mismatches (Q12): (a) "mean lineup percentile 47" was weighted by contest entry (20 entries in 5 contests); per lineup in one contest
  per slate it is 50.25. Only the per-slate definition is used from now on. (b) Paired differences were computed on the 156 slates where every
  rule set produced four lineups; the table showed each rule set on its own valid slates (156-164). On the matched 156: structure +5.47 FP and
  cash +9.46 points; candidate vs v1.3 +12.67 percentile, +18.1 cash points.
- Found while reconciling: v1.3 as written cannot produce four lineups on 6 of 15 slates with 11-12 games (none of the four 10-game slates; 2 nine-game slates in the full history) (tiers + contrarian cap + overlap 4
  run out of players). The build script now stops with a clear message instead of failing silently. The v1.4 structure built 164 of 164.

## Verdicts
| Q | ChatGPT | Test | Verdict |
|---|---|---|---|
| 1 | Exact ranks where standings exist; field model only for mean percentile, cash and top-10%; date-held-out calibration; try a shift-invariant SD formula | Date-held-out, entry by entry, dates weighted equally: absolute error 2.1 percentile points (bias +0.5, SE 0.2), 2.4 near the cash line, 2.3 near the top 10%; cash line off by 2.3 FP on average. Shift-invariant formula: -0.01 (SE 0.33), better on 5 of 12 dates, multiplier less stable (CV 0.147 vs 0.118). Field-mean gap is ownership missing from the list (890-900% listed): 0.8 FP or less in 17 of 18 contests after the correction, 2.0 in the other. | ADOPT the rule; alternative formula not adopted |
| 2 | Freeze CAL, LS when AggProj is missing, write the objective explicitly, verify pre-lock availability, deployment gate, split projection revisions from eligibility | AggProj is in every pre-lock pull we hold (88 of 88 players on 11/7). Pre-lock: MAE 8.16 vs 8.45; lineups +11.4 FP (cap 3) / +13.4 (no cap), 6 of 8 dates. Split on 7 dates, no cap: final projections with the pre-lock pool fixed add 7.5 FP for CAL (SE 6.1) and 1.5 for LS (SE 7.4); letting eligibility change too adds 0.9 (SE 0.6). CAL's margin over LS on those dates: 10.8 FP pre-lock, 17.2 on final data, so the final-data margin (+9.6 on 164 slates) is probably overstated. | ADOPT all; gate currently passed |
| 3 | Keep overlap 6 as the baseline; test four-distinct (overlap 8) with no exposure cap | Final-data: -0.2 FP (SE 0.7), all four miss on 30% of slates vs 24%. Pre-lock: -0.3 FP (SE 3.6); exact payouts $152 vs $190 on $180. | AGREED, keep 6 |
| 4 | Drop the exposure cap; capped candidate becomes the shadow | Pre-lock 2x2: exposure +5.8 FP under CAL (SE 1.1, 7 of 8 dates), +3.9 under LS (SE 2.2). | ADOPT |
| 5 | No paid rule on a tail claim; shadow a ceiling weight of 0.2 | Final-data: 0.2 on all lineups -1.2 FP (SE 0.8), share of 360+ scores 12.3% vs 12.7%, modelled top-1% +0.8 pts (SE 0.8). In the exact standings the closest any replayed lineup came to the top-0.1% line was 15 FP (one finish at the 99.3rd percentile in 24 entries). | ADOPT the rule; 0.2 gets no shadow slot |
| 6 | Shadow: on lineups 3-4 take the lowest-owned lineup within 1.0 FP of the best | Final-data: gives up 0.6 FP of objective, cumulative ownership 222% to 198%; actual -0.9 FP on those lineups (SE 1.3), top-10% -1.5 pts (SE 2.3). | REJECT |
| 7 | Out-only repairs mandatory; narrow exception as a shadow; post-lock value cannot be validated from final values | See corrections. | ADOPT: live rule stays as written in v1.3 (ruled-out replacement; one healthy swap for a newly confirmed starter after a teammate is ruled out, +3.5). Archive a snapshot at every later check; score frozen, narrow and wide lineups afterwards. |
| 8 | T-15 snapshot and build, upload verified by T-5, status recheck, later checks 15 minutes before each tip; log timings | Six dates with two pulls 30 minutes apart: the fresher pull is worth +6.1 FP to the v1.4 build (SE 2.7; better on 4, worse on 0) and +4.6 to +10.2 to the other arms (SE 3.7-7.8). | ADOPT |
| 9 | Fee budget first; lowest current effective rake; no format change on entry limits alone; no double-ups; compare same-slate contests | Same slate, same night: Crossover fields ($9, 4-5k entries) average 13-23 FP higher with cash lines 10-15 FP higher; 63-66% of their entries come from users with 100+ entries (38-51% in the Shot and Floater). $3 Floater and $9 Shot fields are within 1-3.5 FP. $9 Shot filled 87-88% on 11/7 and 11/9 (rake 3-5%). | ADOPT, plus: no Crossover |
| 10 | Remove the contrarian cap; hold team cap 3 and cheap-teammate cap 2 pending a four-arm ablation | Final-data, no exposure cap: contrarian off +0.9 FP (SE 0.8). Team cap 4 vs 3: -0.3 FP (SE 0.4), a 4-from-one-team lineup on 45-51% of slates. Cheap-teammate cap off: -0.1 FP (SE 0.2), binds on 14 of 164 slates. | Contrarian cap out; team cap 3 stays; cheap-teammate cap out (no effect). Rules for 2-3 game slates are labelled unvalidated. |
| 11 | One observation per slate in a primary contest named before the build; frozen protocol and N; single final assessment by confidence interval; no early verdict | SD of the slate value: 17-19 on final-data history, 28-30 on the 8 replays. Its formula gives 24-29 slates at 17-19 and 62 at 28. | ADOPT the definitions, N = 30 new slates. Kept from Gemini: one futility stop at 15 slates (mean under 44), which stops a true 60th-percentile system at most 1.3% of the time. At 30: continue at 55 or better; stakes rise only if the lower 95% limit is above 50 and realized return is positive. |
| 12 | Manifest for every run; recorded confirmation before changing a starter flag; three analyses in order | Manifest added to the build script (script version and hash, mode, input files and hashes, snapshot, log date, eligible list, objective, lineups). Analyses 1-3 done above except the prospective trial. | ADOPT |

## Exact payouts (pre-lock replays, primary contest, 6 dates, 24 entries, $180 fees per rule set)
v1.3 $48 (0.27 per $1) · pure LS, no cap $50 (0.28) · CAL, max 3 of 4 $154 (0.86) · CAL, no cap $190 (1.06) · v1.4 structure $190 (1.06).
Development evidence on six slates; not a profit estimate.
