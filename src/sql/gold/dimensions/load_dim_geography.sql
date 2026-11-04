-- =============================================================================
-- Load: gold.dim_geography
-- Responsibility: Populate unique geographic locations from silver.orders
-- =============================================================================

INSERT INTO gold.dim_geography (
    country,
    state,
    city,
    postal_code,
    market,
    region,
    regional_manager
)
SELECT DISTINCT
    country,
    state,
    city,
    postal_code,
    market,
    region,
    regional_manager
FROM silver.orders
ON CONFLICT (country, state, city, postal_code) DO UPDATE
SET 
    market = EXCLUDED.market,
    region = EXCLUDED.region,
    regional_manager = COALESCE(EXCLUDED.regional_manager, gold.dim_geography.regional_manager);
