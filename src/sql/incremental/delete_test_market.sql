-- Market lookup rows appended by the test batch (same pattern as postal).
DELETE FROM bronze.market WHERE ingestion = ANY(:ids);
