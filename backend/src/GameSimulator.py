from sqlalchemy import create_engine, text, Connection
from proj_secrets import db_username, db_password, db_name
from typing import List, Dict, Tuple, Any
from Team import Team
from GameEngine import GameEngine
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

def run_single_simulation(home_team_abbrev: str, away_team_abbrev: str, print_debug_info=False):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    game_engine = GameEngine(home_team, away_team)
    game_summary = game_engine.run_simulation()
    if print_debug_info:
        print("Number of plays:", game_summary["num_plays_in_game"])
        for play in game_summary["play_log"]:
            print(play)
            print("\n")
    
def run_multiple_simulations(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    
    home_wins = 0
    i = 0
    print(f"Running {num_simulations} simulations of {home_team.name} vs. {away_team.name}.")
    with tqdm(total=num_simulations) as pbar:
        while i < num_simulations:
            game_engine = GameEngine(home_team, away_team)
            game_summary = game_engine.run_simulation()
            final_score = game_summary["final_score"]
            if final_score[home_team.name] > final_score[away_team.name]:
                home_wins += 1
            i += 1
            pbar.update(1)
    
    print(f"{home_team.name} wins {round(100 * (home_wins/num_simulations), 2)} percent of the time.")

# TODO: Add the summary statistics functionality to this function
def run_multiple_simulations_with_statistics(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    
    home_wins = 0
    i = 0
    while i < num_simulations:
        game_engine = GameEngine(home_team, away_team)
        game_summary = game_engine.run_simulation()
        print(game_summary["final_score"])
        print("Number of plays:", game_summary["num_plays_in_game"])
        final_score = game_summary["final_score"]
        if final_score[home_team.name] > final_score[away_team.name]:
            home_wins += 1
        i += 1
    
    print(f"{home_team.name} wins {round(100 * (home_wins/num_simulations), 2)} percent of the time.")
    
if __name__ == "__main__":
    home_team = "ATL"
    away_team = "LAC"
    #run_single_simulation(home_team, away_team, print_debug_info=False)
    run_multiple_simulations(home_team, away_team, 750)