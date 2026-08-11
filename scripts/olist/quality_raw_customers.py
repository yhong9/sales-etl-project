import pandas as pd
from sqlalchemy import text
from db import get_engine

VALID_BRAZIL_STATES={
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO",
}

def read_raw_data():
    engine = get_engine()

    with engine.connect() as connection:
        customers = pd.read_sql_query(text("SELECT * FROM raw.customers"), connection)
        orders = pd.read_sql_query(
            text("""
                SELECT order_id,customer_id
                FROM raw.orders;
            """), connection
        )

    print(f"Read {len(customers):,} rows from raw.customers")

    return customers, orders

def check_raw_customers(customers,orders):
    checks=[]
    def add_check(check_name, issue_count, severity):
        checks.append({
                "source_table": "raw.customers",
                "check_name": check_name,
                "issue_count": int(issue_count),
                "severity": severity,
            }
        )

    add_check(
        "total_rows",
        len(customers),
        "info",
    )

    add_check(
        "unique_customer_ids",
        customers["customer_id"].nunique(),
        "info",
    )

    add_check(
        "unique_real_customers",
        customers["customer_unique_id"].nunique(),
        "info",
    )

    required_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]

    for column in required_columns:
        add_check(
            f"missing_{column}",
            customers[column].isna().sum(),
            "critical",
        )

    add_check(
        "duplicate_customer_id",
        customers["customer_id"]
        .duplicated(keep=False)
        .sum(),
        "critical",
    )

    normalized_states = (
        customers["customer_state"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    invalid_states = (
        customers["customer_state"].notna()
        & ~normalized_states.isin(VALID_BRAZIL_STATES)
    )

    add_check(
        "invalid_customer_state",
        invalid_states.sum(),
        "high",
    )

    normalized_zip_codes = (
        customers["customer_zip_code_prefix"]
        .astype("string")
        .str.strip()
    )

    invalid_zip_codes = (
        customers["customer_zip_code_prefix"].notna()
        & ~normalized_zip_codes.str.fullmatch(
            r"\d{5}",
            na=False,
        )
    )

    add_check(
        "invalid_customer_zip_code_prefix",
        invalid_zip_codes.sum(),
        "high",
    )

    known_customer_ids = set(
        customers["customer_id"].dropna()
    )

    unmatched_orders = (
        orders["customer_id"].notna()
        & ~orders["customer_id"].isin(known_customer_ids)
    )

    add_check(
        "orders_with_unmatched_customer_id",
        unmatched_orders.sum(),
        "critical",
    )

    return pd.DataFrame(checks)

def print_quality_report(quality_report):
    print("\nQuality Report for raw.customers")
    print("-" * 60)
    print(quality_report.to_string(index=False))

    actual_issues = quality_report[
        (quality_report["severity"] != "info")
        & (quality_report["issue_count"] > 0)
    ]

    print()

    if actual_issues.empty:
        print("No customer data quality issues found.")
    else:
        print(
            f"Found {len(actual_issues)} "
            "customer quality checks with issues."
        )

def main():
    customers, orders = read_raw_data()
    quality_report = check_raw_customers(customers, orders)
    print_quality_report(quality_report)

if __name__ == "__main__":
    main()
