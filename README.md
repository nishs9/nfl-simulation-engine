# NFL Simulation Engine
This is a custom simulation engine built to simulate hypothetical NFL games based on up-to-date real-world stats. It is an end-to-end webapp with a frontend
built using React.js with Material UI. For the backend, I built an API with Flask which is connected to a MySQL DB and a set of Python scripts
which contain the logic for the simulation engine itself.

At the moment, everything is hosted locally but I am actively working on deploying this project to the cloud. In addition, my goal is to also set the
project up such that anyone could clone this repository locally and run the app on their machines directly. 

Below is a demo of the app running locally on my personal laptop:

https://github.com/user-attachments/assets/3a15b24a-615d-485f-8c5e-17a39cd80280



For more info on how the model and project work, keep reading:

## Implementation Details

### *Frontend*
---
As you can tell from the screenshot above, the UI is not the main focus of this project. While I will likely add some additional visualizations for 
simulation results and try to clean up the look in general, what you currently see is pretty much going to be the UI layout for the timebeing and 
I don't have any major plans for it at the moment.

In a nutshell, it allows user to specify the 2 teams, set the number of simulations to run, and choose which game model to use (the concept of game model will
be expanded upon later in the doc). When the user clicks "Run Simulation" and after the results load, you see a pie chart representing the percentage of games
that were won by each team during the last simulation run. The stats table that is displayed is also an average of the various statistics over the course of the
simulation runs.

### *Flask API*
---
The majority of the logic for the flask app is contained within `backend/src/simulation_engine_api.py`. It has 2 simple endpoints:
- `/run-simulation`: This is the endpoint that the frontend calls when a user clicks "Run Simulation". It does some basic initialization of the objects
needed to run the simulations and the calls the multi-threaded simulation runner (located in `backend/src/game_simulator.py`). The API then responds with all of the 
details about the simulation results. This is a synchronous process.

- `/run-legacy-simulation`: This is an endpoint that isn't currently used but I simply created it as a failsafe in case I ever run into serious issues with the 
multi-threaded simulation runner. This endpoint simply calls the single-threaded version of the simulation runner and, otherwise, doesn't differ at all to the
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
In the context of this simulation engine, the "Game Model" refers to the specific logic used to determine the outcome of each play in the simulated game. However regardless of the logic within them, each game model fundamentally does the same thing. Each of the concrete game models extensd the `AbstractGameModel` class (contained in `backend/src/GameModels.py`) and implements the `resolve_play()` method. This method simply takes in a game state (which is an attribute of the `GameEngine` class) and returns a play result dictionary which the GameEngine later consumes in order to update the game state. The structure of this play_result dictionary is as follows:
- `play_type`: This will be one of: `run`, `pass`, `field_goal`, `punt`
- `field_goal_made`: Boolean for whether a FG was made (only populated when `play_type == field_goal`)
- `yards_gained`: Yards gained on the previous play
- `time_elapsed`: Time elapsed on the previous play (currently a randomly assigned value between 20-30 seconds)
- `quarter`
- `quarter_seconds_remaining`
- `turnover`
- `touchdown`
- `posteam`

There are currently 3 different game models that can be used by the simulation engine:
1. Prototype Model (`proto`)
3. Game Model V1 (`v1`)
4. Game Model V1a (`v1a`)

#### Prototype Model
[coming soon...]

#### V1 + V1a Model
[coming soon...]

### DB Details
---
[coming soon...]
