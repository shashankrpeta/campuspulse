import os
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# use SQLite by default - no setup needed
# to use PostgreSQL instead, set this env variable before running:
# export DATABASE_URL="postgresql://user:password@localhost:5432/campuspulse"
DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/campuspulse.db")


def get_engine():
    return create_engine(DB_URL)


def save_table(df, table_name):
    engine = get_engine()
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"saved '{table_name}' to db ({len(df)} rows)")


def load_table(table_name):
    engine = get_engine()
    return pd.read_sql_table(table_name, engine)
