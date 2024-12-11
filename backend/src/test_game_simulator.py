import pytest
import random
import GameSimulator

teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
                  "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
                  "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
                  "SEA","SF","TB","TEN","WAS"]

def test_team_initalization():
    home_team_idx = random.randint(0, len(teams)-1)
    away_team_idx = random.randint(0, len(teams)-1)

    home_team_abbrev = teams[home_team_idx]
    away_team_abbrev = teams[away_team_idx]

    home_team, away_team = GameSimulator.initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)

    assert home_team.name == home_team_abbrev
    assert home_team.get_stats is not None
    assert home_team.get_stat("games_played") > 0

    assert away_team.name == away_team_abbrev
    assert away_team.get_stats is not None
    assert away_team.get_stat("games_played") > 0