#!/usr/bin/env python3
"""The NFL totals cells put through the gate the MLB first-five-innings (Cornerstone) work used:
a cell passes only if its return is above zero in EACH period on its own with at least 40 bets in each, and it is then
re-priced one and two steps worse (-115, -120) to see how much price slip it survives.
Second-half cells: real second-half lines 2011-2021 (h2_lines_2011_2021.csv), periods 2011-2016 and 2017-2021.
Full-game wind cells: nflverse closing totals 2011 to 2026-11-09, periods 2011-2016, 2017-2021, 2022-2026.
No prices exist in either source, so -110 is the base price. Second half includes overtime.
Usage: python3 16_totals_cells_gate.py <nflverse games.csv>"""
import sys, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, 'h2_lines_2011_2021.csv')); d = d[d.h2_total_ok == 1].copy()
d['pts1'] = d.h1_home + d.h1_away; d['pts2'] = (d.fin_home + d.fin_away) - d.pts1; d['lead'] = (d.h1_home - d.h1_away).abs()
d['res'] = np.sign(d.h2_total - d.pts2)                       # +1 Under wins, -1 Over wins, 0 push
d['out'] = d.nv_roof.isin(['outdoors', 'open']) & d.nv_wind.notna()
g = pd.read_csv(sys.argv[1]); g = g[(g.season >= 2011) & g.total_line.notna() & g.home_score.notna()].copy()
g['res'] = np.sign(g.total_line - (g.home_score + g.away_score)); g['out'] = g.roof.isin(['outdoors', 'open']) & g.wind.notna()
def roi(w, l, p, price):
    n = w + l + p
    return float('nan') if n == 0 else 100 * (w * 100 / price - l) / n
def row(label, x, side=1):
    w = int((x.res == side).sum()); l = int((x.res == -side).sum()); p = int((x.res == 0).sum())
    pct = 100 * w / (w + l) if w + l else float('nan')
    return w, l, p, pct, roi(w, l, p, 110), roi(w, l, p, 115), roi(w, l, p, 120)
def cell(name, frame, mask, periods, side=1):
    x = frame[mask]; w, l, p, pct, r0, r1, r2 = row(name, x, side)
    parts, ok = [], True
    for lab, lo, hi in periods:
        y = x[(x.season >= lo) & (x.season <= hi)]; a = row(lab, y, side)
        parts.append('%s %d-%d-%d %.1f%% roi %+.1f' % (lab, a[0], a[1], a[2], a[3], a[4]))
        ok = ok and (a[0] + a[1] + a[2] >= 40) and a[4] > 0
    print('%-52s %4d-%-4d-%-3d %5.1f%%  roi at -110 %+5.1f  -115 %+5.1f  -120 %+5.1f  | %s | GATE %s' % (name, w, l, p, pct, r0, r1, r2, ' ; '.join(parts), 'PASS' if ok else 'fail'))
P2 = [('2011-16', 2011, 2016), ('2017-21', 2017, 2021)]; P3 = P2 + [('2022-26', 2022, 2026)]
print('=== UNDER cells, second half, real lines 2011-2021 ===')
cell('base rate: every game', d, d.res.notna(), P2)
cell('SCORE: first-half points 28+', d, d.pts1 >= 28, P2)
cell('SCORE-hi: first-half points 35+', d, d.pts1 >= 35, P2)
cell('WIND-A: outdoor wind 15+', d, d.out & (d.nv_wind >= 15), P2)
cell('WIND-B: outdoor wind 10-14', d, d.out & (d.nv_wind >= 10) & (d.nv_wind < 15), P2)
cell('WIND 10+ and SCORE 28+ together', d, d.out & (d.nv_wind >= 10) & (d.pts1 >= 28), P2)
cell('WIND 10+ only (first half under 28)', d, d.out & (d.nv_wind >= 10) & (d.pts1 < 28), P2)
cell('SCORE 28+ only (no wind 10+)', d, (d.pts1 >= 28) & ~(d.out & (d.nv_wind >= 10)), P2)
print('=== the old overtime worry (NFL 2H v0.4: Unders within 3 at the half were shadow-only) ===')
for lab, m in [('halftime margin 0-3', d.lead <= 3), ('halftime margin 4+', d.lead >= 4)]:
    x = d[m]; print('  %-22s games %4d, went to overtime %.1f%%' % (lab, len(x), 100 * x.ot.mean()))
cell('SCORE 28+, halftime margin 0-3', d, (d.pts1 >= 28) & (d.lead <= 3), P2)
cell('SCORE 28+, halftime margin 4+', d, (d.pts1 >= 28) & (d.lead >= 4), P2)
cell('WIND 10+, halftime margin 0-3', d, d.out & (d.nv_wind >= 10) & (d.lead <= 3), P2)
cell('WIND 10+, halftime margin 4+', d, d.out & (d.nv_wind >= 10) & (d.lead >= 4), P2)
print('=== OVER cells, second half (none was expected to pass) ===')
cell('OVER: every game', d, d.res.notna(), P2, side=-1)
cell('OVER: first-half points 13 or fewer', d, d.pts1 <= 13, P2, side=-1)
cell('OVER: dome or closed roof', d, d.nv_roof.isin(['dome', 'closed']), P2, side=-1)
cell('OVER: outdoor wind under 10', d, d.out & (d.nv_wind < 10), P2, side=-1)
print('=== UNDER cells, full game, nflverse closing totals 2011 to 2026-11-09 ===')
cell('base rate: every game', g, g.res.notna(), P3)
cell('WIND-A: outdoor wind 15+', g, g.out & (g.wind >= 15), P3)
cell('WIND-B: outdoor wind 10-14', g, g.out & (g.wind >= 10) & (g.wind < 15), P3)
cell('OVER: outdoor wind under 10', g, g.out & (g.wind < 10), P3, side=-1)
cell('OVER: dome or closed roof', g, g.roof.isin(['dome', 'closed']), P3, side=-1)
if 'under_odds' in g.columns:
    x = g[g.out & (g.wind >= 10) & g.under_odds.notna()].copy()
    dec = np.where(x.under_odds < 0, 100 / -x.under_odds, x.under_odds / 100)
    pnl = np.where(x.res == 1, dec, np.where(x.res == -1, -1.0, 0.0))
    print('full-game Under, wind 10+, at the nflverse closing Under price where it exists: n %d, roi %+.1f%% (mean price %.0f)' % (len(x), 100 * pnl.mean(), x.under_odds.mean()))
    for lab, lo, hi in P3:
        k = (x.season >= lo) & (x.season <= hi)
        if k.sum(): print('   %s n %d roi %+.1f%%' % (lab, k.sum(), 100 * pnl[k.values].mean()))
