# 01 AWS Setup

## 目的

DatabricksからアクセスするS3データレイクとIAMロールを準備します。

## 手順

1. S3バケットを作成する
2. S3フォルダ構成を作成する
3. Databricks用IAMロールを作成する
4. 必要なS3アクセス権をIAMポリシーで付与する

## 手順1: S3バケットを作成する（AWSコンソール操作）

1. AWSマネジメントコンソールにログインする
2. 上部の検索バーで `S3` と入力し、`S3` をクリックする
3. S3画面右上の `バケットを作成` をクリックする
4. `バケット名` に一意の名前を入力する
	- 例: `tanaka-databricks-demo-20260518`
5. `AWSリージョン` を選択する
	- Databricks Workspaceと同じリージョンを推奨（例: `ap-northeast-1`）
6. `オブジェクト所有権` は `ACL無効（推奨）` のままにする
7. `このバケットのパブリックアクセスをすべてブロック` は有効のままにする
8. `バケットのバージョニング` は学習用途では `無効` のままでよい
9. `デフォルトの暗号化` は `Amazon S3 マネージドキー（SSE-S3）` を選択する
10. 画面下部の `バケットを作成` をクリックする
11. バケット一覧に作成したバケット名が表示されることを確認する

## 手順2: S3フォルダ構成を作成する（AWSコンソール操作）

1. S3の `バケット` 一覧から作成したバケット名をクリックする
2. `オブジェクト` タブで `フォルダを作成` をクリックする
3. `フォルダ名` に `raw` を入力し `フォルダを作成` をクリックする
4. 同じ操作で `bronze`、`silver`、`gold` を作成する
5. `raw` フォルダをクリックして開く
6. `フォルダを作成` をクリックし、`sales` を作成する
7. 必要であれば `raw/sales` にテストCSVをアップロードする
	- `アップロード` -> `ファイルを追加` -> `sales_sample.csv` を選択 -> `アップロード`
8. 最終的に以下構成になっていることを確認する

```text
s3://<your-bucket-name>/
├── raw/
│   └── sales/
├── bronze/
├── silver/
└── gold/
```

## S3バケット命名例

- tanaka-databricks-demo-20260518

## S3フォルダ構成

```text
s3://<your-bucket-name>/
├── raw/
│   └── sales/
├── bronze/
├── silver/
└── gold/
```

## 手順3: Databricks用IAMロールを作成する（AWSコンソール操作）

前提: 先にDatabricks側でStorage Credential作成を開始し、Trust PolicyとExternal IDを表示してからAWS作業に入る（詳細は docs/02_databricks_setup.md）。

1. AWSコンソール上部の検索バーで `IAM` と入力し、`IAM` をクリックする
2. 左メニューの `アクセス管理` -> `ロール` をクリックする
3. 右上の `ロールを作成` をクリックする
4. `信頼されたエンティティタイプ` で `カスタム信頼ポリシー` を選択する
5. 信頼ポリシー入力欄に、Databricksの手順で表示される内容を貼り付ける
	 - ここはDatabricks Workspace（Unity Catalog設定画面）で提示される値を使う
	 - 外部ID（External ID）が必要な構成では、Databricks指定値をそのまま利用する
6. `次へ` をクリックする
7. `アクセス許可ポリシー` は一旦未選択でもよい（次の手順4で作成して付与）
8. `次へ` をクリックする
9. `ロール名` を入力する
	 - 例: `databricks-uc-s3-access-role`
10. 内容を確認し `ロールを作成` をクリックする

### 信頼ポリシー例（形式サンプル）

注記:
- `<databricks-aws-account-id>` と `<databricks-generated-external-id>` は事前に固定値を入れない
- DatabricksのStorage Credential作成画面で表示された値をそのまま貼り付ける
- まだ値が確定していない段階では、このサンプルをそのまま使わず、Databricks表示JSONを優先する

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Principal": {
				"AWS": "arn:aws:iam::<databricks-aws-account-id>:root"
			},
			"Action": "sts:AssumeRole",
			"Condition": {
				"StringEquals": {
					"sts:ExternalId": "<databricks-generated-external-id>"
				}
			}
		}
	]
}
```

## 手順4: 必要なS3アクセス権をIAMポリシーで付与する（AWSコンソール操作）

1. IAM画面左メニューの `アクセス管理` -> `ポリシー` をクリックする
2. 右上の `ポリシーを作成` をクリックする
3. `JSON` タブを選択する
4. 以下サンプルを貼り付け、`<your-bucket-name>` を実バケット名に置換する
5. `次へ` をクリックする
6. `ポリシー名` を入力する
	 - 例: `databricks-uc-s3-access-policy`
7. `ポリシーを作成` をクリックする
8. 左メニュー `ロール` から手順3で作成したロールを開く
9. `アクセス許可を追加` -> `ポリシーをアタッチ` をクリックする
10. 作成したポリシーを検索してチェックし、`アクセス許可を追加` をクリックする

### S3アクセス権ポリシー例（最小構成）

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AllowListBucket",
			"Effect": "Allow",
			"Action": [
				"s3:ListBucket"
			],
			"Resource": "arn:aws:s3:::<your-bucket-name>"
		},
		{
			"Sid": "AllowObjectAccess",
			"Effect": "Allow",
			"Action": [
				"s3:GetObject",
				"s3:PutObject",
				"s3:DeleteObject"
			],
			"Resource": [
				"arn:aws:s3:::<your-bucket-name>/raw/*",
				"arn:aws:s3:::<your-bucket-name>/bronze/*",
				"arn:aws:s3:::<your-bucket-name>/silver/*",
				"arn:aws:s3:::<your-bucket-name>/gold/*"
			]
		}
	]
}
```

### Databricks設定で使うARNの確認

1. IAMの `ロール` 一覧から作成したロールをクリックする
2. `ARN` の値をコピーする
3. このARNをDatabricksのStorage Credential作成時に利用する

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
