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
SELECT DISTINCT ON (country, state, city, postal_code, market, region)
    country,
    state,
    city,
    postal_code,
    market,
    region,
    regional_manager
FROM silver.orders
ORDER BY country, state, city, postal_code, market, region, regional_manager NULLS LAST
ON CONFLICT (country, state, city, postal_code, market, region) DO UPDATE
SET 
    regional_manager = COALESCE(EXCLUDED.regional_manager, gold.dim_geography.regional_manager);
