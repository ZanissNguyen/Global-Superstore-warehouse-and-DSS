SELECT c.segment,
           COUNT(DISTINCT c.customer_id) AS customers,
           COUNT(DISTINCT f.order_id) AS orders,
           SUM(f.sales)::float AS sales,
           SUM(f.profit)::float AS profit,
           (SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100)::float AS margin_pct,
           (SUM(f.sales) / NULLIF(COUNT(DISTINCT f.order_id), 0))::float AS avg_order_value
    FROM gold.fact_sales f
    JOIN gold.dim_customer c ON c.customer_key = f.customer_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key

AND (:market IS NULL OR g.market = :market)
AND (:region IS NULL OR g.region = :region)
AND (:country IS NULL OR g.country = :country)

    GROUP BY c.segment ORDER BY sales DESC
