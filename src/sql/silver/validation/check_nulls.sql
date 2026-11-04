-- Validation: Check for unexpected NULL values in mandatory columns of silver.orders
SELECT 
    COUNT(*) AS total_rows,
    COUNT(CASE WHEN row_id IS NULL THEN 1 END) AS null_row_id,
    COUNT(CASE WHEN order_id IS NULL THEN 1 END) AS null_order_id,
    COUNT(CASE WHEN order_date IS NULL THEN 1 END) AS null_order_date,
    COUNT(CASE WHEN ship_date IS NULL THEN 1 END) AS null_ship_date,
    COUNT(CASE WHEN customer_id IS NULL THEN 1 END) AS null_customer_id,
    COUNT(CASE WHEN product_id IS NULL THEN 1 END) AS null_product_id,
    COUNT(CASE WHEN sales IS NULL THEN 1 END) AS null_sales,
    COUNT(CASE WHEN quantity IS NULL THEN 1 END) AS null_quantity
FROM silver.orders;
