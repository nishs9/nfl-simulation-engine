from sqlalchemy import create_engine
from proj_secrets import db_username, db_password, db_name, alt_db_name

connection_string = f'mysql+pymysql://{db_username}:{db_password}@localhost/{db_name}'
engine = create_engine(connection_string, echo=True)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")