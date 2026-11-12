SELECT MIN(d.full_date) AS first_date, MAX(d.full_date) AS last_date
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key;
