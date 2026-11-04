-- =============================================================================
-- Dimension: gold.dim_product
-- Responsibility: Product catalog and hierarchy (Category -> Sub-Category -> Product)
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,  -- Natural Key
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,           -- Furniture / Office Supplies / Technology
    sub_category VARCHAR(50) NOT NULL,       -- 17 Sub-categories
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_product_id ON gold.dim_product(product_id);
CREATE INDEX IF NOT EXISTS idx_dim_product_cat ON gold.dim_product(category, sub_category);
