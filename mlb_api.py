import os
from datetime import datetime
from typing import List, Optional

import mlbstatsapi
import requests
from pybaseball import statcast, statcast_batter, statcast_pitcher

mlb = mlbstatsapi.Mlb()

# Base URL for The Odds API (https://the-odds-api.com/). The API key is read at
# call time from the ODDS_API_KEY environment variable and is never hardcoded.
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"


def get_odds_api_key() -> str:
    """Return the Odds API key from the environment, or raise a clear error.

    Raises
    ------
    RuntimeError
        If the ODDS_API_KEY environment variable is not set.
    """
    api_key = os.environ.get("ODDS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ODDS_API_KEY environment variable is not set. Set it to your "
            "the-odds-api.com API key to use the odds tools."
        )
    return api_key


def get_multiple_player_stats(
    mlb, person_ids: list, stats: list, groups: list, season: Optional[int] = None, **params
) -> dict:
    """
    returns stat data for a team

    Parameters
    ----------
    mlb : mlbstatsapi.Mlb
        The MLB stats API instance
    person_ids : list
        the person ids
    stats : list
        list of stat types. List of statTypes can be found at https://statsapi.mlb.com/api/v1/statTypes
    groups : list
        list of stat grous. List of statGroups can be found at https://statsapi.mlb.com/api/v1/statGroups
    season : str, optional
        Insert year to return team stats for a particular season, season=2018
    eventType : str, optional
        Notes for individual events for playLog, playlog can be filered by individual events.
        List of eventTypes can be found at https://statsapi.mlb.com/api/v1/eventTypes

    Returns
    -------
    dict
        returns a dict of stats

    See Also
    --------
    Mlb.get_stats : Get stats
    Mlb.get_team_stats : Get team stats
    Mlb.get_players_stats_for_game : Get player stats for a game

    Examples
    --------
    >>> mlb = Mlb()
    >>> stats = ['season', 'seasonAdvanced']
    >>> groups = ['hitting']
    >>> mlb.get_player_stats(647351, stats, groups)
    {'hitting': {'season': [HittingSeason], 'seasonadvanced': [HittingSeasonAdvanced] }}
    """
    from mlbstatsapi import mlb_module

    params["stats"] = stats
    params["group"] = groups

    hydrate_arr = []
    if groups:
        hydrate_arr.append(f"group=[{','.join(groups)}]")
    if stats:
        hydrate_arr.append(f"type=[{','.join(stats)}]")
    if season:
        hydrate_arr.append(f"season={season}")

    mlb_data = mlb._mlb_adapter_v1.get(
        endpoint=f"people?personIds={','.join(person_ids)}&hydrate=stats({','.join(hydrate_arr)})"
    )
    if 400 <= mlb_data.status_code <= 499:
        return {}

    splits = []

    for person in mlb_data.data["people"]:
        if person.get("stats"):
            splits.append(mlb_module.create_split_data(person["stats"]))

    return splits


def get_sabermetrics_for_players(
    mlb, player_ids: list, season: int, stat_name: Optional[str] = None, group: str = "hitting"
) -> dict:
    """
    Get sabermetric statistics (like WAR) for multiple players for a specific season.

    Parameters
    ----------
    mlb : mlbstatsapi.Mlb
        The MLB stats API instance
    player_ids : list
        List of player IDs to get sabermetrics for
    season : int
        The season year to get stats for
    stat_name : str, optional
        Specific sabermetric stat to extract (e.g., 'war', 'woba', 'wRc'). If None, returns all sabermetrics.
    group : str, optional
        The stat group ('hitting' or 'pitching'). Default is 'hitting'.

    Returns
    -------
    dict
        Dictionary containing player sabermetrics data
    """

    # Build the API endpoint URL
    endpoint = f"stats?stats=sabermetrics&group={group}&sportId=1&season={season}"

    # Make the API call directly
    response = mlb._mlb_adapter_v1.get(endpoint=endpoint)

    if 400 <= response.status_code <= 499:
        return {"error": f"API error: {response.status_code}"}

    if not response.data or "stats" not in response.data:
        return {"error": "No stats data found"}

    # Extract the relevant data
    result = {"season": season, "group": group, "players": []}

    # Filter for our specific players
    player_ids_int = [int(pid) for pid in player_ids]

    for stat_group in response.data["stats"]:
        if "splits" in stat_group:
            for split in stat_group["splits"]:
                if "player" in split and split["player"]["id"] in player_ids_int:
                    player_data = {
                        "player_id": split["player"]["id"],
                        "player_name": split["player"].get("fullName", "Unknown"),
                        "position": split.get("position", {}).get("abbreviation", "N/A"),
                        "team": split.get("team", {}).get("name", "N/A"),
                        "team_id": split.get("team", {}).get("id", None),
                    }

                    # Extract the sabermetric stats
                    if "stat" in split:
                        if stat_name:
                            # Return only the specific stat requested
                            if stat_name.lower() in split["stat"]:
                                player_data[stat_name] = split["stat"][stat_name.lower()]
                            else:
                                player_data[stat_name] = None
                                player_data["available_stats"] = list(split["stat"].keys())
                        else:
                            # Return all sabermetric stats
                            player_data["sabermetrics"] = split["stat"]

                    result["players"].append(player_data)

    return result


def get_team_id_from_name(team: str) -> Optional[int]:
    """Helper to get team ID from team name, partial name, or stringified ID."""
    # Accept stringified integer as ID
    try:
        return int(team)
    except (ValueError, TypeError):
        pass
    import csv

    team_lower = team.lower().strip()
    with open("current_mlb_teams.csv", "r") as f:
        reader = csv.DictReader(f)
        # First, try exact match
        for row in reader:
            if team_lower == row["team_name"].lower().strip():
                return int(row["team_id"])
        f.seek(0)
        next(reader)  # skip header
        # Then, try substring match
        for row in reader:
            if team_lower in row["team_name"].lower():
                return int(row["team_id"])
    return None


def get_team_abbreviation_from_name(team: str) -> Optional[str]:
    """
    Given a team name, partial name, or ID, return the 3-letter team abbreviation (e.g., 'NYY' for Yankees).
    Returns None if not found.
    """
    team_id = get_team_id_from_name(team)
    if team_id is None:
        return None
    team_info = mlb.get_team(team_id)
    return getattr(team_info, "abbreviation", None)


def check_result_size(result: dict, context: str) -> Optional[dict]:
    """
    Utility to check the size of a result dictionary (by word count). Returns an error dict if too large, else None.
    """
    import json

    word_count = len(json.dumps(result).split())
    if word_count > 100000:
        return {
            "error": (
                f"Result too large ({word_count} words). Please narrow your query "
                f"(e.g., shorter date range, specific {context})."
            )
        }
    return None


