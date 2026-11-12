#!/usr/bin/env python3
"""Grades CFB_SIDES_TEST_PLAN_LOCKED.md (audit B-CFB-7): three side claims on 2026 college second halves at real halftime prices.
Written after the lock; implements its sections 2 to 5 as written.
  features  cfb_h1_features_2026.csv (60_build_h1_features.py)
  prices    ../../nfl_betting/backtest_2026-11-12/halftime_pull/pulled_cfb_pull_plan*.csv.gz (second-half spreads; point = HOME spread,
            price_a = home, price_b = away; age = seconds since that book's last update)
  a bet     one side at each clean book's own number and price; a game counts once (its books averaged); second half with overtime;
            a tie is a refund; stake to win $300
Usage: python3 62_grade_cfb_sides.py"""
import os, glob, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); HP = os.path.join(HERE, '..', '..', 'nfl_betting', 'backtest_2026-11-12', 'halftime_pull')
def imp(a): a = np.asarray(a, dtype=float); return np.where(a < 0, -a / (-a + 100), 100 / (a + 100))
F = pd.read_csv(os.path.join(HERE, 'cfb_h1_features_2026.csv')); F = F[F.ok == 1].copy()
F['m2'] = (F.fin_home - F.h1_home) - (F.fin_away - F.h1_away); F['ko'] = pd.to_datetime(F.start, utc=True); F['hm'] = F.h1_home - F.h1_away
Q = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(HP, 'pulled_cfb_pull_plan*.csv.gz')))], ignore_index=True)
Q = Q[(Q.market == 'spreads_h2') & Q.game_id.astype(str).str.fullmatch(r'\d+')].copy(); Q['game_id'] = Q.game_id.astype(int)
Q = Q.drop_duplicates(['game_id', 'book', 'point', 'price_a', 'price_b'])
for c in ('point', 'price_a', 'price_b', 'age'): Q[c] = pd.to_numeric(Q[c], errors='coerce')
Q = Q.merge(F[['game_id', 'last_1h', 'q3_kick']], on='game_id', how='inner')
Q['main'] = Q.price_a.between(-200, 200) & Q.price_b.between(-200, 200) & Q.point.notna()
upd = pd.to_datetime(Q.ts, utc=True) - pd.to_timedelta(Q.age.fillna(0), unit='s')
Q['fresh'] = Q.age.notna() & (upd >= pd.to_datetime(Q.last_1h, utc=True)); Q['before_q3'] = pd.to_datetime(Q.ts, utc=True) < pd.to_datetime(Q.q3_kick, utc=True)
C = Q[Q.main & Q.fresh & Q.before_q3].copy(); nb = C.groupby('game_id').book.nunique(); C = C[C.game_id.map(nb) >= 2].copy()
C['pa'], C['pb'] = imp(C.price_a), imp(C.price_b); C['fair_home'] = C.pa / (C.pa + C.pb)
G = F[F.game_id.isin(set(C.game_id))].copy(); med = C.groupby('game_id').point.median(); G['line2'] = G.game_id.map(med)

def grade(sel, books=None, step=0.0, basis='book'):
    """sel: DataFrame with game_id and side ('home' / 'away'). Returns one row per game: net, risk, win, loss, push (book-averaged)."""
    c = C if books is None else C[C.book.isin(books)]
    x = c.merge(sel[['game_id', 'side']], on='game_id').merge(F[['game_id', 'm2', 'week', 'ko']], on='game_id')
    if x.empty: return pd.DataFrame(columns=['game_id', 'net', 'risk', 'win', 'loss', 'push', 'week', 'ko'])
    home = (x.side == 'home').values
    line = np.where(home, x.point, -x.point); mar = np.where(home, x.m2, -x.m2) + line
    if basis == 'fair': p = np.where(home, x.fair_home, 1 - x.fair_home)
    else: p = np.where(home, x.pa, x.pb) + step
    if basis == 'best':                                        # friendliest number for the side, then the cheapest price on it
        x = x.assign(line=line, p=p, mar=mar).sort_values(['game_id', 'line', 'p'], ascending=[True, False, True]).drop_duplicates('game_id')
        line, p, mar = x.line.values, x.p.values, x.mar.values
    risk = 300 * p / (1 - p); net = np.where(mar > 0, 300.0, np.where(mar < 0, -risk, 0.0))
    y = pd.DataFrame(dict(game_id=x.game_id.values, net=net, risk=risk, win=(mar > 0) * 1.0, loss=(mar < 0) * 1.0, push=(mar == 0) * 1.0))
    y = y.groupby('game_id').mean().reset_index()
    return y.merge(F[['game_id', 'week', 'ko']], on='game_id').sort_values('ko')
