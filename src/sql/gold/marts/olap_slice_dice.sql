-- =============================================================================
-- OLAP Operation: SLICE & DICE
-- Part 1: SLICE fixing Market = 'APAC' and Year = 2014
-- Part 2: DICE multi-dimensional subcube: Market in ('APAC', 'EU'), Category in ('Furniture', 'Technology')
-- =============================================================================

-- 1. SLICE
SELECT 
    d.month_name,
    p.category,
    ROUND(SUM(f.sales), 2) AS apac_sales,
    ROUND(SUM(f.profit), 2) AS apac_profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE g.market = 'APAC' AND d.year = 2014
GROUP BY d.month, d.month_name, p.category
ORDER BY d.month, p.category;

-- 2. DICE
SELECT 
    g.market,
    p.category,
    d.quarter,
    ROUND(SUM(f.sales), 2) AS diced_sales,
    ROUND(SUM(f.profit), 2) AS diced_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE g.market IN ('APAC', 'EU')
  AND p.category IN ('Furniture', 'Technology')
  AND d.year = 2014
  AND d.quarter IN (3, 4)
GROUP BY g.market, p.category, d.quarter
ORDER BY g.market, p.category, d.quarter;
