# 06 Execution Runbook (Free Edition -> AWS Workspace)

## ゴール

AWS S3 + Databricks + Unity Catalog（Storage Credential / External Location）で、Bronze / Silver / Gold基盤を再現可能な形で構築する。

## 方針

- Free Editionで制約がある場合は、早めにAWS通常ワークスペースへ移行する
- 以降は公式手順に沿って、IAMロール作成 -> Storage Credential -> External Location の順で実施する
- すべての設定値と画面結果をGitHubに記録する

## フェーズA: 事前判定（30分）

1. Databricks環境が Free Edition か確認する
2. `Catalog` で `Credentials` / `External locations` メニューが表示されるか確認する
3. `Create credential` 画面で以下が取得できるか確認する
   - IAMロールARN入力欄
   - 作成後にExternal IDが表示される導線
4. `No results found` などで進めない場合は、Free Edition制約と判断してフェーズBへ進む

記録する内容:

- 環境名（Free Edition or AWS Workspace）
- 画面の制約内容（例: instance profile候補なし）
- 判断理由（移行する / しない）

## フェーズB: AWS通常ワークスペース準備（1-2時間）

### B-1. Databricks on AWSの通常ワークスペースを作成

1. Databricks公式サイトから `Start free trial` または有償アカウント作成に進む
2. クラウドとして `AWS` を選択する
3. リージョンを選択する
   - 推奨: `ap-northeast-1`（S3バケットと同じリージョン）
4. ワークスペース名を入力する
   - 例: `aws-data-platform-ws`
5. 作成完了後、ワークスペースURLへログインする

記録する値:

- Workspace URL
- リージョン
- Workspace名

### B-2. Unity Catalog利用可否を確認

1. Databricks左メニューで `Catalog` が表示されるか確認する
2. `Catalog` 画面で `External data` -> `Credentials` が表示されるか確認する
3. `Create credential` ボタンが有効か確認する
4. `External data` -> `External locations` が表示されるか確認する

### B-3. 権限とメタストア関連付けを確認

1. `Catalog` 画面でエラーがないか確認する
2. SQL Editorで以下を実行して権限を確認する

```sql
SHOW GRANTS ON METASTORE;
```

3. `CREATE STORAGE CREDENTIAL` と `CREATE EXTERNAL LOCATION` 相当の権限があるか確認する
4. 権限不足なら、管理者に以下を依頼する
   - メタストアに対する必要権限の付与
   - ワークスペースのメタストア関連付け確認

### B-4. このフェーズの完了条件

- `Catalog` が利用可能
- `Credentials` と `External locations` メニューが表示
- Storage Credential作成に進める

完了条件:

- Unity Catalogが利用可能
- `CREATE STORAGE CREDENTIAL` を実行できる権限がある

## フェーズC: AWS側セットアップ（S3/IAM）

### C-1. S3バケットとフォルダを作成

1. AWSコンソールで `S3` を開く
2. `バケットを作成` をクリックする
3. バケット名を入力する
   - `tanaka-databricks-demo-20260518`
4. リージョンを選択する
   - Databricksワークスペースと同じリージョン
5. 以下フォルダを作成する
   - `raw/sales`
   - `bronze`
   - `silver`
   - `gold`

### C-2. IAMロールを作成

1. AWSコンソールで `IAM` -> `ロール` -> `ロールを作成`
2. `信頼されたエンティティタイプ` で `カスタム信頼ポリシー` を選択
3. 暫定Trust Policyを貼り付けてロールを作成
4. ロール名を入力
   - 例: `databricks-uc-s3-access-role`
5. ロールARNを控える

### C-2補足. 暫定Trust Policyとは（重要）

暫定Trust Policyは、DatabricksのExternal IDがまだ未取得の段階で、先にIAMロールARNを作るための一時的な信頼ポリシーです。

使う理由:

- Databricks画面でStorage Credential作成時にIAMロールARNが必須の場合がある
- 先にIAMロールを作らないとARNが得られない
- ただしこの時点ではExternal IDが未確定のため、最終Trust Policyはまだ作れない

一時的に使うJSON例:

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

運用ルール:

1. このポリシーはロールARN作成のためだけに使う
2. Storage Credential作成後に取得した `External ID` を使って、必ずTrust Policyを本番版へ更新する
3. 更新前の暫定ポリシー状態で本番運用を開始しない

本番版へ更新するときのポイント:

- `Principal` はDatabricks公式手順で示される値を使用する
- `Condition.StringEquals.sts:ExternalId` に、Databricksが発行した値を設定する
- プレースホルダー文字列（例: `<databricks-aws-account-id>`）は絶対に残さない

よくある失敗:

- `Invalid principal in policy`
   - 原因: プレースホルダーをそのまま貼り付けた
