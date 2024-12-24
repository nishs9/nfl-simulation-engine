from abc import ABC, abstractmethod
from functools import lru_cache
import random
import joblib
import pandas as pd

class AbstractGameModel(ABC):

    def __init__(self, off_weight=0.55):
        self.off_weight = off_weight
        self.def_weight = 1 - off_weight

    @abstractmethod
    def resolve_play(self, game_state: dict) -> dict:
        pass

    @lru_cache(maxsize=1000)
    def get_weighted_average(self, off_stat, def_stat):
        return (off_stat * self.off_weight) + (def_stat * self.def_weight)

class PrototypeGameModel(AbstractGameModel):

    def __init__(self, off_weight=0.55):
        super().__init__(off_weight)

    def get_model_code(self) -> str:
        return "proto"

    def resolve_play(self, game_state: dict) -> dict:
        posteam = game_state["possession_team"]
        defteam = game_state["defense_team"]

        time_elapsed = random.randint(15,40)

        # Handle 4th down scenarios
        if game_state["down"] == 4 and game_state["yardline"] > 55:
            return {
                "play_type": "punt", 
                "field_goal_made": None,
                "yards_gained": 40,
                "time_elapsed": time_elapsed, 
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        elif game_state["down"] == 4 and game_state["yardline"] <= 45:
            fg_success_rate = posteam.get_stat("field_goal_success_rate")
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": time_elapsed,
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],  
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
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
        
        weighted_yards_per_play = self.get_weighted_average(off_yards_per_play, def_yards_per_play)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam.get_stat("pass_completion_rate") / 100
            def_pass_cmp_rate = defteam.get_stat("pass_completion_rate_allowed") / 100
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam.get_stat("turnover_rate")
        def_turnover_rate = defteam.get_stat("forced_turnover_rate")
        weighted_turnover_rate = self.get_weighted_average(off_turnover_rate, def_turnover_rate)
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam.get_stat("sacks_allowed_rate")
        def_sack_rate = defteam.get_stat("sacks_made_rate")
        weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam.get_stat("sack_yards_allowed")
            def_yards_inflicted_per_sack = defteam.get_stat("sack_yards_inflicted")
            yards_lost_on_sack = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
            yards_gained = yards_lost_on_sack

        return {
            "play_type": play_type, 
            "field_goal_made": None,
            "yards_gained": yards_gained,
            "time_elapsed": time_elapsed,
            "quarter": game_state["quarter"],
            "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
            "turnover": turnover_on_play,
            "touchdown": False, # This will be updated after the play is processed in update_game_state
            "posteam": posteam.name
        }
    
class GameModel_V1(AbstractGameModel):
    
    def __init__(self, off_weight=0.65):
        self.fourth_down_model = joblib.load("game_models/v1_4th_down_playcall_model.pkl")
        self.fourth_down_model_column_mapping = { 0: "run", 1: "pass",
                                                2: "punt", 3: "field_goal" }
        super().__init__(off_weight)

    def get_model_code(self) -> str:
        return "v1"

    def get_half_seconds_remaining(self, qtr, qtr_seconds_remaining) -> int:
        if qtr == 1 or qtr == 3:
            return qtr_seconds_remaining + 900
        else:
            return qtr_seconds_remaining

    def handle_4th_down(self, game_state:dict):
        posteam = game_state["possession_team"].name
        defteam = game_state["defense_team"].name
        fourth_down_data = {
            "game_seconds_remaining": game_state["game_seconds_remaining"],
            "half_seconds_remaining": self.get_half_seconds_remaining(game_state["quarter"], game_state["quarter_seconds_remaining"]),
            "ydstogo": game_state["distance"],
            "yardline_100": game_state["yardline"],
            "score_differential": game_state["score"][posteam] - game_state["score"][defteam]    
        }
        prediction = self.fourth_down_model.predict(pd.DataFrame([fourth_down_data]))
        return self.fourth_down_model_column_mapping[prediction[0]]

    def resolve_play(self, game_state: dict) -> dict:
        posteam = game_state["possession_team"]
        defteam = game_state["defense_team"]

        time_elapsed = random.randint(15,40)

        play_type = None
        if (game_state["down"] == 4):
            # For 4th downs, use our random forest model to determine the play call
            play_type = self.handle_4th_down(game_state)
        else:
            # If not 4th down, run normal simulation logic
            play_type = random.choices(['run', 'pass'], [posteam.get_stat("run_rate"), posteam.get_stat("pass_rate")])[0]

        # Handle 4th down scenarios for punts and field goals
        if game_state["down"] == 4 and play_type == "punt":
            return {
                "play_type": "punt", 
                "field_goal_made": None,
                "yards_gained": 40,
                "time_elapsed": time_elapsed, 
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        elif game_state["down"] == 4 and play_type == "field_goal":
            fg_success_rate = posteam.get_stat("field_goal_success_rate")
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": time_elapsed,
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],  
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }

        # Handle normal play calls (run or pass)
        off_yards_per_play = None
        def_yards_per_play = None
        if (play_type == "run"):
            off_yards_per_play = posteam.sample_offensive_rushing_play()
            def_yards_per_play = defteam.sample_defensive_rushing_play()
        else:
            off_yards_per_play = posteam.sample_offensive_passing_play()
            def_yards_per_play = defteam.sample_defensive_passing_play()
        
        weighted_yards_per_play = self.get_weighted_average(off_yards_per_play, def_yards_per_play)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam.get_stat("pass_completion_rate") / 100
            def_pass_cmp_rate = defteam.get_stat("pass_completion_rate_allowed") / 100
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam.get_stat("turnover_rate")
        def_turnover_rate = defteam.get_stat("forced_turnover_rate")
        weighted_turnover_rate = (0.45) * (self.get_weighted_average(off_turnover_rate, def_turnover_rate))
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam.get_stat("sacks_allowed_rate")
        def_sack_rate = defteam.get_stat("sacks_made_rate")
        weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam.get_stat("sack_yards_allowed")
            def_yards_inflicted_per_sack = defteam.get_stat("sack_yards_inflicted")
            yards_lost_on_sack = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
            yards_gained = yards_lost_on_sack

        return {
            "play_type": play_type, 
            "field_goal_made": None,
            "yards_gained": yards_gained,
            "time_elapsed": time_elapsed,
            "quarter": game_state["quarter"],
            "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
            "turnover": turnover_on_play,
            "touchdown": False, # This will be updated after the play is processed in update_game_state
            "posteam": posteam.name
        }
    
