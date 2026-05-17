-- ==============================================================================
-- フェーズE-5: 高度な分析クエリ
-- 目的: Gold層テーブルを使った経営判断向けの分析
-- ==============================================================================

-- ============================================================================
-- クエリ1: 日次売上トレンド（7日移動平均）
-- ============================================================================

SELECT
    transaction_date,
    total_sales,
    net_sales,
    AVG(total_sales) OVER (
        ORDER BY transaction_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma7_total_sales,
    AVG(net_sales) OVER (
        ORDER BY transaction_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ma7_net_sales
FROM aws_demo_catalog.sales_schema.gold_daily_sales
ORDER BY transaction_date;

-- ============================================================================
-- クエリ2: カテゴリ別売上シェア
-- ============================================================================

SELECT
    category,
    transaction_count,
    total_sales,
    net_sales,
    ROUND(total_sales / SUM(total_sales) OVER () * 100, 2) AS sales_share_pct,
    ROUND(net_sales / SUM(net_sales) OVER () * 100, 2) AS net_sales_share_pct,
    ROUND(avg_discount_rate * 100, 2) AS discount_rate_pct,
    unique_products,
    unique_customers
FROM aws_demo_catalog.sales_schema.gold_category_summary
ORDER BY total_sales DESC;

-- ============================================================================
-- クエリ3: 営業人員パフォーマンススコアリング
-- ============================================================================

SELECT
    sales_person,
    region,
    transaction_count,
    unique_customers,
    total_sales,
    net_sales,
    ROUND(avg_transaction_amount, 2) AS avg_transaction,
    ROUND(avg_discount_rate * 100, 2) AS discount_rate_pct,
    RANK() OVER (ORDER BY net_sales DESC) AS sales_rank,
    CASE 
        WHEN net_sales >= 4000 THEN 'A (Outstanding)'
        WHEN net_sales >= 2000 THEN 'B (Good)'
        WHEN net_sales >= 1000 THEN 'C (Average)'
        ELSE 'D (Needs Improvement)'
    END AS performance_grade
FROM aws_demo_catalog.sales_schema.gold_salesperson_ranking
ORDER BY net_sales DESC;

-- ============================================================================
-- クエリ4: 顧客セグメント分析（Silver層から直接）
-- ============================================================================

SELECT
    region,
    sales_amount_rank,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_amount), 2) AS total_sales,
    ROUND(SUM(net_sales_amount), 2) AS net_sales,
    ROUND(AVG(net_sales_amount), 2) AS avg_transaction
FROM aws_demo_catalog.sales_schema.silver_sales
GROUP BY region, sales_amount_rank
ORDER BY region, 
    CASE 
        WHEN sales_amount_rank = 'High' THEN 1
        WHEN sales_amount_rank = 'Medium' THEN 2
        ELSE 3
    END;

-- ============================================================================
-- クエリ5: 割引戦略の効果分析
-- ============================================================================

SELECT
    CASE 
        WHEN discount_rate = 0.0 THEN 'No Discount'
        WHEN discount_rate <= 0.05 THEN '1-5%'
        WHEN discount_rate <= 0.10 THEN '6-10%'
        ELSE '11%+'
    END AS discount_bucket,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_amount), 2) AS total_sales,
    ROUND(SUM(net_sales_amount), 2) AS net_sales,
    ROUND(SUM(discount_amount), 2) AS discount_given,
    ROUND(AVG(net_sales_amount), 2) AS avg_net_sales,
    ROUND(SUM(net_sales_amount) / SUM(discount_amount), 2) AS roi_ratio
FROM aws_demo_catalog.sales_schema.silver_sales
WHERE discount_rate > 0 OR discount_rate = 0.0
GROUP BY discount_bucket
ORDER BY 
    CASE 
        WHEN discount_bucket = 'No Discount' THEN 1
        WHEN discount_bucket = '1-5%' THEN 2
        WHEN discount_bucket = '6-10%' THEN 3
        ELSE 4
    END;

-- ============================================================================
-- クエリ6: 支払方法別の購買パターン
-- ============================================================================

SELECT
    payment_method,
    COUNT(*) AS transaction_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(total_amount), 2) AS total_sales,
    ROUND(AVG(net_sales_amount), 2) AS avg_transaction,
    ROUND(SUM(discount_amount), 2) AS total_discount,
    ROUND(AVG(discount_rate) * 100, 2) AS avg_discount_pct
FROM aws_demo_catalog.sales_schema.silver_sales
GROUP BY payment_method
ORDER BY total_sales DESC;

-- ============================================================================
-- クエリ7: 商品カテゴリ別の顧客ロイヤルティ
-- ============================================================================

SELECT
    category,
    COUNT(DISTINCT customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN transaction_count_by_customer >= 2 THEN customer_id END) AS repeat_customers,
    ROUND(
        COUNT(DISTINCT CASE WHEN transaction_count_by_customer >= 2 THEN customer_id END) * 100.0 
        / COUNT(DISTINCT customer_id), 2
    ) AS repeat_customer_pct,
    ROUND(AVG(transaction_count_by_customer), 2) AS avg_purchases_per_customer
FROM (
    SELECT
        category,
        customer_id,
        COUNT(*) AS transaction_count_by_customer
    FROM aws_demo_catalog.sales_schema.silver_sales
    GROUP BY category, customer_id
)
GROUP BY category
ORDER BY repeat_customer_pct DESC;

-- ============================================================================
-- クエリ8: KPI ダッシュボード用サマリー
-- ============================================================================

SELECT
    'Overall KPI' AS metric_category,
    COUNT(*) AS value_int,
    ROUND(SUM(total_amount), 2) AS total_sales,
    ROUND(SUM(net_sales_amount), 2) AS net_sales,
    ROUND(AVG(net_sales_amount), 2) AS avg_transaction,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(discount_amount), 2) AS total_discount,
    ROUND(AVG(discount_rate) * 100, 2) AS avg_discount_rate_pct
FROM aws_demo_catalog.sales_schema.silver_sales
UNION ALL
SELECT
    CONCAT('Top Region: ', region) AS metric_category,
    COUNT(*) AS value_int,
    ROUND(SUM(total_amount), 2) AS total_sales,
    ROUND(SUM(net_sales_amount), 2) AS net_sales,
    ROUND(AVG(net_sales_amount), 2) AS avg_transaction,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(discount_amount), 2) AS total_discount,
    ROUND(AVG(discount_rate) * 100, 2) AS avg_discount_rate_pct
FROM aws_demo_catalog.sales_schema.silver_sales
GROUP BY region
ORDER BY net_sales DESC
LIMIT 3;