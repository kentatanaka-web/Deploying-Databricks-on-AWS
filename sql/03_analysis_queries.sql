-- 03_analysis_queries.sql
-- Dashboard用の分析クエリ例

USE CATALOG aws_demo_catalog;
USE SCHEMA sales_schema;

-- 日次売上
SELECT
  order_date,
  SUM(amount) AS total_sales,
  COUNT(DISTINCT order_id) AS total_orders
FROM silver_sales
GROUP BY order_date
ORDER BY order_date;

-- 商品別売上
SELECT
  product_name,
  SUM(amount) AS total_sales,
  SUM(quantity) AS total_quantity
FROM silver_sales
GROUP BY product_name
ORDER BY total_sales DESC;
