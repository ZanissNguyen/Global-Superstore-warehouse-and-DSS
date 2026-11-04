"""
Utility: Export Gold and DSS Data to CSV for Power BI Desktop
Generates flat CSV tables in data/powerbi_export/ for direct file-based import.
"""

from pathlib import Path
import pandas as pd
from src.pipeline.database import create_db_engine
from src.pipeline.executor import query_sql

def export_tables():
    engine = create_db_engine()
    out_dir = Path("data/powerbi_export")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    tables = [
        ("gold.dim_date", "dim_date.csv"),
        ("gold.dim_customer", "dim_customer.csv"),
        ("gold.dim_product", "dim_product.csv"),
        ("gold.dim_geography", "dim_geography.csv"),
        ("gold.dim_ship_mode", "dim_ship_mode.csv"),
        ("gold.fact_sales", "fact_sales.csv"),
        ("dss.association_rule", "association_rule.csv"),
        ("dss.forecast_result", "forecast_result.csv"),
    ]
    
    print("=" * 60)
    print("EXPORTING WAREHOUSE TABLES FOR POWER BI DESKTOP")
    print(f"Target Directory: {out_dir.resolve()}")
    print("=" * 60)
    
    for tbl, filename in tables:
        sql = f"SELECT * FROM {tbl};"
        df = query_sql(engine, sql)
        target_path = out_dir / filename
        df.to_csv(target_path, index=False, encoding="utf-8-sig")
        print(f"Exported {tbl:22} -> {filename:20} ({len(df):>6,} rows)")
        
    print("=" * 60)
    print("Export completed successfully! Tables ready for Power BI import.")

if __name__ == "__main__":
    export_tables()
