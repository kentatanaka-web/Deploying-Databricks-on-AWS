-- 02_create_tables.sql
-- Bronze / Silver / Gold テーブル作成

USE CATALOG aws_demo_catalog;
USE SCHEMA sales_schema;

CREATE TABLE IF NOT EXISTS bronze_sales (
  order_id STRING,
  order_date STRING,
  customer_id STRING,
  product_name STRING,
  quantity STRING,
  unit_price STRING,
  amount STRING
)
USING DELTA;

CREATE TABLE IF NOT EXISTS silver_sales (
  order_id STRING,
  order_date DATE,
  customer_id STRING,
  product_name STRING,
  quantity INT,
  unit_price DECIMAL(12,2),
  amount DECIMAL(12,2)
)
USING DELTA;

CREATE TABLE IF NOT EXISTS gold_sales_daily (
  order_date DATE,
  total_sales DECIMAL(18,2),
  total_orders BIGINT
)
USING DELTA;
