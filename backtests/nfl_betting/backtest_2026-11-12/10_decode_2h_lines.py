#!/usr/bin/env python3
"""Decode real second-half lines for NFL games 2011-2021 and attach weather and the nflverse closing lines.

Source of the lines: the pre-scraped file data/nfl_archive_10Y.json in the public repo
github.com/flancast90/sportsbookreview-scraper (MIT licence, commit 1a820e5), itself a scrape of the
sportsbookreviewsonline.com NFL odds archive. One closing second-half spread and one second-half total per game, no prices.

The archive stores each game as two rows (visitor, home). In each of the Open, Close and 2H columns one row holds the
spread (in the favourite's row) and the other row holds the total. The scraper decided which row is "the spread row" from
the OPEN column only and reused that for Close and 2H, and it set the home/away sign from the closing moneyline. So:
  R = the row with the smaller Open number (the opening favourite's row)
  |home_X_spread| in the json = the value sitting in row R for column X; the json "total" for X = the value in the other row.
This script undoes that:
  - close: if R's close value is the smaller one, R is the closing favourite, else the other row is.
    The closing favourite is the moneyline favourite, which tells us whether R is the home or the away row.
  - 2H: the row holding the smaller 2H value holds the 2H spread, so that team is the 2H favourite.
Checks are printed at the end (closing spread vs nflverse, and 2H margin regressed on the decoded 2H spread).

Usage: python3 10_decode_2h_lines.py <nfl_archive_10Y.json> <nflverse games.csv>"""
import sys, json, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
src, games_csv = sys.argv[1], sys.argv[2]
d = pd.DataFrame(json.load(open(src)))
d = d[d.home_team.apply(lambda x: isinstance(x, str))].copy()          # drops the 10 malformed Super Bowl rows
for c in [c for c in d.columns if 'Qtr' in c or 'final' in c]:
    d[c] = pd.to_numeric(d[c], errors='coerce')
d['gameday'] = pd.to_datetime(d.date.astype(int).astype(str), format='%Y%m%d')
d['h1_home'] = d.home_1stQtr + d.home_2ndQtr; d['h1_away'] = d.away_1stQtr + d.away_2ndQtr
d['reg_home'] = d.h1_home + d.home_3rdQtr + d.home_4thQtr; d['reg_away'] = d.h1_away + d.away_3rdQtr + d.away_4thQtr
d['fin_home'] = d.home_final; d['fin_away'] = d.away_final
d['ot'] = ((d.fin_home != d.reg_home) | (d.fin_away != d.reg_away)).astype(int)

# --- which row is R (opening favourite's row): home or away?
xR_close, xO_close = d.home_close_spread.abs(), d.close_over_under        # close values in row R and in the other row
close_fav_is_R = xR_close < xO_close
ml_fav_home = d.home_close_ml < d.away_close_ml
ml_known = d.home_close_ml != d.away_close_ml
R_is_home = np.where(close_fav_is_R, ml_fav_home, ~ml_fav_home)
d['close_spread_abs'] = np.minimum(xR_close, xO_close); d['close_total'] = np.maximum(xR_close, xO_close)
d['close_fav_home'] = ml_fav_home

# --- 2H
xR, xO = d.home_2H_spread.abs(), d['2H_total']
d['h2_total'] = np.maximum(xR, xO); d['h2_spread_abs'] = np.minimum(xR, xO)
h2_fav_is_R = xR < xO
h2_fav_home = np.where(h2_fav_is_R, R_is_home, ~R_is_home)
# home 2H line: negative = home lays points in the second half
d['h2_home_line'] = np.where(d.h2_spread_abs == 0, 0.0, np.where(h2_fav_home, -d.h2_spread_abs, d.h2_spread_abs))
ok_total = (d.h2_total >= 13) & (d.h2_total <= 40)
ok_side = ok_total & (d.h2_spread_abs >= 0) & (d.h2_spread_abs <= 17) & ((d.h2_spread_abs == 0) | ml_known)
# a json 2H value of 0 can be a true pick'em or a blank ("NL"); with a valid total beside it, it is read as pick'em
d['h2_total_ok'] = ok_total.astype(int); d['h2_side_ok'] = ok_side.astype(int)

