CREATE TABLE IF NOT EXISTS public.demo_job (
    job_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    step TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)
