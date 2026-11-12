# Contradictions and gaps in the NFL protocol text (as of 2026-11-11)

Found by reading the four tabs and the change log end to end. Severity: HIGH = a chat reading the tab can run a different rule;
MED = ambiguous; LOW = stale wording.

## Status after the 11/11/2026 review

Each item now has one reading in `RULES_CURRENT.md` and a "read this first" block at the top of both NFL tabs (plus NFL addenda in the
Game-flow and Robinhood tabs). No existing sentence in the doc was reworded or deleted, so the old text is still there underneath;
the blocks say which parts are dead. Readings marked [R] in the rule list are Phong's to overrule.

| Item | Status | Reading (rule ID) |
|---|---|---|
| X-01 | Fixed by banner | The v0.2 code blocks are history. Dead parts are listed in the banner. One flat list: `RULES_CURRENT.md` |
| X-02 | Fixed going forward | `VERSION_BY_DATE.md` separates the rule sets by date. The checker now prints the rules-text date next to the version label |
| X-03 | Done | `REVIEW_2026-11-11.md` is the data-driven review the freeze called for |
| X-04 | Fixed | Policy rules written into the banner and the rule list (M-01 to M-05) |
| X-05 | Resolved | Robinhood is an execution venue, 10/17 (R-05) |
| X-06 | Resolved | Same; v0.6a's "DSB-only" wording is superseded (R-05) |
| X-07 | Resolved [R] | Ask + 2 cents vs fair at the same strike; a fire needs 3.0 points; "ask <= fair" is the minimum for any ticket (R-06) |
| X-08 | Fixed [FIX] | NFL uses the one-sided table B-NFL-3. 11.5 / 15.3 / 5.7 are CFB figures (R-07) |
| X-09 | Fixed [FIX] | Same table replaces both off-strike shift rules for NFL spreads; totals stay 1.5 per half-point (R-07) |
| X-10 | Resolved [R] | Better-EV venue first; exact tie to DSB (R-09) |
| X-11 | Resolved [R] | Engine-tab key numbers govern NFL (R-08) |
| X-12 | Dead text | DSB overtime veto retired 10/4 (H-03) |
| X-13 | Dead text | Anchor Mode is shadow-only (H-21) |
| X-14 | Resolved [R] | The 3Q kickoff is the only hard stop; Q3 -4 retired by the 10/17 text (H-34) |
| X-15 | Dead text | G-12 |
| X-16 | Resolved | FLOW skip retired 11/9 (F-06, G-07) |
| X-17 | Resolved [R] | Sweep all; FLOW every game; full runs on FLAGGED only; inactives for every game; STATIC re-swept on a 1-point move or a starter change (F-15 to F-18) |
| X-18 | Resolved [R] | Four full runs per window stands (F-16) |
| X-19 | Noted | Label stays "v1.1"; the rule list names it "v1.1 with CLEAR LEAN v1.0 and ALWAYS PULL FLOW" |
| X-20 | Resolved [R] | The CLEAR LEAN list is the monitored list (F-21a) |
| X-21 | Resolved [R] | Direct gap defined: 3.0 points over break-even at the same number, EV > 0, gates and divergence apply (F-28) |
| X-22 | Resolved [R] | 1.5-point gap opens the evaluation; the fire needs 3.0 points priced at DSB's number (H-19) |
| X-23 | Resolved | v0.5 governs: Overs after a 45+ first half are shadow-only (H-25) |
| X-24 | Resolved [R] | Kill switches retired by Liem L3.3; NFL line 17u = $5,100 (M-04) |
| X-25 | Resolved [R] | Two aligned inputs with no hard counter print the lean (G-10). Paper side for filtered games still undefined (G-11, review decision 3) |
| X-26 | Superseded | `LEDGER_REBUILT.md`: 1H leans 18-11-1 since 10/11 |
| X-27 | Superseded | `LEDGER_REBUILT.md`: 2H leans 19-17-1 since 10/11 |

