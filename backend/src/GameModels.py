from abc import ABC, abstractmethod
import random

class AbstractGameModel(ABC):

    @abstractmethod
    def resolve_play(self):
        pass

class PrototypeGameModel(AbstractGameModel):

    def resolve_play(self, game_state: dict) -> dict:
        off_weight = 0.55
        def_weight = 1-off_weight

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
        elif game_state["down"] == 4 and game_state["yardline"] <= 55:
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
        
        weighted_yards_per_play = (off_yards_per_play * off_weight) + (def_yards_per_play * def_weight)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam.get_stat("pass_completion_rate") / 100
            def_pass_cmp_rate = defteam.get_stat("pass_completion_rate_allowed") / 100
            weighted_pass_cmp_rate = (off_pass_cmp_rate * off_weight) + (def_pass_cmp_rate * def_weight)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam.get_stat("turnover_rate")
        def_turnover_rate = defteam.get_stat("forced_turnover_rate")
        weighted_turnover_rate = (off_turnover_rate * off_weight) + (def_turnover_rate * def_weight)
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam.get_stat("sacks_allowed_rate")
        def_sack_rate = defteam.get_stat("sacks_made_rate")
        weighted_sack_rate = (off_sack_rate * off_weight) + (def_sack_rate * def_weight)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam.get_stat("sack_yards_allowed")
            def_yards_inflicted_per_sack = defteam.get_stat("sack_yards_inflicted")
            yards_lost_on_sack = (off_yards_lost_per_sack * off_weight) + (def_yards_inflicted_per_sack * def_weight)
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