"""
Flow: Refresh Warehouse Materialized Views
Refreshes all Gold Data Marts in proper dependency order.
"""

from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql
from src.pipeline.reader import read_sql

def refresh_all_marts(dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    print("=" * 60)
    print("REFRESHING GOLD DATA MARTS (MATERIALIZED VIEWS)")
    print("=" * 60)

    sql = read_sql("gold/marts/refresh_all_marts.sql")
    execute_sql(engine, sql, dry_run=dry_run, rollback=rollback)
    print("All Gold Materialized Views refreshed successfully.")

if __name__ == "__main__":
    from src.pipeline.cli import parse_args
    args = parse_args("Refresh Warehouse Marts")
    refresh_all_marts(dry_run=args.dry_run, rollback=args.rollback)
