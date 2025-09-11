import os
import pandas as pd
from nhlpy import NHLClient
import json
import requests
from bs4 import BeautifulSoup

nhl_teams = [
    "BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR",
    "CAR", "CBJ", "NJD", "NYI", "NYR", "PHI", "PIT", "WSH",
    "CHI", "COL", "DAL", "MIN", "NSH", "STL", "WPG",
    "ANA", "CGY", "EDM", "LAK", "SJS", "SEA", "VAN", "VGK", "UTA" 
]

def get_rosters(season):
    client = NHLClient()
    roster_map = {}

    for team in nhl_teams:
        roster = client.teams.team_roster(team_abbr=team, season=season)
        for position_group in ["forwards", "defensemen", "goalies"]:
            if position_group not in roster:
                continue
            for player in roster[position_group]:
                last_name = player['lastName']['default'].strip()
                first_name = player['firstName']['default'].strip()
                entry = {
                    "id": player.get("id", -1),
                    "pos": player.get("positionCode", "UNK"),
                    "first_name": first_name
                }

                if last_name not in roster_map:
                    roster_map[last_name] = [entry]
                else:
                    roster_map[last_name].append(entry)

    return roster_map

def add_ids_to_csv(csv_file, output_file, roster_map):
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_path, csv_file))
    output_path = os.path.abspath(os.path.join(base_path, output_file))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)
    df["LastName"] = df["Name"].str.split(", ").str[0].str.strip()
    df["FirstName"] = df["Name"].str.split(", ").str[1].str.strip()

    def map_id(row):
        last_name = row["LastName"]
        first_name = row["FirstName"]
        entries = roster_map.get(last_name, [])
        # Try exact first name match
        for e in entries:
            if e["first_name"].lower() == first_name.lower():
                return e["id"]
        # If no exact match, return first in the list
        return entries[0]["id"] if entries else -1

    def map_pos(row):
        last_name = row["LastName"]
        first_name = row["FirstName"]
        entries = roster_map.get(last_name, [])
        for e in entries:
            if e["first_name"].lower() == first_name.lower():
                return e["pos"]
        return entries[0]["pos"] if entries else "NULL"

    df["ID"] = df.apply(map_id, axis=1)
    df["ID"] = df["ID"].apply(lambda x: str(int(x)) if isinstance(x, (int, float)) and x != -1 else str(x))
    df["Pos"] = df.apply(map_pos, axis=1)

    df = df[["ID", "LastName", "FirstName", "Pos"]]
    df.to_csv(output_path, index=False)

def get_sk_stats(csv_file, output_file):
    client = NHLClient()
    sk_stats = {}

    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_path, csv_file))
    output_path = os.path.abspath(os.path.join(base_path, output_file))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    count = 0
    df = pd.read_csv(csv_path)
    for pl in df["ID"]:
        if pl == -1: 
            continue
        sk_stats[pl] = {}
        pl_stats = client.stats.player_career_stats(player_id=pl)
        szn_tot = pl_stats["seasonTotals"]
        for szn in szn_tot:
            if szn.get("leagueAbbrev") == "NHL" and szn.get("gameTypeId") == 2:
                szn_key = str(szn["season"])
                sk_stats[pl][szn_key] = {
                    "gp": szn.get("gamesPlayed", 0),
                    "goals": szn.get("goals", 0),
                    "assists": szn.get("assists", 0),
                    "points": szn.get("points", 0),
                    "ppg": szn.get("powerPlayGoals", 0),
                    "ppa": szn.get("powerPlayPoints", 0),
                    "sog": szn.get("shots", 0),
                }
        count+=1
        print(count)

    with open(output_path, "w") as f:
        json.dump({"sk_stats": sk_stats}, f, indent=2)

def get_gl_stats(csv_file, output_file):
    client = NHLClient()
    gl_stats = {}

    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_path, csv_file))
    output_path = os.path.abspath(os.path.join(base_path, output_file))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    count = 0
    df = pd.read_csv(csv_path)
    for pl in df["ID"]:
        if pl == -1: 
            continue
        gl_stats[pl] = {}
        pl_stats = client.stats.player_career_stats(player_id=pl)
        szn_tot = pl_stats["seasonTotals"]
        for szn in szn_tot:
            if szn.get("leagueAbbrev") == "NHL" and szn.get("gameTypeId") == 2:
                szn_key = str(szn["season"])
                gl_stats[pl][szn_key] = {
                    "gp": szn.get("gamesPlayed", 0),
                    "w": szn.get("wins", 0),
                    "gaa": szn.get("goalsAgainstAvg", 0),
                    "svp": szn.get("savePctg", 0.0),
                }
        count+=1
        print(count)

    with open(output_path, "w") as f:
        json.dump({"gl_stats": gl_stats}, f, indent=2)


def add_caps_to_csv(csv_file, output_file):
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(base_path, csv_file))
    output_path = os.path.abspath(os.path.join(base_path, output_file))

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/117.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    }

    cap_hits = []
    for _, pl in df.iterrows():
        first = pl["FirstName"].lower().replace(" ", "-")
        last = pl["LastName"].lower().replace(" ", "-")
        url = f"https://capwages.com/players/{first}-{last}"

        cap_hit = None
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # find all <span class="hidden sm:inline">
            spans = soup.find_all("span", class_="hidden sm:inline")
            if len(spans) >= 2:
                cap_hit_str = spans[1].text.strip()
                cap_hit = int(cap_hit_str.replace("$", "").replace(",", ""))

        except Exception as e:
            print(f"Failed for {pl['FirstName']} {pl['LastName']}: {e}")

        cap_hits.append(cap_hit)

    df["CapHit"] = cap_hits
    df.to_csv(output_path, index=False)



def build_rosters():
    roster_map = get_rosters("20252026")
    add_ids_to_csv("../data/avail/sk.csv", "../data/gthr/sk.csv", roster_map)
    add_ids_to_csv("../data/avail/gl.csv", "../data/gthr/gl.csv", roster_map)
    add_ids_to_csv("../data/avail/team_sk.csv", "../data/gthr/team_sk.csv", roster_map)
    add_ids_to_csv("../data/avail/team_gl.csv", "../data/gthr/team_gl.csv", roster_map)

def build_stats():
    get_sk_stats("../data/gthr/team_sk.csv","../db/team_sk.json")
    get_gl_stats("../data/gthr/team_gl.csv","../db/team_gl.json")
    get_sk_stats("../data/gthr/sk.csv","../db/sk_stats.json")
    get_gl_stats("../data/gthr/gl.csv","../db/gl_stats.json")

def build_caps():
    add_caps_to_csv("../data/gthr/team_sk.csv", "../data/gthr/team_sk.csv")
    add_caps_to_csv("../data/gthr/team_gl.csv", "../data/gthr/team_gl.csv")
    add_caps_to_csv("../data/gthr/sk.csv", "../data/gthr/sk.csv")
    add_caps_to_csv("../data/gthr/gl.csv", "../data/gthr/gl.csv")


