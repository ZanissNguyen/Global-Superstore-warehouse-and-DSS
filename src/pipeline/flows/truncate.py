"""
Flow: Truncate Schema Tables
Empties every base table in the selected medallion schema(s)
(bronze / silver / gold / dss) using one TRUNCATE statement per schema.

Usage:
    python -m src.pipeline.flows.truncate --schema bronze
    python -m src.pipeline.flows.truncate --schema all
    python -m src.pipeline.flows.truncate --schema bronze,silver --dry-run
"""

import argparse

from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql, query_sql

SCHEMAS = ("bronze", "silver", "gold", "dss")


def list_tables(engine, schema: str) -> list[str]:
    df = query_sql(
        engine,
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :schema
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
        {"schema": schema},
    )
    if df.empty:
        return []
    return df["table_name"].tolist()


def count_rows(engine, schema: str, table: str) -> int:
    # table name comes from information_schema, not user input
    df = query_sql(engine, f'SELECT COUNT(*) AS n FROM "{schema}"."{table}"')
    return int(df.iloc[0]["n"])


def parse_schemas(raw: str) -> list[str]:
    requested = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if "all" in requested:
        return list(SCHEMAS)

    unknown = [part for part in requested if part not in SCHEMAS]
    if unknown:
        raise ValueError(
            f"Unknown schema(s): {', '.join(unknown)}. "
            f"Choose from: {', '.join(SCHEMAS)}, all"
        )
    if not requested:
        raise ValueError("No schema provided. Use --schema bronze (or silver/gold/dss/all).")
    return requested


def run_truncate(schemas: list[str], dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    print("=" * 60)
    print(f"TRUNCATING SCHEMA(S): {', '.join(schemas)}")
    print("=" * 60)

    summary = {}

    for schema in schemas:
        tables = list_tables(engine, schema)

        if not tables:
            print(f"[{schema}] No base tables found (schema not initialized?). Skipped.")
            summary[schema] = []
            continue

        print(f"[{schema}] Tables to truncate ({len(tables)}):")
        for table in tables:
            rows = count_rows(engine, schema, table)
            print(f"    - {schema}.{table}: {rows} rows")

        # One statement per schema: CASCADE handles intra-schema foreign keys
        # (gold.fact_sales -> dims, dss.run -> result).
        table_list = ", ".join(f'"{schema}"."{table}"' for table in tables)
        sql = f"TRUNCATE TABLE {table_list} CASCADE;"

        execute_sql(engine, sql, dry_run=dry_run, rollback=rollback)
        summary[schema] = tables
        print(f"[{schema}] TRUNCATE {'previewed' if dry_run else 'executed'}.")

    print("=" * 60)
    if dry_run and not rollback:
        print("DRY RUN COMPLETED - NO DATA WAS MODIFIED.")
    elif dry_run and rollback:
        print("TEST EXECUTION COMPLETED - ALL CHANGES WERE ROLLED BACK.")
    else:
        print("TRUNCATE COMPLETED SUCCESSFULLY!")
        if "gold" in schemas:
            print("NOTE: gold materialized views still hold the old data.")
            print("      Run: python -m src.pipeline.flows.refresh_warehouse")
    print("=" * 60)

    return summary


def create_parser(description: str = "Truncate Schema Tables"):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--schema",
        required=True,
        help="Schema(s) to truncate: bronze, silver, gold, dss or all "
             "(comma-separated, e.g. bronze,silver)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the TRUNCATE without committing changes",
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Execute SQL then rollback (requires --dry-run)",
    )

    return parser


if __name__ == "__main__":
    parser = create_parser("Truncate Schema Tables")
    args = parser.parse_args()

    if args.rollback and not args.dry_run:
        parser.error("--rollback requires --dry-run")

    try:
        schemas = parse_schemas(args.schema)
    except ValueError as error:
        parser.error(str(error))

    run_truncate(schemas, dry_run=args.dry_run, rollback=args.rollback)
