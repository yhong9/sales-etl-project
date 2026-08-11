import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLIST_SCRIPTS = PROJECT_ROOT / "scripts" / "olist"
OLIST_ANALYTICS_LOGO = (
    PROJECT_ROOT
    / "dashboard"
    / "assets"
    / "olist-analytics-logo.png"
)

sys.path.insert(0, str(OLIST_SCRIPTS))

from db import get_engine  # noqa: E402


st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon=str(OLIST_ANALYTICS_LOGO),
    layout="wide",
)
st.markdown(
    """
    <style>
    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    /* 页面主标题 */
    h1 {
        color: #123b57;
        font-size: 2.7rem !important;
        font-weight: 800 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.035em;
    }

    /* 区域标题 */
    h2, h3 {
        color: #174766;
        font-weight: 750 !important;
        letter-spacing: -0.015em;
    }

    h2 {
        font-size: 1.75rem !important;
    }

    h3 {
        font-size: 1.55rem !important;
    }

    /* 普通文字 */
    p {
        color: #56645d;
    }

    /* 筛选器标签 */
    div[data-testid="stWidgetLabel"] p {
        color: #65736c;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* 下拉框和日期框 */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] input {
        background-color: #ffffff;
        border-color: #e1e8e3;
        border-radius: 9px;
    }

    /* 侧边栏导航 */
    section[data-testid="stSidebar"] {
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    section[data-testid="stSidebar"] label {
        font-size: 1rem;
    }

    /* 深色侧栏需要更高的文字对比度 */
    section[data-testid="stSidebar"] h2 {
        color: #ffffff !important;
        font-size: 1.35rem !important;
        font-weight: 750 !important;
        letter-spacing: 0.015em;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #b8cbd2 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #c8dce7 !important;
        font-size: 1rem !important;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover p {
        color: #ffffff !important;
    }

    /* 品牌名称 */
    section[data-testid="stSidebar"] .sidebar-brand-title {
        color: #ffffff !important;
        font-size: 1.35rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: 0.035em;
        white-space: nowrap;
    }

    section[data-testid="stSidebar"] .sidebar-brand-subtitle {
        color: #8fb1c4 !important;
        font-size: 0.72rem;
        font-weight: 600;
        line-height: 1.25;
        letter-spacing: 0.08em;
        margin-top: 0.35rem;
        white-space: nowrap;
    }

    /* 导航项目占满整行 */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.28rem;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        width: 100%;
        min-height: 44px;
        margin: 0;
        padding: 0.68rem 0.85rem;
        border-radius: 8px;
        transition: background-color 0.18s ease;
    }

    /* 隐藏默认圆形单选按钮 */
    section[data-testid="stSidebar"]
    label[data-baseweb="radio"] > div:first-child {
        display: none;
    }

    /* 鼠标经过的导航项目 */
    section[data-testid="stSidebar"]
    label[data-baseweb="radio"]:hover {
        background-color: rgba(74, 157, 205, 0.18);
    }

    /* 当前选中的导航项目 */
    section[data-testid="stSidebar"]
    label[data-baseweb="radio"]:has(input:checked) {
        background-color: #2f98d0;
        box-shadow: 0 5px 14px rgba(8, 30, 48, 0.20);
    }

    section[data-testid="stSidebar"]
    label[data-baseweb="radio"]:has(input:checked) p {
        color: #ffffff !important;
        font-weight: 750;
    }

    section[data-testid="stSidebar"] div[data-testid="stAlert"] p {
        color: #e4f4ed !important;
        font-weight: 600;
    }

    /* 页面整体背景 */
    .stApp {
        background-color: #f6f8f6;
    }

    /* 页面内容宽度和上边距 */
    .block-container {
        padding-top: 3.6rem;
        padding-bottom: 2rem;
    }

    /* 避免 Streamlit 顶部工具栏遮挡自定义页面标题 */
    section[data-testid="stMain"]
    div[data-testid="stMainBlockContainer"] {
        padding-top: 3.6rem;
    }

    /* KPI 卡片 */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e6ebe7;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 4px 14px rgba(51, 65, 59, 0.05);
        min-height: 125px;
    }

    /* KPI 标题 */
    div[data-testid="stMetricLabel"] {
        color: #718078;
        font-size: 0.9rem;
        font-weight: 600;
    }

    /* KPI 数字 */
    div[data-testid="stMetricValue"] {
        color: #294238;
        font-size: 1.9rem;
        font-weight: 750;
    }

    /* KPI 卡片悬停效果 */
    div[data-testid="stMetric"]:hover {
        border-color: #b8cdbd;
        box-shadow: 0 8px 22px rgba(76, 110, 87, 0.08);
        transform: translateY(-2px);
        transition: all 0.2s ease;
    }

    /* 用背景色强调页面最重要的 Total Sales KPI */
    .st-key-sales_primary_kpi div[data-testid="stMetric"],
    .st-key-overview_primary_kpi div[data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        color: #ffffff;
        border-color: rgba(255, 255, 255, 0.18);
        background: linear-gradient(145deg, #356f92, #62a2c5);
        box-shadow: 0 9px 22px rgba(37, 93, 126, 0.20);
    }

    .st-key-sales_primary_kpi div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #4f8f82, #76b0a5);
        box-shadow: 0 9px 22px rgba(55, 117, 104, 0.20);
    }

    .st-key-review_primary_kpi div[data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        color: #ffffff;
        border-color: rgba(255, 255, 255, 0.20);
        background: linear-gradient(145deg, #b98738, #d4ac61);
        box-shadow: 0 9px 22px rgba(155, 111, 39, 0.20);
    }

    .st-key-quality_primary_kpi div[data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        color: #ffffff;
        border-color: rgba(255, 255, 255, 0.20);
        background: linear-gradient(145deg, #7469a0, #a096c1);
        box-shadow: 0 9px 22px rgba(92, 80, 139, 0.20);
    }

    .st-key-review_primary_kpi div[data-testid="stMetric"]::after,
    .st-key-quality_primary_kpi div[data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        width: 105px;
        height: 105px;
        right: -35px;
        top: -48px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.11);
    }

    .st-key-sales_primary_kpi div[data-testid="stMetric"]::after,
    .st-key-overview_primary_kpi div[data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        width: 105px;
        height: 105px;
        right: -35px;
        top: -48px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.10);
    }

    .st-key-sales_primary_kpi div[data-testid="stMetric"] *,
    .st-key-overview_primary_kpi div[data-testid="stMetric"] *,
    .st-key-review_primary_kpi div[data-testid="stMetric"] *,
    .st-key-quality_primary_kpi div[data-testid="stMetric"] * {
        color: #ffffff !important;
    }

    .st-key-sales_primary_kpi div[data-testid="stMetricLabel"] *,
    .st-key-overview_primary_kpi div[data-testid="stMetricLabel"] *,
    .st-key-review_primary_kpi div[data-testid="stMetricLabel"] * {
        color: #dcecf5 !important;
    }

    .st-key-review_primary_kpi div[data-testid="stMetricLabel"] * {
        color: #fff3d9 !important;
    }

    .st-key-quality_primary_kpi div[data-testid="stMetricLabel"] * {
        color: #eeeafd !important;
    }

    .st-key-sales_primary_kpi div[data-testid="stMetricValue"],
    .st-key-sales_primary_kpi div[data-testid="stMetricValue"] div,
    .st-key-overview_primary_kpi div[data-testid="stMetricValue"],
    .st-key-overview_primary_kpi div[data-testid="stMetricValue"] div {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    .st-key-sales_primary_kpi div[data-testid="stMetric"]:hover,
    .st-key-overview_primary_kpi div[data-testid="stMetric"]:hover {
        border-color: rgba(255, 255, 255, 0.32);
        box-shadow: 0 12px 28px rgba(37, 93, 126, 0.27);
    }

    .st-key-sales_primary_kpi div[data-testid="stMetric"]:hover {
        box-shadow: 0 12px 28px rgba(55, 117, 104, 0.27);
    }

    .st-key-review_primary_kpi div[data-testid="stMetric"]:hover {
        border-color: rgba(255, 255, 255, 0.34);
        box-shadow: 0 12px 28px rgba(155, 111, 39, 0.27);
    }

    .st-key-quality_primary_kpi div[data-testid="stMetric"]:hover {
        border-color: rgba(255, 255, 255, 0.34);
        box-shadow: 0 12px 28px rgba(92, 80, 139, 0.27);
    }

    /* Raw 到 Staging 的可视化对账卡片 */
    .reconciliation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 0.8rem;
        margin: 0.35rem 0 1rem 0;
    }

    .reconciliation-card {
        padding: 1rem;
        border: 1px solid #e2e8e5;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 4px 13px rgba(40, 65, 54, 0.045);
    }

    .reconciliation-name {
        color: #27485c;
        font-size: 0.92rem;
        font-weight: 750;
        margin-bottom: 0.8rem;
    }

    .reconciliation-flow {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.35rem;
    }

    .reconciliation-step {
        min-width: 0;
    }

    .reconciliation-step span {
        display: block;
        color: #8a9aa2;
        font-size: 0.68rem;
        font-weight: 650;
        letter-spacing: 0.055em;
    }

    .reconciliation-step strong {
        display: block;
        color: #29485a;
        margin-top: 0.15rem;
        font-size: 1rem;
    }

    .reconciliation-arrow {
        color: #92a8b4;
        font-size: 1.15rem;
        font-weight: 800;
    }

    .reconciliation-status {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 750;
    }

    .reconciliation-status.passed {
        color: #397662;
        background: #e3f1eb;
    }

    .reconciliation-status.deduplicated {
        color: #8b6728;
        background: #f7edda;
    }

    /* Overview: business recommendations */
    .recommendation-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin: 0.35rem 0 1.3rem 0;
    }

    .recommendation-card {
        padding: 1.15rem;
        border: 1px solid #e2e8e5;
        border-top: 4px solid #78a6bd;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 5px 15px rgba(43, 69, 58, 0.05);
    }

    .recommendation-card.delivery {
        border-top-color: #c98f8f;
    }

    .recommendation-card.market {
        border-top-color: #83aa8d;
    }

    .recommendation-card.feedback {
        border-top-color: #d2aa67;
    }

    .recommendation-label {
        color: #7b8c94;
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.07em;
    }

    .recommendation-title {
        color: #23465a;
        margin: 0.42rem 0;
        font-size: 1.05rem;
        font-weight: 750;
    }

    .recommendation-evidence {
        color: #536a76;
        min-height: 2.6rem;
        font-size: 0.84rem;
    }

    .recommendation-action {
        color: #284c60;
        margin-top: 0.75rem;
        padding-top: 0.7rem;
        border-top: 1px solid #edf1ef;
        font-size: 0.84rem;
        font-weight: 650;
    }

    /* Overview: project architecture */
    .architecture-panel {
        padding: 1.25rem;
        border: 1px solid #dfe7e4;
        border-radius: 14px;
        background: #ffffff;
        box-shadow: 0 5px 15px rgba(43, 69, 58, 0.045);
    }

    .architecture-flow {
        display: flex;
        align-items: stretch;
        justify-content: space-between;
        gap: 0.45rem;
    }

    .architecture-stage {
        flex: 1;
        min-width: 0;
        padding: 0.85rem 0.65rem;
        border-radius: 10px;
        text-align: center;
        background: #f4f8fa;
    }

    .architecture-stage strong {
        display: block;
        color: #244b61;
        font-size: 0.9rem;
    }

    .architecture-stage span {
        display: block;
        color: #7a8f9a;
        margin-top: 0.3rem;
        font-size: 0.7rem;
        line-height: 1.35;
    }

    .architecture-arrow {
        align-self: center;
        color: #73a3bc;
        font-size: 1.2rem;
        font-weight: 800;
    }

    .technology-stack {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.45rem;
        margin-top: 1rem;
        padding-top: 0.9rem;
        border-top: 1px solid #edf1ef;
    }

    .technology-badge {
        color: #35637b;
        padding: 0.3rem 0.62rem;
        border: 1px solid #d7e5ec;
        border-radius: 999px;
        background: #edf5f8;
        font-size: 0.72rem;
        font-weight: 700;
    }

    @media (max-width: 900px) {
        .recommendation-grid {
            grid-template-columns: 1fr;
        }

        .architecture-flow {
            flex-direction: column;
        }

        .architecture-arrow {
            transform: rotate(90deg);
        }
    }

    /* 页面标题与图标 */
    .page-heading {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        min-height: 68px;
        margin: 0 0 0.2rem 0;
    }

    .page-heading-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 52px;
        height: 52px;
        flex: 0 0 52px;
        border-radius: 14px;
        color: #eaf6fc;
        background: linear-gradient(145deg, #4d9ac5, #78b2d1);
        box-shadow: 0 7px 18px rgba(42, 112, 151, 0.18);
        font-size: 1.55rem;
        font-weight: 800;
    }

    .page-heading-icon.icon-overview {
        background: linear-gradient(145deg, #4d9ac5, #78b2d1);
    }

    .page-heading-icon.icon-sales {
        background: linear-gradient(145deg, #5d9e91, #83b8ae);
    }

    .page-heading-icon.icon-reviews {
        background: linear-gradient(145deg, #c79b50, #dbbd7c);
    }

    .page-heading-icon.icon-quality {
        background: linear-gradient(145deg, #8176aa, #a89fc6);
    }

    .page-heading-icon.icon-explorer {
        background: linear-gradient(145deg, #bf7479, #d59a9d);
    }

    .page-heading-title {
        color: #123b57;
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -0.035em;
    }

    .page-heading-subtitle {
        color: #718794;
        margin-top: 0.4rem;
        font-size: 0.92rem;
        font-weight: 500;
    }

    /* 动态星级评分 */
    .rating-card {
        display: flex;
        align-items: center;
        gap: 1.1rem;
        margin: 1rem 0 1.4rem 0;
        padding: 0.9rem 1.15rem;
        border: 1px solid #e4e9e6;
        border-radius: 12px;
        background: #ffffff;
    }

    .rating-stars {
        position: relative;
        display: inline-block;
        color: #dfe5e2;
        font-size: 1.8rem;
        line-height: 1;
        letter-spacing: 0.12rem;
        white-space: nowrap;
    }

    .rating-stars-fill {
        position: absolute;
        top: 0;
        left: 0;
        overflow: hidden;
        color: #d2aa67;
        white-space: nowrap;
    }

    .rating-summary {
        color: #304c5d;
        font-size: 0.95rem;
        font-weight: 650;
    }

    .rating-summary span {
        color: #7a8d97;
        font-size: 0.82rem;
        font-weight: 500;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    logo_col, brand_col = st.columns(
        [0.38, 1.62],
        vertical_alignment="center",
    )

    with logo_col:
        st.image(
            str(OLIST_ANALYTICS_LOGO),
            width=58,
        )

    with brand_col:
        st.markdown(
            """
            <div class="sidebar-brand-title">OLIST DATA</div>
            <div class="sidebar-brand-subtitle">
                INDEPENDENT ANALYTICS
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    selected_page = st.radio(
        "Navigation",
        [
            "▣ Overview",
            "▥ Sales Analysis",
            "★ Customer Reviews",
            "✓ Data Quality",
            "▤ Data Explorer",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("DATA STATUS")
    st.success("PostgreSQL Connected")

    if st.button(
        "Refresh Dashboard",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        "Unofficial portfolio project · Not affiliated with "
        "or endorsed by Olist."
    )



@st.cache_resource
def create_database_engine():
    return get_engine()


@st.cache_data(ttl=600)
def load_query(query):
    engine = create_database_engine()

    with engine.connect() as connection:
        return pd.read_sql_query(
            text(query),
            connection,
        )

@st.cache_data(ttl=600)
def load_sales_filter_options():
    engine = create_database_engine()

    with engine.connect() as connection:
        date_range = pd.read_sql_query(
            text("""
                SELECT
                    MIN(order_purchase_timestamp)::DATE
                        AS min_date,
                    MAX(order_purchase_timestamp)::DATE
                        AS max_date
                FROM mart.fact_sales;
            """),
            connection,
        ).iloc[0]

        states = pd.read_sql_query(
            text("""
                SELECT DISTINCT customer_state
                FROM mart.fact_sales
                ORDER BY customer_state;
            """),
            connection,
        )["customer_state"].tolist()

        categories = pd.read_sql_query(
            text("""
                SELECT DISTINCT
                    product_category_name_english
                        AS product_category
                FROM mart.fact_sales
                ORDER BY product_category;
            """),
            connection,
        )["product_category"].tolist()

    return {
        "min_date": date_range["min_date"],
        "max_date": date_range["max_date"],
        "states": states,
        "categories": categories,
    }


@st.cache_data(ttl=600)
def load_filtered_fact_sales(
    start_date,
    end_date,
    selected_state,
    selected_category,
):
    engine = create_database_engine()

    query = text("""
        SELECT
            order_id,
            order_item_id,
            order_month,
            customer_unique_id,
            customer_state,
            product_category_name_english
                AS product_category,
            price,
            freight_value,
            total_value
        FROM mart.fact_sales
        WHERE order_purchase_timestamp::DATE
            BETWEEN :start_date AND :end_date

          AND (
              :selected_state = 'All'
              OR customer_state = :selected_state
          )

          AND (
              :selected_category = 'All'
              OR product_category_name_english
                  = :selected_category
          );
    """)

    parameters = {
        "start_date": start_date,
        "end_date": end_date,
        "selected_state": selected_state,
        "selected_category": selected_category,
    }

    with engine.connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters,
        )


@st.cache_data(ttl=600)
def load_review_filter_options():
    engine = create_database_engine()

    with engine.connect() as connection:
        date_range = pd.read_sql_query(
            text("""
                SELECT
                    MIN(order_purchase_timestamp)::DATE AS min_date,
                    MAX(order_purchase_timestamp)::DATE AS max_date
                FROM mart.order_reviews
                WHERE order_status = 'delivered';
            """),
            connection,
        ).iloc[0]

        states = pd.read_sql_query(
            text("""
                SELECT DISTINCT customer_state
                FROM mart.order_reviews
                WHERE order_status = 'delivered'
                ORDER BY customer_state;
            """),
            connection,
        )["customer_state"].tolist()

    return {
        "min_date": date_range["min_date"],
        "max_date": date_range["max_date"],
        "states": states,
    }


@st.cache_data(ttl=600)
def load_filtered_reviews(start_date, end_date, selected_state):
    engine = create_database_engine()
    query = text("""
        SELECT
            order_id,
            review_score,
            order_month,
            customer_state,
            is_late,
            has_written_comment
        FROM mart.order_reviews
        WHERE order_status = 'delivered'
          AND order_purchase_timestamp::DATE
              BETWEEN :start_date AND :end_date
          AND (
              :selected_state = 'All'
              OR customer_state = :selected_state
          );
    """)

    with engine.connect() as connection:
        return pd.read_sql_query(
            query,
            connection,
            params={
                "start_date": start_date,
                "end_date": end_date,
                "selected_state": selected_state,
            },
        )


@st.cache_data(ttl=600)
def load_data_quality_results():
    engine = create_database_engine()

    counts_query = text("""
        SELECT 'Raw' AS layer, 'Orders' AS dataset,
               COUNT(*) AS row_count FROM raw.orders
        UNION ALL
        SELECT 'Staging', 'Orders', COUNT(*) FROM staging.orders
        UNION ALL
        SELECT 'Raw', 'Customers', COUNT(*) FROM raw.customers
        UNION ALL
        SELECT 'Staging', 'Customers', COUNT(*)
        FROM staging.customers
        UNION ALL
        SELECT 'Raw', 'Order Items', COUNT(*)
        FROM raw.order_items
        UNION ALL
        SELECT 'Staging', 'Order Items', COUNT(*)
        FROM staging.order_items
        UNION ALL
        SELECT 'Raw', 'Products', COUNT(*) FROM raw.products
        UNION ALL
        SELECT 'Staging', 'Products', COUNT(*)
        FROM staging.products
        UNION ALL
        SELECT 'Raw', 'Order Reviews', COUNT(*)
        FROM raw.order_reviews
        UNION ALL
        SELECT 'Staging', 'Order Reviews', COUNT(*)
        FROM staging.order_reviews
        UNION ALL
        SELECT 'Mart', 'Fact Sales', COUNT(*) FROM mart.fact_sales
        UNION ALL
        SELECT 'Mart', 'Order Reviews', COUNT(*)
        FROM mart.order_reviews;
    """)

    checks_query = text("""
        SELECT 'raw.orders' AS source_table,
               'Missing order ID' AS check_name,
               COUNT(*) AS issue_count,
               'Critical' AS severity
        FROM raw.orders
        WHERE order_id IS NULL OR TRIM(order_id) = ''

        UNION ALL
        SELECT 'raw.orders', 'Duplicate order ID', COUNT(*), 'Critical'
        FROM (
            SELECT order_id
            FROM raw.orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) AS duplicates

        UNION ALL
        SELECT 'raw.customers', 'Missing customer ID', COUNT(*),
               'Critical'
        FROM raw.customers
        WHERE customer_id IS NULL OR TRIM(customer_id) = ''

        UNION ALL
        SELECT 'raw.customers', 'Duplicate customer ID', COUNT(*),
               'Critical'
        FROM (
            SELECT customer_id
            FROM raw.customers
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        ) AS duplicates

        UNION ALL
        SELECT 'raw.order_items', 'Duplicate order item key', COUNT(*),
               'Critical'
        FROM (
            SELECT order_id, order_item_id
            FROM raw.order_items
            GROUP BY order_id, order_item_id
            HAVING COUNT(*) > 1
        ) AS duplicates

        UNION ALL
        SELECT 'staging.orders', 'Unmatched customer ID', COUNT(*),
               'Critical'
        FROM staging.orders AS orders
        LEFT JOIN staging.customers AS customers
          ON orders.customer_id = customers.customer_id
        WHERE customers.customer_id IS NULL

        UNION ALL
        SELECT 'staging.order_items', 'Unmatched product ID', COUNT(*),
               'Critical'
        FROM staging.order_items AS items
        LEFT JOIN staging.products AS products
          ON items.product_id = products.product_id
        WHERE products.product_id IS NULL

        UNION ALL
        SELECT 'mart.fact_sales', 'Duplicate fact key', COUNT(*),
               'Critical'
        FROM (
            SELECT order_id, order_item_id
            FROM mart.fact_sales
            GROUP BY order_id, order_item_id
            HAVING COUNT(*) > 1
        ) AS duplicates

        UNION ALL
        SELECT 'staging.orders',
               'Delivered order missing delivery date', COUNT(*),
               'Warning'
        FROM staging.orders
        WHERE order_status = 'delivered'
          AND order_delivered_customer_date IS NULL

        UNION ALL
        SELECT 'staging.products', 'Unknown product category', COUNT(*),
               'Warning'
        FROM staging.products
        WHERE product_category_name_english = 'unknown'

        UNION ALL
        SELECT 'staging.products', 'Untranslated product category',
               COUNT(*), 'Warning'
        FROM staging.products
        WHERE product_category_name_english LIKE 'untranslated_%'

        UNION ALL
        SELECT 'raw.order_reviews', 'Orders with multiple reviews',
               COUNT(*), 'Warning'
        FROM (
            SELECT order_id
            FROM raw.order_reviews
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) AS multiple_reviews

        UNION ALL
        SELECT 'raw.order_reviews', 'Invalid review score', COUNT(*),
               'Critical'
        FROM raw.order_reviews
        WHERE NULLIF(TRIM(review_score), '')::INTEGER NOT BETWEEN 1 AND 5;
    """)

    refresh_query = text("""
        SELECT GREATEST(
            (SELECT MAX(loaded_at) FROM raw.orders),
            (SELECT MAX(loaded_at) FROM raw.customers),
            (SELECT MAX(loaded_at) FROM raw.order_items),
            (SELECT MAX(loaded_at) FROM raw.products),
            (SELECT MAX(loaded_at) FROM raw.order_reviews)
        ) AS last_refresh;
    """)

    with engine.connect() as connection:
        counts = pd.read_sql_query(counts_query, connection)
        checks = pd.read_sql_query(checks_query, connection)
        last_refresh = pd.read_sql_query(
            refresh_query,
            connection,
        ).iloc[0]["last_refresh"]

    return counts, checks, last_refresh


@st.cache_data(ttl=60)
def load_latest_pipeline_run():
    engine = create_database_engine()

    with engine.connect() as connection:
        audit_table_exists = connection.execute(
            text("SELECT to_regclass('audit.pipeline_runs');")
        ).scalar_one_or_none()

        if audit_table_exists is None:
            return None

        pipeline_run = pd.read_sql_query(
            text("""
                SELECT
                    run_id,
                    pipeline_name,
                    started_at,
                    completed_at,
                    duration_seconds,
                    total_steps,
                    completed_steps,
                    status,
                    failed_step,
                    error_message
                FROM audit.pipeline_runs
                ORDER BY started_at DESC
                LIMIT 1;
            """),
            connection,
        )

    if pipeline_run.empty:
        return None

    return pipeline_run.iloc[0].to_dict()


DATA_EXPLORER_TABLES = {
    "Sales Transactions": "mart.fact_sales",
    "Order Reviews": "mart.order_reviews",
    "Monthly Sales": "mart.monthly_sales",
    "Sales by State": "mart.state_sales",
    "Sales by Product Category": "mart.category_sales",
    "Monthly Reviews": "mart.monthly_reviews",
}


COLUMN_DESCRIPTIONS = {
    "order_id": "Unique identifier for an order.",
    "order_item_id": "Sequential item number within an order.",
    "order_status": "Current processing or delivery status.",
    "order_purchase_timestamp": "Date and time the order was placed.",
    "order_month": "First day of the order month used for reporting.",
    "customer_id": "Order-level customer identifier.",
    "customer_unique_id": "Identifier representing the real customer.",
    "customer_state": "Brazilian state of the customer.",
    "product_id": "Unique identifier for a product.",
    "product_category": "English product category used for reporting.",
    "product_category_name_english": (
        "English product category used for reporting."
    ),
    "seller_id": "Unique identifier for the seller.",
    "price": "Product sales value, excluding freight.",
    "freight_value": "Freight amount charged for the order item.",
    "total_value": "Product price plus freight value.",
    "total_sales": "Sum of product sales, excluding freight.",
    "total_freight": "Sum of freight charges.",
    "total_transaction_value": "Combined product and freight value.",
    "total_orders": "Number of distinct orders.",
    "total_customers": "Number of distinct customers.",
    "average_order_sales": "Average product sales per order.",
    "review_id": "Unique identifier for a customer review.",
    "review_score": "Customer rating from 1 to 5.",
    "review_creation_date": "Date the review survey was created.",
    "review_answer_timestamp": "Date and time the review was submitted.",
    "is_positive_review": "True when the score is 4 or 5.",
    "is_neutral_review": "True when the score is 3.",
    "is_negative_review": "True when the score is 1 or 2.",
    "has_written_comment": "Whether the review contains written text.",
    "reviewed_orders": "Number of orders with a retained review.",
    "average_review_score": "Mean customer review score.",
    "positive_review_rate": "Percentage of scores equal to 4 or 5.",
    "negative_review_rate": "Percentage of scores equal to 1 or 2.",
    "delivery_time_days": "Days from purchase to customer delivery.",
    "is_late": "Whether delivery occurred after the estimated date.",
    "mart_created_at": "Timestamp when the Mart table was created.",
}


def validate_explorer_table(table_name):
    if table_name not in DATA_EXPLORER_TABLES.values():
        raise ValueError("The selected table is not approved for preview.")

    return table_name.split(".", maxsplit=1)


@st.cache_data(ttl=600)
def load_dataset_metadata(table_name):
    schema_name, relation_name = validate_explorer_table(table_name)
    engine = create_database_engine()

    columns_query = text("""
        SELECT
            column_name,
            data_type,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = :schema_name
          AND table_name = :relation_name
        ORDER BY ordinal_position;
    """)
    count_query = text(
        f'SELECT COUNT(*) AS row_count '
        f'FROM "{schema_name}"."{relation_name}";'
    )

    with engine.connect() as connection:
        columns = pd.read_sql_query(
            columns_query,
            connection,
            params={
                "schema_name": schema_name,
                "relation_name": relation_name,
            },
        )
        total_rows = int(
            pd.read_sql_query(
                count_query,
                connection,
            ).iloc[0]["row_count"]
        )

    return columns, total_rows


@st.cache_data(ttl=600)
def load_dataset_preview(table_name, preview_rows, search_term):
    schema_name, relation_name = validate_explorer_table(table_name)
    qualified_table = f'"{schema_name}"."{relation_name}"'
    cleaned_search = search_term.strip()
    parameters = {"preview_rows": int(preview_rows)}
    count_parameters = {}

    if cleaned_search:
        where_clause = "WHERE source_row::TEXT ILIKE :search_pattern"
        parameters["search_pattern"] = f"%{cleaned_search}%"
        count_parameters["search_pattern"] = f"%{cleaned_search}%"
    else:
        where_clause = ""

    preview_query = text(
        f"""
        SELECT *
        FROM {qualified_table} AS source_row
        {where_clause}
        LIMIT :preview_rows;
        """
    )
    matching_count_query = text(
        f"""
        SELECT COUNT(*) AS matching_rows
        FROM {qualified_table} AS source_row
        {where_clause};
        """
    )

    with create_database_engine().connect() as connection:
        preview = pd.read_sql_query(
            preview_query,
            connection,
            params=parameters,
        )
        matching_rows = int(
            pd.read_sql_query(
                matching_count_query,
                connection,
                params=count_parameters,
            ).iloc[0]["matching_rows"]
        )

    return preview, matching_rows

def convert_numeric(dataframe, columns):
    for column in columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    return dataframe


def format_period_delta(
    current_value,
    previous_value,
    comparison_label="vs prior period",
):
    if previous_value is None or previous_value == 0:
        return "No comparable prior value"

    percentage_change = (
        (current_value - previous_value)
        / previous_value
        * 100
    )
    return f"{percentage_change:+.1f}% {comparison_label}"


DATE_PERIOD_OPTIONS = [
    "Full Dataset",
    "Latest 3 Months",
    "Latest 6 Months",
    "Latest 12 Months",
    "2017",
    "2018 Available Data",
    "Custom Range",
]


def resolve_period_dates(period_name, min_date, max_date):
    min_date = pd.Timestamp(min_date).date()
    max_date = pd.Timestamp(max_date).date()

    if period_name == "Full Dataset":
        return min_date, max_date

    if period_name.startswith("Latest"):
        month_count = int(period_name.split()[1])
        calculated_start = (
            pd.Timestamp(max_date)
            - pd.DateOffset(months=month_count)
            + pd.Timedelta(days=1)
        ).date()
        return max(min_date, calculated_start), max_date

    if period_name == "2017":
        return max(min_date, pd.Timestamp("2017-01-01").date()), min(
            max_date,
            pd.Timestamp("2017-12-31").date(),
        )

    if period_name == "2018 Available Data":
        return max(min_date, pd.Timestamp("2018-01-01").date()), max_date

    return min_date, max_date


def resolve_comparison_dates(
    period_name,
    start_date,
    end_date,
    min_date,
):
    min_date = pd.Timestamp(min_date).date()

    if period_name in {"Full Dataset", "2017"}:
        return None

    if period_name == "2018 Available Data":
        comparison_start = (
            pd.Timestamp(start_date) - pd.DateOffset(years=1)
        ).date()
        comparison_end = (
            pd.Timestamp(end_date) - pd.DateOffset(years=1)
        ).date()
    else:
        period_days = (end_date - start_date).days + 1
        comparison_end = start_date - timedelta(days=1)
        comparison_start = comparison_end - timedelta(
            days=period_days - 1
        )

    if comparison_start < min_date:
        return None

    return comparison_start, comparison_end

def style_chart(figure):
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={
            "family": "Inter, Segoe UI, Arial, sans-serif",
            "color": "#647069",
        },
        title={
            "font": {
                "size": 16,
                "color": "#34443c",
            },
            "x": 0.02,
            "xanchor": "left",
        },
        margin={
            "l": 30,
            "r": 20,
            "t": 60,
            "b": 30,
        },
        hoverlabel={
            "bgcolor": "#52645a",
            "font_color": "#ffffff",
            "bordercolor": "#52645a",
        },
    )

    figure.update_xaxes(
        showgrid=False,
        linecolor="#e4eae6",
        tickfont_color="#7a8780",
        title_font_color="#647069",
    )

    figure.update_yaxes(
        gridcolor="#edf1ee",
        linecolor="#e4eae6",
        tickfont_color="#7a8780",
        title_font_color="#647069",
    )

    return figure


def render_page_header(icon, title, subtitle, color_class):
    st.markdown(
        f"""
        <div class="page-heading">
            <div class="page-heading-icon {color_class}">{icon}</div>
            <div>
                <div class="page-heading-title">{title}</div>
                <div class="page-heading-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_star_rating(score, review_count):
    fill_percentage = max(0, min(float(score) / 5 * 100, 100))
    stars = "&#9733;&#9733;&#9733;&#9733;&#9733;"

    st.markdown(
        f"""
        <div class="rating-card">
            <div class="rating-stars">
                {stars}
                <div class="rating-stars-fill"
                     style="width: {fill_percentage:.1f}%">
                    {stars}
                </div>
            </div>
            <div class="rating-summary">
                {float(score):.2f} out of 5<br>
                <span>Based on {int(review_count):,} delivered-order reviews</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def keep_top_groups(dataframe, label_column, top_n=8):
    ranked = dataframe.sort_values(
        "total_sales",
        ascending=False,
    )
    top_groups = ranked.head(top_n)[
        [label_column, "total_sales"]
    ].copy()
    other_sales = ranked.iloc[top_n:]["total_sales"].sum()

    if other_sales > 0:
        other_group = pd.DataFrame(
            {
                label_column: ["Other"],
                "total_sales": [other_sales],
            }
        )
        top_groups = pd.concat(
            [top_groups, other_group],
            ignore_index=True,
        )

    return top_groups


# -------------------------
# 加载数据
# -------------------------

sales_kpis = load_query("""
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(DISTINCT customer_unique_id)
            AS total_customers,
        SUM(price) AS total_sales,
        SUM(freight_value) AS total_freight,
        SUM(total_value) AS total_transaction_value,
        SUM(price) / COUNT(DISTINCT order_id)
            AS average_order_sales
    FROM mart.fact_sales;
""").iloc[0]

review_kpis = load_query("""
    SELECT *
    FROM mart.review_kpis;
""").iloc[0]

monthly_sales = load_query("""
    SELECT *
    FROM mart.monthly_sales
    ORDER BY order_month;
""")

state_sales = load_query("""
    SELECT *
    FROM mart.state_sales
    ORDER BY total_sales DESC;
""")

category_sales = load_query("""
    SELECT *
    FROM mart.category_sales
    ORDER BY total_sales DESC
    LIMIT 15;
""")

review_distribution = load_query("""
    SELECT *
    FROM mart.review_distribution
    ORDER BY review_score;
""")

monthly_reviews = load_query("""
    SELECT *
    FROM mart.monthly_reviews
    ORDER BY order_month;
""")

delivery_reviews = load_query("""
    SELECT *
    FROM mart.delivery_review_summary
    ORDER BY delivery_status;
""")


# -------------------------
# 类型转换
# -------------------------

monthly_sales["order_month"] = pd.to_datetime(
    monthly_sales["order_month"]
)

monthly_reviews["order_month"] = pd.to_datetime(
    monthly_reviews["order_month"]
)

monthly_sales = convert_numeric(
    monthly_sales,
    [
        "total_sales",
        "total_orders",
        "average_order_sales",
    ],
)

state_sales = convert_numeric(
    state_sales,
    [
        "total_sales",
        "total_orders",
    ],
)

category_sales = convert_numeric(
    category_sales,
    [
        "total_sales",
        "total_orders",
    ],
)

review_distribution = convert_numeric(
    review_distribution,
    [
        "review_score",
        "review_count",
        "review_percentage",
    ],
)

monthly_reviews = convert_numeric(
    monthly_reviews,
    [
        "average_review_score",
        "reviewed_orders",
    ],
)

delivery_reviews = convert_numeric(
    delivery_reviews,
    [
        "average_review_score",
        "reviewed_orders",
        "negative_review_rate",
    ],
)
def render_sales_analysis():
    filter_options = load_sales_filter_options()

    header, date_col, state_col, category_col = st.columns(
        [2.2, 1.5, 1.1, 1.7],
        vertical_alignment="bottom",
    )

    with header:
        render_page_header(
            "&#8599;",
            "Sales Analysis",
            "Delivered-order sales performance",
            "icon-sales",
        )

    with date_col:
        selected_period = st.selectbox(
            "Period",
            options=DATE_PERIOD_OPTIONS,
            key="sales_period",
            help=(
                "Latest and Custom ranges are compared with the "
                "immediately preceding period of equal length. "
                "2018 Available Data is compared with the same "
                "dates in 2017. Comparisons require complete data "
                "coverage."
            ),
        )

        if selected_period == "Custom Range":
            with st.popover("Choose custom dates", width="stretch"):
                start_date = st.date_input(
                    "Start Date",
                    value=filter_options["min_date"],
                    min_value=filter_options["min_date"],
                    max_value=filter_options["max_date"],
                    key="sales_custom_start",
                )
                end_date = st.date_input(
                    "End Date",
                    value=filter_options["max_date"],
                    min_value=filter_options["min_date"],
                    max_value=filter_options["max_date"],
                    key="sales_custom_end",
                )
        else:
            start_date, end_date = resolve_period_dates(
                selected_period,
                filter_options["min_date"],
                filter_options["max_date"],
            )

    with state_col:
        selected_state = st.selectbox(
            "State",
            options=[
                "All",
                *filter_options["states"],
            ],
            key="sales_state",
        )

    with category_col:
        selected_category = st.selectbox(
            "Product Category",
            options=[
                "All",
                *filter_options["categories"],
            ],
            key="sales_category",
        )

    if start_date > end_date:
        st.warning(
            "Start Date must be on or before End Date."
        )
        return

    st.caption(
        f"Reporting period: {start_date:%d %b %Y} - "
        f"{end_date:%d %b %Y}"
    )
    comparison_dates = resolve_comparison_dates(
        selected_period,
        start_date,
        end_date,
        filter_options["min_date"],
    )
    comparison_label = (
        "vs same dates in 2017"
        if selected_period == "2018 Available Data"
        else "vs preceding equal-length period"
    )

    if comparison_dates is None:
        st.caption(
            "KPI comparison is unavailable because the preceding "
            "period is not fully covered by the dataset."
        )
    else:
        comparison_start, comparison_end = comparison_dates
        st.caption(
            f"Comparison period: {comparison_start:%d %b %Y} - "
            f"{comparison_end:%d %b %Y}"
        )

    filtered_sales = load_filtered_fact_sales(
        start_date=start_date,
        end_date=end_date,
        selected_state=selected_state,
        selected_category=selected_category,
    )

    if filtered_sales.empty:
        st.warning(
            "No sales records match the selected filters."
        )
        return

    filtered_sales["order_month"] = pd.to_datetime(
        filtered_sales["order_month"]
    )

    filtered_sales = convert_numeric(
        filtered_sales,
        [
            "price",
            "freight_value",
            "total_value",
        ],
    )

    if comparison_dates is None:
        previous_sales = filtered_sales.iloc[0:0].copy()
    else:
        comparison_start, comparison_end = comparison_dates
        previous_sales = load_filtered_fact_sales(
            start_date=comparison_start,
            end_date=comparison_end,
            selected_state=selected_state,
            selected_category=selected_category,
        )
    previous_sales = convert_numeric(
        previous_sales,
        ["price", "freight_value", "total_value"],
    )

    total_sales = filtered_sales["price"].sum()
    total_orders = filtered_sales["order_id"].nunique()
    total_customers = (
        filtered_sales["customer_unique_id"].nunique()
    )

    average_order_sales = (
        total_sales / total_orders
        if total_orders > 0
        else 0
    )

    previous_total_sales = previous_sales["price"].sum()
    previous_total_orders = previous_sales["order_id"].nunique()
    previous_total_customers = previous_sales[
        "customer_unique_id"
    ].nunique()
    previous_average_order_sales = (
        previous_total_sales / previous_total_orders
        if previous_total_orders > 0
        else 0
    )

    monthly_sales = (
        filtered_sales.groupby(
            "order_month",
            as_index=False,
        )
        .agg(
            total_sales=("price", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values("order_month")
    )

    monthly_sales["average_order_sales"] = (
        monthly_sales["total_sales"]
        / monthly_sales["total_orders"]
    )

    state_sales = (
        filtered_sales.groupby(
            "customer_state",
            as_index=False,
        )
        .agg(
            total_sales=("price", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values(
            "total_sales",
            ascending=False,
        )
    )

    category_sales = (
        filtered_sales.groupby(
            "product_category",
            as_index=False,
        )
        .agg(
            total_sales=("price", "sum"),
            total_orders=("order_id", "nunique"),
        )
        .sort_values(
            "total_sales",
            ascending=False,
        )
    )

    state_sales_top = keep_top_groups(
        state_sales,
        "customer_state",
    )
    category_sales_top = keep_top_groups(
        category_sales,
        "product_category",
    )

    st.info(
        "Data coverage for 2016 is incomplete. Monthly trends "
        "should be interpreted primarily using data from "
        "2017 onward."
    )

    col1, col2, col3, col4 = st.columns(4, gap="medium",)

    with col1:
        with st.container(key="sales_primary_kpi"):
            st.metric(
                "Total Sales",
                f"R$ {total_sales:,.2f}",
                delta=format_period_delta(
                    total_sales,
                    previous_total_sales,
                    comparison_label,
                ),
            )

    col2.metric(
        "Total Orders",
        f"{total_orders:,}",
        delta=format_period_delta(
            total_orders,
            previous_total_orders,
            comparison_label,
        ),
    )

    col3.metric(
        "Total Customers",
        f"{total_customers:,}",
        delta=format_period_delta(
            total_customers,
            previous_total_customers,
            comparison_label,
        ),
    )

    col4.metric(
        "Average Order Sales",
        f"R$ {average_order_sales:,.2f}",
        delta=format_period_delta(
            average_order_sales,
            previous_average_order_sales,
            comparison_label,
        ),
    )

    st.subheader("Monthly Performance")

    left, right = st.columns(2)

    monthly_sales_chart = px.line(
        monthly_sales,
        x="order_month",
        y="total_sales",
        markers=True,
        title="Monthly Sales",
        labels={
            "order_month": "Month",
            "total_sales": "Sales (R$)",
        },
    )
    monthly_sales_chart.update_traces(
        line_color="#78a985",
        line_width=3,
        marker={
            "size": 7,
            "color": "#78a985",
        },
    )

    style_chart(monthly_sales_chart)

    left.plotly_chart(
        monthly_sales_chart,
        use_container_width=True,
    )

    monthly_orders_chart = px.line(
        monthly_sales,
        x="order_month",
        y="total_orders",
        markers=True,
        title="Monthly Order Count",
        labels={
            "order_month": "Month",
            "total_orders": "Orders",
        },
    )

    monthly_orders_chart.update_traces(
        line_color="#86a9c9",
        line_width=3,
        marker={
            "size": 7,
            "color": "#86a9c9",
        },
    )

    style_chart(monthly_orders_chart)

    right.plotly_chart(
        monthly_orders_chart,
        use_container_width=True,
    )

    average_order_chart = px.line(
        monthly_sales,
        x="order_month",
        y="average_order_sales",
        markers=True,
        title="Monthly Average Order Sales",
        labels={
            "order_month": "Month",
            "average_order_sales": (
                "Average Order Sales (R$)"
            ),
        },
    )

    average_order_chart.update_traces(
        line_color="#d2aa67",
        line_width=3,
        marker={
            "size": 7,
            "color": "#d2aa67",
        },
        fill="tozeroy",
        fillcolor="rgba(210, 170, 103, 0.12)",
    )

    style_chart(average_order_chart)

    st.plotly_chart(
        average_order_chart,
        use_container_width=True,
    )

    st.subheader("Geographic and Product Performance")

    left, right = st.columns(2)

    state_chart = px.pie(
        state_sales_top,
        names="customer_state",
        values="total_sales",
        hole=0.58,
        title="Sales Share by Customer State",
        labels={
            "customer_state": "State",
            "total_sales": "Sales (R$)",
        },
        color_discrete_sequence=[
            "#789f86",
            "#91b59a",
            "#abc9b1",
            "#88a9bd",
            "#a5bdcc",
            "#b7abc8",
            "#c9bed5",
            "#d7bd8a",
            "#d9ddd9",
        ],
    )

    state_chart.update_traces(
        textposition="inside",
        textinfo="percent",
        marker={
            "line": {
                "color": "#ffffff",
                "width": 2,
            }
        },
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sales: R$ %{value:,.2f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    )

    style_chart(state_chart)
    state_chart.update_layout(
        legend_title_text="State",
        legend={
            "orientation": "v",
            "yanchor": "middle",
            "y": 0.5,
            "xanchor": "left",
            "x": 1.0,
        },
    )

    left.plotly_chart(
        state_chart,
        use_container_width=True,
    )

    category_chart = px.pie(
        category_sales_top,
        names="product_category",
        values="total_sales",
        hole=0.58,
        title="Sales Share by Product Category",
        labels={
            "product_category": "Product Category",
            "total_sales": "Sales (R$)",
        },
        color_discrete_sequence=[
            "#9d91b3",
            "#b2a5c4",
            "#c6bbd2",
            "#83a7b6",
            "#9dbbc5",
            "#91af99",
            "#afc4b4",
            "#d4b77f",
            "#d9ddd9",
        ],
    )

    category_chart.update_traces(
        textposition="inside",
        textinfo="percent",
        marker={
            "line": {
                "color": "#ffffff",
                "width": 2,
            }
        },
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sales: R$ %{value:,.2f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    )

    style_chart(category_chart)
    category_chart.update_layout(
        legend_title_text="Product Category",
        legend={
            "orientation": "v",
            "yanchor": "middle",
            "y": 0.5,
            "xanchor": "left",
            "x": 1.0,
        },
    )

    right.plotly_chart(
        category_chart,
        use_container_width=True,
    )

    with st.expander("View Monthly Sales Data"):
        st.dataframe(
            monthly_sales,
            use_container_width=True,
            hide_index=True,
        )


def render_customer_reviews():
    filter_options = load_review_filter_options()

    header, date_col, state_col = st.columns(
        [3.2, 1.7, 1.1],
        vertical_alignment="bottom",
    )

    with header:
        render_page_header(
            "&#9733;",
            "Customer Reviews",
            "Customer satisfaction and delivery experience",
            "icon-reviews",
        )

    with date_col:
        selected_period = st.selectbox(
            "Period",
            options=DATE_PERIOD_OPTIONS,
            key="review_period",
            help=(
                "Latest and Custom ranges are compared with the "
                "immediately preceding period of equal length. "
                "2018 Available Data is compared with the same "
                "dates in 2017. Comparisons require complete data "
                "coverage."
            ),
        )

        if selected_period == "Custom Range":
            with st.popover("Choose custom dates", width="stretch"):
                start_date = st.date_input(
                    "Start Date",
                    value=filter_options["min_date"],
                    min_value=filter_options["min_date"],
                    max_value=filter_options["max_date"],
                    key="review_custom_start",
                )
                end_date = st.date_input(
                    "End Date",
                    value=filter_options["max_date"],
                    min_value=filter_options["min_date"],
                    max_value=filter_options["max_date"],
                    key="review_custom_end",
                )
        else:
            start_date, end_date = resolve_period_dates(
                selected_period,
                filter_options["min_date"],
                filter_options["max_date"],
            )

    with state_col:
        selected_state = st.selectbox(
            "State",
            options=["All", *filter_options["states"]],
            key="review_state",
        )

    if start_date > end_date:
        st.warning(
            "Start Date must be on or before End Date."
        )
        return

    st.caption(
        f"Reporting period: {start_date:%d %b %Y} – "
        f"{end_date:%d %b %Y}"
    )
    comparison_dates = resolve_comparison_dates(
        selected_period,
        start_date,
        end_date,
        filter_options["min_date"],
    )
    comparison_label = (
        "vs same dates in 2017"
        if selected_period == "2018 Available Data"
        else "vs preceding equal-length period"
    )

    if comparison_dates is None:
        st.caption(
            "KPI comparison is unavailable because the preceding "
            "period is not fully covered by the dataset."
        )
    else:
        comparison_start, comparison_end = comparison_dates
        st.caption(
            f"Comparison period: {comparison_start:%d %b %Y} - "
            f"{comparison_end:%d %b %Y}"
        )

    reviews = load_filtered_reviews(
        start_date,
        end_date,
        selected_state,
    )

    if reviews.empty:
        st.warning(
            "No review records match the selected filters."
        )
        return

    reviews["order_month"] = pd.to_datetime(
        reviews["order_month"]
    )
    reviews["review_score"] = pd.to_numeric(
        reviews["review_score"],
        errors="coerce",
    )

    if comparison_dates is None:
        previous_reviews = reviews.iloc[0:0].copy()
    else:
        comparison_start, comparison_end = comparison_dates
        previous_reviews = load_filtered_reviews(
            comparison_start,
            comparison_end,
            selected_state,
        )
    previous_reviews["review_score"] = pd.to_numeric(
        previous_reviews["review_score"],
        errors="coerce",
    )

    reviewed_orders = reviews["order_id"].nunique()
    average_score = reviews["review_score"].mean()
    positive_rate = (
        reviews["review_score"].ge(4).mean() * 100
    )
    negative_rate = (
        reviews["review_score"].le(2).mean() * 100
    )
    written_comments = int(
        reviews["has_written_comment"].fillna(False).sum()
    )
    previous_reviewed_orders = previous_reviews[
        "order_id"
    ].nunique()
    previous_average_score = (
        previous_reviews["review_score"].mean()
        if not previous_reviews.empty
        else 0
    )
    previous_positive_rate = (
        previous_reviews["review_score"].ge(4).mean() * 100
        if not previous_reviews.empty
        else 0
    )
    previous_negative_rate = (
        previous_reviews["review_score"].le(2).mean() * 100
        if not previous_reviews.empty
        else 0
    )

    st.info(
        "Scores 1–2 are classified as Negative, "
        "3 as Neutral, and 4–5 as Positive."
    )

    col1, col2, col3, col4 = st.columns(
        4,
        gap="medium",
    )
    with col1:
        with st.container(key="review_primary_kpi"):
            st.metric(
                "Average Review Score",
                f"{average_score:.2f} / 5",
                delta=format_period_delta(
                    average_score,
                    previous_average_score,
                    comparison_label,
                ),
            )
    col2.metric(
        "Reviewed Orders",
        f"{reviewed_orders:,}",
        delta=format_period_delta(
            reviewed_orders,
            previous_reviewed_orders,
            comparison_label,
        ),
    )
    col3.metric(
        "Positive Review Rate",
        f"{positive_rate:.2f}%",
        delta=format_period_delta(
            positive_rate,
            previous_positive_rate,
            comparison_label,
        ),
    )
    col4.metric(
        "Negative Review Rate",
        f"{negative_rate:.2f}%",
        delta=format_period_delta(
            negative_rate,
            previous_negative_rate,
            comparison_label,
        ),
        delta_color="inverse",
    )

    render_star_rating(
        average_score,
        reviewed_orders,
    )

    st.subheader("Review Overview")
    left, right = st.columns(2)

    score_distribution = (
        reviews["review_score"]
        .value_counts()
        .reindex(range(1, 6), fill_value=0)
        .rename_axis("review_score")
        .reset_index(name="review_count")
    )
    score_chart = px.bar(
        score_distribution,
        x="review_score",
        y="review_count",
        text="review_count",
        title="Review Score Distribution",
        labels={
            "review_score": "Review Score",
            "review_count": "Reviews",
        },
        color="review_score",
        color_continuous_scale=[
            [0.0, "#c98f8f"],
            [0.5, "#d5bd88"],
            [1.0, "#83aa8d"],
        ],
    )
    score_chart.update_traces(
        textposition="outside",
        marker_line_width=0,
        hovertemplate=(
            "Score %{x}<br>Reviews: %{y:,}<extra></extra>"
        ),
    )
    score_chart.update_layout(
        coloraxis_showscale=False,
        showlegend=False,
    )
    score_chart.update_xaxes(dtick=1)
    style_chart(score_chart)
    left.plotly_chart(
        score_chart,
        use_container_width=True,
    )

    sentiment = pd.DataFrame(
        {
            "sentiment": ["Positive", "Neutral", "Negative"],
            "review_count": [
                int(reviews["review_score"].ge(4).sum()),
                int(reviews["review_score"].eq(3).sum()),
                int(reviews["review_score"].le(2).sum()),
            ],
        }
    )
    sentiment_chart = px.pie(
        sentiment,
        names="sentiment",
        values="review_count",
        hole=0.6,
        title="Review Sentiment",
        color="sentiment",
        color_discrete_map={
            "Positive": "#83aa8d",
            "Neutral": "#d5bd88",
            "Negative": "#c98f8f",
        },
    )
    sentiment_chart.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker={
            "line": {
                "color": "#ffffff",
                "width": 2,
            }
        },
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Reviews: %{value:,}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    )
    style_chart(sentiment_chart)
    sentiment_chart.update_layout(
        legend_title_text="Sentiment",
    )
    right.plotly_chart(
        sentiment_chart,
        use_container_width=True,
    )
    right.caption(
        f"Written comments: {written_comments:,}"
    )

    st.subheader("Review Trends and Delivery Impact")
    left, right = st.columns(2)

    monthly_review_data = (
        reviews.groupby("order_month", as_index=False)
        .agg(
            average_review_score=("review_score", "mean"),
            reviewed_orders=("order_id", "nunique"),
        )
        .sort_values("order_month")
    )
    monthly_review_chart = px.line(
        monthly_review_data,
        x="order_month",
        y="average_review_score",
        markers=True,
        title="Monthly Average Review Score",
        labels={
            "order_month": "Month",
            "average_review_score": "Average Score",
        },
    )
    monthly_review_chart.update_traces(
        line_color="#789f86",
        line_width=3,
        marker={"size": 7, "color": "#789f86"},
        hovertemplate=(
            "%{x|%b %Y}<br>Average score: %{y:.2f}"
            "<extra></extra>"
        ),
    )
    monthly_review_chart.update_yaxes(range=[0, 5])
    style_chart(monthly_review_chart)
    left.plotly_chart(
        monthly_review_chart,
        use_container_width=True,
    )

    delivery_data = reviews.copy()
    unknown_delivery_count = int(
        delivery_data["is_late"].isna().sum()
    )
    delivery_data = delivery_data[
        delivery_data["is_late"].notna()
    ].copy()
    delivery_data["delivery_status"] = (
        delivery_data["is_late"]
        .map({True: "Late", False: "On Time"})
    )
    delivery_summary = (
        delivery_data.groupby(
            "delivery_status",
            as_index=False,
        )
        .agg(
            average_review_score=("review_score", "mean"),
            reviewed_orders=("order_id", "nunique"),
        )
    )
    delivery_chart = px.bar(
        delivery_summary,
        x="delivery_status",
        y="average_review_score",
        color="delivery_status",
        text="average_review_score",
        title="Delivery Status vs Average Review Score",
        labels={
            "delivery_status": "Delivery Status",
            "average_review_score": "Average Score",
        },
        color_discrete_map={
            "On Time": "#83aa8d",
            "Late": "#c98f8f",
        },
    )
    delivery_chart.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>Average score: %{y:.2f}"
            "<extra></extra>"
        ),
    )
    delivery_chart.update_yaxes(range=[0, 5])
    delivery_chart.update_layout(showlegend=False)
    style_chart(delivery_chart)
    right.plotly_chart(
        delivery_chart,
        use_container_width=True,
    )
    if unknown_delivery_count > 0:
        right.caption(
            f"Excluded {unknown_delivery_count:,} delivered orders "
            "with no recorded delivery date; their late status "
            "cannot be determined."
        )

    with st.expander("View Monthly Review Data"):
        st.dataframe(
            monthly_review_data,
            use_container_width=True,
            hide_index=True,
        )


def render_data_quality():
    render_page_header(
        "&#10003;",
        "Data Quality",
        "Pipeline reliability across Raw, Staging, and Mart layers",
        "icon-quality",
    )

    counts, checks, last_refresh = load_data_quality_results()
    counts["row_count"] = pd.to_numeric(
        counts["row_count"],
        errors="coerce",
    ).fillna(0).astype(int)
    checks["issue_count"] = pd.to_numeric(
        checks["issue_count"],
        errors="coerce",
    ).fillna(0).astype(int)

    critical_issues = int(
        checks.loc[
            checks["severity"].eq("Critical"),
            "issue_count",
        ].sum()
    )
    warning_issues = int(
        checks.loc[
            checks["severity"].eq("Warning"),
            "issue_count",
        ].sum()
    )
    passed_checks = int(checks["issue_count"].eq(0).sum())
    pipeline_status = (
        "Healthy" if critical_issues == 0 else "Action Required"
    )

    refresh_timestamp = pd.to_datetime(last_refresh)
    if refresh_timestamp.tzinfo is not None:
        refresh_timestamp = refresh_timestamp.tz_convert("UTC")
    refresh_text = refresh_timestamp.strftime(
        "%d %b %Y · %H:%M"
    )

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        with st.container(key="quality_primary_kpi"):
            st.metric("Pipeline Status", pipeline_status)
    col2.metric("Critical Issues", f"{critical_issues:,}")
    col3.metric("Warning Records", f"{warning_issues:,}")
    col4.metric("Last Raw Refresh", refresh_text)

    if critical_issues == 0:
        st.success(
            "All critical checks passed. The warehouse is ready "
            "for dashboard reporting."
        )
    else:
        st.error(
            "Critical data quality issues were detected. Review "
            "the failed checks before using the warehouse."
        )

    st.subheader("Pipeline Run Summary")
    latest_run = load_latest_pipeline_run()

    if latest_run is None:
        st.info(
            "No persisted Pipeline run is available yet. Run "
            "`python scripts/olist/run_pipeline.py` once to create "
            "the first audit record."
        )
    else:
        run_started_at = pd.to_datetime(latest_run["started_at"])
        if run_started_at.tzinfo is not None:
            run_started_at = run_started_at.tz_convert("UTC")

        duration_value = latest_run["duration_seconds"]
        duration_text = (
            f"{float(duration_value):,.2f} sec"
            if pd.notna(duration_value)
            else "In progress"
        )
        completed_step_count = int(latest_run["completed_steps"])
        total_step_count = int(latest_run["total_steps"])

        run1, run2, run3, run4 = st.columns(4, gap="medium")
        run1.metric("Last Run Status", latest_run["status"])
        run2.metric("Runtime", duration_text)
        run3.metric(
            "Steps Completed",
            f"{completed_step_count} / {total_step_count}",
        )
        run4.metric(
            "Started At",
            run_started_at.strftime("%d %b %Y · %H:%M UTC"),
        )

        progress_value = (
            completed_step_count / total_step_count
            if total_step_count > 0
            else 0
        )
        st.progress(
            progress_value,
            text=(
                f"Pipeline progress: {completed_step_count} of "
                f"{total_step_count} steps completed"
            ),
        )

        if latest_run["status"] == "Failed":
            st.error(
                f"Failed step: {latest_run['failed_step']} · "
                f"{latest_run['error_message']}"
            )

    st.subheader("Raw-to-Staging Reconciliation")

    core_counts = counts[
        counts["layer"].isin(["Raw", "Staging"])
    ]
    reconciliation = (
        core_counts.pivot(
            index="dataset",
            columns="layer",
            values="row_count",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )
    reconciliation["Difference"] = (
        reconciliation["Staging"] - reconciliation["Raw"]
    )
    reconciliation["Status"] = reconciliation.apply(
        lambda row: (
            "Passed"
            if row["Difference"] == 0
            else (
                "Deduplicated"
                if row["dataset"] == "Order Reviews"
                and row["Difference"] < 0
                else "Review"
            )
        ),
        axis=1,
    )
    reconciliation = reconciliation.rename(
        columns={
            "dataset": "Dataset",
            "Raw": "Raw Rows",
            "Staging": "Staging Rows",
        }
    )

    reconciliation_cards = []
    for _, row in reconciliation.iterrows():
        status_class = str(row["Status"]).lower()
        difference = int(row["Difference"])
        status_detail = (
            "No row loss"
            if difference == 0
            else f"{abs(difference):,} rows removed"
        )
        reconciliation_cards.append(
            f'<div class="reconciliation-card">'
            f'<div class="reconciliation-name">{row["Dataset"]}</div>'
            f'<div class="reconciliation-flow">'
            f'<div class="reconciliation-step">'
            f'<span>RAW</span>'
            f'<strong>{int(row["Raw Rows"]):,}</strong>'
            f'</div>'
            f'<div class="reconciliation-arrow">&#8594;</div>'
            f'<div class="reconciliation-step">'
            f'<span>STAGING</span>'
            f'<strong>{int(row["Staging Rows"]):,}</strong>'
            f'</div>'
            f'</div>'
            f'<div class="reconciliation-status {status_class}">'
            f'{row["Status"]} &middot; {status_detail}'
            f'</div>'
            f'</div>'
        )

    st.markdown(
        '<div class="reconciliation-grid">'
        + "".join(reconciliation_cards)
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Order Reviews intentionally contains fewer Staging rows: "
        "the latest review per order is retained during deduplication."
    )

    with st.expander("View Reconciliation Table"):
        st.dataframe(
            reconciliation,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Raw Rows": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Staging Rows": st.column_config.NumberColumn(
                    format="%d"
                ),
                "Difference": st.column_config.NumberColumn(
                    format="%d"
                ),
            },
        )

    st.subheader("Quality Check Results")
    quality_results = checks.copy()
    quality_results["status"] = quality_results.apply(
        lambda row: (
            "Passed"
            if row["issue_count"] == 0
            else (
                "Failed"
                if row["severity"] == "Critical"
                else "Warning"
            )
        ),
        axis=1,
    )
    quality_results = quality_results.rename(
        columns={
            "source_table": "Source Table",
            "check_name": "Quality Check",
            "issue_count": "Issue Count",
            "severity": "Severity",
            "status": "Status",
        }
    )

    def style_quality_status(value):
        status_styles = {
            "Passed": (
                "background-color: #e2f1e9; "
                "color: #2f715b; font-weight: 700;"
            ),
            "Warning": (
                "background-color: #f8ecd4; "
                "color: #8a6424; font-weight: 700;"
            ),
            "Failed": (
                "background-color: #f4dddd; "
                "color: #9a4e4e; font-weight: 700;"
            ),
        }
        return status_styles.get(value, "")

    def style_quality_severity(value):
        severity_styles = {
            "Warning": "color: #9a712e; font-weight: 650;",
            "Critical": "color: #76699f; font-weight: 650;",
        }
        return severity_styles.get(value, "")

    styled_quality_results = (
        quality_results.style
        .map(style_quality_status, subset=["Status"])
        .map(style_quality_severity, subset=["Severity"])
    )

    left, right = st.columns([1.45, 1])
    with left:
        st.dataframe(
            styled_quality_results,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Issue Count": st.column_config.NumberColumn(
                    format="%d"
                ),
            },
        )
        st.caption(
            f"{passed_checks} of {len(checks)} checks passed with "
            "zero issues. Warnings are documented exceptions and "
            "do not stop the pipeline."
        )

    issue_summary = checks[checks["issue_count"].gt(0)].copy()
    issue_summary = issue_summary.sort_values("issue_count")
    with right:
        if issue_summary.empty:
            st.success("No quality issues to visualize.")
        else:
            issue_chart = px.bar(
                issue_summary,
                x="issue_count",
                y="check_name",
                orientation="h",
                color="severity",
                title="Documented Data Exceptions",
                labels={
                    "issue_count": "Affected Records",
                    "check_name": "Quality Check",
                    "severity": "Severity",
                },
                color_discrete_map={
                    "Warning": "#d5bd88",
                    "Critical": "#c98f8f",
                },
            )
            issue_chart.update_traces(
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Affected records: %{x:,}<extra></extra>"
                ),
            )
            style_chart(issue_chart)
            right.plotly_chart(
                issue_chart,
                use_container_width=True,
            )

    st.subheader("Mart Output Rows")
    mart_counts = counts[counts["layer"].eq("Mart")][
        ["dataset", "row_count"]
    ].rename(
        columns={
            "dataset": "Mart Dataset",
            "row_count": "Rows",
        }
    )
    st.dataframe(
        mart_counts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rows": st.column_config.NumberColumn(format="%d"),
        },
    )


def render_data_explorer():
    render_page_header(
        "&#9636;",
        "Data Explorer",
        "Preview, search, and export analytics-ready Mart data",
        "icon-explorer",
    )

    dataset_col, rows_col, search_col = st.columns(
        [1.5, 0.8, 2.2],
        vertical_alignment="bottom",
    )

    with dataset_col:
        selected_label = st.selectbox(
            "Dataset",
            options=list(DATA_EXPLORER_TABLES.keys()),
            key="explorer_dataset",
        )
        selected_table = DATA_EXPLORER_TABLES[selected_label]

    with rows_col:
        preview_rows = st.selectbox(
            "Preview Rows",
            options=[100, 500, 1000, 5000],
            index=1,
            key="explorer_rows",
        )

    with search_col:
        search_term = st.text_input(
            "Search All Columns",
            placeholder="Enter an order ID, state, category, or value",
            key="explorer_search",
        )

    columns, total_rows = load_dataset_metadata(selected_table)
    preview, matching_rows = load_dataset_preview(
        selected_table,
        preview_rows,
        search_term,
    )

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.metric("Selected Table", selected_table)
    col2.metric("Total Rows", f"{total_rows:,}")
    col3.metric("Columns", f"{len(columns):,}")
    col4.metric("Displayed Rows", f"{len(preview):,}")

    if search_term.strip():
        st.info(
            f"Found {matching_rows:,} matching rows. "
            f"Showing the first {len(preview):,}."
        )
    else:
        st.caption(
            f"Showing {len(preview):,} of {total_rows:,} rows. "
            "Use Search All Columns to narrow the result."
        )

    st.subheader("Data Preview")
    st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True,
        height=460,
    )

    csv_data = preview.to_csv(
        index=False,
    ).encode("utf-8-sig")
    safe_filename = selected_table.replace(".", "_")
    st.download_button(
        "Download Current Results as CSV",
        data=csv_data,
        file_name=f"{safe_filename}.csv",
        mime="text/csv",
        use_container_width=False,
    )
    st.caption(
        "The download contains the currently displayed rows after "
        "applying the search and preview limit."
    )

    st.subheader("Column Dictionary")
    column_dictionary = columns[
        ["column_name", "data_type"]
    ].copy()
    column_dictionary["description"] = column_dictionary[
        "column_name"
    ].map(COLUMN_DESCRIPTIONS)
    column_dictionary["description"] = column_dictionary[
        "description"
    ].fillna(
        column_dictionary["column_name"]
        .str.replace("_", " ", regex=False)
        .str.capitalize()
        + "."
    )
    column_dictionary = column_dictionary.rename(
        columns={
            "column_name": "Column",
            "data_type": "PostgreSQL Type",
            "description": "Business Meaning",
        }
    )
    st.dataframe(
        column_dictionary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Column": st.column_config.TextColumn(width="medium"),
            "PostgreSQL Type": st.column_config.TextColumn(
                width="small"
            ),
            "Business Meaning": st.column_config.TextColumn(
                width="large"
            ),
        },
    )


