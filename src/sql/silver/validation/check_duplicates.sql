-- Validation: Check for duplicate row_id in silver.orders
SELECT 
    row_id,
    COUNT(*) AS count_occurrences
FROM silver.orders
GROUP BY row_id
HAVING COUNT(*) > 1;
