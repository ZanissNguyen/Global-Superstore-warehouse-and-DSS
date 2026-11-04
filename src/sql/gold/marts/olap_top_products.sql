-- =============================================================================
-- OLAP Operation: WINDOW FUNCTION (DENSE_RANK Top 5 Products per Category)
-- =============================================================================

WITH ranked_products AS (
    SELECT 
        p.category,
        p.product_name,
        ROUND(SUM(f.sales), 2) AS total_sales,
        ROUND(SUM(f.profit), 2) AS total_profit,
        DENSE_RANK() OVER (
            PARTITION BY p.category 
            ORDER BY SUM(f.sales) DESC
        ) AS sales_rank
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    sales_rank,
    product_name,
    total_sales,
    total_profit
FROM ranked_products
WHERE sales_rank <= 5
ORDER BY category, sales_rank;
