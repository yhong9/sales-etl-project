from sqlalchemy import text

from db import get_engine


def build_review_marts():
    engine = get_engine()

    drop_tables = [
        "DROP TABLE IF EXISTS mart.review_distribution;",
        "DROP TABLE IF EXISTS mart.monthly_reviews;",
        "DROP TABLE IF EXISTS mart.delivery_review_summary;",
        "DROP TABLE IF EXISTS mart.review_kpis;",
        "DROP TABLE IF EXISTS mart.order_reviews;",
    ]

    create_order_reviews_sql = """
        CREATE TABLE mart.order_reviews AS
        SELECT
            reviews.order_id,
            reviews.review_id,
            reviews.review_score,
            reviews.review_creation_date,
            reviews.review_answer_timestamp,
            reviews.is_positive_review,
            reviews.is_neutral_review,
            reviews.is_negative_review,
            reviews.has_written_comment,

            orders.order_status,
            orders.order_purchase_timestamp,

            DATE_TRUNC(
                'month',
                orders.order_purchase_timestamp
            )::DATE AS order_month,

            orders.delivery_time_days,
            orders.is_late,

            customers.customer_unique_id,
            customers.customer_state,

            CURRENT_TIMESTAMP AS mart_created_at

        FROM staging.order_reviews AS reviews

        INNER JOIN staging.orders AS orders
            ON reviews.order_id = orders.order_id

        INNER JOIN staging.customers AS customers
            ON orders.customer_id = customers.customer_id;
    """

    add_order_reviews_key_sql = """
        ALTER TABLE mart.order_reviews
        ADD CONSTRAINT mart_order_reviews_pk
        PRIMARY KEY (order_id);
    """

    create_review_kpis_sql = """
        CREATE TABLE mart.review_kpis AS
        SELECT
            COUNT(*) AS reviewed_orders,

            ROUND(
                AVG(review_score)::NUMERIC,
                2
            ) AS average_review_score,

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE is_positive_review = TRUE
                    ) * 100.0
                    / COUNT(*)
                )::NUMERIC,
                2
            ) AS positive_review_rate,

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE is_negative_review = TRUE
                    ) * 100.0
                    / COUNT(*)
                )::NUMERIC,
                2
            ) AS negative_review_rate,

            COUNT(*) FILTER (
                WHERE has_written_comment = TRUE
            ) AS written_comment_count

        FROM mart.order_reviews
        WHERE order_status = 'delivered';
    """

    create_distribution_sql = """
        CREATE TABLE mart.review_distribution AS
        SELECT
            review_score,

            COUNT(*) AS review_count,

            ROUND(
                (
                    COUNT(*) * 100.0
                    / SUM(COUNT(*)) OVER ()
                )::NUMERIC,
                2
            ) AS review_percentage

        FROM mart.order_reviews
        WHERE order_status = 'delivered'
        GROUP BY review_score;
    """

    create_monthly_reviews_sql = """
        CREATE TABLE mart.monthly_reviews AS
        SELECT
            order_month,

            COUNT(*) AS reviewed_orders,

            ROUND(
                AVG(review_score)::NUMERIC,
                2
            ) AS average_review_score,

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE is_positive_review = TRUE
                    ) * 100.0
                    / COUNT(*)
                )::NUMERIC,
                2
            ) AS positive_review_rate,

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE is_negative_review = TRUE
                    ) * 100.0
                    / COUNT(*)
                )::NUMERIC,
                2
            ) AS negative_review_rate

        FROM mart.order_reviews
        WHERE order_status = 'delivered'
        GROUP BY order_month;
    """

    create_delivery_summary_sql = """
        CREATE TABLE mart.delivery_review_summary AS
        SELECT
            CASE
                WHEN is_late IS NULL
                    THEN 'unknown'
                WHEN is_late = TRUE
                    THEN 'late'
                ELSE 'on_time'
            END AS delivery_status,

            COUNT(*) AS reviewed_orders,

            ROUND(
                AVG(review_score)::NUMERIC,
                2
            ) AS average_review_score,

            ROUND(
                (
                    COUNT(*) FILTER (
                        WHERE is_negative_review = TRUE
                    ) * 100.0
                    / COUNT(*)
                )::NUMERIC,
                2
            ) AS negative_review_rate

        FROM mart.order_reviews
        WHERE order_status = 'delivered'
        GROUP BY delivery_status;
    """

    add_summary_keys_sql = [
        """
            ALTER TABLE mart.review_distribution
            ADD CONSTRAINT mart_review_distribution_pk
            PRIMARY KEY (review_score);
        """,
        """
            ALTER TABLE mart.monthly_reviews
            ADD CONSTRAINT mart_monthly_reviews_pk
            PRIMARY KEY (order_month);
        """,
        """
            ALTER TABLE mart.delivery_review_summary
            ADD CONSTRAINT mart_delivery_review_summary_pk
            PRIMARY KEY (delivery_status);
        """,
    ]

    validation_sql = """
        SELECT
            (
                SELECT COUNT(*)
                FROM mart.order_reviews
                WHERE order_status = 'delivered'
            ) AS delivered_reviewed_orders,

            (
                SELECT SUM(review_count)
                FROM mart.review_distribution
            ) AS distribution_total,

            (
                SELECT SUM(reviewed_orders)
                FROM mart.monthly_reviews
            ) AS monthly_total,

            (
                SELECT SUM(reviewed_orders)
                FROM mart.delivery_review_summary
            ) AS delivery_total;
    """

    with engine.begin() as connection:
        for statement in drop_tables:
            connection.execute(text(statement))

        connection.execute(text(create_order_reviews_sql))
        connection.execute(text(add_order_reviews_key_sql))
        connection.execute(text(create_review_kpis_sql))
        connection.execute(text(create_distribution_sql))
        connection.execute(text(create_monthly_reviews_sql))
        connection.execute(text(create_delivery_summary_sql))

        for statement in add_summary_keys_sql:
            connection.execute(text(statement))

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        expected_total = result["delivered_reviewed_orders"]

        for name in [
            "distribution_total",
            "monthly_total",
            "delivery_total",
        ]:
            if result[name] != expected_total:
                raise ValueError(
                    f"{name} does not reconcile: "
                    f"expected={expected_total:,}, "
                    f"actual={result[name]:,}"
                )

        kpis = connection.execute(
            text("SELECT * FROM mart.review_kpis;")
        ).mappings().one()

    print("Review marts created successfully!")
    print(
        f"Reviewed delivered orders: "
        f"{kpis['reviewed_orders']:,}"
    )
    print(
        f"Average score: "
        f"{kpis['average_review_score']}"
    )
    print(
        f"Positive review rate: "
        f"{kpis['positive_review_rate']}%"
    )
    print(
        f"Negative review rate: "
        f"{kpis['negative_review_rate']}%"
    )
    print(
        f"Written comments: "
        f"{kpis['written_comment_count']:,}"
    )
    print("All review marts reconcile!")


if __name__ == "__main__":
    build_review_marts()