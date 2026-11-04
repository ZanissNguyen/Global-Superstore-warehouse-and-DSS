"""
Gold Layer Data Quality Validation
Verifies fact table grain, referential integrity (foreign keys),
and aggregate reconciliation against Silver.
"""

from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql
from src.pipeline.reader import read_sql

def run_gold_validation(engine):
    print("=== Running Gold Layer Data Validation ===")

    # 1. Fact grain check
    grain_df = query_sql(engine, read_sql("gold/validation/check_fact_grain.sql"))
    print("\n--- Fact Grain (Duplicate row_id) Check ---")
    if grain_df.empty:
        print("PASS: Fact grain is unique at row_id level.")
    else:
        print(f"FAIL: Found {len(grain_df)} duplicated row_ids in fact_sales!")

    # 2. Foreign keys orphan check
    fk_df = query_sql(engine, read_sql("gold/validation/check_foreign_keys.sql"))
    print("\n--- Orphan Foreign Keys Check ---")
    print(fk_df)

    # 3. Aggregate reconciliation check
    agg_df = query_sql(engine, read_sql("gold/validation/check_aggregates.sql"))
    print("\n--- Aggregate Reconciliation (Silver vs Gold) ---")
    print(agg_df)

    print("\nGold validation completed.")

def main():
    engine = create_db_engine()
    run_gold_validation(engine)

if __name__ == "__main__":
    main()
