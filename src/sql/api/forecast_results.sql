SELECT 
    forecast_date,
    series_key,
    actual_value,
    predicted_value,
    lower_bound,
    upper_bound
FROM dss.forecast_result
ORDER BY forecast_date;
