import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

def get_engine():
    url=URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"]
    )
    return create_engine(url)

def test_connection():
    engine = get_engine()
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database();")
        ).scalar_one()

        postgres_version = connection.execute(
            text("SELECT version();")
        ).scalar_one()

    print("Database connection successful!")
    print(f"Connected to database: {database_name}")
    print(f"PostgreSQL version: {postgres_version}")


if __name__ == "__main__":
    test_connection()
