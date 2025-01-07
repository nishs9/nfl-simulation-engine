# Implementation Details

### *Frontend*
---
The UI for this project is pretty straightforward. At the top, it allows user to specify the 2 teams, set the number of simulations to run, and choose which game model to use (the concept of game model will
be expanded upon later in the doc). When the user clicks "Run Simulation" and after the results load, you see a pie chart representing the percentage of games
that were won by each team during the last simulation run. The stats table that is displayed is also an average of the various statistics over the course of the
simulation runs. At the bottom, there is an additional section with a set of visualizations from a randomly selected simulation iteration from the most recent run. You can look at how passing yards, rushing yards, and scoring unfolded over the course of the simulation.

### *Flask API*
---
The majority of the logic for the flask app is contained within `backend/src/simulation_engine_api.py`. It has 2 simple endpoints:
- `/run-simulation`: This is the endpoint that the frontend calls when a user clicks "Run Simulation". It does some basic initialization of the objects
needed to run the simulations and the calls the multi-threaded simulation runner (located in `backend/src/game_simulator.py`). The API then responds with all of the 
details about the simulation results. This is a synchronous process.

- `/run-legacy-simulation`: This is an endpoint that isn't currently used but I created it as a failsafe in case I ever run into serious issues with the 
multi-threaded simulation runner. This endpoint calls the single-threaded version of the simulation runner and, otherwise, doesn't differ at all to the
main endpoint.

### *Sim Engine Backend [this section is a work in progress]*
---
As mentioned earlier, the API is connected to 2 main components: the database and the python scripts which contain the actual simulation logc. In this section,
I'll focus on running through the details about the python side of things. I will discuss the database details in a separate section later. 

For the engine itself, there are 3 main classes where the simulation logic is defined:
1. `Team`: This is an object that represents a team involved in a simulation. It has the following fields/attributes:
    - `name`: Team abbreviation
    - `stats`: Dictionary containing all relevant team stats needed for the simulation
    - `off_passing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards gained on pass plays by the team
    - `off_rushing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards gained on run plays by the team
    - `def_passing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards allowed on pass plays by the team
    - `def_rushing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards allowed on run plays by the team
        - NOTE: The 4 log-normal distributions are only used by the V1 game model at the moment (more info on that later)
2. `AbstractGameModel`: This is an abstract class that represents what simulation logic we want to use when running the game engine.
    - In order to create new game models, all we need to do is extend the AbstractGameModel class and implement the `resolve_play()` method which takes in a dictionary representation of the current game state and returns a dictionary representing the play result.
    - There are currently 2 models that implement this abstract class and I will discuss them in detail shortly.
3. `GameEngine`: This class represents a single simulation iteration. It is also responsible for handling all of the game state management logic as well as calling into the appropriate GameModels to get play outcomes. This class is largely complete and likely won't be touched much further outside of making small tweaks and fixes as I add more complexity and allow for more detailed game states. It has the following fields/attrbutes:
    - `home_team`: A reference to the `Team` object representing the home team in the simulations
    - `away_team`: A reference to the `Team` object representing the away team in the simulations
    -  `game_state`: A dictionary representation of the current game state of the simulation. It contains the following information:
        - `quarter`
        - `game_seconds_remaining`
        - `quarter_seconds_remaining`
        - `possession_team`
        - `defense_team`
        - `yardline`: This is the distance remaining to the opponent's endzone
        - `down`
        - `distance`
        - `score`
        - `play_log`
    - `game_model`: A reference to the game model that is being used for this simulation run

#### Game Model Details
In the context of this simulation engine, the "Game Model" refers to the specific logic used to determine the outcome of each play in the simulated game. However regardless of the logic within them, each game model fundamentally does the same thing. Each of the concrete game models extensd the `AbstractGameModel` class (contained in `backend/src/GameModels.py`) and implements the `resolve_play()` method. This method takes in a game state (which is an attribute of the `GameEngine` class) and returns a play result dictionary which the GameEngine later consumes in order to update the game state. The structure of this play_result dictionary is as follows:

- `play_type`: This will be one of: `run`, `pass`, `field_goal`, `punt`
- `field_goal_made`: Boolean for whether a FG was made (only populated when `play_type == field_goal`)
- `yards_gained`: Yards gained on the previous play
- `time_elapsed`: Time elapsed on the previous play (currently a randomly assigned value between 20-30 seconds)
- `quarter`
- `quarter_seconds_remaining`
- `game_seconds_remaining`
- `turnover`
- `touchdown`
- `posteam`
- `posteam_score`
- `score`
- `yardline`
- `down`
- `distance`