- `AssumeRole` 失敗
   - 原因: External ID不一致、またはTrust Policy未更新

### C-3. S3アクセス用IAMポリシーを作成してアタッチ

#### C-3-1. IAMポリシー作成画面を開く

1. AWSコンソール上部検索で `IAM` を開く
2. 左メニュー `アクセス管理` -> `ポリシー`
3. 右上 `ポリシーを作成` をクリック
4. `JSON` タブを選択

#### C-3-2. S3アクセス権JSONを入力する

1. 既存JSONを全消去して、以下を貼り付ける
2. `<BUCKET>` を `tanaka-databricks-demo-20260518` に置換する

```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Sid": "AllowS3DataAccess",
         "Effect": "Allow",
         "Action": [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ListBucket",
            "s3:GetBucketLocation",
            "s3:ListBucketMultipartUploads",
            "s3:ListMultipartUploadParts",
            "s3:AbortMultipartUpload"
         ],
         "Resource": [
            "arn:aws:s3:::tanaka-databricks-demo-20260518",
            "arn:aws:s3:::tanaka-databricks-demo-20260518/*"
         ]
      },
      {
         "Sid": "AllowRoleSelfAssume",
         "Effect": "Allow",
         "Action": [
            "sts:AssumeRole"
         ],
         "Resource": [
            "arn:aws:iam::779846810360:role/databricks-uc-s3-access-role"
         ]
      }
   ]
}
```

3. `次へ` をクリック
4. ポリシー名を入力
    - 例: `databricks-uc-s3-access-policy`
5. 内容を確認して `ポリシーを作成`

#### C-3-3. 作成したIAMポリシーをロールへアタッチ

1. 左メニュー `ロール` を開く
2. ロール名 `databricks-uc-s3-access-role` をクリック
3. `アクセス許可を追加` -> `ポリシーをアタッチ`
4. `databricks-uc-s3-access-policy` を検索してチェック
5. `アクセス許可を追加` をクリック

#### C-3-4. 反映確認

1. ロール詳細の `アクセス許可` タブに以下が表示されることを確認
    - `databricks-uc-s3-access-policy`
2. `信頼関係` タブは次のD-3で更新するため、この時点では暫定でもよい
3. エラーが出た場合は、JSON内のバケット名とロールARNのスペルを再確認する

### C-4. このフェーズの完了条件

- S3バケットと4階層フォルダ作成済み
- IAMロール作成済み
- IAMロールARNを記録済み
- S3アクセス用ポリシーをロールにアタッチ済み

補足:

- IAMロールは最初に暫定Trust Policyで作成してよい
- Storage Credential作成後にExternal IDを反映してTrust Policyを更新する

## フェーズD: Databricks側セットアップ（Unity Catalog）

### D-1. Catalog/Schemaを作成

1. Databricks SQL Editorを開く
2. 以下SQLを実行する

```sql
CREATE CATALOG IF NOT EXISTS aws_demo_catalog;
CREATE SCHEMA IF NOT EXISTS aws_demo_catalog.sales_schema;
```

3. `aws_demo_catalog.sales_schema` が一覧で見えることを確認する

### D-2. Storage Credentialを作成

1. `Catalog` -> `External data` -> `Credentials` を開く
2. `Create credential` をクリック
3. Credential Typeで `AWS IAM Role` を選択
4. Nameに `sc_s3_databricks_demo` を入力
5. IAM Role ARNに、Cフェーズで控えたARNを入力
6. `Create` をクリック

### D-3. External IDを取得してAWSへ反映

#### D-3-1. AWS IAM信頼ポリシー更新（詳細手順）

1. **AWSコンソール** を開く -> IAM -> `Roles`
2. ロール名 `databricks-uc-s3-access-role` をクリック
3. **Trust relationships** タブを開く
4. **Edit trust policy** をクリック
5. JSON全体を以下のように置き換える
   - 外部ID値は、Databricksで作成したStorage Credentialから取得した値に置き換える

置き換え対象（現在の暫定ポリシー）:
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

