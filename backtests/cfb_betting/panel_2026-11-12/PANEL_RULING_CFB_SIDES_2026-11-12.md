# Panel ruling: college football sides (CFB 1H v2.0e, CFB 2H v2.3b) - 2026-11-12, about 7:00 AM

Panel: Gemini = scout, ChatGPT = doubter, Claude = manager. Ordered by Phong by voice ("write a detailed summaries of what we currently have ... a command prompt so that way ChatGPT and Gemini can help us examine our protocol ... then after that, maybe we can run a back test on the new finding ... let's just do this with the side only"), typed "Cfb review" 5:27 AM, replies posted 6:17 AM ("Here are their responses"). Packet: `../CFB_SIDES_SUMMARY_2026-11-12.md`. Prompts and replies as received: this folder. Locked test plan: `../backtest_2026-11-12/CFB_SIDES_TEST_PLAN_LOCKED.md`.

## 1. Bottom line
- **The doubter's central point stands: nothing in the college side protocols is a demonstrated edge.** The engine is a sound idea that almost never fires; the lean has no proven edge; the two best-looking numbers (58-33, 17-6) were chosen after the fact from two Saturdays.
- **One finding is an arithmetic error in a rule in force.** The first-half HOOK rule (live since v2.0b) converts with the table "3 = 11.5%, 7 = 15.3%", which counts either team winning by that margin. A team laying 3 pushes only when IT wins by exactly 3. The NFL rules had the same error until 11/11. Any college HOOK fire today overstates its edge by roughly a factor of two. A one-sided table is being measured (free); until Phong rules, a HOOK fire should be treated as unproven.
- **One finding is a logical consequence of this morning's change.** With "bet a lean only at the fair or better", a bettable lean at a venue already has the price on its side, so CLEAR LEAN's "2 of 3" is met by ONE of personnel or FLOW. The rule now reads: a good price plus one handicapping signal.
- **The scout's useful contributions:** success rate is the published standard for half-to-half stability (yards per play is not); fumble recoveries are luck; the literature gives no support for a home-team second-half edge. Its resting-order idea was tested on NFL tonight and found no support (9% filled, 15-23).
- **The backtest queued on 11/6 as B-CFB-7 is run now**, with three claims fixed first.

## 2. The doubter's findings
| # | Finding | Ruling |
|---|---|---|
| 1 | The 3.0-point trigger is a hurdle, not evidence; a no-vig median of books that copy each other is an estimate, not a fair; four books needed in 1H but two in 2H | Accepted. The asymmetry stays for now: fewer books post second-half lines. "EV above zero" is redundant once cost is in the test (wording, MINOR) |
| 2 | HOOK: FATAL if the table is applied as a universal adjustment (signed or absolute? conditioned on the line?) | **Accepted and confirmed from the tab's own text**: the table is P(absolute halftime margin = k). See section 1 |
| 3 | Histories cannot certify "30 seconds old, fillable for the full stake" | Accepted. Every result of the test is a displayed-price result, and says so |
| 4 | CLEAR LEAN: with the price gate, two of three collapses; "priced at or above fair" is ambiguous; PERSONNEL and FLOW are not reproducible classifiers; hard counters are unvalidated cut-offs | Accepted. Wording fix proposed (section 5). For the test a classifier is frozen from the written definition |
| 5-6 | What each record can support; 58-33 and 17-6 are screens; reconcile 23-19 with 17-6 | Accepted. Reconciled from the change log: 10/17 was 3-8; 10/24 + 10/31 unfiltered 20-11, of which lead under 21 was 17-6 and lead 21+ was 3-5. So the "under 21" filter was added after the results were seen |
| 7 | NFL carry-over: price discipline is portable, the edge is not; 68 games against 75 bets; with a 2-cent fee and the -115 cap a Robinhood lean needs an ask of 51 cents or less | Accepted. 75 entries in 68 games is right (both sides and both markets can qualify). The 51-cent arithmetic is right and is now noted |
| 8 | Step 0 pulls every game's drives before a candidate exists; the pre-ticket re-pull comes before the news check and can go stale; the 28-point branch and the 0-3 switch | Partly accepted. FLOW on every game is Phong's standing rule and stays. The re-pull should be the LAST step (wording, proposed). The kill switch is a loss limit, not a test, and is his |
| 9-11 | The test: three frozen claims, first eligible observation, block-bootstrap bar, 42,000 credits | Accepted in structure, changed in cost and scope: section 4 |
| 12 | Severity list | Accepted |

## 3. The scout's findings
- **Taken into the test:** success rate against yards per play (finding 7, claim S); fumbles as luck (finding 8, information split); home team second half and FLOW under 21 need an out-of-sample test (11, 12); who receives the third-quarter kickoff (13, information); how the market sets the second-half spread (6, information).
- **Agreed, no test needed:** same-number 3-point prices almost never exist pregame (2), which is our own 91-game result; sharp books lead and the archive does not carry them (5).
- **Not adopted:** resting orders on Robinhood (new idea 1): tested on NFL tonight, no support. Dropping the same-number restriction (drop 2): spreads already convert, but the college table is wrong-sided and must be fixed first; totals stay same-number by Phong's decision this morning. Altitude and look-ahead ideas (15, new 5 and 6): weak sources, one to three games a Saturday.
- **Proposed to Phong, his call:** drop the optional previous-game FLOW read from first-half leans (drop 1). Our own 1H leans beat the close 2 times in 13.
- **Not verified:** the regression-discontinuity football study and its figures; "MathWizardShoe"; the Kalshi maker-fee discount as it applies to a Robinhood customer (Robinhood's own fee page, read tonight, makes no such distinction).

## 4. The test: what was kept and what was changed
- **Kept:** at most three claims, written before any price is pulled; one fixed observation time per game; no new claim after results; FBS-against-FCS shown apart; neutral sites out of the home claim; personnel is not reconstructable, so these are priced feature screens and not replays of CLEAR LEAN; the doubter's block-bootstrap bar is computed and reported.
- **Changed: cost.** One look per game (last first-half play + 10 minutes), second-half spreads only: about 6,700 credits instead of 42,000.
- **Changed: claim A.** "Does Robinhood ever show a qualifying college price" needs the exchange's college event list and is left for a separate free pull. Its place goes to the scout's best-supported idea (claim S).
- **Changed: price basis.** Claims are graded at the books' own numbers and prices on every game (the same basis as the NFL work). Grading at the fair price is shown beside it. Robinhood-gated grading waits for the Robinhood pull.
- **The original classifier's code is gone** (session files of 11/6). The FLOW side is rebuilt from its written definition on a different play-by-play source. On the two discovery Saturdays it names 28 games where the replay had 23. The doubter's condition (exact classifier or leave the claim unused) is therefore only partly met; the reproduction check is printed, and the verdict uses only games outside those two Saturdays.

## 5. Proposed to Phong (nothing changes without his word)
1. **HOOK:** shadow until a one-sided college push table is adopted.
2. **CLEAR LEAN wording:** say plainly that a bettable lean = the fair or better at the venue being bet + one of personnel or FLOW + no hard counter; replace "priced at or above fair" with "the venue's price costs no more than the fair".
3. **Pre-ticket order:** news check first, price re-pull last.
4. **1H FLOW:** drop the optional previous-game read from first-half leans.
