-- All subtotals across year, category and market; supplementary OLAP example.
SELECT d.year, p.category, g.market,
       GROUPING(d.year) AS year_total, GROUPING(p.category) AS category_total,
       GROUPING(g.market) AS market_total,
       SUM(f.sales) AS sales, SUM(f.profit) AS profit
FROM gold.fact_sales f
JOIN gold.dim_date d ON d.date_key = f.order_date_key
JOIN gold.dim_product p ON p.product_key = f.product_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region IS NULL OR g.region = :region)
  AND (:country IS NULL OR g.country = :country)
  AND (:category IS NULL OR p.category = :category)
GROUP BY CUBE (d.year, p.category, g.market)
ORDER BY d.year NULLS FIRST, p.category NULLS FIRST, g.market NULLS FIRST
