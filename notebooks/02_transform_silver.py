# Databricks notebook source
# ==============================================================================
# フェーズE-3: Silver Layer 変換
# 目的: Bronze テーブルをクレンジング・変換して Silver テーブルを作成
# ==============================================================================

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import (
    current_timestamp, col, round, when, 
    to_date, lit, countDistinct
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
BRONZE_TABLE_NAME = "bronze_sales"
SILVER_TABLE_NAME = "silver_sales"

# COMMAND ----------

# ==============================================================================
# 2. Bronze テーブルを読み込む
# ==============================================================================

print("=" * 80)
print("Step 1: Bronze テーブルを読み込む")
print("=" * 80)

# フルテーブルパス
bronze_table_path = f"{CATALOG_NAME}.{SCHEMA_NAME}.{BRONZE_TABLE_NAME}"
print(f"読み込み元テーブル: {bronze_table_path}")

# テーブルから読み込み
df_bronze = spark.table(bronze_table_path)

print(f"\nBronze テーブル情報:")
print(f"  行数: {df_bronze.count()}")
print(f"  列数: {len(df_bronze.columns)}")

print(f"\nBronze スキーマ:")
df_bronze.printSchema()

# COMMAND ----------

# ==============================================================================
# 3. データクレンジング（NULL値、重複チェック）
# ==============================================================================

print("\n" + "=" * 80)
print("Step 2: データクレンジング")
print("=" * 80)

# NULL 値をチェック
print(f"\nNULL値チェック:")
null_counts = df_bronze.select([
    col(column).isNull().cast('int').alias(f'{column}_null') 
    for column in df_bronze.columns
]).groupBy().sum().collect()[0]
print(f"  {dict(null_counts.asDict())}")

# 重複チェック（transaction_id が一意か確認）
total_rows = df_bronze.count()
distinct_txn = df_bronze.select(countDistinct("transaction_id")).collect()[0][0]
print(f"\nトランザクション一意性:")
print(f"  総行数: {total_rows}")
print(f"  一意の transaction_id: {distinct_txn}")
if total_rows == distinct_txn:
    print(f"  ✓ 重複なし（一意性を保証）")
else:
    print(f"  ⚠ 重複あり（{total_rows - distinct_txn}件）")

# COMMAND ----------

# ==============================================================================
# 4. Silver テーブル用に変換処理を適用
# ==============================================================================

print("\n" + "=" * 80)
print("Step 3: ビジネスロジック変換を適用")
print("=" * 80)

# Silver テーブルの作成
df_silver = df_bronze \
    .withColumn(
        "discount_amount",
        round(col("total_amount") * col("discount_rate"), 2)
    ) \
    .withColumn(
        "net_sales_amount",
        round(col("total_amount") - col("discount_amount"), 2)
    ) \
    .withColumn(
        "unit_price_decimal",
        col("unit_price").cast("decimal(10,2)")
    ) \
    .withColumn(
        "transaction_month",
        to_date(col("transaction_date"))
    ) \
    .withColumn(
        "sales_amount_rank",
        when(col("total_amount") >= 1000, "High")
            .when(col("total_amount") >= 100, "Medium")
            .otherwise("Low")
    ) \
    .withColumn(
        "transformed_timestamp",
        current_timestamp()
    ) \
    .select(
        # 元のキー
        "transaction_id",
        "transaction_date",
        "transaction_month",
        # 顧客関連
        "customer_id",
        "region",
        # 商品関連
        "product_name",
        "category",
        "quantity",
        # 金額関連（変換済み）
        "unit_price_decimal",
        "total_amount",
        "discount_rate",
        "discount_amount",
        "net_sales_amount",
        "sales_amount_rank",
        # 営業関連
        "store_id",
        "sales_person",
        # ステータス
        "payment_method",
        "status",
        # メタデータ
        "ingestion_timestamp",
        "processing_date",
        "transformed_timestamp"
    )

print(f"\nSilver テーブルのスキーマ:")
df_silver.printSchema()

print(f"\nSilver テーブルのサンプル（最初の5行）:")
df_silver.show(5, truncate=False)

# COMMAND ----------

# ==============================================================================
# 5. Unity Catalog に Silver テーブルを作成
# ==============================================================================

print("\n" + "=" * 80)
print("Step 4: Unity Catalog に Silver テーブルを作成")
print("=" * 80)

# フルテーブルパス
silver_table_path = f"{CATALOG_NAME}.{SCHEMA_NAME}.{SILVER_TABLE_NAME}"
print(f"テーブルパス: {silver_table_path}")

# テーブルを作成（既存の場合は上書き）
df_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .saveAsTable(silver_table_path)

print(f"\n✓ Silver テーブル作成完了")

# COMMAND ----------

# ==============================================================================
# 6. Silver テーブルの内容を確認
# ==============================================================================

print("\n" + "=" * 80)
print("Step 5: Silver テーブルの確認")
print("=" * 80)

# テーブルから読み込み
df_silver_check = spark.table(silver_table_path)

# 行数
row_count = df_silver_check.count()
print(f"\n行数: {row_count}")

# 列情報
print(f"\n列一覧（{len(df_silver_check.columns)}列）:")
for i, col_name in enumerate(df_silver_check.columns, 1):
    print(f"  {i:2d}. {col_name}")

# データサンプル
print(f"\nデータサンプル（最初の5行）:")
df_silver_check.show(5, truncate=False)

# COMMAND ----------

# ==============================================================================
# 7. Silver テーブルの統計情報と検証
# ==============================================================================

print("\n" + "=" * 80)
print("Step 6: Silver テーブルの統計情報")
print("=" * 80)

# 数値列の統計
print("\n【金額関連の統計】")
df_silver_check.select(
    "total_amount",
    "discount_amount",
    "net_sales_amount"
).describe().show()

# カテゴリ別の統計
print("\n【カテゴリ別の売上統計】")
df_silver_check.groupBy("category") \
    .agg(
        countDistinct("transaction_id").alias("transaction_count")
    ) \
    .show()

# 営業人員別の統計
print("\n【営業人員別の成績】")
df_silver_check.groupBy("sales_person") \
    .agg(
        countDistinct("transaction_id").alias("transaction_count")
    ) \
    .orderBy("transaction_count", ascending=False) \
    .show()

# 売上ランク別の分布
print("\n【売上ランク別の分布】")
df_silver_check.groupBy("sales_amount_rank").count().show()

# 地域別の統計
print("\n【地域別の売上】")
df_silver_check.groupBy("region").count().show()

# COMMAND ----------

# ==============================================================================
# 8. データ品質チェック
# ==============================================================================

print("\n" + "=" * 80)
print("Step 7: データ品質チェック")
print("=" * 80)

# NULL 値をチェック
print("\nNULL値チェック:")
null_check = df_silver_check.select([
    (col(c).isNull().cast("int")).alias(f'{c}_null') for c in df_silver_check.columns
])
null_counts_dict = {}
for col_name in df_silver_check.columns:
    null_count = df_silver_check.filter(col(col_name).isNull()).count()
    if null_count > 0:
        null_counts_dict[col_name] = null_count
        print(f"  {col_name}: {null_count}件のNULL")

if not null_counts_dict:
    print(f"  ✓ NULL値なし")

# 金額の妥当性チェック
print("\n金額の妥当性チェック:")
invalid_amounts = df_silver_check.filter(
    (col("net_sales_amount") < 0) |
    (col("discount_amount") < 0) |
    (col("net_sales_amount") > col("total_amount"))
).count()
print(f"  不正な金額レコード: {invalid_amounts}件")
if invalid_amounts == 0:
    print(f"  ✓ 全金額の妥当性を確認")

# 日付の妥当性チェック
print("\n日付の妥当性チェック:")
invalid_dates = df_silver_check.filter(
    col("transaction_date").isNull()
).count()
print(f"  不正な日付レコード: {invalid_dates}件")
if invalid_dates == 0:
    print(f"  ✓ 全日付の妥当性を確認")

# COMMAND ----------

# ==============================================================================
# 9. 完了ログ
# ==============================================================================

print("\n" + "=" * 80)
print("✓ Silver Layer 変換完了")
print("=" * 80)
print(f"\n【完了情報】")
print(f"  元テーブル: {bronze_table_path}")
print(f"  新テーブル: {silver_table_path}")
print(f"  処理行数: {row_count}")
print(f"  追加列: discount_amount, net_sales_amount, unit_price_decimal, transaction_month, sales_amount_rank, transformed_timestamp")
print(f"\n【次のステップ】")
print(f"  E-4: Gold Layer 集計ノートブック（03_create_gold）を実行")
