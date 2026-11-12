CREATE TABLE IF NOT EXISTS public.demo_session (
    session_id TEXT PRIMARY KEY,
    database_name TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    ingestion_id INTEGER,
    forecast_3_id INTEGER,
    forecast_6_id INTEGER,
    association_run_id INTEGER,
    activated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT FALSE
)
