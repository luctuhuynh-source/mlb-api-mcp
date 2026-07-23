#!/usr/bin/env python3
"""
fd_p1p2_env_backtest_v2.py — adapted to the actual repo files (7/22/26):
  backtests/fd_batter_games.csv  (date,game_pk,player_id,name,team,...,fd_pts,...,baseline_avg,...)
  backtests/fd_gate_starts.csv   (date,game_pk,...,name,team,...,trail_whip,trail_k9,...,opener,gated,...)
Teams are FULL NAMES in those files; census uses abbrevs — mapped below.
Opponent is derived by pairing the two teams sharing a game_pk.
Bat selection uses the pipeline's own point-in-time baseline_avg (v1.3-consistent).

Run from repo root:  python3 fd_p1p2_env_backtest_v2.py
Outputs: backtests/fd_p1_daily.csv, backtests/fd_p2_daily.csv + printed verdicts.
"""

import json
import sys
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd

# ----------------------------- CONFIG ---------------------------------------
CENSUS_FILES = [
    "f5_board_census_MASTER_2025mar18-sep13_2026apr01-jul08.jsonl",  # adjust if named differently
    "f5_board_census_EXT_2026jul09-jul21.jsonl",
]
BATTER_CSV = "backtests/fd_batter_games.csv"
STARTS_CSV = "backtests/fd_gate_starts.csv"
OUT_DIR = Path("backtests")

DATE_MIN, DATE_MAX = "2026-04-01", "2026-07-21"
MIN_BOOKS = 4
STACK_N = 4
DISASTER_LT = 10.0
BLOCK_CEILING = 60.0
RANDOM_DRAWS = 200
SEED = 26
P1_P90_EDGE = 5.0
P1_MEAN_SLACK = 1.0
P2_MEAN_SLACK = 3.0

FULL2ABBR = {
    "Arizona Diamondbacks": "ARI", "Atlanta Braves": "ATL", "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS", "Chicago Cubs": "CHC", "Chicago White Sox": "CWS",
    "Cincinnati Reds": "CIN", "Cleveland Guardians": "CLE", "Colorado Rockies": "COL",
    "Detroit Tigers": "DET", "Houston Astros": "HOU", "Kansas City Royals": "KC",
    "Los Angeles Angels": "LAA", "Los Angeles Dodgers": "LAD", "Miami Marlins": "MIA",
    "Milwaukee Brewers": "MIL", "Minnesota Twins": "MIN", "New York Mets": "NYM",
    "New York Yankees": "NYY", "Athletics": "ATH", "Oakland Athletics": "ATH",
    "Philadelphia Phillies": "PHI", "Pittsburgh Pirates": "PIT", "San Diego Padres": "SD",
    "San Francisco Giants": "SF", "Seattle Mariners": "SEA", "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TB", "Texas Rangers": "TEX", "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSH",
}


def to_abbr(s):
    s = str(s).strip()
    if s in FULL2ABBR:
        return FULL2ABBR[s]
    return s.upper()  # already an abbrev


def as_bool(x):
    return str(x).strip().lower() in ("true", "1", "1.0", "yes")


def add_opp(df):
    """Derive opp by pairing the two distinct teams sharing a game_pk."""
    pairs = df.groupby("game_pk")["team"].agg(lambda s: sorted(set(s)))
    ok = pairs[pairs.map(len) == 2]
    m = {}
    for pk, (t1, t2) in ok.items():
        m[(pk, t1)] = t2
        m[(pk, t2)] = t1
    df["opp"] = [m.get((pk, t)) for pk, t in zip(df["game_pk"], df["team"])]
    return df.dropna(subset=["opp"])


# ----------------------------- LOADERS --------------------------------------
def load_census(paths):
    rows, seen = [], set()
    for p in paths:
        fp = Path(p)
        if not fp.exists():
            sys.exit(f"census file not found: {p} (edit CENSUS_FILES at top of script)")
        for line in fp.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            d, m = r["d"], r["m"]
            if not (DATE_MIN <= d <= DATE_MAX) or (d, m) in seen:
                continue
            bk = r.get("bk") or {}
            lines = [v[0] for v in bk.values() if v and v[0] is not None]
            if len(lines) < MIN_BOOKS:
                continue
            away, home = m.split("@")
            dh = away.endswith("2") or home.endswith("2")
            rows.append(dict(
                date=d, away=away.rstrip("2"), home=home.rstrip("2"),
                game_num=2 if dh else 1, consensus_total=median(lines),
                n_books=len(lines),
                coors=("coors" in (r.get("note") or "")) or home.rstrip("2") == "COL",
            ))
            seen.add((d, m))
    df = pd.DataFrame(rows)
    dh_pairs = set(map(tuple, df.loc[df.game_num == 2, ["date", "away"]].values))
    df["is_dh"] = df.apply(lambda r: (r["date"], r["away"]) in dh_pairs, axis=1)
    return df


