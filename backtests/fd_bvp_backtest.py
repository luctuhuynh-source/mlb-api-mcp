#!/usr/bin/env python3
"""BvP signal test: does career 15+ PA BvP predict baseline-relative FD pts?"""
import csv, json, os, statistics as st, sys, time, urllib.request
from collections import defaultdict

PITCHER_CSV, BATTER_CSV = "fd_gate_starts.csv", "fd_batter_games.csv"
CACHE_FILE, OUT_CSV = "bvp_cache.json", "fd_bvp_results.csv"
TOP_N_PER_TEAM, MIN_PRIOR_GAMES, MIN_BVP_PA = 6, 15, 15
GOOD_AVG, BAD_AVG = 0.300, 0.200

def fnum(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def fbool(v): return str(v).strip().lower() == "true"

def fetch_bvp(batter_id, pitcher_id):
    url = (f"https://statsapi.mlb.com/api/v1/people/{batter_id}/stats"
           f"?stats=vsPlayerTotal&group=hitting&opposingPlayerId={pitcher_id}")
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.load(resp)
        for s in data.get("stats", []):
            for sp in s.get("splits", []):
                stat = sp.get("stat", {})
                pa, avg = stat.get("plateAppearances"), stat.get("avg")
                if pa is not None:
                    return {"pa": int(pa), "avg": fnum(avg)}
    except Exception:
        return None
    return {"pa": 0, "avg": None}

def main():
    starters = {}
    with open(PITCHER_CSV, newline="") as f:
        for r in csv.DictReader(f):
            if not fbool(r.get("opener")):
                starters.setdefault((r["date"], r["game_pk"]), []).append(
                    {"team": r["team"], "pid": r["player_id"]})

    by_team_game = defaultdict(list)
    with open(BATTER_CSV, newline="") as f:
        for r in csv.DictReader(f):
            r["fd_pts"], r["baseline_avg"] = fnum(r.get("fd_pts")), fnum(r.get("baseline_avg"))
            pg = fnum(r.get("prior_games")) or 0
            if (r["fd_pts"] is not None and r["baseline_avg"] is not None
                    and not fbool(r.get("warmup")) and pg >= MIN_PRIOR_GAMES):
                by_team_game[(r["date"], r["game_pk"], r["team"])].append(r)

    tasks = []
    for (date, gpk, team), bats in by_team_game.items():
        opps = [s for s in starters.get((date, gpk), []) if s["team"] != team]
        if len(opps) != 1: continue
        opp = opps[0]["pid"]
        for b in sorted(bats, key=lambda x: x["baseline_avg"], reverse=True)[:TOP_N_PER_TEAM]:
            tasks.append((b["player_id"], opp, b["fd_pts"], b["baseline_avg"], date))
    print(f"{len(tasks)} batter-games; unique pairs to fetch: "
          f"{len({(t[0], t[1]) for t in tasks})}")

    cache = {}
    if os.path.exists(CACHE_FILE):
        cache = json.load(open(CACHE_FILE))
    fetched = 0
    for i, (bid, pid, _, _, _) in enumerate(tasks):
        key = f"{bid}-{pid}"
        if key in cache: continue
        cache[key] = fetch_bvp(bid, pid)
        fetched += 1
        if fetched % 200 == 0:
            json.dump(cache, open(CACHE_FILE, "w"))
            print(f"  fetched {fetched} (task {i}/{len(tasks)})")
        time.sleep(0.05)
    json.dump(cache, open(CACHE_FILE, "w"))
    print(f"fetch done ({fetched} new)")

    rows, buckets = [], defaultdict(list)
    for bid, pid, pts, base, date in tasks:
        c = cache.get(f"{bid}-{pid}")
        if not c or c["pa"] is None or c["pa"] < MIN_BVP_PA or c["avg"] is None:
            continue
        rel = pts - base
        b = "GOOD" if c["avg"] >= GOOD_AVG else ("BAD" if c["avg"] <= BAD_AVG else "MID")
        buckets[b].append(rel)
        rows.append({"date": date, "batter": bid, "pitcher": pid, "bvp_pa": c["pa"],
                     "bvp_avg": c["avg"], "fd_pts": pts, "baseline": base,
                     "rel": round(rel, 2), "bucket": b})

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["none"])
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"\nWrote {len(rows)} qualifying (15+ PA) matchup-games to {OUT_CSV}\n")

    print("=== BvP SIGNAL TEST (fd_pts minus own baseline) ===")
    for b in ("GOOD", "MID", "BAD"):
        xs = buckets.get(b, [])
        if xs:
            print(f"  {b:4s} (n={len(xs)}): mean_rel={st.mean(xs):+.2f}  "
                  f"median_rel={st.median(xs):+.2f}  "
                  f"beat_baseline={sum(1 for x in xs if x > 0)/len(xs):.1%}")
    g, bd = buckets.get("GOOD", []), buckets.get("BAD", [])
    if g and bd:
        print(f"\n  GOOD minus BAD mean_rel: {st.mean(g) - st.mean(bd):+.2f}"
              f"  (criterion: >= +1.00 with n >= 100 per bucket)")

if __name__ == "__main__":
    main()
