from sqlalchemy import text

from db import get_engine


def build_fact_sales():
    engine = get_engine()

    drop_table_sql = """
        DROP TABLE IF EXISTS mart.fact_sales;
    """

    create_table_sql = """
        CREATE TABLE mart.fact_sales AS
        SELECT
            items.order_id,
            items.order_item_id,

            orders.customer_id,
            customers.customer_unique_id,

            items.product_id,
            items.seller_id,

            orders.order_status,
            orders.order_purchase_timestamp,
            DATE_TRUNC(
                'month',
                orders.order_purchase_timestamp
            )::DATE AS order_month,

            orders.order_delivered_customer_date,
            orders.order_estimated_delivery_date,
            orders.delivery_time_days,
            orders.is_late,

            customers.customer_zip_code_prefix,
            customers.customer_city,
            customers.customer_state,

            products.product_category_name,
            products.product_category_name_english,

            items.shipping_limit_date,
            items.price,
            items.freight_value,
            items.total_value,

            CURRENT_TIMESTAMP AS mart_created_at

        FROM staging.order_items AS items

        INNER JOIN staging.orders AS orders
            ON items.order_id = orders.order_id

        INNER JOIN staging.customers AS customers
            ON orders.customer_id = customers.customer_id

        INNER JOIN staging.products AS products
            ON items.product_id = products.product_id

        WHERE orders.order_status = 'delivered';
    """

    add_primary_key_sql = """
        ALTER TABLE mart.fact_sales
        ADD CONSTRAINT mart_fact_sales_pk
        PRIMARY KEY (order_id, order_item_id);
    """

    create_month_index_sql = """
        CREATE INDEX mart_fact_sales_month_idx
        ON mart.fact_sales (order_month);
    """

    create_state_index_sql = """
        CREATE INDEX mart_fact_sales_state_idx
        ON mart.fact_sales (customer_state);
    """

    create_category_index_sql = """
        CREATE INDEX mart_fact_sales_category_idx
        ON mart.fact_sales (
            product_category_name_english
        );
    """

    validation_sql = """
        SELECT
            COUNT(*) AS total_rows,

            COUNT(
                DISTINCT (order_id, order_item_id)
            ) AS unique_order_items,

            COUNT(DISTINCT order_id)
                AS total_orders,

            COUNT(DISTINCT customer_unique_id)
                AS total_customers,

            ROUND(SUM(price), 2)
                AS total_sales,

            ROUND(SUM(freight_value), 2)
                AS total_freight,

            ROUND(SUM(total_value), 2)
                AS total_transaction_value,

            ROUND(
                SUM(price)
                / COUNT(DISTINCT order_id),
                2
            ) AS average_order_sales,

            COUNT(*) FILTER (
                WHERE is_late = TRUE
            ) AS late_item_rows,

            COUNT(DISTINCT order_id) FILTER (
                WHERE is_late = TRUE
            ) AS late_orders

        FROM mart.fact_sales;
    """

    expected_count_sql = """
        SELECT COUNT(*)
        FROM staging.order_items AS items
        INNER JOIN staging.orders AS orders
            ON items.order_id = orders.order_id
        WHERE orders.order_status = 'delivered';
    """

    null_dimension_sql = """
        SELECT COUNT(*)
        FROM mart.fact_sales
        WHERE customer_unique_id IS NULL
           OR customer_state IS NULL
           OR product_id IS NULL
           OR product_category_name_english IS NULL;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_table_sql))
        connection.execute(text(create_table_sql))
        connection.execute(text(add_primary_key_sql))
        connection.execute(text(create_month_index_sql))
        connection.execute(text(create_state_index_sql))
        connection.execute(text(create_category_index_sql))

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        expected_count = connection.execute(
            text(expected_count_sql)
        ).scalar_one()

        null_dimensions = connection.execute(
            text(null_dimension_sql)
        ).scalar_one()

        if result["total_rows"] != expected_count:
            raise ValueError(
                "Fact table row count mismatch: "
                f"expected={expected_count:,}, "
                f"actual={result['total_rows']:,}"
            )

        if (
            result["total_rows"]
            != result["unique_order_items"]
        ):
            raise ValueError(
                "Duplicate composite keys found "
                "in mart.fact_sales."
            )

        if null_dimensions > 0:
            raise ValueError(
                f"Found {null_dimensions:,} fact rows "
                "with missing dimension values."
            )

    print("mart.fact_sales created successfully!")
    print(f"Fact rows: {result['total_rows']:,}")
    print(f"Orders: {result['total_orders']:,}")
    print(f"Customers: {result['total_customers']:,}")
    print(
        f"Total sales: "
        f"R$ {result['total_sales']:,.2f}"
    )
    print(
        f"Total freight: "
        f"R$ {result['total_freight']:,.2f}"
    )
    print(
        "Total transaction value: "
        f"R$ {result['total_transaction_value']:,.2f}"
    )
    print(
        "Average order sales: "
        f"R$ {result['average_order_sales']:,.2f}"
    )
    print(f"Late orders: {result['late_orders']:,}")
    print("Fact table validation passed!")


if __name__ == "__main__":
    build_fact_sales()