#!/usr/bin/env python3
"""
FanDuel MLB DFS — Batter Backtest Framework

Companion to fd_walk_gate_backtest.py. Same architecture:
    1. Pull every final game in [START_DATE, END_DATE] from the MLB Stats API.
    2. Extract every batter's line from the boxscore and score it in
       FanDuel points.
    3. Sort each batter's games chronologically; for each game, compute a
       trailing-form SIGNAL using only PRIOR games (no lookahead).
    4. Bucket games by signal and compare FD-point outcomes.
    5. Optional parameter sweep.

FanDuel hitter scoring:
    1B +3, 2B +6, 3B +9, HR +12, RBI +3.5, R +3.2, BB +3, HBP +3, SB +6

Default signal (swappable):
    HOT  = trailing avg FD pts over prior WINDOW games >= HOT_THRESHOLD
    COLD = otherwise
    (min PRIOR games required, else warmup=True and excluded from headline)

This answers questions like: does chasing trailing form (fire-emoji chasing)
actually predict next-game production, or is it noise? Swap in your own
signal in `compute_signal()` — e.g. HR in last N, BB rate, multi-hit streak.

Usage:
    pip install requests
    python fd_batter_backtest.py --start 2026-04-01 --end 2026-07-10
    python fd_batter_backtest.py --start ... --end ... --sweep
    Output: per-game CSV (fd_batter_games.csv) + summary to stdout.

Note: pull from Opening Day so trailing windows are full. ~0.25s sleep per
boxscore call; a full season-to-date pull takes ~10-15 min. If you already
ran the pitcher script over the same range, the boxscore calls are repeated —
if you want, merge the two scripts later so one pull feeds both analyses.
"""

import argparse
import csv
import statistics
import sys
import time
from collections import defaultdict

import requests

API = "https://statsapi.mlb.com/api/v1"
SLEEP = 0.25

# ---------------------------------------------------------------- FD scoring

def fd_batter_points(singles: int, doubles: int, triples: int, hr: int,
                     rbi: int, runs: int, bb: int, hbp: int, sb: int) -> float:
    return (3.0 * singles + 6.0 * doubles + 9.0 * triples + 12.0 * hr
            + 3.5 * rbi + 3.2 * runs + 3.0 * bb + 3.0 * hbp + 6.0 * sb)


# ---------------------------------------------------------------- data pull

def get_game_pks(start_date: str, end_date: str) -> list[tuple[str, int]]:
    r = requests.get(
        f"{API}/schedule",
        params={"sportId": 1, "startDate": start_date, "endDate": end_date},
        timeout=30,
    )
    r.raise_for_status()
    pks = []
    for day in r.json().get("dates", []):
        for g in day.get("games", []):
            if g.get("status", {}).get("codedGameState") == "F" and \
               g.get("gameType") == "R":
                pks.append((g["officialDate"], g["gamePk"]))
    return pks


def extract_batters(game_date: str, game_pk: int) -> list[dict]:
    """One record per batter who had at least one PA (or SB/R credited)."""
    r = requests.get(f"{API}/game/{game_pk}/boxscore", timeout=30)
    r.raise_for_status()
    box = r.json()
    out = []
    for side in ("home", "away"):
        team = box["teams"][side]
        for pid_key, pdata in team.get("players", {}).items():
            bat = pdata.get("stats", {}).get("batting") or {}
            if not bat:
                continue
            pa = int(bat.get("plateAppearances", 0) or 0)
            if pa == 0:
                continue
            hits = int(bat.get("hits", 0) or 0)
            doubles = int(bat.get("doubles", 0) or 0)
            triples = int(bat.get("triples", 0) or 0)
            hr = int(bat.get("homeRuns", 0) or 0)
            singles = hits - doubles - triples - hr
            rbi = int(bat.get("rbi", 0) or 0)
            runs = int(bat.get("runs", 0) or 0)
            bb = int(bat.get("baseOnBalls", 0) or 0)
            hbp = int(bat.get("hitByPitch", 0) or 0)
            sb = int(bat.get("stolenBases", 0) or 0)
            out.append({
                "date": game_date,
                "game_pk": game_pk,
                "player_id": pdata["person"]["id"],
                "name": pdata["person"]["fullName"],
                "team": team["team"]["name"],
                "pa": pa,
                "ab": int(bat.get("atBats", 0) or 0),
                "h": hits, "2b": doubles, "3b": triples, "hr": hr,
                "rbi": rbi, "r": runs, "bb": bb, "hbp": hbp, "sb": sb,
                "k": int(bat.get("strikeOuts", 0) or 0),
                "fd_pts": round(fd_batter_points(
                    singles, doubles, triples, hr, rbi, runs, bb, hbp, sb), 1),
            })
    return out


