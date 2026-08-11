import pandas as pd
from sqlalchemy import text
from db import get_engine

VALID_ORDERS_FILE = {
    "created",
    "approved",
    "invoiced",
    "processing",
    "shipped",
    "delivered",
    "unavailable",
    "canceled",
}

REQUITED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
    "order_purchase_timestamp",
    "order_estimated_delivery_date",
]

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

def read_raw_orders():
    engine=get_engine()
    query = text("SELECT * FROM raw.orders;")
    with engine.connect() as connection:
        orders=pd.read_sql(query, connection)

    print(f"Read {len(orders):,} rows from raw.orders table")
    return orders

def check_raw_orders(orders):
    checks=[]
    def add_check(check_name,issue_count,severity):
        checks.append({
            "source_table": "raw.orders",
            "check_name": check_name,
            "issue_count": int(issue_count),
            "severity": severity
        })

    #总行数
    add_check("total_rows", len(orders), "info")

    #必填字段检查
    for column in REQUITED_COLUMNS:
        add_check(f"missing_{column}", orders[column].isna().sum(), "critical")
    #order_id应当唯一
    add_check("duplicate_order_id", orders["order_id"].duplicated(keep=False).sum(), "critical")

    #检查订单状态是否属于已知值
    normalized_status = (orders["order_status"].astype(str).str.lower().str.strip())
    invalid_status=(orders["order_status"].notna()) & (~normalized_status.isin(VALID_ORDERS_FILE))
    add_check("invalid_order_status", invalid_status.sum(), "high")

    #检查日期字符串能否转换为日期
    converted_dates={}
    for column in DATE_COLUMNS:
        converted=pd.to_datetime(orders[column],errors="coerce",format="mixed")
        converted_dates[column]=converted
        invalid_dates=(orders[column].notna()) & (converted.isna())
        add_check(f"invalid_{column}", invalid_dates.sum(), "high")

    #已完成订单理论上应该存在实际送达时间
    delivered_missing_delivery_date=(
        normalized_status.eq("delivered") &
        converted_dates["order_delivered_customer_date"].isna()
    )
    add_check("delivered_missing_delivery_date", delivered_missing_delivery_date.sum(), "high")
    quality_report=pd.DataFrame(checks)
    return quality_report

def print_quality_report(quality_report):
    print("Quality Report for raw.orders table:")
    print("-" * 60)
    print(quality_report.to_string(index=False))

    actual_issues=quality_report[
        (quality_report["severity"]!="info") &
        (quality_report["issue_count"] > 0)
    ]

    print()

    if actual_issues.empty:
        print("No data quality issues found.")
    else:
        print(f"Found {len(actual_issues):,} quality checks with issues.")

def main():
    orders=read_raw_orders()
    quality_report=check_raw_orders(orders)
    print_quality_report(quality_report)

if __name__=="__main__":
    main()
