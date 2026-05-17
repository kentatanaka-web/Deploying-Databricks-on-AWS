-- =====================================================
-- E-8: Databricks SQL Dashboard クエリセット
-- =====================================================
-- 用途: SQL Dashboard ビジュアライゼーション用
-- 対象: Gold tables (gold_daily_sales, gold_category_summary, gold_salesperson_ranking)
-- 実行日: 2026-05-18
-- =====================================================

-- =====================================================
-- 1. Daily Sales Trend (折れ線グラフ用)
-- =====================================================
-- Widget: Line Chart (X: transaction_date, Y: net_sales, 7日MA)
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

-- =====================================================
-- 2. Category Sales Mix (円グラフ用)
-- =====================================================
-- Widget: Pie Chart (category, sales_amount)
SELECT
    category,
    net_sales,
    ROUND(net_sales * 100.0 / SUM(net_sales) OVER(), 2) AS pct_of_total,
    transaction_count
FROM aws_demo_catalog.sales_schema.gold_category_summary
ORDER BY net_sales DESC;

-- =====================================================
-- 3. Salesperson Performance Ranking (棒グラフ用)
-- =====================================================
-- Widget: Bar Chart (sales_person/region, net_sales)
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

-- =====================================================
-- 4. KPI Scorecard (数値表示用)
-- =====================================================
-- Widget: Gauge / Number card (複数ウィジェット)
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
    4252.5 AS kpi_value,  -- Osaka (Query 8)
    '¥' AS unit;

-- =====================================================
-- 5. Regional Performance Summary (テーブル用)
-- =====================================================
-- Widget: Table (regions, sales, customers)
-- Note: このクエリは Query 8 の拡張版
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

-- =====================================================
-- 6. Category Performance Detail (テーブル用)
-- =====================================================
-- Widget: Table (category metrics for drill-down)
SELECT
    category,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN repeat_flag >= 2 THEN customer_id END) AS repeat_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN repeat_flag >= 2 THEN customer_id END) * 100.0
        / COUNT(DISTINCT customer_id), 2
    ) AS repeat_customer_pct,
    transaction_count,
    net_sales,
    ROUND(net_sales / transaction_count, 2) AS avg_sale_per_transaction
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

-- =====================================================
-- 7. Payment Method Comparison (棒グラフ用)
-- =====================================================
-- Widget: Bar Chart (支払方法別比較)
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

-- =====================================================
-- 8. Daily Metrics Summary (時系列テーブル用)
-- =====================================================
-- Widget: Table (日別推移)
SELECT
    transaction_date,
    daily_transaction_count,
    daily_customers,
    daily_net_sales,
    daily_avg_transaction,
    ROUND(daily_net_sales / LAG(daily_net_sales) OVER (ORDER BY transaction_date) - 1, 4) * 100 AS mom_growth_pct,
    ROUND(
        AVG(daily_net_sales) OVER (
            ORDER BY transaction_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS ma_7day
FROM aws_demo_catalog.sales_schema.gold_daily_sales
ORDER BY transaction_date DESC;
