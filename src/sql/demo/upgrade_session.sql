ALTER TABLE public.demo_session
    ADD COLUMN IF NOT EXISTS metrics_before JSONB;
ALTER TABLE public.demo_session
    ADD COLUMN IF NOT EXISTS metrics_after JSONB;
