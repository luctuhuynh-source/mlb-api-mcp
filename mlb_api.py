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
            return roster
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    def get_mlb_search_players(fullname: str, sport_id: int = 1, search_key: str = "fullname") -> dict:
        """
        Search for players by name.

        Args:
            fullname (str): Player name to search for.
            sport_id (int): Sport ID (default: 1 for MLB).
            search_key (str): Search key (default: "fullname").

        Returns:
            dict: Player search results.
        """
        try:
            player_ids = mlb.get_people_id(fullname, sport_id=sport_id, search_key=search_key)
            return {"player_ids": player_ids}
        except Exception as e:
            return {"error": str(e)}

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
        """
        Get lineup information for a specific game by game_id.

        Args:
            game_id (int): The game ID.

        Returns:
            dict: Game lineup information.
        """
        try:
            # Get the boxscore data
            boxscore = mlb.get_game_box_score(game_id)

            result = {"game_id": game_id, "teams": {}}

            # Process both teams (away and home)
            for team_type in ["away", "home"]:
                if hasattr(boxscore, "teams") and hasattr(boxscore.teams, team_type):
                    team_data = getattr(boxscore.teams, team_type)

                    team_info = {
                        "team_name": getattr(team_data.team, "name", "Unknown"),
                        "team_id": getattr(team_data.team, "id", None),
                        "players": [],
                    }

                    # Get players from the team data
                    if hasattr(team_data, "players") and team_data.players is not None:
                        players_dict = team_data.players

                        # Extract player information
                        for player_key, player_data in players_dict.items():
                            if player_key.startswith("id"):
                                player_info = {
                                    "player_id": getattr(player_data.person, "id", None),
                                    "player_name": getattr(player_data.person, "fullname", "Unknown"),
                                    "jersey_number": getattr(player_data, "jerseynumber", None),
                                    "positions": [],
                                    "batting_order": None,
                                    "game_entries": [],
                                }

                                # Get position information
                                if hasattr(player_data, "allpositions") and player_data.allpositions is not None:
                                    for position in player_data.allpositions:
                                        position_info = {
                                            "position": getattr(position, "abbreviation", None),
                                            "position_name": getattr(position, "name", None),
                                        }
                                        player_info["positions"].append(position_info)

                                # Get batting order from player data directly
                                if hasattr(player_data, "battingorder"):
                                    player_info["batting_order"] = getattr(player_data, "battingorder", None)

                                # Get game entry information (substitutions, etc.)
                                if hasattr(player_data, "gamestatus"):
                                    game_status = player_data.gamestatus
                                    entry_info = {
                                        "is_on_bench": getattr(game_status, "isonbench", False),
                                        "is_substitute": getattr(game_status, "issubstitute", False),
                                        "status": getattr(game_status, "status", None),
                                    }
                                    player_info["game_entries"].append(entry_info)

                                team_info["players"].append(player_info)

                    # Sort players by batting order (starting lineup first, then substitutes)
                    def sort_key(player):
                        batting_order = player.get("batting_order")
                        if batting_order is None:
                            return 999  # Put non-batting order players at the end
                        return int(str(batting_order).replace("0", ""))  # Handle batting order formatting

                    team_info["players"].sort(key=sort_key)
                    result["teams"][team_type] = team_info

            return result
        except Exception as e:
            return {"error": str(e)}

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
