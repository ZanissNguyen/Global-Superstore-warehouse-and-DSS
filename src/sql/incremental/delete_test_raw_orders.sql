DELETE FROM bronze.raw_orders WHERE ingestion = ANY(:ids);
