-- Validation: Check domain constraints and business rules in silver.orders
SELECT 
    COUNT(CASE WHEN ship_date < order_date THEN 1 END) AS invalid_ship_dates,
    COUNT(CASE WHEN sales < 0 THEN 1 END) AS negative_sales,
    COUNT(CASE WHEN quantity <= 0 THEN 1 END) AS non_positive_quantity,
    COUNT(CASE WHEN discount < 0 OR discount > 1.0 THEN 1 END) AS invalid_discount,
    COUNT(CASE WHEN shipping_cost < 0 THEN 1 END) AS negative_shipping_cost
FROM silver.orders;
