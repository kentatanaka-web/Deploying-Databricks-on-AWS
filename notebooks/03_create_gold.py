# Databricks notebook source
# ==============================================================================
# フェーズE-4: Gold Layer 集計・分析
# 目的: Silver テーブルから分析・ダッシュボード用のテーブルを作成
# ==============================================================================

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import (
    col, sum, avg, count, countDistinct, max, min, round,
    current_timestamp, to_date, date_format
)
import logging

# ロギング設定
logger = logging.getLogger(__name__)

# COMMAND ----------

# ==============================================================================
# 1. 設定値
# ==============================================================================

# Catalog/Schema 設定
CATALOG_NAME = "aws_demo_catalog"
SCHEMA_NAME = "sales_schema"
SILVER_TABLE_NAME = "silver_sales"

# Gold テーブル名
GOLD_DAILY_TABLE = "gold_daily_sales"
GOLD_CATEGORY_TABLE = "gold_category_summary"
GOLD_SALESPERSON_TABLE = "gold_salesperson_ranking"

# COMMAND ----------

# ==============================================================================
# 2. Silver テーブルを読み込む
# ==============================================================================

print("=" * 80)
print("Step 1: Silver テーブルを読み込む")
print("=" * 80)

# フルテーブルパス
silver_table_path = f"{CATALOG_NAME}.{SCHEMA_NAME}.{SILVER_TABLE_NAME}"
print(f"読み込み元テーブル: {silver_table_path}")

# テーブルから読み込み
df_silver = spark.table(silver_table_path)

print(f"\nSilver テーブル情報:")
print(f"  行数: {df_silver.count()}")
print(f"  列数: {len(df_silver.columns)}")

# COMMAND ----------

# ==============================================================================
# 3. Gold-1: 日次売上集計テーブルを作成
# ==============================================================================

print("\n" + "=" * 80)
print("Step 2: 日次売上集計テーブルを作成（Gold-1）")
print("=" * 80)

# 日付ごとの集計
df_gold_daily = df_silver \
    .groupBy("transaction_date") \
    .agg(
        count("transaction_id").alias("transaction_count"),
        countDistinct("customer_id").alias("unique_customers"),
        round(sum("total_amount"), 2).alias("total_sales"),
        round(sum("net_sales_amount"), 2).alias("net_sales"),
        round(sum("discount_amount"), 2).alias("total_discount"),
        round(avg("net_sales_amount"), 2).alias("avg_transaction_amount"),
        round(avg("discount_rate"), 2).alias("avg_discount_rate"),
        max("total_amount").alias("max_transaction_amount"),
        min("total_amount").alias("min_transaction_amount")
    ) \
    .orderBy("transaction_date")

# フルテーブルパス
gold_daily_table_path = f"{CATALOG_NAME}.{SCHEMA_NAME}.{GOLD_DAILY_TABLE}"
print(f"テーブルパス: {gold_daily_table_path}")

# テーブルを作成
df_gold_daily.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(gold_daily_table_path)

print(f"\n✓ Gold-1 テーブル作成完了")
print(f"\n日次売上サンプル:")
df_gold_daily.show()

# COMMAND ----------

# ==============================================================================
# 4. Gold-2: カテゴリ別売上サマリーを作成
# ==============================================================================

print("\n" + "=" * 80)
print("Step 3: カテゴリ別売上サマリーを作成（Gold-2）")
print("=" * 80)

# カテゴリごとの集計
df_gold_category = df_silver \
    .groupBy("category") \
    .agg(
        count("transaction_id").alias("transaction_count"),
        countDistinct("product_name").alias("unique_products"),
        countDistinct("customer_id").alias("unique_customers"),
        round(sum("total_amount"), 2).alias("total_sales"),
        round(sum("net_sales_amount"), 2).alias("net_sales"),
        round(sum("discount_amount"), 2).alias("total_discount"),
        round(avg("net_sales_amount"), 2).alias("avg_transaction_amount"),
        round(avg("quantity"), 2).alias("avg_quantity"),
        round(avg("discount_rate"), 2).alias("avg_discount_rate")
    ) \
    .orderBy(col("total_sales").desc())

