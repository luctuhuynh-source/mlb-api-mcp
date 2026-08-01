#!/usr/bin/env python3
"""FD v1.7 candidate backtest v2 — Q1 form veto + Q2 environment validity
+ Q3 opener-aware side rule (added 7/31, criteria frozen pre-run).
Supersedes fd_v17_backtest.py (Q1/Q2 logic identical; Q3 additive).

Usage:
    python fd_v17_backtest_v2.py --gate backtests/fd_gate_starts.csv \
        --batters backtests/fd_batter_games.csv \
        --census f5_board_census_MASTER_2025mar18-sep28.jsonl \
                 "f5_board_census*2026*.jsonl"
"""
import argparse, csv, glob, json, math, sys
from collections import defaultdict

ALIASES = {
    "date":      ["date", "game_date", "start_date", "gamedate"],
    "pitcher":   ["pitcher", "pitcher_name", "name", "player", "player_name"],
    "team":      ["team", "team_abbr", "tm"],
    "opp":       ["opp", "opponent", "opp_abbr"],
    "ip":        ["ip", "innings", "innings_pitched"],
    "er":        ["er", "earned_runs"],
    "h":         ["h", "hits", "hits_allowed"],
    "bb":        ["bb", "walks", "base_on_balls"],
    "k":         ["k", "so", "strikeouts"],
    "bat_date":  ["date", "game_date"],
    "bat_team":  ["team", "team_abbr", "tm"],
    "bat_name":  ["name", "player", "player_name", "batter"],
    "fd_pts":    ["fd_points", "fd_pts", "fdp", "points", "fanduel_points"],
    "baseline":  ["fd_mean", "baseline_avg", "baseline", "season_mean", "fd_baseline", "fppg"],
}


TEAMMAP = {"ARI":"Arizona Diamondbacks","AZ":"Arizona Diamondbacks","ATH":"Athletics","OAK":"Athletics","ATL":"Atlanta Braves","BAL":"Baltimore Orioles","BOS":"Boston Red Sox","CHC":"Chicago Cubs","CIN":"Cincinnati Reds","CLE":"Cleveland Guardians","COL":"Colorado Rockies","CWS":"Chicago White Sox","DET":"Detroit Tigers","HOU":"Houston Astros","KC":"Kansas City Royals","LAA":"Los Angeles Angels","LAD":"Los Angeles Dodgers","MIA":"Miami Marlins","MIL":"Milwaukee Brewers","MIN":"Minnesota Twins","NYM":"New York Mets","NYY":"New York Yankees","PHI":"Philadelphia Phillies","PIT":"Pittsburgh Pirates","SD":"San Diego Padres","SEA":"Seattle Mariners","SF":"San Francisco Giants","STL":"St. Louis Cardinals","TB":"Tampa Bay Rays","TEX":"Texas Rangers","TOR":"Toronto Blue Jays","WSH":"Washington Nationals"}
def norm(code):
    return TEAMMAP.get(code.strip().rstrip("2"), code)

def map_cols(header, wanted, path):
    out, missing = {}, []
    low = {h.lower(): h for h in header}
    for key in wanted:
        hit = next((low[a] for a in ALIASES[key] if a in low), None)
        if hit: out[key] = hit
        else: missing.append(key)
    if missing:
        sys.exit(f"[SCHEMA] {path}: could not map {missing}.\nHeader = {list(header)}\n"
                 f"Edit ALIASES at top of script and re-run.")
    return out

def fip_ip(v):
    s = str(v)
    if "." in s:
        w, f = s.split(".")
        return int(w) + int(f or 0) / 3.0
    return float(v)

def load_gate(path):
    rows = list(csv.DictReader(open(path)))
    cm = map_cols(rows[0].keys(), ["date","pitcher","team","ip","er","h","bb","k"], path)
    starts = defaultdict(list)
    for r in rows:
        d = r[cm["date"]][:10]
        ip = fip_ip(r[cm["ip"]])
        er = float(r[cm["er"]] or 0); h = float(r[cm["h"]] or 0); bb = float(r[cm["bb"]] or 0)
        starts[r[cm["pitcher"]]].append((d, ip, er, h + bb, r[cm["team"]], ""))
    for p in starts: starts[p].sort()
    return starts

def window(starts, pitcher, before_date, n=6):
    return [s for s in starts.get(pitcher, []) if s[0] < before_date][-n:]

def trailing_whip(starts, pitcher, before_date):
    rows = window(starts, pitcher, before_date)
    ip = sum(s[1] for s in rows); wn = sum(s[3] for s in rows)
    return (wn / ip if ip else None), ip

