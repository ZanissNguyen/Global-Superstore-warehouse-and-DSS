-- =============================================================================
-- Dimension: gold.dim_customer
-- Responsibility: Customer profile and segmentation (SCD Type 1)
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE, -- Natural Key
    customer_name VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL,            -- Consumer / Corporate / Home Office
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_customer_id ON gold.dim_customer(customer_id);
CREATE INDEX IF NOT EXISTS idx_dim_customer_segment ON gold.dim_customer(segment);
