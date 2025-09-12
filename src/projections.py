import os
import json
import pandas as pd
import numpy as np

def project_skaters(sk_stats_json, expected_gp=82, seasons_to_use=None, weights=None):
    projected = []
    for ID, seasons in sk_stats_json.items():
        sorted_seasons = sorted(seasons.items(), key=lambda x: x[0], reverse=True)
        if seasons_to_use is None:
            use_seasons = sorted_seasons
        else:
            use_seasons = sorted_seasons[:seasons_to_use]

        if weights is None:
            weights = np.arange(len(use_seasons), 0, -1)
        weights = weights[:len(use_seasons)]
        weights = weights / weights.sum()

        cats = ["goals", "assists", "points", "ppg", "ppa", "sog"]
        per_game = {c: 0.0 for c in cats}

        for i, (season, stats) in enumerate(use_seasons):
            try:
                gp = max(stats.get("gp", 1), 1)
                for c in cats:
                    val = stats.get(c, 0) or 0
                    per_game[c] += (val / gp) * weights[i]
            except Exception as e:
                print(f"[WARN] Skipping player {ID}, season {season}: {e}")

        if isinstance(expected_gp, dict):
            gp_proj = expected_gp.get(ID, use_seasons[0][1].get("gp", 82))
        else:
            gp_proj = expected_gp

        proj_totals = {
            "ID": int(ID),
            "proj_gp": int(round(gp_proj))
        }
        for c in cats:
            proj_totals[f"proj_{c}"] = int(round(per_game[c] * gp_proj))

        projected.append(proj_totals)

    return pd.DataFrame(projected)


def project_goalies(gl_stats_json, expected_gp=55, seasons_to_use=None, weights=None):
    projected = []
    for ID, seasons in gl_stats_json.items():
        sorted_seasons = sorted(seasons.items(), key=lambda x: x[0], reverse=True)
        if seasons_to_use is None:
            use_seasons = sorted_seasons
        else:
            use_seasons = sorted_seasons[:seasons_to_use]

        if weights is None:
            weights = np.arange(len(use_seasons), 0, -1)
        weights = weights[:len(use_seasons)]
        weights = weights / weights.sum()

        per_game = {"w": 0.0, "gaa": 0.0, "svp": 0.0}

        for i, (season, stats) in enumerate(use_seasons):
            try:
                gp = max(stats.get("gp", 1), 1)
                per_game["w"] += ((stats.get("w", 0) or 0) / gp) * weights[i]
                per_game["gaa"] += (stats.get("gaa", 0) or 0) * weights[i]
                per_game["svp"] += (stats.get("svp", 0) or 0) * weights[i]
            except Exception as e:
                print(f"[WARN] Skipping goalie {ID}, season {season}: {e}")

        if isinstance(expected_gp, dict):
            gp_proj = expected_gp.get(ID, use_seasons[0][1].get("gp", 55))
        else:
            gp_proj = expected_gp

        proj_totals = {
            "ID": int(ID),
            "proj_gp": int(round(gp_proj)),
            "proj_w": int(round(per_game["w"] * gp_proj)),
            "proj_gaa": round(per_game["gaa"], 2),
            "proj_svp": round(per_game["svp"], 3)
        }
        projected.append(proj_totals)

    return pd.DataFrame(projected)


def project_do(type, stats_json, info_csv, output_csv):
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.abspath(os.path.join(base_path, stats_json))
    info_path = os.path.abspath(os.path.join(base_path, info_csv))
    output_path = os.path.abspath(os.path.join(base_path, output_csv))

    with open(json_path, "r") as f:
        data = json.load(f)

    if type == "S":
        df_proj = project_skaters(data["sk_stats"], expected_gp=82, seasons_to_use=3)
    elif type == "G":
        df_proj = project_goalies(data["gl_stats"], expected_gp=55, seasons_to_use=3)
    else:
        raise ValueError(f"Unknown type: {type}")

    # load info CSV (unmodified)
    df_info = pd.read_csv(info_path)

    # merge projections into new DataFrame
    df_merged = df_info.merge(df_proj, on="ID", how="left")

    # save combined (info + projections)
    df_merged.to_csv(output_path, index=False)


def build_projections():
    project_do("S", "../db/team_sk.json", "../data/gthr/team_sk.csv", "../db/proj/proj_team_sk.csv")
    project_do("G", "../db/team_gl.json", "../data/gthr/team_gl.csv", "../db/proj/proj_team_gl.csv")
    project_do("S", "../db/sk_stats.json", "../data/gthr/sk.csv", "../db/proj/proj_all_sk.csv")
    project_do("G", "../db/gl_stats.json", "../data/gthr/gl.csv", "../db/proj/proj_all_gl.csv")
