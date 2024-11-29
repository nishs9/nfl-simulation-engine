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

    home_team = Team("KC", home_team_stats)
    away_team = Team("NYG", away_team_stats)
    

    kc_wins = 0
    i = 0
    while i < 1000:
        game_engine = GameEngine(home_team, away_team)
        game_summary = game_engine.run_simulation()
        print(game_summary)
        final_score = game_summary["final_score"]
        if final_score["KC"] > final_score["NYG"]:
            kc_wins += 1
        i += 1
    
    print(f"KC wins {kc_wins} out of 1000 games.")