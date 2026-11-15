-- Cross-tab by quarter for one selected year; supplementary OLAP example.
SELECT p.sub_category,
       COALESCE(SUM(f.sales) FILTER (WHERE d.quarter = 1), 0) AS q1_sales,
       COALESCE(SUM(f.sales) FILTER (WHERE d.quarter = 2), 0) AS q2_sales,
       COALESCE(SUM(f.sales) FILTER (WHERE d.quarter = 3), 0) AS q3_sales,
       COALESCE(SUM(f.sales) FILTER (WHERE d.quarter = 4), 0) AS q4_sales,
       SUM(f.sales) AS total_year_sales
FROM gold.fact_sales f
JOIN gold.dim_date d ON d.date_key = f.order_date_key
JOIN gold.dim_product p ON p.product_key = f.product_key
JOIN gold.dim_geography g ON g.geography_key = f.geography_key
WHERE f.order_date_key BETWEEN :start_key AND :end_key
  AND d.year = :year
  AND (:market IS NULL OR g.market = :market)
  AND (:region IS NULL OR g.region = :region)
  AND (:country IS NULL OR g.country = :country)
GROUP BY p.sub_category
ORDER BY total_year_sales DESC
