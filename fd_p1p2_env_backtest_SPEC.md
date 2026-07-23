# fd_p1p2_env_backtest — Spec (v1.5 candidates)

Approved 7/22/26. One script, two tests. Commit output CSVs to backtests/ per MCP wiring pattern.

## Data
- Environment signal: F5 closing totals from `f5_board_census_MASTER_2025mar18-sep13_2026apr01-jul08.jsonl` (2026 portion) + `f5_board_census_EXT_2026jul09-jul21.jsonl` (this delivery, same compact format, 132 games).
  Merge with existing dedup on date+matchup; dh games carry "2" suffix per census convention.
- Consensus total per game = median of book lines; drop thin boards (<4 books) per census conventions; Coors flagged (`coors` in note) for regime split but NOT excluded.
- Outcome variable: per-player FD points from the salary/points archive (same source as fd_v12). Grading of F5 results NOT required for P1/P2 — outcome is FD points, not line grades.
- Window: 2026-04-01 → 2026-07-21. bol dark 7/17–7/18 (5–6 book records those days — still above thin-board floor).
- 404s in extension = postponements/no board: PIT@CLE 7/17, LAD@NYY 7/18, PIT@NYY 7/21, BAL@BOS 7/21. Excluded.

## P1 — game-environment stack selection
Hypothesis: stacking from the slate's highest-total game beats WHIP-only bad-arm targeting.
- Arm A (control): v1.3 rule — 4 bats by season baseline vs slate's worst trailing-WHIP qualified starter. Already computed in fd_v12 runs; recompute over the extended window for apples-to-apples.
- Arm B: highest consensus F5 total on slate; within that game, stack the side facing the worse trailing-WHIP starter; 4 bats by season baseline (bat selection held constant — game selection is the only variable).
- Metrics: mean stack pts (4 slots), P90, disaster rate (stack sum <10), win rate vs same-game random-4, monthly splits, Coors vs non-Coors split.
- Pass criterion (pre-agreed): B beats A on P90 by ≥5 FD pts AND B mean ≥ A mean − 1.
- Deferred: team-implied-total arm (needs full-game h2h, ~13K credits) — only if B passes.

## P2 — both-sides shootout construction
Universe: each slate's highest consensus-total game (report sensitivity at total ≥6.0 threshold too).
- Arms: one-side 4-stack (each side scored separately), 2+2 split, 3+1 split. Bats by season baseline per side.
- Metrics (ceiling-weighted per 7/17 structural-mismatch finding): P90 of block sum, hit rate of block ≥60 pts, mean, variance.
- Pass criterion: split arm beats best one-sided arm on P90 AND ≥60-pt rate, with mean within 3 pts.

## Notes
- All results salary-blind (consistent with v1.2/v1.3); salary/value re-test remains a separate pending item.
- Odds API: 51,965 credits remaining after extension pull (~1,380 spent). Downgrade reminder on the 100K plan stands once P1-deferred h2h pull is decided.
