-- =============================================================================
-- Load: gold.fact_sales
-- Responsibility: Populate Fact table with surrogate keys from Dimensions
-- Grain: One order line item (Row ID)
-- =============================================================================

INSERT INTO gold.fact_sales (
    order_date_key,
    ship_date_key,
    customer_key,
    product_key,
    geography_key,
    ship_mode_key,
    order_id,
    row_id,
    order_priority,
    is_returned,
    sales,
    quantity,
    discount,
    profit,
    shipping_cost,
    shipping_days
)
SELECT 
    CAST(TO_CHAR(s.order_date, 'YYYYMMDD') AS INTEGER) AS order_date_key,
    CAST(TO_CHAR(s.ship_date, 'YYYYMMDD') AS INTEGER) AS ship_date_key,
    c.customer_key,
    p.product_key,
    g.geography_key,
    sm.ship_mode_key,
    s.order_id,
    s.row_id::TEXT,
    s.order_priority,
    s.is_returned,
    s.sales,
    s.quantity,
    s.discount,
    s.profit,
    s.shipping_cost,
    (s.ship_date - s.order_date) AS shipping_days
FROM silver.orders s
JOIN gold.dim_customer c ON s.customer_id = c.customer_id
JOIN gold.dim_product p ON s.product_id = p.product_id
JOIN gold.dim_geography g ON s.country = g.country 
    AND s.state = g.state 
    AND s.city = g.city 
    AND s.postal_code = g.postal_code
    AND s.market = g.market
    AND s.region = g.region
JOIN gold.dim_ship_mode sm ON s.ship_mode = sm.ship_mode_name
ON CONFLICT (row_id) DO NOTHING;
