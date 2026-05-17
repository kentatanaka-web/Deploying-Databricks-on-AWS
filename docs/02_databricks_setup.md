# 02 Databricks Setup

## 目的

Unity Catalogを使い、S3をExternal Locationとして安全に管理します。

## 手順

1. Databricks Workspaceにログイン
2. Catalogを作成
3. Schemaを作成
4. Storage Credentialを作成
5. External Locationを作成
6. 権限（GRANT）を設定

## SQLサンプル

```sql
CREATE CATALOG IF NOT EXISTS aws_demo_catalog;

CREATE SCHEMA IF NOT EXISTS aws_demo_catalog.sales_schema;
```

## Storage Credential / External Location の考え方

- Storage Credential: クラウドストレージへ接続する認証情報
- External Location: ストレージパスとStorage Credentialを紐付ける管理オブジェクト

## 設定時に必要な情報

- IAMロールARN
- S3バケットパス（例: s3://tanaka-databricks-demo-2026/）
- 利用するCatalog/Schema名

## チェックポイント

- CatalogとSchemaが作成済み
- Storage Credentialが作成済み
- External Locationが作成済み
- 対象ユーザーやグループへ利用権限を付与済み