置き換え先（本番版ポリシー - 外部IDを含む）:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::779846810360:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "b1454c36-c169-4fdc-bd79-1b117e3746bb"
                }
            }
        },
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "b1454c36-c169-4fdc-bd79-1b117e3746bb"
                }
            }
        }
    ]
}
```

6. **Update policy** をクリック
7. エラーが出ないことを確認

#### D-3-2. ポリシー置き換えのポイント

| 項目 | 説明 |
|------|------|
| **Statement 1** | あなたのAWSアカウント（779846810360）がロールをAssumeする際の信頼設定。ローカルテスト用 |
| **Statement 2** | DatabricksのAWSアカウント（414351767826）がロールをAssumeする際の信頼設定。本番運用で必須 |
| **sts:ExternalId** | Databricksが発行した外部ID。両Statement で同じ値を使用。スペルミスは絶対に避ける |
| **414351767826** | Databricksが管理するAWSアカウント。変更しない |
| **unity-catalog-prod-...** | Databricksの標準ロール名。変更しない |

#### D-3-3. 反映確認

1. ポリシー更新後、Trust relationships タブを確認
2. 以下が表示されることを確認
   - Statement 1（arn:aws:iam::779846810360:root）
   - Statement 2（arn:aws:iam::414351767826:role/...）
   - 両方に `Condition` として sts:ExternalId が設定されている
3. エラーメッセージが出ていない

#### D-3-4. トラブル対応

| エラー | 原因 | 対策 |
|--------|------|------|
| `Invalid principal in policy` | Principal ARNのスペルミス | ARN値を公式ドキュメントから再確認 |
| `Invalid action` | Action値が誤字 | `"sts:AssumeRole"` であることを確認 |
| `Condition format error` | JSON形式エラー | 全体をJSONバリデータで検証 |

### D-4. External Locationを作成

1. `Catalog` -> `External data` -> `External locations`
2. `Create external location` をクリック
3. 以下を入力
   - Name: `ext_s3_sales_lake`
   - URL: `s3://tanaka-databricks-demo-20260518/`
   - Credential: `sc_s3_databricks_demo`
4. `Create` をクリック

### D-5. このフェーズの完了条件

- Storage Credential作成成功
- Trust PolicyがExternal ID反映済み
- External Location作成成功
- 権限不足エラーが出ていない

完了条件:

- Storage Credentialが `Ready` 状態
- External Location作成成功

## フェーズE: データ実装（Bronze / Silver / Gold）

### E-1. 生データをS3へ配置

1. ローカルの `sample_data/sales_sample.csv` を開く
2. AWS S3の `raw/sales` にアップロードする
3. S3上にファイルが見えることを確認する

### E-2. Bronze作成

1. `notebooks/01_ingest_bronze.py` をDatabricksで実行
2. テーブル `aws_demo_catalog.sales_schema.bronze_sales` の件数を確認

### E-3. Silver作成

1. `notebooks/02_transform_silver.py` を実行
2. 型変換・欠損除外が反映されているか確認

### E-4. Gold作成

1. `notebooks/03_create_gold.py` を実行
2. `gold_sales_daily` が作成されているか確認

### E-5. SQLで品質確認

1. `sql/03_analysis_queries.sql` のクエリを実行
2. 日次売上・商品別売上が返ることを確認

### E-6. このフェーズの完了条件

- Bronze / Silver / Gold の3テーブル作成済み
- 分析クエリがエラーなく実行できる

## フェーズF: Job / Dashboard / GitHub公開

### F-1. Jobを作成

1. Databricksの `Workflows` -> `Jobs` を開く
2. `Create job` をクリック
3. タスクを3つ作成
   - Task1: 01_ingest_bronze
   - Task2: 02_transform_silver（Task1依存）
   - Task3: 03_create_gold（Task2依存）
4. `Run now` で実行し、3タスク成功を確認

### F-2. Dashboardを作成

1. Databricks SQLでGoldテーブル向けクエリを作成
2. 可視化（折れ線・棒）を作成
3. Dashboardに配置して保存

### F-3. 証跡を保存

1. 以下のスクリーンショットを取得
   - Storage Credential作成完了
   - External Location作成完了
   - Job成功画面
   - Dashboard画面
2. `images/` 配下に保存する

### F-4. READMEとdocsを更新

1. 実際の実行日と結果を追記
2. トラブルと対処を1行ずつ残す
3. 参照リンク（docs/sql/notebooks）を追記

### F-5. GitHubへ反映

1. 変更ファイルを確認
2. コミット作成
3. `main` へプッシュ

### F-6. このフェーズの完了条件

- Job成功履歴あり
- Dashboard表示確認済み
- GitHubで第三者が手順を追える状態

## 失敗時のチェックリスト

- Invalid principal in policy
  - プレースホルダー値を使っていないか
- AssumeRole失敗
  - External IDが一致しているか
- External Location作成失敗
  - Storage Credential名、S3 URL、権限を確認
- Databricks側メニュー不足
  - Free Edition制約の可能性を再確認

## コマンド記録テンプレート（GitHub向け）

```text
Date:
Workspace type:
Bucket:
IAM Role ARN:
Storage Credential:
External Location:
Result:
Troubleshooting:
```

## 参照

- docs/01_aws_setup.md
- docs/02_databricks_setup.md
- docs/05_free_edition_support_check.md
