#!/usr/bin/env python3
"""Written AFTER the R1 result was seen: description only, no bet is graded and no game result is read.
For the R1 entries (a book whose second-half total sat 3.0+ points of value away from the other books at the first halftime look):
five minutes later, who moved? Did the other books come to the odd book's number (it was early), or did it go back to theirs (it was stale)?
Usage: python3 30_number_gap_who_moved.py <nflverse games.csv>"""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '24_grade_totals_claims.py')).read().split("Q2 = load('pull_plan', 'totals_h2')")[0])
Q2 = load('pull_plan', 'totals_h2'); D2, st2, ok2 = decision_quotes(Q2, True)
E = pd.read_csv(os.path.join(HERE, 'number_table_entries_2023_2026.csv')); pick = D2.groupby('game_id').pick.first()
E = E[E.game_id.map(pick) == 1]; L1, L2 = ok2[ok2.look == 1], ok2[ok2.look == 2]; rows = []
for r in E.itertuples():
    a, b = L1[(L1.game_id == r.game_id) & (L1.book != r.book)], L2[(L2.game_id == r.game_id) & (L2.book != r.book)]; own = L2[(L2.game_id == r.game_id) & (L2.book == r.book)]
    if len(a) < 2 or len(b) < 2 or own.empty: continue
    gap1 = r.point - a.point.median(); pack_move = b.point.median() - a.point.median(); own_move = float(own.point.iloc[0]) - r.point; s = np.sign(gap1)
    rows.append(dict(game_id=r.game_id, book=r.book, side=r.side, gap1=gap1, pack_toward=s * pack_move, own_toward=-s * own_move, gap2=float(own.point.iloc[0]) - b.point.median()))
M = pd.DataFrame(rows); n = len(M)
print('entries with a later look and two or more other books at both looks: %d' % n)
print('gap at the first look (odd book minus the others, in points): mean size %.2f' % M.gap1.abs().mean())
print('five minutes later: the others had moved toward the odd book in %d (%.0f%%), away in %d, not at all in %d' % ((M.pack_toward > 0).sum(), 100 * (M.pack_toward > 0).mean(), (M.pack_toward < 0).sum(), (M.pack_toward == 0).sum()))
print('                    the odd book had moved toward the others in %d (%.0f%%), away in %d, not at all in %d' % ((M.own_toward > 0).sum(), 100 * (M.own_toward > 0).mean(), (M.own_toward < 0).sum(), (M.own_toward == 0).sum()))
print('mean move toward each other: the others %.2f points, the odd book %.2f points | gap left: mean size %.2f' % (M.pack_toward.mean(), M.own_toward.mean(), M.gap2.abs().mean()))
print('by book (odd book moved toward the others, mean points / the others moved toward it, mean points / n):')
for b, y in M.groupby('book'):
    if len(y) >= 10: print('   %-15s %.2f / %.2f / %d' % (b, y.own_toward.mean(), y.pack_toward.mean(), len(y)))
