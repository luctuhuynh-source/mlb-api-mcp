#!/usr/bin/env python3
"""Grades ROBINHOOD_TEST_PLAN_LOCKED.md: Robinhood (Kalshi) second-half spread and total contracts against the books at the same
number, at the two halftime looks, 2026 games. Written after the lock; implements its sections 2 to 4 as written.
  Book quotes:      ../halftime_pull/pulled_pull_plan.csv.gz (main line only, fresh, two or more books for a look to count)
  Robinhood quotes: kalshi_halftime_2026.csv.gz + kalshi_contracts_2026.csv (51_collect_kalshi.py); the standing bid and ask at the
                    first whole minute at or after the book snapshot's time stamp
  Fair:             median no-vig probability of the books posting exactly the contract's number (two or more)
  All-in price:     Yes = ask + 2 cents, No = 100 - bid + 2 cents.  Edge = fair - all-in.  R-03: side price 60 or less,
                    bid-ask spread 4 or less, both a bid and an ask standing
  Grading:          the contract's own settlement, stake to win $300
Usage: python3 52_grade_robinhood.py"""
import os, sys, math, statistics as st, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); HP = os.path.join(HERE, '..', 'halftime_pull'); REV = os.path.join(HERE, '..', '..', 'review_2026-11-11')
sys.path.insert(0, REV)
from nfl_halves import load, favourite_view
D = load(); F, _ = favourite_view(D); lay2 = (F.lay2ot.value_counts() / len(F)).to_dict()
def imp(a): a = float(a); return (-a) / ((-a) + 100) if a < 0 else 100 / (a + 100)
def ep(s): return int(pd.Timestamp(s).timestamp())
def convert(q_i, s_i, s_b, pm):                      # table B-NFL-3, as in ../halftime_pull/25_grade_engine_claims.py
    push_i = pm(-s_i) if float(s_i).is_integer() else 0.0
    W = q_i * (1 - push_i); lo, hi = sorted((-s_b, -s_i))
    mass = sum(pm(k) for k in range(int(np.floor(lo)) - 1, int(np.ceil(hi)) + 2) if lo < k <= hi)
    W_b = W + mass if s_b > s_i else W - mass
    push_b = pm(-s_b) if float(s_b).is_integer() else 0.0
    return W_b / (1 - push_b)

# ---------- games, books ----------
clock = pd.read_csv(os.path.join(HP, 'halftime_clock_2023_2026.csv')); clock = clock[(clock.ok == 1) & (clock.season == 2026)]
T = clock[['game_id', 'kickoff_utc', 'last_1h_play_utc', 'q3_kickoff_utc', 'look1', 'look2']].merge(
    D[['game_id', 'week', 'home', 'away', 'h1_home', 'h1_away', 'fin_home', 'fin_away', 'm2ot']].rename(columns={'home': 'h', 'away': 'a'}), on='game_id', how='left')
T['pts2'] = T.fin_home + T.fin_away - T.h1_home - T.h1_away
T = T.sort_values(['kickoff_utc', 'game_id']).reset_index(drop=True); G = T.set_index('game_id')
Q = pd.read_csv(os.path.join(HP, 'pulled_pull_plan.csv.gz'))
for c in ('point', 'price_a', 'price_b', 'age'): Q[c] = pd.to_numeric(Q[c], errors='coerce')
Q = Q.drop(columns=['home', 'away']).merge(T[['game_id', 'last_1h_play_utc', 'look1', 'look2']], on='game_id', how='inner')
Q['main'] = Q.price_a.between(-200, 200) & Q.price_b.between(-200, 200) & Q.point.notna()
Q['fresh'] = Q.age.notna() & ((pd.to_datetime(Q.ts, utc=True) - pd.to_timedelta(Q.age, unit='s')) >= pd.to_datetime(Q.last_1h_play_utc, utc=True))
Q['look'] = np.where(Q.asked == Q.look1, 1, np.where(Q.asked == Q.look2, 2, 0))
OK = Q[Q.main & Q.fresh & (Q.look > 0)].drop_duplicates(['game_id', 'market', 'look', 'book', 'point'])

