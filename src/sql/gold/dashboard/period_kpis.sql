SELECT COUNT(*) AS line_count,
           COUNT(DISTINCT order_id) AS order_count,
           COALESCE(SUM(sales), 0) AS sales,
           COALESCE(SUM(profit), 0) AS profit,
           COALESCE(AVG(discount), 0) AS avg_discount
    FROM gold.fact_sales f
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key

AND (:market IS NULL OR g.market = :market)
AND (:region IS NULL OR g.region = :region)
AND (:country IS NULL OR g.country = :country)
