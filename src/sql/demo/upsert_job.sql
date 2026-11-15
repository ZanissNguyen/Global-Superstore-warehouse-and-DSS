INSERT INTO public.demo_job(job_id, session_id, step, status, message)
VALUES (:job, :session, :step, :status, :message)
ON CONFLICT(job_id) DO UPDATE SET step = EXCLUDED.step,
    status = EXCLUDED.status, message = EXCLUDED.message,
    updated_at = CURRENT_TIMESTAMP