def validate_date_range(start_date: str, end_date: str) -> Optional[dict]:
    """
    Utility to check that start_date is before or equal to end_date.
    Returns an error dict if invalid, else None.
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start > end:
            return {"error": f"start_date ({start_date}) must be before or equal to end_date ({end_date})"}
    except Exception as e:
        return {"error": f"Invalid date format: {e}"}
    return None


def setup_mlb_tools(mcp):
    """Setup MLB tools for the MCP server"""
    # ---------------------------------------------------------------------------
# FD DFS BACKTEST SUMMARY TOOL — paste INSIDE setup_mlb_tools(mcp),
# indented exactly 4 spaces (as below), or the server crashes on boot.
#
# Serves pre-computed backtest results. Workflow:
#   1. Run fd_walk_gate_backtest.py / fd_batter_backtests.py LOCALLY.
#   2. Commit the output CSVs into backtests/ in the repo:
#        backtests/fd_gate_starts.csv
#        backtests/fd_batter_games.csv
#   3. Paste this tool, push, let Railway redeploy.
#
# No live MLB API calls — reads the committed CSV in milliseconds, so no
# MCP timeout risk. Returns a dict (never a bare list — the server's
# structured_content wrapper rejects lists, per the roster-tool bug).
# ---------------------------------------------------------------------------

    @mcp.tool()
    def get_fd_backtest_summary(
        kind: str = "pitcher",
        date_from: str = "",
        date_to: str = "",
    ) -> dict:
        """Summarize committed FanDuel DFS backtest CSVs.

        kind: 'pitcher' (walk-volatility gate, anchor-pool headline) or
              'batter' (form-delta signal + within-player paired test).
        date_from/date_to: optional YYYY-MM-DD filters on start/game date.
        """
        import csv as _csv
        import statistics as _st
        from collections import defaultdict as _dd
        from pathlib import Path as _Path

        base = _Path(__file__).resolve().parent / "backtests"
        files = {"pitcher": base / "fd_gate_starts.csv",
                 "batter": base / "fd_batter_games.csv"}
        if kind not in files:
            return {"error": "kind must be 'pitcher' or 'batter'"}
        path = files[kind]
        if not path.exists():
            return {"error": f"{path.name} not committed yet — run the "
                             "backtest locally and commit the CSV"}

        def _b(v):  # CSV booleans arrive as strings
            return str(v).strip().lower() == "true"

        with open(path, newline="") as f:
            rows = [r for r in _csv.DictReader(f)]
        if date_from:
            rows = [r for r in rows if r["date"] >= date_from]
        if date_to:
            rows = [r for r in rows if r["date"] <= date_to]
        for r in rows:
            r["fd_pts"] = float(r["fd_pts"])

        def _stats(sub, lo, hi):
            pts = [r["fd_pts"] for r in sub]
            if not pts:
                return {"n": 0}
            return {
                "n": len(pts),
                "mean": round(_st.mean(pts), 2),
                "median": round(_st.median(pts), 2),
                "stdev": round(_st.pstdev(pts), 2),
                "floor_rate_lt%d" % lo:
                    round(sum(p < lo for p in pts) / len(pts), 3),
                "negative_rate":
                    round(sum(p < 0 for p in pts) / len(pts), 3),
                "ceiling_rate_ge%d" % hi:
                    round(sum(p >= hi for p in pts) / len(pts), 3),
            }

        if kind == "pitcher":
            eligible = [r for r in rows
                        if not _b(r["warmup"]) and not _b(r["opener"])]
            pool = [r for r in eligible if _b(r["anchor_pool"])]
            return {
                "kind": "pitcher",
                "rows_total": len(rows),
                "eligible": len(eligible),
                "anchor_pool": len(pool),
                "headline_anchor_pool": {
                    "gated": _stats([r for r in pool if _b(r["gated"])],
                                    5, 35),
                    "passed": _stats([r for r in pool
                                      if not _b(r["gated"])], 5, 35),
                },
                "context_full_population": {
                    "gated": _stats([r for r in eligible
                                     if _b(r["gated"])], 5, 35),
                    "passed": _stats([r for r in eligible
                                      if not _b(r["gated"])], 5, 35),
                },
            }

        # batter
        eligible = [r for r in rows if not _b(r["warmup"])]
        out = {"kind": "batter", "rows_total": len(rows),
               "eligible": len(eligible), "buckets": {}}
        for bucket in ("HOT", "NEUTRAL", "COLD"):
            out["buckets"][bucket] = _stats(
                [r for r in eligible if r["bucket"] == bucket], 5, 25)
        per = _dd(lambda: {"HOT": [], "COLD": []})
        for r in eligible:
            if r["bucket"] in ("HOT", "COLD"):
                per[r["player_id"]][r["bucket"]].append(r["fd_pts"])
        deltas = [
            _st.mean(b["HOT"]) - _st.mean(b["COLD"])
            for b in per.values()
            if len(b["HOT"]) >= 3 and len(b["COLD"]) >= 3
        ]
        if deltas:
            pos = sum(d > 0 for d in deltas)
            out["within_player_paired"] = {
                "players": len(deltas),
                "mean_hot_minus_cold": round(_st.mean(deltas), 2),
                "median": round(_st.median(deltas), 2),
                "share_positive": round(pos / len(deltas), 2),
                "read": "~0 mean and ~0.5 positive = form is noise",
            }
        else:
            out["within_player_paired"] = {"players": 0}
        return out

    @mcp.tool()
    def get_xweather_hourly(location: str, hours: int = 24) -> dict:
        """Hourly Xweather forecast for any location. Accepts 'city,state'
        (e.g. 'san diego,ca'), 'lat,lon' (e.g. '53.765,-3.031' for Royal
        Birkdale), or airport codes. Returns per-hour temp, wind speed,
        gusts, direction, precip probability, and sky cover — built for
        golf wave-split scans and F5 park weather checks."""
        import os
        import requests

        cid = os.environ.get("XWEATHER_CLIENT_ID", "")
        sec = os.environ.get("XWEATHER_CLIENT_SECRET", "")
        if not cid or not sec:
            return {"error": "XWEATHER_CLIENT_ID / XWEATHER_CLIENT_SECRET not set in Railway variables"}

        hours = max(1, min(int(hours), 72))
        try:
            r = requests.get(
                f"https://data.api.xweather.com/forecasts/{location}",
                params={
                    "client_id": cid,
                    "client_secret": sec,
                    "filter": "1hr",
                    "limit": hours,
                },
                timeout=15,
            )
            data = r.json()
        except Exception as e:
            return {"error": f"request failed: {e}"}

        if not data.get("success") or not data.get("response"):
            return {"error": str(data.get("error"))}

        block = data["response"][0]
        periods = []
        for p in block.get("periods", []):
            periods.append({
                "time": p.get("dateTimeISO"),
                "tempF": p.get("tempF"),
                "windMPH": p.get("windSpeedMPH"),
                "gustMPH": p.get("windGustMPH"),
                "windDir": p.get("windDir"),
                "windDirDEG": p.get("windDirDEG"),
                "popPct": p.get("pop"),
                "precipIN": p.get("precipIN"),
                "skyPct": p.get("sky"),
                "weather": p.get("weather"),
            })

        return {
            "place": block.get("place", {}),
            "loc": block.get("loc", {}),
            "hours": len(periods),
            "periods": periods,
        }
# ============================================================
# DATA GOLF TOOLS for mlb-api-mcp (Railway)
# Paste EVERYTHING below inside setup_mlb_tools(mcp), indented
# 4 spaces, same as the Xweather tool. Requires Railway env var:
#   DATAGOLF_API_KEY = <your key>
# ============================================================

    DG_BASE = "https://feeds.datagolf.com"

    def _dg_get(path, params=None):
        import os
        import requests
        key = os.environ.get("DATAGOLF_API_KEY")
        if not key:
            return {"error": "DATAGOLF_API_KEY env var not set on Railway"}
        p = dict(params or {})
        p["key"] = key
        p.setdefault("file_format", "json")
        try:
            r = requests.get(f"{DG_BASE}/{path}", params=p, timeout=25)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": f"datagolf request failed: {e}"}

    def _dg_trim(d, keep_substrings):
        # keep only keys containing any whitelisted substring
        return {k: v for k, v in d.items()
                if any(s in k.lower() for s in keep_substrings)}

    @mcp.tool()
    def get_dg_field_waves(tour: str = "pga") -> dict:
        """Current-event field with tee times and early/late wave label
        per round, plus dg_ids. Primary pre-flight tool: replaces manual
        wave-splitting from screenshots. tour: pga (default), opp, euro,
        kft, alt."""
        data = _dg_get("field-updates", {"tour": tour})
        if isinstance(data, dict) and data.get("error"):
            return data
        field = []
        for pl in data.get("field", []):
            field.append({
                "player_name": pl.get("player_name"),
                "dg_id": pl.get("dg_id"),
                "country": pl.get("country"),
                "dg_rank": pl.get("dg_rank"),
                "teetimes": [
                    {"round": t.get("round_num"),
                     "teetime": t.get("teetime"),
                     "start_hole": t.get("start_hole"),
                     "wave": t.get("wave")}
                    for t in (pl.get("teetimes") or [])
                ],
            })
        return {
            "event_name": data.get("event_name"),
            "event_id": data.get("event_id"),
            "course_name": data.get("course_name"),
            "current_round": data.get("current_round"),
            "field_size": len(field),
            "field": field,
        }

    @mcp.tool()
    def get_dg_event_ids(source: str = "raw", tour: str = "pga") -> dict:
        """List event_ids available in a Data Golf archive.
        source: 'raw' (round-level scoring archive) or 'dfs'
        (hole-scoring / DFS points archive). Use these ids for
        get_dg_rounds / get_dg_hole_scoring."""
        if source == "dfs":
            data = _dg_get("historical-dfs-data/event-list", {})
        else:
            data = _dg_get("historical-raw-data/event-list", {"tour": tour})
        return {"source": source, "events": data}

    @mcp.tool()
    def get_dg_hole_scoring(event_id: int, year: int, tour: str = "pga",
                            site: str = "fanduel") -> dict:
        """Per-player event-level hole scoring (birdies/eagles/bogeys etc.)
        from the DFS archive — the birdie/bogey PROFILE input for GOLF
        v1.x. One event per call; loop recent events locally to build
        profiles. site: fanduel (default) or draftkings."""
        data = _dg_get("historical-dfs-data/points",
                       {"tour": tour, "site": site,
                        "event_id": event_id, "year": year})
        if isinstance(data, dict) and data.get("error"):
            return data
        keep = ["name", "dg_id", "fin", "bird", "bogey", "eagle", "par",
                "hole", "score", "salary"]
        rows = data if isinstance(data, list) else data.get("dfs_points", data)
        try:
            trimmed = [_dg_trim(r, keep) for r in rows if isinstance(r, dict)]
        except TypeError:
            return {"raw": data}  # unexpected shape: return as-is once, inspect
        return {"event_id": event_id, "year": year, "site": site,
                "players": trimmed}

    @mcp.tool()
    def get_dg_rounds(event_id: str, year: int, tour: str = "pga",
                      dg_ids: str = "") -> dict:
        """Round-level scoring/stats/SG + tee times from the raw archive
        (PGA back to 2004). Course-history gate source (8+ rounds,
        computed exactly). dg_ids: optional comma-separated dg_id filter
        to shrink the payload — STRONGLY recommended; a full event
        unfiltered is large. Avoid event_id='all' through MCP (timeout
        risk) — do bulk pulls locally per the backtest pattern."""
        data = _dg_get("historical-raw-data/rounds",
                       {"tour": tour, "event_id": event_id, "year": year})
        if isinstance(data, dict) and data.get("error"):
            return data
        want = None
        if dg_ids.strip():
            want = {int(x) for x in dg_ids.split(",") if x.strip().isdigit()}
        keep = ["name", "dg_id", "round", "score", "sg_", "teetime",
                "course", "fin", "gir", "driving", "prox", "scrambl",
                "putt", "great", "poor"]
        out = []
        rows = data if isinstance(data, list) else data.get("scores", data)
        if isinstance(rows, list):
            for r in rows:
                if not isinstance(r, dict):
                    continue
                if want is not None and r.get("dg_id") not in want:
                    continue
                out.append(_dg_trim(r, keep))
            return {"event_id": event_id, "year": year, "n_rows": len(out),
                    "rounds": out}
        return {"raw": data}  # unexpected shape: inspect once, then re-trim

    @mcp.tool()
    def get_dg_live_hole_stats(tour: str = "pga") -> dict:
        """LIVE hole-by-hole scoring averages and distributions split by
        tee-time WAVE for the ongoing event — direct read on the
        wave-split thesis (AM vs PM birdie environment) during a round.
        Post-mortem + LIVE-READ verification tool; mid-round thesis
        revision stays banned per v1.0."""
        return {"live_hole_stats": _dg_get("preds/live-hole-stats",
                                           {"tour": tour})}

    @mcp.tool()
    def get_dg_skill_ratings(display: str = "value") -> dict:
        """Data Golf skill estimates (SG total + components) for players
        with sufficient measured rounds. Input to aggressive/conservative
        classification. display: value (default) or rank."""
        data = _dg_get("preds/skill-ratings", {"display": display})
        if isinstance(data, dict) and data.get("error"):
            return data
        keep = ["name", "dg_id", "sg_", "driving", "date"]
        players = data.get("players", data) if isinstance(data, dict) else data
        if isinstance(players, list):
            return {"players": [_dg_trim(p, keep) for p in players
                                if isinstance(p, dict)]}
        return {"raw": data}

# ============================================================
# Deploy checklist:
# 1. Railway → project → Variables → add DATAGOLF_API_KEY
# 2. Paste the block above INSIDE setup_mlb_tools(mcp), 4-space
#    indent (server crashes otherwise — known constraint)
# 3. Commit + push → Railway redeploys
# 4. Smoke test from chat: get_dg_field_waves() should return the
#    3M Open field with wave labels
# 5. The two "raw"/inspect fallbacks exist because exact archive
#    field names vary — if a tool returns {"raw": ...}, send me
#    the shape and I'll tighten the trim lists
# ============================================================

    # get_f5_results — batch F5/final results tool for mlb-api-mcp
#
# INSTALL: Paste this function INSIDE setup_mlb_tools(mcp) in mlb_api.py,
# indented 4 spaces (same level as the other @mcp.tool() functions).
# Then commit + push; Railway will auto-redeploy.

# ============================================================
# PATCH: Historical F5 odds backtest tools (3 tools)
# For: luctuhuynh-source/mlb-api-mcp  ->  mlb_api.py
#
# WHERE TO PASTE:
#   Inside setup_mlb_tools(mcp), at the very end of the function,
#   right after your last tool (get_f5_results / get_park_weather).
#   This block is ALREADY INDENTED 4 SPACES for direct paste.
#   Never flush-left. The "@mcp.tool()" lines must line up in the
#   same column as the @mcp.tool() above get_park_weather.
#
# REQUIREMENTS:
#   - PAID Odds API plan (historical endpoints locked on free tier)
#   - ODDS_API_KEY env var on Railway = your NEW 100K-plan key
#     (already confirmed working via get_odds_usage: 100,000 remaining)
#   - `import os` and `import requests` already at top of mlb_api.py
#
# CREDIT COSTS:
#   - get_mlb_historical_events ......... 1 credit per call
#   - get_mlb_f5_odds_historical ........ 10 credits x markets x regions
#   - get_mlb_f5_closing_lines .......... 1 + (10 x games) with defaults
#       e.g. 15-game slate = ~151 credits for closing F5 totals
#   dry_run=True (the default on the batch tool) costs only 1 credit
#   and shows the game count + estimated spend before committing.
# ============================================================

    # ============================================================
    # PATCH: get_f5_lines_for_games - batch historical F5 closing lines
    # For: luctuhuynh-source/mlb-api-mcp -> mlb_api.py
    #
    # WHERE TO PASTE:
    #   Inside setup_mlb_tools(mcp), at the VERY END of the function,
    #   right after your last tool (the 3 historical odds tools).
    #   This block is ALREADY INDENTED 4 SPACES for direct paste.
    #   The @mcp.tool() line must line up in the same column as the
    #   @mcp.tool() lines above it.
    #
    # CREDIT COST: ~1 credit per unique date + ~10 per game.
    #   All 62 backtest games across 3 calls =~ 670 credits.
    # ============================================================
    @mcp.tool()
    def get_f5_lines_for_games(
        games: str,
        minutes_before_start: int = 7,
        markets: str = "totals_1st_5_innings",
        regions: str = "us",
        odds_format: str = "american",
    ) -> dict:
        """Batch-pull historical F5 closing lines for SPECIFIC games only.

        games: semicolon-separated entries of 'YYYY-MM-DD|Away Team|Home Team'
          using full team names, e.g.
          '2026-04-14|Seattle Mariners|San Diego Padres;2026-05-18|Los Angeles Dodgers|San Diego Padres'
          Max ~25 per call. Date = the game's LOCAL calendar date (UTC date of
          first pitch may be the next day for West Coast night games; both are
          checked).

        Returns compact per-game closing lines (one snapshot per game at
        minutes_before_start before first pitch) instead of full-slate pulls.
        Credit cost ~= (#unique dates) + (#games x #markets x #regions x 10)/10.
        """
        import os, requests
        from datetime import datetime, timedelta

        api_key = os.environ.get("ODDS_API_KEY")
        if not api_key:
            return {"error": "ODDS_API_KEY not configured"}

        BASE = "https://api.the-odds-api.com/v4/historical/sports/baseball_mlb"

        entries = []
        for raw in games.split(";"):
            raw = raw.strip()
            if not raw:
                continue
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) != 3:
                return {"error": f"Bad entry '{raw}'. Use 'YYYY-MM-DD|Away|Home'."}
            entries.append({"date": parts[0], "away": parts[1], "home": parts[2]})
        if len(entries) > 25:
            return {"error": "Max 25 games per call."}

        def norm(s):
            return "".join(c for c in s.lower() if c.isalnum())

        # --- 1) One event-list call per unique date (covers UTC spillover) ---
        events_by_date = {}
        quota = {}
        for d in sorted({e["date"] for e in entries}):
            day = datetime.strptime(d, "%Y-%m-%d")
            snap = day.strftime("%Y-%m-%dT18:00:00Z")
            cf = day.strftime("%Y-%m-%dT10:00:00Z")
            ct = (day + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00Z")
            r = requests.get(
                f"{BASE}/events",
                params={
                    "apiKey": api_key, "date": snap,
                    "commenceTimeFrom": cf, "commenceTimeTo": ct,
                }, timeout=30,
            )
            quota = {
                "requests_remaining": r.headers.get("x-requests-remaining"),
                "requests_used": r.headers.get("x-requests-used"),
            }
            if r.status_code != 200:
                return {"error": f"events {d}: HTTP {r.status_code}", "detail": r.text[:300]}
            events_by_date[d] = (r.json() or {}).get("data", [])

        # --- 2) One odds snapshot per matched game ---
        results, unmatched = [], []
        for e in entries:
            match = None
            for ev in events_by_date.get(e["date"], []):
                if norm(ev.get("away_team", "")) == norm(e["away"]) and \
                   norm(ev.get("home_team", "")) == norm(e["home"]):
                    match = ev
                    break
            if match is None:  # loose fallback
                for ev in events_by_date.get(e["date"], []):
                    if norm(e["home"]) in norm(ev.get("home_team", "")) and \
                       norm(e["away"]) in norm(ev.get("away_team", "")):
                        match = ev
                        break
            if match is None:
                unmatched.append(e)
                continue

            commence = datetime.strptime(match["commence_time"], "%Y-%m-%dT%H:%M:%SZ")
            snap_ts = (commence - timedelta(minutes=minutes_before_start)).strftime("%Y-%m-%dT%H:%M:%SZ")
            r = requests.get(
                f"{BASE}/events/{match['id']}/odds",
                params={
                    "apiKey": api_key, "date": snap_ts, "regions": regions,
                    "markets": markets, "oddsFormat": odds_format,
                }, timeout=30,
            )
            quota = {
                "requests_remaining": r.headers.get("x-requests-remaining"),
                "requests_used": r.headers.get("x-requests-used"),
            }
            if r.status_code != 200:
                results.append({**e, "error": f"HTTP {r.status_code}"})
                continue
            data = (r.json() or {}).get("data", {})
            books = []
            for bk in data.get("bookmakers", []):
                for mkt in bk.get("markets", []):
                    if mkt.get("key") != "totals_1st_5_innings":
                        continue
                    line = over = under = None
                    for oc in mkt.get("outcomes", []):
                        if oc.get("name") == "Over":
                            line, over = oc.get("point"), oc.get("price")
                        elif oc.get("name") == "Under":
                            line = oc.get("point") if line is None else line
                            under = oc.get("price")
                    books.append({"b": bk.get("key"), "ln": line, "o": over, "u": under})
            results.append({
                "date": e["date"], "away": e["away"], "home": e["home"],
                "commence": match["commence_time"], "snapshot": snap_ts,
                "books": books,
            })

        return {
            "count": len(results), "results": results,
            "unmatched": unmatched, **quota,
        }
    
    @mcp.tool()
    def get_mlb_historical_events(
        date: str,
        commence_time_from: str = None,
        commence_time_to: str = None,
    ) -> dict:
        """List MLB events as they appeared at a historical snapshot (no odds).

        Use this first to get the 32-char event IDs needed by
        get_mlb_f5_odds_historical.

        Args:
            date: ISO8601 snapshot timestamp, e.g. '2025-07-03T15:00:00Z'.
                  Returns the closest snapshot at or before this time.
            commence_time_from: optional ISO8601 lower bound on game start
                  (use to restrict to a single day's slate).
            commence_time_to: optional ISO8601 upper bound on game start.

        Cost: 1 credit.
        """
        api_key = os.environ.get("ODDS_API_KEY")
        if not api_key:
            return {"error": "ODDS_API_KEY not set"}
        params = {"apiKey": api_key, "date": date}
        if commence_time_from:
            params["commenceTimeFrom"] = commence_time_from
        if commence_time_to:
            params["commenceTimeTo"] = commence_time_to
        try:
            r = requests.get(
                "https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/events",
                params=params,
                timeout=30,
            )
            if r.status_code != 200:
                return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
            payload = r.json()
            events = payload.get("data", [])
            return {
                "snapshot_timestamp": payload.get("timestamp"),
                "previous_snapshot": payload.get("previous_timestamp"),
                "next_snapshot": payload.get("next_timestamp"),
                "event_count": len(events),
                "events": [
                    {
                        "event_id": e.get("id"),
                        "commence_time": e.get("commence_time"),
                        "home_team": e.get("home_team"),
                        "away_team": e.get("away_team"),
                    }
                    for e in events
                ],
                "requests_remaining": r.headers.get("x-requests-remaining"),
                "requests_used": r.headers.get("x-requests-used"),
            }
        except Exception as ex:
            return {"error": str(ex)}

    @mcp.tool()
    def get_mlb_f5_odds_historical(
        event_id: str,
        date: str,
        markets: str = "totals_1st_5_innings",
        regions: str = "us",
        odds_format: str = "american",
    ) -> dict:
        """Get one game's historical F5 odds at a snapshot timestamp.

        For CLOSING lines use a timestamp ~7 minutes before first pitch.
        For OPENING lines use ~24h before first pitch.
        The API returns the closest snapshot at or before `date`.

        Args:
            event_id: 32-char event ID from get_mlb_historical_events.
            date: ISO8601 snapshot timestamp, e.g. '2025-04-14T19:03:00Z'.
            markets: comma-separated. F5 keys: totals_1st_5_innings,
                     h2h_1st_5_innings, spreads_1st_5_innings.
            regions: bookmaker regions (default 'us').
            odds_format: 'american' or 'decimal'.

        Cost: 10 credits x number_of_markets x number_of_regions.
        """
        api_key = os.environ.get("ODDS_API_KEY")
        if not api_key:
            return {"error": "ODDS_API_KEY not set"}
        params = {
            "apiKey": api_key,
            "date": date,
            "markets": markets,
            "regions": regions,
            "oddsFormat": odds_format,
        }
        try:
            r = requests.get(
                f"https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/events/{event_id}/odds",
                params=params,
                timeout=30,
            )
            if r.status_code != 200:
                return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
            payload = r.json()
            data = payload.get("data", {})
            books = []
            for bk in data.get("bookmakers", []):
                entry = {"book": bk.get("key"), "markets": {}}
                for m in bk.get("markets", []):
                    entry["markets"][m.get("key")] = [
                        {
                            "name": o.get("name"),
                            "price": o.get("price"),
                            "point": o.get("point"),
                        }
                        for o in m.get("outcomes", [])
                    ]
                books.append(entry)
            return {
                "snapshot_timestamp": payload.get("timestamp"),
                "previous_snapshot": payload.get("previous_timestamp"),
                "next_snapshot": payload.get("next_timestamp"),
                "event_id": data.get("id"),
                "commence_time": data.get("commence_time"),
                "home_team": data.get("home_team"),
                "away_team": data.get("away_team"),
                "bookmakers": books,
                "requests_remaining": r.headers.get("x-requests-remaining"),
                "requests_used": r.headers.get("x-requests-used"),
            }
        except Exception as ex:
            return {"error": str(ex)}

    @mcp.tool()
    def get_mlb_f5_closing_lines(
        date: str,
        dry_run: bool = True,
        markets: str = "totals_1st_5_innings",
        regions: str = "us",
        odds_format: str = "american",
        minutes_before_start: int = 7,
    ) -> dict:
        """Batch-pull historical F5 CLOSING lines for a full day's slate.

        Lists all games on the date (1 credit), then pulls each game's F5
        odds at a snapshot ~minutes_before_start before its first pitch.

        SAFETY: dry_run defaults to True — it lists the games and the
        estimated credit cost WITHOUT pulling any odds. Re-run with
        dry_run=False to actually spend the credits.

        Args:
            date: slate date, 'YYYY-MM-DD' (games starting that UTC day).
            dry_run: True = preview count/cost only (1 credit total).
            markets: comma-separated F5 market keys.
            regions: bookmaker regions (default 'us').
            odds_format: 'american' or 'decimal'.
            minutes_before_start: snapshot offset for the closer (default 7).

        Cost: 1 credit (dry run) or ~1 + 10 x markets x regions x games.
        """
        api_key = os.environ.get("ODDS_API_KEY")
        if not api_key:
            return {"error": "ODDS_API_KEY not set"}
        from datetime import datetime, timedelta

        slate = datetime.strptime(date, "%Y-%m-%d")
        day_start = (slate + timedelta(hours=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
        day_end = (slate + timedelta(hours=33)).strftime("%Y-%m-%dT%H:%M:%SZ")
        snapshot_ts = (slate + timedelta(hours=16)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Snapshot for the event list: end of day guarantees all games listed
        try:
            r = requests.get(
                "https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/events",
                params={
                    "apiKey": api_key,
                    "date": snapshot_ts,
                    "commenceTimeFrom": day_start,
                    "commenceTimeTo": day_end,
                },
                timeout=30,
            )
            if r.status_code != 200:
                return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
            events = r.json().get("data", [])
        except Exception as ex:
            return {"error": f"event list failed: {ex}"}

        n_markets = len([m for m in markets.split(",") if m.strip()])
        n_regions = len([g for g in regions.split(",") if g.strip()])
        est_cost = 1 + 10 * n_markets * n_regions * len(events)

        if dry_run:
            return {
                "dry_run": True,
                "date": date,
                "game_count": len(events),
                "estimated_credit_cost": est_cost,
                "games": [
                    {
                        "event_id": e.get("id"),
                        "commence_time": e.get("commence_time"),
                        "matchup": f"{e.get('away_team')} @ {e.get('home_team')}",
                    }
                    for e in events
                ],
                "note": "Re-run with dry_run=False to pull closing lines.",
                "requests_remaining": r.headers.get("x-requests-remaining"),
            }

        results = []
        for e in events:
            try:
                ct = datetime.strptime(
                    e["commence_time"], "%Y-%m-%dT%H:%M:%SZ"
                )
                snap = (
                    ct - timedelta(minutes=minutes_before_start)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
                r2 = requests.get(
                    f"https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/events/{e['id']}/odds",
                    params={
                        "apiKey": api_key,
                        "date": snap,
                        "markets": markets,
                        "regions": regions,
                        "oddsFormat": odds_format,
                    },
                    timeout=30,
                )
                if r2.status_code != 200:
                    results.append(
                        {
                            "event_id": e.get("id"),
                            "matchup": f"{e.get('away_team')} @ {e.get('home_team')}",
                            "error": f"HTTP {r2.status_code}",
                        }
                    )
                    continue
                p2 = r2.json()
                d2 = p2.get("data", {})
                books = []
                for bk in d2.get("bookmakers", []):
                    entry = {"book": bk.get("key"), "markets": {}}
                    for m in bk.get("markets", []):
                        entry["markets"][m.get("key")] = [
                            {
                                "name": o.get("name"),
                                "price": o.get("price"),
                                "point": o.get("point"),
                            }
                            for o in m.get("outcomes", [])
                        ]
                    books.append(entry)
                results.append(
                    {
                        "event_id": e.get("id"),
                        "matchup": f"{e.get('away_team')} @ {e.get('home_team')}",
                        "commence_time": e.get("commence_time"),
                        "snapshot_used": p2.get("timestamp"),
                        "bookmakers": books,
                    }
                )
                last_remaining = r2.headers.get("x-requests-remaining")
            except Exception as ex:
                results.append(
                    {
                        "event_id": e.get("id"),
                        "matchup": f"{e.get('away_team')} @ {e.get('home_team')}",
                        "error": str(ex),
                    }
                )
        return {
            "dry_run": False,
            "date": date,
            "game_count": len(events),
            "estimated_credit_cost": est_cost,
            "closing_lines": results,
            "requests_remaining": last_remaining if results else None,
        }    
    
    @mcp.tool()
    def get_f5_results(game_ids: str) -> dict:
        """Get compact first-5-inning (F5) and final results for multiple games in one call.

        Args:
            game_ids: Comma-separated MLB gamePks, e.g. "823387,824439,822736".
                      Recommended max ~25 per call.

        Returns per game: date, teams, F5 score by side, F5 winner (or TIE),
        final score, total hits per side (for outburst verification), and
        innings played (for extra-innings / long-game checks).
        Designed for backtest grading: ~150 bytes per game instead of a
        full 15KB linescore payload.
        """
        import requests
        results = []
        ids = [g.strip() for g in str(game_ids).split(",") if g.strip()]
        for gid in ids[:25]:
            try:
                ls = requests.get(
                    f"https://statsapi.mlb.com/api/v1/game/{gid}/linescore",
                    timeout=10,
                ).json()
                sched = requests.get(
                    f"https://statsapi.mlb.com/api/v1/schedule?gamePk={gid}&sportId=1",
                    timeout=10,
                ).json()
                g = sched["dates"][0]["games"][0]
                away = g["teams"]["away"]["team"]["name"]
                home = g["teams"]["home"]["team"]["name"]
                innings = ls.get("innings", [])
                f5_away = sum(i["away"].get("runs") or 0 for i in innings[:5])
                f5_home = sum(i["home"].get("runs") or 0 for i in innings[:5])
                results.append({
                    "game_id": int(gid),
                    "date": g.get("officialDate"),
                    "away": away,
                    "home": home,
                    "f5_away_runs": f5_away,
                    "f5_home_runs": f5_home,
                    "f5_winner": (
                        away if f5_away > f5_home
                        else home if f5_home > f5_away
                        else "TIE"
                    ),
                    "final_away_runs": ls["teams"]["away"].get("runs"),
                    "final_home_runs": ls["teams"]["home"].get("runs"),
                    "away_hits": ls["teams"]["away"].get("hits"),
                    "home_hits": ls["teams"]["home"].get("hits"),
                    "innings_played": ls.get("currentInning"),
                })
            except Exception as e:
                results.append({"game_id": gid, "error": str(e)})
        return {"count": len(results), "results": results}

    @mcp.tool()
    def get_mlb_f5_odds(markets: str = "totals_1st_5_innings",
                        regions: str = "us",
                        odds_format: str = "american") -> dict:
        """Get F5 (first 5 innings) odds for today's MLB games from The Odds API.
        Markets: totals_1st_5_innings, h2h_1st_5_innings, spreads_1st_5_innings
        (comma-separated). NOTE: each event costs [markets x regions] credits."""
        import os, requests
        key = os.environ.get("ODDS_API_KEY")
        if not key:
            return {"error": "ODDS_API_KEY not set"}
        base = "https://api.the-odds-api.com/v4/sports/baseball_mlb"
        # Step A: list today's events (free call)
        ev = requests.get(f"{base}/events", params={"apiKey": key}, timeout=15)
        if ev.status_code != 200:
            return {"error": f"events fetch failed: {ev.status_code}", "body": ev.text[:300]}
        results, credits_used = [], 0
        for e in ev.json():
            r = requests.get(
                f"{base}/events/{e['id']}/odds",
                params={"apiKey": key, "regions": regions,
                        "markets": markets, "oddsFormat": odds_format},
                timeout=15)
            if r.status_code != 200:
                continue
            credits_used += len(markets.split(",")) * len(regions.split(","))
            d = r.json()
            books = []
            for bk in d.get("bookmakers", []):
                for m in bk.get("markets", []):
                    books.append({
                        "book": bk["key"], "market": m["key"],
                        "outcomes": [
                            {"name": o["name"], "price": o["price"],
                             "point": o.get("point")}
                            for o in m.get("outcomes", [])]})
            if books:
                results.append({"away": d["away_team"], "home": d["home_team"],
                                "commence": d["commence_time"], "books": books})
        return {"count": len(results), "approx_credits_used": credits_used,
                "games": results}

    @mcp.tool()
    def get_mlb_standings(
        season: Optional[int] = None,
        standingsTypes: Optional[str] = None,
        date: Optional[str] = None,
        hydrate: Optional[str] = None,
        fields: Optional[str] = None,
        league: str = "both",
    ) -> dict:
        """
        Get current MLB standings for a given season (year).

        Args:
            season (Optional[int]): The year for which to retrieve standings. Defaults to current year.
            standingsTypes (Optional[str]): The type of standings to retrieve (e.g., 'regularSeason', 'wildCard', etc.).
            date (Optional[str]): Date in 'YYYY-MM-DD' format.
            hydrate (Optional[str]): Additional data to hydrate in the response.
            fields (Optional[str]): Comma-separated list of fields to include in the response.
            league (str): Filter by league. Accepts 'AL', 'NL', or 'both' (default: 'both').

        Returns:
            dict: Standings for the specified league(s) and season.
        """
        try:
            if season is None:
                season = datetime.now().year
            params = {}
            if standingsTypes is not None:
                params["standingsTypes"] = standingsTypes
            if date is not None:
                params["date"] = date
            if hydrate is not None:
                params["hydrate"] = hydrate
            if fields is not None:
                params["fields"] = fields
            league = league.upper()
            result = {}
            if league == "AL" or league == "BOTH":
                result["AL"] = mlb.get_standings(103, season=str(season), **params)
            if league == "NL" or league == "BOTH":
                result["NL"] = mlb.get_standings(104, season=str(season), **params)
            if not result:
                return {"error": "Invalid league parameter. Use 'AL', 'NL', or 'both'."}
            return {"standings": result}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_schedule(
        start_date: str,
        end_date: str,
        sport_id: int = 1,
        team: Optional[str] = None,
    ) -> dict:
        """
        Get MLB schedule for a specific date range, sport ID, or team (ID or name).

        Args:
            sport_id (int): Sport ID (default: 1 for MLB).
            start_date (str): Start date in 'YYYY-MM-DD' format. Required.
            end_date (str): End date in 'YYYY-MM-DD' format. Required.
            team (Optional[str]): Team ID or team name as a string. Can be numeric string, full name, abbreviation, or
              location. If not provided, defaults to all teams.

        Returns:
            dict: Schedule data for the specified parameters.
        """
        try:
            # Validate date range
            date_error = validate_date_range(start_date, end_date)
            if date_error:
                return date_error
            team_id = get_team_id_from_name(team) if team is not None else None
            schedule = mlb.get_schedule(
                start_date=start_date,
                end_date=end_date,
                sport_id=sport_id,
                team_id=team_id,
            )
            if not schedule:
                return {
                    "error": (
                        f"No games found for the given date range ({start_date} to {end_date}). The date range may "
                        "have resulted in nothing being returned."
                    )
                }
            return {"schedule": schedule}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_team_info(
        team: str,
        season: Optional[int] = None,
        sport_id: Optional[int] = None,
        hydrate: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> dict:
        """
        Get information about a specific team by ID or name.

        Args:
            team (str): Team ID or team name as a string. Can be numeric string, full name, abbreviation, or location.
            season (Optional[int]): Season year.
            sport_id (Optional[int]): Sport ID.
            hydrate (Optional[str]): Additional data to hydrate.
            fields (Optional[str]): Comma-separated list of fields to include.

        Returns:
            dict: Team information.
        """
        try:
            params = {}
            if season is not None:
                params["season"] = season
            if sport_id is not None:
                params["sportId"] = sport_id
            if hydrate is not None:
                params["hydrate"] = hydrate
            if fields is not None:
                params["fields"] = fields
            team_id = get_team_id_from_name(team)
            if team_id is None:
                return {"error": f"Could not find team ID for '{team}'"}
            team_info = mlb.get_team(team_id, **params)
            return {"team_info": team_info}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_player_info(player_id: int) -> dict:
        """
        Get information about a specific player by ID.

        Args:
            player_id (int): The player ID.

        Returns:
            dict: Player information.
        """
        try:
            player_info = mlb.get_person(player_id)
            return {"player_info": player_info}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_boxscore(game_id: int, timecode: Optional[str] = None, fields: Optional[str] = None) -> dict:
        """
        Get boxscore for a specific game by game_id.

        Args:
            game_id (int): The game ID.
            timecode (Optional[str]): Specific timecode for the boxscore snapshot.
            fields (Optional[str]): Comma-separated list of fields to include.

        Returns:
            dict: Boxscore information.
        """
        try:
            params = {}
            if timecode is not None:
                params["timecode"] = timecode
            if fields is not None:
                params["fields"] = fields
            boxscore = mlb.get_game_box_score(game_id, **params)
            return boxscore
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_multiple_mlb_player_stats(
        player_ids: str,
        group: Optional[str] = None,
        type: Optional[str] = None,
        season: Optional[int] = None,
        eventType: Optional[str] = None,
    ) -> dict:
        """
        Get player stats by comma separated player_ids, group, type, season, and optional eventType.

        Args:
            player_ids (str): Comma-separated list of player IDs.
            group (Optional[str]): Stat group (e.g., hitting, pitching).
            type (Optional[str]): Stat type (e.g., season, career).
            season (Optional[int]): Season year.
            eventType (Optional[str]): Event type filter.

        Returns:
            dict: Player statistics.
        """
        try:
            player_ids_list = [pid.strip() for pid in player_ids.split(",")]

            # Use the helper function from the original code
            stats = ["season", "seasonAdvanced"] if type == "season" else ["career"]
            groups = [group] if group else ["hitting"]

            splits = get_multiple_player_stats(mlb, player_ids_list, stats, groups, season)
            return {"player_stats": splits}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_sabermetrics(
        player_ids: str, season: int, stat_name: Optional[str] = None, group: str = "hitting"
    ) -> dict:
        """
        Get sabermetric statistics (including WAR) for multiple players for a specific season.

        Args:
            player_ids (str): Comma-separated list of player IDs.
            season (int): Season year.
            stat_name (Optional[str]): Specific sabermetric stat to extract (e.g., 'war', 'woba', 'wRc').
            group (str): Stat group ('hitting' or 'pitching').

        Returns:
            dict: Sabermetric statistics.
        """
        try:
            player_ids_list = [pid.strip() for pid in player_ids.split(",")]
            result = get_sabermetrics_for_players(mlb, player_ids_list, season, stat_name, group)
            return result
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_batter_vs_pitcher(batter_id: int, pitcher_id: int) -> dict:
        """
        Get a batter's career hitting statistics against a specific pitcher (batter-vs-pitcher).

        Queries the MLB Stats API vsPlayerTotal hitting split for the given batter against
        the given opposing pitcher, covering all matchups in MLB Stats API history.

        Args:
            batter_id (int): The MLBAM ID of the batter.
            pitcher_id (int): The MLBAM ID of the opposing pitcher.

        Returns:
            dict: Batter-vs-pitcher hitting statistics as returned by the MLB Stats API.
        """
        try:
            endpoint = (
                f"people/{batter_id}/stats?stats=vsPlayerTotal&group=hitting"
                f"&opposingPlayerId={pitcher_id}"
            )
            response = mlb._mlb_adapter_v1.get(endpoint=endpoint)

            if 400 <= response.status_code <= 499:
                return {"error": f"API error: {response.status_code}"}

            return response.data
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_odds(
        markets: str = "h2h,totals",
        regions: str = "us",
        odds_format: str = "american",
    ) -> dict:
        """
        Get current betting odds for MLB games from The Odds API.

        Requires the ODDS_API_KEY environment variable to be set to a valid
        the-odds-api.com API key.

        Args:
            markets (str): Comma-separated betting markets (default: "h2h,totals").
            regions (str): Comma-separated bookmaker regions (default: "us").
            odds_format (str): Odds format, "american" or "decimal" (default: "american").

        Returns:
            dict: Odds data under "odds" plus the remaining/used quota headers, or an
                error dict on failure.
        """
        api_key = get_odds_api_key()
        try:
            response = requests.get(
                f"{ODDS_API_BASE_URL}/sports/baseball_mlb/odds",
                params={
                    "apiKey": api_key,
                    "markets": markets,
                    "regions": regions,
                    "oddsFormat": odds_format,
                },
                timeout=30,
            )

            if 400 <= response.status_code <= 499:
                return {"error": f"API error: {response.status_code} {response.text}"}
            response.raise_for_status()

            return {
                "requests_remaining": response.headers.get("x-requests-remaining"),
                "requests_used": response.headers.get("x-requests-used"),
                "odds": response.json(),
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_odds_usage() -> dict:
        """
        Get the remaining and used request quota for The Odds API.

        Makes a lightweight call to The Odds API (the /sports listing, which does not
        consume quota) and returns the quota headers, for monitoring usage. Requires
        the ODDS_API_KEY environment variable to be set.

        Returns:
            dict: {"requests_remaining": ..., "requests_used": ...}, or an error dict
                on failure.
        """
        api_key = get_odds_api_key()
        try:
            response = requests.get(
                f"{ODDS_API_BASE_URL}/sports",
                params={"apiKey": api_key},
                timeout=30,
            )

            if 400 <= response.status_code <= 499:
                return {"error": f"API error: {response.status_code} {response.text}"}
            response.raise_for_status()

            return {
                "requests_remaining": response.headers.get("x-requests-remaining"),
                "requests_used": response.headers.get("x-requests-used"),
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_game_highlights(game_id: int) -> dict:
        """
        Get game highlights for a specific game by game_id.

        Args:
            game_id (int): The game ID.

        Returns:
            dict: Game highlights.
        """
        try:
            highlights = mlb.get_game(game_id).content.highlights
            return highlights
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_game_pace(season: int, sport_id: int = 1) -> dict:
        """
        Get game pace statistics for a given season.

        Args:
            season (int): Season year.
            sport_id (int): Sport ID (default: 1 for MLB).

        Returns:
            dict: Game pace statistics.
        """
        try:
            gamepace = mlb.get_gamepace(str(season), sport_id=sport_id)
            return gamepace
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_game_scoring_plays(
        game_id: int, eventType: Optional[str] = None, timecode: Optional[str] = None, fields: Optional[str] = None
    ) -> dict:
        """
        Get plays for a specific game by game_id, with optional filtering by eventType.

        Args:
            game_id (int): The game ID.
            eventType (Optional[str]): Filter plays by this event type (e.g., 'scoring_play', 'home_run').
            timecode (Optional[str]): Specific timecode for the play-by-play snapshot.
            fields (Optional[str]): Comma-separated list of fields to include.

        Returns:
            dict: Game plays, optionally filtered by eventType.
        """
        try:
            params = {}
            if timecode is not None:
                params["timecode"] = timecode
            if fields is not None:
                params["fields"] = fields
            plays = mlb.get_game_play_by_play(game_id, **params)
            if eventType:
                filtered_plays = [
                    play for play in plays.allplays if getattr(play.result, "eventType", None) == eventType
                ]
                return {"plays": filtered_plays}
            else:
                return {"plays": plays.allplays}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_linescore(game_id: int) -> dict:
        """
        Get linescore for a specific game by game_id.

        Args:
            game_id (int): The game ID.

        Returns:
            dict: Linescore information.
        """
        try:
            linescore = mlb.get_game_line_score(game_id)
            return linescore
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_roster(
        team: str,
        date: Optional[str] = None,
        rosterType: Optional[str] = None,
        season: Optional[str] = None,
        hydrate: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> dict:
        """
        Get team roster for a specific team (ID or name), with optional filters.

        Args:
            team (str): Team ID or team name as a string. Can be numeric string, full name, abbreviation, or location.
            date (Optional[str]): Date in 'YYYY-MM-DD' format. If not provided, defaults to today.
            rosterType (Optional[str]): Filter by roster type (e.g., 40Man, fullSeason, etc.).
            season (Optional[str]): Filter by single season (year).
            hydrate (Optional[str]): Additional data to hydrate in the response.
            fields (Optional[str]): Comma-separated list of fields to include.

        Returns:
            dict: Team roster information.
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            params = {}
            if rosterType is not None:
                params["rosterType"] = rosterType
            if season is not None:
                params["season"] = season
            params["date"] = date
            if hydrate is not None:
                params["hydrate"] = hydrate
            if fields is not None:
                params["fields"] = fields
            team_id = get_team_id_from_name(team)
            if team_id is None:
                return {"error": f"Could not find team ID for '{team}'"}
            roster = mlb.get_team_roster(team_id, **params)
            _r = roster
            return _r if isinstance(_r, dict) else {"roster": _r}
        except Exception as e:
            return {"error": str(e)}

    # PATCH: get_mlb_search_players (7/24/26)
# Fix for known quirk: player search returns empty.
# Replaces the old endpoint with /api/v1/people/search, plus a
# season-roster substring fallback if that ever comes back empty.
#
# HOW TO APPLY:
# 1. In the repo, find the existing `get_mlb_search_players` tool block
#    inside setup_mlb_tools(mcp) and DELETE it.
# 2. Paste everything below the marker line in its place — it is already
#    indented 4 spaces to sit inside setup_mlb_tools(mcp).
# 3. Commit → Railway auto-deploys → ping Claude to smoke-test.
#
# Backward compatible: still returns "player_ids" (the old key), and adds
# a richer "players" list (id, name, team, position).
# ---- paste everything below this line ----

    @mcp.tool()
    def get_mlb_search_players(fullname: str, search_key: str = "fullname", sport_id: int = 1) -> dict:
        """Search for players by name. Patched 7/24/26: uses the
        /api/v1/people/search endpoint (handles partial names and
        accents), with a season-roster substring-match fallback."""
        import requests
        from datetime import date

        def trim(p):
            return {
                "id": p.get("id"),
                "fullName": p.get("fullName"),
                "currentTeam": (p.get("currentTeam") or {}).get("name"),
                "primaryPosition": (p.get("primaryPosition") or {}).get("abbreviation"),
                "active": p.get("active"),
            }

        players = []
        errors = []

        # Primary: people/search — the endpoint that actually works in 2026
        try:
            r = requests.get(
                "https://statsapi.mlb.com/api/v1/people/search",
                params={"names": fullname, "sportIds": sport_id},
                timeout=10,
            )
            r.raise_for_status()
            players = [trim(p) for p in r.json().get("people", [])]
        except Exception as e:
            errors.append(f"people/search: {e}")

        # Fallback: current-season player dump + case-insensitive substring
        if not players:
            try:
                r = requests.get(
                    f"https://statsapi.mlb.com/api/v1/sports/{sport_id}/players",
                    params={"season": date.today().year},
                    timeout=15,
                )
                r.raise_for_status()
                q = fullname.lower().strip()
                players = [
                    trim(p) for p in r.json().get("people", [])
                    if q in p.get("fullName", "").lower()
                ]
            except Exception as e:
                errors.append(f"season fallback: {e}")

        out = {
            "player_ids": [p["id"] for p in players],  # legacy key
            "players": players,
        }
        if errors and not players:
            out["error"] = "; ".join(errors)
        return out

    @mcp.tool()
    def get_mlb_players(sport_id: int = 1, season: Optional[int] = None) -> dict:
        """
        Get all players for a specific sport.

        Args:
            sport_id (int): Sport ID (default: 1 for MLB).
            season (Optional[int]): Filter players by a specific season (year).

        Returns:
            dict: All players for the specified sport.
        """
        try:
            params = {}
            if season is not None:
                params["season"] = season
            players = mlb.get_people(sport_id=sport_id, **params)
            return {"players": players}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_draft(year_id: int) -> dict:
        """
        Get draft information for a specific year.

        Args:
            year_id (int): Draft year.

        Returns:
            dict: Draft information.
        """
        try:
            draft = mlb.get_draft(year_id)
            return {"draft": draft}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_awards(award_id: int) -> dict:
        """
        Get award recipients for a specific award.

        Args:
            award_id (int): Award ID.

        Returns:
            dict: Award recipients.
        """
        try:
            awards = mlb.get_awards(award_id)
            return {"awards": awards}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_search_teams(team_name: str, search_key: str = "name") -> dict:
        """
        Search for teams by name or ID.

        Args:
            team_name (str): Team name or ID to search for.
            search_key (str): Search key ("name", "id", or "all").

        Returns:
            dict: Team search results.
        """
        try:
            import csv

            # Load teams from CSV
            teams = []
            with open("current_mlb_teams.csv", "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    teams.append(row)

            # Search for teams
            results = []
            for team in teams:
                if search_key == "id":
                    if team_name == team["team_id"]:
                        results.append(team)
                elif search_key == "name":
                    if team_name.lower() in team["team_name"].lower():
                        results.append(team)
                else:  # search_key == "all"
                    if team_name == team["team_id"] or team_name.lower() in team["team_name"].lower():
                        results.append(team)

            return {"teams": results}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_teams(sport_id: int = 1, season: Optional[int] = None) -> dict:
        """
        Get all teams for a specific sport.

        Args:
            sport_id (int): Sport ID (default: 1 for MLB).
            season (Optional[int]): Filter teams by a specific season (year).

        Returns:
            dict: All teams for the specified sport.
        """
        try:
            params = {}
            if season is not None:
                params["season"] = season
            teams = mlb.get_teams(sport_id=sport_id, **params)
            return {"teams": teams}
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_game_lineup(game_id: int) -> dict:
        """Lineups via boxscore battingOrder. Starters = x00 slots;
        subs x01+. Empty pregame until lineups post."""
        import requests as _rq
        url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/boxscore"
        r = _rq.get(url, timeout=15)
        r.raise_for_status()
        box = r.json()
        out = {"game_id": game_id, "source": "boxscore", "teams": {}}
        for side in ("away", "home"):
            t = box.get("teams", {}).get(side, {}) or {}
            team = t.get("team", {}) or {}
            players = []
            for p in (t.get("players", {}) or {}).values():
                bo = p.get("battingOrder")
                if not bo:
                    continue
                bo = int(bo)
                players.append({
                    "batting_order": bo,
                    "slot": bo // 100,
                    "is_starter": bo % 100 == 0,
                    "id": p.get("person", {}).get("id"),
                    "name": p.get("person", {}).get("fullName"),
                    "position": p.get("position", {}).get("abbreviation"),
                })
            players.sort(key=lambda x: x["batting_order"])
            out["teams"][side] = {
                "team_name": team.get("name"),
                "team_id": team.get("id"),
                "lineup_posted": any(pl["is_starter"] for pl in players),
                "players": players,
            }
        return out

    @mcp.tool()
    def get_statcast_pitcher(
        player_id: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        Retrieve MLB Statcast data for a single pitcher over a date range.

        Parameters
        ----------
        player_id : int
            MLBAM ID of the pitcher.
        start_date : str
            The start date in 'YYYY-MM-DD' format. Required.
        end_date : str
            The end date in 'YYYY-MM-DD' format. Required.

        Returns
        -------
        dict
            Dictionary with Statcast data for the pitcher. If the result is too large, returns an error message.

        Notes
        -----
        Data is sourced from MLB Statcast via pybaseball. See the official documentation for more details:
        https://github.com/jldbc/pybaseball/tree/master/docs
        """
        try:
            # Validate date range
            date_error = validate_date_range(start_date, end_date)
            if date_error:
                return date_error
            data = statcast_pitcher(start_date, end_date, player_id)
            # Convert all columns to string to ensure JSON serializability
            data = data.astype(str)
            result = {"statcast_data": data.to_dict(orient="records")}
            if not result["statcast_data"]:
                return {
                    "error": (
                        f"No Statcast data found for the given date range ({start_date} to {end_date}). The date "
                        "range may have resulted in nothing being returned."
                    )
                }
            size_error = check_result_size(result, "player")
            if size_error:
                return size_error
            return result
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_statcast_batter(
        player_id: int,
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        Retrieve MLB Statcast data for a single batter over a date range.

        Parameters
        ----------
        player_id : int
            MLBAM ID of the batter.
        start_date : str
            The start date in 'YYYY-MM-DD' format. Required.
        end_date : str
            The end date in 'YYYY-MM-DD' format. Required.

        Returns
        -------
        dict
            Dictionary with Statcast data for the batter. If the result is too large, returns an error message.

        Notes
        -----
        Data is sourced from MLB Statcast via pybaseball. See the official documentation for more details:
        https://github.com/jldbc/pybaseball/tree/master/docs
        """
        try:
            # Validate date range
            date_error = validate_date_range(start_date, end_date)
            if date_error:
                return date_error
            data = statcast_batter(start_date, end_date, player_id)
            # Convert all columns to string to ensure JSON serializability
            data = data.astype(str)
            result = {"statcast_data": data.to_dict(orient="records")}
            if not result["statcast_data"]:
                return {
                    "error": (
                        f"No Statcast data found for the given date range ({start_date} to {end_date}). The date "
                        "range may have resulted in nothing being returned."
                    )
                }
            size_error = check_result_size(result, "player")
            if size_error:
                return size_error
            return result
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_statcast_team(
        team: str,
        start_date: str,
        end_date: str,
        fields: List[str],
    ) -> dict:
        """
        Retrieve MLB Statcast data for all players on a team over a date range.

        Parameters
        ----------
        team : str
            Team ID or team name (see MLB team list for valid values).
        start_date : str
            The start date in 'YYYY-MM-DD' format. Required.
        end_date : str
            The end date in 'YYYY-MM-DD' format. Required.
        fields: List[str]
            The field to return. If not provided, defaults to all fields. Available fields:
                 pitch_type, game_date, release_speed, release_pos_x, release_pos_z, player_name, batter, pitcher,
                 events, description, spin_dir, spin_rate_deprecated, break_angle_deprecated, break_length_deprecated,
                 zone, des, game_type, stand, p_throws, home_team, away_team, type, hit_location, bb_type, balls,
                 strikes, game_year, pfx_x, pfx_z, plate_x, plate_z, on_3b, on_2b, on_1b, outs_when_up, inning,
                 inning_topbot, hc_x, hc_y, tfs_deprecated, tfs_zulu_deprecated, umpire, sv_id, vx0, vy0, vz0, ax, ay,
                 az, sz_top, sz_bot, hit_distance_sc, launch_speed, launch_angle, effective_speed, release_spin_rate,
                 release_extension, game_pk, fielder_2, fielder_3, fielder_4, fielder_5, fielder_6, fielder_7,
                 fielder_8, fielder_9, release_pos_y, estimated_ba_using_speedangle,
                 estimated_woba_using_speedangle, woba_value, woba_denom, babip_value, iso_value, launch_speed_angle,
                 at_bat_number, pitch_number, pitch_name, home_score, away_score, bat_score, fld_score,
                 post_away_score, post_home_score, post_bat_score, post_fld_score, if_fielding_alignment,
                 of_fielding_alignment, spin_axis, delta_home_win_exp, delta_run_exp, bat_speed, swing_length,
                 estimated_slg_using_speedangle, delta_pitcher_run_exp, hyper_speed, home_score_diff, bat_score_diff,
                 home_win_exp, bat_win_exp, age_pit_legacy, age_bat_legacy, age_pit, age_bat, n_thruorder_pitcher,
                 n_priorpa_thisgame_player_at_bat, pitcher_days_since_prev_game, batter_days_since_prev_game,
                 pitcher_days_until_next_game, batter_days_until_next_game, api_break_z_with_gravity,
                 api_break_x_arm, api_break_x_batter_in, arm_angle, attack_angle, attack_direction, swing_path_tilt,
                 intercept_ball_minus_batter_pos_x_inches, intercept_ball_minus_batter_pos_y_inches
        Returns
        -------
        dict
            Dictionary with Statcast data for all players on the team. If the result is too large, returns an error
            message.
        Notes
        -----
        This uses the pybaseball `statcast` function, which returns all Statcast events for the specified team and date
        range. See the official documentation for more details:
        https://github.com/jldbc/pybaseball/tree/master/docs
        """
        try:
            # Validate date range
            date_error = validate_date_range(start_date, end_date)
            if date_error:
                return date_error
            abbreviation = get_team_abbreviation_from_name(team)
            if not abbreviation:
                return {"error": f"Could not find 3-letter abbreviation for team '{team}'"}
            data = statcast(start_date, end_date, team=abbreviation)
            # Convert all columns to string to ensure JSON serializability
            data = data.astype(str)
            records = data.to_dict(orient="records")
            # Always include batter and pitcher, plus all requested fields
            filtered_records = []
            for row in records:
                filtered_row = {}
                for key in ["batter", "pitcher", *list(fields)]:
                    if key in row:
                        filtered_row[key] = row[key]
                filtered_records.append(filtered_row)
            result = {"statcast_data": filtered_records}
            if not result["statcast_data"]:
                return {
                    "error": (
                        f"No Statcast data found for the given date range ({start_date} to {end_date}). The date "
                        "range may have resulted in nothing being returned."
                    )
                }
            size_error = check_result_size(result, "team")
            if size_error:
                return size_error
            return result
        except Exception as e:
            return {"error": str(e)}
# ============================================================
    # get_park_weather — Open-Meteo park weather (free, no API key)
    # ============================================================

    MLB_PARKS = {
        "ARI": ("Chase Field", 33.4453, -112.0667, "retractable"),
        "ATH": ("Sutter Health Park (Sacramento)", 38.5802, -121.5136, "open"),
        "ATL": ("Truist Park", 33.8908, -84.4678, "open"),
        "BAL": ("Camden Yards", 39.2839, -76.6217, "open"),
        "BOS": ("Fenway Park", 42.3467, -71.0972, "open"),
        "CHC": ("Wrigley Field", 41.9484, -87.6553, "open"),
        "CWS": ("Rate Field", 41.8299, -87.6338, "open"),
        "CIN": ("Great American Ball Park", 39.0975, -84.5066, "open"),
        "CLE": ("Progressive Field", 41.4962, -81.6852, "open"),
        "COL": ("Coors Field", 39.7559, -104.9942, "open"),
        "DET": ("Comerica Park", 42.3390, -83.0485, "open"),
        "HOU": ("Daikin Park", 29.7573, -95.3555, "retractable"),
        "KC":  ("Kauffman Stadium", 39.0517, -94.4803, "open"),
        "LAA": ("Angel Stadium", 33.8003, -117.8827, "open"),
        "LAD": ("Dodger Stadium", 34.0739, -118.2400, "open"),
        "MIA": ("loanDepot park", 25.7781, -80.2196, "retractable"),
        "MIL": ("American Family Field", 43.0280, -87.9712, "retractable"),
        "MIN": ("Target Field", 44.9817, -93.2776, "open"),
        "NYM": ("Citi Field", 40.7571, -73.8458, "open"),
        "NYY": ("Yankee Stadium", 40.8296, -73.9262, "open"),
        "PHI": ("Citizens Bank Park", 39.9061, -75.1665, "open"),
        "PIT": ("PNC Park", 40.4469, -80.0057, "open"),
        "SD":  ("Petco Park", 32.7076, -117.1570, "open"),
        "SEA": ("T-Mobile Park", 47.5914, -122.3325, "retractable"),
        "SF":  ("Oracle Park", 37.7786, -122.3893, "open"),
        "STL": ("Busch Stadium", 38.6226, -90.1928, "open"),
        "TB":  ("Tropicana Field", 27.7683, -82.6534, "dome"),
        "TEX": ("Globe Life Field", 32.7473, -97.0847, "retractable"),
        "TOR": ("Rogers Centre", 43.6414, -79.3894, "retractable"),
        "WSH": ("Nationals Park", 38.8730, -77.0074, "open"),
    }

    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

    @mcp.tool()
    def get_park_weather(team: str, hours: int = 12) -> dict:
        """Get current conditions and hourly forecast at an MLB park via Open-Meteo.

        Returns temperature (F), wind speed/gusts (mph), wind direction (degrees),
        humidity, and precipitation probability, starting from the current hour.

        Args:
            team: Team abbreviation (e.g., 'SD', 'SF', 'COL'). See MLB_PARKS keys.
            hours: Number of forecast hours to return (default 12, max 48).
        """
        key = team.upper().strip()
        if key not in MLB_PARKS:
            return {
                "error": f"Unknown team '{team}'.",
                "valid_teams": sorted(MLB_PARKS.keys()),
            }

        park_name, lat, lon, roof = MLB_PARKS[key]
        hours = max(1, min(int(hours), 48))

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                       "wind_gusts_10m,wind_direction_10m,precipitation",
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                      "wind_gusts_10m,wind_direction_10m,precipitation_probability",
            "forecast_days": 2,
            "timezone": "auto",
            "wind_speed_unit": "mph",
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
        }

        try:
            resp = requests.get(OPEN_METEO_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return {"error": f"Open-Meteo request failed: {e}"}

        current = data.get("current", {})
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        # Trim hourly arrays to start at the current hour, length = hours
        now_iso = current.get("time", "")
        start_idx = 0
        if now_iso and now_iso[:13] + ":00" in times:
            start_idx = times.index(now_iso[:13] + ":00")

        def slice_h(field):
            vals = hourly.get(field, [])
            return vals[start_idx:start_idx + hours]

        forecast = []
        for i, t in enumerate(times[start_idx:start_idx + hours]):
            forecast.append({
                "time": t,
                "temp_f": slice_h("temperature_2m")[i],
                "humidity_pct": slice_h("relative_humidity_2m")[i],
                "wind_mph": slice_h("wind_speed_10m")[i],
                "gusts_mph": slice_h("wind_gusts_10m")[i],
                "wind_dir_deg": slice_h("wind_direction_10m")[i],
                "precip_prob_pct": slice_h("precipitation_probability")[i],
            })

        return {
            "team": key,
            "park": park_name,
            "roof": roof,
            "timezone": data.get("timezone"),
            "current": {
                "time": current.get("time"),
                "temp_f": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "wind_mph": current.get("wind_speed_10m"),
                "gusts_mph": current.get("wind_gusts_10m"),
                "wind_dir_deg": current.get("wind_direction_10m"),
                "precip_in": current.get("precipitation"),
            },
            "hourly_forecast": forecast,
            "note": "Wind direction is meteorological (direction wind comes FROM). "
                    "For dome/retractable parks, conditions may not apply if roof is closed.",
        }


    # ============================================================
    # PASTE BOTH FUNCTIONS AT THE VERY END OF mlb_api.py
    #
    # CRITICAL: The "@mcp.tool()" lines below must start in the
    # SAME COLUMN as the "@mcp.tool()" on line 1150 (above
    # get_park_weather). If that line is indented 4 spaces, select
    # this entire pasted block in the GitHub editor and press Tab
    # once to indent everything by 4.
    # ============================================================
    
    from datetime import datetime as _dt
    
    
    @mcp.tool()
    def get_mlb_probable_pitchers(date: str = None) -> dict:
        """Get probable starting pitchers for all MLB games on a date.
    
        Args:
            date: Date in 'YYYY-MM-DD' format. Defaults to today.
        """
        if date is None:
            date = _dt.now().strftime("%Y-%m-%d")
        url = "https://statsapi.mlb.com/api/v1/schedule"
        params = {
            "sportId": 1,
            "date": date,
            "hydrate": "probablePitcher(note)",
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return {"error": f"MLB schedule request failed: {e}"}
    
        games = []
        for d in data.get("dates", []):
            for g in d.get("games", []):
    
                def _side(team_side):
                    t = g.get("teams", {}).get(team_side, {})
                    pp = t.get("probablePitcher") or {}
                    return {
                        "team": (t.get("team") or {}).get("name"),
                        "probable_pitcher": pp.get("fullName", "TBD"),
                        "pitcher_id": pp.get("id"),
                    }
    
                games.append(
                    {
                        "game_id": g.get("gamePk"),
                        "game_time_utc": g.get("gameDate"),
                        "venue": (g.get("venue") or {}).get("name"),
                        "status": (g.get("status") or {}).get("detailedState"),
                        "away": _side("away"),
                        "home": _side("home"),
                    }
                )
        return {"date": date, "games": games}
    
    
    @mcp.tool()
    def get_mlb_pitcher_game_log(
        player_id: int, season: int = None, last_n: int = 5
    ) -> dict:
        """Get a pitcher's recent game-by-game log with a trailing-window summary.
    
        Args:
            player_id: MLBAM player ID (from roster or search results).
            season: Season year. Defaults to the current year.
            last_n: Number of most recent appearances to return (default 5).
        """
        if season is None:
            season = _dt.now().year
        url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
        params = {"stats": "gameLog", "group": "pitching", "season": season}
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return {"error": f"MLB game log request failed: {e}"}
    
        splits = []
        for block in data.get("stats", []):
            splits.extend(block.get("splits", []))
        splits.sort(key=lambda s: s.get("date", ""), reverse=True)
    
        games = []
        for s in splits[: max(1, int(last_n))]:
            st = s.get("stat", {})
            games.append(
                {
                    "date": s.get("date"),
                    "opponent": (s.get("opponent") or {}).get("name"),
                    "is_home": s.get("isHome"),
                    "innings_pitched": st.get("inningsPitched"),
                    "earned_runs": st.get("earnedRuns"),
                    "runs": st.get("runs"),
                    "hits": st.get("hits"),
                    "walks": st.get("baseOnBalls"),
                    "strikeouts": st.get("strikeOuts"),
                    "home_runs": st.get("homeRuns"),
                    "pitches": st.get("numberOfPitches"),
                }
            )
    
        def _ip_to_outs(ip):
            try:
                whole, _, frac = str(ip).partition(".")
                return int(whole) * 3 + (int(frac) if frac else 0)
            except Exception:
                return 0
    
        outs = sum(_ip_to_outs(g["innings_pitched"]) for g in games)
        er = sum(int(g["earned_runs"] or 0) for g in games)
        bb = sum(int(g["walks"] or 0) for g in games)
        h = sum(int(g["hits"] or 0) for g in games)
        k = sum(int(g["strikeouts"] or 0) for g in games)
        ip_float = outs / 3 if outs else 0
    
        summary = {
            "games": len(games),
            "innings_pitched": round(ip_float, 1),
            "era": round(er * 9 / ip_float, 2) if ip_float else None,
            "whip": round((bb + h) / ip_float, 2) if ip_float else None,
            "strikeouts": k,
            "earned_runs": er,
        }
        return {
            "player_id": player_id,
            "season": season,
            "last_n": len(games),
            "trailing_summary": summary,
            "game_log": games,
        }

    """
    Kalshi public-data tools for the MLB Stats MCP server (Railway).
    Adds Robinhood-equivalent prediction-market prices to the Cornerstone workflow.
    
    RH prediction markets clear on Kalshi's exchange, and Kalshi market data is
    PUBLIC — no API key, no RSA signing, read-only. The price RH shows as
    "Buy Xc" is the Kalshi ask for that side.
    
    Two tools:
      1. kalshi_discover_mlb(keyword)  -> find the series/event tickers for MLB
                                          F5 markets (run once; ticker names may
                                          differ from guesses, so discover first)
      2. kalshi_get_markets(...)       -> live yes/no prices for those markets
    
    Register both with the same decorator pattern as the existing tools
    (e.g. @mcp.tool() in the FastMCP app), redeploy on Railway, done.
    
    Notes:
      - Order-book quirk: Kalshi books carry yes-bids and no-bids only.
        Buy-Yes price (RH's over/ML "Buy") = 100 - best no_bid = yes_ask.
        The /markets endpoint already returns yes_ask / no_ask fields, so we
        read those directly and skip the orderbook endpoint.
      - Rate limits are ~10-20 req/s; a Cornerstone run makes 2-3 calls total.
      - Public endpoints need no headers. Never add account keys to this file.
    """
    
    
    
    KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
    TIMEOUT = 15
    
    
    def _get(path: str, params: dict | None = None) -> dict:
        r = requests.get(f"{KALSHI_BASE}{path}", params=params or {}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    
    
    # ---------------------------------------------------------------- tool 1
    @mcp.tool()
    def kalshi_discover_mlb(keyword: str = "MLB") -> dict:
        """Discover Kalshi series whose ticker or title matches `keyword`.
    
        Run this ONCE to learn the real series tickers for MLB game-winner and
        first-5-innings totals markets (e.g. something like KXMLBGAME / an F5
        totals series). Then hard-code the confirmed tickers into the daily
        protocol run and stop calling discovery.
    
        Returns: {"series": [{"ticker", "title", "category"}, ...]}
        """
        out, cursor = [], None
        for _ in range(10):  # page cap
            params = {"limit": 200}
            if cursor:
                params["cursor"] = cursor
            data = _get("/series", params)
            for s in data.get("series", []):
                blob = f"{s.get('ticker','')} {s.get('title','')}".upper()
                if keyword.upper() in blob:
                    out.append({
                        "ticker": s.get("ticker"),
                        "title": s.get("title"),
                        "category": s.get("category"),
                    })
            cursor = data.get("cursor")
            if not cursor:
                break
        return {"keyword": keyword, "match_count": len(out), "series": out}
    
    
    # ---------------------------------------------------------------- tool 2
    @mcp.tool()
    def kalshi_get_markets(series_ticker: str = "",
                           event_ticker: str = "",
                           status: str = "open",
                           limit: int = 100) -> dict:
        """Live Kalshi prices for a series or event (public, no auth).
    
        Pass the series_ticker confirmed by discovery (or a specific
        event_ticker for one game). Returns per-market yes/no bid/ask in cents —
        yes_ask is the number RH displays on the Buy button for Yes.
    
        Returns: {"markets": [{"ticker","title","yes_bid","yes_ask",
                               "no_bid","no_ask","close_time","volume"}, ...]}
        """
        def _cents(v):
            try:
                return round(float(v) * 100)
            except (TypeError, ValueError):
                return None

        params = {"status": status, "limit": limit}
        if series_ticker:
            params["series_ticker"] = series_ticker
        if event_ticker:
            params["event_ticker"] = event_ticker
        data = _get("/markets", params)
        mkts = []
        for m in data.get("markets", []):
            mkts.append({
                "ticker": m.get("ticker"),
                "title": m.get("title"),
                "yes_bid": _cents(m.get("yes_bid_dollars")),
                "yes_ask": _cents(m.get("yes_ask_dollars")),          # = RH "Buy Yes" price
                "no_bid": _cents(m.get("no_bid_dollars")),
                "no_ask": _cents(m.get("no_ask_dollars")),            # = RH "Buy No" price
                "floor_strike": m.get("floor_strike"),
                "close_time": m.get("close_time"),
                "volume": m.get("volume_fp"),
            })
        return {"count": len(mkts), "markets": mkts}


    # ================================================================
    # GENERIC ODDS API TOOLS (added 9/25/26) — any sport, any market
    # incl. half/quarter keys. Built for the CFB / NFL 2nd-half
    # protocols: multi-book 2H consensus with in-tool de-vig.
    #
    #   Sport keys:   americanfootball_ncaaf, americanfootball_nfl,
    #                 baseball_mlb, basketball_nba, basketball_ncaab
    #   2H markets:   spreads_h2, totals_h2, h2h_h2
    #   1H markets:   spreads_h1, totals_h1, h2h_h1
    #   Quarters:     spreads_q1..q4, totals_q1..q4, h2h_q1..q4
    #   Full game:    spreads, totals, h2h
    #
    # Credits: each event pulled costs (#markets x #regions). The events
    # listing is free. Use team_filter / event_id so a Saturday slate
    # of 60 games does not burn 180 credits per pull.
    # ================================================================

    def _oa_devig_two_way(p_a, p_b):
        """Multiplicative de-vig of two American prices -> (fair_a, fair_b)."""
        def _imp(am):
            am = float(am)
            return 100.0 / (am + 100.0) if am > 0 else (-am) / (-am + 100.0)
        try:
            ia, ib = _imp(p_a), _imp(p_b)
        except (TypeError, ValueError):
            return None, None
        s = ia + ib
        if s <= 0:
            return None, None
        return round(ia / s, 4), round(ib / s, 4)

    def _oa_prob_to_american(p):
        if p is None or p <= 0 or p >= 1:
            return None
        return int(round(-100 * p / (1 - p))) if p >= 0.5 else int(round(100 * (1 - p) / p))

    def _oa_consensus(books, market_key, home_team, away_team):
        """Per-market consensus across books.

        spreads_*: modal home point (most books) + mean no-vig home prob AT that point,
                   plus mean home point across all books.
        totals_*:  modal total + mean no-vig OVER prob at that point, plus mean total.
        h2h_*:     mean no-vig home prob.
        """
        rows = []
        for bk in books:
            for m in bk.get("markets", []):
                if m.get("key") != market_key:
                    continue
                outs = m.get("outcomes", [])
                if len(outs) != 2:
                    continue
                rows.append((bk.get("key"), outs))
        if not rows:
            return {"book_count": 0}

        kind = "spreads" if market_key.startswith("spreads") else \
               "totals" if market_key.startswith("totals") else "h2h"

        if kind == "h2h":
            probs = []
            for _, outs in rows:
                home = next((o for o in outs if o.get("name") == home_team), None)
                away = next((o for o in outs if o.get("name") == away_team), None)
                if not home or not away:
                    continue
                fh, _ = _oa_devig_two_way(home.get("price"), away.get("price"))
                if fh is not None:
                    probs.append(fh)
            if not probs:
                return {"book_count": 0}
            mean_p = round(sum(probs) / len(probs), 4)
            return {"book_count": len(probs),
                    "fair_home_prob": mean_p,
                    "fair_home_price": _oa_prob_to_american(mean_p),
                    "fair_away_price": _oa_prob_to_american(1 - mean_p)}

        # spreads / totals: key by point
        by_point = {}
        all_points = []
        for _, outs in rows:
            if kind == "spreads":
                home = next((o for o in outs if o.get("name") == home_team), None)
                other = next((o for o in outs if o.get("name") == away_team), None)
            else:
                home = next((o for o in outs if o.get("name") == "Over"), None)
                other = next((o for o in outs if o.get("name") == "Under"), None)
            if not home or not other or home.get("point") is None:
                continue
            pt = float(home["point"])
            all_points.append(pt)
            fh, _ = _oa_devig_two_way(home.get("price"), other.get("price"))
            if fh is not None:
                by_point.setdefault(pt, []).append(fh)
        if not all_points:
            return {"book_count": 0}
        modal_pt = max(by_point.items(), key=lambda kv: (len(kv[1]), -abs(kv[0])))[0]
        probs = by_point[modal_pt]
        mean_p = round(sum(probs) / len(probs), 4)
        label = "home" if kind == "spreads" else "over"
        out = {
            "book_count": len(all_points),
            "modal_point": modal_pt,
            "books_at_modal": len(probs),
            "mean_point": round(sum(all_points) / len(all_points), 2),
            f"fair_{label}_prob_at_modal": mean_p,
            f"fair_{label}_price_at_modal": _oa_prob_to_american(mean_p),
            "points_seen": sorted(set(all_points)),
        }
        if kind == "spreads":
            out["note"] = "modal_point is the HOME spread; away = -modal_point"
        return out

    def _oa_parse_books(d):
        books = []
        for bk in d.get("bookmakers", []):
            books.append({
                "key": bk.get("key"),
                "title": bk.get("title"),
                "last_update": bk.get("last_update"),
                "markets": [
                    {"key": m.get("key"),
                     "outcomes": [
                         {"name": o.get("name"), "price": o.get("price"),
                          "point": o.get("point"), "description": o.get("description")}
                         for o in m.get("outcomes", [])]}
                    for m in bk.get("markets", [])],
            })
        return books

    def _oa_match_team(ev, team_filter):
        if not team_filter:
            return True
        blob = f"{ev.get('home_team','')} {ev.get('away_team','')}".lower()
        return any(t.strip().lower() in blob for t in team_filter.split(",") if t.strip())

    @mcp.tool()
    def get_event_odds(sport: str = "americanfootball_ncaaf",
                       markets: str = "spreads_h2,totals_h2,h2h_h2",
                       team_filter: str = "",
                       event_id: str = "",
                       status: str = "live",
                       regions: str = "us",
                       odds_format: str = "american",
                       max_events: int = 10,
                       dry_run: bool = False) -> dict:
        """Live odds for ANY sport/market from The Odds API, with per-market
        multi-book consensus (de-vigged) computed in-tool.

        Built for halftime runs: sport='americanfootball_ncaaf' (or _nfl),
        markets='spreads_h2,totals_h2,h2h_h2', status='live' (games already
        kicked off), team_filter='Clemson' (comma-separated substrings; matches
        home OR away). Or pass event_id for one game.

        status: 'live' (commence_time in the past, i.e. in progress),
                'upcoming' (not started), 'all'.
        dry_run=True lists matching events + credit cost, pulls nothing.

        Returns per event: event_id (save it — historical pulls need it),
        teams, commence_time, books (raw per-book outcomes), consensus per
        market (modal point, book_count, fair no-vig prob/price at modal).

        Cost: (#markets x #regions) credits per event pulled; listing is free.
        Bookmaker keys returned include draftkings, fanduel, betmgm,
        williamhill_us (Caesars), betrivers, bovada, etc.
        """
        key = os.environ.get("ODDS_API_KEY")
        if not key:
            return {"error": "ODDS_API_KEY not set"}
        base = f"{ODDS_API_BASE_URL}/sports/{sport}"
        try:
            ev = requests.get(f"{base}/events", params={"apiKey": key}, timeout=15)
        except Exception as ex:
            return {"error": f"events fetch failed: {ex}"}
        if ev.status_code != 200:
            return {"error": f"events fetch failed: HTTP {ev.status_code}",
                    "body": ev.text[:300]}
        events = ev.json()
        now = datetime.utcnow()

        def _started(e):
            try:
                ct = datetime.strptime(e["commence_time"], "%Y-%m-%dT%H:%M:%SZ")
                return ct <= now
            except Exception:
                return False

        selected = []
        for e in events:
            if event_id and e.get("id") != event_id:
                continue
            if not event_id:
                if status == "live" and not _started(e):
                    continue
                if status == "upcoming" and _started(e):
                    continue
                if not _oa_match_team(e, team_filter):
                    continue
            selected.append(e)
        selected = selected[:max_events]
        per_event_cost = len(markets.split(",")) * len(regions.split(","))
        summary = [{"event_id": e["id"], "away": e["away_team"],
                    "home": e["home_team"], "commence_time": e["commence_time"]}
                   for e in selected]
        if dry_run or not selected:
            return {"sport": sport, "status_filter": status,
                    "matched": len(selected), "events": summary,
                    "credits_if_pulled": per_event_cost * len(selected),
                    "total_events_listed": len(events), "pulled": False}

        results, credits_used, remaining = [], 0, None
        for e in selected:
            try:
                r = requests.get(
                    f"{base}/events/{e['id']}/odds",
                    params={"apiKey": key, "regions": regions,
                            "markets": markets, "oddsFormat": odds_format},
                    timeout=20)
            except Exception as ex:
                results.append({"event_id": e["id"], "error": str(ex)})
                continue
            if r.status_code != 200:
                results.append({"event_id": e["id"], "away": e["away_team"],
                                "home": e["home_team"],
                                "error": f"HTTP {r.status_code}: {r.text[:200]}"})
                continue
            credits_used += per_event_cost
            remaining = r.headers.get("x-requests-remaining", remaining)
            d = r.json()
            books = _oa_parse_books(d)
            consensus = {mk: _oa_consensus(books, mk, d.get("home_team"), d.get("away_team"))
                         for mk in markets.split(",")}
            results.append({
                "event_id": d.get("id"), "away": d.get("away_team"),
                "home": d.get("home_team"), "commence_time": d.get("commence_time"),
                "book_count": len(books),
                "consensus": consensus,
                "books": books,
            })
        return {"sport": sport, "markets": markets, "pulled": True,
                "count": len(results), "approx_credits_used": credits_used,
                "requests_remaining": remaining,
                "pulled_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "games": results}

    @mcp.tool()
    def get_historical_events(sport: str,
                              date: str,
                              commence_time_from: str = "",
                              commence_time_to: str = "") -> dict:
        """Events for ANY sport as they stood at a historical snapshot (no odds).
        Same as get_mlb_historical_events but with a sport key
        (americanfootball_ncaaf, americanfootball_nfl, ...). Use it to recover
        an event_id you forgot to save. date = ISO8601, e.g. '2026-09-26T23:00:00Z'.
        Cost: 1 credit."""
        key = os.environ.get("ODDS_API_KEY")
        if not key:
            return {"error": "ODDS_API_KEY not set"}
        params = {"apiKey": key, "date": date}
        if commence_time_from:
            params["commenceTimeFrom"] = commence_time_from
        if commence_time_to:
            params["commenceTimeTo"] = commence_time_to
        try:
            r = requests.get(f"{ODDS_API_BASE_URL}/historical/sports/{sport}/events",
                             params=params, timeout=30)
            if r.status_code != 200:
                return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
            payload = r.json()
            return {"snapshot_timestamp": payload.get("timestamp"),
                    "count": len(payload.get("data", [])),
                    "events": [{"event_id": e.get("id"), "away": e.get("away_team"),
                                "home": e.get("home_team"),
                                "commence_time": e.get("commence_time")}
                               for e in payload.get("data", [])],
                    "requests_remaining": r.headers.get("x-requests-remaining")}
        except Exception as ex:
            return {"error": str(ex)}

    @mcp.tool()
    def get_event_odds_historical(sport: str,
                                  event_id: str,
                                  date: str,
                                  markets: str = "spreads_h2,totals_h2,h2h_h2",
                                  regions: str = "us",
                                  odds_format: str = "american") -> dict:
        """One event's odds at a historical snapshot, ANY sport/market, with
        the same in-tool consensus as get_event_odds. This is the grading tool:
        for a 2H CLOSE use date = 3rd-quarter kickoff time (halftime start +
        ~20 min); for a 2H OPEN use halftime start + ~2 min. The API returns
        the closest snapshot at or before `date` (snapshots ~5-10 min apart
        for period markets, so the close may be a few minutes early).

        Cost: 10 credits x #markets x #regions. Historical period markets are
        available from May 2023 on paid plans."""
        key = os.environ.get("ODDS_API_KEY")
        if not key:
            return {"error": "ODDS_API_KEY not set"}
        params = {"apiKey": key, "date": date, "markets": markets,
                  "regions": regions, "oddsFormat": odds_format}
        try:
            r = requests.get(
                f"{ODDS_API_BASE_URL}/historical/sports/{sport}/events/{event_id}/odds",
                params=params, timeout=30)
            if r.status_code != 200:
                return {"error": f"HTTP {r.status_code}: {r.text[:300]}"}
            payload = r.json()
            d = payload.get("data", {}) or {}
            books = _oa_parse_books(d)
            consensus = {mk: _oa_consensus(books, mk, d.get("home_team"), d.get("away_team"))
                         for mk in markets.split(",")}
            return {"snapshot_timestamp": payload.get("timestamp"),
                    "previous_snapshot": payload.get("previous_timestamp"),
                    "next_snapshot": payload.get("next_timestamp"),
                    "event_id": d.get("id"), "away": d.get("away_team"),
                    "home": d.get("home_team"), "commence_time": d.get("commence_time"),
                    "book_count": len(books), "consensus": consensus, "books": books,
                    "requests_remaining": r.headers.get("x-requests-remaining")}
        except Exception as ex:
            return {"error": str(ex)}

    # ---- ESPN football play-by-play tools (added 10/4/26) ----
    # Flush-left source. apply_nfl_pbp.sh indents this block 4 spaces and
    # appends it inside setup_mlb_tools(mcp). Uses module-level `requests`.

    _ESPN_LEAGUE = {"nfl": "nfl", "cfb": "college-football",
                    "ncaaf": "college-football", "college-football": "college-football"}


    def _espn_get(url, params=None, timeout=20):
        r = requests.get(url, params=params, timeout=timeout,
                         headers={"User-Agent": "Mozilla/5.0 (mlb-api-mcp)"})
        if r.status_code != 200:
            return None, {"error": f"HTTP {r.status_code}: {r.text[:200]}"}
        try:
            return r.json(), None
        except Exception as ex:
            return None, {"error": f"bad json: {ex}"}


    def _espn_status(comp):
        st = (comp or {}).get("status", {}) or {}
        t = st.get("type", {}) or {}
        return {"state": t.get("state"), "detail": t.get("shortDetail") or t.get("detail"),
                "period": st.get("period"), "clock": st.get("displayClock"),
                "completed": t.get("completed")}


    def _espn_halftime(status):
        # ESPN marks halftime as period 2, clock 0:00, state "in" (name STATUS_HALFTIME)
        return bool(status) and status.get("period") == 2 and status.get("clock") in ("0:00", "0.0", "0")


    @mcp.tool()
    def get_football_scoreboard(league: str = "nfl", date: str = "") -> dict:
        """Live scoreboard for NFL or college football from ESPN's public JSON
        (no key needed). Returns each game's ESPN event_id — the id you pass to
        get_football_drives — plus teams, score, period, clock, status and whether
        play-by-play is available. league: "nfl" (default) or "cfb".
        date: optional YYYYMMDD; blank = current slate."""
        lg = _ESPN_LEAGUE.get(league.lower(), "nfl")
        params = {"limit": 200}
        if date:
            params["dates"] = date
        data, err = _espn_get(
            f"https://site.api.espn.com/apis/site/v2/sports/football/{lg}/scoreboard", params)
        if err:
            return err
        out = []
        for ev in data.get("events", []) or []:
            comp = (ev.get("competitions") or [{}])[0]
            status = _espn_status(comp)
            teams = {}
            for c in comp.get("competitors", []) or []:
                ab = (c.get("team") or {}).get("abbreviation")
                teams[c.get("homeAway")] = {"abbr": ab,
                                            "name": (c.get("team") or {}).get("displayName"),
                                            "score": c.get("score"),
                                            "linescores": [ls.get("value") for ls in c.get("linescores", []) or []]}
            out.append({"event_id": ev.get("id"), "name": ev.get("shortName"),
                        "start_utc": ev.get("date"),
                        "home": teams.get("home"), "away": teams.get("away"),
                        "status": status, "halftime": _espn_halftime(status),
                        "pbp_available": comp.get("playByPlayAvailable")})
        return {"league": lg, "count": len(out), "games": out}


    @mcp.tool()
    def get_football_drives(event_id: str, league: str = "nfl", half: int = 1,
                            include_plays: bool = True, max_play_chars: int = 110) -> dict:
        """Drive chart + play-by-play for one NFL/CFB game from ESPN's public JSON.
        Built for the 2H halftime protocol: call at halftime with half=1 to get
        every 1H drive (start field position, result, yards, plays, time) with
        its plays, plus a per-team 1H summary (drives, plays, yards, YPP, points,
        turnovers, 3-and-outs, red-zone trips, short-field drives starting inside
        the opponent 40, scoring drives) and the halftime score/linescore.
        half: 1 = periods 1-2 (default), 2 = periods 3-4, 0 = whole game.
        include_plays=False returns drives + summary only (small payload).
        event_id comes from get_football_scoreboard. Cumulative stats are
        computed from the drives, so they stay 1H-only even after Q3 starts."""
        lg = _ESPN_LEAGUE.get(league.lower(), "nfl")
        data, err = _espn_get(
            f"https://site.api.espn.com/apis/site/v2/sports/football/{lg}/summary",
            {"event": event_id})
        if err:
            return err

        # --- header / score ---
        hdr_comp = ((data.get("header") or {}).get("competitions") or [{}])[0]
        status = _espn_status(hdr_comp)
        teams = {}
        for c in hdr_comp.get("competitors", []) or []:
            ab = (c.get("team") or {}).get("abbreviation")
            teams[ab] = {"home_away": c.get("homeAway"), "score": c.get("score"),
                         "linescores": [ls.get("displayValue") for ls in c.get("linescores", []) or []]}

        # --- drives ---
        drives_obj = data.get("drives") or {}
        raw = list(drives_obj.get("previous", []) or [])
        cur = drives_obj.get("current")
        if cur and cur.get("id") not in {d.get("id") for d in raw}:
            raw.append(cur)

        def _period(d):
            return ((d.get("start") or {}).get("period") or {}).get("number")

        def _in_half(p):
            if half == 0 or p is None:
                return True
            return p <= 2 if half == 1 else p >= 3

        def _yl_to_opp_distance(d):
            # ESPN start.yardLine is 0-100 measured from the HOME goal line
            # (verified 10/4 NE@BUF): home offense -> 100 - yl, away offense -> yl
            yl = (d.get("start") or {}).get("yardLine")
            tm_ = (d.get("team") or {}).get("abbreviation")
            try:
                yl = int(yl)
            except Exception:
                return None
            ha = (teams.get(tm_) or {}).get("home_away")
            if ha == "away":
                return yl
            return 100 - yl

        def _score_tuple(d):
            pl = d.get("plays", []) or []
            if not pl:
                return None
            try:
                return (int(pl[-1].get("awayScore")), int(pl[-1].get("homeScore")))
            except Exception:
                return None

        drives, summ = [], {}
        prev_score = (0, 0)
        for d in raw:
            p = _period(d)
            # track running score across ALL drives so deltas stay correct
            cur_score = _score_tuple(d)
            drive_delta = None
            if cur_score is not None:
                drive_delta = (cur_score[0] - prev_score[0], cur_score[1] - prev_score[1])
                prev_score = cur_score
            if not _in_half(p):
                continue
            tm = (d.get("team") or {}).get("abbreviation")
            res = (d.get("result") or d.get("displayResult") or "").strip()
            plays = d.get("plays", []) or []
            n_off = d.get("offensivePlays") or len(plays)
            yards = d.get("yards")
            dist_to_goal = _yl_to_opp_distance(d)
            res_l = res.lower()
            # ESPN drive results are often abbreviations ("INT", "FUMBLE", "Downs").
            # Turnover on downs is NOT a giveaway; count it separately.
            _words = res_l.replace("-", " ").split()
            is_to = ("interception" in res_l or "int" in _words or "int td" in res_l
                     or "fumble" in res_l or "fum" in _words)
            is_downs = "downs" in res_l
            # muffed punt: the drive belongs to the punting team, but the giveaway is
            # the receiving team's -> credit it to the opponent of this drive's team
            muff_by_receiver = ("punt" in res_l or "fumble" in res_l) and any(
                "muff" in (pl.get("text") or "").lower() for pl in plays)
            is_three_out = ("punt" in res_l) and n_off is not None and n_off <= 3
            rz = dist_to_goal is not None and (dist_to_goal <= 20 or any(
                ((pl.get("end") or {}).get("yardsToEndzone") or 99) <= 20 for pl in plays))
            # points = offense's score delta on this drive (score_after - score_before);
            # fallback to ESPN result abbreviations (TD / FG) when play scores are missing
            pts = 0
            ha_off = (teams.get(tm) or {}).get("home_away")
            if drive_delta is not None and ha_off in ("home", "away"):
                pts = max(0, drive_delta[1] if ha_off == "home" else drive_delta[0])
            elif res_l in ("td", "touchdown") or res_l.startswith("td "):
                pts = 7
            elif res_l in ("fg", "field goal", "made fg"):
                pts = 3
            rec = {"team": tm, "period": p,
                   "start": (d.get("start") or {}).get("text"),
                   "start_clock": ((d.get("start") or {}).get("clock") or {}).get("displayValue"),
                   "start_dist_to_goal": dist_to_goal,
                   "result": res, "plays": n_off, "yards": yards,
                   "time": (d.get("timeElapsed") or {}).get("displayValue"),
                   "score_after": f"{(plays[-1].get('awayScore') if plays else '')}-{(plays[-1].get('homeScore') if plays else '')}"}
            if include_plays:
                rec["pbp"] = [{"q": ((pl.get("period") or {}).get("number")),
                               "clock": ((pl.get("clock") or {}).get("displayValue")),
                               "dd": ((pl.get("start") or {}).get("downDistanceText")),
                               "text": (pl.get("text") or "")[:max_play_chars],
                               "score": pl.get("scoringPlay") or False}
                              for pl in plays]
            drives.append(rec)

            s = summ.setdefault(tm, {"drives": 0, "plays": 0, "yards": 0, "points": 0,
                                     "turnovers": 0, "three_and_outs": 0, "rz_trips": 0,
                                     "short_field_drives": 0, "scoring_drives": 0, "results": []})
            s["results"].append(res)
            # kneel-outs / clock-kills are not real possessions: keep them in the
            # drive list and results, but out of every summary counter
            if res_l.startswith("end of"):
                continue
            s["drives"] += 1
            s["plays"] += n_off or 0
            s["yards"] += yards or 0
            s["points"] += pts
            if muff_by_receiver:
                # the punting team recovered the receiver's muff: not this team's giveaway
                is_to = False
                opp = next((k for k in teams if k != tm), None)
                if opp:
                    o = summ.setdefault(opp, {"drives": 0, "plays": 0, "yards": 0, "points": 0,
                                              "turnovers": 0, "turnovers_on_downs": 0,
                                              "three_and_outs": 0, "rz_trips": 0,
                                              "short_field_drives": 0, "scoring_drives": 0,
                                              "results": []})
                    o["turnovers"] = o.get("turnovers", 0) + 1
            s["turnovers"] += int(is_to)
            s["turnovers_on_downs"] = s.get("turnovers_on_downs", 0) + int(is_downs)
            s["three_and_outs"] += int(is_three_out)
            s["rz_trips"] += int(rz)
            s["short_field_drives"] += int(dist_to_goal is not None and dist_to_goal <= 40)
            s["scoring_drives"] += int(pts > 0)
        for s in summ.values():
            s["ypp"] = round(s["yards"] / s["plays"], 2) if s["plays"] else None

        # --- scoring plays (whole game, as ESPN lists them) ---
        scoring = [{"q": ((sp.get("period") or {}).get("number")),
                    "clock": ((sp.get("clock") or {}).get("displayValue")),
                    "team": ((sp.get("team") or {}).get("abbreviation")),
                    "text": (sp.get("text") or "")[:max_play_chars],
                    "away": sp.get("awayScore"), "home": sp.get("homeScore")}
                   for sp in (data.get("scoringPlays") or [])
                   if _in_half(((sp.get("period") or {}).get("number")))]

        return {"event_id": event_id, "league": lg, "status": status,
                "halftime_now": _espn_halftime(status), "half": half,
                "teams": teams, "summary": summ, "drive_count": len(drives),
                "drives": drives, "scoring_plays": scoring,
                "note": "yardLine-based fields are best-effort; 'summary' is computed from drives in the requested half only"}

    # ---------------------------------------------------------------
    # CFB / NFL QB STARTER STATUS (added 10/15/2026) — QB gate v1.4
    # Source: ESPN public site API (no key). For a team: last N completed
    # games' passing lines (starter = first passer listed with attempts),
    # next scheduled game, and any ESPN-listed injuries for the team.
    # Does NOT read conference availability pages or news — those stay
    # manual checks in the protocol.
    # ---------------------------------------------------------------
    @mcp.tool()
    def get_cfb_qb_status(team: str, league: str = "cfb", games: int = 2) -> dict:
        """QB starter assurance inputs for one team (CFB default, league='nfl' also works).

        team: name, nickname, location or abbreviation, e.g. 'Texas State',
              'Colorado State', 'ECU', 'Georgia Southern'.
        games: how many most-recent completed games to read (default 2).

        Returns: resolved team, next_game (opponent, date, event_id, conference
        game flag if ESPN exposes it, injuries listed by ESPN), and per past game:
        opponent, score, starter_qb (first passer listed with attempts), all
        passers with comp/att, and first_snap_qb parsed from the first offensive
        play text when it names a passer/rusher.
        """
        import requests as _rq

        sport = "college-football" if league.lower() in ("cfb", "ncaaf", "college") else "nfl"
        base = "https://site.api.espn.com/apis/site/v2/sports/football/" + sport
        hdr = {"User-Agent": "Mozilla/5.0"}

        def _get(url, **params):
            r = _rq.get(url, params=params or None, headers=hdr, timeout=25)
            r.raise_for_status()
            return r.json()

        try:
            # 1) resolve team id
            tj = _get(base + "/teams", limit=1000)
            teams = tj["sports"][0]["leagues"][0]["teams"]
            q = team.strip().lower()
            # common names ESPN spells differently
            _alias = {"appalachian state": "app state", "appalachian st": "app state",
                      "app st": "app state", "sam houston state": "sam houston",
                      "sam houston st": "sam houston", "southern miss": "southern miss",
                      "southern mississippi": "southern miss", "ul monroe": "ul monroe",
                      "louisiana monroe": "ul monroe", "miami (oh)": "miami (oh)",
                      "miami ohio": "miami (oh)", "ole miss": "ole miss",
                      "mississippi": "ole miss", "jax state": "jacksonville state",
                      "jacksonville st": "jacksonville state", "texas a&m": "texas a&m",
                      "fiu": "florida international", "fau": "florida atlantic",
                      "uconn": "uconn", "connecticut": "uconn", "hawaii": "hawai'i"}
            q = _alias.get(q, q)
            hit = None
            for t in teams:
                tt = t["team"]
                keys = [str(tt.get(k, "")).lower() for k in
                        ("displayName", "shortDisplayName", "abbreviation", "location", "name", "nickname")]
                if q in keys:
                    hit = tt
                    break
            if hit is None:
                for t in teams:
                    tt = t["team"]
                    if q in str(tt.get("displayName", "")).lower():
                        hit = tt
                        break
            if hit is None:
                # last resort: every word of the query appears in location + name
                qw = [w for w in q.replace(".", "").split() if w not in ("state", "st")]
                for t in teams:
                    tt = t["team"]
                    blob = " ".join(str(tt.get(k, "")) for k in
                                    ("displayName", "location", "shortDisplayName")).lower()
                    if qw and all(w in blob for w in qw):
                        hit = tt
                        break
            if hit is None:
                return {"error": f"team not found on ESPN {sport}: {team}"}
            tid = str(hit["id"])
            resolved = {"id": tid, "name": hit.get("displayName"), "abbr": hit.get("abbreviation")}

            # 2) schedule → completed games + next game
            sj = _get(base + f"/teams/{tid}/schedule")
            evs = sj.get("events", [])
            completed, upcoming = [], []
            for e in evs:
                comp = (e.get("competitions") or [{}])[0]
                st = comp.get("status", {}).get("type", {})
                (completed if st.get("completed") else upcoming).append(e)
            recent = completed[-int(games):] if games else []

            def _opp(e):
                comp = (e.get("competitions") or [{}])[0]
                for c in comp.get("competitors", []):
                    if str(c.get("team", {}).get("id")) != tid:
                        return {"opponent": c.get("team", {}).get("displayName"),
                                "home_away": "home" if c.get("homeAway") == "away" else "away"}
                return {"opponent": None, "home_away": None}

            def _score(e):
                comp = (e.get("competitions") or [{}])[0]
                us = them = None
                for c in comp.get("competitors", []):
                    val = c.get("score", {})
                    val = val.get("value") if isinstance(val, dict) else val
                    if str(c.get("team", {}).get("id")) == tid:
                        us = val
                    else:
                        them = val
                return {"us": us, "them": them}

            # 3) per past game: passers + first-snap QB
            past = []
            for e in reversed(recent):
                eid = str(e["id"])
                try:
                    sm = _get(base + "/summary", event=eid)
                except Exception as ex:
                    past.append({"event_id": eid, "error": f"summary failed: {ex}"})
                    continue
                passers = []
                for tb in sm.get("boxscore", {}).get("players", []):
                    if str(tb.get("team", {}).get("id")) != tid:
                        continue
                    for stt in tb.get("statistics", []):
                        if stt.get("name") != "passing":
                            continue
                        for a in stt.get("athletes", []):
                            stats = a.get("stats") or []
                            passers.append({
                                "name": a.get("athlete", {}).get("displayName"),
                                "comp_att": stats[0] if stats else None,
                                "yds": stats[1] if len(stats) > 1 else None,
                                "espn_starter_flag": a.get("starter"),
                            })
                starter = None
                for p in passers:
                    ca = p.get("comp_att") or ""
                    try:
                        att = int(str(ca).split("/")[1])
                    except Exception:
                        att = 0
                    if att > 0:
                        starter = p["name"]
                        break
                starter_source = "boxscore.players passing" if starter else None
                if starter is None:
                    # fallback: ESPN 'leaders' block (top passer by yards)
                    for lb in sm.get("leaders", []):
                        if str(lb.get("team", {}).get("id")) != tid:
                            continue
                        for cat in lb.get("leaders", []):
                            if cat.get("name") in ("passingYards", "passing", "passingLeader"):
                                lead = cat.get("leaders") or []
                                if lead:
                                    starter = lead[0].get("athlete", {}).get("displayName")
                                    starter_source = "leaders.passingYards (fallback)"
                                    passers.append({"name": starter, "comp_att": lead[0].get("displayValue"),
                                                    "yds": None, "espn_starter_flag": None})
                                break
                first_snap = None
                first_play = None
                for d in sm.get("drives", {}).get("previous", []):
                    if str(d.get("team", {}).get("id")) != tid:
                        continue
                    plays = d.get("plays") or []
                    if not plays:
                        continue
                    first_play = plays[0].get("text")
                    txt = first_play or ""
                    for marker in (" pass ", " pass,", " sacked", " scrambles", " run ", " rush "):
                        if marker in txt:
                            first_snap = txt.split(marker)[0].strip()
                            break
                    break
                past.append({
                    "event_id": eid,
                    "date": e.get("date"),
                    **_opp(e),
                    "score": _score(e),
                    "starter_qb": starter,
                    "starter_source": starter_source,
                    "first_snap_qb_parsed": first_snap,
                    "first_play_text": first_play,
                    "passers": passers,
                })

            # 4) next game + ESPN injuries (summary works pregame)
            nxt = None
            if upcoming:
                e = upcoming[0]
                eid = str(e["id"])
                comp = (e.get("competitions") or [{}])[0]
                nxt = {"event_id": eid, "date": e.get("date"), **_opp(e),
                       "conference_game": comp.get("conferenceCompetition"),
                       "injuries": [], "injuries_note": None}
                try:
                    sm = _get(base + "/summary", event=eid)
                    inj = sm.get("injuries") or []
                    for blk in inj:
                        if str(blk.get("team", {}).get("id")) != tid:
                            continue
                        for i in blk.get("injuries", []):
                            ath = i.get("athlete", {})
                            nxt["injuries"].append({
                                "name": ath.get("displayName"),
                                "pos": ath.get("position", {}).get("abbreviation"),
                                "status": i.get("status"),
                                "detail": (i.get("details") or {}).get("type"),
                            })
                    if not inj:
                        nxt["injuries_note"] = "ESPN summary has no injuries block for this game (common for CFB) — check the conference availability report"
                except Exception as ex:
                    nxt["injuries_note"] = f"summary failed: {ex}"

            # 5) assurance hint (table QB1 = starter of most recent game)
            qb1 = past[0].get("starter_qb") if past else None
            consistent = bool(past) and all(g.get("starter_qb") == qb1 for g in past if g.get("starter_qb"))
            qb_flags = []
            if nxt:
                for i in nxt.get("injuries", []):
                    if i.get("pos") == "QB":
                        qb_flags.append(i)
            return {
                "team": resolved,
                "league": sport,
                "table_qb1": qb1,
                "qb1_started_last_n": consistent,
                "qb_injury_flags": qb_flags,
                "next_game": nxt,
                "recent_games": past,
                "note": "Tier B/C still require the conference availability report + news window since the last game; this tool supplies QB1 identity, last-N consistency, and ESPN injuries only.",
            }
        except Exception as ex:
            return {"error": str(ex), "team_query": team}


    # ------------------------------------------------------------------
    # NBA FanDuel protocol tools (job C, 10/30/2026)
    #   get_nba_player_log     — last-N game log + minutes/rate summary
    #   get_nba_team_rotation  — who plays, how much, how stable
    #   get_nba_injury_report  — ESPN injuries + today's games
    # Game-log data = committed CSVs under backtests/nba/ (hoopR/ESPN box
    # scores, refreshed weekly by nba_pull_gamelogs.py). Injuries/schedule
    # are live from ESPN's public JSON (same host as the football tools).
    # ------------------------------------------------------------------
    _NBA_CACHE = {}
    _NBA_TEAM_WORDS = {
        "ATL": "hawks", "BOS": "celtics", "BKN": "nets", "CHA": "hornets", "CHI": "bulls",
        "CLE": "cavaliers", "DAL": "mavericks", "DEN": "nuggets", "DET": "pistons",
        "GS": "warriors", "GSW": "warriors", "HOU": "rockets", "IND": "pacers", "LAC": "clippers",
        "LAL": "lakers", "MEM": "grizzlies", "MIA": "heat", "MIL": "bucks", "MIN": "timberwolves",
        "NO": "pelicans", "NOP": "pelicans", "NY": "knicks", "NYK": "knicks", "OKC": "thunder",
        "ORL": "magic", "PHI": "76ers", "PHX": "suns", "POR": "trail blazers", "SAC": "kings",
        "SA": "spurs", "SAS": "spurs", "TOR": "raptors", "UTAH": "jazz", "UTA": "jazz",
        "WSH": "wizards", "WAS": "wizards",
    }

    def _nba_base():
        from pathlib import Path as _P
        return _P(__file__).resolve().parent / "backtests" / "nba"

    def _nba_seasons():
        import re as _re
        out = []
        for p in sorted(_nba_base().glob("nba_player_games_*.csv")):
            m = _re.search(r"(\d{4}-\d{2})", p.name)
            if m:
                out.append((m.group(1), p))
        return out

    def _nba_load(season=""):
        """Rows of one season's game log (latest season when blank), cached."""
        import csv as _csv
        seasons = _nba_seasons()
        if not seasons:
            return None, "no backtests/nba/nba_player_games_*.csv committed"
        if season:
            hit = [s for s in seasons if s[0] == season]
            if not hit:
                return None, f"season {season} not found; have {[s[0] for s in seasons]}"
            key, path = hit[0]
        else:
            key, path = seasons[-1]
        mt = path.stat().st_mtime
        c = _NBA_CACHE.get(key)
        if c and c[0] == mt:
            return c[1], None
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(_csv.DictReader(f))
        for r in rows:
            r["_season"] = key
            for k in ("minutes", "points", "rebounds", "assists", "steals", "blocks", "turnovers",
                      "field_goals_attempted", "free_throws_attempted", "fd_pts", "fd_per_min",
                      "plus_minus", "team_score", "opponent_team_score"):
                try:
                    r[k] = float(r.get(k) or 0)
                except Exception:
                    r[k] = 0.0
            r["_dnp"] = str(r.get("did_not_play", "")).strip().lower() == "true"
            r["_start"] = str(r.get("starter", "")).strip().lower() == "true"
        _NBA_CACHE[key] = (mt, rows)
        return rows, None

    def _nba_norm(s):
        import unicodedata as _u
        s = _u.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
        return " ".join(s.lower().replace(".", "").replace("'", "").split())

    def _nba_find_player(rows, query):
        q = _nba_norm(query)
        names = {}
        for r in rows:
            names.setdefault(r["athlete_display_name"], r.get("athlete_id"))
        exact = [n for n in names if _nba_norm(n) == q]
        if exact:
            return exact[0], []
        parts = q.split()
        cands = [n for n in names if all(p in _nba_norm(n) for p in parts)]
        if len(cands) == 1:
            return cands[0], []
        return None, sorted(cands)[:10]

    @mcp.tool()
    def get_nba_player_log(player: str, games: int = 10, season: str = "") -> dict:
        """NBA player game log for the FanDuel NBA protocol: the player's last N
        games (newest first) with minutes, starter flag, DNP reason, box score,
        FanDuel points (1 pt, 1.2 reb, 1.5 ast, 3 stl, 3 blk, -1 TO) and FD/min,
        plus a summary (games, starts, avg minutes, last-3 minutes, FD/min season
        and last-5). Also returns the prior season's summary for the rate blend.
        player: full or partial name ("Derik Queen", "queen"). games: 1-40.
        season: "2026-27" style; blank = latest committed season. Data = the
        committed game-log CSVs (weekly refresh) — check data_through."""
        rows, err = _nba_load(season)
        if err:
            return {"error": err}
        name, cands = _nba_find_player(rows, player)
        if not name:
            return {"error": f"player '{player}' not found" + (f"; candidates: {cands}" if cands else "")}
        games = max(1, min(int(games or 10), 40))
        mine = [r for r in rows if r["athlete_display_name"] == name]
        mine.sort(key=lambda r: (r["game_date"], r["game_id"]), reverse=True)
        played = [r for r in mine if not r["_dnp"] and r["minutes"] > 0]
        log = []
        for r in mine[:games]:
            log.append({
                "date": r["game_date"], "team": r["team_abbreviation"], "opp": r["opponent_team_abbreviation"],
                "home_away": r.get("home_away"), "starter": r["_start"], "dnp": r["_dnp"],
                "reason": (r.get("reason") or None) if r["_dnp"] else None,
                "min": r["minutes"], "pts": r["points"], "reb": r["rebounds"], "ast": r["assists"],
                "stl": r["steals"], "blk": r["blocks"], "tov": r["turnovers"],
                "fga": r["field_goals_attempted"], "fta": r["free_throws_attempted"],
                "fd_pts": r["fd_pts"], "fd_per_min": r["fd_per_min"],
                "score": f"{int(r['team_score'])}-{int(r['opponent_team_score'])}",
            })

        def _summ(pl):
            if not pl:
                return None
            mins = sum(r["minutes"] for r in pl)
            fd = sum(r["fd_pts"] for r in pl)
            last3 = pl[:3]
            last5 = pl[:5]
            return {
                "games": len(pl), "starts": sum(1 for r in pl if r["_start"]),
                "avg_min": round(mins / len(pl), 1), "avg_fd": round(fd / len(pl), 1),
                "fd_per_min": round(fd / mins, 3) if mins else None,
                "last3_avg_min": round(sum(r["minutes"] for r in last3) / len(last3), 1),
                "last5_fd_per_min": round(sum(r["fd_pts"] for r in last5) / max(1e-9, sum(r["minutes"] for r in last5)), 3),
                "min_sd": round((sum((r["minutes"] - mins / len(pl)) ** 2 for r in pl) / len(pl)) ** 0.5, 1),
                "fga_per_min": round(sum(r["field_goals_attempted"] for r in pl) / mins, 3) if mins else None,
            }

        cur = _summ(played)
        dnps = [{"date": r["game_date"], "reason": r.get("reason") or ""} for r in mine if r["_dnp"]][:10]
        prior = None
        seasons = [s[0] for s in _nba_seasons()]
        this = rows[0]["_season"] if rows else None
        if this in seasons and seasons.index(this) > 0:
            prow, _e = _nba_load(seasons[seasons.index(this) - 1])
            if prow:
                pp = [r for r in prow if r["athlete_display_name"] == name and not r["_dnp"] and r["minutes"] > 0]
                pp.sort(key=lambda r: r["game_date"], reverse=True)
                prior = _summ(pp)
                if prior:
                    prior["season"] = seasons[seasons.index(this) - 1]
                    prior["team"] = pp[0]["team_abbreviation"] if pp else None
        return {
            "player": name, "team": mine[0]["team_abbreviation"] if mine else None,
            "position": mine[0].get("athlete_position_abbreviation") if mine else None,
            "season": this, "data_through": max(r["game_date"] for r in rows),
            "summary": cur, "dnp": dnps, "prior_season": prior, "log": log,
            "note": "minutes x rate engine: use avg_min/last3_avg_min for the minutes path and fd_per_min "
                    "(this season) blended with prior_season.fd_per_min for the rate; a rookie has no prior_season.",
        }

    @mcp.tool()
    def get_nba_team_rotation(team: str, games: int = 5, season: str = "") -> dict:
        """NBA team rotation for the FanDuel NBA protocol: over the team's last N
        games, every player's starts, minutes per game, average, last-game minutes,
        trend (last game minus average), DNPs with reasons, and FD/min; plus a
        240-minute reconciliation per game and a rotation-stability index (mean
        per-player minutes SD among rotation players — lower = tighter rotation).
        team: abbreviation as in the box scores (ATL, GS, NO, NY, SA, UTAH, WSH...).
        games: 1-20. Data = committed game-log CSVs — check data_through."""
        rows, err = _nba_load(season)
        if err:
            return {"error": err}
        t = str(team or "").upper().strip()
        alias = {"GSW": "GS", "NOP": "NO", "NYK": "NY", "SAS": "SA", "UTA": "UTAH", "WAS": "WSH", "PHO": "PHX"}
        t = alias.get(t, t)
        trows = [r for r in rows if r["team_abbreviation"] == t]
        if not trows:
            have = sorted({r["team_abbreviation"] for r in rows})
            return {"error": f"team '{team}' not found; have {have}"}
        games = max(1, min(int(games or 5), 20))
        gids = sorted({(r["game_date"], r["game_id"]) for r in trows}, reverse=True)[:games]
        gset = {g[1] for g in gids}
        sub = [r for r in trows if r["game_id"] in gset]
        order = [g[1] for g in gids]  # newest first
        per = {}
        for r in sub:
            p = per.setdefault(r["athlete_display_name"], {"pos": r.get("athlete_position_abbreviation"),
                                                            "mins": {}, "starts": 0, "dnp": [], "fd": 0.0, "m": 0.0})
            if r["_dnp"] or r["minutes"] <= 0:
                p["dnp"].append({"date": r["game_date"], "reason": r.get("reason") or ""})
                p["mins"][r["game_id"]] = 0.0
            else:
                p["mins"][r["game_id"]] = r["minutes"]
                p["starts"] += 1 if r["_start"] else 0
                p["fd"] += r["fd_pts"]
                p["m"] += r["minutes"]
        players = []
        sds = []
        for n, p in per.items():
            seq = [p["mins"].get(g) for g in order]
            played = [x for x in seq if x]
            avg = sum(played) / len(played) if played else 0.0
            last = seq[0] if seq and seq[0] is not None else None
            sd = (sum((x - avg) ** 2 for x in played) / len(played)) ** 0.5 if len(played) >= 2 else None
            if avg >= 12 and sd is not None:
                sds.append(sd)
            players.append({
                "player": n, "pos": p["pos"], "gp": len(played), "starts": p["starts"],
                "avg_min": round(avg, 1), "last_min": last,
                "trend": round(last - avg, 1) if last is not None and played else None,
                "min_sd": round(sd, 1) if sd is not None else None,
                "fd_per_min": round(p["fd"] / p["m"], 3) if p["m"] else None,
                "absent_games": len(order) - len(p["mins"]),
                "minutes_by_game": [round(x, 1) if x is not None else None for x in seq],
                "dnp": p["dnp"],
            })
        players.sort(key=lambda x: (-x["avg_min"], x["player"]))
        games_out = []
        for d, g in gids:
            gr = [r for r in sub if r["game_id"] == g]
            tot = sum(r["minutes"] for r in gr)
            any_r = gr[0]
            games_out.append({"date": d, "game_id": g, "opp": any_r["opponent_team_abbreviation"],
                              "home_away": any_r.get("home_away"),
                              "score": f"{int(any_r['team_score'])}-{int(any_r['opponent_team_score'])}",
                              "team_minutes": round(tot, 0),
                              "starters": [r["athlete_display_name"] for r in gr if r["_start"]]})
        return {
            "team": t, "season": rows[0]["_season"], "data_through": max(r["game_date"] for r in rows),
            "games": games_out,
            "rotation_stability_index": round(sum(sds) / len(sds), 2) if sds else None,
            "rotation_players": len([p for p in players if p["avg_min"] >= 12]),
            "players": players,
            "note": "240 team minutes per regulation game (265 with one OT); starters list is per game; "
                    "trend = last game minus average over the window; absent_games = not in the box score "
                    "at all (inactive/injured/not on roster), DNP = dressed but did not play.",
        }

    @mcp.tool()
    def get_nba_injury_report(team: str = "", date: str = "") -> dict:
        """Live NBA injury report from ESPN's public JSON for the FanDuel NBA
        protocol (no key): every listed player with status (out / day-to-day /
        questionable ...), injury type/detail, expected return date and the
        latest note; plus the day's games (tip time UTC, teams, status, score).
        team: optional filter — abbreviation (ATL, GS, NO...) or any part of the
        team name ("hawks"); blank = all teams. date: optional YYYYMMDD for the
        scoreboard; blank = today."""
        inj, err = _espn_get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries", {})
        if err:
            return err
        want = None
        if team:
            tt = str(team).strip()
            want = _NBA_TEAM_WORDS.get(tt.upper(), tt.lower())
        teams = []
        n_players = 0
        for blk in inj.get("injuries", []) or []:
            dn = blk.get("displayName") or ""
            if want and want not in dn.lower():
                continue
            items = []
            for i in blk.get("injuries", []) or []:
                ath = i.get("athlete") or {}
                det = i.get("details") or {}
                items.append({
                    "name": ath.get("displayName"),
                    "pos": (ath.get("position") or {}).get("abbreviation"),
                    "status": i.get("status") or (i.get("type") or {}).get("description"),
                    "fantasy_status": (det.get("fantasyStatus") or {}).get("description"),
                    "injury": det.get("type"), "detail": det.get("detail"), "side": det.get("side"),
                    "return_date": det.get("returnDate"),
                    "updated": i.get("date"),
                    "note": i.get("shortComment"),
                })
            n_players += len(items)
            teams.append({"team": dn, "espn_team_id": blk.get("id"), "injuries": items})
        params = {"limit": 50}
        if date:
            params["dates"] = date
        sb, err2 = _espn_get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", params)
        games = []
        if not err2:
            for ev in sb.get("events", []) or []:
                comp = (ev.get("competitions") or [{}])[0]
                tm = {}
                for c in comp.get("competitors", []) or []:
                    tm[c.get("homeAway")] = {"abbr": (c.get("team") or {}).get("abbreviation"),
                                             "name": (c.get("team") or {}).get("displayName"),
                                             "score": c.get("score")}
                st = (ev.get("status") or {}).get("type") or {}
                games.append({"event_id": ev.get("id"), "name": ev.get("shortName"), "tip_utc": ev.get("date"),
                              "status": st.get("description"), "detail": st.get("detail"),
                              "away": tm.get("away"), "home": tm.get("home")})
        return {
            "as_of": inj.get("timestamp"), "team_filter": team or None,
            "teams_listed": len(teams), "players_listed": n_players, "teams": teams,
            "games": games, "scoreboard_error": err2,
            "note": "ESPN statuses lag the official 5:30 PM ET report by minutes to an hour; confirm "
                    "game-time decisions against the posted starting lineup before lock (late-swap rule).",
        }

    # ===== NBA news + lineups tools (FanDuel NBA protocol, added 10/30) =====
    @mcp.tool()
    def get_nba_player_news(player: str = "", team: str = "", limit: int = 25, days: int = 3) -> dict:
        """NBA player news blurbs with RotoWire's analysis (headline, news,
        analysis, time) for the FanDuel NBA protocol, from RotoWire's free NBA
        news page (latest items across all players in one call). player:
        optional name filter ("maxey"); team: optional filter on text
        ("76ers", "PHI"); limit: max items (1-60). Fallbacks: ESPN fantasy
        news feed, then ESPN general NBA news. parse_ok=false returns a text
        fallback so the news is still readable."""
        import re as _r, html as _h, json as _j, urllib.request as _u, datetime as _d
        def _fetch(url):
            req = _u.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh)"})
            with _u.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", "replace")
        def _txt(x):
            x = _r.sub(r"<[^>]+>", " ", x or "")
            return _r.sub(r"\s+", " ", _h.unescape(x)).strip()
        limit = max(1, min(int(limit or 25), 60))
        pl, tm = (player or "").lower().strip(), (team or "").lower().strip()
        warnings, out, src = [], [], "rotowire_nba_news"
        page = None
        try:
            page = _fetch("https://www.rotowire.com/basketball/news.php")
        except Exception as e:
            warnings.append(f"rotowire news fetch failed: {type(e).__name__}: {e}")
        parsed = 0
        if page:
            for b in _r.split(r'<div class="news-update(?:\s|")', page)[1:]:
                def g(cls):
                    m = _r.search(r'class="news-update__' + cls + r'[^"]*"[^>]*>(.*?)</(?:div|a|span)>', b, _r.S)
                    return _txt(m.group(1)) if m else None
                name = g("player-link")
                head, news, ana, ts = g("headline"), g("news"), g("analysis"), g("timestamp")
                if not (name or head or news):
                    continue
                parsed += 1
                if ana and ana.upper().startswith("ANALYSIS"):
                    ana = ana[8:].strip()
                if ana and "subscribe" in ana.lower():
                    ana = "LOCKED (RotoWire subscriber-only)"
                blob = " ".join(x for x in [name, head, news, ana, _txt(b[:600])] if x).lower()
                if pl and pl not in blob: continue
                if tm and tm not in blob: continue
                out.append({"time": ts, "player": name, "headline": head, "news": news,
                            "analysis": (ana[:1500] if ana else None)})
                if len(out) >= limit: break
        res = {"source": src, "fetched_utc": _d.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"),
               "parse_ok": parsed > 0, "items_parsed": parsed, "count": len(out), "items": out}
        if page and parsed == 0:
            body = _r.sub(r"<(script|style)[^>]*>.*?</\1>", " ", page, flags=_r.S)
            t = _txt(body)
            if pl:
                k = t.lower().find(pl)
                res["text_fallback"] = t[max(0, k - 300): k + 3000] if k >= 0 else "player not found on page"
            else:
                k = t.find("ANALYSIS")
                res["text_fallback"] = t[max(0, k - 1500): max(0, k - 1500) + 15000]
        if not page:
            src = "espn_nba_news"
            try:
                data = _j.loads(_fetch("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news?limit=100"))
                for it in data.get("articles") or []:
                    head = it.get("headline") or ""; story = it.get("description") or ""
                    if pl and pl not in (head + " " + story).lower(): continue
                    out.append({"time": it.get("published"), "player": None, "headline": head,
                                "news": story, "analysis": None})
                    if len(out) >= limit: break
                res.update(source=src, count=len(out), items=out)
            except Exception as e:
                warnings.append(f"espn news failed: {type(e).__name__}: {e}")
        res["warnings"] = warnings or None
        return res

    @mcp.tool()
    def get_nba_lineups(team: str = "") -> dict:
        """Today's NBA starting lineups from RotoWire's free NBA Lineups page
        for the FanDuel NBA protocol: per game, each team's status (Expected /
        Confirmed Lineup), the five starters with positions, and the
        may-not-play list with injury tags (OUT / GTD / Prob / Ques). team:
        optional filter on the team abbreviation as RotoWire prints it (PHI,
        NYK, GSW...). If the page layout changes, parse_ok=false and a
        text fallback is returned so the data is still readable."""
        import re as _r, html as _h, urllib.request as _u, datetime as _d
        url = "https://www.rotowire.com/basketball/nba-lineups.php"
        try:
            req = _u.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh)"})
            with _u.urlopen(req, timeout=25) as r:
                page = r.read().decode("utf-8", "replace")
        except Exception as e:
            return {"error": f"rotowire fetch failed: {type(e).__name__}: {e}"}
        def _txt(s):
            s = _r.sub(r"<[^>]+>", " ", s)
            return _r.sub(r"\s+", " ", _h.unescape(s)).strip()
        boxes = _r.split(r'<div class="lineup is-nba', page)[1:]
        games = []
        for b in boxes:
            abbrs = [_txt(a) for a in _r.findall(r'class="lineup__abbr"[^>]*>(.*?)</', b, _r.S)]
            time_m = _r.search(r'class="lineup__time"[^>]*>(.*?)</div>', b, _r.S)
            sides = _r.split(r'<ul class="lineup__list', b)[1:]
            teams_out = []
            for i, s in enumerate(sides[:2]):
                st = _r.search(r'class="lineup__status[^"]*"[^>]*>(.*?)</li>', s, _r.S)
                players = []
                for li in _r.findall(r'<li class="lineup__player[^"]*"[^>]*>(.*?)</li>', s, _r.S):
                    pos = _r.search(r'class="lineup__pos"[^>]*>(.*?)</div>', li, _r.S)
                    nm = _r.search(r'title="([^"]+)"', li) or _r.search(r'<a[^>]*>(.*?)</a>', li, _r.S)
                    inj = _r.search(r'class="lineup__inj"[^>]*>(.*?)</span>', li, _r.S)
                    players.append({"pos": _txt(pos.group(1)) if pos else None,
                                    "name": _h.unescape(nm.group(1)).strip() if nm else _txt(li),
                                    "tag": _txt(inj.group(1)) if inj else None})
                teams_out.append({"team": abbrs[i] if i < len(abbrs) else None,
                                  "status": _txt(st.group(1)) if st else None,
                                  "starters": players[:5],
                                  "may_not_play": players[5:]})
            if not abbrs:
                continue
            if team and not any(team.upper() == (a or "").upper() for a in abbrs):
                continue
            games.append({"matchup": " @ ".join(abbrs[:2]) if abbrs else None,
                          "time": _txt(time_m.group(1)) if time_m else None,
                          "teams": teams_out})
        parse_ok = bool(games) and any(t["starters"] for g in games for t in g["teams"])
        res = {"source": "rotowire_nba_lineups",
               "fetched_utc": _d.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"),
               "parse_ok": parse_ok, "games": games}
        if not parse_ok:
            body = _r.sub(r"<(script|style)[^>]*>.*?</\1>", " ", page, flags=_r.S)
            t = _txt(body)
            k = t.find("Lineup")
            res["text_fallback"] = t[max(0, k - 200): max(0, k - 200) + 20000]
        return res
