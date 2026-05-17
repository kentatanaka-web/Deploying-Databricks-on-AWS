# Databricks notebook source
# Silver: Clean and cast from Bronze

from pyspark.sql import functions as F

bronze_table = "aws_demo_catalog.sales_schema.bronze_sales"
silver_table = "aws_demo_catalog.sales_schema.silver_sales"

bronze_df = spark.table(bronze_table)

silver_df = (
    bronze_df
    .withColumn("order_date", F.to_date(F.col("order_date"), "yyyy-MM-dd"))
    .withColumn("quantity", F.col("quantity").cast("int"))
    .withColumn("unit_price", F.col("unit_price").cast("decimal(12,2)"))
    .withColumn("amount", F.col("amount").cast("decimal(12,2)"))
    .dropna(subset=["order_id", "order_date", "customer_id", "product_name"])
)

(silver_df
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable(silver_table)
)

print(f"Created Silver table: {silver_table}")
