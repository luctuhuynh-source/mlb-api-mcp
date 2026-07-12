#!/usr/bin/env python3
"""v1.3 daily screen: probables -> gates -> ranked anchor pool + stack target.
Usage: python3 fd_daily_screen.py [YYYY-MM-DD]   (default: today)"""
import json, sys, urllib.request
from datetime import date as dt

WHIP_MAX, K9_MIN, WINDOW, MIN_STARTS_WEAK = 1.35, 8.0, 6, 3
SEASONS = ("2026", "2025")

def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

def outs_of(ip):
    if not ip: return 0
    whole, _, frac = str(ip).partition(".")
    return int(whole) * 3 + (int(frac) if frac else 0)

def trailing(pid, slate_date):
    logs = []
    for season in SEASONS:
        try:
            d = get(f"https://statsapi.mlb.com/api/v1/people/{pid}/stats"
                    f"?stats=gameLog&group=pitching&season={season}")
            for s in d.get("stats", []):
                logs += s.get("splits", [])
        except Exception:
            pass
    logs = [g for g in logs if g.get("date", "9999") < slate_date]
    logs.sort(key=lambda g: g.get("date", ""))
    last = logs[-WINDOW:]
    if len(last) < WINDOW:
        return None  # warmup: fewer than 6 prior appearances
    outs = sum(outs_of(g["stat"].get("inningsPitched")) for g in last)
    bb = sum(int(g["stat"].get("baseOnBalls", 0)) for g in last)
    h = sum(int(g["stat"].get("hits", 0)) for g in last)
    k = sum(int(g["stat"].get("strikeOuts", 0)) for g in last)
    ip = outs / 3
    if ip <= 0: return None
    return {"whip": round((bb + h) / ip, 3), "k9": round(k * 9 / ip, 2),
            "ip": round(ip, 1), "n": len(last)}

def main():
    slate = sys.argv[1] if len(sys.argv) > 1 else dt.today().isoformat()
    sched = get(f"https://statsapi.mlb.com/api/v1/schedule?sportId=1"
                f"&date={slate}&hydrate=probablePitcher")
    games = []
    for d in sched.get("dates", []):
        for g in d.get("games", []):
            if g.get("gameType") != "R": continue
            t = g["teams"]
            for side, opp in (("away", "home"), ("home", "away")):
                pp = t[side].get("probablePitcher")
                if pp:
                    games.append({"pid": pp["id"], "name": pp["fullName"],
                        "team": t[side]["team"]["name"],
                        "opp": t[opp]["team"]["name"],
                        "venue": g.get("venue", {}).get("name", "")})
    if not games:
        sys.exit(f"no probables posted for {slate} yet")
    print(f"{slate}: {len(games)} probables\n")

    pool, failed, warmup = [], [], []
    for g in games:
        tr = trailing(g["pid"], slate)
        if tr is None:
            warmup.append(g); continue
        g.update(tr)
        reasons = []
        if tr["whip"] > WHIP_MAX: reasons.append(f"WHIP {tr['whip']}")
        if tr["k9"] < K9_MIN: reasons.append(f"K/9 {tr['k9']} (K-floor)")
        (pool if not reasons else failed).append(
            g if not reasons else {**g, "why": ", ".join(reasons)})

    print("=== ANCHOR POOL (ranked, v1.3 pick first) ===")
    pool.sort(key=lambda x: (-x["k9"], x["whip"]))
    for i, g in enumerate(pool):
        tag = " <-- PICK" if i == 0 else ""
        print(f"  {g['name']:<24} {g['team']:<22} K/9={g['k9']:<6} "
              f"WHIP={g['whip']:<6} vs {g['opp']}{tag}")
    if not pool: print("  (empty)")

    print("\n=== GATED OUT ===")
    for g in sorted(failed, key=lambda x: x["k9"], reverse=True):
        print(f"  {g['name']:<24} {g['why']}")

    if warmup:
        print("\n=== INSUFFICIENT WINDOW (<6 prior apps) ===")
        for g in warmup: print(f"  {g['name']:<24} {g['team']}")

    weak_c = [g for g in failed + pool if g.get("whip") is not None]
    if weak_c:
        weak = max(weak_c, key=lambda x: x["whip"])
        print(f"\n=== STACK TARGET (worst trailing WHIP) ===")
        print(f"  {weak['name']} ({weak['team']}, WHIP {weak['whip']}) "
              f"-> stack {weak['opp']} bats, top 4 by season baseline")
    print("\nManual checks before lock: pitch-count/leash news on the PICK, "
          "BvP 15+ PA, fade-list conflicts, weather.")

if __name__ == "__main__":
    main()
