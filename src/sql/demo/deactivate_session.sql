UPDATE public.demo_session
SET active = FALSE
WHERE session_id = :session_id AND active = TRUE
RETURNING session_id
