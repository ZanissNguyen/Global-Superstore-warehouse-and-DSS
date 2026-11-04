-- =============================================================================
-- Load: gold.dim_date
-- Responsibility: Generate continuous calendar days from 2011 to 2018
-- =============================================================================

INSERT INTO gold.dim_date (
    date_key,
    full_date,
    day_of_week,
    day_name,
    day_of_month,
    day_of_year,
    week_of_year,
    month,
    month_name,
    quarter,
    year,
    year_month,
    is_weekend
)
SELECT 
    CAST(TO_CHAR(datum, 'YYYYMMDD') AS INTEGER) AS date_key,
    datum AS full_date,
    EXTRACT(ISODOW FROM datum)::INTEGER AS day_of_week,
    TO_CHAR(datum, 'TMDay') AS day_name,
    EXTRACT(DAY FROM datum)::INTEGER AS day_of_month,
    EXTRACT(DOY FROM datum)::INTEGER AS day_of_year,
    EXTRACT(WEEK FROM datum)::INTEGER AS week_of_year,
    EXTRACT(MONTH FROM datum)::INTEGER AS month,
    TO_CHAR(datum, 'TMMonth') AS month_name,
    EXTRACT(QUARTER FROM datum)::INTEGER AS quarter,
    EXTRACT(YEAR FROM datum)::INTEGER AS year,
    TO_CHAR(datum, 'YYYY-MM') AS year_month,
    CASE WHEN EXTRACT(ISODOW FROM datum) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series('2011-01-01'::DATE, '2018-12-31'::DATE, '1 day'::INTERVAL) AS datum
ON CONFLICT (date_key) DO NOTHING;
