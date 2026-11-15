-- Test batches are identified by content (Row ID beyond the baseline range
-- 1-51290 of Global_Superstore.xls), not by file name: the demo input may be
-- a generated batch (60001-60500) or Sample-Superstore.xlsx (51291-61284).
SELECT DISTINCT ingestion AS id
FROM bronze.raw_orders
WHERE CAST("Row ID" AS INTEGER) >= 51291;
