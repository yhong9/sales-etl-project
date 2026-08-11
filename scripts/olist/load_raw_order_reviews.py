from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEWS_FILE = (
    PROJECT_ROOT
    / "data"
    / "archive"
    / "olist_order_reviews_dataset.csv"
)

EXPECTED_COLUMNS = [
    "review_id",
    "order_id",
    "review_score",
    "review_comment_title",
    "review_comment_message",
    "review_creation_date",
    "review_answer_timestamp",
]


def extract_order_reviews():
    reviews = pd.read_csv(
        REVIEWS_FILE,
        dtype="string",
    )

    actual_columns = reviews.columns.tolist()

    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            "Unexpected review columns.\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Actual:   {actual_columns}"
        )

    reviews["source_file"] = REVIEWS_FILE.name
    reviews["loaded_at"] = pd.Timestamp.now(tz="UTC")

    print(
        f"Extracted {len(reviews):,} rows "
        f"from {REVIEWS_FILE.name}"
    )

    return reviews


def load_raw_order_reviews(reviews):
    engine = get_engine()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw.order_reviews (
            review_id TEXT,
            order_id TEXT,
            review_score TEXT,
            review_comment_title TEXT,
            review_comment_message TEXT,
            review_creation_date TEXT,
            review_answer_timestamp TEXT,
            source_file TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
    """

    with engine.begin() as connection:
        connection.execute(text(create_table_sql))

        connection.execute(
            text("TRUNCATE TABLE raw.order_reviews;")
        )

        reviews.to_sql(
            name="order_reviews",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )

        database_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM raw.order_reviews;
            """)
        ).scalar_one()

    source_count = len(reviews)

    if database_count != source_count:
        raise ValueError(
            "Review row count mismatch: "
            f"CSV={source_count:,}, "
            f"database={database_count:,}"
        )

    print(
        f"Loaded {database_count:,} rows "
        "into raw.order_reviews successfully!"
    )
    print("Row count verification passed.")


def main():
    reviews = extract_order_reviews()
    load_raw_order_reviews(reviews)


if __name__ == "__main__":
    main()