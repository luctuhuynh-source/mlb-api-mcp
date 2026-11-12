#!/usr/bin/env python3
"""Detail tables for the Robinhood pilot, from robinhood_vs_fair.csv (written by 31_robinhood_vs_fair.py).
Near strikes = within 3.5 points of the books' line. 'Clean' comparisons = first half, and second-half contracts
that no overtime result can change. Far strikes are shown apart: table B-NFL-3 was not built for them."""
import os, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(os.path.join(HERE, 'robinhood_vs_fair.csv'))
pd.set_option('display.width', 220)
V = R[R.passes_venue]
def roi(x):
    pnl = np.where(x.won, 100 - x.all_in, -x.all_in).sum(); return pnl / x.all_in.sum() * 100
near = V[V.dist_from_books <= 3.5]
print('near strikes that pass venue rules, by half / ot_safe')
for (h, o), x in near.groupby(['half', 'ot_safe']):
    print(h, 'ot_safe' if o else 'ot_could_matter', len(x), 'sides', x.game.nunique(), 'games  mean edge %.2f median %.2f  share edge>=0: %.1f%%  n>=0: %d in %d games' % (x.edge.mean(), x.edge.median(), 100 * (x.edge >= 0).mean(), (x.edge >= 0).sum(), x[x.edge >= 0].game.nunique()))
clean = near[(near.half == '1H') | (near.ot_safe)]
b = clean.groupby(['half', 'game']).edge.max().reset_index()
print('\nbest clean near-strike edge per game: n games', len(b))
print(b.groupby('half').edge.describe().round(2).to_string())
print('games with best edge >= 0:', (b.edge >= 0).sum(), ' >=1:', (b.edge >= 1).sum(), ' >=2:', (b.edge >= 2).sum(), ' >=3:', (b.edge >= 3).sum())
print('\nnear-strike all-in price: median %.0f, min %.0f, max %.0f' % (near.all_in.median(), near.all_in.min(), near.all_in.max()))
ap = near[(near.half == '2H') & (~near.ot_safe) & (near.edge >= 2)].sort_values('edge', ascending=False)
print('\n2H overtime-could-matter, edge >= 2.0:'); print(ap[['game', 'contract', 'side', 'price', 'all_in', 'fair', 'edge', 'dist_from_books', 'fair_range', 'won']].to_string(index=False))
far = V[V.dist_from_books > 3.5]
print('\nFAR strikes (more than 3.5 from the books) that pass venue rules:', len(far), 'sides in', far.game.nunique(), 'games; mean edge %.2f' % far.edge.mean())
for lab, lo, hi in [('3.0+', 3, 99), ('1.0 to 2.9', 1, 3), ('-1 to 0.9', -1, 1), ('worse than -1', -99, -1)]:
    x = far[(far.edge >= lo) & (far.edge < hi)]
    if len(x): print('  edge %-14s %3d sides %2d games  record %d-%d  avg all-in %.1f  win%% %.1f  ROI %+.1f%%' % (lab, len(x), x.game.nunique(), x.won.sum(), (~x.won).sum(), x.all_in.mean(), 100 * x.won.mean(), roi(x)))
x = far[far.edge >= 3]
g = x.groupby(['half', 'game']).agg(n=('won', 'size'), w=('won', 'sum')).reset_index(); print(g.to_string(index=False))
print('\nALL near strikes record by edge bucket (clean only):')
for lab, lo, hi in [('>=0', 0, 99), ('-2 to 0', -2, 0), ('-4 to -2', -4, -2), ('< -4', -99, -4)]:
    x = clean[(clean.edge >= lo) & (clean.edge < hi)]
    print('  %-10s %3d sides  record %d-%d  ROI %+.1f%%' % (lab, len(x), x.won.sum(), (~x.won).sum(), roi(x) if len(x) else 0))
