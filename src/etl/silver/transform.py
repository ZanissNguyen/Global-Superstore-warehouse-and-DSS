"""
Silver ETL Transformation
Reads untransformed records from bronze.raw_orders, applies data quality rules,
parses dates, standardizes types, and loads into silver.orders.
"""

from pathlib import Path
import sys

from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql
from src.pipeline.reader import read_sql
from src.pipeline.logger import setup_logger, log_execution

def init_silver_schema(engine, dry_run: bool = False, rollback: bool = False):
    execute_sql(
        engine,
        read_sql("silver/schema/create_orders.sql"),
        dry_run=dry_run,
        rollback=rollback
    )
    print("Silver schema and orders table initialized.")

def run_silver_transform(engine, dry_run: bool = False, rollback: bool = False):
    logger = setup_logger(name="silver", run_id="silver_transform_001")

    @log_execution(logger)
    def do_transform():
        sql = read_sql("silver/transform/transform_orders.sql")
        result = execute_sql(engine, sql, dry_run=dry_run, rollback=rollback)
        return result

    result = do_transform()
    print(f"Silver transformation completed with result: {result}")
    return result

def main(dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    init_silver_schema(engine, dry_run=dry_run, rollback=rollback)
    run_silver_transform(engine, dry_run=dry_run, rollback=rollback)

if __name__ == "__main__":
    from src.pipeline.cli import parse_args
    args = parse_args("Silver Layer ETL")
    main(dry_run=args.dry_run, rollback=args.rollback)
