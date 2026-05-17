# 05 Free Edition Support Check

## 目的

Databricks Free Editionで、Unity CatalogのStorage Credential / External Locationを使ったAWS S3連携が実行可能かを公式情報で判定します。

## 公式確認結果（2026-05-18時点）

### 1. Free Editionの制約

Databricks公式の Free Edition limitations には、以下が明記されています。

- Unsupported features に `Custom workspace storage locations` が含まれる
- Administrative limitations に `No access to the account console or account-level APIs` が含まれる

上記2点から、Free Editionではクラウド側の連携前提を満たせないケースが発生します。

### 2. S3 External Locationの要件

Databricks公式のS3接続手順には、Storage CredentialとExternal Locationが必須と記載されています。

- Storage Credential（AWS IAMロール）
- External Location（S3パス + Storage Credential）

また手動手順では、以下の順で実施します。

1. AWSでIAMロールを作成（一時的なTrust Policy + placeholder External ID）
2. DatabricksでStorage Credentialを作成（IAMロールARNを入力）
3. Databricksで発行されたExternal IDをAWSのTrust Policyへ反映
4. External Locationを作成

## 判定

- Free Editionのままでは、AWS S3連携を完了できない可能性が高い
- 転職用ポートフォリオとして再現性を重視する場合は、Databricks on AWSの通常ワークスペースへ移行する

## 移行後に再実施する手順（推奨）

1. Databricks on AWSで通常ワークスペースを用意する
2. Unity Catalog metastoreがワークスペースに関連付け済みか確認する
3. docs/01_aws_setup.md に沿ってS3バケットとIAMポリシーを作成する
4. docs/02_databricks_setup.md に沿ってStorage CredentialとExternal Locationを作成する
5. notebooks配下の処理を実行し、Bronze / Silver / Goldを作成する
6. JobとDashboardを作成し、READMEに実行結果を記録する

## 詰まったときの確認ポイント

- Databricks画面に IAMロールARN 入力欄があるか
- インスタンスプロファイル選択で `No results found` になっていないか
- Storage Credential作成後にExternal IDが取得できるか
- AWS側のTrust Policyが最新のExternal IDに更新済みか

## 参考リンク

- Databricks Free Edition limitations:
  https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Connect to an AWS S3 external location:
  https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/
- Manual setup (Catalog Explorer / SQL):
  https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/s3/s3-external-location-manual
