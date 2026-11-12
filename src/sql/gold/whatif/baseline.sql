SELECT COALESCE(SUM(f.sales), 0) AS sales,
       COALESCE(SUM(f.profit), 0) AS profit,
       COALESCE(AVG(f.discount), 0) AS discount,
       COUNT(*) AS lines
FROM gold.fact_sales f
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
JOIN gold.dim_product p ON p.product_key = f.product_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market = 'Tất cả' OR g.market = :market)
  AND (:category = 'Tất cả' OR p.category = :category)
