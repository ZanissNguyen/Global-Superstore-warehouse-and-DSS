DELETE FROM gold.fact_sales WHERE CAST(row_id AS INTEGER) >= 60000;
