import pandas as pd


def transform_data(
        orders:pd.DataFrame, 
        customers:pd.DataFrame, 
        products:pd.DataFrame):
    #remove duplicats, remove NA
    orders=orders.drop_duplicates(subset=["order_id"])
    orders["order_date"] = pd.to_datetime(orders["order_date"],errors=("coerce"))
    orders=orders.dropna(subset=["order_id","customer_id","product_id","order_date","quantity","unit_price"])
    orders=orders[orders["quantity"]>=0]
    orders=orders[orders["unit_price"]>=0]
    
    #join sales table
    sales=orders.merge(customers,on="customer_id",how="left")
    sales=sales.merge(products, on="product_id",how="left")
    
    #calculate business metrics
    sales["revenue"]=sales["quantity"]*sales["unit_price"]
    sales["total_cost"]=sales["quantity"]*sales["cost"]
    sales["profit"]=sales["revenue"]-sales["total_cost"]
    sales["profit_margin"]=sales["profit"]/sales["revenue"]
    
    #create order_month
    sales["order_month"]=sales["order_date"].dt.to_period("M").astype(str)
    

    print("Transform completed!")
    # print(f"Cleaned sales data shape:{sales.shape}")

    return sales


if __name__=="__main__":
    from extract import extract_data
    from quality import (
        validate_data,
        filter_clean_sales,
        save_quality_outputs
    )
    from load import load_data

    orders, customers, products = extract_data(
        "orders.csv",
        "customers.csv" ,
        "products.csv"
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
    quality_report, rejected_records = save_quality_outputs(
        quality_report, 
        rejected_records
    )
     
    load_data(clean_sales)

    print("\nData Quality Report:")
    if rejected_records.empty:
        print("No data quality issues found.")
    else:
        print(quality_report.to_string(index=False))

    print("\nRejected Records Summary:")
    if rejected_records.empty:
        print("No rejected recors found.")
    else:
        summary = rejected_records.groupby(
            ["source_table","error_type"]
        ).size().reset_index(name="record_count")
        print(summary.to_string(index=False))

    print("\nClean sales preivew:")
    print(clean_sales.head())


