#!/usr/bin/env python3
"""Round-2 claim R1 of ROUND2_TEST_PLAN_LOCKED.md: the totals number table, tested by letting each book take a turn as the venue
against the other books ACROSS numbers on the 990 real second-half totals.
  table:  p(k | L) = g(k) x normal((k - L) / s), rescaled; g = share of second halves (overtime in) with exactly k points 2011-2022;
          s = sd of second-half points minus the closing second-half line 2011-2021; L = median number of the other books.
  move:   three outcomes (win, tie, loss). From a book at n: P(points below n) = U x (1 - p(n)) on a whole number, U on a half-point.
          To the venue's number v: add p(k) for whole k with n <= k < v, or subtract for v <= k < n.
  claim:  edge 3.0 or more, ONE wager per game (largest edge among all books and both sides), graded at that book's number and price.
The cleaning and money rules are those of 24_grade_totals_claims.py (its top is run here as is).
Usage: python3 29_grade_number_table.py <nflverse games.csv>"""
import sys, os, statistics as st, numpy as np, pandas as pd
from scipy import stats
HERE = os.path.dirname(os.path.abspath(__file__)); REV = os.path.join(HERE, '..', '..', 'review_2026-11-11')
exec(open(os.path.join(HERE, '24_grade_totals_claims.py')).read().split("Q2 = load('pull_plan', 'totals_h2')")[0])

# ---------- the table, from results before the test period only ----------
A = pd.read_csv(os.path.join(HERE, '..', 'h2_lines_2011_2021.csv')); A['pts2'] = (A.fin_home + A.fin_away) - (A.h1_home + A.h1_away)
B = pd.read_csv(os.path.join(REV, 'halves_2015_2026.csv')); B = B[B.season == 2022].copy(); B['pts2'] = (B.fin_home + B.fin_away) - (B.h1_home + B.h1_away)
allp = pd.concat([A.pts2, B.pts2]).astype(int); KMAX = 90
g = np.array([(allp == k).sum() for k in range(KMAX + 1)], dtype=float); n_g = g.sum(); g = g / n_g
ok_lines = A[A.h2_total_ok == 1]; SIG = float((ok_lines.pts2 - ok_lines.h2_total).std())
print('table built on %d second halves (2011-2022); s = %.2f points' % (int(n_g), SIG))
print('second halves landing exactly on k (count of %d): ' % int(n_g) + ', '.join('%d: %d' % (k, int(round(g[k] * n_g))) for k in range(13, 32)))
KS = np.arange(KMAX + 1)
def masses(L, scale=1.0):
    w = g * stats.norm.pdf((KS - L) / SIG); w = w / w.sum(); return w * scale
def below(n, U, p):
    """P(points strictly below the number n) from a no-vig Under probability U quoted at n."""
    return U * (1 - p[int(n)]) if float(n).is_integer() else U
def move(c, n, v, p):
    if v > n: return c + sum(p[k] for k in range(int(np.ceil(n)), int(np.ceil(v))))            # whole k with n <= k < v
    if v < n: return c - sum(p[k] for k in range(int(np.ceil(v)), int(np.ceil(n))))            # whole k with v <= k < n
    return c
def fair_at(venue_n, others, p):
    """Fair conditional-on-no-tie win probability of the Under and of the Over at the venue's number."""
    cu = []
    for o in others:
        io, iu = be(o[1]), be(o[2]); U = iu / (io + iu)
        cu.append(move(below(o[0], U, p), o[0], venue_n, p))
    tie = p[int(venue_n)] if float(venue_n).is_integer() else 0.0
    und = [c / (1 - tie) for c in cu]; ovr = [(1 - c - tie) / (1 - tie) for c in cu]
    return st.median(und), st.median(ovr), max(und) - min(und)

Q2 = load('pull_plan', 'totals_h2'); D2, st2, ok2 = decision_quotes(Q2, True)
res_ = T.set_index('game_id')[['pts2_ot', 'per', 'season']]

def standin(scale):
    rows = []
    for gid, x in D2.groupby('game_id'):
        if x.book.nunique() < 3: continue
        q = [(r.book, float(r.point), float(r.price_a), float(r.price_b)) for r in x.itertuples()]
        for b, n, pa, pb in q:
            oth = [(o[1], o[2], o[3]) for o in q if o[0] != b]
            if len(oth) < 2: continue
            L = st.median([o[0] for o in oth]); p = masses(L, scale)
            fu, fo, spread = fair_at(n, oth, p)
            for side, fair, price in (('under', fu, pb), ('over', fo, pa)):
                rows.append(dict(game_id=gid, book=b, side=side, point=n, price=price, fair=100 * fair, edge=100 * (fair - be(price)), L=L, gap=n - L, others=len(oth), fair_range=100 * spread))
    return pd.DataFrame(rows)
