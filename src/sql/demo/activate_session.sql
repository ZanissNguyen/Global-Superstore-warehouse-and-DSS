INSERT INTO public.demo_session
    (session_id, database_name, source_hash, ingestion_id,
     forecast_3_id, forecast_6_id, association_run_id,
     metrics_before, metrics_after, active)
VALUES (:session, :database, :hash, :ingestion, :f3, :f6, :rule,
        CAST(:before AS JSONB), CAST(:after AS JSONB), TRUE)
