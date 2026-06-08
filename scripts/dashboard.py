import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from pandas.errors import EmptyDataError

DATABASE_NAME = "sales_etl.db"

def load_sales_data():
    conn = sqlite3.connect(DATABASE_NAME)
    sales=pd.read_sql_query("SELECT * FROM fact_sales",conn)
    conn.close()
    return sales

def load_csv_if_exists(file_path:str):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        return pd.DataFrame()
    except EmptyDataError:
        return pd.DataFrame()
    
st.set_page_config(
    page_title="Sales ETL Dashboard",
    layout="wide"
)

st.title("Sales ETL Dashboard")
st.write("This dashboard shows clean sales data, business insight, and data quality results from the ETL pipeline.")


#Load data
sales = load_sales_data()
quality_report = load_csv_if_exists("data/processed/data_quality_report.csv")
rejected_records =  load_csv_if_exists("data/processed/rejected_records.csv")

#KPI cards
st.header("Key Metrics")

total_revenue=sales["revenue"].sum()
total_profit=sales["profit"].sum()
total_orders=sales["order_id"].nunique() #计算不重复的value
avg_profit_margin=sales["profit_margin"].mean()

col1,col2,col3,col4=st.columns(4)

col1.metric("Total Revenue",f"${total_revenue:,.2f}")
col2.metric("Total Profit",f"${total_profit:,.2f}")
col3.metric("Total Orders",f"${total_orders}")
col4.metric("Avg Profit Margine",f"${avg_profit_margin:.2f}")

#Charts

st.header("Sales Anallysis")

monthly_sales = (
    sales.groupby("order_month", as_index=False)
    .agg( #汇总计算
        total_revenue=("revenue","sum"),
        total_profit=("profit","sum"),
        total_orders=("order_id","nunique")
    )
)

fig_monthly = px.line(
    monthly_sales,
    x="order_month",
    y="total_revenue",
    markers=True,#每个数据上显示圆点
    title="Monthly Revenue Trend"
)

st.plotly_chart(fig_monthly,use_container_width=True)#宽度自动适应页面容器

col1,col2=st.columns(2)

region_sales=(
    sales.groupby("region",as_index=False)
    .agg(total_revenue=("revenue","sum"))
    .sort_values("total_revenue",ascending=False)
)

fig_region = px.bar(
    region_sales,
    x="region",
    y="total_revenue",
    title="Revenue by Region"
)
col1.plotly_chart(fig_region,use_container_width=True)

category_margin=(
    sales.groupby("category",as_index=False)
    .agg(
        total_revenue=("revenue","sum"),
        total_profit=("profit","sum")
    )
)

category_margin["profit_margin"]=(
    category_margin["total_profit"]/category_margin["total_revenue"]
)

fig_category = px.bar(
    category_margin,
    x="category",
    y="profit_margin",
    title="Profit Margin by Category"
)
col2.plotly_chart(fig_category,use_container_width=True)

total_products=(
    sales.groupby(["product_name", "category"], as_index=False)
    .agg(
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum"),
        total_orders=("order_id", "nunique")
        )
    .sort_values("total_revenue", ascending=False)
    .head(10)
)

fig_top_products = px.bar(
    total_products,
    x="total_revenue",
    y="product_name",
    orientation="h",
    title="Top 10 Products by Revenue"
)
st.plotly_chart(fig_top_products,use_container_width=True)

#Data quality section

st.header("Date Qualit Results")

if quality_report.empty:
    st.success("No data quality issues found.")
else:
    st.subheader("Data Quality Report")
    st.dataframe(quality_report,use_container_width=True)

if rejected_records.empty:
    st.success("No rejected records found.")
else:
    st.subheader("REjected Record Summary")
    rejected_summary=(
        rejected_records.groupby(["source_table","error_type"])
        .size()
        .reset_index(name="record_count")
        .sort_values(["source_table","error_type"])
    )
    st.dataframe(rejected_summary,use_container_width=True)
    st.subheader("REjected Records Detail")
    st.dataframe(rejected_records,use_container_width=True)


#Clean Sales Data
st.header("Clean Sales Data")
st.dataframe(sales,use_container_width=True)