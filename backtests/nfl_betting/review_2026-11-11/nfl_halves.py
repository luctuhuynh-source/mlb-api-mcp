"""Loads halves_2015_2026.csv and adds the margins used by every script here.
spread_line is the nflverse closing full-game spread: positive = home team favoured by that many points."""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
def load():
    d = pd.read_csv(os.path.join(HERE, 'halves_2015_2026.csv'))
    d['m1'] = d.h1_home - d.h1_away                                         # home 1H margin
    d['m2reg'] = (d.reg_home - d.h1_home) - (d.reg_away - d.h1_away)        # home 2H margin, regulation only (Robinhood basis)
    d['m2ot'] = (d.fin_home - d.h1_home) - (d.fin_away - d.h1_away)         # home 2H margin incl. overtime (DSB basis)
    return d
def favourite_view(d):
    f = d[d.spread_line != 0].copy(); s = np.sign(f.spread_line)
    f['absspr'] = f.spread_line.abs(); f['fm1'] = s * f.m1; f['fm2reg'] = s * f.m2reg; f['fm2ot'] = s * f.m2ot
    # the team laying points in the 2H: sign of the expected 2H margin given pregame spread and halftime margin
    X = np.column_stack([f.absspr, f.fm1, np.ones(len(f))]); c = np.linalg.lstsq(X, f.fm2ot.values, rcond=None)[0]
    s2 = np.where(X @ c >= 0, 1, -1); f['lay2ot'] = s2 * f.fm2ot; f['lay2reg'] = s2 * f.fm2reg
    return f, c
