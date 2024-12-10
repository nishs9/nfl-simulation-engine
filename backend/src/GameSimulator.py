from sqlalchemy import create_engine, text
from proj_secrets import db_username, db_password, db_name
from typing import Tuple
from Team import Team
from GameEngine import GameEngine
from GameModels import PrototypeGameModel, GameModel_V1
from tqdm import tqdm
import pandas as pd

main_db_engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}")
main_db_conn = main_db_engine.connect()

def initialize_teams_for_game_engine(home_team_abbrev: str, away_team_abbrev: str) -> Tuple:
    home_team_query = text(f"select * from sim_engine_team_stats_2024 where team = '{home_team_abbrev}'")
    home_team_results = main_db_conn.execute(home_team_query)
    home_team_df = pd.DataFrame(home_team_results.fetchall(), columns=home_team_results.keys())
    home_team_stats = home_team_df.iloc[0].to_dict()

    away_team_query = text(f"select * from sim_engine_team_stats_2024 where team = '{away_team_abbrev}'")
    away_team_results = main_db_conn.execute(away_team_query)
    away_team_df = pd.DataFrame(away_team_results.fetchall(), columns=away_team_results.keys())
    away_team_stats = away_team_df.iloc[0].to_dict()

    home_team = Team(home_team_abbrev, home_team_stats)
    away_team = Team(away_team_abbrev, away_team_stats)

    return home_team, away_team

def run_single_simulation(home_team_abbrev: str, away_team_abbrev: str, print_debug_info=False, game_model=PrototypeGameModel()):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    game_engine = GameEngine(home_team, away_team, game_model)
    game_summary = game_engine.run_simulation()
    if print_debug_info:
        print("Number of plays:", game_summary["num_plays_in_game"])
        for play in game_summary["play_log"]:
            print(play)
            print("\n")
    
def run_multiple_simulations(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel()):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev,)
    
    home_wins = 0
    i = 0
    print(f"Running {num_simulations} simulations of {home_team.name} vs. {away_team.name}.")
    with tqdm(total=num_simulations) as pbar:
        while i < num_simulations:
            game_engine = GameEngine(home_team, away_team, game_model)
            game_summary = game_engine.run_simulation()
            final_score = game_summary["final_score"]
            if final_score[home_team.name] > final_score[away_team.name]:
                home_wins += 1
            i += 1
            pbar.update(1)
    
    print(f"{home_team.name} wins {round(100 * (home_wins/num_simulations), 2)} percent of the time.")

