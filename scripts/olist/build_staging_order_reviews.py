from sqlalchemy import text

from db import get_engine


def build_staging_order_reviews():
    engine = get_engine()

    drop_table_sql = """
        DROP TABLE IF EXISTS staging.order_reviews;
    """

    create_table_sql = """
        CREATE TABLE staging.order_reviews AS
        WITH typed_reviews AS (
            SELECT
                NULLIF(
                    TRIM(review_id), ''
                ) AS review_id,

                NULLIF(
                    TRIM(order_id), ''
                ) AS order_id,

                NULLIF(
                    TRIM(review_score), ''
                )::INTEGER AS review_score,

                NULLIF(
                    TRIM(review_comment_title), ''
                ) AS review_comment_title,

                NULLIF(
                    TRIM(review_comment_message), ''
                ) AS review_comment_message,

                NULLIF(
                    TRIM(review_creation_date), ''
                )::TIMESTAMP AS review_creation_date,

                NULLIF(
                    TRIM(review_answer_timestamp), ''
                )::TIMESTAMP AS review_answer_timestamp,

                source_file,
                loaded_at

            FROM raw.order_reviews
        ),

        ranked_reviews AS (
            SELECT
                *,

                ROW_NUMBER() OVER (
                    PARTITION BY order_id
                    ORDER BY
                        review_answer_timestamp DESC,
                        review_creation_date DESC,
                        review_id DESC
                ) AS review_rank

            FROM typed_reviews
        )

        SELECT
            review_id,
            order_id,
            review_score,
            review_comment_title,
            review_comment_message,
            review_creation_date,
            review_answer_timestamp,

            CASE
                WHEN review_score >= 4
                    THEN TRUE
                ELSE FALSE
            END AS is_positive_review,

            CASE
                WHEN review_score <= 2
                    THEN TRUE
                ELSE FALSE
            END AS is_negative_review,

            CASE
                WHEN review_score = 3
                    THEN TRUE
                ELSE FALSE
            END AS is_neutral_review,

            CASE
                WHEN review_comment_title IS NOT NULL
                    OR review_comment_message IS NOT NULL
                    THEN TRUE
                ELSE FALSE
            END AS has_written_comment,

            source_file,
            loaded_at,
            CURRENT_TIMESTAMP AS staged_at

        FROM ranked_reviews
        WHERE review_rank = 1;
    """

    add_primary_key_sql = """
        ALTER TABLE staging.order_reviews
        ADD CONSTRAINT staging_order_reviews_pk
        PRIMARY KEY (order_id);
    """

    create_review_id_index_sql = """
        CREATE INDEX staging_order_reviews_review_id_idx
        ON staging.order_reviews (review_id);
    """

    create_score_index_sql = """
        CREATE INDEX staging_order_reviews_score_idx
        ON staging.order_reviews (review_score);
    """

    validation_sql = """
        SELECT
            COUNT(*) AS total_rows,

            COUNT(DISTINCT order_id)
                AS unique_orders,

            COUNT(DISTINCT review_id)
                AS unique_review_ids,

            ROUND(
                AVG(review_score)::NUMERIC,
                2
            ) AS average_review_score,

            COUNT(*) FILTER (
                WHERE is_positive_review = TRUE
            ) AS positive_reviews,

            COUNT(*) FILTER (
                WHERE is_neutral_review = TRUE
            ) AS neutral_reviews,

            COUNT(*) FILTER (
                WHERE is_negative_review = TRUE
            ) AS negative_reviews,

            COUNT(*) FILTER (
                WHERE has_written_comment = TRUE
            ) AS reviews_with_written_comment

        FROM staging.order_reviews;
    """

    source_unique_orders_sql = """
        SELECT COUNT(DISTINCT order_id)
        FROM raw.order_reviews;
    """

    unmatched_orders_sql = """
        SELECT COUNT(*)
        FROM staging.order_reviews AS reviews
        LEFT JOIN staging.orders AS orders
            ON reviews.order_id = orders.order_id
        WHERE orders.order_id IS NULL;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_table_sql))
        connection.execute(text(create_table_sql))
        connection.execute(text(add_primary_key_sql))
        connection.execute(
            text(create_review_id_index_sql)
        )
        connection.execute(text(create_score_index_sql))

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        source_unique_orders = connection.execute(
            text(source_unique_orders_sql)
        ).scalar_one()

        unmatched_orders = connection.execute(
            text(unmatched_orders_sql)
        ).scalar_one()

        if result["total_rows"] != source_unique_orders:
            raise ValueError(
                "Review deduplication count mismatch: "
                f"expected={source_unique_orders:,}, "
                f"actual={result['total_rows']:,}"
            )

        if (
            result["total_rows"]
            != result["unique_orders"]
        ):
            raise ValueError(
                "staging.order_reviews contains "
                "duplicate order_id values."
            )

        if unmatched_orders > 0:
            raise ValueError(
                f"Found {unmatched_orders:,} reviews "
                "without matching orders."
            )

    print("staging.order_reviews created successfully!")
    print(f"Review rows: {result['total_rows']:,}")
    print(
        f"Unique reviewed orders: "
        f"{result['unique_orders']:,}"
    )
    print(
        f"Average review score: "
        f"{result['average_review_score']}"
    )
    print(
        f"Positive reviews: "
        f"{result['positive_reviews']:,}"
    )
    print(
        f"Neutral reviews: "
        f"{result['neutral_reviews']:,}"
    )
    print(
        f"Negative reviews: "
        f"{result['negative_reviews']:,}"
    )
    print(
        "Reviews with written comments: "
        f"{result['reviews_with_written_comment']:,}"
    )
    print(f"Unmatched orders: {unmatched_orders:,}")
    print("Review staging validation passed!")


if __name__ == "__main__":
    build_staging_order_reviews()