-- =============================================================================
-- Dimension: gold.dim_geography
-- Responsibility: Geographic hierarchy (Market -> Region -> Country -> State -> City)
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.dim_geography (
    geography_key SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL DEFAULT 'Unknown',
    market VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    regional_manager VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dim_geography UNIQUE (country, state, city, postal_code)
);

CREATE INDEX IF NOT EXISTS idx_dim_geo_market_region ON gold.dim_geography(market, region);
CREATE INDEX IF NOT EXISTS idx_dim_geo_country ON gold.dim_geography(country);