def load_batters():
    df = pd.read_csv(BATTER_CSV)
    need = {"date", "game_pk", "name", "team", "fd_pts", "baseline_avg"}
    missing = need - set(df.columns)
    if missing:
        sys.exit(f"{BATTER_CSV} missing columns: {missing}")
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= DATE_MIN) & (df["date"] <= DATE_MAX)].copy()
    df["team"] = df["team"].map(to_abbr)
    df["fd_pts"] = pd.to_numeric(df["fd_pts"], errors="coerce")
    df["baseline"] = pd.to_numeric(df["baseline_avg"], errors="coerce")
    df = df.dropna(subset=["fd_pts"])
    # DH detection on the data side: team with 2 game_pks on a date
    counts = df.groupby(["date", "team"])["game_pk"].nunique().rename("n_games")
    df = df.merge(counts, on=["date", "team"], how="left")
    return df


def load_starters():
    df = pd.read_csv(STARTS_CSV)
    need = {"date", "game_pk", "name", "team", "trail_whip", "opener"}
    missing = need - set(df.columns)
    if missing:
        sys.exit(f"{STARTS_CSV} missing columns: {missing}")
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= DATE_MIN) & (df["date"] <= DATE_MAX)].copy()
    df["team"] = df["team"].map(to_abbr)
    df["trail_whip"] = pd.to_numeric(df["trail_whip"], errors="coerce")
    df["opener"] = df["opener"].map(as_bool)
    df = add_opp(df)
    # qualified target arms: true starters with a trailing sample
    df = df[(~df["opener"]) & df["trail_whip"].notna()]
    counts = df.groupby(["date", "team"])["game_pk"].nunique().rename("n_games")
    df = df.merge(counts, on=["date", "team"], how="left")
    return df[df["n_games"] == 1]  # exclude DH team-days from selection


# ----------------------------- STACKS ---------------------------------------
def day_bats(bats, date, team):
    d = bats[(bats["date"] == date) & (bats["team"] == team) & (bats["n_games"] == 1)]
    return d.dropna(subset=["baseline"])


def stack_sum(bats, date, team, n=STACK_N):
    d = day_bats(bats, date, team)
    if len(d) < n:
        return None
    return float(d.nlargest(n, "baseline")["fd_pts"].sum())


def top_n_pts(bats, date, team, n):
    d = day_bats(bats, date, team)
    if len(d) < n:
        return None
    return float(d.nlargest(n, "baseline")["fd_pts"].sum())


def random_block(bats, date, team, n, rng):
    d = bats[(bats["date"] == date) & (bats["team"] == team) & (bats["n_games"] == 1)]
    if len(d) < n:
        return None
    draws = [d.sample(n, random_state=int(rng.integers(1 << 30)))["fd_pts"].sum()
             for _ in range(RANDOM_DRAWS)]
    return float(np.mean(draws))


# ----------------------------- MAIN LOOP ------------------------------------
def run(census, bats, starters):
    rng = np.random.default_rng(SEED)
    p1_rows, p2_rows, skips = [], [], []

    for date, slate in census.groupby("date"):
        sel = slate[~slate["is_dh"]]
        st = starters[starters["date"] == date]
        if sel.empty or st.empty:
            skips.append((date, "no selectable games or starter data"))
            continue

        # keep starters whose game is in the census slate
        key = set(map(tuple, sel[["away", "home"]].values))
        st = st[[((t, o) in key or (o, t) in key) for t, o in zip(st.team, st.opp)]]
        if st.empty:
            skips.append((date, "starter/census join empty"))
            continue

        # Arm A: v1.3 control — worst trailing-WHIP starter on slate
        worst = st.loc[st["trail_whip"].idxmax()]
        a_team = worst["opp"]
        a_sum = stack_sum(bats, date, a_team)

        # Arm B: highest-total game; side facing worse arm within it
        top = sel.loc[sel["consensus_total"].idxmax()]
        pair = st[((st.team == top.away) & (st.opp == top.home)) |
                  ((st.team == top.home) & (st.opp == top.away))]
        if len(pair) < 2:
            skips.append((date, f"top-game starters missing ({top.away}@{top.home})"))
            continue
        worse_side = pair.loc[pair["trail_whip"].idxmax()]
        b_team = worse_side["opp"]
        b_sum = stack_sum(bats, date, b_team)

        if a_sum is not None and b_sum is not None:
            p1_rows.append(dict(
                date=date, month=date[:7],
                a_team=a_team, a_pitcher=worst["name"], a_whip=float(worst["trail_whip"]),
                a_sum=a_sum, a_rand=random_block(bats, date, a_team, STACK_N, rng),
                b_game=f"{top.away}@{top.home}", b_total=float(top.consensus_total),
                b_team=b_team, b_pitcher=worse_side["name"], b_whip=float(worse_side["trail_whip"]),
                b_sum=b_sum, b_rand=random_block(bats, date, b_team, STACK_N, rng),
                coors=bool(top.coors),
            ))

        h4 = stack_sum(bats, date, top.home)
        a4 = stack_sum(bats, date, top.away)
        h2 = top_n_pts(bats, date, top.home, 2)
        a2 = top_n_pts(bats, date, top.away, 2)
        h3 = top_n_pts(bats, date, top.home, 3)
        a3 = top_n_pts(bats, date, top.away, 3)
        h1 = top_n_pts(bats, date, top.home, 1)
        a1 = top_n_pts(bats, date, top.away, 1)
        if None in (h4, a4, h2, a2, h3, a3, h1, a1):
            continue
        p2_rows.append(dict(
            date=date, month=date[:7], game=f"{top.away}@{top.home}",
            total=float(top.consensus_total), coors=bool(top.coors),
            side4_home=h4, side4_away=a4,
            split22=h2 + a2, split31_h=h3 + a1, split31_a=a3 + h1,
        ))

    return pd.DataFrame(p1_rows), pd.DataFrame(p2_rows), skips


