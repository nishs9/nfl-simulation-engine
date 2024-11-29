from sqlalchemy import create_engine, text, Connection
from proj_secrets import db_username, db_password, db_name
import pandas as pd
from Team import Team
from GameEngine import GameEngine

if __name__ == "__main__":
    main_db_engine = create_engine(f"mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}")
    main_db_conn = main_db_engine.connect()

    home_team_query = text("select * from sim_engine_team_stats_2024 where team = 'ATL'")
    home_team_results = main_db_conn.execute(home_team_query)
    home_team_df = pd.DataFrame(home_team_results.fetchall(), columns=home_team_results.keys())
    home_team_stats = home_team_df.iloc[0].to_dict()

    away_team_query = text("select * from sim_engine_team_stats_2024 where team = 'SEA'")
    away_team_results = main_db_conn.execute(away_team_query)
    away_team_df = pd.DataFrame(away_team_results.fetchall(), columns=away_team_results.keys())
    away_team_stats = away_team_df.iloc[0].to_dict()

    home_team = Team("WAS", home_team_stats)
    away_team = Team("CAR", away_team_stats)
    

    home_wins = 0
    i = 0
    num_simulations = 10000
    while i < num_simulations:
        game_engine = GameEngine(home_team, away_team)
        game_summary = game_engine.run_simulation()
        print(game_summary)
        final_score = game_summary["final_score"]
        if final_score[home_team.name] > final_score[away_team.name]:
            home_wins += 1
        i += 1
    
    print(f"{home_team.name} wins {round(100 * (home_wins/num_simulations), 2)} percent of the time.")