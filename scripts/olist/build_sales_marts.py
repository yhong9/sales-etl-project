from decimal import Decimal

from sqlalchemy import text

from db import get_engine


def build_sales_marts():
    engine = get_engine()

    drop_tables_sql = """
        DROP TABLE IF EXISTS mart.monthly_sales;
        DROP TABLE IF EXISTS mart.state_sales;
        DROP TABLE IF EXISTS mart.category_sales;
    """

    create_monthly_sales_sql = """
        CREATE TABLE mart.monthly_sales AS
        SELECT
            order_month,

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

            COUNT(DISTINCT order_id) FILTER (
                WHERE is_late = TRUE
            ) AS late_orders

        FROM mart.fact_sales
        GROUP BY order_month;
    """

    create_state_sales_sql = """
        CREATE TABLE mart.state_sales AS
        SELECT
            customer_state,

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
            ) AS average_order_sales

        FROM mart.fact_sales
        GROUP BY customer_state;
    """

    create_category_sales_sql = """
        CREATE TABLE mart.category_sales AS
        SELECT
            product_category_name_english
                AS product_category,

            COUNT(DISTINCT order_id)
                AS total_orders,

            COUNT(DISTINCT product_id)
                AS total_products,

            ROUND(SUM(price), 2)
                AS total_sales,

            ROUND(SUM(freight_value), 2)
                AS total_freight,

            ROUND(SUM(total_value), 2)
                AS total_transaction_value,

            ROUND(AVG(price), 2)
                AS average_item_price

        FROM mart.fact_sales
        GROUP BY product_category_name_english;
    """

    add_keys_sql = """
        ALTER TABLE mart.monthly_sales
        ADD CONSTRAINT mart_monthly_sales_pk
        PRIMARY KEY (order_month);

        ALTER TABLE mart.state_sales
        ADD CONSTRAINT mart_state_sales_pk
        PRIMARY KEY (customer_state);

        ALTER TABLE mart.category_sales
        ADD CONSTRAINT mart_category_sales_pk
        PRIMARY KEY (product_category);
    """

    validation_sql = """
        SELECT
            (SELECT ROUND(SUM(price), 2)
             FROM mart.fact_sales)
                AS fact_sales,

            (SELECT ROUND(SUM(total_sales), 2)
             FROM mart.monthly_sales)
                AS monthly_sales,

            (SELECT ROUND(SUM(total_sales), 2)
             FROM mart.state_sales)
                AS state_sales,

            (SELECT ROUND(SUM(total_sales), 2)
             FROM mart.category_sales)
                AS category_sales,

            (SELECT COUNT(*)
             FROM mart.monthly_sales)
                AS month_count,

            (SELECT COUNT(*)
             FROM mart.state_sales)
                AS state_count,

            (SELECT COUNT(*)
             FROM mart.category_sales)
                AS category_count;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_tables_sql))
        connection.execute(text(create_monthly_sales_sql))
        connection.execute(text(create_state_sales_sql))
        connection.execute(text(create_category_sales_sql))
        connection.execute(text(add_keys_sql))

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        fact_sales = result["fact_sales"]

        totals_to_check = {
            "monthly_sales": result["monthly_sales"],
            "state_sales": result["state_sales"],
            "category_sales": result["category_sales"],
        }

        for table_name, total in totals_to_check.items():
            if total != fact_sales:
                raise ValueError(
                    f"{table_name} does not reconcile "
                    "with mart.fact_sales: "
                    f"fact={fact_sales}, mart={total}"
                )

    print("Sales marts created successfully!")
    print(f"Months: {result['month_count']:,}")
    print(f"States: {result['state_count']:,}")
    print(
        f"Product categories: "
        f"{result['category_count']:,}"
    )
    print(
        f"Reconciled total sales: "
        f"R$ {fact_sales:,.2f}"
    )
    print("All sales totals reconcile!")


if __name__ == "__main__":
    build_sales_marts()