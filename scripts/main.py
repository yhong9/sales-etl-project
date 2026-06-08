from extract import extract_data
from transform import transform_data
from quality import(
    validate_data,
    filter_clean_sales,
    save_quality_outputs
)
from load import load_data

def run_pipeline(
        orders_file: str = "orders.csv",
        customers_file: str = " customers.csv",
        products_file: str = "products.csv"
):
    print("Starting ETL pipline...")

    orders, customers, products = extract_data(
        orders_file,
        customers_file,
        products_file
    )

    sales=transform_data(orders, customers, products)

    quality_report, rejected_records = validate_data(
        orders,
        customers,
        products,
        sales
    )

    clean_sales = filter_clean_sales(sales)

    clean_sales.to_csv("data/processed/cleaned_sales.csv", index=False)
    save_quality_outputs(
        quality_report, 
        rejected_records
    )

    load_data(clean_sales)

    print("\nETL pipeline completed successfully.")

if __name__=="__main__":
    run_pipeline(
        "orders_mixed.csv",
        "customers_mixed.csv",
        "products_mixed.csv"
    )