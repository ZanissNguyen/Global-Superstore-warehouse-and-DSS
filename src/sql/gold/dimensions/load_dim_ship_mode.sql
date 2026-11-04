-- =============================================================================
-- Load: gold.dim_ship_mode
-- Responsibility: Populate unique shipping modes
-- =============================================================================

INSERT INTO gold.dim_ship_mode (ship_mode_name)
SELECT DISTINCT ship_mode
FROM silver.orders
ON CONFLICT (ship_mode_name) DO NOTHING;
