-- =============================================================================
-- Schema & Tables: dss.*
-- Responsibility: Store machine learning, forecasting, and association rule results
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS dss;

-- 1. Metadata for time-series forecasting runs
CREATE TABLE IF NOT EXISTS dss.forecast_run (
    run_id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    target_metric VARCHAR(50) NOT NULL,
    series_key VARCHAR(50) DEFAULT 'TOTAL',
    train_start DATE NOT NULL,
    train_end DATE NOT NULL,
    test_start DATE,
    test_end DATE,
    mae NUMERIC(12, 4),
    rmse NUMERIC(12, 4),
    mape NUMERIC(8, 4),
    horizon_months INTEGER,
    wmape NUMERIC(10, 4),
    model_params JSONB,
    history_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Forecasting point estimates and prediction intervals
CREATE TABLE IF NOT EXISTS dss.forecast_result (
    result_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES dss.forecast_run(run_id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    series_key VARCHAR(50) DEFAULT 'TOTAL',
    actual_value NUMERIC(14, 4),
    predicted_value NUMERIC(14, 4) NOT NULL,
    lower_bound NUMERIC(14, 4),
    upper_bound NUMERIC(14, 4)
);

CREATE INDEX IF NOT EXISTS idx_dss_fc_date ON dss.forecast_result(forecast_date);

-- 3. Metadata for Market Basket / Association Rule runs
CREATE TABLE IF NOT EXISTS dss.association_run (
    run_id SERIAL PRIMARY KEY,
    algorithm VARCHAR(50) NOT NULL,
    min_support NUMERIC(6, 4) NOT NULL,
    min_confidence NUMERIC(6, 4) NOT NULL,
    min_lift NUMERIC(6, 4) NOT NULL,
    transaction_count INTEGER NOT NULL,
    rules_found INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Association rules discovered
CREATE TABLE IF NOT EXISTS dss.association_rule (
    rule_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES dss.association_run(run_id) ON DELETE CASCADE,
    antecedents TEXT NOT NULL,
    consequents TEXT NOT NULL,
    antecedent_names TEXT,
    consequent_names TEXT,
    support NUMERIC(8, 6) NOT NULL,
    confidence NUMERIC(8, 6) NOT NULL,
    lift NUMERIC(8, 4) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_dss_rule_lift ON dss.association_rule(lift DESC);
