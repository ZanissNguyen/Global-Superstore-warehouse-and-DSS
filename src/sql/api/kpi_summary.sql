SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(quantity), 0) AS total_units,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(profit) / NULLIF(SUM(sales), 0) * 100, 2) AS profit_margin_pct,
    ROUND(COUNT(CASE WHEN is_returned THEN 1 END)::NUMERIC / NULLIF(COUNT(DISTINCT order_id), 0) * 100, 2) AS return_rate_pct
FROM gold.fact_sales;
