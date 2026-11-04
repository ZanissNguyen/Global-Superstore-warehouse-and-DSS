"""
Silver Layer Data Quality Validation
Executes null checks, duplicate checks, and domain constraint checks on silver.orders.
"""

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql
from src.pipeline.reader import read_sql

def run_silver_validation(engine):
    print("=== Running Silver Layer Data Validation ===")

    # 1. Null check
    null_df = query_sql(engine, read_sql("silver/validation/check_nulls.sql"))
    print("\n--- NULL Check Results ---")
    print(null_df)

    # 2. Duplicate check
    dup_df = query_sql(engine, read_sql("silver/validation/check_duplicates.sql"))
    print("\n--- Duplicate Row ID Check Results ---")
    if dup_df.empty:
        print("PASS: No duplicate row_id found.")
    else:
        print(f"FAIL: Found {len(dup_df)} duplicate keys!")
        print(dup_df.head(10))

    # 3. Data quality check
    dq_df = query_sql(engine, read_sql("silver/validation/check_data_quality.sql"))
    print("\n--- Domain Constraints Check Results ---")
    print(dq_df)

    print("\nSilver validation completed.")

def main():
    engine = create_db_engine()
    run_silver_validation(engine)

if __name__ == "__main__":
    main()