# ----------------------------- REPORT ---------------------------------------
def stats(x):
    return dict(n=len(x), mean=round(x.mean(), 2), p90=round(x.quantile(0.9), 2),
                disaster=round((x < DISASTER_LT).mean(), 3),
                ge60=round((x >= BLOCK_CEILING).mean(), 3))


def report(p1, p2, skips):
    print(f"\n=== P1 (n={len(p1)} slates) ===")
    A, B = stats(p1["a_sum"]), stats(p1["b_sum"])
    print("Arm A (WHIP-only):", A)
    print("Arm B (top-total):", B)
    print("edge vs same-game random-4 — A:", round((p1.a_sum - p1.a_rand).mean(), 2),
          "| B:", round((p1.b_sum - p1.b_rand).mean(), 2))
    for mth, g in p1.groupby("month"):
        print(f"  {mth}: A {g.a_sum.mean():.1f} / B {g.b_sum.mean():.1f} (n={len(g)})")
    for flag, g in p1.groupby("coors"):
        print(f"  coors={flag}: B mean {g.b_sum.mean():.1f} p90 {g.b_sum.quantile(.9):.1f} (n={len(g)})")
    ok = (B["p90"] >= A["p90"] + P1_P90_EDGE) and (B["mean"] >= A["mean"] - P1_MEAN_SLACK)
    print("P1 VERDICT:", "PASS" if ok else "FAIL",
          f"(need B p90 >= {round(A['p90'] + P1_P90_EDGE, 2)} and B mean >= {round(A['mean'] - P1_MEAN_SLACK, 2)})")

    print(f"\n=== P2 (n={len(p2)} top-total games) ===")
    sh, sa = stats(p2["side4_home"]), stats(p2["side4_away"])
    best_one = sh if sh["p90"] >= sa["p90"] else sa
    arms = dict(side4_home=sh, side4_away=sa, split22=stats(p2["split22"]),
                split31_h=stats(p2["split31_h"]), split31_a=stats(p2["split31_a"]))
    for k, v in arms.items():
        print(f"  {k}: {v}")
    verdicts = {k: ("PASS" if (arms[k]["p90"] > best_one["p90"]
                               and arms[k]["ge60"] > best_one["ge60"]
                               and arms[k]["mean"] >= best_one["mean"] - P2_MEAN_SLACK)
                    else "FAIL")
                for k in ("split22", "split31_h", "split31_a")}
    print("P2 VERDICTS:", verdicts)

    if skips:
        print(f"\nSkipped slates ({len(skips)}), first 15:")
        for d, why in skips[:15]:
            print(f"  {d}: {why}")


def main():
    census = load_census(CENSUS_FILES)
    bats = load_batters()
    starters = load_starters()
    print(f"loaded: {len(census)} census games, {len(bats)} batter-games, {len(starters)} starts")
    p1, p2, skips = run(census, bats, starters)
    OUT_DIR.mkdir(exist_ok=True)
    p1.to_csv(OUT_DIR / "fd_p1_daily.csv", index=False)
    p2.to_csv(OUT_DIR / "fd_p2_daily.csv", index=False)
    print(f"wrote {OUT_DIR/'fd_p1_daily.csv'} ({len(p1)} rows), {OUT_DIR/'fd_p2_daily.csv'} ({len(p2)} rows)")
    report(p1, p2, skips)


if __name__ == "__main__":
    main()