def render_overview():
    render_page_header(
        "&#9672;",
        "Brazilian E-Commerce Overview",
        (
            "Executive summary of delivered-order sales and "
            "customer satisfaction"
        ),
        "icon-overview",
    )

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        with st.container(key="overview_primary_kpi"):
            st.metric(
                "Total Sales",
                f"R$ {float(sales_kpis['total_sales']):,.2f}",
            )
    col2.metric(
        "Total Orders",
        f"{int(sales_kpis['total_orders']):,}",
    )
    col3.metric(
        "Total Customers",
        f"{int(sales_kpis['total_customers']):,}",
    )
    col4.metric(
        "Average Review Score",
        f"{float(review_kpis['average_review_score']):.2f} / 5",
    )

    st.subheader("Business Performance")
    left, right = st.columns([1.55, 1])

    overview_sales_chart = px.line(
        monthly_sales,
        x="order_month",
        y="total_sales",
        markers=True,
        title="Monthly Sales Trend",
        labels={
            "order_month": "Month",
            "total_sales": "Sales (R$)",
        },
    )
    overview_sales_chart.update_traces(
        line_color="#789f86",
        line_width=3,
        marker={
            "size": 7,
            "color": "#789f86",
        },
        fill="tozeroy",
        fillcolor="rgba(120, 159, 134, 0.10)",
        hovertemplate=(
            "%{x|%b %Y}<br>Sales: R$ %{y:,.2f}"
            "<extra></extra>"
        ),
    )
    style_chart(overview_sales_chart)
    left.plotly_chart(
        overview_sales_chart,
        use_container_width=True,
    )

    positive_reviews = int(
        review_distribution.loc[
            review_distribution["review_score"].ge(4),
            "review_count",
        ].sum()
    )
    neutral_reviews = int(
        review_distribution.loc[
            review_distribution["review_score"].eq(3),
            "review_count",
        ].sum()
    )
    negative_reviews = int(
        review_distribution.loc[
            review_distribution["review_score"].le(2),
            "review_count",
        ].sum()
    )
    overview_sentiment = pd.DataFrame(
        {
            "sentiment": ["Positive", "Neutral", "Negative"],
            "review_count": [
                positive_reviews,
                neutral_reviews,
                negative_reviews,
            ],
        }
    )
    overview_sentiment_chart = px.pie(
        overview_sentiment,
        names="sentiment",
        values="review_count",
        hole=0.62,
        title="Customer Review Sentiment",
        color="sentiment",
        color_discrete_map={
            "Positive": "#83aa8d",
            "Neutral": "#d5bd88",
            "Negative": "#c98f8f",
        },
    )
    overview_sentiment_chart.update_traces(
        textposition="inside",
        textinfo="percent",
        marker={
            "line": {
                "color": "#ffffff",
                "width": 2,
            }
        },
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Reviews: %{value:,}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    )
    style_chart(overview_sentiment_chart)
    overview_sentiment_chart.update_layout(
        legend_title_text="Sentiment",
    )
    right.plotly_chart(
        overview_sentiment_chart,
        use_container_width=True,
    )

    peak_month = monthly_sales.loc[
        monthly_sales["total_sales"].idxmax()
    ]
    top_state = state_sales.loc[
        state_sales["total_sales"].idxmax()
    ]
    top_category = category_sales.loc[
        category_sales["total_sales"].idxmax()
    ]

    delivery_lookup = delivery_reviews.set_index(
        delivery_reviews["delivery_status"].str.lower()
    )
    on_time_score = float(
        delivery_lookup.loc["on_time", "average_review_score"]
    )
    late_score = float(
        delivery_lookup.loc["late", "average_review_score"]
    )
    delivery_score_gap = on_time_score - late_score

    st.subheader("Key Insights")
    insight1, insight2, insight3, insight4 = st.columns(
        4,
        gap="medium",
    )

    with insight1.container(border=True):
        st.caption("PEAK SALES MONTH")
        st.markdown(
            f"### {peak_month['order_month']:%B %Y}"
        )
        st.write(
            f"R$ {float(peak_month['total_sales']):,.2f} in sales"
        )

    with insight2.container(border=True):
        st.caption("TOP CUSTOMER STATE")
        st.markdown(f"### {top_state['customer_state']}")
        st.write(
            f"R$ {float(top_state['total_sales']):,.2f} in sales"
        )

    category_name = str(
        top_category["product_category"]
    ).replace("_", " ").title()
    with insight3.container(border=True):
        st.caption("TOP PRODUCT CATEGORY")
        st.markdown(f"### {category_name}")
        st.write(
            f"R$ {float(top_category['total_sales']):,.2f} in sales"
        )

    with insight4.container(border=True):
        st.caption("DELIVERY SCORE IMPACT")
        st.markdown(f"### {delivery_score_gap:.2f} points")
        st.write("Higher score for on-time deliveries")

    total_sales_value = float(sales_kpis["total_sales"])
    top_state_share = (
        float(top_state["total_sales"]) / total_sales_value * 100
    )
    top_category_share = (
        float(top_category["total_sales"])
        / total_sales_value
        * 100
    )
    negative_review_rate = float(
        review_kpis["negative_review_rate"]
    )
    written_comment_count = int(
        review_kpis["written_comment_count"]
    )

    st.subheader("Business Recommendations")
    recommendations_html = (
        '<div class="recommendation-grid">'
        '<div class="recommendation-card delivery">'
        '<div class="recommendation-label">CUSTOMER EXPERIENCE</div>'
        '<div class="recommendation-title">Reduce Late Deliveries</div>'
        f'<div class="recommendation-evidence">Late deliveries average '
        f'{late_score:.2f} stars versus {on_time_score:.2f} for on-time '
        f'deliveries, a {delivery_score_gap:.2f}-point gap.</div>'
        '<div class="recommendation-action">Action: monitor carrier SLA '
        'performance and investigate routes with repeated delays.</div>'
        '</div>'
        '<div class="recommendation-card market">'
        '<div class="recommendation-label">MARKET STRATEGY</div>'
        f'<div class="recommendation-title">Build on {top_state["customer_state"]} '
        'Demand</div>'
        f'<div class="recommendation-evidence">The leading state contributes '
        f'{top_state_share:.1f}% of total sales; the top category contributes '
        f'{top_category_share:.1f}%.</div>'
        '<div class="recommendation-action">Action: protect inventory and '
        'delivery capacity in the core market while testing growth in '
        'underpenetrated states.</div>'
        '</div>'
        '<div class="recommendation-card feedback">'
        '<div class="recommendation-label">VOICE OF CUSTOMER</div>'
        '<div class="recommendation-title">Prioritize Negative Feedback</div>'
        f'<div class="recommendation-evidence">{negative_review_rate:.2f}% '
        f'of reviews are negative, with {written_comment_count:,} written '
        'comments available for deeper analysis.</div>'
        '<div class="recommendation-action">Action: classify comments by '
        'delivery, product category, and seller to identify recurring '
        'root causes.</div>'
        '</div>'
        '</div>'
    )
    st.markdown(
        recommendations_html,
        unsafe_allow_html=True,
    )

    st.subheader("Project Architecture")
    architecture_html = (
        '<div class="architecture-panel">'
        '<div class="architecture-flow">'
        '<div class="architecture-stage"><strong>Olist CSV Files</strong>'
        '<span>Public source datasets</span></div>'
        '<div class="architecture-arrow">&#8594;</div>'
        '<div class="architecture-stage"><strong>PostgreSQL Raw</strong>'
        '<span>Source-preserving ingestion</span></div>'
        '<div class="architecture-arrow">&#8594;</div>'
        '<div class="architecture-stage"><strong>Staging</strong>'
        '<span>Typing, cleaning, validation, deduplication</span></div>'
        '<div class="architecture-arrow">&#8594;</div>'
        '<div class="architecture-stage"><strong>Analytics Marts</strong>'
        '<span>Sales facts, reviews, reporting aggregates</span></div>'
        '<div class="architecture-arrow">&#8594;</div>'
        '<div class="architecture-stage"><strong>Streamlit BI</strong>'
        '<span>Interactive analysis and governed export</span></div>'
        '</div>'
        '<div class="technology-stack">'
        '<span class="technology-badge">18 Automated Steps</span>'
        '<span class="technology-badge">Python</span>'
        '<span class="technology-badge">Pandas</span>'
        '<span class="technology-badge">PostgreSQL</span>'
        '<span class="technology-badge">SQLAlchemy</span>'
        '<span class="technology-badge">Plotly</span>'
        '<span class="technology-badge">Streamlit</span>'
        '</div>'
        '</div>'
    )
    st.markdown(
        architecture_html,
        unsafe_allow_html=True,
    )

    st.subheader("Data Status")
    st.success(
        "PostgreSQL connected · Pipeline checks passed · "
        "Analytics marts available"
    )
    st.info(
        "Data coverage for 2016 is incomplete. Monthly trends "
        "should be interpreted primarily using data from 2017 onward."
    )

