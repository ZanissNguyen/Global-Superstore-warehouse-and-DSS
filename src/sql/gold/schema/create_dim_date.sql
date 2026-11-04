-- =============================================================================
-- Dimension: gold.dim_date (Role-Playing Dimension)
-- Responsibility: Date dimension covering Order Date and Ship Date
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_key INTEGER PRIMARY KEY,           -- Format: YYYYMMDD (e.g. 20110115)
    full_date DATE NOT NULL UNIQUE,
    day_of_week INTEGER NOT NULL,          -- 1 = Monday, 7 = Sunday
    day_name VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_year INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL,         -- Format: YYYY-MM
    is_weekend BOOLEAN NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_dim_date_year_month ON gold.dim_date(year, month);
CREATE INDEX IF NOT EXISTS idx_dim_date_full_date ON gold.dim_date(full_date);
