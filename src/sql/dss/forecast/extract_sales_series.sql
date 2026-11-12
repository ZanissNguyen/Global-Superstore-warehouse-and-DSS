SELECT date_trunc('month', d.full_date)::date AS month_date,
       MAX(d.full_date) AS last_order_date,
       SUM(f.sales)::float AS total_sales,
       SUM(f.quantity)::float AS total_quantity
FROM gold.fact_sales f
JOIN gold.dim_date d ON d.date_key = f.order_date_key
GROUP BY 1 ORDER BY 1
