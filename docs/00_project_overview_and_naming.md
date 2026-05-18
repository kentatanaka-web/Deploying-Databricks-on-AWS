# 00 Project Overview and Naming

## 目的

このファイルは、実装前に全体像と命名を固定するための「最初に読む資料」です。

- 全体の大きな流れを把握する
- 命名ブレを防ぐ
- 実装時の迷いを減らす
- 設計意図を一貫して説明しやすくする

---

## まず全体像（5フェーズ）

```text
Phase A: 環境判定（Free Edition制約確認）
   ↓
Phase B: AWS Workspace準備（Unity Catalog利用可能化）
   ↓
Phase C: AWS側準備（S3/IAMロール/ポリシー）
   ↓
Phase D: Databricks側準備（Catalog/Schema/Credential/External Location）
   ↓
Phase E: データ実装（Bronze -> Silver -> Gold） + SQL分析
```

現時点のゴール:

- Eフェーズ完了（Gold作成 + SQL分析完了）
- ダッシュボードは次フェーズ（本スコープ外）

---

## アーキテクチャ（今回の到達点）

```text
Source CSV
  ↓ upload
S3: raw/sales/
  ↓ read by Databricks
Bronze: bronze_sales
  ↓ cleanse / type conversion
Silver: silver_sales
  ↓ aggregation
Gold: gold_daily_sales, gold_salesperson_ranking
  ↓
SQL analysis (E-5)
```

---

## 命名を先に固定する（最重要）

命名を最初に固定すると、手順書・SQL・画面設定の不整合が大きく減ります。

### 1) AWS / S3

| 項目 | 名前 | 備考 |
| --- | --- | --- |
| AWS Region | ap-northeast-1 | Databricksと合わせる |
| S3 Bucket | tanaka-databricks-demo-20260518 | グローバル一意 |
| S3 Prefix | raw/sales/ | 元データ配置 |
| S3 Prefix | bronze/ | 処理層 |
| S3 Prefix | silver/ | 処理層 |
| S3 Prefix | gold/ | 処理層 |

### 2) IAM

| 項目 | 名前 | 用途 |
| --- | --- | --- |
| IAM Role | databricks-uc-s3-access-role | DatabricksがAssumeRoleするロール |
| IAM Policy | databricks-uc-s3-access-policy | S3アクセス許可 |

### 3) Databricks Unity Catalog

| 項目 | 名前 | 用途 |
| --- | --- | --- |
| Catalog | aws_demo_catalog | 最上位管理単位 |
| Schema | sales_schema | テーブル管理単位 |
| Storage Credential | sc_s3_databricks_demo | IAMロール登録 |
| External Location | ext_s3_sales_lake | S3パス登録 |

### 4) Delta Tables

| レイヤー | テーブル名 | 役割 |
| --- | --- | --- |
| Bronze | bronze_sales | 取り込み直後 |
| Silver | silver_sales | 整形・標準化 |
| Gold | gold_daily_sales | 日次集計 |
| Gold | gold_salesperson_ranking | 営業担当別集計 |

### 5) ファイル命名（このリポジトリ）

| 種別 | ファイル | 役割 |
| --- | --- | --- |
| Notebook | notebooks/01_ingest_bronze.py | Bronze作成 |
| Notebook | notebooks/02_transform_silver.py | Silver作成 |
| Notebook | notebooks/03_create_gold.py | Gold作成 |
| SQL | sql/03_analysis_queries.sql | 基本分析 |
| SQL | sql/04_advanced_analytics.sql | 発展分析 |
| Log | sql/05_query_execution_log.md | 実行記録 |

---

## 命名ルール（再利用用）

### ルール

- Role: databricks-uc-<resource>-role
- Policy: databricks-uc-<resource>-policy
- Storage Credential: sc_<cloud>_<purpose>
- External Location: ext_<cloud>_<domain>
- Table: <layer>_<subject>

### 例

- databricks-uc-s3-access-role
- databricks-uc-s3-access-policy
- sc_s3_databricks_demo
- ext_s3_sales_lake
- bronze_sales / silver_sales / gold_daily_sales

---

## 実装前チェック（3分）

以下を満たしたら実装開始:

- [ ] Regionは `ap-northeast-1` で統一
- [ ] S3バケット名が確定
- [ ] IAM Role/Policy名が確定
- [ ] Catalog/Schema名が確定
- [ ] Storage Credential/External Location名が確定
- [ ] Bronze/Silver/Goldのテーブル名が確定

---

## プロジェクト要約（30秒）

AWS S3をデータレイクとして利用し、DatabricksからIAMロール経由でS3にアクセスする構成を実装した。raw/bronze/silver/goldのレイヤーで役割を分離し、再処理性・障害切り分け・分析再現性を高めた。最終的にGoldテーブルをSQL分析し、業務判断に使える状態まで整理した。
