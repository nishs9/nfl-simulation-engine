from sqlalchemy import create_engine, text, Connection
from proj_secrets import db_username, db_password, db_name, alt_db_name
from typing import List, Dict, Tuple, Any
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def setup_db_connections() -> Tuple[object, object]:
    # Setup main and alternate db connections for data processing
    main_db_engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}', echo=True)
    main_db_conn = main_db_engine.connect()

    alt_db_engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@localhost/{alt_db_name}', echo=True)
    alt_db_conn = alt_db_engine.connect()

    return (main_db_conn, alt_db_conn)

def setup_sim_engine_player_stats_table(raw_player_stats_df: pd.DataFrame, main_db_conn: Connection) -> None:
    player_stats_columns = ["player_id", "player_display_name", "position", "passing_yards", "passing_tds", "interceptions",
                            "sacks", "sack_fumbles_lost", "rushing_yards", "rushing_tds", "rushing_fumbles_lost", "receiving_yards", 
                            "receiving_tds", "receiving_fumbles_lost"]
    player_stats_df = raw_player_stats_df[player_stats_columns]
    player_stats_df.to_sql(f'sim_engine_player_stats_2024', con=main_db_conn, if_exists='replace', index=True)

def determine_play_result(row) -> None:
    special_play_type = ["qb_kneel", "qb_spike", "punt", "kickoff"]

    success__yardarges = { 1.0: 0.4, 2.0: 0.6, 3.0: 1.0, 4.0: 1.0}

    if (row["play_type"] in special_play_type):
        return "NA"

    if (row["touchdown"] == 1):
        return "Touchdown"
    
    if (row["play_type"] == "extra_point"):
        if (row["extra_point_result"] == "good"):
            return "Success"
        else:
            return "Failure"
    
    if (row["field_goal_attempt"] == 1):
        if (row["field_goal_result"] == "made"):
            return "Field Goal"
        else:
            return "Failure"
        
    if (row["interception"] == 1 or row["fumble_lost"] == 1):
        return "Turnover"
    
    curr_down = row["down"]
    curr_yards_to_go = row["ydstogo"]
    yards_gained = row['ydsnet']

    if (pd.isna(curr_down)):
        return "NA"

    success_yards_ratio = success__yardarges[curr_down]
    if (yards_gained >= success_yards_ratio * curr_yards_to_go):
        return "Success"
    else:
        return "Failure" 

def setup_sim_engine_pbp_table(raw_pbp_df: pd.DataFrame, main_db_conn: Connection) -> None:
    pbp_columns = ["game_id", "play_id", "posteam", "defteam", "home_team", "away_team", "qtr", "down", "ydstogo",
                   "yardline_100", "ydsnet", "yards_gained", "play_type", "quarter_seconds_remaining", 
                   "game_seconds_remaining", "play_result"]
    raw_pbp_df["play_result"] = raw_pbp_df.apply(determine_play_result, axis=1)
    pbp_df = raw_pbp_df[pbp_columns]
    pbp_df.to_sql(f'sim_engine_pbp_2024', con=main_db_conn, if_exists='replace', index=True)

def initialize_team_stats_dict(team_abbrev_list: List[str]) -> Dict[str, List[any]]:
    team_stats_dict = {}
    team_stats_dict["team"] = team_abbrev_list
    team_stats_dict["games_played"] = None
    team_stats_dict["pass_completion_rate"] = None
    team_stats_dict["rush_yards_per_carry"] = None
    team_stats_dict["scoring_efficiency"] = None
    team_stats_dict["turnover_rate"] = None
    team_stats_dict["redzone_efficiency"] = None
    return team_stats_dict

