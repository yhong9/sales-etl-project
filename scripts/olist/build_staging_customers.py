from sqlalchemy import text

from db import get_engine


def build_staging_customers():
    engine = get_engine()

    drop_table_sql = """
        DROP TABLE IF EXISTS staging.customers;
    """

    create_table_sql = """
        CREATE TABLE staging.customers AS
        SELECT
            NULLIF(
                TRIM(customer_id), ''
            ) AS customer_id,

            NULLIF(
                TRIM(customer_unique_id), ''
            ) AS customer_unique_id,

            NULLIF(
                TRIM(customer_zip_code_prefix), ''
            ) AS customer_zip_code_prefix,

            LOWER(
                NULLIF(TRIM(customer_city), '')
            ) AS customer_city,

            UPPER(
                NULLIF(TRIM(customer_state), '')
            ) AS customer_state,

            source_file,
            loaded_at,
            CURRENT_TIMESTAMP AS staged_at

        FROM raw.customers;
    """

    add_primary_key_sql = """
        ALTER TABLE staging.customers
        ADD CONSTRAINT staging_customers_pk
        PRIMARY KEY (customer_id);
    """

    create_unique_customer_index_sql = """
        CREATE INDEX staging_customers_unique_id_idx
        ON staging.customers (customer_unique_id);
    """

    create_state_index_sql = """
        CREATE INDEX staging_customers_state_idx
        ON staging.customers (customer_state);
    """

    validation_sql = """
        SELECT
            COUNT(*) AS total_rows,

            COUNT(DISTINCT customer_id)
                AS unique_customer_ids,

            COUNT(DISTINCT customer_unique_id)
                AS unique_real_customers

        FROM staging.customers;
    """

    repeat_customers_sql = """
        SELECT COUNT(*)
        FROM (
            SELECT customer_unique_id
            FROM staging.customers
            GROUP BY customer_unique_id
            HAVING COUNT(*) > 1
        ) AS repeated_customers;
    """

    unmatched_orders_sql = """
        SELECT COUNT(*)
        FROM staging.orders AS orders
        LEFT JOIN staging.customers AS customers
            ON orders.customer_id = customers.customer_id
        WHERE customers.customer_id IS NULL;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_table_sql))
        connection.execute(text(create_table_sql))
        connection.execute(text(add_primary_key_sql))
        connection.execute(
            text(create_unique_customer_index_sql)
        )
        connection.execute(text(create_state_index_sql))

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        repeat_customers = connection.execute(
            text(repeat_customers_sql)
        ).scalar_one()

        unmatched_orders = connection.execute(
            text(unmatched_orders_sql)
        ).scalar_one()

        raw_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.customers;")
        ).scalar_one()

        staging_count = result["total_rows"]

        if raw_count != staging_count:
            raise ValueError(
                "Raw and staging customer counts do not match: "
                f"raw={raw_count:,}, "
                f"staging={staging_count:,}"
            )

        if unmatched_orders > 0:
            raise ValueError(
                f"Found {unmatched_orders:,} staging orders "
                "without a matching customer."
            )

    print("staging.customers created successfully!")
    print(f"Total rows: {result['total_rows']:,}")
    print(
        "Unique customer IDs: "
        f"{result['unique_customer_ids']:,}"
    )
    print(
        "Unique real customers: "
        f"{result['unique_real_customers']:,}"
    )
    print(
        "Real customers with multiple customer records: "
        f"{repeat_customers:,}"
    )
    print(f"Unmatched orders: {unmatched_orders:,}")
    print("Raw-to-staging validation passed!")


if __name__ == "__main__":
    build_staging_customers()