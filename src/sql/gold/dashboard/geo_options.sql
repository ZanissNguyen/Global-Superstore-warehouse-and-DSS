SELECT DISTINCT g.market, g.region, g.country
FROM gold.fact_sales f
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
ORDER BY g.market, g.region, g.country
