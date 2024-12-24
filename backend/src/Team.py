import numpy as np
from scipy.stats import lognorm

class Team:
    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = stats
        self.off_passing_distribution = self.init_distribution("off_pass_yards_per_play_mean", "off_pass_yards_per_play_variance")
        self.off_rushing_distribution = self.init_distribution("off_rush_yards_per_play_mean", "off_rush_yards_per_play_variance")
        self.def_passing_distribution = self.init_distribution("def_pass_yards_per_play_mean", "def_pass_yards_per_play_variance")
        self.def_rushing_distribution = self.init_distribution("def_rush_yards_per_play_mean", "def_rush_yards_per_play_variance")

    def init_distribution(self, mean_col_name: str, variance_col_name: str):
        mean = self.get_stat(mean_col_name)
        variance = self.get_stat(variance_col_name)
        sigma = np.sqrt(np.log(1 + (variance / mean**2)))
        mu = np.log(mean) - (sigma**2) / 2
        dist = lognorm(s=sigma, scale=np.exp(mu))
        return dist
    
    def create_custom_distribution(self, mean: float, variance: float):
        sigma = np.sqrt(np.log(1 + (variance / mean**2)))
        mu = np.log(mean) - (sigma**2) / 2
        dist = lognorm(s=sigma, scale=np.exp(mu))
        return dist.rvs()
    
    def sample_offensive_passing_play(self, custom_mean=None) -> float:
        if custom_mean is None:
            return self.off_passing_distribution.rvs()
        else:
            return self.create_custom_distribution(custom_mean, self.get_stat("off_pass_yards_per_play_variance"))
    
    def sample_offensive_rushing_play(self) -> float:
        return self.off_rushing_distribution.rvs()
    
    def sample_defensive_passing_play(self, custom_mean=None) -> float:
        if custom_mean is None:
            return self.off_passing_distribution.rvs()
        else:
            return self.create_custom_distribution(custom_mean, self.get_stat("def_pass_yards_per_play_variance"))
    
    def sample_defensive_rushing_play(self) -> float:
        return self.def_rushing_distribution.rvs()

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