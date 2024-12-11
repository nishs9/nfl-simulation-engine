from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from GameSimulator import run_multiple_simulations_with_statistics
from GameModels import PrototypeGameModel, GameModel_V1
import pandas as pd

app  = Flask(__name__)
CORS(app)

@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    data = request.get_json()
    home_team_abbrev = data['home_team']
    away_team_abbrev = data['away_team']
    num_simulations = int(data['num_simulations'])
    result_dict = run_multiple_simulations_with_statistics(home_team_abbrev, away_team_abbrev, num_simulations, game_model=GameModel_V1())
    return jsonify(result_dict)
    
if __name__ == '__main__':
    app.run(port=5000)