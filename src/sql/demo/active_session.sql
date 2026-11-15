SELECT session_id, database_name, ingestion_id, forecast_3_id,
       forecast_6_id, association_run_id, activated_at,
       metrics_before, metrics_after
FROM public.demo_session WHERE active ORDER BY activated_at DESC LIMIT 1
