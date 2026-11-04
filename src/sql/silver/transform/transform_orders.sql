-- =============================================================================
-- Transform & Load: bronze.raw_orders -> silver.orders
-- Responsibility: Normalize data types, parse mixed dates, impute postal codes,
--                 and resolve returns/manager mappings.
-- =============================================================================

INSERT INTO silver.orders (
    row_id,
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    customer_name,
    segment,
    city,
    state,
    country,
    postal_code,
    market,
    region,
    regional_manager,
    product_id,
    category,
    sub_category,
    product_name,
    sales,
    quantity,
    discount,
    profit,
    shipping_cost,
    order_priority,
    is_returned,
    ingestion_id
)
SELECT 
    CAST(TRIM(r."Row ID") AS INTEGER) AS row_id,
    TRIM(r."Order ID") AS order_id,
    -- Parse mixed date format (handle both d/m/Y and d-m-Y)
    CASE 
        WHEN r."Order Date" ~ '^\d{1,2}/\d{1,2}/\d{4}$' THEN TO_DATE(r."Order Date", 'DD/MM/YYYY')
        WHEN r."Order Date" ~ '^\d{1,2}-\d{1,2}-\d{4}$' THEN TO_DATE(r."Order Date", 'DD-MM-YYYY')
        WHEN r."Order Date" ~ '^\d{4}-\d{1,2}-\d{1,2}$' THEN TO_DATE(r."Order Date", 'YYYY-MM-DD')
        ELSE TO_DATE(r."Order Date", 'DD/MM/YYYY')
    END AS order_date,
    CASE 
        WHEN r."Ship Date" ~ '^\d{1,2}/\d{1,2}/\d{4}$' THEN TO_DATE(r."Ship Date", 'DD/MM/YYYY')
        WHEN r."Ship Date" ~ '^\d{1,2}-\d{1,2}-\d{4}$' THEN TO_DATE(r."Ship Date", 'DD-MM-YYYY')
        WHEN r."Ship Date" ~ '^\d{4}-\d{1,2}-\d{1,2}$' THEN TO_DATE(r."Ship Date", 'YYYY-MM-DD')
        ELSE TO_DATE(r."Ship Date", 'DD/MM/YYYY')
    END AS ship_date,
    TRIM(r."Ship Mode") AS ship_mode,
    TRIM(r."Customer ID") AS customer_id,
    TRIM(r."Customer Name") AS customer_name,
    TRIM(r."Segment") AS segment,
    TRIM(r."City") AS city,
    TRIM(r."State") AS state,
    TRIM(r."Country") AS country,
    COALESCE(NULLIF(TRIM(r."Postal Code"), ''), 'Unknown') AS postal_code,
    TRIM(r."Market") AS market,
    TRIM(r."Region") AS region,
    NULL AS regional_manager, -- populated via enrichment or join
    TRIM(r."Product ID") AS product_id,
    TRIM(r."Category") AS category,
    TRIM(r."Sub-Category") AS sub_category,
    TRIM(r."Product Name") AS product_name,
    CAST(TRIM(r."Sales") AS NUMERIC(12, 4)) AS sales,
    CAST(TRIM(r."Quantity") AS INTEGER) AS quantity,
    CAST(TRIM(r."Discount") AS NUMERIC(5, 4)) AS discount,
    CAST(TRIM(r."Profit") AS NUMERIC(12, 4)) AS profit,
    CAST(COALESCE(NULLIF(TRIM(r."Shipping Cost"), ''), '0') AS NUMERIC(12, 4)) AS shipping_cost,
    COALESCE(NULLIF(TRIM(r."Order Priority"), ''), 'Medium') AS order_priority,
    FALSE AS is_returned,
    r.ingestion AS ingestion_id
FROM bronze.raw_orders r
WHERE r.transform = FALSE
ON CONFLICT (row_id) DO NOTHING;

-- Mark transformed rows in bronze
UPDATE bronze.raw_orders
SET transform = TRUE
WHERE transform = FALSE;
