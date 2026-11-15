WITH segments AS (
    SELECT 'Thị trường' AS kind,
           CONCAT(g.market, ' / ', g.country) AS segment,
           COUNT(DISTINCT f.order_id) AS orders,
           ROUND(SUM(f.sales), 2) AS sales,
           ROUND(SUM(f.profit), 2) AS profit
    FROM gold.fact_sales f
    JOIN gold.dim_geography g ON f.geography_key = g.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:market IS NULL OR g.market = :market)
      AND (:region IS NULL OR g.region = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY g.market, g.country
    HAVING COUNT(DISTINCT f.order_id) >= 3 AND SUM(f.profit) < 0
    UNION ALL
    SELECT 'Ngành hàng con' AS kind,
           CONCAT(p.category, ' / ', p.sub_category) AS segment,
           COUNT(DISTINCT f.order_id) AS orders,
           ROUND(SUM(f.sales), 2) AS sales,
           ROUND(SUM(f.profit), 2) AS profit
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON f.product_key = p.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:market IS NULL OR g.market = :market)
      AND (:region IS NULL OR g.region = :region)
      AND (:country IS NULL OR g.country = :country)
    GROUP BY p.category, p.sub_category
    HAVING COUNT(DISTINCT f.order_id) >= 3 AND SUM(f.profit) < 0
)
SELECT * FROM segments ORDER BY profit ASC LIMIT 5;
