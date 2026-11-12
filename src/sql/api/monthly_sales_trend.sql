SELECT 
    d.year_month,
    ROUND(SUM(f.sales), 2) AS sales,
    ROUND(SUM(f.profit), 2) AS profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
GROUP BY d.year, d.month, d.year_month
ORDER BY d.year, d.month;