def grade(e, step=0.0):
    e = e.merge(res_, left_on='game_id', right_index=True)
    pr = e.price.map(be) + step; e['risk'] = 300 * pr / (1 - pr)
    diff = np.where(e.side == 'under', e.point - e.pts2_ot, e.pts2_ot - e.point); e['res'] = np.sign(diff)
    e['net'] = np.where(e.res > 0, 300.0, np.where(e.res < 0, -e.risk, 0.0)); return e
def r_(e): return float('nan') if len(e) == 0 else 100 * e.net.sum() / e.risk.sum()
def rec(e): return '%d-%d-%d' % ((e.res > 0).sum(), (e.res < 0).sum(), (e.res == 0).sum())
def lcb_(e, z):
    if len(e) < 5: return float('nan')
    x = e.net / e.risk.mean(); r = e.net.sum() / e.risk.sum(); se = (e.net - r * e.risk).std(ddof=1) * np.sqrt(len(e)) / e.risk.sum(); return 100 * (r - z * se)
L2 = ok2[ok2.look == 2][['game_id', 'book', 'point', 'price_a', 'price_b']].rename(columns={'point': 'point2', 'price_a': 'pa2', 'price_b': 'pb2'})
pick = D2.groupby('game_id').pick.first()
def latency(entries):
    """The same book and side five minutes later (look 2), at whatever number and price it then shows."""
    e = entries[entries.game_id.map(pick) == 1].merge(L2, on=['game_id', 'book'], how='left')
    missed = int(e.point2.isna().sum()); e = e[e.point2.notna()].copy()
    e['point'] = e.point2; e['price'] = np.where(e.side == 'under', e.pb2, e.pa2)
    return grade(e), missed, int((entries.game_id.map(pick) != 1).sum())
def report(scale, show=True):
    S = standin(scale); best = S.sort_values('edge', ascending=False).drop_duplicates('game_id'); ent = best[best.edge >= 3.0]
    e, e1 = grade(ent), grade(ent, 0.01); lat, missed, nolater = latency(ent)
    a, b = e[e.per == '2023-24'], e[e.per == '2025-26']
    if len(a) < 40 or len(b) < 40: v = 'UNDERPOWERED (%d and %d games)' % (len(a), len(b))
    else: v = 'PASSED THE SCREEN' if (r_(a) > 0 and r_(b) > 0 and r_(e1) > 0 and r_(lat) > 0) else 'FAILED'
    if show:
        print('games with 3+ books at the decision look: %d | book-sides priced: %d | mean edge %+.2f' % (S.game_id.nunique(), len(S), S.edge.mean()))
        print('R1  edge 3.0+, one wager per game: n %d  %s  %.1f%% won  return %+.1f%%  | one step worse %+.1f%% | 2023-24 n %d %s %+.1f%% ; 2025-26 n %d %s %+.1f%%' % (
            len(e), rec(e), 100 * (e.res > 0).sum() / max(1, (e.res != 0).sum()), r_(e), r_(e1), len(a), rec(a), r_(a), len(b), rec(b), r_(b)))
        print('    five minutes later, same book and side: n %d  %s  return %+.1f%%  (book had pulled the market: %d; no later look: %d)' % (len(lat), rec(lat), r_(lat), missed, nolater))
        print('    cautious end of the return: %+.1f%% plain, %+.1f%% allowing for two claims | %s' % (lcb_(e, 1.645), lcb_(e, 1.96), v))
    return S, best, e, v

print('\n=== CONVERSION CHECK ===')
dq = D2[(D2.point % 1) == 0].drop_duplicates(['game_id', 'point']).merge(res_, left_on='game_id', right_index=True)
med = D2.groupby('game_id').point.median(); dq['pred'] = [masses(med[gid])[int(n)] for gid, n in zip(dq.game_id, dq.point)]; dq['tie'] = (dq.pts2_ot == dq.point).astype(int)
se = np.sqrt(dq.tie.mean() * (1 - dq.tie.mean()) / len(dq))
print('V1 whole-number lines 2023-2026: %d game-numbers | ties predicted by the table %.1f%% | ties that happened %.1f%% (standard error %.1f) | gap %.1f standard errors -> %s' % (
    len(dq), 100 * dq.pred.mean(), 100 * dq.tie.mean(), 100 * se, abs(dq.pred.mean() - dq.tie.mean()) / se, 'PASSES' if abs(dq.pred.mean() - dq.tie.mean()) < 2 * se else 'FAILS'))
for k in sorted(dq.point.unique()):
    y = dq[dq.point == k]
    if len(y) >= 25: print('     line %2d: n %3d  predicted %.1f%%  happened %.1f%%' % (k, len(y), 100 * y.pred.mean(), 100 * y.tie.mean()))