class GameModel_V1a(GameModel_V1):
    
    def __init__(self, off_weight=0.625):
        self.fourth_down_model = joblib.load("game_models/v2a_4th_down_playcall_model.pkl")
        self.fourth_down_model_column_mapping = { 0: "goforit", 1: "field_goal", 2: "punt" }
        super().__init__(off_weight)

    def get_model_code(self) -> str:
        return "v1a"

    def handle_4th_down(self, game_state:dict):
        posteam = game_state["possession_team"]
        defteam = game_state["defense_team"]
        fourth_down_data = {
            "game_seconds_remaining": game_state["game_seconds_remaining"],
            "half_seconds_remaining": self.get_half_seconds_remaining(game_state["quarter"], game_state["quarter_seconds_remaining"]),
            "ydstogo": game_state["distance"],
            "yardline_100": game_state["yardline"],
            "score_differential": game_state["score"][posteam.name] - game_state["score"][posteam.name]    
        }
        prediction_result = self.fourth_down_model.predict(pd.DataFrame([fourth_down_data]))
        prediction = self.fourth_down_model_column_mapping[prediction_result[0]]
        if prediction == "goforit":
            return random.choices(['run', 'pass'], [posteam.get_stat("run_rate"), defteam.get_stat("pass_rate")])[0]
        else:
            return prediction

    def resolve_play(self, game_state: dict) -> dict:
        posteam = game_state["possession_team"]
        defteam = game_state["defense_team"]

        time_elapsed = random.randint(20,30)

        play_type = None
        if (game_state["down"] == 4):
            # For 4th downs, use our random forest model to determine the play call
            play_type = self.handle_4th_down(game_state)
        else:
            # If not 4th down, run normal simulation logic
            play_type = random.choices(['run', 'pass'], [posteam.get_stat("run_rate"), posteam.get_stat("pass_rate")])[0]

        # Handle 4th down scenarios for punts and field goals
        if game_state["down"] == 4 and play_type == "punt":
            return {
                "play_type": "punt", 
                "field_goal_made": None,
                "yards_gained": random.randint(40,55),
                "time_elapsed": time_elapsed, 
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        elif game_state["down"] == 4 and play_type == "field_goal":
            fg_success_rate = posteam.get_stat("field_goal_success_rate")
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": time_elapsed,
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],  
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }

        # Handle normal play calls (run or pass)
        off_yards_per_play = None
        def_yards_per_play = None
        if (play_type == "run"):
            off_yards_per_play = posteam.sample_offensive_rushing_play()
            def_yards_per_play = defteam.sample_defensive_rushing_play()
        else:
            off_yards_per_play = posteam.sample_offensive_passing_play()
            def_yards_per_play = defteam.sample_defensive_passing_play()

        weighted_yards_per_play = self.get_weighted_average(off_yards_per_play, def_yards_per_play)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam.get_stat("pass_completion_rate") / 100
            def_pass_cmp_rate = defteam.get_stat("pass_completion_rate_allowed") / 100
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam.get_stat("turnover_rate")
        def_turnover_rate = defteam.get_stat("forced_turnover_rate")
        weighted_turnover_rate = (0.40) * (self.get_weighted_average(off_turnover_rate, def_turnover_rate))
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam.get_stat("sacks_allowed_rate")
        def_sack_rate = defteam.get_stat("sacks_made_rate")
        weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam.get_stat("sack_yards_allowed")
            def_yards_inflicted_per_sack = defteam.get_stat("sack_yards_inflicted")
            yards_lost_on_sack = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
            yards_gained = yards_lost_on_sack

        return {
            "play_type": play_type, 
            "field_goal_made": None,
            "yards_gained": yards_gained,
            "time_elapsed": time_elapsed,
            "quarter": game_state["quarter"],
            "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
            "turnover": turnover_on_play,
            "touchdown": False, # This will be updated after the play is processed in update_game_state
            "posteam": posteam.name
        }
    
