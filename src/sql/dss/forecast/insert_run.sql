INSERT INTO dss.forecast_run
    (model_name, target_metric, series_key, train_start, train_end,
     test_start, test_end, mae, rmse, mape, horizon_months, wmape, model_params,
     history_end)
VALUES (:model, :target, 'TOTAL', :train_start, :train_end,
        :test_start, :test_end, :mae, :rmse, :mape, :horizon, :wmape,
        CAST(:params AS JSONB), :history_end) RETURNING run_id
