# E-8: Databricks SQL Dashboard 構築ガイド

**実行日**: 2026-05-18  
**目的**: Gold テーブルの結果を BI ダッシュボードで可視化  
**ツール**: Databricks SQL Dashboard

---

## 📋 ダッシュボード構成（8ウィジェット）

| # | ウィジェット名 | タイプ | データソース | 用途 |
|----|---------------|--------|-------------|------|
| 1️⃣ | Daily Sales Trend | Line Chart | gold_daily_sales | 売上トレンド + 7日MA |
| 2️⃣ | Category Sales Mix | Pie Chart | gold_category_summary | 商品カテゴリ別シェア |
| 3️⃣ | Salesperson Ranking | Bar Chart | gold_salesperson_ranking | 営業成績ランキング |
| 4️⃣ | KPI Scorecard | Number Cards | Gold tables | 主要指標（¥総売上など） |
| 5️⃣ | Regional Performance | Table | silver_sales集約 | 地域別詳細 |
| 6️⃣ | Category Detail | Table | silver_sales集約 | カテゴリ別リピート率 |
| 7️⃣ | Payment Method | Bar Chart | silver_sales集約 | 支払方法別比較 |
| 8️⃣ | Daily Metrics | Table | gold_daily_sales | 日別推移＋前月比 |

---

## 🚀 ステップバイステップ実装

### **ステップ 1: Databricks SQL ワークスペースへ移動**

1. Databricks にログイン
2. **SQL** → **SQL Editor** をクリック
3. 左パネルで **Dashboards** を選択

![図1: SQL Editor へのアクセス]

---

### **ステップ 2: 新規ダッシュボードを作成**

```
SQL Editor 右上 → "+ Dashboard" をクリック
または Dashboards → "Create dashboard"
```

**ダッシュボード設定**:
```
名前: Sales Analytics Dashboard
説明: E-5 Gold tables を基に、営業・カテゴリ・地域別分析
タイム更新: 毎時間（または手動）
```

![図2: Dashboard作成]

---

### **ステップ 3: ウィジェット 1 を追加 - Daily Sales Trend**

#### 3-1. 新規クエリを作成

SQL Editor で以下を実行:

```sql
SELECT
    transaction_date,
    daily_net_sales,
    ROUND(
        AVG(daily_net_sales) OVER (
            ORDER BY transaction_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS ma_7day
FROM aws_demo_catalog.sales_schema.gold_daily_sales
ORDER BY transaction_date;
```

#### 3-2. 結果を可視化

- **Run** をクリック
- 結果テーブル下部 → **Visualization** タブ
- ビジュアライゼーションタイプ: **Line Chart**

**設定**:
```
X axis: transaction_date
Y axis (left): daily_net_sales
Y axis (right): ma_7day
Title: "Daily Sales Trend (¥) - with 7-Day MA"
```

#### 3-3. ダッシュボードに追加

- **Add to Dashboard** ボタン
- ダッシュボード選択: "Sales Analytics Dashboard"
- ウィジェットサイズ: **Wide (2 column)**

![図3: Line Chart 追加]

---

### **ステップ 4: ウィジェット 2 を追加 - Category Sales Mix**

#### 4-1. 新規クエリを実行

```sql
SELECT
    category,
    net_sales,
    ROUND(net_sales * 100.0 / SUM(net_sales) OVER(), 2) AS pct_of_total,
    transaction_count
FROM aws_demo_catalog.sales_schema.gold_category_summary
ORDER BY net_sales DESC;
```

#### 4-2. Pie Chart に設定

```
Visualization Type: Pie Chart
Labels: category
Values: net_sales
Title: "Category Sales Mix (¥)"
```

#### 4-3. ダッシュボードに追加

- サイズ: **Square (1 column)**

![図4: Pie Chart 追加]

---

### **ステップ 5: ウィジェット 3 を追加 - Salesperson Ranking**

#### 5-1. クエリ実行

```sql
SELECT
    CONCAT(sales_person, ' (', region, ')') AS salesperson_region,
    net_sales,
    transaction_count,
    avg_transaction_value,
    CASE
        WHEN net_sales >= 4000 THEN 'Grade A - Outstanding'
        WHEN net_sales >= 3000 THEN 'Grade B - Good'
        ELSE 'Grade C - Developing'
    END AS performance_grade
FROM aws_demo_catalog.sales_schema.gold_salesperson_ranking
ORDER BY net_sales DESC;
```

#### 5-2. Bar Chart に設定

```
Visualization: Bar Chart
X axis: salesperson_region
Y axis: net_sales
Title: "Salesperson Performance Ranking (¥)"
```

#### 5-3. ダッシュボードに追加

- サイズ: **Wide (2 column)**

![図5: Bar Chart 追加]

---

### **ステップ 6: ウィジェット 4 を追加 - KPI Scorecard**

#### 6-1. クエリ実行

