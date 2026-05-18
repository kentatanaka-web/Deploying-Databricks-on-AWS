-- 03_analysis_queries.sql
-- Gold作成前後の基本分析クエリ例

USE CATALOG aws_demo_catalog;
USE SCHEMA sales_schema;

-- 日次売上（Silverベース）
SELECT
  transaction_date,
  ROUND(SUM(net_sales_amount), 2) AS total_net_sales,
  COUNT(DISTINCT transaction_id) AS total_transactions
FROM silver_sales
GROUP BY transaction_date
ORDER BY transaction_date;

-- 商品別売上（Silverベース）
SELECT
  product_name,
  ROUND(SUM(net_sales_amount), 2) AS total_net_sales,
  SUM(quantity) AS total_quantity
FROM silver_sales
GROUP BY product_name
ORDER BY total_net_sales DESC;
