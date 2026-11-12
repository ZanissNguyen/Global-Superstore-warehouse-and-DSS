SELECT p.category AS category,
           SUM(f.quantity) AS quantity,
           ROUND(SUM(f.sales), 2) AS sales,
           ROUND(SUM(f.profit), 2) AS profit,
           ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS margin_pct
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key

AND (:market IS NULL OR g.market = :market)
AND (:region IS NULL OR g.region = :region)
AND (:country IS NULL OR g.country = :country)

    GROUP BY p.category ORDER BY sales DESC
