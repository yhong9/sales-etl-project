from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "archive"
    / "olist_products_dataset.csv"
)

CATEGORY_TRANSLATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "archive"
    / "product_category_name_translation.csv"
)

EXPECTED_PRODUCT_COLUMNS = [
    "product_id",
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

EXPECTED_TRANSLATION_COLUMNS = [
    "product_category_name",
    "product_category_name_english",
]


def read_csv_with_validation(
    file_path,
    expected_columns,
):
    dataframe = pd.read_csv(
        file_path,
        dtype="string",
    )

    actual_columns = dataframe.columns.tolist()

    if actual_columns != expected_columns:
        raise ValueError(
            f"Unexpected columns in {file_path.name}.\n"
            f"Expected: {expected_columns}\n"
            f"Actual:   {actual_columns}"
        )

    dataframe["source_file"] = file_path.name
    dataframe["loaded_at"] = pd.Timestamp.now(tz="UTC")

    print(
        f"Extracted {len(dataframe):,} rows "
        f"from {file_path.name}"
    )

    return dataframe


def load_raw_products():
    products = read_csv_with_validation(
        PRODUCTS_FILE,
        EXPECTED_PRODUCT_COLUMNS,
    )

    translations = read_csv_with_validation(
        CATEGORY_TRANSLATION_FILE,
        EXPECTED_TRANSLATION_COLUMNS,
    )

    engine = get_engine()

    create_products_sql = """
        CREATE TABLE IF NOT EXISTS raw.products (
            product_id TEXT,
            product_category_name TEXT,
            product_name_lenght TEXT,
            product_description_lenght TEXT,
            product_photos_qty TEXT,
            product_weight_g TEXT,
            product_length_cm TEXT,
            product_height_cm TEXT,
            product_width_cm TEXT,
            source_file TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
    """

    create_translations_sql = """
        CREATE TABLE IF NOT EXISTS
        raw.product_category_translation (
            product_category_name TEXT,
            product_category_name_english TEXT,
            source_file TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
    """

    with engine.begin() as connection:
        connection.execute(text(create_products_sql))
        connection.execute(text(create_translations_sql))

        connection.execute(
            text("TRUNCATE TABLE raw.products;")
        )
        connection.execute(
            text("""
                TRUNCATE TABLE
                raw.product_category_translation;
            """)
        )

        products.to_sql(
            name="products",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=5000,
            method="multi",
        )

        translations.to_sql(
            name="product_category_translation",
            schema="raw",
            con=connection,
            if_exists="append",
            index=False,
            chunksize=1000,
            method="multi",
        )

        product_database_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.products;")
        ).scalar_one()

        translation_database_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM raw.product_category_translation;
            """)
        ).scalar_one()

        if product_database_count != len(products):
            raise ValueError(
                "Product row count mismatch: "
                f"CSV={len(products):,}, "
                f"database={product_database_count:,}"
            )

        if translation_database_count != len(translations):
            raise ValueError(
                "Translation row count mismatch: "
                f"CSV={len(translations):,}, "
                f"database={translation_database_count:,}"
            )

    print(
        f"Loaded {product_database_count:,} rows "
        "into raw.products"
    )
    print(
        f"Loaded {translation_database_count:,} rows "
        "into raw.product_category_translation"
    )
    print("Row count validation passed!")


if __name__ == "__main__":
    load_raw_products()