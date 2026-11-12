-- Month-over-month growth; selected range may contain partial months.
WITH monthly_sales AS (
    SELECT date_trunc('month', d.full_date)::date AS month_start,
           SUM(f.sales) AS sales
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON d.date_key = f.order_date_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:market IS NULL OR g.market = :market)
      AND (:region IS NULL OR g.region = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY 1
), growth AS (
    SELECT month_start, sales,
           LAG(sales) OVER (ORDER BY month_start) AS previous_sales
    FROM monthly_sales
)
SELECT month_start, sales, previous_sales,
       (sales - previous_sales) / NULLIF(previous_sales, 0) * 100 AS mom_growth_pct
FROM growth
ORDER BY month_start
