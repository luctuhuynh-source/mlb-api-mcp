#!/usr/bin/env python3
"""
LineStar FanDuel NBA history puller.

For every slate-day LineStar offers (~1 season), downloads the GetSalariesV5
payload (site=2 FanDuel, sport=2 NBA) and rebuilds three CSVs:

  backtests/nba/linestar/players.csv    one row per player-slate-day:
      salary, position, team/opp, LineStar projection, actual FD points,
      injury status, Vegas line/total, final score
  backtests/nba/linestar/ownership.csv  realized ownership per contest
      (every tracked contest, incl. the $200K NBA Shot), plus LineStar's
      projected ownership per slate
  backtests/nba/linestar/games.csv      one row per game-day: lines, totals,
      final scores

Raw JSON is kept gzipped under backtests/nba/linestar/raw/ so nothing has to
be re-downloaded; re-running only fetches days not yet on disk (the last few
days are always refreshed because results/ownership fill in after lock).

Usage (from the repo root):
    python3 backtests/nba/linestar_pull.py            # all available days
    python3 backtests/nba/linestar_pull.py --days 30  # only the last 30
"""
import argparse, csv, gzip, io, json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timedelta

BASE = "https://www.linestarapp.com/DesktopModules/DailyFantasyApi/API/Fantasy/GetSalariesV5"
SITE, SPORT = 2, 2          # FanDuel, NBA
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "linestar")
RAW = os.path.join(OUT, "raw")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) backtest-puller/1.0"}
STAT_NAMES = {1: "active", 2: "questionable", 3: "doubtful", 4: "out", 5: "GTD"}


def fetch(period_id):
    q = urllib.parse.urlencode({"site": SITE, "sport": SPORT, "periodId": period_id})
    req = urllib.request.Request(f"{BASE}?{q}", headers=UA)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"  period {period_id}: attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return None


def period_date(p):
    return p["StartDate"][:10]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="only the most recent N slate-days (0 = all)")
    ap.add_argument("--sleep", type=float, default=1.5)
    args = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)

    # period list comes with any payload; use the current one (periodId=0 → latest)
    first = fetch(0)
    if not first:
        sys.exit("could not reach LineStar")
    periods = sorted(first["Periods"], key=period_date)
    if args.days:
        periods = periods[-args.days:]
    today = datetime.utcnow().date()
    print(f"{len(periods)} slate-days: {period_date(periods[0])} .. {period_date(periods[-1])}")

    # ---- download (skip what we have, always refresh the last 3 days) ----
    for p in periods:
        d, pid = period_date(p), p["Id"]
        path = os.path.join(RAW, f"{d}_{pid}.json.gz")
        recent = (today - datetime.strptime(d, "%Y-%m-%d").date()) <= timedelta(days=3)
        if os.path.exists(path) and not recent:
            continue
        data = fetch(pid)
        if data is None:
            print(f"  {d} ({pid}): GAVE UP")
            continue
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(data, f)
        print(f"  {d} ({pid}): saved")
        time.sleep(args.sleep)

    rebuild()


def rebuild():
    """Rebuild the three CSVs from the gzipped raw payloads on disk."""
    players, own, games = [], [], []
    for fn in sorted(os.listdir(RAW)):
        if not fn.endswith(".json.gz"):
            continue
        d, pid = fn[:10], int(fn[11:].split(".")[0])
        with gzip.open(os.path.join(RAW, fn), "rt", encoding="utf-8") as f:
            data = json.load(f)
        sc = json.loads(data.get("SalaryContainerJson") or "{}")
        gmap = {}
        for g in sc.get("Games", []):
            gmap[g["GameId"]] = g
            games.append(dict(date=d, period_id=pid, game_id=g["GameId"], away=g["AwayTeam"], home=g["HomeTeam"],
                              line_home=g.get("VegasLineHome"), total=g.get("VegasOverUnder"),
                              ml_away=g.get("VegasMoneyLineAway"), ml_home=g.get("VegasMoneyLineHome"),
                              away_pts=g.get("AwayTeamPoints"), home_pts=g.get("HomeTeamPoints"),
                              status=g.get("StatusText"), tip_utc=g.get("DateUtc")))
        smap = {}
        for s in sc.get("Salaries", []):
            smap[s["Id"]] = s
            g = gmap.get(s.get("GID"), {})
            is_home = s.get("PTEAM") == g.get("HomeTeam")
            line = g.get("VegasLineHome") if is_home else g.get("VegasLineAway")
            players.append(dict(date=d, period_id=pid, salary_id=s["Id"], player_id=s.get("PID"), name=s.get("Name"),
                                pos=s.get("POS"), team=s.get("PTEAM"), opp=s.get("OTEAM"), home=int(bool(is_home)),
                                salary=s.get("SAL"), ls_proj=s.get("PP"), ls_floor=s.get("Floor"), ls_ceil=s.get("Ceil"),
                                ls_conf=s.get("Conf"), ppg=s.get("PPG"), actual_fd_pts=s.get("PS"),
                                status_code=s.get("STAT"), status=STAT_NAMES.get(s.get("STAT"), s.get("STAT")),
                                game=s.get("GI"), line=line, total=g.get("VegasOverUnder"),
                                opp_rank=s.get("OppRank"), opp_total=s.get("OppTotal")))
        o = data.get("Ownership") or {}
        slate_by_group = {sl.get("DfsSlateId"): sl for sl in (o.get("Slates") or [])}
        for c in o.get("ContestResults") or []:
            cc = c["Contest"]
            sl = slate_by_group.get(cc.get("GroupId"), {})
            for od in c.get("OwnershipData") or []:
                s = smap.get(od["SalaryId"], {})
                own.append(dict(date=d, period_id=pid, kind="actual", contest_id=cc.get("ContestId"),
                                contest=cc.get("ContestName"), entry_fee=cc.get("EntryFee"), entries=cc.get("EntryCount"),
                                purse=cc.get("Purse"), contest_type=cc.get("ContestType"), fd_slate_id=cc.get("GroupId"),
                                slate=sl.get("SlateName"), slate_games=sl.get("Games"),
                                salary_id=od["SalaryId"], player_id=od.get("PlayerId"), name=s.get("Name"),
                                team=s.get("PTEAM"), pos=s.get("POS"), salary=s.get("SAL"), actual_fd_pts=s.get("PS"),
                                owned_pct=od.get("Owned")))
        for sid, rows in (o.get("Projected") or {}).items():
            for od in rows or []:
                s = smap.get(od["SalaryId"], {})
                own.append(dict(date=d, period_id=pid, kind="projected", contest_id=None, contest=None, entry_fee=None,
                                entries=None, purse=None, contest_type=None, fd_slate_id=None, slate=sid, slate_games=None,
                                salary_id=od["SalaryId"], player_id=od.get("PlayerId"), name=s.get("Name"),
                                team=s.get("PTEAM"), pos=s.get("POS"), salary=s.get("SAL"), actual_fd_pts=s.get("PS"),
                                owned_pct=od.get("Owned")))

    for name, rows in (("players.csv", players), ("ownership.csv", own), ("games.csv", games)):
        if not rows:
            continue
        with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(f"{name}: {len(rows):,} rows")
    print("done")



if __name__ == "__main__":
    main()
