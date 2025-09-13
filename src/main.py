import sys
from preproc import *
from projections import *
from lp import *
import os

##===-- INITIAL CONFIG --=====##
cap_space=950,834
need_forwards=1
need_defensemen=2
need_goalies=0


def print_fantadraft_banner(style="big"):
    import shutil
    cols = shutil.get_terminal_size((80, 20)).columns

    BANNERS = {
        "big": r"""
░▒▓████████▓▒░▒▓██████▓▒░░▒▓███████▓▒░▒▓████████▓▒░▒▓██████▓▒░░▒▓███████▓▒░░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓████████▓▒░▒▓████████▓▒░ 
░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░  ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░▒▓██████▓▒░    ░▒▓█▓▒░     
░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░  ░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░     
                                                                                                                                 
                                                                                                                                 
""",
        "narrow": r"""
FANTADRAFT
"""
    }

    meta = "Author: Liam K"
    title = "=== FANTADRAFT ==="

    out = BANNERS["big" if style=="big" else "narrow"]
    for line in out.splitlines():
        if line.strip() == "":
            print()
            continue
        print(line.center(cols))

    print()
    print(title.center(cols))
    print(meta.center(cols))
    print()

def print_opt():
    print("\nSelect an option:")
    print("1 - Build Rosters")
    print("2 - Build Stats")
    print("3 - Build Caps")

    print("f - Find played with Lastname,Firstname")

    print("p - Calculate all projections")
    print("o - Get next draft pick")

    print("rp - Remove available player from pool (someone else has drafted them) and put in drafted")
    print("ap - Add player back to available pool from drafted")
    print("dp - Draft player to team")
    print("du - Undo draft player to team and put back in available roster")

    print("ts - Show team projected stats as of draft pick")

    print("E - Exit\n")

def main():
    print_fantadraft_banner(style="narrow")
    while True:
        print_opt()
        arg = input("Enter option (E to exit): ").strip()
        match arg:
            case "1":
                build_rosters()
            case "2":
                build_stats()
            case "3":
                build_caps()

            case "f":
                pl_input = input("Enter Lastname,Firstname: ").strip()  # e.g., "McDavid,Connor"
                try:
                    last, first = [x.strip() for x in pl_input.split(",")]
                except ValueError:
                    print("Invalid format. Use Lastname,Firstname")
                    break

                base_path = os.path.dirname(os.path.abspath(__file__))
                csv_files = [
                    os.path.join(base_path, "proj_team_sk.csv"),
                    os.path.join(base_path, "proj_team_gl.csv"),
                    os.path.join(base_path, "proj_all_sk.csv"),
                    os.path.join(base_path, "proj_all_gl.csv")
                ]

                # Load and combine all CSVs
                df_all = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True, sort=False)

                # Normalize column names
                df_all.columns = [c.strip() for c in df_all.columns]

                # Filter by LastName and FirstName
                found = df_all[(df_all["LastName"].str.strip().str.lower() == last.lower()) &
                            (df_all["FirstName"].str.strip().str.lower() == first.lower())]

                if not found.empty:
                    print(found)
                else:
                    print(f"No player found matching: {pl_input}")
            
            case "p":
                build_projections()
            case "o":
                base_path = os.path.dirname(os.path.abspath(__file__))
                team_sk_csv = os.path.join(base_path, "proj_team_sk.csv")
                team_gl_csv = os.path.join(base_path, "proj_team_gl.csv")
                avail_sk_csv = os.path.join(base_path, "proj_all_sk.csv")
                avail_gl_csv = os.path.join(base_path, "proj_all_gl.csv")

                chosen_set, next_pick = pick_optimal_set(
                    team_sk_csv,
                    team_gl_csv,
                    avail_sk_csv,
                    avail_gl_csv,
                    cap_remaining=cap_space,
                    need_forwards=need_forwards,
                    need_defensemen=need_defensemen,
                    need_goalies=need_goalies,
                    verbose=True
                )

                print("\n=== Optimal Full Set ===")
                print(chosen_set[["ID", "LastName", "FirstName", "Pos", "CapHit", "score_raw"]])
                print("\n=== Next Pick ===")
                print(next_pick[["ID", "LastName", "FirstName", "Pos", "CapHit", "score_raw"]] if next_pick is not None else "None")

            case "rp":
                pid = input("Enter player ID to remove from pool: ").strip()
                rp(int(pid))
            case "ap":
                pid = input("Enter player ID to add back to pool: ").strip()
                ap(int(pid))
            case "dp":
                pid = input("Enter player ID to draft to team: ").strip()
                dp(int(pid))
            case "du":
                pid = input("Enter player ID to undo draft: ").strip()
                du(int(pid))
            
            case "E" | "e":
                print("Exiting...")
                break
            case _:
                print("Invalid option, try again.")

