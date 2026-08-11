from sqlalchemy import text

from db import get_engine


def build_staging_products():
    engine = get_engine()

    drop_products_sql = """
        DROP TABLE IF EXISTS staging.products;
    """

    drop_translation_sql = """
        DROP TABLE IF EXISTS
        staging.product_category_translation;
    """

    create_translation_sql = """
        CREATE TABLE staging.product_category_translation AS
        SELECT
            LOWER(
                NULLIF(TRIM(product_category_name), '')
            ) AS product_category_name,

            LOWER(
                NULLIF(
                    TRIM(product_category_name_english), ''
                )
            ) AS product_category_name_english,

            source_file,
            loaded_at,
            CURRENT_TIMESTAMP AS staged_at

        FROM raw.product_category_translation;
    """

    add_translation_primary_key_sql = """
        ALTER TABLE staging.product_category_translation
        ADD CONSTRAINT staging_category_translation_pk
        PRIMARY KEY (product_category_name);
    """

    create_products_sql = """
        CREATE TABLE staging.products AS
        SELECT
            NULLIF(
                TRIM(products.product_id), ''
            ) AS product_id,

            COALESCE(
                LOWER(
                    NULLIF(
                        TRIM(
                            products.product_category_name
                        ),
                        ''
                    )
                ),
                'unknown'
            ) AS product_category_name,

            COALESCE(
                translations.product_category_name_english,

                CASE
                    WHEN products.product_category_name IS NULL
                        OR TRIM(
                            products.product_category_name
                        ) = ''
                        THEN 'unknown'
                    ELSE
                        'untranslated_'
                        || LOWER(
                            TRIM(
                                products.product_category_name
                            )
                        )
                END
            ) AS product_category_name_english,

            NULLIF(
                TRIM(products.product_name_lenght), ''
            )::INTEGER AS product_name_length,

            NULLIF(
                TRIM(
                    products.product_description_lenght
                ),
                ''
            )::INTEGER AS product_description_length,

            NULLIF(
                TRIM(products.product_photos_qty), ''
            )::INTEGER AS product_photos_qty,

            NULLIF(
                TRIM(products.product_weight_g), ''
            )::NUMERIC(12, 2) AS product_weight_g,

            NULLIF(
                TRIM(products.product_length_cm), ''
            )::NUMERIC(12, 2) AS product_length_cm,

            NULLIF(
                TRIM(products.product_height_cm), ''
            )::NUMERIC(12, 2) AS product_height_cm,

            NULLIF(
                TRIM(products.product_width_cm), ''
            )::NUMERIC(12, 2) AS product_width_cm,

            CASE
                WHEN products.product_length_cm IS NULL
                    OR products.product_height_cm IS NULL
                    OR products.product_width_cm IS NULL
                    THEN NULL
                ELSE (
                    products.product_length_cm::NUMERIC
                    * products.product_height_cm::NUMERIC
                    * products.product_width_cm::NUMERIC
                )::NUMERIC(14, 2)
            END AS product_volume_cm3,

            products.source_file,
            products.loaded_at,
            CURRENT_TIMESTAMP AS staged_at

        FROM raw.products AS products

        LEFT JOIN staging.product_category_translation
            AS translations
            ON LOWER(
                TRIM(products.product_category_name)
            ) = translations.product_category_name;
    """

    add_product_primary_key_sql = """
        ALTER TABLE staging.products
        ADD CONSTRAINT staging_products_pk
        PRIMARY KEY (product_id);
    """

    create_category_index_sql = """
        CREATE INDEX staging_products_category_idx
        ON staging.products (
            product_category_name_english
        );
    """

    validation_sql = """
        SELECT
            COUNT(*) AS total_rows,

            COUNT(DISTINCT product_id)
                AS unique_products,

            COUNT(*) FILTER (
                WHERE product_category_name = 'unknown'
            ) AS unknown_category_products,

            COUNT(*) FILTER (
                WHERE product_category_name_english
                    LIKE 'untranslated_%'
            ) AS untranslated_products,

            COUNT(*) FILTER (
                WHERE product_weight_g IS NULL
            ) AS missing_weight_products,

            COUNT(*) FILTER (
                WHERE product_volume_cm3 IS NULL
            ) AS missing_volume_products

        FROM staging.products;
    """

    unmatched_order_items_sql = """
        SELECT COUNT(*)
        FROM staging.order_items AS items
        LEFT JOIN staging.products AS products
            ON items.product_id = products.product_id
        WHERE products.product_id IS NULL;
    """

    with engine.begin() as connection:
        connection.execute(text(drop_products_sql))
        connection.execute(text(drop_translation_sql))

        connection.execute(text(create_translation_sql))
        connection.execute(
            text(add_translation_primary_key_sql)
        )

        connection.execute(text(create_products_sql))
        connection.execute(
            text(add_product_primary_key_sql)
        )
        connection.execute(
            text(create_category_index_sql)
        )

        result = connection.execute(
            text(validation_sql)
        ).mappings().one()

        unmatched_order_items = connection.execute(
            text(unmatched_order_items_sql)
        ).scalar_one()

        raw_count = connection.execute(
            text("SELECT COUNT(*) FROM raw.products;")
        ).scalar_one()

        if result["total_rows"] != raw_count:
            raise ValueError(
                "Raw and staging product counts differ: "
                f"raw={raw_count:,}, "
                f"staging={result['total_rows']:,}"
            )

        if unmatched_order_items > 0:
            raise ValueError(
                f"Found {unmatched_order_items:,} order items "
                "without matching products."
            )

    print("staging.products created successfully!")
    print(f"Total products: {result['total_rows']:,}")
    print(
        f"Unique products: "
        f"{result['unique_products']:,}"
    )
    print(
        "Unknown-category products: "
        f"{result['unknown_category_products']:,}"
    )
    print(
        "Untranslated products: "
        f"{result['untranslated_products']:,}"
    )
    print(
        "Products missing weight: "
        f"{result['missing_weight_products']:,}"
    )
    print(
        "Products missing volume: "
        f"{result['missing_volume_products']:,}"
    )
    print(
        f"Unmatched order items: "
        f"{unmatched_order_items:,}"
    )
    print("Raw-to-staging validation passed!")


if __name__ == "__main__":
    build_staging_products()