def roi(g): return float('nan') if len(g) == 0 or g.risk.sum() == 0 else 100 * g.net.sum() / g.risk.sum()
def wr(g): return float('nan') if (g.win.sum() + g.loss.sum()) == 0 else 100 * g.win.sum() / (g.win.sum() + g.loss.sum())
def bar(g, B=100000, seed=20261112):
    w = g.groupby('week')[['net', 'risk']].sum(); K = len(w)
    if K < 8: return float('nan'), K
    rng = np.random.default_rng(seed); idx = rng.integers(0, K, size=(B, K)); r = w.net.values[idx].sum(1) / w.risk.values[idx].sum(1)
    return 100 * float(np.quantile(r, 0.0167)), K
def line(lab, g, g1=None):
    print('  %-58s n %4d  %5.1f%% won  return %+6.1f%%%s' % (lab, len(g), wr(g), roi(g), '' if g1 is None else '  one step worse %+6.1f%%' % roi(g1)))
def claim(tag, lab, sel):
    g, g1 = grade(sel), grade(sel, step=0.01); h = len(g) // 2; a, b = g.iloc[:h], g.iloc[h:]
    lcb, K = bar(g)
    word = 'UNDERPOWERED (%d and %d games)' % (len(a), len(b)) if min(len(a), len(b)) < 40 else ('PASSED THE SCREEN' if roi(a) > 0 and roi(b) > 0 and roi(g1) > 0 else 'FAILED')
    clears = 'not judged (%d weeks)' % K if np.isnan(lcb) else ('YES' if roi(g) > 0 and lcb > 0 else 'no')
    print('%s %s' % (tag, lab)); line('all verdict games', g, g1); line('   first half of them (to %s)' % (a.ko.max().strftime('%m/%d') if len(a) else '-'), a); line('   second half', b)
    print('     %s | doubter\'s bar: lower bound %+.1f%% over %d weeks -> clears: %s | pushes %.1f | by week %s' % (word, lcb, K, clears, g.push.sum(), ' '.join('%d:%+.0f' % (k, roi(v)) for k, v in g.groupby('week'))))
    return g
S = lambda mask, side: pd.DataFrame(dict(game_id=G[mask].game_id.values, side=(side[mask].values if hasattr(side, 'values') else side)))
lead21 = G.lead < 21; nd = G.discovery == 0
leader = pd.Series(np.where(G.hm > 0, 'home', np.where(G.hm < 0, 'away', '')), index=G.index)
trailer = pd.Series(np.where(G.hm > 0, 'away', np.where(G.hm < 0, 'home', '')), index=G.index)
recv = pd.Series(np.where(G.q3_receiver == G.home, 'home', np.where(G.q3_receiver == G.away, 'away', '')), index=G.index)
fav2 = pd.Series(np.where(G.line2 < 0, 'home', np.where(G.line2 > 0, 'away', '')), index=G.index)
ypp_side = pd.Series(np.where(G.ypp_edge >= 1.5, 'home', np.where(G.ypp_edge <= -1.5, 'away', '')), index=G.index)
homeS = pd.Series('home', index=G.index); awayS = pd.Series('away', index=G.index)
fl, sr = G.flow_side.fillna(''), G.sr_side.fillna('')

print('=== 9. COVERAGE ===')
print('usable games %d | with any quote %d | with a counting look (2+ clean books, before the third-quarter kickoff) %d | discovery Saturdays among them %d' % (len(F), Q.game_id.nunique(), len(G), G.discovery.sum()))
print('quotes %d | not main line %d | stale (last update before the end of the half) %d | snapshot after the third-quarter kickoff %d | clean %d | books per counting game: median %d' % (
    len(Q), (~Q.main).sum(), (Q.main & ~Q.fresh).sum(), (~Q.before_q3).sum(), len(C), nb[nb >= 2].median()))
print('clean quotes by book:', C.book.value_counts().to_dict())
print('counting games by week:', G.groupby('week').size().to_dict(), '| by tier: both power-four %d, other FBS v FBS %d, FBS v FCS %d' % ((G.p4 == 1).sum(), ((G.p4 == 0) & (G.away_div == 'fbs') & (G.home_div == 'fbs')).sum(), ((G.away_div != 'fbs') | (G.home_div != 'fbs')).sum()))
lk = (pd.to_datetime(C.ts, utc=True) - pd.to_datetime(C.last_1h, utc=True)).dt.total_seconds() / 60
print('snapshot time after the last first-half play, minutes: median %.1f, 5th to 95th percentile %.1f to %.1f' % (lk.median(), lk.quantile(.05), lk.quantile(.95)))

