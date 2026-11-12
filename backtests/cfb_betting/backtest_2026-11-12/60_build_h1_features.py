#!/usr/bin/env python3
"""First-half features for every 2026 college game with an FBS team, from the public cfbfastR play-by-play
(github.com/sportsdataverse/cfbfastR-data, data/rds/pbp_players_pos_2026.rds, converted to parquet). Definitions are those fixed in
CFB_SIDES_TEST_PLAN_LOCKED.md. Nothing here reads a price. Second-half scores are written to the file for the grader and are not
summarised here.
  scrimmage play   a row with rush == 1 or pass == 1 (sacks included; penalties, kicks, timeouts are not plays)
  yards per play   yards gained on scrimmage plays / scrimmage plays; a play that ends in an interception or a lost fumble counts 0 yards
  success          1st down: gained at least 50% of the distance; 2nd: at least 70%; 3rd and 4th: all of it; a turnover is a failure
  clean points     points on offensive touchdown or field-goal drives that started 40 or more yards from the goal line and gained 30
                   or more yards (change-log definition of 10/11: return scores, short fields and drives under 30 yards taken out)
  halftime clock   median time stamp of the last five plays of period 2 and of the first five plays of period 3 (single
                   mis-stamped plays are common in this feed)
Usage: python3 60_build_h1_features.py <pbp_2026.parquet>"""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
C = ['game_id', 'week', 'period', 'game_play_number', 'drive_number', 'pos_team', 'def_pos_team', 'home', 'away', 'play_type', 'rush', 'pass', 'yards_gained', 'down', 'distance',
     'pos_team_score', 'def_pos_team_score', 'drive_start_yards_to_goal', 'drive_yards', 'drive_start_offense_score', 'drive_end_offense_score', 'wallclock',
     'neutral_site', 'conference_game', 'start_date', 'home_team_division', 'away_team_division', 'home_team_conference', 'away_team_conference', 'spread', 'over_under', 'season_type']
p = pd.read_parquet(sys.argv[1], columns=C)
p = p[(p.home_team_division == 'fbs') | (p.away_team_division == 'fbs')].sort_values(['game_id', 'game_play_number'])
p['wc'] = pd.to_datetime(p.wallclock, utc=True, errors='coerce')
TO_INT = ('Interception Return', 'Interception Return Touchdown'); TO_FUM = ('Fumble Recovery (Opponent)', 'Fumble Recovery (Opponent) Touchdown')
OFF_TD = ('Rushing Touchdown', 'Passing Touchdown')
P4 = {'SEC', 'Big Ten', 'Big 12', 'ACC'}
rows = []
for gid, g in p.groupby('game_id', sort=False):
    home, away = g.home.iloc[0], g.away.iloc[0]
    h1, q3 = g[g.period <= 2], g[g.period == 3]
    if h1.empty or q3.empty: continue
    hs = np.where(g.pos_team == home, g.pos_team_score, np.where(g.def_pos_team == home, g.def_pos_team_score, np.nan))
    as_ = np.where(g.pos_team == away, g.pos_team_score, np.where(g.def_pos_team == away, g.def_pos_team_score, np.nan))
    m1 = (g.period <= 2).values
    r = dict(game_id=int(gid), week=int(g.week.iloc[0]), start=g.start_date.iloc[0], home=home, away=away, home_div=g.home_team_division.iloc[0], away_div=g.away_team_division.iloc[0],
             home_conf=g.home_team_conference.iloc[0], away_conf=g.away_team_conference.iloc[0], neutral=bool(g.neutral_site.iloc[0]), spread=g.spread.iloc[0], over_under=g.over_under.iloc[0],
             h1_home=np.nanmax(hs[m1]), h1_away=np.nanmax(as_[m1]), fin_home=np.nanmax(hs), fin_away=np.nanmax(as_), periods=int(g.period.max()),
             last_1h=h1.wc.dropna().tail(5).median(), q3_kick=q3.wc.dropna().head(5).median(), kick_wc=g.wc.dropna().head(5).median())
    r['p4'] = int((r['home_conf'] in P4 or home == 'Notre Dame') and (r['away_conf'] in P4 or away == 'Notre Dame'))
    k = q3[q3.play_type.astype(str).str.startswith('Kickoff')]
    r['q3_receiver'] = k.pos_team.iloc[0] if len(k) else ''
    for side, tm in (('home', home), ('away', away)):
        s = h1[(h1.pos_team == tm) & ((h1['rush'] == 1) | (h1['pass'] == 1))]
        to = s.play_type.isin(TO_INT + TO_FUM)
        yds = np.where(to, 0.0, s.yards_gained.fillna(0)); n = len(s)
        d = s[s.down.isin([1, 2, 3, 4]) & (s.distance > 0)]; dto = d.play_type.isin(TO_INT + TO_FUM)
        need = np.where(d.down == 1, 0.5, np.where(d.down == 2, 0.7, 1.0)) * d.distance
        ok = (d.yards_gained.fillna(0) >= need) & ~dto
        clean = 0.0
        for dn, dr in h1[h1.pos_team == tm].groupby('drive_number'):
            td, fg = dr.play_type.isin(OFF_TD).any(), (dr.play_type == 'Field Goal Good').any()
            if not (td or fg): continue
            y2g, dy = dr.drive_start_yards_to_goal.iloc[0], dr.drive_yards.iloc[0]
            if pd.isna(y2g) or pd.isna(dy): clean = np.nan; break
            if y2g >= 40 and dy >= 30:
                gain = dr.drive_end_offense_score.iloc[0] - dr.drive_start_offense_score.iloc[0]
                clean += gain if gain in (3, 6, 7, 8) else (7 if td else 3)
        r.update({side + '_plays': n, side + '_yards': float(yds.sum()), side + '_ypp': float(yds.sum()) / n if n else np.nan, side + '_sr_n': len(d),
                  side + '_sr': float(ok.mean()) if len(d) else np.nan, side + '_int': int(s.play_type.isin(TO_INT).sum()), side + '_fum': int(s.play_type.isin(TO_FUM).sum()), side + '_clean': clean})
    rows.append(r)
