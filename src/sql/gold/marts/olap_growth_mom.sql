-- =============================================================================
-- OLAP Operation: WINDOW FUNCTION (Month-over-Month Sales Growth Rate)
-- Uses LAG() window function
-- =============================================================================

WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        d.year_month,
        SUM(f.sales) AS current_sales
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    GROUP BY d.year, d.month, d.year_month
)
SELECT 
    year_month,
    ROUND(current_sales, 2) AS sales,
    ROUND(LAG(current_sales, 1) OVER (ORDER BY year, month), 2) AS prev_month_sales,
    ROUND(
        (current_sales - LAG(current_sales, 1) OVER (ORDER BY year, month)) 
        / NULLIF(LAG(current_sales, 1) OVER (ORDER BY year, month), 0) * 100, 
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY year, month;