Found in the review, not in the list below:
- X-28 HIGH, fixed. The push table (B-NFL-2) counts either team landing on the number. The boards used it as the push probability of a line, which is the one-sided figure and about half as large. See `PUSH_TABLE_B-NFL-3.md`.
- X-29 MED, open. Nothing in the text says a lean bet with live money has to be at a fair price. First-half leans closed 1.0 point worse than fair on average (review decision 2).
- X-32 MED, fixed 11/12. Red105 has been a venue since 10/25 on Phong's word ("I have another platform to use along with dsb. Red105.") but no doc tab named it. Written into the rule list (F-02, H-02, M-03) and the 2H tab's v0.6b section.
- X-33, ruled 11/12. Profile in force: `current`.
- X-31 MED, open. Robinhood 2H contracts are regulation-only; the 10/17 text says "convert before comparing" with no method. Reading until one is written: shadow (H-02).
- X-30 MED, resolved [R]. Robinhood contract count: "contracts = size / ask" treats size as dollars risked, while the unit is $300 to win (R-10).

## The list as found (2026-11-11, before the review)

## Structure
- X-01 HIGH. Both NFL tabs are still titled "analyst protocol v0.2" and open with the v0.2 paste-ready code block. Every later version is an amendment stacked underneath. The code block still states rules that were later superseded: $50K bankroll and 0.5u = $250; Robinhood co-primary; the 70% public-ticket caution; 1H total = 0.485 x full; "QB1 confirmed active"; 2H "under 3 minutes -> shadow only"; the DSB overtime veto; "lead 17+ -> 2H total under only"; the "pregame close minus 1H result" anchor; Anchor Mode fires at 0.25u. A chat that stops at the code block runs v0.2.
- X-02 HIGH. One version label covers different rule sets. "v0.6" (10/15) changed twice on 10/17 (time locks, Robinhood) with no version bump. Results logged as "v0.6" before and after 10/17 are not the same protocol.
- X-03 MED. The freeze said: no rule edits until each engine has 20 boards graded, then one data-driven review. Seven changes followed and no 20-board review has been run.
- X-04 MED. Betting-policy rules live only in memory notes, not in the doc: "$300" = $300 to win; bet only fires and leans; DISC / DISC-UP with a 2u cap declared before the price; one parlay per slate. A chat that reads only the doc does not have them.

## Robinhood
- X-05 HIGH. Venue status flipped three times: co-primary (v0.2, RH tab) -> reference-only (v0.4) -> execution venue (10/17). The RH venue tab was never edited for either flip and still says "co-primary".
- X-06 HIGH. NFL 2H v0.6a "Scope" says "the DSB-only execution venue (RH for reference and when its price favours)" - it contradicts itself and the 10/17 addendum in the same tab.
- X-07 HIGH. Two different RH price tests: RH tab section 3 "ask <= fair no-vig probability" vs 10/17 "ask + 2 cents fee vs fair" clearing "the engine's threshold". Which threshold (3.0 points?) is not stated.
- X-08 HIGH. Two different push tables for the same market. RH tab off-strike rule (10/17): "CFB/NFL 1H: 3 = 11.5%, 7 = 15.3%, tie 5.7%". NFL 1H tab (B-NFL-2): 3 = 15.7%, 7 = 14.2%, tie = 8.3%.
- X-09 MED. Two off-strike shift rules in the RH tab: section 3 "2.5 cents per half-point on spreads (5 crossing 3 or 7), 2 cents on totals" vs the 10/17 section "2.0 points per half-point on spreads, 1.5 on totals".
- X-10 MED. Venue tie-break: RH tab "Tie -> DSB" vs 10/17 "name the better-EV venue first".
- X-11 LOW. RH tab key numbers "3, 7, 10, 14" vs engine tabs (1H 3/7; 2H 3/7).
- X-12 LOW. RH tab section 4 still describes the DSB overtime veto, retired 10/4 (the retirement is recorded lower in the same tab).
- X-13 LOW. RH tab section 3 "Anchor Mode ... 0.25u where the engine fires in Anchor Mode" - Anchor Mode is shadow-only since 2H v0.5.

