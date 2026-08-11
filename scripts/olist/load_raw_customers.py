from pathlib import Path
import pandas as pd
from sqlalchemy import text
from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CUSTOMERS_FILE = (
    PROJECT_ROOT
    / "data"
    / "archive"
    / "olist_customers_dataset.csv"
)

EXPECTED_COLUMNS = [
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state",
]


def extract_customers():
    customers = pd.read_csv(CUSTOMERS_FILE, dtype=str)

    actual_columns = customers.columns.tolist()

    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected customers dataset columns. \n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Actual: {actual_columns}"
        )

    customers["source_file"] = CUSTOMERS_FILE.name
    customers["loaded_at"] = pd.Timestamp.now(tz="UTC")
    print(f"Extracted {len(customers):,} rows from {CUSTOMERS_FILE.name}")

    return customers

def load_raw_customers(customers):
    engine = get_engine()
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw.customers (
            customer_id TEXT,
            customer_unique_id TEXT,
            customer_zip_code_prefix TEXT,
            customer_city TEXT,
            customer_state TEXT,
            source_file TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
    """

    with engine.begin() as connection:
        connection.execute(text(create_table_sql))
        connection.execute(
            text("TRUNCATE TABLE raw.customers;")
        )
        customers.to_sql(
            name="customers",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )
        database_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.customers;")
        ).scalar_one()

    source_count = len(customers)

    if database_count!= source_count:
        raise ValueError(
            "Customers row count mismatch: "
            f"CSV={source_count:,}, database={database_count:,}"
        )

    print(f"Loaded {database_count:,} rows into raw.customers table successfully!")
    print("Row count verification passed.")

def main():
    customers = extract_customers()
    load_raw_customers(customers)

if __name__ == "__main__":
    main()