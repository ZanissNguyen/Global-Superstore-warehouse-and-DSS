SELECT g.region AS area,
           COUNT(DISTINCT f.order_id) AS orders,
           SUM(f.sales)::float AS sales,
           SUM(f.profit)::float AS profit,
           (SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100)::float AS margin_pct
    FROM gold.fact_sales f
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key

AND (:market IS NULL OR g.market = :market)
AND (:region IS NULL OR g.region = :region)
AND (:country IS NULL OR g.country = :country)

    GROUP BY g.region ORDER BY sales DESC
