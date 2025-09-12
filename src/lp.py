# next_pick_optimizer.py
import pandas as pd
import numpy as np
import os
import pulp

def pick_optimal_set(team_sk_csv, team_gl_csv, avail_sk_csv, avail_gl_csv,
                     cap_remaining, need_forwards, need_defensemen, need_goalies,
                     verbose=False):
    # Load available players
    df_sk = pd.read_csv(avail_sk_csv)
    df_gl = pd.read_csv(avail_gl_csv)
    df = pd.concat([df_sk, df_gl], ignore_index=True)
    df["PosGroup"] = df["Pos"].apply(map_position)

    # Clean up CapHit
    df["CapHit"] = pd.to_numeric(df["CapHit"], errors="coerce")
    df = df.dropna(subset=["CapHit"])
    df = df[df["CapHit"] < float("inf")]

    # Normalize stats into a single score (roto-style equal weighting)
    stat_cols_sk = ["proj_goals", "proj_assists", "proj_points", "proj_ppg", "proj_ppa", "proj_sog"]
    stat_cols_gl = ["proj_w", "proj_gaa_flipped", "proj_svp"]

    # Compute z-scores per stat
    for col in stat_cols_sk + stat_cols_gl:
        if col in df:
            if df[col].std() > 0:
                df[f"z_{col}"] = (df[col] - df[col].mean()) / df[col].std()
            else:
                df[f"z_{col}"] = 0

    # Combined score = average of available z-scores
    z_cols = [c for c in df.columns if c.startswith("z_")]
    df["score_raw"] = df[z_cols].mean(axis=1)

    # LP model
    prob = pulp.LpProblem("FantasyDraft", pulp.LpMaximize)

    # Decision vars: 1 if player is picked
    choices = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in df.index}

    # Objective: maximize total score
    prob += pulp.lpSum(df.loc[i, "score_raw"] * choices[i] for i in df.index)

    # Constraints
    prob += pulp.lpSum(df.loc[i, "CapHit"] * choices[i] for i in df.index) <= cap_remaining
    prob += pulp.lpSum((df.loc[i, "PosGroup"] == "F") * choices[i] for i in df.index) >= need_forwards
    prob += pulp.lpSum((df.loc[i, "PosGroup"] == "D") * choices[i] for i in df.index) >= need_defensemen
    prob += pulp.lpSum((df.loc[i, "PosGroup"] == "G") * choices[i] for i in df.index) >= need_goalies

    total_needed = need_forwards + need_defensemen + need_goalies
    prob += pulp.lpSum(choices[i] for i in df.index) == total_needed

    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if verbose:
        print("LP status:", pulp.LpStatus[prob.status])
        print("Objective value:", pulp.value(prob.objective))

    # Extract chosen players
    chosen = df.loc[[i for i in df.index if choices[i].value() == 1]].copy()
    chosen = chosen.sort_values("score_raw", ascending=False)

    # Next pick = best from chosen
    next_pick = chosen.iloc[0] if not chosen.empty else None

    return chosen, next_pick

def map_position(pos):
    if pos in ["C", "L", "R"]:
        return "F"
    return pos
