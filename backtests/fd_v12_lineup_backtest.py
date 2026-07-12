#!/usr/bin/env python3
"""v1.2 rules-only lineup backtest: daily anchor + 4-batter stack vs actuals."""
import csv, os, statistics as st, sys
from collections import defaultdict

PITCHER_CSV = "fd_gate_starts.csv"
BATTER_CSV = "fd_batter_games.csv"
OUT_CSV = "fd_v12_daily.csv"
MIN_WEAK_PRIOR_STARTS = 3
STACK_SIZE = 4

def fnum(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def fbool(v): return str(v).strip().lower() == "true"

def load_pitchers(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            r["fd_pts"] = fnum(r.get("fd_pts"))
            r["trail_whip"] = fnum(r.get("trail_whip"))
            r["trail_k9"] = fnum(r.get("trail_k9"))
            r["prior_starts"] = int(fnum(r.get("prior_starts")) or 0)
            r["warmup"] = fbool(r.get("warmup"))
            r["opener"] = fbool(r.get("opener"))
            r["anchor_pool"] = fbool(r.get("anchor_pool"))
            if r["fd_pts"] is not None: rows.append(r)
    return rows

def load_batters(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            r["fd_pts"] = fnum(r.get("fd_pts"))
            r["baseline_avg"] = fnum(r.get("baseline_avg"))
            r["warmup"] = fbool(r.get("warmup"))
            if r["fd_pts"] is not None: rows.append(r)
    return rows

def mean(xs): return st.mean(xs) if xs else None

def paired_summary(label, diffs):
    if not diffs:
        print(f"  {label}: no data"); return
    wins = sum(1 for d in diffs if d > 0)
    print(f"  {label}: n={len(diffs)}  mean_diff={st.mean(diffs):+.2f}  "
          f"median_diff={st.median(diffs):+.2f}  win_rate={wins/len(diffs):.1%}")

def main():
    for p in (PITCHER_CSV, BATTER_CSV):
        if not os.path.exists(p): sys.exit(f"missing {p} -- run from backtests/")
    pitchers, batters = load_pitchers(PITCHER_CSV), load_batters(BATTER_CSV)

    p_by_date = defaultdict(list)
    for r in pitchers: p_by_date[r["date"]].append(r)
    b_by_game, b_by_date = defaultdict(list), defaultdict(list)
    for r in batters:
        b_by_game[(r["date"], r["game_pk"])].append(r)
        b_by_date[r["date"]].append(r)

    daily = []
    for date in sorted(p_by_date):
        day_p = p_by_date[date]
        qualified = [r for r in day_p if not r["warmup"] and not r["opener"]]
        rec = {"date": date, "n_games": len({r["game_pk"] for r in day_p})}

        pool = [r for r in day_p if r["anchor_pool"] and r["trail_k9"] is not None]
        if pool:
            pick = max(pool, key=lambda r: (r["trail_k9"], -(r["trail_whip"] or 99)))
            pool_mean = mean([r["fd_pts"] for r in pool])
            slate_mean = mean([r["fd_pts"] for r in qualified])
            rec.update(anchor_name=pick["name"], anchor_pts=pick["fd_pts"],
                anchor_pool_n=len(pool), anchor_pool_mean=round(pool_mean, 2),
                anchor_vs_pool=round(pick["fd_pts"] - pool_mean, 2),
                anchor_vs_slate=round(pick["fd_pts"] - slate_mean, 2) if slate_mean is not None else None)

        weak_cands = [r for r in qualified if r["trail_whip"] is not None
                      and r["prior_starts"] >= MIN_WEAK_PRIOR_STARTS]
        if weak_cands:
            weak = max(weak_cands, key=lambda r: r["trail_whip"])
            game_bats = b_by_game.get((date, weak["game_pk"]), [])
            opp = [b for b in game_bats if b["team"] != weak["team"]]
            ranked = sorted([b for b in opp if b["baseline_avg"] is not None and not b["warmup"]],
                            key=lambda b: b["baseline_avg"], reverse=True)
            stack = ranked[:STACK_SIZE]
            if len(stack) == STACK_SIZE:
                stack_pts = sum(b["fd_pts"] for b in stack)
                opp_mean4 = STACK_SIZE * mean([b["fd_pts"] for b in opp])
                day_mean4 = STACK_SIZE * mean([b["fd_pts"] for b in b_by_date[date]])
                rec.update(weak_pitcher=weak["name"], weak_whip=weak["trail_whip"],
                    stack_pts=round(stack_pts, 2),
                    stack_vs_opp=round(stack_pts - opp_mean4, 2),
                    stack_vs_day=round(stack_pts - day_mean4, 2))

        if "anchor_pts" in rec or "stack_pts" in rec: daily.append(rec)

    if not daily: sys.exit("no gradable slate days found")

    fields = ["date","n_games","anchor_name","anchor_pts","anchor_pool_n",
              "anchor_pool_mean","anchor_vs_pool","anchor_vs_slate",
              "weak_pitcher","weak_whip","stack_pts","stack_vs_opp","stack_vs_day"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in daily: w.writerow({k: r.get(k, "") for k in fields})
    print(f"Wrote {len(daily)} slate days to {OUT_CSV}\n")

    def block(rows, title):
        print(f"=== {title} ===")
        a_pts = [r["anchor_pts"] for r in rows if "anchor_pts" in r]
        if a_pts:
            dis = sum(1 for x in a_pts if x < 5) / len(a_pts)
            ceil = sum(1 for x in a_pts if x >= 35) / len(a_pts)
            print(f"  ANCHOR pick: n={len(a_pts)}  mean={st.mean(a_pts):.2f}  "
                  f"median={st.median(a_pts):.2f}  disaster(<5)={dis:.1%}  ceiling(35+)={ceil:.1%}")
            paired_summary("  vs pool mean ", [r["anchor_vs_pool"] for r in rows if "anchor_vs_pool" in r])
            paired_summary("  vs slate mean", [r["anchor_vs_slate"] for r in rows if r.get("anchor_vs_slate") is not None])
        s_pts = [r["stack_pts"] for r in rows if "stack_pts" in r]
        if s_pts:
            print(f"  STACK (4 bats vs weakest arm): n={len(s_pts)}  "
                  f"mean={st.mean(s_pts):.2f}  median={st.median(s_pts):.2f}")
            paired_summary("  vs same-game random 4", [r["stack_vs_opp"] for r in rows if "stack_vs_opp" in r])
            paired_summary("  vs league-wide random 4", [r["stack_vs_day"] for r in rows if "stack_vs_day" in r])
        print()

    block(daily, "OVERALL (all slate days)")
    by_month = defaultdict(list)
    for r in daily: by_month[r["date"][:7]].append(r)
    for m in sorted(by_month): block(by_month[m], f"MONTH {m}")

if __name__ == "__main__":
    main()
