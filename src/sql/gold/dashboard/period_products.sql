SELECT p.product_id, p.product_name,
           SUM(f.quantity) AS quantity,
           ROUND(SUM(f.sales), 2) AS sales
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:category IS NULL OR p.category = :category)

AND (:market IS NULL OR g.market = :market)
AND (:region IS NULL OR g.region = :region)
AND (:country IS NULL OR g.country = :country)

    GROUP BY p.product_id, p.product_name
