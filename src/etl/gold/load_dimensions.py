"""
Gold ETL: Load Dimensions
Initializes Gold dimension schemas and populates all 5 Dimension tables:
DimDate, DimCustomer, DimProduct, DimGeography, DimShipMode.
"""

from src.pipeline.database import create_db_engine
from src.pipeline.executor import execute_sql
from src.pipeline.reader import read_sql
from src.pipeline.logger import setup_logger, log_execution

DIMENSION_SCHEMAS = [
    "gold/schema/create_dim_date.sql",
    "gold/schema/create_dim_customer.sql",
    "gold/schema/create_dim_product.sql",
    "gold/schema/create_dim_geography.sql",
    "gold/schema/create_dim_ship_mode.sql",
]

DIMENSION_LOADERS = [
    ("Date Dimension", "gold/dimensions/load_dim_date.sql"),
    ("Customer Dimension", "gold/dimensions/load_dim_customer.sql"),
    ("Product Dimension", "gold/dimensions/load_dim_product.sql"),
    ("Geography Dimension", "gold/dimensions/load_dim_geography.sql"),
    ("Ship Mode Dimension", "gold/dimensions/load_dim_ship_mode.sql"),
]

def init_gold_dimension_schemas(engine, dry_run: bool = False, rollback: bool = False):
    for schema_file in DIMENSION_SCHEMAS:
        execute_sql(engine, read_sql(schema_file), dry_run=dry_run, rollback=rollback)
    print("Gold dimension tables created/verified.")

def run_dimension_loaders(engine, dry_run: bool = False, rollback: bool = False):
    logger = setup_logger(name="gold_dims", run_id="gold_dims_001")

    @log_execution(logger)
    def load_all():
        for name, sql_file in DIMENSION_LOADERS:
            print(f"Loading {name} via {sql_file}...")
            execute_sql(engine, read_sql(sql_file), dry_run=dry_run, rollback=rollback)
            print(f"{name} loaded successfully.")

    load_all()

def main(dry_run: bool = False, rollback: bool = False):
    engine = create_db_engine()
    init_gold_dimension_schemas(engine, dry_run=dry_run, rollback=rollback)
    run_dimension_loaders(engine, dry_run=dry_run, rollback=rollback)

if __name__ == "__main__":
    from src.pipeline.cli import parse_args
    args = parse_args("Gold Layer Dimensions ETL")
    main(dry_run=args.dry_run, rollback=args.rollback)