print('\n=== THE THREE CLAIMS (average clean book at its own number and price) ===')
gH = claim('H', 'HOME, second half (neutral sites and the two discovery Saturdays out)', S(~G.neutral & nd, homeS))
gF = claim('F', 'FLOW side, lead under 21 (discovery Saturdays out)', S((fl != '') & lead21 & nd, fl))
gS = claim('S', 'SUCCESS-RATE side, lead under 21 (all dates)', S((sr != '') & lead21, sr))
print('overlap: F and S name the same team in %d verdict games, opposite teams in %d' % (((fl == sr) & (fl != '') & lead21 & nd).sum(), ((fl != sr) & (fl != '') & (sr != '') & lead21 & nd).sum()))

print('\n=== 1. REPRODUCTION on the two discovery Saturdays (the 11/6 replay: home 58-33, FLOW under 21 17-6, both at DraftKings\' number) ===')
d = G.discovery == 1
for lab, sel in [('HOME', S(~G.neutral & d, homeS)), ('FLOW side, lead under 21', S((fl != '') & lead21 & d, fl)), ('SUCCESS-RATE side, lead under 21', S((sr != '') & lead21 & d, sr))]:
    cdk = C[C.book == 'draftkings']; y = cdk.merge(sel, on='game_id').merge(F[['game_id', 'm2']], on='game_id')
    mar = np.where(y.side == 'home', y.m2 + y.point, -y.m2 - y.point)
    print('  %-34s at DraftKings: %d-%d-%d | at the average book:' % (lab, (mar > 0).sum(), (mar < 0).sum(), (mar == 0).sum()), end=''); line('', grade(sel))

print('\n=== 2. PRICE BASIS ===')
for lab, sel in [('H', S(~G.neutral & nd, homeS)), ('F', S((fl != '') & lead21 & nd, fl)), ('S', S((sr != '') & lead21, sr))]:
    print('  %s: at the no-vig fair price %+6.1f%% | at the best book %+6.1f%% | at the average book %+6.1f%%' % (lab, roi(grade(sel, basis='fair')), roi(grade(sel, basis='best')), roi(grade(sel))))

print('\n=== 3. CONTROLS (all counting games, all dates) ===')
line('away team (not neutral)', grade(S(~G.neutral, awayS)))
line('home team, all dates', grade(S(~G.neutral, homeS)))
line('halftime leader, lead 1 to 20', grade(S((leader != '') & lead21, leader)))
line('halftime leader, lead 1 to 20, FLOW does not agree', grade(S((leader != '') & lead21 & (fl != leader), leader)))
line('trailing team, deficit 1 to 20', grade(S((trailer != '') & lead21, trailer)))
line('team receiving the third-quarter kickoff', grade(S(recv != '', recv)))
line('favourite of the second-half line', grade(S(fav2 != '', fav2)))

print('\n=== 4. VARIANTS (all dates) ===')
line('yards-per-play edge 1.5+ alone, lead under 21', grade(S((ypp_side != '') & lead21, ypp_side)))
line('FLOW side, all dates, lead under 21', grade(S((fl != '') & lead21, fl)))
line('FLOW side when it leads (1 to 20)', grade(S((fl != '') & lead21 & (fl == leader), fl)))
line('FLOW side when it trails or is tied', grade(S((fl != '') & lead21 & (fl != leader), fl)))
line('SUCCESS-RATE side when it leads (1 to 20)', grade(S((sr != '') & lead21 & (sr == leader), sr)))
line('SUCCESS-RATE side when it trails by 1 to 14 (the scout)', grade(S((sr != '') & (sr == trailer) & (G.lead <= 14), sr)))
fum_more = pd.Series(np.where(sr == 'home', G.home_fum > G.away_fum, np.where(sr == 'away', G.away_fum > G.home_fum, False)), index=G.index)
line('SUCCESS-RATE side that lost more fumbles in the half', grade(S((sr != '') & lead21 & fum_more, sr)))
line('F and S name the same team', grade(S((fl != '') & (fl == sr) & lead21, fl)))
line('FLOW names a team, success rate does not', grade(S((fl != '') & (sr == '') & lead21, fl)))
line('success rate names a team, FLOW does not', grade(S((fl == '') & (sr != '') & lead21, sr)))