# -------------------------
# 页面导航
# -------------------------

if selected_page.endswith("Overview"):
    render_overview()
    st.stop()

if selected_page.endswith("Sales Analysis"):
    render_sales_analysis()
    st.stop()

if selected_page.endswith("Customer Reviews"):
    render_customer_reviews()
    st.stop()

if selected_page.endswith("Data Quality"):
    render_data_quality()
    st.stop()

if selected_page.endswith("Data Explorer"):
    render_data_explorer()
    st.stop()

if not selected_page.endswith("Overview"):
    page_name = selected_page.split(
        " ",
        maxsplit=1,
    )[-1]

    st.title(page_name)

    page_descriptions = {
        "Customer Reviews": (
            "Analyze review scores and the relationship "
            "between delivery performance and satisfaction."
        ),
        "Data Quality": (
            "Monitor missing values, duplicate records, "
            "and unmatched business keys."
        ),
        "Data Explorer": (
            "Explore and download detailed Mart data."
        ),
    }

    st.caption(
        page_descriptions.get(
            page_name,
            "Page under development.",
        )
    )

    st.info(
        "This page will be added in the next step."
    )

    st.stop()

# -------------------------
# 页面标题
# -------------------------

st.title("Brazilian E-Commerce Dashboard")

st.caption(
    "Olist delivered-order sales and customer review analysis"
)