import os
import pandas as pd

def move_player(player_id, src_file, dst_file):
    """Move a player row by ID from src_file to dst_file."""
    base_path = os.path.dirname(os.path.abspath(__file__))  # directory containing main.py
    src_path = os.path.join(base_path, src_file)
    dst_path = os.path.join(base_path, dst_file)

    # Load source and destination files
    df_src = pd.read_csv(src_path)
    if os.path.exists(dst_path):
        df_dst = pd.read_csv(dst_path)
    else:
        df_dst = pd.DataFrame()

    # Check if player exists in source
    if player_id not in df_src["ID"].values:
        print(f"Player {player_id} not found in {src_file}.")
        return

    # Extract row and remove from source
    player_row = df_src[df_src["ID"] == player_id]
    df_src = df_src[df_src["ID"] != player_id]

    # Append to destination, safe against empty df
    if df_dst.empty:
        df_dst = player_row.copy()
    else:
        df_dst = pd.concat([df_dst, player_row], ignore_index=True)

    # Save both files back
    df_src.to_csv(src_path, index=False)
    df_dst.to_csv(dst_path, index=False)

    print(f"Moved player {player_id} from {src_file} to {dst_file}.")

def rp(player_id):
    if is_goalie(player_id, "proj_all_gl.csv"):
        move_player(player_id, "proj_all_gl.csv", "drafted_gl.csv")
    else:
        move_player(player_id, "proj_all_sk.csv", "drafted_sk.csv")

def ap(player_id):
    if is_goalie(player_id, "drafted_gl.csv"):
        move_player(player_id, "drafted_gl.csv", "proj_all_gl.csv")
    else:
        move_player(player_id, "drafted_sk.csv", "proj_all_sk.csv")

def dp(player_id):
    global cap_space, need_forwards, need_defensemen, need_goalies

    if is_goalie(player_id, "proj_all_gl.csv"):
        # Load row before moving
        base_path = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_path, "proj_all_gl.csv"))
        row = df[df["ID"] == player_id].iloc[0]

        move_player(player_id, "proj_all_gl.csv", "proj_team_gl.csv")

        cap_space -= int(row["CapHit"])
        need_goalies = max(0, need_goalies - 1)

    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_path, "proj_all_sk.csv"))
        row = df[df["ID"] == player_id].iloc[0]

        move_player(player_id, "proj_all_sk.csv", "proj_team_sk.csv")

        cap_space -= int(row["CapHit"])
        pos = row["Pos"].upper()
        if pos == "D":
            need_defensemen = max(0, need_defensemen - 1)
        else:
            need_forwards = max(0, need_forwards - 1)

    print(f"Updated cap_space={cap_space}, need_f={need_forwards}, need_d={need_defensemen}, need_g={need_goalies}")


def du(player_id):
    global cap_space, need_forwards, need_defensemen, need_goalies

    if is_goalie(player_id, "proj_team_gl.csv"):
        base_path = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_path, "proj_team_gl.csv"))
        row = df[df["ID"] == player_id].iloc[0]

        move_player(player_id, "proj_team_gl.csv", "proj_all_gl.csv")

        cap_space += int(row["CapHit"])
        need_goalies += 1

    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(base_path, "proj_team_sk.csv"))
        row = df[df["ID"] == player_id].iloc[0]

        move_player(player_id, "proj_team_sk.csv", "proj_all_sk.csv")

        cap_space += int(row["CapHit"])
        pos = row["Pos"].upper()
        if pos == "D":
            need_defensemen += 1
        else:
            need_forwards += 1

    print(f"Updated cap_space={cap_space}, need_f={need_forwards}, need_d={need_defensemen}, need_g={need_goalies}")

def is_goalie(player_id, csv_file):
    base_path = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_path, csv_file))
    row = df[df['ID'] == player_id]
    if row.empty:
        return False
    return row.iloc[0]['Pos'].upper() == 'G'


if __name__ == "__main__":
    main()