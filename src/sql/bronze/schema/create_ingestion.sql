CREATE TABLE IF NOT EXISTS bronze.ingestion (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    loaded_time TIMESTAMP NOT NULL,
    metadata JSONB
);