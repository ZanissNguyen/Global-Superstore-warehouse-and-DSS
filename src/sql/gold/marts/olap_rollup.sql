-- ROLLUP of the selected order-date range and geographic scope.
SELECT d.year, d.quarter, g.market, g.country,
       GROUPING(d.year) AS year_total, GROUPING(d.quarter) AS quarter_total,
       GROUPING(g.market) AS market_total, GROUPING(g.country) AS country_total,
       COUNT(DISTINCT f.order_id) AS total_orders,
       SUM(f.sales) AS total_sales, SUM(f.profit) AS total_profit,
       SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100 AS profit_margin_pct
FROM gold.fact_sales f
JOIN gold.dim_date d ON d.date_key = f.order_date_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND (:market IS NULL OR g.market = :market)
  AND (:region IS NULL OR g.region = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY ROLLUP (d.year, d.quarter, g.market, g.country)
ORDER BY d.year NULLS FIRST, d.quarter NULLS FIRST,
         g.market NULLS FIRST, g.country NULLS FIRST
