SELECT DISTINCT
    f.order_id,
    p.product_name AS item_name
FROM gold.fact_sales f
JOIN gold.dim_product p ON f.product_key = p.product_key
ORDER BY f.order_id;
