#!/usr/bin/env python3
"""Second-half rules graded against REAL second-half closing lines, NFL 2011-2021 (h2_lines_2011_2021.csv, from 10_decode_2h_lines.py).
One line per game, no prices, so every bet is graded at -110 (break-even 52.4%). Second half includes overtime (sportsbook settlement).
Every test here is one of the protocol's own rules or the lean class as it was actually played. Nothing was searched for."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, 'h2_lines_2011_2021.csv'))
d['hm'] = d.h1_home - d.h1_away                                            # home halftime margin
d['m2'] = (d.fin_home - d.h1_home) - (d.fin_away - d.h1_away)              # home 2H margin incl. OT
d['pts1'] = d.h1_home + d.h1_away
d['pts2'] = (d.fin_home + d.fin_away) - d.pts1
d['pre_home_lay'] = np.where(d.close_fav_home, d.close_spread_abs, -d.close_spread_abs)
T = d[d.h2_total_ok == 1].copy(); S = d[d.h2_side_ok == 1].copy()
BE = 110 / 210

def line(label, w, l, p):
    n = w + l
    if n == 0: print('  %-58s n   0' % label); return
    pct = w / n; se = np.sqrt(0.25 / n); z50 = (pct - 0.5) / se; zbe = (pct - BE) / se
    print('  %-58s %4d-%-4d-%-3d  %5.1f%%  (se %.1f)  vs 50%%: z %+.1f   vs 52.4%%: z %+.1f' % (label, w, l, p, 100 * pct, 100 * se, z50, zbe))

def total_rec(label, g, side='over'):
    o = (g.pts2 > g.h2_total).sum(); u = (g.pts2 < g.h2_total).sum(); p = (g.pts2 == g.h2_total).sum()
    line(label + (' [Over]' if side == 'over' else ' [Under]'), o if side == 'over' else u, u if side == 'over' else o, p)

def side_rec(label, g, pick_home):
    """pick_home: boolean array, True = bet the home team on its 2H line, False = bet the away team."""
    r = np.where(pick_home, g.m2 + g.h2_home_line, -(g.m2 + g.h2_home_line))
    line(label, int((r > 0).sum()), int((r < 0).sum()), int((r == 0).sum()))

print('=== SECOND-HALF TOTALS vs the real 2H total, 2011-2021 (n = %d) ===' % len(T))
total_rec('all games', T); total_rec('all games', T, 'under')
print(' by first-half points (H-25: 41+ REGRESSION WATCH, 45+ Overs shadow-only)')
for lo, hi in [(0, 13), (14, 20), (21, 27), (28, 34), (35, 40), (41, 44), (45, 99)]:
    total_rec('1H points %d-%s' % (lo, hi if hi < 99 else 'up'), T[(T.pts1 >= lo) & (T.pts1 <= hi)], 'under')
total_rec('1H points 41 or more', T[T.pts1 >= 41], 'under')
print(' by halftime lead (H-24; the dead v0.2 line said 17+ -> Under only)')
for lo, hi in [(0, 3), (4, 7), (8, 10), (11, 16), (17, 99)]:
    total_rec('lead %d-%s' % (lo, hi if hi < 99 else 'up'), T[(T.hm.abs() >= lo) & (T.hm.abs() <= hi)], 'under')
print(' wind, outdoor games with a reading (H-26: 15+ -> 2H Overs dead, Unders eligible)')
W = T[T.nv_roof.isin(['outdoors', 'open']) & T.nv_wind.notna()]
for lo, hi in [(0, 9), (10, 14), (15, 99)]:
    total_rec('wind %d-%s mph' % (lo, hi if hi < 99 else 'up'), W[(W.nv_wind >= lo) & (W.nv_wind <= hi)], 'under')
total_rec('wind 20+ mph', W[W.nv_wind >= 20], 'under')
total_rec('dome or closed roof', T[T.nv_roof.isin(['dome', 'closed'])], 'under')
print(' stability of the two results above that showed something (first six seasons, then last five)')
total_rec('1H points 28+   2011-2016', T[(T.pts1 >= 28) & (T.season <= 2016)], 'under'); total_rec('1H points 28+   2017-2021', T[(T.pts1 >= 28) & (T.season >= 2017)], 'under')
total_rec('1H points 28 or more, all seasons', T[T.pts1 >= 28], 'under'); total_rec('1H points 35 or more, all seasons', T[T.pts1 >= 35], 'under'); total_rec('1H points under 28, all seasons', T[T.pts1 < 28], 'under')
total_rec('wind 15+        2011-2016', W[(W.nv_wind >= 15) & (W.season <= 2016)], 'under'); total_rec('wind 15+        2017-2021', W[(W.nv_wind >= 15) & (W.season >= 2017)], 'under')
total_rec('second halves that ended in regulation', T[T.ot == 0], 'under'); total_rec('games that went to overtime', T[T.ot == 1], 'under')
print(' Anchor Mode (H-21): 2H total against 0.50 x pregame total. Bet back toward the anchor.')
T['anch'] = T.h2_total - 0.5 * T.close_total
total_rec('2H total 1.5+ ABOVE the anchor -> Under', T[T.anch >= 1.5], 'under')
total_rec('2H total 3.0+ ABOVE the anchor -> Under', T[T.anch >= 3.0], 'under')
total_rec('2H total 1.5+ BELOW the anchor -> Over', T[T.anch <= -1.5], 'over')
total_rec('2H total 3.0+ BELOW the anchor -> Over', T[T.anch <= -3.0], 'over')
print(' pregame total minus first-half points, against the 2H total (pregame cousin of DERIV-LAG, H-20)')
T['der'] = (T.close_total - T.pts1) - T.h2_total
total_rec('derived 3+ ABOVE the 2H total -> Over', T[T.der >= 3], 'over')
total_rec('derived 6+ ABOVE the 2H total -> Over', T[T.der >= 6], 'over')
total_rec('derived 3+ BELOW the 2H total -> Under', T[T.der <= -3], 'under')
total_rec('derived 6+ BELOW the 2H total -> Under', T[T.der <= -6], 'under')
print(' how the market sets the 2H total: 2H total = a x pregame total + b x 1H points + c x halftime lead + k')
X = np.column_stack([T.close_total, T.pts1, T.hm.abs(), np.ones(len(T))]); c = np.linalg.lstsq(X, T.h2_total.values, rcond=None)[0]
print('   line:   %.3f x pregame total %+.3f x 1H points %+.3f x lead %+.2f   (R2 %.2f)' % (c[0], c[1], c[2], c[3], 1 - ((T.h2_total - X @ c) ** 2).sum() / ((T.h2_total - T.h2_total.mean()) ** 2).sum()))
c2 = np.linalg.lstsq(X, T.pts2.values, rcond=None)[0]
print('   actual: %.3f x pregame total %+.3f x 1H points %+.3f x lead %+.2f' % tuple(c2))
r = T.pts2 - T.h2_total
Xr = np.column_stack([T.pts1 - T.pts1.mean(), T.hm.abs() - T.hm.abs().mean(), np.ones(len(T))]); cr = np.linalg.lstsq(Xr, r.values, rcond=None)[0]
res = r - Xr @ cr; cov = np.linalg.inv(Xr.T @ Xr) * res.var(ddof=3)
print('   2H points minus the line: mean %+.2f (se %.2f); per 1H point %+.3f (t %+.1f); per point of lead %+.3f (t %+.1f)' % (
    r.mean(), r.std() / np.sqrt(len(r)), cr[0], cr[0] / np.sqrt(cov[0, 0]), cr[1], cr[1] / np.sqrt(cov[1, 1])))

print()
print('=== SECOND-HALF SIDES vs the real 2H spread, 2011-2021 (n = %d) ===' % len(S))
F = S[S.h2_spread_abs > 0]
side_rec('2H favourite, all', F, (F.h2_home_line < 0).values)
for lo, hi in [(0.5, 2.5), (3, 3), (3.5, 6.5), (7, 99)]:
    g = F[(F.h2_spread_abs >= lo) & (F.h2_spread_abs <= hi)]
    side_rec('2H favourite laying %s-%s' % (lo, hi if hi < 99 else 'up'), g, (g.h2_home_line < 0).values)
print(' halftime leader on its 2H line (the lean class: 18 of the 21 second-half leans were on the leader)')
L = S[S.hm != 0]
side_rec('halftime leader, all', L, (L.hm > 0).values)
for lo, hi in [(1, 3), (4, 7), (8, 10), (11, 16), (17, 99)]:
    g = L[(L.hm.abs() >= lo) & (L.hm.abs() <= hi)]
    side_rec('leader by %d-%s' % (lo, hi if hi < 99 else 'up'), g, (g.hm > 0).values)
g = L[L.hm.abs() >= 17]
side_rec('TRAILER when the lead is 17+ (H-24 allows this side)', g, (g.hm < 0).values)
print(' pregame favourite trailing at the half, bet on its 2H line')
g = S[(S.close_spread_abs > 0) & (np.where(S.close_fav_home, S.hm, -S.hm) < 0)]
side_rec('pregame favourite, trailing', g, g.close_fav_home.values)
g = S[(S.close_spread_abs >= 3) & (np.where(S.close_fav_home, S.hm, -S.hm) <= -7)]
side_rec('pregame favourite of 3+, trailing by 7+', g, g.close_fav_home.values)
print(' pregame underdog leading at the half, bet on its 2H line')
g = S[(S.close_spread_abs > 0) & (np.where(S.close_fav_home, S.hm, -S.hm) < 0)]
side_rec('pregame underdog, leading', g, (~g.close_fav_home).values)

print(' a line derived from pregame spread and halftime score, against the real 2H spread (the idea behind Anchor Mode H-21 and, with live prices, DERIV-LAG H-20)')
Xs = np.column_stack([S.pre_home_lay, S.hm, np.ones(len(S))]); cs = np.linalg.lstsq(Xs, (-S.h2_home_line).values, rcond=None)[0]
S['gap'] = Xs @ cs - (-S.h2_home_line)           # + = the derived line has the home team laying MORE than the market asks -> home looks cheap
print('   market: 2H home lay = %.3f x pregame home lay %+.3f x halftime home margin %+.2f   (R2 %.2f)' % (cs[0], cs[1], cs[2], 1 - (S.gap ** 2).sum() / ((S.h2_home_line - S.h2_home_line.mean()) ** 2).sum()))
for th in (1.5, 2.5):
    g = S[S.gap.abs() >= th]
    side_rec('market %.1f+ off the derived line -> bet the side that looks cheap' % th, g, (g.gap > 0).values)

print()
print('=== FLOW against real 2H lines, 2015-2021 (first-half yards per play from nflverse play-by-play) ===')
fl = pd.read_csv(os.path.join(HERE, '..', 'review_2026-11-11', 'flow_1h_2015_2026.csv'))
fl['ypp'] = fl.yards / fl.plays.replace(0, np.nan)
home = S[['game_id', 'nv_home']].merge(fl, left_on=['game_id', 'nv_home'], right_on=['game_id', 'posteam'], how='inner')[['game_id', 'ypp', 'giveaways']].rename(columns={'ypp': 'ypp_h', 'giveaways': 'gv_h'})
both = fl.merge(S[['game_id', 'nv_home']], on='game_id'); away = both[both.posteam != both.nv_home][['game_id', 'ypp', 'giveaways']].rename(columns={'ypp': 'ypp_a', 'giveaways': 'gv_a'})
G = S.merge(home, on='game_id').merge(away, on='game_id'); G['yd'] = G.ypp_h - G.ypp_a
print('  games with FLOW rows and a real 2H line: %d' % len(G))
g = G[(G.yd.abs() >= 1.5) & (np.sign(G.yd) == np.sign(G.hm))]
side_rec('FLOW side: out-gained by 1.5+ YPP AND leads (protocol test)', g, (g.yd > 0).values)
g = G[(G.yd.abs() >= 1.5)]
side_rec('out-gained by 1.5+ YPP, any score', g, (g.yd > 0).values)
g = G[(G.yd.abs() >= 1.5) & (np.sign(G.yd) == -np.sign(G.hm))]
side_rec('out-gained by 1.5+ YPP but TRAILS', g, (g.yd > 0).values)
g = G[(G.yd.abs() >= 2.5) & (np.sign(G.yd) == np.sign(G.hm))]
side_rec('out-gained by 2.5+ YPP AND leads', g, (g.yd > 0).values)
tot = G[G.h2_total_ok == 1].copy(); tot['ypp_sum'] = tot.ypp_h + tot.ypp_a
hi = tot[tot.ypp_sum >= tot.ypp_sum.quantile(0.8)]; lo = tot[tot.ypp_sum <= tot.ypp_sum.quantile(0.2)]
total_rec('top fifth of combined 1H YPP (FLOW is barred from totals, H-38)', hi, 'over')
total_rec('bottom fifth of combined 1H YPP', lo, 'under')
tot['eff'] = tot.pts1 - (tot.ypp_sum - tot.ypp_sum.mean()) * np.polyfit(tot.ypp_sum, tot.pts1, 1)[0] - tot.pts1.mean()
total_rec('1H points far ABOVE what the yards say (top fifth) -> Under', tot[tot.eff >= tot.eff.quantile(0.8)], 'under')
total_rec('1H points far BELOW what the yards say (bottom fifth) -> Over', tot[tot.eff <= tot.eff.quantile(0.2)], 'over')

print()
print('=== Do a side and a total in the same second half move together? (real lines, 2011-2021) ===')
B = S[(S.h2_total_ok == 1)].copy()
B['over'] = np.sign(B.pts2 - B.h2_total)
def corr(label, cover):
    k = (cover != 0) & (B.over != 0)
    a = (cover[k] > 0).astype(int); b = (B.over[k] > 0).astype(int)
    r = np.corrcoef(a, b)[0, 1]; n = int(k.sum())
    both = ((a == 1) & (b == 1)).mean()
    print('  %-44s n %4d  correlation %+.3f (se %.3f)  both win %.1f%% (independent bets: %.1f%%)' % (label, n, r, 1 / np.sqrt(n), 100 * both, 100 * a.mean() * b.mean()))
fav = pd.Series(np.where(B.h2_home_line < 0, B.m2 + B.h2_home_line, np.where(B.h2_home_line > 0, -(B.m2 + B.h2_home_line), 0)), index=B.index)
corr('2H favourite covers  with  Over', fav)
lead = pd.Series(np.where(B.hm > 0, B.m2 + B.h2_home_line, np.where(B.hm < 0, -(B.m2 + B.h2_home_line), 0)), index=B.index)
corr('halftime leader covers  with  Over', lead)
homec = pd.Series(B.m2 + B.h2_home_line, index=B.index)
corr('home team covers  with  Over', homec)
big = B[B.hm.abs() >= 11].index
B2 = B.loc[big]; k = (lead.loc[big] != 0) & (B2.over != 0)
a = (lead.loc[big][k] > 0).astype(int); b = (B2.over[k] > 0).astype(int)
print('  %-44s n %4d  correlation %+.3f (se %.3f)' % ('leader by 11+ covers  with  Over', int(k.sum()), np.corrcoef(a, b)[0, 1], 1 / np.sqrt(k.sum())))
