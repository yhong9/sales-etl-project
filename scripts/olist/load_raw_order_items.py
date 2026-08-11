from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORDER_ITEMS_FILE = (
    PROJECT_ROOT
    / "data"
    / "archive"
    / "olist_order_items_dataset.csv"
)

EXPECTED_COLUMNS = [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "shipping_limit_date",
    "price",
    "freight_value",
]


def extract_order_items():
    order_items = pd.read_csv(
        ORDER_ITEMS_FILE,
        dtype="string",
    )

    actual_columns = order_items.columns.tolist()

    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected order item columns.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Actual:   {actual_columns}"
        )

    order_items["source_file"] = ORDER_ITEMS_FILE.name
    order_items["loaded_at"] = pd.Timestamp.now(tz="UTC")

    print(
        f"Extracted {len(order_items):,} rows "
        f"from {ORDER_ITEMS_FILE.name}"
    )

    return order_items


def load_raw_order_items(order_items):
    engine = get_engine()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw.order_items (
            order_id TEXT,
            order_item_id TEXT,
            product_id TEXT,
            seller_id TEXT,
            shipping_limit_date TEXT,
            price TEXT,
            freight_value TEXT,
            source_file TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
    """

    with engine.begin() as connection:
        connection.execute(text(create_table_sql))

        connection.execute(
            text("TRUNCATE TABLE raw.order_items;")
        )

        order_items.to_sql(
            name="order_items",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )

        database_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.order_items;")
        ).scalar_one()

    source_count = len(order_items)

    if database_count != source_count:
        raise ValueError(
            "Order item row count mismatch: "
            f"CSV={source_count:,}, "
            f"database={database_count:,}"
        )

    print(
        f"Loaded {database_count:,} rows "
        "into raw.order_items successfully!"
    )
    print("Row count verification passed.")


def main():
    order_items = extract_order_items()
    load_raw_order_items(order_items)


if __name__ == "__main__":
    main()