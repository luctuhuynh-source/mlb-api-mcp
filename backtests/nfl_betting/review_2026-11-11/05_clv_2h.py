#!/usr/bin/env python3
"""Closing-line value for every 2H lean and fire in the rebuilt ledger, 10/18 to 11/5/2026 (24 entries, 23 games).
Close = the last Odds API historical snapshot at least 30 seconds before the 3rd-quarter kickoff
(closes_2h_2026-10-18_to_11-05.json; four US books each: DraftKings, FanDuel, BetRivers, Bovada; their 2H lines include
overtime, like DSB). The 3Q kickoff time is the wall-clock time of the first 3rd-quarter play in nflverse play-by-play
(halftime_clock_2026-10-18_to_11-05.csv). Per book: de-vig, convert to the bet's number with the one-sided 2H table
(B-NFL-3, overtime in), take the median. CLV (Liem L1.1) = closing implied probability minus fill implied probability.
'CLV minus margin' = closing no-vig fair minus fill implied probability.
In a 13 to 15 minute halftime the close is within minutes of the bet, so this mostly measures the DSB price against the
market's fair at the time, which is the test that matters for a lean."""
import os, json, csv, re, statistics as st, collections
import numpy as np, pandas as pd
from nfl_halves import load, favourite_view, HERE
D = load(); F, _ = favourite_view(D); N = len(F)
lay = (F.lay2ot.value_counts() / N).to_dict()            # P(2H favourite's margin, overtime in, = k)
D['t2ot'] = (D.fin_home - D.h1_home) + (D.fin_away - D.h1_away)
tot_all = (D.t2ot.value_counts() / len(D)).to_dict()     # P(2H points, overtime in, = k), every game
closes = json.load(open(os.path.join(HERE, 'closes_2h_2026-10-18_to_11-05.json')))
clock = {r['game']: r for r in csv.DictReader(open(os.path.join(HERE, 'halftime_clock_2026-10-18_to_11-05.csv')))}
state = {r['id']: r for r in csv.DictReader(open(os.path.join(HERE, '2h_entries_by_halftime_state.csv')))}
led = {r['id']: r for r in csv.DictReader(open(os.path.join(HERE, '..', 'ledger_rebuilt_2026-10-18_to_11-05.csv')))}
def imp(a): a = float(a); return (-a) / ((-a) + 100) if a < 0 else 100 / (a + 100)
def find(away_kw, home_kw):
    for d in closes.values():
        if away_kw in d['away'] and home_kw in d['home']: return d
    raise KeyError((away_kw, home_kw))
def convert(q_i, s_i, s_b, pm):
    push_i = pm(-s_i) if float(s_i).is_integer() else 0.0
    W = q_i * (1 - push_i); lo, hi = sorted((-s_b, -s_i))
    mass = sum(pm(k) for k in range(int(np.floor(lo)) - 1, int(np.ceil(hi)) + 2) if lo < k <= hi)
    W_b = W + mass if s_b > s_i else W - mass
    push_b = pm(-s_b) if float(s_b).is_integer() else 0.0
    return W_b / (1 - push_b)
# id, away kw, home kw, our team kw (or 'Over'), our line, fill price
ROWS = [('R07','Titans','Colts','Colts',-2.5,-110), ('R08','Ravens','Browns','Ravens',+0.5,-115), ('R09','Jets','Patriots','Patriots',-2.5,-110),
        ('R10','Saints','Giants','Giants',+1.5,-100), ('R11','Bears','Falcons','Bears',+4,-115), ('R12','Panthers','Eagles','Panthers',-1,-105),
        ('R13','Bills','Raiders','Raiders',+3,-110), ('R14','Chargers','Chiefs','Chiefs',-2.5,-110), ('R15','Bears','Falcons','Over',24.5,-105),
        ('R16','Cardinals','Rams','Cardinals',+6.5,-110), ('R20','Patriots','Bears','Bears',+0.5,-105), ('R30','Browns','Titans','Browns',-0.5,-105),
        ('R31','Giants','Texans','Texans',-3.5,+105), ('R32','Broncos','Cardinals','Broncos',0,-100), ('R33','Packers','Lions','Lions',-1.5,-105),
        ('R35','Cowboys','Eagles','Cowboys',+0.5,-115), ('R39','Raiders','Jets','Jets',+3,-110), ('R40','Browns','Steelers','Steelers',-0.5,-100),
        ('R41','Patriots','Dolphins','Dolphins',+7,-100), ('R42','Chiefs','Broncos','Chiefs',+1,-100), ('R43','Eagles','Commanders','Commanders',-1,-115),
        ('R44','Chargers','Rams','Rams',-3,-105), ('R46','Bears','Seahawks','Bears',+1,-100), ('R48','Jaguars','Ravens','Jaguars',-3,-105)]