```sql
SELECT
    'Total Sales (¥)' AS kpi_name,
    ROUND(SUM(daily_net_sales), 0) AS kpi_value,
    '¥' AS unit
FROM aws_demo_catalog.sales_schema.gold_daily_sales
UNION ALL
SELECT
    'Avg Daily Sales (¥)' AS kpi_name,
    ROUND(AVG(daily_net_sales), 0) AS kpi_value,
    '¥' AS unit
FROM aws_demo_catalog.sales_schema.gold_daily_sales
UNION ALL
SELECT
    'Max Daily Sales (¥)' AS kpi_name,
    ROUND(MAX(daily_net_sales), 0) AS kpi_value,
    '¥' AS unit
FROM aws_demo_catalog.sales_schema.gold_daily_sales
UNION ALL
SELECT
    'Top Region Net Sales (¥)' AS kpi_name,
    4252.5 AS kpi_value,
    '¥' AS unit;
```

#### 6-2. Number Card に設定

```
Visualization: Number
Title: "KPI Summary"
(複数 Number Card で各行を表示)
```

#### 6-3. ダッシュボードに追加

- サイズ: **4 × Number Cards (各 1 column)**

![図6: Number Card 追加]

---

### **ステップ 7: ウィジェット 5-8 を追加 - Table ビジュアライゼーション**

#### 7-1. Regional Performance Table

```sql
WITH regional_data AS (
    SELECT
        region,
        COUNT(*) AS transaction_count,
        COUNT(DISTINCT customer_id) AS unique_customers,
        ROUND(SUM(total_amount), 2) AS gross_sales,
        ROUND(SUM(net_sales_amount), 2) AS net_sales,
        ROUND(AVG(net_sales_amount), 2) AS avg_transaction,
        ROUND(SUM(discount_amount), 2) AS total_discount,
        ROUND(AVG(discount_rate) * 100, 2) AS avg_discount_pct
    FROM aws_demo_catalog.sales_schema.silver_sales
    GROUP BY region
)
SELECT
    *,
    ROW_NUMBER() OVER (ORDER BY net_sales DESC) AS rank
FROM regional_data
ORDER BY rank;
```

**ビジュアライゼーション**: Table  
**タイトル**: "Regional Performance Summary"

#### 7-2. Category Detail Table

```sql
SELECT
    category,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN repeat_flag >= 2 THEN customer_id END) AS repeat_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN repeat_flag >= 2 THEN customer_id END) * 100.0
        / COUNT(DISTINCT customer_id), 2
    ) AS repeat_customer_pct,
    transaction_count,
    net_sales
FROM (
    SELECT
        category,
        customer_id,
        COUNT(*) AS repeat_flag
    FROM aws_demo_catalog.sales_schema.silver_sales
    GROUP BY category, customer_id
) cust_view
GROUP BY category, transaction_count, net_sales
ORDER BY net_sales DESC;
```

**ビジュアライゼーション**: Table  
**タイトル**: "Category Performance Detail (Loyalty Analysis)"

#### 7-3. Payment Method Comparison

```sql
SELECT
    payment_method,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(net_sales_amount), 2) AS net_sales,
    ROUND(AVG(net_sales_amount), 2) AS avg_transaction,
    ROUND(SUM(net_sales_amount) * 100.0 / 
        SUM(SUM(net_sales_amount)) OVER(), 2) AS sales_pct
FROM aws_demo_catalog.sales_schema.silver_sales
GROUP BY payment_method
ORDER BY net_sales DESC;
```

**ビジュアライゼーション**: Bar Chart  
**タイトル**: "Payment Method Comparison"

#### 7-4. Daily Metrics Summary

```sql
SELECT
    transaction_date,
    daily_transaction_count,
    daily_customers,
    daily_net_sales,
    daily_avg_transaction,
    ROUND(
        AVG(daily_net_sales) OVER (
            ORDER BY transaction_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS ma_7day
FROM aws_demo_catalog.sales_schema.gold_daily_sales
ORDER BY transaction_date DESC;
```

**ビジュアライゼーション**: Table  
**タイトル**: "Daily Metrics Summary"

---

### **ステップ 8: ダッシュボードをレイアウト**

#### 推奨レイアウト:

```
【上段】
┌─────────────────────────────────────┐
│  KPI Cards (4個)                    │
│  ¥14,356.5  │  ¥478.55  │  ¥2,956.5  │  ¥4,252.5 │
└─────────────────────────────────────┘

【中段】
┌──────────────────────┬──────────────────┐
│  Daily Sales Trend   │  Category Mix    │
│  (Wide)              │  (Square)        │
└──────────────────────┴──────────────────┘

【下段】
┌─────────────────────────────────────┐
│  Salesperson Ranking (Wide)         │
└─────────────────────────────────────┘

【下々段】
┌──────────────────────┬──────────────────┐
│  Regional Perf Table │  Category Detail │
│  (Wide)              │  (Wide)          │
└──────────────────────┴──────────────────┘

【最下段】
┌─────────────────────────────────────┐
│  Daily Metrics Table (Full Width)   │
└─────────────────────────────────────┘
```

