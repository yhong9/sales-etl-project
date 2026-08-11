import pandas as pd
from sqlalchemy import text

from db import get_engine


REQUIRED_COLUMNS = [
    "order_id",
    "order_item_id",
    "product_id",
    "seller_id",
    "shipping_limit_date",
    "price",
    "freight_value",
]


def read_raw_data():
    engine = get_engine()

    with engine.connect() as connection:
        order_items = pd.read_sql_query(
            text("SELECT * FROM raw.order_items;"),
            connection,
        )

        orders = pd.read_sql_query(
            text("""
                SELECT order_id
                FROM raw.orders;
            """),
            connection,
        )

    print(
        f"Read {len(order_items):,} rows "
        "from raw.order_items"
    )

    return order_items, orders


def check_raw_order_items(order_items, orders):
    checks = []

    def add_check(check_name, issue_count, severity):
        checks.append(
            {
                "source_table": "raw.order_items",
                "check_name": check_name,
                "issue_count": int(issue_count),
                "severity": severity,
            }
        )

    add_check(
        "total_rows",
        len(order_items),
        "info",
    )

    add_check(
        "unique_orders_with_items",
        order_items["order_id"].nunique(),
        "info",
    )

    for column in REQUIRED_COLUMNS:
        add_check(
            f"missing_{column}",
            order_items[column].isna().sum(),
            "critical",
        )

    # 一条明细由 order_id + order_item_id 唯一确定。
    duplicate_composite_key = order_items.duplicated(
        subset=["order_id", "order_item_id"],
        keep=False,
    )

    add_check(
        "duplicate_order_id_order_item_id",
        duplicate_composite_key.sum(),
        "critical",
    )

    # order_item_id 应当是大于零的整数。
    numeric_item_ids = pd.to_numeric(
        order_items["order_item_id"],
        errors="coerce",
    )

    invalid_item_ids = (
        order_items["order_item_id"].notna()
        & (
            numeric_item_ids.isna()
            | numeric_item_ids.le(0)
            | numeric_item_ids.mod(1).ne(0)
        )
    )

    add_check(
        "invalid_order_item_id",
        invalid_item_ids.sum(),
        "high",
    )

    # 检查发货期限格式。
    shipping_dates = pd.to_datetime(
        order_items["shipping_limit_date"],
        errors="coerce",
        format="mixed",
    )

    invalid_shipping_dates = (
        order_items["shipping_limit_date"].notna()
        & shipping_dates.isna()
    )

    add_check(
        "invalid_shipping_limit_date",
        invalid_shipping_dates.sum(),
        "high",
    )

    # 检查价格。
    numeric_prices = pd.to_numeric(
        order_items["price"],
        errors="coerce",
    )

    invalid_prices = (
        order_items["price"].notna()
        & numeric_prices.isna()
    )

    add_check(
        "invalid_price",
        invalid_prices.sum(),
        "critical",
    )

    add_check(
        "negative_price",
        numeric_prices.lt(0).sum(),
        "critical",
    )

    # 检查运费。
    numeric_freight = pd.to_numeric(
        order_items["freight_value"],
        errors="coerce",
    )

    invalid_freight = (
        order_items["freight_value"].notna()
        & numeric_freight.isna()
    )

    add_check(
        "invalid_freight_value",
        invalid_freight.sum(),
        "critical",
    )

    add_check(
        "negative_freight_value",
        numeric_freight.lt(0).sum(),
        "critical",
    )

    # 检查每条商品明细是否能匹配订单。
    known_order_ids = set(
        orders["order_id"].dropna()
    )

    unmatched_order_ids = (
        order_items["order_id"].notna()
        & ~order_items["order_id"].isin(known_order_ids)
    )

    add_check(
        "unmatched_order_id",
        unmatched_order_ids.sum(),
        "critical",
    )

    return pd.DataFrame(checks)


def print_quality_report(quality_report):
    print("\nQuality Report for raw.order_items")
    print("-" * 70)
    print(quality_report.to_string(index=False))

    actual_issues = quality_report[
        (quality_report["severity"] != "info")
        & (quality_report["issue_count"] > 0)
    ]

    print()

    if actual_issues.empty:
        print("No order item data quality issues found.")
    else:
        print(
            f"Found {len(actual_issues)} "
            "order-item quality checks with issues."
        )


def main():
    order_items, orders = read_raw_data()

    quality_report = check_raw_order_items(
        order_items,
        orders,
    )

    print_quality_report(quality_report)


if __name__ == "__main__":
    main()