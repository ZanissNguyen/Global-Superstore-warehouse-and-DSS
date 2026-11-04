-- =============================================================================
-- OLAP Operation: ROLL-UP
-- Aggregates sales and profit from Month -> Quarter -> Year
-- and from Country -> Market
-- =============================================================================

SELECT 
    d.year,
    d.quarter,
    g.market,
    g.country,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
GROUP BY ROLLUP (d.year, d.quarter, g.market, g.country)
ORDER BY d.year NULLS FIRST, d.quarter NULLS FIRST, g.market NULLS FIRST;
