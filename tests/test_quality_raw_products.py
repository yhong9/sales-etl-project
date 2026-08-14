import pandas as pd
import pytest

from quality_raw_products import check_raw_products

def issue_count(report, check_name):
    matching_row = report[
        report["check_name"] == check_name
    ]

    count = matching_row["issue_count"].iloc[0]

    return int(count)

@pytest.fixture
def valid_products():
    return pd.DataFrame(
        [
            {
                "product_id": "product-1",
                "product_category_name": "health_beauty",
                "product_name_lenght": "20",
                "product_description_lenght": "100",
                "product_photos_qty": "1",
                "product_weight_g": "500",
                "product_length_cm": "20",
                "product_height_cm": "10",
                "product_width_cm": "15",
            }
        ]
    )

@pytest.fixture
def valid_translations():
    return pd.DataFrame(
        [
            {
                "product_category_name": "health_beauty",
                "product_category_name_english": "health_beauty",
            }
        ]
    )

@pytest.fixture
def matching_order_items():
    return pd.DataFrame(
        [
            {
                "product_id": "product-1",
            }
        ]
    )

def test_missing_product_category_is_detected(
    valid_products,
    valid_translations,
    matching_order_items,
):

    valid_products.loc[
        0,
        "product_category_name",
    ] = None


    report = check_raw_products(
        valid_products,
        valid_translations,
        matching_order_items,
    )


    assert issue_count(
        report,
        "missing_product_category_name",
    ) == 1


    assert issue_count(
        report,
        "products_without_category_translation",
    ) == 0