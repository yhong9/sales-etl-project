import pandas as pd
from sqlalchemy import text

from db import get_engine


def read_raw_data():
    engine = get_engine()

    with engine.connect() as connection:
        reviews = pd.read_sql_query(
            text("SELECT * FROM raw.order_reviews;"),
            connection,
        )

        orders = pd.read_sql_query(
            text("SELECT order_id FROM raw.orders;"),
            connection,
        )

    print(
        f"Read {len(reviews):,} rows "
        "from raw.order_reviews"
    )

    return reviews, orders


def check_raw_order_reviews(reviews, orders):
    checks = []

    def add_check(check_name, issue_count, severity):
        checks.append(
            {
                "source_table": "raw.order_reviews",
                "check_name": check_name,
                "issue_count": int(issue_count),
                "severity": severity,
            }
        )

    add_check("total_rows", len(reviews), "info")

    # Count distinct review and order identifiers.
    add_check(
        "unique_review_ids",
        reviews["review_id"].nunique(),
        "info",
    )

    add_check(
        "unique_reviewed_orders",
        reviews["order_id"].nunique(),
        "info",
    )

    required_columns = [
        "review_id",
        "order_id",
        "review_score",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    for column in required_columns:
        add_check(
            f"missing_{column}",
            reviews[column].isna().sum(),
            "critical",
        )

    # 评论文字为空是正常业务情况，仅记录。
    add_check(
        "missing_review_comment_title",
        reviews["review_comment_title"].isna().sum(),
        "info",
    )

    add_check(
        "missing_review_comment_message",
        reviews["review_comment_message"].isna().sum(),
        "info",
    )

    # 检查完全相同的重复行。
    business_columns = [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    add_check(
        "exact_duplicate_rows",
        reviews.duplicated(
            subset=business_columns,
            keep=False,
        ).sum(),
        "high",
    )

    # review_id 在原始数据中不一定唯一。
    add_check(
        "duplicate_review_id_rows",
        reviews["review_id"]
        .duplicated(keep=False)
        .sum(),
        "medium",
    )

    # 统计拥有多条评价的订单数量。
    reviews_per_order = (
        reviews.groupby("order_id")
        .size()
    )

    add_check(
        "orders_with_multiple_reviews",
        reviews_per_order.gt(1).sum(),
        "medium",
    )

    # 评分必须是1～5的整数。
    numeric_scores = pd.to_numeric(
        reviews["review_score"],
        errors="coerce",
    )

    invalid_scores = (
        reviews["review_score"].notna()
        & (
            numeric_scores.isna()
            | numeric_scores.lt(1)
            | numeric_scores.gt(5)
            | numeric_scores.mod(1).ne(0)
        )
    )

    add_check(
        "invalid_review_score",
        invalid_scores.sum(),
        "critical",
    )

    for column in [
        "review_creation_date",
        "review_answer_timestamp",
    ]:
        converted_dates = pd.to_datetime(
            reviews[column],
            errors="coerce",
            format="mixed",
        )

        invalid_dates = (
            reviews[column].notna()
            & converted_dates.isna()
        )

        add_check(
            f"invalid_{column}",
            invalid_dates.sum(),
            "high",
        )

    # 每条评价都应当属于一个有效订单。
    known_order_ids = set(
        orders["order_id"].dropna()
    )

    unmatched_orders = (
        reviews["order_id"].notna()
        & ~reviews["order_id"].isin(
            known_order_ids
        )
    )

    add_check(
        "unmatched_order_id",
        unmatched_orders.sum(),
        "critical",
    )

    return pd.DataFrame(checks)


def print_quality_report(quality_report):
    print("\nQuality Report for raw.order_reviews")
    print("-" * 75)
    print(quality_report.to_string(index=False))

    actual_issues = quality_report[
        (quality_report["severity"] != "info")
        & (quality_report["issue_count"] > 0)
    ]

    print()

    if actual_issues.empty:
        print("No review quality issues found.")
    else:
        print("Checks containing issues:")
        print(actual_issues.to_string(index=False))


def main():
    reviews, orders = read_raw_data()

    quality_report = check_raw_order_reviews(
        reviews,
        orders,
    )

    print_quality_report(quality_report)


if __name__ == "__main__":
    main()