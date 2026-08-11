import pandas as pd
from sqlalchemy import text

from db import get_engine


NUMERIC_PRODUCT_COLUMNS = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]


def read_raw_data():
    engine = get_engine()

    with engine.connect() as connection:
        products = pd.read_sql_query(
            text("SELECT * FROM raw.products;"),
            connection,
        )

        translations = pd.read_sql_query(
            text("""
                SELECT *
                FROM raw.product_category_translation;
            """),
            connection,
        )

        order_items = pd.read_sql_query(
            text("""
                SELECT product_id
                FROM raw.order_items;
            """),
            connection,
        )

    print(f"Read {len(products):,} products")
    print(f"Read {len(translations):,} category translations")

    return products, translations, order_items


def check_raw_products(
    products,
    translations,
    order_items,
):
    checks = []

    def add_check(
        source_table,
        check_name,
        issue_count,
        severity,
    ):
        checks.append(
            {
                "source_table": source_table,
                "check_name": check_name,
                "issue_count": int(issue_count),
                "severity": severity,
            }
        )

    add_check(
        "raw.products",
        "total_rows",
        len(products),
        "info",
    )

    add_check(
        "raw.products",
        "unique_product_ids",
        products["product_id"].nunique(),
        "info",
    )

    add_check(
        "raw.products",
        "missing_product_id",
        products["product_id"].isna().sum(),
        "critical",
    )

    add_check(
        "raw.products",
        "duplicate_product_id",
        products["product_id"]
        .duplicated(keep=False)
        .sum(),
        "critical",
    )

    add_check(
        "raw.products",
        "missing_product_category_name",
        products["product_category_name"].isna().sum(),
        "medium",
    )

    for column in NUMERIC_PRODUCT_COLUMNS:
        numeric_values = pd.to_numeric(
            products[column],
            errors="coerce",
        )

        invalid_values = (
            products[column].notna()
            & numeric_values.isna()
        )

        add_check(
            "raw.products",
            f"invalid_{column}",
            invalid_values.sum(),
            "high",
        )

        add_check(
            "raw.products",
            f"negative_{column}",
            numeric_values.lt(0).sum(),
            "high",
        )

    # 订单明细里的商品必须存在于商品表。
    known_product_ids = set(
        products["product_id"].dropna()
    )

    unmatched_order_items = (
        order_items["product_id"].notna()
        & ~order_items["product_id"].isin(
            known_product_ids
        )
    )

    add_check(
        "raw.order_items",
        "unmatched_product_id",
        unmatched_order_items.sum(),
        "critical",
    )

    # 翻译表检查。
    add_check(
        "raw.product_category_translation",
        "total_rows",
        len(translations),
        "info",
    )

    add_check(
        "raw.product_category_translation",
        "duplicate_category_name",
        translations["product_category_name"]
        .duplicated(keep=False)
        .sum(),
        "critical",
    )

    add_check(
        "raw.product_category_translation",
        "missing_category_name",
        translations["product_category_name"]
        .isna()
        .sum(),
        "critical",
    )

    add_check(
        "raw.product_category_translation",
        "missing_english_category_name",
        translations["product_category_name_english"]
        .isna()
        .sum(),
        "high",
    )

    translated_categories = set(
        translations["product_category_name"]
        .dropna()
    )

    categories_without_translation = (
        products["product_category_name"].notna()
        & ~products["product_category_name"].isin(
            translated_categories
        )
    )

    add_check(
        "raw.products",
        "products_without_category_translation",
        categories_without_translation.sum(),
        "medium",
    )

    return pd.DataFrame(checks)


def print_quality_report(quality_report):
    print("\nProduct Quality Report")
    print("-" * 78)
    print(quality_report.to_string(index=False))

    actual_issues = quality_report[
        (quality_report["severity"] != "info")
        & (quality_report["issue_count"] > 0)
    ]

    print()

    if actual_issues.empty:
        print("No product data quality issues found.")
    else:
        print("Checks containing issues:")
        print(actual_issues.to_string(index=False))


def main():
    products, translations, order_items = read_raw_data()

    quality_report = check_raw_products(
        products,
        translations,
        order_items,
    )

    print_quality_report(quality_report)


if __name__ == "__main__":
    main()