import os

import pytest
from sqlalchemy import text

from build_staging_order_reviews import (
    build_staging_order_reviews,
)
from db import get_engine

#将测试标记为integration， 没有安全开关时自动skip
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("RUN_INTEGRATION_TESTS")!="1",
        reason=(
            "Integration tests require an isolated "
            "PostgreSQL test database."
        ),
    ),
]

@pytest.fixture
def postgres_engine():
    engine = get_engine()

    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database();")
        ).scalar_one()

    if database_name != "olist_test":
        engine.dispose()
        raise RuntimeError(
            "Integration tests may only run against "
            f"olist_test, not {database_name!r}."
        )

    with engine.begin() as connection:
        connection.execute(
            text("DROP SCHEMA IF EXISTS staging CASCADE;")
        )
        connection.execute(
            text("DROP SCHEMA IF EXISTS raw CASCADE;")
        )
        connection.execute(
            text("CREATE SCHEMA raw;")
        )
        connection.execute(
            text("CREATE SCHEMA staging;")
        )

        connection.execute(
            text("""
                CREATE TABLE raw.order_reviews(
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
            """)
        )
        connection.execute(
                    text("""
                        CREATE TABLE staging.orders(
                            order_id TEXT PRIMARY KEY
                        );
                    """)
                )

    yield engine

    with engine.begin() as connection:
        connection.execute(
            text("DROP SCHEMA IF EXISTS staging CASCADE;")
        )

        connection.execute(
            text("DROP SCHEMA IF EXISTS raw CASCADE;")
        )
    engine.dispose()

def test_staging_keeps_latest_review_per_order(
        postgres_engine,
):
    reviews = [
        {
            "review_id": "review-old",
            "order_id": "order-1",
            "review_score": "1",
            "review_comment_title": None,
            "review_comment_message": "Original review",
            "review_creation_date": "2018-01-01 00:00:00",
            "review_answer_timestamp": "2018-01-02 10:00:00",
        },
        {
            "review_id": "review-new",
            "order_id": "order-1",
            "review_score": "5",
            "review_comment_title": "Updated review",
            "review_comment_message": None,
            "review_creation_date": "2018-01-01 00:00:00",
            "review_answer_timestamp": "2018-01-03 10:00:00",
        },
        {
            "review_id": "review-neutral",
            "order_id": "order-2",
            "review_score": "3",
            "review_comment_title": None,
            "review_comment_message": None,
            "review_creation_date": "2018-01-02 00:00:00",
            "review_answer_timestamp": "2018-01-04 10:00:00",
        },
    ]

    with postgres_engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO staging.orders (order_id)
                VALUES ('order-1'), ('order-2');
            """)
        )

        connection.execute(
            text("""
                INSERT INTO raw.order_reviews (
                    review_id,
                    order_id,
                    review_score,
                    review_comment_title,
                    review_comment_message,
                    review_creation_date,
                    review_answer_timestamp,
                    source_file,
                    loaded_at
                )
                VALUES (
                    :review_id,
                    :order_id,
                    :review_score,
                    :review_comment_title,
                    :review_comment_message,
                    :review_creation_date,
                    :review_answer_timestamp,
                    'integration-test.csv',
                    CURRENT_TIMESTAMP
                );
            """),
            reviews,
        )

    build_staging_order_reviews()
    
    with postgres_engine.connect() as connection:
        staged_reviews = connection.execute(
            text("""
                SELECT
                    review_id,
                    order_id,
                    review_score,
                    is_positive_review,
                    is_negative_review,
                    is_neutral_review,
                    has_written_comment
                FROM staging.order_reviews
                ORDER BY order_id;
            """)
        ).mappings().all()

        assert len(staged_reviews) == 2

    first_review = staged_reviews[0]
    second_review = staged_reviews[1]

    assert first_review["order_id"] == "order-1"
    assert first_review["review_id"] == "review-new"
    assert first_review["review_score"] == 5
    assert first_review["is_positive_review"] is True
    assert first_review["is_negative_review"] is False
    assert first_review["has_written_comment"] is True

    assert second_review["order_id"] == "order-2"
    assert second_review["review_id"] == "review-neutral"
    assert second_review["review_score"] == 3
    assert second_review["is_neutral_review"] is True
    assert second_review["has_written_comment"] is False