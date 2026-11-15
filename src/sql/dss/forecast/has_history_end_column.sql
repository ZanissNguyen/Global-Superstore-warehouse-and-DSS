SELECT COUNT(*) AS n FROM information_schema.columns
WHERE table_schema='dss' AND table_name='forecast_run'
  AND column_name='history_end'
