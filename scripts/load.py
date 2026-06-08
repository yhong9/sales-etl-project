import sqlite3
import pandas as pd

def load_data(clean_sales:pd.DataFrame,database_name:str="sales_etl.db"):
    conn = sqlite3.connect(database_name)

    clean_sales.to_sql(
        "fact_sales",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(f"Load Completed! Clean sales data loaded into {database_name}.")