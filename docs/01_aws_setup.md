# 01 AWS Setup

## 目的

DatabricksからアクセスするS3データレイクとIAMロールを準備します。

## 手順

1. S3バケットを作成する
2. S3フォルダ構成を作成する
3. Databricks用IAMロールを作成する
4. 必要なS3アクセス権をIAMポリシーで付与する

## S3バケット命名例

- tanaka-databricks-demo-2026

## S3フォルダ構成

```text
s3://<your-bucket-name>/
├── raw/
│   └── sales/
├── bronze/
├── silver/
└── gold/
```

## IAMロール作成メモ

- 用途: Databricks Unity Catalog から S3外部ロケーションを参照するため
- 付与対象: 上記バケット配下の必要パス
- 最小権限: ListBucket, GetObject, PutObject, DeleteObject（必要な範囲のみ）

## チェックポイント

- バケットとフォルダが作成済み
- テストCSVを raw/sales/ に配置済み
- IAMロールARNを控えた

## 記録しておく情報

- AWSアカウントID
- S3バケット名
- IAMロールARN
- リージョン（例: ap-northeast-1）
