from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from game_simulator import run_multiple_simulations_with_statistics, run_multiple_simulations_multi_threaded
from GameModels import PrototypeGameModel, GameModel_V1, GameModel_V1a
from time import time
import pandas as pd

app  = Flask(__name__)
CORS(app)

model_str_to_model = {
    "proto": PrototypeGameModel(),
    "v1": GameModel_V1(),
    "v1a": GameModel_V1a()
}

# Runs the simulation engine in the deafult multi-threaded mode
@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    start_time = time()
    data = request.get_json()
    home_team_abbrev = data['home_team']
    away_team_abbrev = data['away_team']
    num_simulations = int(data['num_simulations'])
    game_model = model_str_to_model[data["game_model"]]
    result_dict = run_multiple_simulations_multi_threaded(home_team_abbrev, away_team_abbrev, num_simulations, game_model=game_model)
    end_time = time()
    print(f"\nSimulation took {end_time - start_time} seconds on the backend!")
    return jsonify(result_dict)

# Runs the simulation engine in a single-threaded mode; only meant for debugging purposes
@app.route('/run-legacy-simulation', methods=['POST'])
def run_legacy_simulation():
    data = request.get_json()
    home_team_abbrev = data['home_team']
    away_team_abbrev = data['away_team']
    num_simulations = int(data['num_simulations'])
    game_model = model_str_to_model[data["game_model"]]
    result_dict = run_multiple_simulations_with_statistics(home_team_abbrev, away_team_abbrev, num_simulations, game_model=game_model)
    return jsonify(result_dict)
    
if __name__ == '__main__':
    app.run(port=5000)