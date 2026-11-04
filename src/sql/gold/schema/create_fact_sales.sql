-- =============================================================================
-- Fact Table: gold.fact_sales
-- Responsibility: Central Star Schema fact table
-- Grain: One line item of an order (Row ID)
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    order_date_key INTEGER NOT NULL REFERENCES gold.dim_date(date_key),
    ship_date_key INTEGER NOT NULL REFERENCES gold.dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES gold.dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES gold.dim_product(product_key),
    geography_key INTEGER NOT NULL REFERENCES gold.dim_geography(geography_key),
    ship_mode_key INTEGER NOT NULL REFERENCES gold.dim_ship_mode(ship_mode_key),
    
    -- Degenerate Dimensions
    order_id VARCHAR(50) NOT NULL,
    row_id VARCHAR(50) NOT NULL UNIQUE,
    order_priority VARCHAR(20) NOT NULL,
    is_returned BOOLEAN NOT NULL DEFAULT FALSE,

    -- Additive Measures
    sales NUMERIC(12, 4) NOT NULL,
    quantity INTEGER NOT NULL,
    discount NUMERIC(5, 4) NOT NULL,
    profit NUMERIC(12, 4) NOT NULL,
    shipping_cost NUMERIC(12, 4) NOT NULL,
    
    -- Calculated Measure
    shipping_days INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Foreign Key Indexes for fast join performance
CREATE INDEX IF NOT EXISTS idx_fact_sales_order_date ON gold.fact_sales(order_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_ship_date ON gold.fact_sales(ship_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer ON gold.fact_sales(customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON gold.fact_sales(product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_geography ON gold.fact_sales(geography_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_ship_mode ON gold.fact_sales(ship_mode_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_order_id ON gold.fact_sales(order_id);
