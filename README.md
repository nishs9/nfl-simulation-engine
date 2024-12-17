# NFL Simulation Engine
This is a custom simulation engine built to simulate hypothetical NFL games based on up-to-date real-world stats. It is an end-to-end webapp with a frontend
built using React.js with Material UI. For the backend, I built an API with Flask which is connected to a MySQL DB and a set of Python scripts
which contain the logic for the simulation engine itself.

At the moment, everything is hosted locally but I am actively working on deploying this project to the cloud. In addition, my goal is to also set the
project up such that anyone could clone this repository locally and run the app on their machines directly. 

Below is a screenshot of what the UI currently looks like:
<p align="center">
    <img src="https://github.com/user-attachments/assets/6aacf474-2d06-4e2f-a11d-f1ee12de180b" alt="frontend_screenshot" style="width:50%;">
</p>

For more info on how the model and project work, keep reading:

## Implementation Details

### Frontend
As you can tell from the screenshot above, the UI is not the main focus of this project. While I will likely add some additional visualizations for 
simulation results and try to clean up the look in general, what you currently see is pretty much going to be the UI layout for the timebeing and 
I don't have any major plans for it at the moment.

In a nutshell, it allows user to specify the 2 teams, set the number of simulations to run, and choose which game model to use (the concept of game model will
be expanded upon later in the doc). When the user clicks "Run Simulation" and after the results load, you see a pie chart representing the percentage of games
that were won by each team during the last simulation run. The stats table that is displayed is also an average of the various statistics over the course of the
simulation runs.

### Flask API
The majority of the logic for the flask app is contained within `backend/src/simulation_engine_api.py`. It has 2 simple endpoints:
- `/run-simulation`: This is the endpoint that the frontend calls when a user clicks "Run Simulation". It does some basic initialization of the objects
needed to run the simulations and the calls the multi-threaded simulation runner (located in `backend/src/game_simulator.py`). The API then responds with all of the 
details about the simulation results. This is a synchronous process.

- `/run-legacy-simulation`: This is an endpoint that isn't currently used but I simply created it as a failsafe in case I ever run into serious issues with the 
multi-threaded simulation runner. This endpoint simply calls the single-threaded version of the simulation runner and, otherwise, doesn't differ at all to the
main endpoint.

### Sim Engine Backend [this section is a work in progress]
As mentioned earlier, the API is connected to 2 main components: the database and the python scripts which contain the actual simulation logc. In this section,
I'll focus on running through the details about the python side of things. I will discuss the database details in a separate section later. 

For the engine itself, there are 3 main classes where the simulation logic is defined:
1. Team: This is an object that represents a team involved in a simulation. It has the following fields/attributes:
    - `name`: Team abbreviation
    - `stats`: Map containing all relevant team stats needed for the simulation
    - `off_passing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards gained on pass plays by the team
    - `off_rushing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards gained on run plays by the team
    - `def_passing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards allowed on pass plays by the team
    - `def_rushing_distribution`: This is a log-normal distribution which approximates the actual distribution of yards allowed on run plays by the team
        - NOTE: The 4 log-normal distributions are only used by the V1 game model at the moment (more info on that later)
2. AbstractGameModel: This is an abstract class that represents what simulation logic we want to use when running the game engine.
    - In order to create new game models, all we need to do is extend the AbstractGameModel class and implement the `resolve_play()` method which takes in a dictionary representation of the current game state and returns a dictionary representing the play result.
    - There are currently 2 models that implement this abstract class and I will discuss them in detail shortly.
3. GameEngine
    a.

#### Game Model Details
[coming soon...]

### DB Details
[coming soon...]