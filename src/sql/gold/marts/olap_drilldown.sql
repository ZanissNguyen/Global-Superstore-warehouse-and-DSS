-- Drill-down of selected category to subcategory and product.
SELECT p.category, p.sub_category, p.product_id, p.product_name,
       SUM(f.quantity) AS total_units_sold, SUM(f.sales) AS total_sales,
       SUM(f.profit) AS total_profit, AVG(f.discount) * 100 AS avg_discount_pct,
       SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100 AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_product p ON p.product_key = f.product_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region IS NULL OR g.region = :region)
  AND (:country IS NULL OR g.country = :country)
  AND (:category IS NULL OR p.category = :category)
GROUP BY p.category, p.sub_category, p.product_id, p.product_name
ORDER BY total_profit ASC, p.product_id
LIMIT :row_limit