st.info(
    "Data coverage for 2016 is incomplete. Monthly trends should be "
    "interpreted primarily using data from 2017 onward."
)


# -------------------------
# KPI
# -------------------------

st.subheader("Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Sales",
    f"R$ {float(sales_kpis['total_sales']):,.2f}",
)

col2.metric(
    "Total Orders",
    f"{int(sales_kpis['total_orders']):,}",
)

col3.metric(
    "Average Order Sales",
    f"R$ {float(sales_kpis['average_order_sales']):,.2f}",
)

col4.metric(
    "Average Review Score",
    f"{float(review_kpis['average_review_score']):.2f} / 5",
)

col5.metric(
    "Positive Review Rate",
    f"{float(review_kpis['positive_review_rate']):.2f}%",
)


# -------------------------
# 月度销售
# -------------------------

st.subheader("Monthly Sales Performance")

left, right = st.columns(2)

monthly_value_data = monthly_sales.melt(
    id_vars="order_month",
    value_vars=[
        "total_sales",
        "average_order_sales",
    ],
    var_name="metric",
    value_name="value",
)

monthly_value_chart = px.line(
    monthly_value_data,
    x="order_month",
    y="value",
    color="metric",
    markers=True,
    title="Monthly Sales and Average Order Sales",
    labels={
        "order_month": "Month",
        "value": "Value (R$)",
        "metric": "Metric",
    },
)

