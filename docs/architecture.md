# Architecture

## 論理構成

```text
AWS S3 (raw/)
  -> Databricks Bronze (Delta)
  -> Databricks Silver (Delta)
  -> Databricks Gold (Delta)
  -> Job (schedule)
  -> Dashboard (BI)
```

## Mermaid図（Markdown描画用）

```mermaid
flowchart TD
    A[S3 raw data] --> B[Bronze Delta Table]
    B --> C[Silver Delta Table]
    C --> D[Gold Delta Table]
    D --> E[Databricks Job]
    D --> F[Dashboard]
```

## 今後追加する図

- images/architecture.png に図を保存
- READMEに画像を埋め込み
