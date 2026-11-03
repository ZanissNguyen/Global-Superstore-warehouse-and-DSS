INSERT INTO bronze.ingestion (
        source_name,
        content_hash,
        loaded_time,
        metadata
    )
    VALUES (
        :source_name,
        :content_hash,
        :loaded_time,
        :metadata
    )
    RETURNING id;