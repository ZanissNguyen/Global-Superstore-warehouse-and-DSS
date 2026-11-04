-- =============================================================================
-- Load: gold.dim_product
-- Responsibility: Populate unique products from silver.orders (SCD Type 1)
-- =============================================================================

INSERT INTO gold.dim_product (product_id, product_name, category, sub_category)
SELECT DISTINCT ON (product_id)
    product_id,
    product_name,
    category,
    sub_category
FROM silver.orders
ORDER BY product_id, order_date DESC
ON CONFLICT (product_id) DO UPDATE
SET 
    product_name = EXCLUDED.product_name,
    category = EXCLUDED.category,
    sub_category = EXCLUDED.sub_category;
