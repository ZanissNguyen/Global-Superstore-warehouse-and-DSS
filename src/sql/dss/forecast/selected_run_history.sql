SELECT run_id, model_name, COALESCE(history_end, train_end) AS data_end,
       mae, rmse, mape, wmape, created_at
FROM dss.forecast_run WHERE run_id=:run_id AND target_metric='sales' AND horizon_months=:horizon AND model_name IN ('Seasonal naive', 'Holt-Winters additive')
