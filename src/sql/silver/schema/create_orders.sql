-- =============================================================================
-- Schema & Table: silver.orders
-- Responsibility: Create cleaned and standardized orders table
-- Grain: 1 source order line item (Row ID)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.orders (
    row_id INTEGER PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL DEFAULT 'Unknown',
    market VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    regional_manager VARCHAR(100),
    product_id VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    sales NUMERIC(12, 4) NOT NULL,
    quantity INTEGER NOT NULL,
    discount NUMERIC(5, 4) NOT NULL,
    profit NUMERIC(12, 4) NOT NULL,
    shipping_cost NUMERIC(12, 4) NOT NULL,
    order_priority VARCHAR(20) NOT NULL,
    is_returned BOOLEAN NOT NULL DEFAULT FALSE,
    ingestion_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_silver_sales CHECK (sales >= 0),
    CONSTRAINT chk_silver_quantity CHECK (quantity > 0),
    CONSTRAINT chk_silver_discount CHECK (discount >= 0 AND discount <= 1.0),
    CONSTRAINT chk_silver_dates CHECK (ship_date >= order_date)
);

CREATE INDEX IF NOT EXISTS idx_silver_orders_order_id ON silver.orders(order_id);
CREATE INDEX IF NOT EXISTS idx_silver_orders_customer_id ON silver.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_silver_orders_product_id ON silver.orders(product_id);
CREATE INDEX IF NOT EXISTS idx_silver_orders_dates ON silver.orders(order_date, ship_date);
