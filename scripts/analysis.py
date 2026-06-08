import sqlite3
import pandas as pd

def run_query(query:str, database_name:str="sales_etl.db"):
    conn = sqlite3.connect(database_name)

    result = pd.read_sql_query(query, conn)

    conn.close()

    return result

if __name__ == "__main__":
    queries = {
        "Monthly Sales Trend":"""
            SELECT
                order_month,
                ROUND(SUM(revenue),2) AS total_revenue, --每个月的revenue加起来，保留两位小数
                ROUND(SUM(profit),2) AS total_profit,
                COUNT(DISTINCT order_id) AS total_orders --每个月多少订单，distinct 避免重复
            FROM fact_sales
            GROUP BY order_month
            ORDER BY order_month;
        """,
        "Revenue by Region":"""
            SELECT
                region,
                ROUND(SUM(revenue),2) AS total_revenue, 
                ROUND(SUM(profit),2) AS total_profit,
                COUNT(DISTINCT order_id) AS total_orders 
            FROM fact_sales
            GROUP BY region
            ORDER BY total_revenue DESC;
            """,

            "Top Products by Revenue":"""
            SELECT
                product_name,
                category,
                ROUND(SUM(revenue),2) AS total_revenue,
                ROUND(SUM(profit),2) AS total_profit,
                COUNT(DISTINCT order_id) AS total_orders 
            FROM fact_sales
            GROUP BY product_name,category
            ORDER BY total_revenue DESC
            LIMIT 10;
            """,

            "Profit Margin by Category":"""
            SELECT
                category,
                ROUND(SUM(revenue), 2) AS total_revenue,
                ROUND(SUM(profit), 2) AS total_profit,
                ROUND(SUM(PROFIT)/SUM(revenue),4) AS profit_margin
            FROM fact_sales
            GROUP BY category
            ORDER BY profit_margin DESC
            LIMIT 10;
            """,
    }

    for query_name,query in queries.items():
        print(f"\n{query_name}")
        print("-"*50)
        
        result = run_query(query)
        print(result.to_string(index=False))