# フルテーブルパス
gold_category_table_path = f"{CATALOG_NAME}.{SCHEMA_NAME}.{GOLD_CATEGORY_TABLE}"
print(f"テーブルパス: {gold_category_table_path}")

# テーブルを作成
df_gold_category.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(gold_category_table_path)

print(f"\n✓ Gold-2 テーブル作成完了")
print(f"\nカテゴリ別売上サマリー:")
df_gold_category.show()

# COMMAND ----------

# ==============================================================================
# 5. Gold-3: 営業人員ランキングを作成
# ==============================================================================

print("\n" + "=" * 80)
print("Step 4: 営業人員ランキングを作成（Gold-3）")
print("=" * 80)

# 営業人員ごとの集計
df_gold_salesperson = df_silver \
    .groupBy("sales_person", "region") \
    .agg(
        count("transaction_id").alias("transaction_count"),
        countDistinct("customer_id").alias("unique_customers"),
        round(sum("total_amount"), 2).alias("total_sales"),
        round(sum("net_sales_amount"), 2).alias("net_sales"),
        round(sum("discount_amount"), 2).alias("total_discount"),
        round(avg("net_sales_amount"), 2).alias("avg_transaction_amount"),
        round(avg("discount_rate"), 2).alias("avg_discount_rate")
    ) \
    .orderBy(col("net_sales").desc())

# フルテーブルパス
gold_salesperson_table_path = f"{CATALOG_NAME}.{SCHEMA_NAME}.{GOLD_SALESPERSON_TABLE}"
print(f"テーブルパス: {gold_salesperson_table_path}")

# テーブルを作成
df_gold_salesperson.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(gold_salesperson_table_path)

print(f"\n✓ Gold-3 テーブル作成完了")
print(f"\n営業人員ランキング:")
df_gold_salesperson.show()

# COMMAND ----------

# ==============================================================================
# 6. Gold-1 テーブルの詳細確認
# ==============================================================================

print("\n" + "=" * 80)
print("Step 5: Gold-1 日次売上テーブルの詳細確認")
print("=" * 80)

# テーブルから読み込み
df_gold_daily_check = spark.table(gold_daily_table_path)

print(f"\n行数: {df_gold_daily_check.count()}")
print(f"スキーマ:")
df_gold_daily_check.printSchema()

print(f"\n統計情報:")
df_gold_daily_check.describe().show()

# COMMAND ----------

# ==============================================================================
# 7. Gold-2 テーブルの詳細確認
# ==============================================================================

print("\n" + "=" * 80)
print("Step 6: Gold-2 カテゴリ別テーブルの詳細確認")
print("=" * 80)

# テーブルから読み込み
df_gold_category_check = spark.table(gold_category_table_path)

print(f"\n行数: {df_gold_category_check.count()}")
print(f"列一覧:")
for i, col_name in enumerate(df_gold_category_check.columns, 1):
    print(f"  {i:2d}. {col_name}")

print(f"\nデータ:")
df_gold_category_check.show()

# COMMAND ----------

# ==============================================================================
# 8. Gold-3 テーブルの詳細確認
# ==============================================================================

print("\n" + "=" * 80)
print("Step 7: Gold-3 営業人員テーブルの詳細確認")
print("=" * 80)

# テーブルから読み込み
df_gold_salesperson_check = spark.table(gold_salesperson_table_path)

print(f"\n行数: {df_gold_salesperson_check.count()}")
print(f"列一覧:")
for i, col_name in enumerate(df_gold_salesperson_check.columns, 1):
    print(f"  {i:2d}. {col_name}")

print(f"\nデータ（売上ランキング順）:")
df_gold_salesperson_check.show()

# COMMAND ----------

# ==============================================================================
# 9. 完了ログ
# ==============================================================================

print("\n" + "=" * 80)
print("✓ Gold Layer 集計・分析完了")
print("=" * 80)
print(f"\n【完了情報】")
print(f"  Gold-1（日次売上）: {gold_daily_table_path}")
print(f"  Gold-2（カテゴリ別）: {gold_category_table_path}")
print(f"  Gold-3（営業人員）: {gold_salesperson_table_path}")
print(f"\n【次のステップ】")
print(f"  E-5: SQL分析クエリとダッシュボード化")
