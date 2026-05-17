# 02 Databricks Setup

## 目的

Unity Catalogを使い、S3をExternal Locationとして安全に管理します。

## 事前確認（重要）

- Free Editionを利用している場合は、先に `docs/05_free_edition_support_check.md` を確認する
- Free Editionではクラウド連携機能に制限があるため、手順どおりに進まない場合がある

## 手順

1. 資格情報（Storage Credential）を作成開始する
2. Databricks画面でAWS IAMロールのTrust Policyを確認する
3. AWS側でIAMロールを作成する
4. IAMロールARNをDatabricks画面へ戻して入力する
5. 外部ロケーション（External Location）を作成する
6. 必要に応じてCatalog/Schema作成と権限（GRANT）を設定する

## 必須フロー（実画面に合わせた順番）

このプロジェクトでは、以下の順番を固定します。

1. Databricksで資格情報作成を開始
2. Databricksが表示するTrust Policyを確認
3. AWS IAMでロール作成（Trust Policy貼り付け）
4. ロールARNをDatabricksへ入力して資格情報を保存
5. DatabricksでExternal Locationを作成

## 今回固定する入力値

- 資格情報名: sc_s3_databricks_demo
- 意味: Storage Credential for S3 Databricks Demo
- IAMロールARN: AWS IAMでロール作成後に入力
	- 例: arn:aws:iam::123456789012:role/databricks-uc-s3-access-role
	- ARN空欄が許可されない画面では、先に暫定IAMロールを作成してARNを入力する

## ARN空欄不可の場合の進め方（暫定ロール先行）

1. AWS IAMで暫定ロールを先に作成する
2. 作成したロールARNをDatabricksの資格情報作成画面へ入力する
3. Databricks画面でTrust Policy/External IDを確認する
4. AWS IAMに戻り、暫定ロールの信頼ポリシーをDatabricks提示値で上書きする
5. Databricksへ戻って資格情報作成を完了する

## 詳細手順（クリック操作）

### 1) 資格情報を作成

1. Databricksにログインする
2. `Catalog` を開く
3. `External data` -> `Credentials` を開く
4. `Create credential` をクリックする
5. 認証方式で `IAM role`（Assume role）を選ぶ
6. `Credential name` に `sc_s3_databricks_demo` を入力する
7. IAMロールARNを入力する（ARN空欄不可の画面のため）
8. 画面上に表示されるTrust PolicyとExternal IDを確認する
9. 必要に応じてAWS側のロール信頼ポリシーを更新する

### 2) AWS IAMロールのTrust Policy確認

1. Databricks画面に表示されたTrust Policy JSONをコピーする
2. JSON内の Principal と `sts:ExternalId` が含まれていることを確認する

### 3) AWS側でIAMロール作成

1. AWSコンソールで `IAM` -> `ロール` -> `ロールを作成` を開く
2. `信頼されたエンティティタイプ` で `カスタム信頼ポリシー` を選択する
3. 暫定ロール作成時は、まず仮の信頼ポリシーでロールを作成する
4. ロール名を入力して作成する（例: databricks-uc-s3-access-role）
5. S3アクセス用ポリシーをロールへアタッチする
6. Databricks表示値が取れたら、ロールの `信頼関係` タブでTrust PolicyをDatabricksのJSONに上書きする
7. DatabricksからコピーしたTrust Policy JSONが最新であることを確認する

### 暫定ロール作成時の仮Trust Policy（例）

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Principal": {
				"AWS": "arn:aws:iam::779846810360:root"
			},
			"Action": "sts:AssumeRole"
		}
	]
}
```

注記:
- 仮Trust Policyは暫定です。最終的には必ずDatabricks画面が提示したTrust Policyに置き換える
- 置き換え前にCredentialを本番利用しない

### 4) IAMロールARNの入力内容を確認して資格情報を保存

1. Databricksの `Create credential` 画面へ戻る
2. ロールARN入力欄が正しいARNになっていることを確認する
	- 例: `arn:aws:iam::123456789012:role/databricks-uc-s3-access-role`
3. `Create` でStorage Credentialを保存する

### 5) 外部ロケーションを作成

1. Databricks `Catalog` -> `External data` -> `External locations` を開く
2. `Create external location` をクリックする
3. `Name` を入力する（例: ext_s3_sales_lake）
4. `URL` に `s3://tanaka-databricks-demo-20260518/` を入力する
5. `Credential` に先ほど作成したStorage Credentialを選択する
6. `Create` をクリックする
7. 必要なユーザーまたはグループに権限を付与する

## SQLサンプル

```sql
CREATE CATALOG IF NOT EXISTS aws_demo_catalog;

CREATE SCHEMA IF NOT EXISTS aws_demo_catalog.sales_schema;
```

## Catalog / Schema 作成のタイミング

- Storage Credential / External Location 作成後に実施して問題ありません
- 既に作成済みの場合は再作成不要です（IF NOT EXISTS）

## Storage Credential / External Location の考え方

- Storage Credential: クラウドストレージへ接続する認証情報
- External Location: ストレージパスとStorage Credentialを紐付ける管理オブジェクト

## 設定時に必要な情報

- Storage Credential名（このプロジェクトでは `sc_s3_databricks_demo`）
- IAMロールARN
- S3バケットパス（例: s3://tanaka-databricks-demo-20260518/）
- 利用するCatalog/Schema名

## チェックポイント

- CatalogとSchemaが作成済み
- Storage Credentialが作成済み
- External Locationが作成済み
- 対象ユーザーやグループへ利用権限を付与済み
