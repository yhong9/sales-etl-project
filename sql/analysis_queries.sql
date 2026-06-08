--查看数据
SELECT *
FROM fact_sales
LIMIT 10;

--每月销售额和利润趋势
SELECT
    order_month,
    ROUND(SUM(revenue),2) AS total_revenue, --每个月的revenue加起来，保留两位小数
    ROUND(SUM(profit),2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders --每个月多少订单，distinct 避免重复
FROM fact_sales
GROUP BY order_month
ORDER BY order_month;

--各地区销售额
SELECT
    region,
    ROUND(SUM(revenue),2) AS total_revenue, 
    ROUND(SUM(profit),2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders 
FROM fact_sales
GROUP BY region
ORDER BY total_revenue DESC;

--销售额最高的products
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

--按种类profit margin
SELECT
    category,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(PROFIT)/SUM(revenue),4) AS profit_margin
FROM fact_sales
GROUP BY category
ORDER BY profit_margin DESC
LIMIT 10;