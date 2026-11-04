import argparse
from pathlib import Path
from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql
from src.pipeline.reader import read_sql

DDL_INIT_SCRIPTS = [
    ("Bronze Schema", "bronze/schema/create_schema.sql"),
    ("Bronze Ingestion Table", "bronze/schema/create_ingestion.sql"),
    ("Bronze Raw Orders Table", "bronze/schema/create_raw_orders.sql"),
    ("Bronze Postal Code Table", "bronze/schema/create_postal_code.sql"),
    ("Bronze Market Table", "bronze/schema/create_market.sql"),
    ("Silver Orders Table", "silver/schema/create_orders.sql"),
    ("Gold Dim Date Table", "gold/schema/create_dim_date.sql"),
    ("Gold Dim Customer Table", "gold/schema/create_dim_customer.sql"),
    ("Gold Dim Product Table", "gold/schema/create_dim_product.sql"),
    ("Gold Dim Geography Table", "gold/schema/create_dim_geography.sql"),
    ("Gold Dim Ship Mode Table", "gold/schema/create_dim_ship_mode.sql"),
    ("Gold Fact Sales Table", "gold/schema/create_fact_sales.sql"),
    ("DSS Schema & Tables", "gold/schema/create_dss_schema.sql"),
    ("Populate Dim Date Calendar", "gold/dimensions/load_dim_date.sql")
]

def init_database(dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    print("=" * 60)
    print("INITIALIZING ALL DATABASE SCHEMAS AND TABLES (INIT DDL)")
    print("=" * 60)

    for name, script_path in DDL_INIT_SCRIPTS:
        print(f"Executing DDL: {name} ({script_path})...", end=" ")
        try:
            sql = read_sql(script_path)
            execute_sql(engine, sql, dry_run=dry_run, rollback=rollback)
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            raise

    print("=" * 60)
    print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)

def create_parser(description: str = "ETL Pipeline"):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional input file or directory path"
    )

    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize all database schemas and tables (DDL init)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute without committing changes"
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Execute SQL then rollback"
    )

    return parser

def parse_args(description: str = "ETL Pipeline"):
    parser = create_parser(description)
    args = parser.parse_args()

    if args.rollback and not args.dry_run:
        parser.error("--rollback requires --dry-run")

    return args

if __name__ == "__main__":
    args = parse_args("Pipeline CLI Utilities")
    if args.init_db:
        init_database(dry_run=args.dry_run, rollback=args.rollback)
    else:
        print("Use --help to see available commands or --init-db to initialize database schemas.")
