SELECT COUNT(*) FROM silver.orders WHERE row_id = ANY(:ids)
