from sqlalchemy import create_engine, text
from proj_secrets import db_username, db_password, db_name
from typing import Tuple
from Team import Team
from GameEngine import GameEngine
from GameModels import PrototypeGameModel, GameModel_V1, GameModel_V1a, GameModel_V1b
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from time import time
import random
import pandas as pd
import math
import os
import play_log_util as plu
import warnings
import csv

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

sim_engine_query = text("select * from sim_engine_team_stats_2024 where team = :team")

def establish_db_connection():
    main_db_engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}")
    main_db_conn = main_db_engine.connect()
    return main_db_conn

def initialize_teams_for_game_engine(home_team_abbrev: str, away_team_abbrev: str) -> Tuple:
    main_db_conn = establish_db_connection()
    home_team_results = main_db_conn.execute(sim_engine_query, {"team": home_team_abbrev})
    home_team_df = pd.DataFrame(home_team_results.fetchall(), columns=home_team_results.keys())
    home_team_stats = home_team_df.iloc[0].to_dict()

    away_team_results = main_db_conn.execute(sim_engine_query, {"team": away_team_abbrev})
    away_team_df = pd.DataFrame(away_team_results.fetchall(), columns=away_team_results.keys())
    away_team_stats = away_team_df.iloc[0].to_dict()

    home_team = Team(home_team_abbrev, home_team_stats)
    away_team = Team(away_team_abbrev, away_team_stats)

    main_db_conn.close()

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

def generate_simulation_stats_summary(home_team, away_team, home_wins, num_simulations, home_team_stats_df_list, away_team_stats_df_list):
    home_team_sim_stats_df = pd.concat(home_team_stats_df_list)
    away_team_sim_stats_df = pd.concat(away_team_stats_df_list)
    combined_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])
    
    home_team_sim_stats_df.to_csv(f"logs/{home_team.name}_sim_stats.csv", index=True)
    away_team_sim_stats_df.to_csv(f"logs/{away_team.name}_sim_stats.csv", index=True)
    combined_sim_stats_df.to_csv(f"logs/{home_team.name}_{away_team.name}_sim_stats.csv", index=True)

    # Load the data
    home_team_df = pd.read_csv(f"logs/{home_team.name}_sim_stats.csv")
    away_team_df = pd.read_csv(f"logs/{away_team.name}_sim_stats.csv")

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
    home_win_pct = round(100 * (home_wins/num_simulations), 2)
    #result_string = f"{home_team.name} wins {home_win_pct} percent of the time."
    result_string = f"Average score difference: {round(average_score_diff, 2)}"
    result_string += f"\nAverage total score: {round(home_score+away_score, 2)}"
    print(result_string)

    return {
        "result_string": result_string,
        "home_win_pct": home_win_pct,
        "total_sim_stats": total_sim_stats_dict,
        "average_score_diff": average_score_diff
    }


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

    return generate_simulation_stats_summary(home_team, away_team, home_wins, num_simulations, home_team_stats_df_list, away_team_stats_df_list)

def run_simulation_chunk(home_team: object, away_team: object, game_model: object, start_index: int, num_simulations_for_chunk: int) -> list:
    chunk_results = []
    for i in range(num_simulations_for_chunk):
        game_engine = GameEngine(home_team, away_team, game_model)
        game_summary = game_engine.run_simulation()
        chunk_results.append((start_index + i, game_summary))
    return chunk_results

