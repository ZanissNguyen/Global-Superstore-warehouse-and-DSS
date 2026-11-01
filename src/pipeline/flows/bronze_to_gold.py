# from etl.bronze.load import run as load_bronze
# from etl.silver.transform import run as transform_silver
# from etl.gold.load_dimensions import run as load_dimensions
# from etl.gold.load_facts import run as load_facts

# def run_pipeline(input_path, engine, dry_run=False):
#     # 1. Ingestion + Bronze
#     batch_id = load_bronze(
#         input_path=input_path,
#         engine=engine,
#         dry_run=dry_run
#     )

#     # 2. Silver
#     transform_silver(
#         engine=engine,
#         batch_id=batch_id,
#         dry_run=dry_run
#     )

#     # 3. Gold
#     load_dimensions(engine=engine, dry_run=dry_run)
#     load_facts(engine=engine, dry_run=dry_run)

#     # 4. Validation
#     # 5. Refresh Materialized Views
#     # REFRESH MATERIALIZED VIEW gold.mv_sales_mart;
#     # REFRESH MATERIALIZED VIEW gold.mv_product_mart;
#     # REFRESH MATERIALIZED VIEW gold.mv_customer_mart;
#     # Các marts cần quan tâm thứ tự các câu truy vấn nếu chúng có quan hệ phụ thuộc với nhau.