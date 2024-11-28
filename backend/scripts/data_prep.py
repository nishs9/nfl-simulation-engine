from sqlalchemy import create_engine, text, Connection
from proj_secrets import db_username, db_password, db_name, alt_db_name
from typing import List, Dict, Tuple, Any
import pandas as pd

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
    team_stats_dict["yards_per_completion"] = None
    team_stats_dict["rush_yards_per_carry"] = None
    team_stats_dict["scoring_efficiency"] = None
    team_stats_dict["turnover_rate"] = None
    team_stats_dict["forced_turnover_rate"] = None
    team_stats_dict["redzone_efficiency"] = None
    team_stats_dict["run_rate"] = None
    team_stats_dict["pass_rate"] = None
    team_stats_dict["sacks_allowed_rate"] = None
    team_stats_dict["sack_yards_allowed"] = None
    team_stats_dict["sacks_made_rate"] = None
    team_stats_dict["sack_yards_inflicted"] = None
    team_stats_dict["field_goal_success_rate"] = None
    team_stats_dict["pass_completion_rate_allowed"] = None
    team_stats_dict["yards_allowed_per_completion"] = None
    team_stats_dict["rush_yards_per_carry_allowed"] = None
    return team_stats_dict

def get_completion_pct(team: str, team_df: pd.DataFrame) -> float:
    pass_comp_pct_df = team_df[(team_df["posteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_attempts = pass_comp_pct_df["pass_attempt"].sum()
    total_completions = pass_comp_pct_df["complete_pass"].sum()
    completion_pct = total_completions / total_attempts
    completion_pct = round(completion_pct * 100, 2)
    return completion_pct

def get_completion_pct_allowed(team: str, team_df: pd.DataFrame) -> float:
    pass_comp_pct_df = team_df[(team_df["defteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_attempts = pass_comp_pct_df["pass_attempt"].sum()
    total_completions = pass_comp_pct_df["complete_pass"].sum()
    completion_pct_allowed = total_completions / total_attempts
    completion_pct_allowed = round(completion_pct_allowed * 100, 2)
    return completion_pct_allowed

def get_yards_per_completion(team: str, team_df: pd.DataFrame) -> float:
    pass_yds_per_comp_df = team_df[(team_df["posteam"] == team) & (team_df["complete_pass"] == 1)]
    total_completions = pass_yds_per_comp_df["complete_pass"].sum()
    total_pass_yds = pass_yds_per_comp_df["passing_yards"].sum()
    yards_per_completion = round(total_pass_yds / total_completions, 2)
    return yards_per_completion

def get_yards_allowed_per_completion(team: str, team_df: pd.DataFrame) -> float:
    pass_yds_per_comp_df = team_df[(team_df["defteam"] == team) & (team_df["complete_pass"] == 1)]
    total_completions = pass_yds_per_comp_df["complete_pass"].sum()
    total_pass_yds_allowed = pass_yds_per_comp_df["passing_yards"].sum()
    yards_allowed_per_completion = round(total_pass_yds_allowed / total_completions, 2)
    return yards_allowed_per_completion

def get_rush_yards_per_carry(team: str, team_df: pd.DataFrame) -> float:
    rush_yds_per_carry_df = team_df[(team_df["posteam"] == team) & (team_df["rush_attempt"] == 1)]
    total_rush_attempts = rush_yds_per_carry_df["rush_attempt"].sum()
    total_rush_yds = rush_yds_per_carry_df["rushing_yards"].sum()
    yards_per_carry = total_rush_yds / total_rush_attempts
    yards_per_carry = round(yards_per_carry, 2)
    return yards_per_carry

def get_rush_yards_allowed_per_carry(team: str, team_df: pd.DataFrame) -> float:
    rush_yds_per_carry_df = team_df[(team_df["defteam"] == team) & (team_df["rush_attempt"] == 1)]
    total_rush_attempts = rush_yds_per_carry_df["rush_attempt"].sum()
    total_rush_yds_allowed = rush_yds_per_carry_df["rushing_yards"].sum()
    yards_allowed_per_carry = total_rush_yds_allowed / total_rush_attempts
    yards_allowed_per_carry = round(yards_allowed_per_carry, 2)
    return yards_allowed_per_carry

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

def get_forced_turnover_rate(team: str, team_df: pd.DataFrame) -> float:
    num_drives = team_df["game_drive_composite_id"].unique().size
    forced_turnover_df = team_df[(team_df["defteam"] == team) & ((team_df["interception"] == 1) | (team_df["fumble_lost"] == 1))]
    total_forced_turnovers = forced_turnover_df["interception"].sum() + forced_turnover_df["fumble_lost"].sum()
    forced_turnovers_per_drive = total_forced_turnovers / num_drives
    forced_turnovers_per_drive = round(forced_turnovers_per_drive, 2)
    return forced_turnovers_per_drive

def get_redzone_efficiency(team: str, team_df: pd.DataFrame) -> float:
    team_df["redzone_drive_composite_id"] = team_df["game_id"] + "_" + team_df["drive"].astype(str) + "_" + team_df["drive_inside20"].astype(str)
    redzone_df = team_df[(team_df["posteam"] == team) & (team_df["drive_inside20"] == 1)]
    redzone_df = redzone_df.drop_duplicates(subset="redzone_drive_composite_id")
    redzone_drives = redzone_df["drive_inside20"].sum()
    redzone_tds = redzone_df[redzone_df["fixed_drive_result"]=="Touchdown"]["fixed_drive_result"].count()
    redzone_efficiency = redzone_tds / redzone_drives
    redzone_efficiency = round(redzone_efficiency * 100, 2)
    return redzone_efficiency

def get_run_and_pass_rates(team: str, team_df: pd.DataFrame) -> Tuple[float, float]:
    team_df = team_df[(team_df["posteam"] == team)]
    num_run_plays = team_df["rush_attempt"].sum()
    num_pass_plays = team_df["pass_attempt"].sum()
    total_plays = num_run_plays + num_pass_plays
    run_rate = round(num_run_plays / total_plays, 2)
    pass_rate = round(1 - run_rate, 2)
    return (run_rate, pass_rate)

def get_sack_rates(team: str, team_df: pd.DataFrame) -> Tuple[float, float, float, float]:
    offense_team_df = team_df[(team_df["posteam"] == team)]
    num_pass_plays_run = offense_team_df["pass_attempt"].sum()
    num_sacks_allowed = offense_team_df["sack"].sum()
    sacks_allowed_rate = round(num_sacks_allowed / num_pass_plays_run, 3)

    offense_sack_df = offense_team_df[(offense_team_df["sack"] == 1)]
    num_yards_lost_to_sacks = offense_sack_df["yards_gained"].sum()
    yards_lost_per_sack = round(num_yards_lost_to_sacks / num_sacks_allowed, 2)

    defense_team_df = team_df[(team_df["defteam"] == team)]
    num_pass_plays_faced = defense_team_df["pass_attempt"].sum()
    num_sacks_made = defense_team_df["sack"].sum()
    sacks_made_rate = round(num_sacks_made / num_pass_plays_faced, 3)

    defense_sack_df = defense_team_df[(defense_team_df["sack"] == 1)]
    num_yards_inflicted_by_sacks = defense_sack_df["yards_gained"].sum()
    yards_inflicted_per_sack = round(num_yards_inflicted_by_sacks / num_sacks_made, 2)

    return (sacks_allowed_rate, yards_lost_per_sack, sacks_made_rate, yards_inflicted_per_sack)
    
def get_field_goal_success_rate(team: str, team_df: pd.DataFrame) -> float:
    field_goal_df = team_df[(team_df["posteam"] == team) & (team_df["field_goal_attempt"] == 1)]
    total_field_goal_attempts = field_goal_df["field_goal_attempt"].sum()
    total_field_goals_made = field_goal_df[field_goal_df["field_goal_result"] == "made"]["field_goal_result"].count()
    field_goal_success_rate = total_field_goals_made / total_field_goal_attempts
    field_goal_success_rate = round(field_goal_success_rate, 2)
    return field_goal_success_rate

def setup_sim_engine_team_stats_table(raw_pbp_df: pd.DataFrame, main_db_conn: Connection) -> None:
    team_abbrev_list = sorted(raw_pbp_df["home_team"].unique())
    team_stats_dict = initialize_team_stats_dict(team_abbrev_list)
    games_played_list = []
    pass_completion_rate_list = []
    yards_per_completion_list = []
    rush_yards_per_carry_list = []
    scoring_efficiency_list = []
    turnover_rate_list = []
    forced_turnover_rate_list = []
    redzone_efficiency_list = []
    run_rate_list = []
    pass_rate_list = []
    sacks_allowed_rate_list = []
    sack_yards_allowed_list = []
    sacks_made_rate_list = []
    sack_yards_inflicted_list = []
    fg_success_rate_list = []
    pass_completion_rate_allowed_list = []
    yards_allowed_per_completion_list = []
    rush_yards_allowed_per_carry_list = []
    for team in team_abbrev_list:
        curr_team_df = raw_pbp_df[(raw_pbp_df["home_team"] == team) | (raw_pbp_df["away_team"] == team)]
        curr_team_df["game_drive_composite_id"] = curr_team_df["game_id"] + "_" + curr_team_df["drive"].astype(str)
        games_played_list.append(curr_team_df["game_id"].unique().size)
        pass_completion_rate_list.append(get_completion_pct(team, curr_team_df))
        yards_per_completion_list.append(get_yards_per_completion(team, curr_team_df))
        rush_yards_per_carry_list.append(get_rush_yards_per_carry(team, curr_team_df))
        scoring_efficiency_list.append(get_scoring_efficiency(team, curr_team_df))
        turnover_rate_list.append(get_turnover_rate(team, curr_team_df))
        forced_turnover_rate_list.append(get_forced_turnover_rate(team, curr_team_df))
        redzone_efficiency_list.append(get_redzone_efficiency(team, curr_team_df))

        run_rate, pass_rate = get_run_and_pass_rates(team, curr_team_df)
        run_rate_list.append(run_rate)
        pass_rate_list.append(pass_rate)

        sacks_allowed_rate, sack_yards_allowed, sacks_made_rate, sack_yards_inflicted = get_sack_rates(team, curr_team_df)
        sacks_allowed_rate_list.append(sacks_allowed_rate)
        sack_yards_allowed_list.append(sack_yards_allowed)
        sacks_made_rate_list.append(sacks_made_rate)
        sack_yards_inflicted_list.append(sack_yards_inflicted)
        fg_success_rate_list.append(get_field_goal_success_rate(team, curr_team_df))
        pass_completion_rate_allowed_list.append(get_completion_pct_allowed(team, curr_team_df))
        yards_allowed_per_completion_list.append(get_yards_allowed_per_completion(team, curr_team_df))
        rush_yards_allowed_per_carry_list.append(get_rush_yards_allowed_per_carry(team, curr_team_df))

    team_stats_dict["games_played"] = games_played_list
    team_stats_dict["pass_completion_rate"] = pass_completion_rate_list
    team_stats_dict["yards_per_completion"] = yards_per_completion_list
    team_stats_dict["rush_yards_per_carry"] = rush_yards_per_carry_list
    team_stats_dict["scoring_efficiency"] = scoring_efficiency_list
    team_stats_dict["turnover_rate"] = turnover_rate_list
    team_stats_dict["forced_turnover_rate"] = forced_turnover_rate_list
    team_stats_dict["redzone_efficiency"] = redzone_efficiency_list
    team_stats_dict["run_rate"] = run_rate_list
    team_stats_dict["pass_rate"] = pass_rate_list
    team_stats_dict["sacks_allowed_rate"] = sacks_allowed_rate_list
    team_stats_dict["sacks_made_rate"] = sacks_made_rate_list
    team_stats_dict["sack_yards_allowed"] = sack_yards_allowed_list
    team_stats_dict["sack_yards_inflicted"] = sack_yards_inflicted_list
    team_stats_dict["field_goal_success_rate"] = fg_success_rate_list
    team_stats_dict["pass_completion_rate_allowed"] = pass_completion_rate_allowed_list
    team_stats_dict["yards_allowed_per_completion"] = yards_allowed_per_completion_list
    team_stats_dict["rush_yards_per_carry_allowed"] = rush_yards_allowed_per_carry_list

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