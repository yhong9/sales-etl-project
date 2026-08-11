from pathlib import Path
import pandas as pd
from sqlalchemy import text
from db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORDERS_FILE = (
    PROJECT_ROOT / "data" / "archive" / "olist_orders_dataset.csv"
)

EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

def extract_orders():
    orders = pd.read_csv(ORDERS_FILE,dtype=str)
    actual_columns = orders.columns.tolist()
    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected columns in the orders dataset. \n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Actual: {actual_columns}"
        )
    orders["source_file"] = ORDERS_FILE.name
    orders["loaded_at"] = pd.Timestamp.now(tz="UTC")
    print(f"Extracted {len(orders):,} rows from {ORDERS_FILE.name}")
    return orders

def load_raw_orders(orders):
    engine = get_engine()
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw.orders (
        order_id TEXT,
        customer_id TEXT,
        order_status TEXT,
        order_purchase_timestamp TEXT,
        order_approved_at TEXT,
        order_delivered_carrier_date TEXT,
        order_delivered_customer_date TEXT,
        order_estimated_delivery_date TEXT,
        source_file TEXT NOT NULL,
        loaded_at TIMESTAMPTZ NOT NULL
        );
    """
    with engine.begin() as connection:
        connection.execute(text(create_table_sql))
        connection.execute(
            text("TRUNCATE TABLE raw.orders;")
        )
        orders.to_sql(
            name="orders",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )

        database_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.orders;")
        ).scalar_one()

        source_file_count = len(orders)
        if database_count != source_file_count:
            raise ValueError(
                "Row count mismatch after loading data into raw.orders table. "
                f"CSV={source_file_count:,}, database={database_count:,}"
            )

        print(f"Loaded {database_count:,} rows into raw.orders table successfully.")
        print("Row count verification passed.")

def main():
    orders = extract_orders()
    load_raw_orders(orders)

if __name__ == "__main__":
    main()