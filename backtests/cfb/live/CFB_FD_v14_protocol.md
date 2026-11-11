# CFB FD v1.4 - IN FORCE from the 11/7 slate
Copy of section 17 of the protocol doc plus the earlier rules it leaves in force, as the script runs them. The doc is the record.

- Canonical script: `backtests/cfb/live/build_live.py`, run as-is, never retyped. If it can't be found, the build stops and Phong is told; no rebuild from notes. Full run or notify (Phong, 11/11): every reply that carries lineups opens with the script's result, word for word: PROTOCOL RUN: FULL, or NOT FULL with each missing item, or STOPPED with the reason. Ratified script: build_live.py 2026-11-11a, hash 2a38d1446c3c6476; a run on any other hash, or on a copy that is not the repo's, is NOT FULL.
- P1: projection = 100% LineStar. Props hybrid is a shadow only (method not yet documented; not built by the script).
- Eligibility (F1, F3, F4, F5): not tagged O, Q or D on the FanDuel list and not out on LineStar; more than 2 games played; LineStar projection 10+ for a QB, 6+ for anyone else.
- F2: QB gate. A posted passing line is supporting evidence only; a QB clears with last-start support plus a complete legal same-window pivot. Unresolved at build = ineligible. The cleared QBs are passed to the script by name.
- C1: SuperFLEX = second QB, mandatory (Phong's call). Second QB chosen by the best complete legal lineup. The best 1-QB lineup and the free-choice lineup are printed as shadows.
- C2: every rostered QB needs one of his own WR/TE projected 8+.
- C3: max 3 per team, 4 when that team's QB is rostered. C8: max 1 RB per team.
- C4: salary $58,500 to $60,000.
- C5: 4 lineups (from 11/7). Any two share at most 5 of 7. A player is in at most 3 of 4, except at most 2 core players named before lock.
- C7: a player ruled out is replaced without the +2.0 FP gate; discretionary swaps need +2.0 on the full lineup.
- B1: 1% of the DFS bankroll per slate is a ceiling; contest type and fees are Phong's call.
- N1/N2: hard failures = no LineStar file, no injury tags, or an unresolved QB gate for a rostered QB at lock.
- Process: the 8:30 AM pull is the build snapshot; every grade prints live + shadow scores against the real cash line.