class GameModel_V1b(GameModel_V1a):
    
    def __init__(self, off_weight=0.525):
        super().__init__(off_weight)

    def get_model_code(self) -> str:
        return "v1b"

    def get_projected_pass_yards_for_play(self, posteam: object, defteam: object) -> float:
        off_air_yards_per_attempt = posteam.sample_offensive_air_yards()
        def_air_yards_per_attempt = defteam.sample_defensive_air_yards()
        weighted_air_yards_per_attempt = self.get_weighted_average(off_air_yards_per_attempt, def_air_yards_per_attempt)

        off_yac_per_completion = posteam.get_stat("off_yac_per_completion")
        def_yac_per_completion = defteam.get_stat("def_yac_per_completion")
        weighted_yac_per_completion = self.get_weighted_average(off_yac_per_completion, def_yac_per_completion)

        return weighted_air_yards_per_attempt + weighted_yac_per_completion

    def resolve_play(self, game_state: dict) -> dict:
        posteam = game_state["possession_team"]
        defteam = game_state["defense_team"]

        time_elapsed = random.randint(17,30)

        play_type = None
        if (game_state["down"] == 4):
            # For 4th downs, use our random forest model to determine the play call
            play_type = self.handle_4th_down(game_state)
        else:
            # If not 4th down, run normal simulation logic
            play_type = random.choices(['run', 'pass'], [posteam.get_stat("run_rate"), posteam.get_stat("pass_rate")])[0]

        # Handle 4th down scenarios for punts and field goals
        if game_state["down"] == 4 and play_type == "punt":
            return {
                "play_type": "punt", 
                "field_goal_made": None,
                "yards_gained": random.randint(40,55),
                "time_elapsed": time_elapsed, 
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        elif game_state["down"] == 4 and play_type == "field_goal":
            fg_success_rate = posteam.get_stat("field_goal_success_rate")
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": time_elapsed,
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],  
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }

        # Handle normal play calls (run or pass)
        weighted_yards_per_play = None
        if (play_type == "run"):
            off_yards_per_play = posteam.sample_offensive_rushing_play()
            def_yards_per_play = defteam.sample_defensive_rushing_play()
            weighted_yards_per_play = self.get_weighted_average(off_yards_per_play, def_yards_per_play)
        else:
            off_pass_cmp_rate = posteam.get_stat("pass_completion_rate") / 100
            def_pass_cmp_rate = defteam.get_stat("pass_completion_rate_allowed") / 100
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0
            else:
                weighted_yards_per_play = self.get_projected_pass_yards_for_play(posteam, defteam)

        off_turnover_rate = posteam.get_stat("turnover_rate")
        def_turnover_rate = defteam.get_stat("forced_turnover_rate")
        weighted_turnover_rate = (0.375) * (self.get_weighted_average(off_turnover_rate, def_turnover_rate))
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam.get_stat("sacks_allowed_rate")
        def_sack_rate = defteam.get_stat("sacks_made_rate")
        weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam.get_stat("sack_yards_allowed")
            def_yards_inflicted_per_sack = defteam.get_stat("sack_yards_inflicted")
            yards_lost_on_sack = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
            yards_gained = yards_lost_on_sack

        return {
            "play_type": play_type, 
            "field_goal_made": None,
            "yards_gained": yards_gained,
            "time_elapsed": time_elapsed,
            "quarter": game_state["quarter"],
            "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
            "turnover": turnover_on_play,
            "touchdown": False, # This will be updated after the play is processed in update_game_state
            "posteam": posteam.name
        }