# Databricks on AWS Data Platform Basic

## 概要

AWS S3とDatabricksを利用して、基本的なデータ基盤を構築する学習用プロジェクトです。

## 最初に読む資料

実装に入る前に、全体フローと命名を固定するために以下を先に確認してください。

- docs/00_project_overview_and_naming.md

## 設計思想（Why）

このプロジェクトの狙いは「作れること」ではなく「なぜこの設計にしたかを説明できること」です。

### 1. なぜ S3 を使うのか

- S3は安価・高耐久・高拡張で、データレイクの保存先として適している
- CSV/JSON/Parquet/ログなど、異なる形式を同じ基盤で管理できる
- 元データを消さずに保持でき、再処理や監査に強い

### 2. なぜ raw / bronze / silver / gold に分けるのか

- 役割分離により、品質管理・障害切り分け・再処理が容易になる
- raw: 元ファイルの原本保管
- bronze: 取り込み直後（最小変換）
- silver: 型変換・クレンジング・業務ルール適用
- gold: 分析・ダッシュボード向け集計済みデータ

### 3. なぜ IAM ロールが必要なのか

- Databricksに長期アクセスキーを持たせず、安全にS3へアクセスするため
- AssumeRoleで一時認証情報を使うことで、漏えいリスクを下げられる
- 権限をバケット/パス単位で最小化しやすい

### 4. なぜ Storage Credential / External Location を作るのか

- Storage Credential: Databricks側で「どのIAMロールでアクセスするか」を定義
- External Location: Databricks側で「どのS3パスを使うか」を定義
- Unity Catalogで認証情報とアクセス先を分離管理し、ガバナンスを明確化

### 5. なぜ Gold から可視化するのか

- ダッシュボードは業務利用前提のため、集計済みで安定した粒度が必要
- raw/bronzeは元データに近く、欠損・型揺れ・明細粒度の影響を受けやすい
- goldを参照すると、クエリが単純化され、再現性と保守性が高い

注記: 本リポジトリの現時点ゴールは「可視化直前（Gold作成とSQL分析完了）」まで。ダッシュボード化は次フェーズとして分離している。

## 用語対応表（必須）

| 項目 | 役割 |
| --- | --- |
| S3 | 元データや処理済みデータの保存先 |
| IAMロール | DatabricksがAWSへアクセスするための権限主体 |
| IAMポリシー | ロールに許可するS3操作（List/Get/Put等） |
| 信頼ポリシー | DatabricksがそのロールをAssumeできる条件 |
| Storage Credential | Databricks側にIAMロールを登録する設定 |
| External Location | Databricks側にS3パスを登録する設定 |
| Bronze | 取り込み直後データ |
| Silver | 整形・標準化データ |
| Gold | 分析・可視化向け集計データ |

## 構成

- AWS S3: データレイク
- Databricks: データ加工・Delta Table管理
- Unity Catalog: カタログ、スキーマ、外部ロケーション管理
- Databricks Job: 処理の自動化

## 学習目的

- AWS上でDatabricksを利用する基本構成を理解する
- S3からDatabricksへデータを取り込む
- Bronze / Silver / Gold構成を体験する
- Delta Tableを作成する
- SQL分析クエリを実行し、結果を解釈できるようにする
- Job化に向けた前提（依存関係と検証観点）を理解する
- 再現可能なデータ基盤の実装記録を作る

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
SQL分析
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
│   ├── 04_advanced_analytics.sql
│   ├── 05_query_execution_log.md
│   └── 03_analysis_queries.sql
├── notebooks/
│   ├── 01_ingest_bronze.py
│   ├── 02_transform_silver.py
│   └── 03_create_gold.py
├── sample_data/
└── images/
```

## 実施フェーズ

- Phase 1: GitHub用の土台作成
- Phase 2: AWS側セットアップ（S3/IAM）
- Phase 3: Databricks側セットアップ（Catalog/Schema/External Location）
- Phase 4: Bronze / Silver / Gold実装
- Phase 5: SQL分析とGitHub公開（ダッシュボードは次フェーズ）

## 次にやること

1. docs/01_aws_setup.md を見ながらS3とIAMロールを作成する
2. docs/02_databricks_setup.md を見ながらStorage CredentialとExternal Locationを作成する
3. SQLとNotebookを追加して、Bronze -> Silver -> Goldを実装する
4. sql/04_advanced_analytics.sql を実行して分析結果を記録する

## Free Edition利用時の確認

- Free Editionで進める場合は、先に docs/05_free_edition_support_check.md を確認してから実装を開始する

## 推奨実行ルート

- 手順全体は docs/06_execution_runbook.md に従う
