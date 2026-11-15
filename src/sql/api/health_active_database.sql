SELECT database_name
FROM public.demo_session
WHERE active
ORDER BY activated_at DESC
LIMIT 1
