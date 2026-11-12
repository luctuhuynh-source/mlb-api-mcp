#!/usr/bin/env python3
"""The ledger's own 46 half bets (10/18 to 11/5/2026: 42 leans, 4 fires), split by how the price taken compared with the
closing fair (clv_minus_margin in the two CLV files: closing no-vig fair minus the price's break-even)."""
import os, pandas as pd
from scipy.stats import fisher_exact
HERE = os.path.dirname(os.path.abspath(__file__))
a = pd.read_csv(os.path.join(HERE, '..', 'clv_1h_2026-10-18_to_11-05.csv')); b = pd.read_csv(os.path.join(HERE, '..', 'clv_2h_2026-10-18_to_11-05.csv'))
x = pd.concat([a[a.cls != 'FG lean'], b]); e = 100 * x.clv_minus_margin
def rec(g): return '%d-%d-%d' % ((g.result == 'W').sum(), (g.result == 'L').sum(), (g.result == 'P').sum())
print('half bets with a closing price: %d, overall %s' % (len(x), rec(x)))
for lab, lo, hi in [('3.0 or more better than fair', 3, 99), ('2.0 to 2.9', 2, 3), ('1.0 to 1.9', 1, 2), ('0 to 0.9', 0, 1), ('0 to 1.0 worse', -1, 0), ('1.0 to 2.0 worse', -2, -1), ('more than 2.0 worse', -99, -2)]:
    g = x[(e >= lo) & (e < hi)]; print('  %-30s n %2d  %s' % (lab, len(g), rec(g)))
g1 = x[e >= 0]; g0 = x[e < 0]
p = fisher_exact([[(g1.result == 'W').sum(), (g1.result == 'L').sum()], [(g0.result == 'W').sum(), (g0.result == 'L').sum()]])[1]
print('at fair or better: n %d, %s | worse than fair: n %d, %s | Fisher exact p = %.2f' % (len(g1), rec(g1), len(g0), rec(g0), p))
