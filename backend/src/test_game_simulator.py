import pytest
import random
import GameSimulator
from typing import Tuple
from GameEngine import GameEngine
from Team import Team
import pandas as pd
from sqlalchemy import create_engine, text
from proj_secrets import db_username, db_password, db_name

teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
                  "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
                  "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
                  "SEA","SF","TB","TEN","WAS"]

def get_random_teams() -> Tuple[str, str]:
    home_team_idx = random.randint(0, len(teams)-1)
    away_team_idx = random.randint(0, len(teams)-1)

    home_team_abbrev = teams[home_team_idx]
    away_team_abbrev = teams[away_team_idx]
    return home_team_abbrev, away_team_abbrev

def init_teams_for_test(home_team_abbrev: str, away_team_abbrev: str) -> Tuple[object, object]:
    main_db_engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}")
    main_db_conn = main_db_engine.connect()
    sim_engine_query = text("select * from sim_engine_team_stats_2024 where team = :team")

    home_team_results = main_db_conn.execute(sim_engine_query, {"team": home_team_abbrev})
    home_team_df = pd.DataFrame(home_team_results.fetchall(), columns=home_team_results.keys())
    home_team_stats = home_team_df.iloc[0].to_dict()

    away_team_results = main_db_conn.execute(sim_engine_query, {"team": away_team_abbrev})
    away_team_df = pd.DataFrame(away_team_results.fetchall(), columns=away_team_results.keys())
    away_team_stats = away_team_df.iloc[0].to_dict()

    home_team = Team(home_team_abbrev, home_team_stats)
    away_team = Team(away_team_abbrev, away_team_stats)

    return home_team, away_team

def test_team_initalization():
    home_team_abbrev, away_team_abbrev = get_random_teams()

    home_team, away_team = GameSimulator.initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)

    assert home_team.name == home_team_abbrev
    assert home_team.get_stats is not None
    assert home_team.get_stat("games_played") > 0

    assert away_team.name == away_team_abbrev
    assert away_team.get_stats is not None
    assert away_team.get_stat("games_played") > 0

def test_game_engine_initialization():
    home_team_abbrev, away_team_abbrev = get_random_teams()
    home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
    
    game_engine = GameEngine(home_team, away_team)

    assert game_engine.home_team.name == home_team_abbrev
    assert game_engine.away_team.name == away_team_abbrev
    assert game_engine.game_state is not None
    assert game_engine.game_model is not None

def test_game_state_initialization():
    home_team_abbrev, away_team_abbrev = get_random_teams()
    home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
    
    game_engine = GameEngine(home_team, away_team)

    assert game_engine.game_state["quarter"] == 1
    assert game_engine.game_state["game_seconds_remaining"] == 3600
    assert game_engine.game_state["quarter_seconds_remaining"] == 900
    assert game_engine.game_state["possession_team"] == home_team
    assert game_engine.game_state["defense_team"] == away_team
    assert game_engine.game_state["yardline"] == 75
    assert game_engine.game_state["down"] == 1
    assert game_engine.game_state["distance"] == 10
    assert game_engine.game_state["score"][home_team.name] == 0
    assert game_engine.game_state["score"][away_team.name] == 0
    assert game_engine.game_state["play_log"] == []