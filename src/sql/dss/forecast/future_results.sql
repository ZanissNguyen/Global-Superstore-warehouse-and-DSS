SELECT forecast_date, predicted_value, lower_bound, upper_bound
FROM dss.forecast_result WHERE run_id=:run_id AND actual_value IS NULL
ORDER BY forecast_date LIMIT :horizon
