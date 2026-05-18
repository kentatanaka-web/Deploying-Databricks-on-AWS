# 04 Job Preparation

## 目的

Notebook処理を定期実行できる形に整理し、SQL分析完了までを運用可能にします。

## Job化の進め方

1. 最初はDatabricks画面からJobを作成
2. Bronze -> Silver -> Goldの順でTaskを定義
3. 失敗時通知とリトライを設定
4. 実行履歴を確認し、READMEへ運用手順を記録

## このドキュメントのスコープ

- 対象: Job設計（依存関係、再実行性、監視）
- 非対象: 可視化実装

## CI/CDの発展ステップ

- 初級: 手動でJob作成・実行
- 中級: READMEに手順と運用ルールを明記
- 上級: Databricks Asset Bundles + GitHub Actionsで自動化

## チェックポイント

- Jobがスケジュール実行される
- 失敗時に原因追跡できる
- Bronze -> Silver -> Goldの依存順が崩れていない
