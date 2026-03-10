import os
from sqlalchemy import create_engine
import psycopg2
from psycopg2 import sql

# Database configuration - adjust as needed or load from environment
DB_NAME = os.getenv("DB_NAME", "forecast")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")


def get_connection():
    """Return a new psycopg2 connection using the configured credentials."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
    )


def get_engine():
    """Return a SQLAlchemy engine for the configured database."""
    conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    return create_engine(conn_str)


def ensure_predictions_table():
    """Create the predictions table if it doesn't already exist."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    day_of_week TEXT,
                    meal_type TEXT,
                    food_item TEXT,
                    popularity_index REAL,
                    predicted_students INTEGER,
                    suggested_quantity INTEGER,
                    waste_risk TEXT
                )
            """
            )
        )


def ensure_actuals_table():
    """Create the actuals table if it doesn't already exist."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS actuals (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    date DATE,
                    meal_type TEXT,
                    food_item TEXT,
                    actual_students INTEGER,
                    actual_quantity REAL,
                    quantity_wasted REAL,
                    quantity_sold REAL
                )
            """
            )
        )