print('V2 what the books charge for crossing a number (pairs of books one point apart on half-points, same look), beside the table:')
pairs = []
for gid, x in D2.groupby('game_id'):
    h = x[(x.point % 1) != 0]; L = float(x.point.median())
    for n in sorted(h.point.unique()):
        a_, b_ = h[h.point == n], h[h.point == n + 1]
        if len(a_) and len(b_):
            ua = np.mean([be(r.price_b) / (be(r.price_a) + be(r.price_b)) for r in a_.itertuples()]); ub = np.mean([be(r.price_b) / (be(r.price_a) + be(r.price_b)) for r in b_.itertuples()])
            pairs.append(dict(k=int(n + 0.5), market=100 * (ub - ua), table=100 * masses(L)[int(n + 0.5)]))
P = pd.DataFrame(pairs)
if len(P):
    print('     all pairs: n %d | books charge %.1f points | table says %.1f points' % (len(P), P.market.mean(), P.table.mean()))
    print('     by number crossed: ' + ' ; '.join('%d: books %.1f, table %.1f (n %d)' % (k, y.market.mean(), y.table.mean(), len(y)) for k, y in P.groupby('k') if len(y) >= 15))
print('     for comparison the engine today uses a flat 3.0 points for a full point (1.5 per half-point)')

print('\n=== R1, the claim ===')
S, best, e, v = report(1.0)
print('\n=== the same with every table value cut by a quarter, then raised by a quarter ===')
vs = [v]
for sc in (0.75, 1.25):
    S_, b_, e_, v_ = report(sc, show=False); a_, bb = e_[e_.per == '2023-24'], e_[e_.per == '2025-26']; vs.append(v_)
    print('  x%.2f: n %d  %s  return %+.1f%%  (2023-24 %+.1f%%, 2025-26 %+.1f%%)  %s' % (sc, len(e_), rec(e_), r_(e_), r_(a_), r_(bb), v_))
print('R1 VERDICT:', 'PASSED THE SCREEN' if all(x == 'PASSED THE SCREEN' for x in vs) else ('UNDERPOWERED' if vs[0].startswith('UNDERPOWERED') else 'FAILED'))

print('\n=== FOR INFORMATION ONLY ===')
for side in ('under', 'over'):
    y = e[e.side == side]; print('  3.0+ entries on the %s: n %d  %s  return %+.1f%%' % (side.capitalize(), len(y), rec(y), r_(y)))
for lab, m in [('venue number half a point off the others', e.gap.abs() <= 0.5), ('one point off', (e.gap.abs() > 0.5) & (e.gap.abs() <= 1.0)), ('more than one point off', e.gap.abs() > 1.0)]:
    y = e[m]; print('  %-42s n %3d  %s  return %+.1f%%' % (lab, len(y), rec(y), r_(y)))
gb = grade(best)
for lab, lo, hi in [('2.0 to 2.9', 2, 3), ('1.0 to 1.9', 1, 2), ('0 to 0.9', 0, 1), ('below 0', -99, 0)]:
    y = gb[(gb.edge >= lo) & (gb.edge < hi)]; print('  best edge in the game %-11s n %3d  %s  return %+.1f%%' % (lab, len(y), rec(y), r_(y)))
print('  how often: a 3.0+ number gap in %d of %d games (%.0f%%); by season %s' % (len(e), S.game_id.nunique(), 100 * len(e) / S.game_id.nunique(), e.groupby('season').size().to_dict()))
print('  who hangs them:', e.book.value_counts().to_dict())
print('  with the flat 1.5 per half-point instead of the table, the same test:')
def standin_flat():
    rows = []
    for gid, x in D2.groupby('game_id'):
        if x.book.nunique() < 3: continue
        q = [(r.book, float(r.point), float(r.price_a), float(r.price_b)) for r in x.itertuples()]
        for b, n, pa, pb in q:
            oth = [o for o in q if o[0] != b]
            if len(oth) < 2: continue
            und = [be(o[3]) / (be(o[2]) + be(o[3])) + 0.03 * (n - o[1]) for o in oth]; fu = st.median(und)
            for side, fair, price in (('under', fu, pb), ('over', 1 - fu, pa)):
                rows.append(dict(game_id=gid, book=b, side=side, point=n, price=price, edge=100 * (fair - be(price)), gap=n - st.median([o[1] for o in oth])))
    return pd.DataFrame(rows)
F_ = standin_flat(); fb = F_.sort_values('edge', ascending=False).drop_duplicates('game_id'); fe = grade(fb[fb.edge >= 3.0])
print('     n %d  %s  return %+.1f%%  (2023-24 %+.1f%%, 2025-26 %+.1f%%)' % (len(fe), rec(fe), r_(fe), r_(fe[fe.per == '2023-24']), r_(fe[fe.per == '2025-26'])))
e.to_csv(os.path.join(HERE, 'number_table_entries_2023_2026.csv'), index=False)
pd.DataFrame(dict(k=KS[:61], share_2011_2022=g[:61])).to_csv(os.path.join(HERE, 'second_half_landing_shares_2011_2022.csv'), index=False)
