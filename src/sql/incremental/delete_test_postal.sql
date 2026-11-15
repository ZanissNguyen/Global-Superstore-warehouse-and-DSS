-- Lookup rows appended by the test batch carry its ingestion id. Rows that
-- matched an existing entry were never inserted (ON CONFLICT DO NOTHING),
-- so only test-owned rows are removed here.
DELETE FROM bronze.postal_code WHERE ingestion = ANY(:ids);
