-- Validation: Check that fact_sales preserves the defined grain of 1 row per source row_id
SELECT 
    row_id,
    COUNT(*) AS count_occurrences
FROM gold.fact_sales
GROUP BY row_id
HAVING COUNT(*) > 1;
