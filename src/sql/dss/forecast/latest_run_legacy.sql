SELECT run_id, model_name, train_end AS data_end,
       mae, rmse, mape, wmape, created_at
FROM dss.forecast_run
WHERE target_metric='sales' AND horizon_months=:horizon AND model_name IN ('Seasonal naive', 'Holt-Winters additive')
ORDER BY run_id DESC LIMIT 1
