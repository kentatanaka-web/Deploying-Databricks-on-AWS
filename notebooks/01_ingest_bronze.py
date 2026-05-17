# Databricks notebook source
# Bronze: S3 raw CSV -> Delta table

from pyspark.sql import functions as F

source_path = "s3://<your-bucket-name>/raw/sales/sales_sample.csv"
bronze_table = "aws_demo_catalog.sales_schema.bronze_sales"

raw_df = (
    spark.read
    .option("header", True)
    .csv(source_path)
)

(raw_df
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable(bronze_table)
)

print(f"Loaded Bronze table: {bronze_table}")
