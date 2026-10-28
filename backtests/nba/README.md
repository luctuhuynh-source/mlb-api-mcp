# NBA FanDuel backtest base

## Player game logs (hoopR / ESPN box scores)
- nba_player_games_2024-25.csv, 2025-26.csv, 2026-27.csv — one row per player-game, regular season only.
- Columns include minutes, starter, did_not_play, reason, box stats, fd_pts (FanDuel scoring: 1 pt, 1.2 reb, 1.5 ast, 3 stl, 3 blk, -1 TO), fd_per_min.
- Refresh: `python3 backtests/nba/nba_pull_gamelogs.py` (source updates nightly).

## standings/ — full-field FanDuel contest standings (realized ownership + actual FD pts)
Downloaded by Phong from FanDuel History -> entry -> contest -> CSV Download.
Columns: Rank, EntryId, EntryName, Points, Lineup, (blank), Player, Roster Position, %Drafted, FPTS, Salary.
Our entries: username dalatcrew.
| file | slate | notes |
|---|---|---|
| 2026-10-20_135251_600K-opening-night.csv | 135251 | own build 313.9, top 7% |
| 2026-10-21_135636_clutch-shot.csv | 135636 | v1.0 shadow |
| 2026-10-21_135636_floater.csv | 135636 | v1.0 shadow |
| 2026-10-22_135658.csv | 135658 | own build 262.6 |
| 2026-10-23_135732.csv | 135732 | v1.1, 4 entries |
| 135772_slate-reviewed-2026-10-26.csv | 135772 | own build 292.0 |

## Player pools and submitted lineups
- YYYY-MM-DD_pool*.csv — FanDuel player-list export (salaries, positions, injury flags) at build time.
- YYYY-MM-DD_lineups*.csv — lineups we built/submitted that day.

## Still missing (step 3 of the plan)
- Historical FD salaries + realized ownership for slates we did not enter (RotoGuru / LineStar) — blocked from this sandbox, to be sourced separately.
