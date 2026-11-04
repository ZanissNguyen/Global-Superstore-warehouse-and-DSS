-- Validation: Compare total Sales, Profit, and Quantity between Silver and Gold layers
SELECT 
    'silver.orders' AS layer,
    COUNT(*) AS total_rows,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM silver.orders

UNION ALL

SELECT 
    'gold.fact_sales' AS layer,
    COUNT(*) AS total_rows,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity
FROM gold.fact_sales;
