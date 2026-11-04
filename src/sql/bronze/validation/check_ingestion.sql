-- Validation: Check latest ingestion logs in bronze.ingestion
SELECT 
    id,
    source_name,
    content_hash,
    loaded_time,
    metadata
FROM bronze.ingestion
ORDER BY id DESC
LIMIT 10;
