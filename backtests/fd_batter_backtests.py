#!/usr/bin/env python3
"""
FanDuel MLB DFS — Batter Form Backtest (patched)

Companion to fd_walk_gate_backtest.py. Same architecture: pull final games,
score every batter-game in FD points, compute a trailing signal from PRIOR
games only, bucket, compare.

PATCH NOTES (v1.1):
    * FORM-DELTA SIGNAL — the old signal (trailing FD avg >= threshold)
      was a BETWEEN-player comparison: the HOT bucket fills with good
      hitters, so HOT "beats" COLD even if form is pure noise. The signal
      is now the trailing WINDOW average MINUS the player's own expanding
      baseline over all prior games:
          delta = trail_avg(window) - baseline_avg(all prior)
          HOT   if delta >= +hot_delta
          COLD  if delta <= -hot_delta
          NEUTRAL otherwise
      This asks the real question: does a player running above HIS OWN
      norm keep doing so tomorrow?
    * WITHIN-PLAYER PAIRED TEST — additionally, for every player with
      enough games in both HOT and COLD buckets, compute (his HOT mean -
      his COLD mean) and aggregate across players. This removes player
      quality from the comparison entirely. If fire-emoji chasing works,
      the mean per-player delta is positive and most players are positive.
    * 0-PA rows with SB or R credited (pinch-runner points) are now
      included, matching the original docstring's intent.
    * Finality via abstractGameState == "Final"; boxscore retries;
      empty-pull guard.

FanDuel hitter scoring:
    1B +3, 2B +6, 3B +9, HR +12, RBI +3.5, R +3.2, BB +3, HBP +3, SB +6

Usage:
    pip install requests
    python fd_batter_backtests.py --start 2026-04-01 --end 2026-07-10
    python fd_batter_backtests.py --start ... --end ... --sweep
    Output: per-game CSV (fd_batter_games.csv) + summary to stdout.

Note: pull from Opening Day so baselines are meaningful. If you already ran
the pitcher script over the same range, the boxscore calls are repeated —
consider merging so one pull feeds both analyses.
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


# ---------------------------------------------------------------- helpers

def get_json(url: str, params=None, retries: int = 2) -> dict:
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception:
            if attempt == retries:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def fd_batter_points(singles: int, doubles: int, triples: int, hr: int,
                     rbi: int, runs: int, bb: int, hbp: int, sb: int) -> float:
    return (3.0 * singles + 6.0 * doubles + 9.0 * triples + 12.0 * hr
            + 3.5 * rbi + 3.2 * runs + 3.0 * bb + 3.0 * hbp + 6.0 * sb)


# ---------------------------------------------------------------- data pull

def get_game_pks(start_date: str, end_date: str) -> list[tuple[str, int]]:
    data = get_json(
        f"{API}/schedule",
        params={"sportId": 1, "startDate": start_date, "endDate": end_date},
    )
    pks = []
    for day in data.get("dates", []):
        for g in day.get("games", []):
            if g.get("status", {}).get("abstractGameState") == "Final" and \
               g.get("gameType") == "R":
                pks.append((g["officialDate"], g["gamePk"]))
    return pks


def extract_batters(game_date: str, game_pk: int) -> list[dict]:
    """One record per batter with a PA, or 0-PA with SB/R credited."""
    box = get_json(f"{API}/game/{game_pk}/boxscore")
    out = []
    for side in ("home", "away"):
        team = box["teams"][side]
        for pid_key, pdata in team.get("players", {}).items():
            bat = pdata.get("stats", {}).get("batting") or {}
            if not bat:
                continue
            pa = int(bat.get("plateAppearances", 0) or 0)
            runs = int(bat.get("runs", 0) or 0)
            sb = int(bat.get("stolenBases", 0) or 0)
            if pa == 0 and runs == 0 and sb == 0:
                continue
            hits = int(bat.get("hits", 0) or 0)
            doubles = int(bat.get("doubles", 0) or 0)
            triples = int(bat.get("triples", 0) or 0)
            hr = int(bat.get("homeRuns", 0) or 0)
            singles = hits - doubles - triples - hr
            rbi = int(bat.get("rbi", 0) or 0)
            bb = int(bat.get("baseOnBalls", 0) or 0)
            hbp = int(bat.get("hitByPitch", 0) or 0)
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

def apply_signal(games_by_batter: dict, window: int, baseline_min: int,
                 hot_delta: float) -> list[dict]:
    """
    delta = trailing WINDOW mean - expanding baseline mean (ALL prior games).
    HOT / COLD / NEUTRAL at +-hot_delta. Warmup until the player has
    baseline_min prior games AND a full trailing window.
    """
    rows = []
    for pid, games in games_by_batter.items():
        games = sorted(games, key=lambda g: (g["date"], g["game_pk"]))
        for i, g in enumerate(games):
            all_prior = games[:i]                    # graded game excluded
            win_prior = games[max(0, i - window):i]
            g = dict(g)
            g["prior_games"] = len(all_prior)
            g["warmup"] = (len(all_prior) < baseline_min
                           or len(win_prior) < window)
            if g["warmup"]:
                g["bucket"] = "WARMUP"
                g["trailing_avg"] = g["baseline_avg"] = g["form_delta"] = None
            else:
                trail = statistics.mean(x["fd_pts"] for x in win_prior)
                base = statistics.mean(x["fd_pts"] for x in all_prior)
                delta = trail - base
                g["trailing_avg"] = round(trail, 2)
                g["baseline_avg"] = round(base, 2)
                g["form_delta"] = round(delta, 2)
                if delta >= hot_delta:
                    g["bucket"] = "HOT"
                elif delta <= -hot_delta:
                    g["bucket"] = "COLD"
                else:
                    g["bucket"] = "NEUTRAL"
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
    for bucket in ("HOT", "NEUTRAL", "COLD"):
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
    within_player_summary(eligible)


def within_player_summary(eligible: list[dict], min_each: int = 3) -> None:
    """Paired test: per-player HOT mean minus COLD mean, aggregated."""
    per = defaultdict(lambda: {"HOT": [], "COLD": []})
    for r in eligible:
        if r["bucket"] in ("HOT", "COLD"):
            per[r["player_id"]][r["bucket"]].append(r["fd_pts"])
    deltas = []
    for pid, b in per.items():
        if len(b["HOT"]) >= min_each and len(b["COLD"]) >= min_each:
            deltas.append(statistics.mean(b["HOT"])
                          - statistics.mean(b["COLD"]))
    print(f"\n  -- within-player paired test "
          f"(players with {min_each}+ games in each bucket) --")
    if not deltas:
        print("  not enough paired players")
        return
    pos = sum(d > 0 for d in deltas)
    print(f"  players: {len(deltas)}  "
          f"mean per-player (HOT - COLD): "
          f"{statistics.mean(deltas):+.2f} FD pts  "
          f"median: {statistics.median(deltas):+.2f}  "
          f"positive: {pos}/{len(deltas)} ({pos / len(deltas):.0%})")
    print("  interpretation: ~0 mean / ~50% positive = form is noise; "
          "clearly positive = hot hand is real.")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--window", type=int, default=7,
                    help="trailing games in the signal window")
    ap.add_argument("--baseline-min", type=int, default=15,
                    help="min prior games for a usable baseline")
    ap.add_argument("--hot-delta", type=float, default=3.0,
                    help="form delta (FD pts above/below own baseline) "
                         "to qualify HOT/COLD")
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
            print(f"  skip game {pk} after retries: {e}", file=sys.stderr)
        if idx % 100 == 0:
            print(f"  {idx}/{len(games)} games")
        time.sleep(SLEEP)

    rows = apply_signal(games_by_batter, args.window, args.baseline_min,
                        args.hot_delta)
    if not rows:
        sys.exit("No batter-games extracted — check date range / API access.")

    with open(args.csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} batter-games to {args.csv}")

    summarize(rows, f"SIGNAL: {args.window}-game form delta vs own baseline, "
                    f"HOT/COLD at +-{args.hot_delta}")

    if args.sweep:
        for window in (5, 7, 10):
            for delta in (2.0, 3.0, 5.0):
                r = apply_signal(games_by_batter, window,
                                 args.baseline_min, delta)
                summarize(r, f"sweep window={window} delta=+-{delta}")


if __name__ == "__main__":
    main()
