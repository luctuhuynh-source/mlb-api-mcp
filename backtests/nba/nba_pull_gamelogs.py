#!/usr/bin/env python3
"""
NBA FanDuel backtest base — step 1: player game logs with FanDuel points.
Source: hoopR-nba-data (ESPN box scores, updated nightly) on GitHub — stats.nba.com blocks us.
Run anywhere with internet:
    cd ~/mlb-api-mcp && python3 backtests/nba/nba_pull_gamelogs.py
Output: backtests/nba/nba_player_games_<season>.csv  (one row per player-game, regular season)
FanDuel scoring: PTS 1, REB 1.2, AST 1.5, STL 3, BLK 3, TOV -1.
"""
import os, sys, io, urllib.request
import pandas as pd, numpy as np
try: import pyarrow  # noqa
except ImportError: sys.exit("pip3 install pyarrow pandas   (then rerun)")
OUT=os.path.dirname(os.path.abspath(__file__))
SEASONS={2025:'2024-25',2026:'2025-26',2027:'2026-27'}
URL="https://raw.githubusercontent.com/sportsdataverse/hoopR-nba-data/main/nba/player_box/parquet/player_box_{y}.parquet"
for y,season in SEASONS.items():
    try: raw=urllib.request.urlopen(URL.format(y=y),timeout=120).read()
    except Exception as e: print(season,"download failed:",e); continue
    df=pd.read_parquet(io.BytesIO(raw)); df=df[df['season_type']==2]
    for c in ['minutes','points','rebounds','assists','steals','blocks','turnovers']: df[c]=pd.to_numeric(df[c],errors='coerce').fillna(0)
    df['fd_pts']=(df.points+1.2*df.rebounds+1.5*df.assists+3*df.steals+3*df.blocks-df.turnovers).round(1)
    df['fd_per_min']=np.where(df.minutes>0, df.fd_pts/df.minutes.replace(0,np.nan), np.nan).round(3)
    keep=['season','game_id','game_date','athlete_id','athlete_display_name','athlete_position_abbreviation','team_abbreviation','opponent_team_abbreviation','home_away','starter','did_not_play','reason','minutes','points','rebounds','assists','steals','blocks','turnovers','field_goals_attempted','free_throws_attempted','plus_minus','team_score','opponent_team_score','fd_pts','fd_per_min']
    out=df[keep].sort_values(['game_date','team_abbreviation','athlete_display_name'])
    path=os.path.join(OUT,f'nba_player_games_{season}.csv'); out.to_csv(path,index=False)
    print(f"{season}: {len(out):,} rows, {out.game_id.nunique():,} games, through {out.game_date.max()} -> {path}")
print("done")
