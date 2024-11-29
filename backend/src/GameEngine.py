import random

class GameEngine:
    def __init__(self, home_team: object, away_team:object):
        self.home_team = home_team
        self.away_team = away_team
        self.game_state = self._initialize_game_state()

    def _initialize_game_state(self):
        return {
            "quarter": 1,
            "game_seconds_remaining": 3600,
            "quarter_seconds_remaining": 900, 
            "possession_team": self.away_team, 
            "defense_team": self.home_team,
            "yardline": 75, 
            "down": 1,
            "distance": 10,
            "score": {self.home_team.name: 0, self.away_team.name: 0},
            "play_log": [],
        }

    def simulate_play(self):
        posteam = self.game_state["possession_team"]
        defteam = self.game_state["defense_team"]

        # Handle 4th down scenarios
        if self.game_state["down"] == 4 and self.game_state["yardline"] > 55:
            return {
                "play_type": "punt", 
                "yards_gained": 40,
                "time_elapsed": 25, 
                "turnover": False
            }
        elif self.game_state["down"] == 4 and self.game_state["yardline"] <= 55:
            fg_success_rate = posteam.get_stat("field_goal_success_rate")
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": 25,  
                "turnover": False
            }
        
        # If not 4th down, run normal simulation logic
        play_type = random.choices(['run', 'pass'], [posteam.get_stat("run_rate"), posteam.get_stat("pass_rate")])[0]

        off_yards_per_play = None
        def_yards_per_play = None
        if (play_type == "run"):
            off_yards_per_play = posteam.get_stat("rush_yards_per_carry")
            def_yards_per_play = defteam.get_stat("rush_yards_per_carry_allowed")
        else:
            off_yards_per_play = posteam.get_stat("yards_per_completion")
            def_yards_per_play = defteam.get_stat("yards_allowed_per_completion")
        
        weighted_yards_per_play = (off_yards_per_play * 0.6) + (def_yards_per_play * 0.4)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam.get_stat("pass_completion_rate")
            def_pass_cmp_rate = defteam.get_stat("pass_completion_rate_allowed")
            weighted_pass_cmp_rate = (off_pass_cmp_rate * 0.6) + (def_pass_cmp_rate * 0.4)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam.get_stat("turnover_rate")
        def_turnover_rate = defteam.get_stat("forced_turnover_rate")
        weighted_turnover_rate = (off_turnover_rate * 0.6) + (def_turnover_rate * 0.4)
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam.get_stat("sacks_allowed_rate")
        def_sack_rate = defteam.get_stat("sacks_made_rate")
        weighted_sack_rate = (off_sack_rate * 0.6) + (def_sack_rate * 0.4)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play):
            off_yards_lost_per_sack = posteam.get_stat("sack_yards_allowed")
            def_yards_inflicted_per_sack = defteam.get_stat("sack_yards_inflicted")
            yards_lost_on_sack = (off_yards_lost_per_sack * 0.6) + (def_yards_inflicted_per_sack * 0.4)
            yards_gained = yards_lost_on_sack

        return {
            "play_type": play_type, 
            "yards_gained": yards_gained,
            "time_elapsed": 25,
            "turnover": turnover_on_play
        }

    def update_game_state(self, play_result: dict) -> bool:
        # Update game state based on play result
        # Update yardline, down, distance, score, time remaining, etc.
        # Append play result to play log
        self.game_state["quarter_seconds_remaining"] -= play_result["time_elapsed"]
        self.game_state["game_seconds_remaining"] -= play_result["time_elapsed"]

        if (play_result["turnover"]):
            self.simulate_turnover()
        elif (play_result["play_type"] == "punt"):
            self.simulate_punt(play_result)
        elif (play_result["play_type"] == "field_goal"):
            self.simulate_field_goal(play_result)
        else:
            self.game_state["yardline"] -= play_result["yards_gained"]

            if (play_result["yards_gained"] >= self.game_state["distance"]):
                self.game_state["down"] = 1
                self.game_state["distance"] = 10
            else:
                self.game_state["down"] += 1
                self.game_state["distance"] -= play_result["yards_gained"]

            if (self.game_state["yardline"] <= 0):
                self.game_state["score"][self.game_state["possession_team"].name] += 7
                self.switch_possession()
                self.game_state["yardline"] = 75
                self.game_state["down"] = 1
                self.game_state["distance"] = 10

        self.game_state["play_log"].append(play_result)

        if (self.game_state["quarter_seconds_remaining"] <= 0 and self.game_state["quarter"] not in [2, 4]):
            self.game_state["quarter"] += 1
            self.game_state["quarter_seconds_remaining"] = 900
            return False
        elif (self.game_state["quarter_seconds_remaining"] <= 0 and self.game_state["quarter"] == 2):
            self.handle_halftime()
            return False
        elif (self.game_state["quarter_seconds_remaining"] <= 0 and self.game_state["quarter"] == 4):
            self.game_state["play_log"].append(play_result)
            return True
    
    def simulate_turnover(self):
        self.switch_possession()
        self.game_state["yardline"] = 100 - self.game_state["yardline"]
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def simulate_punt(self, play_result: dict):
        self.switch_possession()
        self.game_state["yardline"] -= play_result["yards_gained"]
        self.game_state["yardline"] = 100 - self.game_state["yardline"]
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def simulate_field_goal(self, play_result: dict):
        if (play_result["field_goal_made"]):
            self.game_state["score"][self.game_state["possession_team"].name] += 3
        self.switch_possession()
        self.game_state["yardline"] = 75
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def switch_possession(self):
        if (self.game_state["possession_team"] == self.home_team):
            self.game_state["possession_team"] = self.away_team
            self.game_state["defense_team"] = self.home_team
        else:
            self.game_state["possession_team"] = self.home_team
            self.game_state["defense_team"] = self.away_team
    
    def handle_halftime(self):
        self.game_state["quarter"] += 1
        self.game_state["quarter_seconds_remaining"] = 900
        self.switch_possession()
        self.game_state["yardline"] = 75
        self.game_state["down"] = 1
        self.game_state["distance"] = 10
    
    def run_simulation(self) -> dict:
        while True:
            play_result = self.simulate_play()
            game_over = self.update_game_state(play_result)
            if game_over:
                break
        return self.get_game_summary()
    
    def get_game_summary(self):
        """Summarize the game results."""
        return {
            "final_score": self.game_state["score"],
            "play_log": len(self.game_state["play_log"]),
        }