out = []
for rid, akw, hkw, team, line, price in ROWS:
    d = find(akw, hkw); r = led[rid]; fill = imp(price); total = (team == 'Over'); mkey = 'totals_h2' if total else 'spreads_h2'
    books = []
    for b in d['books']:
        for m in b['markets']:
            if m['key'] != mkey: continue
            ours = [o for o in m['outcomes'] if team in o['name']][0]; opp = [o for o in m['outcomes'] if team not in o['name']][0]
            books.append((b['key'], float(ours['point']), float(ours['price']), float(opp['price'])))
    pts = [b[1] for b in books]; med = st.median(pts); modal = collections.Counter(pts).most_common(1)[0][0]
    conv, margins, same = [], [], 0
    for key, pt, po, pp in books:
        io, ip = imp(po), imp(pp); q = io / (io + ip); margins.append(io - q); same += (pt == line)
        if total:   # Over wins when points > line: every whole number between the two lines moves the win probability by its frequency
            lo, hi = sorted((line, pt)); mass = sum(tot_all.get(k, 0) for k in range(int(lo), int(hi) + 2) if lo < k <= hi)
            push_i = tot_all.get(int(pt), 0) if float(pt).is_integer() else 0.0
            W = q * (1 - push_i); conv.append(W + mass if line < pt else W - mass)
        else:
            if med < 0: pm = lambda k: lay.get(k, 0.0)
            elif med > 0: pm = lambda k: lay.get(-k, 0.0)
            else: pm = lambda k: (lay.get(k, 0.0) + lay.get(-k, 0.0)) / 2
            conv.append(convert(q, pt, line, pm))
    fair = st.median(conv); margin = st.mean(margins); net = fair - fill; clv = net + margin
    c = clock[r['game']]
    lead = (pd.Timestamp(c['q3_kickoff_utc']) - pd.Timestamp(d['snapshot_timestamp'])).total_seconds()
    out.append(dict(id=rid, date=r['date'], cls=r['class'], game=r['game'], pick=r['pick'], fill_prob=round(fill, 4),
                    close_snapshot=d['snapshot_timestamp'], seconds_before_3q_kick=int(lead), books=len(books),
                    close_numbers=' / '.join('%+g' % p if not total else '%g' % p for p in pts), close_modal_our_line=modal,
                    line_move_pts=(modal - line if total else line - modal), books_at_our_number=same,
                    close_fair_at_our_number=round(fair, 4), per_side_margin=round(margin, 4), clv_prob=round(clv, 4),
                    clv_minus_margin=round(net, 4), beat_close=int(clv > 0), result=r['result'],
                    halftime_state=state[rid]['state'] if not total else 'total'))
df = pd.DataFrame(out); df.to_csv(os.path.join(HERE, '..', 'clv_2h_2026-10-18_to_11-05.csv'), index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(df[['id', 'date', 'pick', 'fill_prob', 'close_numbers', 'line_move_pts', 'close_fair_at_our_number', 'per_side_margin', 'clv_prob', 'clv_minus_margin', 'beat_close', 'result', 'halftime_state', 'seconds_before_3q_kick']].to_string(index=False))
def line(s, lab):
    n = len(s)
    if n == 0: return
    mn = s.clv_minus_margin.mean(); sd = s.clv_minus_margin.std(ddof=1) if n > 1 else float('nan'); z = mn / (sd / np.sqrt(n)) if n > 1 and sd > 0 else float('nan')
    print('%-40s n %2d | beat close %2d/%2d | mean CLV %+.2f | mean CLV - margin %+.2f (sd %.2f, z %+.2f) | at or better than fair %2d | W-L-P %d-%d-%d | better number than close %d, worse %d, same %d' % (
        lab, n, s.beat_close.sum(), n, 100 * s.clv_prob.mean(), 100 * mn, 100 * sd, z, (s.clv_minus_margin >= 0).sum(),
        (s.result == 'W').sum(), (s.result == 'L').sum(), (s.result == 'P').sum(), (s.line_move_pts > 0).sum(), (s.line_move_pts < 0).sum(), (s.line_move_pts == 0).sum()))
print()
le = df[df.cls == '2H lean']; fi = df[df.cls != '2H lean']
line(df, 'ALL 2H entries'); line(le, '2H leans'); line(fi, '2H engine fires')
line(le[le.halftime_state == 'leader'], '2H leans on the halftime leader'); line(le[le.halftime_state == 'tied'], '2H leans, game tied at half')
line(le[le.id.isin(['R07','R08','R09','R10','R11','R12','R13','R14','R20','R30','R31','R32','R33','R35','R39','R40'])], '2H leans under v0.6 (10/18 - 11/1 AM)')
line(le[le.id.isin(['R41','R42','R43','R46','R48'])], '2H leans under v0.6a (11/1 PM - 11/5)')
line(le[le.result == 'W'], 'winning leans'); line(le[le.result == 'L'], 'losing leans')
line(le[le.clv_minus_margin >= 0], 'leans priced at or better than fair'); line(le[le.clv_minus_margin < 0], 'leans priced worse than fair')
print('average per-side margin at the 2H close: %.1f points (1H close: about 2.4)' % (100 * df.per_side_margin.mean()))
