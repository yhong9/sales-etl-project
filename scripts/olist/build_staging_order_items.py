from sqlalchemy import text

from db import get_engine


def build_staging_order_items():
    engine = get_engine()

    drop_table_sql = """
        DROP TABLE IF EXISTS staging.order_items;
    """

    create_table_sql = """
        CREATE TABLE staging.order_items AS
        WITH typed_order_items AS (
            SELECT
                NULLIF(
                    TRIM(order_id), ''
                ) AS order_id,

                NULLIF(
                    TRIM(order_item_id), ''
                )::INTEGER AS order_item_id,

                NULLIF(
                    TRIM(product_id), ''
                ) AS product_id,

                NULLIF(
                    TRIM(seller_id), ''
                ) AS seller_id,

                NULLIF(
                    TRIM(shipping_limit_date), ''
                )::TIMESTAMP AS shipping_limit_date,

                NULLIF(
                    TRIM(price), ''
                )::NUMERIC(12, 2) AS price,

                NULLIF(
                    TRIM(freight_value), ''
                )::NUMERIC(12, 2) AS freight_value,

                source_file,
                loaded_at

            FROM raw.order_items
        )

        SELECT
            order_id,
            order_item_id,
            product_id,
            seller_id,
            shipping_limit_date,
            price,
            freight_value,

            (
                price + freight_value
            )::NUMERIC(12, 2) AS total_value,

            source_file,
            loaded_at,
            CURRENT_TIMESTAMP AS staged_at

        FROM typed_order_items;
    """

    add_primary_key_sql = """
        ALTER TABLE staging.order_items
        ADD CONSTRAINT staging_order_items_pk
        PRIMARY KEY (order_id, order_item_id);
    """

    create_order_index_sql = """
        CREATE INDEX staging_order_items_order_id_idx
        ON staging.order_items (order_id);
    """

    create_product_index_sql = """
        CREATE INDEX staging_order_items_product_id_idx
        ON staging.order_items (product_id);
    """

    create_seller_index_sql = """
        CREATE INDEX staging_order_items_seller_id_idx
        ON staging.order_items (seller_id);
    """

    validation_sql = """
        SELECT
            COUNT(*) AS total_rows,

            COUNT(
                DISTINCT (order_id, order_item_id)
            ) AS unique_order_items,

            COUNT(DISTINCT order_id)
                AS unique_orders,

            ROUND(SUM(price), 2)
                AS total_product_sales,

            ROUND(SUM(freight_value), 2)
                AS total_freight,

            ROUND(SUM(total_value), 2)
                AS total_value

        FROM staging.order_items;
    """

    unmatched_orders_sql = """
        SELECT COUNT(*)
        FROM staging.order_items AS items
        LEFT JOIN staging.orders AS orders
            ON items.order_id = orders.order_id
        WHERE orders.order_id IS NULL;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_table_sql))
        connection.execute(text(create_table_sql))
        connection.execute(text(add_primary_key_sql))
        connection.execute(text(create_order_index_sql))
        connection.execute(text(create_product_index_sql))
        connection.execute(text(create_seller_index_sql))

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        unmatched_orders = connection.execute(
            text(unmatched_orders_sql)
        ).scalar_one()

        raw_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.order_items;")
        ).scalar_one()

        staging_count = result["total_rows"]

        if raw_count != staging_count:
            raise ValueError(
                "Raw and staging order-item counts differ: "
                f"raw={raw_count:,}, "
                f"staging={staging_count:,}"
            )

        if unmatched_orders > 0:
            raise ValueError(
                f"Found {unmatched_orders:,} order items "
                "without a matching order."
            )

    print("staging.order_items created successfully!")
    print(f"Total rows: {result['total_rows']:,}")
    print(
        "Unique order items: "
        f"{result['unique_order_items']:,}"
    )
    print(
        f"Unique orders: {result['unique_orders']:,}"
    )
    print(
        "Total product sales: "
        f"R$ {result['total_product_sales']:,.2f}"
    )
    print(
        "Total freight: "
        f"R$ {result['total_freight']:,.2f}"
    )
    print(
        "Total value: "
        f"R$ {result['total_value']:,.2f}"
    )
    print(f"Unmatched orders: {unmatched_orders:,}")
    print("Raw-to-staging validation passed!")


if __name__ == "__main__":
    build_staging_order_items()