F = pd.DataFrame(rows)
F['gap_min'] = (F.q3_kick - F.last_1h).dt.total_seconds() / 60; F['h1_len_min'] = (F.last_1h - F.kick_wc).dt.total_seconds() / 60
F['ok'] = (F.gap_min.between(12, 45) & F.h1_len_min.between(60, 150) & (F.home_plays >= 15) & (F.away_plays >= 15)).astype(int)
F['look'] = np.where(F.gap_min >= 11, F.last_1h + pd.Timedelta(minutes=10), F.q3_kick - pd.Timedelta(seconds=60))
F['lead'] = (F.h1_home - F.h1_away).abs(); F['ypp_edge'] = F.home_ypp - F.away_ypp; F['clean_margin'] = F.home_clean - F.away_clean; F['sr_edge'] = F.home_sr - F.away_sr
F['flow_side'] = np.where((F.ypp_edge >= 1.5) & (F.clean_margin > 0), 'home', np.where((F.ypp_edge <= -1.5) & (F.clean_margin < 0), 'away', ''))
trail_home, trail_away = (F.h1_away - F.h1_home).between(1, 14), (F.h1_home - F.h1_away).between(1, 14)
F['sr_side'] = np.where(F.sr_edge >= 0.07, 'home', np.where(F.sr_edge <= -0.07, 'away', ''))
F['s_side'] = np.where(trail_home & (F.sr_edge >= 0.07), 'home', np.where(trail_away & (F.sr_edge <= -0.07), 'away', ''))
F['et_date'] = pd.to_datetime(F.start, utc=True).dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d')
F['discovery'] = F.et_date.isin(['2026-10-24', '2026-10-31']).astype(int)
F = F.sort_values(['start', 'game_id']).reset_index(drop=True); F.to_csv(os.path.join(HERE, 'cfb_h1_features_2026.csv'), index=False)
print('games with an FBS team and both halves in the play-by-play: %d | both FBS %d | FBS v FCS %d | neutral site %d | weeks %d to %d (%s to %s)' % (
    len(F), ((F.home_div == 'fbs') & (F.away_div == 'fbs')).sum(), ((F.home_div != 'fbs') | (F.away_div != 'fbs')).sum(), F.neutral.sum(), F.week.min(), F.week.max(), F.et_date.min(), F.et_date.max()))
print('halftime clock usable: %d of %d | halftime length, minutes: median %.1f, 5th to 95th percentile %.1f to %.1f | first half length: median %.0f' % (
    F.ok.sum(), len(F), F.gap_min.median(), F.gap_min.quantile(.05), F.gap_min.quantile(.95), F.h1_len_min.median()))
print('not usable: halftime gap out of range %d, first-half length out of range %d, under 15 plays for a team %d' % ((~F.gap_min.between(12, 45)).sum(), (~F.h1_len_min.between(60, 150)).sum(), ((F.home_plays < 15) | (F.away_plays < 15)).sum()))
print('first-half numbers: yards per play median %.2f | success rate median %.3f | plays per team median %d | clean margin missing %d' % (
    pd.concat([F.home_ypp, F.away_ypp]).median(), pd.concat([F.home_sr, F.away_sr]).median(), pd.concat([F.home_plays, F.away_plays]).median(), F.clean_margin.isna().sum()))
print('pregame spread present: %d | discovery Saturdays (10/24, 10/31): %d games' % (F.spread.notna().sum(), F.discovery.sum()))
U = F[F.ok == 1]
print('usable games that meet each trigger (no price or result read): HOME (not neutral) %d | FLOW side with a lead under 21: %d | trailing 1 to 14 with a success-rate edge of 7 points: %d' % (
    (~U.neutral).sum(), ((U.flow_side != '') & (U.lead < 21)).sum(), (U.s_side != '').sum()))
print('success-rate side (edge of 7 points or more) with a lead under 21: %d | on the two discovery Saturdays: HOME %d, FLOW under 21 %d (the 11/6 replay had 23), success-rate side %d' % (
    ((U.sr_side != '') & (U.lead < 21)).sum(), (~U[U.discovery == 1].neutral).sum(), ((U.flow_side != '') & (U.lead < 21) & (U.discovery == 1)).sum(), ((U.sr_side != '') & (U.lead < 21) & (U.discovery == 1)).sum()))
print('FLOW and success-rate sides: same team %d, opposite %d, FLOW only %d, success rate only %d (usable games, lead under 21)' % (
    ((U.flow_side == U.sr_side) & (U.flow_side != '') & (U.lead < 21)).sum(), ((U.flow_side != U.sr_side) & (U.flow_side != '') & (U.sr_side != '') & (U.lead < 21)).sum(),
    ((U.flow_side != '') & (U.sr_side == '') & (U.lead < 21)).sum(), ((U.flow_side == '') & (U.sr_side != '') & (U.lead < 21)).sum()))
print('by week, usable games:', U.groupby('week').size().to_dict())