# --- attach nflverse (weather, closing lines) by date +/- 1 day and final score
g = pd.read_csv(games_csv); g = g[(g.season >= 2011) & (g.season <= 2021)].copy()
g['gameday'] = pd.to_datetime(g.gameday)
key = {}
for r in g.itertuples():
    for off in (0, 1, -1):
        key.setdefault((r.gameday + pd.Timedelta(days=off), int(r.home_score), int(r.away_score)), []).append(r)
rows = []
for r in d.itertuples():
    c = key.get((r.gameday, int(r.fin_home), int(r.fin_away)), [])
    c = list({x.game_id: x for x in c}.values())
    rows.append(c[0] if len(c) == 1 else None)
d['game_id'] = [x.game_id if x is not None else '' for x in rows]
for col in ['spread_line', 'total_line', 'roof', 'wind', 'temp', 'week', 'game_type']:
    d['nv_' + col] = [getattr(x, col) if x is not None else np.nan for x in rows]
d['nv_home'] = [x.home_team if x is not None else '' for x in rows]

keep = ['season', 'gameday', 'game_id', 'home_team', 'away_team', 'nv_home', 'h1_home', 'h1_away', 'reg_home', 'reg_away', 'fin_home', 'fin_away', 'ot',
        'close_fav_home', 'close_spread_abs', 'close_total', 'h2_home_line', 'h2_spread_abs', 'h2_total', 'h2_total_ok', 'h2_side_ok',
        'nv_spread_line', 'nv_total_line', 'nv_roof', 'nv_wind', 'nv_temp', 'nv_week', 'nv_game_type']
out = d[keep].copy(); out['gameday'] = out.gameday.dt.strftime('%Y-%m-%d')
out.to_csv(os.path.join(HERE, 'h2_lines_2011_2021.csv'), index=False)

# --- checks
print('games in archive file: %d | matched to nflverse: %d | usable 2H total: %d | usable 2H side: %d' % (len(d), (d.game_id != '').sum(), ok_total.sum(), ok_side.sum()))
m = d[d.game_id != '']
agree = (np.sign(m.nv_spread_line) == np.where(m.close_fav_home, 1, -1)) | (m.nv_spread_line == 0)
print('closing favourite agrees with nflverse: %.1f%% | closing spread within 1 pt of nflverse: %.1f%% | closing total within 1 pt: %.1f%%' % (
    100 * agree.mean(), 100 * ((m.close_spread_abs - m.nv_spread_line.abs()).abs() <= 1).mean(), 100 * ((m.close_total - m.nv_total_line).abs() <= 1).mean()))
s = d[ok_side].copy()
s['m2'] = (s.fin_home - s.h1_home) - (s.fin_away - s.h1_away)             # home 2H margin incl. overtime
X = np.column_stack([-s.h2_home_line, np.ones(len(s))]); b = np.linalg.lstsq(X, s.m2.values, rcond=None)[0]
print('home 2H margin (incl. OT) = %.2f x (points the home team lays in the 2H) %+.2f   [a correct decode gives a slope near 1]' % (b[0], b[1]))
f = s[s.h2_spread_abs > 0]; fm = np.where(f.h2_home_line < 0, f.m2, -f.m2)
print('2H favourite: mean 2H margin %+.2f vs mean spread %.2f | wins the half outright %.1f%% of non-tied halves' % (fm.mean(), f.h2_spread_abs.mean(), 100 * (fm > 0).sum() / (fm != 0).sum()))
t = d[ok_total]; pts2 = (t.fin_home + t.fin_away) - (t.h1_home + t.h1_away)
print('2H total line mean %.2f | actual 2H points incl. OT mean %.2f' % (t.h2_total.mean(), pts2.mean()))
