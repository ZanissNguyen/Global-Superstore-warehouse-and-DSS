ALTER TABLE dss.forecast_run ADD COLUMN IF NOT EXISTS horizon_months INTEGER;
ALTER TABLE dss.forecast_run ADD COLUMN IF NOT EXISTS wmape NUMERIC(10, 4);
ALTER TABLE dss.forecast_run ADD COLUMN IF NOT EXISTS model_params JSONB;
ALTER TABLE dss.forecast_run ADD COLUMN IF NOT EXISTS history_end DATE;
