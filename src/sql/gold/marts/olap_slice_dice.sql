-- Slice when market/category are selected, dice across the remaining dimensions.
SELECT g.market, p.category, d.year, d.quarter,
       SUM(f.sales) AS sales, SUM(f.profit) AS profit,
       SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100 AS margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON d.date_key = f.order_date_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
JOIN gold.dim_product p ON p.product_key = f.product_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region IS NULL OR g.region = :region)
  AND (:country IS NULL OR g.country = :country)
  AND (:category IS NULL OR p.category = :category)
GROUP BY g.market, p.category, d.year, d.quarter
ORDER BY d.year, d.quarter, g.market, p.category