def run_multiple_simulations_with_statistics(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel()) -> dict:
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    
    home_wins = 0
    i = 0
    print(f"Running {num_simulations} simulations of {home_team.name} vs. {away_team.name}.")

    home_team_stats_df_list = []
    away_team_stats_df_list = []

    with tqdm(total=num_simulations) as pbar:
        while i < num_simulations:
            game_engine = GameEngine(home_team, away_team, game_model)
            game_summary = game_engine.run_simulation()
            final_score = game_summary["final_score"]
            if final_score[home_team.name] > final_score[away_team.name]:
                home_wins += 1
            home_team_stats_df_list.append(pd.DataFrame(game_summary[home_team_abbrev], index=[i]))
            away_team_stats_df_list.append(pd.DataFrame(game_summary[away_team_abbrev], index=[i]))
            i += 1
            pbar.update(1)

    home_team_sim_stats_df = pd.concat(home_team_stats_df_list)
    away_team_sim_stats_df = pd.concat(away_team_stats_df_list)
    combined_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])

    home_team_sim_stats_df.to_csv(f"logs/{home_team_abbrev}_sim_stats.csv", index=True)
    away_team_sim_stats_df.to_csv(f"logs/{away_team_abbrev}_sim_stats.csv", index=True)
    combined_sim_stats_df.to_csv(f"logs/{home_team_abbrev}_{away_team_abbrev}_sim_stats.csv", index=True)

    # Load the data
    home_team_df = pd.read_csv(f"logs/{home_team_abbrev}_sim_stats.csv")
    away_team_df = pd.read_csv(f"logs/{away_team_abbrev}_sim_stats.csv")

    stats_columns = ["team","score","run_rate","pass_rate","pass_cmp_rate",
                    "pass_yards","passing_tds","sacks_allowed","pass_yards_per_play",
                    "rushing_attempts","rushing_yards","rushing_tds","rush_yards_per_play",
                    "total_turnovers","fg_pct"]

    home_team_sim_stats_dict = {
                "team": home_team_df["team"].iloc[0],
                "score": round(home_team_df["score"].mean(), 2),
                "run_rate": round(home_team_df["run_rate"].mean(), 2),
                "pass_rate": round(home_team_df["pass_rate"].mean(), 2),
                "pass_cmp_rate": round(home_team_df["pass_cmp_rate"].mean(), 2),
                "pass_yards": round(home_team_df["pass_yards"].mean(), 2),
                "passing_tds": round(home_team_df["passing_tds"].mean(), 2),
                "sacks_allowed": round(home_team_df["sacks_allowed"].mean(), 2),
                "pass_yards_per_play": round(home_team_df["pass_yards_per_play"].mean(), 2),
                "rushing_attempts": round(home_team_df["rushing_attempts"].mean(), 2),
                "rushing_yards": round(home_team_df["rushing_yards"].mean(), 2),
                "rushing_tds": round(home_team_df["rushing_tds"].mean(), 2),
                "rush_yards_per_play": round(home_team_df["rush_yards_per_play"].mean(), 2),
                "total_turnovers": round(home_team_df["total_turnovers"].mean(), 2),
                "fg_pct": round(home_team_df["fg_pct"].mean(), 2),
            }

    away_team_sim_stats_dict = {
                "team": away_team_df["team"].iloc[0],
                "score": round(away_team_df["score"].mean(), 2),
                "run_rate": round(away_team_df["run_rate"].mean(), 2),
                "pass_rate": round(away_team_df["pass_rate"].mean(), 2),
                "pass_cmp_rate": round(away_team_df["pass_cmp_rate"].mean(), 2),
                "pass_yards": round(away_team_df["pass_yards"].mean(), 2),
                "passing_tds": round(away_team_df["passing_tds"].mean(), 2),
                "sacks_allowed": round(away_team_df["sacks_allowed"].mean(), 2),
                "pass_yards_per_play": round(away_team_df["pass_yards_per_play"].mean(), 2),
                "rushing_attempts": round(away_team_df["rushing_attempts"].mean(), 2),
                "rushing_yards": round(away_team_df["rushing_yards"].mean(), 2),
                "rushing_tds": round(away_team_df["rushing_tds"].mean(), 2),
                "rush_yards_per_play": round(away_team_df["rush_yards_per_play"].mean(), 2),
                "total_turnovers": round(away_team_df["total_turnovers"].mean(), 2),
                "fg_pct": round(away_team_df["fg_pct"].mean(), 2),
            }

    home_team_sim_stats_df = pd.DataFrame(home_team_sim_stats_dict, index=[0], columns=stats_columns)
    away_team_sim_stats_df = pd.DataFrame(away_team_sim_stats_dict, index=[0], columns=stats_columns)

    stats_csv_path = "logs/total_sim_stats.csv"

    total_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])
    total_sim_stats_df.to_csv(stats_csv_path, index=False)
    total_sim_stats_dict = total_sim_stats_df.reset_index().to_dict(orient="records")
    #print(total_sim_stats_dict)

    home_score = home_team_sim_stats_dict["score"]
    away_score = away_team_sim_stats_dict["score"]
    average_score_diff = home_score - away_score
    result_string = f"{home_team.name} wins {round(100 * (home_wins/num_simulations), 2)} percent of the time."
    result_string += f"\nAverage score difference: {average_score_diff}"
    result_string += f"\nAverage total score: {home_score+away_score}"
    print(result_string)

    return {
        "result_string": result_string,
        "total_sim_stats": total_sim_stats_dict
    }
    
if __name__ == "__main__":
    home_team = "BAL"
    away_team = "BUF"
    #run_single_simulation(home_team, away_team, print_debug_info=False)
    #run_multiple_simulations(home_team, away_team, 750)
    run_multiple_simulations_with_statistics(home_team, away_team, 100, GameModel_V1())