-- =============================================================================
-- OLAP Operation: GROUP BY CUBE
-- Generates all 2^N dimensional subtotals for (Year, Category, Market)
-- =============================================================================

SELECT 
    d.year,
    p.category,
    g.market,
    ROUND(SUM(f.sales), 2) AS sales,
    ROUND(SUM(f.profit), 2) AS profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_product p ON f.product_key = p.product_key
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
WHERE d.year IN (2013, 2014) AND g.market IN ('APAC', 'EU')
GROUP BY CUBE (d.year, p.category, g.market)
ORDER BY d.year NULLS FIRST, p.category NULLS FIRST, g.market NULLS FIRST;
