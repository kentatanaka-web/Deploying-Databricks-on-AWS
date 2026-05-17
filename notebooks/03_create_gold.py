# Databricks notebook source
# Gold: Aggregate for dashboard

from pyspark.sql import functions as F

silver_table = "aws_demo_catalog.sales_schema.silver_sales"
gold_table = "aws_demo_catalog.sales_schema.gold_sales_daily"

silver_df = spark.table(silver_table)

gold_df = (
    silver_df
    .groupBy("order_date")
    .agg(
        F.sum("amount").alias("total_sales"),
        F.countDistinct("order_id").alias("total_orders")
    )
    .orderBy("order_date")
)

(gold_df
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable(gold_table)
)

print(f"Created Gold table: {gold_table}")
