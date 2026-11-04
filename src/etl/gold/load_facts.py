"""
Gold ETL: Load Facts
Initializes FactSales schema and loads transactional data by resolving
surrogate keys from the 5 Dimension tables. Refreshes Data Marts.
"""

from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql
from src.pipeline.reader import read_sql
from src.pipeline.logger import setup_logger, log_execution

def init_fact_schema(engine, dry_run: bool = False, rollback: bool = False):
    execute_sql(engine, read_sql("gold/schema/create_fact_sales.sql"), dry_run=dry_run, rollback=rollback)
    print("Gold fact_sales table initialized.")

def run_fact_loader(engine, dry_run: bool = False, rollback: bool = False):
    logger = setup_logger(name="gold_facts", run_id="gold_facts_001")

    @log_execution(logger)
    def load_fact():
        print("Loading gold.fact_sales...")
        result = execute_sql(engine, read_sql("gold/facts/load_fact_sales.sql"), dry_run=dry_run, rollback=rollback)
        print("gold.fact_sales loaded successfully.")
        return result

    return load_fact()

def refresh_marts(engine, dry_run: bool = False, rollback: bool = False):
    print("Creating/Refreshing Materialized Views in Gold...")
    execute_sql(engine, read_sql("gold/marts/create_materialized_views.sql"), dry_run=dry_run, rollback=rollback)
    print("Materialized Views refreshed.")

def main(dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    init_fact_schema(engine, dry_run=dry_run, rollback=rollback)
    run_fact_loader(engine, dry_run=dry_run, rollback=rollback)
    refresh_marts(engine, dry_run=dry_run, rollback=rollback)

if __name__ == "__main__":
    from src.pipeline.cli import parse_args
    args = parse_args("Gold Layer Fact Sales ETL")
    main(dry_run=args.dry_run, rollback=args.rollback)
