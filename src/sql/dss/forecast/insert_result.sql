INSERT INTO dss.forecast_result
    (run_id, forecast_date, series_key, predicted_value, lower_bound, upper_bound)
VALUES (:run_id, :dt, 'TOTAL', :pred, :low, :high)
