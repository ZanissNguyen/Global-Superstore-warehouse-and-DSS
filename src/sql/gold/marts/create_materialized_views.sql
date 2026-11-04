-- =============================================================================
-- Materialized Views (Data Marts)
-- Responsibility: Pre-aggregated cubes for ultra-fast Power BI and DSS queries
-- =============================================================================

-- 1. Sales Performance Mart
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.mv_sales_mart AS
SELECT 
    d.year,
    d.quarter,
    d.month,
    d.year_month,
    g.market,
    g.region,
    g.country,
    c.segment,
    COUNT(DISTINCT f.order_id) AS order_count,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(SUM(f.quantity), 0) AS total_units,
    ROUND(AVG(f.discount), 4) AS avg_discount,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_customer c ON f.customer_key = c.customer_key
GROUP BY d.year, d.quarter, d.month, d.year_month, g.market, g.region, g.country, c.segment;

CREATE INDEX IF NOT EXISTS idx_mv_sales_mart_time ON gold.mv_sales_mart(year, month);
CREATE INDEX IF NOT EXISTS idx_mv_sales_mart_geo ON gold.mv_sales_mart(market, country);

-- 2. Product Performance Mart
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.mv_product_mart AS
SELECT 
    p.category,
    p.sub_category,
    p.product_id,
    p.product_name,
    g.market,
    d.year,
    SUM(f.quantity) AS total_quantity,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(AVG(f.discount), 4) AS avg_discount,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_date d ON f.order_date_key = d.date_key
GROUP BY p.category, p.sub_category, p.product_id, p.product_name, g.market, d.year;

CREATE INDEX IF NOT EXISTS idx_mv_prod_mart_cat ON gold.mv_product_mart(category, sub_category);

-- 3. Customer RFM Mart
CREATE MATERIALIZED VIEW IF NOT EXISTS gold.mv_customer_mart AS
WITH customer_summary AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment,
        MAX(d.full_date) AS last_order_date,
        COUNT(DISTINCT f.order_id) AS frequency,
        ROUND(SUM(f.sales), 2) AS monetary,
        ROUND(SUM(f.profit), 2) AS total_profit
    FROM gold.fact_sales f
    JOIN gold.dim_customer c ON f.customer_key = c.customer_key
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    GROUP BY c.customer_id, c.customer_name, c.segment
)
SELECT 
    customer_id,
    customer_name,
    segment,
    last_order_date,
    ('2015-01-01'::DATE - last_order_date) AS recency_days,
    frequency,
    monetary,
    total_profit,
    ROUND(monetary / NULLIF(frequency, 0), 2) AS avg_order_value
FROM customer_summary;

CREATE INDEX IF NOT EXISTS idx_mv_cust_mart_id ON gold.mv_customer_mart(customer_id);
