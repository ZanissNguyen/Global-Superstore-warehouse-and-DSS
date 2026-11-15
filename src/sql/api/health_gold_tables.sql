SELECT table_name, to_regclass('gold.' || table_name) IS NOT NULL AS present
FROM unnest(ARRAY[
    'fact_sales', 'dim_date', 'dim_product',
    'dim_customer', 'dim_geography', 'dim_ship_mode'
]) AS required(table_name)