left.plotly_chart(
    monthly_value_chart,
    use_container_width=True,
)

monthly_orders_chart = px.line(
    monthly_sales,
    x="order_month",
    y="total_orders",
    markers=True,
    title="Monthly Order Count",
    labels={
        "order_month": "Month",
        "total_orders": "Orders",
    },
)

right.plotly_chart(
    monthly_orders_chart,
    use_container_width=True,
)


# -------------------------
# 州和类别
# -------------------------

st.subheader("Sales by State and Product Category")

left, right = st.columns(2)

state_chart = px.bar(
    state_sales.sort_values(
        "total_sales",
        ascending=True,
    ),
    x="total_sales",
    y="customer_state",
    orientation="h",
    title="Sales by Customer State",
    labels={
        "customer_state": "State",
        "total_sales": "Sales (R$)",
    },
)

left.plotly_chart(
    state_chart,
    use_container_width=True,
)

category_chart = px.bar(
    category_sales.sort_values(
        "total_sales",
        ascending=True,
    ),
    x="total_sales",
    y="product_category",
    orientation="h",
    title="Top 15 Product Categories",
    labels={
        "product_category": "Product Category",
        "total_sales": "Sales (R$)",
    },
)

right.plotly_chart(
    category_chart,
    use_container_width=True,
)