# ---------- Robinhood contracts and minute rows ----------
KC = pd.read_csv(os.path.join(HERE, 'kalshi_contracts_2026.csv')); KR = pd.read_csv(os.path.join(HERE, 'kalshi_halftime_2026.csv.gz'))
KC['mk'] = np.where(KC.series == 'KXNFL2HSPREAD', 'spreads_h2', 'totals_h2'); KC['strike'] = pd.to_numeric(KC.strike)
KC['team'] = KC.suffix.str.replace(r'[^A-Z]', '', regex=True).map(lambda x: {'JAC': 'JAX', 'LAR': 'LA'}.get(x, x))
ROWS = {tk: r.sort_values('end_ts') for tk, r in KR.groupby('ticker')}
CONS = {k: v for k, v in KC.groupby(['game_id', 'mk'])}
pilot = set(pd.read_csv(os.path.join(HERE, '..', 'robinhood_pilot', 'pilot_plan.csv')).query("half == '2H'").event_ticker)
PILOT_GAMES = set(KC[KC.event.isin(pilot)].game_id)
def standing(tk, M):
    r = ROWS.get(tk)
    if r is None: return None
    i = int(np.searchsorted(r.end_ts.values, M, side='right')) - 1
    return None if i < 0 else r.iloc[i]
def r03(bid, ask, px): return bool(pd.notna(bid) and pd.notna(ask) and bid > 0 and ask < 100 and ask - bid <= 4 and px <= 60)

def build(shift=0, fee=2.0, convert_other=False):
    """Every contract side with a fair at each look that counts. convert_other=False: the same number only (two or more books on
    it). convert_other=True: the OTHER strikes within 1.5 points of the books' median number, by the conversion in force (R-07)."""
    out = []
    for (gid, mk), g in OK.groupby(['game_id', 'market']):
        cons = CONS.get((gid, mk))
        if cons is None: continue
        t = G.loc[gid]; n = {lk: g[g.look == lk].book.nunique() for lk in (1, 2)}
        pick = 1 if n[1] >= 2 else (2 if n[2] >= 2 else 0)
        for lk in (1, 2):
            x = g[g.look == lk]
            if x.book.nunique() < 2: continue
            M = int(math.ceil(ep(x.ts.iloc[0]) / 60.0)) * 60 - shift
            ia, ib = x.price_a.map(imp), x.price_b.map(imp); x = x.assign(pa=ia / (ia + ib))
            for c in cons.itertuples():
                if mk == 'spreads_h2':
                    is_home = c.team == t.h; line = -c.strike                       # the team's own line: it lays the strike
                    tl = x.point if is_home else -x.point; q = x.pa if is_home else 1 - x.pa
                else:
                    line = c.strike; tl = x.point; q = x.pa                          # Yes = Over
                same = np.isclose(tl, line); med = float(np.median(tl)); dist = abs(line - med)
                if not convert_other:
                    if same.sum() < 2: continue
                    fair_yes = 100 * float(np.median(q[same])); nb = int(same.sum())
                else:
                    if same.sum() >= 2 or dist > 1.5 or len(x) < 2: continue
                    if mk == 'spreads_h2':
                        if med < 0: pm = lambda k: lay2.get(k, 0.0)
                        elif med > 0: pm = lambda k: lay2.get(-k, 0.0)
                        else: pm = lambda k: (lay2.get(k, 0.0) + lay2.get(-k, 0.0)) / 2
                        conv = [convert(qi, li, line, pm) for qi, li in zip(q, tl)]
                    else:
                        conv = [qi - 0.015 * (line - li) / 0.5 for qi, li in zip(q, tl)]   # flat 1.5 points per half-point
                    fair_yes = 100 * float(np.median(conv)); nb = len(conv)
                s = standing(c.ticker, M); bid, ask = (s.bid, s.ask) if s is not None else (np.nan, np.nan)
                for side in ('yes', 'no'):
                    fair = fair_yes if side == 'yes' else 100 - fair_yes
                    px = ask if side == 'yes' else 100 - bid
                    kind = ('lay' if side == 'yes' else 'take') if mk == 'spreads_h2' else ('over' if side == 'yes' else 'under')
                    out.append(dict(game_id=gid, market=mk, look=lk, decision=int(lk == pick), ticker=c.ticker, team=c.team, strike=c.strike, side=side, kind=kind,
                                    nbooks=nb, dist=dist, fair=fair, bid=bid, ask=ask, px=px, allin=px + fee, edge=fair - (px + fee), ok=r03(bid, ask, px),
                                    res=1.0 if (c.result == 'yes') == (side == 'yes') else -1.0, M=M, wk=int(t.week), ko=t.kickoff_utc, pilot=int(gid in PILOT_GAMES)))
    return pd.DataFrame(out)

