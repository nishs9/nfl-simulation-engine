from sqlalchemy import create_engine, text
from proj_secrets import db_username, db_password, db_name, alt_db_name
from typing import List, Dict, Tuple, Any
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def setup_db_connections() -> Tuple[object, object]:
    # Setup main and alternate db connections for data processing
    main_db_engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}', echo=True)
    main_db_conn = main_db_engine.connect()

    alt_db_engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@localhost/{alt_db_name}', echo=True)
    alt_db_conn = alt_db_engine.connect()

    return (main_db_conn, alt_db_conn)

if __name__ == '__main__':
    # Initialize database connections
    main_db_conn, alt_db_conn = setup_db_connections()

    # Load raw data from raw CSV
    raw_pbp_df = pd.read_csv("datasets/2024_NFL.csv")

    # Load raw player stats data from alternate database
    query = text("select * from player_stats_season_2024")
    results = alt_db_conn.execute(query)
    raw_player_stats_df = pd.DataFrame(results.fetchall(), columns=results.keys())

    print(raw_pbp_df.head())
    print(raw_player_stats_df.head())