# ---------------------------------------------------------------- signal

def compute_signal(prior: list[dict], hot_threshold: float) -> tuple[str, float]:
    """
    Default signal: trailing mean FD pts over the prior window.
    Returns (bucket_label, trailing_avg).
    Swap this function to test other signals (HR in last N, BB rate, etc.).
    """
    avg = statistics.mean(g["fd_pts"] for g in prior)
    return ("HOT" if avg >= hot_threshold else "COLD"), round(avg, 2)


def apply_signal(games_by_batter: dict, window: int, min_prior: int,
                 hot_threshold: float) -> list[dict]:
    rows = []
    for pid, games in games_by_batter.items():
        games = sorted(games, key=lambda g: (g["date"], g["game_pk"]))
        for i, g in enumerate(games):
            prior = games[max(0, i - window):i]
            g = dict(g)
            g["prior_games"] = len(prior)
            g["warmup"] = len(prior) < min_prior
            if g["warmup"]:
                g["bucket"], g["trailing_avg"] = "WARMUP", None
            else:
                g["bucket"], g["trailing_avg"] = compute_signal(
                    prior, hot_threshold)
            rows.append(g)
    return rows


# ---------------------------------------------------------------- reporting

def bucket_stats(rows: list[dict]) -> dict:
    pts = [r["fd_pts"] for r in rows]
    if not pts:
        return {}
    return {
        "n": len(pts),
        "mean": round(statistics.mean(pts), 2),
        "median": round(statistics.median(pts), 2),
        "stdev": round(statistics.pstdev(pts), 2),
        "dud_rate_lt5": round(sum(p < 5 for p in pts) / len(pts), 3),
        "ceiling_rate_ge25": round(sum(p >= 25 for p in pts) / len(pts), 3),
        "smash_rate_ge35": round(sum(p >= 35 for p in pts) / len(pts), 3),
    }


def summarize(rows: list[dict], label: str) -> None:
    eligible = [r for r in rows if not r["warmup"]]
    print(f"\n=== {label} ===")
    print(f"eligible games: {len(eligible)}  "
          f"(warmup excluded: {len(rows) - len(eligible)})")
    for bucket in ("HOT", "COLD"):
        sub = [r for r in eligible if r["bucket"] == bucket]
        st = bucket_stats(sub)
        if not st:
            print(f"  {bucket}: no games")
            continue
        print(f"  {bucket}: n={st['n']}  mean={st['mean']}  "
              f"median={st['median']}  sd={st['stdev']}")
        print(f"      dud(<5): {st['dud_rate_lt5']:.1%}   "
              f"ceiling(25+): {st['ceiling_rate_ge25']:.1%}   "
              f"smash(35+): {st['smash_rate_ge35']:.1%}")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--window", type=int, default=7,
                    help="trailing games in the signal window")
    ap.add_argument("--min-prior", type=int, default=5,
                    help="min prior games required (else warmup)")
    ap.add_argument("--hot-threshold", type=float, default=12.0,
                    help="trailing avg FD pts to qualify as HOT")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--csv", default="fd_batter_games.csv")
    args = ap.parse_args()

    print(f"Pulling schedule {args.start} .. {args.end} ...")
    games = get_game_pks(args.start, args.end)
    print(f"{len(games)} final games. Pulling boxscores "
          f"(~{len(games) * SLEEP / 60:.0f}+ min) ...")

    games_by_batter = defaultdict(list)
    for idx, (gdate, pk) in enumerate(games, 1):
        try:
            for rec in extract_batters(gdate, pk):
                games_by_batter[rec["player_id"]].append(rec)
        except Exception as e:  # noqa: BLE001
            print(f"  skip game {pk}: {e}", file=sys.stderr)
        if idx % 100 == 0:
            print(f"  {idx}/{len(games)} games")
        time.sleep(SLEEP)

    rows = apply_signal(games_by_batter, args.window, args.min_prior,
                        args.hot_threshold)

    with open(args.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} batter-games to {args.csv}")

    summarize(rows, f"SIGNAL: trailing {args.window}-game FD avg, "
                    f"HOT >= {args.hot_threshold}")

    if args.sweep:
        for window in (5, 7, 10):
            for thresh in (10.0, 12.0, 15.0):
                r = apply_signal(games_by_batter, window,
                                 min(args.min_prior, window), thresh)
                summarize(r, f"sweep window={window} hot>={thresh}")


if __name__ == "__main__":
    main()
