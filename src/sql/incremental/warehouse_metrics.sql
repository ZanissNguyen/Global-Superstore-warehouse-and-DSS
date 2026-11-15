SELECT 
    (SELECT COUNT(*) FROM bronze.ingestion) AS ingestion_batches,
    (SELECT COALESCE(MAX(id), 0) FROM bronze.ingestion) AS latest_ingestion_id,
    (SELECT COUNT(*) FROM bronze.raw_orders) AS bronze_rows,
    (SELECT COUNT(*) FROM silver.orders) AS silver_rows,
    (SELECT COUNT(*) FROM gold.fact_sales) AS gold_rows,
    (SELECT COALESCE(SUM(sales), 0) FROM gold.fact_sales) AS total_sales,
    (SELECT COALESCE(SUM(profit), 0) FROM gold.fact_sales) AS total_profit
