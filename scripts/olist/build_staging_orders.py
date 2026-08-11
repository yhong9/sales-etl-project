from sqlalchemy import text
from db import get_engine

def build_staging_orders():
    engine=get_engine()
    drop_table_sql = "DROP TABLE IF EXISTS staging.orders;"
    create_table_sql = """
        CREATE TABLE staging.orders AS
        WITH typed_orders AS (
            SELECT
                TRIM(order_id) AS order_id,
                TRIM(customer_id) AS customer_id,
                LOWER(TRIM(order_status)) AS order_status,

                NULLIF(TRIM(order_purchase_timestamp), '')::TIMESTAMPTZ AS order_purchase_timestamp,
                NULLIF(TRIM(order_approved_at), '')::TIMESTAMPTZ AS order_approved_at,
                NULLIF(TRIM(order_delivered_carrier_date), '')::TIMESTAMPTZ AS order_delivered_carrier_date,
                NULLIF(TRIM(order_delivered_customer_date), '')::TIMESTAMPTZ AS order_delivered_customer_date,
                NULLIF(TRIM(order_estimated_delivery_date), '')::TIMESTAMPTZ AS order_estimated_delivery_date,

                source_file,
                loaded_at
            FROM raw.orders
        )
        SELECT
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date,

            CASE
                WHEN order_delivered_customer_date IS NULL OR order_purchase_timestamp IS NULL THEN NULL
                ELSE ROUND(
                    (
                        EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp)) / 86400
                    )::NUMERIC, 2
                )
            END AS delivery_time_days,

            CASE
                WHEN order_delivered_customer_date IS NULL OR order_estimated_delivery_date IS NULL THEN NULL
                WHEN order_delivered_customer_date > order_estimated_delivery_date THEN TRUE
                ELSE FALSE
            END AS is_late,

            source_file,
            loaded_at,
            CURRENT_TIMESTAMP AS staged_at
        FROM typed_orders;
    """

    add_primary_key_sql = """
        ALTER TABLE staging.orders
        ADD CONSTRAINT staging_orders_pk PRIMARY KEY (order_id);
    """

    create_customer_index_sql = """
        CREATE INDEX staging_orders_customer_id_idx ON staging.orders (customer_id);
    """

    create_purchase_date_index_sql = """
        CREATE INDEX staging_orders_purchase_date_idx ON staging.orders (order_purchase_timestamp);
    """

    validation_sql = """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT order_id) AS unique_orders,
            COUNT(*) FILTER(WHERE order_status = 'delivered') AS delivered_orders,
            COUNT(*) FILTER(WHERE is_late = TRUE) AS late_deliveries,
            COUNT(*) FILTER(WHERE order_status = 'delivered' AND is_late IS NULL) AS delivered_orders_without_delivery_result
        FROM staging.orders;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_table_sql))
        connection.execute(text(create_table_sql))
        connection.execute(text(add_primary_key_sql))
        connection.execute(text(create_customer_index_sql))
        connection.execute(text(create_purchase_date_index_sql))

        result = connection.execute(text(validation_sql)).mappings().one()

        raw_count = connection.execute(text("SELECT COUNT(*) FROM raw.orders;")).scalar_one()
        staging_count = result["total_rows"]

        if raw_count != staging_count:
            raise ValueError(
                "Raw and staging orders count mismatch: "
                f"raw={raw_count}, staging={staging_count}"
            )

    print("Staging orders table built successfully!")
    print(f"Total rows: {result['total_rows']:,}")
    print(f"Unique orders: {result['unique_orders']:,}")
    print(f"Delivered orders: {result['delivered_orders']:,}")
    print(f"Late deliveries: {result['late_deliveries']:,}")
    print(
        f"Delivered orders without delivery result: "
        f"{result['delivered_orders_without_delivery_result']:,}")
    print("Raw-to-staging row count verification passed.")

if __name__ == "__main__":
    build_staging_orders()