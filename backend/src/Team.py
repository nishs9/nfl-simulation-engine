import numpy as np
from scipy.stats import lognorm

class Team:
    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = stats
        self.off_passing_distribution = None
        self.off_rushing_distribution = None
        self.def_passing_distribution = None
        self.def_rushing_distribution = None
        self.enhanced_off_passing_dist = None
        self.enhanced_def_passing_dist = None

    def setup_teams_for_game_model(self, game_model_str: str):
        if game_model_str == "proto":
            pass
        elif game_model_str == "v1" or game_model_str == "v1a":
            self.off_passing_distribution = self.init_distribution("off_pass_yards_per_play_mean", "off_pass_yards_per_play_variance")
            self.off_rushing_distribution = self.init_distribution("off_rush_yards_per_play_mean", "off_rush_yards_per_play_variance")
            
            self.def_passing_distribution = self.init_distribution("def_pass_yards_per_play_mean", "def_pass_yards_per_play_variance")
            self.def_rushing_distribution = self.init_distribution("def_rush_yards_per_play_mean", "def_rush_yards_per_play_variance")
        elif game_model_str == "v1b":
            self.enhanced_off_passing_dist = self.init_distribution("off_air_yards_per_attempt", "off_pass_yards_per_play_variance")
            self.off_rushing_distribution = self.init_distribution("off_rush_yards_per_play_mean", "off_rush_yards_per_play_variance")

            self.enhanced_def_passing_dist = self.init_distribution("def_air_yards_per_attempt", "def_pass_yards_per_play_variance")
            self.def_rushing_distribution = self.init_distribution("def_rush_yards_per_play_mean", "def_rush_yards_per_play_variance")
        else:
            raise ValueError(f"Invalid game model string: {game_model_str}")
    
    def init_distribution(self, mean_col_name: str, variance_col_name: str):
        mean = self.get_stat(mean_col_name)
        variance = self.get_stat(variance_col_name)
        sigma = np.sqrt(np.log(1 + (variance / mean**2)))
        mu = np.log(mean) - (sigma**2) / 2
        dist = lognorm(s=sigma, scale=np.exp(mu))
        return dist
    
    def sample_offensive_passing_play(self) -> float:
        return self.off_passing_distribution.rvs()
    
    def sample_offensive_rushing_play(self) -> float:
        return self.off_rushing_distribution.rvs()
    
    def sample_offensive_air_yards(self) -> float:
        return self.enhanced_off_passing_dist.rvs()
    
    def sample_defensive_passing_play(self) -> float:
        return self.def_passing_distribution.rvs()
    
    def sample_defensive_rushing_play(self) -> float:
        return self.def_rushing_distribution.rvs()
    
    def sample_defensive_air_yards(self) -> float:
        return self.enhanced_def_passing_dist.rvs()

    def __str__(self):
        return f"Team object representing {self.name}"
    
    def get_name(self) -> str:
        return self.name
    
    def set_name(self, name: str) -> None:
        self.name = name
    
    def get_stats(self) -> dict:
        return self.stats
    
    def set_stats(self, stats: dict) -> None:
        self.stats = stats

    def get_stat(self, key: str) -> any:
        return self.stats[key]