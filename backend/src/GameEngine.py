import random

class GameEngine:
    def __init__(self, home_team: object, away_team:object):
        self.home_team = home_team
        self.away_team = away_team
        self.game_state = None #initialize game state

    def _initialize_game_state(self):
        return {
            "quarter": 1,
            "game_seconds_remaining": 3600,
            "quarter_seconds_remaining": 900, 
            "possession_team": self.away_team.name, 
            "yardline": 75, 
            "down": 1,
            "distance": 10,
            "score": {self.home_team.name: 0, self.away_team.name: 0},
            "play_log": [],
        }
    
    def simulate_drive(self):
        while True:
            play_result = None #resolve/simulate play
            #update game state with play result
            # if play result is end of drive, break

    def simulate_play(self):
        # Handle 4th down
        if self.game_state["down"] == 4 and self.game_state["yardline"] > 55:
            return {
                "play_type": "punt", 
                "yards_gained": -40, 
                "turnover": False, 
                "end_drive": True
            }
        elif self.game_state["down"] == 4 and self.game_state["yardline"] <= 55:
            return {
                "play_type": "field_goal", 
                "yards_gained": 0, 
                "turnover": False, 
                "end_drive": True
            }
        
        # If not 4th down, run normal simulation logic
        play_type = None # determine play type based on pass + run rates of offense
        yards_gained = None # determine yards gained based on yards per play type for offense and defense (weighted average)
        turnover = False # determine if turnover occurs using turnover rates for offense and defense (weighted average)
        end_drive = False # determine if drive ends (score, turnover, 4th down not in FG range)

        return {
            "play_type": play_type, 
            "yards_gained": yards_gained,
            "turnover": turnover, 
            "end_drive": end_drive
        }

    def update_game_state(self, play_result: dict):
        # Update game state based on play result
        # Update yardline, down, distance, score, time remaining, etc.
        # Append play result to play log
        return

    def switch_possession(self):
        # Switch possession team
        # Update yardline, down, distance, etc.
        # Update quarter if necessary
        return
    
    def handle_halftime(self):
        # Handle halftime
        # Update game state
        return
    
    def run_simulation(self):
        while self.game_state["game_seconds_remaining"] > 0:
            self.simulate_drive()
            self.game_state["quarter_seconds_remaining"] -= 600  # Approximate time for a drive
            self.game_state["game_seconds_remaining"] -= 600

            if self.game_state["quarter_seconds_remaining"] <= 0:
                self.game_state["quarter"] += 1
                self.game_state["quarter_seconds_remaining"] = 900  # Reset quarter time

                if self.game_state["quarter"] == 3:
                    # Handle halftime
                    self.handle_halftime()

        return self.get_game_summary()
    
    def get_game_summary(self):
        """Summarize the game results."""
        return {
            "final_score": self.state["score"],
            "play_log": self.state["play_log"],
        }