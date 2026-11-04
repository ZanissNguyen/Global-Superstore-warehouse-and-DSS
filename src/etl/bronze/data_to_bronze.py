# config
from src.pipeline.cli import parse_args
from pathlib import Path
import sys

from src.pipeline.reader import read_sql

from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql, truncate_table

from src.etl.bronze.extract import extract_market, extract_postal_code, read_raw_data, is_file_extracted, valid_data
from src.etl.bronze.load import record_ingestion, record_market, record_pin, record_raw_orders

def database_init(engine, dry_run: bool = False, rollback: bool = False):
    # database

    # schema init
    execute_sql(engine,
        read_sql("bronze/schema/create_schema.sql"),
        dry_run, rollback
    )
    print("Bronze schema created")

    # table init
    # ingestion
    execute_sql(engine,
        read_sql("bronze/schema/create_ingestion.sql"),
        dry_run, rollback,
    )
    # raw orders
    execute_sql(engine,
        read_sql("bronze/schema/create_raw_orders.sql"),
        dry_run, rollback,
    )
    # postal code
    execute_sql(engine,
        read_sql("bronze/schema/create_postal_code.sql"),
        dry_run, rollback,
    )
    # market
    execute_sql(engine,
        read_sql("bronze/schema/create_market.sql"),
        dry_run, rollback,)
    print("Ingestion table created")

def truncate_tables(engine, dry_run: bool = False, rollback: bool = False):
    truncate_table(engine, "bronze", "ingestion", dry_run=dry_run, rollback=rollback)
    truncate_table(engine, "bronze", "raw_orders", dry_run=dry_run, rollback=rollback)
    truncate_table(engine, "bronze", "postal_code", dry_run=dry_run, rollback=rollback)
    truncate_table(engine, "bronze", "market", dry_run=dry_run, rollback=rollback)

def main(
    input_path: Path | str | None = None,
    dry_run: bool = False,
    rollback: bool = False
):
    if input_path is not None:
        input_path = Path(input_path)
        print(f"Input: {input_path}")
    
    # ETL logic
    # 1. Init config and database schema, tables
    # 1.1. Init config
    PROJECT_ROOT = Path.cwd()
    SRC_DIR = PROJECT_ROOT / "src"

    sys.path.insert(0, str(SRC_DIR))

    print("Project root:", PROJECT_ROOT)
    print("Source exists:", SRC_DIR.exists())
    print("Pipeline exists:", (SRC_DIR / "pipeline").is_dir())

    # 1.2. Init database schema, tables
    engine = create_db_engine()
    database_init(engine, dry_run=dry_run, rollback=rollback)

    # truncate_tables(engine)
    # return

    # 2. Read data from input path
    # 2.1 Extract orders
    df, content_hash, loaded_time = read_raw_data(input_path)
    if is_file_extracted(engine, content_hash):
        print("File already extracted. Skipping ingestion.")
        return
    checked_df = valid_data(df)
    # 2.2 Extract postal code and market for silver mapping
    unique_market, market_count = extract_market(checked_df)
    unique_pin, pin_count = extract_postal_code(checked_df)

    metadata = {
        "market_count": market_count,
        "pin_count": pin_count,
        "rows": checked_df.shape[0],
    }

    # 3. Load data to database
    # 3.1 Record ingestion
    ingestion_id = record_ingestion(
        engine,
        source_name=input_path.name,
        content_hash=content_hash,
        loaded_time=loaded_time,
        metadata=metadata,
        dry_run=dry_run,
        rollback=rollback
    )
    print(f"Ingestion record created with ID: {ingestion_id}")
    # 3.2 Record market
    market_result = record_market(
        engine,
        ingestion_id,
        unique_market,
        market_count,
        dry_run=dry_run,
        rollback=rollback
    )
    print(f"Market record created with result: {market_result}")
    # 3.3 Record postal code
    pin_result = record_pin(
        engine,
        ingestion_id,
        unique_pin,
        pin_count,
        dry_run=dry_run,
        rollback=rollback
    )
    print(f"Postal code record created with result: {pin_result}")
    # 3.4 Record raw orders
    raw_orders_result = record_raw_orders(  
        engine,
        ingestion_id,
        checked_df,
        dry_run=dry_run,
        rollback=rollback
    )
    print(f"Raw orders record created with result: {raw_orders_result}")

    return
    
if __name__ == "__main__":
    args = parse_args("Bronze Layer ETL")

    main(
        input_path=args.input,
        dry_run=args.dry_run,
        rollback=args.rollback
    )
