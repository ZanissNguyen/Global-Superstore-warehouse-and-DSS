-- =============================================================================
-- Dimension: gold.dim_ship_mode
-- Responsibility: Logistics delivery modes
-- =============================================================================

CREATE TABLE IF NOT EXISTS gold.dim_ship_mode (
    ship_mode_key SERIAL PRIMARY KEY,
    ship_mode_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_dim_ship_mode_name ON gold.dim_ship_mode(ship_mode_name);
