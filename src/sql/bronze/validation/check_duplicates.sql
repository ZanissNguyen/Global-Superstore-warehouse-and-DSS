SELECT EXISTS (
    SELECT 1
    FROM bronze.ingestion
    WHERE content_hash = :content_hash
)