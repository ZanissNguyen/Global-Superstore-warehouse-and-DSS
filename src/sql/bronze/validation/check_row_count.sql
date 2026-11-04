-- Validation: Check row counts in all bronze tables
SELECT 
    'bronze.ingestion' AS table_name, 
    COUNT(*) AS row_count 
FROM bronze.ingestion

UNION ALL

SELECT 
    'bronze.raw_orders' AS table_name, 
    COUNT(*) AS row_count 
FROM bronze.raw_orders

UNION ALL

SELECT 
    'bronze.market' AS table_name, 
    COUNT(*) AS row_count 
FROM bronze.market

UNION ALL

SELECT 
    'bronze.postal_code' AS table_name, 
    COUNT(*) AS row_count 
FROM bronze.postal_code;
