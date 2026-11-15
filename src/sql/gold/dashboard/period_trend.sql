SELECT CAST(date_trunc(:grain, d.full_date) AS date) AS period,
           COUNT(DISTINCT f.order_id) AS order_count,
           ROUND(SUM(f.sales), 2) AS sales,
           ROUND(SUM(f.profit), 2) AS profit
    FROM gold.fact_sales f
    JOIN gold.dim_date d ON f.order_date_key = d.date_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key

AND (:market IS NULL OR g.market = :market)
AND (:region IS NULL OR g.region = :region)
AND (:country IS NULL OR g.country = :country)

    GROUP BY 1 ORDER BY 1
