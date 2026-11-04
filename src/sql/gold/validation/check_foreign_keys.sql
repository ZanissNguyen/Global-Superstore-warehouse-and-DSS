-- Validation: Check for orphan foreign keys in gold.fact_sales
SELECT 
    COUNT(CASE WHEN order_date_key IS NULL THEN 1 END) AS orphan_order_date,
    COUNT(CASE WHEN ship_date_key IS NULL THEN 1 END) AS orphan_ship_date,
    COUNT(CASE WHEN customer_key IS NULL THEN 1 END) AS orphan_customer,
    COUNT(CASE WHEN product_key IS NULL THEN 1 END) AS orphan_product,
    COUNT(CASE WHEN geography_key IS NULL THEN 1 END) AS orphan_geography,
    COUNT(CASE WHEN ship_mode_key IS NULL THEN 1 END) AS orphan_ship_mode
FROM gold.fact_sales;
