#!/usr/bin/env python3
"""Totals in NFL halves: which numbers matter and what a half-point is worth.
A. Second half, on REAL 2H total lines 2011-2021 (h2_lines_2011_2021.csv): push rate of whole-number lines, and how often the
   half lands exactly on the whole number next to a half-number line. That is the value of a half-point on a total.
B. First half and second half, 2015-2026 (nflverse half scores, 3,164 games): how often each exact total lands, overall and
   among games whose derived half total (0.50 x the closing full-game total, the protocol's diagnostic) is within 2 of it.
The protocol's rule under test: totals move 1.5 probability points per half-point (R-07, 'unchanged and untested');
key numbers 1H 13/17/20/23 (F-14)."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'review_2026-11-11'))
from nfl_halves import load
d = pd.read_csv(os.path.join(HERE, 'h2_lines_2011_2021.csv'))
T = d[d.h2_total_ok == 1].copy(); T['pts2'] = (T.fin_home + T.fin_away) - (T.h1_home + T.h1_away); T['pts2reg'] = (T.reg_home + T.reg_away) - (T.h1_home + T.h1_away)
print('=== A. Second-half totals on real lines, 2011-2021 (n = %d), second half incl. overtime ===' % len(T))
whole = T[T.h2_total == T.h2_total.round()]; half = T[T.h2_total != T.h2_total.round()]
print('whole-number lines: %d, pushed %d = %.1f%%' % (len(whole), (whole.pts2 == whole.h2_total).sum(), 100 * (whole.pts2 == whole.h2_total).mean()))
up = (half.pts2 == half.h2_total + 0.5).mean(); dn = (half.pts2 == half.h2_total - 0.5).mean()
print('half-number lines: %d. Lands exactly on the whole number just ABOVE the line %.1f%%, just BELOW %.1f%%' % (len(half), 100 * up, 100 * dn))
print('  -> a full point across a whole number moves the win probability by that number\'s share, so a half-point is worth about half of it:')
print('     about %.1f points of win probability per half-point on average (the rule says a flat 1.5)' % (100 * (up + dn) / 4))
print(' by the whole number involved (line on it, or half a point either side):')
rows = []
for N in range(16, 29):
    near = T[(T.h2_total - N).abs() <= 0.5]
    if len(near) < 80: continue
    rows.append((N, len(near), 100 * (near.pts2 == N).mean(), 100 * (near.pts2reg == N).mean()))
print('   number   games with the line within half a point   lands exactly on it (incl. OT)   (regulation only)')
for N, n, p, pr in rows: print('   %4d %10d %38.1f%% %24.1f%%' % (N, n, p, pr))
allp = np.mean([(T[(T.h2_total - N).abs() <= 0.5].pts2 == N).mean() for N in range(16, 29) if len(T[(T.h2_total - N).abs() <= 0.5]) >= 80])
print('   plain average across those numbers: %.1f%% -> %.1f per half-point' % (100 * allp, 50 * allp))

h = load(); h['p1'] = h.h1_home + h.h1_away; h['p2'] = (h.fin_home + h.fin_away) - h.p1; h['p2reg'] = (h.reg_home + h.reg_away) - h.p1
h = h[h.total_line.notna()]
print()
print('=== B. Exact half totals, 2015-2026 (n = %d) ===' % len(h))
for lab, col, rng in [('FIRST HALF', 'p1', range(10, 32)), ('SECOND HALF incl. overtime', 'p2', range(10, 32))]:
    freq = h[col].value_counts(normalize=True)
    print(' %s: most common exact totals: %s' % (lab, ', '.join('%d (%.1f%%)' % (k, 100 * v) for k, v in freq.head(10).items())))
    print('   number   all games   games whose derived half total is within 2 of it (n)')
    for N in rng:
        near = h[(0.5 * h.total_line - N).abs() <= 2]
        if len(near) < 150: continue
        print('   %4d %9.1f%% %12.1f%%  (%d)' % (N, 100 * freq.get(N, 0), 100 * (near[col] == N).mean(), len(near)))
print()
print('first-half points as a share of the closing full-game total: mean %.3f, median %.3f (the dead v0.2 line said 0.485; F-13 uses 0.50 as a diagnostic)' % ((h.p1 / h.total_line).mean(), (h.p1 / h.total_line).median()))
print('first-half points: mean %.2f | second half incl. OT: mean %.2f | regulation second half: mean %.2f' % (h.p1.mean(), h.p2.mean(), h.p2reg.mean()))
for lab, col in [('1H', 'p1'), ('2H incl. OT', 'p2')]:
    o = (h[col] > 0.5 * h.total_line).sum(); u = (h[col] < 0.5 * h.total_line).sum()
    print('%s vs 0.50 x full-game total: over %d, under %d (%.1f%% over)' % (lab, o, u, 100 * o / (o + u)))