def run_multiple_simulations_multi_threaded(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel(), num_workers=None):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    print(f"Running {num_simulations} simulations of {home_team.name} vs. {away_team.name}.")

    number_of_workers = min(num_simulations, os.cpu_count() // 2)
    if num_workers:
        number_of_workers = num_workers
    chunk_size = math.ceil(num_simulations / number_of_workers)

    print(f"Using a chunk size of {chunk_size} and {number_of_workers} workers...\n")

    futures = []
    with ProcessPoolExecutor(max_workers=number_of_workers) as executor:
        start_index = 0
        for _ in range(number_of_workers):
            sim_count_for_curr_chunk = min(chunk_size, num_simulations - start_index)
            if sim_count_for_curr_chunk <= 0:
                break
            futures.append(executor.submit(
                run_simulation_chunk,
                home_team,
                away_team,
                game_model,
                start_index,
                sim_count_for_curr_chunk
            ))
            start_index += sim_count_for_curr_chunk
        
        all_results = []
        print(f"Running {num_simulations} simulations over {number_of_workers} chunks...")
        with tqdm(total=number_of_workers) as pbar:
            for future in as_completed(futures):
                chunk_results = future.result()
                all_results.extend(chunk_results)
                pbar.update(1)

    home_wins = 0
    home_team_stats_df_list = []
    away_team_stats_df_list = []
    
    # Randomly choose a game to be featured in detail on the frontend
    featured_game_index = random.randint(0, len(all_results) - 1)
    featured_play_log = None

    for i, game_summary in all_results:
        final_score = game_summary["final_score"]
        if i == featured_game_index:
            featured_play_log = pd.DataFrame(game_summary["play_log"])
            featured_play_log["game_time_elapsed"] = (featured_play_log["game_seconds_remaining"] - 3600) * -1
            featured_play_log.to_csv("logs/featured_game.csv", index=True)
        if final_score[home_team.name] > final_score[away_team.name]:
            home_wins += 1
        home_team_stats_df_list.append(pd.DataFrame(game_summary[home_team_abbrev], index=[i]))
        away_team_stats_df_list.append(pd.DataFrame(game_summary[away_team_abbrev], index=[i]))

    sim_result = generate_simulation_stats_summary(home_team, away_team, home_wins, num_simulations, home_team_stats_df_list, away_team_stats_df_list)
    sim_result["featured_game_home_pass_data"] = plu.generate_team_passing_stats_summary(home_team_abbrev, featured_play_log)
    sim_result["featured_game_away_pass_data"] = plu.generate_team_passing_stats_summary(away_team_abbrev, featured_play_log)
    sim_result["featured_game_home_rush_data"] = plu.generate_team_rushing_stats_summary(home_team_abbrev, featured_play_log)
    sim_result["featured_game_away_rush_data"] = plu.generate_team_rushing_stats_summary(away_team_abbrev, featured_play_log)
    sim_result["featured_game_home_scoring_data"] = plu.generate_team_scoring_summary(home_team_abbrev, featured_play_log)
    sim_result["featured_game_away_scoring_data"] = plu.generate_team_scoring_summary(away_team_abbrev, featured_play_log)
    return sim_result

def run_weekly_predictions(num_simulations=3000, num_workers=None):
    prediction_run_start = time()
    matchups = read_matchup_column("input.txt")
    game_models = [PrototypeGameModel(), GameModel_V1(), GameModel_V1a(), GameModel_V1b()]
    prediction_results = {key: [] for key in matchups}
    for game_model in game_models:
        for matchup in matchups:
            home_team = matchup[0]
            away_team = matchup[1]
            print(f"Running simulations for {home_team} vs. {away_team} with {game_model.get_model_code()}")
            result = run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, GameModel_V1b(), num_workers=num_workers)
            prediction_results[matchup].append(parse_simulation_result(result["average_score_diff"], home_team, away_team))

    with open("weekly_predictions.csv", "w") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["Matchup", "Prototype", "V1", "V1a", "V1b"])
        writer.writeheader()
        for matchup in matchups:
            writer.writerow({
                "Matchup": f"{matchup[0]} v {matchup[1]}",
                "V1b": prediction_results[matchup][3],
                "V1a": prediction_results[matchup][2],
                "V1": prediction_results[matchup][1],
                "Prototype": prediction_results[matchup][0]
            })
    prediction_run_end = time()
    prediction_run_time = prediction_run_end - prediction_run_start

    print("Weekly predictions have been written to 'weekly_predictions.csv'.")
    print(f"Predictions took {prediction_run_time} seconds to generate with {num_simulations} simulations per matchup for each model.")

def parse_simulation_result(score_diff: float, home_team: str, away_team: str) -> str:
    if score_diff > 0:
        return f"{home_team} wins by {round(score_diff, 2)}"
    elif score_diff < 0:
        return f"{away_team} wins by {round(score_diff * -1, 2)}"
    else:
        return f"{home_team} and {away_team} tie"

def read_matchup_column(file_path):
    matchups = []
    try:
        with open(file_path, mode='r') as input_file:
            for line in input_file:
                line = line.strip()
                teams = line.split(" v ") 
                if len(teams) != 2:
                    raise ValueError("Invalid matchup format. Must be 'TEAM_A v TEAM_B'.")
                matchups.append((teams[0], teams[1])) 
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return matchups

if __name__ == "__main__":
    # away_team = "PIT"
    # home_team = "KC"
    # num_simulations = 3000
    #run_single_simulation(home_team, away_team, print_debug_info=False)
    #run_multiple_simulations(home_team, away_team, 750)
    #run_multiple_simulations_with_statistics(home_team, away_team, 350, GameModel_V1())
    # proto_start = time()
    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, PrototypeGameModel())
    # proto_end = time()
    # proto_time = proto_end - proto_start
    # v1_start = time()
    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, GameModel_V1())
    # v1_end = time()
    # v1_time = v1_end - v1_start
    # v1a_start = time()
    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, GameModel_V1a())
    # v1a_end = time()
    # v1a_time = v1a_end - v1a_start
    # v1b_start = time()
    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, GameModel_V1b(), num_workers=12)
    # v1b_end = time()
    # v1b_time = v1b_end - v1b_start
    # print(f"Game Model Prototype Execution Time: {proto_time}")
    # print(f"Game Model v1 Execution Time: {v1_time}")
    # print(f"Game Model v1a Execution Time: {v1a_time}")
    # print(f"Game Model v1b Execution Time: {v1b_time}")
    run_weekly_predictions(num_simulations=3250)