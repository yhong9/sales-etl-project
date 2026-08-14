import pandas as pd
from quality_raw_customers import check_raw_customers
import pytest


def issue_count(report, check_name):
    matching_row = report[
        report["check_name"] == check_name
    ]

    count = matching_row["issue_count"].iloc[0]
    return int(count)


@pytest.fixture
def valid_customers():
    return pd.DataFrame(
        [
            {
                "customer_id": "customer-1",
                "customer_unique_id": "real-customer-1",
                "customer_zip_code_prefix": "01001",
                "customer_city": "sao paulo",
                "customer_state": "SP",
            }
        ]
    )

@pytest.fixture
def matching_orders():
    return pd.DataFrame(
        [
            {
                "customer_id":"customer-1",
            }
        ]
    )

def test_invalid_customer_state_is_detected(
    valid_customers,
    matching_orders,
):
    # Arrange：只破坏州代码
    valid_customers.loc[
        0,
        "customer_state",
    ] = "XX"

    # Act
    report = check_raw_customers(
        valid_customers,
        matching_orders,
    )

    # Assert
    assert issue_count(
        report,
        "invalid_customer_state",
    ) == 1

@pytest.mark.parametrize(
        "state",
        ["SP","sp"," SP "],
)

def test_valid_customer_state_formats_are_accepted(state,valid_customers,matching_orders):

    valid_customers.loc[
        0,
        "customer_state",
    ]=state

    report = check_raw_customers(valid_customers, matching_orders)

    assert issue_count(
        report,
        "invalid_customer_state",
    )==0