# -------------------------
# 评分分析
# -------------------------

st.subheader("Customer Review Analysis")

left, right = st.columns(2)

review_distribution_chart = px.bar(
    review_distribution,
    x="review_score",
    y="review_count",
    text="review_percentage",
    title="Review Score Distribution",
    labels={
        "review_score": "Review Score",
        "review_count": "Reviews",
    },
)

review_distribution_chart.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)

left.plotly_chart(
    review_distribution_chart,
    use_container_width=True,
)

delivery_review_chart = px.bar(
    delivery_reviews,
    x="delivery_status",
    y="average_review_score",
    color="delivery_status",
    text="average_review_score",
    title="Delivery Status vs Average Review Score",
    labels={
        "delivery_status": "Delivery Status",
        "average_review_score": "Average Score",
    },
)

delivery_review_chart.update_yaxes(
    range=[0, 5]
)

delivery_review_chart.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
)

right.plotly_chart(
    delivery_review_chart,
    use_container_width=True,
)


# -------------------------
# 月度评分趋势
# -------------------------

monthly_review_chart = px.line(
    monthly_reviews,
    x="order_month",
    y="average_review_score",
    markers=True,
    title="Monthly Average Review Score",
    labels={
        "order_month": "Month",
        "average_review_score": "Average Score",
    },
)

monthly_review_chart.update_yaxes(
    range=[0, 5]
)

st.plotly_chart(
    monthly_review_chart,
    use_container_width=True,
)


# -------------------------
# 数据表
# -------------------------

with st.expander("View Monthly Sales Data"):
    st.dataframe(
        monthly_sales,
        use_container_width=True,
        hide_index=True,
    )

with st.expander("View Delivery Review Data"):
    st.dataframe(
        delivery_reviews,
        use_container_width=True,
        hide_index=True,
    )