def get_completion_pct(team: str, team_df: pd.DataFrame) -> float:
    pass_comp_pct_df = team_df[(team_df["posteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_attempts = pass_comp_pct_df["pass_attempt"].sum()
    total_completions = pass_comp_pct_df["complete_pass"].sum()
    completion_pct = total_completions / total_attempts
    completion_pct = round(completion_pct * 100, 2)
    return completion_pct

def get_rush_yards_per_carry(team: str, team_df: pd.DataFrame) -> float:
    rush_yds_per_carry_df = team_df[(team_df["posteam"] == team) & (team_df["rush_attempt"] == 1)]
    total_rush_attempts = rush_yds_per_carry_df["rush_attempt"].sum()
    total_rush_yds = rush_yds_per_carry_df["rushing_yards"].sum()
    yards_per_carry = total_rush_yds / total_rush_attempts
    yards_per_carry = round(yards_per_carry, 2)
    return yards_per_carry

def get_scoring_efficiency(team: str, team_df: pd.DataFrame) -> float:
    num_drives = team_df["game_drive_composite_id"].unique().size
    home_scoring_df = team_df[(team_df["home_team"] == team)]
    home_scoring_df = home_scoring_df.drop_duplicates(subset="game_id")
    total_home_scoring = home_scoring_df["home_score"].sum()

    away_scoring_df = team_df[(team_df["away_team"] == team)]
    away_scoring_df = away_scoring_df.drop_duplicates(subset="game_id")
    total_away_scoring = away_scoring_df["away_score"].sum()

    total_scoring = total_home_scoring + total_away_scoring
    total_scoring_per_drive = total_scoring / num_drives
    total_scoring_per_drive = round(total_scoring_per_drive, 2)
    return total_scoring_per_drive

def get_turnover_rate(team: str, team_df: pd.DataFrame) -> float:
    num_drives = team_df["game_drive_composite_id"].unique().size
    turnover_df = team_df[(team_df["posteam"] == team) & ((team_df["interception"] == 1) | (team_df["fumble_lost"] == 1))]
    total_turnovers = turnover_df["interception"].sum() + turnover_df["fumble_lost"].sum()
    turnovers_per_drive = total_turnovers / num_drives
    turnovers_per_drive = round(turnovers_per_drive, 2)
    return turnovers_per_drive

def get_redzone_efficiency(team: str, team_df: pd.DataFrame) -> float:
    team_df["redzone_drive_composite_id"] = team_df["game_id"] + "_" + team_df["drive"].astype(str) + "_" + team_df["drive_inside20"].astype(str)
    redzone_df = team_df[(team_df["posteam"] == team) & (team_df["drive_inside20"] == 1)]
    redzone_df = redzone_df.drop_duplicates(subset="redzone_drive_composite_id")
    redzone_drives = redzone_df["drive_inside20"].sum()
    redzone_tds = redzone_df[redzone_df["fixed_drive_result"]=="Touchdown"]["fixed_drive_result"].count()
    redzone_efficiency = redzone_tds / redzone_drives
    redzone_efficiency = round(redzone_efficiency * 100, 2)
    return redzone_efficiency

def setup_sim_engine_team_stats_table(raw_pbp_df: pd.DataFrame, main_db_conn: Connection) -> None:
    team_abbrev_list = sorted(raw_pbp_df["home_team"].unique())
    team_stats_dict = initialize_team_stats_dict(team_abbrev_list)
    games_played_list = []
    pass_completion_rate_list = []
    rush_yards_per_carry_list = []
    scoring_efficiency_list = []
    turnover_rate_list = []
    redzone_efficiency_list = []
    for team in team_abbrev_list:
        curr_team_df = raw_pbp_df[(raw_pbp_df["home_team"] == team) | (raw_pbp_df["away_team"] == team)]
        curr_team_df["game_drive_composite_id"] = curr_team_df["game_id"] + "_" + curr_team_df["drive"].astype(str)
        games_played_list.append(curr_team_df["game_id"].unique().size)
        pass_completion_rate_list.append(get_completion_pct(team, curr_team_df))
        rush_yards_per_carry_list.append(get_rush_yards_per_carry(team, curr_team_df))
        scoring_efficiency_list.append(get_scoring_efficiency(team, curr_team_df))
        turnover_rate_list.append(get_turnover_rate(team, curr_team_df))
        redzone_efficiency_list.append(get_redzone_efficiency(team, curr_team_df))

    team_stats_dict["games_played"] = games_played_list
    team_stats_dict["pass_completion_rate"] = pass_completion_rate_list
    team_stats_dict["rush_yards_per_carry"] = rush_yards_per_carry_list
    team_stats_dict["scoring_efficiency"] = scoring_efficiency_list
    team_stats_dict["turnover_rate"] = turnover_rate_list
    team_stats_dict["redzone_efficiency"] = redzone_efficiency_list

    team_stats_df = pd.DataFrame(team_stats_dict)
    team_stats_df.to_sql(f'sim_engine_team_stats_2024', con=main_db_conn, if_exists='replace', index=True)


if __name__ == '__main__':
    # Initialize database connections
    main_db_conn, alt_db_conn = setup_db_connections()

    # Load raw data from raw CSV and create PBP and team stats tables in sim engine DB
    raw_pbp_df = pd.read_csv("datasets/2024_NFL.csv")
    setup_sim_engine_pbp_table(raw_pbp_df, main_db_conn)
    setup_sim_engine_team_stats_table(raw_pbp_df, main_db_conn)

    # Load raw player stats data from alternate database and craete player stats table
    # for sim engine DB
    query = text("select * from player_stats_season_2024")
    results = alt_db_conn.execute(query)
    raw_player_stats_df = pd.DataFrame(results.fetchall(), columns=results.keys())
    setup_sim_engine_player_stats_table(raw_player_stats_df, main_db_conn)