def money(g, step=0.0):
    c = (g.allin + step) / 100.0; risk = 300 * c / (1 - c); return np.where(g.res > 0, 300.0, -risk), risk
def roi(g, step=0.0):
    if len(g) == 0: return float('nan')
    net, risk = money(g, step); return 100 * net.sum() / risk.sum()
def rec(g): return '%d-%d' % ((g.res > 0).sum(), (g.res < 0).sum())
def best(g): return g.sort_values('edge', ascending=False).drop_duplicates(['game_id', 'market'])
def show(lab, g): print('  %-40s n %3d in %3d games  %-7s return %+6.1f%%  one cent worse %+6.1f%%  mean edge %+5.2f' % (lab, len(g), g.game_id.nunique(), rec(g), roi(g), roi(g, 1.0), g.edge.mean() if len(g) else float('nan')))

S = build(); S.to_csv(os.path.join(HERE, 'robinhood_sides_2026.csv'), index=False)
cov = [g for g in T.game_id if (g, 'spreads_h2') in CONS or (g, 'totals_h2') in CONS]; first = set(cov[:(len(cov) + 1) // 2])
S['part'] = np.where(S.game_id.isin(first), 'first half', 'second half')
Dn = S[(S.decision == 1) & S.ok]

print('=== J. COVERAGE ===')
print('games in the plan %d | with Robinhood contracts %d (spread %d, total %d)' % (len(T), len(cov), sum((g, 'spreads_h2') in CONS for g in T.game_id), sum((g, 'totals_h2') in CONS for g in T.game_id)))
for mk in ('spreads_h2', 'totals_h2'):
    gm = OK[OK.market == mk].groupby('game_id').apply(lambda g: 1 if g[g.look == 1].book.nunique() >= 2 else (2 if g[g.look == 2].book.nunique() >= 2 else 0), include_groups=False)
    whole = 0; anyhalf = 0
    for gid, pick in gm.items():
        if pick == 0: continue
        x = OK[(OK.game_id == gid) & (OK.market == mk) & (OK.look == pick)]; md = x.point.round(1).mode().iloc[0]
        whole += float(md).is_integer(); anyhalf += (x.point % 1 != 0).any()
    sn = S[(S.market == mk) & (S.decision == 1)]
    print('%s: games with a decision look %d (look 1: %d, look 2: %d, none: %d) | the books\' most common number is a whole number in %d | a same-number contract with 2+ books in %d games | of those, a side that passes R-03 in %d' % (
        mk, (gm > 0).sum(), (gm == 1).sum(), (gm == 2).sum(), len(T) - (gm > 0).sum(), whole, sn.game_id.nunique(), sn[sn.ok].game_id.nunique()))

print('\n=== H. SETTLEMENT AUDIT: the exchange\'s result against nflverse second-half points with overtime ===')
A = KC.merge(T[['game_id', 'h', 'a', 'm2ot', 'pts2']], on='game_id')
A['pred'] = np.where(A.mk == 'spreads_h2', np.where(A.team == A.h, A.m2ot, -A.m2ot) > A.strike, A.pts2 > A.strike)
A['bad'] = (A.result == 'yes') != A.pred
print('contracts %d | results yes/no %s | disagreements %d' % (len(A), A.result.value_counts().to_dict(), A.bad.sum()))
if A.bad.sum(): print(A[A.bad][['ticker', 'strike', 'result', 'm2ot', 'pts2']].head(20).to_string())
ot = D[(D.season == 2026) & ((D.reg_home != D.fin_home) | (D.reg_away != D.fin_away))].game_id
print('overtime games among them: %d (%s); contracts there whose result differs between regulation and overtime scoring: %d' % (len(ot), ', '.join(ot), int(sum(
    ((np.where(r.team == r.h, 1, -1) * (D.set_index('game_id').loc[r.game_id].m2reg) > r.strike) if r.mk == 'spreads_h2' else
     ((D.set_index('game_id').loc[r.game_id].reg_home + D.set_index('game_id').loc[r.game_id].reg_away - G.loc[r.game_id].h1_home - G.loc[r.game_id].h1_away) > r.strike)) != r.pred
    for r in A[A.game_id.isin(set(ot))].itertuples()))))

print('\n=== K1. THE FROZEN CLAIM: best same-number side per game and market at the decision look, edge 3.0 or more ===')
B = best(Dn); k1 = B[B.edge >= 3.0]
show('K1 edge 3.0 or more', k1)
for p in ('first half', 'second half'): show('   %s of the season' % p, k1[k1.part == p])
a, b = k1[k1.part == 'first half'], k1[k1.part == 'second half']
word = 'UNDERPOWERED (%d and %d entries; 40 needed in each)' % (len(a), len(b)) if min(len(a), len(b)) < 40 else ('PASSED THE SCREEN' if roi(a) > 0 and roi(b) > 0 and roi(k1, 1.0) > 0 else 'FAILED')
print('  RESULT: %s' % word)
if len(k1): print(k1.sort_values('ko')[['game_id', 'market', 'look', 'ticker', 'side', 'nbooks', 'fair', 'bid', 'ask', 'allin', 'edge', 'res']].round(1).to_string(index=False))

print('\n=== A. PRICE LEVEL: edge of every same-number side that passes R-03 (fair minus all-in price, points) ===')
def level(lab, g):
    if len(g) == 0: print('  %-34s n   0' % lab); return
    print('  %-34s n %4d in %3d games  mean %+5.2f  median %+5.2f | share at 0 or better %4.1f%%  1.0+ %4.1f%%  2.0+ %4.1f%%  3.0+ %4.1f%%' % (
        lab, len(g), g.game_id.nunique(), g.edge.mean(), g.edge.median(), 100 * (g.edge >= 0).mean(), 100 * (g.edge >= 1).mean(), 100 * (g.edge >= 2).mean(), 100 * (g.edge >= 3).mean()))
for lk in (1, 2):
    X = S[(S.look == lk) & S.ok]; print('-- look %d --' % lk); level('all sides', X)
    for mk in ('spreads_h2', 'totals_h2'):
        level(mk, X[X.market == mk])
        for kd in (('lay', 'take') if mk == 'spreads_h2' else ('over', 'under')): level('   ' + kd, X[(X.market == mk) & (X.kind == kd)])
    if lk == 2: level('games seen in the pilot (spreads)', X[(X.pilot == 1) & (X.market == 'spreads_h2')]); level('games not in the pilot (spreads)', X[(X.pilot == 0) & (X.market == 'spreads_h2')])
X = S[(S.decision == 1) & S.ok]; print('-- decision look --'); level('all sides', X); level('half the bid-ask spread, for scale', X.assign(edge=(X.ask - X.bid) / 2))

print('\n=== B. HOW OFTEN: games per 100 whose best same-number side (R-03 passed) is at least this good ===')
for lk in (1, 2):
    X = S[(S.look == lk) & S.ok]; ng = S[S.look == lk].game_id.nunique(); bg = X.groupby('game_id').edge.max()
    print('  look %d: %3d games with a same-number contract | ' % (lk, ng) + ' | '.join('%s: %d games (%.1f per 100)' % (lab, (bg >= th).sum(), 100 * (bg >= th).sum() / max(ng, 1)) for lab, th in [('3.0+', 3), ('2.0+', 2), ('1.0+', 1), ('0 or better', 0)]))

print('\n=== C. BANDS: best side per game and market at the decision look ===')
for lab, lo, hi in [('3.0 or more', 3, 99), ('2.0 to 2.9', 2, 3), ('1.0 to 1.9', 1, 2), ('0 to 0.9', 0, 1), ('below 0', -99, 0)]: show(lab, B[(B.edge >= lo) & (B.edge < hi)])
show('0 or better, all together', B[B.edge >= 0]); show('every best side', B)
for mk in ('spreads_h2', 'totals_h2'): show('   0 or better, %s' % mk, B[(B.edge >= 0) & (B.market == mk)])
print('  every same-number side that passes R-03 (not only the best), by kind:')
for kd in ('lay', 'take', 'over', 'under'): show('   ' + kd, Dn[Dn.kind == kd])

print('\n=== D. DOES IT LAST: look-1 prices, the same contract and side later ===')
S1, S2 = S[(S.look == 1) & S.ok], S[S.look == 2].set_index(['ticker', 'side'])
for lab, th in [('3.0 or more', 3.0), ('0 or better', 0.0)]:
    X = S1[S1.edge >= th]; parts = []
    for k in (1, 2, 3, 5):
        still = tot = 0
        for r in X.itertuples():
            s = standing(r.ticker, r.M + 60 * k)
            if s is None: continue
            px = s.ask if r.side == 'yes' else 100 - s.bid; tot += 1; still += bool(pd.notna(px) and px <= r.px)
        parts.append('%d min: %d of %d' % (k, still, tot))
    j = X.join(S2[['fair', 'edge', 'ok']].rename(columns={'fair': 'fair2', 'edge': 'edge2', 'ok': 'ok2'}), on=['ticker', 'side'], how='inner')
    print('  %s at look 1: %d sides. Same price or better still standing after %s' % (lab, len(X), ' | '.join(parts)))
    if len(j): print('     books still on that number at look 2 for %d of them: look-1 price against the look-2 fair %+5.2f on average (%d still 3.0+, %d still 0 or better); Robinhood\'s own look-2 price: edge %+5.2f on average' % (
        len(j), (j.fair2 - j.allin).mean(), ((j.fair2 - j.allin) >= 3).sum(), ((j.fair2 - j.allin) >= 0).sum(), j[j.ok2].edge2.mean()))

print('\n=== E. RESTING ORDERS (flatters the order: first in the queue, enough contracts traded) ===')
def resting(target_gap, fee=2.0):
    out = []
    L1 = S[S.look == 1].sort_values('nbooks', ascending=False).drop_duplicates(['game_id', 'market', 'side', 'ticker'])
    for r in L1.itertuples():
        Tp = min(60, math.floor(r.fair - target_gap - fee + 1e-9))
        if Tp < 1: continue
        if pd.notna(r.px) and r.px <= Tp: continue                                  # already a taker price: belongs to K1
        rows = ROWS.get(r.ticker); Mq = (ep(G.loc[r.game_id].q3_kickoff_utc) // 60) * 60
        w = rows[(rows.end_ts > r.M) & (rows.end_ts <= Mq)] if rows is not None else None
        if w is None or len(w) == 0: fill = False
        elif r.side == 'yes': fill = bool((w.ask_low.fillna(w.ask).min() <= Tp) or (w.trade_low.min() <= Tp))
        else: fill = bool((w.bid_high.fillna(w.bid).max() >= 100 - Tp) or (w.trade_high.max() >= 100 - Tp))
        f2 = S2.fair.get((r.ticker, r.side), np.nan) if (r.ticker, r.side) in S2.index else np.nan
        out.append(dict(game_id=r.game_id, market=r.market, ticker=r.ticker, side=r.side, kind=r.kind, fair=r.fair, px_now=r.px, T=Tp, allin=Tp + fee, edge=r.fair - Tp - fee, filled=int(fill), res=r.res, fair_move=f2 - r.fair, ko=r.ko))
    return pd.DataFrame(out)
for lab, gap in [('T = 3.0 below the fair after the fee (the engine floor)', 3.0), ('T = at the fair after the fee', 0.0)]:
    R = resting(gap); R.to_csv(os.path.join(HERE, 'robinhood_resting_gap%d_2026.csv' % int(gap)), index=False)
    f, u = R[R.filled == 1], R[R.filled == 0]
    print('-- %s --' % lab)
    print('  orders placed %d in %d games | filled %d (%.0f%%) | the standing price was %.1f cents above T on average' % (len(R), R.game_id.nunique(), len(f), 100 * len(f) / max(len(R), 1), (R.px_now - R['T']).mean()))
    show('filled orders, graded at T + 2', f); show('unfilled orders, had they filled', u)
    print('  how the fair moved by look 2 (points, for the order\'s side; minus = against the order): filled %+5.2f on %d | unfilled %+5.2f on %d' % (f.fair_move.mean(), f.fair_move.notna().sum(), u.fair_move.mean(), u.fair_move.notna().sum()))
    for kd in ('lay', 'take', 'over', 'under'): show('   filled, ' + kd, f[f.kind == kd])
    show('   filled, one per game and market (first by kickoff)', f.sort_values('ko').drop_duplicates(['game_id', 'market']))

print('\n=== F. OTHER STRIKES, by the conversion in force (R-07): spreads by table B-NFL-3, totals by 1.5 points per half-point ===')
O = build(convert_other=True); O.to_csv(os.path.join(HERE, 'robinhood_other_strikes_2026.csv'), index=False)
On = O[(O.decision == 1) & O.ok]
for mk in ('spreads_h2', 'totals_h2'):
    for lab, m_ in [('half a point from the books\' median', On.dist <= 0.5), ('1.0 to 1.5 points away', On.dist > 0.5)]:
        Bm = best(On[(On.market == mk) & m_]); print('-- %s, %s: %d games --' % (mk, lab, Bm.game_id.nunique()))
        for bl, lo, hi in [('3.0 or more', 3, 99), ('2.0 to 2.9', 2, 3), ('0 to 1.9', 0, 2), ('below 0', -99, 0)]: show(bl, Bm[(Bm.edge >= lo) & (Bm.edge < hi)])

print('\n=== G. LIQUIDITY: same-number contracts at the decision look ===')
Y = S[(S.decision == 1) & (S.side == 'yes')]; w = (Y.ask - Y.bid)
print('contracts %d | no bid or no ask: %d | bid-ask spread: median %.0f cents, 1 cent %.0f%%, 2 cents %.0f%%, 3 to 4 %.0f%%, wider than 4 %.0f%%' % (
    len(Y), int((Y.bid.isna() | Y.ask.isna() | (Y.bid <= 0) | (Y.ask >= 100)).sum()), w.median(), 100 * (w <= 1).mean(), 100 * ((w > 1) & (w <= 2)).mean(), 100 * ((w > 2) & (w <= 4)).mean(), 100 * (w > 4).mean()))
Z = S[S.decision == 1]; print('sides %d | pass R-03 %d (%.0f%%) | fail on the spread %d | fail on the 60-cent cap only %d' % (len(Z), Z.ok.sum(), 100 * Z.ok.mean(), ((Z.ask - Z.bid) > 4).sum(), ((Z.px > 60) & ((Z.ask - Z.bid) <= 4)).sum()))
vol = []
for r in Y.itertuples():
    rows = ROWS.get(r.ticker); t = G.loc[r.game_id]
    vol.append(0.0 if rows is None else rows[(rows.end_ts > ep(t.last_1h_play_utc)) & (rows.end_ts <= ep(t.q3_kickoff_utc))].volume.fillna(0).sum())
vol = pd.Series(vol); print('contracts traded during halftime, per same-number contract: median %.0f, lowest quarter under %.0f, share with none %.0f%%' % (vol.median(), vol.quantile(.25), 100 * (vol == 0).mean()))

print('\n=== I. SENSITIVITY ===')
for lab, kw in [('as locked', {}), ('Robinhood quote one minute earlier', dict(shift=60)), ('fee 1 cent', dict(fee=1.0))]:
    X = build(**kw); Xn = X[(X.decision == 1) & X.ok]; Bx = best(Xn); k = Bx[Bx.edge >= 3.0]
    print('  %-36s mean edge %+5.2f | best side 3.0+: %d entries %s return %+6.1f%% | 0 or better: %d entries %s return %+6.1f%%' % (lab, Xn.edge.mean(), len(k), rec(k), roi(k), (Bx.edge >= 0).sum(), rec(Bx[Bx.edge >= 0]), roi(Bx[Bx.edge >= 0])))