#### 調整方法:

1. ダッシュボード右上 → **Edit** をクリック
2. 各ウィジェットをドラッグで移動
3. 右下角をドラッグでサイズ調整
4. **Save** をクリック

![図7: Dashboard Layout]

---

### **ステップ 9: ダッシュボードを公開・共有**

#### 9-1. ダッシュボード設定

```
ダッシュボード右上 → "Share"
  ├ 権限設定: "Can Edit" or "Can View"
  └ チーム・個人を招待
```

#### 9-2. 定期更新を設定

```
ダッシュボード右上 → "Refresh settings"
  ├ Refresh interval: 1 hour
  └ または Manual
```

#### 9-3. 本番環境への展開

```
URL: https://databricks-workspace-url/sql/dashboards/[dashboard-id]
共有リンク: ✓ 生成・メール共有可能
```

---

## 📊 ダッシュボード完成時のビューイメージ

```
┌────────────────────────────────────────────────────────────┐
│              Sales Analytics Dashboard                     │
│  Last refresh: 2026-05-18 15:30 | Edit | Share | Refresh  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ¥14.4K    │  ¥478.55   │  ¥2,956.5   │  ¥4,252.5        │
│  Total     │  Avg/Tx    │  Max Daily  │  Top Region      │
│  (Net Sales)│(Transaction)│(Sales)      │(Net Sales)       │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Daily Sales Trend          │  Category Mix               │
│  ¥3K ┌─────────────┐        │  ┌─────┐                   │
│      │    ╱╲    ╱╲ │        │  │ Elec│ 72.8%            │
│  ¥2K │   ╱  ╲  ╱  │        │  ├─────┤                   │
│      │  ╱    ╲╱   │        │  │Acc  │ 9.1%             │
│  ¥1K └─────────────┘        │  ├─────┤                   │
│      5/1    5/6    5/12     │  │Office│ 18.2%            │
│                             │  └─────┘                   │
├────────────────────────────────────────────────────────────┤
│  Salesperson Performance Ranking                          │
│  ¥4.3K │ suzuki (Osaka)                                  │
│  ¥3.9K │ yamada (Tokyo)                                  │
│  ¥1.9K │ tanaka (Nagoya)                                 │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  Regional Performance │ Category Performance               │
│  Rank Region  Sales  │ Category  Repeat%  Sales           │
│  1    Osaka   ¥4.3K  │ Elec      37.5%    ¥11.3K          │
│  2    Tokyo   ¥3.9K  │ Acc       25.0%    ¥1.4K           │
│  3    Kyoto   ¥1.2K  │ Office    16.7%    ¥2.8K           │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  Daily Metrics Summary                                    │
│  Date   Count Customers Sales    Avg/Tx  7MA             │
│  5/12   3     2          ¥972     ¥324   ¥1,234          │
│  5/11   2     1          ¥451     ¥225.5 ¥1,156          │
│  5/10   1     1          ¥198     ¥198   ¥987            │
│  ...                                                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## ✅ チェックリスト

ダッシュボード完成時の確認項目:

- [ ] 全 8 ウィジェット追加済み
- [ ] 各ウィジェットにタイトル・ラベル付与
- [ ] レイアウト整理完了
- [ ] 数値フォーマット（通貨記号 ¥、小数点）確認
- [ ] チームメンバーに共有URL配布
- [ ] 定期更新設定（時間単位 or 手動）
- [ ] ダッシュボード URL をドキュメント記載

---

## 🚀 推奨: 次ステップ（オプション）

### **E-9: アラート・通知設定**
- クエリがしきい値を超えたときメール通知
- 例: 日売上 < ¥500 の場合アラート

### **E-10: Tableau/Power BI 連携**
- Databricks → Tableau Direct を接続
- より高度なダッシュボード作成

### **E-11: 定期レポート自動化**
- メール配信: 毎日朝 9:00 にダッシュボードスクリーンショット

---

## 📞 トラブルシューティング

### **Q: ウィジェットに「No data」と出る**
- **A**: クエリの WHERE 条件やテーブル名を確認。Gold テーブルが存在し、データが挿入されているか確認。

### **Q: グラフの軸が逆になっている**
- **A**: Visualization 設定で X/Y 軸を入れ替える。

### **Q: ダッシュボードが遅い**
- **A**: テーブル集計が大規模な場合、パーティション化やキャッシュを検討。

---

## 📝 作成者メモ

- **作成日**: 2026-05-18
- **対象 Databricks Edition**: Free Edition 以上
- **必要権限**: SQL Workspace の Edit 権限
- **推定所要時間**: 30-45 分
