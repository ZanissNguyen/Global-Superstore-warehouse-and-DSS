-- =============================================================================
-- Load: gold.dim_customer
-- Responsibility: Populate unique customers from silver.orders (SCD Type 1)
-- =============================================================================

INSERT INTO gold.dim_customer (customer_id, customer_name, segment)
SELECT DISTINCT ON (customer_id)
    customer_id,
    customer_name,
    segment
FROM silver.orders
ORDER BY customer_id, order_date DESC
ON CONFLICT (customer_id) DO UPDATE
SET 
    customer_name = EXCLUDED.customer_name,
    segment = EXCLUDED.segment;
