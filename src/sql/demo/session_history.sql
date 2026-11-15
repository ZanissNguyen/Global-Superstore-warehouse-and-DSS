SELECT s.session_id, s.activated_at, s.ingestion_id, s.active,
       s.forecast_3_id, s.forecast_6_id, s.association_run_id
FROM public.demo_session s ORDER BY s.activated_at DESC LIMIT 10