## Time locks
- X-14 HIGH. NFL 2H: v0.5 keeps "Q3 -4 is the hard lock (ruled)" and "tickets by T+7". The 10/17 addendum retires the under-3-minutes rule and the 4-minute UNPOSTED rule and says the 3Q kickoff is the only hard stop, but never mentions Q3 -4. v0.6a (11/1) then says "the Q3 lock [is] unchanged". Whether Q3 -4 is in force is undecided in the text.
- X-15 LOW. Game-flow tab section 1 (2H row) and section 3 still cite "the <3-min rule" and the "DSB-OT veto" as live.

## FLOW
- X-16 MED. "FLOW SKIPPED - TIME PRIORITY": allowed by Game-flow 6.7 and the 1H tab's v0.3 section ("Fallback = skip and say so"); retired by ALWAYS PULL FLOW (11/9). The older sentences are still in both tabs.
- X-17 MED. 1H v0.5 dynamic triage: a lightweight screen on every game every pull, and T-85 inactives for EVERY game. 11/1 slate workflow: STATIC games "get no further work this run". 11/9: FLOW for every game including STATIC. Three different treatments of STATIC games in one tab.
- X-18 MED. Deep-review cap: v0.5 "cap stays four" per window. 11/1 workflow has no cap on FLAGGED games (six were flagged on 11/1).
- X-19 LOW. Game-flow tab is still labelled v1.1 although CLEAR LEAN (10/15) and ALWAYS PULL FLOW (11/9) were appended to it.
- X-20 LOW. Monitored personnel lists differ: v0.5 (QB1, OTs, C, CB1); CLEAR LEAN (adds S1, WR1); 11/1 workflow (QB / OL / WR1).

## Fire classes and thresholds
- X-21 HIGH. 1H "3.0 floor". The slate workflow and every board refer to "the 3.0 floor", but in the 1H tab 3.0 points is defined only inside HOOK and DERIV-LAG. A plain direct price gap as a fire class comes from v0.2 ("3 cents or more") and v0.4 calls the gap "a benchmark". The 11/2 CHI +2.5 1H fire ("+4.0 direct gap") rests on this unstated rule.
- X-22 MED. 2H direct gap: v0.4 says "DSB 1.5+ pts better than the leave-out median"; boards apply "3.0 points of edge" at the same number.
- X-23 MED. 2H Over after a 45+ first half: v0.2 "needs a 2 pt gap", v0.4 "+2.0", v0.5 "shadow-only until the hurdle is defined". Three texts in one tab.
- X-24 MED. Kill switches (1H/FG: 0-3 -> shadow, checkpoints at 5 and 10; 2H: its own 0-3) appear only in v0.2 and are never restated or retired. v0.4 says "the per-sport drawdown line [is] untouched" (Liem). Which governs is not stated. Engine ledgers today: 1H 1-0; 2H DSB-only 0-0 with one ungraded fire.
- X-25 LOW. CLEAR LEAN text: a hard counter "kills the lean even at 2-of-3", but "two soft aligned inputs" is undefined - the cause of the 11/8 zero-lean slate (open item A).

## Ledger
- X-26 HIGH. The 1H lean record is carried as 15-5 since 10/11. The itemised entries add up to 14-5 (see AUDIT_2026.md). One win in the headline has no logged entry behind it; the miscount enters at the 11/1 line "13-4" (items give 12-4).
- X-27 MED. The 2H-SHADOW headline "21-13" is stale: #39, #41 and #42 were graded wins after it was written (24-13 graded), and #34 to #38 are still ungraded.
