import pandas as pd

from quality_raw_orders import check_raw_orders


def issue_count(report, check_name):
    return int(
        report.loc[
            report["check_name"].eq(check_name),
            "issue_count",
        ].iloc[0]
    )


def make_orders():
    return pd.DataFrame(
        [
            {
                "order_id": "order-1",
                "customer_id": "customer-1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2018-01-01 10:00:00",
                "order_approved_at": "2018-01-01 11:00:00",
                "order_delivered_carrier_date": "2018-01-02 10:00:00",
                "order_delivered_customer_date": "2018-01-05 10:00:00",
                "order_estimated_delivery_date": "2018-01-07 00:00:00",
            }
        ]
    )


def test_valid_order_has_no_quality_issues():
    report = check_raw_orders(make_orders())
    actual_issues = report[
        report["severity"].ne("info")
        & report["issue_count"].gt(0)
    ]

    assert actual_issues.empty


def test_invalid_status_and_date_are_detected():
    orders = make_orders()
    orders.loc[0, "order_status"] = "unknown-status"
    orders.loc[0, "order_purchase_timestamp"] = "not-a-date"

    report = check_raw_orders(orders)

    assert issue_count(report, "invalid_order_status") == 1
    assert issue_count(
        report,
        "invalid_order_purchase_timestamp",
    ) == 1


def test_delivered_order_requires_delivery_date():
    orders = make_orders()
    orders.loc[0, "order_delivered_customer_date"] = None

    report = check_raw_orders(orders)

    assert issue_count(
        report,
        "delivered_missing_delivery_date",
    ) == 1

def test_duplicate_order_ids_are_detected():
    orders = make_orders()
    orders=pd.concat([orders,orders.copy()],ignore_index=True)
    report = check_raw_orders(orders)
    assert issue_count(report,"duplicate_order_id") == 2