-- =============================================================================
-- OLAP Operation: PIVOT (Cross-Tabulation)
-- Rotates Quarters (Q1-Q4) into columns for sub-category comparison in 2014
-- =============================================================================

SELECT 
    p.sub_category,
    ROUND(SUM(CASE WHEN d.quarter = 1 THEN f.sales ELSE 0 END), 2) AS q1_sales,
    ROUND(SUM(CASE WHEN d.quarter = 2 THEN f.sales ELSE 0 END), 2) AS q2_sales,
    ROUND(SUM(CASE WHEN d.quarter = 3 THEN f.sales ELSE 0 END), 2) AS q3_sales,
    ROUND(SUM(CASE WHEN d.quarter = 4 THEN f.sales ELSE 0 END), 2) AS q4_sales,
    ROUND(SUM(f.sales), 2) AS total_year_sales
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE d.year = 2014
GROUP BY p.sub_category
ORDER BY total_year_sales DESC;
