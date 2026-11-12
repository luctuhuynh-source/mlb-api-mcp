#!/usr/bin/env python3
"""Screen of QB_UNDER_SCREEN_PLAN.md: second-half Under when the first half was slow (combined yards per play in the bottom third)
and both teams completed under 55% of their first-half passes. Cleaning and money rules: the top of 24_grade_totals_claims.py.
Usage: python3 31_qb_under_screen.py <nflverse games.csv> <folder with pbp_YYYY.parquet>"""
import sys, os, numpy as np, pandas as pd, pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); PBP = sys.argv[2]
exec(open(os.path.join(HERE, '24_grade_totals_claims.py')).read().split("Q2 = load('pull_plan', 'totals_h2')")[0])
Q2 = load('pull_plan', 'totals_h2'); D2, st2, ok2 = decision_quotes(Q2, True)
F = pd.read_csv(os.path.join(HERE, 'h1_flow_2023_2026.csv')); ypp_lo = float(F.ypp.quantile(1 / 3))
rows = []
for season in (2023, 2024, 2025, 2026):
    t = pq.read_table(os.path.join(PBP, f'pbp_{season}.parquet'), columns=['game_id', 'qtr', 'posteam', 'complete_pass', 'incomplete_pass', 'interception', 'yards_gained', 'qb_spike', 'two_point_attempt']).to_pandas()
    t = t[t.game_id.isin(set(F.game_id)) & (t.qtr <= 2) & (t.qb_spike != 1) & (t.two_point_attempt != 1)]
    t = t[(t.complete_pass == 1) | (t.incomplete_pass == 1) | (t.interception == 1)]
    g = t.groupby(['game_id', 'posteam']).agg(att=('complete_pass', 'size'), cmp=('complete_pass', 'sum'), yds=('yards_gained', 'sum')).reset_index(); rows.append(g)
P = pd.concat(rows); P['pct'] = P.cmp / P.att
G = P.groupby('game_id').agg(teams=('pct', 'size'), lo=('pct', 'min'), hi=('pct', 'max'), att=('att', 'sum'), cmp=('cmp', 'sum'), yds=('yds', 'sum')).reset_index()
G['pool'] = G.cmp / G.att; G['ypa'] = G.yds / G.att
F = F.merge(G, on='game_id', how='left'); F.to_csv(os.path.join(HERE, 'h1_qb_2023_2026.csv'), index=False)
print('games %d | with passes for both teams %d | first-half completion rate: team median %.1f%%, pooled median %.1f%% | yards-per-play cut %.2f' % (len(F), (F.teams == 2).sum(), 100 * P.pct.median(), 100 * F.pool.median(), ypp_lo))
slow = F.ypp < ypp_lo; ypa_lo = float(F.ypa.quantile(1 / 3))
def run(lab, mask, side='under'):
    d = D2[D2.game_id.isin(set(F[mask].game_id))]
    g, g1 = per_game(bets(d, 'pts2_ot', side=side)), per_game(bets(d, 'pts2_ot', side=side, step=0.01))
    line(lab, g, g1); return verdict(g, g1).replace('REPLICATED', 'PASSED THE SCREEN')
print('\n=== Q1, THE SCREEN ===')
print('   ->', run('Q1 slow first half, both teams under 55%, Under', slow & (F.hi < 0.55)))
print('\n=== for information only ===')
run('every game, Under', F.ypp > -1)
run('slow first half, no quarterback condition (T2)', slow)
run('slow, both teams under 60%', slow & (F.hi < 0.60))
run('slow, pooled passes under 55%', slow & (F.pool < 0.55))
run('slow, pooled passes under 60%', slow & (F.pool < 0.60))
run('slow, at least one team under 55%', slow & (F.lo < 0.55))
run('slow, both teams 55% or better', slow & (F.lo >= 0.55))
run('any game, both teams under 55%', F.hi < 0.55)
run('any game, both teams under 60%', F.hi < 0.60)
run('any game, pooled passes under 55%', F.pool < 0.55)
run('slow, pooled yards per attempt bottom third (under %.2f)' % ypa_lo, slow & (F.ypa < ypa_lo))
