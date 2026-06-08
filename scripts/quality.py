import os
import pandas as pd

def create_rejected_rows(
        df:pd.DataFrame,
        mask,
        source_table:str,
        error_type:str,
        severity:str,#严重性
        action:str#可以做什么
):
    rejected = df.loc[mask].copy() #df.loc只保留mask里面true的，.copy就是复制一份，避免影响原来的表格
    if rejected.empty:
        return pd.DataFrame()
    #DataFrame.insert(位置, 新列名, 新列的值)
    rejected.insert(0,"source_table",source_table)
    rejected.insert(1,"error_type",error_type)
    rejected.insert(2,"severity",severity)
    rejected.insert(3,"action",action)

    return rejected

def add_quality_check(
        checks:list,
        source_table:str,
        check_name:str,
        issue_count:str,
        severity:str,
        action:str
):
    #最开始是0，随着检验，增加错误数据记录，最终记录错误总数
    checks.append({
        "source_table":source_table,
        "check_name":check_name,
        "issue_count":issue_count,
        "severity":severity,
        "action":action
    })
def run_quality_checks(
    df: pd.DataFrame,
    rules: list,
    source_table: str,
    checks: list,
    rejected_list: list
):
    for rule in rules:
        mask = rule["mask"]

        add_quality_check(
            checks,
            source_table,
            rule["check_name"],
            mask.sum(),
            rule["severity"],
            rule["action"]
        )

        rejected_list.append(
            create_rejected_rows(
                df,
                mask,
                source_table,
                rule["check_name"],
                rule["severity"],
                rule["action"]
            )
        )



def validate_data(
        orders:pd.DataFrame,
        customers:pd.DataFrame,
        products:pd.DataFrame,
        sales: pd.DataFrame
):
    #check raw source before transformation.
    checks=[]
    rejected_list=[]

    #1. table orders

    converted_dates = pd.to_datetime(orders["order_date"],errors="coerce")

    order_rules=[
        {
            "check_name":"duplicated_order_id",
            "mask":orders["order_id"].duplicated(keep=False),
            "severity":"high",
            "action":"remove duplicates"
        },
        {
            "check_name": "missing_order_id",
            "mask": orders["order_id"].isnull(),
            "severity": "critical",
            "action": "reject rows"
        },
        {
            "check_name": "missing_customer_id",
            "mask": orders["customer_id"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_product_id",
            "mask": orders["product_id"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_order_date",
            "mask": orders["order_date"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "invalid_order_date",
            "mask": orders["order_date"].notnull() & converted_dates.isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_quantity",
            "mask": orders["quantity"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "quantity_less_or_equal_zero",
            "mask": orders["quantity"] <= 0,
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_unit_price",
            "mask": orders["unit_price"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "negative_unit_price",
            "mask": orders["unit_price"] < 0,
            "severity": "high",
            "action": "reject rows"
        }
    ]
    run_quality_checks(orders,order_rules,"orders",checks,rejected_list)

    #check customer table

    customer_rules = [
        {
            "check_name": "duplicate_customer_id",
            "mask": customers["customer_id"].duplicated(keep=False),
            "severity": "high",
            "action": "review customer master data"
        },
        {
            "check_name": "missing_customer_id",
            "mask": customers["customer_id"].isnull(),
            "severity": "critical",
            "action": "reject rows"
        },
        {
            "check_name": "missing_customer_name",
            "mask": customers["customer_name"].isnull(),
            "severity": "medium",
            "action": "fill with Unknown or review"
        },
        {
            "check_name": "missing_region",
            "mask": customers["region"].isnull(),
            "severity": "medium",
            "action": "fill with Unknown or review"
        }
    ]

    run_quality_checks(customers,customer_rules,"customers",checks,rejected_list)

    # check products table

    product_rules = [
        {
            "check_name": "duplicate_product_id",
            "mask": products["product_id"].duplicated(keep=False),
            "severity": "high",
            "action": "review product master data"
        },
        {
            "check_name": "missing_product_id",
            "mask": products["product_id"].isnull(),
            "severity": "critical",
            "action": "reject rows"
        },
        {
            "check_name": "missing_product_name",
            "mask": products["product_name"].isnull(),
            "severity": "high",
            "action": "review product master data"
        },
        {
            "check_name": "missing_category",
            "mask": products["category"].isnull(),
            "severity": "medium",
            "action": "fill with Unknown or review"
        },
        {
            "check_name": "missing_cost",
            "mask": products["cost"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "negative_cost",
            "mask": products["cost"] < 0,
            "severity": "high",
            "action": "reject rows"
        }
    ]

    run_quality_checks(products,product_rules,"products",checks,rejected_list)
    
    # check transformed sales table

    sales_rules = [
        {
            "check_name": "duplicate_order_id_after_transform",
            "mask": sales["order_id"].duplicated(keep=False),
            "severity": "high",
            "action": "review transformation logic"
        },
        {
            "check_name": "unmatched_customer_id",
            "mask": sales["customer_name"].isnull(),
            "severity": "medium",
            "action": "reject or fill customer as Unknown"
        },
        {
            "check_name": "unmatched_product_id",
            "mask": sales["product_name"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_cost_after_join",
            "mask": sales["cost"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_revenue",
            "mask": sales["revenue"].isnull(),
            "severity": "critical",
            "action": "reject rows"
        },
        {
            "check_name": "negative_revenue",
            "mask": sales["revenue"] < 0,
            "severity": "critical",
            "action": "reject rows"
        },
        {
            "check_name": "missing_profit",
            "mask": sales["profit"].isnull(),
            "severity": "high",
            "action": "reject rows"
        },
        {
            "check_name": "missing_profit_margin",
            "mask": sales["profit_margin"].isnull(),
            "severity": "high",
            "action": "reject rows"
        }
    ]

    run_quality_checks(sales,sales_rules,"transformed_sales",checks,rejected_list)
    
    quality_report = pd.DataFrame(checks)
    quality_report = quality_report[quality_report["issue_count"]>0]

    rejected_records = pd.concat(
        [df for df in rejected_list if not df.empty],
        ignore_index=True
        ) if any(not df.empty for df in rejected_list)else pd.DataFrame()

    return quality_report,rejected_records

def filter_clean_sales(sales:pd.DataFrame):
    clean_sales = sales.copy()
    clean_sales=clean_sales.dropna(
        subset=["customer_name","product_name","cost","revenue","profit","profit_margin"]
    )
    clean_sales=clean_sales[clean_sales["revenue"]>0]
    clean_sales=clean_sales[clean_sales["profit"].notnull()]
    return clean_sales

def save_quality_outputs(
        quality_report:pd.DataFrame,
        rejected_records:pd.DataFrame
    ):

    output_folder = "data/processed"
    os.makedirs(output_folder,exist_ok=True)

    if not quality_report.empty:
        quality_report=quality_report.sort_values(
            by=["source_table","check_name"]
        )
    
    if not rejected_records.empty:
        rejected_records=rejected_records.sort_values(
            by=["source_table","error_type"]
        )

    quality_report.to_csv(
        f"{output_folder}/data_quality_report.csv",
        index=False
    )

    if rejected_records.empty:
        rejected_records = pd.DataFrame(
            columns=[
                "source_table",
                "error_type",
                "severity",
                "action"
            ]
        )

    rejected_records.to_csv(
        f"{output_folder}/rejected_records.csv",
        index=False
    )

    print("\nData quality report saved to data/processed/data_quality_report.csv")
    print("Rejected records report saved to data/processed/rejected_records.csv")

    return quality_report,rejected_records