There are currently 3 different game models that can be used by the simulation engine:
1. Prototype Model (`proto`)
3. Game Model V1 (`v1`)
4. Game Model V1a (`v1a`)

#### Prototype Model
The logic in the prototype model is relatively straightfoward. For any given play, we use `random.choices()` and plug in weights based on the historical pass vs run rate for the given team in possession. This data is based on the updated data from the current (2024/25) NFL season. Once we have a playcall chosen, I then take a weighted average of run/pass yards per play of the offense and defense. Across all of the models, I use a weight system to favor one side of the ball or the other. Typically, this weight favors the offense given the general offensive bias that has been created in recent years within the NFL due to rule changes and other factors. This is referred to as `off_weight` in other parts of the repo.

In the case of pass plays, I then employ `random.choices()` again using a weighted average of the offense and defense's historical completion rates to determine whether the pass is complete or not. We then also use it to determine whether a sack occurs on the play and finally, in both run or pass plays, we do one last random choice to determine whether a turnover should occur on the play. Just to reiterate, all of these outcomes are also modeled using the historical rate of occurence for the given team (i.e. sacks are based on the sack rate for the offense and defense, etc).

In terms of 4th down logic, this model takes a very simplistic approach. If a team encounters a 4th down, it will always punt unless the field goal is 55 yards or less. There is no concept of a team going for it on 4th down.

#### V1 + V1a Model
The V1 and V1a models build on the original prototype in 2 main ways. First, rather than just using the weighted average of rush/pass yards per play, which ends up leading to every run and pass play being the same length. I fit a log-normal distribution to each team's actual distribution of passing and rushing yards. Using `scipy`, we save the parameters of this approximated log-normal distribution and save it in the DB for every team. Upon initializing the `Team` objects that are inputted into the `GameEngine` instance, we take the saved parameters, build the distribution, and save a copy of it to the `Team` objects. Then when it comes time to calculate the yards gained on the play, the game engine takes a random sample from the offensive and defensive team's respective dsitributions. Then it takes the weighted average of the 2 random samples in order to determine the yards gained on the play. This allows for some realistic variance in the play outcomes which should hopefully aid in increasing the simulation engine's realism.

The other major improvement that I made was to improve simulation logic by introducing the concept of going for it on 4th down. I did this by training a Random Forest ML model using `sklearn`. The 4th down model was trained on league-wide data from 2017-2024. There are no models specific to each team, and the training data didn't include any identifying information about the teams involved. With this model, when the game engine encounters a 4th down it will send the model info about the current game state. The prediction given by the model is then used as the playcall.

There aren't any major differences between the V1 and V1a model. The main update was that I spent time to optimize the 4th dowl model to be more performant and deliver more accurate and realistic predictions. In addition, I made other minor tweaks to the game model logic (including tweaking the offense-defense global weight) to see if I can improve its accuracy.

#### V1b Model [WIP]
The V1b model is a small iteration on the V1a model discussed in the previous section. I made a bunch of small tweaks to try and improve performance and accuracy of the model. The biggest change was related to how passing yards are calculated for individual plays. In previous iterations, I was looking at total passing yards rather than separating the play into 2 parts. One part being for the air yards and one part being for the yards after catch. With this in mind, below is how I now calculate the predicted yards gained for a given pass play:

```
// NOTE: off_weight varies depending on which game model is being used
fn weighted_avg(air, arg2) {
    (off_weight * arg1) + ((1-off_weight) * arg2)
}

off_air_yards_per_target = *randomly sample an approximated distribution of the offense's air yards per attempt*

def_air_yards_per_target_allowed = *randomly sample an approximated distribution of the defense's air yards allowed per attempt*

off_yards_after_catch_per_comp = *take the average YAC per completion for the offense*

def_yards_after_catch_per_comp = **take the average YAC per completion for the defense*

pass_yards_on_play = weighted_avg(off_air_yards_per_target, def_air_yards_per_target_allowed)
	+ weighted_avg(off_yards_after_catch_per_comp, def_yards_after_catch_per_comp) 
```

### DB Details
---
[coming soon...]