print('\n=== 5. TIERS ===')
tiers = [('both power-four', G.p4 == 1), ('other FBS v FBS', (G.p4 == 0) & (G.away_div == 'fbs') & (G.home_div == 'fbs')), ('FBS v FCS', (G.away_div != 'fbs') | (G.home_div != 'fbs'))]
for lab, m, side in [('H', ~G.neutral & nd, homeS), ('F', (fl != '') & lead21 & nd, fl), ('S', (sr != '') & lead21, sr)]:
    for tl, tm in tiers: line('%s, %s' % (lab, tl), grade(S(m & tm, side)))

print('\n=== 6. HOME, split (all dates, not neutral) ===')
for lab, m in [('home is the pregame favourite', G.spread < 0), ('home is the pregame underdog', G.spread > 0), ('home leads at the half', G.hm > 0), ('home trails', G.hm < 0), ('tied', G.hm == 0), ('home leads by 21+', G.hm >= 21), ('home trails by 21+', G.hm <= -21)]:
    line(lab, grade(S(~G.neutral & m, homeS)))

print('\n=== 7. ENGINE PREMISE: a book 3.0+ better than the no-vig median of the other clean books on the same number ===')
rows = []
for gid, x in C.groupby('game_id'):
    if x.book.nunique() < 3: continue
    m2 = float(F.loc[F.game_id == gid, 'm2'].iloc[0])
    for v in x.itertuples():
        o = x[(x.book != v.book) & np.isclose(x.point, v.point)]
        if len(o) < 2: continue
        fh = float(o.fair_home.median())
        for side, fair, p, mar in (('home', fh, v.pa, m2 + v.point), ('away', 1 - fh, v.pb, -m2 - v.point)):
            rows.append(dict(game_id=gid, book=v.book, side=side, edge=100 * (fair - p), p=p, mar=mar))
E = pd.DataFrame(rows)
if len(E):
    E = E.sort_values('edge', ascending=False).drop_duplicates(['game_id', 'side'])
    for lab, lo, hi in [('3.0 or more', 3, 99), ('2.0 to 2.9', 2, 3), ('1.0 to 1.9', 1, 2)]:
        e = E[(E.edge >= lo) & (E.edge < hi)]; risk = 300 * e.p / (1 - e.p); net = np.where(e.mar > 0, 300, np.where(e.mar < 0, -risk, 0))
        print('  %-12s %3d entries in %3d of %d games with 3+ books | %d-%d-%d | return %+6.1f%% | books: %s' % (lab, len(e), e.game_id.nunique(), C[C.game_id.map(nb) >= 3].game_id.nunique(), (e.mar > 0).sum(), (e.mar < 0).sum(), (e.mar == 0).sum(),
              100 * net.sum() / risk.sum() if len(e) else float('nan'), e.book.value_counts().to_dict()))
sp = C.groupby('game_id').point.agg(lambda s: s.max() - s.min()); print('  spread of the books\' second-half numbers within a game: same number %.0f%%, half a point %.0f%%, a point or more %.0f%%' % (100 * (sp == 0).mean(), 100 * (sp == 0.5).mean(), 100 * (sp >= 1).mean()))

print('\n=== 8. HOW THE MARKET SETS THE SECOND-HALF SPREAD (home minus away; counting games with a pregame spread) ===')
R = G[G.spread.notna() & G.ypp_edge.notna()]
X = np.column_stack([np.ones(len(R)), -R.spread, R.hm, R.ypp_edge])
for lab, y in [('market second-half line (home expected margin)', -R.line2), ('actual second-half margin', R.m2)]:
    b, *_ = np.linalg.lstsq(X, y.values.astype(float), rcond=None)
    print('  %-46s = %+.2f %+.3f x pregame home edge %+.3f x halftime margin %+.2f x yards-per-play edge' % (lab, b[0], b[1], b[2], b[3]))
err = (R.m2 + R.line2); print('  actual minus line: mean %+.2f, standard deviation %.1f | home covers %.1f%% of decided games at the median line' % (err.mean(), err.std(), 100 * (err > 0).sum() / ((err > 0).sum() + (err < 0).sum())))
G.assign(cover_home=np.sign(G.m2 + G.line2))[['game_id', 'week', 'home', 'away', 'neutral', 'discovery', 'hm', 'lead', 'spread', 'line2', 'm2', 'flow_side', 'sr_side', 'ypp_edge', 'sr_edge', 'clean_margin', 'cover_home']].to_csv(os.path.join(HERE, 'cfb_sides_graded_2026.csv'), index=False)
