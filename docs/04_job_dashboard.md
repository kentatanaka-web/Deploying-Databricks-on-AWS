# 04 Job and Dashboard

## 目的

Notebook処理を定期実行し、成果を可視化して運用可能な形にします。

## Job化の進め方

1. 最初はDatabricks画面からJobを作成
2. Bronze -> Silver -> Goldの順でTaskを定義
3. 失敗時通知とリトライを設定
4. 実行履歴を確認し、READMEへ運用手順を記録

## Dashboard作成

1. GoldテーブルをもとにSQLクエリ作成
2. 売上推移や商品別売上などの可視化を作成
3. フィルタ付きで確認できるように設定

## CI/CDの発展ステップ

- 初級: 手動でJob作成・実行
- 中級: READMEに手順と運用ルールを明記
- 上級: Databricks Asset Bundles + GitHub Actionsで自動化

## チェックポイント

- Jobがスケジュール実行される
- 失敗時に原因追跡できる
- Dashboardが面接時デモで使える
