SELECT 
    d.year AS "Năm",
    COUNT(f.sales) AS "Số dòng đơn hàng",
    ROUND(SUM(f.sales), 2) AS "Doanh thu ($)",
    ROUND(SUM(f.profit), 2) AS "Lợi nhuận ($)",
    ROUND(AVG(f.discount) * 100, 2) AS "Chiết khấu BQ (%)"
FROM gold.fact_sales f
JOIN gold.dim_date d ON f.order_date_key = d.date_key
GROUP BY d.year
ORDER BY d.year;
