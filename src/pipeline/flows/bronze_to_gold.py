"""
Master Pipeline Flow: Bronze -> Silver -> Gold
Executes full data lifecycle from raw file ingestion to star schema and data marts.
"""

from pathlib import Path
from src.pipeline.database import create_db_engine
from src.pipeline.cli import parse_args

from src.etl.bronze.data_to_bronze import main as run_bronze
from src.etl.silver.transform import main as run_silver
from src.etl.silver.validate import run_silver_validation
from src.etl.gold.load_dimensions import main as run_gold_dimensions
from src.etl.gold.load_facts import main as run_gold_facts
from src.etl.gold.validate import run_gold_validation

def run_pipeline(input_path: Path, dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    print("=" * 60)
    print(f"STARTING FULL MEDALLION ETL PIPELINE FOR: {input_path}")
    print("=" * 60)

    # 1. Bronze Layer
    print("\n>>> STEP 1: BRONZE INGESTION >>>")
    run_bronze(input_path=input_path, dry_run=dry_run, rollback=rollback)

    # 2. Silver Layer
    print("\n>>> STEP 2: SILVER TRANSFORMATION >>>")
    run_silver(dry_run=dry_run, rollback=rollback)
    if not dry_run:
        run_silver_validation(engine)

    # 3. Gold Layer
    print("\n>>> STEP 3: GOLD DIMENSIONAL LOADING >>>")
    run_gold_dimensions(dry_run=dry_run, rollback=rollback)
    run_gold_facts(dry_run=dry_run, rollback=rollback)
    if not dry_run:
        run_gold_validation(engine)

    print("\n" + "=" * 60)
    print("FULL MEDALLION ETL PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    args = parse_args("Master Medallion Pipeline Flow")
    if not args.input:
        print("Error: Please provide --input file path.")
    else:
        run_pipeline(
            input_path=args.input,
            dry_run=args.dry_run,
            rollback=args.rollback
        )
