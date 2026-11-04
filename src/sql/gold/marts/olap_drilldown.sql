-- =============================================================================
-- OLAP Operation: DRILL-DOWN
-- Drills down from Category ('Technology') -> Sub-Category -> Individual Product SKU
-- to identify loss-making items
-- =============================================================================

SELECT 
    p.category,
    p.sub_category,
    p.product_id,
    p.product_name,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND(AVG(f.discount) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE p.category = 'Technology'
GROUP BY p.category, p.sub_category, p.product_id, p.product_name
ORDER BY total_profit ASC
LIMIT 20;
