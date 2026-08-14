import pandas as pd
import pytest

from quality_raw_order_items import check_raw_order_items

def issue_count(report, check_name):
    matching_row = report[
        report["check_name"] == check_name
    ]

    count = matching_row["issue_count"].iloc[0]

    return int(count)

@pytest.fixture
def valid_order_items():
    return pd.DataFrame(
        [
            {
                "order_id": "order-1",
                "order_item_id": "1",
                "product_id": "product-1",
                "seller_id": "seller-1",
                "shipping_limit_date": "2018-01-05 10:00:00",
                "price": "100.00",
                "freight_value": "10.00",
            }
        ]
    )

@pytest.fixture
def known_orders():
    return pd.DataFrame(
        [
            {
                "order_id": "order-1",
            }
        ]
    )

def test_non_numeric_price_is_invalid(valid_order_items,known_orders):

    valid_order_items.loc[
        0,
        "price",
    ]="not-a-number"

    report=check_raw_order_items(
        valid_order_items,
        known_orders
    )

    assert issue_count(
        report,
        "invalid_price",
    )==1

    assert issue_count(
        report,
        "negative_price",
    )==0

def test_negative_price_is_detected(valid_order_items,known_orders):

    valid_order_items.loc[
        0,
        "price",
    ]="-0.01"

    report=check_raw_order_items(
        valid_order_items,
        known_orders,
    )

    assert issue_count(
        report,
        "invalid_price",
    )==0

    assert issue_count(
        report,
        "negative_price",
    )==1
