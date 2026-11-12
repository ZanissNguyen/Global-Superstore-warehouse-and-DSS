SELECT 
    COALESCE(SUM(f.sales), 0) AS total_sales,
    COALESCE(SUM(f.profit), 0) AS total_profit,
    COALESCE(AVG(f.discount), 0) AS avg_discount
FROM gold.fact_sales f
JOIN gold.dim_geography g ON f.geography_key = g.geography_key
JOIN gold.dim_product p ON f.product_key = p.product_key
WHERE (:market IS NULL OR g.market = :market)
  AND (:category IS NULL OR p.category = :category);
