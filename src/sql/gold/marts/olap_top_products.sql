-- Top N within each category. The UI uses global Top N in dashboard SQL.
WITH products AS (
    SELECT p.category, p.product_id, p.product_name,
           SUM(f.quantity) AS quantity, SUM(f.sales) AS sales,
           SUM(f.profit) AS profit
    FROM gold.fact_sales f
    JOIN gold.dim_product p ON p.product_key = f.product_key
    JOIN gold.dim_geography g ON g.geography_key = f.geography_key
    WHERE f.order_date_key BETWEEN :start_key AND :end_key
      AND (:market IS NULL OR g.market = :market)
      AND (:region IS NULL OR g.region = :region)
      AND (:country IS NULL OR g.country = :country)
      AND (:category IS NULL OR p.category = :category)
    GROUP BY p.category, p.product_id, p.product_name
), ranked AS (
    SELECT products.*,
           ROW_NUMBER() OVER (
               PARTITION BY category
               ORDER BY CASE WHEN :metric = 'quantity' THEN quantity ELSE sales END DESC,
                        product_name, product_id
           ) AS product_rank,
           SUM(CASE WHEN :metric = 'quantity' THEN quantity ELSE sales END)
               OVER (PARTITION BY category) AS category_total
    FROM products
)
SELECT category, product_rank, product_id, product_name, quantity, sales, profit,
       CASE WHEN :metric = 'quantity' THEN quantity ELSE sales END
           / NULLIF(category_total, 0) * 100 AS share_pct
FROM ranked
WHERE product_rank <= :top_n
ORDER BY category, product_rank