def is_opener(starts, pitcher, before_date):
    rows = window(starts, pitcher, before_date)
    if len(rows) < 2: return None            # unclassified
    return (sum(s[1] for s in rows) / len(rows)) <= 3.0

def recovered(starts, pitcher, before_date):
    last2 = [s for s in starts.get(pitcher, []) if s[0] < before_date][-2:]
    if len(last2) < 2: return False
    if all(s[2] <= 2 for s in last2): return True
    ip = sum(s[1] for s in last2)
    return ip >= 8 and (sum(s[3] for s in last2) / ip) <= 1.10

def load_census(paths):
    slates = defaultdict(dict)
    for pat in paths:
        for path in glob.glob(pat):
            for line in open(path):
                line = line.strip()
                if not line: continue
                rec = json.loads(line)
                d = (rec.get("d") or rec.get("date") or rec.get("game_date") or "")[:10]
                key = rec.get("m") or rec.get("matchup") or f'{rec.get("away","?")}@{rec.get("home","?")}'
                lines = rec.get("bk") or rec.get("lines") or rec.get("books") or {}
                vals = []
                if isinstance(lines, dict):
                    for bk, v in lines.items():
                        pt = v.get("total") if isinstance(v, dict) else (v[0] if isinstance(v, list) and v else v)
                        if pt is not None: vals.append(float(pt))
                elif isinstance(lines, list):
                    vals = [float(x) for x in lines if x is not None]
                if not vals and rec.get("consensus") is not None:
                    vals = [float(rec["consensus"])]
                if not vals: continue
                vals.sort(); n = len(vals)
                rec["_consensus"] = vals[n//2] if n % 2 else (vals[n//2-1]+vals[n//2])/2
                slates[d][key] = rec
    return slates

def full_game_runs(rec, cache, key, date):
    for f in ("f5_total","final_total_runs","total_runs","full_runs","runs_total"):
        if rec.get(f) is not None: return float(rec[f])
    ck = f"{date}|{key}"
    if ck in cache: return cache[ck]
    try:
        import statsapi
        away, home = [norm(x) for x in key.split("@")]
        for g in statsapi.schedule(date=date):
            names = (g.get("away_name",""), g.get("home_name",""))
            if any(away in n for n in names) or any(home in n for n in names):
                r = (g.get("away_score",0) or 0) + (g.get("home_score",0) or 0)
                cache[ck] = float(r); return cache[ck]
    except Exception:
        return None
    return None

def pct(x): return "n/a" if x is None else f"{100*x:.1f}%"
def p90(xs):
    if not xs: return None
    xs = sorted(xs); i = 0.9 * (len(xs) - 1)
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return xs[lo] if lo == hi else xs[lo] + (i - lo) * (xs[hi] - xs[lo])
def dis(xs): return sum(1 for x in xs if x < 10) / len(xs) if xs else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    ap.add_argument("--batters", required=True)
    ap.add_argument("--census", nargs="+", required=True)
    ap.add_argument("--min-games", type=int, default=6)
    args = ap.parse_args()

    starts = load_gate(args.gate)
    slates = load_census(args.census)

    brows = list(csv.DictReader(open(args.batters)))
    bm = map_cols(brows[0].keys(), ["bat_date","bat_team","bat_name","fd_pts","baseline"], args.batters)
    bat_by_dt = defaultdict(list)
    for r in brows:
        bat_by_dt[(r[bm["bat_date"]][:10], r[bm["bat_team"]])].append(
            (float(r[bm["baseline"]] or 0), r[bm["bat_name"]], float(r[bm["fd_pts"]] or 0)))

    def stack_score(date, team):
        bats = sorted(bat_by_dt.get((date, team), []), reverse=True)[:4]
        return (sum(b[2] for b in bats), len(bats))

    start_by_dt = {}
    for p, rows in starts.items():
        for (d, ip, er, wn, team, opp) in rows:
            start_by_dt[(d, team)] = p

    q1, q2, q3 = [], [], []
    cache = {}
    for date, games in sorted(slates.items()):
        if len(games) < args.min_games: continue
        ranked = sorted(games.items(), key=lambda kv: -kv[1]["_consensus"])

        runs = {k: full_game_runs(rec, cache, k, date) for k, rec in games.items()}
        if all(v is not None for v in runs.values()):
            mx = max(runs.values()); top_key = ranked[0][0]
            q2.append(dict(date=date, n=len(games), top=top_key,
                           hit=int(runs[top_key] == mx),
                           top2=int(runs[top_key] >= sorted(runs.values())[-2])))

        def sides(game_key):
            away, home = [norm(x) for x in game_key.split("@")]
            pa, ph = start_by_dt.get((date, away)), start_by_dt.get((date, home))
            if not pa or not ph: return None
            wa, _ = trailing_whip(starts, pa, date)
            wh, _ = trailing_whip(starts, ph, date)
            if wa is None or wh is None: return None
            return away, home, pa, ph, wa, wh

        def pick_control(game_key):
            s = sides(game_key)
            if not s: return None
            away, home, pa, ph, wa, wh = s
            return (home, pa) if wa >= wh else (away, ph)

        def pick_q3(game_key):
            s = sides(game_key)
            if not s: return None
            away, home, pa, ph, wa, wh = s
            oa, oh = is_opener(starts, pa, date), is_opener(starts, ph, date)
            if oa and not oh and wh is not None and wh < 1.75:
                return (home, pa)
            if oh and not oa and wa is not None and wa < 1.75:
                return (away, ph)
            return (home, pa) if wa >= wh else (away, ph)

        top_key = ranked[0][0]
        control = pick_control(top_key)
        q3pick  = pick_q3(top_key)

        test = None
        for key, rec in ranked:
            pick = pick_control(key)
            if pick is None: continue
            if recovered(starts, pick[1], date): continue
            test = pick; break
        if control:
            cs, cn = stack_score(date, control[0])
            if cn == 4:
                row = dict(date=date, c_team=control[0], c_score=cs)
                if test:
                    ts, tn = stack_score(date, test[0])
                    if tn == 4:
                        row.update(t_team=test[0], t_score=ts,
                                   vetoed=int(test[0] != control[0]))
                        q1.append(row)
                if q3pick:
                    qs, qn = stack_score(date, q3pick[0])
                    if qn == 4:
                        q3.append(dict(date=date, c_team=control[0], c_score=cs,
                                       q_team=q3pick[0], q_score=qs,
                                       fired=int(q3pick[0] != control[0])))

    print("=== Q2: environment validity ===")
    for season in ("2025", "2026"):
        rows = [r for r in q2 if r["date"].startswith(season)]
        if not rows: print(f"{season}: no graded slates"); continue
        hit = sum(r["hit"] for r in rows) / len(rows)
        base = sum(1 / r["n"] for r in rows) / len(rows)
        top2 = sum(r["top2"] for r in rows) / len(rows)
        print(f"{season}: n={len(rows)} hit={pct(hit)} baseline={pct(base)} "
              f"ratio={hit/base:.2f} top2={pct(top2)}  PASS_needs>=1.5x")

    print("\n=== Q1: recent-form veto (2026) ===")
    if q1:
        c = [r["c_score"] for r in q1]; t = [r["t_score"] for r in q1]
        print(f"n={len(q1)} vetoed_on={sum(r['vetoed'] for r in q1)}")
        print(f"CONTROL mean={sum(c)/len(c):.2f} p90={p90(c):.2f} disaster={pct(dis(c))}")
        print(f"TEST    mean={sum(t)/len(t):.2f} p90={p90(t):.2f} disaster={pct(dis(t))}")
        print("PASS needs: test mean >= control+2, disaster <= 2/3*control, p90 >= control-5")
    else:
        print("no Q1 slates scored — check schema/batter coverage")

    print("\n=== Q3: opener-aware side rule (2026) ===")
    if q3:
        c = [r["c_score"] for r in q3]; q = [r["q_score"] for r in q3]
        fired = [r for r in q3 if r["fired"]]
        print(f"n={len(q3)} fired_on={len(fired)}")
        print(f"OVERALL  control mean={sum(c)/len(c):.2f} disaster={pct(dis(c))} | "
              f"q3 mean={sum(q)/len(q):.2f} disaster={pct(dis(q))}")
        if fired:
            fc = [r["c_score"] for r in fired]; fq = [r["q_score"] for r in fired]
            print(f"FIRED    n={len(fired)} control mean={sum(fc)/len(fc):.2f} | "
                  f"q3 mean={sum(fq)/len(fq):.2f}")
        print("PASS needs: fired n>=8 AND fired q3 mean >= fired control mean+3 "
              "AND overall q3 disaster <= overall control disaster; fired n<8 => INSUFFICIENT-N")
    else:
        print("no Q3 slates scored")

    for name, rows in (("fd_v17_q1_slates.csv", q1),
                       ("fd_v17_q2_slates.csv", q2),
                       ("fd_v17_q3_slates.csv", q3)):
        if rows:
            with open(f"backtests/{name}", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
