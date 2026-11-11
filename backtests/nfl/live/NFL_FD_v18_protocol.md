# NFL FD v1.8 - IN FORCE from Week 10 (Sun 2026-11-15)
The NFL protocol has no Claude Doc; until one exists THIS FILE is the written record, and `build_live.py` next to it is what runs it.
Written 2026-11-11 from the protocol log (v1.8 ruling of 11/8, constraint list of 11/1) and the Week 8/9 builder code.

- Canonical script: `backtests/nfl/live/build_live.py`, run as-is, never retyped. If it can't be found, the build stops and Phong is told; no rebuild from notes. Full run or notify (Phong, 11/11): every reply that carries lineups opens with the script's result, word for word: PROTOCOL RUN: FULL, or NOT FULL with each missing item, or STOPPED with the reason.
- **Ratified script: build_live.py 2026-11-11a, hash 4fe8cee66680b29c.** A run on any other hash, or on a copy that is not the repo's, is NOT FULL.
- Projection (v1.8, Phong 11/8 "go with your suggestion"): props only. Median main line across books; FD points = 0.04 pass yd + 4 pass TD + 0.1 rush yd + 0.1 rec yd + 0.5 rec + 6 x E[TD]; E[TD] = -ln(1 - p), p = median anytime-TD implied probability x 0.92; QB -0.6. D-ST = (30 - opponent implied total, floor 2) x 0.55. LineStar is out of the projection (ownership file logged only).
- 3 QBs x 5 = 15 lineups.
- C1 QB + 2 or 3 of his own WR/TE in every lineup.
- C2 no RB from the QB's team; max 1 RB per game. (C2-amended, a pass-catching RB with his own QB, is a shadow only.)
- C3 FLEX = RB; RB x3 salary 20,000+; salary 59,500-60,000.
- C4 no D-ST against our own offensive players; players at 4,500 or less only from the QB's game; WR/TE salary floor 4,500.
- C5 no unpriced players (a TD-only price does not count); role gate on stack and bring-back WR/TE (WOPR 0.30+ or target share 0.18+ over the last 2 games); RB gate 35%+ of team carries over the last 2 games.
- C6 overlap <= 5; exposure <= 7 of 15 (QB and D-ST exempt); non-stack pair <= 6; lineups 2-5 of a QB keep a stack partner of lineup 1, change the D-ST, keep at most 2 of lineup 1's RBs.
- C7 QB pick: salary 6,800-8,300; score = team implied total + 0.4 x game total - 1.5 x max(0, salary - 7,600)/1,000; top 3, one per game.
- Shadows every week, saved in the manifest before lock: v1.6 (props + salary formula 50/50) and C2-amended.
- Kill switch: back to v1.6 after 3 slates if 9 or fewer of 45 cash or the median lineup is below the field's 45th percentile; after 5 if 15 or fewer of 75 or the average median is below the 40th. Slate 1 = Week 10.
- Watch item, not a rule: D-ST exposure above 5 of 15 (the script prints it).

## Differences from the Week 9 code that Phong should know
1. The Week 9 builder dropped skill players whose LineStar projection was 0.5 or less. v1.8 takes LineStar out, so this script does not use that filter; a player the books still price stays eligible unless FanDuel tags him O / IR / NA / D.
2. Replacement-RB exceptions to the 35% carry gate were typed in by hand each week. The script has no such list; a back who needs the exception is a NOT-covered item to raise before the build.
3. When no legal lineup exists the script tries the two Week 9 relaxations and reports them as NOT FULL items needing Phong's OK.
