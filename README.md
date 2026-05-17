# Databricks on AWS Data Platform Basic

## 概要

AWS S3とDatabricksを利用して、基本的なデータ基盤を構築する学習用プロジェクトです。

## 構成

- AWS S3: データレイク
- Databricks: データ加工・Delta Table管理
- Unity Catalog: カタログ、スキーマ、外部ロケーション管理
- Databricks Job: 処理の自動化
- Dashboard: 集計結果の可視化

## 学習目的

- AWS上でDatabricksを利用する基本構成を理解する
- S3からDatabricksへデータを取り込む
- Bronze / Silver / Gold構成を体験する
- Delta Tableを作成する
- JobとDashboardを作成する
- 転職活動で説明できるポートフォリオを作る

## 全体フロー

```text
AWS S3
  ↓
Databricks
  ↓
Bronze / Silver / Gold
  ↓
Delta Table
  ↓
Job化
  ↓
Dashboard
  ↓
GitHubで公開
```

## リポジトリ構成

```text
databricks-aws-data-platform-basic/
├── README.md
├── docs/
│   ├── 01_aws_setup.md
│   ├── 02_databricks_setup.md
│   ├── 03_bronze_silver_gold.md
│   ├── 04_job_dashboard.md
│   ├── 05_free_edition_support_check.md
│   ├── 06_execution_runbook.md
│   └── architecture.md
├── sql/
├── notebooks/
├── sample_data/
└── images/
```

## 実施フェーズ

- Phase 1: GitHub用の土台作成
- Phase 2: AWS側セットアップ（S3/IAM）
- Phase 3: Databricks側セットアップ（Catalog/Schema/External Location）
- Phase 4: Bronze / Silver / Gold実装
- Phase 5: Job化とDashboard作成

## 次にやること

1. docs/01_aws_setup.md を見ながらS3とIAMロールを作成する
2. docs/02_databricks_setup.md を見ながらStorage CredentialとExternal Locationを作成する
3. SQLとNotebookを追加して、Bronze -> Silver -> Goldを実装する

## Free Edition利用時の確認

- Free Editionで進める場合は、先に docs/05_free_edition_support_check.md を確認してから実装を開始する

## 推奨実行ルート

- 手順全体は docs/06_execution_runbook.md に従う
