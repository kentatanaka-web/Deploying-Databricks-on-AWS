# Databricks notebook source
# ==============================================================================
# フェーズE-2: Bronze Layer インジェスト
# 目的: S3（raw/sales）から CSV を読んで Unity Catalog の bronze_sales テーブルを作成
# ==============================================================================

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import current_timestamp, col
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
BRONZE_TABLE_NAME = "bronze_sales"

# S3 外部ロケーション設定
EXTERNAL_LOCATION_NAME = "ext_s3_sales_lake"
RAW_DATA_PATH = "s3://tanaka-databricks-demo-20260518/raw/sales/"

# COMMAND ----------

# ==============================================================================
# 2. CSV ファイルを読み込む
# ==============================================================================

print("=" * 80)
print("Step 1: CSV ファイルを S3 から読み込む")
print("=" * 80)

# S3 パス
csv_file_path = f"{RAW_DATA_PATH}sales_sample.csv"
print(f"読み込みパス: {csv_file_path}")

# CSV を読み込む
df_raw = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(csv_file_path)

# データフレーム情報を表示
print(f"\nデータ件数: {df_raw.count()}")
print(f"\nスキーマ:")
df_raw.printSchema()

print(f"\n最初の10行:")
df_raw.show(10, truncate=False)

# COMMAND ----------

# ==============================================================================
# 3. Bronze テーブル用に列を追加
# ==============================================================================

print("\n" + "=" * 80)
print("Step 2: Bronze テーブル用のメタデータ列を追加")
print("=" * 80)

# タイムスタンプと処理情報を追加
df_bronze = df_raw.withColumn("ingestion_timestamp", current_timestamp()) \
                   .withColumn("processing_date", col("transaction_date"))

print(f"\nBronze テーブルのスキーマ:")
df_bronze.printSchema()

print(f"\nBronze テーブルの最初の5行:")
df_bronze.show(5, truncate=False)

# COMMAND ----------

# ==============================================================================
# 4. Unity Catalog 上に Bronze テーブルを作成（上書き）
# ==============================================================================

print("\n" + "=" * 80)
print("Step 3: Unity Catalog に Bronze テーブルを作成")
print("=" * 80)

# フルテーブルパス
full_table_name = f"{CATALOG_NAME}.{SCHEMA_NAME}.{BRONZE_TABLE_NAME}"
print(f"テーブルパス: {full_table_name}")

# テーブルを作成（既存の場合は上書き）
df_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(full_table_name)

print(f"\n✓ Bronze テーブル作成完了")

# COMMAND ----------

# ==============================================================================
# 5. Bronze テーブルの内容を確認
# ==============================================================================

print("\n" + "=" * 80)
print("Step 4: Bronze テーブルの確認")
print("=" * 80)

# テーブルから読み込み
df_bronze_check = spark.table(full_table_name)

# 行数
row_count = df_bronze_check.count()
print(f"\n行数: {row_count}")

# スキーマ
print(f"\nスキーマ:")
df_bronze_check.printSchema()

# データ確認
print(f"\nデータサンプル（最初の10行）:")
df_bronze_check.show(10, truncate=False)

# 列情報
print(f"\n列一覧:")
print(df_bronze_check.columns)

# COMMAND ----------

# ==============================================================================
# 6. 統計情報を表示
# ==============================================================================

print("\n" + "=" * 80)
print("Step 5: 統計情報")
print("=" * 80)

# 数値列の統計
print("\n数値列の統計:")
df_bronze_check.describe("quantity", "unit_price", "total_amount", "discount_rate").show()

# カテゴリ別の集計
print("\nカテゴリ別の行数:")
df_bronze_check.groupBy("category").count().show()

# 地域別の行数
print("地域別の行数:")
df_bronze_check.groupBy("region").count().show()

# COMMAND ----------

# ==============================================================================
# 7. 完了ログ
# ==============================================================================

print("\n" + "=" * 80)
print("✓ Bronze Layer インジェスト完了")
print("=" * 80)
print(f"\n【完了情報】")
print(f"  テーブル名: {full_table_name}")
print(f"  ソースファイル: {csv_file_path}")
print(f"  行数: {row_count}")
print(f"\n【次のステップ】")
print(f"  E-3: Silver Layer 変換ノートブック（02_transform_silver）を実行")
